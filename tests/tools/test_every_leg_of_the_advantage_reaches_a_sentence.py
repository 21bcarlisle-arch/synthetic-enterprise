"""THE DEFECT: the page summarised ONE leg of a three-leg advantage, and it was the quiet one.

`level_advantage_gbp` has been in every seed row of every noise floor this project has ever
written. Nothing read it. `_error_bar` computed a mean, a standard error, a bar and a verdict for
`selection_gbp` and for nothing else, so the only leg that reached a sentence on the surface was
the leg that could not state a side -- while the level leg, on the very same rows, sat 49 standard
errors from zero with 9 of 9 draws positive and published nothing at all.

A leg nobody summarises is indistinguishable on the page from a leg with nothing in it. And the
half the page was silent about is the half that reads AGAINST the company: one flat margin at the
same price level, with no per-customer inference in it anywhere, beat the control by MORE than the
inference arm did. The enterprise value claimed here is the inference; what this book can
demonstrate is the price.

Every control below names the defect it fires on. The two that matter most are the reachability
one -- a grader that can only ever produce one verdict passes every test of a verdict -- and the
two-routes one, because the new path could read the wrong rows and nothing else would notice.

THE SECOND DEFECT, AND IT WAS IN THIS FILE (2026-09-22). Seven of these controls went red when
`_legs_on_one_bar` became MORE honest: the live pairing is refused, because the published floor is
older than the figure it bounds and did not measure the same book. The controls indexed `legs` and
asserted `available is True`, so they were pinned to a state where the artefacts happened to agree.

The fixture defect underneath was not a stale stamp. This file named two FLOORS and then bolted
both onto whatever `THREE_ARM_PATH` carried on the day the test ran -- and a noise floor bounds THE
RUN IT WAS MEASURED ON. Pairing a 09-10 floor with a 09-18 figure asks a question the bounds rule
is right to refuse, and it is not the question the paragraphs above say this file asks. **The
subject of every control here is a PAIR, and the fixture was half of one.** So each floor is now
named with the contemporaneous run it bounds, both frozen committed artefacts, and the premise that
makes the pair admissible is asserted in `test_each_fixture_pair_is_admitted_for_a_stated_reason`
rather than left for seven assertions to discover the hard way.

WHAT THE CORPUS SAYS ABOUT THE LEGS IS NOT PINNED HERE. Two floors on the live run's own side of
the ordering rule exist and are admitted, and on them the selection leg reads -1,069 at 0.69 SEMs
and -259 at 0.17 SEMs -- against -1,749 at 2.85 SEMs on the 09-10 nine. The negative sign is a
property of which floor was drawn, not of the book. That belongs in the knowledge layer and is
written up in
`docs/staging/SEAT_FINDING_SEVEN_CONTROLS_PAIRED_EVERY_FLOOR_WITH_THE_LIVE_RUN_INSTEAD_OF_THE_RUN_IT_WAS_MEASURED_ON_2026-09-22.md`;
no control below asserts it. These controls assert that the grader DISCRIMINATES, which is a
property. Which way it discriminates today is a result, and a result does not belong in a test.
"""

import json
from pathlib import Path

import pytest

import tools.generate_value_arms_data as gva

PROJECT = Path(__file__).resolve().parents[2]
OBSERVABILITY = PROJECT / "docs" / "observability"

#: A FLOOR AND THE RUN IT WAS MEASURED ON -- the pair, because half a pair cannot be graded. Both
#: families are real artefacts already in this repository, chosen by measuring the corpus rather
#: than by construction: a fabricated family would make every assertion below unfalsifiable. One
#: pair's legs all clear their own bar; the other's SPLIT. They share a run, differ by ninety
#: minutes of wall clock and nine fresh seeds, and disagree about the selection leg by a factor of
#: ten -- which is why both are kept rather than one being preferred.
UNANIMOUS_PAIR = (OBSERVABILITY / "value_cycle_ab_s1_noise_floor.json",
                  OBSERVABILITY / "value_cycle_ab_s1_three_arm_20260910.json")
SPLIT_PAIR = (OBSERVABILITY / "value_cycle_ab_s1_noise_floor_20260910b.json",
              OBSERVABILITY / "value_cycle_ab_s1_three_arm_20260910.json")

