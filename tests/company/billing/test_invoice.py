"""Tests for company.billing.invoice."""

import pytest

from company.billing.invoice import (
    bulk_create_invoices,
    create_invoice,
    create_schema,
    get_invoice,
    invoice_summary,
    invoices_for_account,
    update_payment_status,
)


@pytest.fixture
def db(tmp_path):
    return tmp_path / "test_invoices.db"


def _bill(
    customer_id="C1",
    period_start="2016-01-01",
    period_end="2016-01-31",
    amount=100.0,
    consumption=1500.0,
):
    return {
        "customer_id": customer_id,
        "period_start": period_start,
        "period_end": period_end,
        "total_amount_gbp": amount,
        "total_consumption_kwh": consumption,
        "clarity_score": 0.85,
        "bill_shock_pct": None,
    }


def test_create_schema_idempotent(db):
    create_schema(db)
    create_schema(db)


def test_create_invoice_returns_invoice_number(db):
    num = create_invoice(_bill(), db)
    assert isinstance(num, int)
    assert num >= 1


def test_create_invoice_sequential_numbers(db):
    n1 = create_invoice(_bill(period_end="2016-01-31"), db)
    n2 = create_invoice(_bill(period_end="2016-02-28"), db)
    assert n2 == n1 + 1


def test_get_invoice_returns_record(db):
    num = create_invoice(_bill(), db)
    inv = get_invoice(num, db)
    assert inv is not None
    assert inv["account_id"] == "C1"
    assert inv["total_gbp"] > inv["subtotal_gbp"]  # VAT applied


def test_invoice_includes_vat(db):
    num = create_invoice(_bill(amount=100.0), db)
    inv = get_invoice(num, db)
    # 5% VAT on £100 = £5
    assert abs(inv["vat_gbp"] - 5.0) < 0.01
    assert abs(inv["total_gbp"] - 105.0) < 0.01


def test_get_invoice_returns_none_for_unknown(db):
    create_schema(db)
    assert get_invoice(9999, db) is None


def test_invoices_for_account(db):
    create_invoice(_bill(customer_id="C1", period_end="2016-01-31"), db)
    create_invoice(_bill(customer_id="C1", period_end="2016-02-28"), db)
    create_invoice(_bill(customer_id="C2", period_end="2016-01-31"), db)
    c1_invoices = invoices_for_account("C1", db)
    assert len(c1_invoices) == 2
    assert all(inv["account_id"] == "C1" for inv in c1_invoices)


def test_update_payment_status_paid(db):
    num = create_invoice(_bill(), db)
    update_payment_status(num, "paid", db)
    assert get_invoice(num, db)["payment_status"] == "paid"


def test_update_payment_status_invalid_raises(db):
    num = create_invoice(_bill(), db)
    with pytest.raises(ValueError):
        update_payment_status(num, "overdue", db)


def test_bulk_create_invoices_returns_count(db):
    bills = [
        _bill(period_end="2016-01-31"),
        _bill(period_end="2016-02-28"),
        _bill(period_end="2016-03-31"),
    ]
    count = bulk_create_invoices(bills, db)
    assert count == 3


def test_invoice_summary_totals(db):
    create_invoice(_bill(amount=100.0), db)
    create_invoice(_bill(amount=200.0, period_end="2016-02-28"), db)
    summary = invoice_summary(db)
    assert summary["total_count"] == 2
    # Total billed = 105 + 210 = 315 (with VAT)
    assert abs(summary["total_billed_gbp"] - 315.0) < 0.01


def test_due_date_is_14_days_after_period_end(db):
    num = create_invoice(_bill(period_end="2016-01-31"), db)
    inv = get_invoice(num, db)
    assert inv["due_date"] == "2016-02-14"


def _rich_bill(
    customer_id='C1',
    period_start='2016-01-01',
    period_end='2016-01-31',
    commodity_amount=120.0,
    non_commodity=25.0,
    standing_charge=8.0,
    vat=7.65,
    consumption=1500.0,
):
    subtotal = commodity_amount + non_commodity + standing_charge
    return {
        'customer_id': customer_id,
        'period_start': period_start,
        'period_end': period_end,
        'total_consumption_kwh': consumption,
        'commodity_amount_gbp': commodity_amount,
        'non_commodity_amount_gbp': non_commodity,
        'standing_charge_gbp': standing_charge,
        'vat_gbp': vat,
        'total_amount_gbp': subtotal + vat,
        'clarity_score': 0.85,
        'bill_shock_pct': None,
        'segment': 'resi',
        'commodity': 'electricity',
    }


def test_standing_charge_stored_from_bill(db):
    num = create_invoice(_rich_bill(standing_charge=8.50), db)
    inv = get_invoice(num, db)
    assert abs(inv['standing_charge_gbp'] - 8.50) < 0.01


def test_non_commodity_stored_from_bill(db):
    num = create_invoice(_rich_bill(non_commodity=25.30), db)
    inv = get_invoice(num, db)
    assert abs(inv['non_commodity_amount_gbp'] - 25.30) < 0.01


