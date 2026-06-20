"""Tests for company.crm.churn_model — observable-data churn estimator."""
import pytest
from company.crm.churn_model import (
    BASE_CHURN_RATE,
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
