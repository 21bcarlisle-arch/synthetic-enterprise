"""Phase 83: Portal payment submission tests."""

from pathlib import Path

from starlette.testclient import TestClient

from company.billing.invoice import create_invoice, get_invoice, invoices_for_account
from company.billing.payments import reconcile_payment
from company.portal.app import app

client = TestClient(app, raise_server_exceptions=True)

VAT = 0.05


def _make_invoice(db_path, account_id="C1", period_end="2024-01-31", subtotal=120.0):
    """Create a test invoice. Stored total_gbp = subtotal * 1.05."""
    bill = {
        "customer_id": account_id,
        "period_start": "2024-01-01",
        "period_end": period_end,
        "total_consumption_kwh": 500.0,
        "total_amount_gbp": subtotal,
        "commodity": "electricity",
        "segment": "resi",
        "tariff_type": "fixed",
    }
    return create_invoice(bill, db_path)


def test_pay_full_amount_marks_paid(tmp_path):
    db = tmp_path / "inv.db"
    _make_invoice(db, "C1", "2024-01-31", 120.0)
    full_total = round(120.0 * (1 + VAT), 2)
    result = reconcile_payment(
        {"event_type": "payment_received_event", "customer_id": "C1",
         "bill_period_end": "2024-01-31", "amount_gbp": full_total},
        db,
    )
    assert result == "paid"


def test_pay_partial_amount_marks_partially_paid(tmp_path):
    db = tmp_path / "inv.db"
    _make_invoice(db, "C1", "2024-02-28", 120.0)
    result = reconcile_payment(
        {"event_type": "payment_received_event", "customer_id": "C1",
         "bill_period_end": "2024-02-28", "amount_gbp": 50.0},
        db,
    )
    assert result == "partially_paid"


def test_pay_overpayment_marks_paid(tmp_path):
    db = tmp_path / "inv.db"
    _make_invoice(db, "C1", "2024-03-31", 100.0)
    full_total = round(100.0 * (1 + VAT), 2)
    result = reconcile_payment(
        {"event_type": "payment_received_event", "customer_id": "C1",
         "bill_period_end": "2024-03-31", "amount_gbp": full_total + 20.0},
        db,
    )
    assert result == "paid"


def test_pay_no_matching_invoice_returns_no_match(tmp_path):
    db = tmp_path / "inv.db"
    _make_invoice(db, "C1", "2024-01-31", 100.0)
    result = reconcile_payment(
        {"event_type": "payment_received_event", "customer_id": "C1",
         "bill_period_end": "2099-12-31", "amount_gbp": 100.0},
        db,
    )
    assert result == "no_match"


def test_pay_wrong_customer_no_match(tmp_path):
    db = tmp_path / "inv.db"
    _make_invoice(db, "C1", "2024-01-31", 100.0)
    result = reconcile_payment(
        {"event_type": "payment_received_event", "customer_id": "C2",
         "bill_period_end": "2024-01-31", "amount_gbp": 100.0},
        db,
    )
    assert result == "no_match"


def test_pay_route_unknown_account_returns_404():
    r = client.post(
        "/account/ZZZZ/pay",
        data={"invoice_number": "1", "amount_gbp": "100.00"},
    )
    assert r.status_code == 404


def test_pay_route_unknown_invoice_returns_404():
    r = client.post(
        "/account/C1/pay",
        data={"invoice_number": "999999", "amount_gbp": "100.00"},
    )
    assert r.status_code == 404


def test_bills_template_has_pay_form():
    with open("company/portal/templates/bills.html") as f:
        html = f.read()
    assert "invoice_number" in html
    assert "amount_gbp" in html
    assert "/pay" in html


def test_bills_template_shows_pay_button():
    with open("company/portal/templates/bills.html") as f:
        html = f.read()
    assert "pay-btn" in html
    assert "unpaid" in html


def test_payment_confirm_template_shows_paid_message():
    with open("company/portal/templates/payment_confirm.html") as f:
        html = f.read()
    assert "fully settled" in html
    assert "invoice_number" in html


def test_payment_confirm_template_has_return_link():
    with open("company/portal/templates/payment_confirm.html") as f:
        html = f.read()
    assert "/bills" in html


def test_invoice_summary_outstanding_balance(tmp_path):
    db = tmp_path / "inv.db"
    _make_invoice(db, "C1", "2024-01-31", 120.0)
    _make_invoice(db, "C1", "2024-02-28", 80.0)
    full_total_1 = round(120.0 * (1 + VAT), 2)
    reconcile_payment(
        {"event_type": "payment_received_event", "customer_id": "C1",
         "bill_period_end": "2024-01-31", "amount_gbp": full_total_1},
        db,
    )
    invs = invoices_for_account("C1", db)
    outstanding = sum(
        i["total_gbp"] for i in invs
        if i["payment_status"] in ("unpaid", "partially_paid")
    )
    expected = round(80.0 * (1 + VAT), 2)
    assert abs(outstanding - expected) < 0.01
