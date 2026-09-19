"""The bound on `J_svt` must close from ABOVE too, and its conservatism must run the other way.

THE DEFECT THIS EXISTS TO CATCH, AND IT IS TWO DEFECTS. The first is the one the drawn item names:
`svt_internal_conversion_floor` bounds `J_svt` at 0.0449 and the world it judges runs at 0.1859, so
the floor sits at 0.24x of its own subject and cannot refuse any world this project would build. A
one-sided bound that far below the thing it bounds is a control that cannot fail, and
`against_the_floor_for_this_route` said so itself: *"the bound has no ceiling beside it."*

The second is the one that arrives WITH the repair, and it is the reason most of these legs exist.
A ceiling out of the same identity inherits none of the floor's conservatism -- every choice
inverts. The floor divides by the LARGEST published default share to push itself down; a ceiling
must divide by the SMALLEST to push itself up. The floor takes the MINIMUM across waves; a ceiling
must take the MAXIMUM. And the floor's own docstring records that a six-month rate is a valid
ANNUAL floor -- which is exactly why a six-month rate is NOT a valid annual ceiling. Each of those
three, copied across from the floor rather than inverted, produces a bar tighter than the record
supports, and the world breaches the un-annualised ceiling in four years, so a too-tight ceiling
would publish a refutation of the world that the record does not make. The legs below are what
stop the mirror being written as a copy.

WHY THE LEGS ARE KEYED TO THE PROPERTY AND NOT TO TODAY'S ANSWER. The world currently sits at 0.70
of the binding ceiling and above it in 2018, 2021, 2023 and 2025. A leg pinned to "clears" goes red
the moment the world's SVT-side decision is made more aggressive -- which is the one change this
bound exists to catch -- and a leg pinned to "4 years above" goes red on the next capture. What is
asserted instead is which direction each conservative choice runs, that both verdicts are reachable,
that the ceiling never falls below the floor it pairs with, that the assumption-carrying banner
variant never becomes the bar, and that the whole thing fails closed.

REUSE
-----
REUSE: tests/tools/test_the_worlds_internal_route_is_judged_against_a_ceiling_and_not_only_a_floor.py
CLASS: CUSTOM
INDEX: searched "conversion ceiling", "j_svt", "svt internal", "internal return", "binding
       ceiling", "route split", "two sided", "band".
       `tests/tools/test_the_worlds_internal_route_is_judged_against_the_floor_for_that_route.py` is
       the nearest row and is deliberately NOT extended. It holds the join between the FLOOR and a
       captured world; every leg in it asserts a direction of conservatism that this file asserts
       the INVERSE of, and putting both in one file would put two opposite rules under one name --
       the shape that makes a reader take the wrong one. The one thing genuinely shared is the
       per-year fixture, and it is 15 lines of literal.
       `tests/tools/test_the_svt_conversion_floor_is_a_bound_and_not_a_number.py` holds that the
       floor never becomes `SVT_INTERNAL_CONVERSION_RATE`; the equivalent leg for the ceiling is
       here because the ceiling is here, and it is the same rule rather than the same code.
"""
from __future__ import annotations

from pathlib import Path

import pytest

import tools.fit_year_level_anchor as fitter
import tools.published_route_split as split

_REPO_ROOT = Path(__file__).resolve().parents[2]


def _per_year(rate: float | None, *, returns: int = 3, account_years: float = 30.0) -> dict:
    """One per-year row in the shape `svt_internal_return_and_tenure` builds."""
    return {
        "svt_account_years": account_years,
        "accounts_on_book": 50,
        "stint_fates": {
            fitter.STINT_RETURNED: returns,
            fitter.STINT_DEPARTED: 1,
            fitter.STINT_CENSORED: 0,
        },
        "internal_return_rate": {"per_svt_account_year": rate, "of_the_whole_book": None},
        "long_stayer_share_of_svt_account_days": 0.3,
        "blended_annual_rate_at_this_mix": 0.17,
    }


@pytest.fixture(scope="module")
def ceiling() -> float:
    value = split.svt_internal_conversion_ceiling()["binding_ceiling"]
    assert value is not None and value > 0.0, (
        "the record establishes no binding ceiling, so every leg below would be vacuous."
    )
    return value


