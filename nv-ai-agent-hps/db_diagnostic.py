#!/usr/bin/env python3
"""
==========================================================
  ConfigMaster — All-in-one Oracle Database Diagnostic
==========================================================
  Connects directly to Oracle, calls PL/SQL step-by-step,
  and reports exactly which step fails and why.

  Usage:
      pip install oracledb
      python db_diagnostic.py

  No Spring Boot needed. No SQL Developer needed.
==========================================================
"""

import sys
import textwrap

try:
    import oracledb
except ImportError:
    print("ERROR: oracledb not installed. Run: pip install oracledb")
    sys.exit(1)

# ── Database connection ────────────────────────────────────────
DB_HOST = "10.110.120.14"
DB_PORT = 1521
DB_SERVICE = "PCARD"
DB_USER = "POWERCARD"
DB_PASS = "pcard001"

# ── Test bank parameters ──────────────────────────────────────
BANK_CODE = "ZZT"
BANK_WORDING = "Banque Test"
CURRENCY_CODE = "MAD"
COUNTRY_CODE = "MA"
ACTION_FLAG_CREATE = "1"
ACTION_FLAG_DELETE = "0"


def connect():
    """Connect to Oracle database."""
    dsn = f"{DB_HOST}:{DB_PORT}/{DB_SERVICE}"
    print(f"Connecting to {dsn} as {DB_USER}...")
    conn = oracledb.connect(user=DB_USER, password=DB_PASS, dsn=dsn)
    print(f"  Connected! Oracle {conn.version}\n")
    return conn


def step(label):
    """Print a step header."""
    print(f"{'─'*60}")
    print(f"  {label}")
    print(f"{'─'*60}")


def ok(msg="OK"):
    print(f"  ✅ {msg}")


def fail(msg):
    print(f"  ❌ {msg}")


def info(msg):
    print(f"  ℹ  {msg}")


# ══════════════════════════════════════════════════════════════
#  PHASE 1: DATABASE HEALTH CHECKS
# ══════════════════════════════════════════════════════════════

def check_prerequisites(conn):
    step("PHASE 1: Prerequisites")
    cur = conn.cursor()

    # Check currency
    cur.execute("SELECT currency_code FROM currency_table WHERE TRIM(currency_code_alpha) = :1", [CURRENCY_CODE])
    row = cur.fetchone()
    if row:
        ok(f"Currency {CURRENCY_CODE} → numeric code {row[0]}")
        currency_numeric = row[0]
    else:
        fail(f"Currency {CURRENCY_CODE} not found in currency_table!")
        return None

    # Check country
    cur.execute("SELECT country_code, iso_country_alpha FROM country WHERE TRIM(iso_country_alpha) = :1", [COUNTRY_CODE])
    row = cur.fetchone()
    if not row:
        # Try 3-char
        cur.execute("SELECT country_code, iso_country_alpha FROM country WHERE TRIM(iso_country_alpha) = :1", ["MAR"])
        row = cur.fetchone()
    if row:
        ok(f"Country {COUNTRY_CODE} → numeric code {row[0]}, alpha={row[1]}")
        country_numeric = row[0]
    else:
        fail(f"Country {COUNTRY_CODE} not found in country table!")
        return None

    # Check center 21 status
    cur.execute("SELECT center_code, center_name FROM center WHERE center_code = '21'")
    row = cur.fetchone()
    if row:
        fail(f"CENTER 21 EXISTS: {row[1]} — this will cause PK collision!")
        info("The PL/SQL always generates center_code=21 for new banks.")
        info("This center must be moved or deleted before any bank can be added.")
        return None
    else:
        ok("Center 21 is FREE (no collision)")

    # Check next center code
    cur.execute("SELECT MAX(TO_NUMBER(NVL(CENTER_CODE,0)))+1 FROM CENTER WHERE CENTER_CODE < '21'")
    row = cur.fetchone()
    info(f"Next center_code PL/SQL would generate: {row[0]}")

    # Check if bank ZZT already exists
    cur.execute("SELECT bank_code, bank_name FROM bank WHERE bank_code = :1", [BANK_CODE])
    row = cur.fetchone()
    if row:
        info(f"Bank {BANK_CODE} already exists: {row[1]} — will cleanup first")
    else:
        info(f"Bank {BANK_CODE} does not exist — clean start")

    # Check required PL/SQL packages exist
    packages = [
        "PCRD_ST_BOARD_CONV_MAIN",
        "PCRD_ST_BOARD_CONV_COM",
        "PCRD_ST_BOARD_CONV_ISS_PAR",
        "PCRD_ST_CONV_CLEAN",
        "PCRD_ST_CONV_CATALOGUE",
    ]
    for pkg in packages:
        cur.execute(
            "SELECT status FROM user_objects WHERE object_name = :1 AND object_type = 'PACKAGE BODY'",
            [pkg]
        )
        row = cur.fetchone()
        if row and row[0] == "VALID":
            ok(f"Package {pkg}: VALID")
        elif row:
            fail(f"Package {pkg}: {row[0]} — needs recompilation!")
        else:
            fail(f"Package {pkg}: NOT FOUND!")
            return None

    cur.close()
    return {"currency": currency_numeric, "country": country_numeric}


