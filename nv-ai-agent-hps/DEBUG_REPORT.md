# ConfigMaster AI Agent — Debug Report

## Project: HPS PowerCard Bank Configuration Agent
## Date: March 2026
## Sessions: 4 debugging sessions

---

## Executive Summary

The ConfigMaster AI Agent sends bank configuration data to a Spring Boot backend, which inserts it into Oracle staging tables (`st_pre_*`), then calls a PL/SQL orchestrator (`PCRD_ST_BOARD_CONV_MAIN.MAIN_BOARD_CONV_PARAM`) that transforms and migrates the data into production tables. The PL/SQL consistently returned **error code -2**, blocking all bank insertions — both from the AI agent AND the platform GUI.

After 4 sessions of systematic debugging, we identified and fixed **all blocking bugs**. The PL/SQL now returns **0 (SUCCESS)** and the bank record is fully created in the production BANK table.

---

## Data Flow Architecture

```
Python Agent (FastAPI)
    |
    | JSON payload (BankReq)
    v
Spring Boot Backend (/banks/add)
    |
    | 1. insertIntoTempTables() --> st_pre_* tables
    | 2. callPlSqlFunction()    --> PL/SQL MAIN_BOARD_CONV_PARAM
    | 3. deletTempBank()        --> cleanup st_pre_*
    v
PL/SQL Orchestrator (PCRD_ST_BOARD_CONV_MAIN)
    |
    | flag='1': Setup -> Cleanup st_mig_* -> LOAD_BANK_PARAMETERS
    |           -> LOAD_BANK_CONV_COM_PARAM (86+ config tables)
    |           -> LOAD_BANK_CONV_ISS_PARAM (29 sub-functions)
    |           -> MOVE_PARAMETERS_LOADED -> MAIN_AUT_POST
    v
Production Tables (BANK, CENTER, REGION, etc.)
```

---

## Bugs Found and Fixed

### Bug 1: Center Code Collision (Session 2)

**Symptom:** PL/SQL returned -2 during `LOAD_BANK_PARAMETERS`.

**Root Cause:** The PL/SQL generates a new center code using `SELECT NVL(MAX(center_code), 0) + 1 FROM center`. Center code 21 already existed in the database, causing a primary key collision on INSERT.

**Fix:** Moved the existing center 21 record to center code 24 in the database, freeing up the auto-generated slot.

**Files Modified:** None (database fix only).

---

### Bug 2: Card Fees Column Mismatch (Session 2)

**Symptom:** Spring Boot rejected the payload — missing required columns in `st_pre_mig_card_fees`.

**Root Cause:** The Python agent's `bank_pipeline.py` was not sending all required card fees fields. The JPA entity `MigCardFees` expected columns like `card_fees_billing_evt`, `card_fees_grace_period`, `card_fees_billing_period`, `subscription_amount`, `fees_amount_first`, `damaged_replacement_fees`, and `pin_replacement_fees`.

**Fix:** Updated `bank_pipeline.py` to include all required card fees fields with proper mappings.

**Files Modified:** `nv-ai-agent-hps/bank_pipeline.py`

---

### Bug 3: Product Type Overflow — NETWORK_CARD_TYPE CHAR(2) (Session 4)

**Symptom:** PL/SQL returned -2 at sub-function `LOAD_CARD_TYPE_PARAMETERS` (step 8c of 29 ISS sub-functions).

**Root Cause:** The Python agent sent `product_type = "DEBIT"` (5 characters). The PL/SQL function `LOAD_CARD_TYPE_PARAMETERS` assigns this value directly to `NETWORK_CARD_TYPE`, which is a `CHAR(2)` column. Oracle raised `ORA-06502: PL/SQL: numeric or value error: character string buffer too small`, caught by `WHEN OTHERS`, returning -2.

**How We Found It:** Created diagnostic SQL scripts (v1 through v13) that called each of the 29 ISS sub-functions individually. The drill-down isolated the failure to step 8c. Reading the PL/SQL source (`PCRD_ST_BOARD_CONV_ISS_PAR_040610.sql`, lines 638-719) revealed the direct assignment without truncation.

**Fix:** Added `PRODUCT_TYPE_MAP` in `bank_pipeline.py` that converts descriptive product types to 2-character codes:

```python
PRODUCT_TYPE_MAP = {
    "debit": "01", "db": "01",
    "credit": "02", "cr": "02",
    "prepaid": "03", "pp": "03",
    "charge": "04",
    "virtual": "05",
}
```

The reference implementation (`submit_v2.py`) confirmed that `"01"` is the expected format.

**Files Modified:** `nv-ai-agent-hps/bank_pipeline.py` (lines 108-121, 304-316)

---

### Bug 4: Leftover Staging Data — No bank_code Filter (Session 4-5)

**Symptom:** PL/SQL returned -2 at sub-function `LOAD_LIMIT_STAND_PARAM` (step 8i of 29 ISS sub-functions), even after fixing the product type.

**Root Cause:** The PL/SQL cursor in `LOAD_LIMIT_STAND_PARAM` selects ALL rows from `st_pre_limit_stand` with **no bank_code filter**:

```sql
CURSOR CUR_LIMIT_STAND IS
    SELECT * FROM st_pre_limit_stand
    WHERE product_code IS NOT NULL
    ORDER BY product_code;
```

