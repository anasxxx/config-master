-- ============================================================
-- DIAGNOSTIC v14 — Full cleanup + inline error capture for 8i
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
    v_cnt           NUMBER;
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
        DBMS_OUTPUT.PUT_LINE('[OK] Cleanup (flag=0) => ' || v_ret);
    EXCEPTION WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('[INFO] Cleanup error (OK): ' || SQLERRM);
        ROLLBACK;
    END;

    -- *** CRITICAL FIX: Clean ALL rows from staging tables, not just bank ZZT ***
    -- The PL/SQL cursors do NOT filter by bank_code, so leftover rows cause errors
    BEGIN DELETE FROM st_pre_bin_range_plastic_prod; EXCEPTION WHEN OTHERS THEN NULL; END;
    BEGIN DELETE FROM st_pre_branch;                 EXCEPTION WHEN OTHERS THEN NULL; END;
    BEGIN DELETE FROM st_pre_resources;              EXCEPTION WHEN OTHERS THEN NULL; END;
    BEGIN DELETE FROM st_pre_mig_card_fees;          EXCEPTION WHEN OTHERS THEN NULL; END;
    BEGIN DELETE FROM st_pre_service_prod;           EXCEPTION WHEN OTHERS THEN NULL; END;
    BEGIN DELETE FROM st_pre_limit_stand;            EXCEPTION WHEN OTHERS THEN NULL; END;
    COMMIT;
    DBMS_OUTPUT.PUT_LINE('[OK] ALL staging tables fully cleaned');

    -- Verify tables are empty
    SELECT COUNT(*) INTO v_cnt FROM st_pre_limit_stand;
    DBMS_OUTPUT.PUT_LINE('[INFO] st_pre_limit_stand rows after clean: ' || v_cnt);
    SELECT COUNT(*) INTO v_cnt FROM st_pre_bin_range_plastic_prod;
    DBMS_OUTPUT.PUT_LINE('[INFO] st_pre_bin_range_plastic_prod rows after clean: ' || v_cnt);

    DBMS_OUTPUT.PUT_LINE('');

    -- ============================================================
    -- STEP 2: INSERT staging data
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
                '5000', '100', '2000', '050', '7000', '150',
                '10', '50000',
                '80000', '999', '40000', '500', '120000', '999',
                '20000', '500', '10000', '200', '30000', '700');
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

    -- *** FULL clean of ALL st_pre_* tables ***
    BEGIN DELETE FROM st_pre_bin_range_plastic_prod; EXCEPTION WHEN OTHERS THEN NULL; END;
    BEGIN DELETE FROM st_pre_branch;                 EXCEPTION WHEN OTHERS THEN NULL; END;
    BEGIN DELETE FROM st_pre_resources;              EXCEPTION WHEN OTHERS THEN NULL; END;
    BEGIN DELETE FROM st_pre_mig_card_fees;          EXCEPTION WHEN OTHERS THEN NULL; END;
    BEGIN DELETE FROM st_pre_service_prod;           EXCEPTION WHEN OTHERS THEN NULL; END;
    BEGIN DELETE FROM st_pre_limit_stand;            EXCEPTION WHEN OTHERS THEN NULL; END;
    COMMIT;

    -- Re-insert staging
    BEGIN INSERT INTO st_pre_bin_range_plastic_prod (bank_code, description, bin, plastic_type, product_type, product_code, tranche_min, tranche_max, index_pvk, service_code, network, expiration, renew, prior_exp) VALUES (v_bank, 'Carte Test', '445555', 'PVC', '01', 'TST', '4455550000000000', '4455559999999999', '1', '101', 'VISA', '36', 'A', '3'); EXCEPTION WHEN OTHERS THEN NULL; END;
    BEGIN INSERT INTO st_pre_branch (bank_code, branch_code, branch_wording, region_code, region_wording, city_code, city_wording) VALUES (v_bank, '001', 'Agence Test', '10', 'Grand Casa', '01', 'Casablanca'); EXCEPTION WHEN OTHERS THEN NULL; END;
    BEGIN INSERT INTO st_pre_resources (bank_code, resource_wording) VALUES (v_bank, 'VISA_BASE1'); EXCEPTION WHEN OTHERS THEN NULL; END;
    BEGIN INSERT INTO st_pre_mig_card_fees (bank_code, card_fees_code, description, card_fees_billing_evt, card_fees_grace_period, card_fees_billing_period, subscription_amount, fees_amount_first, damaged_replacement_fees, pin_replacement_fees) VALUES (v_bank, 'TST', 'Frais Test', 'M', 30, 'Y', 50, 10, 25, 5); EXCEPTION WHEN OTHERS THEN NULL; END;
    BEGIN INSERT INTO st_pre_service_prod (bank_code, product_code, retrait, achat, advance, ecommerce, transfert, quasicash, solde, releve, pinchange, refund, moneysend, billpayment, original) VALUES (v_bank, 'TST', '1', '1', NULL, '1', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL); EXCEPTION WHEN OTHERS THEN NULL; END;
    BEGIN INSERT INTO st_pre_limit_stand (bank_code, product_code, limits_id, daily_dom_amnt, daily_dom_nbr, daily_int_amnt, daily_int_nbr, daily_total_amnt, daily_total_nbr, min_amount_per_transaction, max_amount_per_transaction, weekly_dom_amnt, weekly_dom_nbr, weekly_int_amnt, weekly_int_nbr, weekly_total_amnt, weekly_total_nbr, monthly_dom_amnt, monthly_dom_nbr, monthly_int_amnt, monthly_int_nbr, monthly_total_amnt, monthly_total_nbr) VALUES (v_bank, 'LTST', '10', '5000', '100', '2000', '050', '7000', '150', '10', '50000', '80000', '999', '40000', '500', '120000', '999', '20000', '500', '10000', '200', '30000', '700'); EXCEPTION WHEN OTHERS THEN NULL; END;
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

    -- 8c-8h: all use (date, bank, currency)
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

    -- ============================================================
    -- 8i LOAD_LIMIT_STAND_PARAM — INLINE DEBUG VERSION
    -- Instead of calling the function as black box, replicate its
    -- logic to capture the EXACT error point
    -- ============================================================
    DBMS_OUTPUT.PUT_LINE('');
    DBMS_OUTPUT.PUT_LINE('--- 8i LOAD_LIMIT_STAND_PARAM (inline debug) ---');

    -- First try the normal call
    BEGIN
        v_ret := PCRD_ST_BOARD_CONV_ISS_PAR.LOAD_LIMIT_STAND_PARAM(SYSDATE, v_bank, v_curr_num);
        IF v_ret = 0 THEN
            DBMS_OUTPUT.PUT_LINE('[OK] 8i LOAD_LIMIT_STAND_PARAM');
            GOTO after_8i_debug;
        ELSE
            DBMS_OUTPUT.PUT_LINE('[FAIL] 8i LOAD_LIMIT_STAND_PARAM => ' || v_ret);
            DBMS_OUTPUT.PUT_LINE('[DEBUG] Starting inline analysis...');
        END IF;
    EXCEPTION WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('[FAIL] 8i exception: ' || SQLERRM);
        DBMS_OUTPUT.PUT_LINE('[DEBUG] Starting inline analysis...');
    END;

    -- Debug: check what data is in the cursor
    DECLARE
        v_prod_code    VARCHAR2(100);
        v_lim_id       VARCHAR2(10);
        v_d_tot        VARCHAR2(50);
        v_w_tot        VARCHAR2(50);
        v_m_tot        VARCHAR2(50);
        v_desc         VARCHAR2(200);
        v_row_cnt      NUMBER := 0;
    BEGIN
        DBMS_OUTPUT.PUT_LINE('[DEBUG] Rows in st_pre_limit_stand (cursor data):');
        FOR r IN (SELECT * FROM st_pre_limit_stand WHERE product_code IS NOT NULL ORDER BY product_code) LOOP
            v_row_cnt := v_row_cnt + 1;
            DBMS_OUTPUT.PUT_LINE('  row ' || v_row_cnt
                || ': product_code=[' || r.product_code || ']'
                || ' limits_id=[' || r.limits_id || ']'
                || ' daily_tot=[' || r.daily_total_amnt || ']'
                || ' weekly_tot=[' || r.weekly_total_amnt || ']'
                || ' monthly_tot=[' || r.monthly_total_amnt || ']');

            -- Test the SUBSTR lookup
            BEGIN
                SELECT description INTO v_desc
                  FROM st_pre_bin_range_plastic_prod
                 WHERE product_code = SUBSTR(r.product_code, 2, 4);
                DBMS_OUTPUT.PUT_LINE('  => SUBSTR lookup OK: desc=[' || v_desc || ']');
            EXCEPTION
                WHEN NO_DATA_FOUND THEN
                    DBMS_OUTPUT.PUT_LINE('  => [FAIL] SUBSTR(' || r.product_code || ',2,4) = ['
                        || SUBSTR(r.product_code, 2, 4)
                        || '] NOT FOUND in st_pre_bin_range_plastic_prod!');
                WHEN TOO_MANY_ROWS THEN
                    DBMS_OUTPUT.PUT_LINE('  => [FAIL] SUBSTR lookup returned MULTIPLE rows!');
            END;
        END LOOP;
        DBMS_OUTPUT.PUT_LINE('[DEBUG] Total cursor rows: ' || v_row_cnt);

        IF v_row_cnt = 0 THEN
            DBMS_OUTPUT.PUT_LINE('[DEBUG] No rows in cursor — limit_stand may be empty!');
        END IF;
    END;

    -- Debug: check what is in st_pre_bin_range_plastic_prod
    DECLARE
        v_row_cnt NUMBER := 0;
    BEGIN
        DBMS_OUTPUT.PUT_LINE('[DEBUG] Rows in st_pre_bin_range_plastic_prod:');
        FOR r IN (SELECT product_code, description, bank_code FROM st_pre_bin_range_plastic_prod) LOOP
            v_row_cnt := v_row_cnt + 1;
            DBMS_OUTPUT.PUT_LINE('  row ' || v_row_cnt
                || ': bank=[' || r.bank_code || ']'
                || ' product_code=[' || r.product_code || ']'
                || ' desc=[' || r.description || ']');
        END LOOP;
        DBMS_OUTPUT.PUT_LINE('[DEBUG] Total bin_range rows: ' || v_row_cnt);
    END;

    -- Debug: try the INSERT into st_mig_SA_LIMITS_SETUP directly
    DECLARE
        v_mig_rec   st_mig_SA_LIMITS_SETUP%ROWTYPE := NULL;
        v_desc_prod VARCHAR2(200);
    BEGIN
        DBMS_OUTPUT.PUT_LINE('[DEBUG] Testing INSERT into st_mig_SA_LIMITS_SETUP...');

        -- Populate record like the PL/SQL does
        v_mig_rec.bank_code                := v_bank;
        v_mig_rec.limit_index              := 'LTST';
        v_mig_rec.limits_id                := '10';
        v_mig_rec.currency_code            := v_curr_num;
        v_mig_rec.host_scenario_processing := 'R';

        -- Get description
        BEGIN
            SELECT description INTO v_desc_prod
              FROM st_pre_bin_range_plastic_prod
             WHERE product_code = 'TST';
            DBMS_OUTPUT.PUT_LINE('[DEBUG] description=[' || v_desc_prod || ']');
        EXCEPTION WHEN OTHERS THEN
            DBMS_OUTPUT.PUT_LINE('[FAIL] description lookup: ' || SQLERRM);
        END;

        v_mig_rec.wording      := 'DEF_' || SUBSTR(TRIM(v_desc_prod), 1, 24);
        v_mig_rec.abrv_wording := SUBSTR(TRIM(v_desc_prod), 1, 16);

        -- Set all 3 periods (daily+weekly+monthly)
        v_mig_rec.per1_opt    := 'C'; v_mig_rec.per1_type   := 'D';
        v_mig_rec.per1_value  := '1'; v_mig_rec.per1_day_of := '1';
        v_mig_rec.per2_opt    := 'C'; v_mig_rec.per2_type   := 'W';
        v_mig_rec.per2_value  := '1'; v_mig_rec.per2_day_of := '1';
        v_mig_rec.per3_opt    := 'C'; v_mig_rec.per3_type   := 'M';
        v_mig_rec.per3_value  := '1'; v_mig_rec.per3_day_of := '1';
        v_mig_rec.nb_periods  := '3';

        -- online per1 (daily)
        v_mig_rec.on_per1_onus_amnt     := '5000';  v_mig_rec.on_per1_onus_nbr     := '100';
        v_mig_rec.on_per1_nat_amnt      := '5000';  v_mig_rec.on_per1_nat_nbr      := '100';
        v_mig_rec.on_per1_internat_amnt := '2000';  v_mig_rec.on_per1_internat_nbr := '050';
        v_mig_rec.on_per1_tot_amnt      := '7000';  v_mig_rec.on_per1_tot_nbr      := '150';
        -- online per2 (weekly)
        v_mig_rec.on_per2_onus_amnt     := '80000'; v_mig_rec.on_per2_onus_nbr     := '999';
        v_mig_rec.on_per2_nat_amnt      := '80000'; v_mig_rec.on_per2_nat_nbr      := '999';
        v_mig_rec.on_per2_internat_amnt := '40000'; v_mig_rec.on_per2_internat_nbr := '500';
        v_mig_rec.on_per2_tot_amnt      := '120000';v_mig_rec.on_per2_tot_nbr      := '999';
        -- online per3 (monthly)
        v_mig_rec.on_per3_onus_amnt     := '20000'; v_mig_rec.on_per3_onus_nbr     := '500';
        v_mig_rec.on_per3_nat_amnt      := '20000'; v_mig_rec.on_per3_nat_nbr      := '500';
        v_mig_rec.on_per3_internat_amnt := '10000'; v_mig_rec.on_per3_internat_nbr := '200';
        v_mig_rec.on_per3_tot_amnt      := '30000'; v_mig_rec.on_per3_tot_nbr      := '700';
        -- delegation = same as online
        v_mig_rec.off_per1_onus_amnt     := '5000';  v_mig_rec.off_per1_onus_nbr     := '100';
        v_mig_rec.off_per1_nat_amnt      := '5000';  v_mig_rec.off_per1_nat_nbr      := '100';
        v_mig_rec.off_per1_internat_amnt := '2000';  v_mig_rec.off_per1_internat_nbr := '050';
        v_mig_rec.off_per1_tot_amnt      := '7000';  v_mig_rec.off_per1_tot_nbr      := '150';
        v_mig_rec.off_per2_onus_amnt     := '80000'; v_mig_rec.off_per2_onus_nbr     := '999';
        v_mig_rec.off_per2_nat_amnt      := '80000'; v_mig_rec.off_per2_nat_nbr      := '999';
        v_mig_rec.off_per2_internat_amnt := '40000'; v_mig_rec.off_per2_internat_nbr := '500';
        v_mig_rec.off_per2_tot_amnt      := '120000';v_mig_rec.off_per2_tot_nbr      := '999';
        v_mig_rec.off_per3_onus_amnt     := '20000'; v_mig_rec.off_per3_onus_nbr     := '500';
        v_mig_rec.off_per3_nat_amnt      := '20000'; v_mig_rec.off_per3_nat_nbr      := '500';
        v_mig_rec.off_per3_internat_amnt := '10000'; v_mig_rec.off_per3_internat_nbr := '200';
        v_mig_rec.off_per3_tot_amnt      := '30000'; v_mig_rec.off_per3_tot_nbr      := '700';

        -- Try INSERT
        INSERT INTO st_mig_SA_LIMITS_SETUP VALUES v_mig_rec;
        DBMS_OUTPUT.PUT_LINE('[DEBUG] INSERT into st_mig_SA_LIMITS_SETUP => OK!');
        -- Rollback the test insert so it doesn't conflict later
        DELETE FROM st_mig_SA_LIMITS_SETUP WHERE bank_code = v_bank AND limit_index = 'LTST';

    EXCEPTION WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('[FAIL] INSERT st_mig_SA_LIMITS_SETUP: ' || SQLERRM);
        DBMS_OUTPUT.PUT_LINE('[FAIL] SQLCODE: ' || SQLCODE);
    END;

    -- Debug: show st_mig_SA_LIMITS_SETUP table columns
    DECLARE
        v_col_cnt NUMBER;
    BEGIN
        SELECT COUNT(*) INTO v_col_cnt
          FROM user_tab_columns
         WHERE table_name = 'ST_MIG_SA_LIMITS_SETUP';
        DBMS_OUTPUT.PUT_LINE('[DEBUG] st_mig_SA_LIMITS_SETUP has ' || v_col_cnt || ' columns');

        DBMS_OUTPUT.PUT_LINE('[DEBUG] NOT NULL columns:');
        FOR c IN (SELECT column_name, data_type, data_length, nullable
                    FROM user_tab_columns
                   WHERE table_name = 'ST_MIG_SA_LIMITS_SETUP'
                     AND nullable = 'N'
                   ORDER BY column_id) LOOP
            DBMS_OUTPUT.PUT_LINE('  ' || c.column_name || ' ' || c.data_type || '(' || c.data_length || ') NOT NULL');
        END LOOP;
    END;

    -- Check trace table for recent errors
    DBMS_OUTPUT.PUT_LINE('');
    DBMS_OUTPUT.PUT_LINE('[DEBUG] Recent trace entries:');
    BEGIN
        FOR t IN (SELECT * FROM (
                    SELECT function_name, user_message, ROWNUM rn
                      FROM pcrd_traces
                     WHERE package_name = 'PCRD_ST_BOARD_CONV_ISS_PAR'
                     ORDER BY ROWID DESC)
                  WHERE rn <= 5) LOOP
            DBMS_OUTPUT.PUT_LINE('  trace: func=[' || t.function_name || '] msg=[' || SUBSTR(t.user_message, 1, 100) || ']');
        END LOOP;
    EXCEPTION WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('[INFO] Could not read pcrd_traces: ' || SQLERRM);
    END;

    DBMS_OUTPUT.PUT_LINE('');
    DBMS_OUTPUT.PUT_LINE('[INFO] 8i debug complete. Fix the error above, then continue with remaining steps.');

    <<after_8i_debug>>

    -- If 8i passed, continue with remaining functions
    IF v_ret = 0 THEN
        DBMS_OUTPUT.PUT_LINE('');
        DBMS_OUTPUT.PUT_LINE('--- Remaining ISS sub-functions ---');

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
    END IF;

END;
/
