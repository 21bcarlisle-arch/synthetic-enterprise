"""Weather-driven demand model — Phase 4c-2 (physical simulation layer).

Replaces the flat assumption that every customer on a given Profile Class
consumes exactly the population-average shape (`sim/profile_class_1.py` /
`sim/profile_class_3.py`) with a physical adjustment layer on top of that
base shape:

  demand_shape = (base_shape + heating_load + cooling_load)
                 * occupancy_multiplier * occupancy_volume_factor
                 + ev_charging_load - solar_generation

- **Heating/cooling degree days**: standard UK 15.5C heating base
  temperature (the threshold below which buildings need supplementary
  heating — the conventional value used in UK degree-day data, e.g.
  gov.uk/government/statistics/degree-days) and a 22C cooling base. Extra
  load from degree days is spread across the settlement periods a household
  actually runs heating/cooling (`HEATING_PERIOD_WEIGHTS`,
  `COOLING_PERIOD_WEIGHTS`) — morning and evening for heating, afternoon for
  cooling.
- **Occupancy** (W2_13): two DISTINCT responses, both keyed on the property
  record's `people_count` where present.
  * **VOLUME** — `occupancy_volume_factor()` scales *how much* a household uses
    by headcount, following the DESNZ NEED 2023 per-adult **sublinear** median
    curve. This is the piece that did not exist before W2_13: the old
    3-category multiplier only *redistributed* load across the day.
  * **SHAPE** — `occupancy_multiplier()` shifts *when* load is consumed. Its
    09:00-17:00 daytime window now responds to household composition (EFUS
    2017 daytime-occupancy rates); evening and overnight are near-universally
    occupied regardless of composition (88%/94%) and are left UNCHANGED.
  `saas/property_model.py`'s legacy `occupancy_pattern` (single/family/elderly)
  remains the coarse SHAPE fallback when no `people_count` is available.
- **Asset adjustments**: an EV (`assets.ev`) adds an overnight charging
  block; solar (`assets.solar`) subtracts daytime generation (estimated from
  half-hourly irradiance, e.g. `sim.weather_engine.half_hourly_solar_irradiance`)
  from net demand, floored at zero (this models net import only — export is
  out of scope for this sub-phase).

All per-degree-day and per-asset constants below are seed estimates pending
the `customer-archetype-data-enrichment` background task — see
`saas/property_model.py`'s module docstring for the same caveat.

This module is pure: plain values in, plain list-of-48-floats out. It
consumes weather *outputs* (a daily mean temperature, optional half-hourly
irradiance) rather than importing `sim.weather_engine` directly, so it can
be unit-tested without the weather engine's numpy/RNG machinery.
"""

from __future__ import annotations

import functools
import hashlib
import math
import random

PERIODS_PER_DAY = 48

# --- Heating/cooling degree days (UK convention) ---
HEATING_BASE_TEMP_C = 15.5
COOLING_BASE_TEMP_C = 22.0


def heating_degree_days(mean_temp_c: float) -> float:
    """Degrees below the 15.5C UK heating base temperature, floored at 0."""
    return max(0.0, HEATING_BASE_TEMP_C - mean_temp_c)


def cooling_degree_days(mean_temp_c: float) -> float:
    """Degrees above the 22C cooling base temperature, floored at 0."""
    return max(0.0, mean_temp_c - COOLING_BASE_TEMP_C)


# --- Extra load per degree-day (seed estimates) ---
GAS_HEATING_KWH_PER_DEGREE_DAY = 8.0
ELEC_HEATING_KWH_PER_DEGREE_DAY = {
    "electric_storage": 3.0,
    "heat_pump": 1.2,  # heat pumps are more efficient per degree-day than resistive storage heaters
}
ELEC_COOLING_KWH_PER_DEGREE_DAY = 0.5


def _period_weights(active_periods: range) -> list[float]:
    """A 48-length list, equal weight on `active_periods` (1-48 inclusive,
    settlement period numbering), 0 elsewhere, summing to 1."""
    active = set(active_periods)
    weight = 1.0 / len(active)
    return [weight if p in active else 0.0 for p in range(1, PERIODS_PER_DAY + 1)]


# Heating: morning warm-up (06:00-10:00, periods 13-20) and evening
# (16:30-22:00, periods 34-44) — the two periods a household typically runs
# heating.
# Each _period_weights() call sums to 1 individually, so the combined
# morning+evening weights sum to 2 — halve to renormalise to 1.
HEATING_PERIOD_WEIGHTS = [
    (w1 + w2) / 2.0
    for w1, w2 in zip(_period_weights(range(13, 21)), _period_weights(range(34, 45)))
]

