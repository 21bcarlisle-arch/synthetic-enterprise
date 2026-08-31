"""The SVT belief must be able to distinguish two households at the SAME INSTANT.

THE DEFECT THIS NAMES. v1 of `estimate_svt_drift` carried two observables, `years_on_svt` and
`segment_days`, and both are CALENDAR. Two accounts sitting side by side on the same cap period
differed in neither, so the belief returned one number for both and could only ever order the
billing calendar. The instrument measured exactly that: 0.4691 per exposure-day, inside a null of
[0.4164, 0.5834], while the oracle ceiling of 0.6091 cleared. A belief every household shares
cannot select a household.

KEYED TO THE PROPERTY, NOT TO TODAY'S ANSWER, which is this project's most repeated control defect.
Nothing here pins the AUC, the band positions, the spacing, or the current grade set. What is
asserted is that the belief RESPONDS to something that varies per household at one instant — so
this stays green if the observable is replaced by a better one, and goes red the moment the belief
goes back to being a function of the calendar alone. Pinning 0.4691 or the 1.00/0.75/0.50/0.25/0.00
spacing would have done the reverse: red on an improvement, green on a rot.

WHAT IS DELIBERATELY NOT ASSERTED. That the belief is any GOOD. It reads inside or outside its null
on evidence, not on assertion, and `test_the_svt_drift_belief_is_not_wired_to_any_decision` is what
holds it away from decisions until that evidence exists. A control that asserted the model was
working would be asserting the thing the measurement is for.
"""
from __future__ import annotations

import pytest

from company.crm.churn_desk import (
    _ESTIMATE_DP,
    SVT_DRIFT_BELIEF_ANNUAL_LONG_STAYER,
    SVT_DRIFT_BELIEF_ANNUAL_RECENT,
    SVT_DRIFT_BELIEF_BAND_LONG_STAYER,
    SVT_DRIFT_BELIEF_BAND_RECENT,
    SVT_DRIFT_BELIEF_LONG_STAYER_YEARS,
    SvtSegmentObservation,
    estimate_svt_drift,
)

#: One cap quarter, and a tenure inside each published band. Fixed across every case below so that
#: the CALENDAR is held constant and the only thing moving is the household.
SAME_INSTANT_DAYS = 90.0
RECENT_YEARS = 1.0
LONG_STAYER_YEARS = SVT_DRIFT_BELIEF_LONG_STAYER_YEARS + 1.0

#: Best to worst. The ORDER is the claim; the names are whatever the company's own desk emits.
GRADES_BEST_TO_WORST = ("EXCELLENT", "GOOD", "FAIR", "POOR", "CRITICAL")

#: DERIVED FROM THE ESTIMATOR'S OWN ROUNDING, not picked to make these assertions pass.
#:
#: `estimate_svt_drift` rounds its PER-PERIOD answer to `_ESTIMATE_DP`. The two assertions below
#: read the published ANNUAL band, so they invert the constant-hazard conversion — and that
#: inversion multiplies the rounding error by roughly `365.25 / days`. A 90-day segment therefore
#: carries about four half-ulps of slack, and asserting tighter than that would be asserting that
#: the estimator does not round, which it does and says it does.
_ANNUAL_ROUNDING_SLACK = 0.5 * 10 ** -_ESTIMATE_DP * (365.25 / SAME_INSTANT_DAYS) * 1.5


def _belief(years: float, grade: str | None, days: float = SAME_INSTANT_DAYS) -> float:
    return estimate_svt_drift(
        SvtSegmentObservation(years_on_svt=years, segment_days=days, payment_behaviour=grade)
    )


@pytest.mark.parametrize("years", [RECENT_YEARS, LONG_STAYER_YEARS])
def test_two_households_on_the_same_cap_period_get_different_beliefs(years: float) -> None:
    """THE DEFECT ITSELF: identical calendar, different household, one number.

    Everything about these two observations is equal except the company's own collections record.
    If the belief cannot separate them it cannot select anyone, whatever its AUC says.
    """
    best = _belief(years, GRADES_BEST_TO_WORST[0])
    worst = _belief(years, GRADES_BEST_TO_WORST[-1])
    assert best != worst, (
        "the belief returns the same number for a household with a clean payment record and one "
        "in chronic arrears, on the same cap period — it is a function of the calendar alone, "
        "which is the v1 defect this term was added to fix"
    )


@pytest.mark.parametrize("years", [RECENT_YEARS, LONG_STAYER_YEARS])
def test_a_worse_payment_record_never_raises_the_believed_drift(years: float) -> None:
    """The published DIRECTION, and only the direction — no magnitude is asserted.

    An indebted domestic account is less able to leave: a supplier may object to its transfer
    (Ofgem, `Decision on review of domestic objections`, 2016) and indebted prepayment switches run
    through the Debt Assignment Protocol. `docs/market_research/svt_drift_by_payment_behaviour.md`
    records that the direction is established and the magnitude is not.

    Monotone, not strictly monotone, on purpose: collapsing two adjacent grades would be a
    defensible modelling choice, whereas INVERTING the order would mean the belief had been fitted
    to something other than the published mechanism.
    """
    beliefs = [_belief(years, g) for g in GRADES_BEST_TO_WORST]
    assert beliefs == sorted(beliefs, reverse=True), (
        f"believed drift does not fall as the payment record worsens: {dict(zip(GRADES_BEST_TO_WORST, beliefs))} "
        "— the published mechanism runs the other way"
    )


