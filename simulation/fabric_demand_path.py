"""The fabric physics IN the settlement path — W1_11/W1_12 -> the shipped demand seam.

PURPOSE
-------
`simulation.fabric_physics` (W1_11) and `simulation.premise_trace` (W1_12) built a
per-premise, physically-driven half-hourly trace, and `tools/couple_fabric.py`
measured the company's belief against it on a *side panel*. Neither reached the
demand path the company actually settles, bills and hedges on: that path still
rescales one national PC1 shape per customer per day. This module is the seam that
closes it. It turns a customer + the household register + the real weather archive
into the SAME `shape_fn(date_str) -> [48 kWh]` callable every term-pricing path in
`run_phase2b` already consumes, so the provider changes and no consumer does.

That is the whole of W1_11's stated L2->L3 step: with this wired, a company
capability (EAC estimation, hedging, billing, imbalance) faces the fabric world, and
the belief-vs-truth gap is a number measured on the SHIPPED path rather than on a
harness panel standing beside it.

GUARANTEES
----------
1. **No double count.** The trace already contains space heating fuel, hot water,
   appliances, lighting, base load, EV charging and PV generation. For a
   fabric-driven customer the legacy overlay stack — `build_demand_shape`'s HDD/CDD
   heating term, occupancy shape/volume, EV and solar, plus `run_phase2b`'s EPC
   consumption multiplier, ASHP uplift and overnight-EV overlay — is REPLACED, never
   stacked on top. `overlays_are_mutually_exclusive` is the failable control.
2. **No fail-open.** Eligibility is decided up front from real fields
   (`fabric_eligibility`). A customer that IS eligible and whose trace cannot be
   built RAISES; there is no `except: return legacy_shape` anywhere here. A date the
   archive does not cover raises rather than returning zeros — a settlement day of
   zero demand would price as a real (and free) day.
3. **The LCT timeline survives.** The household record changes across the window
   (boiler replacement, solar install, EV acquisition, income stress). The trace is
   generated in contiguous SEGMENTS of a constant household with the thermal state
   CHAINED across each boundary, while the behaviour profile and the away-day
   calendar are drawn ONCE over the whole window — so acquiring an EV cannot
   silently re-roll who lives there or when they go on holiday.
4. **Determinism / C-S2.** Everything here is a pure function of
   `(customer_id, household sequence, weather, seed)`. No global RNG is touched; the
   draws happen inside `premise_trace`'s own named substream.

WHY THIS SHAPE
--------------
The alternative — pushing fabric physics down into `demand_model.build_demand_shape`
— would have to invent a base shape to rescale and would keep the additive overlay
stack that is precisely the smoothing artefact being removed. Replacing the
*provider* at the `shape_fn` seam leaves settlement, billing, hedging and reporting
untouched, and makes the change reversible by one predicate
(`fabric_eligibility(...).is_eligible`).

R12 / R13 PRE-COMMITMENT (recorded BEFORE any downstream number was looked at)
-----------------------------------------------------------------------------
This is a BASELINE fidelity change, decided blind to company P&L. A real premise is
spikier than a rescaled national average and its annual level is set by its fabric
rather than by a declared EAC, so **imbalance cost and net margin will very likely
get WORSE, and per-customer volumes will move materially**. That is the correct
consequence of removing a smoothing artefact and an assumed level. It must not be
treated as a regression, and nothing here may be tuned to bring the old numbers
back (R12: the margin is a diagnostic, never a target).

EPISTEMIC NOTE
--------------
SIM-side generation only. This module imports no `company.*` or `saas.*` state. The
company continues to observe metered totals through its own interfaces; the fabric
parameters, the away-day calendar and the comfort constraint never cross the wall.
"""

from __future__ import annotations

import datetime as dt
import math
from dataclasses import dataclass
from typing import Callable, Mapping, Sequence

