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


# --- Phase KY depth tests ---

def test_customer_id_stored():
    r = calculate_exit_fee('C_KY', date(2023, 12, 31), date(2023, 6, 1), 3600.0)
    assert r.customer_id == 'C_KY'


def test_contract_end_date_stored():
    r = calculate_exit_fee('C1', date(2023, 12, 31), date(2023, 6, 1), 3600.0)
    assert r.contract_end_date == date(2023, 12, 31)


def test_exit_date_stored():
    r = calculate_exit_fee('C1', date(2023, 12, 31), date(2023, 6, 1), 3600.0)
    assert r.exit_date == date(2023, 6, 1)


def test_days_remaining_calculation():
    end = date(2023, 12, 31)
    exit_d = date(2023, 6, 1)
    r = calculate_exit_fee('C1', end, exit_d, 3600.0)
    assert r.days_remaining == (end - exit_d).days


def test_fee_gbp_is_float():
    r = calculate_exit_fee('C1', date(2023, 12, 31), date(2023, 6, 1), 3600.0)
    assert isinstance(r.fee_gbp, float)


def test_waived_is_bool():
    r = calculate_exit_fee('C1', date(2023, 12, 31), date(2023, 6, 1), 3600.0)
    assert isinstance(r.waived, bool)


def test_waive_reason_none_when_charged():
    r = calculate_exit_fee('C1', date(2023, 12, 31), date(2023, 6, 1), 3600.0)
    assert r.waive_reason is None


def test_notice_period_days_constant():
    assert NOTICE_PERIOD_DAYS == 42


def test_gas_fee_lower_than_elec_same_consumption():
    end = date(2023, 12, 31)
    exit_d = date(2023, 6, 1)
    elec = calculate_exit_fee('C1', end, exit_d, 3600.0, 'electricity')
    gas = calculate_exit_fee('C1', end, exit_d, 3600.0, 'gas')
    assert gas.fee_gbp < elec.fee_gbp


def test_fee_zero_when_supplier_breach():
    r = calculate_exit_fee('C1', date(2023, 12, 31), date(2023, 6, 1), 3600.0,
                           waive_reason=ExitFeeWaiveReason.SUPPLIER_BREACH)
    assert r.fee_gbp == pytest.approx(0.0)
    assert r.waived is True
