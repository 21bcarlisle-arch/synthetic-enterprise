"""Phase 79 tests: portal consumption history page."""
import pytest
from pathlib import Path
from starlette.testclient import TestClient

from company.portal.app import app
from company.billing.consumption import consumption_history, monthly_totals
from company.billing.invoice import create_schema, create_invoice


@pytest.fixture
def tmp_db(tmp_path):
    db = tmp_path / "invoices.db"
    create_schema(db)
    return db


def _bill(account_id, period_start, period_end, kwh=100.0, segment="resi", commodity="electricity"):
    return {
        "customer_id": account_id,
        "period_start": period_start,
        "period_end": period_end,
        "total_consumption_kwh": kwh,
        "revenue_gbp": kwh * 0.2,
        "commodity_amount_gbp": kwh * 0.2,
        "non_commodity_amount_gbp": kwh * 0.055,
        "standing_charge_gbp": 5.0,
        "vat_gbp": 2.0,
        "total_amount_gbp": kwh * 0.275 + 7.0,
        "segment": segment,
        "commodity": commodity,
        "contract_type": "fixed_1yr",
    }


# ---------------------------------------------------------------------------
# consumption_history
# ---------------------------------------------------------------------------

def test_consumption_history_empty_when_no_invoices(tmp_db):
    records = consumption_history("C1", tmp_db)
    assert records == []


def test_consumption_history_returns_db_records(tmp_db):
    create_invoice(_bill("C1", "2022-01-01", "2022-01-31", kwh=150.0), tmp_db)
    records = consumption_history("C1", tmp_db)
    assert len(records) == 1
    assert records[0]["kwh"] == pytest.approx(150.0)
    assert records[0]["year"] == 2022
    assert records[0]["month"] == 1


def test_consumption_history_filters_by_account(tmp_db):
    create_invoice(_bill("C1", "2022-01-01", "2022-01-31", kwh=100.0), tmp_db)
    create_invoice(_bill("C2", "2022-01-01", "2022-01-31", kwh=200.0), tmp_db)
    c1_records = consumption_history("C1", tmp_db)
    c2_records = consumption_history("C2", tmp_db)
    assert len(c1_records) == 1
    assert len(c2_records) == 1
    assert c1_records[0]["kwh"] == pytest.approx(100.0)


def test_consumption_history_absent_db_returns_empty(tmp_path):
    missing_db = tmp_path / "no_such.db"
    records = consumption_history("C1", missing_db)
    assert records == []


# ---------------------------------------------------------------------------
# monthly_totals
# ---------------------------------------------------------------------------

def test_monthly_totals_aggregates_within_month(tmp_db):
    create_invoice(_bill("C1", "2022-01-01", "2022-01-15", kwh=80.0), tmp_db)
    create_invoice(_bill("C1", "2022-01-16", "2022-01-31", kwh=70.0), tmp_db)
    records = consumption_history("C1", tmp_db)
    totals = monthly_totals(records)
    assert len(totals) == 1
    assert totals[0]["kwh"] == pytest.approx(150.0)
    assert totals[0]["year"] == 2022
    assert totals[0]["month"] == 1


def test_monthly_totals_sorted_chronologically(tmp_db):
    create_invoice(_bill("C1", "2023-03-01", "2023-03-31", kwh=90.0), tmp_db)
    create_invoice(_bill("C1", "2022-11-01", "2022-11-30", kwh=120.0), tmp_db)
    records = consumption_history("C1", tmp_db)
    totals = monthly_totals(records)
    assert totals[0]["year"] == 2022
    assert totals[1]["year"] == 2023


# ---------------------------------------------------------------------------
# Portal route tests
# ---------------------------------------------------------------------------

@pytest.fixture
def client(tmp_db, monkeypatch):
    monkeypatch.setattr("company.portal.app._DEFAULT_DB", tmp_db)
    return TestClient(app)


def test_consumption_route_returns_200_for_known_account(client, tmp_db):
    create_invoice(_bill("C1", "2022-01-01", "2022-01-31", kwh=100.0), tmp_db)
    resp = client.get("/account/C1/consumption")
    assert resp.status_code == 200


def test_consumption_route_shows_monthly_data(client, tmp_db):
    create_invoice(_bill("C1", "2022-06-01", "2022-06-30", kwh=250.0), tmp_db)
    resp = client.get("/account/C1/consumption")
    assert "250.0" in resp.text or "250" in resp.text


def test_consumption_route_shows_hh_banner_for_c7(client, tmp_db):
    create_invoice(_bill("C7", "2022-06-01", "2022-06-30", kwh=300.0), tmp_db)
    resp = client.get("/account/C7/consumption")
    assert resp.status_code == 200
    assert "Smart meter" in resp.text or "half-hourly" in resp.text


def test_consumption_route_no_banner_for_non_hh(client, tmp_db):
    create_invoice(_bill("C1", "2022-06-01", "2022-06-30", kwh=100.0), tmp_db)
    resp = client.get("/account/C1/consumption")
    assert "Smart meter" not in resp.text


def test_consumption_route_unknown_account_returns_404(client):
    resp = client.get("/account/UNKNOWN_XYZ/consumption")
    assert resp.status_code == 404
