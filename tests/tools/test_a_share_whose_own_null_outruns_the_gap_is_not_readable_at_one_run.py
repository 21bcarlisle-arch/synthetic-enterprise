"""A share whose own seed-redraw range exceeds the gap being attributed may not be read at n=1.

THE DEFECT THIS GUARDS (2026-09-22, Lane 0). `current_world.composition` led with
`level_share_of_advantage: 0.985` and explained its 17.9x disagreement with the superseded panel by
counting three confounders -- the date, the commit and the book. All three genuinely differ and the
explanation is an order of magnitude too small for what it explains: `value_cycle_ab_s1_noise_floor_
next12_20260917.json` re-runs that same world with NOTHING moved but the per-household elasticity
draw and takes the same statistic from 0.067 to 12.074. The page had differenced a quantity,
reasoned about the difference and published the reasoning without ever asking what the quantity
does when nothing is done to it -- while the null sat measured in `docs/observability/` with no
reader. Those two strings appeared zero times in the feed.

WHAT IS KEYED AND WHAT IS DELIBERATELY NOT. The property is *the statistic's own null range is
wider than the gap being attributed*, a comparison of two measured spans. NOTHING here pins 12.9x,
181x, 0.067, 12.074, or today's share. A control pinned to the current span goes red when the
instrument gets quieter -- which is the repair -- and stays green when the claim rots, which is
exactly backwards and is a shape this repository has paid for repeatedly.

THE RARE BRANCH IS ASSERTED REACHABLE BEFORE ANYTHING IS ASSERTED ABOUT IT.
`test_both_verdicts_are_reachable_from_one_family` drives wider AND narrower out of the same
function by moving only the family's endpoints. A refusal that fires on every input passes every
test of a refusal, and the narrower branch is the one nothing on disk currently produces.

R15 -- the mutations, each run and reverted:
  * `null_is_wider_than_the_disagreement` -> always True: `test_a_null_narrower_than_the_gap_does
    _not_refuse_the_share` reds.
  * `null_is_wider_than_the_disagreement` -> always False: `test_a_null_wider_than_the_gap_refuses
    _the_share_at_one_run` reds.
  * compare `>=` instead of `>`: nothing reds -- an EQUIVALENCE at these inputs, not a missing
    test, and it is left alone rather than pinned, because a tie between two measured spans is not
    a state this page can distinguish.
  * drop the `n < 2` guard: `test_a_family_of_one_draw_is_not_a_null` reds (a one-row family has
    range 0 and would read as a null of no width -- the direction in which every share is
    readable).
  * `_read(path) or {}` so an unreadable artefact falls through to the size guard:
    `test_an_unreadable_family_refuses_and_never_licenses_a_reading` reds ON THE REASON STRING and
    not on `available`. That is the leg it was written for -- both mutants refuse, and "we could
    not read the file" and "the family is too small" are the two sentences a reader needs kept
    apart; an assertion on `available` alone would have passed this mutant.
  * `share_of_the_movement` -> denominator `abs(control - level)` instead of the sum of absolute
    changes: `test_the_arm_share_counts_what_it_says_it_counts` reds.
  * `_which_arm_moved` deltas swapped in sign: `test_the_numerator_delta_is_the_two_arms_own
    _difference` reds (the identity is what makes the split exhaustive).
The null rung -- the REAL artefacts, which must keep producing a refusal with the real family's
own numbers in it -- is `test_the_real_feed_publishes_the_null_beside_the_figure`.
"""
from __future__ import annotations

import json

import pytest

from tools import generate_value_arms_data as g

#: THE FEED'S PATH FROM THE PRODUCER'S OWN CONSTANT, never re-rooted off `__file__`. One home for
#: it, so a control cannot go on reading a file the generator stopped writing -- and re-deriving a
#: repo root here is the shape `tests/architecture/test_a_control_reads_python_as_code.py` censuses,
#: which refused this file on its first landing for exactly that reason.
FEED = g.OUT_PATH


def _family(lo, hi, n=12, book=154, mean=None, stdev=1.0):
    """A seed-redraw family in the shape `_the_shares_own_null` reads, with the span it is given."""
    return {
        "world_identity": {"digest": "a-world"},
        "redraw_key_means": "the per-household elasticity assignment",
        "level_share_spread": {"n": n, "min": lo, "max": hi,
                               "mean": (lo + hi) / 2 if mean is None else mean, "stdev": stdev},
        "seeds": [{"billing_accounts_settled_in_window": book} for _ in range(n)],
    }