#: WHAT THE PAGE ACTUALLY PUBLISHES, and it is here to be a REAL instance of the refusing branch.
#: `test_a_floor_that_bounds_nothing_grades_no_leg_and_says_why` used to reach that branch only by
#: hand-mutating a floor's world identity away, which exercises one refusal out of the five
#: `_seed_spreads` can take and proves nothing about the rest. This pair is refused by the
#: production rule over production bytes, and it is deliberately NOT asserted to be refused: what
#: is asserted is that the block agrees with `_seed_spreads` whichever way that goes, so the day
#: the floor is re-run on the figure's own tree this control keeps its meaning with nobody editing
#: a string.
LIVE_PUBLISHED_PAIR = (gva.NOISE_FLOOR_PATH, gva.THREE_ARM_PATH)


def _load(path: Path) -> dict:
    """The artefact, or a named failure. An unavailable subject is a FAILED check, never a skip.

    Also the ONE place in this file that turns a path into bytes. A control that both reads a file
    and asserts over the text it got is the substring-scan shape `tools/substring_source_scan_census`
    enumerates, and it is the shape regardless of the file being JSON -- the census cannot know
    that and must not be asked to guess.
    """
    if not path.is_file():
        pytest.fail("{} is missing -- this control's subject is UNAVAILABLE, and an unavailable "
                    "check is a FAILED check (R15)".format(path))
    return json.loads(path.read_text(encoding="utf-8"))


def _run(pair):
    return _load(pair[1])


def _split(run):
    return run.get("level_vs_selection") or {}


def _bar(pair):
    """The graded block for a (floor, run) pair -- the pair, never a floor against today's run."""
    run = _run(pair)
    split = _split(run)
    return gva._legs_on_one_bar(_load(pair[0]), run, split, split.get("clock"))


def _graded(pair):
    """The block, having first established it was admitted AND said why it could be.

    The failure this exists for is the one that cost this file seven reds: `block["legs"]` on a
    refused block raises `KeyError` in the middle of an assertion about sentences, and the reader
    is told nothing about the pairing that is the actual cause. A fixture whose premise has gone is
    a BROKEN FIXTURE and has to say so in those words.
    """
    block = _bar(pair)
    assert block["available"] is True, (
        "the fixture pair {} x {} is no longer admitted by the bounds rule, so this control has no "
        "subject -- repair the PAIR, do not soften the assertion. The rule's own reason: {}".format(
            pair[0].name, pair[1].name, block.get("reason")))
    return block


def test_each_fixture_pair_is_admitted_for_a_stated_reason():
    """Fires on: the bounds rule ceasing to admit the pairs the rest of this file is built on.

    THE PREMISE, ASSERTED RATHER THAN ASSUMED. Every control below rests on these pairs being
    gradable, and that is a claim about the production rule, not about the fixtures. Asserted here
    once, so a rule change reds ONE control naming the pairing -- rather than reding seven that
    each look like a defect in a leg.

    And it asserts WHY, not just THAT: the ordering is the property the rule is over, so the pair
    has to satisfy the ordering on its own stamps. A pair that passed the rule while failing the
    ordering would mean the rule had stopped being about the ordering.
    """
    for pair in (UNANIMOUS_PAIR, SPLIT_PAIR):
        floor, run = _load(pair[0]), _load(pair[1])
        assert floor["generated_at"] >= run["generated_at"], (
            "{} was measured BEFORE the run it is paired with here, so this fixture asks the "
            "bounds rule a question it is right to refuse".format(pair[0].name))
        assert (floor.get("world_identity") or {}).get("digest") == (
            (run.get("world_identity") or {}).get("digest")), (
            "{} and {} name different worlds".format(pair[0].name, pair[1].name))
        assert gva._seed_spreads(floor, run)["available"] is True, (
            "the bounds rule now refuses {} x {}".format(pair[0].name, pair[1].name))


def test_every_bounded_contrast_reaches_a_reading_of_its_own():
    """Fires on: dropping a leg from the loop, or hard-coding the selection contrast again.

    The defect was not that the level leg was graded wrongly -- it was never graded. So the
    control is over the PARTITION and not over one leg: every contrast this file says it bounds
    has to arrive with its own estimate, its own bar and its own sentence.
    """
    legs = _graded(UNANIMOUS_PAIR)["legs"]
    assert set(legs) == set(gva._BOUNDED_CONTRASTS), (
        "the advantage has {} bounded legs and only {} reached a reading; a leg nobody "
        "summarises reads on the page exactly like a leg with nothing in it".format(
            len(gva._BOUNDED_CONTRASTS), len(legs)))
    for key, leg in legs.items():
        assert leg["available"] is True, (key, leg)
        assert leg["reading"], "{} carries no sentence".format(key)
        assert leg["subject"] in leg["reading"], (
            "{}'s sentence does not name {} -- a reading that names another leg's subject is "
            "worse than none".format(key, leg["subject"]))


