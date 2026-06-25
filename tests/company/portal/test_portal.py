"""Tests for C2: Customer portal (Phase 68)."""

import pytest
from starlette.testclient import TestClient

from company.billing.invoice import create_invoice
from company.portal.app import _CUSTOMER_INDEX, _invoice_summary, app

client = TestClient(app, raise_server_exceptions=True)


def test_login_page_renders():
    r = client.get("/")
    assert r.status_code == 200
    assert "Customer Portal" in r.text
    assert "account_id" in r.text


def test_login_valid_account_redirects():
    r = client.post("/login", data={"account_id": "C1"}, follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"] == "/account/C1"


def test_login_case_insensitive():
    r = client.post("/login", data={"account_id": "c1"}, follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"] == "/account/C1"


def test_login_unknown_account_shows_error():
    r = client.post("/login", data={"account_id": "X999"}, follow_redirects=False)
    assert r.status_code == 401
    assert "X999" in r.text or "not found" in r.text.lower()


def test_dashboard_renders_account_id():
    r = client.get("/account/C1")
    assert r.status_code == 200
    assert "C1" in r.text


def test_dashboard_shows_segment():
    r = client.get("/account/C1")
    assert r.status_code == 200
    assert "resi" in r.text


def test_dashboard_shows_commodity():
    r = client.get("/account/C1")
    assert r.status_code == 200
    assert "electricity" in r.text


def test_dashboard_404_for_unknown():
    r = client.get("/account/ZZZZ")
    assert r.status_code == 404


def test_bills_page_renders():
    r = client.get("/account/C1/bills")
    assert r.status_code == 200
    assert "C1" in r.text


def test_bills_page_shows_no_invoices_message_when_empty(tmp_path):
    from company.billing.invoice import create_schema
    db = tmp_path / "test_invoices.db"
    create_schema(db)
    from unittest.mock import patch
    with patch("company.portal.app._DEFAULT_DB", db):
        r = client.get("/account/C1/bills")
    assert r.status_code == 200
    assert "No invoices" in r.text


def test_bills_page_shows_invoice_row(tmp_path):
    db = tmp_path / "inv.db"
    bill = {
        "customer_id": "C1",
        "period_start": "2016-01-01",
        "period_end": "2016-01-31",
        "total_amount_gbp": 100.0,
        "total_consumption_kwh": 1200.0,
        "clarity_score": 0.9,
        "bill_shock_pct": None,
    }
    create_invoice(bill, db)
    from unittest.mock import patch
    with patch("company.portal.app._DEFAULT_DB", db):
        r = client.get("/account/C1/bills")
    assert r.status_code == 200
    assert "2016-01-31" in r.text


def test_bills_page_404_for_unknown():
    r = client.get("/account/ZZZZ/bills")
    assert r.status_code == 404


def test_invoice_summary_empty_db(tmp_path):
    db = tmp_path / "inv.db"
    result = _invoice_summary("C1", db)
    assert result["count"] == 0
    assert result["billed_gbp"] == 0.0


def test_customer_index_contains_known_accounts():
    assert "C1" in _CUSTOMER_INDEX
    assert "C5" in _CUSTOMER_INDEX
    assert _CUSTOMER_INDEX["C1"]["segment"] == "resi"
