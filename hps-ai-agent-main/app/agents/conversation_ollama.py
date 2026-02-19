import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2:3b"

FIELD_HINTS = {
    "client.name": "Nom complet du client (texte).",
    "client.ice": "Identifiant ICE (texte/numérique).",
    "client.country": "Code pays (ex: MA, FR).",
    "project.type": "Type de projet (ex: ONBOARDING, MIGRATION, SUPPORT).",
    "project.environment": "Environnement (DEV, TEST, PROD).",
}

def ask_ollama_for_field(field: str) -> str:
    hint = FIELD_HINTS.get(field, "Réponds avec une valeur simple.")
    prompt = (
        f"Tu es un assistant de collecte de données.\n"
        f"Je dois remplir le champ: {field}\n"
        f"Contrainte: {hint}\n"
        f"Réponds uniquement par la valeur, sans phrase.\n"
        f"Valeur:"
    )

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    }

    r = requests.post(OLLAMA_URL, json=payload, timeout=60)
    r.raise_for_status()
    text = r.json().get("response", "")
    return text.strip()
