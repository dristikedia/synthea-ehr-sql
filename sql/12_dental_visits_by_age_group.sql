-- QUESTION: Which age groups have dental-related encounters in the record?
-- A dental-related encounter is one whose reason mentions dental care, teeth, or gingivitis.
-- Age is measured on the snapshot date (or date of death).

WITH snapshot AS (
    SELECT MAX(substr(START, 1, 10)) AS snapshot_date
    FROM encounters
),
dental_patients AS (
    SELECT PATIENT, COUNT(*) AS dental_encounters
    FROM encounters
    WHERE REASONDESCRIPTION LIKE '%dental%'
       OR REASONDESCRIPTION LIKE '%tooth%'
       OR REASONDESCRIPTION LIKE '%teeth%'
       OR REASONDESCRIPTION LIKE '%gingiv%'
    GROUP BY PATIENT
),
patient_ages AS (
    SELECT
        p.Id AS patient_id,
        (julianday(COALESCE(p.DEATHDATE, s.snapshot_date)) - julianday(p.BIRTHDATE)) / 365.25 AS age
    FROM patients AS p
    CROSS JOIN snapshot AS s
),
patient_groups AS (
    SELECT
        patient_id,
        CASE
            WHEN age < 18 THEN '0-17'
            WHEN age < 40 THEN '18-39'
            WHEN age < 65 THEN '40-64'
            ELSE '65+'
        END AS age_group
    FROM patient_ages
)
SELECT
    g.age_group,
    COUNT(*) AS patients,
    COUNT(dp.PATIENT) AS patients_with_dental_encounter,
    ROUND(100.0 * COUNT(dp.PATIENT) / COUNT(*), 1) AS pct_with_dental_encounter,
    COALESCE(SUM(dp.dental_encounters), 0) AS dental_encounters
FROM patient_groups AS g
LEFT JOIN dental_patients AS dp ON dp.PATIENT = g.patient_id
GROUP BY g.age_group
ORDER BY g.age_group;