# ══════════════════════════════════════════════════════════════
#  PHASE 2: CLEANUP PREVIOUS RUN
# ══════════════════════════════════════════════════════════════

def cleanup(conn):
    step("PHASE 2: Cleanup previous run")
    cur = conn.cursor()
    ret = cur.var(int)

    try:
        cur.execute("""
            BEGIN
                :ret := PCRD_ST_BOARD_CONV_MAIN.MAIN_BOARD_CONV_PARAM(
                    SYSDATE, :bank, :wording, :currency, :country, '0');
            END;
        """, {
            "ret": ret,
            "bank": BANK_CODE,
            "wording": BANK_WORDING,
            "currency": CURRENCY_CODE,
            "country": COUNTRY_CODE,
        })
        conn.commit()
        val = ret.getvalue()
        if val == 0:
            ok(f"Cleanup returned {val}")
        else:
            info(f"Cleanup returned {val} (may be normal if bank didn't exist)")
    except Exception as e:
        info(f"Cleanup error (usually OK): {e}")
        conn.rollback()

    # Also clean staging tables
    for table in [
        "st_pre_bin_range_plastic_prod",
        "st_pre_branch",
        "st_pre_resources",
        "st_pre_mig_card_fees",
        "st_pre_service_prod",
        "st_pre_limit_stand",
    ]:
        try:
            cur.execute(f"DELETE FROM {table} WHERE bank_code = :1", [BANK_CODE])
        except Exception:
            pass  # table might not exist

    # Clean staging mig tables
    for table in [
        "st_mig_card_type", "st_mig_plastic_list", "st_mig_card_fees",
        "st_mig_card_product", "st_mig_card_range",
    ]:
        try:
            cur.execute(f"DELETE FROM {table} WHERE bank_code = :1", [BANK_CODE])
        except Exception:
            pass

    conn.commit()
    cur.close()
    ok("Staging tables cleaned")


# ══════════════════════════════════════════════════════════════
#  PHASE 3: INSERT STAGING DATA
# ══════════════════════════════════════════════════════════════

