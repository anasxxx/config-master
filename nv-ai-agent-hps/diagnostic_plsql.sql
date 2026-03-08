-- ============================================================
-- ONE-TIME FIX: Delete center 21 to unblock LOAD_BANK_PARAMETERS
--
-- The PL/SQL computes MAX(center_code < '21') + 1 = 21, but
-- center 21 (NEPS CENTER) already exists → PK collision.
--
-- Run in SQL Developer with F5.
-- ============================================================

-- Step 1: Check if any BANK references center 21
SELECT 'BANK referencing center 21' AS info, bank_code, bank_name
FROM BANK WHERE center_code = '21';

-- Step 2: Delete center 21 (and its bank references if any)
-- Uncomment and run ONLY after checking Step 1 results:

-- If Step 1 returns a bank row, delete in this order:
-- DELETE FROM PCARD_TASKS_EXEC_GROUP_BANK WHERE bank_code = '<bank_code_from_step1>';
-- DELETE FROM BANK_ADDENDUM WHERE bank_code = '<bank_code_from_step1>';
-- DELETE FROM BANK WHERE bank_code = '<bank_code_from_step1>';
-- DELETE FROM CENTER WHERE CENTER_CODE = '21';
-- COMMIT;

-- If Step 1 returns NO rows, just delete the center:
-- DELETE FROM CENTER WHERE CENTER_CODE = '21';
-- COMMIT;
