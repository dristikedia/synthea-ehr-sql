-- QUESTION: How often do patients visit? (all encounters over each patient's record)
-- LEFT JOIN keeps patients with zero encounters so nobody silently disappears.

WITH visits_per_patient AS (
    SELECT
        p.Id AS patient_id,
        COUNT(e.Id) AS visits
    FROM patients AS p
    LEFT JOIN encounters AS e ON e.PATIENT = p.Id
    GROUP BY p.Id
),
bucketed AS (
    SELECT
        visits,
        CASE
            WHEN visits = 0 THEN '1) 0 visits'
            WHEN visits <= 10 THEN '2) 1-10 visits'
            WHEN visits <= 25 THEN '3) 11-25 visits'
            WHEN visits <= 50 THEN '4) 26-50 visits'
            WHEN visits <= 100 THEN '5) 51-100 visits'
            ELSE '6) 101+ visits'
        END AS visit_bucket
    FROM visits_per_patient
)
SELECT
    visit_bucket,
    COUNT(*) AS patients,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM patients), 1) AS pct_of_patients,
    MIN(visits) AS min_visits,
    MAX(visits) AS max_visits
FROM bucketed
GROUP BY visit_bucket
ORDER BY visit_bucket;
