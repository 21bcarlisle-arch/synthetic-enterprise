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
# The two gaps this module named for its whole life, closed 2026-08-25          #
# --------------------------------------------------------------------------- #

FRENCH_T_PER_MWH = 0.053   # NESO's own published import factor, via sim/elexon_fuel_outturn.py
DUTCH_T_PER_MWH = 0.474


def test_an_import_is_DIRTY_against_a_windy_night_and_CLEAN_against_a_working_gas_fleet():
    """THE WHOLE REASON THE NET EFFECT HAD TO BE MEASURED RATHER THAN ARGUED.

    The feed's `ERROR_DIRECTION` used to assert that omitting imports made quiet half hours look
    cleaner, while `NAMED_GAPS` twenty lines above asserted it made them look dirtier. Both
    sentences were about the same omission and one of them had to be wrong. Neither was: the sign
    depends on what the import DISPLACES.

      * On a windy night the thermal stack is already idle. A French import at 53 gCO2/kWh
        displaces nothing and simply ADDS carbon to a half hour the model had running on
        must-run and curtailed wind. The clean end goes UP -- which is the direction that
        narrows this model's overstated spread toward NESO's.
      * In a still winter evening the same import displaces CCGT at roughly 380 gCO2/kWh. The
        dirty end goes DOWN.

    MUTATION (must fire): drop the `+ import_mw * import_rate` term, or stop subtracting
    `import_mw` from the residual -- each kills exactly one of the two limbs.
    """
    quiet_demand, quiet_renewables = WINDY_SUMMER_NIGHT
    quiet_without = gci.emissions_rate_t_per_mwh(quiet_demand, quiet_renewables, YEAR)
    quiet_with = gci.emissions_rate_t_per_mwh(
        quiet_demand, quiet_renewables, YEAR,
        import_mw=3_000.0, import_rate_t_per_mwh=FRENCH_T_PER_MWH,
    )
    assert quiet_with > quiet_without, (
        "a 3 GW import into a half hour with no thermal running added no carbon at all"
    )

    busy_demand, busy_renewables = STILL_WINTER_EVENING
    busy_without = gci.emissions_rate_t_per_mwh(busy_demand, busy_renewables, YEAR)
    busy_with = gci.emissions_rate_t_per_mwh(
        busy_demand, busy_renewables, YEAR,
        import_mw=3_000.0, import_rate_t_per_mwh=FRENCH_T_PER_MWH,
    )
    assert busy_with < busy_without, (
        "a French import displaced gas in a still winter evening and the half hour did not clean up"
    )


def test_the_import_FACTOR_decides_the_sign_and_the_Dutch_cable_is_dirtier_than_GB_gas():
    """The rate passed in is not decoration, and this test was written wrong first.

    The first version asserted that a Dutch import at 474 gCO2/kWh must make a STILL WINTER
    EVENING dirtier. It does the opposite, and the model is right: at 45 GW of demand with 2 GW
    of renewables the plant at the margin is an OCGT peaker, `EF_GAS_TCO2_PER_MWH_TH / 0.35` =
    523 gCO2/kWh, so even the dirtiest cable GB has is an improvement on what it displaced.

    So the claim that can actually be made is narrower and more useful: against the MID-MERIT
    CCGT band, ~370 gCO2/kWh at the efficiency actually dispatched, a Dutch import is dirtier and
    a French one is cleaner. Two cables, one half hour, opposite signs -- which no model that
    charges imports at a constant can produce.

    MUTATION (must fire): ignore `import_rate_t_per_mwh` and charge every import at one factor.
    """
    demand, renewables = 30_000.0, 0.0   # thermal 22 GW, inside the 30 GW CCGT band
    plain = gci.emissions_rate_t_per_mwh(demand, renewables, YEAR)
    dutch = gci.emissions_rate_t_per_mwh(
        demand, renewables, YEAR, import_mw=3_000.0, import_rate_t_per_mwh=DUTCH_T_PER_MWH,
    )
    french = gci.emissions_rate_t_per_mwh(
        demand, renewables, YEAR, import_mw=3_000.0, import_rate_t_per_mwh=FRENCH_T_PER_MWH,
    )
    assert dutch > plain > french

    # And the peaker case, stated rather than left as the thing that broke the first draft.
    peak_demand, peak_renewables = STILL_WINTER_EVENING
    assert gci.emissions_rate_t_per_mwh(
        peak_demand, peak_renewables, YEAR,
        import_mw=3_000.0, import_rate_t_per_mwh=DUTCH_T_PER_MWH,
    ) < gci.emissions_rate_t_per_mwh(peak_demand, peak_renewables, YEAR)


