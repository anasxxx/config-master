import argparse
import json
import os
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv

from agents.value_store import unwrap_facts


def _inflate_flat_facts(facts: Dict[str, Any]) -> Dict[str, Any]:
    """Convert flat dot-notation keys (e.g. 'bank.name') into nested dicts.

    If facts already contain nested dicts (e.g. key 'bank' maps to a dict),
    they are returned as-is.  Only top-level string-valued entries whose keys
    contain dots are inflated.
    """
    # Quick check: if any top-level value is already a dict/list, assume nested
    for v in facts.values():
        if isinstance(v, (dict, list)):
            return facts

    nested: Dict[str, Any] = {}
    for dotted_key, value in facts.items():
        parts = dotted_key.split(".")
        cur = nested
        for i, part in enumerate(parts[:-1]):
            if part.isdigit():
                # array index – parent must be a list
                idx = int(part)
                if not isinstance(cur, list):
                    break
                while len(cur) <= idx:
                    cur.append({})
                cur = cur[idx]
            else:
                nxt_part = parts[i + 1] if i + 1 < len(parts) else ""
                default = [] if nxt_part.isdigit() else {}
                if part not in cur:
                    cur[part] = default
                cur = cur[part]
        leaf = parts[-1]
        if isinstance(cur, dict):
            cur[leaf] = value
    return nested

load_dotenv(override=True)

try:
    import pycountry as _pycountry
except ImportError:
    _pycountry = None

BASE_DIR = Path(__file__).resolve().parent.parent
GOALS_DIR = BASE_DIR / "goals"
DEFAULT_API_URL = os.getenv(
    "CONFIGMASTER_API_URL",
    "http://localhost:8084/configmaster_backend/v1/api",
)

SERVICE_MAP = {
    "retrait": "retrait",
    "withdrawal": "retrait",
    "achat": "achat",
    "achats": "achat",
    "purchase": "achat",
    "cash advance": "advance",
    "advance": "advance",
    "e-commerce": "ecommerce",
    "ecommerce": "ecommerce",
    "transferts": "transfert",
    "transfert": "transfert",
    "quasi-cash": "quasicash",
    "quasicash": "quasicash",
    "consultation solde": "solde",
    "solde": "solde",
    "mini-releve": "releve",
    "mini releve": "releve",
    "releve": "releve",
    "changement pin": "pinchange",
    "pin change": "pinchange",
    "remboursements": "refund",
    "refund": "refund",
    "envoi d'argent": "moneysend",
    "moneysend": "moneysend",
    "paiement factures": "billpayment",
    "billpayment": "billpayment",
    "original": "original",
    "authentification": "authentication",
    "authentication": "authentication",
    "3ds": "authentication",
    "cashback": "cashback",
    # common alternative names from conversation agent
    "atm": "retrait",
    "online": "ecommerce",
    "pos": "achat",
    "tokenization": "original",
    "contactless": "achat",
}

LIMIT_ID_MAP = {
    "default": "10",
    "retrait": "1",
    "purchase": "2",
    "cash_advance": "3",
    "cash advance": "3",
    "quasi-cash": "4",
    "quasicash": "4",
    "e-commerce": "9",
    "ecommerce": "9",
}

# ── PL/SQL network name mapping (PCRD_ST_BOARD_CONV_ISS_PAR LOAD_CARD_TYPE) ──
# PL/SQL checks TRIM(network) against exact strings; unknown → PRIVATIVE (00)
NETWORK_MAP = {
    "visa": "VISA",
    "mastercard": "MCRD",
    "mcrd": "MCRD",
    "amex": "AMEX",
    "american express": "AMEX",
    "diners": "DINERS",
    "europay": "EUROPAY",
    "gimn": "GIMN",
    "tag-yup": "TAG-YUP",
    "privative": "PRIVATIVE",
    # common aliases
    "mc": "MCRD",
    "mci": "MCRD",
    "vis": "VISA",
    "upi": "UPI",
    "unionpay": "UPI",
}

