-- QUESTION: Are gum disease, caries, and tooth loss recorded more often in diabetic patients?
-- Gum disease = any description containing "gingiv" or "periodont".
-- Small groups: read the percentages together with the patient counts.

WITH diabetic AS (
    SELECT DISTINCT PATIENT
    FROM conditions
    WHERE DESCRIPTION LIKE '%diabetes mellitus%'
),
oral AS (
    SELECT
        PATIENT,
        MAX(CASE WHEN DESCRIPTION LIKE '%gingiv%' OR DESCRIPTION LIKE '%periodont%' THEN 1 ELSE 0 END)
            AS has_gum_disease,
        MAX(CASE WHEN DESCRIPTION LIKE '%dental caries%' THEN 1 ELSE 0 END) AS has_caries,
        MAX(CASE WHEN DESCRIPTION LIKE '%loss of teeth%' THEN 1 ELSE 0 END) AS has_tooth_loss
    FROM conditions
    GROUP BY PATIENT
)
SELECT
    CASE WHEN d.PATIENT IS NOT NULL THEN 'Diabetic' ELSE 'Not diabetic' END AS patient_group,
    COUNT(*) AS patients,
    SUM(COALESCE(o.has_gum_disease, 0)) AS with_gum_disease,
    ROUND(100.0 * SUM(COALESCE(o.has_gum_disease, 0)) / COUNT(*), 1) AS gum_disease_pct,
    SUM(COALESCE(o.has_caries, 0)) AS with_caries,
    ROUND(100.0 * SUM(COALESCE(o.has_caries, 0)) / COUNT(*), 1) AS caries_pct,
    SUM(COALESCE(o.has_tooth_loss, 0)) AS with_tooth_loss,
    ROUND(100.0 * SUM(COALESCE(o.has_tooth_loss, 0)) / COUNT(*), 1) AS tooth_loss_pct
FROM patients AS p
LEFT JOIN diabetic AS d ON d.PATIENT = p.Id
LEFT JOIN oral AS o ON o.PATIENT = p.Id
GROUP BY patient_group
ORDER BY patient_group;
