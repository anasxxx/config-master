"""
DB Insertion Test — verifies that a full bank payload is accepted by the
Spring Boot backend AND actually stored in the database.

Steps:
  1. Build a complete test payload (using test bank code "TST")
  2. POST it to /banks/add  → expects 200/201
  3. GET  /banks/getBank/TST → expects bank to be found in DB
  4. Print PASS / FAIL with details

Usage:
  cd nv-ai-agent-hps
  python test_db_insert.py --token <YOUR_JWT_TOKEN>
  python test_db_insert.py --token <TOKEN> --api-url http://localhost:8084/configmaster_backend/v1/api
"""

import argparse
import json
import os
import sys

import requests

from agents.bank_pipeline import map_facts_to_bank_req, submit_bank_req, verify_bank

# ── Test data (all fields required by the backend/PL/SQL) ──────────────────
TEST_BANK_CODE = "TST"   # change this if you get code=-2 (duplicate key)

MOCK_STATE = {
    "facts": {
        "bank": {
            "name": "Banque Test Insertion",
            "country": "Maroc",
            "currency": "MAD",
            "bank_code": TEST_BANK_CODE,
            "resources": ["MCD_MDS"],
            "agencies": [
                {
                    "agency_name": "Agence Test",
                    "agency_code": "001",
                    "city": "Casablanca",
                    "city_code": "01",
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
                    "card_description": "Carte Test",
                    "product_type": "DEBIT",
                    "product_code": "TST",   # 3 chars — same as bank code
                    "pvk_index": "1",
                    "service_code": "101",
                    "network": "VISA",        # PL/SQL valid: VISA/MCRD/AMEX/GIMN/...
                    "expiration": "36",
                    "renewal_option": "A",    # 1 char
                    "pre_expiration": "3",    # 1 char
                },
                "card_range": {
                    "start_range": "4455550000000000",
                    "end_range":   "4455559999999999",
                },
                "fees": {
                    "fee_description": "Frais Test",
                    "billing_event": "A",     # 1 char
                    "grace_period": 30,
                    "billing_period": "Y",    # 1 char
                    "registration_fee": "50",
                    "periodic_fee": "10",
                    "replacement_fee": "25",
                    "pin_recalculation_fee": "5",
                },
                "services": {
                    "enabled": ["Retrait", "Achats", "E-commerce"]
                },
                "limits": {
                    "selected_limit_types": ["DEFAULT"],
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
                    },
                },
            }
        ],
    }
}


def _check(label: str, cond: bool, detail: str = ""):
    status = "[PASS]" if cond else "[FAIL]"
    msg = f"  {status}  {label}"
    if detail:
        msg += f" — {detail}"
    print(msg)
    return cond


def main():
    parser = argparse.ArgumentParser(description="Test DB insertion end-to-end")
    parser.add_argument("--token", required=True, help="Bearer JWT token for the backend")
    parser.add_argument(
        "--api-url",
        default=os.getenv("CONFIGMASTER_API_URL", "http://localhost:8084/configmaster_backend/v1/api"),
        help="Backend API base URL",
    )
    args = parser.parse_args()

    print(f"\n=== ConfigMaster DB Insertion Test ===")
    print(f"API  : {args.api_url}")
    print(f"Bank : {TEST_BANK_CODE}\n")

    # ── Step 1: build payload ──────────────────────────────────────────────
    payload = map_facts_to_bank_req(MOCK_STATE)
    print("[1] Payload built:")
    card = payload["cardProducts"][0]
    print(f"    productCode (info)    = {card['info']['productCode']!r}  (want 3 chars)")
    print(f"    productCode (service) = {card['services']['productCode']!r}  (want 3 chars)")
    print(f"    productCode (limit)   = {card['limits'][0]['productCode']!r}  (want 4 chars)")
    print(f"    subscriptionAmount    = {card['fees']['subscriptionAmount']!r}  (want str)")
    print(f"    billingEvt            = {card['fees']['cardFeesBillingEvt']!r}  (want 1 char)")
    print()

    # ── Step 1b: print full payload for debugging ─────────────────────────
    print("\n  Full payload:")
    print(json.dumps(payload, indent=4, ensure_ascii=False))
    print()

    # ── Step 2: submit ────────────────────────────────────────────────────
    print("[2] Submitting to backend...")
    try:
        result = submit_bank_req(payload, args.api_url, args.token)
    except requests.exceptions.ConnectionError as e:
        print(f"  [FAIL]  Could not connect to {args.api_url}")
        print(f"          Make sure the Spring Boot backend is running.")
        print(f"          Error: {e}")
        sys.exit(1)

    status_code = result["status_code"]
    body = result["body"]
    ok_submit = _check(
        f"POST /banks/add returned 2xx",
        status_code in (200, 201),
        f"status={status_code}",
    )
    if not ok_submit:
        print(f"\n  Response body: {json.dumps(body, indent=4, ensure_ascii=False)}")
        print("\n  => Payload was rejected by the backend (validation error or duplicate key).")
        print("     Check the JSON above for field-level errors.")
        sys.exit(2)

    print(f"  Response: {json.dumps(body, indent=4, ensure_ascii=False)}")
    print()

    # ── Step 3: verify DB ────────────────────────────────────────────────
    print("[3] Verifying in DB (GET /banks/getBank/{code})...")
    try:
        verify = verify_bank(args.api_url, args.token, TEST_BANK_CODE)
    except requests.exceptions.ConnectionError as e:
        print(f"  [FAIL]  Could not reach verify endpoint: {e}")
        sys.exit(1)

    v_status = verify["status_code"]
    v_body   = verify["body"]
    ok_verify = _check(
        f"GET /banks/getBank/{TEST_BANK_CODE} returned 2xx",
        v_status in (200, 201),
        f"status={v_status}",
    )
    if ok_verify:
        print(f"  Bank data found in DB:")
        print(f"  {json.dumps(v_body, indent=4, ensure_ascii=False)}")
    else:
        print(f"  Bank NOT found — data was not stored. Response: {v_body}")

    print()
    overall = ok_submit and ok_verify
    if overall:
        print("=== RESULT: PASS — Data was successfully inserted into the DB ===")
    else:
        print("=== RESULT: FAIL — See details above ===")

    sys.exit(0 if overall else 3)


if __name__ == "__main__":
    main()