from simulation.fabric_physics import (
    PERIODS_PER_DAY,
    ThermalState,
    texture_is_not_a_rescaled_shape,
)
from simulation.household import Household
from simulation.premise_trace import (
    REFERENCE_UNIT_PRICE_P_PER_KWH,
    ComfortConstraint,
    TraceWeatherDay,
    away_day_calendar,
    behaviour_profile_for,
    comfort_constraint_for,
    generate_premise_trace,
    load_trace_weather,
)

# The seed for the settlement-path traces. Distinct from `couple_fabric`'s panel
# seed (17) on purpose: the panel and the shipped book are different populations
# and must not accidentally share draws.
DEFAULT_TRACE_SEED = 2016


# ---------------------------------------------------------------------------
# Eligibility — decided up front, from real fields, with the reason recorded
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FabricEligibility:
    """Why a customer is (or is not) driven by fabric physics.

    The reason is carried rather than discarded so a customer silently dropping
    back to the legacy path is visible in the run, not inferred from its numbers.
    """

    customer_id: str
    is_eligible: bool
    reason: str


def fabric_eligibility(
    customer: Mapping,
    household: Household | None,
    *,
    is_half_hourly_metered: bool,
    weather_available: bool,
) -> FabricEligibility:
    """The eligibility predicate. Fabric-driven demand requires a DOMESTIC premise
    with a household record and a weather archive; everything else keeps the legacy
    provider and says so.

    Half-hourly-metered customers are excluded because their demand is READ from
    actual metered data, which outranks any generator — replacing a real read with a
    simulated trace would be a fidelity loss dressed up as a gain.
    """
    cid = str(customer.get("customer_id", ""))
    if not cid:
        raise ValueError("a customer record without a customer_id cannot be classified")
    if is_half_hourly_metered:
        return FabricEligibility(cid, False, "half-hourly metered: real reads outrank a generator")
    if household is None:
        return FabricEligibility(cid, False, "no household record in the register")
    if not household.is_residential:
        return FabricEligibility(cid, False, f"non-domestic premise ({household.property_type})")
    if household.bedrooms is None:
        return FabricEligibility(cid, False, "no bedroom count: the occupancy prior cannot be drawn")
    if not weather_available:
        return FabricEligibility(cid, False, "no weather archive for this customer's location")
    return FabricEligibility(cid, True, "domestic premise with fabric parameters and local weather")


# ---------------------------------------------------------------------------
# Household segmentation — the LCT timeline, preserved
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class HouseholdSegment:
    """A contiguous run of days over which the household record does not change,
    within a single calendar year.

    The calendar-year boundary is a segment boundary as well as a life-event one
    because the prebound response below is re-evaluated annually, when the household
    has had a year's worth of bills to react to.
    """

    household: Household
    year: int
    start_index: int
    end_index: int  # exclusive

    @property
    def n_days(self) -> int:
        return self.end_index - self.start_index


def household_segments(
    household_at_date: Callable[[str], Household | None], dates: Sequence[dt.date]
) -> list[HouseholdSegment]:
    """Split the window into contiguous runs of an unchanged household record within
    one calendar year.

    A life event (boiler replacement, solar install, EV acquisition, a change of
    income stress) starts a new segment, as does 1 January. Raises on an empty window
    or a missing household rather than returning an empty segment list — a book of no
    segments would generate a trace of no days and price as a customer who used
    nothing.
    """
    if not dates:
        raise ValueError("cannot segment an empty window")
    segments: list[HouseholdSegment] = []
    current: Household | None = None
    current_year = dates[0].year
    start = 0
    for index, day in enumerate(dates):
        household = household_at_date(day.isoformat())
        if household is None:
            raise ValueError(f"no household record on {day.isoformat()}: cannot build a fabric trace")
        if current is None:
            current = household
        elif household != current or day.year != current_year:
            segments.append(HouseholdSegment(current, current_year, start, index))
            current = household
            current_year = day.year
            start = index
    segments.append(HouseholdSegment(current, current_year, start, len(dates)))
    return segments


