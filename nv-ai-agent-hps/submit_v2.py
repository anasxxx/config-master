"""Submit bank CDM with properly mapped payload fields."""
import requests, json, sys

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

# Clean staging first
print("=== CLEAN STAGING ===")
r = requests.post(f"{base}/v1/api/banks/diag/clean-staging", headers=h)
print(json.dumps(r.json(), indent=2))

# The payload must match the Module classes EXACTLY:
# - MigBinRangePlasticProdModule: bankCode, description, bin, plasticType, productType, productCode(3),
#     trancheMin, trancheMax, indexPvk, serviceCode, network, expiration(2), renew(1), priorExp(1)
# - PreMigCardFeesModule: bankCode, description, cardFeesCode(3), cardFeesBillingEvt(1),
#     cardFeesGracePeriod(int), cardFeesBillingPeriod(1), subscriptionAmount, feesAmountFirst,
#     damagedReplacementFees, pinReplacementFees
# - MigServiceProdModule: bankCode, productCode(3), retrait(1), achat(1), advance(1), ecommerce(1),
#     transfert(1), quasicash(1), solde(1), releve(1), pinchange(1), refund(1), moneysend(1),
#     billpayment(1), original(1), authentication(1), cashback(1)
# - MigLimitStandModule: bankCode, productCode(4), limitsId(3), dailyDomAmnt, dailyDomNbr(3),
#     dailyIntAmnt, dailyIntNbr(3), dailyTotalAmnt, dailyTotalNbr(3), minAmountPerTransaction,
#     maxAmountPerTransaction, weeklyDomAmnt, weeklyDomNbr(3), weeklyIntAmnt, weeklyIntNbr(3),
#     weeklyTotalAmnt, weeklyTotalNbr(3), monthlyDomAmnt, monthlyDomNbr(3), monthlyIntAmnt,
#     monthlyIntNbr(3), monthlyTotalAmnt, monthlyTotalNbr(3)
# - NewBranchModule: bankCode, branchCode, branchWording, regionCode, regionWording, cityCode, cityWording
# - MigResourcesModule: bankCode, resourceWording

payload = {
    "pBusinessDate": "2026-03-03 00:00:00",
    "pBankCode": "12934",                   # CHAR(6) max
    "pBankWording": "CDM",                  # VARCHAR2(40) max
    "pCountryCode": "MA",                   # alpha-2, backend resolves to numeric 504
    "pCurrencyCode": "MAD",                 # alpha-3, backend resolves to numeric 504
    "p_action_flag": "1",                   # 1=create, 0=delete, 2=clean
    "cardProducts": [
        {
            "info": {
                "bankCode": "12934",
                "description": "STANDARD CARD",          # VARCHAR2(50) — used for wording/abrv
                "bin": "123456",                          # VARCHAR2(20)
                "plasticType": "001",                     # VARCHAR2(20) — plastic code
                "productType": "01",                      # VARCHAR2(20) — PL/SQL takes SUBSTR(1,2) for network_card_type
                "productCode": "PRD",                     # VARCHAR2(20) but functionally 3 chars
                "trancheMin": "0000000000000001",         # VARCHAR2(20)
                "trancheMax": "9999999999999999",         # VARCHAR2(20)
                "indexPvk": "0",                          # VARCHAR2(20)
                "serviceCode": "101",                     # VARCHAR2(20)
                "network": "VISA",                        # MUST match PL/SQL: VISA|MCRD|AMEX|DINERS|EUROPAY|GIMN|TAG-YUP|PRIVATIVE
                "expiration": "36",                       # VARCHAR2(2)
                "renew": "3",                             # VARCHAR2(1)
                "priorExp": "1"                           # VARCHAR2(1)
            },
            "fees": {
                "bankCode": "12934",
                "description": "STANDARD FEES",           # VARCHAR2(30)
                "cardFeesCode": "PRD",                    # CHAR(3)
                "cardFeesBillingEvt": "M",                # CHAR(1) — valid: M=Membership,U=Usage,G=Group,R=Renewal,A=Activation
                "cardFeesGracePeriod": 30,                # NUMBER(3,0)
                "cardFeesBillingPeriod": "Y",             # CHAR(1) — valid: R,M,Q,S,Y=Yearly,O=Once,2-9=N-years
                "subscriptionAmount": 100.0,              # NUMBER(18,3)
                "feesAmountFirst": 50.0,                  # NUMBER(18,3)
                "damagedReplacementFees": 25.0,           # NUMBER(18,3)
                "pinReplacementFees": 10.0                # NUMBER(18,3)
            },
            "services": {
                "bankCode": "12934",
                "productCode": "PRD",                     # CHAR(3) — MUST match bin_range.product_code exactly
                # PL/SQL checks IS NOT NULL: null=disabled, "1"=enabled
                "retrait": "1",
                "achat": "1",
                "ecommerce": "1",
                "solde": "1",
                "releve": "1",
                "pinchange": "1"
                # Disabled services are OMITTED (null) — NOT "0"
            },
            "limits": [
                {
                    "bankCode": "12934",
                    "productCode": "LPRD",                # CHAR(4) = "L" + product_code — SUBSTR(2,4)="PRD" must match bin_range
                    "limitsId": "10",                     # CHAR(3) — valid: 1,2,3,4,9,10 — PL/SQL TRIM'd before compare
                    # Monthly-only: PL/SQL checks daily IS NULL AND weekly IS NULL AND monthly IS NOT NULL
                    "monthlyDomAmnt": "50000",            # VARCHAR2(20)
                    "monthlyDomNbr": "200",               # CHAR(3)
                    "monthlyIntAmnt": "25000",            # VARCHAR2(20)
                    "monthlyIntNbr": "100",               # CHAR(3)
                    "monthlyTotalAmnt": "50000",          # VARCHAR2(20)
                    "monthlyTotalNbr": "200",             # CHAR(3)
                    "minAmountPerTransaction": "10",      # VARCHAR2(20)
                    "maxAmountPerTransaction": "50000"    # VARCHAR2(20)
                    # daily* and weekly* fields OMITTED (null) so PL/SQL picks monthly-only branch
                }
            ]
        }
    ],
    "branches": [
        {
            "bankCode": "12934",
            "branchCode": "555",              # dest CHAR(6) max
            "branchWording": "CENTRE",        # VARCHAR2(20) max
            "regionCode": "001",              # dest CHAR(3) max
            "regionWording": "CENTRE",        # VARCHAR2(20) max
            "cityCode": "001",                # dest CHAR(5) max
            "cityWording": "CASABLANCA"       # VARCHAR2(20) max
        }
    ],
    "ressources": [
        # MUST match PL/SQL constants: VISA_BASE1, VISA_SMS, SID, HOST_BANK, MCD_MDS, MCD_CIS, UPI
        {"bankCode": "12934", "resourceWording": "VISA_BASE1"},
        {"bankCode": "12934", "resourceWording": "VISA_SMS"}
    ]
}

