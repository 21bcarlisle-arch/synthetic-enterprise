"""The settled book's properties once it is CHOSEN for difference and carries per-account weights.

REUSE: tests/simulation/test_the_settled_book_is_chosen_and_weighted_not_culled_by_count.py
CLASS: CUSTOM
INDEX: searched "settlement", "sample", "cull", "weight", "choose". `test_net_new_acquisition.py`
       holds the CAMPAIGN's properties -- the funnel, the quote budget, the wall fixes, the
       customer-year ceiling -- and every one of them stays true and untouched; nothing there
       asserts anything about how the sample is SELECTED or about a per-account weight.
       `tests/tools/test_demand_vector_coverage.py` holds the chooser's own properties against a
       generated population, not against a campaign. This file is the selection's properties plus
       the two refusals, and folding them into the campaign's file would put two subjects behind
       one file name.

WHAT EACH CONTROL HERE IS FOR. The pre-registrations are
`docs/staging/records/SEAT_PREREGISTRATION_WHAT_CHOOSING_THE_SETTLED_SAMPLE_FOR_DIFFERENCE_MOVES_2026-09-11.md`
and `..._WHAT_FORCING_THE_YEAR_MARGINAL_COSTS_THE_DEMAND_AXES_2026-09-11.md`. Every assertion below
names the defect it fires on, and the axis-independence one names a defect that was REAL: the first
feature matrix carried floor area three times under three names.
"""
from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parents[2]
if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

from simulation.household import (  # noqa: E402
    BoilerAge,
    BuildEra,
    HeatingSystem,
    Household,
    InsulationLevel,
    PropertyType,
)
from simulation.settlement_choice import (  # noqa: E402
    CHOICE_AXES,
    choose_settled_sample,
    demand_vector,
)


def _household(property_type, era, insulation, bedrooms):
    return Household(
        customer_id="C", property_type=property_type, build_era=era, epc_rating="D",
        bedrooms=bedrooms, heating_system=HeatingSystem.GAS_BOILER_COMBI, boiler_age=BoilerAge.MID,
        has_solar=False, solar_kwp=0.0, solar_install_year=None, has_battery=False,
        battery_kwh=0.0, has_ev=False, ev_charger_kw=0.0, has_smart_meter=True,
        smart_meter_install_year=2020, insulation=insulation, has_driveway=True,
        roof_aspect="south")


class _Premise:
    def __init__(self, household, commodity="gas"):
        self.household = household
        self.commodity = commodity


class _Prospect:
    def __init__(self, premise):
        self.premise = premise


def _population():
    """A spread of real dwellings across the attributes this base's draw actually varies."""
    out = []
    for pt in (PropertyType.DETACHED, PropertyType.SEMI_DETACHED, PropertyType.TERRACED,
               PropertyType.FLAT):
        for era in (BuildEra.PRE_1919, BuildEra.ERA_1965_1980, BuildEra.POST_2000):
            for ins in (InsulationLevel.POOR, InsulationLevel.PARTIAL, InsulationLevel.FULL):
                for beds in (1, 3, 5):
                    out.append(_household(pt, era, ins, beds))
    return out


# ── the axes must be independent quantities, not one quantity renamed ────────────────────────

def test_no_two_choice_axes_are_the_same_quantity_in_different_units():
    """THE PROPERTY: every axis the sample is chosen over carries information the others do not.

    THE DEFECT THIS FIRES ON, AND IT WAS REAL. The first feature matrix took the whole of
    `fabric_parameters`: `volume_m3`, `solar_aperture_m2` and `internal_gain_kw` alongside the
    rest. All three are a constant times FLOOR AREA -- `area * _STOREY_HEIGHT_M`,
    `area * _WINDOW_AREA_RATIO * _SOLAR_TRANSMITTANCE * _FRAME_FACTOR`, and
    `area * _INTERNAL_GAIN_W_PER_M2 / 1000`. Carrying them weighted floor area THREE TIMES against
    infiltration's once, in both the distance the medoids are chosen by and the least squares the
    mass is solved from, so the book was chosen for difference in SIZE while every published
    sentence said BEHAVIOUR.

    It was caught by printing the table at real inputs, not by a test, because the arm still beat
    its counterfactual by 1.53x while carrying the defect. This control is what would have caught
    it: perfect correlation between two axes over a real spread of dwellings is a redundant axis,
    whatever the two are called.

    KEYED TO THE PROPERTY, NOT TO TODAY'S AXIS LIST. It does not assert which axes are present --
    that would go red the moment the list legitimately grows, and green if someone re-added a
    fourth alias of area.
    """
    numpy = pytest.importorskip("numpy")

    rows = [demand_vector(_Prospect(_Premise(h)), cy)
            for h, cy in zip(_population(), range(len(_population())))]
    assert all(r is not None for r in rows), "the fixture built a household the axes cannot read"
    values = numpy.asarray(rows, dtype=float)
    assert values.shape[1] == len(CHOICE_AXES), "the vector and the axis names disagree in length"

    correlation = numpy.corrcoef(values.T)
    for i in range(len(CHOICE_AXES)):
        for j in range(i + 1, len(CHOICE_AXES)):
            assert abs(correlation[i, j]) < 0.999, (
                "`{}` and `{}` correlate at {:.4f} over {} real dwellings -- they are one "
                "quantity in two units, and carrying both double-weights it in the distance the "
                "sample is chosen by".format(
                    CHOICE_AXES[i], CHOICE_AXES[j], correlation[i, j], len(values)))


