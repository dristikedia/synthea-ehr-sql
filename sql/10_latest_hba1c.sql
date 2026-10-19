-- QUESTION: What does the most recent HbA1c look like for diabetic and other patients?
-- LOINC 4548-4 is Hemoglobin A1c. Values are stored as text, so CAST turns them into numbers.
-- 6.5% or higher is the usual diagnostic cut-off for diabetes; 5.7 to 6.4% is the prediabetes range.
-- Values below 4.0% are rare in real patients, so that column works as a data quality check.

WITH diabetic AS (
    SELECT DISTINCT PATIENT
    FROM conditions
    WHERE DESCRIPTION LIKE '%diabetes mellitus%'
),
latest_date AS (
    SELECT PATIENT, MAX(DATE) AS last_test_date
    FROM observations
    WHERE CODE = '4548-4'
    GROUP BY PATIENT
),
latest_value AS (
    -- AVERAGE IN CASE TWO RESULTS SHARE THE SAME TIMESTAMP
    SELECT o.PATIENT, AVG(CAST(o.VALUE AS REAL)) AS hba1c
    FROM observations AS o
    JOIN latest_date AS l
      ON l.PATIENT = o.PATIENT AND l.last_test_date = o.DATE
    WHERE o.CODE = '4548-4'
    GROUP BY o.PATIENT
)
SELECT
    CASE WHEN d.PATIENT IS NOT NULL THEN 'Diabetic' ELSE 'Not diabetic' END AS patient_group,
    COUNT(*) AS patients_tested,
    ROUND(AVG(v.hba1c), 2) AS avg_latest_hba1c,
    SUM(CASE WHEN v.hba1c >= 6.5 THEN 1 ELSE 0 END) AS at_or_above_6_5,
    SUM(CASE WHEN v.hba1c >= 5.7 AND v.hba1c < 6.5 THEN 1 ELSE 0 END) AS between_5_7_and_6_4,
    SUM(CASE WHEN v.hba1c < 4.0 THEN 1 ELSE 0 END) AS below_4_0
FROM latest_value AS v
LEFT JOIN diabetic AS d ON d.PATIENT = v.PATIENT
GROUP BY patient_group
ORDER BY patient_group;
