"""The half-hourly SHAPE of GB grid carbon intensity — the timing half of the mission's number.

REUSE: sim/grid_carbon_intensity.py
CLASS: CUSTOM
INDEX: searched "carbon", "intensity", "emission", "grid", "fuel mix", "gCO2", "footprint",
       "half-hourly". Five organs came back and every one of them is a different quantity:
       `company/regulatory/carbon_emissions.py` owns the ONE ANNUAL series (and must keep
       owning it — `tools/grid_intensity_guard.py` fails a second one); `company/billing/
       carbon_footprint.py` is that annual number applied to an EAC; `company/sustainability/
       carbon_intensity_register.py` is the statutory Fuel Mix Disclosure; `company/carbon/
       carbon_ledger.py` is the SAVED/SPENT/NET event ledger this eventually feeds; and
       `sim/merit_order_reconstruction.py` is the dispatch model, whose stack and emission
       factors are IMPORTED here rather than restated. What none of them has is a number that
       moves within the day, which is the only thing that makes time-shifting measurable.

WHY THIS EXISTS
---------------
The company's whole thesis is that you abate carbon by changing WHEN a household draws power.
Nothing in the tree could express that. Every carbon figure rested on ONE ANNUAL NUMBER, and an
annual number is blind to timing by construction: move a household's entire load from 4pm to
4am and its carbon does not change by a gram.

The advisor's scope brief of 2026-08-04 puts it first on the disqualification battery — "1. A
single annual emissions factor rather than half-hourly intensity" — and names the reason the
asymmetry matters: *"electricity carbon varies by a factor of several through a day, gas carbon
does not. Time-shifting only pays in electricity."*

WHAT THIS PRODUCES, AND WHAT IT DELIBERATELY DOES NOT
------------------------------------------------------
A DIMENSIONLESS SHAPE: the emissions rate of each half hour relative to the year's
demand-weighted average, which is 1.0 by construction. Not grams. Never grams.

That split is the design, not a shortcut. There is exactly ONE annual grid-intensity series in
this codebase and `company/regulatory/carbon_emissions.py` owns it — a rule with a control
behind it, written after three series in this tree disagreed by up to 55.6% and nothing could
observe that they did. A second absolute series here would be the fourth. So:

    the WORLD owns the SHAPE     — timing physics, from real half-hourly outturn
    the COMPANY owns the LEVEL   — its own published annual reading, single-owner
    the product is the company's ESTIMATE of half-hourly intensity

Which is also the epistemically honest arrangement. A GB supplier that does not buy the NESO
Carbon Intensity feed does exactly this: it takes the published national shape and scales it by
the intensity it reports. The number it gets is a BELIEF, and this codebase has a wall to keep
beliefs distinguishable from truth.

HOW THE SHAPE IS DERIVED
-------------------------
From residual demand, which is real published data, through the dispatch stack, which is
already built and graded:

    residual = national demand outturn - (wind + solar) outturn          [Elexon, half-hourly]
    below the must-run floor          -> near-zero-carbon plant, price-taking
    the CCGT band                     -> gas, at the efficiency actually dispatched
    above it                          -> peakers, at OCGT efficiency

Emissions per half hour are the SUM over what was dispatched. That distinction is the one place
this could quietly have been wrong: `reconstruct_price_gbp_per_mwh` returns the SRMC of the
MARGINAL unit, because price is set by the last plant dispatched — but emissions are set by
ALL of them, and the average dispatched efficiency across a partly-loaded CCGT band is not the
marginal unit's efficiency. Using the marginal figure would have overstated the swing between
quiet and busy half hours, i.e. flattered the very effect this module exists to measure.

Gas emissions per electrical MWh are `EF_GAS_TCO2_PER_MWH_TH / efficiency` — the DESNZ
fuel-input factor over the efficiency of the unit actually running. That is a second,
independently-sourced route to a number DUKES also publishes directly, and the two agree to
within 2.2% in every year 2016-2024. `test_the_two_published_routes_to_a_gas_emission_factor_agree`
pins it, because an agreement nobody checks is a coincidence.

NAMED GAPS — the shape's error bars, stated because a measure that hides them invites false
confidence (R10: named, never fabricated):

  * NO COAL IS DISPATCHED. `merit_order_reconstruction` carries coal for ORDERING only, at zero
    capacity. Coal ran ~9% of GB generation in 2016 at roughly twice CCGT's emissions rate and
    was gone by Sep 2024. So the shape UNDERSTATES the dirty end of coal-heavy years, and the
    understatement shrinks to nothing across the window. Direction known, size not.
  * THE MUST-RUN FLOOR IS A CONSTANT 8 GW. Nuclear outages, hydro seasonality and biomass
    dispatch all move it and none of them is modelled.
  * INTERCONNECTOR IMPORTS ARE NOT MODELLED. NESO's published series counts them; this does
    not, so hours of heavy French nuclear import read dirtier here than they were.
  * NATIONAL ONLY. NESO also publishes 14 regional series, and those are MODELLED from a
    reduced network model rather than measured. This module makes no regional claim at all,
    which is the honest version of not having one.
  * OUTTURN, NOT FORECAST. The brief is explicit that the two answer different questions:
    forecast is what a customer could have acted on, outturn is what actually happened. This is
    outturn, so it grades what DID happen and must never be used to judge shifting advice.
  * NO LOSS CORRECTION IS APPLIED, and none must be added downstream either. The denominator is
    Elexon's transmission-boundary demand outturn, so this is per kWh at that boundary; NESO's
    published series is separately loss-corrected to a consumed basis. Applying a second
    correction on top is item 2 of the disqualification battery.

WHICH WAY THE ERRORS POINT, and this is the sentence to read if you read only one. The two
largest gaps -- no coal and no interconnector imports -- both make the CLEAN end of the shape
cleaner than GB actually was. So ANY BENEFIT COMPUTED FROM MOVING LOAD INTO CLEAN HALF HOURS IS
AN UPPER BOUND on the real one. That is the error direction that matters here, because it
flatters the mission's own thesis, and it must be carried on the face of anything published from
this rather than left in a module nobody opens.

HOW BIG THE GAP ACTUALLY IS. Until 2026-08-25 the paragraph above continued "measured over
2016-2025 this shape's quietest half hours sit around 0.05 of average against NESO's published
series bottoming out nearer 0.16". THAT COMPARISON HAD NEVER BEEN RUN. No NESO series existed in
this tree and no fetch had ever happened -- it was a recollection written in the grammar of a
measurement, in the one docstring whose job is to say which way the errors point.
`sim/neso_carbon_intensity.py` now fetches the published series and `compare_shapes` measures it,
both shapes re-normalised over the half hours they share (2019-2024; NESO publishes from
2018-05-11):

    year      half hours   ours min   NESO min   ours max   NESO max   ours/NESO spread   corr
    2019         16,923      0.057      0.217      1.707      2.019     29.8x /  9.3x     0.85
    2020         16,492      0.055      0.244      1.942      1.965     35.3x /  8.1x     0.82
    2021         16,646      0.056      0.195      1.792      1.769     31.9x /  9.1x     0.90
    2022         14,929      0.070      0.211      2.043      1.741     29.3x /  8.3x     0.82
    2023         17,362      0.058      0.165      1.896      1.958     32.4x / 11.9x     0.77
    2024         17,492      0.059      0.105      1.981      2.279     33.8x / 21.6x     0.68

Three corrections to what the old sentence claimed, and one thing it never mentioned at all:

  * OUR CLEAN END, ~0.059, was stated correctly.
  * NESO'S FLOOR IS NOT 0.16. Over these six years it averages 0.189 and only 2024 falls below
    0.16. The old sentence understated the gap it was warning about: our quietest half hours are
    not 3x too clean but closer to 3.2x, and in 2019-2022 nearer 3.5x.
  * THE DIRTY END "lands in roughly the right place" HELD UP -- 1.71-2.04 against 1.74-2.28.
  * THE SPREAD WAS NEVER STATED AND IS THE HEADLINE. This shape swings 32x from its cleanest to
    its dirtiest half hour; NESO's swings 11.4x. We overstate the total range timing can move by
    about 2.8x. Any abatement number computed from this shape inherits that factor.

And one finding that is about GB rather than about us: NESO'S OWN FLOOR FALLS AND ITS OWN SPREAD
WIDENS across the window (0.217 -> 0.105, 9.3x -> 21.6x). That is real decarbonisation -- as
renewables grow the clean end genuinely gets cleaner -- so the two series are converging on the
spread axis for a reason that has nothing to do with this model improving. Correlation moving
0.85 -> 0.68 over the same years says the opposite about the timing detail, and both facts have
to be carried together.

R15 note on that measurement: the first run against the real feed raised ZeroDivisionError, not
a number. NESO publishes `actual: 0` for five half hours over the window, four consecutive on
2023-06-07, against a lowest genuine reading of 14 gCO2/kWh -- a feed outage, not a clean grid.
The adapter now drops them as absent. Had that guard sat one line later the run would have
reported the cleanest possible grid as fact instead of failing loudly.

R13: nothing here is fitted. The shape is real outturn through a dispatch model built from
published GB engineering figures, and no constant in it was chosen by looking at what came out.
The proof that it was not is that the clean end DISAGREES with the published series and has
been left disagreeing, with the direction named, rather than scaled until it matched.
"""
from __future__ import annotations