# Cooling: early afternoon (11:30-18:00, periods 24-36) — peak temperature
# window.
COOLING_PERIOD_WEIGHTS = _period_weights(range(24, 37))

# --- Occupancy pattern: when load is consumed within the day ---
# Settlement periods 1-48 map to 00:00-24:00 in 30-minute steps; period p
# covers [(p-1)*0.5h, p*0.5h).
_MORNING_PERIODS = range(13, 21)  # 06:00-10:00
_EVENING_PERIODS = range(34, 45)  # 16:30-22:00

# ===========================================================================
# W2_13 — occupancy → consumption VOLUME and SHAPE
# (docs/design/W2_13_OCCUPANCY_CONSUMPTION_VOLUME_SHAPE_DISCOVER.md §5;
#  anchors: docs/market_research/occupancy_consumption_volume_shape_w2_13.md)
#
# WHY this exists: before W2_13 occupancy entered the demand path ONLY as the
# per-period category multiplier below (0.75-1.4, hovering near 1.0). It
# redistributed load across the day but did NOT scale total volume by
# headcount — a family home and a single home on the same base profile ended
# the day at roughly the same daily total. There was no people-count, no
# adults-vs-children distinction, and no per-person volume gradient anywhere.
#
# R13 note: every constant below is justified by fidelity to a published UK
# statistic (DESNZ NEED 2023 / DESNZ-BRE EFUS 2017). None of them was chosen
# by, or checked against, any company P&L or margin outcome.
# ===========================================================================

# --- ANCHOR 1 (H confidence): volume by number of adults -------------------
# DESNZ NEED "Consumption_additional_EW_2023.xlsx", Table A14 (electricity) /
# Table A13 (gas), England & Wales, median kWh/year by number of adults
# (2023 gas/electricity year), parsed direct from the published .xlsx
# 2026-07-23. The SHAPE of the response is the anchor, not any one number:
# electricity jumps hardest on 1→2 adults (+43.8% — a large shared fixed base
# of lighting/fridge/standby/cooking that a second adult adds little marginal
# draw to) then flattens (+15.7/+13.6/+9.5%); gas has a smaller 1→2 step
# (+24.3%) and steadier increments, because space heating tracks dwelling size
# (modelled elsewhere) while hot water and cooking track people. The same
# monotonic-sublinear shape holds in every NEED vintage back to 2005.
NEED_MEDIAN_KWH_BY_ADULTS: dict[str, dict[int, float]] = {
    "electricity": {1: 1993.0, 2: 2867.0, 3: 3318.0, 4: 3772.0, 5: 4129.0},
    "gas": {1: 8546.0, 2: 10624.0, 3: 11576.0, 4: 12734.0, 5: 14486.0},
}
# NEED's top band is "5 or more adults", so the curve is FLAT above 5 — an
# honest reading of the published banding, not an extrapolation.
_NEED_TOP_BAND_ADULTS = 5

# --- ANCHOR 2 (H confidence): daytime occupancy rate by composition --------
# DESNZ/BRE Energy Follow-Up Survey (EFUS) 2017 "Heating patterns and
# occupancy" §4.1-4.2 (n≈1,167-1,179 GB households). Weekday DAYTIME
# (09:00-17:00) "someone home all day" swings ~30pp by composition:
#   household size:  1-person 37%          → 5+-person 67%
#   pensioner:       none 34%              → someone over SPA 63%
#   employment:      someone employed 35%  → all adults unemployed 60%
# EVENING (88%) and OVERNIGHT (94%) are near-universally occupied REGARDLESS
# of composition — consistent with the Elexon PC1 evening-peak/overnight-
# baseload shape already in `sim/profile_class_1.py`. So the composition
# response is confined to the daytime window and those two windows are left
# exactly as they were.
EFUS_DAYTIME_RATE_ONE_PERSON = 0.37
EFUS_DAYTIME_RATE_FIVE_PLUS_PERSON = 0.67
EFUS_DAYTIME_RATE_NO_PENSIONER = 0.34
EFUS_DAYTIME_RATE_PENSIONER_PRESENT = 0.63
EFUS_DAYTIME_RATE_SOMEONE_EMPLOYED = 0.35
EFUS_DAYTIME_RATE_ALL_UNEMPLOYED = 0.60

# The EFUS 09:00-17:00 window is settlement periods 19-34. Periods 19-20 are
# already inside the morning ramp and 34 inside the evening peak, so the
# composition response is applied only to the periods that belong to NEITHER
# — 21-33 (10:00-16:30). That is what makes "evening and overnight unchanged"
# literally true and directly testable, rather than a claim.
_EFUS_DAYTIME_PERIODS = range(19, 35)  # 09:00-17:00
_COMPOSITION_RESPONSE_PERIODS = frozenset(
    p for p in _EFUS_DAYTIME_PERIODS
    if p not in _MORNING_PERIODS and p not in _EVENING_PERIODS
)