def test_an_EXPORT_passed_as_a_negative_import_cannot_credit_the_half_hour():
    """Belt to `elexon_fuel_outturn`'s braces. The adapter clamps per cable; if a later caller
    hands this function a netted negative anyway, it must not become negative tonnage and it must
    not increase GB's thermal requirement either -- the quantity is per kWh of GB DEMAND, and
    under that consumption basis an exported MWh's emissions belong to whoever consumed it.

    MUTATION (must fire): drop the `max(0.0, ...)` clamp on `import_mw`.
    """
    demand, renewables = STILL_WINTER_EVENING
    plain = gci.emissions_rate_t_per_mwh(demand, renewables, YEAR)
    exporting = gci.emissions_rate_t_per_mwh(
        demand, renewables, YEAR, import_mw=-3_000.0, import_rate_t_per_mwh=FRENCH_T_PER_MWH,
    )
    assert exporting == pytest.approx(plain)


def test_coal_dispatches_ABOVE_the_CCGT_band_and_is_invisible_below_it():
    """Coal is a peaking plant in this window -- DUKES 5.10.B load factors of 8-21% against
    CCGT's three to four times that -- so it runs only once the mid-merit band is full.

    Both limbs are needed. A model that dispatched coal FIRST would make every half hour dirtier
    and would still pass a test that only checked "coal raises emissions somewhere".

    MUTATION (must fire): dispatch coal before the CCGT band, or ahead of it in the residual.
    """
    inside_band = 25_000.0   # thermal 17 GW, well inside the 30 GW CCGT band
    assert gci.emissions_rate_t_per_mwh(
        inside_band, 0.0, YEAR, coal_capacity_mw=8_000.0
    ) == pytest.approx(gci.emissions_rate_t_per_mwh(inside_band, 0.0, YEAR))

    above_band = 45_000.0    # thermal 37 GW, 7 GW of it above the CCGT band
    assert gci.emissions_rate_t_per_mwh(
        above_band, 0.0, YEAR, coal_capacity_mw=8_000.0
    ) > gci.emissions_rate_t_per_mwh(above_band, 0.0, YEAR)


def test_coal_above_the_band_displaces_PEAKERS_and_is_charged_at_the_DUKES_coal_factor():
    """Checked at the outcome against a hand-computed dispatch, so it cannot be satisfied by the
    module agreeing with itself. Coal at ~0.92 t/MWh replaces OCGT at
    `EF_GAS_TCO2_PER_MWH_TH / 0.35` ~ 0.52, so the half hour gets dirtier by the difference.

    MUTATION (must fire): charge coal at the gas factor, or leave the peaker MW in place instead
    of subtracting the coal that displaced them (which would double-count 3 GW of generation).
    """
    demand, coal_capacity = 45_000.0, 3_000.0
    thermal = demand - merit.MUST_RUN_FLOOR_MW
    above = thermal - merit.CCGT_CAPACITY_MW
    worst, best = merit._ccgt_efficiency_band(YEAR)
    mean_eff = best - (best - worst) * (merit.CCGT_CAPACITY_MW / merit.CCGT_CAPACITY_MW) / 2.0

    expected = (
        merit.MUST_RUN_FLOOR_MW * gci.MUST_RUN_EMISSIONS_RATE_T_PER_MWH
        + merit.CCGT_CAPACITY_MW * (merit.EF_GAS_TCO2_PER_MWH_TH / mean_eff)
        + coal_capacity * merit.EF_COAL_TCO2_PER_MWH_E_BY_YEAR[YEAR]
        + (above - coal_capacity) * (merit.EF_GAS_TCO2_PER_MWH_TH / merit.OCGT_REFERENCE_EFFICIENCY)
    ) / demand

    assert gci.emissions_rate_t_per_mwh(
        demand, 0.0, YEAR, coal_capacity_mw=coal_capacity
    ) == pytest.approx(expected)


def test_a_year_with_no_coal_capacity_reproduces_the_pre_coal_shape_exactly():
    """The fleet closed in September 2024, and the model has to close with it rather than carry
    a phantom band forward. No end date is written anywhere: the capacity is measured from the
    published outturn and reaches zero on its own.

    MUTATION (must fire): default a missing year's coal capacity to the previous year's.
    """
    d, r = _toy([45_000.0, 25_000.0] * 24, [1_000.0, 4_000.0] * 24, year="2025")
    with_map = gci.build_shape(d, r, coal_capacity_by_year={2024: 9_000.0, 2025: 0.0})
    without = gci.build_shape(d, r)
    assert with_map == without


def test_the_coal_capacity_of_a_CLAMPED_year_is_never_borrowed_from_the_year_before():
    """`_year_of` clamps 2025 to 2024 so the DUKES tables stay in range, and clamping is right
    for a published constant that stops in 2024. It is wrong for a fleet that SHUT: reading the
    coal capacity through the same clamp would resurrect 2024's coal in a year Elexon says the
    fleet generated nothing.

    MUTATION (must fire): key the coal-capacity lookup on `_year_of(year)`.
    """
    d, r = _toy([45_000.0] * 48, [1_000.0] * 48, year="2025")
    borrowed = gci.build_shape(d, r, coal_capacity_by_year={2024: 9_000.0})
    honest = gci.build_shape(d, r)
    # A single-year toy normalises to a mean of 1.0 either way, so the shapes cannot be compared
    # directly -- the absolute rate is where the borrowing would show.
    rate_clamped = gci.emissions_rate_t_per_mwh(45_000.0, 1_000.0, 2025, coal_capacity_mw=9_000.0)
    rate_honest = gci.emissions_rate_t_per_mwh(45_000.0, 1_000.0, 2025, coal_capacity_mw=0.0)
    assert rate_clamped > rate_honest, "this fixture cannot tell the two apart, so it proves nothing"
    assert borrowed == honest


