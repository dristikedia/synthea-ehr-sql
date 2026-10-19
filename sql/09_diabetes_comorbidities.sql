-- QUESTION: Which other disorders are most common in diabetic patients, and how
-- does that compare with patients who do not have diabetes?
-- Only SNOMED "(disorder)" entries are counted, which leaves out social findings
-- such as employment status. Diabetes itself and its complications are excluded.

WITH diabetic AS (
    SELECT DISTINCT PATIENT
    FROM conditions
    WHERE DESCRIPTION LIKE '%diabetes mellitus%'
),
group_sizes AS (
    SELECT
        (SELECT COUNT(*) FROM diabetic) AS n_diabetic,
        (SELECT COUNT(*) FROM patients) - (SELECT COUNT(*) FROM diabetic) AS n_not_diabetic
),
patient_disorders AS (
    SELECT DISTINCT
        c.PATIENT,
        c.DESCRIPTION AS disorder,
        CASE WHEN d.PATIENT IS NOT NULL THEN 1 ELSE 0 END AS is_diabetic
    FROM conditions AS c
    LEFT JOIN diabetic AS d ON d.PATIENT = c.PATIENT
    WHERE c.DESCRIPTION LIKE '%(disorder)%'
      AND c.DESCRIPTION NOT LIKE '%diabet%'
)
SELECT
    disorder,
    SUM(is_diabetic) AS diabetic_patients_with_it,
    ROUND(100.0 * SUM(is_diabetic) / n_diabetic, 1) AS pct_of_diabetic,
    SUM(1 - is_diabetic) AS other_patients_with_it,
    ROUND(100.0 * SUM(1 - is_diabetic) / n_not_diabetic, 1) AS pct_of_not_diabetic
FROM patient_disorders
CROSS JOIN group_sizes
GROUP BY disorder
ORDER BY diabetic_patients_with_it DESC, pct_of_not_diabetic DESC, disorder
LIMIT 10;
