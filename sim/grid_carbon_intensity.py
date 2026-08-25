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

    residual = national demand outturn - (wind + solar) outturn - net imports   [Elexon, HH]
    below the must-run floor          -> near-zero-carbon plant, price-taking
    the CCGT band                     -> gas, at the efficiency actually dispatched
    the coal band above it            -> coal, at the DUKES 5.14 electrical factor
    above that                        -> peakers, at OCGT efficiency

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
confidence (R10: named, never fabricated). The first two on this list were CLOSED on 2026-08-25
and are kept here, rewritten, because what replaced them is a smaller gap and not no gap:

  * COAL IS NOW DISPATCHED, from the fleet's DEMONSTRATED annual maximum measured out of
    Elexon's published FUELHH outturn (14,724 MW in 2016 falling to 1,873 MW in 2024 and 110 MW
    in 2025 — the fleet closes itself in the data, with no hand-written end date to be wrong
    about). REMAINING GAP: its position in merit is FIXED above the CCGT band rather than
    recomputed per half hour from the gas/coal spread, because this function takes no fuel
    prices. That ordering is DUKES 5.10.B's own outcome — coal load factors of 8-21% against
    CCGT's three to four times that — and where it is wrong (the 2021-22 gas spike, when coal
    genuinely went below gas in merit) it UNDERSTATES coal, erring back toward the no-coal
    behaviour rather than past it.
  * INTERCONNECTOR IMPORTS ARE NOW MODELLED, at NESO's OWN published per-cable factors, from
    the same FUELHH outturn. REMAINING GAP, AND IT IS GROWING: two of GB's nine cables postdate
    NESO's published factor table — North Sea Link (Norway, Oct 2021) and Viking Link (Denmark,
    Dec 2023) — so their flow is still dispatched as GB gas. That is 0% of imported MWh in
    2019-2020, 5% in 2021, 28% in 2022, 27% in 2023 and 34% in 2024. Inventing factors for them
    is the fabricated constant R10 forbids; the honest handling is to publish the share, which
    `elexon_fuel_outturn.import_coverage` measures and the feed carries.
  * THE MUST-RUN FLOOR IS A CONSTANT 8 GW. Nuclear outages, hydro seasonality and biomass
    dispatch all move it and none of them is modelled.
  * THE THERMAL STACK NO LONGER REACHES ZERO, and this gap is kept, rewritten, because what
    replaced it is a smaller gap and not no gap. It is floored at the CCGT+OCGT fleet's
    DEMONSTRATED ANNUAL MINIMUM, measured out of Elexon's published FUELHH outturn the same way
    the coal capacity is (1,835 MW in 2016 falling to 303 MW in 2024). REMAINING GAP: that floor
    is the year's SINGLE LOWEST reading, and the 1st percentile of the same year is far higher —
    1,720 MW against 303 MW in 2024. The conservative number is used deliberately (see
    `elexon_fuel_outturn.thermal_floor_by_year` for why the robust statistic is also the
    flattering one here), so quiet half hours still run less gas than GB actually ran.
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

WHICH WAY THE ERRORS POINT, and this is the sentence to read if you read only one. THE RANGE IS
STILL OVERSTATED — p95/p5 runs about 1.36x the published series' — so ANY BENEFIT COMPUTED FROM
MOVING LOAD BETWEEN QUIET AND BUSY HALF HOURS IS AN UPPER BOUND on the real one. That is the
error direction that matters here, because it flatters the mission's own thesis, and it must be
carried on the face of anything published from this rather than left in a module nobody opens.

AND THAT 1.36x IS A BLEND OF TWO AXES THAT POINT OPPOSITE WAYS (2026-08-25). Split day by day by
`neso_carbon_intensity.compare_shapes`, this shape's BETWEEN-day swing matches the published
series to within 7% in every year 2019-2024 (0.93-1.00x, mean 0.96) and its WITHIN-day swing is
too wide in every one of them (1.41-1.58x, mean 1.48). The aggregate figure averages a term this
model gets RIGHT with a term it gets WRONG — and the wrong one is the only axis a customer can
act on, because a household can move the washing from 6pm to 2am and cannot move it to a windier
Tuesday in March. So the annual correction UNDERSTATES what an intra-day shifting claim needs.
Nothing here was tuned to that: the split is a measurement and R12 forbids moving a constant to
change it.

