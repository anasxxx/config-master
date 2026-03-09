-- ============================================================
-- DIAGNOSTIC v11: Replicate LOAD_CARD_TYPE_PARAMETERS logic
-- to get the exact Oracle error.
--
-- Run in SQL Developer with F5.
-- ============================================================

-- Insert test data (if not already there)
DELETE FROM st_pre_bin_range_plastic_prod WHERE bank_code = 'ZZT';
INSERT INTO st_pre_bin_range_plastic_prod VALUES ('ZZT', 'Carte Test', '445555', 'PVC', 'DEBIT', 'TST', '4455550000000000', '4455559999999999', '1', '101', 'VISA', '36', 'A', '3');
COMMIT;

-- Show what the cursor would read
SELECT product_code, product_type, description, network FROM st_pre_bin_range_plastic_prod WHERE product_code IS NOT NULL ORDER BY product_code;

-- Show st_mig_CARD_TYPE table structure
SELECT column_name, data_type, data_length, nullable FROM user_tab_columns WHERE table_name = 'ST_MIG_CARD_TYPE' ORDER BY column_id;

-- Try the insert manually
SET SERVEROUTPUT ON SIZE 1000000;
DECLARE
    v_rec st_mig_CARD_TYPE%ROWTYPE := NULL;
BEGIN
    -- Delete any old staging data
    DELETE FROM st_mig_CARD_TYPE WHERE bank_code = 'ZZT';

    -- Set fields exactly like the PL/SQL does
    v_rec.bank_code            := 'ZZT';
    v_rec.network_card_type    := TRIM('DEBIT');
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
    v_rec.network_code         := '01';  -- VISA

    DBMS_OUTPUT.PUT_LINE('Attempting INSERT INTO st_mig_CARD_TYPE...');
    DBMS_OUTPUT.PUT_LINE('  bank_code=' || v_rec.bank_code);
    DBMS_OUTPUT.PUT_LINE('  network_card_type=' || v_rec.network_card_type);
    DBMS_OUTPUT.PUT_LINE('  network_code=' || v_rec.network_code);
    DBMS_OUTPUT.PUT_LINE('  wording=' || v_rec.wording);

    INSERT INTO st_mig_CARD_TYPE VALUES v_rec;
    DBMS_OUTPUT.PUT_LINE('INSERT OK!');
    ROLLBACK;

EXCEPTION WHEN OTHERS THEN
    DBMS_OUTPUT.PUT_LINE('INSERT FAILED: ' || SQLERRM);
    ROLLBACK;
END;
/

-- Clean up
DELETE FROM st_pre_bin_range_plastic_prod WHERE bank_code = 'ZZT';
COMMIT;