def insert_staging(conn):
    step("PHASE 3: Insert staging data")
    cur = conn.cursor()

    # Card product — product_type='01' (not 'DEBIT'!)
    try:
        cur.execute("""
            INSERT INTO st_pre_bin_range_plastic_prod
            (bank_code, description, bin, plastic_type, product_type,
             product_code, tranche_min, tranche_max, index_pvk,
             service_code, network, expiration, renew, prior_exp)
            VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14)
        """, [BANK_CODE, "Carte Test", "445555", "PVC", "01", "TST",
              "4455550000000000", "4455559999999999", "1", "101", "VISA", "36", "A", "3"])
        ok("st_pre_bin_range_plastic_prod: inserted")
    except Exception as e:
        fail(f"st_pre_bin_range_plastic_prod: {e}")
        return False

    # Branch
    try:
        cur.execute("""
            INSERT INTO st_pre_branch
            (bank_code, branch_code, branch_wording, region_code,
             region_wording, city_code, city_wording)
            VALUES (:1, :2, :3, :4, :5, :6, :7)
        """, [BANK_CODE, "001", "Agence Test", "10", "Grand Casablanca", "01", "Casablanca"])
        ok("st_pre_branch: inserted")
    except Exception as e:
        fail(f"st_pre_branch: {e}")
        info("Continuing without branch data...")

    # Resource
    try:
        cur.execute("""
            INSERT INTO st_pre_resources (bank_code, resource_wording)
            VALUES (:1, :2)
        """, [BANK_CODE, "VISA_BASE1"])
        ok("st_pre_resources: inserted")
    except Exception as e:
        # Try alternate table name
        try:
            cur.execute("""
                INSERT INTO st_pre_resource (bank_code, resource_wording)
                VALUES (:1, :2)
            """, [BANK_CODE, "VISA_BASE1"])
            ok("st_pre_resource: inserted")
        except Exception as e2:
            fail(f"st_pre_resource(s): {e2}")
            info("Continuing without resource data...")

    # Card fees
    try:
        cur.execute("""
            INSERT INTO st_pre_mig_card_fees
            (bank_code, card_fees_code, description, card_fees_billing_evt,
             card_fees_grace_period, card_fees_billing_period,
             subscription_amount, fees_amount_first,
             damaged_replacement_fees, pin_replacement_fees)
            VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10)
        """, [BANK_CODE, "TST", "Frais Test", "M", 30, "Y", 50, 10, 25, 5])
        ok("st_pre_mig_card_fees: inserted")
    except Exception as e:
        fail(f"st_pre_mig_card_fees: {e}")
        info("Continuing without fees data...")

    # Service prod
    try:
        cur.execute("""
            INSERT INTO st_pre_service_prod
            (bank_code, product_code, retrait, achat, advance, ecommerce,
             transfert, quasicash, solde, releve, pinchange, refund,
             moneysend, billpayment, original)
            VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14, :15)
        """, [BANK_CODE, "TST", "1", "1", None, "1", None, None, None, None, None, None, None, None, None])
        ok("st_pre_service_prod: inserted")
    except Exception as e:
        fail(f"st_pre_service_prod: {e}")
        info("Continuing without service data...")

    # Limits
    try:
        cur.execute("""
            INSERT INTO st_pre_limit_card_product
            (bank_code, product_code, limits_id,
             daily_dom_amnt, daily_dom_nbr, daily_int_amnt, daily_int_nbr,
             daily_total_amnt, daily_total_nbr,
             monthly_dom_amnt, monthly_dom_nbr, monthly_int_amnt, monthly_int_nbr,
             monthly_total_amnt, monthly_total_nbr,
             weekly_dom_amnt, weekly_dom_nbr, weekly_int_amnt, weekly_int_nbr,
             weekly_total_amnt, weekly_total_nbr,
             min_amount_per_transaction, max_amount_per_transaction)
            VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13,
                    :14, :15, :16, :17, :18, :19, :20, :21, :22, :23)
        """, [BANK_CODE, "LTST", "10", 5000, "100", 2000, "050", 7000, "150",
              20000, "500", 10000, "200", 30000, "700",
              80000, "999", 40000, "500", 120000, "999", 10, 50000])
        ok("st_pre_limit_card_product: inserted")
    except Exception as e:
        fail(f"st_pre_limit_card_product: {e}")
        info("Continuing without limits data...")

    conn.commit()
    cur.close()
    return True


# ══════════════════════════════════════════════════════════════
#  PHASE 4: CALL MAIN PL/SQL (like Spring Boot does)
# ══════════════════════════════════════════════════════════════

