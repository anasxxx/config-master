-- ============================================================
-- DIAGNOSTIC v10: Drill into LOAD_BANK_CONV_ISS_PARAM (step 8)
-- Calls each of the 29 sub-functions individually.
--
-- Run in SQL Developer with F5.
-- ============================================================

-- Clean up
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
INSERT INTO st_pre_branch VALUES ('001', 'ZZT', 'Agence Test', '10', 'Grand Casablanca', '01', 'Casablanca');
INSERT INTO st_pre_resources VALUES ('ZZT', 'MCD_MDS');
INSERT INTO st_pre_bin_range_plastic_prod VALUES ('ZZT', 'Carte Test', '445555', 'PVC', 'DEBIT', 'TST', '4455550000000000', '4455559999999999', '1', '101', 'VISA', '36', 'A', '3');
INSERT INTO st_pre_mig_CARD_FEES VALUES ('ZZT', 'Frais Test', 'TST', 'M', 30, 'Y', 50, 10, 25, 5);
INSERT INTO st_pre_service_PROD VALUES ('ZZT', 'TST', '1', '1', NULL, '1', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);
INSERT INTO st_pre_limit_stand VALUES ('LTST', '10', 'ZZT', '5000', '100', '2000', '050', '7000', '150', '10', '50000', '20000', '500', '10000', '200', '30000', '700', '80000', '999', '40000', '500', '120000', '999');
COMMIT;

SET SERVEROUTPUT ON SIZE 1000000;
DECLARE
    v_r  PLS_INTEGER;
    v_cr currency_table%ROWTYPE;
    v_co country%ROWTYPE;
    v_ca currency_table.currency_code_alpha%TYPE;
    v_ya country.iso_country_alpha%TYPE;
    v_step VARCHAR2(60);