# --- Population reference: ONS Census 2021 TS017 household size ------------
# England, computed from the published LTLA-level CSV (discovery-agent pass,
# fetched 2026-07-08, ASSUMPTIONS.md "Household Segment & Psychology"): 1p
# 30.1%, 2p 34.0%, 3p 16.0%, 4p 12.9%, 5+p 7.0% (mean 2.37 persons). This is
# the same anchor `simulation.household_segments.OCCUPANCY_POPULATION_SHARE`
# uses, at the FINER 1/2/3/4/5+ granularity the NEED curve needs (that module
# combines 3- and 4-person into one band). Held here rather than imported so
# the volume normaliser cannot be silently re-levelled by an unrelated edit to
# the segment bands.
HOUSEHOLD_SIZE_POPULATION_SHARE: dict[int, float] = {
    1: 0.301, 2: 0.340, 3: 0.160, 4: 0.129, 5: 0.070,
}
assert abs(sum(HOUSEHOLD_SIZE_POPULATION_SHARE.values()) - 1.0) < 1e-9

# --- C-S2 RNG substream ----------------------------------------------------
# This atom's OWN named substream. Its seed is a pure function of
# (STREAM_NAME, salt, household key, book seed), sharing no state with the
# global `random`, with `simulation.premise_demand`'s W1_5 stream, or with
# `household_segments`' per-customer draws — so a draw here can never shift
# another subsystem's sequence, and replay is deterministic across processes.
# A future draw APPENDS a salt; it never inserts into an existing substream.
STREAM_NAME = "W2_13_occupancy_consumption_volume_shape"
_CHILD_EQUIVALENCE_SALT = "child_adult_equivalence"
_DAYTIME_ELASTICITY_SALT = "daytime_shape_elasticity"


def _substream(base_seed: int, salt: str) -> random.Random:
    """An ISOLATED `random.Random` seeded from a STABLE sha256 of
    (STREAM_NAME::salt::base_seed) — C-S2 substream discipline, the same
    construction `simulation.premise_demand` uses for its own stream."""
    key = f"{STREAM_NAME}::{salt}::{base_seed}".encode("utf-8")
    return random.Random(int.from_bytes(hashlib.sha256(key).digest()[:8], "big"))


def _base_seed_for(household_key: str, seed: int | None) -> int:
    """Stable md5 of the household key with any book-level ``seed`` mixed in:
    every household draws a distinct value, and a given ``seed`` makes the
    whole book reproducible (C-S2 deterministic replay)."""
    key = household_key if seed is None else f"{household_key}::{seed}"
    return int.from_bytes(hashlib.md5(key.encode("utf-8")).digest()[:8], "big")


# --- R10 GAP (a): the adults-vs-children marginal increment ----------------
# UNANCHORED, SAMPLED, NEVER A POINT ESTIMATE. NEED Table A13/A14's variable
# is "number of ADULTS" (Experian-modelled; NEED 2025 PDF p.8 fn.3) and no
# NEED table cross-tabulates adults against children, so the marginal volume
# of a child CANNOT be lifted from the anchor. EFUS §5.2.2 gives the DIRECTION
# only — children-present households are far likelier to run under one
# bath/shower per person per day (71% vs 38%), i.e. children dampen per-person
# intensity — so assuming a child consumes like an adult would overstate the
# increment. The magnitude is therefore drawn per household from this interval
# (uniform: no evidence favours any point inside it), not fixed:
CHILD_ADULT_EQUIVALENT_RANGE = (0.35, 0.85)


@functools.lru_cache(maxsize=4096)
def child_adult_equivalence(household_key: str, seed: int | None = None) -> float:
    """A household's draw for R10 GAP (a) — how much of an adult's marginal
    volume a child contributes — from this atom's own C-S2 substream.

    Deterministic in (household_key, seed). `household_key=""` (no key
    available) returns the interval MIDPOINT rather than a draw, so a caller
    without an identity gets the honest central value instead of a silent
    dependence on the global RNG.
    """
    lo, hi = CHILD_ADULT_EQUIVALENT_RANGE
    if not household_key:
        return (lo + hi) / 2.0
    return _substream(_base_seed_for(household_key, seed), _CHILD_EQUIVALENCE_SALT).uniform(lo, hi)


