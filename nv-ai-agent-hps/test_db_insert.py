"""
DB Insertion Test — verifies that a full bank payload is accepted by the
Spring Boot backend AND actually stored in the database.

Steps:
  1. Build a complete test payload (using test bank code "ZZT")
  2. POST it to /banks/add  → expects 201
  3. GET  /banks/getBank/ZZT → expects bank to be found in DB
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
TEST_BANK_CODE = "ZZT"   # change this if you get duplicate key errors

MOCK_STATE = {
    "facts": {
        "bank": {
            "name": "Banque Test",  # max 15 chars (PL/SQL ABREV_NAME limit)
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
                    "product_type": "DEBIT",  # bank_pipeline maps to "01" for NETWORK_CARD_TYPE CHAR(2)
                    "product_code": "TST",
                    "pvk_index": "1",
                    "service_code": "101",
                    "network": "VISA",
                    "expiration": "36",
                    "renewal_option": "A",
                    "pre_expiration": "3",
                },
                "card_range": {
                    "start_range": "4455550000000000",
                    "end_range":   "4455559999999999",
                },
                "fees": {
                    "fee_description": "Frais Test",
                    "billing_event": "M",       # M=Membership (valid: M,U,G,R,A)
                    "grace_period": 30,
                    "billing_period": "Y",       # Y=Yearly
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
                                "daily_count": "100",
                                "weekly_amount": "20000",
                                "weekly_count": "500",
                                "monthly_amount": "80000",
                                "monthly_count": "999",
                            },
                            "international": {
                                "daily_amount": "2000",
                                "daily_count": "50",
                                "weekly_amount": "10000",
                                "weekly_count": "200",
                                "monthly_amount": "40000",
                                "monthly_count": "500",
                            },
                            "total": {
                                "daily_amount": "7000",
                                "daily_count": "150",
                                "weekly_amount": "30000",
                                "weekly_count": "700",
                                "monthly_amount": "120000",
                                "monthly_count": "999",
                            },
                            "per_transaction": {
                                "min_amount": "10",
                                "max_amount": "50000",
                            },
                        }
                    },
                },
            }
        ],
    }
}


DIAGNOSTIC_SQL = """
-- ============================================================
-- Run these queries in SQL Developer (F5) to diagnose code=-2
-- ============================================================

-- [1] Find the PL/SQL trace table (shows which function failed)
SELECT '1-TRACE_TABLES' AS check_name, table_name AS result
FROM user_tables
WHERE table_name LIKE '%TRACE%'
   OR table_name LIKE 'PCRD_LOG%'
   OR table_name LIKE '%GENERAL_LOG%'

UNION ALL

-- [2] Count st_new_* tables (AUT_CONV_GLB_TEMP_ROLLBACK needs 80+)
SELECT '2-ST_NEW_COUNT', TO_CHAR(COUNT(*)) || ' st_new_* tables'
FROM user_tables WHERE table_name LIKE 'ST_NEW_%'

UNION ALL

-- [3] Count st_mig_* tables (AUT_CONV_PRODUCT_TEMP_ROLLBACK needs 10+)
SELECT '3-ST_MIG_COUNT', TO_CHAR(COUNT(*)) || ' st_mig_* tables'
FROM user_tables WHERE table_name LIKE 'ST_MIG_%'

UNION ALL

-- [4] Sequences for Sequence_ajustment (expect 9)
SELECT '4-SEQUENCES', sequence_name
FROM user_sequences WHERE sequence_name IN (
  'CHARGEBACK_REASON_CODE_X','CARD_GEN_COUNTERS_X',
  'PCRD_CARD_PROD_PARAM_X','P7_SERVICES_SETUP_X',
  'P7_SERVICES_CRITERIA_X','AUTH_CTRL_VALUE_PARAM_X',
  'ISS_POSTING_RULES_X','STOP_RENEWAL_CRITERIA_X',
  'MER_EXCHANGE_MATRIX_X')

UNION ALL

-- [5] Tables for Sequence_ajustment (expect 9)
SELECT '5-SEQ_TABLES', table_name
FROM user_tables WHERE table_name IN (
  'CHARGEBACK_REASON_CODE','CARD_GEN_COUNTERS',
  'PCRD_CARD_PROD_PARAM','P7_SERVICES_SETUP',
  'P7_SERVICES_CRITERIA','AUTH_CTRL_VALUE_PARAM',
  'ISS_POSTING_RULES','STOP_RENEWAL_CRITERIA',
  'MER_EXCHANGE_MATRIX')

