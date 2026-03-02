import argparse
import json
import os
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv

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
    facts = state.get("facts", {})
    bank = facts.get("bank", {})

    bank_code = _to_str(bank.get("bank_code"))
    business_date = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    country_raw = _to_str(bank.get("country"))
    country_code = _country_to_alpha2(country_raw)
    currency_code = _to_str(bank.get("currency"))[:3].upper()

    bank_req: Dict[str, Any] = {
        "pBusinessDate": business_date,
        "pBankCode": bank_code[:10],
        "pBankWording": _to_str(bank.get("name")),
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
                "bankCode": bank_code,
                "branchCode": _to_str(agency.get("agency_code")),
                "branchWording": _to_str(agency.get("agency_name")),
                "regionCode": _to_str(agency.get("region_code")),
                "regionWording": _to_str(agency.get("region")),
                "cityCode": _to_str(agency.get("city_code")),
                "cityWording": _to_str(agency.get("city")),
            }
        )

    # Resources
    for resource in bank.get("resources", []) or []:
        bank_req["ressources"].append(
            {
                "bankCode": bank_code,
                "resourceWording": _to_str(resource),
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

        # expiration max 2 chars, renew / priorExp max 1 char
        expiration_raw = _to_str(card_info.get("expiration"))[:2]
        renew_raw = _to_str(card_info.get("renewal_option"))[:1]
        prior_exp_raw = _to_str(card_info.get("pre_expiration"))[:1]

        info_module = {
            "bankCode": bank_code,
            "description": _to_str(card_info.get("card_description")),
            "bin": _to_str(card_info.get("bin")),
            "plasticType": _to_str(card_info.get("plastic_type")),
            "productType": _to_str(card_info.get("product_type")),
            "productCode": product_code[:20] if product_code else "",
            "trancheMin": _to_str(card_range.get("start_range")),
            "trancheMax": _to_str(card_range.get("end_range")),
            "indexPvk": _to_str(card_info.get("pvk_index")),
            "serviceCode": _to_str(card_info.get("service_code")),
            "network": _to_str(card_info.get("network")),
            "expiration": expiration_raw,
            "renew": renew_raw,
            "priorExp": prior_exp_raw,
        }

        # cardFeesCode: exactly 3 chars – take first 3 of product_code
        fees_code = (product_code or "")[:3].ljust(3, "0")
        # billing event / period: exactly 1 char each
        billing_evt = _to_str(fees.get("billing_event"))[:1] or "1"
        billing_period = _to_str(fees.get("billing_period"))[:1] or "M"

        fees_module = {
            "bankCode": bank_code,
            "description": _to_str(fees.get("fee_description")),
            "cardFeesCode": fees_code,
            "cardFeesBillingEvt": billing_evt,
            "cardFeesGracePeriod": _to_number(fees.get("grace_period")) or 0,
            "cardFeesBillingPeriod": billing_period,
            "subscriptionAmount": float(_to_number_str(fees.get("registration_fee"), "0")),
            "feesAmountFirst": float(_to_number_str(fees.get("periodic_fee"), "0")),
            "damagedReplacementFees": float(_to_number_str(fees.get("replacement_fee"), "0")),
            "pinReplacementFees": float(_to_number_str(fees.get("pin_recalculation_fee"), "0")),
        }

        # Services – ALL 15 flags must be present; default "0", enabled → "1"
        _ALL_SERVICE_KEYS = [
            "retrait", "achat", "advance", "ecommerce", "transfert",
            "quasicash", "solde", "releve", "pinchange", "refund",
            "moneysend", "billpayment", "original", "authentication", "cashback",
        ]
        enabled_services = services.get("enabled", []) or []
        service_flags: Dict[str, str] = {
            "bankCode": bank_code,
            "productCode": product_code,
        }
        for svc_key in _ALL_SERVICE_KEYS:
            service_flags[svc_key] = "0"
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
                    _build_limit_module(bank_code, product_code, limit_id, limit_data)
                )
        else:
            limit_modules.append(
                _build_limit_module(bank_code, product_code, "10", {})
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
    # limitsId must be exactly 3 chars, zero-padded
    lid = _pad(_to_str(limit_id), 3)

    return {
        "bankCode": bank_code,
        "productCode": pc,
        "limitsId": lid,
        "dailyDomAmnt": _to_number_str(domestic.get("daily_amount")),
        "dailyDomNbr": _pad(_to_str(domestic.get("daily_count") or "0"), 3),
        "dailyIntAmnt": _to_number_str(international.get("daily_amount")),
        "dailyIntNbr": _pad(_to_str(international.get("daily_count") or "0"), 3),
        "dailyTotalAmnt": _to_number_str(total.get("daily_amount")),
        "dailyTotalNbr": _pad(_to_str(total.get("daily_count") or "0"), 3),
        "minAmountPerTransaction": _to_number_str(per_tx.get("min_amount")),
        "maxAmountPerTransaction": _to_number_str(per_tx.get("max_amount")),
        "weeklyDomAmnt": _to_number_str(domestic.get("weekly_amount")),
        "weeklyDomNbr": _pad(_to_str(domestic.get("weekly_count") or "0"), 3),
        "weeklyIntAmnt": _to_number_str(international.get("weekly_amount")),
        "weeklyIntNbr": _pad(_to_str(international.get("weekly_count") or "0"), 3),
        "weeklyTotalAmnt": _to_number_str(total.get("weekly_amount")),
        "weeklyTotalNbr": _pad(_to_str(total.get("weekly_count") or "0"), 3),
        "monthlyDomAmnt": _to_number_str(domestic.get("monthly_amount")),
        "monthlyDomNbr": _pad(_to_str(domestic.get("monthly_count") or "0"), 3),
        "monthlyIntAmnt": _to_number_str(international.get("monthly_amount")),
        "monthlyIntNbr": _pad(_to_str(international.get("monthly_count") or "0"), 3),
        "monthlyTotalAmnt": _to_number_str(total.get("monthly_amount")),
        "monthlyTotalNbr": _pad(_to_str(total.get("monthly_count") or "0"), 3),
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
