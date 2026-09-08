"""The gas base load, each test named by the defect it catches.

The first version of this module refused to scale hot water with occupancy, quoting the source
study's caveat that the relationship needed confirming. The director corrected the reasoning rather
than the number: *"Omission is not neutrality -- it asserts zero, and zero is usually the one value
we know is wrong."* A per-household constant is the belief that four people take the same number of
showers as one, which is the single answer that is certainly false.
"""
from __future__ import annotations

import math
import random
import statistics

import pytest

from tools import hot_water_base as hw


def test_OMISSION_IS_NOT_NEUTRALITY_and_zero_is_a_value_of_the_parameter():
    """THE DIRECTOR'S RULE, HELD AS A CONTROL. A flat per-household base is not the absence of an
    assumption about occupancy; it is the assumption that occupancy does nothing. It appears in the
    sweep as `0.0` -- one value of the parameter among others -- so choosing it is visible and
    arguable rather than implicit."""
    values = [row["litres_per_person_per_day"] for row in hw.sweep()]
    assert 0.0 in values, (
        "the flat base must appear as a value of the parameter, or omitting the relationship looks "
        "like neutrality rather than the choice of zero that it is")
    flat = next(r for r in hw.sweep() if r["litres_per_person_per_day"] == 0.0)
    assert flat["four_vs_two_person_ratio"] == 1.0, (
        "at zero litres per person a four-person home uses exactly as much hot water as a "
        "two-person one -- which is what the old module asserted")


def test_THE_SCALING_IS_SUB_LINEAR_because_some_draw_off_is_fixed():
    """SAP's `36 + 25N` is a fixed part plus a per-person part, and the structure carries a claim:
    some hot water is drawn whatever the headcount. So four people use about 1.6x the hot water of
    two, not 2x. A proportional model would be a different and worse belief."""
    ratio = hw.occupancy_factor(4) / hw.occupancy_factor(2)
    assert 1.3 < ratio < 1.8, f"four-vs-two ratio {ratio:.3f} is outside the fixed-plus-linear range"
    assert ratio < 2.0, "the relationship has become proportional; the fixed draw-off has been lost"
    assert hw.occupancy_factor(4) > hw.occupancy_factor(2) > hw.occupancy_factor(1), (
        "hot water must rise with headcount")


def test_SAP_AND_THE_MEASUREMENT_CORROBORATE_from_opposite_directions():
    """SAP is NORMATIVE -- what a compliance model assumes. DESNZ is 45,000 METERED homes. At the
    reference occupancy SAP predicts 96 litres a day and DESNZ measures a median of 90. Two sources
    of different kinds agreeing is what makes this an anchor rather than a coincidence, and if they
    ever diverge the anchor is gone and this should say so."""
    predicted = (hw.HOT_WATER_FIXED_LITRES_PER_DAY
                 + hw.HOT_WATER_LITRES_PER_PERSON_PER_DAY * hw.REFERENCE_OCCUPANCY)
    measured = 90.0
    assert abs(predicted - measured) / measured < 0.10, (
        f"SAP predicts {predicted:.0f} L/day and the measurement is {measured:.0f} -- more than "
        "10% apart, so they no longer corroborate")


def test_THE_OCCUPANCY_SPREAD_IS_NOT_DOUBLE_COUNTED():
    """THE TRAP IN THE GRADING. The published quartiles are a MARGINAL across all households and
    already contain the spread occupancy causes. Multiplying a draw from that marginal by an
    occupancy factor counts the same variation twice, so the residual must be narrowed by exactly
    what occupancy explains and the total must land back on the measurement."""
    verdict = hw.grade()
    assert 0.0 < verdict["share_of_spread_explained_by_occupancy"] < 1.0
    assert verdict["consistent_with_measurement"] is True

    rng, pick = random.Random(3), random.Random(9)
    sizes = [n for n, share in hw.HOUSEHOLD_SIZE_SHARE for _ in range(int(share * 1000))]
    drawn = sorted(hw.draw_daily_kwh(rng, 1, people_count=pick.choice(sizes))
                   for _ in range(8000))
    p25, p75 = drawn[len(drawn) // 4], drawn[3 * len(drawn) // 4]
    # The measured January-ish band, interpolated between the two published seasons.
    assert 1.7 <= p25 <= 2.6, f"lower quartile {p25:.2f} is outside the measured 1.9-2.1 band"
    assert 6.0 <= p75 <= 8.6, f"upper quartile {p75:.2f} is outside the measured 6.6-8.0 band"
    assert 3.4 <= statistics.median(drawn) <= 4.8, "the median has left the measured band"


def test_THE_MEASUREMENT_CANNOT_REFUTE_ANY_COEFFICIENT_and_that_is_the_finding():
    """A CONTROL I WROTE AS A FALSIFIER AND HAD TO DEMOTE, because it could not fail.

    It asserted that an absurd per-person coefficient would be refused. It is not, and the reason is
    structural rather than a bug: `occupancy_factor` is a RATIO, so as litres-per-person grows it
    converges on `N / 2.4` and its variance converges with it. Headcount in the English stock varies
    too little for even PERFECT PROPORTIONALITY to account for the measured spread.

    So the honest statement is the ceiling: occupancy can explain at most about a third of the
    variation in daily hot-water energy, whatever coefficient is chosen, and **this measurement can
    therefore refute no value of the parameter.** 25 L/person is anchored by SAP, not by anything
    here. What would refute it is a study measuring hot water AGAINST KNOWN OCCUPANCY, which is the
    named gap -- DESNZ measured at the meter without knowing who lived there."""
    ceiling = hw.grade(litres_per_person=1e9)["share_of_spread_explained_by_occupancy"]
    assert 0.2 < ceiling < 0.45, (
        f"the proportional ceiling is {ceiling:.3f}; if it has moved far from a third, either the "
        "household-size mix or the measured spread has changed and the claim needs re-deriving")
    assert hw.grade(litres_per_person=1e9)["consistent_with_measurement"] is True, (
        "an arbitrarily large coefficient is now refused -- that is a STRONGER world than the one "
        "this control describes; replace it with the falsifier it was originally written as")
    assert math.isclose(hw.grade(0.0)["share_of_spread_explained_by_occupancy"], 0.0, abs_tol=1e-9)


def test_THE_GRADING_IS_HONEST_ABOUT_ITS_OWN_WEAKNESS():
    """AND IT DOES NOT VALIDATE THE CHOSEN VALUE, which must be said rather than implied. Every
    plausible coefficient fits inside the measured spread, so the measurement cannot discriminate
    between them -- 25 L/person is anchored by SAP, not by this grading. If the sweep ever started
    refusing plausible values that would be a stronger result and this control should change."""
    plausible = [hw.grade(v) for v in (10.0, 25.0, 40.0, 60.0)]
    assert all(r["consistent_with_measurement"] for r in plausible), (
        "the measurement now discriminates between plausible coefficients -- that is a better "
        "world than the one this control was written in; tighten the claim rather than delete it")
    assert max(r["share_of_spread_explained_by_occupancy"] for r in plausible) < 0.5, (
        "occupancy explains most of the hot-water spread, which would contradict the finding that "
        "same-size households differ mostly by behaviour")
