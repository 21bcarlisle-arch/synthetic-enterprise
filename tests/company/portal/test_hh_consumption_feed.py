"""Phase 82 tests: HH consumption data feed and portal integration."""
import json
import pytest
from pathlib import Path
from starlette.testclient import TestClient

from simulation.publish_consumption_data import read_hh_data, publish_consumption
from company.billing.hh_consumption import get_hh_consumption, recent_hh_periods, is_feed_available
from company.portal.app import app
from company.billing.invoice import create_schema, create_invoice


@pytest.fixture
def consumption_feed(tmp_path):
    feed = tmp_path / "consumption_feed.json"
    publish_consumption(hh_customers=("C7",), n_days=1, output_path=feed)
    return feed


@pytest.fixture
def client(consumption_feed, monkeypatch):
    monkeypatch.setattr("company.portal.app._CONSUMPTION_FEED_PATH", consumption_feed)
    return TestClient(app)


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

def test_get_hh_consumption_reads_feed(consumption_feed):
    records = get_hh_consumption("C7", consumption_feed)
    assert len(records) == 48


def test_get_hh_consumption_filters_by_customer(consumption_feed):
    records = get_hh_consumption("C8", consumption_feed)
    assert records == []  # C8 not in this fixture


def test_get_hh_consumption_absent_feed_returns_empty(tmp_path):
    records = get_hh_consumption("C7", tmp_path / "no.json")
    assert records == []


def test_recent_hh_periods_returns_last_n(consumption_feed):
    all_rec = get_hh_consumption("C7", consumption_feed)
    recent = recent_hh_periods(all_rec, n_periods=10)
    assert len(recent) == 10
    assert recent[-1]["period"] == 48


def test_is_feed_available_true_when_exists(consumption_feed):
    assert is_feed_available(consumption_feed) is True


def test_is_feed_available_false_when_absent(tmp_path):
    assert is_feed_available(tmp_path / "missing.json") is False


# ---------------------------------------------------------------------------
# Portal route
# ---------------------------------------------------------------------------

def test_consumption_route_shows_hh_table_for_c7(client, tmp_path, monkeypatch):
    db = tmp_path / "invoices.db"
    create_schema(db)
    monkeypatch.setattr("company.portal.app._DEFAULT_DB", db)
    resp = client.get("/account/C7/consumption")
    assert resp.status_code == 200
    assert "Half-Hourly" in resp.text or "half-hourly" in resp.text.lower()
