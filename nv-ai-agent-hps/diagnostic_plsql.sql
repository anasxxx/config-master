-- ============================================================
-- DIAGNOSTIC v9: Full 8-step test with short bank name (max 15)
--
-- Run in SQL Developer with F5.
-- ============================================================

-- Clean up leftovers
DELETE FROM st_pre_branch WHERE bank_code = 'ZZT';
DELETE FROM st_pre_resources WHERE bank_code = 'ZZT';
DELETE FROM st_pre_bin_range_plastic_prod WHERE bank_code = 'ZZT';
DELETE FROM st_pre_mig_CARD_FEES WHERE bank_code = 'ZZT';
DELETE FROM st_pre_service_PROD WHERE bank_code = 'ZZT';
DELETE FROM st_pre_limit_stand WHERE bank_code = 'ZZT';
DELETE FROM CENTER WHERE center_name = 'Banque Test';
DELETE FROM BANK WHERE bank_code = 'ZZT';
DELETE FROM BANK_ADDENDUM WHERE bank_code = 'ZZT';
DELETE FROM PCARD_TASKS_EXEC_GROUP_BANK WHERE bank_code = 'ZZT';
COMMIT;

-- Insert test data
INSERT INTO st_pre_branch (branch_code, bank_code, branch_wording, region_code, region_wording, city_code, city_wording)
VALUES ('001', 'ZZT', 'Agence Test', '10', 'Grand Casablanca', '01', 'Casablanca');

INSERT INTO st_pre_resources (bank_code, resource_wording)
VALUES ('ZZT', 'MCD_MDS');

INSERT INTO st_pre_bin_range_plastic_prod (bank_code, description, bin, plastic_type, product_type, product_code, tranche_min, tranche_max, index_pvk, service_code, network, expiration, renew, prior_exp)
VALUES ('ZZT', 'Carte Test', '445555', 'PVC', 'DEBIT', 'TST', '4455550000000000', '4455559999999999', '1', '101', 'VISA', '36', 'A', '3');

INSERT INTO st_pre_mig_CARD_FEES (bank_code, description, card_fees_code, card_fees_billing_evt, card_fees_grace_period, card_fees_billing_period, subscription_amount, fees_amount_first, damaged_replacement_fees, pin_replacement_fees)
VALUES ('ZZT', 'Frais Test', 'TST', 'M', 30, 'Y', 50, 10, 25, 5);

INSERT INTO st_pre_service_PROD (bank_code, product_code, retrait, achat, advance, ecommerce, transfert, quasicash, solde, releve, pinchange, refund, moneysend, billpayment, original, authentication, cashback)
VALUES ('ZZT', 'TST', '1', '1', NULL, '1', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);

INSERT INTO st_pre_limit_stand (product_code, LIMITS_ID, BANK_CODE, DAILY_DOM_AMNT, DAILY_DOM_NBR, DAILY_INT_AMNT, DAILY_INT_NBR, DAILY_TOTAL_AMNT, DAILY_TOTAL_NBR, MIN_AMOUNT_PER_TRANSACTION, MAX_AMOUNT_PER_TRANSACTION, WEEKLY_DOM_AMNT, WEEKLY_DOM_NBR, WEEKLY_INT_AMNT, WEEKLY_INT_NBR, WEEKLY_TOTAL_AMNT, WEEKLY_TOTAL_NBR, MONTHLY_DOM_AMNT, MONTHLY_DOM_NBR, MONTHLY_INT_AMNT, MONTHLY_INT_NBR, MONTHLY_TOTAL_AMNT, MONTHLY_TOTAL_NBR)
VALUES ('LTST', '10', 'ZZT', '5000', '100', '2000', '050', '7000', '150', '10', '50000', '20000', '500', '10000', '200', '30000', '700', '80000', '999', '40000', '500', '120000', '999');

COMMIT;

-- Run all 8 steps
SET SERVEROUTPUT ON SIZE 1000000;
DECLARE
    v_result       PLS_INTEGER;
    v_currency_rec currency_table%ROWTYPE;
    v_country_rec  country%ROWTYPE;
    v_cur_alpha    currency_table.currency_code_alpha%TYPE;
    v_cty_alpha    country.iso_country_alpha%TYPE;
