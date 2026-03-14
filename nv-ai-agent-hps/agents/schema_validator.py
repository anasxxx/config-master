import re
PAN_RANGE_RE = re.compile(r"^\d{12,19}$")
from typing import Any, Tuple
from agents.prompts import PROMPT_SCHEMA_VALIDATOR
SCHEMA_SPEC = PROMPT_SCHEMA_VALIDATOR
def infer_expected_type(template_value):
    if isinstance(template_value, dict):
        return dict
    if isinstance(template_value, list):
        return list
    return (str, int, float, bool, type(None))


BANK_CODE_RE = re.compile(r"^[A-Z0-9]{1,6}$", re.IGNORECASE)      # CHAR(6)
CURRENCY_RE = re.compile(r"^[A-Z]{3}$")                           # CHAR(3)
BIN_RE = re.compile(r"^\d{6,11}$")                                # VARCHAR2(11) digits
CODE_ALPHANUM_RE = re.compile(r"^[A-Z0-9]{1,5}$", re.IGNORECASE)  # city CHAR(5), region CHAR(3)
AGENCY_CODE_RE = re.compile(r"^[A-Z0-9\-_]{1,6}$", re.IGNORECASE) # CHAR(6)
PLASTIC_TYPE_ENUM = {"STD", "EMB", "VIR"}                         # CHAR(3)
PRODUCT_TYPE_RE = re.compile(r"^[A-Z0-9]{1,2}$", re.IGNORECASE)   # CHAR(2)
SERVICE_CODE_RE = re.compile(r"^[A-Z0-9]{1,3}$", re.IGNORECASE)   # CHAR(3)
PVK_INDEX_RE = re.compile(r"^\d{1}$")                             # NUMBER(1,0)
EXPIRATION_RE = re.compile(r"^\d{1,3}$")                          # NUMBER(3,0)
PRODUCT_CODE_RE = re.compile(r"^[A-Z0-9]{1,3}$", re.IGNORECASE)   # CHAR(3)

NETWORK_ENUM = {"VISA", "MCRD", "EUROPAY", "AMEX", "TAG-YUP", "DINERS", "UPI", "GIMN", "JCB", "PRIVATIVE"}

def validate_format(path: str, value: Any) -> Tuple[bool, str]:
    if value is None:
        return True, ""

    s = str(value).strip()

    if "bank_code" in path:
        if not BANK_CODE_RE.match(s):
            return False, "bank_code must be 1–6 alphanumeric chars (CHAR(6))"

    if "currency" in path:
        if not CURRENCY_RE.match(s.upper()):
            return False, "currency must be ISO-3"

    if ".bin" in path and not path.endswith("billing"):
        if not BIN_RE.match(s):
            return False, "BIN must be 6–11 digits (VARCHAR2(11))"

    if path.endswith("city_code"):
        if not re.match(r"^[A-Z0-9]{1,5}$", s, re.IGNORECASE):
            return False, "city_code must be 1–5 alphanumeric chars (CHAR(5))"

    if path.endswith("region_code"):
        if not re.match(r"^[A-Z0-9]{1,3}$", s, re.IGNORECASE):
            return False, "region_code must be 1–3 alphanumeric chars (CHAR(3))"

    if path.endswith("agency_code"):
        if not AGENCY_CODE_RE.match(s.upper()):
            return False, "agency_code must be 1–6 alphanumeric chars (CHAR(6))"

    if path.endswith("plastic_type"):
        if s.upper() not in PLASTIC_TYPE_ENUM:
            return False, f"plastic_type must be one of: {', '.join(sorted(PLASTIC_TYPE_ENUM))}"

    if path.endswith("product_code"):
        if not PRODUCT_CODE_RE.match(s):
            return False, "product_code must be 1–3 alphanumeric chars (CHAR(3))"

    if path.endswith("service_code"):
        if not SERVICE_CODE_RE.match(s):
            return False, "service_code must be 1–3 chars (CHAR(3))"

    if path.endswith("pvk_index"):
        if not PVK_INDEX_RE.match(s):
            return False, "pvk_index must be a single digit (NUMBER(1,0))"

    if path.endswith("expiration"):
        if not EXPIRATION_RE.match(s):
            return False, "expiration must be 1–3 digits (NUMBER(3,0))"

    if path.endswith("tranche_min") or path.endswith("tranche_max") or path.endswith("start_range") or path.endswith("end_range"):
        if not PAN_RANGE_RE.match(s):
            return False, "PAN range must be 12–19 digits"

    if path.endswith("network"):
        if s.upper() not in NETWORK_ENUM:
            return False, f"network must be one of: {', '.join(sorted(NETWORK_ENUM))}"

    return True, ""


# Fee sub-paths that are actually textual, not numeric
_FEES_STRING_FIELDS = {
    "cards.0.fees.fee_description",
    "cards.0.fees.billing_event",
    "cards.0.fees.billing_period",
}

def validate_value(path: str, value: Any, template_value: Any) -> Tuple[bool, str]:
    # Force strict types for numeric fields even if template value is null.
    if path in _FEES_STRING_FIELDS:
        expected_type = (str, type(None))
    elif path.endswith("_amount") or path.endswith("_count") or path.startswith("cards.0.fees."):
        expected_type = (int, float, type(None))
    else:
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
