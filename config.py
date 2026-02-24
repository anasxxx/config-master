# config.py

# Activer/désactiver l’usage du LLM
USE_LLM = True

LLM_URL = "http://localhost:11434/api/chat"
LLM_MODEL = "llama3.2:3b"

# Seuil de confiance minimum pour accepter une extraction LLM
LLM_MIN_CONF = 0.70

# ✅ NEW: robustesse réseau
LLM_TIMEOUT_S = 20
LLM_MAX_RETRIES = 2
LLM_RETRY_BACKOFF_S = 1.2  # 1.2s, puis 2.4s, etc.
LLM_DEBUG = False          # True si tu veux voir les erreurs LLM
LOG_LEVEL="INFO"
LOG_FILE="logs/agent.log"