import copy
import json
import os
from pathlib import Path
from typing import Any, Dict, List

from jsonschema import Draft202012Validator

import agent as app
from agents.brain import brain_step
from agents.validation_agent import (
    load_template,
    build_required_paths,
    missing_paths,
    next_question_for_missing,
    next_question_advanced,
    resolve_menu_answer,
)
from agents.nlu import detect_intent
from agents.value_store import get_value as vs_get_value, get_meta as vs_get_meta, set_value as vs_set_value


BASE_DIR = Path(__file__).parent
SCENARIOS_DIR = BASE_DIR / "tests" / "conversation_scenarios"
TEMPLATE_FILE = BASE_DIR / "configmaster_required_fields.json"
SCHEMA_FILE = BASE_DIR / "configmaster_schema.json"


def _deepcopy_values_by_paths(facts: dict, paths: List[str]) -> Dict[str, Any]:
    return {p: copy.deepcopy(vs_get_value(facts, p)) for p in paths}


def _changed_paths(before: Dict[str, Any], after: Dict[str, Any]) -> List[str]:
    out = []
    for p, v in before.items():
        if v != after.get(p):
            out.append(p)
    return out


def _mock_llm_factory(rules: List[dict]):
    def _mock_extract_with_llm_status(text: str, allowed_fields, current_facts=None):
        txt = (text or "").lower()
        out = {"fields": {}}
        for r in rules or []:
            contains = str(r.get("contains", "")).lower().strip()
            if contains and contains not in txt:
                continue
            fields = r.get("fields", {}) or {}
            for p, meta in fields.items():
                if p not in set(allowed_fields or []):
                    continue
                if isinstance(meta, dict):
                    out["fields"][p] = {
                        "value": meta.get("value"),
                        "confidence": float(meta.get("confidence", 0.9)),
                    }
        return "LLM_OK", out

    return _mock_extract_with_llm_status


def _apply_seed_values(state: dict, seed_values: List[dict]):
    for s in seed_values or []:
        vs_set_value(
            state["facts"],
            s["path"],
            s.get("value"),
            source=s.get("source", "user"),
            confidence=float(s.get("confidence", 1.0)),
            evidence=s.get("evidence"),
        )


def _new_state(template_obj: dict, goal_text: str):
    st = {
        "meta": {},
        "goal": goal_text,
        "facts": copy.deepcopy(template_obj),
        "provenance": {},
        "dialog_state": app.default_dialog_state(),
        "history": [],
        "done": False,
    }
    app.ensure_dialog_state(st)
    return st


