# agents/conversation_agent.py
import re
import copy
from datetime import datetime
from typing import Any, Dict, Optional, List, Tuple

# Validation pays
try:
    import pycountry
except Exception:
    pycountry = None

_FALLBACK_COUNTRIES = {
    "maroc": "Maroc",
    "morocco": "Maroc",
    "france": "France",
    "usa": "United States",
    "us": "United States",
    "united states": "United States",
    "etats unis": "United States",
    "états unis": "United States",
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

from config import USE_LLM
from security.sanitize import sanitize_text
from agents.llm_extractor import extract_with_llm
from agents.llm_gates import apply_llm_gates
from agents.schema_validator import validate_value


# =========================================================
# AUTO: allowed fields from template (no manual allowlist)
# =========================================================
_ALLOWED_CACHE: Dict[int, set] = {}


def _is_primitive(x: Any) -> bool:
    return x is None or isinstance(x, (str, int, float, bool))


def build_leaf_paths(template_obj: Any, exclude_prefixes=("options",)) -> set:
    out = set()

    def rec(node: Any, path):
        if path and path[0] in set(exclude_prefixes):
            return

        if _is_primitive(node):
            if path:
                out.add(".".join(path))
            return

        if isinstance(node, list):
            idx_path = (path + ["0"]) if path else ["0"]
            if len(node) == 0:
                out.add(".".join(idx_path))
                return
            rec(node[0], idx_path)
            return

        if isinstance(node, dict):
            if len(node) == 0:
                if path:
                    out.add(".".join(path))
                return
            for k, v in node.items():
                if isinstance(k, str):
                    rec(v, path + [k])
            return

    rec(template_obj, [])
    return out


def _get_allowed_fields(template_obj: dict) -> set:
    key = id(template_obj)
    if key in _ALLOWED_CACHE:
        return _ALLOWED_CACHE[key]
    allowed = build_leaf_paths(template_obj, exclude_prefixes=("options",))
    _ALLOWED_CACHE[key] = allowed
    return allowed


# -------------------------
# Provenance (A2)
# -------------------------
def set_provenance(state: dict, path: str, source: str, confidence: float = 1.0, evidence: Optional[str] = None):
    """
    Stocke la provenance par champ dans state["provenance"].
    source: "user" | "llm" | "regex" | "tool" | "default"
    """
    if "provenance" not in state or not isinstance(state.get("provenance"), dict):
        state["provenance"] = {}

    try:
        confidence = float(confidence)
    except Exception:
        confidence = 1.0
    confidence = max(0.0, min(1.0, confidence))

    payload = {
        "source": source,
        "confidence": confidence,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }
    if evidence:
        payload["evidence"] = evidence

    state["provenance"][path] = payload


# -------------------------
# Normalization helpers
# -------------------------
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

    raw = x.strip()
    low = raw.lower()

    if low in _FALLBACK_COUNTRIES:
        return _FALLBACK_COUNTRIES[low]

    if pycountry is not None:
        try:
            c = pycountry.countries.search_fuzzy(raw)[0]
            return c.name
        except Exception:
            pass

    words = re.findall(r"[A-Za-zÀ-ÿ\-]{3,}", raw)
    if words:
        for w in words:
            lw = w.lower()
            if lw in _FALLBACK_COUNTRIES:
                return _FALLBACK_COUNTRIES[lw]

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


# -------------------------
# Path helpers
# -------------------------
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

        if not isinstance(cur, dict):
            return False

        if last:
            cur[part] = value
            return True

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


# -------------------------
# Casting / postprocess / validation
# -------------------------
def cast_value(user_text: str, template_value):
    t = (user_text or "").strip()

    if isinstance(template_value, bool):
        if t.lower() in {"oui", "o", "yes", "y", "true", "1"}:
            return True
        if t.lower() in {"non", "n", "no", "false", "0"}:
            return False
        return bool(t)

    if isinstance(template_value, int):
        clean=t.replace(" ","")
        try:
            return int(clean)
        except Exception:
            return 0

    if isinstance(template_value, float):
        clean = t.lower().replace("dh", "").replace("dhs", "")
        clean = clean.replace(" ", "").replace(",", ".")
        if clean.endswith("k"):
            try:
                return float(clean[:-1]) * 1000
            except Exception:
                return 0.0
        try:
            return float(clean)
        except Exception:
            return 0.0

    if isinstance(template_value, list):
        items = [x.strip() for x in re.split(r"[,\n;]+", t) if x.strip()]
        return items

    return t


def postprocess(path: str, value):
    if isinstance(value, str):
        if path.endswith(".currency") or path.endswith("bank.currency"):
            return normalize_currency(value)
        if path.endswith(".country") or path.endswith("bank.country"):
            return normalize_country(value)
        if path == "cards.0.card_info.network":
            return value.strip().upper()
        if path == "bank.bank_code":
            return value.strip().upper()
    return value


def validate_field_value(path: str, value) -> bool:
    # Validations "business" simples (en plus du schema_validator)
    s = str(value).strip().upper()

    if path == "cards.0.card_info.bin":
        return bool(re.fullmatch(r"\d{6,8}", s))

    if path == "cards.0.card_info.network":
        return s in {"VISA", "MASTERCARD"}

    if "currency" in path:
        return bool(re.fullmatch(r"[A-Z]{3}", s))

    if "bank_code" in path:
        return bool(re.fullmatch(r"\d{3,10}", s))  # aligné prod

    return True


# ✅ helper central: validate + set + provenance
def _safe_set_if_valid(
    state: dict,
    template_obj: dict,
    path: str,
    value,
    source: str = "user",
    confidence: float = 1.0,
    evidence: Optional[str] = None,
) -> bool:
    facts = state["facts"]

    tmpl_value = _get_by_path(template_obj, path)
    ok, err = validate_value(path, value, tmpl_value)
    if not ok:
        print(f"[SCHEMA VALIDATION ERROR] {path} -> {err}")
        return False

    if not validate_field_value(path, value):
        print(f"[FIELD VALIDATION ERROR] {path} -> invalid value")
        return False

    done = set_by_path(facts, path, value, template_obj)
    if done:
        set_provenance(state, path, source=source, confidence=confidence, evidence=evidence)
    return done


# -------------------------
# Public API used by brain/agent
# -------------------------
def apply_single_field_answer(state: dict, template_obj: dict, path: str, user_text: str) -> bool:
    tmpl_value = _get_by_path(template_obj, path)
    v = cast_value(user_text, tmpl_value)
    v = postprocess(path, v)

    # refuse country vide
    if (path.endswith(".country") or path.endswith("bank.country")) and isinstance(v, str) and v.strip() == "":
        return False

    return _safe_set_if_valid(state, template_obj, path, v, source="user", confidence=1.0, evidence=user_text)


def _extract_limit_triplet_values(paths: list, txt: str) -> Optional[Dict[str, str]]:
    if len(paths) != 3:
        return None

    suffixes = {p.split(".")[-1] for p in paths}
    if suffixes != {"daily_amount", "weekly_amount", "monthly_amount"}:
        return None

    period_aliases = {
        "daily_amount": [r"daily", r"par\s+jour", r"jour(?:nalier)?", r"quotidien(?:ne)?", r"jour"],
        "weekly_amount": [r"weekly", r"par\s+semaine", r"hebdo(?:madaire)?", r"semaine"],
        "monthly_amount": [r"monthly", r"par\s+mois", r"mensuel(?:le)?", r"mois"],
    }

    out: Dict[str, str] = {}
    for p in paths:
        suffix = p.split(".")[-1]
        aliases = period_aliases[suffix]
        val = None
        for a in aliases:
            m = re.search(rf"(?i)\b(?:{a})\b[^\d\-]{{0,20}}(-?\d+(?:[.,]\d+)?(?:\s*[kK])?)", txt)
            if not m:
                m = re.search(rf"(?i)(-?\d+(?:[.,]\d+)?(?:\s*[kK])?)\s*(?:{a})\b", txt)
            if m:
                val = m.group(1).strip()
                break
        if val is not None:
            out[p] = val

    if len(out) == 3:
        return out

    nums = re.findall(r"-?\d+(?:[.,]\d+)?(?:\s*[kK])?", txt)
    if len(nums) == 3:
        by_suffix = {p.split(".")[-1]: p for p in paths}
        return {
            by_suffix["daily_amount"]: nums[0],
            by_suffix["weekly_amount"]: nums[1],
            by_suffix["monthly_amount"]: nums[2],
        }

    return None


def apply_multi_field_answer(state: dict, template_obj: dict, paths: list, user_text: str) -> bool:
    txt = (user_text or "").strip()
    if not txt:
        return False

    # Special handling for pair "<label text> + <numeric/alnum code>" even in noisy sentences.
    if len(paths) == 2 and paths[1].endswith("_code"):
        p_name, p_code = paths[0], paths[1]

        code_alias = "code"
        if p_code.endswith("region_code"):
            code_alias = r"(?:code\s*r[ée]gion|region[_\s-]*code|code)"
        elif p_code.endswith("city_code"):
            code_alias = r"(?:code\s*ville|city[_\s-]*code|code)"
        elif p_code.endswith("agency_code"):
            code_alias = r"(?:code\s*agence|agency[_\s-]*code|code)"

        code_val = None
        code_m = re.search(rf"(?i)\b{code_alias}\b\s*[:=]?\s*([A-Za-z0-9\-_]{{1,20}})\b", txt)
        if code_m:
            code_val = code_m.group(1).strip()
            name_chunk = txt[:code_m.start()].strip()
        else:
            nums = list(re.finditer(r"\b[A-Za-z0-9\-_]{1,20}\b", txt))
            code_tok = None
            for m in reversed(nums):
                tok = m.group(0)
                if re.fullmatch(r"\d{1,20}", tok):
                    code_tok = m
                    break
            if code_tok:
                code_val = code_tok.group(0).strip()
                name_chunk = txt[:code_tok.start()].strip()
            else:
                name_chunk = txt

        # Remove obvious trailing noise (e.g. limits discussion) from name field.
        name_chunk = re.split(r"(?i)\b(limites?|plafond|daily|weekly|monthly|par\s+jour|par\s+semaine|par\s+mois)\b", name_chunk)[0].strip()
        name_chunk = re.sub(r"\b\d{1,20}\b", "", name_chunk).strip()
        name_chunk = re.sub(r"(?i)^(region|région|city|ville|agence|agency)\s*[:=]?\s*", "", name_chunk).strip(" ,;:-")

        if name_chunk and code_val:
            ok1 = _safe_set_if_valid(
                state, template_obj, p_name, postprocess(p_name, cast_value(name_chunk, _get_by_path(template_obj, p_name))),
                source="user", confidence=1.0, evidence=user_text
            )
            ok2 = _safe_set_if_valid(
                state, template_obj, p_code, postprocess(p_code, cast_value(code_val, _get_by_path(template_obj, p_code))),
                source="user", confidence=1.0, evidence=user_text
            )
            if ok1 and ok2:
                return True

    # Special handling for limits triplets: daily/weekly/monthly in any order.
    limit_vals = _extract_limit_triplet_values(paths, txt)
    if limit_vals is not None:
        ok_all = True
        for path in paths:
            raw = limit_vals.get(path)
            if raw is None:
                return False
            tmpl_value = _get_by_path(template_obj, path)
            v = cast_value(raw, tmpl_value)
            v = postprocess(path, v)
            ok_one = _safe_set_if_valid(state, template_obj, path, v, source="user", confidence=1.0, evidence=user_text)
            if not ok_one:
                return False
            ok_all = ok_all and ok_one
        return bool(ok_all)

    parts = [p.strip() for p in re.split(r"[,;/]+", txt) if p.strip()]

    # fallback "Ville CODE"
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
        ok_one = _safe_set_if_valid(state, template_obj, path, v, source="user", confidence=1.0, evidence=user_text)
        if not ok_one:
            return False
        ok_all = ok_all and ok_one

    return bool(ok_all)


# -------------------------
# Regex extractors (bank/agence)
# -------------------------
def _cut_value(s: str) -> str:
    return re.split(
        r"\b(au|en|dans|avec|and|et|code|bank|banque|agency|agence|ville|city|region|devise|currency|pays|country|,|\.|\n)\b",
        s,
        flags=re.I,
    )[0].strip()


def _extract_bank_name(text: str):
    m01 = re.search(r"(?i)\b(?:banque|bank)\s+sera\s+([A-Za-z0-9À-ÿ\-_']{2,})\b", text)
    if m01:
        n1 = (m01.group(1) or "").strip()
        if n1:
            return n1.upper()

    m00 = re.search(r"(?i)\b(?:banque|bank)\s+nomm\S*\s+([A-Za-z0-9À-ÿ\-_']{2,})\b", text)
    if m00:
        n = (m00.group(1) or "").strip()
        if n:
            return n.upper()

    m0 = re.search(r"(?i)\bsous\s+nom\s+([A-Za-z0-9\-_ ]{2,})", text)
    if m0:
        name0 = m0.group(1).strip()
        name0 = re.split(
            r"\b(au|en|dans|avec|and|et|bank\s*code|code\s*banque|bank_code|code|devise|currency|pays|country|,|\.|\d{3,})\b",
            name0,
            flags=re.I,
        )[0].strip()
        if name0:
            return name0.upper()

    m = re.search(
        r"(?:s'?appelle|sous\s+le\s+nom|sous\s+nom|nomm(?:e|ee|[ée]e?)|appel(?:e|ee|[ée]e?)|nom(?:\s+de)?\s+la\s+banque|nom\s*[:=]|bank\s+name\s+is)\s+([A-Za-z0-9À-ÿ\-_ ']{2,})",
        text,
        flags=re.I,
    )
    if m:
        name = m.group(1).strip()
        name = re.split(
            r"\b(au|en|dans|avec|and|et|bank\s*code|code\s*banque|bank_code|code|devise|currency|pays|country|,|\.|\d{3,})\b",
            name,
            flags=re.I,
        )[0].strip()
        if name:
            return name.upper()

    for m2 in re.finditer(r"(?i)\b(?:banque|bank)\s+([A-Za-z0-9\-_]{2,})\b", text):
        candidate = (m2.group(1) or "").strip()
        if candidate and not candidate.isdigit() and candidate.lower() not in {"code", "name", "nomm", "nomme", "nommee", "nommée", "sera", "est", "is", "will", "avec"}:
            return candidate.upper()

    m3 = re.search(r"(?i)\bbank\s*name\s*(?:is|=|:)?\s*([A-Za-z0-9\-_]{2,})\b", text)
    if m3:
        return m3.group(1).strip().upper()

    return None



def _extract_bank_code(text: str) -> Optional[str]:
    m = re.search(
        r"(?i)\b(?:bank[_\s-]*code|code\s*banque|bank\s*code|code\s*bank|bank_code)\s*[:=]?\s*([0-9]{2,20})\b",
        text,
    )
    if m:
        return m.group(1).strip()

    # Common phrasing: "banque ... avec code 4896 ..."
    m2 = re.search(
        r"(?i)\b(?:banque|bank)\b.{0,120}?\bavec\s+code\s*[:=]?\s*([0-9]{2,20})\b",
        text,
    )
    if m2:
        return m2.group(1).strip()

    # Fallback when user gives first bank code then agency code in same sentence.
    m3 = re.search(
        r"(?i)\bavec\s+code\s*[:=]?\s*([0-9]{2,20})\b(?=.*\bagence\b)",
        text,
    )
    if m3:
        return m3.group(1).strip()
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


def _extract_city(text: str) -> Optional[str]:
    m = re.search(r"(?i)\b(?:ville|city)\s*[:=]?\s*([A-Za-zÀ-ÿ\-_ ]{2,})", text)
    if m:
        v = _cut_value(m.group(1))
        v = re.sub(r"\s+\d{1,10}$", "", v).strip()
        return v.title() if v else None

    m2 = re.search(r"(?i)\b(?:à|a)\s+([A-Za-zÀ-ÿ\-_]{2,})\b", text)
    if m2:
        return m2.group(1).title()
    return None


def _extract_city_code(text: str) -> Optional[str]:
    m = re.search(
        r"(?i)\b(?:code\s*ville|city[_\s-]*code)\s*[:=]?\s*(\d{1,10})\b",
        text,
    )
    if m:
        return m.group(1).strip()

    m2 = re.search(
        r"(?i)\b(?:ville|city)\s*[:=]?\s*[A-Za-zÀ-ÿ\-_ ]{2,}\s+(\d{1,10})\b",
        text,
    )
    if m2:
        return m2.group(1).strip()
    return None


def _extract_region(text: str) -> Optional[str]:
    m = re.search(r"(?i)\b(?:region|région)\s*[:=]?\s*([A-Za-zÀ-ÿ\-_ ]{2,})", text)
    if m:
        v = _cut_value(m.group(1))
        return v.title() if v else None
    return None


def _extract_agency_name(text: str) -> Optional[str]:
    m0 = re.search(
        r"(?i)\bagence\s+nomm\S*\s+([A-Za-z0-9À-ÿ\-_ ']{2,})",
        text,
    )
    if m0:
        v0 = _cut_value(m0.group(1))
        v0 = re.sub(r"(?i)^(sous\s+le\s+nom|nomm\S*)\s+", "", v0).strip()
        v0 = re.sub(r"\bde\b\s*$", "", v0, flags=re.I).strip()
        return v0.upper() if v0 else None

    m0 = re.search(
        r"(?i)\bagence\s+sous\s+le\s+nom\s+([A-Za-z0-9À-ÿ\-_ ]{2,})",
        text,
    )
    if m0:
        v0 = _cut_value(m0.group(1))
        v0 = re.sub(r"(?i)^(sous\s+le\s+nom)\s+", "", v0).strip()
        v0 = re.sub(r"\bde\b\s*$", "", v0, flags=re.I).strip()
        return v0.upper() if v0 else None

    m = re.search(
        r"(?i)\b(?:agency[_\s-]*name|agence[_\s-]*name|nom\s+agence|agency|agence)\s*[:=]?\s*([A-Za-z0-9À-ÿ\-_ ']{2,})",
        text,
    )
    if m:
        v = _cut_value(m.group(1))
        v = re.sub(r"(?i)^(sous\s+le\s+nom|nomm\S*|s['’]?appelle)\s+", "", v).strip()
        v = re.sub(r"\bde\b\s*$", "", v, flags=re.I).strip()
        return v.upper() if v else None
    return None



def _extract_agency_code(text: str) -> Optional[str]:
    m = re.search(
        r"(?i)\bagence\b.{0,120}?\bde\s+code\s*[:=]?\s*([A-Za-z0-9\-_]{2,20})\b",
        text,
    )
    if m:
        return m.group(1).strip().upper()

    m2 = re.search(
        r"(?i)\bagence\s+[A-Za-z0-9À-ÿ\-_ ']{2,}\s+code\s*[:=]?\s*([A-Za-z0-9\-_]{2,20})\b",
        text,
    )
    if m2:
        return m2.group(1).strip().upper()

    m = re.search(
        r"(?i)\b(?:agency[_\s-]*code|code\s*agence|agency\s*code)\s*[:=]?\s*([A-Za-z0-9\-_]{2,20})\b",
        text,
    )
    if m:
        return m.group(1).strip().upper()
    return None



FIELD_ALIASES = {
    "bank.name": ["bank name", "nom banque", "nom de la banque", "sous nom", "nom"],
    "bank.country": ["country", "pays"],
    "bank.currency": ["currency", "devise", "monnaie"],
    "bank.bank_code": ["bank code", "code banque", "bank_code"],
    "bank.agencies.0.agency_name": ["agency name", "nom agence", "agence"],
    "bank.agencies.0.agency_code": ["agency code", "code agence", "de code", "agence code"],
    "bank.agencies.0.city": ["city", "ville"],
    "bank.agencies.0.city_code": ["city code", "code ville"],
    "bank.agencies.0.region": ["region", "région"],
    "bank.agencies.0.region_code": ["region code", "code region", "code région"],
    "cards.0.card_info.bin": ["bin"],
    "cards.0.card_info.network": ["network", "réseau"],
}


def _aliases_for_path(path: str) -> List[str]:
    aliases = list(FIELD_ALIASES.get(path, []))
    auto = _auto_aliases_for_path(path)
    for a in auto:
        if a not in aliases:
            aliases.append(a)
    return aliases


def _path_explicitly_mentioned(text: str, path: str) -> bool:
    for alias in _aliases_for_path(path):
        if re.search(rf"(?i)\b{re.escape(alias)}\b", text or ""):
            return True
    return False


def _same_value(a: Any, b: Any) -> bool:
    if a is None and b is None:
        return True
    if isinstance(a, str) and isinstance(b, str):
        return a.strip().lower() == b.strip().lower()
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return float(a) == float(b)
    if isinstance(a, list) and isinstance(b, list):
        return [str(x).strip().lower() for x in a] == [str(x).strip().lower() for x in b]
    return a == b


def _record_conflict(state: dict, path: str, old_value: Any, new_value: Any, source: str, evidence: str):
    if "conflicts" not in state or not isinstance(state.get("conflicts"), list):
        state["conflicts"] = []
    state["conflicts"].append(
        {
            "path": path,
            "old_value": old_value,
            "new_value": new_value,
            "source": source,
            "evidence": evidence,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
        }
    )


def _try_set_candidate(
    state: dict,
    template_obj: dict,
    path: str,
    raw_value: Any,
    *,
    source: str,
    confidence: float,
    evidence: str,
    explicit_mention: bool = False,
) -> bool:
    facts = state["facts"]
    current = _get_by_path(facts, path)
    tmpl_value = _get_by_path(template_obj, path)

    v = raw_value
    if not isinstance(raw_value, list):
        v = cast_value(str(raw_value), tmpl_value)
    v = postprocess(path, v)

    if is_missing_value(current):
        return _safe_set_if_valid(state, template_obj, path, v, source=source, confidence=confidence, evidence=evidence)

    if _same_value(current, v):
        return True

    prov = state.get("provenance", {}).get(path, {})
    existing_source = prov.get("source")

    # Conservative overwrite policy to keep conversation stable.
    allow_overwrite = False
    if source == "user":
        allow_overwrite = explicit_mention or existing_source in {"llm", "regex"}
    elif source == "regex":
        allow_overwrite = explicit_mention and existing_source in {"llm", "regex"}
    elif source == "llm":
        allow_overwrite = explicit_mention and existing_source in {"llm", "regex"}

    # Never let non-user extraction override explicit user value.
    if existing_source == "user" and source != "user":
        allow_overwrite = False

    if not allow_overwrite:
        if explicit_mention:
            _record_conflict(state, path, current, v, source, evidence)
        return False

    return _safe_set_if_valid(state, template_obj, path, v, source=source, confidence=confidence, evidence=evidence)


def _auto_aliases_for_path(path: str) -> List[str]:
    parts = [p for p in path.split(".") if not p.isdigit()]
    if not parts:
        return []
    leaf = parts[-1]
    aliases = {leaf, leaf.replace("_", " ")}
    if len(parts) >= 2:
        prev = parts[-2]
        aliases.add(f"{prev}_{leaf}")
        aliases.add(f"{prev} {leaf}".replace("_", " "))
    # Common short forms for limits fields.
    if leaf in {"daily_amount", "weekly_amount", "monthly_amount"}:
        aliases.add(leaf.replace("_", " "))
    return [a.strip() for a in aliases if a.strip()]


def _extract_labeled_fields(text: str, allowed_fields: set, template_obj: dict) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    dedicated_paths = {
        "bank.name",
        "bank.country",
        "bank.currency",
        "bank.bank_code",
        "bank.agencies.0.agency_name",
        "bank.agencies.0.agency_code",
        "bank.agencies.0.city",
        "bank.agencies.0.city_code",
        "bank.agencies.0.region",
        "bank.agencies.0.region_code",
    }

    # Build all label hits first, then extract value chunk until next label hit.
    hits = []
    for path in sorted(allowed_fields):
        if path.startswith("options.") or path in dedicated_paths:
            continue

        aliases = list(dict.fromkeys((FIELD_ALIASES.get(path, []) + _auto_aliases_for_path(path))))
        for alias in aliases:
            for m in re.finditer(rf"(?i)\b{re.escape(alias)}\b", text):
                hits.append({
                    "start": m.start(),
                    "end": m.end(),
                    "path": path,
                    "alias_len": len(alias),
                })

    if not hits:
        return out

    # Keep non-overlapping hits; prefer earliest then longer alias.
    hits.sort(key=lambda h: (h["start"], -h["alias_len"]))
    chosen = []
    last_end = -1
    for h in hits:
        if h["start"] < last_end:
            continue
        chosen.append(h)
        last_end = h["end"]

    for i, h in enumerate(chosen):
        path = h["path"]
        if path in out:
            continue

        next_start = chosen[i + 1]["start"] if i + 1 < len(chosen) else len(text)
        raw = text[h["end"]:next_start]
        raw = re.sub(r"^\s*(?:[:=\-]|is|est)?\s*", "", raw, flags=re.I).strip()
        if not raw:
            continue

        # Normalize based on path expected semantics.
        if path.endswith(".resources") or path.endswith(".enabled") or path.endswith("selected_limit_types"):
            items = [x.strip() for x in re.split(r"[,;/]|(?:\bet\b|\band\b)", raw, flags=re.I) if x.strip()]
            if items:
                out[path] = items
            continue

        if path.endswith(".bin") or path.endswith("bank_code") or path.endswith("agency_code") or path.endswith("city_code") or path.endswith("region_code"):
            m = re.search(r"[A-Za-z0-9\-_]{1,20}", raw)
            if m:
                val = m.group(0).strip()
                out[path] = val.upper() if ("code" in path or path.endswith(".bin")) else val
            continue

        if path.endswith("_amount") or path.endswith("min_amount") or path.endswith("max_amount") or path.endswith("_count"):
            m = re.search(r"-?\d+(?:[.,]\d+)?(?:\s*[kK])?", raw)
            if m:
                out[path] = m.group(0).strip()
            continue

        if path.endswith(".currency") or path.endswith("bank.currency"):
            m = re.search(r"[A-Za-z]{2,5}", raw)
            if m:
                out[path] = m.group(0).upper()
            continue

        if _get_by_path(template_obj, path) is True or _get_by_path(template_obj, path) is False:
            m = re.search(r"(?i)\b(oui|non|yes|no|true|false|0|1)\b", raw)
            if m:
                out[path] = m.group(1)
            continue

        # Generic text field.
        raw = re.split(r"(?i)\s*(?:,|;|\.|\bet\b|\band\b)\s*", raw)[0].strip()
        if raw:
            out[path] = raw

    return out


def apply_user_message_to_facts(state: dict, template_obj: dict, user_text: str):
    """
    A2: on reçoit state (pas facts) pour pouvoir enregistrer provenance.
    """
    txt = (user_text or "").strip()
    if not txt:
        return

    facts = state["facts"]
    allowed_fields = _get_allowed_fields(template_obj)

    # 1) Deterministic label-based extraction (order-independent).
    labeled = _extract_labeled_fields(txt, allowed_fields, template_obj)
    for path, raw_val in labeled.items():
        _try_set_candidate(
            state,
            template_obj,
            path,
            raw_val,
            source="user",
            confidence=0.95,
            evidence=txt,
            explicit_mention=True,
        )

    # 2) LLM schema-driven
    if USE_LLM:
        redacted, _secrets = sanitize_text(txt)
        llm_out = extract_with_llm(redacted, allowed_fields, current_facts=facts)

        clean = apply_llm_gates(llm_out, allowed_fields)

        fields_meta = {}
        if isinstance(llm_out, dict):
            fm = llm_out.get("fields", {})
            if isinstance(fm, dict):
                fields_meta = fm

        for path, value in (clean or {}).items():
            if path.startswith("options."):
                continue

            explicit_mention = _path_explicitly_mentioned(txt, path)

            # Strict fields: require explicit mention to avoid costly hallucinations.
            if (path.endswith("_code") or path.endswith("bank_code")) and not explicit_mention:
                continue
            if path == "bank.currency" and _extract_currency(txt) is None and not explicit_mention:
                continue
            # Region must be user-provided (or filled by deterministic city->region rules), not inferred by LLM.
            if path in {"bank.agencies.0.region", "bank.agencies.0.region_code"}:
                region_mentioned = bool(re.search(r"(?i)\b(region|région|region_code|code\s*region|code\s*région)\b", txt))
                if not region_mentioned:
                    continue

            conf = 1.0
            try:
                conf = float((fields_meta.get(path) or {}).get("confidence", 1.0))
            except Exception:
                conf = 1.0

            # Hybrid mode:
            # - explicit mention -> accept normal confidence
            # - implicit mention -> only very high confidence
            required_conf = 0.90
            if explicit_mention:
                required_conf = 0.70

            if conf < required_conf:
                continue

            _try_set_candidate(
                state,
                template_obj,
                path,
                value,
                source="llm",
                confidence=conf,
                evidence=redacted,
                explicit_mention=explicit_mention,
            )

    # 3) Regex quick wins (bank/agence)
    bn = _extract_bank_name(txt)
    if bn is not None:
        _try_set_candidate(state, template_obj, "bank.name", bn, source="user", confidence=1.0, evidence=txt, explicit_mention=True)

    bc = _extract_bank_code(txt)
    if bc is not None:
        _try_set_candidate(state, template_obj, "bank.bank_code", bc, source="user", confidence=1.0, evidence=txt, explicit_mention=True)

    cur = _extract_currency(txt)
    if cur is not None:
        _try_set_candidate(state, template_obj, "bank.currency", cur, source="user", confidence=1.0, evidence=txt, explicit_mention=True)

    co = _extract_country(txt)
    if co is not None:
        _try_set_candidate(state, template_obj, "bank.country", co, source="user", confidence=1.0, evidence=txt, explicit_mention=True)

    an = _extract_agency_name(txt)
    if an is not None:
        _try_set_candidate(state, template_obj, "bank.agencies.0.agency_name", an, source="user", confidence=1.0, evidence=txt, explicit_mention=True)

    ac = _extract_agency_code(txt)
    if ac is not None:
        _try_set_candidate(state, template_obj, "bank.agencies.0.agency_code", ac, source="user", confidence=1.0, evidence=txt, explicit_mention=True)

    city = _extract_city(txt)
    if city is not None:
        _try_set_candidate(state, template_obj, "bank.agencies.0.city", city, source="user", confidence=1.0, evidence=txt, explicit_mention=True)

    city_code = _extract_city_code(txt)
    if city_code is not None:
        _try_set_candidate(state, template_obj, "bank.agencies.0.city_code", city_code, source="user", confidence=1.0, evidence=txt, explicit_mention=True)

    reg = _extract_region(txt)
    if reg is not None:
        _try_set_candidate(state, template_obj, "bank.agencies.0.region", reg, source="user", confidence=1.0, evidence=txt, explicit_mention=True)