ORDER BY check_name, result;

-- Then query the trace table found in [1]:
-- SELECT * FROM <TRACE_TABLE> ORDER BY 1 DESC FETCH FIRST 20 ROWS ONLY;
""".strip()


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
    print(f"    limitsId              = {card['limits'][0]['limitsId']!r}  (want 1-3 chars, NO zero-pad)")
    print(f"    subscriptionAmount    = {card['fees']['subscriptionAmount']!r}  (want str)")
    print(f"    billingEvt            = {card['fees']['cardFeesBillingEvt']!r}  (want 1 char)")
    print(f"    network               = {card['info']['network']!r}")
    print()

    # ── Step 1b: print full payload for debugging ─────────────────────────
    print("  Full payload:")
    print(json.dumps(payload, indent=4, ensure_ascii=False))
    print()

    # ── Step 1c: cleanup previous run (flag='0') ──────────────────────────
    print("[1c] Sending cleanup call (flag='0') to delete leftovers from previous runs...")
    cleanup_payload = dict(payload)
    cleanup_payload["p_action_flag"] = "0"
    try:
        cleanup_result = submit_bank_req(cleanup_payload, args.api_url, args.token)
        c_status = cleanup_result["status_code"]
        print(f"    Cleanup response: status={c_status}")
        if c_status not in (200, 201):
            print(f"    (Non-success is OK — means nothing to clean up)")
    except requests.exceptions.ConnectionError as e:
        print(f"  [FAIL]  Could not connect to {args.api_url}")
        print(f"          Make sure the Spring Boot backend is running.")
        sys.exit(1)
    print()

    # ── Step 2: submit ────────────────────────────────────────────────────
    print("[2] Submitting to backend (flag='1' — create)...")
    try:
        result = submit_bank_req(payload, args.api_url, args.token)
    except requests.exceptions.ConnectionError as e:
        print(f"  [FAIL]  Could not connect to {args.api_url}")
        print(f"          Make sure the Spring Boot backend is running.")
        print(f"          Error: {e}")
        sys.exit(1)

    status_code = result["status_code"]
    body = result["body"]

    # Backend returns 201 on success, 400 when PL/SQL returns non-zero
    ok_submit = _check(
        "POST /banks/add returned 201 (created)",
        status_code == 201,
        f"status={status_code}",
    )

    if not ok_submit:
        print(f"\n  Response body: {json.dumps(body, indent=4, ensure_ascii=False)}")

        if status_code == 400:
            # Check if it's a validation error (field errors) vs PL/SQL error
            if isinstance(body, dict) and "errors" in body:
                print("\n  => VALIDATION ERROR — the payload has invalid fields:")
                for field, msg in body.get("errors", {}).items():
                    print(f"     {field}: {msg}")
            else:
                print("\n  => PL/SQL returned error code (likely -2).")
                print("     This means the payload was accepted by Spring Boot,")
                print("     inserted into temp tables, but PL/SQL MAIN_BOARD_CONV_PARAM failed.")
                print("\n  IMPORTANT: Check the Spring Boot console output for lines like:")
                print("     '=== PL/SQL CALL DEBUG ==='")
                print("     'PL/SQL raw return = -2'")
                print()
                print("  To find the ACTUAL error, run this in SQL Developer:")
                print("  " + "=" * 60)
                print("  -- Clean up any leftover data from previous runs:")
                print(f"  DELETE FROM CENTER WHERE center_name = '{MOCK_STATE['facts']['bank']['name']}';")
                print(f"  DELETE FROM BANK WHERE bank_code = '{TEST_BANK_CODE}';")
                print(f"  DELETE FROM BANK_ADDENDUM WHERE bank_code = '{TEST_BANK_CODE}';")
                print(f"  DELETE FROM PCARD_TASKS_EXEC_GROUP_BANK WHERE bank_code = '{TEST_BANK_CODE}';")
                print("  COMMIT;")
                print()
                print("  -- Then re-run the test.")
                print("  " + "=" * 60)
        elif status_code == 500:
            print("\n  => INTERNAL SERVER ERROR — check Spring Boot console logs.")
        else:
            print(f"\n  => Unexpected status {status_code}.")

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
