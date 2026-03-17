from typing import Any, Dict, List, Optional
import re

from agents.powercard_constraints import is_powercard_profile


def brain_step(
    *,
    state: Dict[str, Any],
    template_obj: Dict[str, Any],
    req_paths: List[str],
    user_msg: Optional[str],
    dialog_state: Optional[Dict[str, Any]] = None,
    apply_user_message_to_facts=None,
    apply_single_field_answer=None,
    apply_multi_field_answer=None,
    missing_paths=None,
    next_question_for_missing=None,
    next_question_advanced=None,
    auto_fill=None,
) -> Dict[str, Any]:
    strict_profile = is_powercard_profile(state)

    ignore_patterns = [
        r"^cards\.0\.limits\.selected_limit_types$",
        r"^cards\.0\.limits\.by_type\.DEFAULT\.(domestic|international|total)\.(daily|weekly|monthly)_count$",
        r"^cards\.0\.limits\.by_type\.DEFAULT\.total\.(daily|weekly|monthly)_amount$",
        r"^cards\.0\.limits\.by_type\.DEFAULT\.per_transaction\.(min|max)_amount$",
    ]

    def _is_ignored(path: str) -> bool:
        if strict_profile:
            return False
        return any(re.match(pattern, path) for pattern in ignore_patterns)

    if user_msg:
        last_paths = state.get("meta", {}).get("last_question_paths") or []

        apply_user_message_to_facts(state, template_obj, user_msg)
        auto_fill(state["facts"])

        if last_paths:
            miss_after = missing_paths(state["facts"], template_obj, req_paths)
            miss_after = [p for p in miss_after if not _is_ignored(p)]
            pending_last_paths = [p for p in last_paths if p in miss_after]

            if len(pending_last_paths) > 1:
                ok = apply_multi_field_answer(state, template_obj, pending_last_paths, user_msg)
                if ok:
                    auto_fill(state["facts"])
            elif len(pending_last_paths) == 1:
                last_path = pending_last_paths[0]
                if last_path in miss_after:
                    ok = apply_single_field_answer(state, template_obj, last_path, user_msg)
                    if ok:
                        auto_fill(state["facts"])

    miss = missing_paths(state["facts"], template_obj, req_paths)
    miss = [p for p in miss if not _is_ignored(p)]
    if not miss:
        return {"type": "DONE"}

    def _validation_hint(path: str) -> str:
        meta = state.get("meta", {}) if isinstance(state.get("meta", {}), dict) else {}
        err = meta.get("last_validation_error")
        if isinstance(err, dict) and err.get("path") == path:
            return str(err.get("message") or "").strip()
        return ""

    if callable(next_question_advanced):
        adv = next_question_advanced(miss, dialog_state or {}, next_question_for_missing)
        if isinstance(adv, dict):
            adv_paths = adv.get("paths") or []
            adv_q = adv.get("question") or ""
            if adv_paths and adv_q:
                hint = _validation_hint(adv_paths[0])
                if hint:
                    adv_q = f"{hint}\n{adv_q}"
                state.setdefault("meta", {})["last_question_paths"] = adv_paths
                out = {"type": "ASK", "question": adv_q, "paths": adv_paths}
                if adv.get("menu") is not None:
                    out["menu"] = adv.get("menu")
                if adv.get("form") is not None:
                    out["form"] = adv.get("form")
                return out

    next_path = miss[0]
    state.setdefault("meta", {})["last_question_paths"] = [next_path]
    q = next_question_for_missing(next_path)
    hint = _validation_hint(next_path)
    if hint:
        q = f"{hint}\n{q}"
    return {"type": "ASK", "question": q, "paths": [next_path]}
