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
CURRENCY_ALPHA = "MAD"
COUNTRY_ALPHA = "MA"


def connect():
    dsn = f"{DB_HOST}:{DB_PORT}/{DB_SERVICE}"
    print(f"Connecting to {dsn} as {DB_USER}...")
    conn = oracledb.connect(user=DB_USER, password=DB_PASS, dsn=dsn)
    print(f"  Connected! Oracle {conn.version}\n")
    return conn


def step(label):
    print(f"\n{'─'*60}\n  {label}\n{'─'*60}")


def ok(msg="OK"):
    print(f"  [OK] {msg}")


def fail(msg):
    print(f"  [FAIL] {msg}")


def info(msg):
    print(f"  [INFO] {msg}")


def call_plsql(cur, label, sql, params):
    """Call a PL/SQL function and return (success, return_value)."""
    ret = cur.var(int)
    params["ret"] = ret
    try:
        cur.execute(sql, params)
        val = ret.getvalue()
        if val == 0:
            ok(f"{label} => {val}")
            return True, val
        else:
            fail(f"{label} => {val}")
            return False, val
    except Exception as e:
        fail(f"{label} => {e}")
        return False, -99


def get_traces(cur, n=3):
    """Try to get recent PCARD_TRACES for error details."""
    try:
        cur.execute("""
            SELECT user_message FROM pcard_traces
            WHERE ROWNUM <= :n ORDER BY date_create DESC
        """, {"n": n})
        for row in cur.fetchall():
            if row[0]:
                info(f"TRACE: {row[0]}")
    except Exception:
        pass


# ══════════════════════════════════════════════════════════════
#  PHASE 1: PREREQUISITES
# ══════════════════════════════════════════════════════════════

def check_prerequisites(conn):
    step("PHASE 1: Prerequisites")
    cur = conn.cursor()

    # Resolve currency: alpha → numeric
    cur.execute("""
        SELECT currency_code, currency_code_alpha
        FROM currency_table WHERE TRIM(currency_code_alpha) = :1
    """, [CURRENCY_ALPHA])
    row = cur.fetchone()
    if row:
        currency_num = str(row[0]).strip()
        currency_alpha = str(row[1]).strip()
        ok(f"Currency {CURRENCY_ALPHA} => numeric={currency_num}, alpha={currency_alpha}")
    else:
        fail(f"Currency {CURRENCY_ALPHA} not found!")
        return None

    # Resolve country: alpha → numeric
    cur.execute("""
        SELECT country_code, iso_country_alpha
        FROM country WHERE TRIM(iso_country_alpha) = :1
    """, [COUNTRY_ALPHA])
    row = cur.fetchone()
    if not row:
        cur.execute("""
            SELECT country_code, iso_country_alpha
            FROM country WHERE TRIM(iso_country_alpha) = :1
        """, ["MAR"])
        row = cur.fetchone()
    if row:
        country_num = str(row[0]).strip()
        country_alpha = str(row[1]).strip()
        ok(f"Country {COUNTRY_ALPHA} => numeric={country_num}, alpha={country_alpha}")
    else:
        fail(f"Country {COUNTRY_ALPHA} not found!")
        return None

    # Check center 21
    cur.execute("SELECT center_code, center_name FROM center WHERE center_code = '21'")
    row = cur.fetchone()
    if row:
        fail(f"CENTER 21 EXISTS: {row[1]} — PK collision will occur!")
        return None
    else:
        ok("Center 21 is FREE")

    # Check packages are VALID
    for pkg in ["PCRD_ST_BOARD_CONV_MAIN", "PCRD_ST_BOARD_CONV_COM",
                "PCRD_ST_BOARD_CONV_ISS_PAR", "PCRD_ST_CONV_CLEAN", "PCRD_ST_CONV_CATALOGUE"]:
        cur.execute("""
            SELECT status FROM user_objects
            WHERE object_name = :1 AND object_type = 'PACKAGE BODY'
        """, [pkg])
        row = cur.fetchone()
        if row and row[0] == "VALID":
            ok(f"Package {pkg}: VALID")
        elif row:
            fail(f"Package {pkg}: {row[0]} — INVALID!")
            return None
        else:
            fail(f"Package {pkg}: NOT FOUND!")
            return None

    cur.close()
    return {
        "currency_num": currency_num,
        "currency_alpha": currency_alpha,
        "country_num": country_num,
        "country_alpha": country_alpha,
    }


