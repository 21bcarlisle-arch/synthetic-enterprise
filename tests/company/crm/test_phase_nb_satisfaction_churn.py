"""Phase NB: Satisfaction score wired into company combined churn model.

Tests combined_churn_probability with satisfaction_score parameter.
Verifies three-signal model: bill_shock + behaviour + satisfaction.
All inputs are company observables -- no SIM ground truth.
"""
import pytest
from company.crm.payment_behaviour_analytics import BehaviourScore
from company.crm.payment_churn_model import (
    CHURN_UPLIFT_BY_SCORE,
    _HIGH_SATISFACTION_THRESHOLD,
    _HIGH_SATISFACTION_UPLIFT,
    _LOW_SATISFACTION_THRESHOLD,
    _LOW_SATISFACTION_UPLIFT,
    _satisfaction_uplift,
    combined_churn_probability,
)
from saas.churn_model import BASE_ANNUAL_CHURN_PROBABILITY, MAX_CHURN_PROBABILITY


def test_satisfaction_none_no_change():
    p1 = combined_churn_probability(0, None, None)
    p2 = combined_churn_probability(0, None)
    assert abs(p1 - p2) < 1e-9


def test_high_satisfaction_suppresses_churn():
    p_none = combined_churn_probability(0, None, None)
    p_high = combined_churn_probability(0, None, 0.85)
    assert p_high < p_none


def test_low_satisfaction_raises_churn():
    p_none = combined_churn_probability(0, None, None)
    p_low = combined_churn_probability(0, None, 0.40)
    assert p_low > p_none


def test_mid_satisfaction_no_change():
    p_none = combined_churn_probability(0, None, None)
    p_mid = combined_churn_probability(0, None, 0.65)
    assert abs(p_mid - p_none) < 1e-9


def test_satisfaction_uplift_low_value():
    assert _satisfaction_uplift(0.40) == _LOW_SATISFACTION_UPLIFT


def test_satisfaction_uplift_high_value():
    assert _satisfaction_uplift(0.85) == _HIGH_SATISFACTION_UPLIFT


def test_satisfaction_uplift_mid_range_zero():
    assert _satisfaction_uplift(0.65) == 0.0


def test_satisfaction_uplift_none_zero():
    assert _satisfaction_uplift(None) == 0.0


def test_satisfaction_uplift_at_low_threshold():
    # at exactly 0.50, which is not < 0.50, should be 0
    assert _satisfaction_uplift(_LOW_SATISFACTION_THRESHOLD) == 0.0


def test_satisfaction_uplift_just_below_low_threshold():
    assert _satisfaction_uplift(_LOW_SATISFACTION_THRESHOLD - 0.01) == _LOW_SATISFACTION_UPLIFT


def test_satisfaction_uplift_at_high_threshold():
    assert _satisfaction_uplift(_HIGH_SATISFACTION_THRESHOLD) == _HIGH_SATISFACTION_UPLIFT


def test_three_signals_stack():
    # all three signals: 2 shocks + POOR + low satisfaction
    p = combined_churn_probability(2, BehaviourScore.POOR, 0.30)
    base = BASE_ANNUAL_CHURN_PROBABILITY + 2 * 0.03  # 2 shocks
    expected = min(base + 0.10 + _LOW_SATISFACTION_UPLIFT, MAX_CHURN_PROBABILITY)
    assert abs(p - expected) < 1e-9


def test_three_signals_cap_at_095():
    p = combined_churn_probability(100, BehaviourScore.CRITICAL, 0.10)
    assert p == MAX_CHURN_PROBABILITY


def test_excellent_behaviour_and_high_satisfaction_suppresses():
    p = combined_churn_probability(0, BehaviourScore.EXCELLENT, 0.90)
    assert p < BASE_ANNUAL_CHURN_PROBABILITY


def test_poor_behaviour_and_low_satisfaction_highest_risk():
    p_poor_low = combined_churn_probability(3, BehaviourScore.POOR, 0.30)
    p_base = combined_churn_probability(3, None, None)
    assert p_poor_low > p_base


def test_satisfaction_backward_compatible_with_phase_my():
    # calling with only two args still works
    import inspect
    from company.crm.payment_churn_model import combined_churn_probability as cp
    sig = inspect.signature(cp)
    assert "satisfaction_score" in sig.parameters
    assert sig.parameters["satisfaction_score"].default is None
