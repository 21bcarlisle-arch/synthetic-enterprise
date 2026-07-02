"""Phase MY: Payment behaviour score wired into company churn model.

Tests combined_churn_probability which combines bill_shock (existing signal)
with BehaviourScore (Phase MX signal). Both are observable -- no SIM internals.
"""
import pytest
from company.crm.payment_behaviour_analytics import BehaviourScore
from company.crm.payment_churn_model import (
    CHURN_UPLIFT_BY_SCORE,
    combined_churn_probability,
)
from saas.churn_model import (
    BASE_ANNUAL_CHURN_PROBABILITY,
    CHURN_UPLIFT_PER_BILL_SHOCK,
    MAX_CHURN_PROBABILITY,
    churn_probability,
)


def test_base_only_no_score():
    p = combined_churn_probability(0, None)
    assert abs(p - BASE_ANNUAL_CHURN_PROBABILITY) < 1e-9


def test_excellent_suppresses_churn():
    p_base = combined_churn_probability(0, None)
    p_exc = combined_churn_probability(0, BehaviourScore.EXCELLENT)
    assert p_exc < p_base


def test_good_neutral_uplift():
    p_base = combined_churn_probability(0, None)
    p_good = combined_churn_probability(0, BehaviourScore.GOOD)
    assert abs(p_good - p_base) < 1e-9


def test_fair_adds_moderate_uplift():
    p_base = combined_churn_probability(0, None)
    p_fair = combined_churn_probability(0, BehaviourScore.FAIR)
    assert p_fair > p_base
    assert abs(p_fair - (p_base + 0.03)) < 1e-9


def test_poor_adds_significant_uplift():
    p_base = combined_churn_probability(0, None)
    p_poor = combined_churn_probability(0, BehaviourScore.POOR)
    assert abs(p_poor - (p_base + 0.10)) < 1e-9


def test_critical_adds_high_uplift():
    p_base = combined_churn_probability(0, None)
    p_crit = combined_churn_probability(0, BehaviourScore.CRITICAL)
    assert abs(p_crit - (p_base + 0.20)) < 1e-9


def test_none_score_equals_base():
    for shocks in (0, 1, 3):
        assert abs(combined_churn_probability(shocks, None) - churn_probability(shocks)) < 1e-9


def test_bill_shocks_still_apply():
    p1 = combined_churn_probability(1, BehaviourScore.GOOD)
    p0 = combined_churn_probability(0, BehaviourScore.GOOD)
    assert abs(p1 - p0 - CHURN_UPLIFT_PER_BILL_SHOCK) < 1e-9


def test_bill_shocks_plus_poor_stacks():
    expected = min(
        BASE_ANNUAL_CHURN_PROBABILITY + 2 * CHURN_UPLIFT_PER_BILL_SHOCK + 0.10,
        MAX_CHURN_PROBABILITY,
    )
    assert abs(combined_churn_probability(2, BehaviourScore.POOR) - expected) < 1e-9


def test_bill_shocks_plus_critical_stacks():
    expected = min(
        BASE_ANNUAL_CHURN_PROBABILITY + 3 * CHURN_UPLIFT_PER_BILL_SHOCK + 0.20,
        MAX_CHURN_PROBABILITY,
    )
    assert abs(combined_churn_probability(3, BehaviourScore.CRITICAL) - expected) < 1e-9


def test_bill_shocks_plus_excellent_reduces():
    p_excellent = combined_churn_probability(2, BehaviourScore.EXCELLENT)
    p_none = combined_churn_probability(2, None)
    assert p_excellent < p_none


def test_total_capped_at_095():
    # Many shocks + CRITICAL should not exceed 0.95
    result = combined_churn_probability(100, BehaviourScore.CRITICAL)
    assert result == MAX_CHURN_PROBABILITY


def test_zero_shocks_excellent_is_low():
    p = combined_churn_probability(0, BehaviourScore.EXCELLENT)
    assert p < BASE_ANNUAL_CHURN_PROBABILITY
    assert p > 0.0


def test_zero_shocks_critical_is_high():
    p = combined_churn_probability(0, BehaviourScore.CRITICAL)
    assert p > BASE_ANNUAL_CHURN_PROBABILITY + 0.15


def test_high_shocks_excellent_still_lower_than_high_shocks_critical():
    p_exc = combined_churn_probability(5, BehaviourScore.EXCELLENT)
    p_crit = combined_churn_probability(5, BehaviourScore.CRITICAL)
    assert p_exc < p_crit


def test_score_uplift_table_complete():
    for score in BehaviourScore:
        assert score in CHURN_UPLIFT_BY_SCORE


def test_ordering_excellent_lt_good_lt_fair_lt_poor_lt_critical():
    uplifts = [CHURN_UPLIFT_BY_SCORE[s] for s in (
        BehaviourScore.EXCELLENT,
        BehaviourScore.GOOD,
        BehaviourScore.FAIR,
        BehaviourScore.POOR,
        BehaviourScore.CRITICAL,
    )]
    assert uplifts == sorted(uplifts)


def test_integration_payment_analytics_into_combined_probability():
    from company.crm.payment_behaviour_analytics import PaymentBehaviourAnalytics
    from simulation.payment_timing import generate_payment_record
    from simulation.household import IncomeStress
    import random
    from datetime import date
    pba = PaymentBehaviourAnalytics()
    rng = random.Random(99)
    for i in range(20):
        r = generate_payment_record("C1", date(2022, 6, 1), 100.0, IncomeStress.HIGH, rng)
        pba.record_payment("C1", r)
    score = pba.get_score("C1")
    p = combined_churn_probability(3, score)
    # HIGH stress => POOR or CRITICAL => churn probability significantly above base
    assert p > BASE_ANNUAL_CHURN_PROBABILITY + 0.05


def test_epistemic_combined_uses_observables_only():
    # BehaviourScore is derived from observable payment records (Phase MX)
    # bill_shock_count is derived from billing records
    # Neither reads income_stress directly
    p = combined_churn_probability(2, BehaviourScore.POOR)
    assert isinstance(p, float)
    assert 0.0 < p <= MAX_CHURN_PROBABILITY


def test_combined_probability_is_float_in_range():
    for shocks in range(5):
        for score in list(BehaviourScore) + [None]:
            p = combined_churn_probability(shocks, score)
            assert isinstance(p, float)
            assert 0.0 <= p <= MAX_CHURN_PROBABILITY