BEGIN
    v_result := PCRD_GET_PARAM_GENERAL_ROWS.GET_CURRENCY_TABLE('504', v_currency_rec);
    v_cur_alpha := v_currency_rec.currency_code_alpha;
    DBMS_OUTPUT.PUT_LINE('1. GET_CURRENCY_TABLE => ' || v_result || '  [' || v_cur_alpha || ']');
    IF v_result <> 0 THEN ROLLBACK; RETURN; END IF;

    v_result := PCRD_GET_PARAM_GENERAL_ROWS.GET_COUNTRY('504', v_country_rec);
    v_cty_alpha := v_country_rec.iso_country_alpha;
    DBMS_OUTPUT.PUT_LINE('2. GET_COUNTRY => ' || v_result || '  [' || v_cty_alpha || ']');
    IF v_result <> 0 THEN ROLLBACK; RETURN; END IF;

    v_result := pcrd_st_board_conv_com.Sequence_ajustment;
    DBMS_OUTPUT.PUT_LINE('3. Sequence_ajustment => ' || v_result);
    IF v_result <> 0 THEN ROLLBACK; RETURN; END IF;
    COMMIT;

    v_result := PCRD_ST_CONV_CLEAN.AUT_CONV_GLB_TEMP_ROLLBACK('ZZT', 'Banque Test', '504');
    DBMS_OUTPUT.PUT_LINE('4. AUT_CONV_GLB_TEMP_ROLLBACK => ' || v_result);
    IF v_result <> 0 THEN ROLLBACK; RETURN; END IF;

    v_result := PCRD_ST_CONV_CLEAN.AUT_CONV_PRODUCT_TEMP_ROLLBACK('ZZT', 'Banque Test', '504');
    DBMS_OUTPUT.PUT_LINE('5. AUT_CONV_PRODUCT_TEMP_ROLLBACK => ' || v_result);
    IF v_result <> 0 THEN ROLLBACK; RETURN; END IF;

    v_result := pcrd_st_board_conv_com.LOAD_BANK_PARAMETERS(
        SYSDATE, 'ZZT', 'Banque Test', '504', v_cur_alpha, '504', v_cty_alpha);
    DBMS_OUTPUT.PUT_LINE('6. LOAD_BANK_PARAMETERS => ' || v_result);
    IF v_result <> 0 THEN DBMS_OUTPUT.PUT_LINE('   FAILED at step 6!'); ROLLBACK; RETURN; END IF;

    v_result := pcrd_st_board_conv_com.LOAD_BANK_CONV_COM_PARAM(
        SYSDATE, 'ZZT', 'Banque Test', '504', '504');
    DBMS_OUTPUT.PUT_LINE('7. LOAD_BANK_CONV_COM_PARAM => ' || v_result);
    IF v_result <> 0 THEN DBMS_OUTPUT.PUT_LINE('   FAILED at step 7!'); ROLLBACK; RETURN; END IF;

    v_result := pcrd_st_board_conv_iss_par.LOAD_BANK_CONV_ISS_PARAM(
        SYSDATE, 'ZZT', 'Banque Test', '504', v_cur_alpha, '504', v_cty_alpha);
    DBMS_OUTPUT.PUT_LINE('8. LOAD_BANK_CONV_ISS_PARAM => ' || v_result);
    IF v_result <> 0 THEN DBMS_OUTPUT.PUT_LINE('   FAILED at step 8!'); ROLLBACK; RETURN; END IF;

    DBMS_OUTPUT.PUT_LINE('=== ALL 8 STEPS PASSED ===');
    ROLLBACK;

EXCEPTION WHEN OTHERS THEN
    DBMS_OUTPUT.PUT_LINE('EXCEPTION: ' || SQLERRM);
    ROLLBACK;
END;
/

-- Clean up
DELETE FROM st_pre_branch WHERE bank_code = 'ZZT';
DELETE FROM st_pre_resources WHERE bank_code = 'ZZT';
DELETE FROM st_pre_bin_range_plastic_prod WHERE bank_code = 'ZZT';
DELETE FROM st_pre_mig_CARD_FEES WHERE bank_code = 'ZZT';
DELETE FROM st_pre_service_PROD WHERE bank_code = 'ZZT';
DELETE FROM st_pre_limit_stand WHERE bank_code = 'ZZT';
COMMIT;