def test_both_verdicts_are_reachable(ceiling):
    """MUTATION: freeze `clears_the_binding_ceiling` to True (or to False) and this fires.

    CLAUDE.md's rare-branch rule, and it bites harder here than it did for the floor. Today's
    capture clears the ceiling at book level, so a verdict frozen True looks exactly like the
    mechanism working -- and the whole point of adding a ceiling was to be able to say NO to a
    world that moves up. One control over the whole partition, not a leg per branch.
    """
    under = fitter._internal_return_vs_the_published_ceiling(
        {"2019": _per_year(ceiling / 2.0)}, ceiling / 2.0
    )
    over = fitter._internal_return_vs_the_published_ceiling(
        {"2019": _per_year(ceiling * 2.0)}, ceiling * 2.0
    )
    assert under["clears_the_binding_ceiling"] is True
    assert over["clears_the_binding_ceiling"] is False
    assert under["per_year"]["2019"]["clears_the_binding_ceiling"] is True
    assert over["per_year"]["2019"]["clears_the_binding_ceiling"] is False
    assert under["years_above_the_ceiling"] == [] and under["years_within_the_ceiling"] == ["2019"]
    assert over["years_above_the_ceiling"] == ["2019"] and over["years_within_the_ceiling"] == []


def test_the_verdict_at_the_exact_ceiling_is_clearing_and_the_boundary_is_not_strict(ceiling):
    """MUTATION: write `rate < ceiling` instead of `rate <= ceiling` and this fires.

    A BOUND IS INCLUSIVE, the same rule the floor's boundary leg states from the other side.
    `svt_internal_conversion_ceiling` publishes the MOST conversion the record can bear, so a world
    sitting exactly on it has not exceeded it.
    """
    exact = fitter._internal_return_vs_the_published_ceiling({"2019": _per_year(ceiling)}, ceiling)
    assert exact["clears_the_binding_ceiling"] is True
    assert exact["per_year"]["2019"]["clears_the_binding_ceiling"] is True


def test_the_ceiling_divides_by_the_smallest_default_share_and_not_the_largest():
    """MUTATION: take `band[1]` (the floor's `s_max`) instead of `band[0]` and this fires.

    THE INVERSION THAT MATTERS MOST, because it is the one a reader of the floor would get wrong by
    copying. `J_svt <= I / s`: a SMALLER `s` concentrates the same published internal switching into
    fewer SVT households and RAISES the per-household ceiling. For an upper bound the safe choice is
    the one that raises it, which is the opposite of the floor's.

    Asserted as the defining property rather than by recomputing the expression -- a leg that
    recomputes `rate / min(...)` agrees with any mutation applied to both copies. What is asserted
    is that no published endpoint in the window could have produced a HIGHER ceiling, which is what
    "most generous" means and which `s_max` fails at wave 6, where the window spans a default share
    of 0.64-0.70 in 2025 and 0.80-0.86 in 2024.
    """
    reading = split.svt_internal_conversion_ceiling()
    by_wave = {row["wave"]: row for row in reading["per_wave"]}
    windows_with_a_choice = 0
    for obs in split.SWITCHER_SPLIT_OBSERVATIONS:
        row = by_wave[obs.wave]
        if row["ceiling_on_j_svt"] is None:
            continue
        endpoints = [
            end
            for year in obs.recall_window_years
            if (band := split.default_tariff_share(year, "all_domestic")) is not None
            for end in band
        ]
        assert endpoints
        if len(set(endpoints)) > 1:
            windows_with_a_choice += 1
        for end in endpoints:
            # 1e-6 and not 0: both sides round to 6dp and this one divides an ALREADY-rounded rate,
            # so the two disagree in the last place at wave 3. The mutation this leg exists for --
            # dividing by `s_max` -- moves the ceiling by 0.02 at every wave, four orders of
            # magnitude above the tolerance, so widening it here costs the leg nothing.
            assert row["ceiling_on_j_svt"] >= round(
                row["internal_rate_of_all_households_6mo"] / end, 6
            ) - 1e-6, (
                f"wave {obs.wave}: a published default share of {end} in the recall window would "
                f"admit a HIGHER ceiling than the {row['ceiling_on_j_svt']} published, so the "
                f"ceiling is not the most generous one the record allows."
            )
    assert windows_with_a_choice, (
        "every recall window resolved to a single default share, so this leg could not have "
        "distinguished the smallest endpoint from the largest and is vacuous."
    )


