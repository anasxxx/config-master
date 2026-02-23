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


from config import USE_LLM, ALLOWED_LLM_FIELDS

from security.sanitize import sanitize_text
from agents.llm_extractor import extract_with_llm
from agents.llm_gates import apply_llm_gates


def normalize_currency(x: str) -> str:
    if not x:
        return ""
    x = x.strip().upper()
    if x in {"DH", "DHS"}:
        return "MAD"
    return x


def normalize_country(x: str) -> str:
    """
    Normalise un pays vers un nom lisible (fallback local + pycountry si dispo).
    Retourne "" si non reconnu.
    """
    if not x:
        return ""

    raw = x.strip()
    low = raw.lower()

    # 1) fallback direct
    if low in _FALLBACK_COUNTRIES:
        return _FALLBACK_COUNTRIES[low]

    # 2) pycountry fuzzy
    if pycountry is not None:
        try:
            c = pycountry.countries.search_fuzzy(raw)[0]
            return c.name
        except Exception:
            pass

    # 3) fallback sur un mot clé si phrase longue 
    words = re.findall(r"[A-Za-zÀ-ÿ\-]{3,}", raw)
    if words:
        for w in words:
            lw = w.lower()
            if lw in _FALLBACK_COUNTRIES:
                return _FALLBACK_COUNTRIES[lw]

        # tentative pycountry sur un mot si dispo
        if pycountry is not None:
            try:
                c = pycountry.countries.search_fuzzy(words[0])[0]
                return c.name
            except Exception:
                pass

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
    # strings
    if isinstance(value, str):
        if path.endswith(".currency") or path.endswith("bank.currency"):
            return normalize_currency(value)
        if path.endswith(".country") or path.endswith("bank.country"):
            return normalize_country(value)
        if path == "cards.0.card_info.network":
            return value.strip().upper()
        if path == "bank.bank_code":
            return value.strip().upper()

    # lists
    if isinstance(value, list):
        if path == "bank.resources":
            return normalize_resources(value)
        if path == "cards.0.services.enabled":
            return normalize_services(value)

    return value









def _normalize_list_items(items):
    
    out = []
    for x in (items or []):
        if x is None:
            continue
        s = str(x).strip()
        if not s:
            continue
        out.append(s)

    
    uniq = []
    seen = set()
    for s in out:
        key = s.lower()
        if key not in seen:
            uniq.append(s)
            seen.add(key)
    return uniq


def normalize_resources(items):
    """
    resources: on garde en lowercase (accounts, cards, transactions)
    """
    items = _normalize_list_items(items)
    return [re.sub(r"[^a-z0-9_\-]+", "", s.lower()) for s in items if s.strip()]


def normalize_services(items):
    """
    services.enabled: on garde en UPPER (3DS, TOKENIZATION, VISA_SMS)
    """
    items = _normalize_list_items(items)
    out = []
    for s in items:
        s2 = s.upper().replace(" ", "_")
        s2 = re.sub(r"[^A-Z0-9_]+", "", s2)
        if s2:
            out.append(s2)
    
    uniq = []
    seen = set()
    for s in out:
        if s not in seen:
            uniq.append(s)
            seen.add(s)
    return uniq


def validate_field_value(path: str, value) -> bool:
    """
    Retourne True si value est acceptable pour ce path.
    """
    # --- strings ---
    if path == "cards.0.card_info.bin":
        s = str(value).strip()
        return bool(re.fullmatch(r"\d{6,8}", s))

    if path == "cards.0.card_info.network":
        s = str(value).strip().upper()
        return s in {"VISA", "MASTERCARD"}

    if path == "bank.currency" or path.endswith(".currency"):
        s = str(value).strip().upper()
        return bool(re.fullmatch(r"[A-Z]{3}", s))

    if path == "bank.bank_code" or path.endswith("bank_code"):
        s = str(value).strip().upper()
        return bool(re.fullmatch(r"[A-Z0-9\-_]{2,20}", s))

    # --- lists ---
    if path == "bank.resources":
        if not isinstance(value, list):
            return False
        items = normalize_resources(value)
        return len(items) > 0

    if path == "cards.0.services.enabled":
        if not isinstance(value, list):
            return False
        items = normalize_services(value)
        return len(items) > 0

    # défaut: accepte
    return True








