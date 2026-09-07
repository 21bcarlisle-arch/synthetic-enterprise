"""The defect: 216/2,039 = 10.59% was published as the method's reach.

Its denominator counts TERM BOUNDARIES. 1,350 of those were households on the standard variable
tariff, whose "boundary" is an Ofgem cap revision at which no rate is struck for the household and
no offer is made -- so the published figure was mostly a measure of what fraction of a domestic
book sits on a default tariff, which is a fact about GB and not a result of this company. The
decision is `docs/staging/SEAT_DECISION_AN_SVT_HOUSEHOLD_IS_NOT_A_DECISION_THIS_ARM_DECLINES
_2026-09-07.md`.

Every control here fires on a specific way the repair could be undone or could be vacuous. The
one they are all built around: a denominator that quietly drops the ways the arm LOSES would be
fitted to the flattering answer, so `no_observed_history` -- which has counted zero on every run
measured -- is inside the population and there is a control that says so at a nonzero count.
"""
from __future__ import annotations

import company.pricing.value_based_renewal as vbr
from tools.decisions_that_existed import STAGE_PRESENTED_A_DECISION, decisions_that_existed


def _funnel(counts: dict, by_tariff_type: dict | None = None) -> dict:
    """A funnel of exactly the arm's own stages, so nothing here can pass on a shape it invented."""
    offered = sum(counts.values())
    priced = counts.get(vbr.STAGE_PRICED, 0)
    return {
        "stages": [{"stage": s, "count": counts.get(s, 0)} for s in vbr.FUNNEL_STAGES],
        "renewals_the_world_offered": offered,
        "priced_share_of_renewals_offered": round(priced / offered, 4) if offered else None,
        "product_not_upliftable_by_tariff_type": by_tariff_type or {},
    }


def test_every_stage_the_arm_can_reach_is_placed_on_one_side_or_the_other():
    """MUTATION: add a guard to the arm and not to the membership rule.

    The failure this repairs one level down is a denominator silently missing a guard, so a
    membership rule that is silently missing one is the same defect wearing this module's name.
    Both directions: an entry for a stage the arm no longer has is a rule about nothing.
    """
    assert set(STAGE_PRESENTED_A_DECISION) == set(vbr.FUNNEL_STAGES)


def test_both_sides_of_the_partition_are_reachable_and_neither_is_empty():
    """A membership rule that answered False for everything would pass every leg-by-leg test.

    THE WHOLE PARTITION IN ONE CONTROL. It also asserts each side holds more than one stage: a
    rule with a single member on either side is one edit from being a rule about one guard.
    """
    inside = [s for s, (member, _) in STAGE_PRESENTED_A_DECISION.items() if member]
    outside = [s for s, (member, _) in STAGE_PRESENTED_A_DECISION.items() if not member]
    assert len(inside) >= 2 and len(outside) >= 2, (
        "the partition has collapsed to one side: inside={} outside={}".format(inside, outside))
    assert vbr.STAGE_PRICED in inside and vbr.STAGE_PRODUCT_NOT_UPLIFTABLE in outside


def test_every_membership_carries_a_reason_a_reader_can_disagree_with():
    """MUTATION: replace the reasons with a bare boolean map.

    The flag is not the load-bearing half. A reader who thinks a stage is on the wrong side needs
    a sentence to argue with, and a reason set at the same statement as the flag cannot drift
    from it the way this panel's last prose did.
    """
    for stage, (_, why) in STAGE_PRESENTED_A_DECISION.items():
        assert isinstance(why, str) and len(why) > 50, (
            "{} carries no reason worth reading: {!r}".format(stage, why))


def test_the_population_excludes_term_boundaries_at_which_no_rate_was_struck():
    """THE DEFECT ITSELF, at the run's own numbers.

    216 priced, 63 declined, 1,350 SVT, 252 acquisition terms: the reach over decisions is 77.42%
    and the reach over boundaries is 10.59%, and both are published. MUTATION: put the product
    gate or the acquisition term back inside the population and this fails on both figures.
    """
    block = decisions_that_existed(_funnel(
        {vbr.STAGE_PRICED: 216, vbr.STAGE_DECLINED: 63,
         vbr.STAGE_PRODUCT_NOT_UPLIFTABLE: 1350, vbr.STAGE_ACQUISITION_TERM: 252},
        {"'svt'": 1350}))

    assert block["decisions_that_existed"] == 279
    assert block["priced_share_of_the_decisions_that_existed"] == 0.7742
    # AND THE OTHER RATIO SURVIVES, named for what it counts. Dropping it would leave a reader
    # thinking the arm sees three quarters of the book.
    assert block["renewals_the_world_offered"] == 1881
    assert set(block["what_each_denominator_counts"]) == {
        "renewals_the_world_offered", "decisions_that_existed"}