from collections.abc import Iterable, Mapping

from sim.merit_order_reconstruction import (
    CCGT_CAPACITY_MW,
    EF_GAS_TCO2_PER_MWH_TH,
    MUST_RUN_FLOOR_MW,
    OCGT_REFERENCE_EFFICIENCY,
    TOTAL_DISPATCHABLE_MW,
    _ccgt_efficiency_band,
    _year_of,
)

#: What the numbers below are, in one line, for anything that publishes them (R14 applied to a
#: basis rather than to a clock). Every consumer is expected to carry this forward verbatim.
SHAPE_BASIS = (
    "dimensionless; the half hour's emissions rate relative to the calendar year's "
    "DEMAND-WEIGHTED mean, which is 1.0 by construction. National, generation-based, outturn, "
    "no loss correction, no coal dispatch, no interconnector imports."
)

#: Biomass, gCO2/kWh, on NESO's own Carbon Intensity methodology -- the same methodology whose
#: published series this shape stands in for. Zero would be the convenient choice and it is the
#: one number here that must not be zero: a must-run floor asserted at exactly zero makes every
#: very quiet half hour read as a perfectly clean grid, which is the shape a fabricated number
#: takes and would inflate the value of time-shifting without bound.
BIOMASS_G_CO2_PER_KWH = 120.0