# ── PL/SQL resource_wording exact constants (RELOAD_RESOURCES_PARAM) ──
# Only these 7 values trigger actual resource creation. Anything else is ignored.
VALID_RESOURCE_WORDINGS = {
    "VISA_BASE1", "VISA_SMS", "SID", "HOST_BANK",
    "MCD_MDS", "MCD_CIS", "UPI",
}

# ── PL/SQL product_type → NETWORK_CARD_TYPE mapping ────────────────────────
# st_pre_bin_range_plastic_prod.product_type is assigned directly to
# st_mig_CARD_TYPE.network_card_type which is CHAR(2).
# Descriptive names must be converted to 2-char numeric codes.
# ── product_type mapping: descriptive names → CHAR(2) codes ──────────────
# ParamCorrectif: PRODUCT_TYPE CHAR(2 CHAR), example "CL"
PRODUCT_TYPE_MAP = {
    "debit": "01",
    "db": "01",
    "credit": "02",
    "cr": "02",
    "prepaid": "03",
    "pp": "03",
    "charge": "04",
    "virtual": "05",
    # Supervisor examples — 2-char letter codes
    "classic": "CL",
    "cl": "CL",
    "gold": "GO",
    "go": "GO",
    "platinum": "PL",
    "pl": "PL",
}

# ── plastic_type mapping: display names → CHAR(3) codes ──────────────────
# ParamCorrectif: PLASTIC_TYPE CHAR(3 CHAR), example "STD"
PLASTIC_TYPE_MAP = {
    "printed": "STD",
    "standard": "STD",
    "std": "STD",
    "embossed": "EMB",
    "emb": "EMB",
    "virtual": "VIR",
    "virtuel": "VIR",
    "vir": "VIR",
    # Legacy values — map to closest equivalent
    "pvc": "STD",
    "metal": "EMB",
    "other": "STD",
}

RESOURCE_WORDING_MAP = {
    "visa": "VISA_BASE1",
    "visa_base1": "VISA_BASE1",
    "visa base1": "VISA_BASE1",
    "visa_sms": "VISA_SMS",
    "visa sms": "VISA_SMS",
    "sid": "SID",
    "host": "HOST_BANK",
    "host_bank": "HOST_BANK",
    "host bank": "HOST_BANK",
    "mastercard": "MCD_MDS",
    "mcd_mds": "MCD_MDS",
    "mcd_cis": "MCD_CIS",
    "upi": "UPI",
    "unionpay": "UPI",
}


