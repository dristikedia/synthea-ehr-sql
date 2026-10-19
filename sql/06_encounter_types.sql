-- QUESTION: What kinds of encounters make up the record?
-- ENCOUNTERCLASS is the care setting: wellness, ambulatory, emergency, inpatient, and so on.

SELECT
    ENCOUNTERCLASS AS encounter_class,
    COUNT(*) AS encounters,
    COUNT(DISTINCT PATIENT) AS patients,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM encounters), 1) AS pct_of_encounters
FROM encounters
GROUP BY ENCOUNTERCLASS
ORDER BY encounters DESC, encounter_class;