print(f"\n=== SUBMITTING BANK ===")
print(f"Payload size: {len(json.dumps(payload))} bytes")
print(f"Bank: {payload['pBankCode']} / {payload['pBankWording']}")

resp = requests.post(f"{base}/v1/api/banks/add", json=payload, headers=h)
print(f"\nHTTP Status: {resp.status_code}")
try:
    body = resp.json()
    print(f"Response: {json.dumps(body, indent=2)[:1000]}")
except:
    print(f"Response text: {resp.text[:500]}")

# Verify in staging tables
print(f"\n=== STAGING TABLE COUNTS ===")
for t in ["st_pre_branch", "st_pre_resources", "st_pre_bin_range_plastic_prod", "st_pre_mig_card_fees", "st_pre_service_prod", "st_pre_limit_stand"]:
    r2 = query(f"SELECT COUNT(*) AS cnt FROM {t}")
    cnt = r2.get("rows", [{}])[0].get("CNT", "?")
    print(f"  {t}: {cnt} rows")

# Check bank in main table
print(f"\n=== BANK IN DATABASE ===")
bank_check = query("SELECT bank_code, bank_wording FROM bank WHERE TRIM(bank_code) = '12934'")
print(f"  {json.dumps(bank_check, indent=2)}")

# Try GET bank
print(f"\n=== GET BANK VIA API ===")
r3 = requests.get(f"{base}/v1/api/banks/getBank/12934", headers=h)
print(f"  Status: {r3.status_code}")
if r3.status_code == 200:
    print(f"  Data: {json.dumps(r3.json(), indent=2)[:500]}")

# Summary
print(f"\n{'='*60}")
if resp.status_code in (200, 201):
    print("[PASS] Bank submission succeeded!")
elif resp.status_code == 400:
    print(f"[FAIL] PL/SQL returned non-zero code")
    # Check PCARD_TRACES for error details
    print(f"\n=== PCARD_TRACES (last 10 for bank 12934) ===")
    traces = query("""
        SELECT trace_id, package_name, function_name, plsql_line, user_message, text
        FROM pcard_traces 
        WHERE LOWER(text) LIKE '%12934%' OR LOWER(user_message) LIKE '%12934%'
           OR trace_id IN (SELECT trace_id FROM pcard_traces WHERE ROWNUM <= 10 ORDER BY trace_id DESC)
        ORDER BY trace_id DESC FETCH FIRST 10 ROWS ONLY
    """)
    for row in traces.get("rows", []):
        print(f"  [{row.get('PACKAGE_NAME','')}.{row.get('FUNCTION_NAME','')}@{row.get('PLSQL_LINE','')}] {row.get('USER_MESSAGE','')} | {row.get('TEXT','')[:120]}")
else:
    print(f"[FAIL] HTTP {resp.status_code}")