# ══════════════════════════════════════════════════════════════
#  PHASE 2: CLEANUP
# ══════════════════════════════════════════════════════════════

def cleanup(conn, codes):
    step("PHASE 2: Cleanup")
    cur = conn.cursor()

    # Call main with flag='0' (delete)
    try:
        ret = cur.var(int)
        cur.execute("""
            BEGIN
                :ret := PCRD_ST_BOARD_CONV_MAIN.MAIN_BOARD_CONV_PARAM(
                    SYSDATE, :bank, :wording, :curr, :country, '0');
            END;
        """, {"ret": ret, "bank": BANK_CODE, "wording": BANK_WORDING,
              "curr": codes["currency_num"], "country": codes["country_num"]})
        conn.commit()
        ok(f"Main cleanup => {ret.getvalue()}")
    except Exception as e:
        info(f"Cleanup exception (OK): {e}")
        conn.rollback()

    # Clean staging tables
    for tbl in ["st_pre_bin_range_plastic_prod", "st_pre_branch",
                "st_pre_resources", "st_pre_mig_card_fees",
                "st_pre_service_prod", "st_pre_limit_stand"]:
        try:
            cur.execute(f"DELETE FROM {tbl} WHERE bank_code = :1", [BANK_CODE])
        except Exception:
            pass

    # Clean mig staging tables
    for tbl in ["st_mig_card_type", "st_mig_plastic_list", "st_mig_card_fees",
                "st_mig_card_product", "st_mig_card_range", "st_mig_services_name",
                "st_mig_services_setup", "st_mig_sa_limits_setup",
                "st_mig_spec_trans_limits", "st_mig_p7_limits",
                "st_mig_emv_limit_setup", "st_mig_card_gen_counters",
                "st_mig_ctrl_verification_flags"]:
        try:
            cur.execute(f"DELETE FROM {tbl} WHERE bank_code = :1", [BANK_CODE])
        except Exception:
            pass

    conn.commit()
    ok("Staging tables cleaned")
    cur.close()


# ══════════════════════════════════════════════════════════════
#  PHASE 3: INSERT STAGING DATA
# ══════════════════════════════════════════════════════════════