@pytest.mark.parametrize(
    "years,band",
    [(RECENT_YEARS, SVT_DRIFT_BELIEF_BAND_RECENT), (LONG_STAYER_YEARS, SVT_DRIFT_BELIEF_BAND_LONG_STAYER)],
)
def test_no_payment_record_can_push_the_belief_outside_its_published_band(
    years: float, band: tuple[float, float]
) -> None:
    """The band edges are published; the payment term places WITHIN them and may not escape them.

    This is the control against the repair the pre-registration forbids — moving the company's band
    up to the world's 0.20/0.10 to close the belief-vs-truth gap. A term that could exceed the
    published top edge would be that repair arriving through a side door, one grade at a time.

    Compared as ANNUAL rates by inverting the constant-hazard conversion the estimator applies, so
    this reads the published band directly rather than a per-period shadow of it.
    """
    low, high = band
    for grade in (*GRADES_BEST_TO_WORST, None, "NOT_A_GRADE"):
        period = _belief(years, grade)
        annual = 1.0 - (1.0 - period) ** (365.25 / SAME_INSTANT_DAYS)
        assert low - _ANNUAL_ROUNDING_SLACK <= annual <= high + _ANNUAL_ROUNDING_SLACK, (
            f"payment grade {grade!r} puts the believed annual drift at {annual:.4f}, outside the "
            f"published band {band} it is supposed to be placing an account inside"
        )


@pytest.mark.parametrize(
    "years,midpoint",
    [
        (RECENT_YEARS, SVT_DRIFT_BELIEF_ANNUAL_RECENT),
        (LONG_STAYER_YEARS, SVT_DRIFT_BELIEF_ANNUAL_LONG_STAYER),
    ],
)
@pytest.mark.parametrize("absent", [None, "NOT_A_GRADE", ""])
def test_an_absent_or_unreadable_payment_record_reads_as_the_midpoint(
    years: float, midpoint: float, absent: str | None
) -> None:
    """An absence must be scored as an absence, never as a good record.

    WHAT REACHES THE BELIEF IS `None`, and the belief scores it as the midpoint — the same answer
    v1 gave every account, and the honest reading of "cannot tell". An unrecognised grade string
    takes the same path, so a desk that grows a sixth grade degrades to "cannot tell" rather than
    to a guessed position.

    AND THE NEARBY FAIL-OPEN IS AN EQUIVALENCE, NOT A HOLE — established rather than assumed,
    because assuming the flattering answer is how this class survives. `score_payment_history`
    does return EXCELLENT for an EMPTY record list, which would score a brand-new account at the
    TOP of the band purely for being new. It is unreachable through the desk:
    `PaymentBehaviourAnalytics.record_payment` creates the list and appends in the same call, so a
    present key never has an empty list, and an absent key returns `None` from `get_score` before
    `score_payment_history` is reached. So this test asserts the `None` path, which is the one that
    exists; it does not claim to have closed the other, which cannot currently fire.
    """
    assert _belief(years, absent) == _belief(years, "FAIR"), (
        "an absent payment record is not scored the same as a middling one"
    )
    annual = 1.0 - (1.0 - _belief(years, absent)) ** (365.25 / SAME_INSTANT_DAYS)
    assert annual == pytest.approx(midpoint, abs=_ANNUAL_ROUNDING_SLACK), (
        f"an account with no payment history reads {annual:.4f} rather than the published "
        f"midpoint {midpoint} the belief used before this term existed"
    )


def test_the_payment_term_cannot_reorder_the_two_published_bands() -> None:
    """A long-stayer is the more inert segment WHATEVER their payment record.

    The two bands do not overlap (5-10% against 15-20%) and the published claim is about tenure, so
    the within-band placement must not be able to lift a long-stayer above a recent roller. If it
    could, the belief would be asserting something §4 does not say, and the tenure signal — the one
    part of v1 that was about the account rather than the calendar — would have been spent.
    """
    best_long_stayer = _belief(LONG_STAYER_YEARS, GRADES_BEST_TO_WORST[0])
    worst_recent = _belief(RECENT_YEARS, GRADES_BEST_TO_WORST[-1])
    assert best_long_stayer < worst_recent, (
        f"a spotless long-stayer ({best_long_stayer}) is believed more likely to drift than a "
        f"chronically-arrears recent roller ({worst_recent}) — the payment term has overwhelmed a "
        "published band separation it was only meant to place accounts inside"
    )


def test_a_zero_length_cap_period_still_believes_nothing_can_happen() -> None:
    """Unchanged from v1 and asserted so the new branch cannot have moved it.

    No exposure, no opportunity to leave. The payment term multiplies a rate, so a grade must not
    be able to manufacture drift across a segment that never ran.
    """
    for grade in (*GRADES_BEST_TO_WORST, None):
        assert _belief(RECENT_YEARS, grade, days=0.0) == 0.0
