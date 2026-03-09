-- ============================================================
-- DIAGNOSTIC v12: Full 8-step test with FIXED product_type='01'
-- (was 'DEBIT' which is 5 chars, NETWORK_CARD_TYPE is CHAR(2))
--
-- Run in SQL Developer with F5.
-- ============================================================

SET SERVEROUTPUT ON SIZE 1000000;

DECLARE
    v_ret      PLS_INTEGER;
    v_bdate    DATE := SYSDATE;
    v_bank     VARCHAR2(6)  := 'ZZT';
    v_country  VARCHAR2(3)  := 'MA';
    v_currency VARCHAR2(3)  := 'MAD';
    v_wording  VARCHAR2(40) := 'Banque Test';
    v_flag     VARCHAR2(1)  := '1';     -- create
BEGIN
    ---------------------------------------------------------------
    -- CLEANUP: delete leftovers from previous runs
    ---------------------------------------------------------------
    DBMS_OUTPUT.PUT_LINE('=== CLEANUP ===');
    BEGIN
        v_ret := PCRD_ST_BOARD_CONV_PARAM.MAIN_BOARD_CONV_PARAM(
                     v_bdate, v_bank, v_country, v_currency, v_wording, '0');
        DBMS_OUTPUT.PUT_LINE('  cleanup returned ' || v_ret);
        COMMIT;
    EXCEPTION WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('  cleanup error (OK): ' || SQLERRM);
        ROLLBACK;
    END;

    ---------------------------------------------------------------
    -- Insert staging data with product_type='01' (was 'DEBIT')
    ---------------------------------------------------------------
    DELETE FROM st_pre_bin_range_plastic_prod WHERE bank_code = v_bank;
    INSERT INTO st_pre_bin_range_plastic_prod VALUES
        (v_bank, 'Carte Test', '445555', 'PVC', '01', 'TST',
         '4455550000000000', '4455559999999999', '1', '101', 'VISA', '36', 'A', '3');

    DELETE FROM st_pre_branch WHERE bank_code = v_bank;
    INSERT INTO st_pre_branch VALUES
        (v_bank, '001', 'Agence Test', '10', 'Grand Casablanca', '01', 'Casablanca');

    DELETE FROM st_pre_mig_card_fees WHERE bank_code = v_bank;
    INSERT INTO st_pre_mig_card_fees VALUES
        (v_bank, 'TST', 'Frais Test', 'M', 30, 'Y', 50, 10, 25, 5);

    DELETE FROM st_pre_service_prod WHERE bank_code = v_bank;
    INSERT INTO st_pre_service_prod VALUES
        (v_bank, 'TST', '1', '1', NULL, '1', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);

    DELETE FROM st_pre_limit_card_product WHERE bank_code = v_bank;
    INSERT INTO st_pre_limit_card_product VALUES
        (v_bank, 'LTST', '10', 5000, '100', 2000, '050', 7000, '150',
         20000, '500', 10000, '200', 30000, '700',
         80000, '999', 40000, '500', 120000, '999', 10, 50000);

    DELETE FROM st_pre_resource WHERE bank_code = v_bank;
    INSERT INTO st_pre_resource VALUES (v_bank, 'MCD_MDS');

    COMMIT;
    DBMS_OUTPUT.PUT_LINE('=== Staging data ready (product_type=01) ===');
    DBMS_OUTPUT.PUT_LINE('');

    ---------------------------------------------------------------
    -- Steps 1-5 (GET_CURRENCY, GET_COUNTRY, etc.)
    ---------------------------------------------------------------
    DBMS_OUTPUT.PUT_LINE('--- Step 1: GET_CURRENCY_TABLE ---');
    v_ret := PCRD_ST_BOARD_CONV_PARAM.GET_CURRENCY_TABLE(v_bdate, v_bank, v_country, v_currency);
    DBMS_OUTPUT.PUT_LINE('  => ' || v_ret);
    IF v_ret <> 0 THEN DBMS_OUTPUT.PUT_LINE('STOP at step 1'); ROLLBACK; RETURN; END IF;

    DBMS_OUTPUT.PUT_LINE('--- Step 2: GET_COUNTRY ---');
    v_ret := PCRD_ST_BOARD_CONV_PARAM.GET_COUNTRY(v_bdate, v_bank, v_country, v_currency);
    DBMS_OUTPUT.PUT_LINE('  => ' || v_ret);
    IF v_ret <> 0 THEN DBMS_OUTPUT.PUT_LINE('STOP at step 2'); ROLLBACK; RETURN; END IF;

    DBMS_OUTPUT.PUT_LINE('--- Step 3: Sequence_ajustment ---');
    v_ret := PCRD_ST_BOARD_CONV_PARAM.Sequence_ajustment(v_bdate, v_bank, v_country, v_currency);
    DBMS_OUTPUT.PUT_LINE('  => ' || v_ret);
    IF v_ret <> 0 THEN DBMS_OUTPUT.PUT_LINE('STOP at step 3'); ROLLBACK; RETURN; END IF;

    COMMIT;

    DBMS_OUTPUT.PUT_LINE('--- Step 4: AUT_CONV_GLB_TEMP_ROLLBACK ---');
    v_ret := PCRD_ST_CONV_CLEAN.AUT_CONV_GLB_TEMP_ROLLBACK(v_bdate, v_bank, v_country, v_currency);
    DBMS_OUTPUT.PUT_LINE('  => ' || v_ret);
    IF v_ret <> 0 THEN DBMS_OUTPUT.PUT_LINE('STOP at step 4'); ROLLBACK; RETURN; END IF;

    DBMS_OUTPUT.PUT_LINE('--- Step 5: AUT_CONV_PRODUCT_TEMP_ROLLBACK ---');
    v_ret := PCRD_ST_CONV_CLEAN.AUT_CONV_PRODUCT_TEMP_ROLLBACK(v_bdate, v_bank, v_country, v_currency);
    DBMS_OUTPUT.PUT_LINE('  => ' || v_ret);
    IF v_ret <> 0 THEN DBMS_OUTPUT.PUT_LINE('STOP at step 5'); ROLLBACK; RETURN; END IF;

    ---------------------------------------------------------------
    -- Step 6: LOAD_BANK_PARAMETERS
    ---------------------------------------------------------------
    DBMS_OUTPUT.PUT_LINE('--- Step 6: LOAD_BANK_PARAMETERS ---');
    v_ret := PCRD_ST_BOARD_CONV_COM.LOAD_BANK_PARAMETERS(v_bdate, v_bank, v_country, v_currency, v_wording);
    DBMS_OUTPUT.PUT_LINE('  => ' || v_ret);
    IF v_ret <> 0 THEN DBMS_OUTPUT.PUT_LINE('STOP at step 6'); ROLLBACK; RETURN; END IF;

    ---------------------------------------------------------------
    -- Step 7: LOAD_BANK_CONV_COM_PARAM
    ---------------------------------------------------------------
    DBMS_OUTPUT.PUT_LINE('--- Step 7: LOAD_BANK_CONV_COM_PARAM ---');
    v_ret := PCRD_ST_BOARD_CONV_COM.LOAD_BANK_CONV_COM_PARAM(v_bdate, v_bank, v_currency);
    DBMS_OUTPUT.PUT_LINE('  => ' || v_ret);
    IF v_ret <> 0 THEN DBMS_OUTPUT.PUT_LINE('STOP at step 7'); ROLLBACK; RETURN; END IF;

    ---------------------------------------------------------------
    -- Step 8: LOAD_BANK_CONV_ISS_PARAM  (29 sub-functions)
    ---------------------------------------------------------------
    DBMS_OUTPUT.PUT_LINE('--- Step 8: LOAD_BANK_CONV_ISS_PARAM ---');

    DBMS_OUTPUT.PUT_LINE('  8a. RELOAD_RESOURCES_PARAM');
    v_ret := PCRD_ST_BOARD_CONV_ISS_PAR.RELOAD_RESOURCES_PARAM(v_bdate, v_bank, v_currency);
    DBMS_OUTPUT.PUT_LINE('    => ' || v_ret);
    IF v_ret <> 0 THEN DBMS_OUTPUT.PUT_LINE('STOP at 8a'); ROLLBACK; RETURN; END IF;

    DBMS_OUTPUT.PUT_LINE('  8b. LOAD_branch_PARAMETERS');
    v_ret := PCRD_ST_BOARD_CONV_ISS_PAR.LOAD_branch_PARAMETERS(v_bdate, v_bank, v_currency);
    DBMS_OUTPUT.PUT_LINE('    => ' || v_ret);
    IF v_ret <> 0 THEN DBMS_OUTPUT.PUT_LINE('STOP at 8b'); ROLLBACK; RETURN; END IF;

    DBMS_OUTPUT.PUT_LINE('  8c. LOAD_CARD_TYPE_PARAMETERS');
    v_ret := PCRD_ST_BOARD_CONV_ISS_PAR.LOAD_CARD_TYPE_PARAMETERS(v_bdate, v_bank, v_currency);
    DBMS_OUTPUT.PUT_LINE('    => ' || v_ret);
    IF v_ret <> 0 THEN DBMS_OUTPUT.PUT_LINE('STOP at 8c'); ROLLBACK; RETURN; END IF;

    DBMS_OUTPUT.PUT_LINE('  8d. LOAD_BIN_RANGE_PLASTIC_PAR');
    v_ret := PCRD_ST_BOARD_CONV_ISS_PAR.LOAD_BIN_RANGE_PLASTIC_PAR(v_bdate, v_bank, v_currency);
    DBMS_OUTPUT.PUT_LINE('    => ' || v_ret);
    IF v_ret <> 0 THEN DBMS_OUTPUT.PUT_LINE('STOP at 8d'); ROLLBACK; RETURN; END IF;

    DBMS_OUTPUT.PUT_LINE('  8e. LOAD_CARD_FEES_PARAMETERS');
    v_ret := PCRD_ST_BOARD_CONV_ISS_PAR.LOAD_CARD_FEES_PARAMETERS(v_bdate, v_bank, v_currency);
    DBMS_OUTPUT.PUT_LINE('    => ' || v_ret);
    IF v_ret <> 0 THEN DBMS_OUTPUT.PUT_LINE('STOP at 8e'); ROLLBACK; RETURN; END IF;

    DBMS_OUTPUT.PUT_LINE('  8f. LOAD_SERVICE_PROD_PARAM');
    v_ret := PCRD_ST_BOARD_CONV_ISS_PAR.LOAD_SERVICE_PROD_PARAM(v_bdate, v_bank, v_currency);
    DBMS_OUTPUT.PUT_LINE('    => ' || v_ret);
    IF v_ret <> 0 THEN DBMS_OUTPUT.PUT_LINE('STOP at 8f'); ROLLBACK; RETURN; END IF;

    DBMS_OUTPUT.PUT_LINE('  8g. LOAD_SERVICE_SETUP_PARAM');
    v_ret := PCRD_ST_BOARD_CONV_ISS_PAR.LOAD_SERVICE_SETUP_PARAM(v_bdate, v_bank, v_currency);
    DBMS_OUTPUT.PUT_LINE('    => ' || v_ret);
    IF v_ret <> 0 THEN DBMS_OUTPUT.PUT_LINE('STOP at 8g'); ROLLBACK; RETURN; END IF;

    DBMS_OUTPUT.PUT_LINE('  8h. LOAD_P7_limits_PARAMETERS');
    v_ret := PCRD_ST_BOARD_CONV_ISS_PAR.LOAD_P7_limits_PARAMETERS(v_bdate, v_bank, v_currency);
    DBMS_OUTPUT.PUT_LINE('    => ' || v_ret);
    IF v_ret <> 0 THEN DBMS_OUTPUT.PUT_LINE('STOP at 8h'); ROLLBACK; RETURN; END IF;

    DBMS_OUTPUT.PUT_LINE('  8i. LOAD_LIMIT_STAND_PARAM');
    v_ret := PCRD_ST_BOARD_CONV_ISS_PAR.LOAD_LIMIT_STAND_PARAM(v_bdate, v_bank, v_currency);
    DBMS_OUTPUT.PUT_LINE('    => ' || v_ret);
    IF v_ret <> 0 THEN DBMS_OUTPUT.PUT_LINE('STOP at 8i'); ROLLBACK; RETURN; END IF;

    DBMS_OUTPUT.PUT_LINE('  8j. LOAD_SA_LIMITS_SETUP_PARAM');
    v_ret := PCRD_ST_BOARD_CONV_ISS_PAR.LOAD_SA_LIMITS_SETUP_PARAM(v_bdate, v_bank, v_currency);
    DBMS_OUTPUT.PUT_LINE('    => ' || v_ret);
    IF v_ret <> 0 THEN DBMS_OUTPUT.PUT_LINE('STOP at 8j'); ROLLBACK; RETURN; END IF;

    DBMS_OUTPUT.PUT_LINE('  8k. LOAD_EMV_LIMIT_SETUP');
    v_ret := PCRD_ST_BOARD_CONV_ISS_PAR.LOAD_EMV_LIMIT_SETUP(v_bdate, v_bank, v_currency);
    DBMS_OUTPUT.PUT_LINE('    => ' || v_ret);
    IF v_ret <> 0 THEN DBMS_OUTPUT.PUT_LINE('STOP at 8k'); ROLLBACK; RETURN; END IF;

    DBMS_OUTPUT.PUT_LINE('  8l. LOAD_CARD_PRODUCT_PARAM');
    v_ret := PCRD_ST_BOARD_CONV_ISS_PAR.LOAD_CARD_PRODUCT_PARAM(v_bdate, v_bank, v_currency);
    DBMS_OUTPUT.PUT_LINE('    => ' || v_ret);
    IF v_ret <> 0 THEN DBMS_OUTPUT.PUT_LINE('STOP at 8l'); ROLLBACK; RETURN; END IF;

    DBMS_OUTPUT.PUT_LINE('  8m. LOAD_CARD_RANGE_PARAM');
    v_ret := PCRD_ST_BOARD_CONV_ISS_PAR.LOAD_CARD_RANGE_PARAM(v_bdate, v_bank, v_currency);
    DBMS_OUTPUT.PUT_LINE('    => ' || v_ret);
    IF v_ret <> 0 THEN DBMS_OUTPUT.PUT_LINE('STOP at 8m'); ROLLBACK; RETURN; END IF;

    DBMS_OUTPUT.PUT_LINE('  8n. LOAD_CARD_GEN_COUNTER_PARAM');
    v_ret := PCRD_ST_BOARD_CONV_ISS_PAR.LOAD_CARD_GEN_COUNTER_PARAM(v_bdate, v_bank, v_currency);
    DBMS_OUTPUT.PUT_LINE('    => ' || v_ret);
    IF v_ret <> 0 THEN DBMS_OUTPUT.PUT_LINE('STOP at 8n'); ROLLBACK; RETURN; END IF;

    DBMS_OUTPUT.PUT_LINE('  8o. LOAD_ISS_POSTING_RULES');
    v_ret := PCRD_ST_BOARD_CONV_ISS_PAR.LOAD_ISS_POSTING_RULES(v_bdate, v_bank, v_currency);
    DBMS_OUTPUT.PUT_LINE('    => ' || v_ret);
    IF v_ret <> 0 THEN DBMS_OUTPUT.PUT_LINE('STOP at 8o'); ROLLBACK; RETURN; END IF;

    DBMS_OUTPUT.PUT_LINE('  8p. LOAD_CONV_CATALOGUE');
    v_ret := PCRD_ST_CONV_CATALOGUE.LOAD_CONV_CATALOGUE(v_bdate, v_bank, v_currency);
    DBMS_OUTPUT.PUT_LINE('    => ' || v_ret);
    IF v_ret <> 0 THEN DBMS_OUTPUT.PUT_LINE('STOP at 8p'); ROLLBACK; RETURN; END IF;

    DBMS_OUTPUT.PUT_LINE('  8q. LOAD_AUTH_CTRL_VALUE_PARAM');
    v_ret := PCRD_ST_BOARD_CONV_ISS_PAR.LOAD_AUTH_CTRL_VALUE_PARAM(v_bdate, v_bank, v_currency);
    DBMS_OUTPUT.PUT_LINE('    => ' || v_ret);
    IF v_ret <> 0 THEN DBMS_OUTPUT.PUT_LINE('STOP at 8q'); ROLLBACK; RETURN; END IF;

    DBMS_OUTPUT.PUT_LINE('  8r. LOAD_STOP_RENEWAL_CRITERIA');
    v_ret := PCRD_ST_BOARD_CONV_ISS_PAR.LOAD_STOP_RENEWAL_CRITERIA(v_bdate, v_bank, v_currency);
    DBMS_OUTPUT.PUT_LINE('    => ' || v_ret);
    IF v_ret <> 0 THEN DBMS_OUTPUT.PUT_LINE('STOP at 8r'); ROLLBACK; RETURN; END IF;

    DBMS_OUTPUT.PUT_LINE('  8s. LOAD_CARD_PROD_PARAM');
    v_ret := PCRD_ST_BOARD_CONV_ISS_PAR.LOAD_CARD_PROD_PARAM(v_bdate, v_bank, v_currency);
    DBMS_OUTPUT.PUT_LINE('    => ' || v_ret);
    IF v_ret <> 0 THEN DBMS_OUTPUT.PUT_LINE('STOP at 8s'); ROLLBACK; RETURN; END IF;

    DBMS_OUTPUT.PUT_LINE('  8t. LOAD_P7_SERVICES_SETUP');
    v_ret := PCRD_ST_BOARD_CONV_ISS_PAR.LOAD_P7_SERVICES_SETUP(v_bdate, v_bank, v_currency);
    DBMS_OUTPUT.PUT_LINE('    => ' || v_ret);
    IF v_ret <> 0 THEN DBMS_OUTPUT.PUT_LINE('STOP at 8t'); ROLLBACK; RETURN; END IF;

    DBMS_OUTPUT.PUT_LINE('  8u. LOAD_P7_SERVICES_CRITERIA');
    v_ret := PCRD_ST_BOARD_CONV_ISS_PAR.LOAD_P7_SERVICES_CRITERIA(v_bdate, v_bank, v_currency);
    DBMS_OUTPUT.PUT_LINE('    => ' || v_ret);
    IF v_ret <> 0 THEN DBMS_OUTPUT.PUT_LINE('STOP at 8u'); ROLLBACK; RETURN; END IF;

    DBMS_OUTPUT.PUT_LINE('  8v. LOAD_MER_EXCHANGE_MATRIX');
    v_ret := PCRD_ST_BOARD_CONV_ISS_PAR.LOAD_MER_EXCHANGE_MATRIX(v_bdate, v_bank, v_currency);
    DBMS_OUTPUT.PUT_LINE('    => ' || v_ret);
    IF v_ret <> 0 THEN DBMS_OUTPUT.PUT_LINE('STOP at 8v'); ROLLBACK; RETURN; END IF;

    DBMS_OUTPUT.PUT_LINE('  8w. LOAD_CHARGEBACK_REASON_CODE');
    v_ret := PCRD_ST_BOARD_CONV_ISS_PAR.LOAD_CHARGEBACK_REASON_CODE(v_bdate, v_bank, v_currency);
    DBMS_OUTPUT.PUT_LINE('    => ' || v_ret);
    IF v_ret <> 0 THEN DBMS_OUTPUT.PUT_LINE('STOP at 8w'); ROLLBACK; RETURN; END IF;

    DBMS_OUTPUT.PUT_LINE('  8x. MOVE_PARAMETERS_LOADED');
    v_ret := PCRD_ST_BOARD_CONV_ISS_PAR.MOVE_PARAMETERS_LOADED(v_bdate, v_bank, v_currency);
    DBMS_OUTPUT.PUT_LINE('    => ' || v_ret);
    IF v_ret <> 0 THEN DBMS_OUTPUT.PUT_LINE('STOP at 8x'); ROLLBACK; RETURN; END IF;

    DBMS_OUTPUT.PUT_LINE('  8y. MAIN_AUT_POST');
    v_ret := PCRD_ST_BOARD_CONV_ISS_PAR.MAIN_AUT_POST(v_bdate, v_bank, v_currency);
    DBMS_OUTPUT.PUT_LINE('    => ' || v_ret);
    IF v_ret <> 0 THEN DBMS_OUTPUT.PUT_LINE('STOP at 8y'); ROLLBACK; RETURN; END IF;

    ---------------------------------------------------------------
    DBMS_OUTPUT.PUT_LINE('');
    DBMS_OUTPUT.PUT_LINE('=== ALL STEPS PASSED! ===');
    COMMIT;

    ---------------------------------------------------------------
    -- FINAL CLEANUP
    ---------------------------------------------------------------
    DBMS_OUTPUT.PUT_LINE('--- Final cleanup (flag=0) ---');
    v_ret := PCRD_ST_BOARD_CONV_PARAM.MAIN_BOARD_CONV_PARAM(
                 v_bdate, v_bank, v_country, v_currency, v_wording, '0');
    DBMS_OUTPUT.PUT_LINE('  cleanup => ' || v_ret);
    COMMIT;

EXCEPTION WHEN OTHERS THEN
    DBMS_OUTPUT.PUT_LINE('UNEXPECTED ERROR: ' || SQLERRM);
    DBMS_OUTPUT.PUT_LINE('  at line ' || DBMS_UTILITY.FORMAT_ERROR_BACKTRACE);
    ROLLBACK;
END;
/
