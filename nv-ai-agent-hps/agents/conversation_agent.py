import re
import copy

# Validation pays
try:
    import pycountry
except Exception:
    pycountry = None

_FALLBACK_COUNTRIES = {
    "maroc": "Maroc",
    "morocco": "Maroc",
    "france": "France",
    "suisse": "Suisse",
    "switzerland": "Suisse",
    "ghana": "Ghana",
    "tunisie": "Tunisie",
    "tunisia": "Tunisie",
    "algerie": "Algérie",
    "algeria": "Algérie",
    "espagne": "Espagne",
    "spain": "Espagne",
    
}

def normalize_currency(x: str) -> str:
    if not x:
        return ""
    x = x.strip().upper()
    if x in {"DH", "DHS"}:
        return "MAD"
    return x

def normalize_country(x: str) -> str:
    if not x:
        return ""

    x = x.strip()
    low = x.lower()

    
    if low in _FALLBACK_COUNTRIES:
        return _FALLBACK_COUNTRIES[low]

    
    if pycountry is not None:
        try:
            c = pycountry.countries.search_fuzzy(x)[0]
            return c.name
        except Exception:
            return ""

   

   
    if low in _FALLBACK_COUNTRIES:
        return _FALLBACK_COUNTRIES[low]

    
    if len(x.split()) > 3:
        m = re.search(r"\b([A-Za-zÀ-ÿ\-]{3,})\b", x)
        if m:
            x = m.group(1)

    if pycountry is None:
        return _FALLBACK_COUNTRIES.get(x.lower(), "")

    try:
        c = pycountry.countries.get(name=x)
        if c:
            return c.name
        c = pycountry.countries.search_fuzzy(x)[0]
        return c.name
    except Exception:
        return ""

def is_missing_value(v) -> bool:
    if v is None:
        return True
    if isinstance(v, str) and v.strip() == "":
        return True
    if isinstance(v, list) and len(v) == 0:
        return True
    if isinstance(v, dict) and len(v) == 0:
        return True
    return False

def _get_by_path(obj, path: str):
    cur = obj
    for part in path.split("."):
        if part.isdigit():
            idx = int(part)
            if not isinstance(cur, list) or idx >= len(cur):
                return None
            cur = cur[idx]
        else:
            if not isinstance(cur, dict) or part not in cur:
                return None
            cur = cur[part]
    return cur

def _ensure_list_index(lst: list, idx: int, template_item):
    while len(lst) <= idx:
        lst.append(copy.deepcopy(template_item))

def set_by_path(obj, path: str, value, template_obj) -> bool:
    """
    Safely set nested value using template to create missing structures.
    Supports dotted paths and numeric indices.
    """
    parts = path.split(".")
    cur = obj
    tmpl = template_obj

    for i, part in enumerate(parts):
        last = (i == len(parts) - 1)

        if part.isdigit():
            idx = int(part)
            if not isinstance(cur, list):
                return False

            tmpl_item = {}
            if isinstance(tmpl, list) and len(tmpl) > 0:
                tmpl_item = tmpl[0]
            _ensure_list_index(cur, idx, tmpl_item)

            if last:
                cur[idx] = value
                return True

            cur = cur[idx]
            tmpl = tmpl_item
            continue

        # dict key
        if not isinstance(cur, dict):
            return False

        if last:
            cur[part] = value
            return True

        # create container based on template
        next_tmpl = tmpl.get(part) if isinstance(tmpl, dict) else {}
        if part not in cur or cur[part] is None:
            if isinstance(next_tmpl, list):
                cur[part] = []
            elif isinstance(next_tmpl, dict):
                cur[part] = {}
            else:
                cur[part] = {}

        cur = cur[part]
        tmpl = next_tmpl

    return False

def cast_value(user_text: str, template_value):
    t = user_text.strip()

    if isinstance(template_value, bool):
        if t.lower() in {"oui", "o", "yes", "y", "true", "1"}:
            return True
        if t.lower() in {"non", "n", "no", "false", "0"}:
            return False
        return bool(t)

    if isinstance(template_value, int):
        try:
            return int(t)
        except Exception:
            return 0

    if isinstance(template_value, float):
        try:
            return float(t.replace(",", "."))
        except Exception:
            return 0.0

    if isinstance(template_value, list):
        items = [x.strip() for x in re.split(r"[,\n;]+", t) if x.strip()]
        return items

    # default: string / None
    return t

def postprocess(path: str, value):
    if isinstance(value, str):
        if path.endswith(".currency") or path.endswith("bank.currency"):
            return normalize_currency(value)
        if path.endswith(".country") or path.endswith("bank.country"):
            return normalize_country(value)  
    return value

def apply_single_field_answer(facts: dict, template_obj: dict, path: str, user_text: str) -> bool:
    tmpl_value = _get_by_path(template_obj, path)
    v = cast_value(user_text, tmpl_value)
    v = postprocess(path, v)

    
    if (path.endswith(".country") or path.endswith("bank.country")) and isinstance(v, str) and v.strip() == "":
        return False

    return set_by_path(facts, path, v, template_obj)


def _extract_bank_name(text: str):
    
    m = re.search(r"(?:s'?appelle|nom(?:\s+de)?\s+la\s+banque|bank\s+name\s+is)\s+([A-Za-z0-9\-_ ]{2,})", text, flags=re.I)
    if m:
        name = m.group(1).strip()
        
        name = re.split(r"\b(au|en|dans|et|,|\.|\bmaroc\b|\bfrance\b|\beur\b|\bmad\b|\busd\b)\b", name, flags=re.I)[0].strip()
        if name:
            return name.upper()
    return None

def _extract_currency(text: str):
    m = re.search(r"\b(MAD|EUR|USD|GBP|CHF|CAD|AUD)\b", text, flags=re.I)
    if m:
        return normalize_currency(m.group(1))
    
    if re.search(r"\b(dh|dhs)\b", text, flags=re.I):
        return "MAD"
    return None

def _extract_country(text: str):
    
    m = re.search(r"\b(?:au|en|in)\s+([A-Za-zÀ-ÿ\-]{3,})\b", text, flags=re.I)
    if m:
        c = normalize_country(m.group(1))
        return c or None
    
    for k, v in _FALLBACK_COUNTRIES.items():
        if re.search(rf"\b{k}\b", text, flags=re.I):
            return v
    return None

def apply_user_message_to_facts(facts: dict, template_obj: dict, user_text: str):
    """
    Conservative extraction:
    - Fill only a few high-confidence fields if they exist in template:
      bank.name, bank.country, bank.currency
    Never invent.
    """
    txt = user_text.strip()
    if not txt:
        return

    # bank.name
    bn = _extract_bank_name(txt)
    if bn is not None:
        set_by_path(facts, "bank.name", bn, template_obj)

    # bank.currency
    cur = _extract_currency(txt)
    if cur is not None:
        set_by_path(facts, "bank.currency", cur, template_obj)

    # bank.country
    co = _extract_country(txt)
    if co is not None:
        set_by_path(facts, "bank.country", co, template_obj)