def insert_staging(conn):
    step("PHASE 3: Insert staging data")
    cur = conn.cursor()
    errors = 0

    # 1. Card product — product_type='01' (CHAR(2) for NETWORK_CARD_TYPE)
    try:
        cur.execute("""
            INSERT INTO st_pre_bin_range_plastic_prod
            (bank_code, description, bin, plastic_type, product_type,
             product_code, tranche_min, tranche_max, index_pvk,
             service_code, network, expiration, renew, prior_exp)
            VALUES (:1,:2,:3,:4,:5,:6,:7,:8,:9,:10,:11,:12,:13,:14)
        """, [BANK_CODE, "Carte Test", "445555", "PVC", "01", "TST",
              "4455550000000000", "4455559999999999", "1", "101",
              "VISA", "36", "A", "3"])
        ok("st_pre_bin_range_plastic_prod")
    except Exception as e:
        fail(f"st_pre_bin_range_plastic_prod: {e}")
        errors += 1

    # 2. Branch
    try:
        cur.execute("""
            INSERT INTO st_pre_branch
            (bank_code, branch_code, branch_wording, region_code,
             region_wording, city_code, city_wording)
            VALUES (:1,:2,:3,:4,:5,:6,:7)
        """, [BANK_CODE, "001", "Agence Test", "10",
              "Grand Casablanca", "01", "Casablanca"])
        ok("st_pre_branch")
    except Exception as e:
        fail(f"st_pre_branch: {e}")
        errors += 1

    # 3. Resource
    try:
        cur.execute("""
            INSERT INTO st_pre_resources (bank_code, resource_wording)
            VALUES (:1, :2)
        """, [BANK_CODE, "VISA_BASE1"])
        ok("st_pre_resources")
    except Exception as e:
        fail(f"st_pre_resources: {e}")
        errors += 1

    # 4. Card fees
    try:
        cur.execute("""
            INSERT INTO st_pre_mig_card_fees
            (bank_code, card_fees_code, description, card_fees_billing_evt,
             card_fees_grace_period, card_fees_billing_period,
             subscription_amount, fees_amount_first,
             damaged_replacement_fees, pin_replacement_fees)
            VALUES (:1,:2,:3,:4,:5,:6,:7,:8,:9,:10)
        """, [BANK_CODE, "TST", "Frais Test", "M", 30, "Y", 50, 10, 25, 5])
        ok("st_pre_mig_card_fees")
    except Exception as e:
        fail(f"st_pre_mig_card_fees: {e}")
        errors += 1

    # 5. Service prod
    try:
        cur.execute("""
            INSERT INTO st_pre_service_prod
            (bank_code, product_code, retrait, achat, advance, ecommerce,
             transfert, quasicash, solde, releve, pinchange, refund,
             moneysend, billpayment, original)
            VALUES (:1,:2,:3,:4,:5,:6,:7,:8,:9,:10,:11,:12,:13,:14,:15)
        """, [BANK_CODE, "TST", "1", "1", None, "1",
              None, None, None, None, None, None, None, None, None])
        ok("st_pre_service_prod")
    except Exception as e:
        fail(f"st_pre_service_prod: {e}")
        errors += 1

    # 6. Limits
    try:
        cur.execute("""
            INSERT INTO st_pre_limit_stand
            (bank_code, product_code, limits_id,
             daily_dom_amnt, daily_dom_nbr, daily_int_amnt, daily_int_nbr,
             daily_total_amnt, daily_total_nbr,
             min_amount_per_transaction, max_amount_per_transaction,
             weekly_dom_amnt, weekly_dom_nbr, weekly_int_amnt, weekly_int_nbr,
             weekly_total_amnt, weekly_total_nbr,
             monthly_dom_amnt, monthly_dom_nbr, monthly_int_amnt, monthly_int_nbr,
             monthly_total_amnt, monthly_total_nbr)
            VALUES (:1,:2,:3,:4,:5,:6,:7,:8,:9,:10,:11,:12,:13,:14,:15,:16,:17,:18,:19,:20,:21,:22,:23)
        """, [BANK_CODE, "LTST", "10",
              "5000", "100", "2000", "050", "7000", "150",
              "10", "50000",
              "80000", "999", "40000", "500", "120000", "999",
              "20000", "500", "10000", "200", "30000", "700"])
        ok("st_pre_limit_stand")
    except Exception as e:
        fail(f"st_pre_limit_stand: {e}")
        errors += 1

    conn.commit()
    cur.close()
    return errors == 0


# ══════════════════════════════════════════════════════════════
#  PHASE 4: CALL MAIN PL/SQL
# ══════════════════════════════════════════════════════════════

def call_main(conn, codes):
    step("PHASE 4: Call MAIN_BOARD_CONV_PARAM (flag='1')")
    cur = conn.cursor()
    success, val = call_plsql(cur, "MAIN", """
        BEGIN
            :ret := PCRD_ST_BOARD_CONV_MAIN.MAIN_BOARD_CONV_PARAM(
                SYSDATE, :bank, :wording, :curr, :country, '1');
        END;
    """, {"bank": BANK_CODE, "wording": BANK_WORDING,
          "curr": codes["currency_num"], "country": codes["country_num"]})

    if success:
        conn.commit()
    else:
        conn.rollback()
    cur.close()
    return success


# ══════════════════════════════════════════════════════════════
#  PHASE 5: DRILL DOWN — each sub-function with CORRECT params
# ══════════════════════════════════════════════════════════════

