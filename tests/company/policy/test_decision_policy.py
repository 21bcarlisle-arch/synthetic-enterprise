import pytest

from company.policy.decision_policy import CURRENT_POLICY, NAIVE_POLICY, DecisionPolicy, framing_type_for


def test_current_policy_tiered_discount_matches_phase_14a_tiers():
    assert CURRENT_POLICY.retention_discount_mode == "tiered"
    assert CURRENT_POLICY.retention_discount_for_risk(0.80) == 0.08   # high risk
    assert CURRENT_POLICY.retention_discount_for_risk(0.75) == 0.08   # exactly at high-risk threshold
    assert CURRENT_POLICY.retention_discount_for_risk(0.60) == 0.05   # medium risk
    assert CURRENT_POLICY.retention_discount_for_risk(0.50) == 0.05   # exactly at medium threshold
    assert CURRENT_POLICY.retention_discount_for_risk(0.40) == 0.03   # low-risk-above-threshold
    assert CURRENT_POLICY.retention_discount_for_risk(0.30) == 0.03   # exactly at retention threshold
    assert CURRENT_POLICY.retention_discount_for_risk(0.20) == 0.00   # below any tier


def test_current_policy_includes_acq_cost_and_var_hedge():
    assert CURRENT_POLICY.include_acq_cost_saved_in_guard is True
    assert CURRENT_POLICY.use_var_hedge_decision is True


def test_naive_policy_flat_discount_regardless_of_risk():
    """Phase 12d/pre-14a state: flat 5% discount, no risk-tiering."""
    assert NAIVE_POLICY.retention_discount_mode == "flat"
    for risk in (0.30, 0.50, 0.75, 0.95):
        assert NAIVE_POLICY.retention_discount_for_risk(risk) == 0.05


def test_naive_policy_excludes_acq_cost_and_var_hedge():
    """Phase 12d margin-only guard (pre-15b) + pre-43b hedging (Phase 22b state)."""
    assert NAIVE_POLICY.include_acq_cost_saved_in_guard is False
    assert NAIVE_POLICY.use_var_hedge_decision is False


def test_policies_are_frozen_dataclasses():
    with pytest.raises(Exception):
        CURRENT_POLICY.name = "mutated"


def test_flat_mode_ignores_tiers_even_if_present():
    policy = DecisionPolicy(
        name="flat-with-tiers",
        retention_discount_mode="flat",
        retention_tiers=((0.75, 0.08),),
        flat_discount_pct=0.10,
        include_acq_cost_saved_in_guard=True,
        use_var_hedge_decision=True,
    )
    assert policy.retention_discount_for_risk(0.90) == 0.10


def test_current_policy_ab_tests_framing():
    assert CURRENT_POLICY.framing_mode == "ab_test"


def test_naive_policy_fixed_gain_framing():
    assert NAIVE_POLICY.framing_mode == "gain_framed"


def test_framing_type_for_fixed_mode_returns_constant():
    for date in ("2020-01-01", "2021-06-01", "2025-12-31"):
        assert framing_type_for(NAIVE_POLICY, "C1", date) == "gain_framed"


def test_framing_type_for_ab_test_varies_by_date_same_customer():
    seen = set()
    for i in range(50):
        date = "20{:02d}-01-01".format(i)
        seen.add(framing_type_for(CURRENT_POLICY, "C1", date))
    assert seen == {"loss_framed", "gain_framed"}


def test_framing_type_for_ab_test_is_deterministic():
    a = framing_type_for(CURRENT_POLICY, "C1", "2020-01-01")
    b = framing_type_for(CURRENT_POLICY, "C1", "2020-01-01")
    assert a == b


def test_framing_type_for_ab_test_roughly_balanced_across_customers():
    from collections import Counter
    counts = Counter(
        framing_type_for(CURRENT_POLICY, "C" + str(i), "2020-01-01") for i in range(1, 500)
    )
    total = sum(counts.values())
    assert 0.35 < counts["loss_framed"] / total < 0.65
    assert 0.35 < counts["gain_framed"] / total < 0.65