def test_a_half_hour_with_NOTHING_left_to_dispatch_still_runs_gas():
    """THE DEFECT THIS CLOSED, stated as the half hour that produced it.

    Renewables plus must-run cover the whole of demand, so the stack has nothing to do and the
    model dispatched EXACTLY ZERO thermal plant -- 16.1% of 2024's half hours and 30.8% of
    2025's. GB never does that: gas runs for inertia, reserve and voltage whatever the residual
    says. Those are also precisely the half hours a time-shifting recommendation points a
    customer at, so the error sat exactly where it did the most damage.

    MUTATION (must fire): drop the `thermal_mw = max(thermal_mw, floor_mw)` line.
    """
    quiet = dict(demand_mw=22_000.0, renewable_generation_mw=18_000.0, year=YEAR)
    without = gci.emissions_rate_t_per_mwh(**quiet)
    with_floor = gci.emissions_rate_t_per_mwh(**quiet, thermal_floor_mw=4_000.0)
    assert with_floor > without, "the floor must put carbon into a half hour that had none"
    # And it is the MUST-RUN rate exactly when no floor is given -- i.e. the old behaviour was a
    # grid of nothing but biomass-blended baseload.
    assert without == pytest.approx(gci.MUST_RUN_EMISSIONS_RATE_T_PER_MWH * 8_000.0 / 22_000.0)


def test_the_floor_displaces_RENEWABLES_and_never_manufactures_generation_above_demand():
    """The floor is served by constraining wind off, not by generating more than the half hour
    used -- the same call the must-run floor already makes two lines above it.

    A floor larger than the room under demand would push total generation past demand and divide
    it by demand anyway, reporting an intensity for energy nobody consumed.

    MUTATION (must fire): drop the `min(..., demand_mw - must_run_mw)` cap.
    """
    # 9 GW demand, 8 GW must-run: only 1 GW of room, against a 5 GW floor.
    capped = gci.emissions_rate_t_per_mwh(9_000.0, 9_000.0, YEAR, thermal_floor_mw=5_000.0)
    exactly_the_room = gci.emissions_rate_t_per_mwh(9_000.0, 9_000.0, YEAR, thermal_floor_mw=1_000.0)
    assert capped == pytest.approx(exactly_the_room)
    absurd = gci.emissions_rate_t_per_mwh(9_000.0, 9_000.0, YEAR, thermal_floor_mw=50_000.0)
    assert absurd == pytest.approx(exactly_the_room)


def test_a_BUSY_half_hour_is_UNCHANGED_by_the_floor():
    """The correction must reach the quiet end and nothing else. A still winter evening already
    dispatches far more than any year's floor, so the floor is not binding and must not move it.

    MUTATION (must fire): apply the floor as an ADDITION to thermal rather than a lower bound.
    """
    busy = dict(demand_mw=45_000.0, renewable_generation_mw=2_000.0, year=YEAR)
    assert gci.emissions_rate_t_per_mwh(**busy, thermal_floor_mw=4_000.0) == pytest.approx(
        gci.emissions_rate_t_per_mwh(**busy)
    )


def test_the_DEFAULT_floor_reproduces_the_known_wrong_shape_exactly():
    """The signature is fail-open by construction and this pins that rather than hiding it: a
    caller that forgets the floor gets the pre-2026-08-25 series, silently.

    That is why the control is NOT here. It is `generate_grid_intensity_feed.fuel_mix()`, which
    RAISES when the thermal series is absent so the published feed cannot quietly revert. This
    test exists so the fail-open default is a known and stated property.

    MUTATION (must fire): give `thermal_floor_mw` a non-zero default, which would change the
    shape of every existing caller without any of them saying so.
    """
    d, r = _toy([45_000.0, 25_000.0] * 24, [1_000.0, 4_000.0] * 24, year="2024")
    assert gci.build_shape(d, r, thermal_floor_by_year={2024: 0.0}) == gci.build_shape(d, r)


