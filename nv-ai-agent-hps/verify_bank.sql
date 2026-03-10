-- Quick verification: where did bank ZZT end up?
-- Run in SQL Developer (F5)
SET SERVEROUTPUT ON SIZE 100000;

DECLARE
    v_cnt  NUMBER;
    v_code VARCHAR2(100);
    v_name VARCHAR2(200);
    v_cur  SYS_REFCURSOR;
BEGIN
    -- Check production BANK table
    SELECT COUNT(*) INTO v_cnt FROM bank WHERE bank_code = 'ZZT';
    DBMS_OUTPUT.PUT_LINE('BANK table (exact ZZT): ' || v_cnt || ' rows');

    SELECT COUNT(*) INTO v_cnt FROM bank WHERE TRIM(bank_code) = 'ZZT';
    DBMS_OUTPUT.PUT_LINE('BANK table (trimmed ZZT): ' || v_cnt || ' rows');

    SELECT COUNT(*) INTO v_cnt FROM bank WHERE bank_code LIKE '%ZZT%';
    DBMS_OUTPUT.PUT_LINE('BANK table (LIKE ZZT): ' || v_cnt || ' rows');

    -- Check staging migration table (dynamic SQL — table may not exist)
    BEGIN
        EXECUTE IMMEDIATE 'SELECT COUNT(*) FROM st_mig_bank WHERE bank_code = ''ZZT''' INTO v_cnt;
        DBMS_OUTPUT.PUT_LINE('st_mig_bank (ZZT): ' || v_cnt || ' rows');
    EXCEPTION WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('st_mig_bank: ' || SQLERRM);
    END;

    -- Check CENTER table for new center
    DBMS_OUTPUT.PUT_LINE('');
    DBMS_OUTPUT.PUT_LINE('--- Recent CENTER entries (last 5) ---');
    FOR r IN (SELECT * FROM (SELECT center_code, center_name FROM center ORDER BY center_code DESC) WHERE ROWNUM <= 5) LOOP
        DBMS_OUTPUT.PUT_LINE('  center_code=[' || r.center_code || '] name=[' || r.center_name || ']');
    END LOOP;

    -- Check last 5 banks
    DBMS_OUTPUT.PUT_LINE('');
    DBMS_OUTPUT.PUT_LINE('--- Last 5 BANK entries ---');
    FOR r IN (SELECT * FROM (SELECT bank_code, bank_name FROM bank ORDER BY ROWID DESC) WHERE ROWNUM <= 5) LOOP
        DBMS_OUTPUT.PUT_LINE('  bank_code=[' || r.bank_code || '] name=[' || r.bank_name || ']');
    END LOOP;

    -- Check BANK_ADDENDUM (dynamic SQL — table may not exist)
    BEGIN
        EXECUTE IMMEDIATE 'SELECT COUNT(*) FROM bank_addendum WHERE bank_code = ''ZZT''' INTO v_cnt;
        DBMS_OUTPUT.PUT_LINE('');
        DBMS_OUTPUT.PUT_LINE('BANK_ADDENDUM (ZZT): ' || v_cnt || ' rows');
    EXCEPTION WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('BANK_ADDENDUM: ' || SQLERRM);
    END;

    -- Check if bank was created with center
    DBMS_OUTPUT.PUT_LINE('');
    BEGIN
        SELECT COUNT(*) INTO v_cnt FROM center WHERE center_code = '21';
        DBMS_OUTPUT.PUT_LINE('CENTER 21 exists now: ' || CASE WHEN v_cnt > 0 THEN 'YES' ELSE 'NO' END);
    EXCEPTION WHEN OTHERS THEN NULL;
    END;

END;
/
