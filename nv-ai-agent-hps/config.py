# Activer/désactiver l’usage du LLM
USE_LLM = False

# Champs que le LLM a le droit de remplir (sécurité)
ALLOWED_LLM_FIELDS = {
    "bank.name",
    "bank.country",
    "bank.currency",
    "bank.bank_code",
    "bank.resources",
}


LLM_URL = "http://localhost:11434"

LLM_MODEL = "llama3.2:3b"
# Seuil de confiance minimum pour accepter une extraction LLM
LLM_MIN_CONF = 0.70