def test_the_floor_of_a_year_is_never_borrowed_from_another_year():
    """A year with no measured floor gets none -- the pre-existing behaviour -- rather than the
    neighbouring year's, which would be a measurement asserted where none was taken.

    MUTATION (must fire): key the floor lookup on `_year_of(year)`, or fall back to any year.
    """
    d, r = _toy([22_000.0] * 48, [18_000.0] * 48, year="2025")
    rate_2025 = gci.emissions_rate_t_per_mwh(22_000.0, 18_000.0, 2025, thermal_floor_mw=4_000.0)
    rate_none = gci.emissions_rate_t_per_mwh(22_000.0, 18_000.0, 2025, thermal_floor_mw=0.0)
    assert rate_2025 > rate_none, "this fixture cannot tell the two apart, so it proves nothing"
    assert gci.build_shape(d, r, thermal_floor_by_year={2024: 4_000.0}) == gci.build_shape(d, r)


def test_an_import_larger_than_demand_cannot_meet_the_half_hour_twice():
    """A feed defect, or a half hour where GB wheeled power across itself, must not produce a
    rate computed on more energy than was consumed.

    MUTATION (must fire): drop the `min(..., demand_mw)` clamp.
    """
    rate = gci.emissions_rate_t_per_mwh(
        10_000.0, 0.0, YEAR, import_mw=40_000.0, import_rate_t_per_mwh=DUTCH_T_PER_MWH,
    )
    assert rate < DUTCH_T_PER_MWH + gci.MUST_RUN_EMISSIONS_RATE_T_PER_MWH


def test_the_anchor_still_holds_once_coal_and_cables_are_dispatched():
    """The normalisation is what stops a consumer's published annual total from moving. Adding
    two new emission sources to the numerator is exactly the change that could break it silently.
    """
    demands = [20_000.0, 30_000.0, 45_000.0, 25_000.0] * 12
    renewables = [10_000.0, 5_000.0, 2_000.0, 12_000.0] * 12
    d, r = _toy(demands, renewables)
    imports = {k: (2_000.0, FRENCH_T_PER_MWH) for k in d}

    shape = gci.build_shape(d, r, imports_by_period=imports, coal_capacity_by_year={2024: 5_000.0})

    assert gci.demand_weighted_mean(shape, d, "2024") == pytest.approx(1.0)


def test_a_half_hour_with_NO_import_reading_is_dispatched_with_none_rather_than_DROPPED():
    """The opposite call from the one made for a missing renewable outturn, and the difference is
    which way the error runs. A missing wind reading treated as zero INVENTS a dirty half hour;
    a missing cable reading treated as zero reproduces the behaviour this series had for its
    whole life and is bounded by it. Dropping the half hour instead would shorten the series the
    year's normalisation is taken over -- a coverage change disguised as a physics one.

    MUTATION (must fire): `continue` when a key is absent from `imports_by_period`.
    """
    d, r = _toy([20_000.0, 30_000.0] * 24, [8_000.0, 6_000.0] * 24)
    partial = {k: (2_000.0, FRENCH_T_PER_MWH) for k in list(d)[:10]}

    shape = gci.build_shape(d, r, imports_by_period=partial)

    assert len(shape) == len(d)


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
# --------------------------------------------------------------------------- #
# The measured zero-carbon must-run block                                     #
# --------------------------------------------------------------------------- #

def test_the_DEFAULTED_argument_reproduces_the_flat_8_GW_BLOCK_EXACTLY():
    """The refactor that split the block must change no number until the series is supplied.

    This is what makes the before/after measurement mean anything: the two arms differ by ONE
    input, not by an arithmetic rewrite that happened to travel with it. The old code applied one
    blended rate (0.30 x 120 g) to the whole 8,000 MW; the new code applies 120 g to the 2,400 MW
    of biomass inside it. Those are the same tonnage, and they have to stay the same tonnage
    across every regime -- oversupply, the CCGT band, above it, and demand below the block.

    MUTATION (must fire): change `MUST_RUN_BIOMASS_MW`, or take the biomass share of the whole
    block instead of the share of what was SERVED.
    """
    for demand, renewables in [
        (45_000.0, 2_000.0),     # still winter evening, above the CCGT band
        (30_000.0, 12_000.0),    # ordinary, inside the band
        (22_000.0, 18_000.0),    # quiet, nothing left to dispatch
        (6_000.0, 1_000.0),      # demand BELOW the must-run block, so it is scaled down
    ]:
        expected = (
            min(demand, merit.MUST_RUN_FLOOR_MW) * gci.MUST_RUN_EMISSIONS_RATE_T_PER_MWH
        )
        rate = gci.emissions_rate_t_per_mwh(demand, renewables, YEAR)
        must_run_only = gci.emissions_rate_t_per_mwh(demand, demand, YEAR)
        assert must_run_only == pytest.approx(expected / demand), (
            f"the block's own tonnage moved at demand={demand:,.0f}"
        )
        assert rate > 0.0
    # And the two names still decompose the constant they were derived from.
    assert gci.MUST_RUN_BIOMASS_MW + gci.MUST_RUN_ZERO_CARBON_MW == pytest.approx(
        merit.MUST_RUN_FLOOR_MW
    )
    assert gci.MUST_RUN_ZERO_CARBON_MW == pytest.approx(5_600.0)


