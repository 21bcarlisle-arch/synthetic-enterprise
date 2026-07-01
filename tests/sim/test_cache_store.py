"""Tests for sim/cache_store.py -- file cache coverage checking and read/write.

Uses tmp_path fixture to avoid touching the real sim/cache directory.
"""

import json
import pytest
from pathlib import Path

import sim.cache_store as cache_store


@pytest.fixture(autouse=True)
def patch_cache_dir(tmp_path, monkeypatch):
    """Redirect CACHE_DIR to a temp directory for all tests in this file."""
    monkeypatch.setattr(cache_store, "CACHE_DIR", tmp_path)


def _write_records(tmp_path, records, filename="elexon_ssp_full.json"):
    (tmp_path / filename).write_text(json.dumps(records))


def test_miss_when_no_cache_file(tmp_path):
    result = cache_store.get_cached_prices("2024-01-01", "2024-01-31")
    assert result is None


def test_miss_when_cache_file_empty(tmp_path):
    _write_records(tmp_path, [])
    result = cache_store.get_cached_prices("2024-01-01", "2024-01-31")
    assert result is None


def test_miss_when_range_not_covered_start(tmp_path):
    records = [{"settlementDate": "2024-02-01", "systemSellPrice": 50.0}]
    _write_records(tmp_path, records)
    result = cache_store.get_cached_prices("2024-01-01", "2024-02-01")
    assert result is None


def test_miss_when_range_not_covered_end(tmp_path):
    records = [{"settlementDate": "2024-01-01", "systemSellPrice": 50.0}]
    _write_records(tmp_path, records)
    result = cache_store.get_cached_prices("2024-01-01", "2024-02-28")
    assert result is None


def test_hit_returns_records_within_range(tmp_path):
    records = [
        {"settlementDate": "2024-01-01", "systemSellPrice": 50.0},
        {"settlementDate": "2024-01-15", "systemSellPrice": 55.0},
        {"settlementDate": "2024-01-31", "systemSellPrice": 60.0},
    ]
    _write_records(tmp_path, records)
    result = cache_store.get_cached_prices("2024-01-01", "2024-01-31")
    assert result is not None
    assert len(result) == 3


def test_hit_filters_to_requested_subrange(tmp_path):
    records = [
        {"settlementDate": "2024-01-01", "systemSellPrice": 50.0},
        {"settlementDate": "2024-02-01", "systemSellPrice": 55.0},
        {"settlementDate": "2024-03-01", "systemSellPrice": 60.0},
    ]
    _write_records(tmp_path, records)
    result = cache_store.get_cached_prices("2024-01-01", "2024-02-28")
    assert result is not None
    assert len(result) == 2
    assert all(r["settlementDate"] <= "2024-02-28" for r in result)


def test_write_cached_prices(tmp_path):
    records = [{"settlementDate": "2024-01-01", "systemSellPrice": 50.0}]
    cache_store.write_cached_prices(records)
    cache_file = tmp_path / "elexon_ssp_full.json"
    assert cache_file.exists()
    loaded = json.loads(cache_file.read_text())
    assert loaded == records


def test_write_cached_prices_custom_filename(tmp_path):
    records = [{"settlementDate": "2024-01-01", "systemSellPrice": 50.0}]
    cache_store.write_cached_prices(records, "gas_prices.json")
    assert (tmp_path / "gas_prices.json").exists()