def drill_down(conn, codes):
    step("PHASE 5: Drill-down (exact PL/SQL parameter signatures)")
    cur = conn.cursor()

    # Re-setup: cleanup and re-insert staging data
    cleanup(conn, codes)
    insert_staging(conn)

    cn = codes["currency_num"]
    ca = codes["currency_alpha"]
    ctn = codes["country_num"]
    cta = codes["country_alpha"]

    # ── Steps 1-3: Sequence adjustment ──
    success, _ = call_plsql(cur, "5.1 Sequence_ajustment",
        "BEGIN :ret := PCRD_ST_BOARD_CONV_COM.Sequence_ajustment; END;", {})
    if not success:
        return "5.1"
    conn.commit()

    # ── Steps 4-5: Temp rollbacks (3 params: bank, wording, country) ──
    for label, fn in [("5.2", "AUT_CONV_GLB_TEMP_ROLLBACK"),
                      ("5.3", "AUT_CONV_PRODUCT_TEMP_ROLLBACK")]:
        success, _ = call_plsql(cur, f"{label} {fn}", f"""
            BEGIN :ret := PCRD_ST_CONV_CLEAN.{fn}(:b, :w, :c); END;
        """, {"b": BANK_CODE, "w": BANK_WORDING, "c": ctn})
        if not success:
            return label

    # ── Step 6: LOAD_BANK_PARAMETERS (7 params) ──
    success, _ = call_plsql(cur, "5.4 LOAD_BANK_PARAMETERS", """
        BEGIN :ret := PCRD_ST_BOARD_CONV_COM.LOAD_BANK_PARAMETERS(
            SYSDATE, :bank, :wording, :cn, :ca, :ctn, :cta); END;
    """, {"bank": BANK_CODE, "wording": BANK_WORDING,
          "cn": cn, "ca": ca, "ctn": ctn, "cta": cta})
    if not success:
        get_traces(cur)
        return "5.4"

    # ── Step 7: LOAD_BANK_CONV_COM_PARAM (5 params) ──
    success, _ = call_plsql(cur, "5.5 LOAD_BANK_CONV_COM_PARAM", """
        BEGIN :ret := PCRD_ST_BOARD_CONV_COM.LOAD_BANK_CONV_COM_PARAM(
            SYSDATE, :bank, :wording, :cn, :ctn); END;
    """, {"bank": BANK_CODE, "wording": BANK_WORDING, "cn": cn, "ctn": ctn})
    if not success:
        get_traces(cur)
        return "5.5"

    # ══════════════════════════════════════════════════════════
    #  Step 8: ISS sub-functions — EXACT signatures from orchestrator
    # ══════════════════════════════════════════════════════════

    # 8a: RELOAD_RESOURCES_PARAM(date, WORDING, bank_code) — note param order!
    success, _ = call_plsql(cur, "8a RELOAD_RESOURCES_PARAM", """
        BEGIN :ret := PCRD_ST_BOARD_CONV_ISS_PAR.RELOAD_RESOURCES_PARAM(
            SYSDATE, :wording, :bank); END;
    """, {"wording": BANK_WORDING, "bank": BANK_CODE})
    if not success:
        get_traces(cur)
        return "8a"

    # 8b: LOAD_branch_PARAMETERS(date, country, currency, bank) — 4 params!
    success, _ = call_plsql(cur, "8b LOAD_branch_PARAMETERS", """
        BEGIN :ret := PCRD_ST_BOARD_CONV_ISS_PAR.LOAD_branch_PARAMETERS(
            SYSDATE, :country, :curr, :bank); END;
    """, {"country": ctn, "curr": cn, "bank": BANK_CODE})
    if not success:
        get_traces(cur)
        return "8b"

    # 8c-8z: Standard signature (date, bank, currency)
    iss_standard = [
        ("8c",  "LOAD_CARD_TYPE_PARAMETERS"),
        ("8d",  "LOAD_BIN_RANGE_PLASTIC_PAR"),
        ("8e",  "LOAD_CARD_FEES_PARAMETERS"),
        ("8f",  "LOAD_SERVICE_PROD_PARAM"),
        ("8g",  "LOAD_SERVICE_SETUP_PARAM"),
        ("8h",  "LOAD_P7_limits_PARAMETERS"),
        ("8i",  "LOAD_LIMIT_STAND_PARAM"),
        ("8j",  "LOAD_SA_LIMITS_SETUP_PARAM"),
        ("8k",  "LOAD_EMV_LIMIT_SETUP"),
        ("8l",  "LOAD_EMV_KEYS_ASSIG_PARAM"),
        ("8m",  "LOAD_EMV_ICC_APPL_DEF"),
        ("8n",  "LOAD_CONTROL_VERIFICATION_PARAM"),
        ("8o",  "LOAD_CARD_PRODUCT_PARAM"),
        ("8p",  "LOAD_CARD_RANGE_PARAM"),
        ("8q",  "LOAD_CARD_GEN_COUNTERS_PARAM"),
        ("8r",  "LOAD_ROUTING_CRITERIA_PARAM"),
        ("8s",  "LOAD_RENEWAL_CRITERIA_PARAM"),
        ("8t",  "LOAD_PCRD_CARD_PROD_PARAM"),
        ("8u",  "LOAD_Product_domain_PARAM"),
        ("8v",  "LOAD_Entity_event_PARAM"),
        ("8w",  "LOAD_icc_application_PARAM"),
        ("8x",  "LOAD_markup_calcul"),
        ("8y",  "LOAD_markup_index"),
        ("8z",  "LOAD_markup_el_cur"),
        ("8A",  "LOAD_Fleet_ctrl_PARAM"),
    ]

    for label, fn in iss_standard:
        success, _ = call_plsql(cur, f"{label} {fn}", f"""
            BEGIN :ret := PCRD_ST_BOARD_CONV_ISS_PAR.{fn}(
                SYSDATE, :bank, :curr); END;
        """, {"bank": BANK_CODE, "curr": cn})
        if not success:
            get_traces(cur)
            return label

    # 8B: MOVE_PARAMETERS_LOADED(date, bank) — only 2 params!
    success, _ = call_plsql(cur, "8B MOVE_PARAMETERS_LOADED", """
        BEGIN :ret := PCRD_ST_BOARD_CONV_ISS_PAR.MOVE_PARAMETERS_LOADED(
            SYSDATE, :bank); END;
    """, {"bank": BANK_CODE})
    if not success:
        get_traces(cur)
        return "8B"

    # 8C: MAIN_AUT_POST(bank) — only 1 param!
    success, _ = call_plsql(cur, "8C MAIN_AUT_POST (catalogue)", """
        BEGIN :ret := PCRD_ST_CONV_CATALOGUE.MAIN_AUT_POST(:bank); END;
    """, {"bank": BANK_CODE})
    if not success:
        get_traces(cur)
        return "8C"

    conn.commit()
    ok("ALL SUB-FUNCTIONS PASSED!")
    cur.close()
    return None


