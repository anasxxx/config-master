# agents/llm_gates.py
from config import LLM_MIN_CONF
from agents.prompts import PROMPT_LLM_GATES
# PROMPT_LLM_GATES est la spécification du comportement des gates.
# Les gates restent déterministes (code-only) pour la sécurité.
def apply_llm_gates(llm_output: dict, allowed_fields: set):
    """
    Nettoie la sortie LLM:
    - ignore tout champ non autorisé
    - ignore value vide
    - ignore confidence < LLM_MIN_CONF
    """
    clean = {}

    if not isinstance(llm_output, dict):
        return clean

    fields = llm_output.get("fields", {})
    if not isinstance(fields, dict):
        return clean

    for name, data in fields.items():
        if name not in allowed_fields:
            continue
        if not isinstance(data, dict):
            continue

        value = data.get("value")
        confidence = data.get("confidence")

        if value is None:
            continue
        if isinstance(value, str) and value.strip() == "":
            continue

        try:
            confidence = float(confidence)
        except Exception:
            continue

        if confidence < LLM_MIN_CONF:
            continue

        clean[name] = value

    return clean