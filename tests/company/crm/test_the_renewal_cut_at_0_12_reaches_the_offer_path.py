"""The retention cut moves to 0.12 behind a default-off switch, and only behind it.

Defect named: on candidate A's book the nine value-arm flips sit at a churn belief of 0.111 to
0.137, under the 0.30 cut, so the guard never weighs them (`THE_VALUE_TEST_REDESIGN.md` §12f). The
switch has two halves, and either one alone reaches nothing:
  * the cut: a renewal at 0.13 must be CONSIDERED;
  * the tier table: under `risk_tiers` sizing a belief under the lowest tier is sized at 0%,
    `retention_cut_share_at_risk_tiers` returns None, and no offer is made. That 0% tier is a
    second cut at 0.30, found offline on 19 Nov before any run.
With the switch off, both halves must return exactly what the 0.30 path returned.
"""
from __future__ import annotations

import ast
import dataclasses
import inspect

import simulation.run_phase2b as run_phase2b
from company.interfaces.growth_desk import (
    CONSIDERED_OVER_THE_BELIEF_THRESHOLD,
    NOT_CONSIDERED_UNDER_THE_BELIEF_THRESHOLD,
    RETENTION_THRESHOLD,
    RETENTION_THRESHOLD_AT_THE_FLIPS,
    retention_considers_the_renewal,
    retention_cut_share_at_risk_tiers,
    retention_threshold,
    retention_tier_share,
)
from company.policy.decision_policy import CURRENT_POLICY, VALUE_ARM_POLICY, DecisionPolicy

FIELD = "retention_cut_at_the_flips"
BELIEFS = [i / 1000 for i in range(0, 1001)]


def _offered(policy, belief, on):
    """Considered, and sized to a cut the risk-tier sizing would give: the offer path's two gates."""
    considered, _ = retention_considers_the_renewal(
        belief, threshold=retention_threshold(on), skip_threshold=False,
        ending_term_type=None, renewal_year=None)
    share = retention_tier_share(policy, belief, cut_at_the_flips=on)
    return considered and retention_cut_share_at_risk_tiers(100.0, share, cost_floor=50.0) is not None


def test_a_renewal_at_0_13_reaches_the_offer_path_only_with_the_switch_on():
    """Both sides of the partition. Reds if the switch stops moving the cut, or stops lifting the
    0% tier, or if either half starts acting with the switch off."""
    assert _offered(VALUE_ARM_POLICY, 0.13, on=True)
    assert not _offered(VALUE_ARM_POLICY, 0.13, on=False)
    assert retention_considers_the_renewal(
        0.13, threshold=retention_threshold(True), skip_threshold=False,
        ending_term_type=None, renewal_year=None) == (True, CONSIDERED_OVER_THE_BELIEF_THRESHOLD)
    assert retention_considers_the_renewal(
        0.13, threshold=retention_threshold(False), skip_threshold=False,
        ending_term_type=None, renewal_year=None)[1] == NOT_CONSIDERED_UNDER_THE_BELIEF_THRESHOLD
    # Under the new cut still refused: the switch moves the cut, it does not remove it.
    assert not _offered(VALUE_ARM_POLICY, 0.11, on=True)
    assert not _offered(VALUE_ARM_POLICY, 0.12, on=True)
    # The tier lift is the lowest tier's share, not a new number.
    assert retention_tier_share(VALUE_ARM_POLICY, 0.13, cut_at_the_flips=True) == min(
        d for _, d in VALUE_ARM_POLICY.retention_tiers)


def test_with_the_switch_off_the_0_30_path_is_unchanged_at_every_belief():
    assert retention_threshold(False) is RETENTION_THRESHOLD
    assert RETENTION_THRESHOLD == 0.30 and RETENTION_THRESHOLD_AT_THE_FLIPS == 0.12
    for policy in (CURRENT_POLICY, VALUE_ARM_POLICY):
        for b in BELIEFS:
            assert retention_tier_share(policy, b, cut_at_the_flips=False) == \
                policy.retention_discount_for_risk(b)
    # With it on, nothing over 0.30 moves either: the switch only acts in (0.12, 0.30].
    for b in BELIEFS:
        if b > 0.30 or b <= 0.12:
            assert retention_tier_share(VALUE_ARM_POLICY, b, cut_at_the_flips=True) == \
                VALUE_ARM_POLICY.retention_discount_for_risk(b)


def test_the_switch_is_off_on_every_standing_policy():
    assert {f.name: f.default for f in dataclasses.fields(DecisionPolicy)}[FIELD] is False
    assert getattr(CURRENT_POLICY, FIELD) is False
    assert getattr(VALUE_ARM_POLICY, FIELD) is False


def test_the_run_loop_reads_both_halves_from_the_policy_switch():
    """Read from the run loop's syntax tree: the cut and the tier share are each handed the run's
    own `policy.retention_cut_at_the_flips`, so neither half can be wired to a constant."""
    tree = ast.parse(inspect.getsource(run_phase2b))
    for name in ("retention_threshold", "retention_tier_share"):
        calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)
                 and getattr(n.func, "id", None) == name]
        assert len(calls) == 1, name
        args = list(calls[0].args) + [k.value for k in calls[0].keywords]
        assert any(getattr(a, "attr", None) == FIELD
                   and getattr(getattr(a, "value", None), "id", None) == "policy" for a in args), name