#: Share of the 8 GW must-run floor that is biomass rather than nuclear or hydro. A STATED
#: SIMPLIFICATION from GB fleet capacities of the order nuclear ~5 GW, biomass ~2.5 GW, hydro
#: ~0.5 GW -- round structural scales, in the same spirit (and with the same honesty) as the
#: floor itself, which `merit_order_reconstruction` already declares a stated simplification.
MUST_RUN_BIOMASS_SHARE = 0.30

#: DERIVED, never a literal, so a caller can always decompose the number it was given -- the
#: rule `carbon_emissions.grid_intensity_g_co2e_per_kwh` already keeps on the annual side.
MUST_RUN_EMISSIONS_RATE_T_PER_MWH = MUST_RUN_BIOMASS_SHARE * BIOMASS_G_CO2_PER_KWH / 1000.0


class ShapeUnavailable(Exception):
    """The shape could not be built. Never a silently flat series.

    A flat shape is the one failure this module must not have: it is exactly the annual-only
    number it exists to replace, and it would read as "timing does not matter here" rather
    than as "this did not run" (R15 fail-silent).
    """


def emissions_rate_t_per_mwh(demand_mw: float, renewable_generation_mw: float, year: int) -> float:
    """Tonnes CO2 per MWh of demand met, in ONE half hour, on the dispatch above.

    ABSOLUTE and therefore NOT for publication — it exists so the shape has something to be a
    ratio of, and so a test can check the shape against a hand-computed dispatch. The published
    quantity is the dimensionless shape; see the module docstring for why there is no second
    absolute grid-intensity series in this repository.
    """
    y = _year_of(int(year))
    worst_eff, best_eff = _ccgt_efficiency_band(y)
    demand_mw = float(demand_mw)
    if demand_mw <= 0.0:
        raise ShapeUnavailable("a half hour with no demand has no emissions rate")

    residual_mw = demand_mw - float(renewable_generation_mw)
    # MUST-RUN MEANS MUST RUN, and getting this wrong put a hard zero in the series. Written
    # first as `min(max(residual, 0), floor)`, it made the floor the RESIDUAL's leftovers -- so
    # in every half hour where wind and solar exceeded national demand the model switched
    # nuclear off, emissions came out at exactly 0.000, and the shape reported a perfectly clean
    # grid several hundred times a year. GB does not do that: when renewables and must-run
    # together exceed demand it is WIND that is constrained off, and the nuclear fleet keeps
    # running because it cannot economically do anything else. So the floor is taken against
    # DEMAND, and the renewable surplus is curtailed rather than the baseload.
    must_run_mw = min(demand_mw, MUST_RUN_FLOOR_MW)
    thermal_mw = max(0.0, residual_mw - MUST_RUN_FLOOR_MW)

    ccgt_mw = min(thermal_mw, CCGT_CAPACITY_MW)
    peaker_mw = max(0.0, thermal_mw - CCGT_CAPACITY_MW)
    peaker_mw = min(peaker_mw, max(0.0, TOTAL_DISPATCHABLE_MW - MUST_RUN_FLOOR_MW - CCGT_CAPACITY_MW))

    # THE AVERAGE OF WHAT RAN, NOT THE LAST UNIT TO RUN. Efficiency slides best -> worst across
    # the band, so a band loaded to fraction f has run everything from `best` down to
    # `best - (best-worst)*f`; its MEAN is the midpoint of that ramp. Taking the marginal unit
    # instead would overstate the gap between quiet and busy half hours -- flattering exactly
    # the effect this module was written to measure, which is the direction to be most careful
    # about.
    load_fraction = (ccgt_mw / CCGT_CAPACITY_MW) if CCGT_CAPACITY_MW > 0 else 0.0
    mean_dispatched_eff = best_eff - (best_eff - worst_eff) * load_fraction / 2.0

    tonnes = (
        must_run_mw * MUST_RUN_EMISSIONS_RATE_T_PER_MWH
        + ccgt_mw * (EF_GAS_TCO2_PER_MWH_TH / mean_dispatched_eff)
        + peaker_mw * (EF_GAS_TCO2_PER_MWH_TH / OCGT_REFERENCE_EFFICIENCY)
    )
    return tonnes / demand_mw