# --- R10 GAP (b): the occupancy-rate → kWh-shape-weight conversion ---------
# UNANCHORED, SAMPLED. The EFUS daytime-occupancy RATES above are H-confidence,
# but "probability someone is home" is not kWh: a 1pp change in occupancy does
# not move daytime consumption 1pp, because a real share of daytime draw
# (fridge/freezer, standby, timed heating/hot water) runs with nobody in.
# The conversion exponent is therefore a build-time modelling choice with no
# published magnitude, drawn per household from this sub-unit interval rather
# than fixed. (1.0 would mean a fully proportional pass-through, which the
# unattended base load rules out; 0.0 would mean occupancy does not move
# consumption at all.)
DAYTIME_RATE_TO_KWH_ELASTICITY_RANGE = (0.30, 0.80)

# --- R10 GAP (c): cooking-fuel split and overnight device/standby load -----
# NOT BUILT, and deliberately not invented. Neither the gas-vs-electric
# cooking split nor composition-driven overnight standby load could be
# anchored to a published UK source in the DISCOVER pass; the named unfetched
# follow-up lead is EFUS `efus-light-appliances-smart-tech.pdf`. Until it is
# fetched, this model applies NO composition response to the overnight window
# (which EFUS independently shows is 94% occupied regardless of composition),
# rather than fabricating one. Stated here so the gap is visible where the
# mechanism lives.


@functools.lru_cache(maxsize=4096)
def daytime_rate_elasticity(household_key: str, seed: int | None = None) -> float:
    """A household's draw for R10 GAP (b) — the exponent converting a daytime
    occupancy RATE ratio into a kWh shape-weight ratio — from this atom's own
    C-S2 substream. `household_key=""` returns the interval midpoint."""
    lo, hi = DAYTIME_RATE_TO_KWH_ELASTICITY_RANGE
    if not household_key:
        return (lo + hi) / 2.0
    return _substream(_base_seed_for(household_key, seed), _DAYTIME_ELASTICITY_SALT).uniform(lo, hi)


def _need_curve(commodity: str) -> dict[int, float]:
    """The NEED median curve for a commodity, normalised to the 1-adult median
    (so the value at 1 adult is exactly 1.0). Anything that is not "gas" uses
    the electricity curve, matching `build_demand_shape`'s own commodity
    branch."""
    table = NEED_MEDIAN_KWH_BY_ADULTS["gas" if commodity == "gas" else "electricity"]
    base = table[1]
    return {n: v / base for n, v in table.items()}


def adult_equivalents(people_count: int, children_count: int, child_weight: float) -> float:
    """Convert a headcount into the NEED curve's own unit — ADULT EQUIVALENTS.

    NEED is keyed on adults only, so children enter at ``child_weight`` of an
    adult (R10 GAP (a) above). Raises rather than defaulting on nonsense input
    (a zero/negative/non-finite headcount, or more children than people) —
    an unusable headcount is a caller error, never a silent 1.0 (FAIL-OPEN
    guard, R15).
    """
    if not isinstance(people_count, (int, float)) or not math.isfinite(people_count):
        raise ValueError(f"people_count must be a finite number, got {people_count!r}")
    if people_count < 1:
        raise ValueError(f"people_count must be at least 1, got {people_count!r}")
    if not math.isfinite(children_count) or children_count < 0:
        raise ValueError(f"children_count must be >= 0, got {children_count!r}")
    if children_count > people_count - 1:
        raise ValueError(
            "a household must contain at least one adult: "
            f"children_count={children_count!r} vs people_count={people_count!r}"
        )
    adults = people_count - children_count
    return adults + child_weight * children_count


def need_volume_index(people_count: int, commodity: str, *, children_count: int = 0,
                      child_weight: float | None = None) -> float:
    """The RAW (un-normalised) NEED volume index for a household: annual
    consumption relative to a 1-adult household, interpolated along the
    published per-adult medians.

    Piecewise-linear between the integer knots (adult equivalents can be
    fractional once children are weighted at less than 1), and FLAT at and
    above 5 because NEED's top band is "5 or more adults".
    """
    if child_weight is None:
        child_weight = sum(CHILD_ADULT_EQUIVALENT_RANGE) / 2.0
    ae = adult_equivalents(people_count, children_count, child_weight)
    curve = _need_curve(commodity)
    if ae >= _NEED_TOP_BAND_ADULTS:
        return curve[_NEED_TOP_BAND_ADULTS]
    lo = int(math.floor(ae))
    if lo >= _NEED_TOP_BAND_ADULTS:
        return curve[_NEED_TOP_BAND_ADULTS]
    frac = ae - lo
    return curve[lo] + frac * (curve[lo + 1] - curve[lo])


