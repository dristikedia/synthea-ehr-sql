-- QUESTION: How many encounters happen per year over the last 11 calendar years?
-- The most recent year is usually incomplete, so it is flagged.

WITH yearly AS (
    SELECT
        CAST(substr(START, 1, 4) AS INTEGER) AS year,
        COUNT(*) AS encounters,
        COUNT(DISTINCT PATIENT) AS patients_seen
    FROM encounters
    GROUP BY year
),
last_year AS (
    SELECT MAX(year) AS max_year FROM yearly
)
SELECT
    y.year,
    y.encounters,
    y.patients_seen,
    ROUND(1.0 * y.encounters / y.patients_seen, 1) AS visits_per_patient_seen,
    CASE WHEN y.year = l.max_year THEN 1 ELSE 0 END AS is_partial_year
FROM yearly AS y
CROSS JOIN last_year AS l
WHERE y.year >= l.max_year - 10
ORDER BY y.year;