def test_commodity_amount_stored_from_bill(db):
    num = create_invoice(_rich_bill(commodity_amount=120.00), db)
    inv = get_invoice(num, db)
    assert abs(inv['commodity_amount_gbp'] - 120.00) < 0.01


def test_correct_vat_from_bill_line_items(db):
    num = create_invoice(_rich_bill(commodity_amount=100.0, non_commodity=0.0,
                                     standing_charge=0.0, vat=5.0), db)
    inv = get_invoice(num, db)
    assert abs(inv['vat_gbp'] - 5.0) < 0.01
    assert abs(inv['total_gbp'] - 105.0) < 0.01


def test_format_invoice_text_has_header():
    from company.billing.invoice import format_invoice_text
    inv = {'invoice_number': 42, 'account_id': 'C1', 'commodity': 'electricity',
           'issue_date': '2016-01-31', 'due_date': '2016-02-14',
           'billing_period_start': '2016-01-01', 'billing_period_end': '2016-01-31',
           'consumption_kwh': 1500.0, 'unit_rate_p_per_kwh': 12.5,
           'commodity_amount_gbp': 187.50, 'non_commodity_amount_gbp': 25.30,
           'standing_charge_gbp': 8.60, 'subtotal_gbp': 221.40,
           'vat_gbp': 11.07, 'total_gbp': 232.47, 'payment_status': 'unpaid'}
    text = format_invoice_text(inv)
    assert 'INVOICE' in text
    assert '=======' in text


def test_format_invoice_text_shows_account_id():
    from company.billing.invoice import format_invoice_text
    inv = {'invoice_number': 1, 'account_id': 'C3', 'commodity': 'electricity',
           'issue_date': '2016-01-31', 'due_date': '2016-02-14',
           'billing_period_start': '2016-01-01', 'billing_period_end': '2016-01-31',
           'consumption_kwh': 0.0, 'unit_rate_p_per_kwh': 0.0,
           'commodity_amount_gbp': 0.0, 'non_commodity_amount_gbp': 0.0,
           'standing_charge_gbp': 0.0, 'subtotal_gbp': 0.0,
           'vat_gbp': 0.0, 'total_gbp': 0.0, 'payment_status': 'unpaid'}
    text = format_invoice_text(inv)
    assert 'C3' in text


def test_format_invoice_text_shows_total():
    from company.billing.invoice import format_invoice_text
    inv = {'invoice_number': 1, 'account_id': 'C1', 'commodity': 'electricity',
           'issue_date': '2016-01-31', 'due_date': '2016-02-14',
           'billing_period_start': '2016-01-01', 'billing_period_end': '2016-01-31',
           'consumption_kwh': 1500.0, 'unit_rate_p_per_kwh': 12.5,
           'commodity_amount_gbp': 187.50, 'non_commodity_amount_gbp': 0.0,
           'standing_charge_gbp': 0.0, 'subtotal_gbp': 187.50,
           'vat_gbp': 9.38, 'total_gbp': 196.88, 'payment_status': 'unpaid'}
    text = format_invoice_text(inv)
    assert 'TOTAL DUE' in text
    assert '196.88' in text


def test_format_invoice_text_shows_billing_period():
    from company.billing.invoice import format_invoice_text
    inv = {'invoice_number': 1, 'account_id': 'C1', 'commodity': 'electricity',
           'issue_date': '2022-06-30', 'due_date': '2022-07-14',
           'billing_period_start': '2022-06-01', 'billing_period_end': '2022-06-30',
           'consumption_kwh': 200.0, 'unit_rate_p_per_kwh': 50.0,
           'commodity_amount_gbp': 100.0, 'non_commodity_amount_gbp': 0.0,
           'standing_charge_gbp': 0.0, 'subtotal_gbp': 100.0,
           'vat_gbp': 5.0, 'total_gbp': 105.0, 'payment_status': 'unpaid'}
    text = format_invoice_text(inv)
    assert '2022-06-01' in text
    assert '2022-06-30' in text


def test_format_invoice_text_shows_line_items():
    from company.billing.invoice import format_invoice_text
    inv = {'invoice_number': 1, 'account_id': 'C1', 'commodity': 'electricity',
           'issue_date': '2016-01-31', 'due_date': '2016-02-14',
           'billing_period_start': '2016-01-01', 'billing_period_end': '2016-01-31',
           'consumption_kwh': 1500.0, 'unit_rate_p_per_kwh': 12.5,
           'commodity_amount_gbp': 187.50, 'non_commodity_amount_gbp': 25.30,
           'standing_charge_gbp': 8.60, 'subtotal_gbp': 221.40,
           'vat_gbp': 11.07, 'total_gbp': 232.47, 'payment_status': 'unpaid'}
    text = format_invoice_text(inv)
    assert 'Energy Charge' in text
    assert 'Standing Charge' in text
    assert 'Network' in text