# --- The base profile's LEVEL: the household's own EAC, not the nation's ------
#
# `sim/profile_class_1.py` returns Group Average Demand: the ABSOLUTE half-hourly
# series of the average PC1 customer, ~3,921 kWh annualised. Used unnormalised it
# gives every household in the book the same level, so a household's drawn
# `eac_kwh` -- the world's own statement about how much it consumes -- reached
# pricing and hedging and never reached the volume. Measured 2026-08-31 over the
# 133 resi/PC1/legacy accounts live in 2024: Spearman rho(drawn EAC, settled kWh)
# = -0.0016, and the settled lower quartile sat exactly on the national average.
#
# The repair is the settlement convention, not an invention: profile coefficient
# x EAC. The profile supplies the SHAPE; the EAC supplies the LEVEL.
#
# The divisor is the profile's own annual total FOR THAT YEAR, never a frozen
# constant. GAD annualises to 3,921.8 in 2019 and 3,904.2 in 2022 because the
# season/day-type calendar moves; a frozen divisor would push that +-0.5% year
# effect into every household's level and attribute it to nothing.


@functools.lru_cache(maxsize=64)
def profile_annual_kwh(base_shape_fn, year: int) -> float:
    """Total kWh a base profile function delivers across every day of `year`.

    `base_shape_fn` is a `SHAPE_LOADERS[...]`-shaped callable: a date (ISO string
    or `date`) in, 48 half-hourly kWh values out. Cached per (function, year) --
    365 loader calls the first time a year is asked for, none afterwards.
    """
    import datetime as _dt

    day = _dt.date(year, 1, 1)
    total = 0.0
    while day.year == year:
        total += sum(base_shape_fn(day.isoformat()))
        day += _dt.timedelta(days=1)
    return total


def eac_scaled_shape_fn(base_shape_fn, eac_kwh: float):
    """Wrap a base-shape function so its ANNUAL INTEGRAL is `eac_kwh`.

    The within-year shape is untouched -- every period is multiplied by the one
    scalar `eac_kwh / profile_annual_kwh(...)`, so season, day-type and
    time-of-day structure survive exactly and only the level moves.

    This scales the BASE PROFILE ONLY. The additive physical overlays that
    `build_demand_shape` and its callers stack on top -- degree-day heating and
    cooling load, EV charging, ASHP uplift -- are absolute kWh quantities and are
    deliberately NOT divided by the household's EAC: an EV does not charge less
    because the house it is parked at consumes little. A household's settled
    total therefore need not equal its EAC, which is also true of a real EAC.
    """
    def scaled(target_date):
        year = (
            int(target_date[:4]) if isinstance(target_date, str) else target_date.year
        )
        factor = eac_kwh / profile_annual_kwh(base_shape_fn, year)
        return [v * factor for v in base_shape_fn(target_date)]

    return scaled


@functools.lru_cache(maxsize=8)
def volume_factor_normaliser(commodity: str) -> float:
    """The share-weighted mean RAW NEED index over the ONS TS017 reference
    population — the divisor that makes `occupancy_volume_factor` mean-1.

    WHY normalise at all: the NEED index is anchored on a 1-adult household,
    so applying it raw would multiply national demand by ~1.45 (electricity)
    overnight. The occupancy response must REDISTRIBUTE volume between
    households of different size, not re-level the aggregate — an unannounced
    baseline shift would be an R13 breach dressed up as a fidelity gain.
    """
    return sum(
        share * need_volume_index(n, commodity)
        for n, share in HOUSEHOLD_SIZE_POPULATION_SHARE.items()
    )


def occupancy_volume_factor(people_count: int, commodity: str, *, children_count: int = 0,
                            household_key: str = "", seed: int | None = None) -> float:
    """**The VOLUME response** — how much a household of this size uses,
    relative to the population average, following the DESNZ NEED 2023
    per-adult SUBLINEAR curve.

    This is the term that did not exist before W2_13. It is DETERMINISTIC in
    the household's composition (the only stochastic input is the R10 GAP (a)
    child weight, and only when children are present) and is therefore
    DISTINCT from — and multiplies independently with —
    `simulation.premise_demand.idiosyncratic_factor`, W1_5's mean-1
    per-premise NOISE. Occupancy explains a population-structured share of the
    variance W1_5 currently absorbs as noise; neither re-derives the other.

    Mean-1 over the ONS TS017 reference population by construction (see
    `volume_factor_normaliser`), so switching it on redistributes demand
    between households without moving the aggregate.
    """
    child_weight = child_adult_equivalence(household_key, seed) if children_count else None
    raw = need_volume_index(
        people_count, commodity, children_count=children_count, child_weight=child_weight
    )
    return raw / volume_factor_normaliser(commodity)


