import requests
import json
import re
import os
from typing import Any, Iterable, Optional
from config import (
    LLM_URL,
    LLM_MODEL,
    LLM_TEMPERATURE,
    LLM_TOP_P,
    LLM_TIMEOUT_S,
    LLM_DEBUG,
)
from agents.prompts import GLOBAL_POLICY, PROMPT_EXTRACTION_AGENT, PROMPT_EXTRACTION_AGENT_STRICT
MAX_FIELDS_IN_PROMPT = 1200  # augmente si ton modèle supporte; 800-1500 ok


def _effective_model() -> str:
    env_model = (os.getenv("HPS_LLM_MODEL", "") or "").strip()
    return env_model or LLM_MODEL


def _effective_options() -> dict:
    temp_raw = (os.getenv("HPS_LLM_TEMPERATURE", "") or "").strip()
    top_p_raw = (os.getenv("HPS_LLM_TOP_P", "") or "").strip()
    num_predict_raw = (os.getenv("HPS_LLM_NUM_PREDICT", "") or "").strip()

    try:
        temperature = float(temp_raw) if temp_raw else float(LLM_TEMPERATURE)
    except Exception:
        temperature = float(LLM_TEMPERATURE)

    try:
        top_p = float(top_p_raw) if top_p_raw else float(LLM_TOP_P)
    except Exception:
        top_p = float(LLM_TOP_P)

    try:
        num_predict = int(num_predict_raw) if num_predict_raw else 320
    except Exception:
        num_predict = 320

    temperature = max(0.0, min(1.0, temperature))
    top_p = max(0.0, min(1.0, top_p))
    num_predict = max(128, min(4096, num_predict))
    return {"temperature": temperature, "top_p": top_p, "num_predict": num_predict}


def _extraction_prompt() -> str:
    strict = (os.getenv("HPS_EXTRACTION_PROMPT_STRICT", "1") or "1").strip().lower()
    if strict in {"1", "true", "yes", "on"}:
        return (PROMPT_EXTRACTION_AGENT_STRICT or PROMPT_EXTRACTION_AGENT).strip()
    return PROMPT_EXTRACTION_AGENT.strip()


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
            return _recover_fields_from_partial(content)
        try:
            return json.loads(m.group(0))
        except Exception:
            partial = _recover_fields_from_partial(content)
            return partial if partial else {}


def _find_matching_brace(s: str, start: int) -> int:
    depth = 0
    in_str = False
    escape = False
    for i in range(start, len(s)):
        ch = s[i]
        if in_str:
            if escape:
                escape = False
                continue
            if ch == "\\":
                escape = True
                continue
            if ch == '"':
                in_str = False
                continue
            continue
        if ch == '"':
            in_str = True
            continue
        if ch == "{":
            depth += 1
            continue
        if ch == "}":
            depth -= 1
            if depth == 0:
                return i
    return -1


def _recover_fields_from_partial(content: str) -> dict:
    txt = (content or "").strip()
    if not txt:
        return {}

    i_fields = txt.find('"fields"')
    if i_fields < 0:
        return {}
    i_obj = txt.find("{", i_fields)
    if i_obj < 0:
        return {}

    dec = json.JSONDecoder()
    i = i_obj + 1
    out = {}
    n = len(txt)

    while i < n:
        while i < n and txt[i] in " \r\n\t,":
            i += 1
        if i >= n or txt[i] == "}":
            break
        if txt[i] != '"':
            break
        try:
            key, i_key_end = dec.raw_decode(txt, i)
        except Exception:
            break
        i = i_key_end
        while i < n and txt[i] in " \r\n\t":
            i += 1
        if i >= n or txt[i] != ":":
            break
        i += 1
        while i < n and txt[i] in " \r\n\t":
            i += 1
        if i >= n or txt[i] != "{":
            break

        j = _find_matching_brace(txt, i)
        if j < 0:
            break
        obj_txt = txt[i : j + 1]
        try:
            meta = json.loads(obj_txt)
        except Exception:
            i = j + 1
            continue

        if isinstance(meta, dict) and "value" in meta:
            out[str(key)] = meta
        i = j + 1

    if out:
        return {"fields": out}
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