WHAT THAT RE-DIAGNOSED, and it is the reason the level did not move. The thermal floor closed a
LEVEL error at the clean end and left CORRELATION untouched at 0.726 in 2024 — the model knows
how clean a quiet half hour is and still does not know WHICH half hours were the quiet ones. The
decomposition says where that lives: the day MEANS track well (day-mean correlation 0.761 in
2024, 0.931 in 2019), the within-day ordering does not. Measured against the candidates in the
gap list above, the error correlates with RENEWABLE SHARE (-0.49 in 2024) far more than with
anything else, and the deeper reading is structural rather than a missing correction: this
shape's own correlation with renewable share is -0.84 where the published series' is only -0.53,
and that divergence has widened every year since 2019. A dispatch model handed demand, wind and
solar can only be a function of residual demand; GB's actual intensity increasingly is not.

WHAT IS NO LONGER TRUE, and it changed on 2026-08-25 when the thermal floor was measured: the
CLEAN END is no longer uniformly optimistic. It used to sit ~3.2x too clean in every year. It is
now MIXED — still slightly cleaner than published in 2019, 2022 and 2023, and DIRTIER than
published in 2020 and 2021. A single-direction sentence about the clean end would now be
contradicted by this module's own measurement in two years out of six, so it is not made.

The REASON is not one story, and an earlier version of this paragraph got it wrong by insisting
that it was. Coal's omission was a DIRTY-end error; the cables' omission is signed, and the sign
depends on what an import displaces — against the mid-merit CCGT band a Dutch import at 474
gCO2/kWh is DIRTIER than what it replaced, against an OCGT peaker at 523 even that cable is
cleaner, and against a windy night with nothing thermal running every import adds carbon the
model did not have. Only the NET is knowable, which is why it is measured below and never argued.

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

WHAT CLOSING THE TWO GAPS ACTUALLY BOUGHT (2026-08-25, same measurement re-run with coal
dispatched and cables carried). The table above is the BEFORE and is left standing, because a
record you rewrite when the number improves is not a record:

    year   ours min: was -> now   NESO   p95/p5: was -> now   NESO   corr: was -> now  cables
    2019       0.057 -> 0.081    0.217      3.27 ->  3.59     2.78     0.85 -> 0.86     100%
    2020       0.055 -> 0.096    0.244     11.00 ->  6.80     3.12     0.82 -> 0.85     100%
    2021       0.056 -> 0.091    0.195      5.01 ->  5.86     3.26     0.90 -> 0.89      95%
    2022       0.070 -> 0.076    0.211     14.88 ->  7.27     4.10     0.82 -> 0.85      72%
    2023       0.058 -> 0.079    0.165     16.24 -> 10.01     4.34     0.77 -> 0.80      73%
    2024       0.059 -> 0.080    0.105     18.42 -> 10.36     5.06     0.68 -> 0.73      66%

  * THE CLEAN END ROSE by 35-75% and the gap to NESO fell from 3.2x too clean to 2.3x. That is
    the direction the whole build was for and it is the smaller half of what happened.
  * THE HEADLINE OVERSTATEMENT, the factor every abatement figure inherits, went from 2.88x to
    1.90x on p95/p5 and from 3.15x to 2.43x on max/min. Most of that is 2020 and 2022-2024,
    where imports are large.
  * IT IS NOT A CLEAN WIN AND MUST NOT BE REPORTED AS ONE. 2019 and 2021 got WORSE on spread
    (3.27 -> 3.59, 5.01 -> 5.86), because those are the years where coal still had a fleet and
    the cables were already fully priced: dispatching coal widens the dirty end with no offset.
    2021 also lost correlation (0.900 -> 0.885) and mean absolute error (0.113 -> 0.135). Five
    years of six improved on both; one did not, and the one that did not is named here rather
    than averaged away.
  * THE CABLES COLUMN IS WHY THE RECENT YEARS STILL MISS. Coverage falls to 66% by 2024 as
    Norwegian and Danish flow grows, and every uncovered MWh is dispatched as GB gas.

