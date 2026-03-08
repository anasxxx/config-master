-- ============================================================
-- DIAGNOSTIC v3: Investigate CENTER_CODE 21 collision
--
-- Run in SQL Developer with F5.
-- ============================================================

SET SERVEROUTPUT ON SIZE 1000000;
DECLARE
    v_seq   PLS_INTEGER;
    v_cnt   PLS_INTEGER;
BEGIN
    -- 1. What sequence_id would LOAD_BANK_PARAMETERS compute?
    SELECT MAX(TO_NUMBER(NVL(CENTER_CODE,0))) + 1 INTO v_seq
    FROM CENTER WHERE CENTER_CODE < '21';
    DBMS_OUTPUT.PUT_LINE('Computed next center_code = ' || v_seq);

    -- 2. Does that center already exist?
    SELECT COUNT(*) INTO v_cnt FROM CENTER WHERE CENTER_CODE = TO_CHAR(v_seq);
    DBMS_OUTPUT.PUT_LINE('Center ' || v_seq || ' exists? ' || CASE WHEN v_cnt > 0 THEN 'YES' ELSE 'NO' END);

    -- 3. Show ALL centers (code + name) to understand the data
    DBMS_OUTPUT.PUT_LINE('--- ALL CENTERS ---');
    FOR rec IN (SELECT CENTER_CODE, CENTER_NAME FROM CENTER ORDER BY TO_NUMBER(NVL(CENTER_CODE,0))) LOOP
        DBMS_OUTPUT.PUT_LINE('  code=[' || rec.CENTER_CODE || '] name=[' || rec.CENTER_NAME || ']');
    END LOOP;

    -- 4. Total count
    SELECT COUNT(*) INTO v_cnt FROM CENTER;
    DBMS_OUTPUT.PUT_LINE('Total centers: ' || v_cnt);
END;
/
