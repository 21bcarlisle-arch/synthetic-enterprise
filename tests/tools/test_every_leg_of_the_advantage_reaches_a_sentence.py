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
"""

import json
from pathlib import Path

import pytest

import tools.generate_value_arms_data as gva

PROJECT = Path(__file__).resolve().parents[2]
OBSERVABILITY = PROJECT / "docs" / "observability"

#: A floor whose legs all clear their own bar, and one whose legs SPLIT. Both are real artefacts
#: already in this repository, chosen by measuring the corpus rather than by construction -- a
#: fabricated family would make every assertion below unfalsifiable.
UNANIMOUS_FLOOR = OBSERVABILITY / "value_cycle_ab_s1_noise_floor.json"
SPLIT_FLOOR = OBSERVABILITY / "value_cycle_ab_s1_noise_floor_20260910b.json"


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


def _run():
    return _load(gva.THREE_ARM_PATH)


def _split(run):
    return run.get("level_vs_selection") or {}


def _bar(floor_path):
    run = _run()
    split = _split(run)
    return gva._legs_on_one_bar(_load(floor_path),
                                run, split, split.get("clock"))


def test_every_bounded_contrast_reaches_a_reading_of_its_own():
    """Fires on: dropping a leg from the loop, or hard-coding the selection contrast again.

    The defect was not that the level leg was graded wrongly -- it was never graded. So the
    control is over the PARTITION and not over one leg: every contrast this file says it bounds
    has to arrive with its own estimate, its own bar and its own sentence.
    """
    block = _bar(UNANIMOUS_FLOOR)
    assert block["available"] is True, block
    legs = block["legs"]
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
    leg = _bar(UNANIMOUS_FLOOR)["legs"][gva.LEVEL_CONTRAST]
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
    run = _run()
    floor = _load(UNANIMOUS_FLOOR)
    rows = [s for s in floor["seeds"] if isinstance(s, dict)]
    legs = _bar(UNANIMOUS_FLOOR)["legs"]
    for key, leg in legs.items():
        values = [row[key] for row in rows]
        assert leg["estimate_gbp"] == pytest.approx(sum(values) / len(values)), (
            "{}'s estimate is not the mean of {}'s own seed rows".format(key, key))
        assert leg["estimate_seeds"] == leg["bound_seeds"] == len(values), leg
    sems = {key: leg["bound_gbp"] for key, leg in legs.items()}
    assert len(set(sems.values())) == len(sems), (
        "two legs share a standard error, so at least one is bounded by another leg's "
        "family: {}".format(sems))
    assert run is not None


def test_the_selection_leg_reads_the_same_on_both_routes():
    """Fires on: the new path reading the wrong seed rows.

    `error_bar.selection_leg` comes from the spread the floor's PRODUCER publishes;
    `legs_on_one_bar` derives every leg from the floor's own rows. The selection leg is the one
    place the two routes overlap, so it is the only thing that can check the derivation that
    bounds the other two -- and a derivation that cannot reproduce the single figure it is
    checkable against has no business bounding anything.
    """
    run = _run()
    split = _split(run)
    floor = _load(UNANIMOUS_FLOOR)
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
    This asserts the level leg CAN be stated while the selection leg CANNOT, on a floor that is
    already in this repository -- which is the state the whole finding is about -- and that a
    floor exists where every leg clears. Neither family is constructed here; both were found by
    running this grader over the real corpus.
    """
    unanimous = _bar(UNANIMOUS_FLOOR)["legs"]
    split = _bar(SPLIT_FLOOR)["legs"]
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
    clause = _bar(SPLIT_FLOOR)["the_verdicts"]
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
    clause = _bar(UNANIMOUS_FLOOR)["the_verdicts"]
    legs = _bar(UNANIMOUS_FLOOR)["legs"]
    against_us = (legs[gva.LEVEL_CONTRAST]["sign"] == "positive"
                  and legs[gva.SELECTION_CONTRAST]["sign"] == "negative")
    assert against_us, "this floor no longer reads against the company; the control below is moot"
    assert "AGAINST THIS COMPANY" in clause, clause
    assert "flat rule beat the control by MORE" in clause, clause


def test_a_floor_that_bounds_nothing_grades_no_leg_and_says_why():
    """Fires on: the new block inventing a bound the bounds block itself refuses.

    Every leg here is graded off the same rows `_seed_spreads` guards, so a floor it refuses is a
    floor that bounds no leg. The permissive failure -- deriving the level and value families
    locally and skipping those five refusals -- is the one this is written against.
    """
    run = _run()
    split = _split(run)
    floor = _load(UNANIMOUS_FLOOR)
    worldless = dict(floor, world_identity={})
    block = gva._legs_on_one_bar(worldless, run, split, split.get("clock"))
    assert block["available"] is False, block
    assert "legs" not in block, "a refused floor still handed the page legs to render"
    assert block["reason"], block
    assert block["why_no_leg_is_graded"], block
    assert block["reason"] == gva._seed_spreads(worldless, run)["reason"], (
        "the refusal was softened rather than republished; a narrower reason about one leg is "
        "how a page comes to render two legs a bound was withheld from")
