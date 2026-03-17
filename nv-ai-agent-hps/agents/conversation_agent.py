# agents/conversation_agent.py
import re
import copy
import time
import os
import unicodedata
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
    "maghrib": "Maroc",
    "france": "France",
    "usa": "United States",
    "us": "United States",
    "united states": "United States",
    "etats unis": "United States",
    "Ã©tats unis": "United States",
    "suisse": "Suisse",
    "switzerland": "Suisse",
    "ghana": "Ghana",
    "tunisie": "Tunisie",
    "tunisia": "Tunisie",
    "algerie": "AlgÃ©rie",
    "algeria": "AlgÃ©rie",
    "espagne": "Espagne",
    "spain": "Espagne",
}

from config import USE_LLM, LLM_MIN_CONF, LLM_MAX_ATTEMPTS, LLM_RETRY_BACKOFF_S
from security.sanitize import sanitize_text
from agents.llm_extractor import extract_with_llm, extract_with_llm_status
from agents.llm_gates import apply_llm_gates
from agents.schema_validator import validate_value
from agents.powercard_constraints import (
    NETWORK_ENUM,
    PLASTIC_TYPE_ENUM,
    PRODUCT_TYPE_ENUM,
    RESOURCE_ENUM,
    SERVICE_FLAG_KEYS,
    is_powercard_profile,
    normalize_network,
    normalize_resource_item,
    normalize_services_input,
    services_to_flags,
)
from agents.value_store import (
    get_value as vs_get_value,
    get_meta as vs_get_meta,
    set_value as vs_set_value,
    is_authoritative,
    normalize_source,
)


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
                # Empty list in template means "list of primitives": keep parent path.
                if path:
                    out.add(".".join(path))
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


def _is_strict_profile(state: dict) -> bool:
    return is_powercard_profile(state or {})


def _set_validation_error(state: dict, path: str, message: str) -> None:
    meta = state.setdefault("meta", {})
    meta["last_validation_error"] = {"path": path, "message": message}


def _clear_validation_error(state: dict, path: str) -> None:
    meta = state.setdefault("meta", {})
    err = meta.get("last_validation_error")
    if isinstance(err, dict) and err.get("path") == path:
        meta.pop("last_validation_error", None)


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
        "source": normalize_source(source),
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


def _repair_mojibake(text: str) -> str:
    t = (text or "").strip()
    if not t:
        return ""

    t = (
        t.replace("\u2019", "'")
        .replace("\u2018", "'")
        .replace("\u201c", '"')
        .replace("\u201d", '"')
    )

    # Typical UTF-8 decoded as latin1 artifacts: "appelÃ©e", "Lâ€™..."
    if ("\u00c3" in t) or ("\u00e2" in t):
        try:
            repaired = t.encode("latin1").decode("utf-8")
            if repaired:
                return repaired
        except Exception:
            pass
    return t


def _country_candidate_text(text: str) -> str:
    raw = _repair_mojibake(text or "")
    words = re.findall(r"[A-Za-z\-]{2,}", raw)
    if not words:
        return raw.strip()

    stopwords = {
        "le",
        "la",
        "les",
        "de",
        "du",
        "des",
        "pour",
        "au",
        "aux",
        "en",
        "dans",
        "sur",
        "sera",
        "est",
        "pays",
        "country",
        "retenu",
        "retenu",
        "finalement",
        "comme",
        "notre",
        "nous",
        "utiliserons",
        "utilisera",
    }
    filtered = [w for w in words if w.lower() not in stopwords]
    return " ".join(filtered[:3]).strip()


def normalize_country(x: str) -> str:
    if not x:
        return ""

    raw = _repair_mojibake(x)
    low = raw.lower()
    candidate = _country_candidate_text(raw)
    candidate_low = candidate.lower()

    if low in _FALLBACK_COUNTRIES:
        return _FALLBACK_COUNTRIES[low]
    if candidate_low in _FALLBACK_COUNTRIES:
        return _FALLBACK_COUNTRIES[candidate_low]

    if pycountry is not None and candidate:
        try:
            c = pycountry.countries.lookup(candidate)
            return c.name
        except Exception:
            pass

    words = re.findall(r"[A-Za-z\-]{3,}", candidate)
    if words:
        for w in words:
            lw = w.lower()
            if lw in _FALLBACK_COUNTRIES:
                return _FALLBACK_COUNTRIES[lw]

        if pycountry is not None and len(words) == 1:
            try:
                c = pycountry.countries.lookup(words[0])
                return c.name
            except Exception:
                pass

    return ""


def is_missing_value(v) -> bool:
    if isinstance(v, dict) and "value" in v:
        return is_missing_value(v.get("value"))
    if v is None:
        return True
    if isinstance(v, str) and v.strip().lower() in {"", "none", "null", "n/a", "na", "nil", "unknown"}:
        return True
    if isinstance(v, list):
        if len(v) == 0:
            return True
        return all(is_missing_value(x) for x in v)
    if isinstance(v, dict) and len(v) == 0:
        return True
    return False


# -------------------------
# Path helpers
# -------------------------
def _get_by_path(obj, path: str):
    return vs_get_value(obj, path)


def _ensure_list_index(lst: list, idx: int, template_item):
    while len(lst) <= idx:
        lst.append(copy.deepcopy(template_item))


def set_by_path(obj, path: str, value, template_obj) -> bool:
    return vs_set_value(obj, path, value, source="user", confidence=1.0)


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
            return t

    if isinstance(template_value, float):
        clean = t.lower().replace("dh", "").replace("dhs", "")
        clean = clean.replace(" ", "").replace(",", ".")
        if clean.endswith("k"):
            try:
                return float(clean[:-1]) * 1000
            except Exception:
                return t
        try:
            return float(clean)
        except Exception:
            return t

    if isinstance(template_value, list):
        items = [x.strip() for x in re.split(r"[,\n;]+", t) if x.strip()]
        return items

    return t


def _clean_targeted_list_answer(path: str, values: List[Any]) -> List[Any]:
    cleaned: List[Any] = []
    for item in values:
        raw = str(item).strip().strip(" .")
        if not raw:
            continue

        if path == "cards.0.services.enabled":
            raw = re.sub(
                r"(?i)^(?:pour\s+les\s+services(?:\s+de\s+la\s+carte)?|les\s+services|services?)\s*[:=]?\s*",
                "",
                raw,
            ).strip(" .")
            raw = re.sub(
                r"(?i)^(?:nous\s+voulons\s+activer|nous\s+voulons|merci\s+d['’]activer|veuillez\s+activer|activez?|activer)\s+",
                "",
                raw,
            ).strip(" .")
        elif path == "bank.resources":
            raw = re.sub(
                r"(?i)^(?:pour\s+les\s+ressources|les\s+ressources|resources?|ressources?)\s*[:=]?\s*",
                "",
                raw,
            ).strip(" .")
            raw = re.sub(
                r"(?i)^(?:nous\s+voulons\s+activer|nous\s+voulons|merci\s+d['’]activer|veuillez\s+activer|activez?|activer)\s+",
                "",
                raw,
            ).strip(" .")
        elif path == "cards.0.limits.selected_limit_types":
            raw = re.sub(
                r"(?i)^(?:pour\s+les\s+types\s+de\s+limites|les\s+types\s+de\s+limites|types?\s+de\s+limites|types?\s+limites|limit\s+types?)\s*[:=]?\s*",
                "",
                raw,
            ).strip(" .")
            raw = re.sub(
                r"(?i)^(?:nous\s+retenons|nous\s+voulons|merci\s+de\s+retenir|veuillez\s+retenir|retenez?)\s+",
                "",
                raw,
            ).strip(" .")

        cleaned.append(raw)
    return cleaned


def postprocess(path: str, value):
    if isinstance(value, str):
        if path == "bank.name":
            cleaned = _clean_bank_name(value)
            return cleaned
        if path == "bank.agencies.0.city":
            cleaned_city = _clean_city_name(value)
            if cleaned_city:
                return cleaned_city
            return value.strip().title()
        if path == "bank.agencies.0.agency_name":
            cleaned_agency = re.sub(
                r"(?i)^(?:nom\s+agence|agency[_\s-]*name|nom\s+de\s+l['’]agence)\s*[:=]?\s*",
                "",
                value.strip(),
            ).strip(" ,;:-")
            if _looks_like_sentence_noise(value):
                extracted_agency = _extract_agency_name(value)
                if extracted_agency:
                    return extracted_agency
            finalized_agency = _finalize_agency_name(value, cleaned_agency)
            return finalized_agency if finalized_agency else value.strip().upper()
        if path.endswith(".currency") or path.endswith("bank.currency"):
            return normalize_currency(value)
        if path.endswith(".country") or path.endswith("bank.country"):
            return normalize_country(value)
        if path == "cards.0.card_info.network":
            nv = value.strip().upper().replace("_", " ")
            mapping = {
                "AMERICAN EXPRESS": "AMEX",
                "MASTER CARD": "MCRD",
                "MASTERCARD": "MCRD",
                "DINERS CLUB": "DINERS",
                "TAG YUP": "TAG-YUP",
                "TAGYUP": "TAG-YUP",
            }
            return normalize_network(mapping.get(nv, nv))
        if path == "cards.0.card_info.product_type":
            v = value.strip().lower()
            mapping = {
                "debit": "DEBIT",
                "dÃ©bit": "DEBIT",
                "credit": "CREDIT",
                "crÃ©dit": "CREDIT",
                "prepaid": "PREPAID",
                "prÃ©payÃ©e": "PREPAID",
                "prepayee": "PREPAID",
            }
            return mapping.get(v, value.strip().upper())
        if path == "cards.0.card_info.plastic_type":
            v = value.strip().lower()
            mapping = {
                "printed": "PVC",
                "pvc": "PVC",
                "embossed": "PETG",
                "emboss": "PETG",
                "petg": "PETG",
                "metal": "MTL",
                "mÃ©tal": "MTL",
                "virtual": "VRT",
                "virtuelle": "VRT",
                "virtuel": "VRT",
                "other": "OTH",
                "autre": "OTH",
                "plastic": "PVC",
            }
            return mapping.get(v, value.strip().upper())
        if path == "cards.0.card_info.renewal_option":
            v = value.strip().lower()
            mapping = {
                "auto": "AUTO",
                "automatic": "AUTO",
                "automatique": "AUTO",
                "y": "AUTO",
                "yes": "AUTO",
                "oui": "AUTO",
                "manual": "MANUAL",
                "manuel": "MANUAL",
                "manuelle": "MANUAL",
                "n": "MANUAL",
                "no": "MANUAL",
                "non": "MANUAL",
            }
            return mapping.get(v, value.strip().upper())
        if path == "cards.0.fees.billing_period":
            v = value.strip().upper()
            period_norm = {
                "MONTHLY": "M", "MENSUEL": "M", "MENSUELLE": "M",
                "YEARLY": "A", "ANNUAL": "A", "ANNUEL": "A", "ANNUELLE": "A",
                "QUARTERLY": "T", "TRIMESTRIEL": "T", "TRIMESTRIELLE": "T",
                "SEMESTER": "S", "SEMESTRIAL": "S", "SEMESTRIEL": "S", "SEMESTRIELLE": "S",
            }
            return period_norm.get(v, v)
        if path == "bank.agencies.0.region":
            cleaned_region = _cut_value(value)
            cleaned_region = re.sub(r"(?i)^(?:region)\s+", "", cleaned_region).strip()
            cleaned_region = re.split(r"(?i)\b(?:avec|et|code)\b", cleaned_region, maxsplit=1)[0].strip()
            return cleaned_region.title() if cleaned_region else value.strip().title()
        if path == "bank.bank_code":
            return value.strip().upper()
        if path == "cards.0.card_info.product_code":
            return value.strip().upper()
        if path == "cards.0.card_info.service_code":
            return value.strip().upper()
        if path.startswith("cards.0.services.flags."):
            s = str(value).strip()
            if s in {"", "NULL", "NONE"}:
                return None
            return "1" if s == "1" else s
    if isinstance(value, list):
        return _clean_targeted_list_answer(path, value)
    return value


