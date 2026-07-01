"""Tests for company/billing/breathing_space_register.py (Sprint CXLIX)."""
import datetime as dt
import pytest

from company.billing.breathing_space_register import (
    BreathingSpaceRegister,
    BreathingSpaceRecord,
    BreathingSpaceType,
    BreathingSpaceStatus,
)

START = dt.date(2022, 6, 1)


def _reg():
    return BreathingSpaceRegister()


def test_record_id_starts_with_bs():
    reg = _reg()
    r = reg.register_entry("C1", BreathingSpaceType.STANDARD, START, 200.0)
    assert r.record_id.startswith("BS-")


def test_account_id_stored():
    reg = _reg()
    r = reg.register_entry("C1", BreathingSpaceType.STANDARD, START, 200.0)
    assert r.account_id == "C1"


def test_bs_type_stored():
    reg = _reg()
    r = reg.register_entry("C1", BreathingSpaceType.MENTAL_HEALTH_CRISIS, START, 100.0)
    assert r.bs_type == BreathingSpaceType.MENTAL_HEALTH_CRISIS


def test_debt_frozen_stored():
    reg = _reg()
    r = reg.register_entry("C1", BreathingSpaceType.STANDARD, START, 350.0)
    assert r.debt_frozen_gbp == 350.0


def test_standard_expected_end_date_60_days():
    reg = _reg()
    r = reg.register_entry("C1", BreathingSpaceType.STANDARD, START, 100.0)
    assert r.expected_end_date == START + dt.timedelta(days=60)


def test_mh_crisis_expected_end_date_none():
    reg = _reg()
    r = reg.register_entry("C1", BreathingSpaceType.MENTAL_HEALTH_CRISIS, START, 100.0)
    assert r.expected_end_date is None


def test_is_active_within_60_days():
    reg = _reg()
    r = reg.register_entry("C1", BreathingSpaceType.STANDARD, START, 100.0)
    assert r.is_active_as_of(START + dt.timedelta(days=30)) is True


def test_is_not_active_after_60_days():
    reg = _reg()
    r = reg.register_entry("C1", BreathingSpaceType.STANDARD, START, 100.0)
    assert r.is_active_as_of(START + dt.timedelta(days=61)) is False


def test_days_remaining_positive_within_period():
    reg = _reg()
    r = reg.register_entry("C1", BreathingSpaceType.STANDARD, START, 100.0)
    remaining = r.days_remaining(START + dt.timedelta(days=10))
    assert remaining == 50


def test_pre_scheme_date_raises():
    reg = _reg()
    with pytest.raises(ValueError, match="scheme started"):
        reg.register_entry("C1", BreathingSpaceType.STANDARD, dt.date(2020, 1, 1), 100.0)
