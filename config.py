# config.py

# Activer/désactiver l’usage du LLM
USE_LLM = True

LLM_URL = "http://localhost:11434/api/chat"
LLM_MODEL = "llama3.2:3b"

# Seuil de confiance minimum pour accepter une extraction LLM
LLM_MIN_CONF = 0.70

# Liste blanche des champs que le LLM a le droit de renvoyer.
# Si vide ou None, tous les champs du template sont autorisés.
ALLOWED_LLM_FIELDS = [
    "bank.name",
    "bank.country",
    "bank.currency",
    "bank.bank_code",
    "bank.agencies.0.agency_name",
    "bank.agencies.0.agency_code",
    "bank.agencies.0.city",
    "bank.agencies.0.region",
    "cards.0.card_info.network",
    "cards.0.card_info.product_type",
    "cards.0.card_info.plastic_type",
    "cards.0.card_info.card_description",
    "cards.0.services.enabled",
    "cards.0.limits.selected_limit_types",
    "cards.0.limits.by_type.DEFAULT.domestic.daily_amount",
    "cards.0.limits.by_type.DEFAULT.international.daily_amount",
]

# ✅ NEW: robustesse réseau
LLM_TIMEOUT_S = 20
LLM_MAX_ATTEMPTS = 3
LLM_RETRY_BACKOFF_S = 1.2  # 1.2s, puis 2.4s, etc.
# Compat legacy (deprecated): garder pour d'anciens imports.
LLM_MAX_RETRIES = max(0, LLM_MAX_ATTEMPTS - 1)
LLM_DEBUG = False          # True si tu veux voir les erreurs LLM
LOG_LEVEL="INFO"
LOG_FILE="logs/agent.log"