def validate_field_value(path: str, value) -> bool:
    # Fast guards before strict validator.
    s = str(value).strip().upper()

    if path == "cards.0.card_info.bin":
        return bool(re.fullmatch(r"\d{6,11}", s))

    if path == "cards.0.card_info.network":
        return normalize_network(s) in NETWORK_ENUM

    if path == "cards.0.card_info.product_type":
        return s in PRODUCT_TYPE_ENUM

    if path == "cards.0.card_info.plastic_type":
        return s in PLASTIC_TYPE_ENUM

    if "currency" in path:
        return bool(re.fullmatch(r"[A-Z]{3}", s))

    if path == "bank.resources":
        if not isinstance(value, list):
            return False
        return bool(value) and all(normalize_resource_item(v) in RESOURCE_ENUM for v in value)

    if path == "cards.0.services.enabled":
        if not isinstance(value, list):
            return False
        return all(str(v).strip().lower() in SERVICE_FLAG_KEYS for v in value)

    if path == "bank.bank_code":
        return bool(re.fullmatch(r"[A-Z0-9]{2,20}", s))

    if path in {"bank.agencies.0.agency_code", "bank.agencies.0.city_code", "bank.agencies.0.region_code"}:
        if not re.fullmatch(r"[A-Z0-9\-_]{2,20}", s):
            return False
        return True

    if path.endswith(".city"):
        return not _is_known_country_name(str(value).strip())

    return True


def _coerce_value_for_path(path: str, value):
    if value is None:
        return None

    fee_amount_paths = {
        "cards.0.fees.registration_fee",
        "cards.0.fees.periodic_fee",
        "cards.0.fees.replacement_fee",
        "cards.0.fees.pin_recalculation_fee",
    }
    if path in fee_amount_paths or path.endswith("_amount"):
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

    int_like_paths = {
        "cards.0.card_info.pvk_index",
        "cards.0.card_info.expiration",
        "cards.0.card_info.pre_expiration",
        "cards.0.fees.grace_period",
    }
    if path in int_like_paths:
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


def _normalize_list_field(path: str, values: List[Any]) -> List[Any]:
    normalized, _invalid = _normalize_list_field_with_invalids(path, values)
    return normalized


def _normalize_list_field_with_invalids(path: str, values: List[Any]) -> Tuple[List[Any], List[str]]:
    if not isinstance(values, list):
        return values, []

    if path == "bank.resources":
        canon = []
        invalid = []
        alias_map = {
            "visa base1": "VISA_BASE1",
            "visa_base1": "VISA_BASE1",
            "visa sms": "VISA_SMS",
            "visa_sms": "VISA_SMS",
            "mcd mds": "MCD_MDS",
            "mcd_mds": "MCD_MDS",
            "mcd cis": "MCD_CIS",
            "mcd_cis": "MCD_CIS",
            "host bank": "HOST_BANK",
            "host_bank": "HOST_BANK",
        }
        for v in values:
            raw = str(v).strip()
            s = raw.lower().replace("-", " ")
            if not s:
                continue
            normalized = alias_map.get(s, normalize_resource_item(s))
            if normalized in RESOURCE_ENUM:
                canon.append(normalized)
            else:
                invalid.append(raw)
        return list(dict.fromkeys(canon)), invalid

    if path == "cards.0.services.enabled":
        canon = []
        invalid = []
        for v in values:
            raw = str(v).strip()
            if not raw:
                continue
            normalized = normalize_services_input([raw])
            if normalized:
                canon.extend(normalized)
            else:
                invalid.append(raw)
        return list(dict.fromkeys(canon)), invalid

    if path == "cards.0.limits.selected_limit_types":
        canon = []
        invalid = []
        for v in values:
            raw = str(v).strip()
            s = raw.lower().replace("_", " ")
            if not s:
                continue
            found = []
            if re.search(r"\b(retrait|withdraw|atm)\b", s):
                found.append("Retrait")
            if re.search(r"\b(paiement|payment|purchase|achat)\b", s):
                found.append("Purchase")
            if re.search(r"\be-?commerce\b", s):
                found.append("E-commerce")
            if re.search(r"\bcash\s*advance\b", s):
                found.append("CASH_advance")
            if re.search(r"\bquasi[-\s]*cash\b", s):
                found.append("Quasi-cash")
            if found:
                canon.extend(found)
            else:
                invalid.append(raw)
        return list(dict.fromkeys(canon)), invalid

    return values, []


# âœ… helper central: validate + set + provenance
def _safe_set_if_valid(
    state: dict,
    template_obj: dict,
    path: str,
    value,
    source: str = "user",
    confidence: float = 1.0,
    evidence: Optional[str] = None,
    explicit_mention: bool = False,
) -> bool:
    facts = state["facts"]
    source = normalize_source(source)
    record_user_error = source in {"user", "menu"}
    strict_profile = _is_strict_profile(state)
    menu_paths = list((state.get("meta", {}) or {}).get("menu_selected_paths") or [])
    if source == "user" and path in menu_paths:
        source = "menu"
    value = _coerce_value_for_path(path, value)

    # Reject placeholder values coming from weak extraction ("None", "null", etc.).
    if isinstance(value, str) and value.strip().lower() in {"none", "null", "n/a", "na", "nil", "unknown"}:
        if record_user_error:
            _set_validation_error(state, path, f"Valeur invalide pour {path}: valeur vide/non exploitable.")
        return False
    if isinstance(value, list):
        cleaned_list = []
        for x in value:
            xv = x.get("value") if isinstance(x, dict) and "value" in x else x
            if isinstance(xv, str) and xv.strip().lower() in {"", "none", "null", "n/a", "na", "nil", "unknown"}:
                continue
            cleaned_list.append(xv)
        if not cleaned_list:
            if record_user_error:
                _set_validation_error(state, path, f"Valeur invalide pour {path}: liste vide.")
            return False
        value, invalid_items = _normalize_list_field_with_invalids(path, cleaned_list)
        if strict_profile and invalid_items:
            if record_user_error:
                joined = ", ".join(str(x) for x in invalid_items[:3])
                _set_validation_error(
                    state,
                    path,
                    f"Valeur invalide pour {path}: valeurs non supportees detectees ({joined}).",
                )
            return False
        if not value:
            if record_user_error:
                _set_validation_error(state, path, f"Valeur invalide pour {path}: aucune valeur autorisee detectee.")
            return False

    if strict_profile and source == "llm" and not explicit_mention:
        guarded_prefixes = (
            "bank.",
            "cards.0.card_info.",
            "cards.0.card_range.",
            "cards.0.fees.",
            "cards.0.limits.",
            "cards.0.services.",
        )
        if path.startswith(guarded_prefixes):
            if record_user_error:
                _set_validation_error(
                    state,
                    path,
                    f"Valeur invalide pour {path}: valeur LLM rejetee sans mention explicite utilisateur.",
                )
            return False

    tmpl_value = _get_by_path(template_obj, path)
    ok, err = validate_value(
        path,
        value,
        tmpl_value,
        state=state,
        source=source,
        explicit_mention=explicit_mention,
    )
    if not ok:
        if record_user_error:
            _set_validation_error(state, path, err)
        return False

    if not validate_field_value(path, value):
        if record_user_error:
            _set_validation_error(state, path, f"Valeur invalide pour {path}: format non autorise.")
        return False

    done = vs_set_value(facts, path, value, source=source, confidence=confidence, evidence=evidence)
    if done:
        set_provenance(state, path, source=source, confidence=confidence, evidence=evidence)
        _clear_validation_error(state, path)
        if path in menu_paths:
            state.setdefault("meta", {})["menu_selected_paths"] = [p for p in menu_paths if p != path]
        if strict_profile and path == "cards.0.services.enabled":
            flags = services_to_flags(value)
            for key, flag_val in flags.items():
                flag_path = f"cards.0.services.flags.{key}"
                vs_set_value(facts, flag_path, flag_val, source="derived", confidence=confidence, evidence=evidence)
                set_provenance(state, flag_path, source="derived", confidence=confidence, evidence=evidence)
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
    if any(m in t for m in markers):
        return True
    words = re.findall(r"\w+", t)
    if len(words) <= 4:
        return False
    if re.search(r"[,.!?;:]", t):
        return True
    if any(w in {"je", "tu", "il", "elle", "on", "nous", "vous", "ils", "elles"} for w in words[:3]):
        return True
    return False


def _apply_targeted_llm_answer(state: dict, template_obj: dict, paths: list, user_text: str) -> int:
    """Use LLM to fill paths from user_text. Returns 0 on LLM failure so callers can use regex/ordered fallbacks."""
    if not USE_LLM:
        return 0
    txt = (user_text or "").strip()
    if not txt or not paths:
        return 0

    allowed = set(paths)
    llm_status, llm_out = extract_with_llm_status(txt, allowed, current_facts=state.get("facts", {}))
    if llm_status != "LLM_OK":
        # Graceful fallback: return 0 so apply_multi_field_answer can try regex / comma-separated parsing
        return 0
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
            explicit_mention=True,
        )
        if ok:
            applied += 1
    return applied