BEGIN
    -- Steps 1-7 (known to pass)
    v_r := PCRD_GET_PARAM_GENERAL_ROWS.GET_CURRENCY_TABLE('504', v_cr); v_ca := v_cr.currency_code_alpha;
    v_r := PCRD_GET_PARAM_GENERAL_ROWS.GET_COUNTRY('504', v_co); v_ya := v_co.iso_country_alpha;
    v_r := pcrd_st_board_conv_com.Sequence_ajustment; COMMIT;
    v_r := PCRD_ST_CONV_CLEAN.AUT_CONV_GLB_TEMP_ROLLBACK('ZZT', 'Banque Test', '504');
    v_r := PCRD_ST_CONV_CLEAN.AUT_CONV_PRODUCT_TEMP_ROLLBACK('ZZT', 'Banque Test', '504');
    v_r := pcrd_st_board_conv_com.LOAD_BANK_PARAMETERS(SYSDATE, 'ZZT', 'Banque Test', '504', v_ca, '504', v_ya);
    DBMS_OUTPUT.PUT_LINE('6. LOAD_BANK_PARAMETERS => ' || v_r);
    IF v_r <> 0 THEN DBMS_OUTPUT.PUT_LINE('STOPPED at step 6'); ROLLBACK; RETURN; END IF;
    v_r := pcrd_st_board_conv_com.LOAD_BANK_CONV_COM_PARAM(SYSDATE, 'ZZT', 'Banque Test', '504', '504');
    DBMS_OUTPUT.PUT_LINE('7. LOAD_BANK_CONV_COM_PARAM => ' || v_r);
    IF v_r <> 0 THEN DBMS_OUTPUT.PUT_LINE('STOPPED at step 7'); ROLLBACK; RETURN; END IF;

    -- Step 8: ISS sub-functions one by one
    v_step := '8a. RELOAD_RESOURCES_PARAM';
    v_r := pcrd_st_board_conv_iss_par.RELOAD_RESOURCES_PARAM(SYSDATE, 'Banque Test', 'ZZT');
    DBMS_OUTPUT.PUT_LINE(v_step || ' => ' || v_r);
    IF v_r <> 0 THEN ROLLBACK; RETURN; END IF;

    v_step := '8b. LOAD_branch_PARAMETERS';
    v_r := pcrd_st_board_conv_iss_par.LOAD_branch_PARAMETERS(SYSDATE, '504', '504', 'ZZT');
    DBMS_OUTPUT.PUT_LINE(v_step || ' => ' || v_r);
    IF v_r <> 0 THEN ROLLBACK; RETURN; END IF;

    v_step := '8c. LOAD_CARD_TYPE_PARAMETERS';
    v_r := pcrd_st_board_conv_iss_par.LOAD_CARD_TYPE_PARAMETERS(SYSDATE, 'ZZT', '504');
    DBMS_OUTPUT.PUT_LINE(v_step || ' => ' || v_r);
    IF v_r <> 0 THEN ROLLBACK; RETURN; END IF;

    v_step := '8d. LOAD_BIN_RANGE_PLASTIC_PAR';
    v_r := pcrd_st_board_conv_iss_par.LOAD_BIN_RANGE_PLASTIC_PAR(SYSDATE, 'ZZT', '504');
    DBMS_OUTPUT.PUT_LINE(v_step || ' => ' || v_r);
    IF v_r <> 0 THEN ROLLBACK; RETURN; END IF;

    v_step := '8e. LOAD_CARD_FEES_PARAMETERS';
    v_r := pcrd_st_board_conv_iss_par.LOAD_CARD_FEES_PARAMETERS(SYSDATE, 'ZZT', '504');
    DBMS_OUTPUT.PUT_LINE(v_step || ' => ' || v_r);
    IF v_r <> 0 THEN ROLLBACK; RETURN; END IF;

    v_step := '8f. LOAD_SERVICE_PROD_PARAM';
    v_r := pcrd_st_board_conv_iss_par.LOAD_SERVICE_PROD_PARAM(SYSDATE, 'ZZT', '504');
    DBMS_OUTPUT.PUT_LINE(v_step || ' => ' || v_r);
    IF v_r <> 0 THEN ROLLBACK; RETURN; END IF;

    v_step := '8g. LOAD_SERVICE_SETUP_PARAM';
    v_r := pcrd_st_board_conv_iss_par.LOAD_SERVICE_SETUP_PARAM(SYSDATE, 'ZZT', '504');
    DBMS_OUTPUT.PUT_LINE(v_step || ' => ' || v_r);
    IF v_r <> 0 THEN ROLLBACK; RETURN; END IF;

    v_step := '8h. LOAD_P7_limits_PARAMETERS';
    v_r := pcrd_st_board_conv_iss_par.LOAD_P7_limits_PARAMETERS(SYSDATE, 'ZZT', '504');
    DBMS_OUTPUT.PUT_LINE(v_step || ' => ' || v_r);
    IF v_r <> 0 THEN ROLLBACK; RETURN; END IF;

    v_step := '8i. LOAD_LIMIT_STAND_PARAM';
    v_r := pcrd_st_board_conv_iss_par.LOAD_LIMIT_STAND_PARAM(SYSDATE, 'ZZT', '504');
    DBMS_OUTPUT.PUT_LINE(v_step || ' => ' || v_r);
    IF v_r <> 0 THEN ROLLBACK; RETURN; END IF;

    v_step := '8j. LOAD_SA_LIMITS_SETUP_PARAM';
    v_r := pcrd_st_board_conv_iss_par.LOAD_SA_LIMITS_SETUP_PARAM(SYSDATE, 'ZZT', '504');
    DBMS_OUTPUT.PUT_LINE(v_step || ' => ' || v_r);
    IF v_r <> 0 THEN ROLLBACK; RETURN; END IF;

    v_step := '8k. LOAD_EMV_LIMIT_SETUP';
    v_r := pcrd_st_board_conv_iss_par.LOAD_EMV_LIMIT_SETUP(SYSDATE, 'ZZT', '504');
    DBMS_OUTPUT.PUT_LINE(v_step || ' => ' || v_r);
    IF v_r <> 0 THEN ROLLBACK; RETURN; END IF;

    v_step := '8l. LOAD_EMV_KEYS_ASSIG_PARAM';
    v_r := pcrd_st_board_conv_iss_par.LOAD_EMV_KEYS_ASSIG_PARAM(SYSDATE, 'ZZT', '504');
    DBMS_OUTPUT.PUT_LINE(v_step || ' => ' || v_r);
    IF v_r <> 0 THEN ROLLBACK; RETURN; END IF;

    v_step := '8m. LOAD_EMV_ICC_APPL_DEF';
    v_r := pcrd_st_board_conv_iss_par.LOAD_EMV_ICC_APPL_DEF(SYSDATE, 'ZZT', '504');
    DBMS_OUTPUT.PUT_LINE(v_step || ' => ' || v_r);
    IF v_r <> 0 THEN ROLLBACK; RETURN; END IF;

    v_step := '8n. LOAD_CONTROL_VERIFICATION';
    v_r := pcrd_st_board_conv_iss_par.LOAD_CONTROL_VERIFICATION_PARAM(SYSDATE, 'ZZT', '504');
    DBMS_OUTPUT.PUT_LINE(v_step || ' => ' || v_r);
    IF v_r <> 0 THEN ROLLBACK; RETURN; END IF;

    v_step := '8o. LOAD_CARD_PRODUCT_PARAM';
    v_r := pcrd_st_board_conv_iss_par.LOAD_CARD_PRODUCT_PARAM(SYSDATE, 'ZZT', '504');
    DBMS_OUTPUT.PUT_LINE(v_step || ' => ' || v_r);
    IF v_r <> 0 THEN ROLLBACK; RETURN; END IF;

    v_step := '8p. LOAD_CARD_RANGE_PARAM';
    v_r := pcrd_st_board_conv_iss_par.LOAD_CARD_RANGE_PARAM(SYSDATE, 'ZZT', '504');
    DBMS_OUTPUT.PUT_LINE(v_step || ' => ' || v_r);
    IF v_r <> 0 THEN ROLLBACK; RETURN; END IF;

    v_step := '8q. LOAD_CARD_GEN_COUNTERS';
    v_r := pcrd_st_board_conv_iss_par.LOAD_CARD_GEN_COUNTERS_PARAM(SYSDATE, 'ZZT', '504');
    DBMS_OUTPUT.PUT_LINE(v_step || ' => ' || v_r);
    IF v_r <> 0 THEN ROLLBACK; RETURN; END IF;

    v_step := '8r. LOAD_ROUTING_CRITERIA';
    v_r := pcrd_st_board_conv_iss_par.LOAD_ROUTING_CRITERIA_PARAM(SYSDATE, 'ZZT', '504');
    DBMS_OUTPUT.PUT_LINE(v_step || ' => ' || v_r);
    IF v_r <> 0 THEN ROLLBACK; RETURN; END IF;

    v_step := '8s. LOAD_RENEWAL_CRITERIA';
    v_r := pcrd_st_board_conv_iss_par.LOAD_RENEWAL_CRITERIA_PARAM(SYSDATE, 'ZZT', '504');
    DBMS_OUTPUT.PUT_LINE(v_step || ' => ' || v_r);
    IF v_r <> 0 THEN ROLLBACK; RETURN; END IF;

    v_step := '8t. LOAD_PCRD_CARD_PROD';
    v_r := pcrd_st_board_conv_iss_par.LOAD_PCRD_CARD_PROD_PARAM(SYSDATE, 'ZZT', '504');
    DBMS_OUTPUT.PUT_LINE(v_step || ' => ' || v_r);
    IF v_r <> 0 THEN ROLLBACK; RETURN; END IF;

    v_step := '8u. LOAD_Product_domain';
    v_r := pcrd_st_board_conv_iss_par.LOAD_Product_domain_PARAM(SYSDATE, 'ZZT', '504');
    DBMS_OUTPUT.PUT_LINE(v_step || ' => ' || v_r);
    IF v_r <> 0 THEN ROLLBACK; RETURN; END IF;

    v_step := '8v. LOAD_Entity_event';
    v_r := pcrd_st_board_conv_iss_par.LOAD_Entity_event_PARAM(SYSDATE, 'ZZT', '504');
    DBMS_OUTPUT.PUT_LINE(v_step || ' => ' || v_r);
    IF v_r <> 0 THEN ROLLBACK; RETURN; END IF;

    v_step := '8w. LOAD_icc_application';
    v_r := pcrd_st_board_conv_iss_par.LOAD_icc_application_PARAM(SYSDATE, 'ZZT', '504');
    DBMS_OUTPUT.PUT_LINE(v_step || ' => ' || v_r);
    IF v_r <> 0 THEN ROLLBACK; RETURN; END IF;

    v_step := '8x. LOAD_markup_calcul';
    v_r := pcrd_st_board_conv_iss_par.LOAD_markup_calcul(SYSDATE, 'ZZT', '504');
    DBMS_OUTPUT.PUT_LINE(v_step || ' => ' || v_r);
    IF v_r <> 0 THEN ROLLBACK; RETURN; END IF;

    v_step := '8y. LOAD_markup_index';
    v_r := pcrd_st_board_conv_iss_par.LOAD_markup_index(SYSDATE, 'ZZT', '504');
    DBMS_OUTPUT.PUT_LINE(v_step || ' => ' || v_r);
    IF v_r <> 0 THEN ROLLBACK; RETURN; END IF;

    v_step := '8z. LOAD_markup_el_cur';
    v_r := pcrd_st_board_conv_iss_par.LOAD_markup_el_cur(SYSDATE, 'ZZT', '504');
    DBMS_OUTPUT.PUT_LINE(v_step || ' => ' || v_r);
    IF v_r <> 0 THEN ROLLBACK; RETURN; END IF;

    v_step := '8A. LOAD_Fleet_ctrl';
    v_r := pcrd_st_board_conv_iss_par.LOAD_Fleet_ctrl_PARAM(SYSDATE, 'ZZT', '504');
    DBMS_OUTPUT.PUT_LINE(v_step || ' => ' || v_r);
    IF v_r <> 0 THEN ROLLBACK; RETURN; END IF;

    v_step := '8B. MOVE_PARAMETERS_LOADED';
    v_r := pcrd_st_board_conv_iss_par.MOVE_PARAMETERS_LOADED(SYSDATE, 'ZZT');
    DBMS_OUTPUT.PUT_LINE(v_step || ' => ' || v_r);
    IF v_r <> 0 THEN ROLLBACK; RETURN; END IF;

    v_step := '8C. MAIN_AUT_POST';
    v_r := pcrd_st_conv_catalogue.MAIN_AUT_POST('ZZT');
    DBMS_OUTPUT.PUT_LINE(v_step || ' => ' || v_r);
    IF v_r <> 0 THEN ROLLBACK; RETURN; END IF;

    DBMS_OUTPUT.PUT_LINE('=== ALL STEPS PASSED ===');
    ROLLBACK;

EXCEPTION WHEN OTHERS THEN
    DBMS_OUTPUT.PUT_LINE('EXCEPTION at ' || v_step || ': ' || SQLERRM);
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
