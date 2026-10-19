-- QUESTION: How many patients are in the data, and what do they look like?
-- The "snapshot date" is the last encounter date in the data. Using it instead of
-- today's date keeps the ages the same every time the query is run.

WITH snapshot AS (
    SELECT MAX(substr(START, 1, 10)) AS snapshot_date
    FROM encounters
)
SELECT
    COUNT(*) AS total_patients,
    SUM(CASE WHEN DEATHDATE IS NULL THEN 1 ELSE 0 END) AS living_patients,
    SUM(CASE WHEN DEATHDATE IS NOT NULL THEN 1 ELSE 0 END) AS deceased_patients,
    SUM(CASE WHEN GENDER = 'F' THEN 1 ELSE 0 END) AS female_patients,
    SUM(CASE WHEN GENDER = 'M' THEN 1 ELSE 0 END) AS male_patients,
    -- AGE OF LIVING PATIENTS ON THE SNAPSHOT DATE
    ROUND(AVG(CASE WHEN DEATHDATE IS NULL
                   THEN (julianday(snapshot_date) - julianday(BIRTHDATE)) / 365.25 END), 1)
        AS avg_age_living_years,
    snapshot_date
FROM patients
CROSS JOIN snapshot;
