import requests
import json
from config import LLM_URL, LLM_MODEL


def extract_with_llm(text: str, allowed_fields: set):
    prompt = f"""
Tu es un extracteur de données. Réponds UNIQUEMENT en JSON valide.

Champs autorisés:
{sorted(list(allowed_fields))}

Règles strictes:
- Pour chaque champ que tu extrais, tu dois renvoyer un objet {{"value": ..., "confidence": ...}}
- confidence est un nombre entre 0 et 1 (jamais null)
- Si tu n'es pas sûr: value = null et confidence = 0
- Ne rajoute aucun texte hors JSON.

Format EXACT:
{{
  "fields": {{
    "bank.name": {{"value": "HPS", "confidence": 0.9}},
    "bank.country": {{"value": "Mali", "confidence": 0.9}},
    "bank.currency": {{"value": null, "confidence": 0}}
  }}
}}

Texte:
{text}
"""

    payload = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "stream": False
    }

    response = requests.post(LLM_URL, json=payload)
    content = response.json()["message"]["content"]

    try:
        return json.loads(content)
    except:
        return {}