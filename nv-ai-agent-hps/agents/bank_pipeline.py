import argparse
import json
import os
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

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

    bank_req: Dict[str, Any] = {
        "pBusinessDate": business_date,
        "pBankCode": bank_code,
        "pBankWording": _to_str(bank.get("name")),
        "pCountryCode": _to_str(bank.get("country")),
        "pCurrencyCode": _to_str(bank.get("currency")),
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

        info_module = {
            "bankCode": bank_code,
            "description": _to_str(card_info.get("card_description")),
            "bin": _to_str(card_info.get("bin")),
            "plasticType": _to_str(card_info.get("plastic_type")),
            "productType": _to_str(card_info.get("product_type")),
            "productCode": product_code,
            "trancheMin": _to_str(card_range.get("start_range")),
            "trancheMax": _to_str(card_range.get("end_range")),
            "indexPvk": _to_str(card_info.get("pvk_index")),
            "serviceCode": _to_str(card_info.get("service_code")),
            "network": _to_str(card_info.get("network")),
            "expiration": _to_str(card_info.get("expiration")),
            "renew": _to_str(card_info.get("renewal_option")),
            "priorExp": _to_str(card_info.get("pre_expiration")),
        }

        fees_module = {
            "bankCode": bank_code,
            "description": _to_str(fees.get("fee_description")),
            "cardFeesCode": product_code,
            "cardFeesBillingEvt": _to_str(fees.get("billing_event")),
            "cardFeesGracePeriod": _to_number(fees.get("grace_period")),
            "cardFeesBillingPeriod": _to_str(fees.get("billing_period")),
            "subscriptionAmount": _to_number(fees.get("registration_fee")),
            "feesAmountFirst": _to_number(fees.get("periodic_fee")),
            "damagedReplacementFees": _to_number(fees.get("replacement_fee")),
            "pinReplacementFees": _to_number(fees.get("pin_recalculation_fee")),
        }

        # Services
        enabled_services = services.get("enabled", []) or []
        service_flags: Dict[str, str] = {
            "bankCode": bank_code,
            "productCode": product_code,
        }
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

    return {
        "bankCode": bank_code,
        "productCode": f"L{product_code}" if product_code else "",
        "limitsId": limit_id,
        "dailyDomAmnt": _to_str(domestic.get("daily_amount")),
        "dailyDomNbr": _to_str(domestic.get("daily_count")),
        "dailyIntAmnt": _to_str(international.get("daily_amount")),
        "dailyIntNbr": _to_str(international.get("daily_count")),
        "dailyTotalAmnt": _to_str(total.get("daily_amount")),
        "dailyTotalNbr": _to_str(total.get("daily_count")),
        "minAmountPerTransaction": _to_str(per_tx.get("min_amount")),
        "maxAmountPerTransaction": _to_str(per_tx.get("max_amount")),
        "weeklyDomAmnt": _to_str(domestic.get("weekly_amount")),
        "weeklyDomNbr": _to_str(domestic.get("weekly_count")),
        "weeklyIntAmnt": _to_str(international.get("weekly_amount")),
        "weeklyIntNbr": _to_str(international.get("weekly_count")),
        "weeklyTotalAmnt": _to_str(total.get("weekly_amount")),
        "weeklyTotalNbr": _to_str(total.get("weekly_count")),
        "monthlyDomAmnt": _to_str(domestic.get("monthly_amount")),
        "monthlyDomNbr": _to_str(domestic.get("monthly_count")),
        "monthlyIntAmnt": _to_str(international.get("monthly_amount")),
        "monthlyIntNbr": _to_str(international.get("monthly_count")),
        "monthlyTotalAmnt": _to_str(total.get("monthly_amount")),
        "monthlyTotalNbr": _to_str(total.get("monthly_count")),
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
