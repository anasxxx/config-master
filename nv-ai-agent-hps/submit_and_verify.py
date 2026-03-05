"""Submit bank CDM and verify it persists in the database."""
import requests, json, sys, time

base = "http://localhost:8084/configmaster_backend"

# Fresh login
login = requests.post(f"{base}/v1/api/login", json={"email": "full@gmail.com", "password": "full"})
if login.status_code != 200:
    print(f"LOGIN FAILED: {login.status_code} {login.text}")
    sys.exit(1)
token = login.json()["token"]
h = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

def query(sql):
    r = requests.post(f"{base}/v1/api/banks/diag/query", json={"sql": sql}, headers=h)
    return r.json()

def execute(sql):
    r = requests.post(f"{base}/v1/api/banks/diag/execute", json={"sql": sql}, headers=h)
    return r.json()

# ===================== PRE-FLIGHT CHECKS =====================
print("=" * 60)
print("PRE-FLIGHT CHECKS")
print("=" * 60)

# 1) All packages valid
print("\n--- Package Status ---")
pkgs = query("SELECT object_name, object_type, status FROM user_objects WHERE object_type IN ('PACKAGE','PACKAGE BODY') AND object_name LIKE 'PCRD_ST%' ORDER BY object_name, object_type")
all_valid = True
for row in pkgs.get("rows", []):
    st = row["STATUS"]
    mark = "PASS" if st == "VALID" else "FAIL"
    if st != "VALID": all_valid = False
    print(f"  [{mark}] {row['OBJECT_NAME']} ({row['OBJECT_TYPE']}): {st}")

if not all_valid:
    print("\n  Recompiling all packages...")
    for pkg in ["PCRD_ST_CONV_CLEAN", "PCRD_ST_CONV_CATALOGUE", "PCRD_ST_BOARD_CONV_COM", "PCRD_ST_BOARD_CONV_ISS_PAR", "PCRD_ST_BOARD_CONV_MAIN"]:
        for t in ["PACKAGE", "BODY"]:
            try:
                execute(f"ALTER PACKAGE {pkg} COMPILE {t}")
            except:
                pass
    # Re-check
    pkgs = query("SELECT object_name, object_type, status FROM user_objects WHERE object_type IN ('PACKAGE','PACKAGE BODY') AND object_name LIKE 'PCRD_ST%' ORDER BY object_name, object_type")
    for row in pkgs.get("rows", []):
        print(f"  [RE-CHECK] {row['OBJECT_NAME']} ({row['OBJECT_TYPE']}): {row['STATUS']}")

# 2) Clean staging tables
print("\n--- Cleaning Staging Tables ---")
clean = requests.post(f"{base}/v1/api/banks/diag/clean-staging", headers=h)
print(f"  {clean.json()}")

# 3) Verify currency and country resolution
print("\n--- Currency Resolution (MAD) ---")
cur = query("SELECT currency_code, currency_code_alpha FROM currency_table WHERE TRIM(currency_code_alpha) = 'MAD'")
print(f"  {cur}")

print("\n--- Country Resolution (MA -> MAR -> ?) ---")
ctr = query("SELECT country_code, iso_country_alpha, country_wording FROM country WHERE TRIM(iso_country_alpha) = 'MAR'")
print(f"  {ctr}")

# ===================== BANK SUBMISSION =====================
print("\n" + "=" * 60)
print("BANK SUBMISSION")
print("=" * 60)