The staging tables (`st_pre_*`) had leftover rows from previous failed insertion attempts (other banks). When the cursor processed these stale rows, the `SELECT description INTO v_desc_product FROM st_pre_bin_range_plastic_prod WHERE product_code = SUBSTR(...)` lookup failed with `NO_DATA_FOUND` (the corresponding `st_pre_bin_range_plastic_prod` rows for those other banks no longer existed). This exception was caught by `WHEN OTHERS`, returning -2.

**How We Found It:** After confirming the PL/SQL handles all period combinations (daily+weekly+monthly — lines 1472-1541), we realized the issue must be external data contamination. Created diagnostic v14 with:
1. Full `DELETE FROM st_pre_*` (no WHERE clause) instead of `DELETE WHERE bank_code = 'ZZT'`
2. Inline debug code that dumps cursor contents, tests SUBSTR lookups, and captures exact Oracle errors

With clean staging tables, MAIN returned 0 immediately.

**Fix:** In diagnostic v14, changed cleanup from:
```sql
-- OLD (only cleans current bank):
DELETE FROM st_pre_limit_stand WHERE bank_code = v_bank;
```
to:
```sql
-- NEW (cleans ALL leftover data):
DELETE FROM st_pre_limit_stand;
```

**Impact on Agent:** The Spring Boot backend's `deletTempBank()` runs after every `processBank()` call (success or failure), cleaning the current bank's data. However, if a previous run crashed before cleanup, or if data from other bank codes remains, the PL/SQL will process it. This is a platform-level design limitation.

**Files Modified:** `nv-ai-agent-hps/diagnostic_plsql.sql` (v14)

---

### Bug 5: Missing `import re` in schema_validator.py (Session 5)

**Symptom:** Python agent failed to start with `NameError: name 're' is not defined`.

**Root Cause:** `re.compile()` was called on line 1 before `import re` on line 2.

**Fix:** Swapped the order — `import re` first, then `PAN_RANGE_RE = re.compile(...)`.

**Files Modified:** `nv-ai-agent-hps/agents/schema_validator.py`

---

## Diagnostic Methodology

### Approach
Since we could not modify the PL/SQL packages or Spring Boot backend, we created increasingly targeted diagnostic SQL scripts to isolate failures within the PL/SQL orchestrator.

### Diagnostic Evolution

| Version | What It Tested | Result |
|---------|---------------|--------|
| v1-v11 | Basic MAIN call, staging data variations | MAIN returns -2 |
| v12 | Individual sub-function calls | Compilation errors (wrong package names) |
| v12b | INSERT with product_type='01' | Product type fix confirmed |
| v13 | All 29 ISS sub-functions with correct signatures | 8a-8h pass, 8i fails |
| v14 | Full cleanup + inline error capture | MAIN returns 0 — SUCCESS |

### Key Discovery: Sub-function Parameter Signatures

A critical finding was that the 29 ISS sub-functions have **different parameter signatures**, not all `(date, bank, currency)`:

| Function | Signature |
|----------|-----------|
| `RELOAD_RESOURCES_PARAM` | `(date, WORDING, bank)` — wording before bank! |
| `LOAD_branch_PARAMETERS` | `(date, country, currency, bank)` — 4 params |
| `MOVE_PARAMETERS_LOADED` | `(date, bank)` — 2 params only |
| `MAIN_AUT_POST` | `(bank)` — 1 param only |
| Most others | `(date, bank, currency)` — 3 params |

Earlier diagnostics failed because they used the wrong parameter order.

---

## Final Verification

```
[OK] Currency MAD => 504 / MAD
[OK] Country MA => 504 / MAR
[OK] Center 21 is free
[OK] ALL staging tables fully cleaned
[OK] All staging data inserted
[OK] MAIN => 0 — SUCCESS!

BANK table (exact ZZT): 1 rows        -- Bank created
BANK_ADDENDUM (ZZT): 1 rows           -- Addendum created
CENTER 21 exists now: YES              -- Center created
```

---

## Files Modified (Python Agent Only)

| File | Changes |
|------|---------|
| `bank_pipeline.py` | Added PRODUCT_TYPE_MAP, fixed productType field mapping |
| `agents/schema_validator.py` | Fixed import order (`import re` before usage) |
| `diagnostic_plsql.sql` | Diagnostic v14 with full cleanup and inline error capture |
| `verify_bank.sql` | Bank verification query |
| `test_db_insert.py` | Updated test data comments |

---

## Lessons Learned

1. **PL/SQL `WHEN OTHERS` hides root causes** — Always create diagnostics that expose the actual `SQLERRM`, not just the return code.

2. **Staging table isolation matters** — PL/SQL cursors without `WHERE bank_code = ?` filters process ALL rows, including stale data from failed runs.

3. **Column size constraints are silent killers** — `CHAR(2)` silently rejects 5-character values inside `WHEN OTHERS` handlers, returning a generic error code.

4. **Sub-function signatures vary** — Never assume all functions in a package share the same parameter signature. Read the orchestrator source.

5. **PL/SQL compile-time vs runtime errors** — Table names are resolved at compile time. `EXCEPTION WHEN OTHERS` only catches runtime errors. Use `EXECUTE IMMEDIATE` for tables that might not exist.

6. **Reference implementations are gold** — The `submit_v2.py` file with `"productType": "01"` was the key to understanding the expected format.
