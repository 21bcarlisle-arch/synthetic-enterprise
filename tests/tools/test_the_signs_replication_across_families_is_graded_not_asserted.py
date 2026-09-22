"""THE DEFECT: the page answered "we cannot tell" out of ONE refused pair while holding four.

`error_bar.legs_on_one_bar` is refused on today's publish -- correctly, the floor is older than the
figure and priced a different book -- so the page rendered one amber sentence and said nothing about
any leg. Meanwhile four same-world families in this repository grade the same three contrasts. They
AGREE on the value and level legs and they DISAGREE on the selection leg: -1,749 at 2.85 errors and
a stated NEGATIVE on one nine-seed floor, -170 at 0.55 on another nine-seed floor drawn from the
SAME RUN ninety minutes later. A sign that moves by a factor of ten between two draws of one
instrument is a property of the draw, and the page's strongest claim about the choosing rested on
whichever draw was published.

EVERY CONTROL HERE IS OVER A PROPERTY, NEVER OVER TODAY'S FOUR NUMBERS. What the corpus currently
says is a RESULT and results do not belong in tests -- it is written up in
`docs/staging/records/PREREG_THE_SIGN_ACROSS_FOUR_SAME_WORLD_FAMILIES_IS_PUBLISHED_AS_A`
`_QUESTION_2026-09-22.md`. What is asserted below is that the grader DISCRIMINATES: that it can say
`replicates` and can say it does not, that it reaches both answers off real production artefacts
rather than off a hand-built fixture, and that a family which could not be graded is counted as
neither agreement nor disagreement.

THE CONTROL THAT MATTERS MOST is `test_the_verdict_discriminates_replication_from_contest`. A
verdict that can only ever produce one answer passes every test OF that answer, and this project has
entered that trap through three different doors in one afternoon. So the partition is asserted whole
-- both outcomes, from one function, over committed bytes -- rather than one leg at a time.
"""

import json
from pathlib import Path

import pytest

import tools.generate_value_arms_data as gva

PROJECT = Path(__file__).resolve().parents[2]
OBSERVABILITY = PROJECT / "docs" / "observability"

#: A PAIR SET DRAWN FROM PRODUCTION THAT MAKES EVERY LEG REPLICATE, and it is the first entry of
#: the production tuple rather than anything constructed here. A single unanimous family trivially
#: agrees with itself, which is exactly the property needed: it is the `replicates` outcome reached
#: over real bytes. Fabricating a family to reach it would make the discrimination control assert
#: something about a fixture instead of about the rule.
UNANIMOUS_SUBSET = gva._REPLICATION_PAIRS[:1]


def _load(path: Path) -> dict:
    """The artefact, or a named failure. An unavailable subject is a FAILED check, never a skip."""
    if not path.is_file():
        pytest.fail("{} is missing -- this control's subject is UNAVAILABLE, and an unavailable "
                    "check is a FAILED check (R15)".format(path))
    return json.loads(path.read_text(encoding="utf-8"))


def _verdicts(block: dict) -> dict:
    return {key: leg["verdict"] for key, leg in block["per_leg"].items()}


def test_every_bounded_leg_reaches_a_replication_verdict():
    """Fires on: grading only the contested leg, so `contested` has nothing to be contested against.

    The claim this block makes is the CONTRAST between a leg whose sign survives a change of floor
    and one whose sign does not. A census over the selection leg alone could not make that claim --
    it would publish a disagreement with nothing on the page showing what agreement looks like, and
    a reader could dismiss the whole thing as these floors being too noisy to grade anything. So
    the control is over the PARTITION and not over the interesting member of it.
    """
    block = gva._the_sign_across_families()
    assert set(block["per_leg"]) == set(gva._BOUNDED_CONTRASTS), (
        "the advantage has {} bounded legs and only {} reached a replication verdict; a leg whose "
        "sign nobody tests for replication reads on the page exactly like a leg whose sign "
        "replicates".format(len(gva._BOUNDED_CONTRASTS), len(block["per_leg"])))
    for key, leg in block["per_leg"].items():
        assert leg["verdict"] in (
            "replicates", "contested", "not_settled", "no_family_grades_it"), (key, leg)
        assert leg["subject"], "{} reaches a verdict under no subject".format(key)


