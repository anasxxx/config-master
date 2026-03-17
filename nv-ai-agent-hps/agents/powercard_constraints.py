import re
import unicodedata
from typing import Any, Dict, List, Tuple
from decimal import Decimal, InvalidOperation


POWERCARD_PROFILE = "powercard_v1"


OFFICIAL_TO_INTERNAL_PATH = {
    "bank_name": "bank.name",
    "BANK_CODE": "bank.bank_code",
    "country": "bank.country",
    "currency": "bank.currency",
    "BRANCH_NAME": "bank.agencies.0.agency_name",
    "BRANCH_CODE": "bank.agencies.0.agency_code",
    "REGION_NAME": "bank.agencies.0.region",
    "REGION_CODE": "bank.agencies.0.region_code",
    "CITY_NAME": "bank.agencies.0.city",
    "CITY_CODE": "bank.agencies.0.city_code",
    "resource_wording": "bank.resources",
    "PRODUCT_CODE": "cards.0.card_info.product_code",
    "description": "cards.0.card_info.card_description",
    "bin": "cards.0.card_info.bin",
    "PLASTIC_TYPE": "cards.0.card_info.plastic_type",
    "PRODUCT_TYPE": "cards.0.card_info.product_type",
    "NETWORK_TYPE": "cards.0.card_info.network",
    "SERVICE_CODE": "cards.0.card_info.service_code",
    "index_pvk": "cards.0.card_info.pvk_index",
    "expiration": "cards.0.card_info.expiration",
    "renewal_option": "cards.0.card_info.renewal_option",
    "pre_expiration": "cards.0.card_info.pre_expiration",
    "tranche_min": "cards.0.card_range.tranche_min",
    "tranche_max": "cards.0.card_range.tranche_max",
    "card_fees_billing_evt": "cards.0.fees.billing_event",
    "card_fees_billing_period": "cards.0.fees.billing_period",
    "grace_period": "cards.0.fees.grace_period",
    "fees_amount_first": "cards.0.fees.registration_fee",
    "subscription_amount": "cards.0.fees.periodic_fee",
    "damaged_replacement_fees": "cards.0.fees.replacement_fee",
    "pin_replacement_fees": "cards.0.fees.pin_recalculation_fee",
    "min_amount_per_transaction": "cards.0.limits.by_type.DEFAULT.per_transaction.min_amount",
    "max_amount_per_transaction": "cards.0.limits.by_type.DEFAULT.per_transaction.max_amount",
}


RESOURCE_ENUM = {
    "VISA_BASE1",
    "VISA_SMS",
    "MCD_MDS",
    "MCD_CIS",
    "UPI",
    "HOST_BANK",
    "SID",
}

NETWORK_ENUM = {
    "VISA",
    "MCRD",
    "EUROPAY",
    "AMEX",
    "TAG-YUP",
    "DINERS",
    "UPI",
    "GIMN",
    "JCB",
    "PRIVATIVE",
}

NETWORK_ALIASES = {
    "MASTERCARD": "MCRD",
    "MASTER CARD": "MCRD",
    "MCD": "MCRD",
    "TAG YUP": "TAG-YUP",
    "TAGYUP": "TAG-YUP",
    "DINERS CLUB": "DINERS",
    "AMERICAN EXPRESS": "AMEX",
}

SERVICE_FLAG_KEYS = [
    "retrait",
    "achat",
    "advance",
    "ecommerce",
    "transfert",
    "quasicash",
    "solde",
    "releve",
    "pinchange",
    "refund",
    "moneysend",
    "billpayment",
    "original",
    "authentication",
    "cashback",
]

SERVICE_ALIASES = {
    "withdrawal": "retrait",
    "withdraw": "retrait",
    "payments": "achat",
    "paiements": "achat",
    "achat": "achat",
    "purchase": "achat",
    "cash advance": "advance",
    "advance": "advance",
    "ecommerce": "ecommerce",
    "e-commerce": "ecommerce",
    "e commerce": "ecommerce",
    "transfer": "transfert",
    "transfert": "transfert",
    "quasi cash": "quasicash",
    "quasi-cash": "quasicash",
    "solde": "solde",
    "balance": "solde",
    "releve": "releve",
    "statement": "releve",
    "pinchange": "pinchange",
    "pin change": "pinchange",
    "refund": "refund",
    "remboursement": "refund",
    "moneysend": "moneysend",
    "money send": "moneysend",
    "billpayment": "billpayment",
    "bill payment": "billpayment",
    "paiement facture": "billpayment",
    "original": "original",
    "authentication": "authentication",
    "authentification": "authentication",
    "cashback": "cashback",
}

