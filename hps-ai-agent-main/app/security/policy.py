# Champs jamais envoyés au LLM
SENSITIVE_FIELDS = {
    "client.ice",
    "hps.internal_code",
    # ajoute ici d'autres champs sensibles
}

def is_sensitive_field(field: str) -> bool:
    return field in SENSITIVE_FIELDS
