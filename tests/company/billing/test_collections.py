"""Phase 96: Collections queue tests."""

from datetime import date
from pathlib import Path
from company.billing.collections import (
    _aging_tier, get_overdue_invoices, get_collections_queue
)
from company.billing.invoice import create_invoice, create_schema
from starlette.testclient import TestClient
from company.portal.app import app

client = TestClient(app, raise_server_exceptions=True)


def _make_bill(account_id, commodity, period_start, period_end, kwh, amount):
    return {
        "customer_id": account_id,
        "account_id": account_id,
        "commodity": commodity,
        "period_start": period_start,
        "period_end": period_end,
        "total_consumption_kwh": kwh,
        "total_amount_gbp": amount,
    }


def test_aging_tier_0_30():
    assert _aging_tier(15) == "0-30"


def test_aging_tier_30_60():
    assert _aging_tier(45) == "30-60"


def test_aging_tier_60_90():
    assert _aging_tier(75) == "60-90"


def test_aging_tier_90_plus():
    assert _aging_tier(120) == "90+"


def test_collections_empty_db_returns_empty(tmp_path):
    db = tmp_path / "inv.db"
    result = get_collections_queue(db)
    assert result == []


def test_collections_overdue_invoice(tmp_path):
    db = tmp_path / "inv.db"
    create_schema(db)
    create_invoice(_make_bill("C1", "electricity", "2025-01-01", "2025-01-31", 500.0, 1000.0), db)
    # Invoice is overdue (due date in the past)
    as_of = date(2026, 6, 26)
    queue = get_collections_queue(db, as_of=as_of)
    assert len(queue) == 1
    assert queue[0]["account_id"] == "C1"
    assert queue[0]["max_days_overdue"] > 0


def test_collections_tier_90_plus_for_old_debt(tmp_path):
    db = tmp_path / "inv.db"
    create_schema(db)
    create_invoice(_make_bill("C2", "electricity", "2024-01-01", "2024-01-31", 200.0, 500.0), db)
    as_of = date(2026, 6, 26)
    queue = get_collections_queue(db, as_of=as_of)
    assert queue[0]["tier"] == "90+"


def test_collections_multiple_customers_sorted(tmp_path):
    db = tmp_path / "inv.db"
    create_schema(db)
    # C1: recent overdue
    create_invoice(_make_bill("C1", "electricity", "2026-04-01", "2026-04-30", 100.0, 200.0), db)
    # C2: old overdue
    create_invoice(_make_bill("C2", "electricity", "2024-01-01", "2024-01-31", 200.0, 500.0), db)
    as_of = date(2026, 6, 26)
    queue = get_collections_queue(db, as_of=as_of)
    # C2 (older debt) should be first
    assert queue[0]["account_id"] == "C2"


def test_admin_collections_route_returns_200():
    r = client.get("/admin/collections")
    assert r.status_code == 200


def test_admin_collections_shows_clear_state_or_table():
    r = client.get("/admin/collections")
    assert "Collections" in r.text


def test_aging_tier_exactly_30():
    assert _aging_tier(30) == "30-60"


def test_aging_tier_exactly_0():
    assert _aging_tier(0) == "0-30"


def test_admin_collections_content_type_is_html():
    r = client.get("/admin/collections")
    assert "text/html" in r.headers.get("content-type", "")