def run_scenario(scenario: dict) -> dict:
    template_obj = load_template(TEMPLATE_FILE)
    schema_obj = json.loads(Path(SCHEMA_FILE).read_text(encoding="utf-8-sig"))
    validator = Draft202012Validator(schema_obj)
    req_paths = build_required_paths(template_obj)

    state = _new_state(template_obj, scenario.get("name", "scenario"))
    _apply_seed_values(state, scenario.get("seed_values", []))

    llm_mode = (scenario.get("llm_mode") or "normal").lower()
    old_env = os.getenv("HPS_FORCE_LLM_DOWN")
    patched = None
    import agents.conversation_agent as conv

    if llm_mode == "down":
        os.environ["HPS_FORCE_LLM_DOWN"] = "1"
    elif llm_mode == "mock":
        os.environ.pop("HPS_FORCE_LLM_DOWN", None)
        patched = conv.extract_with_llm_status
        conv.extract_with_llm_status = _mock_llm_factory(scenario.get("mock_llm_rules", []))
    else:
        os.environ.pop("HPS_FORCE_LLM_DOWN", None)

    turns = []
    status = "RUNNING"

    def auto_fill_tool(facts: dict):
        state["facts"] = facts
        from tools import call_tool

        call_tool("autofill", state=state)
        return state["facts"]

    def apply_user_message_to_facts_tool(state_, template_obj_, user_text_):
        from tools import call_tool

        return call_tool("extract_fields", state=state_, template_obj=template_obj_, user_text=user_text_)

    try:
        for i, user_msg in enumerate(scenario.get("messages", []), start=1):
            decision = brain_step(
                state=state,
                template_obj=template_obj,
                req_paths=req_paths,
                user_msg=None,
                dialog_state=state.get("dialog_state"),
                apply_user_message_to_facts=apply_user_message_to_facts_tool,
                apply_single_field_answer=app.apply_single_field_answer,
                apply_multi_field_answer=app.apply_multi_field_answer,
                missing_paths=missing_paths,
                next_question_for_missing=next_question_for_missing,
                next_question_advanced=next_question_advanced,
                auto_fill=auto_fill_tool,
            )

            if decision["type"] == "DONE":
                state["done"] = True
                state["dialog_state"]["step"] = "completed"
                status = "DONE"
                break

            ds = state["dialog_state"]
            q = decision["question"]
            paths = list(decision.get("paths") or [])
            ds["step"] = "collecting"
            ds["last_question"] = q
            ds["last_question_paths"] = paths
            ds["missing_fields"] = missing_paths(state.get("facts", {}), template_obj, req_paths)
            ds["active_menu"] = decision.get("menu")
            ds["last_user_message"] = user_msg
            ds["asked_fields"] = list(ds.get("asked_fields") or [])
            for p in paths:
                if p not in ds["asked_fields"]:
                    ds["asked_fields"].append(p)

            turn = {
                "turn": i,
                "user": user_msg,
                "question": q,
                "question_paths": paths,
                "intent": None,
                "changed_paths": [],
                "step": ds.get("step"),
                "last_extraction": {},
            }

            active_menu = ds.get("active_menu")
            normalized_user = user_msg
            if isinstance(active_menu, dict) and active_menu.get("options"):
                ok, mapped = resolve_menu_answer(active_menu, user_msg)
                if ok:
                    normalized_user = mapped
                    state.setdefault("meta", {})["menu_selected_paths"] = list(ds.get("last_question_paths") or [])

            intent = detect_intent(normalized_user, ds, state.get("facts", {}))
            ds["last_intent"] = intent
            turn["intent"] = intent

            if intent in {"show_status", "greeting", "thanks", "help_or_confusion", "clarification_request", "out_of_scope", "create", "modify", "delete", "resume"}:
                if intent == "help_or_confusion":
                    ds["mode"] = "simplified"
                    ds["nlu_fail_count"] = int(ds.get("nlu_fail_count") or 0) + 1
                turn["step"] = ds.get("step")
                turn["last_extraction"] = copy.deepcopy((state.get("meta", {}) or {}).get("last_extraction") or {})
                turns.append(turn)
                continue

            if intent in {"confirmation_yes", "confirmation_no"}:
                pending = ds.get("pending_confirmations") if isinstance(ds.get("pending_confirmations"), list) else []
                if ds.get("step") == "confirming_conflict" and pending:
                    cur = pending.pop(0)
                    if intent == "confirmation_yes":
                        app.vs_set_value(
                            state["facts"],
                            cur.get("path"),
                            cur.get("new_value"),
                            source=str(cur.get("new_source") or "user"),
                            confidence=1.0,
                        )
                        auto_fill_tool(state["facts"])
                    ds["step"] = "collecting" if not pending else "confirming_conflict"
                turn["step"] = ds.get("step")
                turn["last_extraction"] = copy.deepcopy((state.get("meta", {}) or {}).get("last_extraction") or {})
                turns.append(turn)
                continue

            if intent == "correction":
                before_conflicts = len(state.get("conflicts", [])) if isinstance(state.get("conflicts"), list) else 0
                before = _deepcopy_values_by_paths(state.get("facts", {}), req_paths)
                apply_user_message_to_facts_tool(state, template_obj, normalized_user)
                auto_fill_tool(state["facts"])
                after = _deepcopy_values_by_paths(state.get("facts", {}), req_paths)
                turn["changed_paths"] = _changed_paths(before, after)
                conflicts = state.get("conflicts", []) if isinstance(state.get("conflicts"), list) else []
                new_conflicts = conflicts[before_conflicts:] if len(conflicts) >= before_conflicts else []
                if new_conflicts:
                    c = new_conflicts[-1]
                    ds["pending_confirmations"] = list(ds.get("pending_confirmations") or [])
                    ds["pending_confirmations"].append(
                        {
                            "path": c.get("path"),
                            "old_value": c.get("old_value"),
                            "new_value": c.get("new_value"),
                            "old_source": c.get("old_source", "rules"),
                            "new_source": c.get("new_source", "user"),
                            "reason": "user_correction",
                            "created_at": c.get("created_at"),
                        }
                    )
                    ds["step"] = "confirming_conflict"
                turn["step"] = ds.get("step")
                turn["last_extraction"] = copy.deepcopy((state.get("meta", {}) or {}).get("last_extraction") or {})
                turns.append(turn)
                continue

            before = _deepcopy_values_by_paths(state.get("facts", {}), req_paths)
            state["history"].append({"agent": q, "user": normalized_user})
            _ = brain_step(
                state=state,
                template_obj=template_obj,
                req_paths=req_paths,
                user_msg=normalized_user,
                dialog_state=state.get("dialog_state"),
                apply_user_message_to_facts=apply_user_message_to_facts_tool,
                apply_single_field_answer=app.apply_single_field_answer,
                apply_multi_field_answer=app.apply_multi_field_answer,
                missing_paths=missing_paths,
                next_question_for_missing=next_question_for_missing,
                next_question_advanced=next_question_advanced,
                auto_fill=auto_fill_tool,
            )
            app._normalize_numeric_fields_in_facts(state.get("facts", {}))
            after = _deepcopy_values_by_paths(state.get("facts", {}), req_paths)
            turn["changed_paths"] = _changed_paths(before, after)
            state["dialog_state"]["missing_fields"] = missing_paths(state.get("facts", {}), template_obj, req_paths)
            if state["dialog_state"]["step"] != "completed":
                state["dialog_state"]["step"] = "collecting"
            turn["step"] = state["dialog_state"]["step"]
            turn["last_extraction"] = copy.deepcopy((state.get("meta", {}) or {}).get("last_extraction") or {})
            turns.append(turn)

        if status == "RUNNING":
            status = "DONE" if state.get("done") else "PARTIAL"
    finally:
        if patched is not None:
            conv.extract_with_llm_status = patched
        if old_env is None:
            os.environ.pop("HPS_FORCE_LLM_DOWN", None)
        else:
            os.environ["HPS_FORCE_LLM_DOWN"] = old_env

    trace = {
        "scenario": scenario.get("name", "scenario"),
        "status": status,
        "turns": turns,
        "final_dialog_step": state.get("dialog_state", {}).get("step"),
        "final_mode": state.get("dialog_state", {}).get("mode"),
        "pending_confirmations": state.get("dialog_state", {}).get("pending_confirmations", []),
        "final_last_extraction": (state.get("meta", {}) or {}).get("last_extraction", {}),
        "facts_sources": {},
    }
    for p in scenario.get("source_paths", []):
        m = vs_get_meta(state.get("facts", {}), p)
        trace["facts_sources"][p] = m.get("source", "legacy")

    return trace


