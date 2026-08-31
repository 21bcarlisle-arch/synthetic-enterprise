"""Rung 3 of the world validation ladder, on churn: is there anything for the company to infer?

Canon: `docs/staging/DIRECTOR_CANON_WORLD_VALIDATION_LADDER_2026-08-31.md` §2 rung 3. *"A variable
that passes rungs 0-2 and fails rung 3 is a world that replays rather than lives."* This is the
control that says which. Assessment: `docs/design/LADDER_APPLIED_TO_CHURN_2026-08-31.md`.

WHY THIS CONTROL EXISTS AND WHAT IT IS NOT. It is not a quality bar on the company's model. The
score it reads is the WORLD's own realised hazard -- ground truth the company may never see -- so it
measures whether the world contains per-customer signal at all. If this goes red, every A/B result
in the programme is an artefact, and no company-side improvement could have helped.

KEYED TO THE PROPERTY, NOT TO TODAY'S ANSWER. Nothing here asserts 0.6760. Rebuilding the hazards
from the individuals up -- which the canon requires where a rung fails -- should move that number a
long way, and a control pinned to it would go red for the work being done right. What is asserted
is: the reading clears its own null, the null is a real null, a world with no per-customer variation
cannot pass, and the reading is taken over the WHOLE BOOK rather than whichever part of it a capture
happened to see.

THE SUBJECT IS A CAPTURED ARTEFACT AND HALF ITS PRODUCER IS NOT YET IN GIT. `ladder_churn_factors
_svt_segment_decisions.json` was produced by `run_phase2b` recording `_svt_decisions`, an
observability-only addition that sits in the working tree ON TOP OF C1b's departure roll -- which is
another lane's uncommitted work at the time this landed. So this control's subject is reproducible
from the tree that ran, and NOT from this commit alone, until C1b lands. Named here rather than left
to be discovered: re-running `tools/capture_departure_factors` before then writes an EMPTY SVT file
and says so loudly on stderr, and the fourth leg below then refuses rather than reporting a clean
AUC over 144 renewals.

THE SECOND AND THIRD LEGS WERE LEARNED BY PAYING FOR THEM. A control shaped only as "observed >
null_high" is green the moment the null collapses -- exactly the failure that let three of four
mutations survive on the domain-constant gate the night before this was written
(`feedback_a_ratchet_with_no_floor_cannot_fail`). Legs 2 and 3 put a floor under the null itself: it
must have width, it must sit on chance, and a score that carries no information must NOT clear it.
Every fail-open in the AUC or the shuffle breaks at least one of those.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools import measure_churn_heterogeneity as mch
from tools.inference_claim import CANNOT_TELL

PROJECT = Path(__file__).resolve().parents[2]
TABLE = PROJECT / "docs" / "reports" / "ladder_churn_factors.json"

#: Fewer shuffles than the tool's default. 300 puts the 95% endpoints on the 7th and 292nd order
#: statistic, which moves the interval by under 0.01 between seeds -- and every assertion below has
#: far more margin than that. Measured, not assumed: the observed reading clears the null high end
#: by ~0.098 and the null median sits within 0.002 of 0.5.
PERMUTATIONS = 300

#: A null distribution for a rank statistic on shuffled labels is centred on chance. This is how
#: wide a window that claim gets before the null is not a null.
CHANCE = 0.5
CHANCE_TOLERANCE = 0.05

#: The narrowest a real permutation interval can be here. With 82 departures the sampling spread of
#: an AUC is wide; the observed interval is ~0.16 across. A null narrower than this has collapsed,
#: and a collapsed null makes leg 1 pass for free.
MIN_NULL_WIDTH = 0.05

#: Both departure routes must be in the reading. Not a fact about today's capture -- a property the
#: reading must have, and the one C1b broke silently: the renewal table went 465 -> 144 decisions
#: when the book moved onto the standard variable product, and no control could see that its
#: subject had become a minority of the thing it claimed to describe.
REQUIRED_ROUTES = frozenset({"renewal", "svt_segment"})


@pytest.fixture(scope="module")
def reading() -> dict:
    return mch.report(TABLE, permutations=PERMUTATIONS)


def test_the_world_carries_per_customer_churn_signal_and_it_clears_its_own_null(reading):
    """RUNG 3. The world's own hazard discriminates who leaves, beyond chance, inside a stratum.

    Inside a stratum matters twice over: two of the terms reaching the hazard take one value per
    calendar year, and the two departure routes run mean hazards 5.7x apart. A pooled reading would
    score "it is 2020" and "this household is on a fixed deal" as per-customer signal.

    MUTATION: replace `realized_churn_probability` with a constant in the loaded rows and this
    fires -- a constant score cannot clear a null.
    """
    assert reading["clears_the_null"] is True, (
        f"the world's churn does not carry per-customer signal: oracle AUC "
        f"{reading['oracle_auc']:.4f} sits inside its null "
        f"[{reading['null']['low']:.4f}, {reading['null']['high']:.4f}] — {CANNOT_TELL}. "
        "Rung 3 has failed and every A/B result in the programme is an artefact. "
        "The repair goes to the individual model, never to the aggregate."
    )
    assert reading["oracle_auc"] > reading["null"]["high"]


def test_the_null_is_a_real_null_and_has_not_collapsed(reading):
    """Leg 1 is meaningless if the null can be made to vanish. This is the floor under it.

    MUTATION: make `permutation_null` return `{"low": 0.0, "high": 0.0, "median": 0.0, ...}` and
    leg 1 still passes -- an AUC of anything beats 0.0. This fires on both the width and the centre.
    """
    null = reading["null"]
    width = null["high"] - null["low"]
    assert width >= MIN_NULL_WIDTH, (
        f"the null interval is {width:.4f} wide, below {MIN_NULL_WIDTH}: it has collapsed, and a "
        "collapsed null makes the rung-3 verdict pass for free"
    )
    assert abs(null["median"] - CHANCE) <= CHANCE_TOLERANCE, (
        f"the null median is {null['median']:.4f}, not chance: shuffled labels must score ~0.5, so "
        "either the shuffle is not shuffling or the AUC is not a rank statistic"
    )
    assert null["permutations"] == PERMUTATIONS


def test_a_score_that_carries_NO_information_does_not_clear_the_null(reading):
    """The other direction, and the one a pass-only control cannot ask.

    A constant score must land on chance and must NOT clear the null. If it does, the comparison is
    fail-open and leg 1 is green whatever the world does.

    MUTATION: make `auc` return 1.0 unconditionally, or compare with `>=` against a null whose high
    end is 1.0, and this fires.
    """
    rows = mch.load(TABLE)
    flat, pairs = mch.within_strata_auc(rows, lambda r: 1.0)
    assert pairs > 0
    assert flat == pytest.approx(CHANCE, abs=1e-9), (
        f"a constant score scored {flat}, not {CHANCE}: ties are not being scored at 0.5 and every "
        "AUC in this module is therefore not an AUC"
    )
    null = mch.permutation_null(rows, lambda r: 1.0, permutations=PERMUTATIONS)
    assert not (flat > null["high"]), (
        "a score carrying no information cleared its null: the rung-3 comparison is fail-open"
    )


def test_the_reading_REFUSES_a_book_too_thin_to_carry_it_and_names_the_count(tmp_path):
    """FAIL CLOSED. "We could not read enough of the book" must never reach a reader as "no signal".

    The population floor is the specific defence against a control going quiet by losing its
    subject. It is deliberately set so that **losing the SVT route alone would trip it**: the
    renewal route is 144 decisions and the floor is 200, so a capture that silently reverted to
    renewals-only refuses rather than reporting a clean-looking AUC over a minority of the book.

    MUTATION: delete the `MIN_DECISIONS` / `MIN_DEPARTURES` checks from `load` and this fires.
    """
    thin = tmp_path / "thin.json"
    rows = json.loads(TABLE.read_text())[:20]
    thin.write_text(json.dumps(rows))
    with pytest.raises(mch.Unreadable) as exc:
        mch.load(thin)
    assert "20" in str(exc.value) and str(mch.MIN_DECISIONS) in str(exc.value)

    empty = tmp_path / "empty.json"
    empty.write_text("[]")
    with pytest.raises(mch.Unreadable):
        mch.load(empty)

    with pytest.raises(mch.Unreadable) as exc:
        mch.load(tmp_path / "does_not_exist.json")
    assert "no factor table" in str(exc.value)

    # And the renewal route ALONE is below the floor, which is the C1b failure made mechanical.
    with pytest.raises(mch.Unreadable):
        mch.load(TABLE, whole_book=False)


def test_the_reading_covers_BOTH_departure_routes_and_says_which(reading):
    """A rung-3 verdict is a claim about a population, so the population is on the reading.

    C1b added a departure route that never reaches a renewal roll, and the capture kept recording
    renewal decisions only -- so the subject silently narrowed from the whole book to a minority of
    it and nothing went red. This asserts both halves: the reading SAYS what it covers, and what it
    covers is the whole book.

    MUTATION: drop `route_coverage` from `report`, let it return `{}`, or stop `capture_departure_
    factors` writing the SVT companion file, and this fires.
    """
    cover = reading["route_coverage"]
    assert set(cover) >= {"causes", "routes", "departures_by_route", "covers_svt_route", "population"}
    assert cover["population"]
    assert cover["causes"], "a table with no departure causes cannot support a rung-3 verdict"
    assert REQUIRED_ROUTES <= set(cover["routes"]), (
        f"the reading covers routes {sorted(cover['routes'])} but churn departs by "
        f"{sorted(REQUIRED_ROUTES)}: this is a verdict over part of the book presented as one over "
        "all of it — re-capture with `tools/capture_departure_factors`"
    )
    assert REQUIRED_ROUTES <= set(cover["departures_by_route"]), (
        "a route with zero departures cannot contribute to a rung-3 reading; if that is real, it "
        "is a finding about the world and not something to pass over"
    )
