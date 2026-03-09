-- ============================================================
-- ONE-TIME FIX: Move center 21 (NEPS) to code 24 (free slot)
-- so LOAD_BANK_PARAMETERS can use code 21 for new banks.
--
-- This does NOT delete any bank data — just renumbers the center.
--
-- Run in SQL Developer with F5.
-- ============================================================

-- Step 1: Copy center 21 into a temp table
CREATE TABLE tmp_center_21 AS SELECT * FROM CENTER WHERE CENTER_CODE = '21';

-- Step 2: Change the code to 24 in the temp table
UPDATE tmp_center_21 SET CENTER_CODE = '24';

-- Step 3: Insert the copy as center 24
INSERT INTO CENTER SELECT * FROM tmp_center_21;

-- Step 4: Point bank 101010 from center 21 to center 24
UPDATE BANK SET center_code = '24' WHERE center_code = '21';

-- Step 5: Delete the old center 21 (now has no FK references)
DELETE FROM CENTER WHERE CENTER_CODE = '21';

-- Step 6: Clean up temp table
DROP TABLE tmp_center_21;

-- Step 7: Commit
COMMIT;

-- Step 8: Verify
SELECT 'Center 21 gone?' AS check1, COUNT(*) AS cnt FROM CENTER WHERE CENTER_CODE = '21'
UNION ALL
SELECT 'Center 24 exists?', COUNT(*) FROM CENTER WHERE CENTER_CODE = '24'
UNION ALL
SELECT 'Bank 101010 on 24?', COUNT(*) FROM BANK WHERE bank_code = '101010' AND center_code = '24';
