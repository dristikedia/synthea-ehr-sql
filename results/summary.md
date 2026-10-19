# Results summary

Generated automatically by src/03_run_queries.py on 2026-10-17.
Data file SHA-256: d61417b551e5b0997c33851b339c157421751f0ea68c18ea686ceb1850907c35

## Key numbers

- The data holds 108 synthetic patients (51 female, 57 male, 9 deceased); the last encounter is dated 2026-08-16.
- 8 of 108 patients (7.4%) have a diabetes diagnosis and 34 (31.5%) have prediabetes.
- Gum disease is recorded for 8 of 8 diabetic patients (100.0%) versus 80 of 100 other patients (80.0%). Tooth loss: 37.5% versus 7.0%.
- Among 7 diabetic patients with an HbA1c result, the average latest value is 4.36%; the number at or above 6.5% is 1 and the number below 4.0% is 3 (values that low are rare in real patients).
- The most common encounter class is ambulatory (2939 encounters, 52.8% of all encounters).

## 01_patient_overview

How many patients are in the data, and what do they look like?

| total_patients | living_patients | deceased_patients | female_patients | male_patients | avg_age_living_years | snapshot_date |
| --- | --- | --- | --- | --- | --- | --- |
| 108 | 99 | 9 | 51 | 57 | 37.4 | 2026-08-16 |

## 02_diabetes_prevalence

What share of patients have ever had a diabetes diagnosis?

| total_patients | diabetic_patients | diabetes_pct | prediabetic_patients | prediabetes_pct |
| --- | --- | --- | --- | --- |
| 108 | 8 | 7.4 | 34 | 31.5 |

## 03_diabetes_by_age_group

How does diabetes prevalence change with age?

| age_group | patients | diabetic_patients | diabetes_pct |
| --- | --- | --- | --- |
| 0-17 | 22 | 0 | 0.0 |
| 18-39 | 38 | 1 | 2.6 |
| 40-64 | 38 | 4 | 10.5 |
| 65+ | 10 | 3 | 30.0 |

## 04_visit_frequency

How often do patients visit? (all encounters over each patient's record)

| visit_bucket | patients | pct_of_patients | min_visits | max_visits |
| --- | --- | --- | --- | --- |
| 2) 1-10 visits | 3 | 2.8 | 2 | 10 |
| 3) 11-25 visits | 27 | 25.0 | 12 | 25 |
| 4) 26-50 visits | 45 | 41.7 | 26 | 50 |
| 5) 51-100 visits | 25 | 23.1 | 51 | 94 |
| 6) 101+ visits | 8 | 7.4 | 104 | 565 |

## 05_encounters_per_year

How many encounters happen per year over the last 11 calendar years?

| year | encounters | patients_seen | visits_per_patient_seen | is_partial_year |
| --- | --- | --- | --- | --- |
| 2016 | 198 | 74 | 2.7 | 0 |
| 2017 | 317 | 88 | 3.6 | 0 |
| 2018 | 338 | 82 | 4.1 | 0 |
| 2019 | 362 | 87 | 4.2 | 0 |
| 2020 | 431 | 92 | 4.7 | 0 |
| 2021 | 561 | 92 | 6.1 | 0 |
| 2022 | 539 | 87 | 6.2 | 0 |
| 2023 | 526 | 92 | 5.7 | 0 |
| 2024 | 521 | 92 | 5.7 | 0 |
| 2025 | 523 | 90 | 5.8 | 0 |
| 2026 | 351 | 80 | 4.4 | 1 |

## 06_encounter_types

What kinds of encounters make up the record?

| encounter_class | encounters | patients | pct_of_encounters |
| --- | --- | --- | --- |
| ambulatory | 2939 | 106 | 52.8 |
| wellness | 1262 | 108 | 22.7 |
| outpatient | 759 | 101 | 13.6 |
| emergency | 270 | 83 | 4.8 |
| urgentcare | 195 | 35 | 3.5 |
| home | 63 | 3 | 1.1 |
| inpatient | 58 | 33 | 1.0 |
| snf | 9 | 7 | 0.2 |
| hospice | 8 | 8 | 0.1 |
| virtual | 8 | 6 | 0.1 |

## 07_encounter_types_by_age_group

Do children, adults, and older adults use different kinds of care?

