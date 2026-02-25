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
)

from agents.conversation_agent import (
    apply_user_message_to_facts,
    apply_single_field_answer,
    apply_multi_field_answer,
)
import logging
from config import LOG_LEVEL, LOG_FILE

Path("logs").mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL,logging.INFO),
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
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
    s = s.strip().lower()
    s = re.sub(r"\s+", "_", s)
    s = re.sub(r"[^a-z0-9_]+", "", s)
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


def next_client_number(index: dict, client_slug: str) -> int:
    max_n = 0
    for g in index.get("goals", []):
        if g.get("client") == client_slug:
            max_n = max(max_n, int(g.get("client_n", 0)))
    return max_n + 1


def make_goal_folder_name(client_slug: str, client_n: int, action: str) -> str:
    return f"{client_slug}_{client_n:03d}_{action}"


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

        "history": [],
        "done": False,
    }


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
        print("AGENT> Cette demande est dÃ©jÃ  terminÃ©e. Dis-moi ce que tu veux faire maintenant.\n")
        return

    print("\nAGENT> Dâ€™accord. On complÃ¨te le formulaire ensemble.")
    print("AGENT> (Tu peux taper 'exit' pour arrÃªter, ou 'continue' plus tard.)\n")

    while not state.get("done"):
        decision = brain_step(
            state=state,
            template_obj=template_obj,
            req_paths=req_paths,
            user_msg=None,
            apply_user_message_to_facts=apply_user_message_to_facts_tool,
            apply_single_field_answer=apply_single_field_answer,
            apply_multi_field_answer=apply_multi_field_answer,  
            missing_paths=missing_paths,
            next_question_for_missing=next_question_for_missing,
            auto_fill=auto_fill_tool,
        )
        

        if decision["type"] == "DONE":
            state["done"] = True
            state["history"].append({"agent": "DONE", "user": "all fields filled"})
            save_json(state_path, state)
            
            is_valid,err = validate_facts(validator,state["facts"])
            if not is_valid:
                print(f"AGENT> âš  DonnÃ©e invalide: {err}")
            logger.info(f"Goal completed | id={goal_id}")
            print("AGENT> Merci, câ€™est complet\n")
            return "DONE"

        q = decision["question"]
        print(f"AGENT> {q}")
        user_msg = input("CLIENT> ").strip()

        if user_msg.lower().strip() == "exit":
            save_json(state_path, state)
            is_valid, err = validate_facts(validator, state["facts"])
            if not is_valid:
                print(f"AGENT> âš  DonnÃ©e invalide: {err}")
            print("AGENT> au revoir. Tu pourras reprendre en disant 'continue'.\n")
            return "EXIT_APP"

        if user_msg.lower().strip() == "continue":
            save_json(state_path, state)
            is_valid, err = validate_facts(validator, state["facts"])
            if not is_valid:
                print(f"AGENT> âš  DonnÃ©e invalide: {err}")
            print("AGENT> OK. On met en pause. Dis 'continue' pour reprendre.\n")
            return "PAUSE"

        if not user_msg:
            print("AGENT> Je nâ€™ai pas reÃ§u ta rÃ©ponse. Tu peux prÃ©ciser ?\n")
            continue
        previous_state = copy.deepcopy(state)
        before_facts = json.dumps(state.get("facts", {}), ensure_ascii=False, sort_keys=True)
        state["history"].append({"agent": q, "user": user_msg})

        _ = brain_step(
            state=state,
            template_obj=template_obj,
            req_paths=req_paths,
            user_msg=user_msg,
            apply_user_message_to_facts=apply_user_message_to_facts_tool,
            apply_single_field_answer=apply_single_field_answer,
            apply_multi_field_answer=apply_multi_field_answer,
            missing_paths=missing_paths,
            next_question_for_missing=next_question_for_missing,
            auto_fill=auto_fill_tool,
        )

        _normalize_numeric_fields_in_facts(state.get("facts", {}))
        is_valid, err = validate_facts(validator, state["facts"])
        if not is_valid:
            print(f"AGENT> âš  DonnÃ©e invalide: {err}")
            state = previous_state
            print("AGENT> La valeur a Ã©tÃ© refusÃ©e. Merci de corriger.\n")
            continue

        after_facts = json.dumps(state.get("facts", {}), ensure_ascii=False, sort_keys=True)
        extracted_anything = before_facts != after_facts

        if user_msg.lower().strip() in SMALLTALK and not extracted_anything:
            print("Agent> ok tu peux repondre avec la valeur demandÃ©e.\n")
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
    errors = sorted(validator.iter_errors(facts), key=lambda e: list(e.path))
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

    folder = make_goal_folder_name(client_slug, client_n, action_slug)
    goal_dir = GOALS_DIR / folder
    (goal_dir / "artifacts").mkdir(parents=True, exist_ok=True)

    state = new_goal_state(goal_id, client_slug, client_n, action_slug, msg, template_obj)

    call_tool("extract_fields", state=state, template_obj=template_obj, user_text=msg)
    call_tool("autofill", state=state)

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
    bank = (state.get("facts") or {}).get("bank", {}) if isinstance(state, dict) else {}
    name = str(bank.get("name") or "").strip().upper()
    code = str(bank.get("bank_code") or "").strip().upper()
    country = str(bank.get("country") or "").strip().upper()
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

    print(" Bonjour. DÃ©cris ce que tu veux faire.")
    print("Tu peux dire: 'crÃ©er', 'modifier', 'continue' ou 'liste'. Tape 'exit' pour quitter.\n")

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
                print("AGENT> Je nâ€™ai rien en cours. Dis-moi ce que tu veux faire maintenant.\n")
                continue

            match = next((g for g in index.get("goals", []) if int(g["goal_id"]) == gid), None)
            if not match:
                print("Agent> Erreur: demande introuvable.\n")
                continue

            state_path = GOALS_DIR / match["folder"] / "state.json"
            state = load_json(state_path, {})
            miss = missing_paths(state.get("facts", {}), template_obj, req_paths)

            if not miss:
                print("Agent> toutes les donnÃ©es sont complÃ¨tes.\n")
            else:
                print("Agent> il manque encore:")
                print(humain_missing_list(miss))
                print("")

            print("AGENT> OK, je reprends lÃ  oÃ¹ on sâ€™est arrÃªtÃ©.\n")
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
            if msg.lower().strip() in {"creer", "crÃ©er", "ajouter", "add", "nouveau", "new", "nv"}:
                print("AGENT> OK. DÃ©cris la banque en une phrase (nom + pays + devise si possible).")
                msg = input("CLIENT> ").strip()
                if not msg:
                    print("AGENT> Dâ€™accord. Recommence quand tu veux.\n")
                    continue

            identity = extract_bank_identity_from_text(msg, template_obj)
            existing = find_existing_goal_by_bank_identity(index, identity)
            if existing:
                folder = existing.get("folder")
                print(f"AGENT> Ce fichier existe dÃ©jÃ : '{folder}' (mÃªme nom, mÃªme code et mÃªme pays).")
                ans = input("AGENT> Est-ce que vous voulez le modifier ? (oui/non)\nCLIENT> ").strip().lower()
                if ans in {"oui", "o", "yes", "y"}:
                    print("AGENT> Vous pouvez modifier: nom banque, pays, devise, code banque, ressources, nom agence, code agence, ville, code ville, region, code region.\n")
                    modify_goal_folder(index, folder, template_obj)
                    continue
                print("AGENT> D'accord, je crÃ©e un nouveau fichier.\n")

            print("AGENT> Dâ€™accord. On commence.\n")
            gid = create_goal(index, msg, template_obj)

            index = load_json(INDEX_FILE, {"last_id": 0, "goals": []})
            status = run_goal(index, gid, template_obj, req_paths,validator)
            if status == "EXIT_APP":
                break
            continue


if __name__ == "__main__":
    main()

