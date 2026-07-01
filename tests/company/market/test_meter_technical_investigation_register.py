import datetime as dt
import pytest
from company.market.meter_technical_investigation_register import (
    MeterTechnicalInvestigationRegister, Fuel, MeterTestType, MeterTestOutcome, MTIStatus,
)

DATE = dt.date(2022, 5, 1)


def _reg(fuel=None):
    r = MeterTechnicalInvestigationRegister()
    r.commission_investigation("ACC-001", "MPAN-111", fuel or Fuel.ELECTRICITY,
                               MeterTestType.IN_SITU, DATE)
    return r


def test_reference_prefix():
    reg = _reg()
    assert reg._records[0].reference.startswith("MTI-")


def test_status_default_commissioned():
    reg = _reg()
    assert reg._records[0].status == MTIStatus.COMMISSIONED


def test_electricity_within_tolerance_charges_150():
    reg = _reg(Fuel.ELECTRICITY)
    ref = reg._records[0].reference
    updated = reg.record_outcome(ref, MeterTestOutcome.WITHIN_TOLERANCE, DATE, 0.5)
    assert updated.customer_charge_gbp == 150.0


def test_gas_within_tolerance_no_charge():
    reg = _reg(Fuel.GAS)
    ref = reg._records[0].reference
    updated = reg.record_outcome(ref, MeterTestOutcome.WITHIN_TOLERANCE, DATE, 0.8)
    assert updated.customer_charge_gbp == 0.0


def test_outside_tolerance_rebill_required():
    reg = _reg()
    ref = reg._records[0].reference
    updated = reg.record_outcome(ref, MeterTestOutcome.OUTSIDE_TOLERANCE, DATE, -3.0, rebill_period_days=365)
    assert updated.rebill_required is True


def test_outside_tolerance_stores_rebill_period():
    reg = _reg()
    ref = reg._records[0].reference
    updated = reg.record_outcome(ref, MeterTestOutcome.OUTSIDE_TOLERANCE, DATE, -3.0, rebill_period_days=180)
    assert updated.rebill_period_days == 180


def test_within_tolerance_no_rebill():
    reg = _reg()
    ref = reg._records[0].reference
    updated = reg.record_outcome(ref, MeterTestOutcome.WITHIN_TOLERANCE, DATE, 0.5, rebill_period_days=365)
    assert updated.rebill_period_days == 0


def test_outcome_due_date_20wd():
    reg = _reg()
    r = reg._records[0]
    due = r.outcome_due_date
    assert (due - DATE).days >= 20


def test_total_customer_charges_sums_completed():
    reg = _reg(Fuel.ELECTRICITY)
    reg.commission_investigation("ACC-002", "MPAN-222", Fuel.ELECTRICITY,
                                 MeterTestType.REMOVED_TO_LAB, DATE)
    for i, ref in enumerate([r.reference for r in reg._records]):
        reg.record_outcome(ref, MeterTestOutcome.WITHIN_TOLERANCE, DATE, 0.1)
    assert reg.total_customer_charges_gbp == 300.0


def test_accuracy_dispute_rate_none_empty():
    reg = MeterTechnicalInvestigationRegister()
    assert reg.accuracy_dispute_rate_pct() is None