def test_the_MEASURED_series_is_multiplied_by_no_emission_factor_at_all():
    """The boundary claim, made arithmetically rather than in prose.

    Nuclear and hydro may cross at half-hourly grain BECAUSE they carry no carbon: what crosses
    changes the residual the merit order serves, never the merit order's answer. If this series
    ever picked up a factor, that argument would be void and the reconstruction would be reading
    NESO's arithmetic. So: in the ordinary regime the must-run tonnage must be EXACTLY the
    modelled biomass block, whatever the measured series says.

    MUTATION (must fire): price the handed-over MW at any non-zero factor -- e.g. restore
    `must_run_mw * MUST_RUN_EMISSIONS_RATE_T_PER_MWH` over the widened block.
    """
    # ISOLATE THE MUST-RUN TERM. Renewables cover the whole of demand, so the residual is
    # negative, no thermal plant runs and no floor is given: every gram returned is the must-run
    # block's own. Whatever the measured series says, that tonnage must be the BIOMASS block and
    # nothing else -- 2,400 MW at 120 gCO2/kWh -- because the measured half of the block is
    # multiplied by NESO's published factor for it, which is zero.
    demand = 40_000.0
    isolated = {
        mw: gci.emissions_rate_t_per_mwh(demand, demand, YEAR, zero_carbon_must_run_mw=mw)
        for mw in (1_000.0, 3_950.0, 5_600.0, 9_800.0)
    }
    expected = gci.MUST_RUN_BIOMASS_MW * gci.BIOMASS_G_CO2_PER_KWH / 1000.0 / demand
    for mw, rate in isolated.items():
        assert rate == pytest.approx(expected), (
            f"{mw:,.0f} MW of zero-carbon must-run changed the block's carbon; it must not"
        )
    # THE FIXTURE MUST BE ABLE TO SEE THE DEFECT, and the first version of this test could not:
    # priced at the old blended rate the whole block is 0.036 t/MWh, which at the FALLBACK 5,600
    # MW is arithmetically identical to 2,400 MW of biomass at 120 g. Only a measured value away
    # from 5,600 can tell them apart, so this asserts that the panel above contains some.
    assert [mw for mw in isolated if mw != gci.MUST_RUN_ZERO_CARBON_MW], (
        "every fixture sits at the fallback, where the correct and the mispriced arithmetic agree"
    )

    # And in a dispatching half hour, more measured baseload can only ever make it cleaner.
    ordered = [
        gci.emissions_rate_t_per_mwh(demand, 5_000.0, YEAR, zero_carbon_must_run_mw=mw)
        for mw in sorted(isolated)
    ]
    assert ordered == sorted(ordered, reverse=True), (
        "more zero-carbon must-run made a half hour DIRTIER, which is not a dispatch"
    )


def test_an_UNPUBLISHED_half_hour_falls_back_to_the_flat_BLOCK_and_never_to_zero():
    """`None` means "not published for this half hour", and it must not mean "no reactors ran".

    Read as zero, a gap in the feed hands the gas stack the entire residual and invents a dirty
    half hour out of nothing -- the fail-open shape the parse refuses one layer up, reintroduced
    at the point of use. The fallback is the flat 5,600 MW: the behaviour this whole series is
    correcting, which is bounded and already published.

    MUTATION (must fire): `(zero_carbon_must_run_by_period or {}).get(key, 0.0)` in `build_shape`,
    or default the parameter to `0.0` instead of `None`.
    """
    assert gci.emissions_rate_t_per_mwh(
        40_000.0, 5_000.0, YEAR, zero_carbon_must_run_mw=None
    ) == pytest.approx(gci.emissions_rate_t_per_mwh(40_000.0, 5_000.0, YEAR))
    assert gci.emissions_rate_t_per_mwh(
        40_000.0, 5_000.0, YEAR, zero_carbon_must_run_mw=0.0
    ) > gci.emissions_rate_t_per_mwh(40_000.0, 5_000.0, YEAR), (
        "this fixture cannot tell absent from zero, so it proves nothing"
    )

    d = {("2024-03-01", 1): 40_000.0, ("2024-03-01", 2): 40_000.0}
    r = {("2024-03-01", 1): 5_000.0, ("2024-03-01", 2): 5_000.0}
    # Period 2 is published at a real 2024 reading of 3,950 MW; period 1 is absent. Supplying
    # period 1 EXPLICITLY at the flat block must therefore change nothing at all, and supplying
    # it as zero must change it a great deal. That pair is what tells absent from zero -- the
    # shape alone cannot, which is the whole reason this test is written this way.
    partial = gci.build_shape(d, r, zero_carbon_must_run_by_period={("2024-03-01", 2): 3_950.0})
    explicit_flat = gci.build_shape(d, r, zero_carbon_must_run_by_period={
        ("2024-03-01", 1): gci.MUST_RUN_ZERO_CARBON_MW, ("2024-03-01", 2): 3_950.0,
    })
    assert partial == explicit_flat
    as_zero = gci.build_shape(d, r, zero_carbon_must_run_by_period={
        ("2024-03-01", 1): 0.0, ("2024-03-01", 2): 3_950.0,
    })
    assert as_zero != partial, "this fixture cannot tell the fallback from zero, so it proves nothing"
    # And the published half hour carries LESS baseload than the flat block it replaced (3,950 MW
    # against 5,600 MW), so it reads dirtier -- the flat block was too generous in 2024, which is
    # the level half of what this correction found.
    assert partial[("2024-03-01", 2)] > partial[("2024-03-01", 1)]
    assert gci.build_shape(d, r, zero_carbon_must_run_by_period={}) == gci.build_shape(d, r)


