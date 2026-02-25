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
        if path == "bank.name":
            cleaned = _clean_bank_name(value)
            if cleaned:
                return cleaned
            return value.strip().upper()
        if path == "bank.agencies.0.city":
            cleaned_city = _clean_city_name(value)
            if cleaned_city:
                return cleaned_city
            return value.strip().title()
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

    if path.endswith(".city"):
        return not _is_known_country_name(str(value).strip())

    return True


def _coerce_value_for_path(path: str, value):
    if value is None:
        return None

    if path.startswith("cards.0.fees.") or path.endswith("_amount"):
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            s = value.strip().lower().replace("dh", "").replace("dhs", "")
            s = s.replace(" ", "").replace(",", ".")
            if s.endswith("k"):
                try:
                    return float(s[:-1]) * 1000
                except Exception:
                    return value
            try:
                return float(s)
            except Exception:
                return value

    if path.endswith("_count"):
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            return int(value)
        if isinstance(value, str):
            s = value.strip().replace(" ", "").replace(",", ".")
            try:
                return int(float(s))
            except Exception:
                return value

    return value


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
    value = _coerce_value_for_path(path, value)

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


def _is_identifier_like_path(path: str) -> bool:
    return (
        path.endswith(".name")
        or path.endswith("_code")
        or path.endswith(".bin")
        or path in {"bank.bank_code", "cards.0.card_info.network"}
    )


def _looks_like_sentence_noise(text: str) -> bool:
    t = (text or "").strip().lower()
    if not t:
        return False
    words = re.findall(r"\w+", t)
    if len(words) <= 4:
        return False
    markers = [
        "je veux",
        "svp",
        "s il vous plait",
        "stp",
        "merci",
        "elle se trouve",
        "qui se trouve",
        "au maroc",
        "en france",
    ]
    return any(m in t for m in markers)


def _apply_targeted_llm_answer(state: dict, template_obj: dict, paths: list, user_text: str) -> int:
    if not USE_LLM:
        return 0
    txt = (user_text or "").strip()
    if not txt or not paths:
        return 0

    allowed = set(paths)
    llm_out = extract_with_llm(txt, allowed, current_facts=state.get("facts", {}))
    clean = apply_llm_gates(llm_out, allowed)
    if not clean:
        return 0

    fields_meta = {}
    if isinstance(llm_out, dict) and isinstance(llm_out.get("fields"), dict):
        fields_meta = llm_out.get("fields") or {}

    applied = 0
    for path in paths:
        if path not in clean:
            continue
        value = postprocess(path, clean[path])
        conf = 1.0
        try:
            conf = float((fields_meta.get(path) or {}).get("confidence", 1.0))
        except Exception:
            conf = 1.0

        ok = _safe_set_if_valid(
            state,
            template_obj,
            path,
            value,
            source="llm",
            confidence=conf,
            evidence=txt,
        )
        if ok:
            applied += 1
    return applied


# -------------------------
# Public API used by brain/agent
# -------------------------
def apply_single_field_answer(state: dict, template_obj: dict, path: str, user_text: str) -> bool:
    llm_applied = _apply_targeted_llm_answer(state, template_obj, [path], user_text)
    if llm_applied == 1:
        return True

    tmpl_value = _get_by_path(template_obj, path)

    if isinstance(tmpl_value, str) and _is_identifier_like_path(path) and _looks_like_sentence_noise(user_text):
        # Avoid storing an entire conversational sentence in identifier-like fields.
        return False

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

    llm_applied = _apply_targeted_llm_answer(state, template_obj, paths, txt)
    if llm_applied == len(paths):
        return True

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


def _clean_bank_name(raw: str) -> str:
    s = (raw or "").strip()
    if not s:
        return ""
    s = re.sub(r"(?i)^(la|le|les|une|un)\s+", "", s).strip()
    s = re.sub(r"\s+", " ", s).strip(" ,;:-")
    s = re.split(r"(?i)\s*[,;\.]\s*", s, maxsplit=1)[0].strip(" ,;:-")
    s = re.split(
        r"(?i)\b(?:se\s+trouve|elle\s+se\s+trouve|qui\s+se\s+trouve|est\s+situ[ée]e?|located|based|basee|bas[eé]e?)\b",
        s,
        maxsplit=1,
    )[0].strip(" ,;:-")
    s = re.split(
        r"(?i)\b(?:au|en|dans|avec|and|et|code|bank\s*code|code\s*banque|bank_code|devise|currency|pays|country)\b",
        s,
        maxsplit=1,
    )[0].strip(" ,;:-")
    return s.upper() if s else ""