def _daytime_occupancy_rate(people_count: int, pensioner_present: bool | None,
                            someone_employed: bool | None) -> float:
    """The EFUS weekday-daytime "someone home all day" rate for a composition.

    Household size is the primary cut (linear in size between the two
    published endpoints, 1-person 37% and 5+-person 67% — EFUS publishes the
    ends, the interior is a stated linear reading, not a further anchor).
    Pensioner-presence and employment are INDEPENDENT published marginal cuts;
    when supplied they are combined with the size cut as an equal-weight
    average of the available cuts. Unknown cuts are simply absent from the
    average rather than defaulted, so a caller who knows only the headcount
    gets the size response alone.
    """
    span = EFUS_DAYTIME_RATE_FIVE_PLUS_PERSON - EFUS_DAYTIME_RATE_ONE_PERSON
    capped = min(max(float(people_count), 1.0), 5.0)
    rates = [EFUS_DAYTIME_RATE_ONE_PERSON + span * (capped - 1.0) / 4.0]
    if pensioner_present is not None:
        rates.append(
            EFUS_DAYTIME_RATE_PENSIONER_PRESENT if pensioner_present
            else EFUS_DAYTIME_RATE_NO_PENSIONER
        )
    if someone_employed is not None:
        rates.append(
            EFUS_DAYTIME_RATE_SOMEONE_EMPLOYED if someone_employed
            else EFUS_DAYTIME_RATE_ALL_UNEMPLOYED
        )
    return sum(rates) / len(rates)


@functools.lru_cache(maxsize=1)
def _reference_daytime_rate() -> float:
    """The share-weighted mean daytime occupancy rate over the ONS TS017
    reference population — the rate the composition response is CENTRED on.

    Centring on the population's own mean is what keeps the shape response
    aggregate-neutral: a household above the mean draws more daytime, one
    below draws less, and the population mean multiplier stays ~1.0. (It lands
    at 0.470 under the size cut alone, above EFUS's all-household 43%, because
    EFUS's headline mixes in composition cuts — pensioner, employment — that
    are not modelled at population level here. Centring on 0.43 instead would
    silently lift daytime demand ~5%; `population_mean_daytime_multiplier`
    below is the control that would catch exactly that.)
    """
    return sum(
        share * _daytime_occupancy_rate(n, None, None)
        for n, share in HOUSEHOLD_SIZE_POPULATION_SHARE.items()
    )


def occupancy_multiplier(occupancy_pattern: str, period: int, *,
                         people_count: int | None = None,
                         children_count: int = 0,
                         pensioner_present: bool | None = None,
                         someone_employed: bool | None = None,
                         household_key: str = "",
                         seed: int | None = None) -> float:
    """**The SHAPE response** — a multiplier (around 1.0) applied to a
    settlement period's demand, reflecting WHEN a household is home.

    period is 1-48 (settlement period numbering).

    With no ``people_count`` this is byte-identical to the pre-W2_13 function:
    the 3-way `occupancy_pattern` category (single/family/elderly, unknown
    values falling back to "single") is the COARSE FALLBACK for a household
    whose headcount is unknown.

    With a ``people_count`` the category value is kept as the base and the
    DAYTIME window only (periods 21-33, the part of EFUS's 09:00-17:00 window
    that is neither the morning ramp nor the evening peak) is scaled by the
    household's daytime-occupancy rate relative to the population mean, raised
    to the R10 GAP (b) elasticity. Morning, EVENING and OVERNIGHT periods are
    returned unchanged — EFUS measures 88%/94% occupancy there regardless of
    composition, so there is no composition signal to apply.

    ``children_count`` is accepted for interface symmetry with
    `occupancy_volume_factor` but does not currently move the shape: EFUS's
    daytime cut is by household SIZE, not by children specifically, and
    inventing a separate child shape term would be exactly the unanchored
    point estimate R10 forbids.
    """
    morning = period in _MORNING_PERIODS
    evening = period in _EVENING_PERIODS

    if occupancy_pattern == "elderly":
        # Home most of the day — flatter profile, daytime load close to peak.
        base = 1.1 if (morning or evening) else 1.2
    elif occupancy_pattern == "family":
        # Out at work/school during the day, sharp evening peak.
        base = 1.4 if evening else (1.1 if morning else 0.85)
    else:
        # "single" (default): out most of the day, moderate evening peak.
        base = 1.25 if evening else (1.0 if morning else 0.75)

    if people_count is None or period not in _COMPOSITION_RESPONSE_PERIODS:
        return base

    rate = _daytime_occupancy_rate(people_count, pensioner_present, someone_employed)
    elasticity = daytime_rate_elasticity(household_key, seed)
    return base * (rate / _reference_daytime_rate()) ** elasticity


# --- R15 controls: neither response may silently re-level the aggregate ----
# Diagnostic bands, not targets (R12). Both controls compare a computed
# population mean against the CONSTANT 1.0 that the normalisation is supposed
# to deliver — not against a value re-derived from the same code path — so
# they genuinely fire when the normalisation is wrong, removed, or centred on
# the wrong reference rate.
VOLUME_FACTOR_BIAS_TOL = 0.02
DAYTIME_SHAPE_BIAS_TOL = 0.02