def test_a_decision_the_arm_could_not_make_for_want_of_history_stays_in_the_denominator():
    """THE CONTROL THAT KEEPS THE MEASURE HONEST, and the reason it is written at a nonzero count.

    `no_observed_history` counts zero on every run measured so far, so a membership rule that put
    it outside the population would look identical on today's data and would be a denominator
    fitted to the flattering answer: it drops renewals the world OFFERED and the arm failed to
    price. MUTATION: flip its flag to False -- unobservable on any real artefact, red here.
    """
    block = decisions_that_existed(_funnel(
        {vbr.STAGE_PRICED: 10, vbr.STAGE_NO_OBSERVED_HISTORY: 90}))
    assert block["decisions_that_existed"] == 100
    assert block["priced_share_of_the_decisions_that_existed"] == 0.1


def test_refusals_whose_product_was_never_decided_are_excluded_as_unknown_not_as_outside():
    """"We know it is not a decision" and "we do not know what this is" are opposite readings.

    The unlabelled bucket is a record defect, so those households may well have presented a
    decision. They are excluded, NAMED, and published with the population they would produce --
    a prediction filed before the fidelity determination that settles them. MUTATION: fold them
    into the SVT bucket and the caveat disappears silently.
    """
    block = decisions_that_existed(_funnel(
        {vbr.STAGE_PRICED: 216, vbr.STAGE_DECLINED: 63, vbr.STAGE_PRODUCT_NOT_UPLIFTABLE: 1508},
        {"'svt'": 1350, "None": 158}))

    assert block["decisions_that_existed"] == 279
    assert block["unresolved"]["renewals"] == 158
    admitted = block["unresolved"]["if_the_owed_determination_admits_them"]
    assert admitted["decisions_that_existed"] == 437
    assert admitted["priced_share_of_the_decisions_that_existed"] == 0.4943


def test_a_run_whose_refusals_are_all_explained_carries_no_unresolved_caveat():
    """THE OTHER LEG. A caveat that is always present says nothing; this is the world in which
    the gas determination has landed, and the block must stop hedging.
    """
    block = decisions_that_existed(_funnel(
        {vbr.STAGE_PRICED: 216, vbr.STAGE_DECLINED: 63, vbr.STAGE_PRODUCT_NOT_UPLIFTABLE: 1350},
        {"'svt'": 1350}))
    assert block["unresolved"] is None


def test_a_stage_the_membership_rule_cannot_place_refuses_the_whole_population():
    """FAIL CLOSED. MUTATION: compute the population over the stages that WERE recognised.

    That is the exact defect one level down -- a denominator missing a guard, reading as a
    denominator nobody needed. The refusal names the stage.
    """
    funnel = _funnel({vbr.STAGE_PRICED: 216, vbr.STAGE_DECLINED: 63})
    funnel["stages"].append({"stage": "a_guard_added_later", "count": 900})
    block = decisions_that_existed(funnel)
    assert block["available"] is False
    assert "a_guard_added_later" in block["reason"]
    assert "decisions_that_existed" not in block


def test_a_funnel_with_no_stages_refuses_rather_than_reconstructing_one():
    """A population guessed from the totals is the defect this surface exists to have repaired."""
    block = decisions_that_existed({"renewals_the_world_offered": 2039, "priced": 216})
    assert block["available"] is False
    assert "not" in block["reason"].lower()


def test_the_reading_says_which_of_the_two_small_reaches_this_run_is_showing():
    """A reach small because the book is on a default tariff and a reach small because the method
    fails are the same fraction and opposite conclusions.

    NULL RUNG in the same control: a run where every decision was priced must read as WIDE, or
    the sentence is a constant wearing a measurement's clothes.
    """
    narrow = decisions_that_existed(_funnel(
        {vbr.STAGE_PRICED: 216, vbr.STAGE_DECLINED: 63,
         vbr.STAGE_PRODUCT_NOT_UPLIFTABLE: 1350}, {"'svt'": 1350}))["reading"]
    assert "77.4%" in narrow and "1,629 term boundaries" in narrow

    wide = decisions_that_existed(_funnel({vbr.STAGE_PRICED: 40}))["reading"]
    assert "100.0%" in wide and "term boundaries" not in wide

    empty = decisions_that_existed(_funnel({vbr.STAGE_PRODUCT_NOT_UPLIFTABLE: 40}))
    assert empty["priced_share_of_the_decisions_that_existed"] is None
    assert "undefined" in empty["reading"]