def apply_single_field_answer(facts: dict, template_obj: dict, path: str, user_text: str) -> bool:
    tmpl_value = _get_by_path(template_obj, path)
    v = cast_value(user_text, tmpl_value)
    v = postprocess(path, v)

    # sécurité: country vide -> refuse
    if (path.endswith(".country") or path.endswith("bank.country")) and isinstance(v, str) and v.strip() == "":
        return False

    # ✅ validation forte
    if not validate_field_value(path, v):
        return False

    return set_by_path(facts, path, v, template_obj)


def apply_multi_field_answer(facts: dict, template_obj: dict, paths: list, user_text: str) -> bool:
    txt = (user_text or "").strip()
    if not txt:
        return False

    # split standard
    parts = [p.strip() for p in re.split(r"[,;/]+", txt) if p.strip()]

    # fallback "Ville CODE" / "BIN VISA"
    if len(parts) < len(paths) and len(paths) == 2:
        tokens = txt.split()
        if len(tokens) >= 2:
            parts = [" ".join(tokens[:-1]).strip(), tokens[-1].strip()]

    if len(parts) < len(paths):
        return False

    ok_all = True
    for path, part in zip(paths, parts):
        tmpl_value = _get_by_path(template_obj, path)
        v = cast_value(part, tmpl_value)
        v = postprocess(path, v)

        if not validate_field_value(path, v):
            return False

        ok_all = ok_all and set_by_path(facts, path, v, template_obj)

    return bool(ok_all)


def _extract_bank_name(text: str):
    
    m = re.search(
        r"(?:"
        r"s'?appelle|"
        r"sous\s+le\s+nom|"
        r"nomm[eé]e|"
        r"appel[eé]e|"
        r"nom(?:\s+de)?\s+la\s+banque|"
        r"nom\s*[:=]|"
        r"bank\s+name\s+is"
        r")\s+([A-Za-z0-9\-_ ]{2,})",
        text,
        flags=re.I,
    )
    if m:
        name = m.group(1).strip()

        # coupe dès qu'on arrive à des mots qui ne font plus partie du nom
        name = re.split(
            r"\b(au|en|dans|avec|and|et|bank\s*code|code\s*banque|bank_code|code|devise|currency|pays|country|,|\.|\d{3,})\b",
            name,
            flags=re.I,
        )[0].strip()

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
    Extraction hybride:
    1) (optionnel) LLM sur texte redacted -> filtré par gates -> merge safe
    2) fallback regex (ton comportement actuel) -> merge
    """
    txt = (user_text or "").strip()
    if not txt:
        return

    # --- 1) LLM (feature flag) ---
    # Ne casse rien : si USE_LLM=False, ce bloc ne fait rien
    if USE_LLM:
        redacted, _secrets = sanitize_text(txt)
        llm_out = extract_with_llm(redacted, ALLOWED_LLM_FIELDS)
        clean = apply_llm_gates(llm_out)

        # merge safe: ne pas écraser une valeur déjà présente
        for path, value in clean.items():
            if is_missing_value(_get_by_path(facts, path)):
                set_by_path(facts, path, value, template_obj)

    # --- 2) Fallback regex (comme avant) ---
    bn = _extract_bank_name(txt)
    if bn is not None and is_missing_value(_get_by_path(facts, "bank.name")):
        set_by_path(facts, "bank.name", bn, template_obj)

    cur = _extract_currency(txt)
    if cur is not None and is_missing_value(_get_by_path(facts, "bank.currency")):
        set_by_path(facts, "bank.currency", cur, template_obj)

    co = _extract_country(txt)
    if co is not None and is_missing_value(_get_by_path(facts, "bank.country")):
        set_by_path(facts, "bank.country", co, template_obj)