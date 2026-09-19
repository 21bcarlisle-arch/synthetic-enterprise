"""Annualising the CIM internal row may loosen the ceiling and tighten the floor, never the reverse.

THE DEFECT THIS EXISTS TO CATCH. A drawn item asked for a published repeat-switching figure in
order to *"turn this bound from live into firing"* -- the bound being
`svt_internal_conversion_ceiling`, which the world sits at 0.70 of. The arithmetic says that cannot
happen: the annualisation factor `a = P12/p` is in [1, 2] for every population by
inclusion-exclusion, so an annual ceiling is at least the six-month bar and never less, and the
four above-ceiling years get FURTHER from a breach when the bar is annualised. The defect is the
obvious repair -- adopting some factor below 1, or reading a repeat-switching figure as licensing a
tighter ceiling -- which would publish a refutation of the world the record does not make. That is
the same class as the three choices `svt_internal_conversion_ceiling` had to invert from the floor,
arriving a fourth time through a new door.

THE SECOND DEFECT, AND IT IS THE ONE A READER IS MOST LIKELY TO COMMIT. The two sides do not move
together. A repeat figure bounds the both-halves overlap `q` from ABOVE, which floors the annual
incidence and therefore RAISES the floor -- up to 0.1676 from 0.0449. So the evidence the item
asked for is real evidence, applied to the other bound. A repair that moved both bounds in the same
direction, or that wrote one direction sentence and reused it for both, would look exactly like the
mechanism working.

THE THIRD, from this project's own catalogue: a fourth refusal of a fact three functions have
already declined to assume is where the refusal gets quietly reversed. `REPEAT_INTERNAL_SWITCH_
SHARE_WITHIN_A_YEAR` is that fact, and one leg below exists only to red if it ever stops being None.

WHY THE LEGS ARE KEYED TO PROPERTIES AND NOT TO TODAY'S ANSWER. The world is at 1.11x the tightest
annual floor. A leg pinned to "clears" reds the moment the SVT-side decision is made less
aggressive, which is the change this band exists to catch; a leg pinned to "FLOOR is the live side"
reds when the world moves, which is not a defect either. What is asserted instead is: that the
`r = 1` corner of the annualised family IS the landed floor (the join between the new reading and
the bound already in force), that no factor in the band puts the annual ceiling below the bar in
force, that the floor family is monotone and spans a NON-EMPTY range, that both live-side verdicts
are reachable, that the located-but-unusable series is not filed as "nothing published", and that
the whole thing fails closed.

REUSE
-----
REUSE: tests/tools/test_annualising_the_internal_row_moves_the_floor_and_never_the_ceiling.py
CLASS: CUSTOM
INDEX: searched "annualis", "repeat switch", "six month", "j_svt", "internal conversion", "band",
       "ceiling", "floor", "twelve month".
       `tests/tools/test_the_worlds_internal_route_is_judged_against_a_ceiling_and_not_only_a_
       floor.py` is the nearest row and is deliberately NOT extended: every leg in it asserts a
       property of the SIX-MONTH bar, and the subject here is what changes when that convention is
       removed. Its closing claim -- that the ceiling is the side that can refuse -- is what one
       leg here is the counter-example to, and a counter-example filed inside the file it refutes
       is a file that argues with itself under one name.
       `tests/tools/test_the_svt_conversion_floor_is_a_bound_and_not_a_number.py` holds that a
       bound never becomes the point estimate; the same rule applies to every corner of the family
       below and is asserted here because the family is here.
"""
from __future__ import annotations

import pytest

import tools.fit_year_level_anchor as fitter
import tools.published_route_split as split


@pytest.fixture(scope="module")
def reading() -> dict:
    return split.svt_internal_conversion_annualisation()


def test_the_total_repetition_corner_is_the_landed_floor_itself(reading: dict) -> None:
    """The `r = 1` corner must BE `svt_internal_conversion_floor`, not merely resemble it.

    This is the join between the new family and the bound already in force, and it is the leg that
    fails if either side is edited alone. It also establishes the claim the reading makes in
    words -- that the floor in force is not "un-annualised" but annualised at total repetition --
    rather than leaving it as prose nothing checks.
    """
    landed = split.svt_internal_conversion_floor()["binding_floor"]
    assert reading["the_floor_in_force_is_the_total_repetition_corner"] == landed
    assert reading["the_r_1_corner_reproduces_the_landed_floor"] is True
    corner = next(row for row in reading["floor_by_repeat_share"] if row["repeat_share"] == 1.0)
    assert corner["binding_floor"] == landed


def test_no_factor_in_the_band_puts_the_annual_ceiling_below_the_bar_in_force(
    reading: dict,
) -> None:
    """The ceiling can only loosen. This is the leg the drawn item's premise fails.

    Swept across the factor band rather than asserted at its endpoints, because an endpoint-only
    check passes if the band is silently inverted.
    """
    six_month = reading["six_month_ceiling"]
    lo, hi = reading["annualisation_factor_band"]
    assert lo == 1.0, "a factor below 1 would license a ceiling tighter than the record supports"
    assert hi > lo, "an empty or inverted factor band makes every verdict below vacuous"
    for step in range(21):
        factor = lo + (hi - lo) * step / 20
        assert factor * six_month >= six_month
    assert reading["the_six_month_bar_is_already_the_tightest_annual_ceiling"] is True