# ---------------------------------------------------------------------------
# The series
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FabricDemandSeries:
    """One customer's fabric-driven half-hourly demand across the whole window.

    `gross_electricity_kwh` is consumption BEFORE on-site PV, and
    `pv_generation_kwh` is the generation, kept separate so a caller that dispatches
    a battery can net them itself — exactly the composition the legacy path uses.
    """

    customer_id: str
    heating_commodity: str
    gross_electricity_kwh: dict[str, list[float]]
    pv_generation_kwh: dict[str, list[float]]
    gas_kwh: dict[str, list[float]]
    segments: tuple[HouseholdSegment, ...]
    annual_electricity_kwh: float
    annual_gas_kwh: float
    constraint_by_year: dict[int, ComfortConstraint]
    """The comfort constraint each calendar year was generated under — the prebound
    response, recorded rather than discarded so it can be read back and judged."""

    def dates(self) -> list[str]:
        return sorted(self.gross_electricity_kwh)


def build_fabric_series(
    *,
    customer_id: str,
    household_at_date: Callable[[str], Household | None],
    weather: Sequence[TraceWeatherDay],
    latitude_deg: float,
    seed: int = DEFAULT_TRACE_SEED,
    reference_unit_price_p_per_kwh: float = REFERENCE_UNIT_PRICE_P_PER_KWH,
) -> FabricDemandSeries:
    """Generate one customer's whole-window fabric trace, segment by segment.

    The behaviour profile and the away-day calendar are drawn ONCE, from the FIRST
    segment's household and over the FULL window, and passed into every segment: a
    life event changes the building and the money, never the occupants' routine or
    the holidays they had already booked. The thermal state chains across segment
    boundaries, so a boiler swap on 3 March does not reset the walls to setback.

    THE PREBOUND CHANNEL, FED
    -------------------------
    `premise_trace.comfort_constraint_for` already implements the bill-pressure half
    of the prebound response — and NO caller supplied `prior_year_bill_gbp`, so on the
    settlement path it was a live mechanism with a dead input: every household heated
    to full comfort no matter what its dwelling cost to run. That is what makes an
    uninsulated solid-wall detached simulate at its SAP-theoretical demand, which is
    precisely where the empirical prebound gap is largest.

    So each calendar year's constraint is built from the PREVIOUS year's heating
    bill, computed here from the trace's own kWh at a published reference price. The
    first year has no prior bill and is generated unconstrained, which is honest: the
    household has not yet had one. No coefficient of the response is touched — 0.35
    per unit of bill pressure and the £1,200 affordability reference are
    `premise_trace`'s, fixed before any number in this book was looked at, and
    re-tuning either to move an outcome would be the R12 defect this note exists to
    forbid.

    TWO SIMPLIFICATIONS, REGISTERED
    -------------------------------
    (1) the reference price is FIXED, so the household shows no response to the
    2021-22 crisis prices it actually paid — closing that needs the tariff the
    company charged, i.e. a demand<->price coupling that belongs to W1_12, not to
    this seam; (2) the bill is priced at a GAS reference rate, so an electrically
    heated premise's bill is understated here and its prebound response correspondingly
    weak. Both are recorded, not hidden: the whole book is gas-heated today.
    """
    if not weather:
        raise ValueError("cannot build a fabric series with no weather days")
    if not (reference_unit_price_p_per_kwh > 0):
        raise ValueError("the reference unit price must be positive")
    dates = [day.date for day in weather]
    segments = household_segments(household_at_date, dates)

    profile = behaviour_profile_for(customer_id, segments[0].household, seed=seed)
    away = away_day_calendar(customer_id, profile, dates, seed=seed)

    gross: dict[str, list[float]] = {}
    pv: dict[str, list[float]] = {}
    gas: dict[str, list[float]] = {}
    constraint_by_year: dict[int, ComfortConstraint] = {}
    heating_kwh_by_year: dict[int, float] = {}
    state: ThermalState | None = None
    heating_commodity = ""
    for segment in segments:
        prior = heating_kwh_by_year.get(segment.year - 1)
        constraint = comfort_constraint_for(
            income_stress=segment.household.income_stress,
            prior_year_bill_gbp=(
                None if prior is None else prior * reference_unit_price_p_per_kwh / 100.0
            ),
        )
        constraint_by_year[segment.year] = constraint
        trace = generate_premise_trace(
            premise_id=customer_id,
            household=segment.household,
            weather=weather[segment.start_index : segment.end_index],
            seed=seed,
            behaviour=profile,
            constraint=constraint,
            away_days=away,
            latitude_deg=latitude_deg,
            initial_state=state,
        )
        state = trace.final_state
        heating_commodity = trace.heating_commodity
        for day in trace.days:
            key = day.date.isoformat()
            gross[key] = list(day.electricity_kwh)
            pv[key] = list(day.pv_generation_kwh)
            gas[key] = list(day.gas_kwh)
            heating_kwh_by_year[segment.year] = heating_kwh_by_year.get(segment.year, 0.0) + (
                day.gas_total_kwh if heating_commodity == "gas" else day.electricity_total_kwh
            )

    n_days = len(dates)
    return FabricDemandSeries(
        customer_id=customer_id,
        heating_commodity=heating_commodity,
        gross_electricity_kwh=gross,
        pv_generation_kwh=pv,
        gas_kwh=gas,
        segments=tuple(segments),
        annual_electricity_kwh=sum(sum(v) for v in gross.values()) / n_days * 365.25,
        annual_gas_kwh=sum(sum(v) for v in gas.values()) / n_days * 365.25,
        constraint_by_year=constraint_by_year,
    )


