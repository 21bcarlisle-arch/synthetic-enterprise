"""Controls for the physical/commercial layer cut (W2_31).

Each test names the defect it exists to catch. The defects are all live shapes
this project has paid for before, not hypotheticals:

  * the MERGE -- a physical attribute quietly reading a commercial one, so a
    household that was away and a household that could not afford it produce the
    same record with nothing to tell them apart;
  * the SILENT RE-MERGE -- a new attribute landing on `Household` with no layer,
    which is how the boundary would rot without anything going red;
  * the PICKED COEFFICIENT -- a correlation strength invented to fill a slot,
    which reads as established within a week;
  * the WRONG MARGINAL -- headcount drawn from bedrooms rather than from the
    census, which is the state this atom found and fixed.
"""

from __future__ import annotations

import dataclasses
import datetime as dt

import pytest

from simulation.household import IncomeStress
from simulation.household_physical_layer import (
    LAYER_CORRELATIONS,
    LAYER_OF,
    ComfortAttribution,
    Layer,
    LayerCorrelation,
    attribute_lost_comfort,
    occupancy_band_for,
    people_count_for,
    physical_layer_for,
    unclassified_household_fields,
)
from simulation.household_segments import OCCUPANCY_POPULATION_SHARE
from simulation.population_draw import draw_population
from simulation.premise_trace import ComfortConstraint, behaviour_profile_for

# ONS Census 2021 TS017, England -- the same anchor `household_segments` cites for
# OCCUPANCY_POPULATION_SHARE, restated here as the target the draw must hit.
_CENSUS_MEAN_PEOPLE = 2.37


@pytest.fixture(scope="module")
def drawn_households():
    """Real premises off the live draw, not a hand-built fixture.

    A fixture invented here would be fitted to whatever this module already does;
    the population is what the world actually generates.
    """
    pop = draw_population(11, acquisitions_per_year_lambda=400.0)
    residential = [
        (c.premise.premise_id, c.premise.household)
        for c in pop
        if c.premise.household.is_residential
    ]
    assert len(residential) > 800, (
        f"the draw returned only {len(residential)} residential premises -- too few "
        "for a distributional control to say anything"
    )
    return residential


def test_the_physical_layer_does_not_move_when_only_the_commercial_layer_moves(
    drawn_households,
):
    """DEFECT: the merge. `income_stress` sits on the `Household` record beside the
    fabric, so any physical draw can read it without anything noticing. If it ever
    does, the layers are one again and the director's sentence is back."""
    moved = []
    for premise_id, household in drawn_households[:200]:
        base = physical_layer_for(premise_id, household)
        for stress in IncomeStress:
            if stress == household.income_stress:
                continue
            other = dataclasses.replace(household, income_stress=stress)
            if physical_layer_for(premise_id, other) != base:
                moved.append((premise_id, stress))
    assert not moved, (
        "the physical layer moved when only income_stress changed -- it is reading "
        f"the commercial layer: {moved[:5]}"
    )


def test_the_commercial_attribute_is_absent_from_the_assembled_physical_record(
    drawn_households,
):
    """DEFECT: the merge again, by the other door. Invariance above is satisfied by
    a layer that COPIES income_stress onto itself unchanged for every household --
    it would not move when income moved for one household, it would just carry it.
    This asserts the value is not on the record at all."""
    premise_id, household = drawn_households[0]
    layer = physical_layer_for(premise_id, household)
    flattened = repr(dataclasses.asdict(layer))
    for stress in IncomeStress:
        assert stress.value not in flattened, (
            f"the physical layer record carries the commercial value {stress.value!r}"
        )
    assert "income" not in {f.name for f in dataclasses.fields(layer)}


def test_every_drawn_household_attribute_is_assigned_to_exactly_one_layer():
    """DEFECT: the silent re-merge. A new attribute lands on `Household` and nobody
    says which layer it belongs to, so the boundary decays with nothing red. This
    is keyed to the PROPERTY (every field is placed), not to today's field list."""
    unplaced = unclassified_household_fields()
    assert unplaced == (), (
        "these Household attributes are in neither layer -- classify them in "
        f"LAYER_OF or name them as identity: {unplaced}"
    )
    assert set(LAYER_OF.values()) == {Layer.PHYSICAL, Layer.COMMERCIAL}, (
        "one of the two layers has no members, which makes the split decorative"
    )


