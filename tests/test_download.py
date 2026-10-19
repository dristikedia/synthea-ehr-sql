import zipfile
from types import SimpleNamespace

import pytest
import requests

from conftest import load_script

download = load_script("01_download_data.py")


# FINDING FILES INSIDE THE ZIP
def test_find_member_at_top_level():
    assert download.find_member(["patients.csv", "encounters.csv"], "patients") == "patients.csv"


def test_find_member_inside_folder():
    names = ["csv/patients.csv", "csv/encounters.csv"]
    assert download.find_member(names, "encounters") == "csv/encounters.csv"


def test_find_member_does_not_match_similar_names():
    assert download.find_member(["my_patients.csv"], "patients") is None


# UNZIPPING
def test_extract_tables_writes_requested_files(tmp_path):
    zip_path = tmp_path / "data.zip"
    with zipfile.ZipFile(zip_path, "w") as archive:
        archive.writestr("csv/patients.csv", "Id\np1\n")
        archive.writestr("csv/encounters.csv", "Id\ne1\n")
        archive.writestr("csv/claims.csv", "Id\nc1\n")
    out_dir = tmp_path / "out"
    files = download.extract_tables(zip_path, out_dir, ["patients", "encounters"])
    assert sorted(p.name for p in files) == ["encounters.csv", "patients.csv"]
    assert (out_dir / "patients.csv").read_text() == "Id\np1\n"
    assert not (out_dir / "claims.csv").exists()


def test_extract_tables_missing_table_raises(tmp_path):
    zip_path = tmp_path / "data.zip"
    with zipfile.ZipFile(zip_path, "w") as archive:
        archive.writestr("patients.csv", "Id\np1\n")
    with pytest.raises(RuntimeError, match="does not contain encounters.csv"):
        download.extract_tables(zip_path, tmp_path / "out", ["patients", "encounters"])


def test_extract_tables_rejects_broken_zip(tmp_path):
    bad = tmp_path / "broken.zip"
    bad.write_text("this is not a zip file")
    with pytest.raises(RuntimeError, match="not a valid zip"):
        download.extract_tables(bad, tmp_path / "out", ["patients"])


# DOWNLOADING WITH RETRIES (THE NETWORK IS REPLACED BY FAKE FUNCTIONS)
def fake_response(status_code, body=b""):
    """A stand-in for a requests response: a status code and the body in one chunk."""
    return SimpleNamespace(status_code=status_code, iter_content=lambda chunk_size: [body])


def test_download_retries_then_succeeds(tmp_path, monkeypatch):
    calls = []

    def fake_get(url, stream, timeout):
        calls.append(url)
        if len(calls) == 1:
            raise requests.ConnectionError("network down")
        return fake_response(200, b"zip-bytes")

    monkeypatch.setattr(download.requests, "get", fake_get)
    target = tmp_path / "file.zip"
    download.download_file("http://example.test/file.zip", target, attempts=3, wait_seconds=0)
    assert target.read_bytes() == b"zip-bytes"
    assert len(calls) == 2


def test_download_gives_clear_error_after_all_attempts(tmp_path, monkeypatch):
    monkeypatch.setattr(download.requests, "get", lambda url, stream, timeout: fake_response(404))
    target = tmp_path / "file.zip"
    with pytest.raises(RuntimeError, match="after 3 attempts.*HTTP status 404"):
        download.download_file("http://example.test/file.zip", target, attempts=3, wait_seconds=0)
    assert not target.exists()
    assert not (tmp_path / "file.zip.part").exists()