def test_the_binding_ceiling_is_the_loosest_wave_and_not_the_tightest():
    """MUTATION: take `min(ceilings)` -- the floor's aggregation -- and this fires.

    EACH WAVE BOUNDS `J_svt` AT ITS OWN TIME AND `J_svt` MOVES. The floor takes the minimum because
    that is the rate every wave independently establishes. The mirror is the maximum: the ceiling
    every wave independently permits. Taking the minimum would assert a bound no single wave makes
    and would put the binding bar at 0.1380 -- BELOW the world's own 0.1859 -- turning a world the
    record admits into a published breach.
    """
    reading = split.svt_internal_conversion_ceiling()
    per_wave = [
        row["ceiling_on_j_svt"] for row in reading["per_wave"]
        if row["ceiling_on_j_svt"] is not None
    ]
    assert len(per_wave) > 1 and len(set(per_wave)) > 1, (
        "the waves agree on one ceiling, so min and max coincide and this leg is vacuous."
    )
    assert reading["binding_ceiling"] == max(per_wave)
    for value in per_wave:
        assert reading["binding_ceiling"] >= value


def test_the_ceiling_is_never_below_the_floor_it_pairs_with():
    """MUTATION: drop the `(1-s)*0.35` term from the FLOOR, or invert either bound, and this fires.

    THE ONE PROPERTY THAT TIES THE TWO BOUNDS TOGETHER, and the only leg here that would survive a
    rewrite of both. `J_svt >= (I - c)/s_max` and `J_svt <= I/s_min` describe the same quantity, so
    the band must be non-empty: at every wave the ceiling must be at least the floor, and the same
    must hold for the binding pair. A band whose ceiling sits under its floor is a derivation error
    that no verdict leg would notice, because both verdicts would still be computable.
    """
    floors = {
        row["wave"]: row["floor_on_j_svt"]
        for row in split.svt_internal_conversion_floor()["per_wave"]
    }
    ceilings = {
        row["wave"]: row["ceiling_on_j_svt"]
        for row in split.svt_internal_conversion_ceiling()["per_wave"]
    }
    compared = 0
    for wave, low in floors.items():
        high = ceilings.get(wave)
        if low is None or high is None:
            continue
        compared += 1
        assert high >= low, f"wave {wave}: ceiling {high} is below floor {low} -- an empty band."
    assert compared, "no wave carries both bounds, so the band was never checked."
    assert (
        split.svt_internal_conversion_ceiling()["binding_ceiling"]
        >= split.svt_internal_conversion_floor()["binding_floor"]
    )


def test_the_tariff_banner_ceiling_never_becomes_the_binding_bar():
    """MUTATION: set `binding_ceiling` to the banner figure and this fires.

    THE BAR MUST BE THE ONE THAT COSTS NO ASSUMPTION. The tariff-type banner is tighter -- 0.2389
    against 0.2659 -- and it is tighter by exactly the internal switchers who report a VARIABLE
    tariff, which is safe only if none of those is a conversion whose mover mis-reported. That is a
    real assumption about self-report, and `whether_the_survey_split_identifies_phi` refuses this
    same banner outright for `phi`. Carrying the tighter number is worth doing; making it the bar
    would put an assumption underneath a refusal without the refusal saying so.
    """
    reading = split.svt_internal_conversion_ceiling()
    banner = reading["binding_ceiling_from_the_tariff_banner"]
    assert banner is not None and banner < reading["binding_ceiling"], (
        "the banner ceiling is not tighter than the assumption-free one, so either the cut is not "
        "being applied or the two have been swapped."
    )
    assert reading["what_the_banner_ceiling_assumes"]
    for row in reading["per_wave"]:
        if row["ceiling_on_j_svt_from_the_tariff_banner"] is None:
            continue
        assert row["ceiling_on_j_svt_from_the_tariff_banner"] <= row["ceiling_on_j_svt"], (
            f"wave {row['wave']}: dropping the variable column RAISED the ceiling, which cannot "
            "happen if the numerator is a subset."
        )