def evaluate_assertions(trace: dict, scenario: dict):
    failures = []
    turns = trace.get("turns", [])

    def _turn(n: int):
        if n <= 0 or n > len(turns):
            return {}
        return turns[n - 1]

    for a in scenario.get("assertions", []):
        kind = a.get("type")
        if kind == "intent_equals":
            t = _turn(int(a["turn"]))
            if t.get("intent") != a.get("value"):
                failures.append(f"turn {a['turn']} intent expected={a.get('value')} got={t.get('intent')}")
        elif kind == "step_equals":
            t = _turn(int(a["turn"]))
            if t.get("step") != a.get("value"):
                failures.append(f"turn {a['turn']} step expected={a.get('value')} got={t.get('step')}")
        elif kind == "source_equals":
            got = trace.get("facts_sources", {}).get(a.get("path"))
            if got != a.get("value"):
                failures.append(f"source {a.get('path')} expected={a.get('value')} got={got}")
        elif kind == "used_fallback_rules":
            t = _turn(int(a["turn"]))
            got = ((t.get("last_extraction") or {}).get("used_fallback_rules"))
            if bool(got) != bool(a.get("value")):
                failures.append(f"turn {a['turn']} used_fallback_rules expected={a.get('value')} got={got}")
        elif kind == "question_contains":
            t = _turn(int(a["turn"]))
            if str(a.get("value", "")).lower() not in str(t.get("question", "")).lower():
                failures.append(f"turn {a['turn']} question missing '{a.get('value')}'")
        else:
            failures.append(f"unknown assertion type: {kind}")

    return failures


def main():
    files = sorted(SCENARIOS_DIR.glob("*.json"))
    if not files:
        print("No scenarios found.")
        return 1

    out_dir = BASE_DIR / "tests" / "conversation_reports"
    out_dir.mkdir(parents=True, exist_ok=True)

    total = 0
    failed = 0
    for f in files:
        scenario = json.loads(f.read_text(encoding="utf-8-sig"))
        trace = run_scenario(scenario)
        failures = evaluate_assertions(trace, scenario)
        total += 1
        if failures:
            failed += 1
            verdict = "FAIL"
        else:
            verdict = "PASS"
        trace["assertion_failures"] = failures
        (out_dir / f"{f.stem}.trace.json").write_text(json.dumps(trace, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"[{verdict}] {scenario.get('name', f.stem)}")
        for x in failures:
            print(f"  - {x}")

    print(f"\nSummary: {total - failed}/{total} passed, {failed} failed")
    return 0 if failed == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
