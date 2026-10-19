import sqlite3

import pandas as pd
import pytest

from conftest import load_script

loader = load_script("02_load_to_sqlite.py")
TABLES = ["patients", "encounters", "conditions", "medications", "observations"]


def test_check_csv_files_reports_missing(tmp_path):
    (tmp_path / "patients.csv").write_text("Id\np1\n")
    assert loader.check_csv_files(tmp_path, ["patients", "encounters"]) == ["encounters.csv"]


def test_check_csv_files_all_present(fixtures_dir):
    assert loader.check_csv_files(fixtures_dir, TABLES) == []


def test_load_tables_row_counts(fixtures_dir, tmp_path):
    db = tmp_path / "test.db"
    counts = loader.load_tables(fixtures_dir, db, TABLES)
    assert counts == {"patients": 4, "encounters": 6, "conditions": 7, "medications": 4, "observations": 5}


def test_empty_cells_become_null(fixtures_dir, tmp_path):
    db = tmp_path / "test.db"
    loader.load_tables(fixtures_dir, db, TABLES)
    connection = sqlite3.connect(db)
    living = connection.execute("SELECT COUNT(*) FROM patients WHERE DEATHDATE IS NULL").fetchone()[0]
    connection.close()
    assert living == 3


def test_codes_keep_text_type(fixtures_dir, tmp_path):
    db = tmp_path / "test.db"
    loader.load_tables(fixtures_dir, db, TABLES)
    connection = sqlite3.connect(db)
    code_type = connection.execute("SELECT typeof(CODE) FROM observations LIMIT 1").fetchone()[0]
    connection.close()
    assert code_type == "text"


def test_convert_number_columns():
    df = pd.DataFrame({"HEALTHCARE_EXPENSES": ["10.5", "", "abc"], "Id": ["a", "b", "c"]})
    out = loader.convert_number_columns(df)
    assert out["HEALTHCARE_EXPENSES"].iloc[0] == 10.5
    assert out["HEALTHCARE_EXPENSES"].isna().sum() == 2
    assert out["Id"].tolist() == ["a", "b", "c"]


def test_main_exits_with_message_when_csvs_missing(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(loader, "CSV_DIR", tmp_path)
    with pytest.raises(SystemExit):
        loader.main()
    assert "run  python src/01_download_data.py  first" in capsys.readouterr().out
