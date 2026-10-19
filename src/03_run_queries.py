"""Run every SQL file in sql/ and save each result as a CSV table, plus a summary.

Run from the project folder:
    python src/03_run_queries.py
"""

import hashlib
import sqlite3
import sys
from datetime import date
from pathlib import Path

import pandas as pd

# SETTINGS
PROJECT_DIR = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_DIR / "data" / "synthea.db"
SQL_DIR = PROJECT_DIR / "sql"
TABLES_DIR = PROJECT_DIR / "results" / "tables"
SUMMARY_PATH = PROJECT_DIR / "results" / "summary.md"
ZIP_PATH = PROJECT_DIR / "data" / "raw" / "synthea_sample_data_csv_latest.zip"


def list_sql_files(sql_dir):
    """Return the .sql files sorted by name, so 01 runs before 02."""
    return sorted(Path(sql_dir).glob("*.sql"))


def run_query_file(connection, sql_path):
    """Run one SQL file and return the result as a DataFrame."""
    query = Path(sql_path).read_text(encoding="utf-8")
    return pd.read_sql_query(query, connection)


def first_comment_line(sql_path):
    """Return the QUESTION line at the top of a SQL file, used as a heading."""
    for line in Path(sql_path).read_text(encoding="utf-8").splitlines():
        if line.startswith("-- QUESTION:"):
            return line.replace("-- QUESTION:", "").strip()
    return Path(sql_path).stem


def to_markdown_table(df):
    """Turn a DataFrame into a simple Markdown table (no extra packages needed)."""
    if df.empty:
        return "_No rows returned._"
    header = "| " + " | ".join(str(c) for c in df.columns) + " |"
    divider = "| " + " | ".join("---" for _ in df.columns) + " |"
    rows = []
    # ASTYPE(OBJECT) KEEPS WHOLE NUMBERS LOOKING LIKE 8 INSTEAD OF 8.0
    for row in df.astype(object).values.tolist():
        cells = ["" if pd.isna(value) else str(value) for value in row]
        rows.append("| " + " | ".join(cells) + " |")
    return "\n".join([header, divider] + rows)


def file_sha256(path):
    """Fingerprint a file so anyone can check they used the same data."""
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        chunk = f.read(1024 * 1024)
        while chunk:
            digest.update(chunk)
            chunk = f.read(1024 * 1024)
    return digest.hexdigest()


def key_findings(results):
    """Build plain-language sentences from the result tables.

    .at[row, column] reads one cell and keeps its original type (8 stays 8, not 8.0).
    """
    lines = []
    overview = results["01_patient_overview"]
    lines.append(
        f"The data holds {overview.at[0, 'total_patients']} synthetic patients "
        f"({overview.at[0, 'female_patients']} female, {overview.at[0, 'male_patients']} male, "
        f"{overview.at[0, 'deceased_patients']} deceased); "
        f"the last encounter is dated {overview.at[0, 'snapshot_date']}."
    )

    prevalence = results["02_diabetes_prevalence"]
    lines.append(
        f"{prevalence.at[0, 'diabetic_patients']} of {prevalence.at[0, 'total_patients']} patients "
        f"({prevalence.at[0, 'diabetes_pct']}%) have a diabetes diagnosis and "
        f"{prevalence.at[0, 'prediabetic_patients']} ({prevalence.at[0, 'prediabetes_pct']}%) have prediabetes."
    )

    oral = results["11_oral_conditions_by_diabetes"].set_index("patient_group")
    if "Diabetic" in oral.index and "Not diabetic" in oral.index:
        lines.append(
            f"Gum disease is recorded for {oral.at['Diabetic', 'with_gum_disease']} of "
            f"{oral.at['Diabetic', 'patients']} diabetic patients ({oral.at['Diabetic', 'gum_disease_pct']}%) "
            f"versus {oral.at['Not diabetic', 'with_gum_disease']} of {oral.at['Not diabetic', 'patients']} "
            f"other patients ({oral.at['Not diabetic', 'gum_disease_pct']}%). Tooth loss: "
            f"{oral.at['Diabetic', 'tooth_loss_pct']}% versus {oral.at['Not diabetic', 'tooth_loss_pct']}%."
        )

    hba1c = results["10_latest_hba1c"].set_index("patient_group")
    if "Diabetic" in hba1c.index:
        lines.append(
            f"Among {hba1c.at['Diabetic', 'patients_tested']} diabetic patients with an HbA1c result, "
            f"the average latest value is {hba1c.at['Diabetic', 'avg_latest_hba1c']}%; "
            f"the number at or above 6.5% is {hba1c.at['Diabetic', 'at_or_above_6_5']} and "
            f"the number below 4.0% is {hba1c.at['Diabetic', 'below_4_0']} "
            f"(values that low are rare in real patients)."
        )

    types = results["06_encounter_types"]
    lines.append(
        f"The most common encounter class is {types.at[0, 'encounter_class']} "
        f"({types.at[0, 'encounters']} encounters, {types.at[0, 'pct_of_encounters']}% of all encounters)."
    )
    return lines


def write_summary(results, questions, summary_path, data_fingerprint):
    """Write results/summary.md with key findings and every result table."""
    parts = [
        "# Results summary",
        "",
        f"Generated automatically by src/03_run_queries.py on {date.today().isoformat()}.",
        f"Data file SHA-256: {data_fingerprint}",
        "",
        "## Key numbers",
        "",
    ]
    parts += [f"- {line}" for line in key_findings(results)]
    parts.append("")
    for name, df in results.items():
        parts += [f"## {name}", "", questions[name], "", to_markdown_table(df), ""]
    Path(summary_path).parent.mkdir(parents=True, exist_ok=True)
    Path(summary_path).write_text("\n".join(parts), encoding="utf-8")


def main():
    # CHECK THE DATABASE EXISTS
    if not DB_PATH.exists():
        print(f"ERROR: database not found at {DB_PATH}")
        print("Fix: run  python src/01_download_data.py  then  python src/02_load_to_sqlite.py")
        sys.exit(1)

    sql_files = list_sql_files(SQL_DIR)
    if not sql_files:
        print(f"ERROR: no .sql files found in {SQL_DIR}")
        sys.exit(1)

    # RUN EACH QUERY AND SAVE ITS TABLE
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    results = {}
    questions = {}
    connection = sqlite3.connect(DB_PATH)
    try:
        for sql_path in sql_files:
            name = sql_path.stem
            df = run_query_file(connection, sql_path)
            df.to_csv(TABLES_DIR / f"{name}.csv", index=False)
            results[name] = df
            questions[name] = first_comment_line(sql_path)
            print(f"{name}: {len(df)} rows")
    finally:
        connection.close()

    # WRITE THE SUMMARY
    fingerprint = file_sha256(ZIP_PATH) if ZIP_PATH.exists() else "zip file not found"
    write_summary(results, questions, SUMMARY_PATH, fingerprint)
    print(f"Summary written to {SUMMARY_PATH.relative_to(PROJECT_DIR)}")


if __name__ == "__main__":
    main()