def test_the_verdict_discriminates_replication_from_contest():
    """Fires on: a verdict that can only ever say one thing -- the control that cannot fail.

    THE TRAP THIS IS WRITTEN AGAINST. Every other control here asks "does the block refuse
    correctly", and a grader that answered `not_settled` for every input would pass all of them
    while the page published a permanent shrug. The partition is therefore asserted WHOLE: one
    function, two pair sets of real committed artefacts, two different answers for the SAME leg.

    It is keyed to the property and not to which way today's corpus falls. It does not say the
    selection leg is contested; it says the grader can reach both sides of its own partition. The
    day a re-run makes the four families agree, `_the_sign_across_families()` moves to `replicates`
    and this control keeps its meaning with nobody editing a string.
    """
    unanimous = _verdicts(gva._the_sign_across_families(UNANIMOUS_SUBSET))
    everything = _verdicts(gva._the_sign_across_families())
    assert "replicates" in unanimous.values(), (
        "no pair set in this repository produces a `replicates` verdict, so the grader has never "
        "been shown to be able to say a sign SURVIVES a change of floor: {}".format(unanimous))
    assert set(everything.values()) - {"replicates"}, (
        "every leg replicates across every family, so the grader has never been shown to be able "
        "to say a sign is a property of the DRAW: {}".format(everything))
    moved = [key for key in gva._BOUNDED_CONTRASTS if unanimous[key] != everything[key]]
    assert moved, (
        "no leg's verdict changed between {} families and {} -- the verdict is not a function of "
        "the families at all, which is a constant wearing a computation's clothes".format(
            len(UNANIMOUS_SUBSET), len(gva._REPLICATION_PAIRS)))


def test_the_classifier_reaches_all_three_of_its_own_outcomes():
    """Fires on: `contested` and `not_settled` collapsing into one another.

    WRITTEN BECAUSE A MUTATION WAS SILENT, AND THE SILENCE WAS THE FLATTERING READING UNTIL IT WAS
    CHECKED. Replacing `verdict = "contested"` with `"not_settled"` reded nothing across eighteen
    controls. That is not an equivalence: it is an UNREACHABLE BRANCH. No two families on this disk
    state OPPOSITE signs today -- every sign stated is `negative` -- so nothing in the corpus can
    distinguish "the floors disagree about the sign" from "some floor cannot state one".

    Those are different claims and collapsing them would flatter whichever is convenient: a genuine
    disagreement between two instruments is much worse evidence than one instrument being quiet,
    and a page that printed the milder wording for both would understate what it found. So the
    distinction is kept, and its reachability is asserted HERE rather than left to a corpus that
    cannot currently exercise it.

    THE SUBJECT IS THE CLASSIFIER AND NOT THE WORLD, which is why rows are built here. This
    fabricates no evidence about the book: nothing below reaches the page, and `_the_sign_across_
    families` grades only real artefacts through the production rule. What is asserted is that
    `_leg_replication` is a function of its rows with three distinguishable outcomes -- a grader
    that can only ever produce one verdict passes every test OF that verdict.
    """
    def _row(available, states):
        return {"available": available,
                "legs": {"selection_gbp": {"what_this_family_states": states,
                                           "sems_from_zero": 2.9}}}

    quiet_row = _row(True, gva._NO_SIGN_AT_ITS_OWN_BAR)
    agree = [_row(True, "negative"), _row(True, "negative")]
    disagree = [_row(True, "negative"), _row(True, "positive")]
    quiet = [_row(True, "negative"), quiet_row]
    outcomes = {
        "replicates": gva._leg_replication(agree, "selection_gbp"),
        "contested": gva._leg_replication(disagree, "selection_gbp"),
        "not_settled": gva._leg_replication(quiet, "selection_gbp"),
    }
    for expected, got in outcomes.items():
        assert got["verdict"] == expected, (
            "two families that {} produced {!r} rather than {!r} -- the classifier cannot tell "
            "its own outcomes apart, so the page's wording is not a function of the "
            "evidence".format(
                {"replicates": "state the SAME sign", "contested": "state OPPOSITE signs",
                 "not_settled": "differ in whether a sign is stateable"}[expected],
                got["verdict"], expected))
    assert outcomes["replicates"]["signs_stated"] == ["negative"], outcomes["replicates"]
    assert outcomes["contested"]["signs_stated"] == ["negative", "positive"], (
        "a leg whose floors DISAGREE does not publish BOTH signs, so a reader is handed one "
        "instrument's answer as though every instrument gave it")
    assert outcomes["not_settled"]["families_that_state_a_sign"] == 1, outcomes["not_settled"]
    assert gva._leg_replication([], "selection_gbp")["verdict"] == "no_family_grades_it", (
        "an EMPTY family set reaches a verdict about replication, which is a control's own "
        "filters emptying the evidence and the guard reading empty as no complaint")