def _null(lo, hi, share=0.98, superseded=0.06, books=(164, 165), tmp_path=None, **kw):
    path = tmp_path / "family.json"
    path.write_text(json.dumps(_family(lo, hi, **kw)), encoding="utf-8")
    return g._the_shares_own_null(share, superseded, books, path)


# --- the partition, asserted reachable before anything is asserted about either half -------------

def test_both_verdicts_are_reachable_from_one_family(tmp_path):
    """Wider and narrower both come out of the same function on the same shape of input.

    THE CONTROL OVER THE WHOLE PARTITION, written before the two legs below and not derived from
    them. Each leg on its own is satisfied by a function that answers the same way always; only
    asking for both answers out of one call site catches that.
    """
    gap = 0.9
    wide = _null(0.0, gap * 3, superseded=0.98 - gap, tmp_path=tmp_path)
    narrow = _null(0.0, gap / 3, superseded=0.98 - gap, tmp_path=tmp_path)
    assert wide["null_is_wider_than_the_disagreement"] is True
    assert narrow["null_is_wider_than_the_disagreement"] is False
    assert wide["statement"] != narrow["statement"]


def test_a_null_wider_than_the_gap_refuses_the_share_at_one_run(tmp_path):
    """The refusal fires, says it is a property of the STATISTIC, and reaches `why_not_readable`."""
    null = _null(0.0, 2.7, share=0.98, superseded=0.08, tmp_path=tmp_path)
    block = g._composition_in_this_world(
        {"level_share_of_advantage": 0.98}, None, 0.08, "a-world",
        later_runs=[], shares_own_null=null)
    assert block["readable"] is False
    assert block["the_shares_own_null"] is null
    # The refusal LEADS -- it is the reason that does not depend on which two runs are compared.
    assert block["why_not_readable"].startswith(null["statement"])
    assert "PROPERTY OF THE STATISTIC" in null["statement"]


def test_a_null_narrower_than_the_gap_does_not_refuse_the_share(tmp_path):
    """The quiet branch: the null is published, it does not refuse, and it still reaches the page.

    THE LEG THAT MAKES THE REFUSAL MEAN SOMETHING. If this verdict could not be reached, the
    refusal above would be a constant wearing a comparison's clothes.
    """
    null = _null(0.0, 0.2, share=0.98, superseded=0.08, tmp_path=tmp_path)
    block = g._composition_in_this_world(
        {"level_share_of_advantage": 0.98}, None, 0.08, "a-world",
        later_runs=[], shares_own_null=null)
    assert null["null_is_wider_than_the_disagreement"] is False
    assert block["readable"] is not False or "seed-redraw null" in block["why_not_readable"]
    # It is still SAID -- a page that printed the null only when it refused is one a reader could
    # not tell from a page that never measured it.
    assert null["statement"] in block["why_not_readable"]
    assert "NARROWER" in null["statement"]


# --- what the comparison counts ------------------------------------------------------------------

def test_the_comparison_is_two_spans_of_one_statistic_and_not_a_fold(tmp_path):
    """`times_the_observed_disagreement` divides two differences, never one share by another.

    THE ENDPOINT FOLD -- 12.074 / 0.067 -- is what this defect was FOUND by and is deliberately
    not the comparator: it is undefined the day a draw lands at or below zero, and this family's
    numerator is not determined enough in sign to rule that out.
    """
    null = _null(-1.0, 1.0, share=0.9, superseded=0.4, tmp_path=tmp_path)
    assert null["range"] == pytest.approx(2.0)
    assert null["observed_disagreement"] == pytest.approx(0.5)
    assert null["times_the_observed_disagreement"] == pytest.approx(4.0)
    # A negative endpoint does not break it, which is the whole reason for the choice.
    assert null["null_is_wider_than_the_disagreement"] is True


def test_a_family_of_one_draw_is_not_a_null(tmp_path):
    """One row has range zero, and a null of no width makes every share readable."""
    null = _null(0.5, 0.5, n=1, tmp_path=tmp_path)
    assert null["available"] is False
    assert "two or more draws" in null["why_not"]
    assert "null_is_wider_than_the_disagreement" not in null


def test_an_unreadable_family_refuses_and_never_licenses_a_reading(tmp_path):
    """Absence of a null is not a null of no width, and it may not set `readable` True."""
    missing = g._the_shares_own_null(0.98, 0.06, (164, 165), tmp_path / "nothing.json")
    assert missing["available"] is False
    assert "unmeasured here" in missing["why_not"]
    block = g._composition_in_this_world(
        {"level_share_of_advantage": 0.98}, None, 0.06, "a-world",
        later_runs=[], shares_own_null=missing)
    assert block["readable"] is not True


