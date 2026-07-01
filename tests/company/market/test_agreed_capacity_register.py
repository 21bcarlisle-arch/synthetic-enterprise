"""Tests for company/market/agreed_capacity_register.py (Sprint CL)."""
import datetime as dt
import pytest

from company.market.agreed_capacity_register import (
    AgreedCapacityRegister,
    CapacityChangeType,
    CapacityChangeStatus,
)

DATE = dt.date(2022, 6, 1)


def _reg():
    return AgreedCapacityRegister()


def test_record_id_starts_with_agcap():
    reg = _reg()
    r = reg.register_capacity("M1", "LPN", DATE, 500.0, CapacityChangeType.INITIAL_REGISTRATION)
    assert r.record_id.startswith("AGCAP-")


def test_mpan_stored():
    reg = _reg()
    r = reg.register_capacity("M1", "LPN", DATE, 500.0, CapacityChangeType.INITIAL_REGISTRATION)
    assert r.mpan == "M1"


def test_agreed_capacity_stored():
    reg = _reg()
    r = reg.register_capacity("M1", "LPN", DATE, 750.0, CapacityChangeType.INITIAL_REGISTRATION)
    assert r.agreed_capacity_kva == 750.0


def test_zero_capacity_raises():
    reg = _reg()
    with pytest.raises(ValueError):
        reg.register_capacity("M1", "LPN", DATE, 0.0, CapacityChangeType.INITIAL_REGISTRATION)


def test_is_applied_true_by_default():
    reg = _reg()
    r = reg.register_capacity("M1", "LPN", DATE, 500.0, CapacityChangeType.INITIAL_REGISTRATION)
    assert r.is_applied is True


def test_is_reduction_true_when_capacity_decreases():
    reg = _reg()
    r = reg.register_capacity("M1", "LPN", DATE, 400.0, CapacityChangeType.CUSTOMER_REDUCTION,
                               previous_capacity_kva=500.0)
    assert r.is_reduction is True


def test_capacity_change_kva_computed():
    reg = _reg()
    r = reg.register_capacity("M1", "LPN", DATE, 400.0, CapacityChangeType.CUSTOMER_REDUCTION,
                               previous_capacity_kva=500.0)
    assert abs(r.capacity_change_kva - (-100.0)) < 0.01


def test_record_exceedance_and_excess_charge():
    reg = _reg()
    e = reg.record_exceedance("M1", DATE, 500.0, 600.0, 2.5)
    assert e.excess_kva == 100.0
    assert abs(e.excess_charge_gbp - 100.0 * 2.5 * 3.0) < 0.01


def test_current_capacity_for_mpan():
    reg = _reg()
    reg.register_capacity("M1", "LPN", DATE, 500.0, CapacityChangeType.INITIAL_REGISTRATION)
    assert reg.current_capacity_for("M1") == 500.0


def test_total_excess_charge_sums_exceedances():
    reg = _reg()
    reg.record_exceedance("M1", DATE, 100.0, 120.0, 2.0)
    reg.record_exceedance("M1", DATE, 100.0, 130.0, 2.0)
    total = reg.total_excess_charge_gbp()
    assert total > 0.0