def build_fabric_series_for_site(
    *,
    customer_id: str,
    household_at_date: Callable[[str], Household | None],
    weather_site: str,
    latitude_deg: float,
    start: dt.date,
    end: dt.date,
    seed: int = DEFAULT_TRACE_SEED,
) -> FabricDemandSeries:
    """`build_fabric_series` against the real Open-Meteo archive for a location.

    The archive read is deliberately not wrapped: a missing or short archive raises
    in `load_trace_weather`, because a trace built on invented weather would settle
    real money against a number with no meaning.
    """
    weather = load_trace_weather(weather_site, start=start, end=end)
    return build_fabric_series(
        customer_id=customer_id,
        household_at_date=household_at_date,
        weather=weather,
        latitude_deg=latitude_deg,
        seed=seed,
    )


# ---------------------------------------------------------------------------
# The book-level provider set — ONE eligibility decision, shared by the runner
# and the measurement tool
# ---------------------------------------------------------------------------

# The two refusals below are NOT the same kind of thing, and conflating them is
# how a thrown switch un-throws itself in silence.
#
# A STRUCTURAL refusal (half-hourly metered, non-domestic, no household record) is
# a permanent property of the premise: that customer was never going to settle on
# fabric, and the legacy provider is the right answer forever.
#
# A COVERAGE refusal is a property of the ARCHIVE, not the premise. The premise is
# domestic, has fabric parameters and has local weather — it passed every
# structural test — and it is dropped back to the legacy rescaled-PC1 shape only
# because the weather file stops short of the settlement window. Extend the window
# by one day past the archive, or truncate the archive, and every fabric premise in
# the book silently reverts while `settlement_providers_match_eligibility` keeps
# returning True: nobody was declared eligible, so nobody failed to be switched.
# That is a FAIL-OPEN of exactly the R15 shape (a control that passes on an empty
# set), and it is why the marker exists and why the runner asserts on it separately.
COVERAGE_REFUSAL = "archive does not cover the settlement window"