def call_main_plsql(conn):
    step("PHASE 4: Call MAIN_BOARD_CONV_PARAM (flag='1')")
    cur = conn.cursor()
    ret = cur.var(int)

    try:
        cur.execute("""
            BEGIN
                :ret := PCRD_ST_BOARD_CONV_MAIN.MAIN_BOARD_CONV_PARAM(
                    SYSDATE, :bank, :wording, :currency, :country, :flag);
            END;
        """, {
            "ret": ret,
            "bank": BANK_CODE,
            "wording": BANK_WORDING,
            "currency": CURRENCY_CODE,
            "country": COUNTRY_CODE,
            "flag": ACTION_FLAG_CREATE,
        })
        val = ret.getvalue()
        if val == 0:
            ok(f"MAIN returned {val} — SUCCESS!")
            conn.commit()
            return True
        else:
            fail(f"MAIN returned {val} — FAILED")
            conn.rollback()
            return False
    except Exception as e:
        fail(f"Exception: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()


# ══════════════════════════════════════════════════════════════
#  PHASE 5: DRILL DOWN — call each sub-function individually
# ══════════════════════════════════════════════════════════════

def drill_down(conn):
    step("PHASE 5: Drill-down — calling sub-functions individually")
    cur = conn.cursor()
    ret = cur.var(int)

    # Re-insert staging data (previous call may have been rolled back)
    cleanup(conn)
    insert_staging(conn)

    # ── Steps 1-3: Currency, Country, Sequence ──
    sub_steps = [
        ("5.1", "Sequence_ajustment",
         "BEGIN :ret := PCRD_ST_BOARD_CONV_COM.Sequence_ajustment; END;",
         {}),
    ]
    for label, name, sql, params in sub_steps:
        try:
            p = {"ret": ret}
            p.update(params)
            cur.execute(sql, p)
            val = ret.getvalue()
            if val == 0:
                ok(f"{label} {name} => {val}")
            else:
                fail(f"{label} {name} => {val}")
                return label
        except Exception as e:
            fail(f"{label} {name} => {e}")
            return label

    conn.commit()

    # ── Steps 4-5: Temp rollbacks ──
    for label, name in [
        ("5.2", "AUT_CONV_GLB_TEMP_ROLLBACK"),
        ("5.3", "AUT_CONV_PRODUCT_TEMP_ROLLBACK"),
    ]:
        try:
            cur.execute(f"""
                BEGIN
                    :ret := PCRD_ST_CONV_CLEAN.{name}(:bank, :wording, :country);
                END;
            """, {"ret": ret, "bank": BANK_CODE, "wording": BANK_WORDING, "country": COUNTRY_CODE})
            val = ret.getvalue()
            if val == 0:
                ok(f"{label} {name} => {val}")
            else:
                fail(f"{label} {name} => {val}")
                return label
        except Exception as e:
            fail(f"{label} {name} => {e}")
            return label

    # ── Step 6: LOAD_BANK_PARAMETERS ──
    # This function needs 7 params including alpha codes
    # We need to resolve them first
    try:
        cur.execute("SELECT currency_code, currency_code_alpha FROM currency_table WHERE TRIM(currency_code_alpha) = :1", [CURRENCY_CODE])
        curr_row = cur.fetchone()
        cur.execute("SELECT country_code, iso_country_alpha FROM country WHERE TRIM(iso_country_alpha) IN (:1, :2)", [COUNTRY_CODE, "MAR"])
        country_row = cur.fetchone()

        currency_numeric = str(curr_row[0]).strip() if curr_row else CURRENCY_CODE
        currency_alpha = str(curr_row[1]).strip() if curr_row else CURRENCY_CODE
        country_numeric = str(country_row[0]).strip() if country_row else COUNTRY_CODE
        country_alpha = str(country_row[1]).strip() if country_row else COUNTRY_CODE

        info(f"Currency: {currency_alpha} -> {currency_numeric}")
        info(f"Country: {country_alpha} -> {country_numeric}")
    except Exception as e:
        fail(f"Could not resolve currency/country: {e}")
        return "5.4"

    try:
        cur.execute("""
            BEGIN
                :ret := PCRD_ST_BOARD_CONV_COM.LOAD_BANK_PARAMETERS(
                    SYSDATE, :bank, :wording, :currency, :curr_alpha,
                    :country, :country_alpha);
            END;
        """, {
            "ret": ret,
            "bank": BANK_CODE,
            "wording": BANK_WORDING,
            "currency": currency_numeric,
            "curr_alpha": currency_alpha,
            "country": country_numeric,
            "country_alpha": country_alpha,
        })
        val = ret.getvalue()
        if val == 0:
            ok(f"5.4 LOAD_BANK_PARAMETERS => {val}")
        else:
            fail(f"5.4 LOAD_BANK_PARAMETERS => {val}")
            return "5.4"
    except Exception as e:
        fail(f"5.4 LOAD_BANK_PARAMETERS => {e}")
        return "5.4"

    # ── Step 7: LOAD_BANK_CONV_COM_PARAM ──
    try:
        cur.execute("""
            BEGIN
                :ret := PCRD_ST_BOARD_CONV_COM.LOAD_BANK_CONV_COM_PARAM(
                    SYSDATE, :bank, :wording, :currency, :country);
            END;
        """, {
            "ret": ret,
            "bank": BANK_CODE,
            "wording": BANK_WORDING,
            "currency": currency_numeric,
            "country": country_numeric,
        })
        val = ret.getvalue()
        if val == 0:
            ok(f"5.5 LOAD_BANK_CONV_COM_PARAM => {val}")
        else:
            fail(f"5.5 LOAD_BANK_CONV_COM_PARAM => {val}")
            return "5.5"
    except Exception as e:
        fail(f"5.5 LOAD_BANK_CONV_COM_PARAM => {e}")
        return "5.5"

    # ── Step 8: ISS sub-functions (the 29 steps) ──
    iss_steps = [
        ("8a", "RELOAD_RESOURCES_PARAM"),
        ("8b", "LOAD_branch_PARAMETERS"),
        ("8c", "LOAD_CARD_TYPE_PARAMETERS"),
        ("8d", "LOAD_BIN_RANGE_PLASTIC_PAR"),
        ("8e", "LOAD_CARD_FEES_PARAMETERS"),
        ("8f", "LOAD_SERVICE_PROD_PARAM"),
        ("8g", "LOAD_SERVICE_SETUP_PARAM"),
        ("8h", "LOAD_P7_limits_PARAMETERS"),
        ("8i", "LOAD_LIMIT_STAND_PARAM"),
        ("8j", "LOAD_SA_LIMITS_SETUP_PARAM"),
        ("8k", "LOAD_EMV_LIMIT_SETUP"),
        ("8l", "LOAD_CARD_PRODUCT_PARAM"),
        ("8m", "LOAD_CARD_RANGE_PARAM"),
        ("8n", "LOAD_CARD_GEN_COUNTER_PARAM"),
        ("8o", "LOAD_ISS_POSTING_RULES"),
    ]

    for label, name in iss_steps:
        try:
            cur.execute(f"""
                BEGIN
                    :ret := PCRD_ST_BOARD_CONV_ISS_PAR.{name}(SYSDATE, :bank, :currency);
                END;
            """, {"ret": ret, "bank": BANK_CODE, "currency": currency_numeric})
            val = ret.getvalue()
            if val == 0:
                ok(f"{label} {name} => {val}")
            else:
                fail(f"{label} {name} => {val}")
                # Try to get PCARD_TRACES for error detail
                try:
                    cur.execute("""
                        SELECT user_message FROM pcard_traces
                        WHERE ROWNUM <= 3
                        ORDER BY date_create DESC
                    """)
                    for trow in cur.fetchall():
                        info(f"  TRACE: {trow[0]}")
                except Exception:
                    pass
                return label
        except Exception as e:
            fail(f"{label} {name} => {e}")
            return label

    # Continue with catalogue and remaining steps
    extra_steps = [
        ("8p", "PCRD_ST_CONV_CATALOGUE", "LOAD_CONV_CATALOGUE"),
        ("8q", "PCRD_ST_BOARD_CONV_ISS_PAR", "LOAD_AUTH_CTRL_VALUE_PARAM"),
        ("8r", "PCRD_ST_BOARD_CONV_ISS_PAR", "LOAD_STOP_RENEWAL_CRITERIA"),
        ("8s", "PCRD_ST_BOARD_CONV_ISS_PAR", "LOAD_CARD_PROD_PARAM"),
        ("8t", "PCRD_ST_BOARD_CONV_ISS_PAR", "LOAD_P7_SERVICES_SETUP"),
        ("8u", "PCRD_ST_BOARD_CONV_ISS_PAR", "LOAD_P7_SERVICES_CRITERIA"),
        ("8v", "PCRD_ST_BOARD_CONV_ISS_PAR", "LOAD_MER_EXCHANGE_MATRIX"),
        ("8w", "PCRD_ST_BOARD_CONV_ISS_PAR", "LOAD_CHARGEBACK_REASON_CODE"),
        ("8x", "PCRD_ST_BOARD_CONV_ISS_PAR", "MOVE_PARAMETERS_LOADED"),
        ("8y", "PCRD_ST_BOARD_CONV_ISS_PAR", "MAIN_AUT_POST"),
    ]

    for label, pkg, name in extra_steps:
        try:
            cur.execute(f"""
                BEGIN
                    :ret := {pkg}.{name}(SYSDATE, :bank, :currency);
                END;
            """, {"ret": ret, "bank": BANK_CODE, "currency": currency_numeric})
            val = ret.getvalue()
            if val == 0:
                ok(f"{label} {name} => {val}")
            else:
                fail(f"{label} {name} => {val}")
                return label
        except Exception as e:
            fail(f"{label} {name} => {e}")
            return label

    ok("ALL 29 SUB-FUNCTIONS PASSED!")
    conn.commit()
    cur.close()
    return None


# ══════════════════════════════════════════════════════════════
#  PHASE 6: VERIFY
# ══════════════════════════════════════════════════════════════

def verify(conn):
    step("PHASE 6: Verify bank was created")
    cur = conn.cursor()

    cur.execute("SELECT bank_code, bank_name, abrev_name FROM bank WHERE bank_code = :1", [BANK_CODE])
    row = cur.fetchone()
    if row:
        ok(f"Bank {row[0]} exists! name={row[1]}, abrev={row[2]}")
        return True
    else:
        fail(f"Bank {BANK_CODE} NOT found in BANK table")
        return False


# ══════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print("  ConfigMaster — Oracle Database Diagnostic")
    print("=" * 60)
    print()

    conn = connect()

    # Phase 1: Prerequisites
    resolved = check_prerequisites(conn)
    if resolved is None:
        print("\n⛔ Prerequisites failed. Fix the issues above first.")
        conn.close()
        return

    # Phase 2: Cleanup
    cleanup(conn)

    # Phase 3: Insert staging data
    if not insert_staging(conn):
        print("\n⛔ Could not insert staging data.")
        conn.close()
        return

    # Phase 4: Call main PL/SQL
    success = call_main_plsql(conn)

    if success:
        print()
        verify(conn)
        print()
        print("🎉 " + "=" * 56)
        print("🎉  BANK INSERTION SUCCEEDED!")
        print("🎉 " + "=" * 56)
    else:
        # Phase 5: Drill down to find exact failure
        print()
        info("Main call failed. Drilling down to find exact failure...")
        print()
        failed_step = drill_down(conn)

        if failed_step:
            print()
            print("⛔ " + "=" * 56)
            print(f"⛔  FAILED AT STEP: {failed_step}")
            print("⛔  Share this output and I'll fix it.")
            print("⛔ " + "=" * 56)
        else:
            print()
            info("Interesting: sub-functions pass individually but main fails.")
            info("This could mean a parameter mismatch between main and subs.")

    # Final cleanup
    print()
    step("CLEANUP")
    try:
        cur = conn.cursor()
        ret = cur.var(int)
        cur.execute("""
            BEGIN
                :ret := PCRD_ST_BOARD_CONV_MAIN.MAIN_BOARD_CONV_PARAM(
                    SYSDATE, :bank, :wording, :currency, :country, '0');
            END;
        """, {
            "ret": ret,
            "bank": BANK_CODE,
            "wording": BANK_WORDING,
            "currency": CURRENCY_CODE,
            "country": COUNTRY_CODE,
        })
        conn.commit()
        ok("Cleanup done")
    except Exception as e:
        info(f"Cleanup: {e}")
        conn.rollback()

    conn.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