def test_the_floor_family_is_monotone_and_spans_a_range_that_is_not_empty(
    reading: dict,
) -> None:
    """Falling repetition must raise the floor, and the span must be real.

    The non-emptiness leg is not decoration. A family whose corners coincide would satisfy every
    monotonicity assertion trivially and would report a "span" that no evidence could ever move --
    the shape where a bound's two ends collapse and no verdict can see it.
    """
    floors = [row["binding_floor"] for row in reading["floor_by_repeat_share"]]
    assert all(a >= b for a, b in zip(floors, floors[1:])), "less repetition must not lower a floor"
    assert reading["the_family_is_monotone_in_the_repeat_share"] is True
    assert reading["the_floor_if_nobody_repeats"] > reading[
        "the_floor_in_force_is_the_total_repetition_corner"
    ], "a family whose ends coincide cannot be tightened by any evidence and is not a family"


def test_the_two_directions_are_not_one_sentence_reused(reading: dict) -> None:
    """The ceiling's direction and the floor's are opposite claims and must read as two.

    Building the mirror of an existing bound is where a conservative choice gets copied instead of
    inverted, and the cheapest symptom is one sentence doing both jobs.
    """
    ceiling_says = reading["no_published_fact_can_tighten_the_ceiling"]
    floor_says = reading["which_side_of_the_band_annualising_moves"]
    assert ceiling_says != floor_says
    assert "ABOVE" in ceiling_says and "BELOW" in ceiling_says, (
        "the ceiling's refusal turns on which side of q a repeat figure bounds; a version that "
        "does not name both sides has lost the argument it is recording"
    )
    # Inequality alone is too weak and a mutation proved it: blanking the floor sentence left the
    # two unequal and this leg green. Each must NAME the bound it is about, which is the content
    # the reader needs and the thing a copied or emptied sentence loses.
    assert "FLOOR" in floor_says, (
        "the floor's direction sentence must say that the floor is what a repeat figure moves; "
        "without it a reader has only the ceiling's refusal and concludes the fact is worthless"
    )
    assert "ceiling" in ceiling_says.lower() and "FLOOR" not in ceiling_says


def test_both_live_side_verdicts_are_reachable(reading: dict) -> None:
    """A world can be put on either side, so the verdict is not frozen by construction.

    The partition control. Every other leg asks whether the reading refuses correctly, and a
    reading that answered "FLOOR" for every world would pass all of them.
    """
    del reading
    near_the_floor = fitter._internal_return_vs_the_annualised_band(0.05)
    near_the_ceiling = fitter._internal_return_vs_the_annualised_band(0.50)
    assert near_the_floor["the_live_side_of_the_band"] == "FLOOR"
    assert near_the_ceiling["the_live_side_of_the_band"] == "CEILING"
    below_every_floor = fitter._internal_return_vs_the_annualised_band(0.001)
    assert below_every_floor["the_world_clears_the_tightest_floor"] is False, (
        "the floor must be failable by some world, or it is a bound that cannot refuse -- which is "
        "the defect the ceiling was built to repair, arriving on the other side"
    )


def test_the_annual_reading_fails_closed_on_a_missing_world(reading: dict) -> None:
    """No world rate is a refusal with a reason, never a pass."""
    del reading
    refused = fitter._internal_return_vs_the_annualised_band(None)
    assert refused["refused"] is not None
    assert refused["the_world_clears_the_tightest_floor"] is None
    assert refused["the_live_side_of_the_band"] is None
    assert refused["share_of_the_tightest_annual_ceiling"] is None


def test_the_repeat_share_is_still_refused_and_the_refusal_names_its_reason(
    reading: dict,
) -> None:
    """The fourth refusal of the same fact, and the leg that reds if it is quietly reversed.

    Three functions declined to assume this figure before this one did. A number appearing here
    later -- read off a survey with the wrong event or the wrong window, which is exactly what the
    located instruments offer -- is the failure this file was written to make loud.
    """
    assert split.REPEAT_INTERNAL_SWITCH_SHARE_WITHIN_A_YEAR is None
    assert reading["the_repeat_share_is"] is None
    gap = reading["why_there_is_no_repeat_share"]
    assert "SUPPLIER" in gap and "lifetime" in gap, (
        "the refusal must name WHY the frequency question that does exist is the wrong one -- "
        "wrong event and wrong window -- or the next session reads it as 'not looked for'"
    )


def test_a_located_but_unusable_series_is_not_filed_as_nothing_published(
    reading: dict, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The twelve-month series is held, and the reason it is unused is DERIVED, not asserted.

    "We looked and found nothing" would send the next session back to the same fetch. The overlap
    flag is the checkable half of the reason, so it is mutated here: a series that did share a year
    with a CIM wave must say so, and the prose must stop being the last word.
    """
    assert reading["a_twelve_month_reading_of_the_same_event_exists"], (
        "a located source that did not answer the question still belongs on the shelf"
    )
    assert reading["any_year_overlaps_a_cim_wave"] is False
    overlapping = split.TWELVE_MONTH_INTERNAL_SWITCHING_OBSERVATIONS + (
        split.TwelveMonthInternalSwitchingObservation(2022, 0.15, "fabricated, for this leg only"),
    )
    monkeypatch.setattr(split, "TWELVE_MONTH_INTERNAL_SWITCHING_OBSERVATIONS", overlapping)
    assert split.svt_internal_conversion_annualisation()["any_year_overlaps_a_cim_wave"] is True


def test_no_corner_of_the_family_becomes_the_point_estimate(reading: dict) -> None:
    """A bound with an assumption attached is still a bound. `J_svt` stays `None`."""
    assert split.SVT_INTERNAL_CONVERSION_RATE is None
    assert reading["the_point_estimate_is"] is None
    corners = [row["binding_floor"] for row in reading["floor_by_repeat_share"]]
    corners += list(reading["annual_ceiling_at_each_endpoint"].values())
    assert split.SVT_INTERNAL_CONVERSION_RATE not in corners