def fabric_providers_for_book(
    *,
    customers: Sequence[Mapping],
    household_at_date: Callable[[str, str], Household | None],
    is_half_hourly_metered: Callable[[Mapping], bool],
    weather_site_for: Callable[[Mapping], str],
    weather_available: Callable[[str], bool],
    latitude_for: Callable[[Mapping], float],
    start: dt.date,
    end: dt.date,
    seed: int = DEFAULT_TRACE_SEED,
) -> tuple[dict[str, FabricDemandSeries], list[FabricEligibility]]:
    """Decide, ONCE for the whole book, which customers settle on fabric physics,
    and build their traces.

    `run_phase2b` (which settles real money in the sim) and
    `tools/fabric_settlement_gap` (which reports what switching does) must not be
    able to disagree about who is fabric-driven — a measurement of a different
    population from the one that settles is not a measurement of the switch. So the
    predicate, the segmentation and the trace generation all live here and both
    callers pass their own accessors in.

    COVERAGE IS PART OF ELIGIBILITY, decided up front. A customer whose weather
    archive does not span the whole settlement window is recorded INELIGIBLE with
    that reason and keeps the legacy provider, rather than being handed a
    `shape_fn` that raises on the first uncovered day halfway through a run. This
    is not the fail-open the module forbids: nothing silently substitutes a shape,
    the refusal is decided before any settlement happens, and the reason is carried
    into the run's own record where an unexplained population drop is visible.

    Returns `(series_by_customer_id, eligibility_for_every_customer)`. The second
    element covers EVERY customer passed in, eligible or not, so a caller can log
    the reason a premise is not fabric-driven instead of inferring it from an
    absence.
    """
    if end < start:
        raise ValueError(f"an empty settlement window ({start}..{end}) has no providers")
    window = [start + dt.timedelta(days=i) for i in range((end - start).days + 1)]

    series_by_customer: dict[str, FabricDemandSeries] = {}
    verdicts: list[FabricEligibility] = []
    for customer in customers:
        cid = str(customer.get("customer_id", ""))
        site = weather_site_for(customer)
        verdict = fabric_eligibility(
            customer,
            household_at_date(cid, start.isoformat()),
            is_half_hourly_metered=is_half_hourly_metered(customer),
            weather_available=weather_available(site),
        )
        if not verdict.is_eligible:
            verdicts.append(verdict)
            continue
        series = build_fabric_series_for_site(
            customer_id=cid,
            household_at_date=lambda d, _cid=cid: household_at_date(_cid, d),
            weather_site=site,
            latitude_deg=latitude_for(customer),
            start=start,
            end=end,
            seed=seed,
        )
        if not series_covers_window(series, window):
            verdicts.append(
                FabricEligibility(
                    cid,
                    False,
                    f"{COVERAGE_REFUSAL}: weather archive {site!r} does not cover the "
                    f"whole settlement window {start.isoformat()}..{end.isoformat()}",
                )
            )
            continue
        series_by_customer[cid] = series
        verdicts.append(verdict)
    return series_by_customer, verdicts


# ---------------------------------------------------------------------------
# The seam itself
# ---------------------------------------------------------------------------


def fabric_shape_fn(
    series: FabricDemandSeries,
    commodity: str = "electricity",
    *,
    battery_dispatch: Callable[[list[float], list[float], str], list[float]] | None = None,
) -> Callable[[str], list[float]]:
    """A `shape_fn(date_str) -> [48 kWh]` backed by the fabric trace.

    Contract-identical to `run_phase2b._weather_adjusted_shape_fn`'s return value,
    which is the point: every consumer (deemed/flex/fixed term pricing, demand
    response, settlement) keeps working unchanged.

    Electricity is returned NET of on-site PV and floored at zero, matching the
    legacy provider's treatment of solar. `battery_dispatch(gross, generation,
    date_str)` is the one composition left to the caller, because the battery is
    the single asset the trace generator does not model.

    A date outside the trace RAISES. The legacy provider falls back to an
    unadjusted base shape when weather is missing; doing the same here would settle
    a physically-driven customer against a national average for that day and hide it
    in the totals.
    """
    if commodity not in ("electricity", "gas"):
        raise ValueError(f"unknown commodity {commodity!r}")

    def shape_fn(date_str: str) -> list[float]:
        if commodity == "gas":
            try:
                return list(series.gas_kwh[date_str])
            except KeyError:
                raise KeyError(
                    f"{series.customer_id}: no fabric trace for {date_str}"
                ) from None
        try:
            gross = series.gross_electricity_kwh[date_str]
            generation = series.pv_generation_kwh[date_str]
        except KeyError:
            raise KeyError(f"{series.customer_id}: no fabric trace for {date_str}") from None
        if battery_dispatch is not None:
            return [max(0.0, v) for v in battery_dispatch(list(gross), list(generation), date_str)]
        return [max(0.0, g - p) for g, p in zip(gross, generation)]

    return shape_fn


