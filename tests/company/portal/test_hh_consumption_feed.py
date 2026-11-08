"""Phase 82 tests: HH consumption data feed and portal integration."""
import json
import pytest
from pathlib import Path

from simulation.publish_consumption_data import read_hh_data, publish_consumption
from company.billing.invoice import create_schema, create_invoice


@pytest.fixture
def consumption_feed(tmp_path):
    feed = tmp_path / "consumption_feed.json"
    publish_consumption(hh_customers=("C7",), n_days=1, output_path=feed)
    return feed


# ---------------------------------------------------------------------------
# publish_consumption_data
# ---------------------------------------------------------------------------

def test_read_hh_data_returns_48_periods_per_day():
    records = read_hh_data("C7", n_days=1)
    assert len(records) == 48


def test_read_hh_data_periods_range_1_to_48():
    records = read_hh_data("C7", n_days=1)
    periods = [r["period"] for r in records]
    assert min(periods) == 1
    assert max(periods) == 48


def test_read_hh_data_kwh_nonnegative():
    records = read_hh_data("C7", n_days=1)
    assert all(r["kwh"] >= 0 for r in records)


def test_read_hh_data_unknown_customer_returns_empty():
    records = read_hh_data("UNKNOWN", n_days=1)
    assert records == []


def test_publish_consumption_creates_feed_file(tmp_path):
    out = tmp_path / "cf.json"
    publish_consumption(hh_customers=("C7",), output_path=out)
    assert out.exists()


def test_publish_consumption_feed_has_all_customers(tmp_path):
    out = tmp_path / "cf.json"
    publish_consumption(hh_customers=("C7", "C8"), n_days=1, output_path=out)
    data = json.loads(out.read_text())
    ids = {r["customer_id"] for r in data["records"]}
    assert "C7" in ids
    assert "C8" in ids


# ---------------------------------------------------------------------------
# hh_consumption (company layer)
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Portal route
# ---------------------------------------------------------------------------