# ══════════════════════════════════════════════════════════════
#  PHASE 6: VERIFY
# ══════════════════════════════════════════════════════════════

def verify(conn):
    step("PHASE 6: Verify")
    cur = conn.cursor()
    cur.execute("SELECT bank_code, bank_name FROM bank WHERE bank_code = :1", [BANK_CODE])
    row = cur.fetchone()
    if row:
        ok(f"Bank {row[0]} exists! name={row[1]}")
        return True
    else:
        fail(f"Bank {BANK_CODE} NOT found in BANK table")
        return False


# ══════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print("  ConfigMaster — Oracle Database Diagnostic v2")
    print("=" * 60)

    conn = connect()

    # Phase 1
    codes = check_prerequisites(conn)
    if not codes:
        print("\n*** Prerequisites failed. Fix above issues first. ***")
        conn.close()
        return

    # Phase 2
    cleanup(conn, codes)

    # Phase 3
    if not insert_staging(conn):
        print("\n*** Could not insert staging data. ***")
        conn.close()
        return

    # Phase 4: Try main orchestrator
    if call_main(conn, codes):
        verify(conn)
        print("\n" + "=" * 60)
        print("  SUCCESS! Bank insertion works!")
        print("=" * 60)
    else:
        # Phase 5: Drill down
        print("\n  Main failed. Drilling down to find exact failure...\n")
        failed = drill_down(conn, codes)
        if failed:
            print("\n" + "=" * 60)
            print(f"  FAILED AT STEP: {failed}")
            print("  Share this output to fix the issue.")
            print("=" * 60)

    # Final cleanup
    step("CLEANUP")
    try:
        cur = conn.cursor()
        ret = cur.var(int)
        cur.execute("""
            BEGIN :ret := PCRD_ST_BOARD_CONV_MAIN.MAIN_BOARD_CONV_PARAM(
                SYSDATE, :b, :w, :c, :ct, '0'); END;
        """, {"ret": ret, "b": BANK_CODE, "w": BANK_WORDING,
              "c": codes["currency_num"], "ct": codes["country_num"]})
        conn.commit()
        ok("Done")
    except Exception:
        conn.rollback()

    conn.close()


if __name__ == "__main__":
    main()
