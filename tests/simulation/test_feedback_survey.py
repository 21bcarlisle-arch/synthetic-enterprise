"""Phase RU -- FEEDBACK_AND_REPUTATION.md Layer 1: solicited feedback survey engine.

Tests for simulation/feedback_survey.py: response propensity shape, deterministic
dispatch, and complaint occurrence/resolution-timing bands.
"""
import pytest

from simulation.feedback_survey import (
    BASE_RESPONSE_RATE,
    HIGH_SATISFACTION_THRESHOLD,
    LOW_SATISFACTION_THRESHOLD,
    COMPLAINT_BASE_PROBABILITY,
    BILL_SHOCK_COMPLAINT_PENALTY,
    ON_TIME_DAYS_MAX,
    response_propensity,
    dispatch_csat_survey,
    dispatch_nps_survey,
    dispatch_complaint_and_resolution,
)
from simulation.household import IncomeStress
from company.core.reputation_index import ReputationEventType


def test_response_propensity_is_u_shaped():
    mid = response_propensity(0.6)
    high = response_propensity(0.9)
    low = response_propensity(0.1)
    assert mid == pytest.approx(BASE_RESPONSE_RATE)
    assert high > mid
    assert low > mid


def test_response_propensity_boundary_inclusive():
    at_high = response_propensity(HIGH_SATISFACTION_THRESHOLD)
    at_low = response_propensity(LOW_SATISFACTION_THRESHOLD)
    assert at_high > BASE_RESPONSE_RATE
    assert at_low > BASE_RESPONSE_RATE


def test_income_stress_suppresses_response():
    baseline = response_propensity(0.1, IncomeStress.LOW)
    stressed = response_propensity(0.1, IncomeStress.HIGH)
    assert stressed < baseline


def test_response_propensity_clamped_to_one():
    # Even at the most extreme satisfaction, propensity is a rate, not >1.
    assert response_propensity(0.0) <= 1.0
    assert response_propensity(1.0) <= 1.0


def test_csat_dispatch_is_deterministic():
    r1 = dispatch_csat_survey("C1", "2020-01-01", 0.9)
    r2 = dispatch_csat_survey("C1", "2020-01-01", 0.9)
    assert r1 == r2


def test_csat_dispatch_varies_by_date():
    responses = [
        dispatch_csat_survey("C1", f"20{yr}-01-01", 0.95).responded
        for yr in range(16, 26)
    ]
    # Not every year should give the same responded/not-responded outcome --
    # otherwise the "response" roll isn't actually varying per event.
    assert len(set(responses)) > 1


def test_csat_score_in_range_when_responded():
    for yr in range(16, 40):
        r = dispatch_csat_survey("C1", f"20{yr}-01-01", 0.95)
        if r.responded:
            assert 0.0 <= r.score_0_10 <= 10.0


def test_nps_score_is_int_in_range_when_responded():
    for yr in range(16, 40):
        r = dispatch_nps_survey("C1", f"20{yr}-01-01", 0.05)
        if r.responded:
            assert isinstance(r.score_0_10, int)
            assert 0 <= r.score_0_10 <= 10


def test_no_response_has_no_score():
    # A customer with mid-satisfaction and a low propensity roll: some fraction
    # of dispatches must come back with no response at all.
    outcomes = [dispatch_csat_survey("C1", f"20{yr}-01-01", 0.6) for yr in range(16, 60)]
    non_responses = [o for o in outcomes if not o.responded]
    assert non_responses, "expected at least one non-response in the silent middle"
    assert all(o.score_0_10 is None for o in non_responses)


def test_complaint_more_likely_with_bill_shock():
    n = 200
    with_shock = sum(
        1 for i in range(n)
        if dispatch_complaint_and_resolution(f"C{i}", "2020-01-01", True).occurred
    )
    without_shock = sum(
        1 for i in range(n)
        if dispatch_complaint_and_resolution(f"C{i}", "2020-01-01", False).occurred
    )
    assert with_shock > without_shock


def test_complaint_resolution_outcome_types():
    seen_types = set()
    for i in range(500):
        outcome = dispatch_complaint_and_resolution(f"C{i}", "2020-06-15", True)
        if outcome.occurred:
            seen_types.add(outcome.reputation_event_type)
            assert outcome.days_to_resolve is not None
            assert outcome.days_to_resolve >= 1
    # Across enough rolls, all three resolution bands should appear.
    assert ReputationEventType.COMPLAINT_RESOLVED_ON_TIME in seen_types
    assert ReputationEventType.COMPLAINT_RESOLVED_LATE in seen_types
    assert ReputationEventType.COMPLAINT_UPHELD_AT_OMBUDSMAN in seen_types


def test_complaint_on_time_within_target_days():
    for i in range(500):
        outcome = dispatch_complaint_and_resolution(f"C{i}", "2020-06-15", True)
        if outcome.occurred and outcome.reputation_event_type == ReputationEventType.COMPLAINT_RESOLVED_ON_TIME:
            assert outcome.days_to_resolve <= ON_TIME_DAYS_MAX


def test_no_complaint_result_has_no_event_type():
    result = dispatch_complaint_and_resolution("C_never", "2020-01-01", False)
    if not result.occurred:
        assert result.reputation_event_type is None
        assert result.days_to_resolve is None