def test_the_level_leg_states_its_sign_because_its_own_family_determines_one():
    """Fires on: the level leg reaching a reading that withholds a sign its family earns.

    Keyed to the family and not to today's answer: the assertion is that the verdict FOLLOWS the
    measurement. A level leg whose draws straddled zero would fail this by its own numbers, which
    is the correct direction for it to fail in.
    """
    leg = _graded(UNANIMOUS_PAIR)["legs"][gva.LEVEL_CONTRAST]
    assert leg["sems_from_zero"] > leg["sems_needed_to_state_a_sign"], leg
    assert leg["sign_is_stateable"] is True, leg
    assert leg["sign"] == ("positive" if leg["estimate_gbp"] > 0 else "negative"), leg
    assert leg["sign"] in leg["reading"], leg["reading"]


def test_each_leg_is_graded_at_its_own_familys_bar_and_over_its_own_rows():
    """Fires on: grading one leg against another's standard error or another's rows.

    The mutation this is written for is the cheap version of the repair -- publish three legs, one
    spread. It would render three verdicts, all of them wrong for two legs, and every other
    control here would stay green.
    """
    floor = _load(UNANIMOUS_PAIR[0])
    rows = [s for s in floor["seeds"] if isinstance(s, dict)]
    legs = _graded(UNANIMOUS_PAIR)["legs"]
    for key, leg in legs.items():
        values = [row[key] for row in rows]
        assert leg["estimate_gbp"] == pytest.approx(sum(values) / len(values)), (
            "{}'s estimate is not the mean of {}'s own seed rows".format(key, key))
        assert leg["estimate_seeds"] == leg["bound_seeds"] == len(values), leg
    sems = {key: leg["bound_gbp"] for key, leg in legs.items()}
    assert len(set(sems.values())) == len(sems), (
        "two legs share a standard error, so at least one is bounded by another leg's "
        "family: {}".format(sems))


def test_the_selection_leg_reads_the_same_on_both_routes():
    """Fires on: the new path reading the wrong seed rows.

    `error_bar.selection_leg` comes from the spread the floor's PRODUCER publishes;
    `legs_on_one_bar` derives every leg from the floor's own rows. The selection leg is the one
    place the two routes overlap, so it is the only thing that can check the derivation that
    bounds the other two -- and a derivation that cannot reproduce the single figure it is
    checkable against has no business bounding anything.
    """
    run = _run(UNANIMOUS_PAIR)
    split = _split(run)
    floor = _load(UNANIMOUS_PAIR[0])
    bar = gva._error_bar(floor, split.get("selection_gbp"), run, split.get("clock"), split)
    published = bar["selection_leg"]
    derived = bar["legs_on_one_bar"]["legs"][gva.SELECTION_CONTRAST]
    # THE VERDICT KEYS ARE COMPARED EXACTLY AND THE MONEY KEYS TO A PENNY. The two routes take
    # the square root in a different order -- one over the artefact's published variance, one over
    # a variance summed here -- so they agree to the last float bit but not to the last bit of
    # it. Demanding bit equality would red on a difference of 1e-13 of a penny and teach the next
    # reader that this control is noise; demanding a penny is the claim actually being made.
    for key in ("estimate_seeds", "bound_seeds", "sign_is_stateable", "sign"):
        assert derived[key] == published[key], (
            "the two routes to the selection leg disagree on {}: {} against {}".format(
                key, derived[key], published[key]))
    for key in ("estimate_gbp", "bound_gbp", "sems_from_zero", "sems_needed_to_state_a_sign"):
        assert derived[key] == pytest.approx(published[key], abs=0.01), (
            "the two routes to the selection leg disagree on {}: {} against {}".format(
                key, derived[key], published[key]))


def test_both_verdicts_are_reachable_over_real_floors_on_this_disk():
    """Fires on: a grader that can only ever produce one verdict.

    A partition every test asks one side of is a partition nothing has established is a partition.
    This asserts the level leg CAN be stated while the selection leg CANNOT, on a pair that is
    already in this repository -- which is the state the whole finding is about -- and that a pair
    exists where every leg clears. Neither family is constructed here; both were found by running
    this grader over the real corpus, and they share a run, so the difference between them is nine
    seeds and nothing else.
    """
    unanimous = _graded(UNANIMOUS_PAIR)["legs"]
    split = _graded(SPLIT_PAIR)["legs"]
    assert all(leg["sign_is_stateable"] is True for leg in unanimous.values()), unanimous
    assert split[gva.LEVEL_CONTRAST]["sign_is_stateable"] is True, split[gva.LEVEL_CONTRAST]
    assert split[gva.SELECTION_CONTRAST]["sign_is_stateable"] is False, (
        split[gva.SELECTION_CONTRAST])
    assert split[gva.SELECTION_CONTRAST]["sign"] is None, split[gva.SELECTION_CONTRAST]


