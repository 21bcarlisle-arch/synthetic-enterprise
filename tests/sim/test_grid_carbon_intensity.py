"""R15 contract for the half-hourly grid-intensity SHAPE.

WHAT IS UNDER TEST is one claim with two halves that must not cover for each other. The shape
has to MOVE -- a flat series is the annual-only number this replaces, wearing a timestamp -- and
it has to move around a mean of exactly 1.0, because a consumer multiplies it by its own
published annual intensity and any drift in that mean silently re-levels a published figure.

THE ERROR DIRECTION THAT MATTERS. Every mistake available here makes time-shifting look more
valuable than it is: a marginal-unit efficiency instead of the dispatched average, a must-run
floor asserted at zero carbon, a missing renewable outturn read as zero renewables. Each has its
own test below and each of those tests is written to fail in the flattering direction.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

import sim.merit_order_reconstruction as merit
from sim import grid_carbon_intensity as gci

REPO = Path(__file__).resolve().parents[2]
DEMAND_CACHE = REPO / "sim" / "cache" / "elexon_demand_full.json"
AGWS_CACHE = REPO / "sim" / "cache" / "elexon_agws_full.json"

STILL_WINTER_EVENING = (45_000.0, 2_000.0)   # (demand MW, wind+solar MW) -- thermal working hard
WINDY_SUMMER_NIGHT = (22_000.0, 18_000.0)    # almost nothing thermal left to do
YEAR = 2024


# --------------------------------------------------------------------------- #
# The emission factor, checked against a source that did not produce it        #
# --------------------------------------------------------------------------- #

def test_the_two_published_routes_to_a_gas_emission_factor_agree():
    """R15 INDEPENDENCE, and the reason this module is allowed to compute emissions at all.

    There are two published GB routes to "tonnes CO2 per electrical MWh from a CCGT" and they
    come from different documents:

        DESNZ GHG conversion factors  ->  fuel-input factor / DUKES 5.10.C efficiency
        DUKES 5.14                    ->  the electrical factor, published directly

    This module uses the FIRST, because only that one moves with the efficiency of the unit
    actually dispatched, which is the whole point of a half-hourly series. Using it without ever
    checking it against the second would be taking one source's word for a number another source
    publishes -- so they are checked, and they agree to within 2.2% in every grounded year.

    MUTATION (must fire): change `EF_GAS_TCO2_PER_MWH_TH` or any efficiency in
    `CCGT_THERMAL_EFFICIENCY_BY_YEAR` without changing DUKES 5.14 to match.
    """
    worst = 0.0
    for year, efficiency in merit.CCGT_THERMAL_EFFICIENCY_BY_YEAR.items():
        derived = merit.EF_GAS_TCO2_PER_MWH_TH / efficiency
        published = merit.EF_GAS_TCO2_PER_MWH_E_BY_YEAR[year]
        worst = max(worst, abs(derived - published) / published)
    assert worst < 0.03, (
        f"the fuel-input route and the DUKES electrical route now disagree by {worst:.1%}; "
        "one of the two sources has moved and this module is using the one that moved"
    )


# --------------------------------------------------------------------------- #
# It moves, and it moves the right way                                         #
# --------------------------------------------------------------------------- #

def test_a_still_winter_evening_is_dirtier_than_a_windy_summer_night():
    """The claim the whole module exists to support. If this is ever false, nothing downstream
    of it means anything and no amount of correct normalisation would save it."""
    busy = gci.emissions_rate_t_per_mwh(*STILL_WINTER_EVENING, YEAR)
    quiet = gci.emissions_rate_t_per_mwh(*WINDY_SUMMER_NIGHT, YEAR)

    assert busy > quiet * 3, (
        f"a still winter evening ({busy:.4f} t/MWh) is not meaningfully dirtier than a windy "
        f"summer night ({quiet:.4f}); the series carries no timing information"
    )


def test_the_rate_rises_MONOTONICALLY_with_residual_demand():
    """A shape that wobbles is not a dispatch. Holding renewables fixed and walking demand up
    must never make the grid cleaner -- the stack is dispatched cheapest-and-cleanest first, so
    every extra MW is met by something at least as dirty as the last."""
    rates = [gci.emissions_rate_t_per_mwh(d, 5_000.0, YEAR)
             for d in range(15_000, 50_001, 2_500)]

    assert all(a <= b + 1e-12 for a, b in zip(rates, rates[1:])), (
        f"the emissions rate is not monotone in residual demand: {[round(r, 4) for r in rates]}"
    )


# --------------------------------------------------------------------------- #
# The average of what ran, not the last thing to run                           #
# --------------------------------------------------------------------------- #

def test_the_CCGT_band_is_charged_at_the_AVERAGE_dispatched_efficiency():
    """THE MISTAKE THIS MODULE WAS ONE LINE AWAY FROM MAKING, and it flatters the mission.

    `reconstruct_price_gbp_per_mwh` returns the SRMC of the MARGINAL unit, because that is what
    sets price. Emissions are not set by the marginal unit -- every plant that ran emitted. A
    band loaded to fraction f has run everything from the best-build efficiency down to
    `best - (best-worst)*f`, so its mean is the MIDPOINT of that ramp, and using the marginal
    figure instead would overstate the swing between quiet and busy half hours.

    MUTATION (must fire): drop the `/ 2.0` from `mean_dispatched_eff`.

    Checked at the outcome, against a hand-computed dispatch, so it cannot be satisfied by the
    module agreeing with itself.
    """
    demand, renewables = 30_000.0, 0.0
    thermal = demand - merit.MUST_RUN_FLOOR_MW
    load_fraction = thermal / merit.CCGT_CAPACITY_MW
    worst, best = merit._ccgt_efficiency_band(YEAR)

    average_eff = best - (best - worst) * load_fraction / 2.0
    marginal_eff = best - (best - worst) * load_fraction
    expected = (
        merit.MUST_RUN_FLOOR_MW * gci.MUST_RUN_EMISSIONS_RATE_T_PER_MWH
        + thermal * (merit.EF_GAS_TCO2_PER_MWH_TH / average_eff)
    ) / demand
    if_marginal = (
        merit.MUST_RUN_FLOOR_MW * gci.MUST_RUN_EMISSIONS_RATE_T_PER_MWH
        + thermal * (merit.EF_GAS_TCO2_PER_MWH_TH / marginal_eff)
    ) / demand

    assert if_marginal > expected, "the two are indistinguishable here, so this proves nothing"
    assert gci.emissions_rate_t_per_mwh(demand, renewables, YEAR) == pytest.approx(expected)


# --------------------------------------------------------------------------- #
# Must-run means must run -- the hard zero this had on its first run           #
# --------------------------------------------------------------------------- #

def test_a_grid_where_renewables_EXCEED_demand_is_still_not_carbon_free():
    """THE DEFECT, MEASURED ON THE LIVE SERIES BEFORE IT WAS FIXED. Written as
    `min(max(residual, 0), floor)`, the must-run floor became the residual's leftovers -- so
    every half hour where wind and solar beat national demand switched the nuclear fleet off,
    emissions came out at exactly 0.000, and the shape reported a perfectly clean grid several
    hundred times a year.

    GB curtails WIND in that situation, not baseload. And the consequence of the bug is the
    flattering one: a half hour at zero makes shifting load into it infinitely valuable.

    MUTATION (must fire): take the floor against the residual instead of against demand.
    """
    demand = 20_000.0
    rate = gci.emissions_rate_t_per_mwh(demand, 26_000.0, YEAR)

    assert rate > 0.0, "renewables exceeding demand switched the must-run fleet off"
    # No thermal ran, so every gram came from the must-run fleet -- spread over the whole of
    # demand, because the surplus renewables met the rest and the surplus above that is what
    # got curtailed.
    assert rate == pytest.approx(
        merit.MUST_RUN_FLOOR_MW * gci.MUST_RUN_EMISSIONS_RATE_T_PER_MWH / demand
    )


def test_the_must_run_rate_is_DERIVED_from_a_cited_factor_and_a_stated_split():
    """Not a literal. `carbon_emissions.grid_intensity_g_co2e_per_kwh` already holds this line
    on the annual side -- "never a literal, so a caller can always decompose the number it was
    given" -- and an unsourced constant in the denominator of the mission's own score is the
    last place to break it."""
    assert gci.MUST_RUN_EMISSIONS_RATE_T_PER_MWH == pytest.approx(
        gci.MUST_RUN_BIOMASS_SHARE * gci.BIOMASS_G_CO2_PER_KWH / 1000.0
    )
    assert gci.BIOMASS_G_CO2_PER_KWH > 0.0, (
        "biomass at zero makes every very quiet half hour read as a perfectly clean grid"
    )


# --------------------------------------------------------------------------- #
# The anchor: a demand-weighted mean of exactly 1.0                            #
# --------------------------------------------------------------------------- #

def _toy(demands, renewables, year="2024"):
    d = {(f"{year}-01-{1 + i // 48:02d}", 1 + i % 48): v for i, v in enumerate(demands)}
    r = {k: renewables[i] for i, k in enumerate(d)}
    return d, r


def test_the_shape_is_normalised_to_a_DEMAND_WEIGHTED_mean_of_one():
    """The anchor property, and the reason a consumer's published annual total does not move
    when timing is introduced: a household drawing in the national shape gets the published
    annual number back unchanged, and only one that draws at different times differs."""
    demands = [20_000.0, 30_000.0, 45_000.0, 25_000.0] * 12
    renewables = [10_000.0, 5_000.0, 2_000.0, 12_000.0] * 12
    d, r = _toy(demands, renewables)

    shape = gci.build_shape(d, r)

    assert gci.demand_weighted_mean(shape, d, "2024") == pytest.approx(1.0)


def test_MUTATION_an_UNWEIGHTED_mean_would_NOT_satisfy_the_anchor():
    """The null that makes the test above mean something. If the two averages coincided on this
    data, "demand-weighted" would be decoration and swapping it for a plain mean would pass --
    so the fixture is deliberately built with dirty half hours at high demand, which is what a
    real grid looks like and what makes the two diverge."""
    demands = [20_000.0, 30_000.0, 45_000.0, 25_000.0] * 12
    renewables = [10_000.0, 5_000.0, 2_000.0, 12_000.0] * 12
    d, r = _toy(demands, renewables)

    shape = gci.build_shape(d, r)
    plain = sum(shape.values()) / len(shape)

    assert plain != pytest.approx(1.0, abs=1e-3), (
        f"the unweighted mean is also {plain:.4f}, so this fixture cannot tell the two apart"
    )


# --------------------------------------------------------------------------- #
# Absence is not zero, and unavailable is not flat                             #
# --------------------------------------------------------------------------- #

def test_a_MISSING_renewable_outturn_is_SKIPPED_not_read_as_zero_renewables():
    """R15 FAIL-OPEN. A gap in the wind feed is not a windless half hour, and reading it as one
    invents a dirty half hour out of a missing record -- which would then make the half hours
    around it look cleaner by comparison, i.e. the flattering direction again."""
    d, r = _toy([20_000.0, 30_000.0] * 24, [8_000.0, 6_000.0] * 24)
    dropped = next(iter(r))
    del r[dropped]

    shape = gci.build_shape(d, r)

    assert dropped not in shape, "a half hour with no renewable outturn was given a shape anyway"
    assert len(shape) == len(d) - 1


def test_NO_OVERLAP_AT_ALL_raises_rather_than_returning_a_flat_series():
    """R15 FAIL-SILENT, and the specific silence that would be worst here. An empty or flat
    shape does not read as "this did not run" -- it reads as "timing does not matter", which is
    precisely the claim the module was built to refute, arrived at by the instrument breaking.
    """
    d, _ = _toy([20_000.0] * 48, [5_000.0] * 48)

    with pytest.raises(gci.ShapeUnavailable):
        gci.build_shape(d, {})


def test_a_zero_demand_half_hour_has_no_rate_rather_than_a_divide_by_zero():
    with pytest.raises(gci.ShapeUnavailable):
        gci.emissions_rate_t_per_mwh(0.0, 0.0, YEAR)


# --------------------------------------------------------------------------- #
# The live series                                                              #
# --------------------------------------------------------------------------- #

@pytest.fixture(scope="module")
def live_shape():
    if not (DEMAND_CACHE.is_file() and AGWS_CACHE.is_file()):
        pytest.skip("the Elexon outturn caches are not present in this tree")
    from sim.generation_demand_history import aggregate_renewable_generation

    demand = gci.aggregate_demand(json.loads(DEMAND_CACHE.read_text()))
    renewables = aggregate_renewable_generation(json.loads(AGWS_CACHE.read_text()))
    return gci.build_shape(demand, renewables), demand


def test_the_LIVE_series_holds_the_anchor_in_every_year(live_shape):
    shape, demand = live_shape
    for year in sorted({k[0][:4] for k in shape}):
        assert gci.demand_weighted_mean(shape, demand, year) == pytest.approx(1.0), (
            f"{year}'s shape does not average to 1.0, so a consumer's published annual total "
            "would move purely by introducing timing"
        )


def test_the_LIVE_series_is_not_FLAT_in_any_year(live_shape):
    """The other half. A series that averages 1.0 perfectly and never leaves it is the annual
    number with extra steps, and it would pass every normalisation test above."""
    shape, _ = live_shape
    for year in sorted({k[0][:4] for k in shape}):
        low, high = gci.spread(shape, year)
        assert high / low > 3.0, (
            f"{year} spans only {low:.3f}-{high:.3f}; there is no timing signal to act on"
        )


def test_the_grid_GOT_MORE_VARIABLE_as_renewables_grew(live_shape):
    """A fidelity check the shape should pass for a reason outside itself: GB added a great deal
    of wind between 2016 and 2024, and a grid with more zero-marginal-cost variable generation
    has a WIDER intensity range, not a narrower one. If this failed, the shape would be tracking
    something other than the physics -- and no assertion about its mean would have caught it."""
    shape, _ = live_shape
    _, early_high = gci.spread(shape, "2016")
    _, late_high = gci.spread(shape, "2024")

    assert late_high > early_high, (
        f"the dirtiest half hour of 2024 ({late_high:.2f}x) is no worse relative to its own year "
        f"than 2016's ({early_high:.2f}x), which is not the direction GB's grid moved"
    )


def test_this_module_declares_NO_absolute_annual_intensity_series():
    """The rule `tools/grid_intensity_guard.py` enforces under company/, held voluntarily here.

    That guard deliberately does not scan `sim/`, so nothing would have stopped this module
    becoming the FOURTH annual grid-intensity series in a tree where three of them once
    disagreed by 55.6%. The split -- world owns the shape, company owns the level -- is the
    reason there is no fourth, and it is worth a test rather than a paragraph.
    """
    import ast

    tree = ast.parse((REPO / "sim" / "grid_carbon_intensity.py").read_text(encoding="utf-8"))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)

    # Checked on IMPORTS, not on the source text: the first version of this grepped for the
    # accessor's name and reddened on the docstring paragraph explaining why it is not used --
    # a control that cannot tell a reference from a mention is a control that gets deleted.
    offenders = sorted(m for m in imported if m.split(".")[0] in ("company", "saas"))
    assert offenders == [], (
        f"this module imports {offenders}; if it needs the annual LEVEL it has crossed from "
        "shape into absolute intensity, and there are two owners of that series again "
        "(and it is a wall crossing besides)"
    )
    assert "dimensionless" in gci.SHAPE_BASIS