# -------------------------
# Public API used by brain/agent
# -------------------------
def apply_single_field_answer(state: dict, template_obj: dict, path: str, user_text: str) -> bool:
    # If user provides "agency name + city" in one phrase, split and fill both.
    if path == "bank.agencies.0.agency_name":
        txt = (user_text or "").strip()
        m_loc = re.search(r"(?i)\b(?:au|a|Ã |en|in)\s+([A-Za-z\-_]{2,})\b", txt)
        if m_loc:
            city_guess = _clean_city_name(m_loc.group(1))
            agency_guess = re.split(r"(?i)\b(?:au|a|Ã |en|in)\b", txt, maxsplit=1)[0].strip(" ,;:-")
            if agency_guess:
                _safe_set_if_valid(
                    state,
                    template_obj,
                    "bank.agencies.0.agency_name",
                    postprocess("bank.agencies.0.agency_name", cast_value(agency_guess, _get_by_path(template_obj, "bank.agencies.0.agency_name"))),
                    source="user",
                    confidence=1.0,
                    evidence=user_text,
                )
            if city_guess and not _is_known_country_name(city_guess):
                _safe_set_if_valid(
                    state,
                    template_obj,
                    "bank.agencies.0.city",
                    postprocess("bank.agencies.0.city", cast_value(city_guess, _get_by_path(template_obj, "bank.agencies.0.city"))),
                    source="user",
                    confidence=1.0,
                    evidence=user_text,
                )
            # if agency name got set, we are done for this targeted question
            current_name = _get_by_path(state["facts"], "bank.agencies.0.agency_name")
            if not is_missing_value(current_name):
                return True

    tmpl_value = _get_by_path(template_obj, path)

    if path == "cards.0.card_info.network":
        network_guess = _extract_network_value(user_text)
        if network_guess:
            v = postprocess(path, cast_value(network_guess, tmpl_value))
            return _safe_set_if_valid(state, template_obj, path, v, source="user", confidence=1.0, evidence=user_text)

    if isinstance(tmpl_value, str) and _is_identifier_like_path(path) and _looks_like_sentence_noise(user_text):
        # Avoid storing an entire conversational sentence in identifier-like fields.
        _set_validation_error(state, path, f"Valeur invalide pour {path}: reponse trop bruitée pour un champ identifiant.")
        return False

    v = cast_value(user_text, tmpl_value)
    v = postprocess(path, v)

    # refuse country vide
    if (path.endswith(".country") or path.endswith("bank.country")) and isinstance(v, str) and v.strip() == "":
        _set_validation_error(
            state,
            path,
            f"Valeur invalide pour {path}: champ requis. Exemple attendu: Maroc.",
        )
        return False
    if path == "bank.currency" and _looks_like_sentence_noise(user_text) and _extract_currency(user_text) is None:
        _set_validation_error(
            state,
            path,
            "Valeur invalide pour bank.currency: code devise ISO sur 3 lettres majuscules. Exemple attendu: MAD.",
        )
        return False

    # Side-fill deterministic codes when user provides both value and code in one answer.
    txt = (user_text or "").strip()
    if path == "bank.agencies.0.agency_name":
        agency_code = _extract_agency_code(txt)
        if agency_code:
            _safe_set_if_valid(
                state,
                template_obj,
                "bank.agencies.0.agency_code",
                agency_code,
                source="user",
                confidence=1.0,
                evidence=user_text,
            )
    elif path == "bank.agencies.0.city":
        city_guess = _extract_city(txt)
        if city_guess:
            v = postprocess(path, city_guess)
        elif _looks_like_sentence_noise(user_text):
            _set_validation_error(
                state,
                path,
                "Valeur invalide pour bank.agencies.0.city: ville non reconnue ou confuse avec un pays.",
            )
            return False
        city_code = _extract_city_code(txt)
        if city_code:
            _safe_set_if_valid(
                state,
                template_obj,
                "bank.agencies.0.city_code",
                city_code,
                source="user",
                confidence=1.0,
                evidence=user_text,
            )
    elif path == "bank.agencies.0.region":
        region_guess = _extract_region(txt)
        if region_guess:
            v = postprocess(path, region_guess)
        region_code = _extract_region_code(txt)
        if region_code:
            _safe_set_if_valid(
                state,
                template_obj,
                "bank.agencies.0.region_code",
                region_code,
                source="user",
                confidence=1.0,
                evidence=user_text,
            )

    strict_targeted_list_paths = {
        "bank.resources",
        "cards.0.services.enabled",
        "cards.0.limits.selected_limit_types",
    }
    if path in strict_targeted_list_paths and isinstance(v, list):
        return _safe_set_if_valid(state, template_obj, path, v, source="user", confidence=1.0, evidence=user_text)

    # PrioritÃ© au parsing dÃ©terministe de la rÃ©ponse utilisateur.

    # Fallback LLM uniquement si la voie dÃ©terministe Ã©choue.
    llm_applied = _apply_targeted_llm_answer(state, template_obj, [path], user_text)
    if llm_applied == 1:
        return True

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

    path_set = set(paths)
    agency_triplet = {
        "bank.agencies.0.agency_name",
        "bank.agencies.0.city",
        "bank.agencies.0.agency_code",
    }
    if path_set == agency_triplet:
        parts = [p.strip() for p in re.split(r"[,;/]+", txt) if p.strip()]
        if len(parts) >= 3:
            ordered = [
                ("bank.agencies.0.agency_name", parts[0]),
                ("bank.agencies.0.city", parts[1]),
                ("bank.agencies.0.agency_code", parts[2]),
            ]
            ok_all = True
            for path, raw in ordered:
                tmpl_value = _get_by_path(template_obj, path)
                v = postprocess(path, cast_value(raw, tmpl_value))
                ok_one = _safe_set_if_valid(
                    state, template_obj, path, v, source="user", confidence=1.0, evidence=user_text
                )
                if not ok_one:
                    return False
                ok_all = ok_all and ok_one
            return bool(ok_all)
        if len(parts) == 2 and re.fullmatch(r"[A-Za-z0-9\-_]{1,20}", parts[1]):
            pairs = [
                ("bank.agencies.0.agency_name", parts[0]),
                ("bank.agencies.0.agency_code", parts[1]),
            ]
            ok_all = True
            for path, raw in pairs:
                tmpl_value = _get_by_path(template_obj, path)
                v = postprocess(path, cast_value(raw, tmpl_value))
                ok_one = _safe_set_if_valid(
                    state, template_obj, path, v, source="user", confidence=1.0, evidence=user_text
                )
                if not ok_one:
                    return False
                ok_all = ok_all and ok_one
            return bool(ok_all)

    card_profile_triplet = {
        "cards.0.card_info.network",
        "cards.0.card_info.product_type",
        "cards.0.card_info.plastic_type",
    }
    if path_set == card_profile_triplet:
        network = None
        if re.search(r"(?i)\bmaster\s*card\b|\bmastercard\b", txt):
            network = "MCRD"
        elif re.search(r"(?i)\bamex\b|\bamerican\s*express\b", txt):
            network = "AMEX"
        elif re.search(r"(?i)\bdiners(?:\s*club)?\b", txt):
            network = "DINERS"
        elif re.search(r"(?i)\beuropay\b", txt):
            network = "EUROPAY"
        elif re.search(r"(?i)\bupi\b", txt):
            network = "UPI"
        elif re.search(r"(?i)\bjcb\b", txt):
            network = "JCB"
        elif re.search(r"(?i)\bprivative\b", txt):
            network = "PRIVATIVE"
        elif re.search(r"(?i)\bgimn\b", txt):
            network = "GIMN"
        elif re.search(r"(?i)\btag[-\s]*yup\b", txt):
            network = "TAG-YUP"
        elif re.search(r"(?i)\bvisa\b", txt):
            network = "VISA"

        products = []
        if re.search(r"(?i)\bd[Ã©e]bit\b", txt):
            products.append("DEBIT")
        if re.search(r"(?i)\bcr[Ã©e]dit\b|\bcredit\b", txt):
            products.append("CREDIT")
        if re.search(r"(?i)\bprepaid\b|\bpr[Ã©e]pay[Ã©e]e?\b", txt):
            products.append("PREPAID")
        products = list(dict.fromkeys(products))
        product = products[0] if len(products) == 1 else None

        plastic = None
        if re.search(r"(?i)\bpvc\b|\bplastic\b", txt):
            plastic = "PVC"
        elif re.search(r"(?i)\bpetg\b", txt):
            plastic = "PETG"
        elif re.search(r"(?i)\bm[Ã©e]tal\b|\bmetal\b", txt):
            plastic = "MTL"
        elif re.search(r"(?i)\b(?:virtual|virtuelle|virtuel)\b", txt):
            plastic = "VRT"
        elif re.search(r"(?i)\bautre\b|\bother\b", txt):
            plastic = "OTH"

        extracted = {
            "cards.0.card_info.network": network,
            "cards.0.card_info.product_type": product,
            "cards.0.card_info.plastic_type": plastic,
        }

        applied = 0
        for path in [
            "cards.0.card_info.network",
            "cards.0.card_info.product_type",
            "cards.0.card_info.plastic_type",
        ]:
            raw = extracted.get(path)
            if raw is None:
                continue
            tmpl_value = _get_by_path(template_obj, path)
            v = postprocess(path, cast_value(raw, tmpl_value))
            ok_one = _safe_set_if_valid(
                state, template_obj, path, v, source="user", confidence=1.0, evidence=user_text
            )
            if ok_one:
                applied += 1
        if applied > 0:
            return True

    tranche_pair = {
        "cards.0.card_range.tranche_min",
        "cards.0.card_range.tranche_max",
    }
    if path_set == tranche_pair:
        extracted = {}
        m_min = re.search(r"(?i)\bmin(?:imum)?\b[^\d]{0,8}(\d{1,22})\b", txt)
        if m_min:
            extracted["cards.0.card_range.tranche_min"] = m_min.group(1)
        m_max = re.search(r"(?i)\bmax(?:imum)?\b[^\d]{0,8}(\d{1,22})\b", txt)
        if m_max:
            extracted["cards.0.card_range.tranche_max"] = m_max.group(1)
        if len(extracted) < 2:
            nums = re.findall(r"\b\d{1,22}\b", txt)
            if len(nums) >= 2:
                extracted.setdefault("cards.0.card_range.tranche_min", nums[0])
                extracted.setdefault("cards.0.card_range.tranche_max", nums[1])

        if len(extracted) == 2:
            ok_all = True
            for path in [
                "cards.0.card_range.tranche_min",
                "cards.0.card_range.tranche_max",
            ]:
                raw = extracted.get(path)
                tmpl_value = _get_by_path(template_obj, path)
                v = postprocess(path, cast_value(raw, tmpl_value))
                ok_one = _safe_set_if_valid(
                    state, template_obj, path, v, source="user", confidence=1.0, evidence=user_text
                )
                if not ok_one:
                    return False
                ok_all = ok_all and ok_one
            return bool(ok_all)

    fee_form_paths = {
        "cards.0.fees.fee_description",
        "cards.0.fees.billing_event",
        "cards.0.fees.grace_period",
        "cards.0.fees.billing_period",
        "cards.0.fees.registration_fee",
        "cards.0.fees.periodic_fee",
        "cards.0.fees.replacement_fee",
        "cards.0.fees.pin_recalculation_fee",
    }
    if path_set.issubset(fee_form_paths):
        extracted = {}
        extracted.update(_extract_fee_fields(txt))
        extracted.update(_extract_fee_amounts(txt))

        # Convenience aliases for compact form-style replies.
        m_evt_short = re.search(r"(?i)\b(?:evt|evenement|event)\b\s*[:=]?\s*([123])\b", txt)
        if m_evt_short:
            extracted["cards.0.fees.billing_event"] = m_evt_short.group(1)

        m_period_short = re.search(r"(?i)\b(?:periode|period)\b\s*[:=]?\s*([MAST])\b", txt)
        if m_period_short:
            extracted["cards.0.fees.billing_period"] = m_period_short.group(1).upper()

        m_grace_short = re.search(r"(?i)\b(?:grace)\b\s*[:=]?\s*(\d+)\b", txt)
        if m_grace_short:
            extracted["cards.0.fees.grace_period"] = int(m_grace_short.group(1))

        short_amount_patterns = {
            "cards.0.fees.registration_fee": r"(?i)\b(?:inscription|registration)\b\s*[:=]?\s*(\d+(?:[.,]\d+)?)",
            "cards.0.fees.periodic_fee": r"(?i)\b(?:periodique|periodic|mensuel|monthly)\b\s*[:=]?\s*(\d+(?:[.,]\d+)?)",
            "cards.0.fees.replacement_fee": r"(?i)\b(?:remplacement|replacement)\b\s*[:=]?\s*(\d+(?:[.,]\d+)?)",
            "cards.0.fees.pin_recalculation_fee": r"(?i)\b(?:pin|recalcul\s*pin|pin\s*recalculation)\b\s*[:=]?\s*(\d+(?:[.,]\d+)?)",
        }
        for path, pattern in short_amount_patterns.items():
            m = re.search(pattern, txt)
            if m:
                extracted[path] = float(m.group(1).replace(",", "."))

        # If regex/keyword extraction managed to fill all requested paths, apply them.
        if all(p in extracted for p in paths):
            ok_all = True
            for path in paths:
                raw = extracted.get(path)
                tmpl_value = _get_by_path(template_obj, path)
                if isinstance(raw, str):
                    v = postprocess(path, cast_value(raw, tmpl_value))
                else:
                    v = postprocess(path, raw)
                ok_one = _safe_set_if_valid(
                    state, template_obj, path, v, source="user", confidence=1.0, evidence=user_text
                )
                if not ok_one:
                    return False
                ok_all = ok_all and ok_one
            return bool(ok_all)

        # Explicit comma-separated fee form: "1, 0, A, 50, 20, 17, 25" (7 values, no description) or 8 values.
        if path_set == fee_form_paths and len(paths) == 8:
            raw_parts = [p.strip() for p in re.split(r"[,;/]+", txt)]
            if len(raw_parts) == 7:
                raw_parts = ["Frais"] + raw_parts
            if len(raw_parts) >= 8:
                parts = raw_parts[:8]
                ok_all = True
                for path, part in zip(paths, parts):
                    tmpl_value = _get_by_path(template_obj, path)
                    v = postprocess(path, cast_value(part, tmpl_value))
                    ok_one = _safe_set_if_valid(
                        state, template_obj, path, v, source="user", confidence=1.0, evidence=user_text
                    )
                    if not ok_one:
                        return False
                    ok_all = ok_all and ok_one
                if ok_all:
                    return True

    # Special handling for pair "<label text> + <numeric/alnum code>" even in noisy sentences.
    if len(paths) == 2 and paths[1].endswith("_code"):
        p_name, p_code = paths[0], paths[1]

        code_alias = "code"
        if p_code.endswith("region_code"):
            code_alias = r"(?:code\s*r[Ã©e]gion|region[_\s-]*code|code)"
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
        name_chunk = re.sub(r"(?i)^(region|rÃ©gion|city|ville|agence|agency)\s*[:=]?\s*", "", name_chunk).strip(" ,;:-")

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

    # Keep empty parts so form submissions with blank fields still match path count (1:1).
    raw_parts = [p.strip() for p in re.split(r"[,;/]+", txt)]

    # Fee form: 8 paths but user often sends 7 values (omitting description). Prepend default so mapping is correct.
    if path_set == fee_form_paths and len(paths) == 8 and len(raw_parts) == 7:
        raw_parts = ["Frais"] + raw_parts  # fee_description default "Frais", then billing_event, grace_period, ...

    # fallback "Ville CODE" when exactly 2 paths and we got fewer parts
    if len(raw_parts) < len(paths) and len(paths) == 2:
        tokens = txt.split()
        if len(tokens) >= 2:
            raw_parts = [" ".join(tokens[:-1]).strip(), tokens[-1].strip()]

    # Pad with empty strings so we have exactly len(paths); take first len(paths) if too many.
    parts = (raw_parts + [""] * len(paths))[: len(paths)]

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