| age_group | encounter_class | encounters | pct_within_age_group |
| --- | --- | --- | --- |
| 0-17 | ambulatory | 545 | 50.0 |
| 0-17 | wellness | 393 | 36.1 |
| 0-17 | outpatient | 93 | 8.5 |
| 0-17 | emergency | 37 | 3.4 |
| 0-17 | urgentcare | 14 | 1.3 |
| 0-17 | inpatient | 4 | 0.4 |
| 0-17 | hospice | 1 | 0.1 |
| 0-17 | snf | 1 | 0.1 |
| 0-17 | virtual | 1 | 0.1 |
| 18-39 | ambulatory | 974 | 52.3 |
| 18-39 | wellness | 429 | 23.0 |
| 18-39 | outpatient | 323 | 17.3 |
| 18-39 | emergency | 92 | 4.9 |
| 18-39 | inpatient | 22 | 1.2 |
| 18-39 | urgentcare | 19 | 1.0 |
| 18-39 | hospice | 2 | 0.1 |
| 18-39 | virtual | 2 | 0.1 |
| 40-64 | ambulatory | 1050 | 56.8 |
| 40-64 | wellness | 369 | 20.0 |
| 40-64 | outpatient | 235 | 12.7 |
| 40-64 | emergency | 112 | 6.1 |
| 40-64 | urgentcare | 43 | 2.3 |
| 40-64 | inpatient | 28 | 1.5 |
| 40-64 | snf | 5 | 0.3 |
| 40-64 | virtual | 4 | 0.2 |
| 40-64 | hospice | 1 | 0.1 |
| 65+ | ambulatory | 370 | 47.9 |
| 65+ | urgentcare | 119 | 15.4 |
| 65+ | outpatient | 108 | 14.0 |
| 65+ | wellness | 71 | 9.2 |
| 65+ | home | 63 | 8.2 |
| 65+ | emergency | 29 | 3.8 |
| 65+ | hospice | 4 | 0.5 |
| 65+ | inpatient | 4 | 0.5 |
| 65+ | snf | 3 | 0.4 |
| 65+ | virtual | 1 | 0.1 |

## 08_top_medications_diabetic

Which medications are most common among diabetic patients?

| medication | diabetic_patients | prescriptions | prescriptions_for_diabetes |
| --- | --- | --- | --- |
| sodium fluoride 0.0272 MG/MG Oral Gel | 8 | 60 | 0 |
| insulin isophane  human 70 UNT/ML / insulin  regular  human 30 UNT/ML Injectable Suspension [Humulin] | 5 | 422 | 422 |
| tropicamide 5 MG/ML Ophthalmic Solution | 5 | 44 | 0 |
| Acetaminophen 325 MG Oral Tablet | 5 | 6 | 0 |
| 24 HR Metformin hydrochloride 500 MG Extended Release Oral Tablet | 4 | 218 | 218 |
| 24 HR metoprolol succinate 100 MG Extended Release Oral Tablet | 4 | 4 | 0 |
| Clopidogrel 75 MG Oral Tablet | 4 | 4 | 0 |
| Ibuprofen 200 MG Oral Tablet | 4 | 4 | 0 |
| Nitroglycerin 0.4 MG/ACTUAT Mucosal Spray | 4 | 4 | 0 |
| Simvastatin 20 MG Oral Tablet | 4 | 4 | 0 |

## 09_diabetes_comorbidities

Which other disorders are most common in diabetic patients, and how

| disorder | diabetic_patients_with_it | pct_of_diabetic | other_patients_with_it | pct_of_not_diabetic |
| --- | --- | --- | --- | --- |
| Gingivitis (disorder) | 8 | 100.0 | 76 | 76.0 |
| Anemia (disorder) | 7 | 87.5 | 32 | 32.0 |
| Metabolic syndrome X (disorder) | 7 | 87.5 | 3 | 3.0 |
| Viral sinusitis (disorder) | 6 | 75.0 | 65 | 65.0 |
| Gingival disease (disorder) | 6 | 75.0 | 45 | 45.0 |
| Chronic kidney disease stage 1 (disorder) | 6 | 75.0 | 0 | 0.0 |
| Acute bronchitis (disorder) | 5 | 62.5 | 36 | 36.0 |
| Primary dental caries (disorder) | 5 | 62.5 | 33 | 33.0 |
| Hypertriglyceridemia (disorder) | 5 | 62.5 | 0 | 0.0 |
| Essential hypertension (disorder) | 4 | 50.0 | 16 | 16.0 |

## 10_latest_hba1c

What does the most recent HbA1c look like for diabetic and other patients?

| patient_group | patients_tested | avg_latest_hba1c | at_or_above_6_5 | between_5_7_and_6_4 | below_4_0 |
| --- | --- | --- | --- | --- | --- |
| Diabetic | 7 | 4.36 | 1 | 1 | 3 |
| Not diabetic | 32 | 6.07 | 0 | 30 | 0 |

## 11_oral_conditions_by_diabetes

Are gum disease, caries, and tooth loss recorded more often in diabetic patients?

| patient_group | patients | with_gum_disease | gum_disease_pct | with_caries | caries_pct | with_tooth_loss | tooth_loss_pct |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Diabetic | 8 | 8 | 100.0 | 5 | 62.5 | 3 | 37.5 |
| Not diabetic | 100 | 80 | 80.0 | 33 | 33.0 | 7 | 7.0 |

## 12_dental_visits_by_age_group

Which age groups have dental-related encounters in the record?

| age_group | patients | patients_with_dental_encounter | pct_with_dental_encounter | dental_encounters |
| --- | --- | --- | --- | --- |
| 0-17 | 22 | 18 | 81.8 | 67 |
| 18-39 | 38 | 37 | 97.4 | 153 |
| 40-64 | 38 | 37 | 97.4 | 212 |
| 65+ | 10 | 10 | 100.0 | 121 |
