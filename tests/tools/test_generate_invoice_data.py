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


def test_real_invoice_credited_status_for_catchup_overcharge():
    """Expert-Hour finding, 2026-07-12: a credit invoice must not read PAID."""
    inv = _real_invoice(_raw_invoice(payment_status="credited", total_amount_gbp=-2.03))
    assert inv["status"] == "CREDITED"


def test_real_invoice_derives_a_unit_rate_that_REPRODUCES_the_printed_amount():
    """D_printed_figure_rederivation (2026-08-03): this used to assert
    `round(63.32/471.1*100, 2)` -- i.e. it pinned the defect. That 2dp rate is
    13.44p, and 471.1 x 13.44p is GBP 63.32... only by luck of this fixture; on
    the real book the same formula made 86.1% of rendered usage lines fail
    their own multiplication. The assertion is now the PROPERTY the printed
    figures must have, not the formula that produced them."""
    inv = _real_invoice(_raw_invoice())
    rate = inv["unit_rate_p_per_kwh"]
    assert rate is not None
    assert round(inv["consumption_kwh"] * rate / 100, 2) == inv["commodity_amount_gbp"]


def test_real_invoice_carries_through_a_unit_rate_the_ledger_already_printed():
    """The ledger chooses the display precision; the mapper must not re-round
    it. Two independent derivations of one printed figure is how they drift."""
    inv = _real_invoice(_raw_invoice(unit_rate_p_per_kwh=13.4408))
    assert inv["unit_rate_p_per_kwh"] == 13.4408


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


# D3 step 2 (docs/design/maturity_map.yaml "Estimated billing & catch-up
# rebilling cycle"): catchup_* fields carried through unchanged, same
# passthrough pattern as read_type above.

def test_real_invoice_catchup_absent_defaults_false():
    inv = _real_invoice(_raw_invoice())
    assert inv["catchup_applied"] is False
    assert inv["catchup_adjustment_gbp"] is None


def test_real_invoice_carries_through_catchup_fields():
    inv = _real_invoice(_raw_invoice(
        catchup_applied=True, catchup_direction="overcharge",
        catchup_periods_covered=3, catchup_raw_delta_gbp=-42.0,
        catchup_adjustment_gbp=-42.0, catchup_written_off_gbp=0.0,
        catchup_back_billing_cap_applied=False,
    ))
    assert inv["catchup_applied"] is True
    assert inv["catchup_direction"] == "overcharge"
    assert inv["catchup_periods_covered"] == 3
    assert inv["catchup_adjustment_gbp"] == -42.0
    assert inv["catchup_back_billing_cap_applied"] is False


def test_real_invoices_for_missing_customer_returns_empty_list():
    assert real_invoices_for("NOPE", {}) == []


def test_real_invoices_for_maps_all_invoices():
    ledger_customers = {"C1": {"invoices": [_raw_invoice(invoice_number=1), _raw_invoice(invoice_number=2)]}}
    result = real_invoices_for("C1", ledger_customers)
    assert len(result) == 2
    assert result[0]["id"] == "C1-INV1"
    assert result[1]["id"] == "C1-INV2"