def test_the_banner_columns_must_be_shown_to_partition_the_internal_switchers():
    """MUTATION: hardcode `the_banner_partitions_the_internal_switchers` to True and this fires.

    DROPPING A COLUMN IS ONLY SAFE IF THE PAIR IS EXHAUSTIVE. The banner ceiling keeps the fixed
    column and discards the variable one; if some internal switchers sat in neither -- a third
    tariff-type group, or respondents who gave none -- the kept column would miss conversions and
    the "ceiling" would be a number the record does not bound anything by. The two columns do
    partition the switchers in all six waves, and that is a fact about the table which must be
    CHECKED rather than asserted -- the BASES are a different question with a different answer
    (whole base in W1-W5, 0.46% short at W6), so "the banner covers everyone" is not available as
    a reason and the switcher property has to carry it alone.
    """
    observed = [
        obs for obs in split.SWITCHER_SPLIT_OBSERVATIONS
        if obs.internal_weighted_reporting_fixed is not None
    ]
    assert len(observed) == len(split.SWITCHER_SPLIT_OBSERVATIONS)
    for obs in observed:
        assert obs.the_banner_partitions_the_internal_switchers is True
        pair = obs.internal_weighted_reporting_fixed + obs.internal_weighted_reporting_variable
        assert abs(pair - obs.internal_weighted) <= 0.001

    broken = split.SwitcherSplitObservation(
        wave=99, fieldwork="never", recall_window_years=(2023,),
        base_unweighted=1000, base_weighted=1000.0,
        external_weighted=50.0, internal_weighted=100.0, net_switched_weighted=150.0,
        internal_weighted_reporting_fixed=60.0, internal_weighted_reporting_variable=20.0,
    )
    assert broken.the_banner_partitions_the_internal_switchers is False, (
        "a wave whose two columns account for 80 of 100 internal switchers is reported as "
        "partitioned, so the check cannot detect the case it exists for."
    )


def test_a_record_with_no_ceiling_is_refused_and_never_passed(monkeypatch, ceiling):
    """MUTATION: return `clears_the_binding_ceiling = True` when the ceiling is None and this fires.

    FAIL CLOSED, AND SAY SO ON THE SURFACE. A `None` ceiling with a `True` verdict reads as a world
    sitting under a bar nobody set -- and the flattering branch is the tempting repair, because a
    comparison against `None` raises.
    """
    monkeypatch.setattr(
        split, "svt_internal_conversion_ceiling",
        lambda: {
            "binding_ceiling": None,
            "binding_ceiling_unit": "n/a",
            "source": "test",
            "waves_with_a_ceiling": 0,
            "binding_ceiling_from_the_tariff_banner": None,
            "what_the_banner_ceiling_assumes": "n/a",
            "the_verdict_that_is_safe": "n/a",
            "the_point_estimate_is": None,
        },
    )
    reading = fitter._internal_return_vs_the_published_ceiling(
        {"2019": _per_year(ceiling / 5.0)}, ceiling / 5.0
    )
    assert reading["refused"], (
        "no ceiling and no refusal: the reading is silent where it cannot tell."
    )
    assert reading["clears_the_binding_ceiling"] is None
    assert reading["per_year"]["2019"]["clears_the_binding_ceiling"] is None
    assert reading["years_scored"] == [] and reading["years_above_the_ceiling"] == []
    assert reading["the_verdict_is_not_uniform"] is False
    assert reading["the_band_is_now_two_sided"]["world_is_inside_the_band"] is None


def test_a_year_with_no_measurable_rate_is_scored_as_neither(ceiling):
    """MUTATION: treat a `None` per-year rate as 0.0 and this fires by calling it inside the band.

    AND THE FLATTERING BRANCH IS THE OPPOSITE ONE TO THE FLOOR'S, which is why this is not the same
    leg twice. Read as zero, a year with no SVT exposure is BELOW the floor -- a visible red -- and
    UNDER the ceiling, which is a silent pass. The same silent `None` is therefore a complaint on
    one bound and a clean bill on the other.
    """
    reading = fitter._internal_return_vs_the_published_ceiling(
        {"2019": _per_year(None, returns=0, account_years=0.0), "2020": _per_year(ceiling / 2.0)},
        ceiling / 2.0,
    )
    assert reading["per_year"]["2019"]["clears_the_binding_ceiling"] is None
    assert reading["years_scored"] == ["2020"]
    assert "2019" not in reading["years_above_the_ceiling"]
    assert "2019" not in reading["years_within_the_ceiling"]


def test_the_uniformity_flag_is_derived_and_not_declared(ceiling):
    """MUTATION: hardcode `the_verdict_is_not_uniform` and this fires on one of the two shapes.

    A SPREAD IS THE READING. Frozen True, it claims a disagreement across years that a uniform
    capture does not contain; frozen False, it hides the one this capture does.
    """
    mixed = fitter._internal_return_vs_the_published_ceiling(
        {"2019": _per_year(ceiling / 2.0), "2020": _per_year(ceiling * 2.0)}, ceiling
    )
    uniform = fitter._internal_return_vs_the_published_ceiling(
        {"2019": _per_year(ceiling / 2.0), "2020": _per_year(ceiling / 3.0)}, ceiling / 2.0
    )
    assert mixed["the_verdict_is_not_uniform"] is True
    assert uniform["the_verdict_is_not_uniform"] is False