WHAT THE THERMAL FLOOR BOUGHT (2026-08-25, third build). Measured BEFORE and AFTER IN ONE
PROCESS against identical caches, with the floor as the only variable — an earlier version of
this docstring compared two separate runs and the published series' own figures moved between
them, which is a confound, not a result:

    year   floor MW   ours min: was -> now    NESO    p95/p5: was -> now   NESO    corr
    2019      1,394       0.081 -> 0.206     0.217      3.59 ->  3.56      2.78   0.862 -> 0.863
    2020      2,369       0.096 -> 0.314     0.244      6.80 ->  3.58      3.12   0.846 -> 0.849
    2021      1,700       0.091 -> 0.233     0.195      5.86 ->  4.25      3.26   0.885 -> 0.883
    2022      1,403       0.076 -> 0.199     0.211      7.27 ->  4.72      4.10   0.850 -> 0.844
    2023        791       0.079 -> 0.143     0.165     10.01 ->  6.75      4.34   0.796 -> 0.793
    2024        303       0.080 -> 0.108     0.105     10.36 ->  8.79      5.06   0.726 -> 0.726

  * THE HEADLINE OVERSTATEMENT, the factor every abatement figure inherits, went from 1.90x to
    1.36x on p95/p5 and from 2.44x to 1.04x on max/min. Mean absolute error fell in EVERY year.
  * THE CLEAN END NOW OVERSHOOTS IN TWO YEARS. 2020 reads 0.314 against a published 0.244 and
    2021 reads 0.233 against 0.195 — dirtier than GB was, not cleaner. This is reported because
    it is what happened, not despite it: a correction that only ever improved things in the
    direction its author wanted is the shape of a fitted one.
  * CORRELATION DID NOT MOVE, in any year, by more than 0.004. That is the most useful line in
    the table and it re-diagnoses the atom. The floor fixed a LEVEL error at the clean end and
    left the TIMING error untouched: this shape now knows how clean a quiet half hour is, and
    still does not know which half hours were the quiet ones (0.73 in 2024, falling by year).

STILL L2 AFTER THIS BUILD, and the reason has CHANGED rather than merely survived, which is the
part worth reading. The gap the last pass named as what held the level — the zero-thermal half
hours, 16% of 2024 — is closed and measured. What holds it now is the correlation line above: an
instrument at 0.73 against the published series is one that would still point a customer at the
wrong half hours, and no amount of getting the LEVEL of the clean end right fixes that. L3 means
the thing FAILS LIKE REALITY, and this fails in a different place than it did this morning. LAW
A: the plan is a diagnostic, and where a date and a test conflict the date is wrong.

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
    EF_COAL_TCO2_PER_MWH_E_BY_YEAR,
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
    "no loss correction. Coal dispatched from its demonstrated annual capacity; interconnector "
    "imports counted at NESO's published per-cable factors for the cables it publishes one for "
    "(84% of imported MWh over the series, 66% in 2024); the thermal stack held at or above the "
    "CCGT+OCGT fleet's demonstrated annual MINIMUM output, so no half hour is dispatched with no "
    "gas running at all."
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


