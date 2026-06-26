import pytest
from datetime import date
from company.billing.exit_fee import (
    ExitFeeResult, ExitFeeWaiveReason, NOTICE_PERIOD_DAYS, calculate_exit_fee
)


def test_fee_charged_outside_notice_period():
    # 90 days remaining, well outside 42-day window
    r = calculate_exit_fee("C1", date(2022, 12, 31), date(2022, 10, 1), 3500.0)
    assert not r.waived
    assert r.fee_gbp > 0


def test_fee_waived_within_notice_period():
    # 30 days remaining -> within 42-day window
    r = calculate_exit_fee("C1", date(2022, 12, 31), date(2022, 12, 1), 3500.0)
    assert r.waived
    assert r.waive_reason == ExitFeeWaiveReason.WITHIN_NOTICE_PERIOD
    assert r.fee_gbp == 0.0


def test_fee_waived_exactly_at_notice_boundary():
    # Exactly 42 days remaining -> waived (<=42)
    r = calculate_exit_fee("C1", date(2022, 12, 31), date(2022, 11, 19), 3500.0)
    assert r.days_remaining == 42
    assert r.waived


def test_fee_charged_just_outside_notice_period():
    # 43 days -> not waived
    r = calculate_exit_fee("C1", date(2022, 12, 31), date(2022, 11, 18), 3500.0)
    assert r.days_remaining == 43
    assert not r.waived


def test_fee_waived_when_contract_expired():
    # Exit date after contract end
    r = calculate_exit_fee("C1", date(2022, 6, 30), date(2022, 9, 1), 3500.0)
    assert r.waived
    assert r.waive_reason == ExitFeeWaiveReason.CONTRACT_EXPIRED
    assert r.fee_gbp == 0.0


def test_fee_calculation_elec():
    # 90 days remaining, 3500 kWh/yr, 1.5p/kWh
    # fee = 90/365 * 3500 * 0.015 = GBP 12.91
    r = calculate_exit_fee("C1", date(2022, 12, 31), date(2022, 10, 2), 3500.0, "electricity")
    expected = round(90 / 365 * 3500 * 0.015, 2)
    assert abs(r.fee_gbp - expected) < 0.01


def test_fee_calculation_gas():
    # gas rate is 1.0p/kWh vs electricity 1.5p
    r_elec = calculate_exit_fee("C1", date(2022, 12, 31), date(2022, 10, 2), 3500.0, "electricity")
    r_gas = calculate_exit_fee("C1", date(2022, 12, 31), date(2022, 10, 2), 3500.0, "gas")
    assert r_gas.fee_gbp < r_elec.fee_gbp


def test_manual_waive_reason():
    r = calculate_exit_fee(
        "C1", date(2022, 12, 31), date(2022, 10, 1), 3500.0,
        waive_reason=ExitFeeWaiveReason.CUSTOMER_DEATH
    )
    assert r.waived
    assert r.waive_reason == ExitFeeWaiveReason.CUSTOMER_DEATH
    assert r.fee_gbp == 0.0


def test_days_remaining_in_result():
    r = calculate_exit_fee("C1", date(2022, 12, 31), date(2022, 10, 1), 3500.0)
    assert r.days_remaining == 91


def test_zero_days_remaining_at_expiry():
    r = calculate_exit_fee("C1", date(2022, 12, 31), date(2022, 12, 31), 3500.0)
    assert r.days_remaining == 0
    assert r.waived