def build_shape(
    demand_by_period: Mapping[tuple[str, int], float],
    renewables_by_period: Mapping[tuple[str, int], float],
) -> dict[tuple[str, int], float]:
    """{(settlement date, period): shape}, normalised per CALENDAR YEAR to a demand-weighted
    mean of exactly 1.0.

    DEMAND-WEIGHTED, and the weighting is the whole meaning of the anchor. A consumer multiplies
    this by its own published ANNUAL intensity, so the arithmetic has to be such that a
    household drawing in the national shape gets the published annual number back, unchanged --
    and only a household that draws at different times gets a different answer. An unweighted
    mean would have quietly re-levelled every consumer's annual total, which is a change to a
    published figure disguised as a units convention.

    Periods present in one mapping and not the other are skipped rather than defaulted: a
    missing renewable outturn is not zero renewables, and treating it as zero would invent a
    dirty half hour out of a gap in the feed (R15 fail-open).
    """
    rates: dict[tuple[str, int], float] = {}
    demands: dict[tuple[str, int], float] = {}
    for key, demand_mw in demand_by_period.items():
        renewable_mw = renewables_by_period.get(key)
        if renewable_mw is None or not demand_mw or float(demand_mw) <= 0.0:
            continue
        try:
            rates[key] = emissions_rate_t_per_mwh(float(demand_mw), float(renewable_mw), int(key[0][:4]))
        except (ShapeUnavailable, ValueError, KeyError):
            continue
        demands[key] = float(demand_mw)

    if not rates:
        raise ShapeUnavailable(
            "no half hour had BOTH a demand outturn and a renewable outturn, so there is no "
            "shape. This is an absence, not a flat series."
        )

    totals: dict[str, list[float]] = {}
    for key, rate in rates.items():
        year = key[0][:4]
        acc = totals.setdefault(year, [0.0, 0.0])
        acc[0] += rate * demands[key]
        acc[1] += demands[key]

    shape: dict[tuple[str, int], float] = {}
    for key, rate in rates.items():
        weighted_sum, weight = totals[key[0][:4]]
        if weight <= 0.0:
            continue
        mean_rate = weighted_sum / weight
        if mean_rate <= 0.0:
            continue
        shape[key] = rate / mean_rate
    if not shape:
        raise ShapeUnavailable("every year's demand-weighted mean emissions rate was zero")
    return shape


def demand_weighted_mean(
    shape: Mapping[tuple[str, int], float],
    demand_by_period: Mapping[tuple[str, int], float],
    year: str,
) -> float:
    """The year's demand-weighted mean of `shape`. 1.0 when the normalisation held.

    Exists so the normalisation is checkable by a caller and not only by this module's own
    tests -- the anchor's correctness is what stops the company's published annual total from
    moving when timing is introduced, and that is a claim worth being able to re-derive.
    """
    num = den = 0.0
    for key, value in shape.items():
        if key[0][:4] != year:
            continue
        weight = float(demand_by_period.get(key) or 0.0)
        num += value * weight
        den += weight
    if den <= 0.0:
        raise ShapeUnavailable(f"no demand-weighted half hours in {year}")
    return num / den


def spread(shape: Mapping[tuple[str, int], float], year: str) -> tuple[float, float]:
    """(min, max) of the year's shape — how much timing can possibly be worth.

    Published beside any figure derived from the shape, because it bounds the claim: if the
    cleanest and dirtiest half hours of a year differ by 1.6x, then no amount of shifting can
    change a household's carbon by more than that, and a claim that it did is refuted by this
    pair alone without anyone re-running anything.
    """
    values = [v for k, v in shape.items() if k[0][:4] == year]
    if not values:
        raise ShapeUnavailable(f"no shape values in {year}")
    return min(values), max(values)


def aggregate_demand(records: Iterable[Mapping]) -> dict[tuple[str, int], float]:
    """Elexon demand-outturn records -> {(date, period): MW}, keeping the LAST record for a
    period. INDO is revised, and a revision is the better number."""
    out: dict[tuple[str, int], float] = {}
    for record in records:
        date_str = record.get("settlementDate")
        period = record.get("settlementPeriod")
        value = record.get("initialDemandOutturn")
        if date_str is None or period is None or value is None:
            continue
        out[(str(date_str), int(period))] = float(value)
    return out
