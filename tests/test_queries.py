import sqlite3

import pandas as pd
import pytest

from conftest import PROJECT_DIR, load_script

loader = load_script("02_load_to_sqlite.py")
runner = load_script("03_run_queries.py")
TABLES = ["patients", "encounters", "conditions", "medications", "observations"]


@pytest.fixture
def results(fixtures_dir, tmp_path):
    """Load the fixture data and run every SQL file against it."""
    db = tmp_path / "test.db"
    loader.load_tables(fixtures_dir, db, TABLES)
    connection = sqlite3.connect(db)
    output = {}
    for sql_path in runner.list_sql_files(PROJECT_DIR / "sql"):
        output[sql_path.stem] = runner.run_query_file(connection, sql_path)
    connection.close()
    return output


def test_there_are_twelve_queries():
    assert len(runner.list_sql_files(PROJECT_DIR / "sql")) == 12


def test_patient_overview(results):
    row = results["01_patient_overview"].iloc[0]
    assert row["total_patients"] == 4
    assert row["deceased_patients"] == 1
    assert row["snapshot_date"] == "2025-12-31"
    # AGES ON 2025-12-31: ABOUT 76.0, 35.5 AND 10.8
    assert row["avg_age_living_years"] == pytest.approx(40.8, abs=0.1)


def test_diabetes_prevalence_excludes_prediabetes(results):
    row = results["02_diabetes_prevalence"].iloc[0]
    assert row["diabetic_patients"] == 1
    assert row["diabetes_pct"] == 25.0
    assert row["prediabetic_patients"] == 1


def test_diabetes_by_age_group_uses_age_at_death(results):
    table = results["03_diabetes_by_age_group"].set_index("age_group")
    assert table.at["65+", "patients"] == 2
    assert table.at["65+", "diabetes_pct"] == 50.0
    assert table.at["0-17", "patients"] == 1


def test_visit_frequency_keeps_patients_with_no_visits(results):
    table = results["04_visit_frequency"].set_index("visit_bucket")
    assert table.at["1) 0 visits", "patients"] == 1
    assert table.at["2) 1-10 visits", "patients"] == 3
    assert table["patients"].sum() == 4


def test_last_year_is_flagged_partial(results):
    table = results["05_encounters_per_year"]
    assert table["is_partial_year"].tolist()[-1] == 1
    assert table["is_partial_year"].sum() == 1


def test_encounter_types_percent_adds_to_100(results):
    assert results["06_encounter_types"]["pct_of_encounters"].sum() == pytest.approx(100, abs=0.2)


def test_encounter_types_by_age_group_each_group_adds_to_100(results):
    sums = results["07_encounter_types_by_age_group"].groupby("age_group")["pct_within_age_group"].sum()
    for value in sums:
        assert value == pytest.approx(100, abs=0.2)


def test_top_medications_only_diabetic_patients(results):
    table = results["08_top_medications_diabetic"].set_index("medication")
    metformin = "24 HR Metformin hydrochloride 500 MG Extended Release Oral Tablet"
    assert table.at[metformin, "prescriptions"] == 2
    assert table.at[metformin, "prescriptions_for_diabetes"] == 2
    # IBUPROFEN: P2 ALSO TOOK IT, BUT P2 IS NOT DIABETIC, SO ONLY ONE PRESCRIPTION COUNTS
    assert table.at["Ibuprofen 200 MG Oral Tablet", "prescriptions"] == 1


def test_comorbidities_count_each_patient_once(results):
    table = results["09_diabetes_comorbidities"].set_index("disorder")
    assert table.at["Essential hypertension (disorder)", "diabetic_patients_with_it"] == 1
    assert table.at["Gingivitis (disorder)", "pct_of_not_diabetic"] == pytest.approx(33.3)
    assert not table.index.str.contains("iabet").any()


def test_latest_hba1c_uses_most_recent_value(results):
    table = results["10_latest_hba1c"].set_index("patient_group")
    assert table.at["Diabetic", "avg_latest_hba1c"] == 6.8
    assert table.at["Diabetic", "at_or_above_6_5"] == 1
    assert table.at["Not diabetic", "between_5_7_and_6_4"] == 1
    assert table.at["Not diabetic", "below_4_0"] == 0


def test_oral_conditions_by_diabetes(results):
    table = results["11_oral_conditions_by_diabetes"].set_index("patient_group")
    assert table.at["Diabetic", "gum_disease_pct"] == 100.0
    assert table.at["Not diabetic", "patients"] == 3
    assert table.at["Not diabetic", "with_caries"] == 1


def test_dental_visits_by_age_group(results):
    table = results["12_dental_visits_by_age_group"].set_index("age_group")
    assert table.at["65+", "patients_with_dental_encounter"] == 1
    assert table.at["18-39", "dental_encounters"] == 1
    assert table.at["0-17", "patients_with_dental_encounter"] == 0


def test_markdown_table_keeps_whole_numbers():
    df = pd.DataFrame({"count": [8], "pct": [7.4]})
    text = runner.to_markdown_table(df)
    assert "| 8 | 7.4 |" in text


def test_markdown_table_empty():
    assert runner.to_markdown_table(pd.DataFrame()) == "_No rows returned._"


def test_summary_is_written(results, tmp_path):
    questions = {name: name for name in results}
    path = tmp_path / "summary.md"
    runner.write_summary(results, questions, path, "abc123")
    text = path.read_text()
    assert "1 of 4 patients (25.0%) have a diabetes diagnosis" in text
    assert "abc123" in text


def test_main_exits_with_message_when_database_missing(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(runner, "DB_PATH", tmp_path / "missing.db")
    with pytest.raises(SystemExit):
        runner.main()
    assert "database not found" in capsys.readouterr().out
