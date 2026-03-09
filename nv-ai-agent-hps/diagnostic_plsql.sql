-- ============================================================
-- DIAGNOSTIC v8: Drill into LOAD_BANK_PARAMETERS again
-- Center 21 should be free — find the REAL error now.
--
-- Run in SQL Developer with F5.
-- ============================================================

SET SERVEROUTPUT ON SIZE 1000000;
DECLARE
    v_result        PLS_INTEGER;
    v_currency_rec  currency_table%ROWTYPE;
    v_country_rec   country%ROWTYPE;
    v_cur_alpha     currency_table.currency_code_alpha%TYPE;
    v_cty_alpha     country.iso_country_alpha%TYPE;
    v_count         PLS_INTEGER;
    v_region_code   region.region_code%TYPE;
    v_city_code     city.city_code%TYPE;
    v_sequence_id   PLS_INTEGER;
BEGIN
    -- Prerequisites
    v_result := PCRD_GET_PARAM_GENERAL_ROWS.GET_CURRENCY_TABLE('504', v_currency_rec);
    v_cur_alpha := v_currency_rec.currency_code_alpha;
    v_result := PCRD_GET_PARAM_GENERAL_ROWS.GET_COUNTRY('504', v_country_rec);
    v_cty_alpha := v_country_rec.iso_country_alpha;
    v_result := pcrd_st_board_conv_com.Sequence_ajustment;
    COMMIT;
    v_result := PCRD_ST_CONV_CLEAN.AUT_CONV_GLB_TEMP_ROLLBACK('ZZT', 'Banque Test Insertion', '504');
    v_result := PCRD_ST_CONV_CLEAN.AUT_CONV_PRODUCT_TEMP_ROLLBACK('ZZT', 'Banque Test Insertion', '504');
    DBMS_OUTPUT.PUT_LINE('Prerequisites OK. cur=[' || v_cur_alpha || '] cty=[' || v_cty_alpha || ']');

    -- Check center 21 status
    SELECT COUNT(*) INTO v_count FROM CENTER WHERE CENTER_CODE = '21';
    DBMS_OUTPUT.PUT_LINE('Center 21 exists BEFORE insert? ' || CASE WHEN v_count > 0 THEN 'YES!!' ELSE 'NO (good)' END);

    -- 6a. REGION lookup
    BEGIN
        SELECT count(*) INTO v_count FROM region WHERE country_code = '504';
        DBMS_OUTPUT.PUT_LINE('6a. REGION count for country 504 = ' || v_count);
        IF v_count = 0 THEN
            v_region_code := '001';
            INSERT INTO REGION VALUES('504', v_region_code, 'DEFAULT', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 30, NULL, 'POWERCARD', NULL, NULL, NULL);
            DBMS_OUTPUT.PUT_LINE('    Inserted new REGION 001');
        ELSE
            SELECT region_code INTO v_region_code FROM region WHERE country_code = '504' AND rownum = 1;
            DBMS_OUTPUT.PUT_LINE('    Using existing region_code = [' || v_region_code || ']');
        END IF;
    EXCEPTION WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('6a. REGION FAILED: ' || SQLERRM);
        ROLLBACK; RETURN;
    END;

    -- 6b. CITY lookup
    BEGIN
        SELECT count(*) INTO v_count FROM city WHERE region_code = v_region_code AND country_code = '504';
        DBMS_OUTPUT.PUT_LINE('6b. CITY count for region ' || v_region_code || ' = ' || v_count);
        IF v_count = 0 THEN
            v_city_code := '00001';
            INSERT INTO CITY VALUES('504', v_city_code, 'DEFAULT', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, v_region_code, 'GMT', NULL, NULL, NULL, NULL);
            DBMS_OUTPUT.PUT_LINE('    Inserted new CITY 00001');
        ELSE
            SELECT city_code INTO v_city_code FROM city WHERE region_code = v_region_code AND country_code = '504' AND rownum = 1;
            DBMS_OUTPUT.PUT_LINE('    Using existing city_code = [' || v_city_code || ']');
        END IF;
    EXCEPTION WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('6b. CITY FAILED: ' || SQLERRM);
        ROLLBACK; RETURN;
    END;

    -- 6c. CENTER insert
    BEGIN
        SELECT MAX(TO_NUMBER(NVL(CENTER_CODE, 0))) + 1 INTO v_sequence_id
        FROM CENTER WHERE CENTER_CODE < '21';
        DBMS_OUTPUT.PUT_LINE('6c. CENTER next sequence_id = ' || v_sequence_id);

        SELECT COUNT(*) INTO v_count FROM CENTER WHERE CENTER_CODE = TO_CHAR(v_sequence_id);
        DBMS_OUTPUT.PUT_LINE('    Center ' || v_sequence_id || ' already exists? ' || CASE WHEN v_count > 0 THEN 'YES!!' ELSE 'NO (good)' END);

        INSERT INTO CENTER
        VALUES(v_sequence_id, 'L', 'Banque Test Insertion', '01', 'Y', '504', v_cty_alpha, '504', v_cur_alpha, 'SIAINT_BO', TO_DATE('2016-07-25 10:08:08', 'YYYY-MM-DD HH24:MI:SS'), NULL, NULL);
        DBMS_OUTPUT.PUT_LINE('    CENTER inserted OK');
    EXCEPTION WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('6c. CENTER FAILED: ' || SQLERRM);
        DBMS_OUTPUT.PUT_LINE('    sequence_id was: ' || v_sequence_id);
        ROLLBACK; RETURN;
    END;

    -- 6d. BANK insert
    BEGIN
        INSERT INTO BANK
        VALUES('ZZT', 'BU', v_sequence_id, 'Banque Test Insertion', 'Banque Test Insertion', 'Co-operative House', 'Huteau Lane', NULL, NULL, v_city_code, NULL, v_region_code, NULL, '504', NULL, NULL, NULL, NULL, NULL, EMPTY_CLOB(), 'P', 'N', 'N', 'Y', '000001', NULL, NULL, 0, TO_DATE('2003-02-24 00:00:00', 'YYYY-MM-DD HH24:MI:SS'), NULL, NULL, NULL, NULL, NULL, TO_DATE('2003-02-24 00:00:00', 'YYYY-MM-DD HH24:MI:SS'), NULL, '504', 'O', 10, 'N', 10, 'N', 24, 'N', 11, 'N', 10, 'N', 10, 'N', NULL, 0, 'C', NULL, NULL, NULL, 'A', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'POWERCARD', SYSDATE, 'POWERCARD', SYSDATE);
        DBMS_OUTPUT.PUT_LINE('6d. BANK inserted OK');
    EXCEPTION WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('6d. BANK FAILED: ' || SQLERRM);
        ROLLBACK; RETURN;
    END;

    -- 6e. BANK_ADDENDUM insert
    BEGIN
        INSERT INTO BANK_ADDENDUM
        VALUES('ZZT', 'ZZT', 'N', NULL, NULL, NULL, 'N', NULL, '0000100000', NULL, 'N', NULL, NULL, NULL, 'G', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'N', 'N', 'N', 'Y', NULL, NULL, 'N', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'User02', TO_DATE('2016-07-25 10:09:07', 'YYYY-MM-DD HH24:MI:SS'), NULL, NULL);
        DBMS_OUTPUT.PUT_LINE('6e. BANK_ADDENDUM inserted OK');
    EXCEPTION WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('6e. BANK_ADDENDUM FAILED: ' || SQLERRM);
        ROLLBACK; RETURN;
    END;

    -- 6f. PCARD_TASKS_EXEC_GROUP_BANK insert
    BEGIN
        INSERT INTO PCARD_TASKS_EXEC_GROUP_BANK
        VALUES('DFLGRP', 'ZZT', 'firstUser', TO_DATE('2024-02-28 16:15:37', 'YYYY-MM-DD HH24:MI:SS'), 'firstUser', TO_DATE('2024-02-28 17:16:38', 'YYYY-MM-DD HH24:MI:SS'));
        DBMS_OUTPUT.PUT_LINE('6f. PCARD_TASKS_EXEC_GROUP_BANK inserted OK');
    EXCEPTION WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('6f. PCARD_TASKS FAILED: ' || SQLERRM);
        ROLLBACK; RETURN;
    END;

    DBMS_OUTPUT.PUT_LINE('=== ALL SUB-STEPS PASSED ===');
    ROLLBACK;

EXCEPTION WHEN OTHERS THEN
    DBMS_OUTPUT.PUT_LINE('UNEXPECTED: ' || SQLERRM);
    DBMS_OUTPUT.PUT_LINE(DBMS_UTILITY.FORMAT_ERROR_BACKTRACE);
    ROLLBACK;
END;
/