def emissions_rate_t_per_mwh(
    demand_mw: float,
    renewable_generation_mw: float,
    year: int,
    *,
    import_mw: float = 0.0,
    import_rate_t_per_mwh: float = 0.0,
    coal_capacity_mw: float = 0.0,
    thermal_floor_mw: float = 0.0,
) -> float:
    """Tonnes CO2 per MWh of demand met, in ONE half hour, on the dispatch above.

    ABSOLUTE and therefore NOT for publication — it exists so the shape has something to be a
    ratio of, and so a test can check the shape against a hand-computed dispatch. The published
    quantity is the dimensionless shape; see the module docstring for why there is no second
    absolute grid-intensity series in this repository.

    `import_mw` / `import_rate_t_per_mwh` — the half hour's OBSERVED net import across the cables
    whose carbon intensity NESO actually publishes, and the MW-weighted rate of those cables.
    Supplied by `sim/elexon_fuel_outturn.py`; see that module for why a cross-border flow is an
    observable rather than something this dispatch model could ever derive.

    `coal_capacity_mw` — the coal fleet's demonstrated maximum output IN THAT YEAR. A capacity,
    not a dispatch: how much of it runs in this half hour is decided here, by the merit order,
    which is the question the reconstruction exists to answer independently of NESO.

    `thermal_floor_mw` — the smallest CCGT+OCGT output Elexon published in that year, from
    `elexon_fuel_outturn.thermal_floor_by_year`. The same class of input as the coal capacity and
    supplied at the same grain, one scalar per year, for the same reason: a half-hourly gas
    series would make this NESO's arithmetic rather than a second route to it.

    THE DEFAULTS REPRODUCE THE PRE-2026-08-25 SHAPE EXACTLY, and that is a liability rather than
    a convenience: a caller that forgets them gets the known-wrong series silently. The control
    against that is not in this signature — it is `generate_grid_intensity_feed.generate()`,
    which loads the mix and RAISES if it is absent, so the published feed cannot quietly revert.
    """
    y = _year_of(int(year))
    worst_eff, best_eff = _ccgt_efficiency_band(y)
    demand_mw = float(demand_mw)
    if demand_mw <= 0.0:
        raise ShapeUnavailable("a half hour with no demand has no emissions rate")

    # IMPORTS ARE SERVED BEFORE ANYTHING GB BURNS, because that is what a cable does: it delivers
    # whatever the cross-border spread told it to deliver and the GB stack dispatches around the
    # remainder. Clamped at zero (an export is not a negative import — see `elexon_fuel_outturn`)
    # and at demand, because a half hour cannot be met more than once.
    import_mw = min(max(0.0, float(import_mw)), demand_mw)
    residual_mw = demand_mw - float(renewable_generation_mw) - import_mw
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

    # THE THERMAL FLOOR, and it is the correction that took this shape's largest remaining
    # clean-end error. The line above lets the stack reach EXACTLY ZERO, and GB's never does:
    # there is always gas running for inertia, reserve and voltage, whatever the residual says.
    # Measured, this model dispatched no thermal plant at all in 16.1% of 2024's half hours and
    # 30.8% of 2025's, and those are precisely the half hours a time-shifting recommendation
    # points a customer at -- so the error was concentrated exactly where it did the most damage.
    #
    # WHAT THE FLOOR DISPLACES IS RENEWABLE OUTPUT, NOT DEMAND, which is the same call already
    # made three lines up for must-run: when generation exceeds demand it is WIND that is
    # constrained off. So the floor is capped at the room left under demand once must-run is
    # served, never allowed to manufacture generation the half hour had no use for.
    floor_mw = min(max(0.0, float(thermal_floor_mw)), max(0.0, demand_mw - must_run_mw))
    thermal_mw = max(thermal_mw, floor_mw)

    ccgt_mw = min(thermal_mw, CCGT_CAPACITY_MW)

    # COAL SITS ABOVE THE CCGT BAND, and that ordering is sourced rather than assumed. Carbon
    # Price Support (a flat ~GBP 18/tCO2 across the whole window) plus the ETS is applied to
    # coal's ~0.95 tCO2 per electrical MWh against gas's ~0.38, which is what pushed coal out of
    # merit for most of the period — and the outcome is visible in DUKES 5.10.B, whose coal load
    # factors run 8-21% over 2016-2024 while CCGT's run three to four times that. A plant with
    # that load factor is a peaking plant, so it dispatches after the mid-merit band.
    #
    # STATED SIMPLIFICATION, WITH ITS DIRECTION: this ordering is fixed rather than recomputed
    # per half hour from the gas/coal spread, because this function takes no fuel prices. In the
    # winter of 2021-22 gas spiked far enough that coal genuinely went BELOW gas in merit for
    # weeks; by then the fleet measured below was a fraction of a gigawatt, so the half hours
    # that mis-orders are few and their coal volume small. Where it is wrong it UNDERSTATES coal,
    # i.e. it errs toward the pre-existing no-coal-at-all behaviour rather than away from it.
    above_ccgt_mw = max(0.0, thermal_mw - CCGT_CAPACITY_MW)
    coal_mw = min(above_ccgt_mw, max(0.0, float(coal_capacity_mw)))
    peaker_mw = max(0.0, above_ccgt_mw - coal_mw)
    peaker_mw = min(peaker_mw, max(0.0, TOTAL_DISPATCHABLE_MW - MUST_RUN_FLOOR_MW - CCGT_CAPACITY_MW))

    # THE AVERAGE OF WHAT RAN, NOT THE LAST UNIT TO RUN. Efficiency slides best -> worst across
    # the band, so a band loaded to fraction f has run everything from `best` down to
    # `best - (best-worst)*f`; its MEAN is the midpoint of that ramp. Taking the marginal unit
    # instead would overstate the gap between quiet and busy half hours -- flattering exactly
    # the effect this module was written to measure, which is the direction to be most careful
    # about.
    load_fraction = (ccgt_mw / CCGT_CAPACITY_MW) if CCGT_CAPACITY_MW > 0 else 0.0
    mean_dispatched_eff = best_eff - (best_eff - worst_eff) * load_fraction / 2.0

    # COAL IS PRICED PER ELECTRICAL MWh, not through a fuel-input factor over an efficiency the
    # way gas is, and the asymmetry is deliberate: DUKES 5.14 publishes the per-supplied-MWh coal
    # factor directly and `merit_order_reconstruction` already imports that exact series to price
    # coal's SRMC. Deriving a second route would mean inventing a coal fuel-input factor that is
    # nowhere in this tree. Sanity, not calibration: the 2019 DUKES figure of 0.992 sits 5.9%
    # above NESO's own published coal factor of 0.937, on the dirtier side of it.
    tonnes = (
        must_run_mw * MUST_RUN_EMISSIONS_RATE_T_PER_MWH
        + import_mw * max(0.0, float(import_rate_t_per_mwh))
        + ccgt_mw * (EF_GAS_TCO2_PER_MWH_TH / mean_dispatched_eff)
        + coal_mw * EF_COAL_TCO2_PER_MWH_E_BY_YEAR[y]
        + peaker_mw * (EF_GAS_TCO2_PER_MWH_TH / OCGT_REFERENCE_EFFICIENCY)
    )
    return tonnes / demand_mw


