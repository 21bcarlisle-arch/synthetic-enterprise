"""Tests for company/regulatory/green_gas_levy_register.py (Sprint CLIII)."""
import datetime as dt
import pytest

from company.regulatory.green_gas_levy_register import (
    GreenGasLevyRegister,
    GGLPaymentStatus,
)


def _reg():
    return GreenGasLevyRegister()


def test_total_levy_computed():
    reg = _reg()
    ob = reg.record_obligation(2022, 1, 100, rate_gbp_per_meter_per_day=0.001, days_in_quarter=90)
    assert abs(ob.total_levy_gbp - 100 * 0.001 * 90) < 0.001


def test_quarter_label_contains_year():
    reg = _reg()
    ob = reg.record_obligation(2022, 2, 100)
    assert "2022" in ob.quarter_label


def test_payment_due_date_is_28d_after_quarter_end():
    reg = _reg()
    ob = reg.record_obligation(2022, 1, 100)
    assert ob.payment_due_date == dt.date(2022, 3, 31) + dt.timedelta(days=28)


def test_is_overdue_when_past_due_date():
    reg = _reg()
    ob = reg.record_obligation(2022, 1, 100)
    assert ob.is_overdue(dt.date(2022, 6, 1)) is True


def test_is_not_overdue_before_due_date():
    reg = _reg()
    ob = reg.record_obligation(2022, 1, 100)
    assert ob.is_overdue(dt.date(2022, 3, 15)) is False


def test_mark_paid_is_paid():
    reg = _reg()
    reg.record_obligation(2022, 1, 100)
    reg.mark_paid(2022, 1)
    assert reg.is_paid(2022, 1) is True


def test_unpaid_obligations_excludes_paid():
    reg = _reg()
    reg.record_obligation(2022, 1, 100)
    reg.record_obligation(2022, 2, 100)
    reg.mark_paid(2022, 1)
    unpaid = reg.unpaid_obligations()
    assert len(unpaid) == 1
    assert unpaid[0].quarter == 2


def test_pre_ggl_date_raises():
    reg = _reg()
    with pytest.raises(ValueError):
        reg.record_obligation(2021, 3, 100)


def test_annual_levy_sums_for_year():
    reg = _reg()
    reg.record_obligation(2022, 1, 100, rate_gbp_per_meter_per_day=0.001, days_in_quarter=90)
    reg.record_obligation(2022, 2, 100, rate_gbp_per_meter_per_day=0.001, days_in_quarter=91)
    annual = reg.annual_levy_gbp(2022)
    expected = 100 * 0.001 * (90 + 91)
    assert abs(annual - expected) < 0.001


def test_obligations_for_year_filters():
    reg = _reg()
    reg.record_obligation(2022, 1, 100)
    reg.record_obligation(2023, 1, 100)
    assert len(reg.obligations_for_year(2022)) == 1
