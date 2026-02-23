from config import LLM_MIN_CONF, ALLOWED_LLM_FIELDS


def apply_llm_gates(llm_output: dict):
    """
    Nettoie la sortie LLM de façon robuste.
    - ignore tout champ non allowlist
    - ignore si data n'est pas un dict (None, string, etc.)
    - ignore si value vide
    - ignore si confidence absente/None ou < seuil
    """
    clean = {}

    if not isinstance(llm_output, dict):
        return clean

    fields = llm_output.get("fields", {})
    if not isinstance(fields, dict):
        return clean

    for name, data in fields.items():

        # allowlist
        if name not in ALLOWED_LLM_FIELDS:
            continue

        # si le modèle renvoie None / string / autre → on ignore
        if not isinstance(data, dict):
            continue

        value = data.get("value")
        confidence = data.get("confidence")

        # valeur vide
        if value is None:
            continue
        if isinstance(value, str) and value.strip() == "":
            continue

        # confidence obligatoire
        if confidence is None:
            continue

        # certains modèles renvoient confidence en string
        try:
            confidence = float(confidence)
        except Exception:
            continue

        if confidence < LLM_MIN_CONF:
            continue

        clean[name] = value

    return clean