import pytest

from company.policy.decision_policy import CURRENT_POLICY, NAIVE_POLICY, DecisionPolicy


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
