import json, re, requests

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.2:3b"

def ollama_json(system_text: str, user_obj: dict) -> dict:
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_text},
            {"role": "user", "content": json.dumps(user_obj, ensure_ascii=False)},
        ],
        "stream": False,
    }
    r = requests.post(OLLAMA_URL, json=payload, timeout=60)
    r.raise_for_status()
    content = r.json()["message"]["content"]
    m = re.search(r"\{.*\}", content, flags=re.DOTALL)
    if not m:
        raise ValueError("LLM n'a pas renvoyé de JSON.")
    return json.loads(m.group(0))

def extract_bank_facts(text: str) -> dict:
    system = (
        "Extract bank.name, bank.country, bank.currency from the text.\n"
        "Return ONLY JSON.\n"
        "bank.name must be short (only name), not full sentence.\n"
        "bank.currency must be code (MAD/EUR/USD).\n"
        "Example: la banque s'appelle cih au maroc en mad\n"
        '{"facts":{"bank.name":"CIH","bank.country":"Maroc","bank.currency":"MAD"}}'
    )
    out = ollama_json(system, {"text": text})
    facts = out.get("facts", {})
    return facts if isinstance(facts, dict) else {}