def test_a_MEASURED_block_larger_than_demand_cannot_manufacture_generation():
    """The same cap the flat block and the thermal floor already carry, on a series that now
    reaches 9,831 MW in the published outturn -- above some summer-night demands.

    Uncapped, the block would push total generation past demand and the rate would still be
    divided by demand, reporting an intensity for energy nobody consumed.

    MUTATION (must fire): drop the `min(demand_mw, must_run_capacity_mw)` cap.
    """
    rate = gci.emissions_rate_t_per_mwh(6_000.0, 0.0, YEAR, zero_carbon_must_run_mw=9_800.0)
    # Demand is 6 GW against a 12.2 GW block: biomass is served pro-rata, nothing else runs.
    served_fraction = 6_000.0 / (gci.MUST_RUN_BIOMASS_MW + 9_800.0)
    expected_tonnes = gci.MUST_RUN_BIOMASS_MW * served_fraction * gci.BIOMASS_G_CO2_PER_KWH / 1000.0
    assert rate == pytest.approx(expected_tonnes / 6_000.0)
    assert rate < gci.MUST_RUN_EMISSIONS_RATE_T_PER_MWH, (
        "a half hour drowned in zero-carbon baseload must read cleaner than the blended block"
    )


# --------------------------------------------------------------------------- #
# The DISPATCHED biomass fleet -- an envelope crossed, a schedule decided here #
# --------------------------------------------------------------------------- #
#
# The band these tests work in is chosen so the arithmetic is hand-checkable. When the residual
# left after the zero-carbon block sits INSIDE the envelope, biomass absorbs it exactly and the
# thermal stack dispatches nothing -- so the whole rate is the biomass term and a wrong dispatch
# cannot hide behind a gas number that moved to compensate.

ENVELOPE_FLOOR_MW = 900.0      # the 2024 fortnight's demonstrated minimum
ENVELOPE_CAPACITY_MW = 3_180.0  # and its demonstrated maximum


def biomass_only_rate(demand: float, renewables: float, *, zero_carbon: float,
                      floor: float | None = None, capacity: float | None = None) -> float:
    return gci.emissions_rate_t_per_mwh(
        demand, renewables, YEAR,
        zero_carbon_must_run_mw=zero_carbon,
        biomass_floor_mw=floor,
        biomass_capacity_mw=capacity,
    )


def test_the_DEFAULTED_envelope_reproduces_the_FLAT_2400_MW_FLEET_EXACTLY():
    """The enabling refactor must change no number until an envelope is supplied.

    This is what makes the before/after measurement mean anything: the two arms differ by ONE
    input and not by an arithmetic rewrite that travelled with it. It is asserted twice over --
    defaulted, and handed a DELIBERATELY FLAT envelope -- because those are two different code
    paths through the clamp and only the second proves the clamp itself collapses to the
    constant it replaced.

    MUTATION (must fire): default `biomass_floor_mw` to 0 instead of to the capacity, which is
    the natural-looking choice and lets the fleet switch off in every quiet half hour.
    """
    for demand, renewables in [
        (45_000.0, 2_000.0),     # still winter evening, above the CCGT band
        (30_000.0, 12_000.0),    # ordinary, inside the band
        (22_000.0, 18_000.0),    # quiet, nothing left to dispatch
        (6_000.0, 1_000.0),      # demand BELOW the block, so it is scaled down
        (20_000.0, 20_000.0),    # renewables meet the lot; the block still runs
    ]:
        for zero_carbon in (None, 5_600.0, 9_800.0, 700.0):
            base = gci.emissions_rate_t_per_mwh(
                demand, renewables, YEAR, zero_carbon_must_run_mw=zero_carbon
            )
            flat = gci.emissions_rate_t_per_mwh(
                demand, renewables, YEAR, zero_carbon_must_run_mw=zero_carbon,
                biomass_capacity_mw=gci.MUST_RUN_BIOMASS_MW,
                biomass_floor_mw=gci.MUST_RUN_BIOMASS_MW,
            )
            assert flat == base, (
                f"a flat envelope moved the rate at demand={demand:,.0f} zc={zero_carbon}: "
                "the clamp does not collapse to the constant it replaced, so no measurement "
                "against this baseline isolates the dispatch"
            )


