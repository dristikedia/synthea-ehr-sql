import pandas as pd
import pytest

from conftest import load_script

charts = load_script("04_make_charts.py")


def test_top_classes_with_other_folds_small_classes():
    df = pd.DataFrame({
        "age_group": ["0-17", "0-17", "0-17"],
        "encounter_class": ["ambulatory", "hospice", "snf"],
        "pct_within_age_group": [90.0, 6.0, 4.0],
    })
    table = charts.top_classes_with_other(df, ["ambulatory"])
    assert list(table.columns) == ["ambulatory", "other"]
    assert table.at["0-17", "other"] == 10.0


def test_charts_are_saved(tmp_path):
    yearly = pd.DataFrame({"year": [2024, 2025], "encounters": [10, 4], "is_partial_year": [0, 1]})
    path = tmp_path / "chart.png"
    charts.chart_encounters_per_year(yearly, path)
    assert path.exists() and path.stat().st_size > 1000


def test_main_exits_with_message_when_tables_missing(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(charts, "TABLES_DIR", tmp_path)
    with pytest.raises(SystemExit):
        charts.main()
    assert "run  python src/03_run_queries.py  first" in capsys.readouterr().out