RENEWAL_OPTION_ENUM = {"AUTO", "MANUAL", "Y", "N"}
BILLING_EVENT_ENUM = {"1", "2", "3"}
BILLING_PERIOD_ENUM = {"M", "A", "T", "S"}
LIMIT_TYPE_ENUM = {"Retrait", "Purchase", "CASH_advance", "Quasi-cash", "E-commerce"}
PRODUCT_TYPE_ENUM = {"DEBIT", "CREDIT", "PREPAID"}
PLASTIC_TYPE_ENUM = {"PVC", "PETG", "MTL", "VRT", "OTH"}


BASE_USER_OWNED_REQUIRED_PATHS = {
    "bank.name",
    "bank.country",
    "bank.currency",
    "bank.bank_code",
    "bank.resources",
    "bank.agencies.0.agency_name",
    "bank.agencies.0.agency_code",
    "bank.agencies.0.city",
    "bank.agencies.0.city_code",
    "bank.agencies.0.region",
    "bank.agencies.0.region_code",
    "cards.0.card_info.bin",
    "cards.0.card_info.plastic_type",
    "cards.0.card_info.card_description",
    "cards.0.card_info.product_type",
    "cards.0.card_info.product_code",
    "cards.0.card_info.pvk_index",
    "cards.0.card_info.service_code",
    "cards.0.card_info.network",
    "cards.0.card_info.expiration",
    "cards.0.card_info.renewal_option",
    "cards.0.card_info.pre_expiration",
    "cards.0.card_range.tranche_min",
    "cards.0.card_range.tranche_max",
    "cards.0.fees.fee_description",
    "cards.0.fees.billing_event",
    "cards.0.fees.grace_period",
    "cards.0.fees.billing_period",
    "cards.0.fees.registration_fee",
    "cards.0.fees.periodic_fee",
    "cards.0.fees.replacement_fee",
    "cards.0.fees.pin_recalculation_fee",
    "cards.0.services.enabled",
    "cards.0.limits.selected_limit_types",
}


AMOUNT_PATHS = {
    "cards.0.fees.registration_fee",
    "cards.0.fees.periodic_fee",
    "cards.0.fees.replacement_fee",
    "cards.0.fees.pin_recalculation_fee",
    "cards.0.limits.by_type.DEFAULT.domestic.daily_amount",
    "cards.0.limits.by_type.DEFAULT.domestic.weekly_amount",
    "cards.0.limits.by_type.DEFAULT.domestic.monthly_amount",
    "cards.0.limits.by_type.DEFAULT.international.daily_amount",
    "cards.0.limits.by_type.DEFAULT.international.weekly_amount",
    "cards.0.limits.by_type.DEFAULT.international.monthly_amount",
    "cards.0.limits.by_type.DEFAULT.total.daily_amount",
    "cards.0.limits.by_type.DEFAULT.total.weekly_amount",
    "cards.0.limits.by_type.DEFAULT.total.monthly_amount",
    "cards.0.limits.by_type.DEFAULT.per_transaction.min_amount",
    "cards.0.limits.by_type.DEFAULT.per_transaction.max_amount",
}

COUNT_PATHS = {
    "cards.0.limits.by_type.DEFAULT.domestic.daily_count",
    "cards.0.limits.by_type.DEFAULT.domestic.weekly_count",
    "cards.0.limits.by_type.DEFAULT.domestic.monthly_count",
    "cards.0.limits.by_type.DEFAULT.international.daily_count",
    "cards.0.limits.by_type.DEFAULT.international.weekly_count",
    "cards.0.limits.by_type.DEFAULT.international.monthly_count",
    "cards.0.limits.by_type.DEFAULT.total.daily_count",
    "cards.0.limits.by_type.DEFAULT.total.weekly_count",
    "cards.0.limits.by_type.DEFAULT.total.monthly_count",
}

USER_OWNED_REQUIRED_PATHS = BASE_USER_OWNED_REQUIRED_PATHS | AMOUNT_PATHS | COUNT_PATHS


def _as_meta_dict(state_or_meta: Any) -> Dict[str, Any]:
    if not isinstance(state_or_meta, dict):
        return {}
    if isinstance(state_or_meta.get("meta"), dict):
        return state_or_meta.get("meta") or {}
    return state_or_meta


def is_powercard_profile(state_or_meta: Any) -> bool:
    meta = _as_meta_dict(state_or_meta)
    profile = str(meta.get("validation_profile") or "").strip().lower()
    if not profile:
        # Default to strict validation when profile is absent.
        return True
    return profile == POWERCARD_PROFILE