def test_the_fleet_RAMPS_with_the_residual_and_never_leaves_its_ENVELOPE():
    """The dispatch decision this module owns, checked at all three regimes of the clamp.

    Inside the band the biomass term IS the residual left after the zero-carbon block, which is
    what a CfD-supported plant does: it takes what the residual offers up to its capacity. Below
    the band it holds at its demonstrated minimum; above it, it saturates and gas takes the rest.

    MUTATION (must fire): drop either end of the clamp, or dispatch biomass from the year's
    `mean_mw` instead of from the residual -- the flattering choice, because a mean fits the
    published series better than either honest end.
    """
    demand, zero_carbon = 20_000.0, 5_600.0
    rate_of = lambda mw: mw * gci.BIOMASS_G_CO2_PER_KWH / 1000.0 / demand  # noqa: E731

    # BELOW the band: the residual cannot fill the floor, and the fleet holds at it.
    floored = biomass_only_rate(demand, 14_000.0, zero_carbon=zero_carbon,
                                floor=ENVELOPE_FLOOR_MW, capacity=ENVELOPE_CAPACITY_MW)
    assert floored == pytest.approx(rate_of(ENVELOPE_FLOOR_MW))

    # INSIDE the band: biomass absorbs the residual exactly and nothing thermal runs.
    for renewables, expected_mw in [(13_000.0, 1_400.0), (12_000.0, 2_400.0)]:
        inside = biomass_only_rate(demand, renewables, zero_carbon=zero_carbon,
                                   floor=ENVELOPE_FLOOR_MW, capacity=ENVELOPE_CAPACITY_MW)
        assert inside == pytest.approx(rate_of(expected_mw)), (
            f"the fleet did not follow the residual at renewables={renewables:,.0f}"
        )

    # ABOVE the band: it saturates at the demonstrated maximum and the gas stack takes the rest,
    # so the rate must EXCEED the pure-biomass rate rather than continuing to track the residual.
    above = biomass_only_rate(demand, 11_000.0, zero_carbon=zero_carbon,
                              floor=ENVELOPE_FLOOR_MW, capacity=ENVELOPE_CAPACITY_MW)
    # THE COMPARISON IS AGAINST THE UNCAPPED FLEET, NOT AGAINST THE CAPACITY, and the first
    # version of this line got that wrong: `above > rate_of(capacity)` is satisfied by a fleet
    # that simply kept growing past its maximum, so the mutation that removes the upper clamp
    # SURVIVED it. The residual left after saturation is 3,400 MW; served as biomass it would
    # cost 120 g, and it must instead cost the gas stack's several hundred.
    uncapped_mw = demand - 11_000.0 - zero_carbon
    assert above > rate_of(uncapped_mw), (
        "past the demonstrated maximum the fleet must saturate and the REMAINDER must be served "
        "by gas at several times biomass's factor -- a rate at or below the uncapped fleet's "
        "means the clamp let biomass grow past what GB's plant was ever observed to produce"
    )

    # And the ramp is MONOTONE across the whole range, which no single point above can show.
    rates = [
        biomass_only_rate(demand, renewables, zero_carbon=zero_carbon,
                          floor=ENVELOPE_FLOOR_MW, capacity=ENVELOPE_CAPACITY_MW)
        for renewables in range(14_500, 10_000, -250)
    ]
    assert rates == sorted(rates), "the rate must rise monotonically as the residual grows"


def test_a_QUIET_half_hour_backs_the_fleet_DOWN_TO_ITS_FLOOR_AND_NEVER_TO_ZERO():
    """The fail-open this envelope was given a bottom end to prevent.

    A fleet modelled between zero and its maximum switches off exactly when renewables meet
    demand -- and biomass is the ONLY carbon-carrying term in the must-run block, so switching
    it off makes the half hour read as a perfectly clean grid. That is the same defect the
    thermal floor was built to remove one fuel over, at the one fuel where it does most damage,
    because a perfectly clean half hour is precisely what a time-shifting recommendation points
    a customer at.

    MUTATION (must fire): clamp the fleet to `[0, capacity]` instead of `[floor, capacity]`.
    """
    demand = 20_000.0
    at_floor = biomass_only_rate(demand, demand, zero_carbon=5_600.0,
                                 floor=ENVELOPE_FLOOR_MW, capacity=ENVELOPE_CAPACITY_MW)
    assert at_floor == pytest.approx(
        ENVELOPE_FLOOR_MW * gci.BIOMASS_G_CO2_PER_KWH / 1000.0 / demand
    )
    assert at_floor > 0.0, (
        "a half hour whose renewables met the whole of demand still burns wood; a zero here is "
        "the fabricated perfectly-clean grid this module exists to refuse"
    )


