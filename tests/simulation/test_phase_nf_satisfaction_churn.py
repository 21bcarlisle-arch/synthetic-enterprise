"""Phase NF -- Gap 3 Dim 4 SIM-side: Satisfaction -> Actual Churn Probability.

Tests for simulation/sim_satisfaction.py and simulation/satisfaction_churn.py.
Verifies the SIM-side ground-truth satisfaction score drives actual churn probability
via roll_lifecycle_event, analogous to Phase MZ income_stress wiring.
"""
import pytest
from simulation.sim_satisfaction import (
    BASELINE_SATISFACTION,
    _BILL_SHOCK_DELTA,
    _INCOME_STRESS_DELTA,
    _MAX_TENURE_BONUS,
    _TENURE_BONUS_PER_YEAR,
    sim_satisfaction_score,
)
from simulation.satisfaction_churn import (
    _HIGH_SATISFACTION_MULTIPLIER,
    _HIGH_SATISFACTION_THRESHOLD,
    _LOW_SATISFACTION_MULTIPLIER,
    _LOW_SATISFACTION_THRESHOLD,
    adjust_churn_for_satisfaction,
    satisfaction_churn_multiplier,
)
from simulation.household import IncomeStress
from saas.churn_model import MAX_CHURN_PROBABILITY


def test_baseline_no_shocks_no_stress():
    score = sim_satisfaction_score(0, 0.0, None)
    assert score == pytest.approx(BASELINE_SATISFACTION)


def test_single_bill_shock_reduces_satisfaction():
    score = sim_satisfaction_score(1, 0.0, None)
    assert score == pytest.approx(BASELINE_SATISFACTION + _BILL_SHOCK_DELTA)


def test_multiple_shocks_accumulate():
    score = sim_satisfaction_score(3, 0.0, None)
    assert score == pytest.approx(BASELINE_SATISFACTION + 3 * _BILL_SHOCK_DELTA)


def test_satisfaction_clamped_at_zero():
    score = sim_satisfaction_score(100, 0.0, None)
    assert score == 0.0


def test_satisfaction_clamped_at_one():
    score = sim_satisfaction_score(0, 1000.0, None)
    assert score == pytest.approx(BASELINE_SATISFACTION + _MAX_TENURE_BONUS)


def test_tenure_bonus_increases_satisfaction():
    no_tenure = sim_satisfaction_score(0, 0.0, None)
    with_tenure = sim_satisfaction_score(0, 5.0, None)
    assert with_tenure > no_tenure


def test_tenure_bonus_capped_at_max():
    score_5yr = sim_satisfaction_score(0, 5.0, None)
    score_100yr = sim_satisfaction_score(0, 100.0, None)
    assert abs(score_5yr - score_100yr) < 1e-6


def test_tenure_max_bonus_value():
    max_bonus = _MAX_TENURE_BONUS
    threshold_years = max_bonus / _TENURE_BONUS_PER_YEAR
    score = sim_satisfaction_score(0, threshold_years + 1, None)
    expected = min(1.0, BASELINE_SATISFACTION + max_bonus)
    assert score == pytest.approx(expected)


def test_income_stress_high_reduces_satisfaction():
    low = sim_satisfaction_score(0, 0.0, IncomeStress.LOW)
    high = sim_satisfaction_score(0, 0.0, IncomeStress.HIGH)
    assert high < low


def test_income_stress_low_no_delta():
    score_none = sim_satisfaction_score(0, 0.0, None)
    score_low = sim_satisfaction_score(0, 0.0, IncomeStress.LOW)
    assert score_low == pytest.approx(score_none + _INCOME_STRESS_DELTA[IncomeStress.LOW])


def test_satisfaction_multiplier_high_is_below_one():
    assert _HIGH_SATISFACTION_MULTIPLIER < 1.0


def test_satisfaction_multiplier_low_is_above_one():
    assert _LOW_SATISFACTION_MULTIPLIER > 1.0


def test_satisfaction_churn_multiplier_high():
    mult = satisfaction_churn_multiplier(_HIGH_SATISFACTION_THRESHOLD)
    assert mult == _HIGH_SATISFACTION_MULTIPLIER


def test_satisfaction_churn_multiplier_low():
    mult = satisfaction_churn_multiplier(_LOW_SATISFACTION_THRESHOLD - 0.01)
    assert mult == _LOW_SATISFACTION_MULTIPLIER


def test_adjust_churn_high_satisfaction_suppresses():
    base = 0.20
    adjusted = adjust_churn_for_satisfaction(base, _HIGH_SATISFACTION_THRESHOLD)
    assert adjusted < base


def test_adjust_churn_low_satisfaction_raises_capped_at_max():
    base = 0.80
    adjusted = adjust_churn_for_satisfaction(base, _LOW_SATISFACTION_THRESHOLD - 0.01)
    assert adjusted <= MAX_CHURN_PROBABILITY