def test_the_book_the_null_was_drawn_on_is_stated_against_the_shares_own(tmp_path):
    """A null on a neighbouring book is published WITH the mismatch, never as this run's own.

    KEYED TO CONTAINMENT AND NOT EQUALITY, because the arms of every three-arm run on disk span
    two books: a function asking `==` would answer `None` on every real input, and a caveat that
    is structurally unanswerable agrees with every answer to it.
    """
    outside = _null(0.0, 3.0, books=(164, 165), book=154, tmp_path=tmp_path)
    inside = _null(0.0, 3.0, books=(164, 165), book=164, tmp_path=tmp_path)
    assert outside["book_matches_the_share"] is False
    assert "NEIGHBOURING book" in outside["statement"]
    assert inside["book_matches_the_share"] is True
    assert "NEIGHBOURING book" not in inside["statement"]
    unknown = _null(0.0, 3.0, books=None, tmp_path=tmp_path)
    assert unknown["book_matches_the_share"] is None


# --- which arm moved -----------------------------------------------------------------------------

def _contrast(control, level):
    return {"available": True, "control_net_gbp": control, "level_arm_net_gbp": level}


def test_the_numerator_delta_is_the_two_arms_own_difference():
    """`level_advantage_gbp` is level-minus-control, so its movement is exactly the two deltas'.

    THE IDENTITY IS WHAT MAKES THE SPLIT EXHAUSTIVE. If it did not hold, "97.5% of the movement is
    the control arm" would be a share of something other than the thing that moved.
    """
    moved = g._which_arm_moved(_contrast(100.0, 500.0), _contrast(300.0, 560.0))
    assert moved["control_net_gbp"]["delta"] == pytest.approx(200.0)
    assert moved["level_arm_net_gbp"]["delta"] == pytest.approx(60.0)
    assert moved["numerator_delta_gbp"] == pytest.approx((560.0 - 300.0) - (500.0 - 100.0))


def test_the_arm_share_counts_what_it_says_it_counts():
    """One arm's absolute change over the SUM of both -- not over the numerator's own change."""
    moved = g._which_arm_moved(_contrast(100.0, 500.0), _contrast(300.0, 560.0))
    assert moved["share_of_the_movement"] == pytest.approx(200.0 / (200.0 + 60.0))
    assert moved["the_arm_that_moved"] == "control"
    # The other arm can carry it too -- the verdict is not a constant.
    other = g._which_arm_moved(_contrast(100.0, 500.0), _contrast(110.0, 900.0))
    assert other["the_arm_that_moved"] == "level"


def test_no_movement_at_all_is_refused_rather_than_divided():
    """A share of zero movement is a divide by a rounding error dressed as a percentage."""
    still = g._which_arm_moved(_contrast(100.0, 500.0), _contrast(100.0, 500.0))
    assert still["available"] is False
    assert "no movement here to attribute" in still["why_not"]


def test_a_run_without_an_arm_contrast_refuses_with_its_reason_named():
    assert g._which_arm_moved(_contrast(1.0, 2.0), None)["available"] is False
    partial = g._which_arm_moved(_contrast(1.0, 2.0), {"available": True, "control_net_gbp": 3.0})
    assert partial["available"] is False
    assert "level_arm_net_gbp" in partial["why_not"]


# --- the null rung: the real feed --------------------------------------------------------------

def test_the_real_feed_publishes_the_null_beside_the_figure():
    """The shipped feed carries the null and the arm split, with the family's own numbers in them.

    NOT A PIN ON THE SPAN. This asserts the block is present, available and composed from the
    family it names -- the endpoints are read out of the feed and compared to each other, never to
    a literal, so the day a quieter instrument lands this stays green and the REFUSAL lifts by
    itself in `_the_shares_own_null`.
    """
    if not FEED.exists():
        pytest.skip("the feed has not been generated in this tree")
    comp = (json.loads(FEED.read_text(encoding="utf-8")).get("current_world")
            or {}).get("composition") or {}
    if not comp.get("available"):
        pytest.skip("this publish states no composition, which its own block explains")
    null = comp.get("the_shares_own_null") or {}
    assert null.get("available") is True, null.get("why_not")
    assert null["range"] == pytest.approx(null["max"] - null["min"])
    assert null["n"] >= 2
    # Whatever the verdict, it is the one the two measured spans imply -- never a stored answer.
    assert null["null_is_wider_than_the_disagreement"] is (
        null["range"] > null["observed_disagreement"])
    assert null["statement"] in comp["why_not_readable"]
    arms = comp.get("which_arm_moved") or {}
    assert arms.get("available") is True, arms.get("why_not")
    assert arms["numerator_delta_gbp"] == pytest.approx(
        arms["level_arm_net_gbp"]["delta"] - arms["control_net_gbp"]["delta"])


