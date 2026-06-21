"""Tests for company.crm.churn_model — observable-data churn estimator."""
import pytest

from company.crm.churn_model import (
    BASE_CHURN_RATE,
    BILL_STRESS_SENSITIVITY,
    BILL_STRESS_THRESHOLD_GBP,
    MAX_CHURN_PROBABILITY,
    RATE_SENSITIVITY,
    TENURE_DISCOUNT_PER_YEAR,
    estimate_churn_probability,
)


def test_flat_rate_no_increase_returns_base_minus_tenure():
    """No rate change: probability = base - tenure_discount."""
    p = estimate_churn_probability(100.0, 100.0, tenure_years=2.0)
    expected = BASE_CHURN_RATE - TENURE_DISCOUNT_PER_YEAR * 2.0
    assert abs(p - expected) < 1e-9


def test_zero_tenure_flat_rate_returns_base():
    """Brand-new customer, no rate change: probability == base rate."""
    p = estimate_churn_probability(100.0, 100.0, tenure_years=0.0)
    assert abs(p - BASE_CHURN_RATE) < 1e-9


def test_rate_increase_raises_probability():
    """A 10% rate increase adds RATE_SENSITIVITY * 0.10 to base probability."""
    p = estimate_churn_probability(100.0, 110.0, tenure_years=0.0)
    expected = BASE_CHURN_RATE + RATE_SENSITIVITY * 0.10
    assert abs(p - expected) < 1e-9


def test_rate_decrease_lowers_probability():
    """A rate decrease can push probability well below base (floored at 0)."""
    p = estimate_churn_probability(110.0, 100.0, tenure_years=0.0)
    rate_change = (100.0 - 110.0) / 110.0  # ~-0.0909
    expected = max(0.0, BASE_CHURN_RATE + RATE_SENSITIVITY * rate_change)
    assert abs(p - expected) < 1e-9


def test_tenure_discount_caps_at_five_years():
    """Tenure discount stops accumulating after 5 years."""
    p_5yr = estimate_churn_probability(100.0, 100.0, tenure_years=5.0)
    p_10yr = estimate_churn_probability(100.0, 100.0, tenure_years=10.0)
    assert abs(p_5yr - p_10yr) < 1e-9


def test_crisis_rate_spike_approaches_max():
    """A massive rate spike (100% increase) should approach MAX_CHURN_PROBABILITY."""
    p = estimate_churn_probability(100.0, 200.0, tenure_years=0.0)
    # 0.10 + 0.8 * 1.0 = 0.90, well below cap
    assert p == pytest.approx(0.90)


def test_extreme_rate_spike_clamps_to_max():
    """Probability is clamped to MAX_CHURN_PROBABILITY regardless of rate spike."""
    p = estimate_churn_probability(100.0, 1000.0, tenure_years=0.0)
    assert p == MAX_CHURN_PROBABILITY


def test_probability_never_below_zero():
    """Probability is clamped at 0.0 even with rate cut + long tenure."""
    p = estimate_churn_probability(200.0, 100.0, tenure_years=5.0)
    assert p >= 0.0


def test_zero_old_rate_does_not_raise():
    """If old rate is 0 (bootstrap edge case), rate_increase_pct defaults to 0."""
    p = estimate_churn_probability(0.0, 100.0, tenure_years=0.0)
    assert p == pytest.approx(BASE_CHURN_RATE)


def test_output_is_float():
    p = estimate_churn_probability(100.0, 120.0, tenure_years=3.0)
    assert isinstance(p, float)


# ── Bill burden signal (Phase 13c) ───────────────────────────────────────────

def test_no_consumption_gives_no_bill_stress():
    """Default annual_consumption_kwh=0 means bill stress term is zero."""
    p_no_kwh = estimate_churn_probability(100.0, 100.0, tenure_years=0.0, annual_consumption_kwh=0.0)
    assert abs(p_no_kwh - BASE_CHURN_RATE) < 1e-9


