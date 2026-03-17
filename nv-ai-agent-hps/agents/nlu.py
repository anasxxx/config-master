import re
import unicodedata
from typing import Dict, Any


INTENTS = {
    # business
    "create",
    "modify",
    "delete",
    "resume",
    "show_status",
    # conversational
    "greeting",
    "thanks",
    "help_or_confusion",
    "clarification_request",
    "correction",
    "confirmation_yes",
    "confirmation_no",
    "out_of_scope",
    "unknown",
}


def _norm_text(s: str) -> str:
    t = (s or "").strip().lower()
    t = unicodedata.normalize("NFKD", t)
    t = "".join(ch for ch in t if not unicodedata.combining(ch))
    t = t.replace("’", "'")
    t = re.sub(r"\s+", " ", t)
    return t


def _looks_like_business_payload(m: str) -> bool:
    if not m:
        return False

    business_cues = [
        "banque",
        "bank",
        "agence",
        "agency",
        "devise",
        "currency",
        "code banque",
        "bank code",
        "code agence",
        "bin",
        "visa",
        "mastercard",
        "limit",
        "plafond",
        "maroc",
        "france",
        "usa",
        "mad",
        "eur",
        "usd",
    ]
    if any(c in m for c in business_cues):
        return True

    # Numbers are often business values: codes, BIN, limits.
    if re.search(r"\b\d{3,}\b", m):
        return True

    return False


def _unwrap_value(v: Any) -> Any:
    if isinstance(v, dict) and "value" in v:
        return v.get("value")
    return v


def _get_by_path(obj: Any, path: str):
    cur = obj
    for part in (path or "").split("."):
        if part.isdigit():
            idx = int(part)
            if not isinstance(cur, list) or idx >= len(cur):
                return None
            cur = cur[idx]
        else:
            if not isinstance(cur, dict) or part not in cur:
                return None
            cur = cur[part]
    return _unwrap_value(cur)


def _is_missing(v: Any) -> bool:
    if v is None:
        return True
    if isinstance(v, str):
        return v.strip().lower() in {"", "none", "null", "n/a", "na", "unknown"}
    if isinstance(v, list):
        return len(v) == 0
    if isinstance(v, dict):
        return len(v) == 0
    return False


def _count_core_identity_filled(facts: Dict[str, Any]) -> int:
    core_paths = ["bank.name", "bank.country", "bank.currency", "bank.bank_code"]
    n = 0
    for p in core_paths:
        if not _is_missing(_get_by_path(facts or {}, p)):
            n += 1
    return n


def _looks_like_question(text: str) -> bool:
    t = text or ""
    if "?" in t:
        return True
    q_tokens = [
        "pourquoi",
        "comment",
        "c est quoi",
        "c'est quoi",
        "what",
        "why",
        "how",
        "which",
        "quel",
        "quelle",
    ]
    low = _norm_text(t)
    return any(q in low for q in q_tokens)


def detect_intent(user_text: str, dialog_state: Dict[str, Any], facts: Dict[str, Any]) -> str:
    """
    Intent router central (règles + contexte).
    Priorité:
    1) contexte (confirming_conflict => oui/non)
    2) règles robustes
    3) unknown
    """
    m = _norm_text(user_text)
    ds = dialog_state if isinstance(dialog_state, dict) else {}

    yes_tokens = {"oui", "o", "yes", "y", "ok", "daccord", "d'accord", "confirme"}
    no_tokens = {"non", "n", "no", "annule", "annuler", "garde l ancienne", "garde l'ancienne"}
    if ds.get("step") == "confirming_conflict" and isinstance(ds.get("pending_confirmations"), list) and ds.get("pending_confirmations"):
        if m in yes_tokens:
            return "confirmation_yes"
        if m in no_tokens:
            return "confirmation_no"

    if any(x in m for x in ["ou on en est", "ou en est", "ou on est", "resume", "resumer", "qu est ce qui manque", "qu'est ce qui manque", "status", "etat", "etat actuel", "manque"]):
        return "show_status"

    has_payload = _looks_like_business_payload(m)

    if any(x in m for x in ["bonjour", "salut", "hello", "hey", "bonsoir"]) and not has_payload:
        return "greeting"
    if any(x in m for x in ["merci", "thanks", "thank you", "super merci"]) and not has_payload:
        return "thanks"

    if any(x in m for x in ["je comprends pas", "je ne comprends pas", "j ai pas compris", "aide", "help", "explique", "j suis perdu", "je suis perdu"]):
        return "help_or_confusion"

    if any(x in m for x in ["c est quoi", "c'est quoi", "ca veut dire", "qu est ce que", "qu'est-ce que", "definition de", "definis", "c quoi"]):
        return "clarification_request"

    if m.startswith("non ") or m.startswith("non,") or m.startswith("c est pas") or m.startswith("c'est pas") or m.startswith("corrige") or m.startswith("plutot") or m.startswith("plutot "):
        return "correction"
    if any(x in m for x in ["corrige", "correction", "change", "remplace"]):
        return "correction"

    if m in yes_tokens:
        return "confirmation_yes"
    if m in no_tokens:
        return "confirmation_no"

    if any(x in m for x in ["meteo", "temperature", "temps a", "news", "sport", "match", "politique", "blague", "recette", "bitcoin", "bourse", "film", "musique"]):
        return "out_of_scope"

    if any(x in m for x in ["creer", "create", "ajouter", "add", "nouveau", "nouvelle"]):
        return "create"
    if any(x in m for x in ["modifier", "modify", "mettre a jour", "update", "changer"]):
        return "modify"
    if any(x in m for x in ["supprimer", "delete", "effacer"]):
        return "delete"
    if any(x in m for x in ["continue", "reprends", "reprendre", "on continue"]):
        return "resume"

    # Implicit intent inference:
    # user can provide business payload without explicit verbs.
    if has_payload:
        # If this is likely a question, keep conversational behavior.
        if _looks_like_question(user_text):
            return "clarification_request"

        # During active field collection, payload-like text is often just an answer.
        if isinstance(ds.get("last_question_paths"), list) and ds.get("last_question_paths"):
            return "unknown"

        # No core identity yet -> likely a creation request.
        core_filled = _count_core_identity_filled(facts if isinstance(facts, dict) else {})
        if core_filled == 0:
            return "create"

        # Existing entity with new payload -> likely modification.
        return "modify"

    return "unknown"
