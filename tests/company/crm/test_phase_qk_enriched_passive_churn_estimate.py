"""Phase QK: Enriched passive-renewal churn estimate.

estimate_passive_churn_probability() (SVT-inertia model) deliberately gives passive
renewers low rate-sensitivity, but its own docstring says their real churn driver is
life events, not price. This closes the gap: enriched_passive_churn_estimate() lets
observable payment-behaviour/satisfaction signal raise a passive renewer's estimate
above the SVT-inertia cap, the same max()-combination rule enriched_churn_estimate()
already applies to active/I&C renewals.

Root cause this fixes: the live company-vs-SIM churn classifier
(company/analytics/churn_accuracy_report.py) showed recall=0%/precision=0% across
all 10 years of the production run -- every actual churner's company_churn_estimate
stayed under the 0.30 retention threshold because passive renewals (65% of resi
renewals most years, 100% in crisis years) never received the payment/satisfaction
signal at all.
"""
import pytest

from company.crm.churn_model import (
    PASSIVE_BASE_CHURN_RATE,
    PASSIVE_CHURN_CAP,
    estimate_passive_churn_probability,
)
from company.crm.enriched_churn_estimate import enriched_passive_churn_estimate
from company.crm.payment_behaviour_analytics import BehaviourScore
from saas.churn_model import MAX_CHURN_PROBABILITY


def test_no_behaviour_signals_matches_passive_rate_model():
    rate = estimate_passive_churn_probability(80.0, 80.0, 1.0)
    enriched = enriched_passive_churn_estimate(80.0, 80.0, 1.0)
    assert abs(enriched - rate) < 1e-9


def test_critical_behaviour_breaks_above_passive_cap():
    """The whole point: a passive renewer sliding into arrears must be able to
    exceed the SVT-inertia rate-model's structural 0.10 ceiling."""
    p = enriched_passive_churn_estimate(
        80.0, 80.0, 2.0,
        behaviour_score=BehaviourScore.CRITICAL,
        satisfaction_score=0.30,
    )
    assert p > PASSIVE_CHURN_CAP


def test_large_rate_increase_alone_stays_within_passive_cap():
    """Passive renewers remain rate-insensitive absent a behaviour signal --
    this is the SVT-inertia property the model must preserve."""
    p = enriched_passive_churn_estimate(50.0, 200.0, 1.0)
    assert p <= PASSIVE_CHURN_CAP


def test_excellent_behaviour_does_not_raise_above_rate_model():
    p = enriched_passive_churn_estimate(80.0, 80.0, 2.0, behaviour_score=BehaviourScore.EXCELLENT)
    rate_only = estimate_passive_churn_probability(80.0, 80.0, 2.0)
    assert p <= rate_only + 1e-9


def test_max_is_taken_not_sum():
    from company.crm.payment_churn_model import combined_churn_probability
    rate = estimate_passive_churn_probability(80.0, 100.0, 1.0)
    payment = combined_churn_probability(1, BehaviourScore.GOOD, None)
    expected = max(rate, payment)
    got = enriched_passive_churn_estimate(80.0, 100.0, 1.0, bill_shock_count=1, behaviour_score=BehaviourScore.GOOD)
    assert abs(got - expected) < 1e-9


def test_capped_at_max_churn_probability():
    p = enriched_passive_churn_estimate(
        50.0, 200.0, 0.5,
        bill_shock_count=30,
        behaviour_score=BehaviourScore.CRITICAL,
        satisfaction_score=0.20,
    )
    assert p == MAX_CHURN_PROBABILITY


def test_result_never_below_zero():
    p = enriched_passive_churn_estimate(100.0, 50.0, 5.0, behaviour_score=BehaviourScore.EXCELLENT)
    assert p >= 0.0


def test_no_renewal_year_unchanged():
    p_none = enriched_passive_churn_estimate(80.0, 90.0, 1.0)
    p_explicit_none = enriched_passive_churn_estimate(80.0, 90.0, 1.0, renewal_year=None)
    assert p_none == pytest.approx(p_explicit_none)


def test_crisis_year_suppresses_combined_estimate_below_calm_year():
    p_crisis = enriched_passive_churn_estimate(
        80.0, 90.0, 1.0, behaviour_score=BehaviourScore.POOR, renewal_year=2022,
    )
    p_calm = enriched_passive_churn_estimate(
        80.0, 90.0, 1.0, behaviour_score=BehaviourScore.POOR, renewal_year=2016,
    )
    assert p_crisis < p_calm


def test_baseline_matches_passive_base_churn_rate():
    p = enriched_passive_churn_estimate(80.0, 80.0, 0.0)
    assert p == pytest.approx(PASSIVE_BASE_CHURN_RATE)