# ---------------------------------------------------------------------------
# R15-failable controls
#
# Each RAISES on insufficient input rather than passing vacuously, and each has a
# named mutation in tests/simulation/test_fabric_demand_path.py that makes it fire.
# ---------------------------------------------------------------------------


# The legacy overlays a fabric-driven customer must NOT also receive, because the
# trace already contains each of them. Named rather than described so the control
# below compares against a list, not against a docstring.
LEGACY_OVERLAYS = (
    "hdd_heating_uplift",
    "epc_consumption_multiplier",
    "ashp_electricity_uplift",
    "overnight_ev_overlay",
    "solar_generation_offset",
    "occupancy_shape_and_volume",
)


def overlays_are_mutually_exclusive(
    fabric_driven: bool, applied_overlays: Sequence[str]
) -> bool:
    """GUARANTEE 1, as a failable predicate: True iff a fabric-driven customer
    received NONE of the legacy overlays.

    It FIRES the moment the wiring stacks the physical trace on top of an overlay
    that already accounts for the same energy — the double-count that would make a
    fabric-driven customer's bill silently wrong in the customer's favour or the
    company's. An unrecognised overlay name RAISES rather than passing: a control
    that ignores what it does not recognise is fail-open.
    """
    unknown = [name for name in applied_overlays if name not in LEGACY_OVERLAYS]
    if unknown:
        raise ValueError(f"unrecognised overlay(s) {unknown}: cannot judge the double-count")
    if not fabric_driven:
        return True
    return not applied_overlays


# The provider names a settled customer's demand can have come from. Named rather
# than described so the control below compares against a list.
FABRIC_PROVIDER = "fabric_physics"
LEGACY_PROVIDER = "legacy_pc1_rescaled"
METERED_PROVIDER = "hh_metered_reads"
DEMAND_PROVIDERS = (FABRIC_PROVIDER, LEGACY_PROVIDER, METERED_PROVIDER)


def settlement_providers_match_eligibility(
    provider_by_customer: Mapping[str, str],
    eligibility: Sequence[FabricEligibility],
) -> bool:
    """THE SWITCH ITSELF, as a failable predicate: True iff every customer the
    eligibility pass declared fabric-driven actually SETTLED on the fabric
    provider, and no other customer did.

    This is the control the wiring needed and did not have. `fabric_eligibility`
    deciding a customer is eligible has never made `run_phase2b` use the trace —
    the branch that chooses the provider is separate code, and a switch that is
    declared but not thrown reads identically to one that is thrown from
    everywhere except the settled numbers. It FIRES on a branch that computes the
    eligibility and then keeps the legacy shape, and on a branch that hands a
    fabric shape to a customer with no trace.

    Raises on an unrecognised provider name, on an empty book, and on a customer
    that SETTLED without ever being classified: a control that ignores what it
    cannot classify reports a clean switch on a book it did not check. The
    converse — a classified customer that never settled — is legitimate (a
    successor customer gated behind a churn event that did not fire) and is
    simply not judged.
    """
    unknown = sorted({p for p in provider_by_customer.values() if p not in DEMAND_PROVIDERS})
    if unknown:
        raise ValueError(f"unrecognised demand provider(s) {unknown}: cannot judge the switch")
    if not provider_by_customer:
        raise ValueError("a book with no settled customers is not a switched book")
    judged = {v.customer_id: v for v in eligibility}
    unclassified = sorted(set(provider_by_customer) - set(judged))
    if unclassified:
        raise ValueError(
            f"customers {unclassified} settled without an eligibility verdict: "
            "cannot judge whether the switch reached them"
        )
    for cid, provider in provider_by_customer.items():
        if (provider == FABRIC_PROVIDER) != judged[cid].is_eligible:
            return False
    return True


