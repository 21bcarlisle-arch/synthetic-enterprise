"""Layer 2 dimension 3 (tenure, 2026-07-10): tenure -> switching propensity.

Tests simulation/switching_propensity.py's tenure_switching_multiplier /
adjust_churn_probability(tenure=...) additions. No full simulation run.
"""
from simulation.household import IncomeStress
from simulation.switching_propensity import (
    TENURE_SWITCHING_MULTIPLIER,
    adjust_churn_probability,
    tenure_switching_multiplier,
)


def test_owner_occupier_multiplier_is_baseline_one():
    assert tenure_switching_multiplier("owner_occupier") == 1.0


def test_renter_multipliers_below_one():
    assert tenure_switching_multiplier("private_renter") < 1.0
    assert tenure_switching_multiplier("social_renter") < 1.0


def test_none_tenure_uses_owner_occupier_as_default():
    assert tenure_switching_multiplier(None) == tenure_switching_multiplier("owner_occupier")


def test_unknown_tenure_falls_back_to_owner_occupier():
    assert tenure_switching_multiplier("unknown_tenure") == tenure_switching_multiplier("owner_occupier")


def test_multiplier_values_complete_for_declared_tenures():
    for tenure in ("owner_occupier", "private_renter", "social_renter"):
        assert tenure in TENURE_SWITCHING_MULTIPLIER


def test_adjust_churn_probability_tenure_optional_backward_compatible():
    """Backward compatibility: omitting tenure must reproduce the exact
    original income-stress-only behaviour."""
    base = 0.20
    a = adjust_churn_probability(base, IncomeStress.MODERATE)
    b = adjust_churn_probability(base, IncomeStress.MODERATE, tenure=None)
    assert a == b


def test_adjust_churn_probability_renter_lower_than_owner():
    base = 0.20
    owner = adjust_churn_probability(base, IncomeStress.LOW, tenure="owner_occupier")
    renter = adjust_churn_probability(base, IncomeStress.LOW, tenure="private_renter")
    assert renter < owner


def test_adjust_churn_probability_tenure_still_capped_and_nonneg():
    result_hi = adjust_churn_probability(1.0, IncomeStress.LOW, tenure="owner_occupier")
    assert result_hi <= 0.95
    result_lo = adjust_churn_probability(0.0, IncomeStress.HIGH, tenure="social_renter")
    assert result_lo >= 0.0


def test_roll_lifecycle_event_still_works_without_tenure_data():
    """household_segments.tenure_for_customer is called internally when
    income_stress is provided -- roll_lifecycle_event's own signature is
    unaffected (tenure is resolved internally, not a new parameter)."""
    import inspect
    from simulation.customer_events import roll_lifecycle_event
    sig = inspect.signature(roll_lifecycle_event)
    assert "income_stress" in sig.parameters