def _strip_bank_name_labels(s: str) -> str:
    return re.sub(r"(?i)^(?:nom\s+banque|bank\s+name|nom|name)\s*[:=]?\s*", "", s or "").strip()


def _clean_bank_name(raw: str) -> str:
    s = (raw or "").strip()
    if not s:
        return ""
    s = re.sub(r"(?i)^(?:pour|for)\s+(?:cette|ce|this)\s+(?:banque|bank)\b", "", s).strip()
    s = re.sub(r"(?i)^(?:je\s+veux\s+ajouter|je\s+veux|nous\s+voulons\s+ajouter|nous\s+voulons|ajouter|add|creer|create)\s+", "", s).strip()
    s = re.sub(r"(?i)^(?:nomm\S*|appel(?:e|ee|Ã©e)|called|nom\s+de\s+la\s+banque)\s*[:=]?\s*", "", s).strip()
    s = re.sub(r"(?i)^(the|la|le|les|une|un)\s+", "", s).strip()
    if not re.match(r"(?i)^(?:bank\s+of|banque\s+de)\b", s):
        s = re.sub(r"(?i)^(?:banque|bank)\s+", "", s).strip()
    s = re.sub(r"\s+", " ", s).strip(" ,;:-")
    s = re.split(r"(?i)\s*[,;\.]\s*", s, maxsplit=1)[0].strip(" ,;:-")
    s = re.split(
        r"(?i)\b(?:se\s+trouve|elle\s+se\s+trouve|qui\s+se\s+trouve|est\s+situ[Ã©e]e?|located|based|basee|bas[eÃ©]e?)\b",
        s,
        maxsplit=1,
    )[0].strip(" ,;:-")
    s = re.split(
        r"(?i)\b(?:au|en|dans|avec|and|et|code|bank\s*code|code\s*banque|bank_code|devise|currency|pays|country)\b",
        s,
        maxsplit=1,
    )[0].strip(" ,;:-")
    s = re.sub(r"(?i)^(?:nomm\S*|nom\s+de\s+la\s+banque)\s*[:=]?\s*", "", s).strip()
    if re.fullmatch(r"(?i)(?:pour|for)?\s*(?:cette|ce|this)?\s*(?:banque|bank)", s):
        return ""
    if re.fullmatch(r"(?i)(?:banque|bank)", s):
        return ""
    s = _strip_bank_name_labels(s)
    return s.upper() if s else ""


