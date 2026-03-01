import argparse
import json
import sys
import hmac
import hashlib
import base64
from datetime import datetime
from datetime import timedelta
from pathlib import Path
from typing import Any, Dict

import requests


BASE_DIR = Path(__file__).resolve().parents[1]
GOALS_DIR = BASE_DIR / "goals"

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from agents.bank_pipeline import run_pipeline


def build_test_state(bank_code: str) -> Dict[str, Any]:
    return {
        "meta": {
            "goal_id": -1,
            "client": "auto",
            "client_n": 0,
            "action": "other",
            "created_at": datetime.now().isoformat(timespec="seconds"),
        },
        "goal": "automated smoke test",
        "facts": {
            "bank": {
                "name": "CIH",
                "country": "Maroc",
                "country_alpha2": "MA",
                "currency": "MAD",
                "bank_code": bank_code,
                "resources": ["accounts", "cards", "transactions"],
                "agencies": [
                    {
                        "agency_name": "Agence Centre",
                        "agency_code": "555",
                        "city": "Casablanca",
                        "city_code": "001",
                        "region": "Grand Casablanca",
                        "region_code": "10",
                    }
                ],
            },
            "cards": [
                {
                    "card_info": {
                        "bin": "445555",
                        "plastic_type": "PVC",
                        "card_description": "Carte Classic",
                        "product_type": "DEBIT, CREDIT",
                        "product_code": "001",
                        "pvk_index": "1",
                        "service_code": "101",
                        "network": "VISA",
                        "expiration": "36",
                        "renewal_option": "AUTO",
                        "pre_expiration": "30",
                    },
                    "card_range": {
                        "start_range": "",
                        "end_range": "",
                    },
                    "fees": {
                        "fee_description": "FRAIS",
                        "billing_event": "ISSUANCE, RENEWAL",
                        "grace_period": "30",
                        "billing_period": "YEARLY",
                        "registration_fee": "50",
                        "periodic_fee": "10",
                        "replacement_fee": "25",
                        "pin_recalculation_fee": "5",
                    },
                    "services": {
                        "enabled": ["3DS", "TOKENIZATION"],
                    },
                    "limits": {
                        "by_type": {
                            "DEFAULT": {
                                "domestic": {
                                    "daily_amount": "5000",
                                    "weekly_amount": "20000",
                                    "monthly_amount": "80000",
                                },
                                "international": {
                                    "daily_amount": "2000",
                                    "weekly_amount": "10000",
                                    "monthly_amount": "40000",
                                },
                            }
                        }
                    },
                }
            ],
        },
        "history": [],
        "done": True,
    }


def fetch_token(api_url: str, email: str, password: str) -> str:
    url = api_url.rstrip("/") + "/login"
    resp = requests.post(url, json={"email": email, "password": password}, timeout=30)
    resp.raise_for_status()
    body = resp.json()
    token = body.get("token")
    if not token:
        raise ValueError("Login response does not contain token")
    return token


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def build_test_jwt(secret: str, subject: str, hours_valid: int = 24) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    exp = int((datetime.utcnow() + timedelta(hours=hours_valid)).timestamp())
    payload = {"sub": subject, "exp": exp}

    header_b64 = _b64url(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_b64 = _b64url(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
    signature = hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
    sig_b64 = _b64url(signature)
    return f"{header_b64}.{payload_b64}.{sig_b64}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Automated smoke test for bank pipeline")
    parser.add_argument("--api-url", default="http://localhost:8084/configmaster_backend/v1/api")
    parser.add_argument("--email")
    parser.add_argument("--password")
    parser.add_argument("--token")
    parser.add_argument("--generate-token", action="store_true")
    parser.add_argument("--subject", default="full@gmail.com")
    parser.add_argument("--jwt-secret", default="ConfigMasterJwtSecretKeyForHs256MustBeAtLeast32CharsLong")
    parser.add_argument("--bank-code", default="000345")
    parser.add_argument("--verify", action="store_true", help="Call verification endpoint after submit")
    args = parser.parse_args()

    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    goal_dir = GOALS_DIR / f"auto_{run_id}_other"
    state_path = goal_dir / "state.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)

    state = build_test_state(args.bank_code)
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

    token = args.token
    if not token:
        if args.generate_token:
            token = build_test_jwt(args.jwt_secret, args.subject)
        else:
            if not args.email or not args.password:
                raise ValueError("Provide --token, or --generate-token, or both --email and --password")
            token = fetch_token(args.api_url, args.email, args.password)

    result = run_pipeline(
        state_path=state_path,
        api_base_url=args.api_url,
        token=token,
        do_verify=args.verify,
    )

    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"State: {state_path}")
    print(f"Artifacts: {goal_dir / 'artifacts'}")


if __name__ == "__main__":
    main()
