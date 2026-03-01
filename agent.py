# agent.py
import json
from pathlib import Path
from datetime import datetime
import re
import copy
import unicodedata
from jsonschema import Draft202012Validator
from agents.auto_fill_rules import auto_fill
from agents.brain import brain_step
from tools import call_tool
from agents.schema_validator import format_schema_error
from agents.validation_agent import (
    load_template,
    build_required_paths,
    missing_paths,
    next_question_for_missing,  
    humain_missing_list,
    next_question_advanced,
    resolve_menu_answer,
)

from agents.conversation_agent import (
    apply_user_message_to_facts,
    apply_single_field_answer,
    apply_multi_field_answer,
)
from agents.nlu import detect_intent
from agents.value_store import (
    get_value as vs_get_value,
    get_meta as vs_get_meta,
    set_value as vs_set_value,
    unwrap_facts as vs_unwrap_facts,
)
import logging
from config import LOG_LEVEL, LOG_FILE

Path("logs").mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL,logging.INFO),
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE)
    ]

)
logger=logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent
GOALS_DIR = BASE_DIR / "goals"
INDEX_FILE = GOALS_DIR / "index.json"
TEMPLATE_FILE = BASE_DIR / "configmaster_required_fields.json"
SCHEMA_FILE=BASE_DIR / "configmaster_schema.json"

# -------------------- JSON I/O --------------------
def load_json(path: Path, default):
    if not path.exists():
        return default
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def save_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# -------------------- Utils --------------------
SMALLTALK = {"ok", "okay", "merci", "thx", "cool", "parfait", "bien", "daccord", "d'accord", "ðŸ‘", "âœ…"}