def test_a_family_that_could_not_be_graded_is_neither_agreement_nor_disagreement():
    """Fires on: counting a structurally silent family as a family that states no sign.

    THE SHAPE THIS FORBIDS. A family the bounds rule refused, or one whose artefacts are missing,
    cannot state a sign -- and if the denominator counted it, its silence would read as evidence
    that the sign does not replicate. A field structurally unable to answer a question agrees with
    every answer to it, and here it would manufacture a contest out of an absence.

    The published pair is the live instance: `NOISE_FLOOR_PATH` x `THREE_ARM_PATH` is refused by
    the production rule today, and appending it must move no verdict.
    """
    absent = ("a pair whose artefacts are not on this disk",
              "value_cycle_ab_s1_noise_floor_THERE_IS_NO_SUCH_FILE.json",
              "value_cycle_ab_s1_three_arm.json")
    base = gva._the_sign_across_families()
    padded = gva._the_sign_across_families(gva._REPLICATION_PAIRS + (absent,))
    assert padded["families_offered"] == base["families_offered"] + 1, (
        "the unreadable family was DROPPED rather than reported; a census that silently omits "
        "what it could not open publishes a smaller disagreement than it found")
    assert padded["families_graded"] == base["families_graded"], padded["families_graded"]
    assert _verdicts(padded) == _verdicts(base), (
        "an unreadable family moved a replication verdict, so silence is being counted as an "
        "answer: {} against {}".format(_verdicts(padded), _verdicts(base)))
    for key, leg in padded["per_leg"].items():
        assert leg["families_that_state_a_sign"] <= leg["families_that_could_grade_it"], (key, leg)
    # AND IT SAYS WHY IT COULD NOT BE GRADED, in the field the page renders. Reporting the row
    # while withholding its reason puts "we tried and could not read it" and "nobody asked" into
    # the same pixels -- the fail-silent shape one level down from dropping it outright, and the
    # mutation that renamed this key survived every assertion above.
    row = padded["families"][-1]
    assert row["readable"] is False and row["available"] is False, row
    assert row.get("reason"), (
        "the unreadable family is reported carrying NO reason, so a reader cannot tell a family "
        "this census failed to open from one it never had: {}".format(row))


def test_the_published_refused_pair_moves_no_verdict_either():
    """Fires on: admitting a refused pair into the census, where its silence would read as a sign.

    The live publish is the real instance of the refusing branch, and it is REFUSED BY THE
    PRODUCTION RULE over production bytes rather than by anything this file arranged. It is
    deliberately not asserted to be refused: what is asserted is that the census agrees with
    `_legs_on_one_bar` whichever way that rule goes, so the day the floor is re-run on the figure's
    own book this control keeps its meaning.
    """
    live = ("the pair this page publishes",
            gva.NOISE_FLOOR_PATH.name, gva.THREE_ARM_PATH.name)
    base = gva._the_sign_across_families()
    padded = gva._the_sign_across_families(gva._REPLICATION_PAIRS + (live,))
    row = padded["families"][-1]
    floor, run = _load(gva.NOISE_FLOOR_PATH), _load(gva.THREE_ARM_PATH)
    rule = gva._seed_spreads(floor, run)["available"]
    assert row["available"] is bool(rule), (
        "the census and the bounds rule disagree about the published pair -- the census is a "
        "second grader, which is the permissive one because none of `_seed_spreads`' five "
        "refusals come with it")
    if not rule:
        assert _verdicts(padded) == _verdicts(base), (
            "a pair the bounds rule REFUSED moved a replication verdict")
        assert row.get("reason"), "a refused family is in the census carrying no reason"


def test_no_family_is_graded_by_anything_but_the_production_rule():
    """Fires on: re-deriving the legs here instead of calling `_legs_on_one_bar`.

    A second implementation of the grading rule would be the permissive one -- it would carry none
    of the five refusals `_seed_spreads` takes -- and it would publish readings the rest of the
    page would refuse. So every row is checked against what the production grader returns for the
    same pair, figure for figure.
    """
    for row in gva._the_sign_across_families()["families"]:
        run = _load(OBSERVABILITY / row["run"])
        split = run.get("level_vs_selection") or {}
        direct = gva._legs_on_one_bar(_load(OBSERVABILITY / row["floor"]), run, split,
                                      split.get("clock"))
        assert row["available"] is bool(direct.get("available")), row["family"]
        if not row["available"]:
            continue
        for key, leg in row["legs"].items():
            straight = direct["legs"][key]
            assert leg["what_this_family_states"] == gva._what_a_family_states(straight), (
                row["family"], key)
            # AND THE STRING IS THE SIGN ITSELF WHEN THERE IS ONE, so the row cannot quietly
            # become prose that no longer tracks the grader it claims to report.
            if straight["sign_is_stateable"] is True:
                assert leg["what_this_family_states"] == straight["sign"], (row["family"], key)
            assert leg["sems_from_zero"] == straight["sems_from_zero"], (row["family"], key)


