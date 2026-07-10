"""Tests for tools/generate_invoice_data.py's pure invoice-mapping function."""
from tools.generate_invoice_data import _real_invoice, real_invoices_for


def _raw_invoice(**overrides):
    base = dict(
        customer_id="C1", invoice_number=1, period_start="2016-01-01",
        period_end="2016-01-31", commodity="electricity", consumption_kwh=471.1,
        commodity_amount_gbp=63.32, standing_charge_gbp=8.37,
        non_commodity_amount_gbp=24.5, vat_gbp=4.81, total_amount_gbp=101.0,
        payment_status="paid", meter_serial="M1", mpan="123", mprn=None,
        read_type="A", opening_read_kwh=0.0, closing_read_kwh=471.1, registers=[],
    )
    base.update(overrides)
    return base


def test_real_invoice_maps_id_date_amount_status():
    inv = _real_invoice(_raw_invoice())
    assert inv["id"] == "C1-INV1"
    assert inv["date"] == "2016-01-31"
    assert inv["amount_gbp"] == 101.0
    assert inv["status"] == "PAID"


def test_real_invoice_derives_unit_rate():
    inv = _real_invoice(_raw_invoice())
    assert inv["unit_rate_p_per_kwh"] == round(63.32 / 471.1 * 100, 2)


def test_real_invoice_unit_rate_none_when_zero_consumption():
    inv = _real_invoice(_raw_invoice(consumption_kwh=0))
    assert inv["unit_rate_p_per_kwh"] is None


# --- days_in_period / standing_charge_gbp_per_day (2026-07-10, director page
# comment: "Days x standing charges... explain the maths properly") ---

def test_real_invoice_carries_through_days_in_period_and_daily_rate():
    inv = _real_invoice(_raw_invoice(days_in_period=31, standing_charge_gbp_per_day=0.27))
    assert inv["days_in_period"] == 31
    assert inv["standing_charge_gbp_per_day"] == 0.27


def test_real_invoice_days_fields_none_when_absent_from_source():
    """Bills computed before the fix landed have no days_in_period/
    standing_charge_gbp_per_day in the source ledger record -- must degrade
    to None, not raise."""
    inv = _real_invoice(_raw_invoice())
    assert inv["days_in_period"] is None
    assert inv["standing_charge_gbp_per_day"] is None


def test_real_invoices_for_missing_customer_returns_empty_list():
    assert real_invoices_for("NOPE", {}) == []


def test_real_invoices_for_maps_all_invoices():
    ledger_customers = {"C1": {"invoices": [_raw_invoice(invoice_number=1), _raw_invoice(invoice_number=2)]}}
    result = real_invoices_for("C1", ledger_customers)
    assert len(result) == 2
    assert result[0]["id"] == "C1-INV1"
    assert result[1]["id"] == "C1-INV2"
