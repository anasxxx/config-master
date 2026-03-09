-- ============================================================
-- DIAGNOSTIC v13 — FULL drill-down with correct signatures
-- Copy-paste into SQL Developer, press F5
-- ============================================================
SET SERVEROUTPUT ON SIZE 1000000;

DECLARE
    v_ret           PLS_INTEGER;
    v_bank          VARCHAR2(6)   := 'ZZT';
    v_wording       VARCHAR2(40)  := 'Banque Test';

    -- Will be resolved from DB
    v_curr_num      VARCHAR2(10);
    v_curr_alpha    VARCHAR2(10);
    v_country_num   VARCHAR2(10);
    v_country_alpha VARCHAR2(10);

    v_dummy         NUMBER;
BEGIN

    -- ============================================================
    -- STEP 0: Resolve currency & country codes
    -- ============================================================
    BEGIN
        SELECT TRIM(currency_code), TRIM(currency_code_alpha)
          INTO v_curr_num, v_curr_alpha
          FROM currency_table
         WHERE TRIM(currency_code_alpha) = 'MAD'
           AND ROWNUM = 1;
        DBMS_OUTPUT.PUT_LINE('[OK] Currency MAD => ' || v_curr_num || ' / ' || v_curr_alpha);
    EXCEPTION WHEN NO_DATA_FOUND THEN
        DBMS_OUTPUT.PUT_LINE('[FAIL] Currency MAD not found!');
        RETURN;
    END;

    BEGIN
        SELECT TRIM(country_code), TRIM(iso_country_alpha)
          INTO v_country_num, v_country_alpha
          FROM country
         WHERE TRIM(iso_country_alpha) IN ('MA','MAR')
           AND ROWNUM = 1;
        DBMS_OUTPUT.PUT_LINE('[OK] Country MA => ' || v_country_num || ' / ' || v_country_alpha);
    EXCEPTION WHEN NO_DATA_FOUND THEN
        DBMS_OUTPUT.PUT_LINE('[FAIL] Country MA not found!');
        RETURN;
    END;

    -- Check center 21
    BEGIN
        SELECT 1 INTO v_dummy FROM center WHERE center_code = '21';
        DBMS_OUTPUT.PUT_LINE('[FAIL] Center 21 EXISTS — will cause PK collision!');
        RETURN;
    EXCEPTION WHEN NO_DATA_FOUND THEN
        DBMS_OUTPUT.PUT_LINE('[OK] Center 21 is free');
    END;

    DBMS_OUTPUT.PUT_LINE('');

    -- ============================================================
    -- STEP 1: CLEANUP previous run (flag=0)
    -- ============================================================
    DBMS_OUTPUT.PUT_LINE('--- CLEANUP ---');
    BEGIN
        v_ret := PCRD_ST_BOARD_CONV_MAIN.MAIN_BOARD_CONV_PARAM(
            SYSDATE, v_bank, v_wording, v_curr_num, v_country_num, '0');
        COMMIT;
        DBMS_OUTPUT.PUT_LINE('[OK] Cleanup => ' || v_ret);
    EXCEPTION WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('[INFO] Cleanup error (OK): ' || SQLERRM);
        ROLLBACK;
    END;

    -- Clean staging tables
    BEGIN DELETE FROM st_pre_bin_range_plastic_prod WHERE bank_code = v_bank; EXCEPTION WHEN OTHERS THEN NULL; END;
    BEGIN DELETE FROM st_pre_branch       WHERE bank_code = v_bank; EXCEPTION WHEN OTHERS THEN NULL; END;
    BEGIN DELETE FROM st_pre_resources    WHERE bank_code = v_bank; EXCEPTION WHEN OTHERS THEN NULL; END;
    BEGIN DELETE FROM st_pre_mig_card_fees WHERE bank_code = v_bank; EXCEPTION WHEN OTHERS THEN NULL; END;
    BEGIN DELETE FROM st_pre_service_prod WHERE bank_code = v_bank; EXCEPTION WHEN OTHERS THEN NULL; END;
    BEGIN DELETE FROM st_pre_limit_stand  WHERE bank_code = v_bank; EXCEPTION WHEN OTHERS THEN NULL; END;
    COMMIT;
    DBMS_OUTPUT.PUT_LINE('[OK] Staging tables cleaned');
    DBMS_OUTPUT.PUT_LINE('');

    -- ============================================================
    -- STEP 2: INSERT staging data (product_type='01' not 'DEBIT')
    -- ============================================================
    DBMS_OUTPUT.PUT_LINE('--- INSERT STAGING DATA ---');

    BEGIN
        INSERT INTO st_pre_bin_range_plastic_prod
            (bank_code, description, bin, plastic_type, product_type,
             product_code, tranche_min, tranche_max, index_pvk,
             service_code, network, expiration, renew, prior_exp)
        VALUES (v_bank, 'Carte Test', '445555', 'PVC', '01', 'TST',
                '4455550000000000', '4455559999999999', '1', '101',
                'VISA', '36', 'A', '3');
        DBMS_OUTPUT.PUT_LINE('[OK] st_pre_bin_range_plastic_prod');
    EXCEPTION WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('[FAIL] st_pre_bin_range_plastic_prod: ' || SQLERRM);
    END;

    BEGIN
        INSERT INTO st_pre_branch (bank_code, branch_code, branch_wording,
            region_code, region_wording, city_code, city_wording)
        VALUES (v_bank, '001', 'Agence Test', '10', 'Grand Casa', '01', 'Casablanca');
        DBMS_OUTPUT.PUT_LINE('[OK] st_pre_branch');
    EXCEPTION WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('[FAIL] st_pre_branch: ' || SQLERRM);
    END;

    BEGIN
        INSERT INTO st_pre_resources (bank_code, resource_wording)
        VALUES (v_bank, 'VISA_BASE1');
        DBMS_OUTPUT.PUT_LINE('[OK] st_pre_resources');
    EXCEPTION WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('[FAIL] st_pre_resources: ' || SQLERRM);
    END;

    BEGIN
        INSERT INTO st_pre_mig_card_fees
            (bank_code, card_fees_code, description, card_fees_billing_evt,
             card_fees_grace_period, card_fees_billing_period,
             subscription_amount, fees_amount_first,
             damaged_replacement_fees, pin_replacement_fees)
        VALUES (v_bank, 'TST', 'Frais Test', 'M', 30, 'Y', 50, 10, 25, 5);
        DBMS_OUTPUT.PUT_LINE('[OK] st_pre_mig_card_fees');
    EXCEPTION WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('[FAIL] st_pre_mig_card_fees: ' || SQLERRM);
    END;

    BEGIN
        INSERT INTO st_pre_service_prod
            (bank_code, product_code, retrait, achat, advance, ecommerce,
             transfert, quasicash, solde, releve, pinchange, refund,
             moneysend, billpayment, original)
        VALUES (v_bank, 'TST', '1', '1', NULL, '1',
                NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);
        DBMS_OUTPUT.PUT_LINE('[OK] st_pre_service_prod');
    EXCEPTION WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('[FAIL] st_pre_service_prod: ' || SQLERRM);
    END;

    BEGIN
        INSERT INTO st_pre_limit_stand
            (bank_code, product_code, limits_id,
             daily_dom_amnt, daily_dom_nbr, daily_int_amnt, daily_int_nbr,
             daily_total_amnt, daily_total_nbr,
             min_amount_per_transaction, max_amount_per_transaction,
             weekly_dom_amnt, weekly_dom_nbr, weekly_int_amnt, weekly_int_nbr,
             weekly_total_amnt, weekly_total_nbr,
             monthly_dom_amnt, monthly_dom_nbr, monthly_int_amnt, monthly_int_nbr,
             monthly_total_amnt, monthly_total_nbr)
        VALUES (v_bank, 'LTST', '10',
                5000, '100', 2000, '050', 7000, '150',
                10, 50000,
                80000, '999', 40000, '500', 120000, '999',
                20000, '500', 10000, '200', 30000, '700');
        DBMS_OUTPUT.PUT_LINE('[OK] st_pre_limit_stand');
    EXCEPTION WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('[FAIL] st_pre_limit_stand: ' || SQLERRM);
    END;

    COMMIT;
    DBMS_OUTPUT.PUT_LINE('');

    -- ============================================================
    -- STEP 3: Call MAIN (like Spring Boot does)
    -- ============================================================
    DBMS_OUTPUT.PUT_LINE('--- CALL MAIN_BOARD_CONV_PARAM (flag=1) ---');
    BEGIN
        v_ret := PCRD_ST_BOARD_CONV_MAIN.MAIN_BOARD_CONV_PARAM(
            SYSDATE, v_bank, v_wording, v_curr_num, v_country_num, '1');
        IF v_ret = 0 THEN
            DBMS_OUTPUT.PUT_LINE('[OK] MAIN => 0 — SUCCESS!');
            COMMIT;
            -- Verify
            DECLARE v_name VARCHAR2(100);
            BEGIN
                SELECT bank_name INTO v_name FROM bank WHERE bank_code = v_bank;
                DBMS_OUTPUT.PUT_LINE('[OK] Bank ' || v_bank || ' verified: ' || v_name);
            EXCEPTION WHEN NO_DATA_FOUND THEN
                DBMS_OUTPUT.PUT_LINE('[FAIL] Bank not in BANK table despite return=0');
            END;
            DBMS_OUTPUT.PUT_LINE('');
            DBMS_OUTPUT.PUT_LINE('============================================');
            DBMS_OUTPUT.PUT_LINE('  SUCCESS! BANK INSERTION WORKS!');
            DBMS_OUTPUT.PUT_LINE('============================================');
            RETURN;  -- Done!
        ELSE
            DBMS_OUTPUT.PUT_LINE('[FAIL] MAIN => ' || v_ret);
            ROLLBACK;
        END IF;
    EXCEPTION WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('[FAIL] MAIN exception: ' || SQLERRM);
        ROLLBACK;
    END;

    -- ============================================================
    -- STEP 4: DRILL DOWN — re-setup and call each function
    -- ============================================================
    DBMS_OUTPUT.PUT_LINE('');
    DBMS_OUTPUT.PUT_LINE('--- DRILL DOWN: calling each sub-function ---');
    DBMS_OUTPUT.PUT_LINE('');

    -- Re-cleanup
    BEGIN
        v_ret := PCRD_ST_BOARD_CONV_MAIN.MAIN_BOARD_CONV_PARAM(
            SYSDATE, v_bank, v_wording, v_curr_num, v_country_num, '0');
        COMMIT;
    EXCEPTION WHEN OTHERS THEN ROLLBACK;
    END;

    -- Re-clean staging
    BEGIN DELETE FROM st_pre_bin_range_plastic_prod WHERE bank_code = v_bank; EXCEPTION WHEN OTHERS THEN NULL; END;
    BEGIN DELETE FROM st_pre_branch       WHERE bank_code = v_bank; EXCEPTION WHEN OTHERS THEN NULL; END;
    BEGIN DELETE FROM st_pre_resources    WHERE bank_code = v_bank; EXCEPTION WHEN OTHERS THEN NULL; END;
    BEGIN DELETE FROM st_pre_mig_card_fees WHERE bank_code = v_bank; EXCEPTION WHEN OTHERS THEN NULL; END;
    BEGIN DELETE FROM st_pre_service_prod WHERE bank_code = v_bank; EXCEPTION WHEN OTHERS THEN NULL; END;
    BEGIN DELETE FROM st_pre_limit_stand  WHERE bank_code = v_bank; EXCEPTION WHEN OTHERS THEN NULL; END;
    COMMIT;

    -- Re-insert staging
    BEGIN INSERT INTO st_pre_bin_range_plastic_prod (bank_code, description, bin, plastic_type, product_type, product_code, tranche_min, tranche_max, index_pvk, service_code, network, expiration, renew, prior_exp) VALUES (v_bank, 'Carte Test', '445555', 'PVC', '01', 'TST', '4455550000000000', '4455559999999999', '1', '101', 'VISA', '36', 'A', '3'); EXCEPTION WHEN OTHERS THEN NULL; END;
    BEGIN INSERT INTO st_pre_branch (bank_code, branch_code, branch_wording, region_code, region_wording, city_code, city_wording) VALUES (v_bank, '001', 'Agence Test', '10', 'Grand Casa', '01', 'Casablanca'); EXCEPTION WHEN OTHERS THEN NULL; END;
    BEGIN INSERT INTO st_pre_resources (bank_code, resource_wording) VALUES (v_bank, 'VISA_BASE1'); EXCEPTION WHEN OTHERS THEN NULL; END;
    BEGIN INSERT INTO st_pre_mig_card_fees (bank_code, card_fees_code, description, card_fees_billing_evt, card_fees_grace_period, card_fees_billing_period, subscription_amount, fees_amount_first, damaged_replacement_fees, pin_replacement_fees) VALUES (v_bank, 'TST', 'Frais Test', 'M', 30, 'Y', 50, 10, 25, 5); EXCEPTION WHEN OTHERS THEN NULL; END;
    BEGIN INSERT INTO st_pre_service_prod (bank_code, product_code, retrait, achat, advance, ecommerce, transfert, quasicash, solde, releve, pinchange, refund, moneysend, billpayment, original) VALUES (v_bank, 'TST', '1', '1', NULL, '1', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL); EXCEPTION WHEN OTHERS THEN NULL; END;
    BEGIN INSERT INTO st_pre_limit_stand (bank_code, product_code, limits_id, daily_dom_amnt, daily_dom_nbr, daily_int_amnt, daily_int_nbr, daily_total_amnt, daily_total_nbr, min_amount_per_transaction, max_amount_per_transaction, weekly_dom_amnt, weekly_dom_nbr, weekly_int_amnt, weekly_int_nbr, weekly_total_amnt, weekly_total_nbr, monthly_dom_amnt, monthly_dom_nbr, monthly_int_amnt, monthly_int_nbr, monthly_total_amnt, monthly_total_nbr) VALUES (v_bank, 'LTST', '10', 5000, '100', 2000, '050', 7000, '150', 10, 50000, 80000, '999', 40000, '500', 120000, '999', 20000, '500', 10000, '200', 30000, '700'); EXCEPTION WHEN OTHERS THEN NULL; END;
    COMMIT;

    -- 4.1 Sequence_ajustment (no params)
    BEGIN
        v_ret := PCRD_ST_BOARD_CONV_COM.Sequence_ajustment;
        IF v_ret = 0 THEN DBMS_OUTPUT.PUT_LINE('[OK] 4.1 Sequence_ajustment');
        ELSE DBMS_OUTPUT.PUT_LINE('[FAIL] 4.1 Sequence_ajustment => ' || v_ret); RETURN;
        END IF;
    EXCEPTION WHEN OTHERS THEN DBMS_OUTPUT.PUT_LINE('[FAIL] 4.1 ' || SQLERRM); RETURN;
    END;
    COMMIT;

    -- 4.2 AUT_CONV_GLB_TEMP_ROLLBACK(bank, wording, country)
    BEGIN
        v_ret := PCRD_ST_CONV_CLEAN.AUT_CONV_GLB_TEMP_ROLLBACK(v_bank, v_wording, v_country_num);
        IF v_ret = 0 THEN DBMS_OUTPUT.PUT_LINE('[OK] 4.2 AUT_CONV_GLB_TEMP_ROLLBACK');
        ELSE DBMS_OUTPUT.PUT_LINE('[FAIL] 4.2 AUT_CONV_GLB_TEMP_ROLLBACK => ' || v_ret); RETURN;
        END IF;
    EXCEPTION WHEN OTHERS THEN DBMS_OUTPUT.PUT_LINE('[FAIL] 4.2 ' || SQLERRM); RETURN;
    END;

    -- 4.3 AUT_CONV_PRODUCT_TEMP_ROLLBACK(bank, wording, country)
    BEGIN
        v_ret := PCRD_ST_CONV_CLEAN.AUT_CONV_PRODUCT_TEMP_ROLLBACK(v_bank, v_wording, v_country_num);
        IF v_ret = 0 THEN DBMS_OUTPUT.PUT_LINE('[OK] 4.3 AUT_CONV_PRODUCT_TEMP_ROLLBACK');
        ELSE DBMS_OUTPUT.PUT_LINE('[FAIL] 4.3 AUT_CONV_PRODUCT_TEMP_ROLLBACK => ' || v_ret); RETURN;
        END IF;
    EXCEPTION WHEN OTHERS THEN DBMS_OUTPUT.PUT_LINE('[FAIL] 4.3 ' || SQLERRM); RETURN;
    END;

    -- 4.4 LOAD_BANK_PARAMETERS(date, bank, wording, curr, curr_alpha, country, country_alpha)
    BEGIN
        v_ret := PCRD_ST_BOARD_CONV_COM.LOAD_BANK_PARAMETERS(
            SYSDATE, v_bank, v_wording, v_curr_num, v_curr_alpha, v_country_num, v_country_alpha);
        IF v_ret = 0 THEN DBMS_OUTPUT.PUT_LINE('[OK] 4.4 LOAD_BANK_PARAMETERS');
        ELSE DBMS_OUTPUT.PUT_LINE('[FAIL] 4.4 LOAD_BANK_PARAMETERS => ' || v_ret); RETURN;
        END IF;
    EXCEPTION WHEN OTHERS THEN DBMS_OUTPUT.PUT_LINE('[FAIL] 4.4 ' || SQLERRM); RETURN;
    END;

    -- 4.5 LOAD_BANK_CONV_COM_PARAM(date, bank, wording, curr, country)
    BEGIN
        v_ret := PCRD_ST_BOARD_CONV_COM.LOAD_BANK_CONV_COM_PARAM(
            SYSDATE, v_bank, v_wording, v_curr_num, v_country_num);
        IF v_ret = 0 THEN DBMS_OUTPUT.PUT_LINE('[OK] 4.5 LOAD_BANK_CONV_COM_PARAM');
        ELSE DBMS_OUTPUT.PUT_LINE('[FAIL] 4.5 LOAD_BANK_CONV_COM_PARAM => ' || v_ret); RETURN;
        END IF;
    EXCEPTION WHEN OTHERS THEN DBMS_OUTPUT.PUT_LINE('[FAIL] 4.5 ' || SQLERRM); RETURN;
    END;

    DBMS_OUTPUT.PUT_LINE('');
    DBMS_OUTPUT.PUT_LINE('--- ISS sub-functions (step 8) ---');

    -- 8a RELOAD_RESOURCES_PARAM(date, WORDING, bank)
    BEGIN
        v_ret := PCRD_ST_BOARD_CONV_ISS_PAR.RELOAD_RESOURCES_PARAM(SYSDATE, v_wording, v_bank);
        IF v_ret = 0 THEN DBMS_OUTPUT.PUT_LINE('[OK] 8a RELOAD_RESOURCES_PARAM');
        ELSE DBMS_OUTPUT.PUT_LINE('[FAIL] 8a RELOAD_RESOURCES_PARAM => ' || v_ret); RETURN;
        END IF;
    EXCEPTION WHEN OTHERS THEN DBMS_OUTPUT.PUT_LINE('[FAIL] 8a ' || SQLERRM); RETURN;
    END;

    -- 8b LOAD_branch_PARAMETERS(date, country, currency, bank)
    BEGIN
        v_ret := PCRD_ST_BOARD_CONV_ISS_PAR.LOAD_branch_PARAMETERS(SYSDATE, v_country_num, v_curr_num, v_bank);
        IF v_ret = 0 THEN DBMS_OUTPUT.PUT_LINE('[OK] 8b LOAD_branch_PARAMETERS');
        ELSE DBMS_OUTPUT.PUT_LINE('[FAIL] 8b LOAD_branch_PARAMETERS => ' || v_ret); RETURN;
        END IF;
    EXCEPTION WHEN OTHERS THEN DBMS_OUTPUT.PUT_LINE('[FAIL] 8b ' || SQLERRM); RETURN;
    END;

    -- 8c to 8A: all use (date, bank, currency)
    BEGIN v_ret := PCRD_ST_BOARD_CONV_ISS_PAR.LOAD_CARD_TYPE_PARAMETERS(SYSDATE, v_bank, v_curr_num);
        IF v_ret=0 THEN DBMS_OUTPUT.PUT_LINE('[OK] 8c LOAD_CARD_TYPE_PARAMETERS'); ELSE DBMS_OUTPUT.PUT_LINE('[FAIL] 8c LOAD_CARD_TYPE_PARAMETERS => '||v_ret); RETURN; END IF;
    EXCEPTION WHEN OTHERS THEN DBMS_OUTPUT.PUT_LINE('[FAIL] 8c '||SQLERRM); RETURN; END;

    BEGIN v_ret := PCRD_ST_BOARD_CONV_ISS_PAR.LOAD_BIN_RANGE_PLASTIC_PAR(SYSDATE, v_bank, v_curr_num);
        IF v_ret=0 THEN DBMS_OUTPUT.PUT_LINE('[OK] 8d LOAD_BIN_RANGE_PLASTIC_PAR'); ELSE DBMS_OUTPUT.PUT_LINE('[FAIL] 8d LOAD_BIN_RANGE_PLASTIC_PAR => '||v_ret); RETURN; END IF;
    EXCEPTION WHEN OTHERS THEN DBMS_OUTPUT.PUT_LINE('[FAIL] 8d '||SQLERRM); RETURN; END;

    BEGIN v_ret := PCRD_ST_BOARD_CONV_ISS_PAR.LOAD_CARD_FEES_PARAMETERS(SYSDATE, v_bank, v_curr_num);
        IF v_ret=0 THEN DBMS_OUTPUT.PUT_LINE('[OK] 8e LOAD_CARD_FEES_PARAMETERS'); ELSE DBMS_OUTPUT.PUT_LINE('[FAIL] 8e LOAD_CARD_FEES_PARAMETERS => '||v_ret); RETURN; END IF;
    EXCEPTION WHEN OTHERS THEN DBMS_OUTPUT.PUT_LINE('[FAIL] 8e '||SQLERRM); RETURN; END;

    BEGIN v_ret := PCRD_ST_BOARD_CONV_ISS_PAR.LOAD_SERVICE_PROD_PARAM(SYSDATE, v_bank, v_curr_num);
        IF v_ret=0 THEN DBMS_OUTPUT.PUT_LINE('[OK] 8f LOAD_SERVICE_PROD_PARAM'); ELSE DBMS_OUTPUT.PUT_LINE('[FAIL] 8f LOAD_SERVICE_PROD_PARAM => '||v_ret); RETURN; END IF;
    EXCEPTION WHEN OTHERS THEN DBMS_OUTPUT.PUT_LINE('[FAIL] 8f '||SQLERRM); RETURN; END;

    BEGIN v_ret := PCRD_ST_BOARD_CONV_ISS_PAR.LOAD_SERVICE_SETUP_PARAM(SYSDATE, v_bank, v_curr_num);
        IF v_ret=0 THEN DBMS_OUTPUT.PUT_LINE('[OK] 8g LOAD_SERVICE_SETUP_PARAM'); ELSE DBMS_OUTPUT.PUT_LINE('[FAIL] 8g LOAD_SERVICE_SETUP_PARAM => '||v_ret); RETURN; END IF;
    EXCEPTION WHEN OTHERS THEN DBMS_OUTPUT.PUT_LINE('[FAIL] 8g '||SQLERRM); RETURN; END;

    BEGIN v_ret := PCRD_ST_BOARD_CONV_ISS_PAR.LOAD_P7_limits_PARAMETERS(SYSDATE, v_bank, v_curr_num);
        IF v_ret=0 THEN DBMS_OUTPUT.PUT_LINE('[OK] 8h LOAD_P7_limits_PARAMETERS'); ELSE DBMS_OUTPUT.PUT_LINE('[FAIL] 8h LOAD_P7_limits_PARAMETERS => '||v_ret); RETURN; END IF;
    EXCEPTION WHEN OTHERS THEN DBMS_OUTPUT.PUT_LINE('[FAIL] 8h '||SQLERRM); RETURN; END;

    BEGIN v_ret := PCRD_ST_BOARD_CONV_ISS_PAR.LOAD_LIMIT_STAND_PARAM(SYSDATE, v_bank, v_curr_num);
        IF v_ret=0 THEN DBMS_OUTPUT.PUT_LINE('[OK] 8i LOAD_LIMIT_STAND_PARAM'); ELSE DBMS_OUTPUT.PUT_LINE('[FAIL] 8i LOAD_LIMIT_STAND_PARAM => '||v_ret); RETURN; END IF;
    EXCEPTION WHEN OTHERS THEN DBMS_OUTPUT.PUT_LINE('[FAIL] 8i '||SQLERRM); RETURN; END;

    BEGIN v_ret := PCRD_ST_BOARD_CONV_ISS_PAR.LOAD_SA_LIMITS_SETUP_PARAM(SYSDATE, v_bank, v_curr_num);
        IF v_ret=0 THEN DBMS_OUTPUT.PUT_LINE('[OK] 8j LOAD_SA_LIMITS_SETUP_PARAM'); ELSE DBMS_OUTPUT.PUT_LINE('[FAIL] 8j LOAD_SA_LIMITS_SETUP_PARAM => '||v_ret); RETURN; END IF;
    EXCEPTION WHEN OTHERS THEN DBMS_OUTPUT.PUT_LINE('[FAIL] 8j '||SQLERRM); RETURN; END;

    BEGIN v_ret := PCRD_ST_BOARD_CONV_ISS_PAR.LOAD_EMV_LIMIT_SETUP(SYSDATE, v_bank, v_curr_num);
        IF v_ret=0 THEN DBMS_OUTPUT.PUT_LINE('[OK] 8k LOAD_EMV_LIMIT_SETUP'); ELSE DBMS_OUTPUT.PUT_LINE('[FAIL] 8k LOAD_EMV_LIMIT_SETUP => '||v_ret); RETURN; END IF;
    EXCEPTION WHEN OTHERS THEN DBMS_OUTPUT.PUT_LINE('[FAIL] 8k '||SQLERRM); RETURN; END;

    BEGIN v_ret := PCRD_ST_BOARD_CONV_ISS_PAR.LOAD_EMV_KEYS_ASSIG_PARAM(SYSDATE, v_bank, v_curr_num);
        IF v_ret=0 THEN DBMS_OUTPUT.PUT_LINE('[OK] 8l LOAD_EMV_KEYS_ASSIG_PARAM'); ELSE DBMS_OUTPUT.PUT_LINE('[FAIL] 8l LOAD_EMV_KEYS_ASSIG_PARAM => '||v_ret); RETURN; END IF;
    EXCEPTION WHEN OTHERS THEN DBMS_OUTPUT.PUT_LINE('[FAIL] 8l '||SQLERRM); RETURN; END;

    BEGIN v_ret := PCRD_ST_BOARD_CONV_ISS_PAR.LOAD_EMV_ICC_APPL_DEF(SYSDATE, v_bank, v_curr_num);
        IF v_ret=0 THEN DBMS_OUTPUT.PUT_LINE('[OK] 8m LOAD_EMV_ICC_APPL_DEF'); ELSE DBMS_OUTPUT.PUT_LINE('[FAIL] 8m LOAD_EMV_ICC_APPL_DEF => '||v_ret); RETURN; END IF;
    EXCEPTION WHEN OTHERS THEN DBMS_OUTPUT.PUT_LINE('[FAIL] 8m '||SQLERRM); RETURN; END;

    BEGIN v_ret := PCRD_ST_BOARD_CONV_ISS_PAR.LOAD_CONTROL_VERIFICATION_PARAM(SYSDATE, v_bank, v_curr_num);
        IF v_ret=0 THEN DBMS_OUTPUT.PUT_LINE('[OK] 8n LOAD_CONTROL_VERIFICATION_PARAM'); ELSE DBMS_OUTPUT.PUT_LINE('[FAIL] 8n LOAD_CONTROL_VERIFICATION_PARAM => '||v_ret); RETURN; END IF;
    EXCEPTION WHEN OTHERS THEN DBMS_OUTPUT.PUT_LINE('[FAIL] 8n '||SQLERRM); RETURN; END;

    BEGIN v_ret := PCRD_ST_BOARD_CONV_ISS_PAR.LOAD_CARD_PRODUCT_PARAM(SYSDATE, v_bank, v_curr_num);
        IF v_ret=0 THEN DBMS_OUTPUT.PUT_LINE('[OK] 8o LOAD_CARD_PRODUCT_PARAM'); ELSE DBMS_OUTPUT.PUT_LINE('[FAIL] 8o LOAD_CARD_PRODUCT_PARAM => '||v_ret); RETURN; END IF;
    EXCEPTION WHEN OTHERS THEN DBMS_OUTPUT.PUT_LINE('[FAIL] 8o '||SQLERRM); RETURN; END;

    BEGIN v_ret := PCRD_ST_BOARD_CONV_ISS_PAR.LOAD_CARD_RANGE_PARAM(SYSDATE, v_bank, v_curr_num);
        IF v_ret=0 THEN DBMS_OUTPUT.PUT_LINE('[OK] 8p LOAD_CARD_RANGE_PARAM'); ELSE DBMS_OUTPUT.PUT_LINE('[FAIL] 8p LOAD_CARD_RANGE_PARAM => '||v_ret); RETURN; END IF;
    EXCEPTION WHEN OTHERS THEN DBMS_OUTPUT.PUT_LINE('[FAIL] 8p '||SQLERRM); RETURN; END;

    BEGIN v_ret := PCRD_ST_BOARD_CONV_ISS_PAR.LOAD_CARD_GEN_COUNTERS_PARAM(SYSDATE, v_bank, v_curr_num);
        IF v_ret=0 THEN DBMS_OUTPUT.PUT_LINE('[OK] 8q LOAD_CARD_GEN_COUNTERS_PARAM'); ELSE DBMS_OUTPUT.PUT_LINE('[FAIL] 8q LOAD_CARD_GEN_COUNTERS_PARAM => '||v_ret); RETURN; END IF;
    EXCEPTION WHEN OTHERS THEN DBMS_OUTPUT.PUT_LINE('[FAIL] 8q '||SQLERRM); RETURN; END;

    BEGIN v_ret := PCRD_ST_BOARD_CONV_ISS_PAR.LOAD_ROUTING_CRITERIA_PARAM(SYSDATE, v_bank, v_curr_num);
        IF v_ret=0 THEN DBMS_OUTPUT.PUT_LINE('[OK] 8r LOAD_ROUTING_CRITERIA_PARAM'); ELSE DBMS_OUTPUT.PUT_LINE('[FAIL] 8r LOAD_ROUTING_CRITERIA_PARAM => '||v_ret); RETURN; END IF;
    EXCEPTION WHEN OTHERS THEN DBMS_OUTPUT.PUT_LINE('[FAIL] 8r '||SQLERRM); RETURN; END;

    BEGIN v_ret := PCRD_ST_BOARD_CONV_ISS_PAR.LOAD_RENEWAL_CRITERIA_PARAM(SYSDATE, v_bank, v_curr_num);
        IF v_ret=0 THEN DBMS_OUTPUT.PUT_LINE('[OK] 8s LOAD_RENEWAL_CRITERIA_PARAM'); ELSE DBMS_OUTPUT.PUT_LINE('[FAIL] 8s LOAD_RENEWAL_CRITERIA_PARAM => '||v_ret); RETURN; END IF;
    EXCEPTION WHEN OTHERS THEN DBMS_OUTPUT.PUT_LINE('[FAIL] 8s '||SQLERRM); RETURN; END;

    BEGIN v_ret := PCRD_ST_BOARD_CONV_ISS_PAR.LOAD_PCRD_CARD_PROD_PARAM(SYSDATE, v_bank, v_curr_num);
        IF v_ret=0 THEN DBMS_OUTPUT.PUT_LINE('[OK] 8t LOAD_PCRD_CARD_PROD_PARAM'); ELSE DBMS_OUTPUT.PUT_LINE('[FAIL] 8t LOAD_PCRD_CARD_PROD_PARAM => '||v_ret); RETURN; END IF;
    EXCEPTION WHEN OTHERS THEN DBMS_OUTPUT.PUT_LINE('[FAIL] 8t '||SQLERRM); RETURN; END;

    BEGIN v_ret := PCRD_ST_BOARD_CONV_ISS_PAR.LOAD_Product_domain_PARAM(SYSDATE, v_bank, v_curr_num);
        IF v_ret=0 THEN DBMS_OUTPUT.PUT_LINE('[OK] 8u LOAD_Product_domain_PARAM'); ELSE DBMS_OUTPUT.PUT_LINE('[FAIL] 8u LOAD_Product_domain_PARAM => '||v_ret); RETURN; END IF;
    EXCEPTION WHEN OTHERS THEN DBMS_OUTPUT.PUT_LINE('[FAIL] 8u '||SQLERRM); RETURN; END;

    BEGIN v_ret := PCRD_ST_BOARD_CONV_ISS_PAR.LOAD_Entity_event_PARAM(SYSDATE, v_bank, v_curr_num);
        IF v_ret=0 THEN DBMS_OUTPUT.PUT_LINE('[OK] 8v LOAD_Entity_event_PARAM'); ELSE DBMS_OUTPUT.PUT_LINE('[FAIL] 8v LOAD_Entity_event_PARAM => '||v_ret); RETURN; END IF;
    EXCEPTION WHEN OTHERS THEN DBMS_OUTPUT.PUT_LINE('[FAIL] 8v '||SQLERRM); RETURN; END;

    BEGIN v_ret := PCRD_ST_BOARD_CONV_ISS_PAR.LOAD_icc_application_PARAM(SYSDATE, v_bank, v_curr_num);
        IF v_ret=0 THEN DBMS_OUTPUT.PUT_LINE('[OK] 8w LOAD_icc_application_PARAM'); ELSE DBMS_OUTPUT.PUT_LINE('[FAIL] 8w LOAD_icc_application_PARAM => '||v_ret); RETURN; END IF;
    EXCEPTION WHEN OTHERS THEN DBMS_OUTPUT.PUT_LINE('[FAIL] 8w '||SQLERRM); RETURN; END;

    BEGIN v_ret := PCRD_ST_BOARD_CONV_ISS_PAR.LOAD_markup_calcul(SYSDATE, v_bank, v_curr_num);
        IF v_ret=0 THEN DBMS_OUTPUT.PUT_LINE('[OK] 8x LOAD_markup_calcul'); ELSE DBMS_OUTPUT.PUT_LINE('[FAIL] 8x LOAD_markup_calcul => '||v_ret); RETURN; END IF;
    EXCEPTION WHEN OTHERS THEN DBMS_OUTPUT.PUT_LINE('[FAIL] 8x '||SQLERRM); RETURN; END;

    BEGIN v_ret := PCRD_ST_BOARD_CONV_ISS_PAR.LOAD_markup_index(SYSDATE, v_bank, v_curr_num);
        IF v_ret=0 THEN DBMS_OUTPUT.PUT_LINE('[OK] 8y LOAD_markup_index'); ELSE DBMS_OUTPUT.PUT_LINE('[FAIL] 8y LOAD_markup_index => '||v_ret); RETURN; END IF;
    EXCEPTION WHEN OTHERS THEN DBMS_OUTPUT.PUT_LINE('[FAIL] 8y '||SQLERRM); RETURN; END;

    BEGIN v_ret := PCRD_ST_BOARD_CONV_ISS_PAR.LOAD_markup_el_cur(SYSDATE, v_bank, v_curr_num);
        IF v_ret=0 THEN DBMS_OUTPUT.PUT_LINE('[OK] 8z LOAD_markup_el_cur'); ELSE DBMS_OUTPUT.PUT_LINE('[FAIL] 8z LOAD_markup_el_cur => '||v_ret); RETURN; END IF;
    EXCEPTION WHEN OTHERS THEN DBMS_OUTPUT.PUT_LINE('[FAIL] 8z '||SQLERRM); RETURN; END;

    BEGIN v_ret := PCRD_ST_BOARD_CONV_ISS_PAR.LOAD_Fleet_ctrl_PARAM(SYSDATE, v_bank, v_curr_num);
        IF v_ret=0 THEN DBMS_OUTPUT.PUT_LINE('[OK] 8A LOAD_Fleet_ctrl_PARAM'); ELSE DBMS_OUTPUT.PUT_LINE('[FAIL] 8A LOAD_Fleet_ctrl_PARAM => '||v_ret); RETURN; END IF;
    EXCEPTION WHEN OTHERS THEN DBMS_OUTPUT.PUT_LINE('[FAIL] 8A '||SQLERRM); RETURN; END;

    -- 8B MOVE_PARAMETERS_LOADED(date, bank) — only 2 params!
    BEGIN v_ret := PCRD_ST_BOARD_CONV_ISS_PAR.MOVE_PARAMETERS_LOADED(SYSDATE, v_bank);
        IF v_ret=0 THEN DBMS_OUTPUT.PUT_LINE('[OK] 8B MOVE_PARAMETERS_LOADED'); ELSE DBMS_OUTPUT.PUT_LINE('[FAIL] 8B MOVE_PARAMETERS_LOADED => '||v_ret); RETURN; END IF;
    EXCEPTION WHEN OTHERS THEN DBMS_OUTPUT.PUT_LINE('[FAIL] 8B '||SQLERRM); RETURN; END;

    -- 8C MAIN_AUT_POST(bank) — only 1 param!
    BEGIN v_ret := PCRD_ST_CONV_CATALOGUE.MAIN_AUT_POST(v_bank);
        IF v_ret=0 THEN DBMS_OUTPUT.PUT_LINE('[OK] 8C MAIN_AUT_POST'); ELSE DBMS_OUTPUT.PUT_LINE('[FAIL] 8C MAIN_AUT_POST => '||v_ret); RETURN; END IF;
    EXCEPTION WHEN OTHERS THEN DBMS_OUTPUT.PUT_LINE('[FAIL] 8C '||SQLERRM); RETURN; END;

    COMMIT;
    DBMS_OUTPUT.PUT_LINE('');
    DBMS_OUTPUT.PUT_LINE('============================================');
    DBMS_OUTPUT.PUT_LINE('  ALL SUB-FUNCTIONS PASSED!');
    DBMS_OUTPUT.PUT_LINE('============================================');

END;
/