def test_a_declared_correlation_is_either_sourced_or_openly_unestablished():
    """DEFECT: the picked coefficient. The canon asks for the between-layer
    correlations to be modelled as correlations; the failure mode is a strength
    invented because a number was needed. Keyed to the property: established
    REQUIRES a source, and unestablished REQUIRES a reason, whichever way a future
    row goes."""
    assert LAYER_CORRELATIONS, "the correlations between the layers are not declared at all"
    for row in LAYER_CORRELATIONS:
        if row.established:
            assert row.source, f"{row.physical} <-> {row.commercial} is established with no source"
        else:
            assert len(row.reason) > 80, (
                f"{row.physical} <-> {row.commercial} is unestablished with no usable "
                "reason -- an honest gap must say what would close it"
            )
    # The guard is real, not decorative: constructing a sourceless established row
    # is refused.
    with pytest.raises(ValueError):
        LayerCorrelation(
            physical="occupancy",
            commercial="income_stress",
            established=True,
            source=None,
            reason="a coefficient with nothing behind it",
        )


def test_the_headcount_reproduces_the_census_marginal_and_the_bedrooms_draw_does_not(
    drawn_households,
):
    """DEFECT: the wrong marginal. Occupancy had two sources that disagreed --
    `occupancy_for_customer` on ONS TS017, and `behaviour_profile_for` drawing
    people_count from BEDROOMS on its own substream because no caller ever passed
    the segmentation field. The bedroom-derived one was what the demand path saw.

    Both legs are asserted. The second is what stops this being vacuous: it proves
    the tolerance below is narrow enough to reject a real, plausible, wrong draw --
    the one that was live in this tree.
    """
    from collections import Counter

    census_band = dict(OCCUPANCY_POPULATION_SHARE)
    # Read off the ASSEMBLED layer, not off `people_count_for` directly. The first
    # draft called the function and passed even when `physical_layer_for` was put
    # back on the bedrooms draw -- it graded the estimator and was blind to the
    # wiring, which is the only thing the demand path sees.
    counts = Counter(
        physical_layer_for(pid, hh).people_count for pid, hh in drawn_households
    )
    total = sum(counts.values())
    bands = Counter(
        occupancy_band_for(pid) for pid, _ in drawn_households
    )
    assert people_count_for(drawn_households[0][0]) == physical_layer_for(
        *drawn_households[0]
    ).people_count, "the assembled layer's headcount is not the census-anchored one"

    for band, target in census_band.items():
        got = bands[band] / total
        assert abs(got - target) < 0.025, (
            f"band {band.value} at {got:.3f} against the census {target:.3f}"
        )
    mean = sum(k * v for k, v in counts.items()) / total
    assert abs(mean - _CENSUS_MEAN_PEOPLE) < 0.06, (
        f"mean headcount {mean:.3f} against the census {_CENSUS_MEAN_PEOPLE}"
    )

    # The poison: the draw this replaced, run over the same premises.
    legacy = Counter(
        behaviour_profile_for(pid, hh).people_count for pid, hh in drawn_households
    )
    legacy_total = sum(legacy.values())
    legacy_one_person = legacy[1] / legacy_total
    legacy_mean = sum(k * v for k, v in legacy.items()) / legacy_total
    assert abs(legacy_one_person - census_band[list(census_band)[0]]) > 0.025, (
        "the bedrooms-derived draw now matches the census one-person share, so this "
        "control no longer discriminates -- re-derive the poison or delete the leg"
    )
    assert abs(legacy_mean - _CENSUS_MEAN_PEOPLE) > 0.06, (
        "the bedrooms-derived mean now matches the census, so the tolerance above "
        "cannot reject the draw this atom replaced"
    )