def coverage_refusals(eligibility: Sequence[FabricEligibility]) -> list[str]:
    """The customers that would have settled on fabric physics but for the weather
    archive stopping short of the settlement window.

    Separated from `settlement_providers_match_eligibility` on purpose: that control
    asks "did the switch reach everyone it was DECLARED for", and this one asks "was
    the declaration itself quietly emptied". A book where every fabric premise was
    coverage-refused satisfies the first control perfectly — nobody was declared, so
    nobody was missed — while settling the entire book on the rescaled national
    shape the switch exists to replace.

    Raises on an empty verdict list rather than returning `[]`: a book nothing was
    judged on has not been checked, and reporting "no coverage refusals" for it is
    the fail-silent half of the same defect.
    """
    if not eligibility:
        raise ValueError("no eligibility verdicts: the book was never judged for coverage")
    return sorted(
        v.customer_id
        for v in eligibility
        if not v.is_eligible and v.reason.startswith(COVERAGE_REFUSAL)
    )


def settled_shape_is_physically_textured(
    shape_fn: Callable[[str], list[float]],
    dates: Sequence[str],
    *,
    max_day_multiplicity: int | None = None,
) -> bool:
    """THE CONTROL ON THE SHAPE SETTLEMENT ACTUALLY RECEIVES, and the one the other
    two cannot be: they judge the LABEL and the DECLARATION, this judges the NUMBERS.

    `settlement_providers_match_eligibility` asks whether the customers declared
    fabric-driven carry the fabric provider name, and `coverage_refusals` asks
    whether that declaration was quietly emptied. BOTH PASS UNCHANGED on a book
    where `fabric_shape_fn` returns the rescaled national shape for every premise —
    the provider string is assigned by the same branch that builds the callable, so
    a label can never disagree with itself. That is the fail-open this closes: a
    switch is only thrown if the series arriving at settlement is texturally
    different from the artefact it replaces, and nothing on the shipped path
    checked that.

    WHY IT IS NOT ENOUGH THAT `fabric_physics` ALREADY CHECKS TEXTURE. The L1.5
    control `texture_is_not_a_rescaled_shape` runs inside the physics module on the
    RAW trace. Between that point and settlement the series passes through PV
    netting, battery dispatch and a zero floor (`fabric_shape_fn`), each of which
    can flatten or degenerate a day, and none of which is covered upstream. L3 for
    this atom is the claim that the company SETTLES on physics, so the control has
    to stand at the settlement seam and consume the same callable
    `run_phase2b` hands to term pricing — not a value computed beside it.

    Reuses the physics module's own measured threshold rather than inventing a
    second one, so there is exactly one definition of "this is a rescaled shape".

    Raises rather than passing on: fewer than two days (nothing to compare), a
    non-finite value, or an all-zero book (a premise settling at zero demand every
    day is not a textured premise, and `max(0.0, ...)` in `fabric_shape_fn` makes
    that reachable rather than theoretical).
    """
    if len(dates) < 2:
        raise ValueError(
            "a settled shape cannot be judged for texture on fewer than two days"
        )
    days: list[list[float]] = []
    for date_str in dates:
        day = list(shape_fn(date_str))
        if len(day) != 48:
            raise ValueError(
                f"settled shape for {date_str} has {len(day)} periods, not 48: "
                "this is not a settlement shape"
            )
        if any(not math.isfinite(v) for v in day):
            raise ValueError(
                f"settled shape for {date_str} contains a non-finite value: "
                "a NaN compares False against every threshold, so it must be "
                "rejected before the texture test, not by it"
            )
        days.append(day)
    if not any(v > 0.0 for day in days for v in day):
        raise ValueError(
            "every settled period is zero across the sampled window: a premise that "
            "settles at zero demand has no texture to judge and is not fabric-driven"
        )
    return texture_is_not_a_rescaled_shape(days, max_day_multiplicity=max_day_multiplicity)


