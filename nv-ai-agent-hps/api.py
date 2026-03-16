"""
FastAPI wrapper around the ConfigMaster AI agent.
Run:  uvicorn api:app --reload --port 8000
"""

import json, copy, os, re
from pathlib import Path
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agents.auto_fill_rules import auto_fill
from agents.brain import brain_step
from agents.validation_agent import (
    load_template,
    build_required_paths,
    missing_paths,
    next_question_for_missing,
    humain_missing_list,
)
from agents.conversation_agent import (
    apply_user_message_to_facts,
    apply_single_field_answer,
    apply_multi_field_answer,
)
from agents.bank_pipeline import run_pipeline
from agents.pdf import JSONToPDFAgent

# ─── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
GOALS_DIR = BASE_DIR / "goals"
INDEX_FILE = GOALS_DIR / "index.json"
TEMPLATE_FILE = BASE_DIR / "configmaster_required_fields.json"

# ─── Helpers ──────────────────────────────────────────────────────────────────
def _load_json(path: Path, default=None):
    if not path.exists():
        return default if default is not None else {}
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def _save_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ─── Load template once ──────────────────────────────────────────────────────
GOALS_DIR.mkdir(parents=True, exist_ok=True)
template_obj = load_template(TEMPLATE_FILE)
_all_req_paths = build_required_paths(template_obj)

# Same ignore list as brain.py – these fields are never asked to the user
_IGNORE_PATTERNS = [
    r"^cards\.0\.limits\.selected_limit_types$",
    r"^cards\.0\.limits\.by_type\.DEFAULT\.(domestic|international|total)\.(daily|weekly|monthly)_count$",
    r"^cards\.0\.limits\.by_type\.DEFAULT\.total\.(daily|weekly|monthly)_amount$",
    r"^cards\.0\.limits\.by_type\.DEFAULT\.per_transaction\.(min|max)_amount$",
]

def _is_ignored(path: str) -> bool:
    return any(re.match(pat, path) for pat in _IGNORE_PATTERNS)

req_paths = [p for p in _all_req_paths if not _is_ignored(p)]

