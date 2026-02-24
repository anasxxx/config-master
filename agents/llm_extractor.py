import time
import requests
import json
import re
from typing import Iterable, Optional
from config import (LLM_URL, LLM_MODEL ,LLM_TIMEOUT_S,LLM_MAX_RETRIES,LLM_RETRY_BACKOFF_S,LLM_DEBUG,)
from agents.prompts import GLOBAL_POLICY, PROMPT_EXTRACTION_AGENT
MAX_FIELDS_IN_PROMPT = 1200  # augmente si ton modèle supporte; 800-1500 ok


def _clean_json(content: str) -> str:
    content = (content or "").strip()
    if content.startswith("```"):
        content = re.sub(r"^```[a-zA-Z]*", "", content).strip()
        if content.endswith("```"):
            content = content[:-3].strip()
    return content


def _safe_load_json(content: str):
    try:
        return json.loads(content)
    except Exception:
        # Fallback: extract first JSON object if model added prose around it.
        m = re.search(r"\{.*\}", content or "", flags=re.DOTALL)
        if not m:
            return {}
        try:
            return json.loads(m.group(0))
        except Exception:
            return {}


def _normalize_output(data: dict, allowed_fields_set: set):
    if not isinstance(data, dict) or "fields" not in data or not isinstance(data["fields"], dict):
        return {"fields": {}}

    cleaned = {}
    for path, meta in data["fields"].items():
        if path not in allowed_fields_set or not isinstance(meta, dict):
            continue

        value = meta.get("value")
        conf = meta.get("confidence", 0)

        try:
            conf = float(conf)
        except Exception:
            conf = 0.0

        conf = max(0.0, min(conf, 1.0))
        cleaned[path] = {"value": value, "confidence": conf}

    return {"fields": cleaned}



def _post_llm(payload: dict) -> str:
    """
    Appelle le LLM avec retry + backoff.
    Retourne le champ "content" (string). Sinon string vide.
    """
    last_err = None

    for attempt in range(LLM_MAX_RETRIES + 1):
        try:
            r = requests.post(LLM_URL, json=payload, timeout=LLM_TIMEOUT_S)
            r.raise_for_status()
            data = r.json()
            return (data.get("message", {}) or {}).get("content", "") or ""
        except Exception as e:
            last_err = e
            if attempt >= LLM_MAX_RETRIES:
                if LLM_DEBUG:
                    print(f"[LLM ERROR] {type(e).__name__}: {e}")
                return ""
            time.sleep(LLM_RETRY_BACKOFF_S * (2**attempt))

    if LLM_DEBUG and last_err is not None:
        print(f"[LLM ERROR] {type(last_err).__name__}: {last_err}")
    return ""






def extract_with_llm(text: str, allowed_fields: Iterable[str], current_facts: Optional[dict] = None):
    """
    Extract fields from free-form user text by mapping meaning -> schema paths.
    The model must not invent keys.
    Returns: {"fields": {path: {"value": ..., "confidence": ...}}}
    """
    if current_facts is None:
        current_facts = {}

    allowed_list = list(allowed_fields or [])
    allowed_set = set(allowed_list)

    # Pour éviter un prompt géant si template énorme:
    allowed_list_sorted = sorted(allowed_list)
    if len(allowed_list_sorted) > MAX_FIELDS_IN_PROMPT:
        # On envoie un subset (mais gates côté code restent stricts)
        allowed_list_sorted = allowed_list_sorted[:MAX_FIELDS_IN_PROMPT]

    messages = [
    {"role": "system", "content": GLOBAL_POLICY.strip()},
    {"role": "system", "content": PROMPT_EXTRACTION_AGENT.strip()},
    {
        "role": "user",
        "content": f"""
    allowed_fields:
    {allowed_list_sorted}

    user_text:
    {text}

    current_facts (partial):
    {current_facts}
    IMPORTANT:
    - Retourne uniquement un JSON valide.
    - Aucun texte hors JSON.
    - Si rien à extraire: {{"fields": {{}}}}
    """.strip(),
    },
    ]

    payload = {
    "model": LLM_MODEL,
    "messages": messages,
    "format": "json",
    "stream": False,
    }

    
    raw = _post_llm(payload)
    if not raw.strip():
        return {"fields": {}}

    cleaned = _clean_json(raw)
    data = _safe_load_json(cleaned)
    return _normalize_output(data, allowed_set)
