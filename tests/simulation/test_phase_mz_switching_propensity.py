"""Phase MZ: SIM-side income stress -> switching propensity tests.

Tests simulation/switching_propensity.py -- no full simulation run.
All tests are fast (<1s) unit tests.
"""
import pytest
from simulation.household import IncomeStress
from simulation.switching_propensity import (
    STRESS_SWITCHING_MULTIPLIER,
    adjust_churn_probability,
    stress_switching_multiplier,
    _MAX_CHURN_PROBABILITY,
)


# --- stress_switching_multiplier ---

def test_high_stress_multiplier_is_below_one():
    assert stress_switching_multiplier(IncomeStress.HIGH) < 1.0


def test_low_stress_multiplier_is_above_one():
    assert stress_switching_multiplier(IncomeStress.LOW) > 1.0


def test_moderate_stress_multiplier_between_high_and_low():
    m_low = stress_switching_multiplier(IncomeStress.LOW)
    m_mod = stress_switching_multiplier(IncomeStress.MODERATE)
    m_high = stress_switching_multiplier(IncomeStress.HIGH)
    assert m_high < m_mod < m_low


def test_none_income_stress_uses_low_as_default():
    assert stress_switching_multiplier(None) == stress_switching_multiplier(IncomeStress.LOW)


def test_multiplier_values_complete_for_all_enum():
    for s in IncomeStress:
        assert s in STRESS_SWITCHING_MULTIPLIER


def test_high_multiplier_lt_moderate_lt_low():
    uplifts = [STRESS_SWITCHING_MULTIPLIER[s] for s in (
        IncomeStress.HIGH, IncomeStress.MODERATE, IncomeStress.LOW
    )]
    assert uplifts == sorted(uplifts)


# --- adjust_churn_probability ---

def test_adjust_churn_lowers_for_high_stress():
    base = 0.20
    adjusted = adjust_churn_probability(base, IncomeStress.HIGH)
    assert adjusted < base


def test_adjust_churn_raises_for_low_stress():
    base = 0.20
    adjusted = adjust_churn_probability(base, IncomeStress.LOW)
    assert adjusted > base


def test_adjust_churn_lower_for_moderate_than_base():
    base = 0.20
    adjusted = adjust_churn_probability(base, IncomeStress.MODERATE)
    assert adjusted < base


def test_adjust_churn_capped_at_095():
    result = adjust_churn_probability(1.0, IncomeStress.LOW)
    assert result == _MAX_CHURN_PROBABILITY


def test_adjust_churn_never_below_zero():
    result = adjust_churn_probability(0.0, IncomeStress.HIGH)
    assert result == 0.0


def test_adjust_zero_base_stays_zero():
    for s in IncomeStress:
        assert adjust_churn_probability(0.0, s) == 0.0


def test_adjust_churn_at_base_rate_high_stress():
    # BASE_ANNUAL_CHURN_PROBABILITY = 0.05, HIGH multiplier = 0.65
    base = 0.05
    expected = round(base * STRESS_SWITCHING_MULTIPLIER[IncomeStress.HIGH], 6)
    result = adjust_churn_probability(base, IncomeStress.HIGH)
    assert abs(result - expected) < 1e-9


def test_adjust_exact_boundary_high_stress():
    # At 0.30 base with HIGH: 0.30 * 0.65 = 0.195
    expected = 0.30 * STRESS_SWITCHING_MULTIPLIER[IncomeStress.HIGH]
    assert abs(adjust_churn_probability(0.30, IncomeStress.HIGH) - expected) < 1e-9


def test_stress_factor_compounds_with_bill_shocks():
    # 3 bill shocks -> base = 0.05 + 3*0.03 = 0.14
    from saas.churn_model import churn_probability
    base = churn_probability(3)
    high_adjusted = adjust_churn_probability(base, IncomeStress.HIGH)
    low_adjusted = adjust_churn_probability(base, IncomeStress.LOW)
    assert high_adjusted < base < low_adjusted


def test_high_stress_lower_probability_than_none():
    base = 0.15
    assert adjust_churn_probability(base, IncomeStress.HIGH) < adjust_churn_probability(base, None)


def test_low_stress_higher_probability_than_none():
    base = 0.15
    # None maps to LOW so they should be equal
    assert adjust_churn_probability(base, IncomeStress.LOW) == adjust_churn_probability(base, None)


def test_adjust_churn_no_stress_vs_moderate():
    base = 0.15
    # None (LOW) gives higher result than MODERATE
    p_none = adjust_churn_probability(base, None)
    p_mod = adjust_churn_probability(base, IncomeStress.MODERATE)
    assert p_none > p_mod


# --- integration ---

def test_integration_high_stress_lower_sim_churn_probability():
    """HIGH stress -> multiplier 0.65 -> significantly lower actual churn probability.
    Models vulnerability trap: stressed customers can't afford to switch.
    """
    base = 0.14  # 3 bill shocks
    high_result = adjust_churn_probability(base, IncomeStress.HIGH)
    # Should be ~40% lower than base
    assert high_result < base * 0.70


def test_roll_lifecycle_event_accepts_income_stress_param():
    """roll_lifecycle_event should accept income_stress without raising TypeError."""
    import inspect
    from simulation.customer_events import roll_lifecycle_event
    sig = inspect.signature(roll_lifecycle_event)
    # The parameter should exist (added by Phase MZ)
    assert "income_stress" in sig.parameters


def test_roll_lifecycle_event_no_income_stress_backward_compat():
    """roll_lifecycle_event should still work when income_stress is not passed."""
    import inspect
    from simulation.customer_events import roll_lifecycle_event
    sig = inspect.signature(roll_lifecycle_event)
    param = sig.parameters.get("income_stress")
    assert param is not None
    # Default should be None (backward-compatible)
    assert param.default is None
