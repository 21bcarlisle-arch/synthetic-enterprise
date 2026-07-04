"""Phase NC: Enriched company churn estimate -- rate + payment behaviour signals.

Tests enriched_churn_estimate() and the extended sim_interface.get_churn_estimate().
All inputs are observable company signals; no SIM internals accessed.
"""
import pytest
from company.crm.enriched_churn_estimate import enriched_churn_estimate
from company.crm.payment_behaviour_analytics import BehaviourScore
from company.interfaces.sim_interface import StubSimInterface
from saas.churn_model import BASE_ANNUAL_CHURN_PROBABILITY, MAX_CHURN_PROBABILITY


def _rate_est(old, new, tenure=1.0, kwh=0.0):
    from company.crm.churn_model import estimate_churn_probability
    return estimate_churn_probability(old, new, tenure, kwh)


def test_no_behaviour_signals_matches_rate_model():
    rate = _rate_est(80.0, 100.0)
    enriched = enriched_churn_estimate(80.0, 100.0, 1.0)
    assert abs(enriched - rate) < 1e-9


def test_critical_behaviour_elevates_above_stable_rate():
    p = enriched_churn_estimate(80.0, 80.0, 2.0, behaviour_score=BehaviourScore.CRITICAL)
    rate_only = _rate_est(80.0, 80.0, 2.0)
    assert p > rate_only


def test_excellent_behaviour_can_suppress_below_rate_model():
    p = enriched_churn_estimate(80.0, 82.0, 1.0, bill_shock_count=0, behaviour_score=BehaviourScore.EXCELLENT)
    rate_only = _rate_est(80.0, 82.0, 1.0)
    assert p <= rate_only


def test_low_satisfaction_elevates_estimate():
    p_none = enriched_churn_estimate(80.0, 80.0, 2.0)
    p_low = enriched_churn_estimate(80.0, 80.0, 2.0, satisfaction_score=0.30)
    assert p_low > p_none


def test_high_rate_increase_dominates_over_excellent_payment():
    p = enriched_churn_estimate(50.0, 150.0, 1.0, behaviour_score=BehaviourScore.EXCELLENT)
    rate_only = _rate_est(50.0, 150.0, 1.0)
    assert abs(p - rate_only) < 1e-9


def test_all_three_signals_capped_at_095():
    p = enriched_churn_estimate(50.0, 200.0, 0.5, 10000.0,
                                 bill_shock_count=10,
                                 behaviour_score=BehaviourScore.CRITICAL,
                                 satisfaction_score=0.20)
    assert p == MAX_CHURN_PROBABILITY


def test_max_is_taken_not_sum():
    from company.crm.payment_churn_model import combined_churn_probability
    rate = _rate_est(80.0, 100.0)
    payment = combined_churn_probability(1, BehaviourScore.GOOD, None)
    expected = max(rate, payment)
    got = enriched_churn_estimate(80.0, 100.0, 1.0, bill_shock_count=1, behaviour_score=BehaviourScore.GOOD)
    assert abs(got - expected) < 1e-9


def test_result_never_below_zero():
    p = enriched_churn_estimate(100.0, 50.0, 5.0, behaviour_score=BehaviourScore.EXCELLENT)
    assert p >= 0.0


def test_sim_interface_backward_compatible():
    s = StubSimInterface()
    p1 = s.get_churn_estimate("C1", 80.0, 100.0, 2.0, 3500.0)
    p2 = enriched_churn_estimate(80.0, 100.0, 2.0, 3500.0)
    assert abs(p1 - p2) < 1e-9


def test_sim_interface_with_critical_behaviour():
    s = StubSimInterface()
    p_none = s.get_churn_estimate("C1", 80.0, 80.0, 2.0)
    p_crit = s.get_churn_estimate("C1", 80.0, 80.0, 2.0, behaviour_score=BehaviourScore.CRITICAL)
    assert p_crit > p_none


def test_sim_interface_with_low_satisfaction():
    s = StubSimInterface()
    p_none = s.get_churn_estimate("C1", 80.0, 80.0, 2.0)
    p_low_sat = s.get_churn_estimate("C1", 80.0, 80.0, 2.0, satisfaction_score=0.30)
    assert p_low_sat > p_none


def test_sim_interface_accepts_bill_shock_count():
    s = StubSimInterface()
    p0 = s.get_churn_estimate("C1", 80.0, 80.0, 2.0, bill_shock_count=0)
    p3 = s.get_churn_estimate("C1", 80.0, 80.0, 2.0, bill_shock_count=3)
    assert p3 >= p0


def test_sim_interface_all_three_signals():
    s = StubSimInterface()
    p = s.get_churn_estimate(
        "C1", 80.0, 80.0, 2.0,
        bill_shock_count=2,
        behaviour_score=BehaviourScore.POOR,
        satisfaction_score=0.35,
    )
    assert p > 0.20


def test_poor_behaviour_no_rate_change_higher_than_base():
    p = enriched_churn_estimate(80.0, 80.0, 1.0, behaviour_score=BehaviourScore.POOR)
    assert p > BASE_ANNUAL_CHURN_PROBABILITY


def test_enriched_estimate_no_regression_with_gas():
    p = enriched_churn_estimate(50.0, 80.0, 1.0, fuel="gas")
    rate_only = _rate_est(50.0, 80.0, 1.0)
    from company.crm.churn_model import GAS_BASE_CHURN_RATE
    assert p >= 0.0


def test_three_signals_higher_than_any_single():
    p_rate = enriched_churn_estimate(80.0, 90.0, 1.0)
    p_payment = enriched_churn_estimate(80.0, 80.0, 1.0, behaviour_score=BehaviourScore.POOR)
    p_sat = enriched_churn_estimate(80.0, 80.0, 1.0, satisfaction_score=0.30)
    p_all = enriched_churn_estimate(80.0, 90.0, 1.0,
                                      behaviour_score=BehaviourScore.POOR,
                                      satisfaction_score=0.30)
    assert p_all >= p_rate
    assert p_all >= p_payment
    assert p_all >= p_sat


# ── Phase QB: observable market-conditions signal ─────────────────────────────

def test_no_renewal_year_unchanged():
    """Default (no renewal_year) behaviour is unchanged — backward compatible."""
    p_none = enriched_churn_estimate(80.0, 90.0, 1.0)
    p_explicit_none = enriched_churn_estimate(80.0, 90.0, 1.0, renewal_year=None)
    assert p_none == pytest.approx(p_explicit_none)


def test_crisis_year_suppresses_combined_estimate_below_calm_year():
    """2022 (crisis, multiplier 0.44) must give a lower combined estimate than
    2016 (peak competition, multiplier 2.17) for identical inputs, even with a
    payment-behaviour signal in the mix."""
    p_crisis = enriched_churn_estimate(
        80.0, 90.0, 1.0, behaviour_score=BehaviourScore.POOR, renewal_year=2022,
    )
    p_calm = enriched_churn_estimate(
        80.0, 90.0, 1.0, behaviour_score=BehaviourScore.POOR, renewal_year=2016,
    )
    assert p_crisis < p_calm


def test_market_multiplier_clamped_to_valid_range():
    p = enriched_churn_estimate(80.0, 300.0, 1.0, behaviour_score=BehaviourScore.CRITICAL, renewal_year=2016)
    assert 0.0 <= p <= MAX_CHURN_PROBABILITY