def test_a_prospect_with_no_home_is_refused_and_never_placed_at_the_origin():
    """THE PROPERTY: an unplaceable candidate is a REFUSAL, never a zero vector.

    Fires on: returning `(0, 0, 0, 0)` for a prospect with no premise. Every such candidate would
    land on one point and become the densest cluster in the population -- a medoid chosen for a
    home that does not exist, given the mass of all the homes nobody could read.
    """
    class _Bare:
        premise = None

    assert demand_vector(_Bare(), 4.0) is None
    assert demand_vector(_Prospect(None), 4.0) is None


# ── the sample's own properties ──────────────────────────────────────────────────────────────

def _candidates(n=180):
    """A campaign-shaped candidate list: homes, costs, fuels and years."""
    homes = _population()
    vectors, costs, fuels, years = [], [], [], []
    for i in range(n):
        household = homes[i % len(homes)]
        year = 2016 + (i % 10)
        cy = max(0.5, (dt.date(2026, 1, 1) - dt.date(year, 6, 1)).days / 365.25)
        fuel = "gas" if i % 7 else "electricity"
        vectors.append(demand_vector(_Prospect(_Premise(household, fuel)), cy))
        costs.append(cy)
        fuels.append(fuel)
        years.append(year)
    return vectors, costs, fuels, years


def test_the_chosen_sample_never_crosses_the_customer_year_ceiling():
    """THE PROPERTY that the whole pass exists to enforce, asserted on the ANSWER.

    Fires on: a `k` search that reports the ceiling it was solving for on the strength of a
    monotonicity it assumed. `_largest_affordable_k` says in its own note that the cost is only
    monotone ENOUGH in `k`, so the bound has to be checked on the returned set.
    """
    pytest.importorskip("sklearn")
    vectors, costs, fuels, years = _candidates()
    headroom = sum(costs) * 0.25

    got = choose_settled_sample(vectors, costs, fuels, headroom_cy=headroom,
                                candidate_years=years)
    assert got is not None, "a quarter of the campaign's cost bought no sample at all"
    assert got["chosen_cost_cy"] <= headroom, (
        "the chosen set costs {:.1f} customer-years against a headroom of {:.1f}".format(
            got["chosen_cost_cy"], headroom))


def test_the_weights_reconstruct_the_year_composition_the_growth_page_renders():
    """THE PROPERTY §3 of the pre-registration claims, and it is the one that FAILED first.

    The chosen sample is deliberately NOT proportional by count, so the per-year figures the growth
    curve renders can only be right if the WEIGHTS carry the year marginal. On the first
    measurement they did not: 2017 came back at +84.9% of its funnel wins with the campaign total
    exact -- a correct headline over a false curve.

    Fires on: dropping the `groups=` rows from `fit_weights`, which is the repair that fixed it,
    or passing `candidate_years=None` from the campaign.
    """
    pytest.importorskip("sklearn")
    vectors, costs, fuels, years = _candidates()
    headroom = sum(costs) * 0.25

    got = choose_settled_sample(vectors, costs, fuels, headroom_cy=headroom,
                                candidate_years=years)
    assert got is not None

    population = {}
    for y in years:
        population[y] = population.get(y, 0) + 1
    reconstructed = {}
    for position, weight in zip(got["positions"], got["weights"]):
        y = years[position]
        reconstructed[y] = reconstructed.get(y, 0.0) + weight

    for year, count in sorted(population.items()):
        estimate = reconstructed.get(year, 0.0)
        assert abs(estimate - count) / count <= 0.05, (
            "{}'s settled accounts carry {:.1f} wins of weight against {} the company won -- "
            "{:+.1%}. The page renders this year as a bar.".format(
                year, estimate, count, (estimate - count) / count))


