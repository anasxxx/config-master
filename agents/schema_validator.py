import re
from typing import Any, Tuple
from agents.prompts import PROMPT_SCHEMA_VALIDATOR
SCHEMA_SPEC = PROMPT_SCHEMA_VALIDATOR
def infer_expected_type(template_value):
    if isinstance(template_value, dict):
        return dict
    if isinstance(template_value, list):
        return list
    return (str, int, float, bool, type(None))


BANK_CODE_RE = re.compile(r"^\d{3,10}$")
CURRENCY_RE = re.compile(r"^[A-Z]{3}$")
BIN_RE = re.compile(r"^\d{6,8}$")
CODE_NUM_RE = re.compile(r"^\d{1,10}$")
AGENCY_CODE_RE = re.compile(r"^[A-Z0-9\-_]{2,20}$")


def validate_format(path: str, value: Any) -> Tuple[bool, str]:
    if value is None:
        return True, ""

    s = str(value).strip()

    if "bank_code" in path:
        if not BANK_CODE_RE.match(s):
            return False, "bank_code must be 3–10 digits"

    if "currency" in path:
        if not CURRENCY_RE.match(s.upper()):
            return False, "currency must be ISO-3"

    if ".bin" in path:
        if not BIN_RE.match(s):
            return False, "BIN must be 6–8 digits"

    if path.endswith("city_code") or path.endswith("region_code"):
        if not CODE_NUM_RE.match(s):
            return False, "code must be numeric"

    if path.endswith("agency_code"):
        if not AGENCY_CODE_RE.match(s.upper()):
            return False, "agency_code invalid"

    return True, ""


def validate_value(path: str, value: Any, template_value: Any) -> Tuple[bool, str]:
    expected_type = infer_expected_type(template_value)

    if not isinstance(value, expected_type):
        return False, f"type mismatch expected {expected_type} got {type(value)}"

    ok, msg = validate_format(path, value)
    if not ok:
        return False, msg

    return True, ""
def format_schema_error(path: str, message: str) -> str:
    # prompt = spec, mais on fait une version déterministe (fiable)
    return (
        f"⚠ Donnée invalide sur '{path}'.\n"
        f"Raison: {message}\n"
        f"Donne une valeur au bon format (exemples: BIN=445555, currency=MAD, code ville=001)."
    )