def build_shape(
    demand_by_period: Mapping[tuple[str, int], float],
    renewables_by_period: Mapping[tuple[str, int], float],
    *,
    imports_by_period: Mapping[tuple[str, int], tuple[float, float]] | None = None,
    coal_capacity_by_year: Mapping[int, float] | None = None,
    thermal_floor_by_year: Mapping[int, float] | None = None,
) -> dict[tuple[str, int], float]:
    """{(settlement date, period): shape}, normalised per CALENDAR YEAR to a demand-weighted
    mean of exactly 1.0.

    `imports_by_period`, `coal_capacity_by_year` and `thermal_floor_by_year` all come from
    `sim/elexon_fuel_outturn.py` and close three of the gaps this module has named. The floor is
    `{year: floor_mw}` — the caller unpacks `floor_mw` from that module's per-year record, so the
    diagnostic `p1_mw` beside it cannot reach the dispatch by accident. A half hour with no import reading
    is dispatched with none — NOT skipped, because a missing cable reading is not a missing half
    hour and dropping it would shorten the series that the year's normalisation is taken over.
    That is the opposite call from the one made for renewables two paragraphs down, and the
    difference is which way the error runs: a missing renewable outturn treated as zero INVENTS
    a dirty half hour out of nothing, whereas a missing import treated as zero reproduces the
    behaviour this series had for its whole life and is bounded by it.

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
        year = int(key[0][:4])
        import_mw, import_rate = (imports_by_period or {}).get(key, (0.0, 0.0))
        # KEYED ON THE REAL YEAR, NEVER THE CLAMPED ONE. `_year_of` exists to keep the DUKES
        # efficiency and emission-factor tables from being read out of range, and clamping is the
        # right answer for a published constant that stops in 2024. It is the wrong answer for a
        # fleet that CLOSED: clamping 2025 to 2024 would resurrect the coal capacity of the year
        # before the last unit shut, in a year Elexon says the fleet generated nothing.
        coal_mw = float((coal_capacity_by_year or {}).get(year, 0.0))
        # THE REAL YEAR HERE TOO, and for the mirror of the coal reason. Clamping would carry a
        # year's measured floor into a year it was not measured in; a year with no measurement
        # gets no floor, which is the pre-existing behaviour rather than an invented one.
        floor_mw = float((thermal_floor_by_year or {}).get(year, 0.0))
        try:
            rates[key] = emissions_rate_t_per_mwh(
                float(demand_mw),
                float(renewable_mw),
                year,
                import_mw=float(import_mw),
                import_rate_t_per_mwh=float(import_rate),
                coal_capacity_mw=coal_mw,
                thermal_floor_mw=floor_mw,
            )
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