def _clean_city_name(raw: str) -> str:
    s = (raw or "").strip()
    if not s:
        return ""
    s = re.sub(r"(?i)^(?:au|a|en|dans|in)\s+", "", s).strip()
    s = re.sub(r"(?i)^(?:ville|city)\s+", "", s).strip()
    s = re.split(
        r"(?i)\b(?:avec|et|code|region|agence|agency|bank|banque|devise|currency|pays|country)\b",
        s,
        maxsplit=1,
    )[0]
    s = re.sub(r"[^A-Za-z0-9\-_' ]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip(" ,;:-")
    return s.title() if s else ""

def _is_known_country_name(text: str) -> bool:
    candidate = _country_candidate_text(text or "")
    if not candidate:
        return False
    return bool(normalize_country(candidate))


def _is_placeholder_city_candidate(text: str) -> bool:
    words = [w.strip("'").lower() for w in re.findall(r"[A-Za-z']+", text or "")]
    if not words:
        return True
    noise = {"de", "d", "l", "la", "le", "les", "ce", "cet", "cette", "this", "ville", "city", "agence", "agency"}
    return all(w in noise for w in words)


def _finalize_agency_name(text: str, raw_value: str) -> Optional[str]:
    value = (raw_value or "").strip()
    if not value:
        return None

    value = re.sub(r"\s+", " ", value).strip(" ,;:-")
    value = re.sub(
        r"(?i)^(?:s(?:['’]|\s+)?appell(?:e|era)|appel(?:e|ee|[ée]e?)|nomm\w*|sous\s+le\s+nom)\s+",
        "",
        value,
    ).strip()
    if not value:
        return None

    if _is_known_country_name(value):
        return None

    city_guess = _extract_city(text or "")
    explicit_name_cue = bool(
        re.search(
            r"(?i)\b(?:nom\s+agence|agency[_\s-]*name|appel(?:e|ee|e|ee)|nomm\w*|s.?appell(?:e|era)|sous\s+le\s+nom)\b",
            text or "",
        )
    )
    if city_guess and value.upper() == city_guess.upper() and not explicit_name_cue:
        return None

    if value.upper() in {"CETTE VILLE", "THIS CITY", "VILLE", "CITY"}:
        return None

    return value.upper()


def _extract_bank_name(text: str):
    txt = _repair_mojibake(text or "").replace("â€™", "'").strip()

    # 1) Explicit phrases: bank nommee ..., bank s'appelle ..., bank name is ...
    explicit_patterns = [
        r"(?i)\b(?:banque|bank)\s+nomm\w*\s+(.+)",
        r"(?i)\b(?:banque|bank)\s+(?:est|is)\s+nomm\w*\s+(.+)",
        r"(?i)\b(?:banque|bank)\s+appel(?:e|ee|Ã©e)\s+(.+)",
        r"(?i)\b(?:banque|bank)\s+called\s+(.+)",
        r"(?i)\b(?:banque|bank)\s+will\s+be\s+called\s+(.+)",
        r"(?i)\b(?:banque|bank)\s+s.?appelle\s+(.+)",
        r"(?i)\bbank\s*name\s*(?:is|=|:)\s*(.+)",
        r"(?i)\bnom(?:\s+de)?\s+la\s+banque\s*(?:is|est|=|:)\s*(.+)",
        r"(?i)\bnom\s+banque\s*(?:is|est|=|:)?\s*(.+)",
    ]
    for pat in explicit_patterns:
        m = re.search(pat, txt)
        if not m:
            continue
        cand = _clean_bank_name((m.group(1) or "").strip())
        if cand and cand not in {"BANK", "BANQUE"}:
            return cand

    # 2) "<name> bank" form
    for m_brand_bank in reversed(
        list(
            re.finditer(
                r"(?i)\b([A-Za-z0-9][A-Za-z0-9'\-]{1,}(?:\s+[A-Za-z0-9][A-Za-z0-9'\-]{1,}){0,3})\s+(bank|banque)\b",
                txt,
            )
        )
    ):
        resources_ctx = bool(re.search(r"(?i)\b(resources?|ressources?)\b", txt))
        left = (m_brand_bank.group(1) or "").strip()
        if re.search(r"(?i)\b(resources?|ressources?|accounts?|comptes?)\b", left):
            continue
        if re.search(r"(?i)\bcode$", left):
            continue
        left = re.sub(
            r"(?i)\b(?:bonjour|salut|hello|hey|bonsoir|je|tu|il|elle|nous|vous|the|veux|voudrais|voulons|souhaite|souhaitons|"
            r"ajouter|add|creer|create|configurer|configure|une|un|nouvelle?|la|le|les|banque|bank|est|is|nomm\w*)\b",
            " ",
            left,
        )
        left = re.sub(r"\s+", " ", left).strip(" ,;:-")
        cand = _clean_bank_name(f"{left} {m_brand_bank.group(2)}") if left else ""
        if resources_ctx and cand in {"HOST BANK"}:
            continue
        if cand and cand not in {"BANK", "BANQUE"}:
            return cand

    # 3) Last resort: first token after bank/banque (avoid placeholders)
    for m2 in re.finditer(r"(?i)\b(?:banque|bank)\s+([A-Za-z0-9\-_]{2,})\b", txt):
        prefix = txt[max(0, m2.start() - 24):m2.start()]
        if re.search(r"(?i)(?:bank[_\s-]*code|code(?:\s+de)?)\s*$", prefix):
            continue
        candidate = _clean_bank_name((m2.group(1) or "").strip())
        if candidate and not candidate.isdigit() and candidate.lower() not in {
            "code", "name", "nomm", "nomme", "nommee", "appelee", "appele", "called", "sera", "seront", "est", "is", "will", "avec", "bank", "banque",
            "active", "activer", "activate", "this", "cette", "cette-ci", "ce"
        }:
            return candidate

    return None

def _extract_bank_code(text: str) -> Optional[str]:
    m = re.search(
        r"(?i)\b(?:bank[_\s-]*code|code\s*banq(?:ue|u?e?)|bank\s*code|code\s*bank|bank_code|code\s+de\s+bank|code\s+de\s+banque)\s*(?:is|est|soit)?\s*[:=]?\s*([A-Za-z0-9]{2,20})\b",
        text,
    )
    if m:
        return m.group(1).strip().upper()

    m_de = re.search(
        r"(?i)\b(?:son\s+)?code(?:\s+de)?\s*(?:bank|banque)\s*(?:is|est|soit)?\s*[:=]?\s*([A-Za-z0-9]{2,20})\b",
        text,
    )
    if m_de:
        return m_de.group(1).strip().upper()

    # Common phrasing: "banque ... avec code ATB001 ..."
    m2 = re.search(
        r"(?i)\b(?:banque|bank)\b.{0,120}?\bavec\s+code\s*[:=]?\s*([A-Za-z0-9]{2,20})\b",
        text,
    )
    if m2:
        return m2.group(1).strip().upper()
    return None


def _extract_currency(text: str):
    m0 = re.search(r"(?i)\b(?:devise|currency|monnaie)\b\s*(?:is|est|=|:)?\s*(MAD|EUR|USD|GBP|CHF|CAD|AUD|GHS|TND|DH|DHS)\b", text)
    if m0:
        return normalize_currency(m0.group(1))

    m = re.search(r"\b(MAD|EUR|USD|GBP|CHF|CAD|AUD|GHS|TND)\b", text, flags=re.I)
    if m:
        limit_ctx = bool(
            re.search(
                r"(?i)\b(limit|limits|plafond|daily|weekly|monthly|jour|semaine|mois|minimum|maximum|min|max|transaction|paiements?|payments?|purchase|achats?|national|domestic|international)\b",
                text,
            )
        )
        bank_currency_ctx = bool(re.search(r"(?i)\b(devise|currency|monnaie|banque|bank)\b", text))
        if limit_ctx and not bank_currency_ctx:
            return None
        return normalize_currency(m.group(1))
    if re.search(r"\b(dh|dhs)\b", text, flags=re.I):
        limit_ctx = bool(
            re.search(
                r"(?i)\b(limit|limits|plafond|daily|weekly|monthly|jour|semaine|mois|minimum|maximum|min|max|transaction|paiements?|payments?|purchase|achats?|national|domestic|international)\b",
                text,
            )
        )
        bank_currency_ctx = bool(re.search(r"(?i)\b(devise|currency|monnaie|banque|bank)\b", text))
        if limit_ctx and not bank_currency_ctx:
            return None
        return "MAD"
    return None


def _extract_country(text: str):
    txt = _repair_mojibake(text or "")
    m = re.search(r"\b(?:au|en|in)\s+([A-Za-z\-]{3,})\b", txt, flags=re.I)
    if m:
        c = normalize_country(m.group(1))
        if c:
            return c

    for k, v in _FALLBACK_COUNTRIES.items():
        if re.search(rf"\b{k}\b", txt, flags=re.I):
            return v
    return None


def _extract_city(text: str) -> Optional[str]:
    txt = unicodedata.normalize("NFKD", _repair_mojibake(text or ""))
    txt = "".join(ch for ch in txt if not unicodedata.combining(ch))

    # Prefer explicit "situee a ..." / "located in ..." cues.
    m_explicit = re.search(
        r"(?i)\b(?:situee|situe|located|based)\s+(?:a|au|en|in)\s+([A-Za-z\-_]{2,})\b",
        txt,
    )
    if m_explicit:
        c_exp = _clean_city_name(m_explicit.group(1))
        if c_exp and not _is_known_country_name(c_exp):
            return c_exp

    m = re.search(
        r"(?i)\b(?:ville|city)\b(?:\s+de\s+l['’]agence)?\s*(?:[:=]|est|sera|is|will\s+be)?\s*([A-Za-z\-_ ]{2,})",
        txt,
    )
    if m:
        v = _clean_city_name(_cut_value(m.group(1)))
        v = re.sub(r"\s+\d{1,10}$", "", v).strip()
        if v and not _is_placeholder_city_candidate(v) and not _is_known_country_name(v):
            return v.title()
        return None

    # Compact triplet form: "Agence Centrale, Casablanca, 0001"
    m_triplet = re.search(
        r"(?i)\bagence\b[^,\n]*,\s*([A-Za-z\-_ ]{2,})\s*,\s*[A-Za-z0-9\-_]{2,20}\b",
        txt,
    )
    if m_triplet:
        c_trip = _clean_city_name(m_triplet.group(1))
        if c_trip and not _is_known_country_name(c_trip):
            return c_trip

    has_agency_context = bool(re.search(r"(?i)\b(agence|agency|code\s*agence|nom\s*agence)\b", txt))
    if not has_agency_context:
        return None

    for m2 in re.finditer(r"(?i)\b(?:au|a|en|dans|in)\s+([A-Za-z\-_]{2,})\b", txt):
        c = _clean_city_name(m2.group(1))
        if not c:
            continue
        if _is_placeholder_city_candidate(c):
            continue
        if _is_known_country_name(c):
            continue
        return c
    return None


def _extract_city_code(text: str) -> Optional[str]:
    m = re.search(
        r"(?i)\b(?:code\s*ville|city[_\s-]*code)\s*[:=]?\s*([A-Za-z0-9\-_]{1,20})\b",
        text,
    )
    if m:
        return m.group(1).strip().upper()

    return None


def _extract_region(text: str) -> Optional[str]:
    txt = unicodedata.normalize("NFKD", _repair_mojibake(text or ""))
    txt = "".join(ch for ch in txt if not unicodedata.combining(ch))
    m = re.search(r"(?i)\b(?:region|r\W*gion)\s*[:=]?\s*([A-Za-z\-_ ]{2,})", txt)
    if m:
        v = _cut_value(m.group(1))
        return v.title() if v else None
    return None


def _extract_region_code(text: str) -> Optional[str]:
    txt = unicodedata.normalize("NFKD", _repair_mojibake(text or ""))
    txt = "".join(ch for ch in txt if not unicodedata.combining(ch))
    m = re.search(
        r"(?i)\b(?:code\s*(?:region|r\W*gion)|(?:region|r\W*gion)[_\s-]*code)\s*[:=]?\s*([A-Za-z0-9\-_]{1,20})\b",
        txt,
    )
    if m:
        return m.group(1).strip().upper()

    m2 = re.search(r"(?i)\b(?:region|r\W*gion)\b[^\n]{0,80}?\bcode\s*[:=]?\s*([A-Za-z0-9\-_]{1,20})\b", txt)
    if m2:
        return m2.group(1).strip().upper()
    return None


def _extract_network_value(text: str) -> Optional[str]:
    txt = text or ""
    if re.search(r"(?i)\bmaster\s*card\b|\bmastercard\b", txt):
        return "MCRD"
    if re.search(r"(?i)\bamex\b|\bamerican\s*express\b", txt):
        return "AMEX"
    if re.search(r"(?i)\bdiners(?:\s*club)?\b", txt):
        return "DINERS"
    if re.search(r"(?i)\beuropay\b", txt):
        return "EUROPAY"
    if re.search(r"(?i)\bupi\b", txt):
        return "UPI"
    if re.search(r"(?i)\bjcb\b", txt):
        return "JCB"
    if re.search(r"(?i)\bprivative\b", txt):
        return "PRIVATIVE"
    if re.search(r"(?i)\bgimn\b", txt):
        return "GIMN"
    if re.search(r"(?i)\btag[-\s]*yup\b", txt):
        return "TAG-YUP"
    if re.search(r"(?i)\bvisa\b", txt):
        return "VISA"
    return None


def _has_explicit_network_context(text: str) -> bool:
    return bool(re.search(r"(?i)\b(?:network|reseau|r[ée]seau|profil\s*carte|card\s*profile)\b", text or ""))


def _has_network_profile_support(text: str) -> bool:
    return bool(
        re.search(
            r"(?i)\b(?:bin|debit|d[ée]bit|credit|cr[ée]dit|prepaid|plastic|plastique|pvc|petg|metal|virtual)\b",
            text or "",
        )
    )


def _has_card_description_context(text: str) -> bool:
    return bool(
        re.search(
            r"(?i)\b(?:nom\s*/\s*description(?:\s+de\s+la\s+carte)?|description(?:\s+commerciale)?(?:\s+de\s+la\s+carte|\s+carte|\s+card)?|card\s*description)\b",
            text or "",
        )
    )


def _extract_agency_name(text: str) -> Optional[str]:
    m00 = re.search(r"(?i)\bagence\s+principale\s+(?:sera|est)\s+([A-Za-z0-9\-_ ']{2,})", text)
    if m00:
        v00 = (m00.group(1) or "").strip()
        v00 = re.split(r"(?i)\b(?:dont|avec|code|region|r[Ã©e]gion|identifi\w+)\b", v00, maxsplit=1)[0].strip()
        v00 = re.sub(r"(?i)^(?:sera|est)?\s*(?:situ(?:e|Ã©)e?|located|based|bas(?:e|Ã©)e?)\s+(?:a|au|Ã |en|in)\s+", "", v00).strip()
        v00 = re.sub(r"\b\d{2,10}\b.*$", "", v00).strip()
        return _finalize_agency_name(text, v00)

    m00b = re.search(r"(?i)\bagence\s+principale\s+([A-Za-z0-9\-_ ']{2,})", text)
    if m00b:
        v00b = (m00b.group(1) or "").strip()
        v00b = re.sub(r"(?i)^(?:sera|est)?\s*(?:situ(?:e|Ã©)e?|located|based|bas(?:e|Ã©)e?)\s+(?:a|au|Ã |en|in)\s+", "", v00b).strip()
        v00b = re.split(r"(?i)\b(?:au|a|Ã |en|in|dans|avec|code|region|r[Ã©e]gion|identifi\w+)\b", v00b, maxsplit=1)[0].strip()
        v00b = re.sub(r"\b\d{2,10}\b.*$", "", v00b).strip()
        return _finalize_agency_name(text, v00b)

    m01 = re.search(r"(?i)\bagence\s+(?:principale\s+)?appel(?:e|ee|[Ã©e]e?)\s+([A-Za-z0-9\-_ ']{2,})", text)
    if m01:
        v01 = (m01.group(1) or "").strip()
        v01 = re.sub(r"(?i)^(?:sera|est)?\s*(?:situ(?:e|Ã©)e?|located|based|bas(?:e|Ã©)e?)\s+(?:a|au|Ã |en|in)\s+", "", v01).strip()
        v01 = re.split(r"(?i)\b(?:dont|avec|code|region|r[Ã©e]gion|identifi\w+)\b", v01, maxsplit=1)[0].strip()
        v01 = re.split(r"(?i)\b(?:au|a|Ã |en|in|dans)\b", v01, maxsplit=1)[0].strip()
        v01 = re.sub(r"\b\d{2,10}\b.*$", "", v01).strip()
        return _finalize_agency_name(text, v01)

    m0 = re.search(
        r"(?i)\bagence\s+nomm\S*\s+([A-Za-z0-9\-_ ']{2,})",
        text,
    )
    if m0:
        v0 = _cut_value(m0.group(1))
        v0 = re.sub(r"(?i)^(sous\s+le\s+nom|nomm\S*)\s+", "", v0).strip()
        v0 = re.sub(r"(?i)^(?:sera|est)?\s*(?:situ(?:e|Ã©)e?|located|based|bas(?:e|Ã©)e?)\s+(?:a|au|Ã |en|in)\s+", "", v0).strip()
        v0 = re.split(r"(?i)\b(?:au|a|Ã |en|in|dans)\b", v0, maxsplit=1)[0].strip()
        v0 = re.sub(r"\b\d{2,10}\b.*$", "", v0).strip()
        v0 = re.sub(r"\bde\b\s*$", "", v0, flags=re.I).strip()
        return _finalize_agency_name(text, v0)

    m0 = re.search(
        r"(?i)\bagence\s+sous\s+le\s+nom\s+([A-Za-z0-9\-_ ]{2,})",
        text,
    )
    if m0:
        v0 = _cut_value(m0.group(1))
        v0 = re.sub(r"(?i)^(sous\s+le\s+nom)\s+", "", v0).strip()
        v0 = re.sub(r"(?i)^(?:sera|est)?\s*(?:situ(?:e|Ã©)e?|located|based|bas(?:e|Ã©)e?)\s+(?:a|au|Ã |en|in)\s+", "", v0).strip()
        v0 = re.split(r"(?i)\b(?:au|a|Ã |en|in|dans)\b", v0, maxsplit=1)[0].strip()
        v0 = re.sub(r"\b\d{2,10}\b.*$", "", v0).strip()
        v0 = re.sub(r"\bde\b\s*$", "", v0, flags=re.I).strip()
        return _finalize_agency_name(text, v0)

    m = re.search(
        r"(?i)\b(?:agency[_\s-]*name|agence[_\s-]*name|nom\s+agence|agency|agence)\s*[:=]?\s*([A-Za-z0-9\-_ ']{2,})",
        text,
    )
    if m:
        v = re.split(
            r"\b(au|en|dans|avec|and|et|code|region|devise|currency|pays|country|,|\.|\n)\b",
            m.group(1),
            flags=re.I,
        )[0].strip()
        v = re.sub(r"(?i)^(?:sera|est)?\s*(?:situ(?:e|Ã©)e?|located|based|bas(?:e|Ã©)e?)\s+(?:a|au|Ã |en|in)\s+", "", v).strip()
        v = re.split(r"(?i)\b(?:a|Ã |in)\b", v, maxsplit=1)[0].strip()
        v = re.sub(r"(?i)^(sous\s+le\s+nom|nomm\S*|s(?:['â€™]|\s+)?appell(?:e|era))\s+", "", v).strip()
        v = re.sub(r"\b\d{2,10}\b.*$", "", v).strip()
        v = re.sub(r"\bde\b\s*$", "", v, flags=re.I).strip()
        return _finalize_agency_name(text, v)
    return None



def _extract_agency_code(text: str) -> Optional[str]:
    m = re.search(
        r"(?i)\bagence\b.{0,120}?\bde\s+code\s*[:=]?\s*([A-Za-z0-9\-_]{2,20})\b",
        text,
    )
    if m:
        return m.group(1).strip().upper()

    m2 = re.search(
        r"(?i)\bagence\s+[A-Za-z0-9\-_ ']{2,}\s+code(?:\s*agence)?\s*[:=]?\s*([A-Za-z0-9\-_]*\d[A-Za-z0-9\-_]{0,20})\b",
        text,
    )
    if m2:
        return m2.group(1).strip().upper()

    m2d = re.search(r"(?i)\bagence\b[^\n]{0,80}?\bcode(?:\s*agence)?\s*[:=]?\s*([A-Za-z0-9\-_]*\d[A-Za-z0-9\-_]{0,20})\b", text)
    if m2d:
        return m2d.group(1).strip().upper()

    m2e = re.search(
        r"(?i)\bagence\s+[A-Za-z0-9\-_ ']{2,}\s*[,;]\s*[A-Za-z\-_ ']{2,}\s*[,;]\s*([A-Za-z0-9\-_]*\d[A-Za-z0-9\-_]{0,20})\b",
        text,
    )
    if m2e:
        return m2e.group(1).strip().upper()

    # "agence Rabat Agdal 0025, ..."
    m2c = re.search(
        r"(?i)\bagence\s+[A-Za-z0-9\-_ ']{2,}?\s+(\d{2,20})\b(?=\s*[,;]|$)",
        text,
    )
    if m2c:
        return m2c.group(1).strip().upper()

    # Common compact phrasing: "agence X, 2589"
    m2b = re.search(
        r"(?i)\bagence\s+[A-Za-z0-9\-_ ']{2,}\s*[,;]\s*([A-Za-z0-9\-_]*\d[A-Za-z0-9\-_]{0,20})\b",
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
    txt = text or ""

    explicit_match = re.search(
        r"(?i)\b(?:les\s+)?(?:comptes?|accounts?|resources?|ressources?)\b(?:\s+bank)?\s*(?:seront|will\s+be|is|est|=|:)?\s*([^\n\.]+)",
        txt,
    )
    explicit_items: List[str] = []
    if explicit_match:
        raw = (explicit_match.group(1) or "").strip()
        raw = re.sub(r"(?i)^(?:bank|bancaires?)\s+", "", raw).strip()
        raw = re.split(
            r"(?i)\b(?:et\s+la\s+carte|and\s+the\s+card|et\s+carte|and\s+card|card|carte|network|reseau|r[ée]seau|bin|product[_\s-]*code|code\s*produit|service[_\s-]*code|code\s*service)\b",
            raw,
            maxsplit=1,
        )[0].strip(" ,;")
        if raw:
            explicit_items = [x.strip() for x in re.split(r"[,;/]|(?:\bet\b|\band\b)", raw, flags=re.I) if x.strip()]
    if not explicit_items:
        explicit_items = _extract_explicit_list_items(txt, r"comptes?|accounts?|resources?|ressources?")
    if explicit_items:
        return explicit_items
    if not re.search(r"(?i)\b(comptes?|accounts?|resources?|ressources?)\b", txt):
        return []
    vals = []
    mapping = {
        "VISA_BASE1": [r"visa[_\s-]*base1"],
        "VISA_SMS": [r"visa[_\s-]*sms"],
        "MCD_MDS": [r"mcd[_\s-]*mds"],
        "MCD_CIS": [r"mcd[_\s-]*cis"],
        "UPI": [r"\bupi\b"],
        "HOST_BANK": [r"host[_\s-]*bank"],
        "SID": [r"\bsid\b"],
    }
    for token, patterns in mapping.items():
        if any(re.search(rf"(?i){pat}", txt) for pat in patterns):
            vals.append(token)
    return vals


def _extract_limit_daily_amounts(text: str) -> Dict[str, float]:
    out: Dict[str, float] = {}
    txt = _repair_mojibake(text or "")

    def _to_float(raw: str) -> Optional[float]:
        try:
            return float((raw or "").replace(" ", "").replace(",", "."))
        except Exception:
            return None

    # 1) Explicit geography first (domestic/international).
    m_dom = re.search(
        r"(?i)\b(?:domestic|national|domestique|local)\b[^\n]{0,120}?(?:daily|jour|quotidien)?[^\d]{0,20}(\d[\d\s,\.]*)",
        txt,
    )
    if m_dom:
        v = _to_float(m_dom.group(1))
        if v is not None:
            out["cards.0.limits.by_type.DEFAULT.domestic.daily_amount"] = v

    m_int = re.search(
        r"(?i)\binternational\b[^\n]{0,120}?(?:daily|jour|quotidien)?[^\d]{0,20}(\d[\d\s,\.]*)",
        txt,
    )
    if m_int:
        v = _to_float(m_int.group(1))
        if v is not None:
            out["cards.0.limits.by_type.DEFAULT.international.daily_amount"] = v

    if out:
        return out

    # 2) Operation-based amounts (withdrawal/payment) without forcing payment->international.
    m_ret = re.search(
        r"(?i)\b(?:retraits?|withdrawals?)\b[^\d]{0,20}(\d+(?:[.,]\d+)?)|\b(\d+(?:[.,]\d+)?)\s*[A-Z]{0,4}[^\n]{0,25}\b(?:retraits?|withdrawals?)\b",
        txt,
    )
    if m_ret:
        ret = m_ret.group(1) or m_ret.group(2)
        v_ret = _to_float(ret or "")
        if v_ret is not None:
            out["cards.0.limits.by_type.DEFAULT.domestic.daily_amount"] = v_ret

    m_pay = re.search(
        r"(?i)\b(?:paiements?|payments?|purchase|achats?)\b[^\d]{0,20}(\d+(?:[.,]\d+)?)|\b(\d+(?:[.,]\d+)?)\s*[A-Z]{0,4}[^\n]{0,25}\b(?:paiements?|payments?|purchase|achats?)\b",
        txt,
    )
    if m_pay and re.search(
        r"(?i)(?:international\b[^\n]{0,40}\b(?:paiements?|payments?|purchase|achats?)\b)|"
        r"(?:\b(?:paiements?|payments?|purchase|achats?)\b[^\n]{0,40}\binternational\b)",
        txt,
    ):
        pay = m_pay.group(1) or m_pay.group(2)
        v_pay = _to_float(pay or "")
        if v_pay is not None:
            out["cards.0.limits.by_type.DEFAULT.international.daily_amount"] = v_pay
    return out


def _extract_fee_amounts(text: str) -> Dict[str, float]:
    out: Dict[str, float] = {}
    m_iss = re.search(r"(?i)\b(?:issuance|registration|inscription)\b[^\d]{0,10}(\d+(?:[.,]\d+)?)", text)
    if m_iss:
        out["cards.0.fees.registration_fee"] = float(m_iss.group(1).replace(",", "."))
    m_mon = re.search(r"(?i)\b(?:monthly|periodic|periodique)\b[^\d]{0,10}(\d+(?:[.,]\d+)?)", text)
    if m_mon:
        out["cards.0.fees.periodic_fee"] = float(m_mon.group(1).replace(",", "."))
    m_rep = re.search(r"(?i)\b(?:replacement|remplacement)\b[^\d]{0,12}(\d+(?:[.,]\d+)?)", text)
    if m_rep:
        out["cards.0.fees.replacement_fee"] = float(m_rep.group(1).replace(",", "."))
    m_pin = re.search(r"(?i)\b(?:pin\s*recalculation|recalcul\s*pin)\b[^\d]{0,12}(\d+(?:[.,]\d+)?)", text)
    if m_pin:
        out["cards.0.fees.pin_recalculation_fee"] = float(m_pin.group(1).replace(",", "."))
    return out


def _extract_fee_fields(text: str) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    t = text or ""

    m_desc = re.search(
        r"(?i)\b(?:fee\s*description|description\s*frais?|frais)\b\s*[:=]?\s*([^,\n\.]{3,64})",
        t,
    )
    if m_desc:
        out["cards.0.fees.fee_description"] = m_desc.group(1).strip()[:32]

    m_evt = re.search(
        r"(?i)\b(?:billing\s*event|event\s*de\s*facturation|card[_\s-]*fees[_\s-]*billing[_\s-]*evt)\b[^\d]{0,12}([123])\b",
        t,
    )
    if m_evt:
        out["cards.0.fees.billing_event"] = m_evt.group(1)

    m_period_code = re.search(
        r"(?i)\b(?:billing\s*period|periode\s*de\s*facturation|periodicite)\b[^\w]{0,8}([MAST])\b",
        t,
    )
    if m_period_code:
        out["cards.0.fees.billing_period"] = m_period_code.group(1).upper()
    else:
        period_map = {
            "monthly": "M",
            "mensuel": "M",
            "mensuelle": "M",
            "annual": "A",
            "yearly": "A",
            "annuel": "A",
            "annuelle": "A",
            "trimester": "T",
            "quarterly": "T",
            "trimestriel": "T",
            "trimestrielle": "T",
            "semester": "S",
            "semestrial": "S",
            "semestriel": "S",
            "semestrielle": "S",
        }
        for key, code in period_map.items():
            if re.search(rf"(?i)\b{re.escape(key)}\b", t):
                out["cards.0.fees.billing_period"] = code
                break

    m_grace = re.search(r"(?i)\b(?:grace\s*period|delai\s*de\s*grace|grace)\b[^\d]{0,10}(\d{1,3})\b", t)
    if m_grace:
        out["cards.0.fees.grace_period"] = int(m_grace.group(1))

    return out



def _extract_card_profile_fields(text: str) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    t = text or ""

    plastic_map = [
        ("PVC", r"(?i)\bprinted\b"),
        ("PETG", r"(?i)\bpetg\b"),
        ("PETG", r"(?i)\bemboss(?:ed)?\b"),
        ("PVC", r"(?i)\b(?:pvc|plastic)\b"),
        ("MTL", r"(?i)\b(?:metal|m[Ã©e]tal)\b"),
        ("VRT", r"(?i)\b(?:virtual|virtuelle|virtuel)\b"),
        ("OTH", r"(?i)\b(?:other|autre)\b"),
    ]
    plastics = [code for code, pattern in plastic_map if re.search(pattern, t)]
    plastics = list(dict.fromkeys(plastics))
    if len(plastics) == 1:
        out["cards.0.card_info.plastic_type"] = plastics[0]

    # product_type should stay at business type level only.
    product_map = [
        ("DEBIT", r"(?i)\bd[Ã©e]bit\b"),
        ("PREPAID", r"(?i)\b(?:prepaid|pr[Ã©e]pay[Ã©e]e?)\b"),
        ("CREDIT", r"(?i)\bcr[Ã©e]dit\b|\bcredit\b"),
    ]
    products = [code for code, pattern in product_map if re.search(pattern, t)]
    products = list(dict.fromkeys(products))
    if len(products) == 1:
        out["cards.0.card_info.product_type"] = products[0]

    # Card tiers are better represented as description, not product_type.
    tiers = []
    for tier in ["classic", "gold", "platinum"]:
        if re.search(rf"(?i)\b{re.escape(tier)}\b", t):
            tiers.append(tier.title())
    if tiers and "cards.0.card_info.card_description" not in out:
        out["cards.0.card_info.card_description"] = " ".join(dict.fromkeys(tiers))

    def _clean_card_description_candidate(raw: str) -> str:
        s = (raw or "").strip().strip("\"'` ")
        s = re.sub(
            r"(?i)^(?:de\s+la\s+carte|de\s+carte|carte)\s*[:=/-]?\s*",
            "",
            s,
        ).strip()
        s = re.sub(r"(?i)^(?:sera|est|is)\s+", "", s).strip()
        s = re.split(
            r"(?i)\s*(?:,|;|\.(?=\s|$)|\b(?:product[_\s-]*code|code\s*produit|service[_\s-]*code|code\s*service|bin|pvk|plastic[_\s-]*type|type\s*plastique|product[_\s-]*type|type\s*produit)\b)",
            s,
            maxsplit=1,
        )[0].strip(" .,:;")
        return s

    m_desc = re.search(
        r"(?i)\b(?:nom\s*/\s*description(?:\s+de\s+la\s+carte)?|description(?:\s+commerciale)?(?:\s+de\s+la\s+carte|\s+carte|\s+card)?|card\s*description)\b\s*(?:sera|est|is)?\s*[:=]?\s*[\"â€œ]?([^\n]{3,})",
        t,
    )
    if m_desc:
        cleaned_desc = _clean_card_description_candidate(m_desc.group(1))
        if cleaned_desc:
            out["cards.0.card_info.card_description"] = cleaned_desc

    m_prod_code = re.search(r"(?i)\b(?:product[_\s-]*code|code\s*produit)\b\s*(?:is|est)?\s*[:=]?\s*([A-Za-z0-9\-_]{2,20})", t)
    if m_prod_code:
        out["cards.0.card_info.product_code"] = m_prod_code.group(1).strip().upper()
    else:
        m_prod_code_short = re.search(
            r"(?i)(?:\bproduit\b|\bproduct\b)[^\n]{0,20}\b([A-Z0-9]{3})\b",
            t,
        )
        if m_prod_code_short:
            out["cards.0.card_info.product_code"] = m_prod_code_short.group(1).strip().upper()

    m_prod_type_code = re.search(
        r"(?i)\b(?:product[_\s-]*type|type\s*produit|type\s*carte)\b\s*(?:is|est)?\s*[:=]?\s*(DEBIT|CREDIT|PREPAID)\b",
        t,
    )
    if m_prod_type_code:
        out["cards.0.card_info.product_type"] = m_prod_type_code.group(1).strip().upper()

    m_plastic_code = re.search(
        r"(?i)\b(?:plastic[_\s-]*type|type\s*plastique|plastic)\b\s*[:=]?\s*(PVC|PETG|MTL|VRT|OTH)\b",
        t,
    )
    if m_plastic_code:
        out["cards.0.card_info.plastic_type"] = m_plastic_code.group(1).strip().upper()

    m_service_code = re.search(
        r"(?i)\b(?:service[_\s-]*code|code\s*service)\b\s*[:=]?\s*([A-Z0-9]{3})\b",
        t,
    )
    if m_service_code:
        out["cards.0.card_info.service_code"] = m_service_code.group(1).strip().upper()

    m_pvk = re.search(r"(?i)\b(?:pvk(?:\s*index)?|index[_\s-]*pvk)\b[^\d]{0,8}(\d)\b", t)
    if m_pvk:
        out["cards.0.card_info.pvk_index"] = int(m_pvk.group(1))

    m_exp = re.search(
        r"(?i)\bexpiration\b(?![^\n]{0,20}\bpre\b)[^\d]{0,10}(\d{1,3})\b",
        t,
    )
    if m_exp:
        out["cards.0.card_info.expiration"] = int(m_exp.group(1))

    m_pre_exp = re.search(
        r"(?i)\b(?:pre[_\s-]*expiration|pre\s*expiration|pre-expiration)\b[^\d]{0,10}(\d{1,2})\b",
        t,
    )
    if m_pre_exp:
        out["cards.0.card_info.pre_expiration"] = int(m_pre_exp.group(1))

    m_renew = re.search(
        r"(?i)\b(?:renewal(?:\s*option)?|renouvellement)\b[^\w]{0,8}(AUTO|MANUAL|Y|N)\b",
        t,
    )
    if m_renew:
        renew_raw = m_renew.group(1).upper()
        out["cards.0.card_info.renewal_option"] = "AUTO" if renew_raw in {"AUTO", "Y"} else "MANUAL"

    m_tranche_min = re.search(
        r"(?i)\b(?:tranche|pan)\b[^\n]{0,20}\bmin(?:imum)?\b[^\d]{0,8}(\d{1,22})\b",
        t,
    )
    if m_tranche_min:
        out["cards.0.card_range.tranche_min"] = m_tranche_min.group(1)

    m_tranche_max = re.search(
        r"(?i)\b(?:tranche|pan)\b[^\n]{0,20}\bmax(?:imum)?\b[^\d]{0,8}(\d{1,22})\b",
        t,
    )
    if m_tranche_max:
        out["cards.0.card_range.tranche_max"] = m_tranche_max.group(1)

    m_range_note = re.search(
        r"(?i)\b(?:card[_\s-]*range[_\s-]*note|note\s*tranche)\b\s*[:=]?\s*([^,\n\.]{3,80})",
        t,
    )
    if m_range_note:
        out["cards.0.card_range.note"] = m_range_note.group(1).strip()

    return out


def _has_services_context(text: str) -> bool:
    t = text or ""
    if re.search(r"(?i)\b(limit\s*types?|types?\s*limites?|type\s*operation|types?\s*d['’]?operation)\b", t):
        return False
    if re.search(r"(?i)\b(service|services|activer|enabled|enable|feature|fonction)\b", t):
        return True
    if re.search(
        r"(?i)\b(retrait|withdraw|atm|cash\s*advance|quasi[-\s]*cash|e-?commerce|pin\s*change|authentication|3ds|refund|cashback|moneysend|bill\s*payment)\b",
        t,
    ):
        return True
    if re.search(r"(?i)\b(paiements?|payments?|purchase|achats?)\b", t):
        return bool(re.search(r"(?i)\b(carte|card|transaction|operation|service|plafond|limit)\b", t))
    return False


def _extract_explicit_list_items(text: str, label_pattern: str) -> List[str]:
    m = re.search(
        rf"(?i)\b(?:{label_pattern})\b\s*(?:is|est|=|:)?\s*([^\n\.]+)",
        text or "",
    )
    if not m:
        return []
    raw = (m.group(1) or "").strip()
    if not raw:
        return []
    return [x.strip() for x in re.split(r"[,;/]|(?:\bet\b|\band\b)", raw, flags=re.I) if x.strip()]


def _extract_services_enabled(text: str) -> List[str]:
    t = text or ""
    explicit_items = _extract_explicit_list_items(t, r"services?(?:\s+enabled)?|activer\s+services?")
    if explicit_items:
        return explicit_items
    if not _has_services_context(t):
        return []
    vals: List[str] = []
    if re.search(r"(?i)\b(retraits?|withdrawals?|withdraw|atm)\b", t):
        vals.append("retrait")
    if re.search(r"(?i)\b(paiements?|payments?|purchase|achats?)\b", t):
        vals.append("achat")
    if re.search(r"(?i)\bcash\s*advance\b", t):
        vals.append("advance")
    if re.search(r"(?i)\be-?commerce\b", t):
        vals.append("ecommerce")
    if re.search(r"(?i)\b(transfert|transfer)\b", t):
        vals.append("transfert")
    if re.search(r"(?i)\bquasi[-\s]*cash\b", t):
        vals.append("quasicash")
    if re.search(r"(?i)\b(solde|balance)\b", t):
        vals.append("solde")
    if re.search(r"(?i)\b(releve|statement)\b", t):
        vals.append("releve")
    if re.search(r"(?i)\b(pin\s*change|changement\s*pin)\b", t):
        vals.append("pinchange")
    if re.search(r"(?i)\b(refund|remboursement)\b", t):
        vals.append("refund")
    if re.search(r"(?i)\b(moneysend|money\s*send)\b", t):
        vals.append("moneysend")
    if re.search(r"(?i)\b(bill\s*payment|paiement\s*facture)\b", t):
        vals.append("billpayment")
    if re.search(r"(?i)\boriginal\b", t):
        vals.append("original")
    if re.search(r"(?i)\b(3d\s*secure|3ds|authentication|authentification)\b", t):
        vals.append("authentication")
    if re.search(r"(?i)\bcashback\b", t):
        vals.append("cashback")
    return normalize_services_input(list(dict.fromkeys(vals)))


def _extract_limit_types(text: str) -> List[str]:
    t = text or ""
    explicit_items = _extract_explicit_list_items(
        t,
        r"limit\s*types?|types?\s*limites?|type\s*operation|types?\s*d['’]?operation",
    )
    if explicit_items:
        return explicit_items
    if not re.search(
        r"(?i)\b(limit|limits|limite|limites|plafond|daily|weekly|monthly|jour|semaine|mois|minimum|maximum|min|max|transaction|par\s+transaction)\b",
        t,
    ):
        return []
    normalized_t = t.replace("_", " ")
    vals: List[str] = []
    if re.search(r"(?i)\b(retraits?|withdrawals?|atm)\b", normalized_t):
        vals.append("Retrait")
    if re.search(r"(?i)\b(paiements?|payments?|purchase|achats?)\b", normalized_t):
        vals.append("Purchase")
    if re.search(r"(?i)\bcash\s*advance\b", normalized_t):
        vals.append("CASH_advance")
    if re.search(r"(?i)\bquasi[-\s]*cash\b", normalized_t):
        vals.append("Quasi-cash")
    if re.search(r"(?i)\be-?commerce\b", normalized_t):
        vals.append("E-commerce")
    explicit_type_ctx = bool(re.search(r"(?i)\b(limit\s*types?|types?\s*limites?|type\s*operation|types?\s*d['’]?operation|operations?)\b", t))
    if not explicit_type_ctx and len(vals) < 2:
        return []
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


def _extract_limit_block_values(text: str) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    t = text or ""
    if not re.search(r"(?i)\b(?:daily|weekly|monthly)\s*(?:amount|count)\b", t):
        return out

    block_specs = {
        "domestic": r"(?:domestic|national|nationale?)",
        "international": r"(?:international|internationale?)",
        "total": r"(?:total)",
    }

    for scope, scope_pat in block_specs.items():
        block_pat = rf"(?is)\b{scope_pat}\b(?P<blk>.*?)(?=\b(?:domestic|national|nationale?|international|internationale?|total|min(?:imum)?|max(?:imum)?|$))"
        blk = ""
        for m_block in re.finditer(block_pat, t):
            candidate = m_block.group("blk") or ""
            if re.search(r"(?i)\b(?:daily|weekly|monthly)\s*(?:amount|count)\b", candidate):
                blk = candidate
                break
        if not blk:
            continue
        for period in ["daily", "weekly", "monthly"]:
            m_amt = re.search(rf"(?i)\b{period}\s*amount\b[^\d]{{0,12}}(\d+(?:[.,]\d+)?)", blk)
            if m_amt:
                out[f"cards.0.limits.by_type.DEFAULT.{scope}.{period}_amount"] = float(m_amt.group(1).replace(",", "."))

            m_cnt = re.search(rf"(?i)\b{period}\s*count\b[^\d]{{0,12}}(\d+)", blk)
            if m_cnt:
                out[f"cards.0.limits.by_type.DEFAULT.{scope}.{period}_count"] = int(m_cnt.group(1))

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
    "bank.agencies.0.region": ["region", "rÃ©gion"],
    "bank.agencies.0.region_code": ["region code", "code region", "code rÃ©gion"],
    "cards.0.card_info.bin": ["bin"],
    "cards.0.card_info.network": ["network", "rÃ©seau"],
    "cards.0.card_info.plastic_type": ["plastic type", "plastique", "matiere carte", "material", "printed", "embossed", "embossed type", "virtual"],
    "cards.0.card_info.product_type": ["product type", "type carte", "card type", "type produit", "product_type"],
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
    if path == "bank.country" and _extract_country(text or "") is not None:
        return True
    if path == "bank.currency" and _extract_currency(text or "") is not None:
        return True
    if path == "bank.name" and _extract_bank_name(text or "") is not None:
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


def _merge_list_values(current: Any, candidate: Any) -> Any:
    if not (isinstance(current, list) and isinstance(candidate, list)):
        return candidate
    out = []
    seen = set()
    for x in list(current) + list(candidate):
        key = str(x).strip().lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(x)
    return out


def _record_conflict(
    state: dict,
    path: str,
    old_value: Any,
    new_value: Any,
    old_source: str,
    new_source: str,
    reason: str,
    evidence: str,
):
    if "conflicts" not in state or not isinstance(state.get("conflicts"), list):
        state["conflicts"] = []
    state["conflicts"].append(
        {
            "path": path,
            "old_value": old_value,
            "new_value": new_value,
            "old_source": normalize_source(old_source),
            "new_source": normalize_source(new_source),
            "reason": reason,
            "evidence": evidence,
            "created_at": datetime.now().isoformat(timespec="seconds"),
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
    source = normalize_source(source)

    v = raw_value
    if not isinstance(raw_value, list):
        v = cast_value(str(raw_value), tmpl_value)
    v = postprocess(path, v)

    if is_missing_value(current):
        return _safe_set_if_valid(
            state,
            template_obj,
            path,
            v,
            source=source,
            confidence=confidence,
            evidence=evidence,
            explicit_mention=explicit_mention,
        )

    if _same_value(current, v):
        return True

    existing_meta = vs_get_meta(facts, path)
    existing_source = normalize_source(existing_meta.get("source") or "")
    if not existing_source:
        prov = state.get("provenance", {}).get(path, {})
        existing_source = normalize_source(str(prov.get("source") or ""))
    if not existing_source:
        existing_source = "rules"

    # Same source in same user turn: merge only list fields, keep scalar stable.
    if normalize_source(existing_source) == normalize_source(source):
        if isinstance(current, list) and isinstance(v, list):
            merged = _merge_list_values(current, v)
            if _same_value(current, merged):
                return True
            return _safe_set_if_valid(
                state,
                template_obj,
                path,
                merged,
                source=source,
                confidence=confidence,
                evidence=evidence,
                explicit_mention=explicit_mention,
            )
        # For scalar conflicts from same source, keep explicit conflict flow.

    if not is_authoritative(existing_source, source) and normalize_source(existing_source) != normalize_source(source):
        return False

    _record_conflict(
        state,
        path,
        current,
        v,
        old_source=existing_source,
        new_source=source,
        reason=f"{source}_differs",
        evidence=evidence,
    )
    return False


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
        target_path = path
        if path.endswith(".0"):
            parent_path = path.rsplit(".", 1)[0]
            parent_tmpl = _get_by_path(template_obj, parent_path)
            if isinstance(parent_tmpl, list):
                target_path = parent_path

        if path.startswith("options.") or target_path in dedicated_paths:
            continue

        aliases = list(dict.fromkeys((FIELD_ALIASES.get(target_path, []) + _auto_aliases_for_path(target_path))))
        for alias in aliases:
            for m in re.finditer(rf"(?i)\b{re.escape(alias)}\b", text):
                hits.append({
                    "start": m.start(),
                    "end": m.end(),
                    "path": target_path,
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


def _select_llm_allowed_fields(text: str, allowed_fields: set) -> set:
    txt = text or ""
    cap_raw = (os.getenv("HPS_LLM_ALLOWED_FIELDS_CAP", "") or "").strip()
    try:
        cap = int(cap_raw) if cap_raw else 28
    except Exception:
        cap = 28
    cap = max(12, min(120, cap))

    core = [
        "bank.name",
        "bank.country",
        "bank.currency",
        "bank.bank_code",
    ]

    out = []
    allowed_sorted = sorted(p for p in (allowed_fields or set()) if not p.startswith("options."))
    allowed_set = set(allowed_sorted)

    for p in core:
        if p in allowed_set:
            out.append(p)

    for p in allowed_sorted:
        if p in out:
            continue
        if _path_explicitly_mentioned(txt, p):
            out.append(p)
            if len(out) >= cap:
                break

    # Domain cues to keep important groups even if aliases are absent.
    if re.search(r"(?i)\b(fee|frais|issuance|registration|monthly|periodic|replacement|pin)\b", txt):
        for p in allowed_sorted:
            if p.startswith("cards.0.fees.") and p not in out:
                out.append(p)
                if len(out) >= cap:
                    break
    if re.search(r"(?i)\b(agence|agency|branch|ville|city|rabat|casablanca|marrakech|tanger)\b", txt):
        for p in (
            "bank.agencies.0.agency_name",
            "bank.agencies.0.agency_code",
            "bank.agencies.0.city",
        ):
            if p in allowed_set and p not in out:
                out.append(p)
    if re.search(r"(?i)\b(mcd[_\s-]*mds|mcd[_\s-]*cis|upi|host[_\s-]*bank|sid|visa[_\s-]*base1|visa[_\s-]*sms|resources?|ressources?)\b", txt):
        if "bank.resources" in allowed_set and "bank.resources" not in out:
            out.append("bank.resources")
    if re.search(r"(?i)\b(card|carte|bin|network|reseau|r[Ã©e]seau|visa|mastercard|amex|diners|europay|upi|jcb|privative|gimn|tag[-\s]*yup|debit|d[Ã©e]bit|credit|cr[Ã©e]dit|prepaid|pvc|petg|metal|virtual|printed|emboss(?:ed)?)\b", txt):
        for p in (
            "cards.0.card_info.bin",
            "cards.0.card_info.network",
            "cards.0.card_info.product_type",
            "cards.0.card_info.plastic_type",
        ):
            if p in allowed_set and p not in out:
                out.append(p)
    if re.search(r"(?i)\b(service|services|activer|enable|enabled|feature|fonction|withdraw|retrait|purchase|paiement|payment|e-?commerce|cashback|refund|moneysend|authentication|3ds)\b", txt):
        if "cards.0.services.enabled" in allowed_set and "cards.0.services.enabled" not in out:
            out.append("cards.0.services.enabled")
    if re.search(r"(?i)\b(limit|limits|plafond|daily|weekly|monthly|jour|semaine|mois|international|domestic|national|min|max|transaction)\b", txt):
        for p in (
            "cards.0.limits.selected_limit_types",
            "cards.0.limits.by_type.DEFAULT.domestic.daily_amount",
            "cards.0.limits.by_type.DEFAULT.international.daily_amount",
            "cards.0.limits.by_type.DEFAULT.total.daily_amount",
            "cards.0.limits.by_type.DEFAULT.per_transaction.min_amount",
            "cards.0.limits.by_type.DEFAULT.per_transaction.max_amount",
        ):
            if p in allowed_set and p not in out:
                out.append(p)
    if re.search(r"(?i)\b(region|rÃ©gion|region_code|code\s*region|code\s*rÃ©gion)\b", txt):
        for p in ("bank.agencies.0.region", "bank.agencies.0.region_code"):
            if p in allowed_set and p not in out:
                out.append(p)
    if re.search(r"(?i)\b(total|min(?:imum)?|max(?:imum)?)\b", txt):
        for p in (
            "cards.0.limits.by_type.DEFAULT.total.daily_amount",
            "cards.0.limits.by_type.DEFAULT.per_transaction.min_amount",
            "cards.0.limits.by_type.DEFAULT.per_transaction.max_amount",
        ):
            if p in allowed_set and p not in out:
                out.append(p)

    if len(out) > cap:
        out = out[:cap]
    return set(out) if out else set(allowed_sorted[:cap])


def apply_user_message_to_facts(state: dict, template_obj: dict, user_text: str):
    """
    A2: on reÃ§oit state (pas facts) pour pouvoir enregistrer provenance.
    """
    txt = _repair_mojibake(user_text or "")
    if not txt:
        return

    facts = state["facts"]
    allowed_fields = _get_allowed_fields(template_obj)
    llm_allowed_fields = _select_llm_allowed_fields(txt, allowed_fields)
    meta = state.setdefault("meta", {})
    trace = {
        "used_llm": False,
        "used_fallback_rules": False,
        "used_deterministic_extractors": False,
        "llm_attempts": 0,
        "llm_final_status": "LLM_SKIPPED",
    }

    def _save_trace():
        meta["last_extraction"] = trace

    if USE_LLM:
        redacted, _secrets = sanitize_text(txt)
        attempts = max(1, int(LLM_MAX_ATTEMPTS or 1))
        final_status = "LLM_DOWN"
        llm_applied = False

        for attempt in range(1, attempts + 1):
            trace["used_llm"] = True
            trace["llm_attempts"] = attempt

            llm_status, llm_out = extract_with_llm_status(redacted, llm_allowed_fields, current_facts=facts)
            final_status = llm_status
            if llm_status != "LLM_OK":
                if attempt < attempts:
                    time.sleep(LLM_RETRY_BACKOFF_S * (2 ** (attempt - 1)))
                continue

            clean = apply_llm_gates(llm_out, allowed_fields)
            fields_meta = {}
            if isinstance(llm_out, dict):
                fm = llm_out.get("fields", {})
                if isinstance(fm, dict):
                    fields_meta = fm

            if not clean:
                final_status = "LLM_REJECTED_INVALID"
                if attempt < attempts:
                    time.sleep(LLM_RETRY_BACKOFF_S * (2 ** (attempt - 1)))
                continue

            applied_count = 0
            for path, value in (clean or {}).items():
                if path.startswith("options."):
                    continue

                explicit_mention = _path_explicitly_mentioned(txt, path)
                resources_mentioned = bool(
                    re.search(r"(?i)\b(resources?|ressources?|accounts?|comptes?|cards?|transactions?)\b", txt)
                )
                network_mentioned = bool(
                    re.search(r"(?i)\b(VISA|MCRD|MASTERCARD|AMEX|DINERS|EUROPAY|UPI|JCB|PRIVATIVE|GIMN|TAG[-\s]*YUP)\b", txt)
                )
                product_mentioned = bool(re.search(r"(?i)\b(debit|dÃ©bit|credit|crÃ©dit|prepaid|prÃ©payÃ©e?)\b", txt))
                bin_mentioned = bool(re.search(r"(?i)\bbin\b|\b\d{6,8}\b", txt))

                if path == "bank.name" and _extract_bank_name(txt) is None:
                    continue

                if path == "bank.country" and not explicit_mention:
                    continue

                if (path.endswith("_code") or path.endswith("bank_code")) and not explicit_mention:
                    continue
                if path == "bank.currency" and _extract_currency(txt) is None and not explicit_mention:
                    continue
                if path.startswith("bank.resources") and not resources_mentioned and not explicit_mention:
                    continue
                if path == "cards.0.card_info.plastic_type":
                    plastic_mentioned = bool(re.search(r"(?i)\b(plastic|plastique|pvc|petg|recycled|printed|emboss(?:ed)?|virtual)\b", txt))
                    if not plastic_mentioned and not explicit_mention:
                        continue
                if path == "cards.0.card_info.network" and not network_mentioned and not explicit_mention:
                    continue
                if path == "cards.0.card_info.product_type" and not product_mentioned and not explicit_mention:
                    continue
                if path == "cards.0.card_info.bin" and not bin_mentioned and not explicit_mention:
                    continue
                if path.startswith("cards.0.fees."):
                    fee_mentioned = bool(re.search(r"(?i)\b(fee|frais|issuance|registration|monthly|periodic|replacement|pin)\b", txt))
                    if not fee_mentioned and not explicit_mention:
                        continue
                if path in {"bank.agencies.0.region", "bank.agencies.0.region_code"}:
                    region_mentioned = bool(re.search(r"(?i)\b(region|rÃ©gion|region_code|code\s*region|code\s*rÃ©gion)\b", txt))
                    if not region_mentioned:
                        continue

                conf = 1.0
                try:
                    conf = float((fields_meta.get(path) or {}).get("confidence", 1.0))
                except Exception:
                    conf = 1.0

                required_conf = 0.90
                if explicit_mention:
                    required_conf = LLM_MIN_CONF

                if conf < required_conf:
                    continue

                before = _get_by_path(state["facts"], path)
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
                after = _get_by_path(state["facts"], path)
                if not is_missing_value(after) and not _same_value(before, after):
                    applied_count += 1

            if applied_count > 0:
                final_status = "LLM_OK"
                llm_applied = True
                break

            final_status = "LLM_REJECTED_INVALID"
            if attempt < attempts:
                time.sleep(LLM_RETRY_BACKOFF_S * (2 ** (attempt - 1)))

        trace["llm_final_status"] = final_status
    else:
        trace["llm_final_status"] = "LLM_SKIPPED"
        llm_applied = False

    if llm_applied:
        trace["used_deterministic_extractors"] = False
        trace["used_fallback_rules"] = False
        _save_trace()
        return

    before_deterministic_facts = copy.deepcopy(state.get("facts", {}))

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

    # 3) Regex quick wins (bank/agence)
    bn = _extract_bank_name(txt)
    if bn is not None:
        _try_set_candidate(
            state,
            template_obj,
            "bank.name",
            bn,
            source="user",
            confidence=1.0,
            evidence=txt,
            explicit_mention=True,
        )

    bc = _extract_bank_code(txt)
    if bc is not None:
        _try_set_candidate(state, template_obj, "bank.bank_code", bc, source="user", confidence=1.0, evidence=txt, explicit_mention=True)

    cur = _extract_currency(txt)
    if cur is not None:
        _try_set_candidate(state, template_obj, "bank.currency", cur, source="user", confidence=1.0, evidence=txt, explicit_mention=True)
    elif re.search(r"(?i)\b(?:devise|currency|monnaie)\b", txt):
        _set_validation_error(
            state,
            "bank.currency",
            "Valeur invalide pour bank.currency: code devise ISO sur 3 lettres majuscules. Exemple attendu: MAD.",
        )

    co = _extract_country(txt)
    if co is not None:
        agency_ctx = bool(re.search(r"(?i)\b(agence|agency|code\s*agence|nom\s*agence|ville|city)\b", txt))
        bank_ctx = bool(re.search(r"(?i)\b(banque|bank|pays|country|code\s*banque|bank\s*code|devise|currency)\b", txt))
        if bank_ctx or not agency_ctx:
            _try_set_candidate(
                state,
                template_obj,
                "bank.country",
                co,
                source="user",
                confidence=1.0,
                evidence=txt,
                explicit_mention=True,
            )

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

    fee_fields = _extract_fee_fields(txt)
    for path, value in fee_fields.items():
        _try_set_candidate(state, template_obj, path, value, source="user", confidence=1.0, evidence=txt, explicit_mention=True)

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

    block_limits = _extract_limit_block_values(txt)
    for path, value in block_limits.items():
        _try_set_candidate(state, template_obj, path, value, source="user", confidence=1.0, evidence=txt, explicit_mention=True)

    nets = re.findall(r"(?i)\b(VISA|MCRD|MASTERCARD|AMEX|DINERS|EUROPAY|UPI|JCB|PRIVATIVE|GIMN|TAG[-\s]*YUP)\b", txt)
    explicit_network_ctx = _has_explicit_network_context(txt)
    profile_support_ctx = _has_network_profile_support(txt)
    description_ctx = _has_card_description_context(txt)
    if nets and (explicit_network_ctx or profile_support_ctx) and not (description_ctx and not explicit_network_ctx and not profile_support_ctx):
        _try_set_candidate(
            state,
            template_obj,
            "cards.0.card_info.network",
            normalize_network(str(nets[0]).upper().replace(" ", "")),
            source="user",
            confidence=1.0,
            evidence=txt,
            explicit_mention=True,
        )

    deterministic_changed = before_deterministic_facts != state.get("facts", {})
    trace["used_deterministic_extractors"] = deterministic_changed
    trace["used_fallback_rules"] = deterministic_changed and not llm_applied
    _save_trace()



