-- QUESTION: Which medications are most common among diabetic patients?
-- Counted by number of different diabetic patients who ever received each drug.
-- The last column shows how many of those prescriptions list diabetes as the reason,
-- which separates diabetes drugs from everything else these patients take.

WITH diabetic AS (
    SELECT DISTINCT PATIENT
    FROM conditions
    WHERE DESCRIPTION LIKE '%diabetes mellitus%'
)
SELECT
    m.DESCRIPTION AS medication,
    COUNT(DISTINCT m.PATIENT) AS diabetic_patients,
    COUNT(*) AS prescriptions,
    SUM(CASE WHEN m.REASONDESCRIPTION LIKE '%diabetes%' THEN 1 ELSE 0 END)
        AS prescriptions_for_diabetes
FROM medications AS m
JOIN diabetic AS d ON d.PATIENT = m.PATIENT
GROUP BY m.DESCRIPTION
ORDER BY diabetic_patients DESC, prescriptions DESC, medication
LIMIT 10;