def _is_missing_value(v: Any) -> bool:
    if isinstance(v, dict) and "value" in v:
        return _is_missing_value(v.get("value"))
    if v is None:
        return True
    if isinstance(v, str) and v.strip().lower() in {"", "none", "null", "n/a", "na", "nil", "unknown"}:
        return True
    if isinstance(v, list):
        if len(v) == 0:
            return True
        return all(_is_missing_value(x) for x in v)
    if isinstance(v, dict) and len(v) == 0:
        return True
    return False


def _unwrap_value_object(v: Any) -> Any:
    if isinstance(v, dict) and "value" in v:
        return _unwrap_value_object(v.get("value"))
    if isinstance(v, dict):
        return {k: _unwrap_value_object(x) for k, x in v.items()}
    if isinstance(v, list):
        return [_unwrap_value_object(x) for x in v]
    return v


def _prune_for_llm(node: Any, leaves_ref: list, max_leaves: int, depth: int, max_depth: int) -> Any:
    if leaves_ref[0] >= max_leaves or depth > max_depth:
        return None

    node = _unwrap_value_object(node)
    if _is_missing_value(node):
        return None

    if isinstance(node, dict):
        out = {}
        for k, v in node.items():
            if leaves_ref[0] >= max_leaves:
                break
            pv = _prune_for_llm(v, leaves_ref, max_leaves, depth + 1, max_depth)
            if pv is None or _is_missing_value(pv):
                continue
            out[k] = pv
        return out if out else None

    if isinstance(node, list):
        out = []
        for v in node[:8]:
            if leaves_ref[0] >= max_leaves:
                break
            pv = _prune_for_llm(v, leaves_ref, max_leaves, depth + 1, max_depth)
            if pv is None or _is_missing_value(pv):
                continue
            out.append(pv)
        return out if out else None

    leaves_ref[0] += 1
    return node


def _compact_current_facts(current_facts: Optional[dict]) -> str:
    send_raw = (os.getenv("HPS_LLM_SEND_CURRENT_FACTS", "1") or "1").strip().lower()
    if send_raw in {"0", "false", "no", "off"}:
        return "{}"

    try:
        max_chars = int((os.getenv("HPS_LLM_MAX_FACTS_CHARS", "") or "").strip() or 1400)
    except Exception:
        max_chars = 1400
    try:
        max_depth = int((os.getenv("HPS_LLM_MAX_FACTS_DEPTH", "") or "").strip() or 6)
    except Exception:
        max_depth = 6
    try:
        max_leaves_default = int((os.getenv("HPS_LLM_MAX_FACTS_LEAVES", "") or "").strip() or 56)
    except Exception:
        max_leaves_default = 56

    max_chars = max(300, min(6000, max_chars))
    max_depth = max(2, min(10, max_depth))
    max_leaves_default = max(8, min(200, max_leaves_default))

    for leaves in [max_leaves_default, 40, 24, 12]:
        ref = [0]
        pruned = _prune_for_llm(current_facts or {}, ref, leaves, depth=0, max_depth=max_depth)
        if pruned is None:
            continue
        try:
            packed = json.dumps(pruned, ensure_ascii=False, separators=(",", ":"))
        except Exception:
            continue
        if len(packed) <= max_chars:
            return packed
    return "{}"


def _trim_user_text(text: str) -> str:
    try:
        max_chars = int((os.getenv("HPS_LLM_MAX_TEXT_CHARS", "") or "").strip() or 2600)
    except Exception:
        max_chars = 2600
    max_chars = max(400, min(12000, max_chars))

    t = (text or "").strip()
    if len(t) <= max_chars:
        return t
    return (t[:max_chars] + "\n[truncated]").strip()