def test_low_bill_below_threshold_gives_no_stress():
    """Bill below BILL_STRESS_THRESHOLD_GBP adds no stress term."""
    # £100/MWh × 2800 kWh / 1000 = £280/year << £3000 threshold
    p = estimate_churn_probability(100.0, 100.0, tenure_years=0.0, annual_consumption_kwh=2800.0)
    assert abs(p - BASE_CHURN_RATE) < 1e-9


def test_bill_exactly_at_threshold_gives_no_stress():
    """Bill exactly at threshold: max(0, 1-1) = 0, no stress added."""
    kwh = BILL_STRESS_THRESHOLD_GBP * 1000 / 100.0  # at £100/MWh, this is 30,000 kWh
    p = estimate_churn_probability(100.0, 100.0, tenure_years=0.0, annual_consumption_kwh=kwh)
    assert abs(p - BASE_CHURN_RATE) < 1e-9


def test_bill_above_threshold_adds_stress():
    """Bill above threshold raises churn probability."""
    # £100/MWh × 45,000 kWh = £4,500 bill (above £3,000)
    p_with = estimate_churn_probability(100.0, 100.0, tenure_years=0.0, annual_consumption_kwh=45000.0)
    p_without = estimate_churn_probability(100.0, 100.0, tenure_years=0.0, annual_consumption_kwh=0.0)
    assert p_with > p_without


def test_bill_stress_quantified():
    """Verify bill stress formula: SENSITIVITY × (bill/threshold - 1)."""
    # £250/MWh × 45,000 kWh / 1000 = £11,250 prev annual bill
    prev_bill = 250.0 * 45000.0 / 1000.0  # £11,250
    expected_stress = BILL_STRESS_SENSITIVITY * (prev_bill / BILL_STRESS_THRESHOLD_GBP - 1.0)
    # With flat rate (no rate increase), 5yr tenure
    p = estimate_churn_probability(250.0, 250.0, tenure_years=5.0, annual_consumption_kwh=45000.0)
    expected_p = max(0.0, min(MAX_CHURN_PROBABILITY,
        BASE_CHURN_RATE + 0.0 - TENURE_DISCOUNT_PER_YEAR * 5.0 + expected_stress))
    assert abs(p - expected_p) < 1e-9


def test_c6_scenario_falling_rate_high_consumption_detectable():
    """C6 churn failure mode: falling rate + large SME consumption → above 30% threshold.

    C6 in 2024: old_rate ~£250/MWh (crisis-era), new_rate ~£150/MWh (falling),
    45,000 kWh/year. Rate-only model returns 0. With bill burden: detectable.
    """
    p_rate_only = estimate_churn_probability(250.0, 150.0, tenure_years=8.0, annual_consumption_kwh=0.0)
    p_with_burden = estimate_churn_probability(250.0, 150.0, tenure_years=8.0, annual_consumption_kwh=45000.0)
    assert p_rate_only == 0.0, "Rate-only model should return 0 for falling rate + long tenure"
    assert p_with_burden > 0.30, f"Bill burden should push estimate above 30% threshold, got {p_with_burden:.3f}"


def test_small_resi_unaffected_by_bill_burden_in_normal_years():
    """Small resi customer (C1, 2800 kWh) at normal rates: bill stress stays zero."""
    # £60/MWh × 2800 kWh / 1000 = £168 — well below threshold
    p = estimate_churn_probability(60.0, 60.0, tenure_years=0.0, annual_consumption_kwh=2800.0)
    assert abs(p - BASE_CHURN_RATE) < 1e-9


def test_bill_stress_caps_at_max_churn_probability():
    """Extreme bill burden doesn't push probability above MAX_CHURN_PROBABILITY."""
    p = estimate_churn_probability(1000.0, 1000.0, tenure_years=0.0, annual_consumption_kwh=100000.0)
    assert p == MAX_CHURN_PROBABILITY
