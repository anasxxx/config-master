-- ============================================================
-- ONE-TIME FIX: Remove bank 101010 (NEPS) to free center 21
--
-- Uses the PL/SQL's own cleanup function (flag='0') which
-- handles all FK dependencies (BANK_NETWORK, etc.)
--
-- Run in SQL Developer with F5.
-- ============================================================

SET SERVEROUTPUT ON SIZE 1000000;
DECLARE
    v_result  PLS_INTEGER;
    v_bank    BANK%ROWTYPE;
BEGIN
    -- Look up bank 101010's details
    SELECT * INTO v_bank FROM BANK WHERE bank_code = '101010';
    DBMS_OUTPUT.PUT_LINE('Bank: ' || v_bank.bank_code || ' / ' || v_bank.bank_name);
    DBMS_OUTPUT.PUT_LINE('Currency: ' || v_bank.currency_code || ' Country: ' || v_bank.country_code);

    -- Call MAIN_BOARD_CONV_PARAM with flag='0' (full cascade cleanup)
    v_result := pcrd_st_board_conv_main.MAIN_BOARD_CONV_PARAM(
        SYSDATE,
        '101010',
        v_bank.bank_name,
        v_bank.currency_code,
        v_bank.country_code,
        '0'
    );

    IF v_result = 0 THEN
        DBMS_OUTPUT.PUT_LINE('Cleanup OK! Center 21 should now be free.');
        COMMIT;
    ELSE
        DBMS_OUTPUT.PUT_LINE('Cleanup returned: ' || v_result);
        ROLLBACK;
    END IF;

    -- Verify center 21 is gone
    DECLARE v_cnt PLS_INTEGER;
    BEGIN
        SELECT COUNT(*) INTO v_cnt FROM CENTER WHERE CENTER_CODE = '21';
        DBMS_OUTPUT.PUT_LINE('Center 21 still exists? ' || CASE WHEN v_cnt > 0 THEN 'YES (problem!)' ELSE 'NO (good!)' END);
    END;
END;
/