def _build_messages(text: str, allowed_list_sorted: list, current_facts: Optional[dict]) -> list:
    compact_facts = _compact_current_facts(current_facts)
    trimmed_text = _trim_user_text(text)
    return [
        {"role": "system", "content": GLOBAL_POLICY.strip()},
        {"role": "system", "content": _extraction_prompt()},
        {
            "role": "user",
            "content": f"""
    allowed_fields:
    {allowed_list_sorted}

    user_text:
    {trimmed_text}

    current_facts (partial):
    {compact_facts}
    IMPORTANT:
    - Retourne uniquement un JSON valide.
    - Aucun texte hors JSON.
    - Si rien à extraire: {{"fields": {{}}}}
    - Format strict: {{"fields": {{"path": {{"value": ..., "confidence": 0.0}}}}}}
    - N'ajoute jamais "evidence", "reasoning", ni d'autres clés.
    - Répond avec un JSON compact.
    """.strip(),
        },
    ]



def _post_llm_with_status(payload: dict) -> tuple[str, str]:
    """
    Appelle le LLM une seule fois.
    Retourne (content, status).
    status: LLM_OK | LLM_TIMEOUT | LLM_DOWN
    """
    if str(os.getenv("HPS_FORCE_LLM_DOWN", "")).strip().lower() in {"1", "true", "yes", "on"}:
        return "", "LLM_DOWN"
    try:
        r = requests.post(LLM_URL, json=payload, timeout=LLM_TIMEOUT_S)
        r.raise_for_status()
        data = r.json()
        content = (data.get("message", {}) or {}).get("content", "") or ""
        return content, "LLM_OK"
    except requests.exceptions.Timeout as e:
        if LLM_DEBUG:
            print(f"[LLM ERROR] {type(e).__name__}: {e}")
        return "", "LLM_TIMEOUT"
    except requests.exceptions.ConnectionError as e:
        if LLM_DEBUG:
            print(f"[LLM ERROR] {type(e).__name__}: {e}")
        return "", "LLM_DOWN"
    except requests.exceptions.RequestException as e:
        if LLM_DEBUG:
            print(f"[LLM ERROR] {type(e).__name__}: {e}")
        return "", "LLM_DOWN"
    except Exception as e:
        if LLM_DEBUG:
            print(f"[LLM ERROR] {type(e).__name__}: {e}")
        return "", "LLM_DOWN"


def _post_llm(payload: dict) -> str:
    """
    Appelle le LLM une seule fois.
    Retourne le champ "content" (string). Sinon string vide.
    """
    content, _status = _post_llm_with_status(payload)
    return content






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

    messages = _build_messages(text, allowed_list_sorted, current_facts)

    payload = {
        "model": _effective_model(),
        "messages": messages,
        "format": "json",
        "stream": False,
        "options": _effective_options(),
    }

    
    raw = _post_llm(payload)
    if not raw.strip():
        return {"fields": {}}

    cleaned = _clean_json(raw)
    data = _safe_load_json(cleaned)
    return _normalize_output(data, allowed_set)


def extract_with_llm_status(text: str, allowed_fields: Iterable[str], current_facts: Optional[dict] = None):
    """
    Same as extract_with_llm but returns (status, output).
    status: LLM_OK | LLM_TIMEOUT | LLM_DOWN | LLM_INVALID_JSON
    """
    if current_facts is None:
        current_facts = {}

    allowed_list = list(allowed_fields or [])
    allowed_set = set(allowed_list)

    allowed_list_sorted = sorted(allowed_list)
    if len(allowed_list_sorted) > MAX_FIELDS_IN_PROMPT:
        allowed_list_sorted = allowed_list_sorted[:MAX_FIELDS_IN_PROMPT]

    messages = _build_messages(text, allowed_list_sorted, current_facts)

    payload = {
        "model": _effective_model(),
        "messages": messages,
        "format": "json",
        "stream": False,
        "options": _effective_options(),
    }

    raw, status = _post_llm_with_status(payload)
    if status != "LLM_OK":
        return status, {"fields": {}}

    if not raw.strip():
        return "LLM_INVALID_JSON", {"fields": {}}

    cleaned = _clean_json(raw)
    data = _safe_load_json(cleaned)
    if not isinstance(data, dict) or "fields" not in data or not isinstance(data.get("fields"), dict):
        return "LLM_INVALID_JSON", {"fields": {}}

    return "LLM_OK", _normalize_output(data, allowed_set)
