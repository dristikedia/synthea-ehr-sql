"""Load the Synthea CSV tables into one SQLite database file.

Run from the project folder:
    python src/02_load_to_sqlite.py
"""

import sqlite3
import sys
from pathlib import Path

import pandas as pd

# SETTINGS
PROJECT_DIR = Path(__file__).resolve().parent.parent
CSV_DIR = PROJECT_DIR / "data" / "raw" / "csv"
DB_PATH = PROJECT_DIR / "data" / "synthea.db"
TABLES = ["patients", "encounters", "conditions", "medications", "observations"]

# INDEXES MAKE JOINS ON PATIENT IDS FAST
INDEXES = {
    "encounters": "CREATE INDEX IF NOT EXISTS idx_encounters_patient ON encounters (PATIENT)",
    "conditions": "CREATE INDEX IF NOT EXISTS idx_conditions_patient ON conditions (PATIENT)",
    "medications": "CREATE INDEX IF NOT EXISTS idx_medications_patient ON medications (PATIENT)",
    "observations": "CREATE INDEX IF NOT EXISTS idx_observations_patient_code ON observations (PATIENT, CODE)",
}


def check_csv_files(csv_dir, tables):
    """Return a list of CSV files that are missing."""
    return [f"{table}.csv" for table in tables if not (Path(csv_dir) / f"{table}.csv").exists()]


def load_tables(csv_dir, db_path, tables):
    """Read each CSV with pandas and write it into SQLite. Returns row counts."""
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    row_counts = {}

    connection = sqlite3.connect(db_path)
    try:
        for table in tables:
            # READ EVERY COLUMN AS TEXT FIRST SO CODES LIKE "0123" KEEP THEIR ZEROS
            df = pd.read_csv(Path(csv_dir) / f"{table}.csv", dtype=str)
            df = convert_number_columns(df)
            df.to_sql(table, connection, if_exists="replace", index=False)
            row_counts[table] = len(df)

        for table in tables:
            if table in INDEXES:
                connection.execute(INDEXES[table])
        connection.commit()
    finally:
        connection.close()
    return row_counts


def convert_number_columns(df):
    """Turn known money and value columns into numbers. Other columns stay text."""
    number_columns = [
        "HEALTHCARE_EXPENSES", "HEALTHCARE_COVERAGE", "INCOME",
        "BASE_ENCOUNTER_COST", "TOTAL_CLAIM_COST", "PAYER_COVERAGE",
        "BASE_COST", "DISPENSES", "TOTALCOST",
    ]
    for column in number_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")
    return df


def main():
    # CHECK THE INPUT FILES FIRST
    missing = check_csv_files(CSV_DIR, TABLES)
    if missing:
        print(f"ERROR: missing CSV files in {CSV_DIR}: {', '.join(missing)}")
        print("Fix: run  python src/01_download_data.py  first.")
        sys.exit(1)

    # LOAD
    counts = load_tables(CSV_DIR, DB_PATH, TABLES)
    for table, count in counts.items():
        print(f"{table}: {count:,} rows")
    print(f"Database written to {DB_PATH.relative_to(PROJECT_DIR)}")


if __name__ == "__main__":
    main()