def _norm_token(value: str) -> str:
    t = (value or "").strip().lower()
    t = unicodedata.normalize("NFKD", t)
    t = "".join(ch for ch in t if not unicodedata.combining(ch))
    t = t.replace("_", " ").replace("-", " ")
    t = re.sub(r"\s+", " ", t)
    return t.strip()


def normalize_network(value: Any) -> Any:
    if value is None:
        return None
    s = str(value).strip().upper()
    s = NETWORK_ALIASES.get(s, s)
    if s == "MASTERCARD":
        return "MCRD"
    return s


def empty_service_flags() -> Dict[str, Any]:
    return {k: None for k in SERVICE_FLAG_KEYS}


def normalize_services_input(values: Any) -> List[str]:
    if values is None:
        return []
    raw_items: List[str] = []
    if isinstance(values, list):
        raw_items = [str(v) for v in values]
    elif isinstance(values, str):
        raw_items = re.split(r"[,\n;/]+", values)
    else:
        raw_items = [str(values)]

    out: List[str] = []
    seen = set()
    for item in raw_items:
        n = _norm_token(item)
        if not n:
            continue
        key = SERVICE_ALIASES.get(n, n)
        if key in SERVICE_FLAG_KEYS and key not in seen:
            seen.add(key)
            out.append(key)
    return out


def services_to_flags(values: Any) -> Dict[str, Any]:
    flags = empty_service_flags()
    for key in normalize_services_input(values):
        flags[key] = "1"
    return flags


def normalize_resource_item(value: Any) -> str:
    s = str(value or "").strip().upper().replace(" ", "_")
    return s


def should_block_autofill(path: str, state_or_meta: Any) -> bool:
    if not is_powercard_profile(state_or_meta):
        return False
    allowed_in_strict = {
        "bank.country_alpha2",
        "bank.currency",
        "bank.agencies.0.city_code",
        "bank.agencies.0.region",
        "bank.agencies.0.region_code",
    }
    if path in allowed_in_strict:
        return False
    return path.startswith("bank.") or path.startswith("cards.0.")


def service_flag_path_keys() -> set:
    return {f"cards.0.services.flags.{k}" for k in SERVICE_FLAG_KEYS}


def validation_error(path: str, rule: str, example: str = "") -> str:
    msg = f"Valeur invalide pour {path}: {rule}."
    if example:
        msg += f" Exemple attendu: {example}."
    return msg


