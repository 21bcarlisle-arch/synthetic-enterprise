"""THE DEFECT: an AUC travels to a page without the strata it was computed inside.

`measure_churn_heterogeneity` computes every reading inside `by_year_and_route` and says so ONCE,
at the foot of `report`, in `stratified_by`. The blocks a downstream page lifts --
`per_route.renewal.company_belief[]`, which `generate_value_arms_data._renewal_churn_belief` reads
wholesale -- carried a bare `belief_auc` and a bare `pairs`, and `pairs` counts SAME-STRATUM pairs.
So a reader of the live page met `0.6706 on 384 pairs` with nothing saying that 384 is 15% of the
route's 2,501 comparable pairs, or that the figure is a stratified one at all.

WHY THAT IS THE EXPENSIVE SHAPE HERE AND NOT A TIDINESS POINT. This repository withdrew a household
claim on 2026-09-10 for the mirror of it: a POOLED AUC published where a stratified one was owed,
12% of whose pairs compared two households in the same year. The remedy chosen then --
`decisions.discrimination_auc_within_year`, `method_skill.churn_auc_within_year` -- was to publish
the stratified twin beside the headline WITH its pair count and share. The renewal-belief block,
which now carries the company's most direct claim about itself, shipped with neither twin nor
share, and a reader had no way to tell which of the two statistics they were holding.

EACH LEG BELOW NAMES ITS OWN DEFECT. The partition leg is the load-bearing one: a block that
asserted the stratified reading is the conservative one would be keyed to the day it was written,
and on this book it is the HIGHER of the two.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

from tools.measure_churn_heterogeneity import (
    STRATIFIED_BY,
    belief_readings,
    stratification,
    within_strata_auc,
)

PROJECT = Path(__file__).resolve().parents[2]


def _rows(pairs_by_year: dict, field: str = "belief") -> list[dict]:
    """`{year: [(score, departed), ...]}` -> rows this module's estimators accept."""
    out = []
    for year, entries in pairs_by_year.items():
        for score, departed in entries:
            out.append({
                "market_year": year,
                "route": "renewal",
                "event_type": "churned" if departed else "renewed",
                field: score,
            })
    return out


#: Stratifying DROPS the reading: inside each year the departed household scores BELOW the one that
#: stayed, and only the year level puts the later year's departure above the earlier year's stayer.
#: Pooled reads 0.25; within-year reads 0.0.
_STRATIFYING_LOWERS = {2020: [(1.0, True), (2.0, False)], 2021: [(3.0, True), (4.0, False)]}
#: Stratifying RAISES it: the ordering is right inside every year, and pooling drags it down by
#: comparing an early departure with a late stayer. Pooled 0.75; within-year 1.0.
_STRATIFYING_RAISES = {2020: [(2.0, True), (1.0, False)], 2021: [(4.0, True), (3.0, False)]}


def _stratification_for(spec: dict) -> dict:
    rows = _rows(spec)
    score = lambda r: r["belief"]  # noqa: E731 — handed to the estimator, not called here
    observed, pairs = within_strata_auc(rows, score)
    return stratification(rows, score, observed, pairs)


def test_the_direction_is_derived_and_both_sides_are_reachable():
    """THE DEFECT: `the_stratified_reading_is` is pinned to whichever side today's book lands on.

    A control that only ever saw one side would pass just as happily against a constant, and the
    block would go on asserting "the stratified figure is the conservative one" long after the book
    stopped supporting it. ONE assertion over the WHOLE partition, per the rule this project wrote
    after entering the same trap three times in an afternoon: both branches are shown reachable
    here, so a hardcoded side reds whichever side it was hardcoded to.
    """
    lower = _stratification_for(_STRATIFYING_LOWERS)
    higher = _stratification_for(_STRATIFYING_RAISES)

    assert lower["the_stratified_reading_is"] == "lower", lower
    assert higher["the_stratified_reading_is"] == "higher", higher
    assert lower["stratification_moved_the_reading"] < 0 < \
        higher["stratification_moved_the_reading"]
    # AND THE SIGN AGREES WITH THE TWO FIGURES IT IS DERIVED FROM, on both sides. A field that
    # named a direction its own numbers contradict is the shape `_renewal_churn_belief`'s ceiling
    # sentence rotted into: a verdict string beside figures that had moved past it.
    for block in (lower, higher):
        assert block["stratification_moved_the_reading"] == pytest.approx(
            block["auc_stratified"] - block["auc_pooled"])


def test_the_share_is_a_quotient_of_the_two_counts_beside_it():
    """THE DEFECT: `same_stratum_share` is a number that no longer divides the counts it sits by.

    Before dividing two numbers, say what each one counts -- this one is same-stratum pairs over
    ALL comparable pairs on the same rows, and the two counts are published beside it precisely so
    a reader can do the division. A share that stopped being that quotient would be a figure with
    the authority of a measurement and the content of a guess.
    """
    block = _stratification_for(_STRATIFYING_LOWERS)
    assert block["comparable_pairs_pooled"] >= block["same_stratum_pairs"] > 0
    assert block["same_stratum_share"] == pytest.approx(
        block["same_stratum_pairs"] / block["comparable_pairs_pooled"])
    # Four rows, one departure and one stayer in each of two years: 2 same-stratum pairs of 4
    # comparable ones. Typed here because a quotient control that computes both sides from the
    # same call cannot tell a right answer from a consistent wrong one.
    assert (block["same_stratum_pairs"], block["comparable_pairs_pooled"]) == (2, 4)


