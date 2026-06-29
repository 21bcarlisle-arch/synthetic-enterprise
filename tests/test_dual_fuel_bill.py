"""Tests for dual_fuel_bill.py — DualFuelBill Engine."""
import pytest
from company.billing.dual_fuel_bill import (
    DualFuelBillBook,
    DualFuelBill,
    FuelBillSection,
    _period_key,
    _days_in_period,
    _invoice_to_section,
    BILLING_CALENDAR,
    VAT_RATE_BY_MARKET,
)


def _elec_inv(period_start, period_end, kwh=250.0, total=52.50,
              sc_gbp=18.0, energy=28.0, levies=6.0, status="paid"):
    return {
        "invoice_number": 1,
        "account_id": "C1",
        "commodity": "electricity",
        "billing_period_start": period_start,
        "billing_period_end": period_end,
        "consumption_kwh": kwh,
        "unit_rate_p_per_kwh": 24.5,
        "standing_charge_gbp": sc_gbp,
        "commodity_amount_gbp": energy,
        "non_commodity_amount_gbp": levies,
        "subtotal_gbp": energy + levies + sc_gbp,
        "vat_gbp": round((energy + levies + sc_gbp) * 0.05, 2),
        "total_gbp": total,
        "payment_status": status,
    }


def _gas_inv(period_start, period_end, kwh=1000.0, total=82.0,
             sc_gbp=27.0, energy=50.0, status="paid"):
    return {
        "invoice_number": 2,
        "account_id": "C1g",
        "commodity": "gas",
        "billing_period_start": period_start,
        "billing_period_end": period_end,
        "consumption_kwh": kwh,
        "unit_rate_p_per_kwh": 5.5,
        "standing_charge_gbp": sc_gbp,
        "commodity_amount_gbp": energy,
        "non_commodity_amount_gbp": 0.0,
        "subtotal_gbp": energy + sc_gbp,
        "vat_gbp": round((energy + sc_gbp) * 0.05, 2),
        "total_gbp": total,
        "payment_status": status,
    }


# --- _period_key ---

def test_period_key_normal():
    assert _period_key("2023-03-31") == "2023-03"

def test_period_key_bad_date():
    assert _period_key("") == ""

def test_period_key_short_string():
    result = _period_key("2023-0")
    assert len(result) <= 7


# --- _days_in_period ---

def test_days_in_period_30_day_month():
    assert _days_in_period("2023-01-01", "2023-01-31") == 30

def test_days_in_period_invalid():
    assert _days_in_period("bad", "also_bad") == 30


# --- FuelBillSection via _invoice_to_section ---

def test_invoice_to_section_electricity():
    inv = _elec_inv("2023-01-01", "2023-01-31")
    sec = _invoice_to_section(inv, "electricity", "resi")
    assert sec.fuel == "electricity"
    assert sec.consumption_kwh == 250.0
    assert sec.standing_charge_gbp == 18.0
    assert sec.days_in_period == 30
    assert sec.vat_rate == pytest.approx(0.05, abs=0.01)

def test_invoice_to_section_gas():
    inv = _gas_inv("2023-01-01", "2023-01-31")
    sec = _invoice_to_section(inv, "gas", "resi")
    assert sec.fuel == "gas"
    assert sec.standing_charge_pence_per_day == pytest.approx(90.0, abs=1.0)

def test_invoice_to_section_paid_status():
    inv = _elec_inv("2023-01-01", "2023-01-31", status="paid")
    sec = _invoice_to_section(inv, "electricity", "resi")
    assert sec.is_paid is True

def test_invoice_to_section_unpaid_status():
    inv = _elec_inv("2023-01-01", "2023-01-31", status="unpaid")
    sec = _invoice_to_section(inv, "electricity", "resi")
    assert sec.is_paid is False

def test_sme_vat_high_usage():
    # Invoice with no stored vat_gbp -- engine derives from market type + usage
    inv = {
        "billing_period_start": "2023-01-01",
        "billing_period_end": "2023-01-31",
        "consumption_kwh": 1500.0,
        "unit_rate_p_per_kwh": 24.5,
        "standing_charge_gbp": 18.0,
        "commodity_amount_gbp": 280.0,
        "non_commodity_amount_gbp": 60.0,
        "payment_status": "unpaid",
    }
    # 1500 kWh / 30 days = 50 kWh/day > 33 threshold --> 20% VAT
    sec = _invoice_to_section(inv, "electricity", "SME")
    assert sec.vat_rate == pytest.approx(0.20, abs=0.01)

def test_ic_vat_rate():
    # Invoice with no stored vat_gbp -- engine derives from market type
    inv = {
        "billing_period_start": "2023-01-01",
        "billing_period_end": "2023-01-31",
        "consumption_kwh": 250.0,
        "unit_rate_p_per_kwh": 24.5,
        "standing_charge_gbp": 18.0,
        "commodity_amount_gbp": 28.0,
        "non_commodity_amount_gbp": 6.0,
        "payment_status": "unpaid",
    }
    sec = _invoice_to_section(inv, "electricity", "I&C")
    assert sec.vat_rate == pytest.approx(0.20, abs=0.01)