def population_mean_volume_factor(people_counts: list[int], weights: list[float],
                                  commodity: str, *, children_counts: list[int] | None = None,
                                  household_keys: list[str] | None = None,
                                  seed: int | None = None) -> float:
    """The weight-normalised mean occupancy volume factor over a book.

    Raises on empty input, length mismatch, or non-positive total weight — the
    mean factor of no households is a caller error, never a silently-passing
    1.0 (FAIL-OPEN guard, R15).
    """
    n = len(people_counts)
    if n == 0:
        raise ValueError("cannot take the mean volume factor of an empty population")
    if len(weights) != n:
        raise ValueError("people_counts and weights must be the same length")
    if children_counts is None:
        children_counts = [0] * n
    if household_keys is None:
        household_keys = [""] * n
    if len(children_counts) != n or len(household_keys) != n:
        raise ValueError("children_counts/household_keys must match people_counts")
    total = float(sum(weights))
    if not math.isfinite(total) or total <= 0.0:
        raise ValueError("population weights must sum to a positive finite value")
    return sum(
        (weights[i] / total) * occupancy_volume_factor(
            people_counts[i], commodity, children_count=children_counts[i],
            household_key=household_keys[i], seed=seed,
        )
        for i in range(n)
    )


def volume_factor_is_unbiased(people_counts: list[int], weights: list[float], commodity: str, *,
                              children_counts: list[int] | None = None,
                              household_keys: list[str] | None = None,
                              seed: int | None = None,
                              tol: float = VOLUME_FACTOR_BIAS_TOL) -> bool:
    """R15-failable control: True iff the occupancy VOLUME response leaves
    aggregate demand where it found it (population mean factor within ``tol``
    of 1.0). FIRES when the normaliser is dropped or mis-levelled — dropping
    it alone puts the electricity mean at ~1.45."""
    return abs(
        population_mean_volume_factor(
            people_counts, weights, commodity, children_counts=children_counts,
            household_keys=household_keys, seed=seed,
        ) - 1.0
    ) <= tol


def population_mean_daytime_multiplier(people_counts: list[int], weights: list[float], *,
                                       occupancy_pattern: str = "single", period: int = 25,
                                       household_keys: list[str] | None = None,
                                       seed: int | None = None) -> float:
    """The weight-normalised mean DAYTIME shape multiplier over a book,
    expressed relative to the category baseline (so 1.0 == "the composition
    response moved load between households without moving the total").

    Raises on empty input / non-positive weight (FAIL-OPEN guard, R15), and on
    a period outside the composition-response window (where the ratio would be
    trivially 1.0 and the control could not fire).
    """
    if period not in _COMPOSITION_RESPONSE_PERIODS:
        raise ValueError(f"period {period} is outside the composition-response window")
    n = len(people_counts)
    if n == 0:
        raise ValueError("cannot take the mean daytime multiplier of an empty population")
    if len(weights) != n:
        raise ValueError("people_counts and weights must be the same length")
    if household_keys is None:
        household_keys = [""] * n
    if len(household_keys) != n:
        raise ValueError("household_keys must match people_counts")
    total = float(sum(weights))
    if not math.isfinite(total) or total <= 0.0:
        raise ValueError("population weights must sum to a positive finite value")
    base = occupancy_multiplier(occupancy_pattern, period)
    return sum(
        (weights[i] / total) * occupancy_multiplier(
            occupancy_pattern, period, people_count=people_counts[i],
            household_key=household_keys[i], seed=seed,
        ) / base
        for i in range(n)
    )


def daytime_shape_is_mean_neutral(people_counts: list[int], weights: list[float], *,
                                  occupancy_pattern: str = "single", period: int = 25,
                                  household_keys: list[str] | None = None,
                                  seed: int | None = None,
                                  tol: float = DAYTIME_SHAPE_BIAS_TOL) -> bool:
    """R15-failable control: True iff the daytime composition response is
    aggregate-neutral over the population. FIRES if the response is centred on
    a rate the population does not actually have (e.g. EFUS's headline 43%
    rather than this population's own 0.470 mean, which would lift daytime
    demand ~5%)."""
    return abs(
        population_mean_daytime_multiplier(
            people_counts, weights, occupancy_pattern=occupancy_pattern, period=period,
            household_keys=household_keys, seed=seed,
        ) - 1.0
    ) <= tol


# --- Asset adjustments ---
EV_CHARGING_KWH_PER_NIGHT = 8.0
EV_CHARGING_PERIODS = range(1, 9)  # 00:00-04:00, off-peak overnight charging

