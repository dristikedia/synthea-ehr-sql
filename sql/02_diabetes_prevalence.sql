-- QUESTION: What share of patients have ever had a diabetes diagnosis?
-- Diabetes = any condition whose description contains "diabetes mellitus".
-- This catches type 2 diabetes and its complications (for example diabetic
-- neuropathy) but not prediabetes, which is counted separately.

WITH diabetic AS (
    SELECT DISTINCT PATIENT
    FROM conditions
    WHERE DESCRIPTION LIKE '%diabetes mellitus%'
),
prediabetic AS (
    SELECT DISTINCT PATIENT
    FROM conditions
    WHERE DESCRIPTION LIKE 'Prediabetes%'
)
SELECT
    (SELECT COUNT(*) FROM patients) AS total_patients,
    (SELECT COUNT(*) FROM diabetic) AS diabetic_patients,
    ROUND(100.0 * (SELECT COUNT(*) FROM diabetic) / (SELECT COUNT(*) FROM patients), 1)
        AS diabetes_pct,
    (SELECT COUNT(*) FROM prediabetic) AS prediabetic_patients,
    ROUND(100.0 * (SELECT COUNT(*) FROM prediabetic) / (SELECT COUNT(*) FROM patients), 1)
        AS prediabetes_pct;