def test_the_reading_is_composed_from_the_verdicts_and_not_written_beside_them():
    """Fires on: a constant sentence -- the one that stays true-sounding after the evidence moves.

    A sentence asserting the selection leg's sign is a property of the draw would go on saying so
    on the day a re-run settled it. So the two pair sets that reach opposite verdicts must also
    reach different sentences, and the one whose legs all replicate must not claim a contest.
    """
    unanimous = gva._the_sign_across_families(UNANIMOUS_SUBSET)
    everything = gva._the_sign_across_families()
    assert unanimous["the_reading"] != everything["the_reading"], (
        "the same sentence is published for a family set where every leg replicates and one where "
        "a leg does not -- it is a literal, not a reading")
    assert "not a gap in it" not in unanimous["the_reading"], (
        "the all-replicate reading claims a contrast between legs that do and do not replicate, "
        "when every leg replicated: {}".format(unanimous["the_reading"]))
    for key, leg in everything["per_leg"].items():
        if leg["verdict"] != "replicates":
            assert leg["subject"] in everything["the_reading"], (
                "{} does not replicate and the sentence never names it".format(key))


def test_the_strength_of_the_replicating_legs_is_measured_and_not_typed():
    """Fires on: re-introducing the hard-coded `49 standard errors` the first draft carried.

    That literal is what makes "these floors are not simply too noisy to call anything" a claim
    rather than an assertion, and as a literal it would still read 49 on the day the replicating
    legs weakened to 3 -- the claim inverting while the page went on stating it. It is keyed to the
    property: whatever number the sentence quotes must be the one the rows actually reach.
    """
    def _quoted(pairs):
        block = gva._the_sign_across_families(pairs)
        keys = {key for key, leg in block["per_leg"].items() if leg["verdict"] == "replicates"}
        strongest = gva._strongest_sems(gva._replication_pair_blocks(pairs), keys)
        assert strongest is not None, "no replicating leg reached a distance from zero"
        assert "{:.1f} standard errors".format(strongest) in block["the_reading"], (
            "the sentence quotes a distance the rows do not reach: {!r}".format(
                block["the_reading"]))
        return strongest

    # TWO PAIR SETS, BECAUSE ONE CANNOT TELL A LITERAL FROM A FUNCTION. Asserting only that the
    # sentence quotes `_strongest_sems(...)` was silent under the exact mutation it was written
    # for -- re-typing the number as `49.5` -- because that literal IS today's value. A control
    # keyed to today's answer agrees with the defect it exists to catch. The subset below drops
    # the family carrying the strongest leg, so a hard-coded number can satisfy at most one of
    # these two and a derived one satisfies both.
    full = _quoted(gva._REPLICATION_PAIRS)
    weaker = _quoted(gva._REPLICATION_PAIRS[1:])
    assert full != weaker, (
        "dropping the family that carries the strongest replicating leg did not move the number "
        "the sentence quotes, so that number is not a function of the families at all")
    rows = gva._replication_pair_blocks()
    keys = {key for key, leg in gva._the_sign_across_families()["per_leg"].items()
            if leg["verdict"] == "replicates"}
    assert gva._strongest_sems(rows, set()) is None, (
        "a leg set nobody replicates still reports a strength, so the figure is not a function of "
        "the legs it claims to be about")
    assert gva._strongest_sems([], keys) is None, (
        "an EMPTY family set still reports a strength -- the guard is reading empty as no "
        "complaint, which is how a control's own filters manufacture a pass")


def test_the_feed_carries_the_census_on_the_branch_that_needs_it():
    """Fires on: attaching the census only where `legs_on_one_bar` was already available.

    The refusing branch is the branch the page is silent on, and it is the branch this whole block
    exists for. Publishing the census only when the legs already graded would put it exactly where
    it adds nothing.
    """
    feed = json.loads((PROJECT / "site" / "data" / "value_arms.json").read_text(encoding="utf-8"))
    bar = (feed.get("error_bar") or {})
    census = bar.get("does_the_sign_replicate")
    assert census, "the published feed carries no replication census at all"
    assert census.get("the_reading"), "the census reaches the feed carrying no sentence"
    assert census.get("families"), "the census reaches the feed naming no family"
    if not (bar.get("legs_on_one_bar") or {}).get("available"):
        assert census.get("families_graded"), (
            "the published pair is REFUSED and the census graded nothing either, so the page is "
            "silent on every leg while four same-world families sit on this disk")