def _is_missing(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and value.strip() == "":
        return True
    return False


def _is_numeric(value: Any) -> bool:
    if isinstance(value, (int, float)):
        return True
    if isinstance(value, str):
        return bool(re.fullmatch(r"-?\d+(?:[.,]\d+)?", value.strip()))
    return False


def _is_int_like(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, int):
        return True
    if isinstance(value, float):
        return value.is_integer()
    if isinstance(value, str):
        return bool(re.fullmatch(r"\d+", value.strip()))
    return False


def _validate_number_18_3(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    s = str(value).strip().replace(",", ".")
    if not re.fullmatch(r"\d+(?:\.\d+)?", s):
        return False
    parts = s.split(".")
    int_part = parts[0]
    frac_part = parts[1] if len(parts) == 2 else ""
    if len(int_part) > 15:
        return False
    if len(frac_part) > 3:
        return False
    try:
        d = Decimal(s)
    except (InvalidOperation, ValueError):
        return False
    return d >= 0


def _to_float(value: Any) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    return float(str(value).strip().replace(",", "."))


def _to_int(value: Any) -> int:
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    return int(float(str(value).strip().replace(",", ".")))


def validate_powercard_field(path: str, value: Any) -> Tuple[bool, str]:
    if path == "bank.name":
        s = str(value or "").strip()
        if _is_missing(s):
            return False, validation_error(path, "champ requis", "Sahara Bank")
        if len(s) > 40:
            return False, validation_error(path, "longueur maximale 40", "Sahara Bank")
        if not re.fullmatch(r"[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ ]{0,39}", s):
            return False, validation_error(path, "lettres et espaces uniquement", "Sahara Bank")
        return True, ""

    if path == "bank.bank_code":
        s = str(value or "").strip().upper()
        if not re.fullmatch(r"[A-Z0-9]{6}", s):
            return False, validation_error(path, "exactement 6 caracteres alphanumeriques majuscules", "SAH01X")
        return True, ""

    if path == "bank.country":
        s = str(value or "").strip()
        if _is_missing(s):
            return False, validation_error(path, "champ requis", "Maroc")
        if len(s) > 50:
            return False, validation_error(path, "longueur maximale 50", "Maroc")
        return True, ""

    if path == "bank.currency":
        s = str(value or "").strip().upper()
        if not re.fullmatch(r"[A-Z]{3}", s):
            return False, validation_error(path, "code devise ISO sur 3 lettres majuscules", "MAD")
        return True, ""

    if path == "bank.agencies.0.agency_name":
        s = str(value or "").strip()
        if _is_missing(s):
            return False, validation_error(path, "champ requis", "Agence Maarif")
        if len(s) > 40:
            return False, validation_error(path, "longueur maximale 40", "Agence Maarif")
        return True, ""

    if path == "bank.agencies.0.agency_code":
        s = str(value or "").strip().upper()
        if not re.fullmatch(r"[A-Z0-9]{6}", s):
            return False, validation_error(path, "exactement 6 caracteres alphanumeriques majuscules", "AG001X")
        return True, ""

    if path == "bank.agencies.0.region":
        s = str(value or "").strip()
        if _is_missing(s):
            return False, validation_error(path, "champ requis", "Casablanca-Settat")
        if len(s) > 30:
            return False, validation_error(path, "longueur maximale 30", "Casablanca-Settat")
        return True, ""

    if path == "bank.agencies.0.region_code":
        s = str(value or "").strip().upper()
        if not re.fullmatch(r"[A-Z0-9]{1,3}", s):
            return False, validation_error(path, "longueur maximale 3 en majuscules", "CS")
        return True, ""

    if path == "bank.agencies.0.city":
        s = str(value or "").strip()
        if _is_missing(s):
            return False, validation_error(path, "champ requis", "Casablanca")
        if len(s) > 32:
            return False, validation_error(path, "longueur maximale 32", "Casablanca")
        return True, ""

    if path == "bank.agencies.0.city_code":
        s = str(value or "").strip().upper()
        if not re.fullmatch(r"[A-Z0-9]{1,5}", s):
            return False, validation_error(path, "longueur maximale 5 en majuscules", "CASA")
        return True, ""

    if path == "bank.resources":
        if not isinstance(value, list) or not value:
            return False, validation_error(path, "liste requise", "VISA_BASE1")
        invalid = [v for v in value if normalize_resource_item(v) not in RESOURCE_ENUM]
        if invalid:
            return False, validation_error(path, f"valeurs autorisees {sorted(RESOURCE_ENUM)}", "VISA_BASE1")
        return True, ""

    if path == "cards.0.card_info.product_code":
        s = str(value or "").strip().upper()
        if not re.fullmatch(r"[A-Z0-9]{3}", s):
            return False, validation_error(path, "exactement 3 caracteres majuscules", "VCL")
        return True, ""

    if path == "cards.0.card_info.card_description":
        s = str(value or "").strip()
        if _is_missing(s):
            return False, validation_error(path, "champ requis", "Visa Classic Internationale")
        if len(s) > 40:
            return False, validation_error(path, "longueur maximale 40", "Visa Classic Internationale")
        return True, ""

    if path == "cards.0.card_info.bin":
        s = str(value or "").strip()
        if not re.fullmatch(r"\d{6,11}", s):
            return False, validation_error(path, "BIN numerique de 6 a 11 chiffres", "445566")
        return True, ""

    if path == "cards.0.card_info.plastic_type":
        s = str(value or "").strip().upper()
        if s not in PLASTIC_TYPE_ENUM:
            return False, validation_error(path, f"valeurs autorisees {sorted(PLASTIC_TYPE_ENUM)}", "PVC")
        return True, ""

    if path == "cards.0.card_info.product_type":
        s = str(value or "").strip().upper()
        if s not in PRODUCT_TYPE_ENUM:
            return False, validation_error(path, f"valeurs autorisees {sorted(PRODUCT_TYPE_ENUM)}", "DEBIT")
        return True, ""

    if path == "cards.0.card_info.network":
        s = normalize_network(value)
        if s not in NETWORK_ENUM:
            return False, validation_error(path, f"valeurs autorisees {sorted(NETWORK_ENUM)}", "VISA")
        return True, ""

    if path == "cards.0.card_info.service_code":
        s = str(value or "").strip().upper()
        if not re.fullmatch(r"[A-Z0-9]{3}", s):
            return False, validation_error(path, "exactement 3 caracteres", "101")
        return True, ""

    if path == "cards.0.card_info.pvk_index":
        if not _is_int_like(value):
            return False, validation_error(path, "entier entre 0 et 9", "1")
        i = _to_int(value)
        if i < 0 or i > 9:
            return False, validation_error(path, "entier entre 0 et 9", "1")
        return True, ""

    if path == "cards.0.card_info.expiration":
        if not _is_int_like(value):
            return False, validation_error(path, "nombre de mois", "5")
        i = _to_int(value)
        if i < 0 or i > 999:
            return False, validation_error(path, "nombre de mois entre 0 et 999", "5")
        return True, ""

    if path == "cards.0.card_info.renewal_option":
        s = str(value or "").strip().upper()
        if s not in RENEWAL_OPTION_ENUM:
            return False, validation_error(path, "valeurs autorisees: AUTO ou MANUAL", "AUTO")
        return True, ""

    if path == "cards.0.card_info.pre_expiration":
        if not _is_int_like(value):
            return False, validation_error(path, "nombre entier entre 0 et 99", "3")
        i = _to_int(value)
        if i < 0 or i > 99:
            return False, validation_error(path, "nombre entier entre 0 et 99", "3")
        return True, ""

    if path == "cards.0.card_range.note":
        s = str(value or "").strip()
        if _is_missing(s):
            return False, validation_error(path, "champ requis", "Tranche principale")
        if len(s) > 120:
            return False, validation_error(path, "longueur maximale 120", "Tranche principale")
        return True, ""

    if path in {"cards.0.card_range.tranche_min", "cards.0.card_range.tranche_max"}:
        s = str(value or "").strip()
        if not re.fullmatch(r"\d{1,22}", s):
            return False, validation_error(path, "chiffres uniquement, longueur max 22", "4455660000000000")
        return True, ""

    if path == "cards.0.fees.fee_description":
        s = str(value or "").strip()
        if _is_missing(s):
            return False, validation_error(path, "champ requis", "Frais carte")
        if len(s) > 32:
            return False, validation_error(path, "longueur maximale 32", "Frais carte")
        return True, ""

    if path == "cards.0.fees.billing_event":
        s = str(value or "").strip()
        if s not in BILLING_EVENT_ENUM:
            return False, validation_error(path, "valeurs autorisees: 1, 2, 3", "1")
        return True, ""

    if path == "cards.0.fees.billing_period":
        s = str(value or "").strip().upper()
        if s not in BILLING_PERIOD_ENUM:
            return False, validation_error(path, "valeurs autorisees: M, A, T, S", "M")
        return True, ""

    if path == "cards.0.fees.grace_period":
        if not _is_int_like(value):
            return False, validation_error(path, "entier entre 0 et 999", "0")
        i = _to_int(value)
        if i < 0 or i > 999:
            return False, validation_error(path, "entier entre 0 et 999", "0")
        return True, ""

    if path in AMOUNT_PATHS:
        if not _validate_number_18_3(value):
            return False, validation_error(path, "nombre NUMBER(18,3) >= 0", "100.000")
        return True, ""

    if path in COUNT_PATHS:
        if not _is_int_like(value):
            return False, validation_error(path, "compteur NUMBER(4,0) entre 0 et 9999", "10")
        i = _to_int(value)
        if i < 0 or i > 9999:
            return False, validation_error(path, "compteur NUMBER(4,0) entre 0 et 9999", "10")
        return True, ""

    if path == "cards.0.limits.selected_limit_types":
        if not isinstance(value, list):
            return False, validation_error(path, "liste attendue", "Retrait, Purchase")
        invalid = [str(v) for v in value if str(v) not in LIMIT_TYPE_ENUM]
        if invalid:
            return False, validation_error(path, f"valeurs autorisees: {sorted(LIMIT_TYPE_ENUM)}", "Retrait")
        return True, ""

    if path == "cards.0.services.enabled":
        if not isinstance(value, list):
            return False, validation_error(path, "liste attendue", "retrait, achat")
        for item in value:
            if str(item or "").strip().lower() not in SERVICE_FLAG_KEYS:
                return False, validation_error(path, "service non reconnu", "retrait")
        return True, ""

    if path.startswith("cards.0.services.flags."):
        leaf = path.rsplit(".", 1)[-1]
        if leaf not in SERVICE_FLAG_KEYS:
            return False, validation_error(path, "service non supporte", "retrait")
        if value is None:
            return True, ""
        if str(value).strip() != "1":
            return False, validation_error(path, "valeurs autorisees: '1' ou null", "1")
        return True, ""

    return True, ""
