-- QUESTION: How does diabetes prevalence change with age?
-- Age is measured on the snapshot date for living patients and on the date of
-- death for deceased patients.

WITH snapshot AS (
    SELECT MAX(substr(START, 1, 10)) AS snapshot_date
    FROM encounters
),
diabetic AS (
    SELECT DISTINCT PATIENT
    FROM conditions
    WHERE DESCRIPTION LIKE '%diabetes mellitus%'
),
patient_ages AS (
    SELECT
        p.Id AS patient_id,
        (julianday(COALESCE(p.DEATHDATE, s.snapshot_date)) - julianday(p.BIRTHDATE)) / 365.25 AS age
    FROM patients AS p
    CROSS JOIN snapshot AS s
),
grouped AS (
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
    COUNT(d.PATIENT) AS diabetic_patients,
    ROUND(100.0 * COUNT(d.PATIENT) / COUNT(*), 1) AS diabetes_pct
FROM grouped AS g
LEFT JOIN diabetic AS d ON d.PATIENT = g.patient_id
GROUP BY g.age_group
ORDER BY g.age_group;
