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

    if any(x in m for x in ["bonjour", "salut", "hello", "hey", "bonsoir"]):
        return "greeting"
    if any(x in m for x in ["merci", "thanks", "thank you", "super merci"]):
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

    return "unknown"
