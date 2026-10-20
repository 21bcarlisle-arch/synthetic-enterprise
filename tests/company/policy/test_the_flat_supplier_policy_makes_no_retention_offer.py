"""B11: the flat supplier, the baseline EP17's per-customer switch has to beat, targets nobody.

The defect each leg names: an arm labelled "flat" that still sends retention offers by its own
churn belief, or splits its letters by segment, measures per-customer PRICING inside a company
that targets per customer in both arms -- the narrower claim
`SEAT_FINDING_B11_THE_FLAT_SUPPLIER_ARM_HAS_NO_DOOR_ON_A_VARIED_BOOK_2026-10-16` found the value
cycle's A/B was making. Field values alone cannot show it: the reachability leg runs the window.

The reachability half is keyed to the CUT, not to an offer. Through 2016 the run holds three
renewals, all below the churn threshold, so neither arm reached the guard and both read (0, 0)
however the flat arm behaved. Since `c61d8b608` the guard prices the term's contribution, and
current's offers depend on that economics. Whether a renewal past the threshold is given a cut
does not. Through 2017, current gives 24 renewals a cut (23 churners withheld as uneconomical,
one offer) and flat stops the same 23 at the cut (2026-10-20 measurement,
`docs/staging/SEAT_FINDING_THE_FLAT_SUPPLIER_REACHABILITY_LEG_IS_KEYED_TO_THE_CUT_2026-10-20.md`).
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
WINDOW_END = "2017-12-31"
#: The withheld reasons a renewal can carry WITHOUT being given a cut. Any other reason was
#: asked after the cut, so an unknown new reason counts against the flat arm.
STOPPED_BEFORE_THE_CUT = {"below_threshold", "the_fix_has_no_room_above_its_cost_floor",
                          "the_fix_already_meets_the_best_published_deal"}


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
        reasons = [e.get("no_offer_reason") for e in run["no_offer_churn_log"]]
        out[policy.name] = {
            "offers": (len(run["retention_log"]), len(run["retention_cost_events"])),
            "past_the_cut": sum(r not in STOPPED_BEFORE_THE_CUT for r in reasons),
            "no_room": reasons.count("the_fix_has_no_room_above_its_cost_floor"),
        }
    return out


def test_a_run_under_the_flat_supplier_makes_no_retention_offer(offers_by_arm):
    """DEFECT: the flat arm's fields are right and the run still offers, or still sizes a cut,
    through a route the fields do not reach. Current gives renewals a cut in the same window, and
    flat stops some at the cut, so the zero is the policy's and both branches were taken."""
    current, flat = offers_by_arm["current"], offers_by_arm["flat_supplier"]
    assert current["offers"][0] + current["past_the_cut"] > 0, offers_by_arm
    assert flat["no_room"] > 0, offers_by_arm
    assert flat["offers"] == (0, 0) and flat["past_the_cut"] == 0, offers_by_arm