def _load_json(path: Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _normalize_text(value: str) -> str:
    value = value.strip().lower()
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii")
    return value


def _to_str(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def _clip(value: Any, max_len: int) -> str:
    """Convert value to string and enforce backend max length."""
    return _to_str(value)[:max_len]


def _to_number(value: Any) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return value
    try:
        cleaned = str(value).replace(",", "").strip()
        return float(cleaned)
    except (ValueError, TypeError):
        return None


def _to_number_str(value: Any, default: str = "0") -> str:
    """Convert to numeric string suitable for backend decimal fields."""
    n = _to_number(value)
    if n is None:
        return default
    if n == int(n):
        return str(int(n))
    return str(n)


def _pad(value: str, width: int, fill: str = "0") -> str:
    """Left-pad a string to the required width."""
    return value.zfill(width) if value else fill * width


# ── Country name → ISO 3166-1 alpha-2 code ──────────────────────────────────
_COUNTRY_NAME_TO_ALPHA2 = {
    "maroc": "MA", "morocco": "MA",
    "france": "FR",
    "suisse": "CH", "switzerland": "CH",
    "ghana": "GH",
    "tunisie": "TN", "tunisia": "TN",
    "algerie": "DZ", "algeria": "DZ",
    "espagne": "ES", "spain": "ES",
    "marshall islands": "MH",
    "united states": "US", "usa": "US",
    "united kingdom": "GB", "uk": "GB",
    "germany": "DE", "allemagne": "DE",
    "italy": "IT", "italie": "IT",
    "canada": "CA",
    "senegal": "SN", "sénégal": "SN",
    "cote d'ivoire": "CI", "côte d'ivoire": "CI",
    "cameroon": "CM", "cameroun": "CM",
    "niger": "NE", "nigeria": "NG",
    "mali": "ML", "benin": "BJ", "bénin": "BJ",
    "togo": "TG", "gabon": "GA",
    "egypt": "EG", "egypte": "EG",
    "south africa": "ZA", "afrique du sud": "ZA",
}


def _country_to_alpha2(name: str) -> str:
    """Best-effort conversion of a country name to its ISO alpha-2 code."""
    if not name:
        return ""
    raw = name.strip()
    # Already a 2-char code?
    if len(raw) == 2 and raw.isalpha():
        return raw.upper()
    low = raw.lower()
    if low in _COUNTRY_NAME_TO_ALPHA2:
        return _COUNTRY_NAME_TO_ALPHA2[low]
    # Try pycountry fuzzy search
    if _pycountry is not None:
        try:
            c = _pycountry.countries.search_fuzzy(raw)[0]
            return c.alpha_2
        except Exception:
            pass
    # Last resort: return first 2 chars
    return raw[:2].upper()


def find_latest_state(goals_dir: Path) -> Optional[Path]:
    state_files = list(goals_dir.glob("**/state.json"))
    if not state_files:
        return None
    return max(state_files, key=lambda p: p.stat().st_mtime)


def map_facts_to_bank_req(state: Dict[str, Any]) -> Dict[str, Any]:
    raw_facts = unwrap_facts(state.get("facts", {}))
    facts = _inflate_flat_facts(raw_facts)
    bank = facts.get("bank", {})

    bank_code = _to_str(bank.get("bank_code"))
    business_date = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    country_raw = _to_str(bank.get("country"))
    country_code = _country_to_alpha2(country_raw)
    currency_code = _to_str(bank.get("currency"))[:3].upper()

    bank_req: Dict[str, Any] = {
        "pBusinessDate": business_date,
        "pBankCode": bank_code[:6],
        "pBankWording": _clip(bank.get("name"), 40),  # ParamCorrectif: bank_name VARCHAR2(40 CHAR)
        "pCountryCode": country_code,
        "pCurrencyCode": currency_code,
        "p_action_flag": "1",
        "cardProducts": [],
        "branches": [],
        "ressources": [],
    }

    # Branches
    agencies = bank.get("agencies", []) or bank.get("branches", [])
    for agency in agencies:
        bank_req["branches"].append(
            {
                "bankCode": bank_code[:6],
                "branchCode": _clip(agency.get("agency_code"), 6),   # CHAR(6)
                "branchWording": _clip(agency.get("agency_name"), 40),  # VARCHAR2(40)
                "regionCode": _clip(agency.get("region_code"), 3),   # CHAR(3)
                "regionWording": _clip(agency.get("region"), 30),    # VARCHAR2(30)
                "cityCode": _clip(agency.get("city_code"), 5),      # CHAR(5)
                "cityWording": _clip(agency.get("city"), 32),        # VARCHAR2(32)
            }
        )

    # Resources — PL/SQL only recognizes specific constants
    for resource in bank.get("resources", []) or []:
        raw_wording = _to_str(resource).strip()
        # Try to map to a valid PL/SQL resource wording
        mapped = RESOURCE_WORDING_MAP.get(raw_wording.lower(), raw_wording.upper())
        if mapped in VALID_RESOURCE_WORDINGS:
            bank_req["ressources"].append(
                {
                    "bankCode": bank_code[:6],
                    "resourceWording": mapped,
                }
            )

    # Cards
    for card in facts.get("cards", []) or []:
        card_info = card.get("card_info", {})
        card_range = card.get("card_range", {})
        fees = card.get("fees", {})
        services = card.get("services", {})
        limits = card.get("limits", {})

        product_code = _to_str(card_info.get("product_code"))
        product_code_3 = product_code[:3].ljust(3, "0") if product_code else "000"

        # ParamCorrectif: expiration NUMBER(3,0), renewal_option CHAR(1) Y/N,
        # pre_expiration NUMBER(2,0)
        expiration_raw = _to_str(card_info.get("expiration"))[:3]
        # Renewal: supervisor uses Y/N. Map legacy A/M to Y/N.
        renew_val = _to_str(card_info.get("renewal_option")).strip().upper()[:1]
        RENEWAL_MAP = {"A": "Y", "M": "N", "Y": "Y", "N": "N",
                       "O": "Y", "1": "Y", "0": "N"}
        renew_raw = RENEWAL_MAP.get(renew_val, renew_val or "Y")
        prior_exp_raw = _to_str(card_info.get("pre_expiration"))[:2]

        # product_type → NETWORK_CARD_TYPE (CHAR(2)): map descriptive names to 2-char codes
        raw_product_type = _to_str(card_info.get("product_type")).strip()
        if len(raw_product_type) <= 2:
            product_type_code = raw_product_type  # already a short code
        else:
            product_type_code = PRODUCT_TYPE_MAP.get(raw_product_type.lower(), "01")

        # plastic_type → CHAR(3): map display names to 3-char codes
        raw_plastic = _to_str(card_info.get("plastic_type")).strip()
        if len(raw_plastic) <= 3 and raw_plastic.upper() in {"STD", "EMB", "VIR"}:
            plastic_code = raw_plastic.upper()
        else:
            plastic_code = PLASTIC_TYPE_MAP.get(raw_plastic.lower(), raw_plastic[:3].upper() or "STD")

        info_module = {
            "bankCode": bank_code[:6],
            "description": _clip(card_info.get("card_description"), 40),  # VARCHAR2(40)
            "bin": _clip(card_info.get("bin"), 11),  # VARCHAR2(11)
            "plasticType": plastic_code,  # CHAR(3)
            "productType": product_type_code,
            "productCode": product_code_3,
            "trancheMin": _clip(card_range.get("start_range"), 20),
            "trancheMax": _clip(card_range.get("end_range"), 20),
            "indexPvk": _clip(card_info.get("pvk_index"), 20),
            "serviceCode": _clip(card_info.get("service_code"), 20),
            "network": NETWORK_MAP.get(
                _to_str(card_info.get("network")).strip().lower(), "VISA"
            ),
            "expiration": expiration_raw,
            "renew": renew_raw,
            "priorExp": prior_exp_raw,
        }

        # cardFeesCode: exactly 3 chars – take first 3 of product_code
        fees_code = product_code_3

        # ParamCorrectif: card_fees_billing_evt CHAR(1) ENUM "1"|"2"|"3"
        VALID_BILLING_EVT = {"1", "2", "3"}
        billing_evt_raw = _to_str(fees.get("billing_event")).strip()[:1]
        billing_evt = billing_evt_raw if billing_evt_raw in VALID_BILLING_EVT else "1"

        # ParamCorrectif: card_fees_billing_period CHAR(1) ENUM "M"|"A"|"T"|"S"
        VALID_BILLING_PERIOD = {"M", "A", "T", "S"}
        BILLING_PERIOD_MAP = {
            "annual": "A", "yearly": "A", "year": "A", "annuel": "A",
            "monthly": "M", "month": "M", "mensuel": "M",
            "quarterly": "T", "quarter": "T", "trimestriel": "T",
            "semi-annual": "S", "semiannual": "S", "semi": "S", "semestriel": "S",
            # Legacy mappings
            "y": "A", "q": "T", "r": "M", "o": "A",
        }
        billing_period_raw = _to_str(fees.get("billing_period")).strip().lower()
        if billing_period_raw.upper() in VALID_BILLING_PERIOD:
            billing_period = billing_period_raw.upper()
        else:
            billing_period = BILLING_PERIOD_MAP.get(billing_period_raw, "A")

        fees_module = {
            "bankCode": bank_code[:6],
            "description": _clip(fees.get("fee_description"), 32),  # VARCHAR2(32)
            "cardFeesCode": fees_code,
            "cardFeesBillingEvt": billing_evt,
            "cardFeesGracePeriod": int(_to_number(fees.get("grace_period")) or 0),
            "cardFeesBillingPeriod": billing_period,
            "subscriptionAmount": _to_number_str(fees.get("registration_fee"), "0"),
            "feesAmountFirst": _to_number_str(fees.get("periodic_fee"), "0"),
            "damagedReplacementFees": _to_number_str(fees.get("replacement_fee"), "0"),
            "pinReplacementFees": _to_number_str(fees.get("pin_recalculation_fee"), "0"),
        }

        # Services — PL/SQL checks IS NOT NULL: null=disabled, "1"=enabled
        _ALL_SERVICE_KEYS = [
            "retrait", "achat", "advance", "ecommerce", "transfert",
            "quasicash", "solde", "releve", "pinchange", "refund",
            "moneysend", "billpayment", "original", "authentication", "cashback",
        ]
        enabled_services = services.get("enabled", []) or []
        service_flags: Dict[str, Any] = {
            "bankCode": bank_code[:6],
            "productCode": product_code_3,
        }
        # Start with all flags as None (null → disabled in PL/SQL)
        for svc_key in _ALL_SERVICE_KEYS:
            service_flags[svc_key] = None
        # Set enabled services to "1"
        for raw in enabled_services:
            norm = _normalize_text(_to_str(raw))
            key = SERVICE_MAP.get(norm)
            if key:
                service_flags[key] = "1"

        # Limits
        limit_modules: List[Dict[str, Any]] = []
        by_type = limits.get("by_type", {}) or {}
        if by_type:
            for limit_key, limit_data in by_type.items():
                limit_id = LIMIT_ID_MAP.get(_normalize_text(str(limit_key)), "10")
                limit_modules.append(
                    _build_limit_module(bank_code[:6], product_code_3, limit_id, limit_data)
                )
        else:
            limit_modules.append(
                _build_limit_module(bank_code[:6], product_code_3, "10", {})
            )

        bank_req["cardProducts"].append(
            {
                "info": info_module,
                "fees": fees_module,
                "services": service_flags,
                "limits": limit_modules,
            }
        )

    return bank_req


def _build_limit_module(
    bank_code: str,
    product_code: str,
    limit_id: str,
    limit_data: Dict[str, Any],
) -> Dict[str, Any]:
    domestic = limit_data.get("domestic", {}) if isinstance(limit_data, dict) else {}
    international = (
        limit_data.get("international", {}) if isinstance(limit_data, dict) else {}
    )
    total = limit_data.get("total", {}) if isinstance(limit_data, dict) else {}
    per_tx = (
        limit_data.get("per_transaction", {}) if isinstance(limit_data, dict) else {}
    )

    # productCode must be exactly 4 chars (e.g. "LABC")
    pc = f"L{product_code}" if product_code else "L000"
    pc = pc[:4].ljust(4, "0")
    # limitsId: 1-3 chars — Java @Size(min=1,max=3)
    # PL/SQL compares TRIM(limits_id) against '1','2','3','4','9','10'
    # so we must NOT zero-pad (e.g. '010' ≠ '10')
    lid = _to_str(limit_id)

    # --- Helper: only include period fields that have real values ------
    # PL/SQL uses IS NULL checks to pick the right period combination
    # (monthly-only, weekly-only, weekly+monthly, daily-only, etc.)
    # Sending "0" would make the column non-NULL and break the logic.
    def _amt(val):
        """Return numeric-string or None (→ DB NULL)."""
        n = _to_number(val)
        return _to_number_str(val) if n and n > 0 else None

    def _nbr(val):
        """Return count string or None (→ DB NULL). ParamCorrectif: NUMBER(4,0)."""
        n = _to_number(val)
        if n and n > 0:
            capped = min(int(n), 9999)
            return _pad(_to_str(capped), 3)  # Keep 3-char pad for backward compat
        return None

    return {
        "bankCode": bank_code,
        "productCode": pc,
        "limitsId": lid,
        "dailyDomAmnt": _amt(domestic.get("daily_amount")),
        "dailyDomNbr": _nbr(domestic.get("daily_count")),
        "dailyIntAmnt": _amt(international.get("daily_amount")),
        "dailyIntNbr": _nbr(international.get("daily_count")),
        "dailyTotalAmnt": _amt(total.get("daily_amount")),
        "dailyTotalNbr": _nbr(total.get("daily_count")),
        "minAmountPerTransaction": _to_number_str(per_tx.get("min_amount")),
        "maxAmountPerTransaction": _to_number_str(per_tx.get("max_amount")),
        "weeklyDomAmnt": _amt(domestic.get("weekly_amount")),
        "weeklyDomNbr": _nbr(domestic.get("weekly_count")),
        "weeklyIntAmnt": _amt(international.get("weekly_amount")),
        "weeklyIntNbr": _nbr(international.get("weekly_count")),
        "weeklyTotalAmnt": _amt(total.get("weekly_amount")),
        "weeklyTotalNbr": _nbr(total.get("weekly_count")),
        "monthlyDomAmnt": _amt(domestic.get("monthly_amount")),
        "monthlyDomNbr": _nbr(domestic.get("monthly_count")),
        "monthlyIntAmnt": _amt(international.get("monthly_amount")),
        "monthlyIntNbr": _nbr(international.get("monthly_count")),
        "monthlyTotalAmnt": _amt(total.get("monthly_amount")),
        "monthlyTotalNbr": _nbr(total.get("monthly_count")),
    }


def submit_bank_req(
    bank_req: Dict[str, Any],
    api_base_url: str,
    token: str,
) -> Dict[str, Any]:
    url = api_base_url.rstrip("/") + "/banks/add"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(url, json=bank_req, headers=headers, timeout=60)
    return {
        "status_code": response.status_code,
        "body": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text,
    }


def verify_bank(
    api_base_url: str,
    token: str,
    bank_code: str,
) -> Dict[str, Any]:
    url = api_base_url.rstrip("/") + f"/banks/getBank/{bank_code}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers, timeout=60)
    return {
        "status_code": response.status_code,
        "body": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text,
    }


def write_artifacts(goal_dir: Path, payload: Dict[str, Any], submission: Dict[str, Any], verification: Optional[Dict[str, Any]]) -> None:
    artifacts_dir = goal_dir / "artifacts"
    _save_json(artifacts_dir / "bank_payload.json", payload)
    _save_json(artifacts_dir / "submission_result.json", submission)
    if verification is not None:
        _save_json(artifacts_dir / "verification.json", verification)


def run_pipeline(
    state_path: Optional[Path] = None,
    api_base_url: Optional[str] = None,
    token: Optional[str] = None,
    do_verify: bool = True,
) -> Dict[str, Any]:
    if state_path is None:
        state_path = find_latest_state(GOALS_DIR)
        if state_path is None:
            raise FileNotFoundError("No state.json found in goals directory.")

    state = _load_json(state_path)
    bank_req = map_facts_to_bank_req(state)

    api_url = api_base_url or DEFAULT_API_URL
    auth_token = token or os.getenv("CONFIGMASTER_TOKEN")
    if not auth_token:
        raise ValueError("Missing API token. Set CONFIGMASTER_TOKEN or pass --token.")

    submission = submit_bank_req(bank_req, api_url, auth_token)
    verification = None
    if do_verify:
        bank_code = bank_req.get("pBankCode", "")
        if bank_code:
            verification = verify_bank(api_url, auth_token, bank_code)

    goal_dir = state_path.parent
    write_artifacts(goal_dir, bank_req, submission, verification)

    return {
        "state_path": str(state_path),
        "submission": submission,
        "verification": verification,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Submit bank data from a goal state.json")
    parser.add_argument("--state", help="Path to a specific state.json")
    parser.add_argument("--api-url", help="Override API base URL")
    parser.add_argument("--token", help="Bearer token for API authentication")
    parser.add_argument("--no-verify", action="store_true", help="Skip verification call")
    args = parser.parse_args()

    state_path = Path(args.state) if args.state else None
    result = run_pipeline(
        state_path=state_path,
        api_base_url=args.api_url,
        token=args.token,
        do_verify=not args.no_verify,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
