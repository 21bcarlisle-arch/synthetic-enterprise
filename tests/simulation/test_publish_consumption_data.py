"""Tests for simulation/publish_consumption_data.py -- HH data reading and feed publishing.

Uses tmp_path to avoid touching real sim/hh_data/ or market_data/ files.
"""

import json
import csv
from pathlib import Path
import pytest

import simulation.publish_consumption_data as pcd


def _write_hh_csv(path: Path, rows: list[list]) -> None:
    """Write a minimal HH CSV with header + data rows."""
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        header = ["date"] + [str(p) for p in range(1, 49)]
        writer.writerow(header)
        for row in rows:
            writer.writerow(row)


def _data_row(date_str: str, kwh: float = 0.1) -> list:
    return [date_str] + [kwh] * 48


@pytest.fixture(autouse=True)
def patch_dirs(tmp_path, monkeypatch):
    monkeypatch.setattr(pcd, "HH_DATA_DIR", tmp_path / "hh_data")
    (tmp_path / "hh_data").mkdir()
    monkeypatch.setattr(pcd, "FEED_PATH", tmp_path / "consumption_feed.json")


def test_read_hh_data_no_file(tmp_path):
    result = pcd.read_hh_data("C7")
    assert result == []


def test_read_hh_data_empty_file(tmp_path):
    hh_dir = tmp_path / "hh_data"
    path = hh_dir / "C7.csv"
    _write_hh_csv(path, [])
    result = pcd.read_hh_data("C7")
    assert result == []


def test_read_hh_data_returns_48_per_day(tmp_path):
    hh_dir = tmp_path / "hh_data"
    path = hh_dir / "C7.csv"
    _write_hh_csv(path, [_data_row("2024-01-01")])
    result = pcd.read_hh_data("C7", n_days=1)
    assert len(result) == 48


def test_read_hh_data_period_range(tmp_path):
    hh_dir = tmp_path / "hh_data"
    path = hh_dir / "C7.csv"
    _write_hh_csv(path, [_data_row("2024-01-01")])
    result = pcd.read_hh_data("C7", n_days=1)
    periods = [r["period"] for r in result]
    assert min(periods) == 1
    assert max(periods) == 48


def test_read_hh_data_customer_id_in_record(tmp_path):
    hh_dir = tmp_path / "hh_data"
    path = hh_dir / "C7.csv"
    _write_hh_csv(path, [_data_row("2024-01-01")])
    result = pcd.read_hh_data("C7", n_days=1)
    assert all(r["customer_id"] == "C7" for r in result)


def test_read_hh_data_respects_n_days(tmp_path):
    hh_dir = tmp_path / "hh_data"
    path = hh_dir / "C7.csv"
    _write_hh_csv(path, [
        _data_row("2024-01-01"),
        _data_row("2024-01-02"),
        _data_row("2024-01-03"),
    ])
    result = pcd.read_hh_data("C7", n_days=1)
    assert all(r["date"] == "2024-01-03" for r in result)
    assert len(result) == 48


def test_read_hh_data_kwh_value(tmp_path):
    hh_dir = tmp_path / "hh_data"
    path = hh_dir / "C7.csv"
    _write_hh_csv(path, [_data_row("2024-01-01", kwh=0.5)])
    result = pcd.read_hh_data("C7", n_days=1)
    assert all(r["kwh"] == 0.5 for r in result)


def test_read_hh_data_hour_field(tmp_path):
    hh_dir = tmp_path / "hh_data"
    path = hh_dir / "C7.csv"
    _write_hh_csv(path, [_data_row("2024-01-01")])
    result = pcd.read_hh_data("C7", n_days=1)
    # Period 1 -> hour 0.0, period 2 -> hour 0.5, period 48 -> hour 23.5
    assert result[0]["hour"] == 0.0
    assert result[1]["hour"] == 0.5
    assert result[47]["hour"] == 23.5


def test_publish_consumption_creates_file(tmp_path):
    hh_dir = tmp_path / "hh_data"
    for cid in ("C7", "C8", "C9"):
        _write_hh_csv(hh_dir / f"{cid}.csv", [_data_row("2024-01-01")])
    feed_path = tmp_path / "consumption_feed.json"
    pcd.publish_consumption(
        hh_customers=("C7", "C8", "C9"),
        n_days=1,
        output_path=feed_path,
    )
    assert feed_path.exists()


def test_publish_consumption_json_structure(tmp_path):
    hh_dir = tmp_path / "hh_data"
    for cid in ("C7",):
        _write_hh_csv(hh_dir / f"{cid}.csv", [_data_row("2024-01-01")])
    feed_path = tmp_path / "consumption_feed.json"
    pcd.publish_consumption(hh_customers=("C7",), n_days=1, output_path=feed_path)
    payload = json.loads(feed_path.read_text())
    assert "published_at" in payload
    assert "records" in payload
    assert len(payload["records"]) == 48


def test_read_hh_data_date_field_matches_csv(tmp_path):
    hh_dir = tmp_path / "hh_data"
    path = hh_dir / "C7.csv"
    _write_hh_csv(path, [_data_row("2024-03-15")])
    result = pcd.read_hh_data("C7", n_days=1)
    assert all(r["date"] == "2024-03-15" for r in result)


def test_publish_consumption_records_have_customer_id(tmp_path):
    hh_dir = tmp_path / "hh_data"
    _write_hh_csv(hh_dir / "C7.csv", [_data_row("2024-01-01")])
    feed_path = tmp_path / "consumption_feed.json"
    pcd.publish_consumption(hh_customers=("C7",), n_days=1, output_path=feed_path)
    payload = __import__("json").loads(feed_path.read_text())
    assert all("customer_id" in r for r in payload["records"])


def test_read_hh_data_period_starts_at_1(tmp_path):
    hh_dir = tmp_path / "hh_data"
    path = hh_dir / "C7.csv"
    _write_hh_csv(path, [_data_row("2024-01-01")])
    result = pcd.read_hh_data("C7", n_days=1)
    assert result[0]["period"] == 1