def prebound_channel_is_fed(series: FabricDemandSeries) -> bool:
    """GUARANTEE: the prebound response is a LIVE input on the shipped path, not a
    mechanism with a dead argument.

    True iff a premise whose bill exceeds the affordability reference actually
    tightened its comfort constraint across the window. FIRES on the defect this
    seam was built to close — `prior_year_bill_gbp` left at None, so every household
    heats to full SAP comfort however expensive its dwelling is to run. It also fires
    if a future refactor stops threading the prior-year bill through.

    A premise whose bill never reaches the reference is legitimately unconstrained,
    so it is reported as satisfied — the control asks whether the CHANNEL works, not
    whether every household rations. Raises on a series with fewer than two years:
    a response to last year's bill is not observable in one year.
    """
    years = sorted(series.constraint_by_year)
    if len(years) < 2:
        raise ValueError("the prebound channel needs at least two years to be observable")
    intensities = [series.constraint_by_year[y].rationing_intensity for y in years]
    annual_bill = series.annual_gas_kwh if series.heating_commodity == "gas" else (
        series.annual_electricity_kwh
    )
    annual_bill *= REFERENCE_UNIT_PRICE_P_PER_KWH / 100.0
    if annual_bill <= _AFFORDABLE_BILL_REFERENCE_GBP:
        return True
    return max(intensities) > intensities[0] + 1e-9


# `premise_trace.comfort_constraint_for`'s own affordability reference, restated
# here ONLY so this control can decide whether a premise should have responded.
# Drift between the two is caught by
# tests/simulation/test_fabric_demand_path.py::test_the_affordability_reference_has_not_drifted.
_AFFORDABLE_BILL_REFERENCE_GBP = 1200.0


def series_covers_window(series: FabricDemandSeries, dates: Sequence[dt.date]) -> bool:
    """True iff the trace has a shape for EVERY settlement day in the window.

    FIRES on a gap. A missing day is not a small error: `shape_fn` raises on it
    mid-run, and a provider that silently skipped days would bill a customer for a
    shorter year than they lived. Raises on an empty window rather than passing —
    covering no days is not coverage.
    """
    if not dates:
        raise ValueError("an empty window is not covered by anything")
    return all(day.isoformat() in series.gross_electricity_kwh for day in dates)


def trace_carries_half_hourly_texture(series: FabricDemandSeries) -> bool:
    """True iff the electricity series still has WITHIN-DAY structure once the
    trace reaches the seam — i.e. the seam did not flatten what Layer 1 generated.

    This is the seam's own plumbing guard, deliberately NOT a restatement of the
    harness's texture cell (which this module must not know about, let alone
    import): it fires if a plumbing bug — a daily total spread evenly across 48
    periods, a stale list reused for every day — drained the texture between the
    generator and the settlement path. Raises on a series too short to have a
    distribution.
    """
    days = list(series.gross_electricity_kwh.values())
    if len(days) < 2:
        raise ValueError("half-hourly texture needs at least two days")
    flat_days = 0
    for day in days:
        if len(day) != PERIODS_PER_DAY:
            raise ValueError(f"a settlement day must have {PERIODS_PER_DAY} periods, got {len(day)}")
        span = max(day) - min(day)
        mean = sum(day) / len(day)
        if mean <= 0.0 or span / mean < 0.10:
            flat_days += 1
    return flat_days == 0
