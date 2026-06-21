"""Tests for ToU period classification and tariff pricing."""

import pytest
from simulation.tou_periods import is_peak_period, period_start_time
from saas.tariff_pricing import price_tou_tariff, price_fixed_tariff, TOU_PEAK_MULTIPLIER, TOU_OFFPEAK_MULTIPLIER


# ── is_peak_period ────────────────────────────────────────────────────────────

def test_morning_peak_weekday():
    # Period 15 = 07:00-07:30, Monday 2022-09-05
    assert is_peak_period("2022-09-05", 15) is True


def test_evening_peak_weekday():
    # Period 33 = 16:00-16:30, Monday
    assert is_peak_period("2022-09-05", 33) is True


def test_off_peak_night():
    # Period 1 = 00:00, always off-peak
    assert is_peak_period("2022-09-05", 1) is False


def test_off_peak_weekend_morning_peak_hours():
    # Period 15 on Saturday — weekends are always off-peak
    assert is_peak_period("2022-09-10", 15) is False  # Saturday


def test_off_peak_weekend_evening():
    assert is_peak_period("2022-09-11", 33) is False  # Sunday


def test_shoulder_period_is_off_peak():
    # Period 23 = 11:00-11:30, outside peak windows
    assert is_peak_period("2022-09-05", 23) is False


def test_last_morning_peak_period():
    # Period 22 = 10:30-11:00, still in morning peak
    assert is_peak_period("2022-09-05", 22) is True


def test_first_period_after_morning_peak():
    # Period 23 = 11:00, no longer peak
    assert is_peak_period("2022-09-05", 23) is False


def test_last_evening_peak_period():
    # Period 40 = 19:30-20:00
    assert is_peak_period("2022-09-05", 40) is True


def test_first_period_after_evening_peak():
    # Period 41 = 20:00-20:30
    assert is_peak_period("2022-09-05", 41) is False


def test_period_start_time():
    import datetime
    assert period_start_time(1) == datetime.time(0, 0)
    assert period_start_time(15) == datetime.time(7, 0)
    assert period_start_time(33) == datetime.time(16, 0)
    assert period_start_time(48) == datetime.time(23, 30)


# ── price_tou_tariff ──────────────────────────────────────────────────────────

def test_tou_tariff_returns_two_rates():
    rates = price_tou_tariff(50.0, 3000, "2020-01-01")
    assert len(rates) == 2
    peak, offpeak = rates
    assert peak > offpeak


def test_tou_peak_rate_above_flat():
    flat = price_fixed_tariff(50.0, 3000, "2020-01-01")
    peak, _ = price_tou_tariff(50.0, 3000, "2020-01-01")
    assert peak > flat


def test_tou_offpeak_rate_below_flat():
    flat = price_fixed_tariff(50.0, 3000, "2020-01-01")
    _, offpeak = price_tou_tariff(50.0, 3000, "2020-01-01")
    assert offpeak < flat


def test_tou_rates_are_multiples_of_flat():
    flat = price_fixed_tariff(50.0, 3000, "2020-01-01")
    peak, offpeak = price_tou_tariff(50.0, 3000, "2020-01-01")
    assert abs(peak - flat * TOU_PEAK_MULTIPLIER) < 1e-9
    assert abs(offpeak - flat * TOU_OFFPEAK_MULTIPLIER) < 1e-9


def test_tou_revenue_neutral_at_30_70_split():
    """Weighted average at 30% peak / 70% off-peak should equal the flat rate."""
    flat = price_fixed_tariff(50.0, 3000, "2020-01-01")
    peak, offpeak = price_tou_tariff(50.0, 3000, "2020-01-01")
    weighted = 0.30 * peak + 0.70 * offpeak
    assert abs(weighted - flat) < 1e-6


# ── ToU in hedged_settlement ──────────────────────────────────────────────────

def test_tou_rates_applied_per_period():
    """With tou_rates, peak periods get peak rate and off-peak get offpeak rate."""
    from simulation.hedged_settlement import run_hedged_term
    from simulation.tou_periods import is_peak_period

    flat = 50.0
    peak_r, offpeak_r = flat * 1.5, flat * 0.786

    # Minimal stub: one weekday with synthetic price records
    date_str = "2022-09-05"  # Monday
    records_stub = [
        {"settlementDate": date_str, "settlementPeriod": p, "systemSellPrice": 60.0}
        for p in range(1, 49)
    ]
    shape_stub = lambda d: [0.5] * 48  # 0.5 kWh per period

    result = run_hedged_term(
        "C7", date_str, "2022-09-06",
        flat, 50.0, 0.85, 0.0,
        shape_stub, records_stub,
        tou_rates=(peak_r, offpeak_r),
    )

    for rec in result:
        period = rec["settlement_period"]
        expected_rate = peak_r if is_peak_period(date_str, period) else offpeak_r
        assert abs(rec["unit_rate_gbp_per_mwh"] - expected_rate) < 1e-9, (
            f"Period {period}: expected {expected_rate:.4f}, got {rec['unit_rate_gbp_per_mwh']:.4f}"
        )