def test_the_reading_names_which_direction_its_bar_flatters_and_it_is_the_floors_inverted(ceiling):
    """MUTATION: delete the direction statement, or copy the floor's, and this fires.

    THE SENTENCE IS LOAD-BEARING AND IT IS NOT THE FLOOR'S. Both bars are six-month rates read
    against an annual world figure. For the floor that is flattering and a year BELOW is the
    established verdict. For the ceiling the identical fact makes the bar HARSHER than the record
    supports, so a year ABOVE establishes nothing and CLEARS is the established verdict. A reader
    holding both at once will reach for the four above-ceiling years as a refutation; the reading
    has to say, in its own output, that they are not one.
    """
    reading = fitter._internal_return_vs_the_published_ceiling(
        {"2019": _per_year(ceiling / 2.0)}, ceiling / 2.0
    )
    statement = reading["the_bar_is_weak_in_this_direction"]
    assert statement and "BELOW" in statement
    assert "annual" in statement and "six-month" in statement
    floor_statement = fitter._internal_return_vs_the_published_floor(
        {"2019": _per_year(ceiling / 2.0)}, ceiling / 2.0
    )["the_bar_is_weak_in_this_direction"]
    assert statement != floor_statement, (
        "the ceiling publishes the floor's direction-of-flattering verbatim, so one of the two "
        "bounds is telling the reader the wrong way round."
    )
    assert reading["what_this_cannot_say"]


def test_the_ceiling_is_a_bound_and_never_becomes_the_point_estimate(ceiling):
    """MUTATION: set `SVT_INTERNAL_CONVERSION_RATE` to the binding ceiling and this fires.

    THE RULE THE FLOOR WAS ALREADY HELD TO, restated because a SECOND bound is the moment it gets
    broken: with a floor and a ceiling in hand, a midpoint looks like an estimate. It is not one --
    nothing establishes that `J_svt` sits anywhere particular in the band, and a number written into
    the slot named for a point estimate is read as one within a week.
    """
    assert split.SVT_INTERNAL_CONVERSION_RATE is None
    assert split.SVT_INTERNAL_CONVERSION_RATE_GAP
    reading = split.svt_internal_conversion_ceiling()
    assert reading["the_point_estimate_is"] is None
    assert reading["why_there_is_no_point_estimate"] == split.SVT_INTERNAL_CONVERSION_RATE_GAP
    joined = fitter._internal_return_vs_the_published_ceiling(
        {"2019": _per_year(ceiling / 2.0)}, ceiling / 2.0
    )
    assert joined["the_point_estimate_is_still"] is None


def test_the_band_membership_verdict_is_reachable_in_all_three_directions(ceiling):
    """MUTATION: freeze `world_is_inside_the_band` and this fires on one of the three shapes.

    THE BAND IS THE WHOLE GAIN AND ITS VERDICT HAS THREE OUTCOMES, not two. A world can be below
    the floor, inside, or above the ceiling, and a two-valued flag would collapse one end into the
    middle. This is the leg that makes the band's own claim -- that it can now refuse -- checkable.
    """
    floor = split.svt_internal_conversion_floor()["binding_floor"]
    below = fitter._internal_return_vs_the_published_ceiling(
        {"2019": _per_year(floor / 2.0)}, floor / 2.0
    )
    inside = fitter._internal_return_vs_the_published_ceiling(
        {"2019": _per_year((floor + ceiling) / 2.0)}, (floor + ceiling) / 2.0
    )
    above = fitter._internal_return_vs_the_published_ceiling(
        {"2019": _per_year(ceiling * 2.0)}, ceiling * 2.0
    )
    assert below["the_band_is_now_two_sided"]["world_is_inside_the_band"] is False
    assert inside["the_band_is_now_two_sided"]["world_is_inside_the_band"] is True
    assert above["the_band_is_now_two_sided"]["world_is_inside_the_band"] is False
    assert below["clears_the_binding_ceiling"] is True, (
        "a world under the FLOOR is also under the ceiling; if the band flag and the ceiling "
        "verdict disagree here, one of them is reading the wrong bound."
    )
    assert above["clears_the_binding_ceiling"] is False