# ─── FastAPI app ──────────────────────────────────────────────────────────────
app = FastAPI(title="ConfigMaster AI Agent API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Pydantic models ─────────────────────────────────────────────────────────
class CreateGoalReq(BaseModel):
    message: str          # e.g. "ajouter banque Alpha au Maroc en MAD"


class ChatReq(BaseModel):
    message: str


class GoalSummary(BaseModel):
    goal_id: int
    client: str
    action: str
    folder: str
    done: bool
    missing_count: int
    created_at: Optional[str] = None


# ─── Utility ──────────────────────────────────────────────────────────────────
import re

def _slugify(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"\s+", "_", s)
    s = re.sub(r"[^a-z0-9_]+", "", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "client"


def _parse_client_and_action(msg: str):
    m = msg.lower()
    action = "other"
    if any(w in m for w in ["ajouter", "add", "creer", "créer", "nouveau", "nv", "new"]):
        action = "add"
    if any(w in m for w in ["modifier", "modify", "update", "mettre a jour", "mettre à jour", "changer"]):
        action = "modify"
    client = "client"
    mm = re.search(r"\bpour\s+([a-z0-9_ -]+)", m)
    if mm:
        client = mm.group(1).strip().split()[0]
    return client, action


def _next_client_number(index: dict, client_slug: str) -> int:
    mx = 0
    for g in index.get("goals", []):
        if g.get("client") == client_slug:
            mx = max(mx, int(g.get("client_n", 0)))
    return mx + 1


def _goal_state_path(folder: str) -> Path:
    return GOALS_DIR / folder / "state.json"


def _get_goal_entry(index: dict, goal_id: int):
    return next((g for g in index.get("goals", []) if int(g["goal_id"]) == goal_id), None)


def _compute_progress(state: dict) -> dict:
    """Compute completion percentage and missing fields."""
    facts = state.get("facts", {})
    miss = missing_paths(facts, template_obj, req_paths)
    total = len(req_paths)
    filled = total - len(miss)
    pct = round(filled / total * 100) if total else 100
    return {
        "total_fields": total,
        "filled_fields": filled,
        "missing_count": len(miss),
        "completion_pct": pct,
        "missing_paths": miss[:20],  # return first 20 for UI
    }


# ═══════════════════════════════════════════════════════════════════════════════
#  ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

# ── List all goals ────────────────────────────────────────────────────────────
@app.get("/api/goals", response_model=list[GoalSummary])
def list_goals():
    index = _load_json(INDEX_FILE, {"last_id": 0, "goals": []})
    results = []
    for g in index.get("goals", []):
        try:
            folder = g.get("folder", "")
            sp = _goal_state_path(folder)
            if not sp.parent.exists():
                continue  # skip goals whose folder was deleted
            st = _load_json(sp, {})
            miss = missing_paths(st.get("facts", {}), template_obj, req_paths) if st else req_paths
            results.append(GoalSummary(
                goal_id=int(g["goal_id"]),
                client=g.get("client", ""),
                action=g.get("action", ""),
                folder=folder,
                done=st.get("done", False) if st else False,
                missing_count=len(miss),
                created_at=st.get("meta", {}).get("created_at") if st else None,
            ))
        except Exception:
            continue  # skip corrupted goal entries
    return results


# ── Create a new goal ─────────────────────────────────────────────────────────
@app.post("/api/goals")
def create_goal(req: CreateGoalReq):
    index = _load_json(INDEX_FILE, {"last_id": 0, "goals": []})

    client_name, action = _parse_client_and_action(req.message)
    client_slug = _slugify(client_name)
    action_slug = _slugify(action)

    goal_id = int(index.get("last_id", 0)) + 1
    client_n = _next_client_number(index, client_slug)
    folder = f"{client_slug}_{client_n:03d}_{action_slug}"

    goal_dir = GOALS_DIR / folder
    (goal_dir / "artifacts").mkdir(parents=True, exist_ok=True)

    state = {
        "meta": {
            "goal_id": goal_id,
            "client": client_slug,
            "client_n": client_n,
            "action": action_slug,
            "created_at": datetime.now().isoformat(timespec="seconds"),
        },
        "goal": req.message,
        "facts": copy.deepcopy(template_obj),
        "history": [],
        "done": False,
    }

    # Extract initial info from the creation message
    apply_user_message_to_facts(state, template_obj, req.message)
    auto_fill(state["facts"])

    _save_json(goal_dir / "state.json", state)

    index["last_id"] = goal_id
    index["goals"].append({
        "goal_id": goal_id,
        "client": client_slug,
        "client_n": client_n,
        "action": action_slug,
        "folder": folder,
    })
    _save_json(INDEX_FILE, index)

    # Get first question
    decision = brain_step(
        state=state,
        template_obj=template_obj,
        req_paths=req_paths,
        user_msg=None,
        apply_user_message_to_facts=apply_user_message_to_facts,
        apply_single_field_answer=apply_single_field_answer,
        apply_multi_field_answer=apply_multi_field_answer,
        missing_paths=missing_paths,
        next_question_for_missing=next_question_for_missing,
        auto_fill=auto_fill,
    )
    _save_json(goal_dir / "state.json", state)

    progress = _compute_progress(state)

    return {
        "goal_id": goal_id,
        "folder": folder,
        "decision": decision,
        "progress": progress,
    }


# ── Chat with a goal (send answer, get next question) ────────────────────────
@app.post("/api/goals/{goal_id}/chat")
def chat_with_goal(goal_id: int, req: ChatReq):
    index = _load_json(INDEX_FILE, {"last_id": 0, "goals": []})
    entry = _get_goal_entry(index, goal_id)
    if not entry:
        raise HTTPException(404, "Goal not found")

    state_path = _goal_state_path(entry["folder"])
    state = _load_json(state_path, {})
    if not state:
        raise HTTPException(404, "State not found")

    if state.get("done"):
        return {
            "decision": {"type": "DONE"},
            "progress": _compute_progress(state),
            "message": "This goal is already complete.",
        }

    # First brain_step: process user's answer
    brain_step(
        state=state,
        template_obj=template_obj,
        req_paths=req_paths,
        user_msg=req.message,
        apply_user_message_to_facts=apply_user_message_to_facts,
        apply_single_field_answer=apply_single_field_answer,
        apply_multi_field_answer=apply_multi_field_answer,
        missing_paths=missing_paths,
        next_question_for_missing=next_question_for_missing,
        auto_fill=auto_fill,
    )

    # Append to history
    last_q = state.get("meta", {}).get("last_question_path", "")
    state.setdefault("history", []).append({
        "agent": last_q,
        "user": req.message,
    })

    # Second brain_step: get next question
    decision = brain_step(
        state=state,
        template_obj=template_obj,
        req_paths=req_paths,
        user_msg=None,
        apply_user_message_to_facts=apply_user_message_to_facts,
        apply_single_field_answer=apply_single_field_answer,
        apply_multi_field_answer=apply_multi_field_answer,
        missing_paths=missing_paths,
        next_question_for_missing=next_question_for_missing,
        auto_fill=auto_fill,
    )

    if decision["type"] == "DONE":
        state["done"] = True

    _save_json(state_path, state)

    progress = _compute_progress(state)

    return {
        "decision": decision,
        "progress": progress,
    }


# ── Get goal state & progress ────────────────────────────────────────────────
@app.get("/api/goals/{goal_id}")
def get_goal(goal_id: int):
    index = _load_json(INDEX_FILE, {"last_id": 0, "goals": []})
    entry = _get_goal_entry(index, goal_id)
    if not entry:
        raise HTTPException(404, "Goal not found")

    state_path = _goal_state_path(entry["folder"])
    state = _load_json(state_path, {})
    if not state:
        raise HTTPException(404, "State not found")

    progress = _compute_progress(state)

    return {
        "goal_id": goal_id,
        "folder": entry["folder"],
        "client": entry.get("client", ""),
        "action": entry.get("action", ""),
        "done": state.get("done", False),
        "goal": state.get("goal", ""),
        "progress": progress,
        "history": state.get("history", []),
        "facts": state.get("facts", {}),
    }


# ── Submit completed goal to backend ─────────────────────────────────────────
@app.post("/api/goals/{goal_id}/submit")
def submit_goal(goal_id: int):
    index = _load_json(INDEX_FILE, {"last_id": 0, "goals": []})
    entry = _get_goal_entry(index, goal_id)
    if not entry:
        raise HTTPException(404, "Goal not found")

    state_path = _goal_state_path(entry["folder"])
    state = _load_json(state_path, {})
    if not state:
        raise HTTPException(404, "State not found")

    if not state.get("done"):
        raise HTTPException(400, "Goal is not complete yet. Finish the conversation first.")

    try:
        result = run_pipeline(state_path=state_path, do_verify=True)
        return {"status": "success", "result": result}
    except Exception as exc:
        raise HTTPException(500, f"Submission failed: {exc}")


# ── Generate PDF report ──────────────────────────────────────────────────────
@app.post("/api/goals/{goal_id}/pdf")
def generate_pdf(goal_id: int):
    index = _load_json(INDEX_FILE, {"last_id": 0, "goals": []})
    entry = _get_goal_entry(index, goal_id)
    if not entry:
        raise HTTPException(404, "Goal not found")

    state_path = _goal_state_path(entry["folder"])
    state = _load_json(state_path, {})
    if not state:
        raise HTTPException(404, "State not found")

    pdf_name = f"HPS_Config_Report_{entry['folder']}.pdf"
    try:
        agent = JSONToPDFAgent(pdf_name, json_path=str(state_path))
        agent.run()
        pdf_path = os.path.join(agent.OUTPUT_FOLDER, pdf_name)
        if not os.path.isfile(pdf_path):
            raise HTTPException(500, "PDF was generated but file not found")
        return FileResponse(
            path=pdf_path,
            media_type="application/pdf",
            filename=pdf_name,
            headers={"Content-Disposition": f"inline; filename={pdf_name}"},
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(500, f"PDF generation failed: {exc}")


# ── Delete a goal ─────────────────────────────────────────────────────────────
@app.delete("/api/goals/{goal_id}")
def delete_goal(goal_id: int):
    index = _load_json(INDEX_FILE, {"last_id": 0, "goals": []})
    entry = _get_goal_entry(index, goal_id)
    if not entry:
        raise HTTPException(404, "Goal not found")

    # Remove folder
    import shutil
    goal_dir = GOALS_DIR / entry["folder"]
    if goal_dir.exists():
        shutil.rmtree(goal_dir)

    # Remove from index
    index["goals"] = [g for g in index["goals"] if int(g["goal_id"]) != goal_id]
    _save_json(INDEX_FILE, index)

    return {"status": "deleted", "goal_id": goal_id}


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/api/health")
def health():
    return {"status": "ok", "template_fields": len(req_paths)}
