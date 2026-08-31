"""The world's satisfaction heterogeneity must survive the trip from the population to the hazard.

Ladder rung 3: `docs/design/LADDER_APPLIED_TO_CHURN_2026-08-31.md` item 1.
Pre-registration: `docs/staging/WORKER_PREREGISTRATION_WHAT_A_CONTINUOUS_SATISFACTION_RESPONSE_MUST_SHOW_2026-08-31.md`.

WHAT WENT WRONG AND WHY NOTHING SAW IT. `sim_satisfaction` was made continuous in July,
knowledge-first, against Ofgem/Citizens Advice Wave 20 -- and `satisfaction_churn_multiplier` went
on collapsing its 434 distinct values to three, 88% of the book sharing one. The repair reached the
producer and stopped at the consumer, and every test on both sides passed throughout, because each
side was correct in isolation. The measured cost was `sim_dissatisfaction_response` tied on 92.0% of
within-stratum pairs and contributing **+0.0000** to the world's rung-3 discrimination.

KEYED TO THE PROPERTY, NOT TO THE CURVE. Nothing here asserts a multiplier value that is not already
a declared constant of the module. The thresholds are miscalibrated against the published
distribution (0.6% of the book above 0.80 against a published 38% very satisfied) and re-aiming them
is registered work -- **this control must pass when that happens.** What it holds is that the
population's variation ARRIVES: households who differ in satisfaction differ in hazard, the ordering
runs the right way, and the module's three declared anchors stay mutually consistent.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from simulation.satisfaction_churn import (
    _HIGH_SATISFACTION_MULTIPLIER,
    _HIGH_SATISFACTION_THRESHOLD,
    _LOW_SATISFACTION_MULTIPLIER,
    _LOW_SATISFACTION_THRESHOLD,
    satisfaction_churn_multiplier,
)
from simulation.sim_satisfaction import BASELINE_SATISFACTION

PROJECT = Path(__file__).resolve().parents[2]
#: Real captured satisfaction scores, not synthetic ones: the defect was invisible to every
#: hand-written input and visible immediately on the book.
CAPTURE = PROJECT / "docs" / "reports" / "ladder_churn_factors.json"

#: How many captured decisions this control needs before it will say anything. Population floor:
#: a scan that finds fewer has lost its subject, and a tie fraction over eight rows is noise.
#:
#: PROVEN LOAD-BEARING, AND THE FIRST MUTATION I WROTE FOR IT WAS AN EQUIVALENCE. Removing the
#: floor alone leaves every leg green -- because 144 rows clears 100 either way, so the bound was
#: not binding and relaxing it changes nothing. The mutation that establishes it has to make the
#: population thin AS WELL: on an 8-row capture this control ERRORS with the floor and reads
#: **3 passed** without it. A green tie fraction over eight households is exactly the shape that
#: reads as a result. Recorded because "the mutation did not fire" was the flattering reading and
#: it was the wrong one.
MIN_DECISIONS = 100
#: And the scores must actually vary. If the producer regresses to a point mass, the tie fraction
#: below would read 100% and this names the real cause rather than blaming the consumer.
MIN_DISTINCT_SCORES = 50

#: The ceiling on tied (household, household) pairs. Three buckets gave 92%; a continuous function
#: over a continuous score gives essentially none. Set well above zero so that a future model with
#: a genuine plateau -- say a saturating response at the extremes -- still passes, and far below 92
#: so the defect cannot return.
MAX_TIE_FRACTION = 0.35


@pytest.fixture(scope="module")
def scores() -> list[float]:
    rows = json.loads(CAPTURE.read_text())
    values = [r["satisfaction_score"] for r in rows if r.get("satisfaction_score") is not None]
    assert len(values) >= MIN_DECISIONS, (
        f"{len(values)} captured satisfaction scores is below the floor of {MIN_DECISIONS}: this "
        "control has lost its subject and would pass on an empty book"
    )
    assert len(set(values)) >= MIN_DISTINCT_SCORES, (
        f"only {len(set(values))} distinct satisfaction scores in {len(values)} decisions: the "
        "PRODUCER has regressed to a near-point-mass, and no consumer can carry variation that is "
        "not there. Fix sim_satisfaction, not satisfaction_churn."
    )
    return values


def test_the_populations_satisfaction_variation_ARRIVES_at_the_hazard(scores):
    """The measured property: households who differ in satisfaction differ in churn multiplier.

    MUTATION: return a constant, or restore any bucketing (`return 1.0` between the thresholds),
    and this fires -- three buckets over this book give a tie fraction of 0.92.
    """
    multipliers = [satisfaction_churn_multiplier(s) for s in scores]
    n = len(multipliers)
    pairs = n * (n - 1) // 2
    tied = sum(
        1
        for i in range(n)
        for j in range(i + 1, n)
        if multipliers[i] == multipliers[j]
    )
    fraction = tied / pairs
    assert fraction <= MAX_TIE_FRACTION, (
        f"{fraction:.1%} of household pairs get an IDENTICAL churn multiplier from "
        f"{len(set(scores))} distinct satisfaction scores. A tied pair scores 0.5 in any rank "
        "statistic whatever hazard is attached to it, so this variable cannot discriminate at any "
        "magnitude — the population's heterogeneity is being discarded between the producer and "
        "the hazard. Ladder rung 3."
    )


def test_the_response_is_MONOTONE_because_more_satisfaction_is_never_more_churn(scores):
    """Direction, over the real book and over the whole domain.

    MUTATION: swap the two endpoint multipliers, or invert the interpolation, and this fires.
    """
    grid = [i / 500 for i in range(501)] + sorted(scores)
    ordered = sorted(set(grid))
    values = [satisfaction_churn_multiplier(s) for s in ordered]
    for a, b, va, vb in zip(ordered, ordered[1:], values, values[1:]):
        assert vb <= va + 1e-12, (
            f"satisfaction {b:.4f} carries multiplier {vb:.4f}, ABOVE satisfaction {a:.4f}'s "
            f"{va:.4f}: a happier household is being modelled as more likely to leave"
        )
    assert values[0] > values[-1], "the response is flat across its whole domain"


def test_the_three_declared_ANCHORS_stay_mutually_consistent(scores):
    """The neutral point is the model's own baseline, and it is DERIVED rather than chosen.

    `sim_satisfaction.BASELINE_SATISFACTION` is the score of a household with no bill shock, no
    income stress and no tenure bonus. It must be neutral. It is not written down anywhere in
    `satisfaction_churn` -- it falls out of the line between the two declared endpoints -- and this
    leg is what keeps that true when someone re-aims a threshold or a dose.

    The thresholds ARE miscalibrated (0.6% of the book above 0.80 against a published 38% very
    satisfied) and re-aiming them is registered work. When that happens this leg reds unless the
    endpoints are re-derived with it, which is the point: three anchors that no longer agree are a
    model that has silently moved its neutral point.

    MUTATION: move either threshold or either multiplier alone and this fires.
    """
    assert satisfaction_churn_multiplier(BASELINE_SATISFACTION) == pytest.approx(1.0, abs=1e-12), (
        f"a household at BASELINE_SATISFACTION={BASELINE_SATISFACTION} gets multiplier "
        f"{satisfaction_churn_multiplier(BASELINE_SATISFACTION)}, not 1.0. The three anchors this "
        "model declares no longer agree: either a threshold moved without the doses being "
        "re-derived, or the producer's baseline moved. Re-derive, do not add a fourth constant."
    )
    assert satisfaction_churn_multiplier(_HIGH_SATISFACTION_THRESHOLD) == _HIGH_SATISFACTION_MULTIPLIER
    assert satisfaction_churn_multiplier(_LOW_SATISFACTION_THRESHOLD) == _LOW_SATISFACTION_MULTIPLIER
    assert _LOW_SATISFACTION_THRESHOLD < BASELINE_SATISFACTION < _HIGH_SATISFACTION_THRESHOLD, (
        "the model's neutral satisfaction sits outside the band this function interpolates over, "
        "so the neutral point is no longer derivable from the endpoints"
    )