SOLAR_KWP = 3.5  # typical UK residential rooftop array size
SOLAR_PERFORMANCE_FACTOR = 0.85  # inverter/system losses


def solar_generation_shape(irradiance_w_m2_periods: list[float], kwp: float = SOLAR_KWP) -> list[float]:
    """Convert 48 half-hourly irradiance values (W/m^2, e.g. from
    `sim.weather_engine.half_hourly_solar_irradiance`) to kWh generated by a
    `kwp`-rated rooftop array over each half-hour period."""
    return [(irr / 1000.0) * kwp * SOLAR_PERFORMANCE_FACTOR * 0.5 for irr in irradiance_w_m2_periods]


def build_demand_shape(
    base_shape: list[float],
    mean_temp_c: float,
    commodity: str,
    property: dict,
    irradiance_w_m2_periods: list[float] | None = None,
) -> list[float]:
    """Apply weather, occupancy, and asset adjustments to a 48-period base
    consumption shape (e.g. `sim.profile_class_1.load_pc1_shape()`).

    commodity: "electricity" or "gas".
    property: a `saas.property_model.build_properties()` record —
        `heating_system`, `occupancy_pattern`, and `assets` are used, plus
        the W2_13 occupancy fields where present: `people_count`
        (primary key for both occupancy responses), `children_count`,
        `pensioner_present`, `someone_employed`, and `customer_id` /
        `premise_id` (the C-S2 substream key). A record without
        `people_count` gets exactly the pre-W2_13 result.
    irradiance_w_m2_periods: 48 half-hourly irradiance values, required only
        if `property["assets"]["solar"]` is set and commodity is
        "electricity" — ignored otherwise.

    Returns a new 48-length list of kWh values, floored at 0. `base_shape`
    is not mutated.
    """
    hdd = heating_degree_days(mean_temp_c)
    cdd = cooling_degree_days(mean_temp_c)
    shape = list(base_shape)
    heating_system = property["heating_system"]

    if commodity == "gas":
        if heating_system == "gas_boiler" and hdd > 0:
            extra = hdd * GAS_HEATING_KWH_PER_DEGREE_DAY
            shape = [s + extra * w for s, w in zip(shape, HEATING_PERIOD_WEIGHTS)]
    else:
        if hdd > 0 and heating_system in ELEC_HEATING_KWH_PER_DEGREE_DAY:
            extra = hdd * ELEC_HEATING_KWH_PER_DEGREE_DAY[heating_system]
            shape = [s + extra * w for s, w in zip(shape, HEATING_PERIOD_WEIGHTS)]
        if cdd > 0:
            extra = cdd * ELEC_COOLING_KWH_PER_DEGREE_DAY
            shape = [s + extra * w for s, w in zip(shape, COOLING_PERIOD_WEIGHTS)]

    # --- Occupancy (W2_13): SHAPE then VOLUME, one call site, two responses.
    # `people_count` absent (SME defaults, legacy fixtures) → both terms
    # collapse to the pre-W2_13 behaviour exactly.
    occupancy_pattern = property["occupancy_pattern"]
    people_count = property.get("people_count")
    children_count = property.get("children_count", 0) or 0
    household_key = property.get("customer_id") or property.get("premise_id") or ""
    shape = [
        s * occupancy_multiplier(
            occupancy_pattern, p,
            people_count=people_count,
            children_count=children_count,
            pensioner_present=property.get("pensioner_present"),
            someone_employed=property.get("someone_employed"),
            household_key=household_key,
        )
        for p, s in enumerate(shape, start=1)
    ]
    if people_count is not None:
        # VOLUME scales the base level (base profile + heating/cooling load).
        # NEED's medians are whole-household annual totals INCLUDING space and
        # water heating, so the anchor applies to the heated shape. It is
        # applied BEFORE the asset terms below: EV charging and solar export
        # are asset-driven, not people-driven, and must not be scaled by
        # headcount.
        volume_factor = occupancy_volume_factor(
            people_count, commodity,
            children_count=children_count, household_key=household_key,
        )
        shape = [s * volume_factor for s in shape]

    if commodity == "electricity":
        assets = property.get("assets", {})
        if assets.get("ev"):
            per_period = EV_CHARGING_KWH_PER_NIGHT / len(EV_CHARGING_PERIODS)
            for p in EV_CHARGING_PERIODS:
                shape[p - 1] += per_period
        if assets.get("solar") and irradiance_w_m2_periods is not None:
            generation = solar_generation_shape(irradiance_w_m2_periods)
            shape = [max(0.0, s - g) for s, g in zip(shape, generation)]

    return [max(0.0, s) for s in shape]