def _clean_city_name(raw: str) -> str:
    s = (raw or "").strip()
    if not s:
        return ""
    s = re.sub(r"(?i)^(?:au|a|à|en|dans|in)\s+", "", s).strip()
    s = re.split(
        r"(?i)\b(?:code|region|région|agence|agency|bank|banque|devise|currency|pays|country)\b",
        s,
        maxsplit=1,
    )[0]
    s = re.sub(r"[^A-Za-zÀ-ÿ\-_ ]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip(" ,;:-")
    return s.title() if s else ""


def _is_known_country_name(text: str) -> bool:
    c = normalize_country(text or "")
    if not c:
        return False
    return c.strip().lower() == (text or "").strip().lower()


def _extract_bank_name(text: str):
    txt = (text or "").replace("â€™", "'").replace("’", "'")

    m_bank_called = re.search(r"(?i)\b(?:banque|bank)\s+s.?appelle\s+([A-Za-z0-9À-ÿ\-_ ']{2,})", txt)
    if m_bank_called:
        nbc = _clean_bank_name((m_bank_called.group(1) or "").strip())
        if nbc:
            return nbc

    m_brand_bank = re.search(r"(?i)\b([A-Za-z0-9][A-Za-z0-9À-ÿ'\- ]{1,40})\s+(bank|banque)\b", txt)
    if m_brand_bank:
        left = (m_brand_bank.group(1) or "").strip()
        left = re.sub(r"(?i)\b(?:creer|créer|create|configurer|configure|nous|voulons|une|un|nouvelle?|la|le|les)\b", " ", left)
        left = re.sub(r"\s+", " ", left).strip(" ,;:-")
        if left:
            return _clean_bank_name(f"{left} {m_brand_bank.group(2)}")

    m_pre = re.search(r"(?i)\bqui\s+s.?appelle\s+([A-Za-z0-9À-ÿ\-_ ']{2,})", txt)
    if m_pre:
        npre = _clean_bank_name((m_pre.group(1) or "").strip())
        if npre:
            return npre

    m01 = re.search(r"(?i)\b(?:banque|bank)\s+sera\s+([A-Za-z0-9À-ÿ\-_']{2,})\b", txt)
    if m01:
        n1 = _clean_bank_name((m01.group(1) or "").strip())
        if n1:
            return n1

    m00 = re.search(r"(?i)\b(?:banque|bank)\s+nomm\S*\s+([A-Za-z0-9À-ÿ\-_ ']{2,})", txt)
    if m00:
        n = _clean_bank_name((m00.group(1) or "").strip())
        if n:
            return n

    m0 = re.search(r"(?i)\bsous\s+nom\s+([A-Za-z0-9\-_ ]{2,})", txt)
    if m0:
        name0 = m0.group(1).strip()
        name0 = re.split(
            r"\b(au|en|dans|avec|and|et|bank\s*code|code\s*banque|bank_code|code|devise|currency|pays|country|,|\.|\d{3,})\b",
            name0,
            flags=re.I,
        )[0].strip()
        name0 = _clean_bank_name(name0)
        if name0:
            return name0

    m = re.search(
        r"(?:s'?appelle|sous\s+le\s+nom|sous\s+nom|nomm(?:e|ee|[ée]e?)|appel(?:e|ee|[ée]e?)|nom(?:\s+de)?\s+la\s+banque|nom\s*[:=]|bank\s+name\s+is)\s+([A-Za-z0-9À-ÿ\-_ ']{2,})",
        txt,
        flags=re.I,
    )
    if m:
        name = m.group(1).strip()
        name = re.split(
            r"\b(au|en|dans|avec|and|et|bank\s*code|code\s*banque|bank_code|code|devise|currency|pays|country|,|\.|\d{3,})\b",
            name,
            flags=re.I,
        )[0].strip()
        name = _clean_bank_name(name)
        if name:
            return name

    for m2 in re.finditer(r"(?i)\b(?:banque|bank)\s+([A-Za-z0-9\-_]{2,})\b", txt):
        candidate = _clean_bank_name((m2.group(1) or "").strip())
        if candidate and not candidate.isdigit() and candidate.lower() not in {"code", "name", "nomm", "nomme", "nommee", "nommée", "sera", "est", "is", "will", "avec"}:
            return candidate

    m3 = re.search(r"(?i)\bbank\s*name\s*(?:is|=|:)?\s*([A-Za-z0-9\-_]{2,})\b", txt)
    if m3:
        return _clean_bank_name(m3.group(1).strip())

    return None



def _extract_bank_code(text: str) -> Optional[str]:
    m = re.search(
        r"(?i)\b(?:bank[_\s-]*code|code\s*banque|bank\s*code|code\s*bank|bank_code)\s*(?:is|est)?\s*[:=]?\s*([0-9]{2,20})\b",
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
    m4 = re.search(r"(?i)\bcode\s*[:=]?\s*([0-9]{3,20})\b(?=.*\bagence\b)", text)
    if m4:
        return m4.group(1).strip()
    m5 = re.search(r"(?i)\b(?:son\s+code|le\s+code|code)\s*(?:is|est)?\s*[:=]?\s*([0-9]{3,20})\b", text)
    if m5:
        return m5.group(1).strip()
    return None


def _extract_currency(text: str):
    m0 = re.search(r"(?i)\b(?:devise|currency|monnaie)\b[^\n]{0,30}\b(MAD|EUR|USD|GBP|CHF|CAD|AUD|GHS|TND)\b", text)
    if m0:
        return normalize_currency(m0.group(1))

    m = re.search(r"\b(MAD|EUR|USD|GBP|CHF|CAD|AUD|GHS|TND)\b", text, flags=re.I)
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
        v = _clean_city_name(_cut_value(m.group(1)))
        v = re.sub(r"\s+\d{1,10}$", "", v).strip()
        return v.title() if v else None

    has_agency_context = bool(re.search(r"(?i)\b(agence|agency|code\s*agence|nom\s*agence)\b", text))
    m2 = re.search(r"(?i)\b(?:au|à|a|en|dans|in)\s+([A-Za-zÀ-ÿ\-_]{2,})\b", text)
    if m2:
        c = _clean_city_name(m2.group(1))
        if c:
            if has_agency_context:
                if _is_known_country_name(c):
                    return None
                return c
            # Without agency context, avoid obvious country captures.
            country_guess = normalize_country(c)
            if not country_guess or country_guess.lower() == c.lower():
                return c
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


def _extract_region_code(text: str) -> Optional[str]:
    m = re.search(r"(?i)\b(?:code\s*r[ée]gion|region[_\s-]*code)\s*[:=]?\s*(\d{1,10})\b", text)
    if m:
        return m.group(1).strip()

    m2 = re.search(r"(?i)\b(?:region|r[ée]gion)\b[^\n]{0,80}?\bcode\s*[:=]?\s*(\d{1,10})\b", text)
    if m2:
        return m2.group(1).strip()
    return None


def _extract_agency_name(text: str) -> Optional[str]:
    m00 = re.search(r"(?i)\bagence\s+principale\s+(?:sera|est)\s+([A-Za-z0-9À-ÿ\-_ ']{2,})", text)
    if m00:
        v00 = (m00.group(1) or "").strip()
        v00 = re.split(r"(?i)\b(?:dont|avec|code|region|r[ée]gion|identifi\w+)\b", v00, maxsplit=1)[0].strip()
        v00 = re.sub(r"\b\d{2,10}\b.*$", "", v00).strip()
        v00 = re.sub(r"(?i)^agence\s+", "", v00).strip()
        return v00.upper() if v00 else None

    m01 = re.search(r"(?i)\bagence\s+(?:principale\s+)?appel(?:e|ee|[ée]e?)\s+([A-Za-z0-9À-ÿ\-_ ']{2,})", text)
    if m01:
        v01 = (m01.group(1) or "").strip()
        v01 = re.split(r"(?i)\b(?:dont|avec|code|region|r[ée]gion|identifi\w+)\b", v01, maxsplit=1)[0].strip()
        v01 = re.sub(r"\b\d{2,10}\b.*$", "", v01).strip()
        v01 = re.sub(r"(?i)^agence\s+", "", v01).strip()
        return v01.upper() if v01 else None

    m0 = re.search(
        r"(?i)\bagence\s+nomm\S*\s+([A-Za-z0-9À-ÿ\-_ ']{2,})",
        text,
    )
    if m0:
        v0 = _cut_value(m0.group(1))
        v0 = re.sub(r"(?i)^(sous\s+le\s+nom|nomm\S*)\s+", "", v0).strip()
        v0 = re.sub(r"\b\d{2,10}\b.*$", "", v0).strip()
        v0 = re.sub(r"\bde\b\s*$", "", v0, flags=re.I).strip()
        return v0.upper() if v0 else None

    m0 = re.search(
        r"(?i)\bagence\s+sous\s+le\s+nom\s+([A-Za-z0-9À-ÿ\-_ ]{2,})",
        text,
    )
    if m0:
        v0 = _cut_value(m0.group(1))
        v0 = re.sub(r"(?i)^(sous\s+le\s+nom)\s+", "", v0).strip()
        v0 = re.sub(r"\b\d{2,10}\b.*$", "", v0).strip()
        v0 = re.sub(r"\bde\b\s*$", "", v0, flags=re.I).strip()
        return v0.upper() if v0 else None

    m = re.search(
        r"(?i)\b(?:agency[_\s-]*name|agence[_\s-]*name|nom\s+agence|agency|agence)\s*[:=]?\s*([A-Za-z0-9À-ÿ\-_ ']{2,})",
        text,
    )
    if m:
        v = re.split(
            r"\b(au|en|dans|avec|and|et|code|ville|city|region|devise|currency|pays|country|,|\.|\n)\b",
            m.group(1),
            flags=re.I,
        )[0].strip()
        v = re.sub(r"(?i)^(agence|agency)\s+", "", v).strip()
        v = re.sub(r"(?i)^(sous\s+le\s+nom|nomm\S*|s['’]?appelle)\s+", "", v).strip()
        v = re.sub(r"\b\d{2,10}\b.*$", "", v).strip()
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

    m2d = re.search(r"(?i)\bagence\b[^\n]{0,80}?\bcode\s*[:=]?\s*(\d{2,20})\b", text)
    if m2d:
        return m2d.group(1).strip().upper()

    # "agence Rabat Agdal 0025, ..."
    m2c = re.search(
        r"(?i)\bagence\s+[A-Za-z0-9À-ÿ\-_ ']{2,}?\s+(\d{2,20})\b(?=\s*[,;]|$)",
        text,
    )
    if m2c:
        return m2c.group(1).strip().upper()

    # Common compact phrasing: "agence X, 2589"
    m2b = re.search(
        r"(?i)\bagence\s+[A-Za-z0-9À-ÿ\-_ ']{2,}\s*[,;]\s*([A-Za-z0-9\-_]*\d[A-Za-z0-9\-_]{0,20})\b",
        text,
    )
    if m2b:
        return m2b.group(1).strip().upper()

    m = re.search(
        r"(?i)\b(?:agency[_\s-]*code|code\s*agence|agency\s*code)\s*(?:is|est)?\s*[:=]?\s*([A-Za-z0-9\-_]{2,20})\b",
        text,
    )
    if m:
        return m.group(1).strip().upper()
    return None


def _extract_resources(text: str) -> List[str]:
    if not re.search(r"(?i)\b(comptes?|accounts?|resources?|ressources?)\b", text):
        if re.search(r"(?i)\b(domestic|national|domestique|local|international|transactions?)\b", text):
            return ["TRANSACTIONS"]
        return []
    vals = []
    for token in ["CURRENT", "SAVINGS", "BUSINESS", "CARDS", "TRANSACTIONS", "ACCOUNTS"]:
        if re.search(rf"(?i)\b{token}\b", text):
            vals.append(token)
    if re.search(r"(?i)\b(domestic|national|domestique|local|international|transactions?)\b", text):
        if "TRANSACTIONS" not in vals:
            vals.append("TRANSACTIONS")
    return vals


def _extract_limit_daily_amounts(text: str) -> Dict[str, float]:
    out: Dict[str, float] = {}
    # Priority: explicit withdrawal/payment amounts.
    m_ret = re.search(
        r"(?i)\b(?:retraits?|withdrawals?)\b[^\d]{0,20}(\d+(?:[.,]\d+)?)|\b(\d+(?:[.,]\d+)?)\s*[A-Z]{0,4}[^\n]{0,25}\b(?:retraits?|withdrawals?)\b",
        text,
    )
    m_pay = re.search(
        r"(?i)\b(?:paiements?|payments?|purchase|achats?)\b[^\d]{0,20}(\d+(?:[.,]\d+)?)|\b(\d+(?:[.,]\d+)?)\s*[A-Z]{0,4}[^\n]{0,25}\b(?:paiements?|payments?|purchase|achats?)\b",
        text,
    )
    if m_ret and m_pay:
        try:
            ret = m_ret.group(1) or m_ret.group(2)
            pay = m_pay.group(1) or m_pay.group(2)
            if ret and pay:
                out["cards.0.limits.by_type.DEFAULT.domestic.daily_amount"] = float(ret.replace(",", "."))
                out["cards.0.limits.by_type.DEFAULT.international.daily_amount"] = float(pay.replace(",", "."))
                return out
        except Exception:
            pass

    m_dom = re.search(r"(?i)\b(?:domestic|national|domestique|local)\b[^\n]{0,100}?(\d[\d\s,\.]*)(?:\s*[A-Z]{3})?\s*/?\s*(?:jour|daily|quotidien)", text)
    if m_dom:
        try:
            out["cards.0.limits.by_type.DEFAULT.domestic.daily_amount"] = float(m_dom.group(1).replace(" ", "").replace(",", ""))
        except Exception:
            pass
    m_int_all = list(re.finditer(r"(?i)\binternational\b[^\n]{0,100}?(\d[\d\s,\.]*)(?:\s*[A-Z]{3})?\s*/?\s*(?:jour|daily|quotidien)", text))
    if m_int_all:
        try:
            out["cards.0.limits.by_type.DEFAULT.international.daily_amount"] = float(
                m_int_all[-1].group(1).replace(" ", "").replace(",", "")
            )
        except Exception:
            pass

    # Fallback for phrasing like:
    # "local et international, limite 10000 pour retraits et 30000 pour paiements"
    if (
        "cards.0.limits.by_type.DEFAULT.domestic.daily_amount" not in out
        and "cards.0.limits.by_type.DEFAULT.international.daily_amount" not in out
        and re.search(r"(?i)\b(local|domestic|national|domestique)\b", text)
        and re.search(r"(?i)\binternational\b", text)
    ):
        m_ret = re.search(r"(?i)(\d+(?:[.,]\d+)?)\s*[A-Z]{0,4}[^\n]{0,35}\b(retraits?|withdrawals?)\b", text)
        m_pay = re.search(r"(?i)(\d+(?:[.,]\d+)?)\s*[A-Z]{0,4}[^\n]{0,35}\b(paiements?|payments?|purchase|achats?)\b", text)
        if m_ret and m_pay:
            try:
                out["cards.0.limits.by_type.DEFAULT.domestic.daily_amount"] = float(m_ret.group(1).replace(",", "."))
                out["cards.0.limits.by_type.DEFAULT.international.daily_amount"] = float(m_pay.group(1).replace(",", "."))
            except Exception:
                pass
    return out


def _extract_fee_amounts(text: str) -> Dict[str, float]:
    out: Dict[str, float] = {}
    m_iss = re.search(r"(?i)\b(?:issuance|registration)\b[^\d]{0,10}(\d+(?:[.,]\d+)?)", text)
    if m_iss:
        out["cards.0.fees.registration_fee"] = float(m_iss.group(1).replace(",", "."))
    m_mon = re.search(r"(?i)\b(?:monthly|periodic)\b[^\d]{0,10}(\d+(?:[.,]\d+)?)", text)
    if m_mon:
        out["cards.0.fees.periodic_fee"] = float(m_mon.group(1).replace(",", "."))
    m_rep = re.search(r"(?i)\b(?:replacement|remplacement)\b[^\d]{0,12}(\d+(?:[.,]\d+)?)", text)
    if m_rep:
        out["cards.0.fees.replacement_fee"] = float(m_rep.group(1).replace(",", "."))
    m_pin = re.search(r"(?i)\b(?:pin\s*recalculation|recalcul\s*pin)\b[^\d]{0,12}(\d+(?:[.,]\d+)?)", text)
    if m_pin:
        out["cards.0.fees.pin_recalculation_fee"] = float(m_pin.group(1).replace(",", "."))
    return out



def _extract_card_profile_fields(text: str) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    t = text or ""

    plastics = []
    for p in ["PVC", "PETG", "RECYCLED PVC", "PLASTIC"]:
        if re.search(rf"(?i)\b{re.escape(p)}\b", t):
            plastics.append(p)
    if plastics:
        out["cards.0.card_info.plastic_type"] = ", ".join(dict.fromkeys(plastics))

    # product_type should stay at business type level only.
    products = []
    for p in ["debit", "prepaid", "credit"]:
        if re.search(rf"(?i)\b{re.escape(p)}\b", t):
            products.append(p.title())
    if products:
        out["cards.0.card_info.product_type"] = ", ".join(dict.fromkeys(products))

    # Card tiers are better represented as description, not product_type.
    tiers = []
    for tier in ["classic", "gold", "platinum"]:
        if re.search(rf"(?i)\b{re.escape(tier)}\b", t):
            tiers.append(tier.title())
    if tiers and "cards.0.card_info.card_description" not in out:
        out["cards.0.card_info.card_description"] = " ".join(dict.fromkeys(tiers))

    m_desc = re.search(r"(?i)\b(?:description(?:\s+carte|\s+card)?|card\s*description)\b\s*[:=]?\s*[\"“]?([^\"”\n\.]{3,})", t)
    if m_desc:
        out["cards.0.card_info.card_description"] = m_desc.group(1).strip()

    m_prod_code = re.search(r"(?i)\b(?:product[_\s-]*code|code\s*produit)\b\s*(?:is|est)?\s*[:=]?\s*([A-Za-z0-9\-_]{2,20})", t)
    if m_prod_code:
        out["cards.0.card_info.product_code"] = m_prod_code.group(1).strip().upper()

    return out


def _extract_services_enabled(text: str) -> List[str]:
    t = text or ""
    vals: List[str] = []
    mapping = [
        (r"(?i)\b3d\s*secure\b|\b3ds\b", "Authentification"),
        (r"(?i)\btokeni[sz]ation\b", "Tokenization"),
        (r"(?i)\bsms\s*(alert|notification)?\b", "SMS Notification"),
        (r"(?i)\be-?commerce\b", "E-commerce"),
    ]
    for pat, name in mapping:
        if re.search(pat, t):
            vals.append(name)
    return list(dict.fromkeys(vals))


def _extract_limit_types(text: str) -> List[str]:
    t = text or ""
    vals: List[str] = []
    if re.search(r"(?i)\b(retraits?|withdrawals?|atm)\b", t):
        vals.append("Retrait")
    if re.search(r"(?i)\b(paiements?|payments?|purchase|achats?)\b", t):
        vals.append("Purchase")
    if re.search(r"(?i)\bcash\s*advance\b", t):
        vals.append("CASH_advance")
    if re.search(r"(?i)\bquasi[-\s]*cash\b", t):
        vals.append("Quasi-cash")
    if re.search(r"(?i)\be-?commerce\b", t):
        vals.append("E-commerce")
    return vals


def _extract_more_limit_values(text: str) -> Dict[str, float]:
    out: Dict[str, float] = {}
    t = text or ""
    m_tot = re.search(r"(?i)\btotal\b[^\n]{0,80}?(\d+(?:[.,]\d+)?)", t)
    if m_tot:
        out["cards.0.limits.by_type.DEFAULT.total.daily_amount"] = float(m_tot.group(1).replace(",", "."))
    m_min = re.search(r"(?i)\b(?:min(?:imum)?\s*(?:par\s*transaction)?|minimum)\b[^\d]{0,15}(\d+(?:[.,]\d+)?)", t)
    if m_min:
        out["cards.0.limits.by_type.DEFAULT.per_transaction.min_amount"] = float(m_min.group(1).replace(",", "."))
    m_max = re.search(r"(?i)\b(?:max(?:imum)?\s*(?:par\s*transaction)?|maximum)\b[^\d]{0,15}(\d+(?:[.,]\d+)?)", t)
    if m_max:
        out["cards.0.limits.by_type.DEFAULT.per_transaction.max_amount"] = float(m_max.group(1).replace(",", "."))
    return out


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
    "cards.0.card_info.plastic_type": ["plastic type", "plastique", "matiere carte", "material"],
    "cards.0.card_info.product_type": ["product type", "type carte", "card type"],
    "cards.0.card_info.card_description": ["description carte", "card description"],
    "cards.0.card_info.product_code": ["product code", "code produit"],
    "cards.0.services.enabled": ["services", "services enabled", "activer services"],
    "cards.0.limits.selected_limit_types": ["limit types", "types limites", "type operation"],
    "cards.0.limits.by_type.DEFAULT.total.daily_amount": ["total daily amount", "plafond total journalier"],
    "cards.0.limits.by_type.DEFAULT.per_transaction.min_amount": ["min per transaction", "minimum par transaction"],
    "cards.0.limits.by_type.DEFAULT.per_transaction.max_amount": ["max per transaction", "maximum par transaction"],
    "cards.0.fees.replacement_fee": ["replacement fee", "frais remplacement"],
    "cards.0.fees.pin_recalculation_fee": ["pin recalculation fee", "frais recalcul pin"],
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
            if path == "bank.name":
                out[path] = _clean_bank_name(raw) or raw
                continue
            if path == "bank.agencies.0.city":
                out[path] = _clean_city_name(raw) or raw
                continue
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
            if path == "cards.0.card_info.plastic_type":
                plastic_mentioned = bool(re.search(r"(?i)\b(plastic|plastique|pvc|petg|recycled)\b", txt))
                if not plastic_mentioned and not explicit_mention:
                    continue
            if path.startswith("cards.0.fees."):
                fee_mentioned = bool(re.search(r"(?i)\b(fee|frais|issuance|registration|monthly|periodic|replacement|pin)\b", txt))
                if not fee_mentioned and not explicit_mention:
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

    reg_code = _extract_region_code(txt)
    if reg_code is not None:
        _try_set_candidate(state, template_obj, "bank.agencies.0.region_code", reg_code, source="user", confidence=1.0, evidence=txt, explicit_mention=True)

    resources = _extract_resources(txt)
    if resources:
        _try_set_candidate(state, template_obj, "bank.resources", resources, source="user", confidence=1.0, evidence=txt, explicit_mention=True)

    lims = _extract_limit_daily_amounts(txt)
    for path, amount in lims.items():
        _try_set_candidate(state, template_obj, path, amount, source="user", confidence=1.0, evidence=txt, explicit_mention=True)

    fees = _extract_fee_amounts(txt)
    for path, amount in fees.items():
        _try_set_candidate(state, template_obj, path, amount, source="user", confidence=1.0, evidence=txt, explicit_mention=True)

    card_profile = _extract_card_profile_fields(txt)
    for path, value in card_profile.items():
        _try_set_candidate(state, template_obj, path, value, source="user", confidence=1.0, evidence=txt, explicit_mention=True)

    enabled_services = _extract_services_enabled(txt)
    if enabled_services:
        _try_set_candidate(
            state,
            template_obj,
            "cards.0.services.enabled",
            enabled_services,
            source="user",
            confidence=1.0,
            evidence=txt,
            explicit_mention=True,
        )

    limit_types = _extract_limit_types(txt)
    if limit_types:
        _try_set_candidate(
            state,
            template_obj,
            "cards.0.limits.selected_limit_types",
            limit_types,
            source="user",
            confidence=1.0,
            evidence=txt,
            explicit_mention=True,
        )

    more_limits = _extract_more_limit_values(txt)
    for path, amount in more_limits.items():
        _try_set_candidate(state, template_obj, path, amount, source="user", confidence=1.0, evidence=txt, explicit_mention=True)

    nets = re.findall(r"(?i)\b(VISA|MASTERCARD)\b", txt)
    if nets:
        _try_set_candidate(
            state,
            template_obj,
            "cards.0.card_info.network",
            str(nets[0]).upper(),
            source="user",
            confidence=1.0,
            evidence=txt,
            explicit_mention=True,
        )

    # 4) Deterministic fallback: infer city from agency name when city is still missing.
    city_now = _get_by_path(state["facts"], "bank.agencies.0.city")
    agency_name_now = _get_by_path(state["facts"], "bank.agencies.0.agency_name")
    if is_missing_value(city_now) and isinstance(agency_name_now, str) and agency_name_now.strip():
        tokens = re.findall(r"[A-Za-zÀ-ÿ\-]+", agency_name_now.strip())
        if tokens:
            candidate_city = _clean_city_name(tokens[0])
            if candidate_city and not _is_known_country_name(candidate_city):
                _try_set_candidate(
                    state,
                    template_obj,
                    "bank.agencies.0.city",
                    candidate_city,
                    source="regex",
                    confidence=0.75,
                    evidence=txt,
                    explicit_mention=False,
                )
