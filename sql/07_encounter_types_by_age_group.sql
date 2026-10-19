-- QUESTION: Do children, adults, and older adults use different kinds of care?
-- Age is the patient's age on the day of each encounter.
-- Percent is within each age group, so each age group adds up to 100.

WITH encounter_ages AS (
    SELECT
        e.ENCOUNTERCLASS AS encounter_class,
        (julianday(substr(e.START, 1, 10)) - julianday(p.BIRTHDATE)) / 365.25 AS age
    FROM encounters AS e
    JOIN patients AS p ON p.Id = e.PATIENT
),
grouped AS (
    SELECT
        encounter_class,
        CASE
            WHEN age < 18 THEN '0-17'
            WHEN age < 40 THEN '18-39'
            WHEN age < 65 THEN '40-64'
            ELSE '65+'
        END AS age_group
    FROM encounter_ages
),
group_totals AS (
    SELECT age_group, COUNT(*) AS total
    FROM grouped
    GROUP BY age_group
)
SELECT
    g.age_group,
    g.encounter_class,
    COUNT(*) AS encounters,
    ROUND(100.0 * COUNT(*) / t.total, 1) AS pct_within_age_group
FROM grouped AS g
JOIN group_totals AS t ON t.age_group = g.age_group
GROUP BY g.age_group, g.encounter_class
ORDER BY g.age_group, encounters DESC, g.encounter_class;