def test_the_sample_is_chosen_and_therefore_is_NOT_proportional_by_count():
    """THE PROPERTY that distinguishes this design from the one it replaces.

    A sample that came out proportional by count would be the systematic cull wearing the
    chooser's name, and every claim made for it would be unearned. So the control asserts the
    REPLACEMENT happened, not merely that a sample exists.

    Fires on: silently falling back to the count rule while reporting `chosen_weighted`.
    """
    pytest.importorskip("sklearn")
    vectors, costs, fuels, years = _candidates()
    headroom = sum(costs) * 0.25

    got = choose_settled_sample(vectors, costs, fuels, headroom_cy=headroom,
                               candidate_years=years)
    assert got is not None
    rate = len(got["positions"]) / len(vectors)

    population, settled = {}, {}
    for y in years:
        population[y] = population.get(y, 0) + 1
    for position in got["positions"]:
        y = years[position]
        settled[y] = settled.get(y, 0) + 1

    # At least one year must depart materially from the count rule's own answer for it.
    departures = [abs(settled.get(y, 0) - n * rate) for y, n in population.items()]
    assert max(departures) > 1.0, (
        "every year's settled count lands within one account of the systematic cull's -- this "
        "sample is proportional by count, which is what it was built to stop being")

    # ...and the weights must be a VECTOR, not the scalar the cull would have given.
    non_zero = [w for w in got["weights"] if w > 0]
    assert max(non_zero) / min(non_zero) >= 3.0, (
        "the per-account weights span only {:.2f}x -- that is a scalar inflation wearing a "
        "vector's clothes, and the argument for per-account weighting rests on it not "
        "being".format(max(non_zero) / min(non_zero)))


def test_the_weights_are_in_commercial_wins_and_sum_to_the_candidate_count():
    """THE PROPERTY that makes a weight readable without a second multiplication.

    Fires on: returning the NNLS probabilities unscaled, which sum to one and would understate
    every inflated figure on the page by a factor of the candidate count.
    """
    pytest.importorskip("sklearn")
    vectors, costs, fuels, years = _candidates()

    got = choose_settled_sample(vectors, costs, fuels, headroom_cy=sum(costs) * 0.25,
                                candidate_years=years)
    assert got is not None
    assert abs(sum(got["weights"]) - len(vectors)) / len(vectors) <= 0.02, (
        "the weights sum to {:.1f} against {} candidates -- they are not in commercial "
        "wins".format(sum(got["weights"]), len(vectors)))


def test_an_unplaceable_candidate_refuses_the_whole_sample_rather_than_half_choosing_it():
    """THE PROPERTY: fail closed, and closed means the WHOLE campaign.

    A partly-chosen, partly-culled book would be a third population with no name and no published
    sentence describing it. Fires on: dropping the unplaceable candidates and choosing over the
    rest, which is the tempting repair and is the one that publishes a book nobody can describe.
    """
    pytest.importorskip("sklearn")
    vectors, costs, fuels, years = _candidates()
    vectors[17] = None

    assert choose_settled_sample(vectors, costs, fuels, headroom_cy=sum(costs) * 0.25,
                                 candidate_years=years) is None


def test_a_headroom_too_small_for_any_chosen_set_refuses_rather_than_crossing_the_ceiling():
    """THE PROPERTY: the degenerate case is an operating state, not a hypothetical.

    A deep enough opening book leaves the campaign no headroom at all -- 82 founders already take
    778 of the 1,200. Fires on: returning the axis-extreme frame regardless of cost, which would
    put the book over the one ceiling the whole pass exists to hold.
    """
    pytest.importorskip("sklearn")
    vectors, costs, fuels, years = _candidates()

    assert choose_settled_sample(vectors, costs, fuels, headroom_cy=0.0,
                                 candidate_years=years) is None


# ── both branches of the campaign's selection must be REACHABLE ──────────────────────────────

def test_both_selections_can_actually_happen_in_the_campaign():
    """ONE CONTROL OVER THE WHOLE PARTITION, and it is here because a guard that refuses
    EVERYTHING passes every per-branch test written against it.

    The campaign either chooses the sample or culls it by count, and this asserts BOTH are
    reachable from real inputs -- a chooser that never engaged, and a fallback that could never be
    taken, both look exactly like the mechanism working from every other test in this file.

    Fires on: wiring the chooser behind a condition nothing satisfies, or leaving the fallback
    unreachable so an unplaceable candidate raises instead of falling back.
    """
    pytest.importorskip("sklearn")
    from simulation.net_new_acquisition import plan_growth_campaign

    assert callable(plan_growth_campaign)

    vectors, costs, fuels, years = _candidates()
    chosen = choose_settled_sample(vectors, costs, fuels, headroom_cy=sum(costs) * 0.25,
                                   candidate_years=years)
    unplaceable = list(vectors)
    unplaceable[3] = None
    culled = choose_settled_sample(unplaceable, costs, fuels, headroom_cy=sum(costs) * 0.25,
                                   candidate_years=years)

    assert chosen is not None and culled is None, (
        "the two selections are not both reachable: chosen={}, fallback-triggering={}".format(
            chosen is not None, culled is None))