def slugify(s: str) -> str:
    s = (s or "").strip().lower()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r"\s+", "_", s)
    s = re.sub(r"[^a-z0-9_]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "client"


def norm_text(s: str) -> str:
    t = (s or "").strip().lower()
    t = unicodedata.normalize("NFKD", t)
    t = "".join(ch for ch in t if not unicodedata.combining(ch))
    t = t.replace("’", "'")
    t = re.sub(r"\s+", " ", t)
    return t


def parse_client_and_action(msg: str):
    m = norm_text(msg)
    action = "other"
    if any(w in m for w in ["ajouter", "add", "creer", "nouveau", "nouvelle", "nv", "new", "create"]):
        action = "add"
    if any(w in m for w in ["modifier", "modify", "update", "mettre a jour", "changer"]):
        action = "modify"

    client = "client"

    # Prefer bank name when present in initial sentence.
    bank_patterns = [
        r"(?i)\b(?:banque|bank)\s+nomm\S*\s+([A-Za-z0-9\-_']{2,})\b",
        r"(?i)\b(?:banque|bank)\s+sous\s+nom\s+([A-Za-z0-9\-_']{2,})\b",
        r"(?i)\b(?:banque|bank)\s+s['â€™]?appelle\s+([A-Za-z0-9\-_']{2,})\b",
        r"(?i)\b(?:banque|bank)\s+sera\s+([A-Za-z0-9\-_']{2,})\b",
        r"(?i)\b(?:banque|bank)\s+([A-Za-z0-9\-_']{2,})\b",
    ]
    stop_words = {"code", "name", "nomm", "nomme", "nommee", "nommee", "sera", "est", "is", "will", "avec"}
    for pat in bank_patterns:
        mm_bank = re.search(pat, msg)
        if not mm_bank:
            continue
        cand = (mm_bank.group(1) or "").strip().lower()
        if cand and cand not in stop_words and not cand.isdigit():
            client = cand
            break

    mm = re.search(r"\bpour\s+([a-z0-9_ -]+)", m)
    if mm:
        client = mm.group(1).strip().split()[0]
    return client, action


def classify(msg: str) -> str:
    m = norm_text(msg)
    if m in {"exit", "quit", "bye"}:
        return "EXIT"
    if m in SMALLTALK or m in {"bonjour", "salut", "hello", "hi", "hey"}:
        return "SMALLTALK"
    if any(w in m for w in ["liste", "list", "mes demandes", "mes actions", "affiche", "montre"]):
        return "LIST"
    if any(w in m for w in ["continue", "reprendre", "reprends", "continuer"]):
        return "CONTINUE"
    if m.startswith(("modifier", "modify", "update", "nouveau")):
        return "MODIFY_FOLDER"
    if any(
        w in m
        for w in [
            "ajouter",
            "add",
            "creer",
            "create",
            "nouveau",
            "nouvelle",
            "modifier",
            "modify",
            "update",
            "mettre a jour",
            "souhaitons creer",
            "souhaite creer",
            "creer une banque",
            "nouvelle banque",
        ]
    ):
        return "CREATE"
    return "UNKNOWN"


def _is_how_to_create_question(msg: str) -> bool:
    m = norm_text(msg)
    help_markers = ["comment", "how", "?"]
    create_markers = ["ajouter", "add", "creer", "create", "nouveau", "nouvelle"]
    return any(h in m for h in help_markers) and any(c in m for c in create_markers)


def next_client_number(index: dict, client_slug: str) -> int:
    max_n = 0
    for g in index.get("goals", []):
        if g.get("client") == client_slug:
            max_n = max(max_n, int(g.get("client_n", 0)))
    return max_n + 1


def _existing_folders(index: dict) -> set:
    return {g.get("folder") for g in index.get("goals", []) if g.get("folder")}


def make_goal_folder_name(bank_slug: str, index: dict) -> str:
    base = bank_slug or "bank"
    existing = _existing_folders(index)
    if base not in existing:
        return base
    i = 2
    while f"{base}_{i}" in existing:
        i += 1
    return f"{base}_{i}"


def _bank_slug_from_state(state: dict) -> str:
    name = str(vs_get_value((state.get("facts") or {}), "bank.name") or "").strip() if isinstance(state, dict) else ""
    return slugify(name) if name else ""


def migrate_goal_folders_to_bank_slug(index: dict, template_obj: dict):
    if not index.get("goals"):
        return index
    used = _existing_folders(index)
    for g in index.get("goals", []):
        folder = g.get("folder")
        if not folder:
            continue
        state_path = GOALS_DIR / folder / "state.json"
        st = load_json(state_path, {})
        if not st:
            continue
        bank_slug = _bank_slug_from_state(st)
        if not bank_slug:
            continue
        # keep if already correct or is a suffixed variant of bank slug
        if folder == bank_slug or re.fullmatch(rf"{re.escape(bank_slug)}_\d+", folder):
            continue
        # pick a unique target
        target = bank_slug
        if target in used:
            i = 2
            while f"{bank_slug}_{i}" in used:
                i += 1
            target = f"{bank_slug}_{i}"
        try:
            (GOALS_DIR / folder).rename(GOALS_DIR / target)
            g["folder"] = target
            used.add(target)
        except Exception:
            continue
    save_json(INDEX_FILE, index)
    return index


def new_goal_state(goal_id: int, client: str, client_n: int, action: str, goal_text: str, template_obj: dict):
    return {
        "meta": {
            "goal_id": goal_id,
            "client": client,
            "client_n": client_n,
            "action": action,
            "created_at": datetime.now().isoformat(timespec="seconds"),
        },
        "goal": goal_text,
        "facts": copy.deepcopy(template_obj),

        # âœ… NEW (A2)
        "provenance": {},

        "dialog_state": default_dialog_state(),

        "history": [],
        "done": False,
    }


def default_dialog_state() -> dict:
    return {
        "step": "collecting",  # collecting | confirming_conflict | clarifying | completed | paused
        "mode": "normal",  # normal | simplified
        "last_intent": "",
        "last_question": "",
        "last_question_paths": [],
        "missing_fields": [],
        "asked_fields": [],
        "pending_confirmations": [],
        "nlu_fail_count": 0,
        "last_user_message": "",
    }


def ensure_dialog_state(state: dict) -> dict:
    if not isinstance(state, dict):
        return state

    defaults = default_dialog_state()
    current = state.get("dialog_state")
    if not isinstance(current, dict):
        current = {}

    valid_steps = {"collecting", "confirming_conflict", "clarifying", "completed", "paused"}
    valid_modes = {"normal", "simplified"}

    merged = {
        "step": current.get("step") if current.get("step") in valid_steps else defaults["step"],
        "mode": current.get("mode") if current.get("mode") in valid_modes else defaults["mode"],
        "last_intent": str(current.get("last_intent") or defaults["last_intent"]),
        "last_question": str(current.get("last_question") or defaults["last_question"]),
        "last_question_paths": current.get("last_question_paths")
        if isinstance(current.get("last_question_paths"), list)
        else list(defaults["last_question_paths"]),
        "missing_fields": current.get("missing_fields")
        if isinstance(current.get("missing_fields"), list)
        else list(defaults["missing_fields"]),
        "asked_fields": current.get("asked_fields")
        if isinstance(current.get("asked_fields"), list)
        else list(defaults["asked_fields"]),
        "pending_confirmations": current.get("pending_confirmations")
        if isinstance(current.get("pending_confirmations"), list)
        else list(defaults["pending_confirmations"]),
        "nlu_fail_count": int(current.get("nlu_fail_count") or 0),
        "last_user_message": str(current.get("last_user_message") or defaults["last_user_message"]),
    }

    state["dialog_state"] = merged
    return state


def _get_by_path(obj, path: str):
    return vs_get_value(obj, path)


def _set_by_path(obj, path: str, value) -> bool:
    return vs_set_value(obj, path, value, source="user", confidence=1.0)


def _status_summary(state: dict, template_obj: dict, req_paths: list):
    miss = missing_paths(state.get("facts", {}), template_obj, req_paths)
    filled = [p for p in req_paths if p not in miss]
    categories = {}
    for p in filled:
        k = p.split(".")[0]
        categories[k] = categories.get(k, 0) + 1
    top_cats = ", ".join(f"{k}:{v}" for k, v in sorted(categories.items(), key=lambda x: x[0])[:5]) or "aucune"
    miss_short = ", ".join(miss[:5]) if miss else "aucun"
    filled_preview = []
    for p in filled[:3]:
        v = vs_get_value(state.get("facts", {}), p)
        meta = vs_get_meta(state.get("facts", {}), p)
        src = meta.get("source") or "legacy"
        filled_preview.append((p, v, src))
    return len(filled), len(miss), top_cats, miss_short, filled_preview


def _clarification_reply(user_msg: str):
    m = norm_text(user_msg)
    defs = [
        ("code agence", "Le code agence identifie l'agence bancaire.", "Exemple: 0025"),
        ("code banque", "Le code banque identifie la banque.", "Exemple: 90001"),
        ("devise", "La devise est la monnaie du compte.", "Exemple: MAD"),
        ("bin", "Le BIN est le prefixe numerique de la carte.", "Exemple: 445555"),
        ("reseau", "Le reseau est la marque carte acceptee.", "Exemple: VISA"),
        ("region", "La region est la zone administrative de l'agence.", "Exemple: Grand Casablanca"),
    ]
    for key, d, ex in defs:
        if key in m:
            return f"{d} {ex}"
    return "C'est une information de configuration bancaire demandee dans le formulaire. Exemple: code agence 0025."


def _simple_question(last_q: str):
    q = (last_q or "").strip()
    if not q:
        return "Donne juste la valeur demandee, par exemple: code agence 0025."
    return f"En simple: {q}"


def list_goals(index: dict, template_obj: dict, req_path: list):
    goals = index.get("goals", [])
    if not goals:
        print("Agent> tu n'as encore aucune demande enregistrÃ©e.\n")
        return

    print("Agent> voici tous les dossiers:\n")
    for g in goals:
        folder = g.get("folder")
        state_path = GOALS_DIR / folder / "state.json"
        st = load_json(state_path, {})
        if not st:
            print(f"- {folder} (state.json introuvable)")
            continue

        if st.get("done") is True:
            print(f"- {folder} Complet")
            continue

        miss = missing_paths(st.get("facts", {}), template_obj, req_path)
        if not miss:
            print(f"- {folder} complet")
        else:
            print(f"- {folder} incomplet (manque {len(miss)})")
    print("")


def find_last_not_done(index: dict):
    for g in reversed(index.get("goals", [])):
        state_path = GOALS_DIR / g["folder"] / "state.json"
        st = load_json(state_path, {})
        if st and st.get("done") is False:
            return int(g["goal_id"])
    return None


def run_goal(index: dict, goal_id: int, template_obj: dict, req_paths: list,validator):
    match = next((g for g in index.get("goals", []) if int(g["goal_id"]) == goal_id), None)
    if not match:
        print("AGENT> Je ne retrouve pas cette demande. Dis-moi ce que tu veux faire.\n")
        return

    state_path = GOALS_DIR / match["folder"] / "state.json"
    state = load_json(state_path, {})
    
    if not state:
        print("AGENT> Erreur: Ã©tat introuvable.\n")
        return
    ensure_dialog_state(state)
    _normalize_numeric_fields_in_facts(state.get("facts", {}))
    save_json(state_path, state)
    logger.info(f"Run goal | id={goal_id}")
    def auto_fill_tool(facts: dict):
        state["facts"] = facts
        call_tool("autofill", state=state)
        return state["facts"]

    def apply_user_message_to_facts_tool(state_: dict, template_obj_: dict, user_text_: str):
        return call_tool(
            "extract_fields",
            state=state_,
            template_obj=template_obj_,
            user_text=user_text_,
        )

    if state.get("done") is True:
        print("AGENT> Cette demande est deja terminee. Dis-moi ce que tu veux faire maintenant.\n")
        return

    print("\nAGENT> D'accord. On complete le formulaire ensemble.")
    print("AGENT> (Tu peux taper 'exit' pour arreter, ou 'continue' plus tard.)\n")

    while not state.get("done"):
        decision = brain_step(
            state=state,
            template_obj=template_obj,
            req_paths=req_paths,
            user_msg=None,
            dialog_state=state.get("dialog_state"),
            apply_user_message_to_facts=apply_user_message_to_facts_tool,
            apply_single_field_answer=apply_single_field_answer,
            apply_multi_field_answer=apply_multi_field_answer,  
            missing_paths=missing_paths,
            next_question_for_missing=next_question_for_missing,
            next_question_advanced=next_question_advanced,
            auto_fill=auto_fill_tool,
        )
        

        if decision["type"] == "DONE":
            state["done"] = True
            ds = state.get("dialog_state", {})
            ds["step"] = "completed"
            ds["last_question"] = ""
            ds["last_question_paths"] = []
            ds["missing_fields"] = []
            state["history"].append({"agent": "DONE", "user": "all fields filled"})
            save_json(state_path, state)
            
            is_valid,err = validate_facts(validator,state["facts"])
            if not is_valid:
                print(f"AGENT> Donnee invalide: {err}")
            logger.info(f"Goal completed | id={goal_id}")
            print("AGENT> Merci, c'est complet\n")
            return "DONE"

        q = decision["question"]
        ds = state.get("dialog_state", {})
        asked_paths = decision.get("paths", []) or []
        ds["step"] = "collecting"
        ds["last_question"] = q
        ds["last_question_paths"] = list(asked_paths)
        ds["missing_fields"] = missing_paths(state.get("facts", {}), template_obj, req_paths)
        ds["active_menu"] = decision.get("menu")
        ds["asked_fields"] = list(ds.get("asked_fields") or [])
        for p in asked_paths:
            if p not in ds["asked_fields"]:
                ds["asked_fields"].append(p)

        print(f"AGENT> {q}")
        user_msg = input("CLIENT> ").strip()
        ds["last_user_message"] = user_msg

        if user_msg.lower().strip() == "exit":
            ds["step"] = "paused"
            save_json(state_path, state)
            is_valid, err = validate_facts(validator, state["facts"])
            if not is_valid:
                print(f"AGENT> Donnee invalide: {err}")
            print("AGENT> au revoir. Tu pourras reprendre en disant 'continue'.\n")
            return "EXIT_APP"

        if user_msg.lower().strip() == "continue":
            ds["step"] = "paused"
            save_json(state_path, state)
            is_valid, err = validate_facts(validator, state["facts"])
            if not is_valid:
                print(f"AGENT> Donnee invalide: {err}")
            print("AGENT> OK. On met en pause. Dis 'continue' pour reprendre.\n")
            return "PAUSE"

        if not user_msg:
            print("AGENT> Je n'ai pas recu ta reponse. Tu peux preciser ?\n")
            continue
        active_menu = ds.get("active_menu")
        if isinstance(active_menu, dict) and active_menu.get("options"):
            mapped_ok, mapped_val = resolve_menu_answer(active_menu, user_msg)
            if mapped_ok:
                user_msg = mapped_val
                ds["last_user_message"] = user_msg
                state.setdefault("meta", {})["menu_selected_paths"] = list(ds.get("last_question_paths") or [])
            else:
                mnorm = norm_text(user_msg)
                if mnorm not in {"show_status", "ou on en est", "ou en est", "status", "aide", "help", "exit", "continue"}:
                    print("AGENT> Je n'ai pas reconnu ce choix. Reponds par 1/2/3 ou par le texte de l'option.\n")
                    save_json(state_path, state)
                    continue
        intent = detect_intent(user_msg, ds, state.get("facts", {}))
        ds["last_intent"] = intent

        if intent == "show_status":
            filled_n, miss_n, top_cats, miss_short, filled_preview = _status_summary(state, template_obj, req_paths)
            print(f"AGENT> Etat actuel: etape={ds.get('step','collecting')}.")
            print(f"AGENT> Champs remplis: {filled_n} ({top_cats}).")
            for p, v, src in filled_preview[:3]:
                print(f"AGENT> {p}: {v} ({src})")
            print(f"AGENT> Il manque encore ({miss_n}): {miss_short}.\n")
            save_json(state_path, state)
            continue

        if intent in {"greeting", "thanks"}:
            print("AGENT> Avec plaisir. On continue.\n")
            save_json(state_path, state)
            continue

        if intent == "help_or_confusion":
            ds["mode"] = "simplified"
            ds["step"] = "clarifying"
            ds["nlu_fail_count"] = int(ds.get("nlu_fail_count") or 0) + 1
            print("AGENT> Pas de souci. On remplit juste les infos de la banque, une par une.")
            print(f"AGENT> {_simple_question(ds.get('last_question',''))}\n")
            ds["step"] = "collecting"
            save_json(state_path, state)
            continue

        if intent == "clarification_request":
            print(f"AGENT> {_clarification_reply(user_msg)}")
            print(f"AGENT> {_simple_question(ds.get('last_question',''))}\n")
            save_json(state_path, state)
            continue

        if intent == "out_of_scope":
            print("AGENT> Je reste sur la configuration de banque.")
            print("AGENT> Tu peux: 'creer', 'modifier', ou 'ou on en est'.\n")
            save_json(state_path, state)
            continue

        if intent in {"create", "modify", "delete", "resume"}:
            command_only = norm_text(user_msg) in {
                "creer",
                "créer",
                "ajouter",
                "add",
                "modifier",
                "modify",
                "supprimer",
                "delete",
                "continue",
                "reprendre",
                "reprends",
            }
            if command_only:
                print("AGENT> On est deja dans la collecte de ce formulaire. Donne juste la valeur demandee.\n")
                save_json(state_path, state)
                continue

        if intent in {"confirmation_yes", "confirmation_no"}:
            pending = ds.get("pending_confirmations") if isinstance(ds.get("pending_confirmations"), list) else []
            if ds.get("step") == "confirming_conflict" and pending:
                current = pending.pop(0)
                path = current.get("path")
                old_value = current.get("old_value")
                new_value = current.get("new_value")
                new_source = str(current.get("new_source") or "user")
                if intent == "confirmation_yes":
                    ok = vs_set_value(state["facts"], path, new_value, source=new_source, confidence=1.0)
                    if ok:
                        auto_fill_tool(state["facts"])
                        print("AGENT> Merci. J'ai mis a jour la valeur.\n")
                    else:
                        print("AGENT> Je n'ai pas pu appliquer la mise a jour. Peux-tu reformuler ?\n")
                else:
                    print("AGENT> D'accord, je garde l'ancienne valeur.\n")
                if not pending:
                    ds["step"] = "collecting"
                else:
                    nxt = pending[0]
                    ds["step"] = "confirming_conflict"
                    print(f"AGENT> Confirmation: remplacer '{nxt.get('old_value')}' par '{nxt.get('new_value')}' pour {nxt.get('path')} ? (oui/non)\n")
                save_json(state_path, state)
                continue
            print("AGENT> Tu confirmes quoi exactement ?\n")
            save_json(state_path, state)
            continue

        if intent == "correction":
            before_conflicts = len(state.get("conflicts", [])) if isinstance(state.get("conflicts"), list) else 0
            before_facts = json.dumps(state.get("facts", {}), ensure_ascii=False, sort_keys=True)
            apply_user_message_to_facts_tool(state, template_obj, user_msg)
            auto_fill_tool(state["facts"])
            after_facts = json.dumps(state.get("facts", {}), ensure_ascii=False, sort_keys=True)
            conflicts = state.get("conflicts", []) if isinstance(state.get("conflicts"), list) else []
            new_conflicts = conflicts[before_conflicts:] if len(conflicts) >= before_conflicts else []

            if new_conflicts:
                c = new_conflicts[-1]
                pending_item = {
                    "path": c.get("path"),
                    "old_value": c.get("old_value"),
                    "new_value": c.get("new_value"),
                    "old_source": c.get("old_source", "rules"),
                    "new_source": c.get("new_source", "user"),
                    "reason": "user_correction",
                    "created_at": datetime.now().isoformat(timespec="seconds"),
                    "evidence": c.get("evidence", ""),
                }
                ds["pending_confirmations"] = list(ds.get("pending_confirmations") or [])
                ds["pending_confirmations"].append(pending_item)
                ds["step"] = "confirming_conflict"
                print(f"AGENT> Tu veux remplacer '{pending_item['old_value']}' par '{pending_item['new_value']}' pour {pending_item['path']} ? (oui/non)\n")
                save_json(state_path, state)
                continue

            if before_facts != after_facts:
                ds["step"] = "collecting"
                print("AGENT> C'est note, correction appliquee.\n")
                save_json(state_path, state)
                continue

            print("AGENT> Je n'ai pas compris la correction. Exemple: 'non, le code agence est 0025'.\n")
            save_json(state_path, state)
            continue

        if intent == "unknown":
            tokens = re.findall(r"\w+", user_msg or "")
            if "?" in user_msg or len(tokens) >= 3:
                print("AGENT> Je peux t'aider a creer/modifier une banque ou continuer la collecte.")
                print("AGENT> Exemple: 'code agence 0025' ou 'ou on en est'.\n")
        previous_state = copy.deepcopy(state)
        before_facts = json.dumps(state.get("facts", {}), ensure_ascii=False, sort_keys=True)
        state["history"].append({"agent": q, "user": user_msg})

        _ = brain_step(
            state=state,
            template_obj=template_obj,
            req_paths=req_paths,
            user_msg=user_msg,
            dialog_state=state.get("dialog_state"),
            apply_user_message_to_facts=apply_user_message_to_facts_tool,
            apply_single_field_answer=apply_single_field_answer,
            apply_multi_field_answer=apply_multi_field_answer,
            missing_paths=missing_paths,
            next_question_for_missing=next_question_for_missing,
            next_question_advanced=next_question_advanced,
            auto_fill=auto_fill_tool,
        )

        _normalize_numeric_fields_in_facts(state.get("facts", {}))
        is_valid, err = validate_facts(validator, state["facts"])
        if not is_valid:
            print(f"AGENT> Donnee invalide: {err}")
            state = previous_state
            print("AGENT> La valeur a ete refusee. Merci de corriger.\n")
            continue
        state["dialog_state"]["missing_fields"] = missing_paths(state.get("facts", {}), template_obj, req_paths)
        if state["dialog_state"]["step"] != "completed":
            state["dialog_state"]["step"] = "collecting"

        after_facts = json.dumps(state.get("facts", {}), ensure_ascii=False, sort_keys=True)
        extracted_anything = before_facts != after_facts

        if user_msg.lower().strip() in SMALLTALK and not extracted_anything:
            print("Agent> ok tu peux repondre avec la valeur demandee.\n")
            save_json(state_path, state)
            continue

        save_json(state_path, state)
        continue

        
def _normalize_numeric_fields_in_facts(facts: dict):
    if not isinstance(facts, dict):
        return

    fee_keys = {"registration_fee", "periodic_fee", "replacement_fee", "pin_recalculation_fee"}

    def rec(node, parent_key=""):
        if isinstance(node, dict):
            for k, v in list(node.items()):
                if isinstance(v, str):
                    s = v.strip().replace(" ", "").replace(",", ".")
                    if s:
                        if k in fee_keys or k.endswith("_amount"):
                            try:
                                node[k] = float(s)
                                continue
                            except Exception:
                                node[k] = None
                                continue
                        if k.endswith("_count"):
                            try:
                                node[k] = int(float(s))
                                continue
                            except Exception:
                                node[k] = None
                                continue
                if k == "bin" and isinstance(v, str):
                    vv = v.strip()
                    if vv and not re.fullmatch(r"\d{6,8}", vv):
                        node[k] = None
                        continue
                rec(v, k)
        elif isinstance(node, list):
            for item in node:
                rec(item, parent_key)

    rec(facts)


def validate_facts(validator, facts: dict):
    plain = vs_unwrap_facts(facts)
    errors = sorted(validator.iter_errors(plain), key=lambda e: list(e.path))
    if not errors:
        return True, None

    first = errors[0]
    path = ".".join(str(p) for p in first.path)
    return False, f"{path}: {first.message}"

def create_goal(index: dict, msg: str, template_obj: dict):
    client_name, action = parse_client_and_action(msg)
    client_slug = slugify(client_name)
    action_slug = slugify(action)

    goal_id = int(index.get("last_id", 0)) + 1
    client_n = next_client_number(index, client_slug)

    identity = extract_bank_identity_from_text(msg, template_obj)
    bank_slug = slugify(identity.get("name", "")) if identity else ""
    folder = make_goal_folder_name(bank_slug or client_slug, index)
    goal_dir = GOALS_DIR / folder
    (goal_dir / "artifacts").mkdir(parents=True, exist_ok=True)

    state = new_goal_state(goal_id, client_slug, client_n, action_slug, msg, template_obj)

    call_tool("extract_fields", state=state, template_obj=template_obj, user_text=msg)
    call_tool("autofill", state=state)

    # If bank name is now known, align folder name to bank slug.
    new_bank_slug = _bank_slug_from_state(state)
    if new_bank_slug:
        existing = _existing_folders(index) - {folder}
        target = new_bank_slug
        if target in existing:
            i = 2
            while f"{new_bank_slug}_{i}" in existing:
                i += 1
            target = f"{new_bank_slug}_{i}"
        if target != folder:
            try:
                (GOALS_DIR / folder).rename(GOALS_DIR / target)
                folder = target
                goal_dir = GOALS_DIR / folder
            except Exception:
                pass

    save_json(goal_dir / "state.json", state)

    index["last_id"] = goal_id
    index["goals"].append(
        {
            "goal_id": goal_id,
            "client": client_slug,
            "client_n": client_n,
            "action": action_slug,
            "folder": folder,
        }
    )
    save_json(INDEX_FILE, index)
    logger.info(f"Goal created | id={goal_id} | client={client_slug} | action={action_slug}")
    return goal_id


def _bank_identity_from_state(state: dict):
    facts = (state.get("facts") or {}) if isinstance(state, dict) else {}
    name = str(vs_get_value(facts, "bank.name") or "").strip().upper()
    code = str(vs_get_value(facts, "bank.bank_code") or "").strip().upper()
    country = str(vs_get_value(facts, "bank.country") or "").strip().upper()
    if not name or not code or not country:
        return None
    return {"name": name, "code": code, "country": country}


def extract_bank_identity_from_text(msg: str, template_obj: dict):
    temp_state = {
        "facts": copy.deepcopy(template_obj),
        "provenance": {},
        "meta": {},
        "history": [],
        "done": False,
    }
    call_tool("extract_fields", state=temp_state, template_obj=template_obj, user_text=msg)
    call_tool("autofill", state=temp_state)
    return _bank_identity_from_state(temp_state)


def find_existing_goal_by_bank_identity(index: dict, identity: dict):
    if not identity:
        return None
    for g in reversed(index.get("goals", [])):
        folder = g.get("folder")
        if not folder:
            continue
        st = load_json(GOALS_DIR / folder / "state.json", {})
        st_id = _bank_identity_from_state(st)
        if not st_id:
            continue
        if (
            st_id["name"] == identity["name"]
            and st_id["code"] == identity["code"]
            and st_id["country"] == identity["country"]
        ):
            return g
    return None


def modify_goal_folder(index: dict, target_folder: str, template_obj: dict):
    match = next((g for g in index.get("goals", []) if g.get("folder") == target_folder), None)
    if not match:
        print("AGENT> Dossier introuvable. Tape 'liste' pour voir les dossiers.\n")
        return

    state_path = GOALS_DIR / target_folder / "state.json"
    state = load_json(state_path, {})
    if not state:
        print("AGENT> state.json introuvable.\n")
        return

    print(f"AGENT> D'accord, nous allons modifier ce dossier: {target_folder}")
    print("AGENT> Champs disponibles: nom banque, pays, devise, code banque, ressources, nom agence, code agence, ville, code ville, region, code region")
    print("AGENT> Tape 'stop' pour sortir.\n")

    aliases = {
        "nom": "bank.name",
        "nom banque": "bank.name",
        "pays": "bank.country",
        "devise": "bank.currency",
        "code": "bank.bank_code",
        "code banque": "bank.bank_code",
        "ressources": "bank.resources",
        "nom agence": "bank.agencies.0.agency_name",
        "code agence": "bank.agencies.0.agency_code",
        "ville": "bank.agencies.0.city",
        "code ville": "bank.agencies.0.city_code",
        "region": "bank.agencies.0.region",
        "code region": "bank.agencies.0.region_code",
    }

    while True:
        field = input("CHAMP> ").strip()
        if field.lower() in {"stop", "exit", "quit"}:
            save_json(state_path, state)
            print("AGENT> OK. TerminÃƒÂ©.\n")
            break

        path = aliases.get(field.lower())
        if not path:
            print("AGENT> Merci. Choisis un champ de la liste proposÃ©e.\n")
            continue
        new_val = input("VALEUR> ").strip()

        ok = apply_single_field_answer(state, template_obj, path, new_val)
        if ok:
            auto_fill(state["facts"])
            save_json(state_path, state)
            print("AGENT> Merci, c'est bien mis ÃƒÂ  jour.\n")
        else:
            print("AGENT> Je n'ai pas pu valider cette valeur. Peux-tu la reformuler ?\n")


def main():
    GOALS_DIR.mkdir(parents=True, exist_ok=True)
    index = load_json(INDEX_FILE, {"last_id": 0, "goals": []})

    template_obj = load_template(TEMPLATE_FILE)
    schema_obj=load_json(SCHEMA_FILE,{})
    validator=Draft202012Validator(schema_obj)
    req_paths = build_required_paths(template_obj)

    index = migrate_goal_folders_to_bank_slug(index, template_obj)

    print(" Bonjour. Decris ce que tu veux faire.")
    print("Tu peux dire: 'creer', 'modifier', 'continue' ou 'liste'. Tape 'exit' pour quitter.\n")

    while True:
        msg = input("CLIENT> ").strip()
        intent = classify(msg)

        if intent == "EXIT":
            print("AGENT> byeee")
            break

        index = load_json(INDEX_FILE, {"last_id": 0, "goals": []})

        if intent == "SMALLTALK":
            print("AGENT> Dis-moi une action: creer, modifier, continue ou liste.\n")
            continue

        if intent == "LIST":
            list_goals(index, template_obj, req_paths)
            continue

        if intent == "CONTINUE":
            parts = msg.split()
            target_folder = parts[1] if len(parts) > 1 else None

            if target_folder:
                match = next((g for g in index["goals"] if g["folder"] == target_folder), None)
                if not match:
                    print("Agent> Dossier introuvable.\n")
                    continue
                gid = match["goal_id"]
            else:
                gid = find_last_not_done(index)

            if gid is None:
                print("AGENT> Je n'ai rien en cours. Dis-moi ce que tu veux faire maintenant.\n")
                continue

            match = next((g for g in index.get("goals", []) if int(g["goal_id"]) == gid), None)
            if not match:
                print("Agent> Erreur: demande introuvable.\n")
                continue

            state_path = GOALS_DIR / match["folder"] / "state.json"
            state = load_json(state_path, {})
            ensure_dialog_state(state)
            miss = missing_paths(state.get("facts", {}), template_obj, req_paths)

            if not miss:
                print("Agent> toutes les donnees sont completes.\n")
            else:
                print("Agent> il manque encore:")
                print(humain_missing_list(miss))
                print("")

            print("AGENT> OK, je reprends la ou on s'est arrete.\n")
            status = run_goal(index, gid, template_obj, req_paths,validator)
            if status == "EXIT_APP":
                break
            continue

        if intent == "MODIFY_FOLDER":
            parts = msg.split(maxsplit=1)
            target_folder = parts[1].strip() if len(parts) > 1 else ""
            if not target_folder:
                print("AGENT> Donne le nom du dossier.")
                target_folder = input("DOSSIER> ").strip()

            match = next((g for g in index.get("goals", []) if g.get("folder") == target_folder), None)
            if not match:
                print("AGENT> Dossier introuvable. Tape 'liste' pour voir les dossiers.\n")
                continue

            state_path = GOALS_DIR / target_folder / "state.json"
            state = load_json(state_path, {})
            if not state:
                print("AGENT> state.json introuvable.\n")
                continue

            print(f"AGENT> Mode modification: {target_folder}")
            print("AGENT> Champs: nom, pays, devise, code, ressources")
            print("AGENT> Ou path exact: bank.name, bank.country, bank.currency, bank.bank_code, bank.resources")
            print("AGENT> Tape 'stop' pour sortir.\n")

            aliases = {
                "nom": "bank.name",
                "pays": "bank.country",
                "devise": "bank.currency",
                "code": "bank.bank_code",
                "ressources": "bank.resources",
            }

            while True:
                field = input("CHAMP> ").strip()
                if field.lower() in {"stop", "exit", "quit"}:
                    save_json(state_path, state)
                    print("AGENT> OK. TerminÃ©.\n")
                    break

                path = aliases.get(field.lower(), field)
                new_val = input("VALEUR> ").strip()

                ok = apply_single_field_answer(state, template_obj, path, new_val)
                if ok:
                    auto_fill(state["facts"])
                    save_json(state_path, state)
                    print("AGENT> Mis Ã  jour dans le mÃªme state.json.\n")
                else:
                    print("AGENT> Valeur refusÃ©e.\n")

            continue

        if intent == "UNKNOWN":
            print("AGENT> Action non reconnue. Utilise: creer, modifier, continue ou liste.\n")
            continue

        if intent == "CREATE":
            if _is_how_to_create_question(msg):
                print("AGENT> Pour ajouter une banque, envoie une phrase avec nom + pays + devise + code.")
                print("AGENT> Exemple: 'Creer Atlas Bank au Maroc devise MAD code 90001'.")
                msg = input("CLIENT> ").strip()
                if not msg:
                    print("AGENT> D'accord. Recommence quand tu veux.\n")
                    continue

            if msg.lower().strip() in {"creer", "créer", "ajouter", "add", "nouveau", "new", "nv"}:
                print("AGENT> OK. Decris la banque en une phrase (nom + pays + devise si possible).")
                msg = input("CLIENT> ").strip()
                if not msg:
                    print("AGENT> D'accord. Recommence quand tu veux.\n")
                    continue

            identity = extract_bank_identity_from_text(msg, template_obj)
            existing = find_existing_goal_by_bank_identity(index, identity)
            if existing:
                folder = existing.get("folder")
                print(f"AGENT> Ce fichier existe deja: '{folder}' (meme nom, meme code et meme pays).")
                ans = input("AGENT> Est-ce que vous voulez le modifier ? (oui/non)\nCLIENT> ").strip().lower()
                if ans in {"oui", "o", "yes", "y"}:
                    print("AGENT> Vous pouvez modifier: nom banque, pays, devise, code banque, ressources, nom agence, code agence, ville, code ville, region, code region.\n")
                    modify_goal_folder(index, folder, template_obj)
                    continue
                print("AGENT> D'accord, je cree un nouveau fichier.\n")

            print("AGENT> D'accord. On commence.\n")
            gid = create_goal(index, msg, template_obj)

            index = load_json(INDEX_FILE, {"last_id": 0, "goals": []})
            status = run_goal(index, gid, template_obj, req_paths,validator)
            if status == "EXIT_APP":
                break
            continue


if __name__ == "__main__":
    main()