payload = {
    "pBusinessDate": "2026-03-03 00:00:00.000",
    "pBankCode": "12934",
    "pBankWording": "CDM",
    "pCountryCode": "MA",
    "pCurrencyCode": "MAD",
    "p_action_flag": "1",
    "cardProducts": [
        {
            "info": {
                "productCode": "PRD",
                "productWording": "STANDARD",
                "networkCode": "001",
                "binAcquirer": "123456",
                "cardScheme": "001",
                "servicecode": "101",
                "pinVerificationValue": "00",
                "pvki": "0",
                "cvv": "01",
                "icvv": "01",
                "cardValidityDuration": "36",
                "reissueDuration": "3",
                "seuilOnLine": "10000",
                "seuilAutorisationOffLine": "5000",
                "panLength": "16",
                "chipCard": "0",
                "accountDebitFee": "0",
                "accountCreditFee": "0"
            },
            "fees": {
                "cardFeesCode": "PRD",
                "subscriptionFees": "100",
                "reissueCardFees": "50",
                "renewalFees": "100",
                "oppositionFees": "25",
                "withdrawFees": "0",
                "internationalWithdrawFees": "0",
                "paymentFees": "0",
                "internationalPaymentFees": "0"
            },
            "services": {
                "productCode": "PRD",
                "ecommerce": "1",
                "contactless": "1",
                "withdrawal": "1",
                "payment": "1",
                "cashAdvance": "0",
                "international": "1"
            },
            "limits": [
                {
                    "productCode": "PRD",
                    "limitsId": "010",
                    "globalPlafond": "50000",
                    "globalWithdrawPlafond": "20000",
                    "globalPaymentPlafond": "50000",
                    "weeklyWithdrawPlafond": "10000",
                    "weeklyPaymentPlafond": "30000",
                    "dailyWithdrawPlafond": "5000",
                    "dailyPaymentPlafond": "15000",
                    "globalInterWithdrawPlafond": "10000",
                    "globalInterPaymentPlafond": "25000"
                }
            ]
        }
    ],
    "branches": [
        {
            "branchCode": "555",
            "branchWording": "CENTRE"
        }
    ],
    "ressources": [
        {"resourceWording": "CARDS"},
        {"resourceWording": "TRANSACTIONS"},
        {"resourceWording": "ACCOUNTS"}
    ]
}

print(f"\nPayload size: {len(json.dumps(payload))} bytes")
print(f"Bank: {payload['pBankCode']} / {payload['pBankWording']}")
print(f"Country: {payload['pCountryCode']}, Currency: {payload['pCurrencyCode']}")

resp = requests.post(f"{base}/v1/api/banks/add", json=payload, headers=h)
print(f"\nHTTP Status: {resp.status_code}")
try:
    body = resp.json()
    print(f"Response: {json.dumps(body, indent=2)}")
except:
    print(f"Response text: {resp.text[:500]}")

# ===================== VERIFICATION =====================
print("\n" + "=" * 60)
print("VERIFICATION")
print("=" * 60)

# Check via API
print("\n--- GET Bank via API ---")
r = requests.get(f"{base}/v1/api/banks/getBank/12934", headers=h)
print(f"  Status: {r.status_code}")
if r.status_code == 200:
    try:
        print(f"  Data: {json.dumps(r.json(), indent=2)[:500]}")
    except:
        print(f"  Text: {r.text[:500]}")

# Check directly in DB
print("\n--- Direct DB Check ---")
bank_check = query("SELECT bank_code, bank_wording, country_code, currency_code FROM bank WHERE TRIM(bank_code) = '12934'")
print(f"  Bank table: {json.dumps(bank_check, indent=2)}")

# Check staging tables (should be empty if PL/SQL cleaned up)
print("\n--- Staging Table Status ---")
for tbl in ["MIG_BANQUE", "MIG_BIN_RANGE_PLASTIC_PROD", "MIG_CARD_FEE", "MIG_CARD_SERVICE", "MIG_LIMIT_STAND", "MIG_BRANCH"]:
    r = query(f"SELECT COUNT(*) AS cnt FROM {tbl}")
    cnt = r.get("rows", [{}])[0].get("CNT", "?")
    print(f"  {tbl}: {cnt} rows")

# ===================== SUMMARY =====================
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
if resp.status_code in (200, 201):
    print("[PASS] Bank submission succeeded!")
elif resp.status_code == 400:
    print("[FAIL] Bank submission returned 400 — check PL/SQL result code above")
else:
    print(f"[FAIL] Bank submission returned HTTP {resp.status_code}")