def test_an_unreadable_reading_leaves_the_move_unstated_rather_than_zero():
    """THE DEFECT: a reading that could not be computed publishes a zero difference.

    `None` and `0.0` are opposite findings here -- "we could not compare the two" against "the
    stratification changed nothing" -- and the second is the flattering one. Declared `None` and
    silent `None` collapsing into the flattering branch is a shape this repository has paid for.
    """
    rows = _rows(_STRATIFYING_LOWERS)
    score = lambda r: r["belief"]  # noqa: E731
    block = stratification(rows, score, None, 0)
    assert block["stratification_moved_the_reading"] is None
    assert block["the_stratified_reading_is"] is None
    # The POOLED side is still readable on these rows and is still published: withholding a
    # measurement that succeeded because a different one failed is the wrong blast radius.
    assert block["auc_pooled"] is not None


def test_every_graded_belief_carries_the_strata_and_not_only_the_artefact_foot():
    """THE DEFECT: the stratification is declared where the page does not read.

    `_renewal_churn_belief` lifts `per_route.renewal.company_belief[]` and nothing else. This is the
    leg that reds if the declaration is moved back to a single `stratified_by` at the top of the
    artefact, which is exactly where it was and exactly why the page could not carry it.
    """
    rows = _rows(_STRATIFYING_RAISES, field="company_churn_estimate")
    graded = [b for b in belief_readings(rows, "renewal", 50) if b.get("available")]
    assert graded, "no belief arm graded on these rows — the leg below would be vacuous"
    for arm in graded:
        block = arm["stratification"]
        assert block["stratified_by"] == STRATIFIED_BY
        assert block["the_published_reading_is_the_stratified_one"] is True
        # THE ARM'S OWN HEADLINE FIGURES ARE THE ONES DESCRIBED, not a second computation that
        # could drift from them. A block describing a different number than the one beside it is
        # worse than no block.
        assert block["auc_stratified"] == arm["belief_auc"]
        assert block["same_stratum_pairs"] == arm["pairs"]


def test_a_reseeded_capture_refuses_to_land_on_the_production_stem():
    """THE DEFECT: the second draw overwrites the first, and the pair it was taken for is gone.

    `capture_departure_factors --roll-seed` exists to produce a SECOND reading of one book beside
    the first. Written to the default stem it would replace it, and every reader downstream joins a
    capture to its SVT sibling by NAME -- so the halves would silently describe two different
    draws. Refused at the entry point, with the reason on stderr.
    """
    out = subprocess.run(
        [sys.executable, "-m", "tools.capture_departure_factors", "--roll-seed", "1"],
        cwd=PROJECT, capture_output=True, text=True, timeout=120)
    assert out.returncode == 2, out.stdout[-2000:] + out.stderr[-2000:]
    assert "stem of its own" in out.stderr


def test_the_reseeded_roll_moves_the_dice_and_nothing_else():
    """THE DEFECT: a "re-seeded" run comes back byte-identical and reports a spread of zero.

    Two ways to get that, and both have been paid for in this tree: patching the WRONG module (the
    importing one rather than the defining one), and a substitute that is not actually a different
    stream. The first is caught by the second capture's own row count; this leg catches the second,
    and asserts the distribution is unchanged -- a re-draw that moved the distribution would be a
    different WORLD, which is not what a repetition control may be.
    """
    from simulation.customer_events import churn_roll_for_renewal
    from tools.capture_departure_factors import reseeded_churn_roll

    accounts = [f"BA{i:04d}" for i in range(400)]
    term = "2021-04-01"
    real = [churn_roll_for_renewal(a, term) for a in accounts]
    patched = reseeded_churn_roll(churn_roll_for_renewal, 20260922)
    drawn = [patched(a, term) for a in accounts]

    assert all(0.0 <= r < 1.0 for r in drawn)
    # A DIFFERENT STREAM: not one account keeps its roll. Anything less and the patch is reaching
    # only part of the book.
    assert all(a != b for a, b in zip(real, drawn))
    # THE SAME DISTRIBUTION: uniform on [0, 1), so the two means sit within a few standard errors
    # of each other. Loose on purpose — this leg asks whether the substitute is still uniform, and
    # a tight bound here would be a control on the seed rather than on the mechanism.
    assert abs(sum(drawn) / len(drawn) - sum(real) / len(real)) < 0.1
    # AND THE SEED IS IN THE STREAM. Two seeds that produced one stream would make every
    # repetition a replay of the first draw wearing a new number.
    assert drawn != [reseeded_churn_roll(churn_roll_for_renewal, 1)(a, term) for a in accounts]


def test_the_live_artefact_carries_the_block_wherever_it_carries_an_auc():
    """THE DEFECT: the repair holds in the function and not in the file the page actually reads.

    A green unit test over synthetic rows says the producer can do this. It does not say the
    committed artefact does, and the artefact is what `_renewal_churn_belief` opens. SKIPPED rather
    than passed when the artefact predates the repair: a skip is honest about having measured
    nothing, and a pass here would certify a file nobody checked.
    """
    path = PROJECT / "docs" / "observability" / "svt_drift_belief_grade.json"
    if not path.exists():
        pytest.skip(f"no grade artefact at {path}")
    grade = json.loads(path.read_text())
    arms = [b for b in ((grade.get("per_route") or {}).get("renewal") or {}).get(
        "company_belief", []) if b.get("available")]
    if not arms or "stratification" not in arms[0]:
        pytest.skip("the committed grade predates this repair — re-take it with "
                    "`python3 -m tools.measure_churn_heterogeneity "
                    "--out=docs/observability/svt_drift_belief_grade.json`")
    for arm in arms:
        assert arm["stratification"]["same_stratum_pairs"] == arm["pairs"]
        assert arm["stratification"]["comparable_pairs_pooled"] >= arm["pairs"]
