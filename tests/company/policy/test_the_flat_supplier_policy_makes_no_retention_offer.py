"""B11: the flat supplier, the baseline EP17's per-customer switch has to beat, targets nobody.

The defect each leg names: an arm labelled "flat" that still sends retention offers by its own
churn belief, or splits its letters by segment, measures per-customer PRICING inside a company
that targets per customer in both arms -- the narrower claim
`SEAT_FINDING_B11_THE_FLAT_SUPPLIER_ARM_HAS_NO_DOOR_ON_A_VARIED_BOOK_2026-10-16` found the value
cycle's A/B was making. Field values alone cannot show it: the reachability leg runs the year.
"""
from __future__ import annotations

import dataclasses

import pytest

from company.interfaces.growth_desk import retention_cut_share_at_risk_tiers
from company.policy.decision_policy import (
    CURRENT_POLICY,
    FLAT_SUPPLIER_POLICY,
    framing_type_for,
    policy_scope,
    tone_for,
)

#: The fields that hold a per-customer view, and the name.
PER_CUSTOMER_FIELDS = {"name", "retention_discount_mode", "flat_discount_pct", "retention_tiers",
                       "framing_mode", "tone_mode"}
WINDOW_END = "2016-12-31"


def _differing(a, b) -> set[str]:
    return {f.name for f in dataclasses.fields(a) if getattr(a, f.name) != getattr(b, f.name)}


def test_the_flat_supplier_policy_differs_from_current_in_exactly_the_per_customer_fields():
    """DEFECT: a second field moved with the posture (a hedge rule, a guard term), so the delta
    against current carries an uncontrolled variable."""
    assert _differing(CURRENT_POLICY, FLAT_SUPPLIER_POLICY) == PER_CUSTOMER_FIELDS


def test_the_tier_cut_can_offer_under_current_and_cannot_under_flat():
    """The partition first: a cut function that refused everything would pass the flat leg."""
    rate, floor = 200.0, 150.0
    assert retention_cut_share_at_risk_tiers(
        rate, CURRENT_POLICY.retention_discount_for_risk(0.9), cost_floor=floor) == 0.08
    for belief in (0.0, 0.31, 0.6, 0.99):
        assert retention_cut_share_at_risk_tiers(
            rate, FLAT_SUPPLIER_POLICY.retention_discount_for_risk(belief),
            cost_floor=floor) is None


def test_every_household_gets_one_framing_and_one_tone():
    ids = [f"C{i}" for i in range(40)]
    assert {framing_type_for(CURRENT_POLICY, c, "2018-01-01") for c in ids} == {
        "gain_framed", "loss_framed"}
    assert {framing_type_for(FLAT_SUPPLIER_POLICY, c, "2018-01-01") for c in ids} == {
        "gain_framed"}
    assert {tone_for(FLAT_SUPPLIER_POLICY, c, "2018-01-31") for c in ids} == {"firm_toned"}


@pytest.fixture(scope="module")
def offers_by_arm():
    from simulation.run_phase2b import main as run_phase2b
    out = {}
    for policy in (CURRENT_POLICY, FLAT_SUPPLIER_POLICY):
        with policy_scope(policy):
            run = run_phase2b(report_end=WINDOW_END, policy=policy)
        out[policy.name] = (len(run["retention_log"]), len(run["retention_cost_events"]))
    return out


def test_a_run_under_the_flat_supplier_makes_no_retention_offer(offers_by_arm):
    """DEFECT: the flat arm's fields are right and the run still offers, through a route the
    fields do not reach. Current offers in the same window, so the zero is the policy's."""
    offers, costs = offers_by_arm["current"]
    assert offers > 0 and costs > 0, offers_by_arm
    assert offers_by_arm["flat_supplier"] == (0, 0), offers_by_arm