def test_effective_rate_pence():
    inv = _elec_inv("2023-01-01", "2023-01-31", kwh=200.0, total=50.0)
    sec = _invoice_to_section(inv, "electricity", "resi")
    assert sec.effective_rate_pence == pytest.approx(25.0, abs=1.0)


# --- DualFuelBillBook.build_bills ---

def test_build_bills_dual_fuel():
    book = DualFuelBillBook()
    elec = [_elec_inv("2023-01-01", "2023-01-31", total=52.50)]
    gas = [_gas_inv("2023-01-01", "2023-01-31", total=82.00)]
    bills = book.build_bills("C1", "resi", elec, gas)
    assert len(bills) == 1
    bill = bills[0]
    assert bill.is_dual_fuel
    assert bill.electricity is not None
    assert bill.gas is not None

def test_build_bills_electricity_only():
    book = DualFuelBillBook()
    elec = [_elec_inv("2023-01-01", "2023-01-31", total=52.50)]
    bills = book.build_bills("C1", "resi", elec, [])
    assert len(bills) == 1
    assert bills[0].is_electricity_only

def test_build_bills_total_billed():
    book = DualFuelBillBook()
    elec = [_elec_inv("2023-01-01", "2023-01-31", total=52.50)]
    gas = [_gas_inv("2023-01-01", "2023-01-31", total=82.00)]
    bills = book.build_bills("C1", "resi", elec, gas)
    assert bills[0].total_billed_gbp == pytest.approx(134.50, abs=0.01)

def test_build_bills_balance_zero_when_all_paid():
    book = DualFuelBillBook()
    elec = [_elec_inv("2023-01-01", "2023-01-31", total=52.50, status="paid")]
    gas = [_gas_inv("2023-01-01", "2023-01-31", total=82.00, status="paid")]
    bills = book.build_bills("C1", "resi", elec, gas)
    assert bills[0].balance_gbp == pytest.approx(0.0, abs=0.01)

def test_build_bills_balance_negative_when_unpaid():
    book = DualFuelBillBook()
    elec = [_elec_inv("2023-01-01", "2023-01-31", total=52.50, status="unpaid")]
    gas = [_gas_inv("2023-01-01", "2023-01-31", total=82.00, status="unpaid")]
    bills = book.build_bills("C1", "resi", elec, gas)
    assert bills[0].balance_gbp < 0
    assert bills[0].amount_owing_gbp == pytest.approx(134.50, abs=0.01)

def test_build_bills_multiple_months():
    book = DualFuelBillBook()
    elec = [
        _elec_inv("2023-01-01", "2023-01-31", total=52.50),
        _elec_inv("2023-02-01", "2023-02-28", total=48.00),
    ]
    gas = [
        _gas_inv("2023-01-01", "2023-01-31", total=82.00),
        _gas_inv("2023-02-01", "2023-02-28", total=70.00),
    ]
    bills = book.build_bills("C1", "resi", elec, gas)
    assert len(bills) == 2

def test_billing_calendar_resi():
    book = DualFuelBillBook()
    bills = book.build_bills("C1", "resi", [_elec_inv("2023-01-01", "2023-01-31")], [])
    assert bills[0].billing_calendar == "monthly"

def test_billing_calendar_sme():
    book = DualFuelBillBook()
    bills = book.build_bills("C1", "SME", [_elec_inv("2023-01-01", "2023-01-31")], [])
    assert bills[0].billing_calendar == "quarterly"

def test_gas_account_id():
    book = DualFuelBillBook()
    assert book.gas_account_id("C1") == "C1g"
    assert book.gas_account_id("C4") == "C4g"

def test_cumulative_balance_all_paid():
    book = DualFuelBillBook()
    invoices = [
        {"total_gbp": 50.0, "payment_status": "paid"},
        {"total_gbp": 80.0, "payment_status": "paid"},
    ]
    assert book.cumulative_balance_gbp(invoices) == pytest.approx(0.0)

def test_cumulative_balance_partial_payment():
    book = DualFuelBillBook()
    invoices = [
        {"total_gbp": 50.0, "payment_status": "paid"},
        {"total_gbp": 80.0, "payment_status": "unpaid"},
    ]
    assert book.cumulative_balance_gbp(invoices) == pytest.approx(-80.0)

def test_outstanding_invoices():
    book = DualFuelBillBook()
    invoices = [
        {"total_gbp": 50.0, "payment_status": "paid", "invoice_number": 1},
        {"total_gbp": 80.0, "payment_status": "unpaid", "invoice_number": 2},
        {"total_gbp": 30.0, "payment_status": "partially_paid", "invoice_number": 3},
    ]
    outstanding = book.outstanding_invoices(invoices)
    assert len(outstanding) == 2
    assert all(i["payment_status"] in ("unpaid", "partially_paid") for i in outstanding)