def test_the_split_verdict_says_the_level_is_what_can_be_called():
    """Fires on: a verdict sentence that reports two legs without reporting the contrast.

    The contrast IS the claim. "The level leg is positive" and "the selection leg cannot be
    called" are each half an answer, and a reader left to pair them from two paragraphs has been
    handed the conflation this feed refuses everywhere else.
    """
    clause = _graded(SPLIT_PAIR)["the_verdicts"]
    assert "price LEVEL" in clause, clause
    assert "value MOVED" in clause, clause
    assert "cannot yet call" in clause, clause


def test_a_unanimous_family_that_reads_against_the_company_says_so():
    """Fires on: a verdict sentence that states a positive level and a negative choosing as two
    neutral measurements.

    Derived from the two signs and never asserted: a publish where the choosing turns positive
    drops the sentence with nobody editing a string. That is what makes it a reading rather than
    a confession pinned to today's answer.
    """
    block = _graded(UNANIMOUS_PAIR)
    legs = block["legs"]
    against_us = (legs[gva.LEVEL_CONTRAST]["sign"] == "positive"
                  and legs[gva.SELECTION_CONTRAST]["sign"] == "negative")
    assert against_us, "this pair no longer reads against the company; the control below is moot"
    clause = block["the_verdicts"]
    assert "AGAINST THIS COMPANY" in clause, clause
    assert "flat rule beat the control by MORE" in clause, clause


def test_a_floor_that_bounds_nothing_grades_no_leg_and_says_why():
    """Fires on: the new block inventing a bound the bounds block itself refuses.

    Every leg here is graded off the same rows `_seed_spreads` guards, so a floor it refuses is a
    floor that bounds no leg. The permissive failure -- deriving the level and value families
    locally and skipping those five refusals -- is the one this is written against.
    """
    run = _run(UNANIMOUS_PAIR)
    split = _split(run)
    floor = _load(UNANIMOUS_PAIR[0])
    worldless = dict(floor, world_identity={})
    block = gva._legs_on_one_bar(worldless, run, split, split.get("clock"))
    assert block["available"] is False, block
    assert "legs" not in block, "a refused floor still handed the page legs to render"
    assert block["reason"], block
    assert block["why_no_leg_is_graded"], block
    assert block["reason"] == gva._seed_spreads(worldless, run)["reason"], (
        "the refusal was softened rather than republished; a narrower reason about one leg is "
        "how a page comes to render two legs a bound was withheld from")


def test_the_published_pair_is_graded_by_the_bounds_rule_and_by_nothing_else():
    """Fires on: the block second-guessing `_seed_spreads` on the pair the READER actually meets.

    The control above reaches the refusing branch by hand-mutating a world identity away, which
    exercises ONE of the five refusals `_seed_spreads` can take. This asks the same question of
    production bytes through the production rule -- today that is a staleness-and-book refusal,
    which the mutated fixture cannot reach at all.

    KEYED TO THE PROPERTY AND NOT TO TODAY'S REFUSAL, deliberately: it asserts the block AGREES
    with the bounds rule, in both directions, and that a refusal costs the page every leg. The day
    the floor is re-run on the figure's own tree this goes on meaning the same thing with nobody
    editing a string -- and the day the block starts grading legs off a pairing the rule refused,
    it reds. Pinning `available is False` here would have reproduced the exact defect this file
    was just repaired for, one branch over.
    """
    run = _run(LIVE_PUBLISHED_PAIR)
    floor = _load(LIVE_PUBLISHED_PAIR[0])
    spreads = gva._seed_spreads(floor, run)
    block = _bar(LIVE_PUBLISHED_PAIR)
    assert block["available"] is spreads["available"], (
        "the legs block and the bounds rule disagree about whether {} bounds {}".format(
            LIVE_PUBLISHED_PAIR[0].name, LIVE_PUBLISHED_PAIR[1].name))
    if block["available"]:
        assert set(block["legs"]) == set(gva._BOUNDED_CONTRASTS), block["legs"]
        assert block["the_verdicts"], block
    else:
        assert "legs" not in block, "a refused pairing still handed the page legs to render"
        assert block["reason"] == spreads["reason"], (
            "the page's refusal is not the bounds rule's refusal, so a reader is being given a "
            "cause nothing measured")
        assert block["why_no_leg_is_graded"], block