def test_the_household_that_was_away_and_the_one_that_could_not_afford_it_are_told_apart(
    drawn_households,
):
    """DEFECT: the director's own sentence -- 'we cannot tell a household that used
    less because nobody was home from one that could not afford it, and those
    demand the opposite response from a supplier.'

    ONE control over the WHOLE partition rather than a leg per branch: a
    discriminator that answers PHYSICAL for everything, or refuses for everything,
    passes any single-branch test. All four outcomes must be reachable over the
    real population, and the refusal must carry its reason and its recipe.

    The window is a BILLING MONTH, which is what a supplier actually attributes
    over. It also happens to be the window that makes the partition reachable at
    all: over a full year every household is away at some point, so the
    commercial-only and neither branches do not exist there. That is a property of
    the world rather than of the discriminator, and it is why this control
    asserts the partition rather than one branch -- the first draft used a year,
    and two of the four branches were unreachable.
    """
    dates = [dt.date(2023, 1, 1) + dt.timedelta(days=n) for n in range(31)]
    unconstrained = ComfortConstraint.unconstrained()
    rationing = ComfortConstraint(
        rationing_intensity=0.4, setpoint_reduction_c=1.2, comfort_hours_retained=0.8
    )

    seen: dict[str, ComfortAttribution] = {}
    for premise_id, household in drawn_households[:400]:
        layer = physical_layer_for(premise_id, household)
        for constraint in (unconstrained, rationing):
            att = attribute_lost_comfort(layer, constraint, dates)
            if att.presence_is_a_cause and att.affordability_is_a_cause:
                seen.setdefault("both", att)
            elif att.presence_is_a_cause:
                seen.setdefault("physical", att)
            elif att.affordability_is_a_cause:
                seen.setdefault("commercial", att)
            else:
                seen.setdefault("neither", att)

    assert set(seen) == {"both", "physical", "commercial", "neither"}, (
        "not every attribution outcome is reachable over the real population, so a "
        f"discriminator that always answered the same way would pass: got {sorted(seen)}"
    )

    assert seen["physical"].dominant_layer is Layer.PHYSICAL
    assert seen["commercial"].dominant_layer is Layer.COMMERCIAL
    assert seen["physical"].days_absent > 0
    assert seen["commercial"].days_absent == 0

    # The refusal fails CLOSED and says why, on the record, with what would settle it.
    both = seen["both"]
    assert both.dominant_layer is None
    assert both.why_not_ranked and "cannot yet tell" in both.why_not_ranked
    assert both.counterfactual_recipe and "unconstrained" in both.counterfactual_recipe

    # Nothing-to-attribute is a refusal too, and a different one: it names no
    # recipe, because there is no split to run.
    assert seen["neither"].dominant_layer is None
    assert seen["neither"].counterfactual_recipe is None

    # The away calendar is drawn over the whole year and intersected with the
    # window, never redistributed into it. Handing the month straight to
    # `away_day_calendar` puts a year of holidays inside January, which made every
    # household absent in every window and collapsed the partition to two branches.
    absent_in_month = sum(
        1
        for premise_id, household in drawn_households[:200]
        if attribute_lost_comfort(
            physical_layer_for(premise_id, household), unconstrained, dates
        ).days_absent
        > 0
    )
    assert 0 < absent_in_month < 150, (
        f"{absent_in_month} of 200 households are away in a single month -- the "
        "year's away days are being redistributed into the observation window"
    )


def test_the_two_causes_are_never_summed_into_one_number(drawn_households):
    """DEFECT: 'before dividing two numbers, say out loud what each one counts.'
    Days absent and degrees of setpoint reduction are not commensurable, and the
    tempting fix is a single 'lost comfort score' whose ratio counts nothing. The
    attribution record must expose both terms and no combined scalar."""
    premise_id, household = drawn_households[0]
    layer = physical_layer_for(premise_id, household)
    att = attribute_lost_comfort(
        layer,
        ComfortConstraint(
            rationing_intensity=0.4, setpoint_reduction_c=1.2, comfort_hours_retained=0.8
        ),
        [dt.date(2023, 1, 1) + dt.timedelta(days=n) for n in range(365)],
    )
    fields = {f.name for f in dataclasses.fields(att)}
    assert "days_absent" in fields and "setpoint_reduction_c" in fields
    for banned in ("total", "combined", "score", "lost_comfort_index"):
        assert not any(banned in name for name in fields), (
            f"the attribution carries a {banned!r} field -- the two causes have been "
            "summed into a quantity that counts nothing"
        )
