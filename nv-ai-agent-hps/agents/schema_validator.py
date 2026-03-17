import re
from typing import Any, Tuple

from agents.prompts import PROMPT_SCHEMA_VALIDATOR
from agents.powercard_constraints import (
    AMOUNT_PATHS,
    COUNT_PATHS,
    USER_OWNED_REQUIRED_PATHS,
    is_powercard_profile,
    validate_powercard_field,
)

SCHEMA_SPEC = PROMPT_SCHEMA_VALIDATOR


def infer_expected_type(template_value):
    if isinstance(template_value, dict):
        return dict
    if isinstance(template_value, list):
        return list
    return (str, int, float, bool, type(None))


CODE_RE = re.compile(r"^[A-Za-z0-9\-_]{1,32}$")
CURRENCY_RE = re.compile(r"^[A-Z]{3}$")
ALPHA2_RE = re.compile(r"^[A-Z]{2}$")
BIN_RE = re.compile(r"^\d{6,11}$")


CODE_FIELDS = {
    "bank.bank_code",
    "bank.agencies.0.agency_code",
    "bank.agencies.0.city_code",
    "bank.agencies.0.region_code",
    "cards.0.card_info.product_code",
    "cards.0.card_info.service_code",
}


def validate_format(path: str, value: Any) -> Tuple[bool, str]:
    if value is None:
        return True, ""

    s = str(value).strip()

    if path in CODE_FIELDS:
        if not CODE_RE.match(s):
            return False, "code must match [A-Za-z0-9_-] and length 1..32"

    if path == "bank.currency":
        if not CURRENCY_RE.match(s):
            return False, "currency must be 3 uppercase letters"

    if path == "bank.country_alpha2":
        if not ALPHA2_RE.match(s):
            return False, "country_alpha2 must be 2 uppercase letters"

    if ".bin" in path:
        if not BIN_RE.match(s):
            return False, "BIN must be 6-11 digits"

    return True, ""


def validate_value(
    path: str,
    value: Any,
    template_value: Any,
    *,
    state: dict | None = None,
    source: str = "user",
    explicit_mention: bool = False,
) -> Tuple[bool, str]:
    strict_profile = is_powercard_profile(state or {})

    if strict_profile:
        if path in USER_OWNED_REQUIRED_PATHS and source in {"llm", "rules", "autofill"} and not explicit_mention:
            return False, f"Valeur invalide pour {path}: champ obligatoire a fournir explicitement par l'utilisateur."
        ok, msg = validate_powercard_field(path, value)
        if not ok:
            return False, msg

    is_amount_field = path.endswith("_amount") or path in AMOUNT_PATHS
    is_count_field = path in COUNT_PATHS
    is_code_like = path in CODE_FIELDS or path in {"bank.currency", "bank.country_alpha2"} or ".bin" in path

    if is_code_like:
        expected_type = (str, type(None))
    elif is_count_field:
        expected_type = (int, type(None))
    elif is_amount_field:
        expected_type = (int, float, type(None))
    else:
        expected_type = infer_expected_type(template_value)

    if not isinstance(value, expected_type):
        # In strict mode, numeric fields can come as numeric strings before coercion.
        if strict_profile and is_amount_field and isinstance(value, str):
            try:
                float(value.replace(",", "."))
            except Exception:
                return False, f"type mismatch expected {expected_type} got {type(value)}"
        elif strict_profile and is_count_field and isinstance(value, str):
            try:
                int(float(value.replace(",", ".")))
            except Exception:
                return False, f"type mismatch expected {expected_type} got {type(value)}"
        else:
            return False, f"type mismatch expected {expected_type} got {type(value)}"

    if is_count_field and value is not None:
        try:
            if int(value) < 0:
                return False, "count must be integer >= 0"
        except Exception:
            return False, "count must be integer >= 0"

    if is_amount_field and value is not None:
        try:
            if float(value) < 0:
                return False, "amount/fee must be >= 0"
        except Exception:
            return False, "amount/fee must be >= 0"

    ok, msg = validate_format(path, value)
    if not ok:
        return False, msg

    return True, ""


def format_schema_error(path: str, message: str) -> str:
    return f"Valeur invalide pour {path}: {message}."
