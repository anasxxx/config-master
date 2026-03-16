-- ============================================================
-- ConfigMaster DB Insertion Test Script
-- Goal: client_078_other (bank: cih, code: 200)
-- Target: Oracle POWERCARD @ 10.110.120.14:1521/PCARD
-- ============================================================
SET SERVEROUTPUT ON;

-- ── Step 1: Insert into staging tables ─────────────────────

INSERT INTO st_pre_branch (bank_code, branch_code, branch_wording, region_code, region_wording, city_code, city_wording)
VALUES ('200', '102', 'tahrir', '245', 'Casablanca', '001', 'Casablanca');

INSERT INTO st_pre_bin_range_plastic_prod (
    product_code, bank_code, description, bin, plastic_type, product_type,
    tranche_min, tranche_max, index_pvk, service_code, network,
    expiration, renew, prior_exp
) VALUES (
    'prd', '200', 'carte fidelité', '445555',
    'STD', '02', '', '',
    '1', '101', 'VISA',
    '36', 'Y', '30'
);

INSERT INTO st_pre_mig_card_fees (
    card_fees_code, bank_code, description, card_fees_billing_evt,
    card_fees_grace_period, card_fees_billing_period,
    subscription_amount, fees_amount_first,
    damaged_replacement_fees, pin_replacement_fees
) VALUES (
    'prd', '200', '5000, 20000, 80000',
    '1', 30, 'M',
    50, 10,
    25, 5
);

INSERT INTO st_pre_service_prod (
    bank_code, product_code, retrait, achat, advance, ecommerce, transfert, quasicash, solde, releve, pinchange, refund, moneysend, billpayment, original, authentication, cashback
) VALUES (
    '200', 'prd', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '1', '1', NULL
);

INSERT INTO st_pre_limit_stand (
    bank_code, product_code, limits_id,
    daily_dom_amnt, daily_dom_nbr, daily_int_amnt, daily_int_nbr,
    daily_total_amnt, daily_total_nbr,
    min_amount_per_transaction, max_amount_per_transaction,
    weekly_dom_amnt, weekly_dom_nbr, weekly_int_amnt, weekly_int_nbr,
    weekly_total_amnt, weekly_total_nbr,
    monthly_dom_amnt, monthly_dom_nbr, monthly_int_amnt, monthly_int_nbr,
    monthly_total_amnt, monthly_total_nbr
) VALUES (
    '200', 'Lprd', '10',
    '5000', NULL, '5000', NULL,
    NULL, NULL,
    '0', '0',
    '20000', NULL, '20000', NULL,
    NULL, NULL,
    '80000', NULL, '80000', NULL,
    NULL, NULL
);

COMMIT;

-- ── Step 2: Call PL/SQL main function ──────────────────────

DECLARE
    v_result         PLS_INTEGER;
    v_currency_code  VARCHAR2(3);
    v_country_code   VARCHAR2(3);
BEGIN
    SELECT currency_code INTO v_currency_code
    FROM currency_table WHERE TRIM(currency_code_alpha) = 'MAD';

    SELECT country_code INTO v_country_code
    FROM country WHERE TRIM(iso_country_alpha) = 'MAR';

    DBMS_OUTPUT.PUT_LINE('Resolved currency: ' || v_currency_code);
    DBMS_OUTPUT.PUT_LINE('Resolved country:  ' || v_country_code);

    v_result := PCRD_ST_BOARD_CONV_MAIN.MAIN_BOARD_CONV_PARAM(
        p_business_date  => SYSTIMESTAMP,
        p_bank_code      => '200',
        p_bank_wording   => 'cih',
        p_currency_code  => v_currency_code,
        p_country_code   => v_country_code,
        p_action_flag    => '1'
    );

    DBMS_OUTPUT.PUT_LINE('PL/SQL result: ' || v_result);
    IF v_result = 0 THEN
        DBMS_OUTPUT.PUT_LINE('SUCCESS: Bank cih (code 200) inserted.');
        COMMIT;
    ELSE
        DBMS_OUTPUT.PUT_LINE('ERROR: PL/SQL returned ' || v_result);
        ROLLBACK;
    END IF;
END;
/

-- ── Step 3: Cleanup staging tables ─────────────────────────
DELETE FROM st_pre_branch WHERE branch_code = '102';
DELETE FROM st_pre_bin_range_plastic_prod WHERE product_code = 'prd';
DELETE FROM st_pre_mig_card_fees WHERE card_fees_code = 'prd';
DELETE FROM st_pre_service_prod WHERE product_code = 'prd';
DELETE FROM st_pre_limit_stand WHERE product_code = 'Lprd' AND limits_id = '10';
COMMIT;

-- ── Step 4: Verify final tables ───────────────────────────
SELECT * FROM bank WHERE bank_code = '200';
SELECT * FROM branch WHERE bank_code = '200';
SELECT * FROM card_type WHERE bank_code = '200';
SELECT * FROM card_fees WHERE bank_code = '200';
SELECT * FROM limits WHERE bank_code = '200';