def test_ONLY_the_two_ENDS_of_the_envelope_reach_the_dispatch():
    """R15 INDEPENDENCE, and the control that keeps the boundary claim checkable.

    The envelope record carries `mean_mw`, `p1_mw`, `p99_mw` and `half_hours` beside the two
    ends. None of them may reach a half hour: `mean_mw` in particular is a summary of WHEN the
    fleet ran, it would fit the published series better than either honest end, and consuming it
    would make this a reading of biomass outturn wearing the word "envelope".

    Asserted by CONSEQUENCE rather than by inspection -- perturb each field and see whether the
    published shape moves -- because a grep for the field name cannot tell a use from a mention.

    MUTATION (must fire): pass the whole record down to `emissions_rate_t_per_mwh`, or dispatch
    from `mean_mw`.
    """
    # THE FIXTURE HAS TO SPAN BOTH ENDS OF THE CLAMP, and the first version of it did not: with
    # renewables never above 15 GW the residual always cleared the floor, `floor_mw` was never
    # the binding end, and the control below reported that the floor "did not reach the
    # dispatch" -- a finding about the fixture, not about the code. Renewables run from 5 GW
    # (capacity binds) to 19.5 GW (floor binds) so both ends are exercised.
    demand = {("2024-03-01", p): 20_000.0 for p in range(1, 40)}
    renewables = {key: 5_000.0 + 375.0 * key[1] for key in demand}
    envelope = {
        2024: {"capacity_mw": ENVELOPE_CAPACITY_MW, "floor_mw": ENVELOPE_FLOOR_MW,
               "p1_mw": 950.0, "p99_mw": 3_100.0, "mean_mw": 2_455.0, "half_hours": 17_568.0},
    }
    baseline = gci.build_shape(demand, renewables, biomass_envelope_by_year=envelope)

    for field, moved in [("p1_mw", 2_900.0), ("p99_mw", 1_000.0),
                         ("mean_mw", 400.0), ("half_hours", 3.0)]:
        perturbed = {2024: {**envelope[2024], field: moved}}
        assert gci.build_shape(
            demand, renewables, biomass_envelope_by_year=perturbed
        ) == baseline, f"`{field}` reached the dispatch; it is a diagnostic, not an input"

    for field, moved in [("capacity_mw", 1_500.0), ("floor_mw", 100.0)]:
        perturbed = {2024: {**envelope[2024], field: moved}}
        assert gci.build_shape(
            demand, renewables, biomass_envelope_by_year=perturbed
        ) != baseline, f"`{field}` did NOT reach the dispatch, so this test proves nothing"


def test_a_year_with_NO_envelope_falls_back_to_the_FLAT_BLOCK_and_never_to_zero_biomass():
    """The mirror of the must-run fallback, and the same fail-open it refuses.

    A `.get(year, 0.0)` default would say "the fleet generated nothing that year", which the
    dispatch answers by reading every quiet half hour as clean -- worse than the flat block it
    replaced rather than better.

    MUTATION (must fire): default the missing year to a zero-width envelope at zero.
    """
    demand = {("2019-03-01", p): 25_000.0 for p in range(1, 20)}
    renewables = {key: 24_000.0 for key in demand}
    only_2024 = {2024: {"capacity_mw": ENVELOPE_CAPACITY_MW, "floor_mw": ENVELOPE_FLOOR_MW,
                        "p1_mw": 950.0, "p99_mw": 3_100.0, "mean_mw": 2_455.0,
                        "half_hours": 17_568.0}}
    assert gci.build_shape(
        demand, renewables, biomass_envelope_by_year=only_2024
    ) == gci.build_shape(demand, renewables)
    assert gci.build_shape(demand, renewables, biomass_envelope_by_year={}) == gci.build_shape(
        demand, renewables
    )
    # And the fallback is the FLAT FLEET, not an absent one: the rate is still positive in a
    # half hour whose renewables met almost all of demand.
    assert gci.emissions_rate_t_per_mwh(25_000.0, 25_000.0, 2019) > 0.0


def test_a_DISPATCHED_fleet_larger_than_demand_cannot_manufacture_generation():
    """The same cap the flat block and the thermal floor already carry, on a term that now
    moves -- and the pro-rata scaling has to follow the DISPATCHED fleet, not the constant.

    MUTATION (must fire): scale the served share by `MUST_RUN_BIOMASS_MW` instead of by the
    fleet this half hour actually dispatched.
    """
    demand = 6_000.0
    rate = biomass_only_rate(demand, 0.0, zero_carbon=9_800.0,
                             floor=ENVELOPE_FLOOR_MW, capacity=ENVELOPE_CAPACITY_MW)
    # Residual 6,000 minus a 9,800 MW zero-carbon block is negative, so biomass holds at its
    # floor and the block is 10,700 MW against 6,000 MW of demand.
    served_fraction = demand / (ENVELOPE_FLOOR_MW + 9_800.0)
    expected = ENVELOPE_FLOOR_MW * served_fraction * gci.BIOMASS_G_CO2_PER_KWH / 1000.0
    assert rate == pytest.approx(expected / demand)
