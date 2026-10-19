"""Download the Synthea sample CSV data and unzip the tables this project uses.

Run from the project folder:
    python src/01_download_data.py
"""

import sys
import time
import zipfile
from pathlib import Path

import requests

# SETTINGS
PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_DIR / "data" / "raw"
ZIP_PATH = RAW_DIR / "synthea_sample_data_csv_latest.zip"
CSV_DIR = RAW_DIR / "csv"
DATA_URL = (
    "https://github.com/synthetichealth/synthea-sample-data/raw/main/"
    "downloads/latest/synthea_sample_data_csv_latest.zip"
)
TABLES = ["patients", "encounters", "conditions", "medications", "observations"]


def download_file(url, destination, attempts=3, wait_seconds=5, timeout=120):
    """Download a URL to a file, retrying a few times if the network fails."""
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temp_path = destination.with_name(destination.name + ".part")
    last_error = ""

    for attempt in range(1, attempts + 1):
        try:
            print(f"Downloading (attempt {attempt} of {attempts}): {url}")
            response = requests.get(url, stream=True, timeout=timeout)
            if response.status_code != 200:
                last_error = f"server answered with HTTP status {response.status_code}"
            else:
                # WRITE IN CHUNKS SO LARGE FILES DO NOT FILL MEMORY
                with open(temp_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=1024 * 1024):
                        f.write(chunk)
                temp_path.replace(destination)
                return destination
        except requests.RequestException as error:
            last_error = str(error)

        print(f"  Failed: {last_error}")
        if attempt < attempts:
            time.sleep(wait_seconds)

    if temp_path.exists():
        temp_path.unlink()
    raise RuntimeError(f"Could not download {url} after {attempts} attempts. Last error: {last_error}")


def find_member(zip_names, table):
    """Find the zip entry for a table, whether or not it sits inside a folder."""
    wanted = f"{table}.csv"
    for name in zip_names:
        if name == wanted or name.endswith("/" + wanted):
            return name
    return None


def extract_tables(zip_path, output_dir, tables):
    """Unzip only the CSV tables we need into output_dir."""
    zip_path = Path(zip_path)
    output_dir = Path(output_dir)
    if not zipfile.is_zipfile(zip_path):
        raise RuntimeError(f"{zip_path} is not a valid zip file. Delete it and run this script again.")

    output_dir.mkdir(parents=True, exist_ok=True)
    extracted = []
    with zipfile.ZipFile(zip_path) as archive:
        names = archive.namelist()
        for table in tables:
            member = find_member(names, table)
            if member is None:
                raise RuntimeError(f"The zip file does not contain {table}.csv. Found: {names}")
            target = output_dir / f"{table}.csv"
            with archive.open(member) as source, open(target, "wb") as out:
                out.write(source.read())
            extracted.append(target)
    return extracted


def main():
    # DOWNLOAD ONLY IF WE DO NOT ALREADY HAVE A GOOD COPY
    if ZIP_PATH.exists() and zipfile.is_zipfile(ZIP_PATH):
        print(f"Zip already present: {ZIP_PATH}")
    else:
        try:
            download_file(DATA_URL, ZIP_PATH)
        except RuntimeError as error:
            print(f"ERROR: {error}")
            print("Fix: check your internet connection, or download the file by hand from")
            print("  https://github.com/synthetichealth/synthea-sample-data/tree/main/downloads/latest")
            print(f"and save it as {ZIP_PATH}")
            sys.exit(1)

    # UNZIP THE TABLES WE USE
    try:
        files = extract_tables(ZIP_PATH, CSV_DIR, TABLES)
    except RuntimeError as error:
        print(f"ERROR: {error}")
        sys.exit(1)

    for path in files:
        print(f"Ready: {path.relative_to(PROJECT_DIR)}")


if __name__ == "__main__":
    main()
