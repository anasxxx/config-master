-- ============================================================
-- DIAGNOSTIC v12b: Quick verify product_type='01' fits in
-- NETWORK_CARD_TYPE CHAR(2), then run FULL main orchestrator.
--
-- Run in SQL Developer with F5.
-- ============================================================

-- [A] Quick INSERT test: product_type='01' into st_mig_CARD_TYPE
SET SERVEROUTPUT ON SIZE 1000000;
DECLARE
    v_rec st_mig_CARD_TYPE%ROWTYPE := NULL;
BEGIN
    DELETE FROM st_mig_CARD_TYPE WHERE bank_code = 'ZZT';

    v_rec.bank_code            := 'ZZT';
    v_rec.network_card_type    := TRIM('01');   -- was 'DEBIT' (5 chars), now '01' (2 chars)
    v_rec.abrv_wording         := SUBSTR(TRIM('Carte Test'), 1, 16);
    v_rec.wording              := SUBSTR(TRIM('Carte Test'), 1, 30);
    v_rec.class                := '01';
    v_rec.class_group          := 'IN';
    v_rec.class_level          := '1';
    v_rec.corporate_card_flag  := 'N';
    v_rec.cobranded_card_flag  := 'N';
    v_rec.purchase_card_flag   := 'N';
    v_rec.business_card_flag   := 'N';
    v_rec.affinity_card_flag   := 'N';
    v_rec.network_code         := '01';

    INSERT INTO st_mig_CARD_TYPE VALUES v_rec;
    DBMS_OUTPUT.PUT_LINE('[A] INSERT with product_type=01 => OK!');
    ROLLBACK;
EXCEPTION WHEN OTHERS THEN
    DBMS_OUTPUT.PUT_LINE('[A] INSERT FAILED: ' || SQLERRM);
    ROLLBACK;
END;
/

-- [B] Call MAIN_BOARD_CONV_PARAM directly (like Spring Boot does)
-- Package: PCRD_ST_BOARD_CONV_MAIN
-- Signature: (p_business_date, p_bank_code, p_bank_wording,
--             p_currency_code, p_country_code, p_action_flag)
--
-- NOTE: staging tables must already be populated by the Spring Boot
-- backend (test_db_insert.py). This block just tests the PL/SQL
-- main orchestrator in isolation.
--
-- To test end-to-end, run test_db_insert.py instead.
-- This section is commented out — uncomment if you want to test.
/*
DECLARE
    v_ret PLS_INTEGER;
BEGIN
    -- Cleanup first (flag='0')
    v_ret := PCRD_ST_BOARD_CONV_MAIN.MAIN_BOARD_CONV_PARAM(
        SYSDATE, 'ZZT', 'Banque Test', 'MAD', 'MA', '0');
    DBMS_OUTPUT.PUT_LINE('[B] cleanup => ' || v_ret);
    COMMIT;

    -- Create (flag='1')
    v_ret := PCRD_ST_BOARD_CONV_MAIN.MAIN_BOARD_CONV_PARAM(
        SYSDATE, 'ZZT', 'Banque Test', 'MAD', 'MA', '1');
    DBMS_OUTPUT.PUT_LINE('[B] create  => ' || v_ret);
    IF v_ret = 0 THEN
        DBMS_OUTPUT.PUT_LINE('[B] === ALL PASSED ===');
        COMMIT;
    ELSE
        DBMS_OUTPUT.PUT_LINE('[B] === FAILED with code ' || v_ret || ' ===');
        ROLLBACK;
    END IF;
EXCEPTION WHEN OTHERS THEN
    DBMS_OUTPUT.PUT_LINE('[B] ERROR: ' || SQLERRM);
    ROLLBACK;
END;
/
*/
