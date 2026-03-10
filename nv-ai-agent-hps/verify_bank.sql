-- Quick verification: where did bank ZZT end up?
-- Run in SQL Developer (F5)
SET SERVEROUTPUT ON SIZE 100000;

DECLARE
    v_cnt NUMBER;
BEGIN
    -- Check production BANK table
    SELECT COUNT(*) INTO v_cnt FROM bank WHERE bank_code = 'ZZT';
    DBMS_OUTPUT.PUT_LINE('BANK table (exact ZZT): ' || v_cnt || ' rows');

    SELECT COUNT(*) INTO v_cnt FROM bank WHERE TRIM(bank_code) = 'ZZT';
    DBMS_OUTPUT.PUT_LINE('BANK table (trimmed ZZT): ' || v_cnt || ' rows');

    SELECT COUNT(*) INTO v_cnt FROM bank WHERE bank_code LIKE '%ZZT%';
    DBMS_OUTPUT.PUT_LINE('BANK table (LIKE ZZT): ' || v_cnt || ' rows');

    -- Check staging migration table
    BEGIN
        SELECT COUNT(*) INTO v_cnt FROM st_mig_bank WHERE bank_code = 'ZZT';
        DBMS_OUTPUT.PUT_LINE('st_mig_bank (ZZT): ' || v_cnt || ' rows');
    EXCEPTION WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('st_mig_bank: ' || SQLERRM);
    END;

    -- Check CENTER table for new center
    DBMS_OUTPUT.PUT_LINE('');
    DBMS_OUTPUT.PUT_LINE('--- Recent CENTER entries ---');
    FOR r IN (SELECT center_code, center_name FROM center ORDER BY center_code DESC FETCH FIRST 5 ROWS ONLY) LOOP
        DBMS_OUTPUT.PUT_LINE('  center_code=[' || r.center_code || '] name=[' || r.center_name || ']');
    END LOOP;

    -- Check last 5 banks
    DBMS_OUTPUT.PUT_LINE('');
    DBMS_OUTPUT.PUT_LINE('--- Last 5 BANK entries ---');
    FOR r IN (SELECT bank_code, bank_name FROM bank ORDER BY ROWID DESC FETCH FIRST 5 ROWS ONLY) LOOP
        DBMS_OUTPUT.PUT_LINE('  bank_code=[' || r.bank_code || '] name=[' || r.bank_name || ']');
    END LOOP;

    -- Check BANK_ADDENDUM
    BEGIN
        SELECT COUNT(*) INTO v_cnt FROM bank_addendum WHERE bank_code = 'ZZT';
        DBMS_OUTPUT.PUT_LINE('');
        DBMS_OUTPUT.PUT_LINE('BANK_ADDENDUM (ZZT): ' || v_cnt || ' rows');
    EXCEPTION WHEN OTHERS THEN NULL;
    END;
END;
/