# --- the zero gap: two causes, neither of them an agreement --------------------------------------

def _zero_gap(tmp_path, same_run):
    """Both panels reporting the SAME share, with the two runs' identity block as the only input
    that moves. `_family(0.0, 2.7)` is the wide null the legs above already use."""
    path = tmp_path / "family.json"
    path.write_text(json.dumps(_family(0.0, 2.7)), encoding="utf-8")
    return g._the_shares_own_null(0.5, 0.5, (164, 165), path,
                                  differences={"the_same_run": same_run})


def test_both_causes_of_a_zero_gap_are_reachable_and_say_different_things(tmp_path):
    """The partition over `observed == 0`, asserted reachable before either leg is read.

    THE DEFECT THIS GUARDS (2026-09-23, Lane 0). `times_the_observed_disagreement` guards
    `observed > 0`; the `statement` branch three lines under it did not, and evaluated
    `null_range / observed` unconditionally. So the first pair of panels whose shares matched
    exactly did not publish a wrong figure -- it raised ZeroDivisionError out of `generate()` and
    produced NO FEED AT ALL. One legal rule, two implementations, and the guard on only one of
    them. Found by building the feed on the 2026-09-18 corrected one-book run, where the two panel
    constants resolve to a single artefact.

    AND IT IS REACHED WITHOUT ANYONE EDITING A CONSTANT. `value_cycle_ab_s1_three_arm.json` is the
    path the release machinery PROMOTES the newest run onto, so a promotion alone can point
    `THREE_ARM_PATH` and `CURRENT_WORLD_THREE_ARM_PATH` at the same file.

    ZERO HAS TWO CAUSES AND THEY MUST NOT COLLAPSE. One run compared with itself replicated
    nothing; two runs that happened to return the same share are a coincidence inside a wide null.
    A reader told only "the shares are equal" would take either for a replication, and it is
    neither. So the two are driven out of ONE call site here, with the identity block as the only
    moving part -- a single-cause version of this test would pass against a function that answered
    the same way whatever produced the zero.
    """
    same = _zero_gap(tmp_path, True)
    coincide = _zero_gap(tmp_path, False)
    assert same["statement"] != coincide["statement"]
    assert "NO SECOND RUN" in same["statement"]
    assert "EXACTLY EQUAL" in coincide["statement"]
    # NEITHER MAY BE DIVIDED BY, and neither may read as the instrument having replicated.
    for block in (same, coincide):
        assert block["available"] is True
        assert block["observed_disagreement"] == 0
        assert block["times_the_observed_disagreement"] is None
        assert block["null_is_wider_than_the_disagreement"] is True
        assert "replicat" in block["statement"] or "coincidence" in block["statement"]


def test_a_zero_gap_refuses_the_share_through_the_production_caller(tmp_path):
    """The rule is reached by the function that builds the block, not only by a direct call.

    A control that only ever types the helper stays green while no production caller reaches it.
    `_composition_in_this_world` is the caller, and this drives it with the two panels carrying
    one share -- the state that used to raise before any block was built.
    """
    same = _zero_gap(tmp_path, True)
    block = g._composition_in_this_world(
        {"level_share_of_advantage": 0.5}, None, 0.5, "a-world",
        later_runs=[], shares_own_null=same)
    assert block["readable"] is False
    assert block["why_not_readable"].startswith(same["statement"])


def test_the_zero_gap_branch_is_what_stops_the_divide_and_not_a_caller_check(tmp_path):
    """Driven with NO identity block at all, which is how a stale caller would reach it.

    `differences=None` is the shape every caller written before 2026-09-23 passes. It must still
    return a block rather than raise: a guard that only holds when its caller remembers to supply
    an argument is a guard the next caller removes by omission.
    """
    path = tmp_path / "family.json"
    path.write_text(json.dumps(_family(0.0, 2.7)), encoding="utf-8")
    block = g._the_shares_own_null(0.5, 0.5, (164, 165), path)
    assert block["available"] is True
    assert block["times_the_observed_disagreement"] is None
    # Unknown identity falls to the COINCIDENCE wording, never to "there is no second run":
    # claiming one artefact when nothing established it is the flattering reading of an absence.
    assert "EXACTLY EQUAL" in block["statement"]
