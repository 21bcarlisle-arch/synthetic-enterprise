import pytest
from company.billing.dual_fuel_bill import (
    DualFuelBill, FuelBillSection, BILLING_CALENDAR,
)


def _section(paid=True, total=50.0, kwh=500.0):
    return FuelBillSection(
        fuel="electricity",
        period_start="2022-01-01", period_end="2022-01-31",
        days_in_period=31, consumption_kwh=kwh,
        unit_rate_pence=10.0, standing_charge_pence_per_day=50.0,
        standing_charge_gbp=15.5, energy_charge_gbp=50.0,
        levies_gbp=2.0, subtotal_gbp=67.5,
        vat_rate=0.05, vat_gbp=3.375,
        total_gbp=total,
        invoice_number=1,
        payment_status="paid" if paid else "pending",
    )


def _bill(elec=True, gas=True, billed=100.0, paid=100.0, mtype="resi"):
    return DualFuelBill(
        account_id="ACC-001", market_type=mtype,
        billing_period_start="2022-01-01", billing_period_end="2022-01-31",
        electricity=_section() if elec else None,
        gas=_section() if gas else None,
        total_billed_gbp=billed, total_paid_gbp=paid,
    )


def test_is_dual_fuel_both_sections():
    bill = _bill()
    assert bill.is_dual_fuel is True


def test_is_electricity_only():
    bill = _bill(gas=False)
    assert bill.is_electricity_only is True


def test_is_gas_only():
    bill = _bill(elec=False)
    assert bill.is_gas_only is True


def test_balance_gbp_positive_in_credit():
    bill = _bill(billed=80.0, paid=100.0)
    assert bill.balance_gbp == pytest.approx(20.0)


def test_amount_owing_when_deficit():
    bill = _bill(billed=100.0, paid=80.0)
    assert bill.amount_owing_gbp == pytest.approx(20.0)


def test_in_credit_true_positive_balance():
    bill = _bill(billed=80.0, paid=100.0)
    assert bill.in_credit is True


def test_in_credit_false_deficit():
    bill = _bill(billed=100.0, paid=80.0)
    assert bill.in_credit is False


def test_all_paid_true_when_sections_paid():
    bill = _bill()
    assert bill.all_paid is True


def test_billing_calendar_resi_monthly():
    bill = _bill(mtype="resi")
    assert bill.billing_calendar == "monthly"


def test_billing_calendar_sme_quarterly():
    bill = _bill(mtype="SME")
    assert bill.billing_calendar == "quarterly"
