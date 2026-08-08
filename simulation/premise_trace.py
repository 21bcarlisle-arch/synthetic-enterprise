"""Premise trace generator — Layer 2 of the two-layer premise demand engine (W1_12).

PURPOSE
-------
Turn one premise's *behaviour* — who is in, when they heat, what they switch on,
when they go away, and how hard the bill is squeezing them — into per-premise
**half-hourly gas and electricity traces**, by driving W1_11's fabric physics
rather than by rescaling a stored national shape.

GUARANTEES
----------
1. **The separability contract is the hard requirement, and it is TESTED.**
   Layer 1 (`simulation.fabric_physics`) is a pure function of
   `(fabric, weather, assets, setpoint schedule)` and knows nothing of segments,
   engagement, psychology or tariffs. Layer 2's ENTIRE influence on Layer 1 is
   the three fields of `LayerTwoInputs` — setpoint schedule, gain profile `Phi_p`,
   and the income/comfort constraint. There is exactly ONE call into Layer 1 in
   this module (`fabric_physics.simulate_day`) and it is fed from that dataclass.
   Two controls make the contract falsifiable rather than conventional:
   `fabric_only_moves_level_and_character` and
   `behaviour_only_moves_timing_and_volume`.
2. **Texture is generated, never injected.** Nothing here adds per-period noise to
   an output series. Half-hourly texture comes from DISCRETE EVENTS with physical
   power ratings and durations (a kettle is 2.8 kW for three minutes; an oven is
   2 kW for three quarters of an hour) plus the Layer 1 burner duty cycle. An
   empty house is representable: on an away day the premise falls to base load,
   which is the only way L1.3's trough requirement can be met honestly.
3. **Determinism / C-S2.** Every draw comes from this module's OWN named seeded
   substream (`STREAM_NAME`), salted per premise AND per day, so (a) a draw here
   can never shift another subsystem's sequence, and (b) any single day is
   reproducible without replaying the days before it (thermal state excepted,
   which chains by design).

THE BLOCKING QUESTION THE FRAME TOLD US TO ANSWER FIRST — ANSWERED, MEASURED
---------------------------------------------------------------------------
The FRAME (`maturity_map.yaml`, W1_12, 2026-08-03) said the computational cost of
a per-premise 2R2C simulation across the full book "is plausibly the BINDING
constraint on this atom's design and may force an archetype-and-perturb approach
rather than true per-premise simulation. Answer it at this atom's FRAME close
before any BUILD shape is fixed."

`observed 2026-08-03, measured on the project hardware` (i5-13400F, CPython,
single core, real Open-Meteo archive `sim/weather_data/C1.csv`, 3,446 days,
four fabric archetypes): **0.438 s per premise-year**, 1.20 ms per premise-day,
25 us per settlement period. Spread across archetypes is small (0.42–0.48 s);
the cost is set by the 1,440 sub-steps/day, not by the fabric.

| book | premise-years | CPU cost | 16-thread wall |
|---|---|---|---|
| **9 distinct domestic premises (the book that actually exists)** | 85 | **37 s** | seconds |
| 18 records incl. gas twins | 170 | 74 s | seconds |
| 1,000 | 9,400 | 1.1 h | 4 min |
| 100,000 | 943,000 | 4.8 CPU-days | 7.2 h |

**Verdict: TRUE PER-PREMISE. Archetype-and-perturb is NOT taken.** The measured
headroom at the real book size is ~3 orders of magnitude (37 seconds against a
sim run measured in minutes), so cost cannot be the thing that decides this
atom's shape — and archetype-and-perturb has a *fidelity* cost that is fatal
here, not merely unattractive: sharing one Layer 1 solve between premises is
precisely the "clone one home N times" mutation the harness spec names as the
defect for L2.1 and L2.2. Buying speed we do not need with the exact defect the
programme exists to remove would be indefensible.

The decision is recorded so it can be RE-decided, not assumed: `PREMISE_YEAR_
SECONDS_MEASURED` + `estimate_book_cost()` make the cost model explicit and
re-measurable, and the crossing point is stated — per-premise stays under one
CPU-hour to ~870 premises over the ten-year window, and the generator is a pure
function per premise (no shared state), so a process pool is the first lever
long before archetyping is. Full working: `docs/design/PREMISE_TRACE_SIZING_AND_
BUILD_NOTE.md`.

GAS — HALF-HOURLY BY CONSTRUCTION, DAILY BY EVIDENCE (binding, from the FRAME)
-----------------------------------------------------------------------------
The 2R2C model produces `Phi_h` every step regardless, so the gas trace here is
half-hourly and truncating it would discard information the model already has.
But public anchor data for half-hourly DOMESTIC gas texture is far weaker than
for electricity, so the controls in this module hold gas to DAILY targets only —
annual level, seasonal ratio, per-home HDD-response gradient, day-to-day
variability. **Half-hourly gas texture is registered as an explicitly UNVALIDATED
SIMPLIFICATION** on the atom. That is a recorded refusal to claim fidelity
without an anchor, not an oversight.

R12 / R13 PRE-COMMITMENT (recorded BEFORE any downstream number was looked at)
-----------------------------------------------------------------------------
This is a BASELINE fidelity change decided blind to company P&L. Real premise
traces are spikier than a rescaled national average, so imbalance cost and margin
will very likely get WORSE when this is wired into the demand path. That is the
CORRECT consequence of removing a smoothing artefact and must not be treated as a
regression or tuned back. No band in this module is a target (R12).

ANCHOR INDEPENDENCE
-------------------
Ofgem TDCV (published typical domestic consumption values) and NEED are used to
JUDGE annual level and spread; they are never used to parameterise anything here.
The appliance catalogue is parameterised from equipment power ratings and usage
frequencies (`domain-knowledge`), which are not the same source. SAP/RdSAP
parameterises Layer 1 and judges nothing.

EPISTEMIC NOTE
--------------
SIM-side generation. It reads no `company.*` or `saas.*` state and exposes no
simulation internal: the company sees metered totals through its own interfaces,
never the `ComfortConstraint`, the away-day calendar or the appliance event list.
"""

from __future__ import annotations

import csv
import datetime as dt
import hashlib
import math
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Mapping, Sequence

from simulation.fabric_physics import (
    DEFAULT_DEADBAND_C,
    DEFAULT_LATITUDE_DEG,
    PERIODS_PER_DAY,
    DailyWeather,
    FabricParameters,
    HeatingSchedule,
    HeatSource,
    ThermalState,
    daylight_hours,
    fabric_parameters,
    heat_pump_cop,
    heat_source_for,
    heating_schedule_for,
    reconstruct_ambient_profile,
    reconstruct_irradiance_profile,
    simulate_day,
    solar_declination_deg,
    solar_elevation_sin,
)
from simulation.household import (
    HeatingSystem,
    Household,
    IncomeStress,
    InsulationLevel,
    PropertyType,
)

STREAM_NAME = "W1_12_premise_trace"

PERIOD_HOURS = 0.5

# `observed 2026-08-03` — measured on the project hardware, four archetypes, the
# real 3,446-day weather archive. A MEASURED CONSTANT, not a budget or a target:
# it exists so the sizing decision above can be re-checked rather than believed.
PREMISE_YEAR_SECONDS_MEASURED = 0.438
PREMISE_YEAR_SECONDS_MEASURED_ON = "i5-13400F / CPython / single core / 2026-08-03"


# ---------------------------------------------------------------------------
# C-S2 — this module's own named substream
# ---------------------------------------------------------------------------


def _substream(base_seed: int, salt: str = "") -> random.Random:
    """An ISOLATED `random.Random` seeded from a STABLE sha256 of
    (`STREAM_NAME`::`salt`::`base_seed`).

    Shares no state with the global `random`, with W1_11's substream, or with any
    other subsystem, so no draw here can shift another sequence (C-S2).
    """
    key = f"{STREAM_NAME}::{salt}::{base_seed}".encode("utf-8")
    return random.Random(int.from_bytes(hashlib.sha256(key).digest()[:8], "big"))


def _base_seed_for(premise_id: str, seed: int | None) -> int:
    key = premise_id if seed is None else f"{premise_id}::{seed}"
    return int.from_bytes(hashlib.md5(key.encode("utf-8")).digest()[:8], "big")


def _require_finite(name: str, value: float) -> float:
    """Reject non-finite input FIRST — `abs(nan) <= tol` is False by luck, not by
    design, so every guard in this module rejects NaN/inf before comparing."""
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(float(value)):
        raise ValueError(f"{name} must be a finite number, got {value!r}")
    return float(value)


# ---------------------------------------------------------------------------
# Weather input (the real daily archive, plus the day it fell on)
# ---------------------------------------------------------------------------

WEATHER_DATA_DIR = Path(__file__).resolve().parents[1] / "sim" / "weather_data"


@dataclass(frozen=True)
class TraceWeatherDay:
    """One archive day, carrying the CALENDAR date as well as the weather.

    Layer 2 needs the date that `DailyWeather` does not carry: weekday/weekend
    behaviour and the away-day calendar are day-of-week and year facts.
    """

    date: dt.date
    weather: DailyWeather

    @property
    def is_weekend(self) -> bool:
        return self.date.weekday() >= 5


def load_trace_weather(
    location_id: str,
    *,
    start: dt.date | None = None,
    end: dt.date | None = None,
    directory: Path | None = None,
) -> list[TraceWeatherDay]:
    """Read `sim/weather_data/{location_id}.csv` — the REAL Open-Meteo reanalysis
    archive (Historical Ground Truth). Raises if the file is absent: a missing
    weather file must FAIL, never silently produce an empty (vacuously passing)
    trace."""
    path = (directory or WEATHER_DATA_DIR) / f"{location_id}.csv"
    if not path.exists():
        raise FileNotFoundError(f"no weather archive for location {location_id!r} at {path}")
    days: list[TraceWeatherDay] = []
    with path.open(newline="") as handle:
        for row in csv.DictReader(handle):
            date = dt.date.fromisoformat(row["date"])
            if start is not None and date < start:
                continue
            if end is not None and date > end:
                continue
            days.append(
                TraceWeatherDay(
                    date=date,
                    weather=DailyWeather(
                        day_of_year=date.timetuple().tm_yday,
                        temperature_min_c=float(row["temperature_min_c"]),
                        temperature_max_c=float(row["temperature_max_c"]),
                        temperature_mean_c=float(row["temperature_mean_c"]),
                        cloud_cover_pct=float(row["cloud_cover_pct"]),
                    ),
                )
            )
    if not days:
        raise ValueError(f"weather archive {path} yielded no days in the requested window")
    return days


# ---------------------------------------------------------------------------
# Layer 2 — the behaviour profile (STRUCTURAL: drawn once per premise)
# ---------------------------------------------------------------------------

# `domain-knowledge` — occupancy priors. `Household` carries no headcount, so it
# is drawn from bedrooms unless a caller supplies the existing segmentation
# fields (`people_count` etc.), which attach here UNCHANGED, per the FRAME.
_PEOPLE_BY_BEDROOMS: dict[int, tuple[float, ...]] = {
    1: (1.0, 1.0, 2.0),
    2: (1.0, 2.0, 2.0, 3.0),
    3: (2.0, 2.0, 3.0, 3.0, 4.0),
    4: (2.0, 3.0, 4.0, 4.0, 5.0),
    5: (3.0, 4.0, 5.0, 6.0),
}

# `domain-knowledge` — ONS/BEIS holiday-taking: most UK households take two to
# three trips a year. A CANDIDATE TO VERIFY against a published source, not a
# settled constant; it is the parameter L1.3 (an empty house must be
# representable) is most sensitive to.
_AWAY_DAYS_PER_YEAR_RANGE = (6, 26)
_AWAY_BLOCK_LENGTH_RANGE = (2, 12)
AWAY_SETPOINT_C = 12.0
"""Frost-protection setpoint while the premise is empty. Not zero: a real house
is left on frost protection, and asserting zero would make away days trivially
detectable in a way real meter data is not."""

# `domain-knowledge` — households keep HABITS, and the habit is the household's,
# not the nation's. Some homes sit down to eat at 17:30, some at 20:30, and each
# does so on MOST days. An appliance window like the oven's (32, 42) is the
# population ENVELOPE; it is not any single household's clock.
#
# Drawing each day's start uniformly from that envelope gives every home a
# different day-to-day timing but the SAME long-run centre — the envelope mean.
# In population terms that is a point mass, which is the identical defect L2.3
# exists to catch (`HEATING_PERIOD_WEIGHTS` as one national constant), one level
# subtler: it hides behind within-home variation instead of being visibly
# constant. The routine offset is what makes the centre the HOUSEHOLD'S.
#
# The systematic part is the part that has a reason: retired households eat
# earlier, commuting households later, and children pull the evening meal
# forward. The idiosyncratic part is everything else about a family's clock.
_ROUTINE_RETIRED_PERIODS = -1.5
_ROUTINE_COMMUTER_PERIODS = 1.0
_ROUTINE_CHILDREN_PERIODS = -0.5
_ROUTINE_IDIOSYNCRATIC_SD_PERIODS = 1.0
_MAX_ROUTINE_OFFSET_PERIODS = 3.0
"""+/- three half-hours. With an ~18:45 envelope centre that spans roughly
17:15-20:15, which is the realistic UK spread of the evening main meal. It is a
DIAGNOSTIC envelope drawn from domain knowledge, never a value chosen to move
L2.3 (R12) — the population sd it implies is a consequence, not a target."""


@dataclass(frozen=True)
class BehaviourProfile:
    """One premise's own behavioural structure. Drawn ONCE per premise from this
    module's substream — never re-drawn per period, so between-premise diversity
    is structural rather than sprinkled."""

    people_count: int
    children_count: int
    pensioner_present: bool
    someone_employed: bool
    wake_period: int
    """Half-hour index at which the household gets up on a weekday."""
    sleep_period: int
    weekend_shift_periods: int
    daytime_occupancy: float
    """Fraction of the working day for which somebody is at home."""
    away_days_per_year: int
    appliance_intensity: float
    """Sublinear scale on event rates with household size."""
    routine_offset_periods: float = 0.0
    """This household's habitual shift, in half-hours, of its discretionary
    activity relative to the national envelope — the home's own clock.

    Drawn ONCE per premise and applied every day, so it is a HABIT rather than
    noise: it moves the home's long-run centre, which is what distinguishes two
    households from each other, while leaving each home's day-to-day variation
    intact. It drives both fuels — a household that eats at 20:30 also heats at
    20:30 — so it is read by `draw_appliance_events`, `draw_dhw_events` and
    `daily_schedule` alike, and never re-drawn in any of them."""

    @property
    def adult_count(self) -> int:
        return max(1, self.people_count - self.children_count)


def behaviour_profile_for(
    premise_id: str,
    household: Household,
    *,
    seed: int | None = None,
    people_count: int | None = None,
    children_count: int | None = None,
    pensioner_present: bool | None = None,
    someone_employed: bool | None = None,
) -> BehaviourProfile:
    """Draw a premise's behavioural structure.

    The existing segmentation fields (`people_count`, `children_count`,
    `pensioner_present`, `someone_employed`) attach UNCHANGED where a caller has
    them — the fabric layer must not fork the segmentation programme. Where they
    are absent they are drawn from bedrooms.
    """
    base = _base_seed_for(premise_id, seed)
    bedrooms = 2 if household.bedrooms is None else max(1, min(5, household.bedrooms))

    if people_count is None:
        people_count = int(_substream(base, "people").choice(_PEOPLE_BY_BEDROOMS[bedrooms]))
    people_count = max(1, int(people_count))
    if children_count is None:
        children_count = (
            _substream(base, "children").randint(0, max(0, people_count - 1))
            if people_count >= 3
            else 0
        )
    children_count = max(0, min(int(children_count), people_count - 1))
    if pensioner_present is None:
        pensioner_present = _substream(base, "pensioner").random() < 0.22
    if someone_employed is None:
        someone_employed = not pensioner_present or _substream(base, "employed").random() < 0.25

    rise = _substream(base, "rise")
    # Weekday rise 05:30–08:30, retire 21:30–24:00 (half-hour indices).
    wake_period = rise.randint(11, 17)
    sleep_period = rise.randint(43, 47)
    weekend_shift = rise.randint(1, 4)

    # Daytime occupancy: a pensioner or non-working household is largely in; a
    # fully-employed household largely out.
    occ = _substream(base, "daytime")
    if pensioner_present and not someone_employed:
        daytime = occ.uniform(0.70, 0.95)
    elif someone_employed and children_count == 0:
        daytime = occ.uniform(0.05, 0.35)
    else:
        daytime = occ.uniform(0.25, 0.65)

    away = _substream(base, "away_days").randint(*_AWAY_DAYS_PER_YEAR_RANGE)
    if pensioner_present:
        away = int(away * 0.7)

    # The household's own clock. Structural, drawn once, from its own substream:
    # two premises differ in WHEN they live, not only in how much they use.
    systematic = 0.0
    if pensioner_present and not someone_employed:
        systematic += _ROUTINE_RETIRED_PERIODS
    elif someone_employed:
        systematic += _ROUTINE_COMMUTER_PERIODS
    if children_count > 0:
        systematic += _ROUTINE_CHILDREN_PERIODS
    routine_offset = systematic + _substream(base, "routine").gauss(
        0.0, _ROUTINE_IDIOSYNCRATIC_SD_PERIODS
    )
    routine_offset = max(
        -_MAX_ROUTINE_OFFSET_PERIODS, min(_MAX_ROUTINE_OFFSET_PERIODS, routine_offset)
    )

    return BehaviourProfile(
        people_count=people_count,
        children_count=children_count,
        pensioner_present=bool(pensioner_present),
        someone_employed=bool(someone_employed),
        wake_period=wake_period,
        sleep_period=sleep_period,
        weekend_shift_periods=weekend_shift,
        daytime_occupancy=daytime,
        away_days_per_year=away,
        # Sublinear in headcount, as EFUS/NEED volume scaling is.
        appliance_intensity=(people_count / 2.4) ** 0.6,
        routine_offset_periods=routine_offset,
    )


def away_day_calendar(
    premise_id: str,
    profile: BehaviourProfile,
    dates: Sequence[dt.date],
    *,
    seed: int | None = None,
) -> frozenset[dt.date]:
    """The premise's away days, drawn as BLOCKS (holidays are consecutive), from
    this module's own substream, per calendar year present in `dates`."""
    if not dates:
        raise ValueError("away_day_calendar needs at least one date")
    base = _base_seed_for(premise_id, seed)
    by_year: dict[int, list[dt.date]] = {}
    for date in dates:
        by_year.setdefault(date.year, []).append(date)

    away: set[dt.date] = set()
    for year, year_dates in by_year.items():
        if profile.away_days_per_year <= 0:
            continue
        rng = _substream(base, f"away::{year}")
        remaining = profile.away_days_per_year
        guard = 0
        while remaining > 0 and guard < 50:
            guard += 1
            length = min(remaining, rng.randint(*_AWAY_BLOCK_LENGTH_RANGE))
            start = rng.randrange(len(year_dates))
            for offset in range(length):
                if start + offset < len(year_dates):
                    away.add(year_dates[start + offset])
            remaining -= length
    return frozenset(away)


# ---------------------------------------------------------------------------
# Layer 2 — the PREBOUND / income-comfort constraint (a LIVE mechanism)
# ---------------------------------------------------------------------------

# `domain-knowledge` — the prebound effect (Sunikka-Blank & Galvin 2012; Firth et
# al. 2013): households in poorly-performing homes consume materially less than
# the standard-occupancy model predicts, because they UNDER-HEAT to manage the
# bill. Today that lives in this codebase as a hard-coded constant in
# `Household.epc_consumption_multiplier`'s docstring ("adjusted 50% toward 1.0
# for prebound effect") — a number, applied identically to every household in
# every year at every price. Here it becomes a MECHANISM: the household lowers
# its setpoint and shortens its heating hours, and the consumption reduction
# EMERGES from the physics instead of being multiplied on.
_MAX_SETPOINT_REDUCTION_C = 3.5
_MAX_COMFORT_HOURS_LOST = 0.45
_INCOME_STRESS_INTENSITY: dict[IncomeStress, float] = {
    IncomeStress.LOW: 0.05,
    IncomeStress.MODERATE: 0.40,
    IncomeStress.HIGH: 0.80,
}
# Price response: the intensity added when the unit rate doubles against the
# household's reference price. `domain-knowledge`, candidate to verify.
_PRICE_ELASTICITY = 0.45
REFERENCE_UNIT_PRICE_P_PER_KWH = 4.0
"""Pre-crisis domestic gas unit rate — the household's own reference point, not a
market datum. A DIAL on the mechanism's zero, published for auditability."""


@dataclass(frozen=True)
class ComfortConstraint:
    """The income/comfort constraint — one of the exactly three things Layer 2
    hands Layer 1. Nothing in it is read from the thermal model."""

    rationing_intensity: float
    setpoint_reduction_c: float
    comfort_hours_retained: float

    @staticmethod
    def unconstrained() -> "ComfortConstraint":
        return ComfortConstraint(0.0, 0.0, 1.0)


def comfort_constraint_for(
    *,
    income_stress: IncomeStress,
    unit_price_p_per_kwh: float = REFERENCE_UNIT_PRICE_P_PER_KWH,
    reference_price_p_per_kwh: float = REFERENCE_UNIT_PRICE_P_PER_KWH,
    rationing_severity: float = 0.0,
    prior_year_bill_gbp: float | None = None,
    affordable_bill_gbp: float = 1200.0,
) -> ComfortConstraint:
    """The LIVE prebound response: income stress + price + (optionally) last
    year's bill -> how much comfort the household gives up.

    Every argument is something the HOUSEHOLD knows — its own circumstances, the
    price on its tariff, the bill it received. None of them is a fabric parameter,
    which is what keeps the separability contract one-way: Layer 2 never reads
    inside the thermal model. `prior_year_bill_gbp` is an OBSERVABLE (a bill the
    household was sent) and is therefore an INPUT here, not a live feedback loop;
    the across-year coupling that produces is real household behaviour and is
    recorded as such, not smuggled in as a fabric read.

    `rationing_severity` is the coupling to `simulation.self_rationing` — the
    hidden budget-driven "pay but don't heat" state. There the severity is applied
    as a scalar cut to annual kWh; here the same severity becomes the physical act
    that causes the cut.
    """
    _require_finite("unit_price_p_per_kwh", unit_price_p_per_kwh)
    _require_finite("reference_price_p_per_kwh", reference_price_p_per_kwh)
    _require_finite("rationing_severity", rationing_severity)
    _require_finite("affordable_bill_gbp", affordable_bill_gbp)
    if reference_price_p_per_kwh <= 0 or affordable_bill_gbp <= 0:
        raise ValueError("reference price and affordable bill must be positive")
    if not 0.0 <= rationing_severity <= 1.0:
        raise ValueError(f"rationing_severity must be in [0, 1], got {rationing_severity!r}")
    if income_stress not in _INCOME_STRESS_INTENSITY:
        raise ValueError(f"unknown income stress {income_stress!r}")

    intensity = _INCOME_STRESS_INTENSITY[income_stress]
    price_ratio = max(0.0, unit_price_p_per_kwh / reference_price_p_per_kwh - 1.0)
    intensity += _PRICE_ELASTICITY * price_ratio
    if prior_year_bill_gbp is not None:
        _require_finite("prior_year_bill_gbp", prior_year_bill_gbp)
        bill_pressure = max(0.0, prior_year_bill_gbp / affordable_bill_gbp - 1.0)
        intensity += 0.35 * bill_pressure
    # The self-rationing state is a stronger signal than either: it is already the
    # household having decided to stop heating.
    intensity = max(intensity, rationing_severity)
    intensity = max(0.0, min(1.0, intensity))

    return ComfortConstraint(
        rationing_intensity=intensity,
        setpoint_reduction_c=_MAX_SETPOINT_REDUCTION_C * intensity,
        comfort_hours_retained=1.0 - _MAX_COMFORT_HOURS_LOST * intensity,
    )


# ---------------------------------------------------------------------------
# Layer 2 — the appliance event stream (non-heating electricity texture)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ApplianceSpec:
    """One appliance's PHYSICS: a real power rating and a real duration.

    Texture is generated from these, never injected: a 2.8 kW kettle for three
    minutes IS 0.14 kWh in one half hour and nothing in the next.
    """

    name: str
    power_kw: float
    duration_hours: float
    events_per_day: float
    window: tuple[int, int]
    """Inclusive half-hour index range in which the event may start."""
    heat_fraction: float = 0.9
    """Share of the electricity that ends up as useful internal gain. Cooking
    extract and a vented dryer put much of it outside."""
    scales_with_people: bool = True


# `domain-knowledge` — nameplate ratings and usage frequencies. Judged (never
# parameterised) against Ofgem TDCV medium non-heating electricity, 2,700 kWh/yr.
APPLIANCE_CATALOGUE: tuple[ApplianceSpec, ...] = (
    ApplianceSpec("kettle", 2.8, 0.05, 4.0, (12, 45), heat_fraction=0.95),
    ApplianceSpec("toaster", 1.1, 0.05, 0.8, (12, 20), heat_fraction=0.95),
    ApplianceSpec("microwave", 0.9, 0.10, 0.8, (20, 43), heat_fraction=0.8),
    ApplianceSpec("oven", 2.0, 0.75, 0.55, (32, 42), heat_fraction=0.6),
    ApplianceSpec("hob", 1.8, 0.35, 0.70, (33, 43), heat_fraction=0.6),
    ApplianceSpec("washing_machine", 0.55, 1.5, 0.60, (14, 40), heat_fraction=0.5),
    ApplianceSpec("dishwasher", 0.70, 1.5, 0.50, (36, 46), heat_fraction=0.5),
    ApplianceSpec("tumble_dryer", 2.2, 0.70, 0.22, (16, 42), heat_fraction=0.3),
    ApplianceSpec("vacuum_iron", 1.2, 0.30, 0.25, (18, 40), heat_fraction=0.9),
)

# `domain-knowledge` — the always-on load, and it is NOT a constant.
#
# A fridge and a freezer are THERMOSTATIC CYCLING devices: exactly the same class
# of mechanism as W1_11's boiler deadband, one level down. The compressor runs for
# part of a cycle whose length is not a whole number of half hours, so the
# overlap with each settlement period differs period to period AND drifts across
# days. That is where the overnight texture of a real home comes from — an empty
# house is not flat, it hums. Modelling this as a flat 0.075 kW would reproduce
# exactly the artefact this atom exists to remove (a smooth series), and adding
# noise instead would fail L1.5.
_STANDBY_KW = 0.025
"""Router, alarm, standby draws — genuinely constant."""


@dataclass(frozen=True)
class ColdApplianceSpec:
    name: str
    power_kw: float
    cycle_minutes: float
    duty: float


COLD_APPLIANCES: tuple[ColdApplianceSpec, ...] = (
    ColdApplianceSpec("fridge_freezer", 0.090, 47.0, 0.32),
    ColdApplianceSpec("freezer", 0.100, 61.0, 0.30),
)

_LIGHTING_KW_PER_PERSON = 0.035
_ELECTRONICS_KW_PER_PERSON = 0.055

# `domain-knowledge` — lighting and electronics are SWITCHED devices, and this is
# the same argument the note on `_STANDBY_KW` already makes for the fridge, just
# applied to the loads it was not applied to. A room is lit or it is not; a TV is
# on or it is not. Multiplying a per-person wattage by an occupancy fraction
# produces a load that is CONSTANT for the whole of an occupancy block — the
# quiet-afternoon signature `0.1453, 0.1453, 0.1536` — which is the smooth series
# this atom exists to remove, reappearing in the one place the module had not yet
# swept.
#
# Each unit is a two-state chain whose STATIONARY probability is the occupancy
# this module already computes, so the expected load in every period is EXACTLY
# what the continuous form produced. Level, annual kWh and the L2.5 aggregate
# reconciliation are therefore untouched by construction; only the texture
# changes. That is the difference between generating texture and injecting it.
_LIGHTING_UNITS_PER_PERSON = 2.0
"""Rooms lit at once. A three-person household lighting six rooms across an
evening is `domain-knowledge`, not a fitted count."""
_ELECTRONICS_UNITS_PER_PERSON = 2.0
"""Screens/devices drawing at once."""
_SWITCH_PERSISTENCE = 0.7
"""Lag-1 autocorrelation of a unit's on/off state: a mean dwell of
1/(1-0.7) = 3.3 half-hours, i.e. a light left on for about an hour and a half.
A DIAGNOSTIC of how long people leave things on, never a texture setting (R12)."""
_METABOLIC_GAIN_KW_PER_PERSON = 0.085


def _square_wave_on_hours(
    start_h: float, end_h: float, *, cycle_h: float, duty: float, phase_h: float
) -> float:
    """Hours for which a cycling compressor is ON within `[start_h, end_h)`.

    Exact, not sampled: the on-window of every cycle overlapping the settlement
    period is intersected with it. Determinism is structural — the phase is drawn
    once per premise, and nothing is re-drawn per period.
    """
    if cycle_h <= 0 or not 0.0 < duty <= 1.0:
        raise ValueError("cold-appliance cycle must be positive with duty in (0, 1]")
    on_h = 0.0
    first = math.floor((start_h - phase_h) / cycle_h)
    last = math.floor((end_h - phase_h) / cycle_h)
    for k in range(first, last + 1):
        cycle_start = phase_h + k * cycle_h
        on_start = cycle_start
        on_end = cycle_start + duty * cycle_h
        on_h += max(0.0, min(end_h, on_end) - max(start_h, on_start))
    return on_h


def switched_units_on(
    rng: random.Random,
    units: int,
    occupancy: float,
    state: int,
    *,
    previous_occupancy: float | None = None,
) -> int:
    """Step one period of a bank of `units` two-state switched loads.

    `occupancy` is the STATIONARY on-probability of each unit and `state` is how
    many were on last period. Transition probabilities are set so the chain's
    stationary distribution is Binomial(units, occupancy): within a block of
    constant occupancy the expected load is exactly the continuous form's value,
    and the persistence only decides HOW the same energy is arranged in time.

    When occupancy STEPS — the household wakes, leaves, comes home — the bank is
    re-seeded from the new stationary distribution instead of relaxing into it.
    That is both the physical moment (a step in occupancy IS everyone switching
    things on at once) and the only way the mean is preserved: a chain that
    relaxes with a 3.3-period time constant across a step spends the first few
    periods of every block below its own stationary level, which measured as a
    systematic -2.2% of non-heating electricity — a silent baseline drift, and
    the sort of thing R13 forbids far more firmly than it forbids being smooth.

    Raises on an occupancy outside [0, 1]: a probability that is not one must
    FAIL rather than be silently clipped into a plausible-looking load (R15).
    """
    if units < 0:
        raise ValueError("a bank cannot have a negative number of units")
    if not 0.0 <= occupancy <= 1.0:
        raise ValueError(f"occupancy must be a probability in [0, 1], got {occupancy}")
    if previous_occupancy is None or abs(previous_occupancy - occupancy) > 1e-9:
        return sum(1 for _ in range(units) if rng.random() < occupancy)
    state = max(0, min(units, state))
    turn_on = (1.0 - _SWITCH_PERSISTENCE) * occupancy
    turn_off = (1.0 - _SWITCH_PERSISTENCE) * (1.0 - occupancy)
    on = 0
    for unit in range(units):
        if unit < state:
            on += 0 if rng.random() < turn_off else 1
        else:
            on += 1 if rng.random() < turn_on else 0
    return on


def cold_appliance_phases(
    base_seed: int, *, specs: Sequence[ColdApplianceSpec] = COLD_APPLIANCES
) -> tuple[float, ...]:
    """Compressor phases — STRUCTURAL, drawn ONCE per premise. Two premises differ
    overnight because their fridges are out of step, not because noise was added."""
    return tuple(
        _substream(base_seed, f"cold::{spec.name}").uniform(0.0, spec.cycle_minutes / 60.0)
        for spec in specs
    )


def cold_appliance_kwh(
    phases: Sequence[float],
    day_index: int,
    period: int,
    *,
    specs: Sequence[ColdApplianceSpec] = COLD_APPLIANCES,
) -> float:
    """Cold-appliance energy in one settlement period, from the cycling model."""
    if len(phases) != len(specs):
        raise ValueError("one phase per cold-appliance spec is required")
    absolute_start = day_index * 24.0 + period * PERIOD_HOURS
    total = 0.0
    for spec, phase in zip(specs, phases):
        on_h = _square_wave_on_hours(
            absolute_start,
            absolute_start + PERIOD_HOURS,
            cycle_h=spec.cycle_minutes / 60.0,
            duty=spec.duty,
            phase_h=phase,
        )
        total += spec.power_kw * on_h
    return total


@dataclass(frozen=True)
class ApplianceEvent:
    name: str
    start_period: int
    power_kw: float
    duration_hours: float
    heat_fraction: float

    @property
    def energy_kwh(self) -> float:
        return self.power_kw * self.duration_hours


def draw_appliance_events(
    base_seed: int,
    day_index: int,
    profile: BehaviourProfile,
    *,
    is_weekend: bool,
    is_away: bool,
) -> list[ApplianceEvent]:
    """Draw one day's appliance events from this module's own substream, salted
    per day so any single day replays without the days before it (C-S2).

    An away day draws NOTHING — the empty house is the point.
    """
    if is_away:
        return []
    rng = _substream(base_seed, f"appliance::{day_index}")
    shift = profile.weekend_shift_periods if is_weekend else 0
    events: list[ApplianceEvent] = []
    for spec in APPLIANCE_CATALOGUE:
        rate = spec.events_per_day * (profile.appliance_intensity if spec.scales_with_people else 1.0)
        if is_weekend:
            rate *= 1.15  # more at home, more cooking and washing
        # Poisson-ish integer count: floor plus a Bernoulli on the remainder.
        count = int(rate) + (1 if rng.random() < rate - int(rate) else 0)
        # The spec window is the population envelope; this household lives on its
        # OWN clock inside it, so the envelope is shifted by the routine before
        # the day's draw. The offset is read from the profile, never re-drawn
        # here — that is what makes it a habit rather than another day's noise.
        routine = profile.routine_offset_periods
        lo, hi = spec.window
        lo = max(profile.wake_period + shift, int(math.floor(lo + shift + routine)))
        hi = min(profile.sleep_period + shift, int(math.ceil(hi + shift + routine)))
        if hi <= lo:
            continue
        for _ in range(count):
            events.append(
                ApplianceEvent(
                    name=spec.name,
                    start_period=rng.randint(lo, hi),
                    power_kw=spec.power_kw,
                    duration_hours=spec.duration_hours,
                    heat_fraction=spec.heat_fraction,
                )
            )
    return events


def _spread_event(event: ApplianceEvent, series: list[float], *, scale: float = 1.0) -> None:
    """Lay one event's energy across the half hours it actually spans."""
    remaining_h = event.duration_hours
    period = event.start_period
    while remaining_h > 1e-9 and period < PERIODS_PER_DAY:
        used = min(PERIOD_HOURS, remaining_h)
        series[period] += event.power_kw * used * scale
        remaining_h -= used
        period += 1


def occupancy_at(profile: BehaviourProfile, period: int, *, is_weekend: bool, is_away: bool) -> float:
    """People at home in `period`, as a fraction of the household. The single
    driver of lighting, electronics, metabolic gain and DHW timing."""
    if is_away:
        return 0.0
    shift = profile.weekend_shift_periods if is_weekend else 0
    wake = profile.wake_period + shift
    sleep = min(PERIODS_PER_DAY - 1, profile.sleep_period + shift)
    if period < wake or period > sleep:
        return 0.25  # asleep in the house: present, but nothing switched on
    if is_weekend:
        return 0.9
    # Weekday: the daytime window (09:00–17:00) is the part that varies.
    if 18 <= period < 34:
        return max(profile.daytime_occupancy, 0.05)
    return 0.9


# ---------------------------------------------------------------------------
# Layer 2 — domestic hot water
# ---------------------------------------------------------------------------

# `domain-knowledge` — BS EN 12831 / SAP hot-water draw: ~40 litres per person per
# day at a 45 K rise ≈ 2.1 kWh thermal per person per day.
_DHW_LITRES_PER_PERSON_DAY = 40.0
_DHW_DELTA_T_K = 45.0
_DHW_KWH_PER_LITRE = 4.18 * _DHW_DELTA_T_K / 3600.0
_DHW_COMBI_EFFICIENCY = 0.80
_DHW_HEAT_PUMP_COP_PENALTY = 0.62  # a cylinder at 55 C is a worse duty than space heat
_DHW_EVENT_HOURS = 0.2


def draw_dhw_events(
    base_seed: int,
    day_index: int,
    profile: BehaviourProfile,
    *,
    is_weekend: bool,
    is_away: bool,
) -> list[ApplianceEvent]:
    """Hot-water draws as EVENTS (showers, baths, washing up), not a flat rate."""
    if is_away:
        return []
    rng = _substream(base_seed, f"dhw::{day_index}")
    shift = profile.weekend_shift_periods if is_weekend else 0
    daily_kwh = _DHW_LITRES_PER_PERSON_DAY * _DHW_KWH_PER_LITRE * profile.people_count
    n_events = max(2, int(round(profile.people_count * 1.4)))
    events: list[ApplianceEvent] = []
    weights = []
    for _ in range(n_events):
        # Most draws cluster on the morning rise and the evening; the rest scatter.
        roll = rng.random()
        if roll < 0.5:
            start = min(PERIODS_PER_DAY - 1, profile.wake_period + shift + rng.randint(0, 3))
        elif roll < 0.85:
            # The evening cluster sits on the household's own clock, not on a
            # national 18:00 — the same routine that moves its cooking.
            evening_base = 36 + shift + profile.routine_offset_periods
            start = min(
                PERIODS_PER_DAY - 1,
                max(0, int(math.floor(evening_base)) + rng.randint(0, 6)),
            )
        else:
            start = rng.randint(
                min(profile.wake_period + shift, PERIODS_PER_DAY - 2),
                min(profile.sleep_period + shift, PERIODS_PER_DAY - 1),
            )
        weight = rng.uniform(0.5, 1.5)
        weights.append(weight)
        events.append(
            ApplianceEvent(
                name="dhw",
                start_period=start,
                power_kw=1.0,  # rescaled below once the weights are known
                duration_hours=_DHW_EVENT_HOURS,
                heat_fraction=0.15,  # standing/pipe losses that stay in the house
            )
        )
    total_weight = sum(weights) or 1.0
    return [
        ApplianceEvent(
            name=e.name,
            start_period=e.start_period,
            power_kw=daily_kwh * w / total_weight / _DHW_EVENT_HOURS,
            duration_hours=e.duration_hours,
            heat_fraction=e.heat_fraction,
        )
        for e, w in zip(events, weights)
    ]


# ---------------------------------------------------------------------------
# LCT rewiring — EV (event-driven) and PV (by orientation)
# ---------------------------------------------------------------------------

# `domain-knowledge` — DfT NTS: ~20 miles/day mean car use, heavily skewed, with a
# large share of zero-mileage days. Efficiency ~3.5 mi/kWh.
_EV_MEAN_MILES_PER_DAY = 20.0
_EV_ZERO_MILEAGE_DAY_PROBABILITY = 0.25
_EV_MILES_PER_KWH = 3.5
_EV_USABLE_BATTERY_KWH = 55.0
_EV_CHARGE_EFFICIENCY = 0.90
_EV_PLUG_IN_THRESHOLD = 0.55
"""Drivers plug in when the battery is down, not every night — the single biggest
reason real EV load is event-driven rather than a nightly block."""


@dataclass(frozen=True)
class EvState:
    soc_kwh: float


def draw_ev_day(
    base_seed: int,
    day_index: int,
    household: Household,
    state: EvState,
    *,
    is_away: bool,
    smart_charging_window: tuple[int, int] | None = None,
) -> tuple[list[float], EvState]:
    """One day of EV charging as an EVENT: miles driven -> SoC deficit -> a charge
    that starts when the car gets home and runs until it is full.

    Returns (per-period kWh, new state). Away days consume no home charge — the
    car is not there — which is part of what makes an away day visible.
    """
    series = [0.0] * PERIODS_PER_DAY
    if not household.has_ev or household.ev_charger_kw <= 0.0 or not household.has_driveway:
        return series, state
    rng = _substream(base_seed, f"ev::{day_index}")
    if is_away:
        return series, state

    if rng.random() < _EV_ZERO_MILEAGE_DAY_PROBABILITY:
        miles = 0.0
    else:
        # Lognormal-ish spread about the mean: most days short, a few long.
        miles = min(300.0, rng.lognormvariate(math.log(_EV_MEAN_MILES_PER_DAY), 0.75))
    used_kwh = miles / _EV_MILES_PER_KWH
    soc = max(0.0, state.soc_kwh - used_kwh)

    if soc >= _EV_USABLE_BATTERY_KWH * _EV_PLUG_IN_THRESHOLD:
        return series, EvState(soc)

    deficit = _EV_USABLE_BATTERY_KWH - soc
    if smart_charging_window is not None:
        start = smart_charging_window[0]
    else:
        start = rng.randint(32, 42)  # home between 16:00 and 21:00
    remaining = deficit
    period = start
    while remaining > 1e-6 and period < PERIODS_PER_DAY + 20:
        idx = period % PERIODS_PER_DAY
        delivered = min(household.ev_charger_kw * PERIOD_HOURS, remaining)
        # Charging that runs past midnight lands on the following morning's
        # periods, which is exactly what an overnight charge does.
        series[idx] += delivered / _EV_CHARGE_EFFICIENCY
        remaining -= delivered
        period += 1
    return series, EvState(_EV_USABLE_BATTERY_KWH)


# `domain-knowledge` — array tilt and the orientation azimuths a UK EPC records.
_PV_TILT_DEG = 35.0
_PV_SYSTEM_DERATE = 0.80
_PV_BEAM_FRACTION = 0.80
_ROOF_AZIMUTH_DEG: dict[str, tuple[float, ...]] = {
    "south": (180.0,),
    "east_west": (90.0, 270.0),
    "north": (0.0,),
    "na": (180.0,),
}


def solar_azimuth_deg(latitude_deg: float, day_of_year: int, hour: float) -> float:
    """Solar azimuth, degrees clockwise from north. Needed because PV output
    TIMING is what orientation actually changes — an east-facing array peaks
    before breakfast-time and a west-facing one after the evening peak begins."""
    lat = math.radians(latitude_deg)
    dec = math.radians(solar_declination_deg(day_of_year))
    hour_angle = math.radians(15.0 * (hour - 12.0))
    sin_alt = solar_elevation_sin(latitude_deg, day_of_year, hour)
    alt = math.asin(max(-1.0, min(1.0, sin_alt)))
    cos_alt = math.cos(alt)
    if abs(cos_alt) < 1e-6:
        return 180.0
    cos_az = (math.sin(dec) - sin_alt * math.sin(lat)) / (cos_alt * math.cos(lat))
    az = math.degrees(math.acos(max(-1.0, min(1.0, cos_az))))
    return az if hour_angle <= 0 else 360.0 - az


def pv_generation_kwh(
    household: Household,
    *,
    irradiance_kw_per_m2: Sequence[float],
    day_of_year: int,
    latitude_deg: float,
) -> list[float]:
    """PV output by ORIENTATION against the same reconstructed irradiance field
    the thermal model uses — one weather truth, two consumers."""
    series = [0.0] * PERIODS_PER_DAY
    if not household.has_solar or household.solar_kwp <= 0.0:
        return series
    azimuths = _ROOF_AZIMUTH_DEG.get((household.roof_aspect or "na").lower(), (180.0,))
    share = 1.0 / len(azimuths)
    tilt = math.radians(_PV_TILT_DEG)
    for period in range(PERIODS_PER_DAY):
        ghi = irradiance_kw_per_m2[period]
        if ghi <= 0.0:
            continue
        hour = (period + 0.5) * PERIOD_HOURS
        sin_alt = solar_elevation_sin(latitude_deg, day_of_year, hour)
        if sin_alt <= 0.02:
            continue
        sun_az = math.radians(solar_azimuth_deg(latitude_deg, day_of_year, hour))
        alt = math.asin(max(-1.0, min(1.0, sin_alt)))
        beam = ghi * _PV_BEAM_FRACTION
        diffuse = ghi - beam
        for azimuth_deg in azimuths:
            panel_az = math.radians(azimuth_deg)
            cos_theta = math.sin(alt) * math.cos(tilt) + math.cos(alt) * math.sin(tilt) * math.cos(
                sun_az - panel_az
            )
            cos_theta = max(0.0, cos_theta)
            # Transposition, clamped: at very low sun the beam ratio explodes.
            beam_poa = beam * min(3.0, cos_theta / max(sin_alt, 0.05))
            diffuse_poa = diffuse * (1.0 + math.cos(tilt)) / 2.0
            poa = beam_poa + diffuse_poa
            series[period] += (
                poa * household.solar_kwp * _PV_SYSTEM_DERATE * share * PERIOD_HOURS
            )
    return series


# ---------------------------------------------------------------------------
# THE SEAM — the only three things Layer 2 may hand Layer 1
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class LayerTwoInputs:
    """Layer 2's ENTIRE influence on Layer 1. Three fields, by contract.

    If a fourth ever appears here, the separability contract has been broken and
    the two contract controls below will say which half moved.
    """

    schedule: HeatingSchedule
    internal_gain_kw: tuple[float, ...]
    constraint: ComfortConstraint


LAYER_TWO_TO_LAYER_ONE_FIELDS: frozenset[str] = frozenset(
    {"schedule", "internal_gain_kw", "constraint"}
)


def daily_schedule(
    base_schedule: HeatingSchedule,
    profile: BehaviourProfile,
    constraint: ComfortConstraint,
    *,
    is_weekend: bool,
    is_away: bool,
) -> HeatingSchedule:
    """Layer 2's first argument: the setpoint schedule for ONE day.

    Weekend shift, away-day frost protection, and the prebound constraint (a lower
    comfort setpoint AND shorter heating hours) all land here — never inside the
    thermal model.
    """
    if is_away:
        return HeatingSchedule(
            comfort_setpoint_c=AWAY_SETPOINT_C,
            setback_setpoint_c=AWAY_SETPOINT_C,
            morning_start_period=0,
            morning_end_period=0,
            evening_start_period=0,
            evening_end_period=0,
            deadband_c=base_schedule.deadband_c,
            continuous=base_schedule.continuous,
        )
    shift = profile.weekend_shift_periods if is_weekend else 0
    # One routine drives both fuels: a household that eats at 20:30 heats at
    # 20:30 too. Without this the gas and electricity legs of the SAME home
    # would tell two different stories about when its occupants are up.
    routine = int(round(profile.routine_offset_periods))
    comfort = base_schedule.comfort_setpoint_c - constraint.setpoint_reduction_c
    setback = min(base_schedule.setback_setpoint_c, comfort - 1.0)
    retained = max(0.0, min(1.0, constraint.comfort_hours_retained))

    morning_len = base_schedule.morning_end_period - base_schedule.morning_start_period
    evening_len = base_schedule.evening_end_period - base_schedule.evening_start_period
    morning_len = max(1, int(round(morning_len * retained)))
    evening_len = max(1, int(round(evening_len * retained)))
    morning_start = base_schedule.morning_start_period + shift
    # A shortened evening period is given up at the START (people heat when they
    # get cold in the evening), which is why rationing moves the peak as well as
    # shrinking it.
    evening_start = base_schedule.evening_start_period + shift + routine + (
        (base_schedule.evening_end_period - base_schedule.evening_start_period) - evening_len
    )
    return HeatingSchedule(
        comfort_setpoint_c=comfort,
        setback_setpoint_c=setback,
        morning_start_period=morning_start,
        morning_end_period=morning_start + morning_len,
        evening_start_period=evening_start,
        evening_end_period=evening_start + evening_len,
        deadband_c=base_schedule.deadband_c,
        continuous=base_schedule.continuous,
    )


def internal_gain_profile(
    profile: BehaviourProfile,
    appliance_kwh: Sequence[float],
    appliance_heat_kwh: Sequence[float],
    *,
    is_weekend: bool,
    is_away: bool,
) -> list[float]:
    """Layer 2's second argument: Phi_p, the occupant + appliance gain in kW.

    This is the hook the FRAME names — the appliance event stream that supplies
    non-heating electricity texture is the SAME series that warms the house, so
    the two cannot drift apart.
    """
    gains = []
    for period in range(PERIODS_PER_DAY):
        occupancy = occupancy_at(profile, period, is_weekend=is_weekend, is_away=is_away)
        metabolic = _METABOLIC_GAIN_KW_PER_PERSON * profile.people_count * occupancy
        appliance = appliance_heat_kwh[period] / PERIOD_HOURS
        gains.append(metabolic + appliance)
    return gains


# ---------------------------------------------------------------------------
# The trace
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PremiseDayTrace:
    """One premise-day at half-hourly resolution."""

    date: dt.date
    day_of_year: int
    is_weekend: bool
    is_away: bool
    mean_ambient_c: float
    setpoint_c: tuple[float, ...]
    indoor_air_c: tuple[float, ...]
    heat_delivered_kwh: tuple[float, ...]
    heating_fuel_kwh: tuple[float, ...]
    behavioural_electricity_kwh: tuple[float, ...]
    """Appliances + lighting + electronics + base load + electric DHW. FABRIC-
    INDEPENDENT by construction — the series the separability control checks."""
    dhw_fuel_kwh: tuple[float, ...]
    ev_kwh: tuple[float, ...]
    pv_generation_kwh: tuple[float, ...]
    electricity_kwh: tuple[float, ...]
    """Gross electricity consumption at the premise, before PV offset."""
    gas_kwh: tuple[float, ...]
    internal_gain_kw: tuple[float, ...]

    @property
    def net_electricity_kwh(self) -> tuple[float, ...]:
        """Consumption net of on-site PV. May go negative (export) — that is a
        real premise, not an error."""
        return tuple(c - g for c, g in zip(self.electricity_kwh, self.pv_generation_kwh))

    @property
    def electricity_total_kwh(self) -> float:
        return sum(self.electricity_kwh)

    @property
    def gas_total_kwh(self) -> float:
        return sum(self.gas_kwh)

    @property
    def heat_total_kwh(self) -> float:
        return sum(self.heat_delivered_kwh)


@dataclass(frozen=True)
class PremiseTrace:
    premise_id: str
    heating_commodity: str
    days: tuple[PremiseDayTrace, ...]
    fabric: FabricParameters
    behaviour: BehaviourProfile
    constraint: ComfortConstraint
    source: HeatSource
    base_schedule: HeatingSchedule
    final_state: ThermalState
    """The thermal state at the END of the last day, so a caller that generates the
    window in segments (a life event changes the household mid-window) can CHAIN
    them. Without it every segment boundary would reset the walls to setback and
    inject a fake heating spike the premise never had."""

    def daily(self, commodity: str) -> list[float]:
        if commodity == "gas":
            return [d.gas_total_kwh for d in self.days]
        if commodity == "electricity":
            return [d.electricity_total_kwh for d in self.days]
        raise ValueError(f"unknown commodity {commodity!r}")

    def half_hourly(self, commodity: str) -> list[list[float]]:
        if commodity == "gas":
            return [list(d.gas_kwh) for d in self.days]
        if commodity == "electricity":
            return [list(d.electricity_kwh) for d in self.days]
        raise ValueError(f"unknown commodity {commodity!r}")

    def behavioural_electricity(self) -> list[list[float]]:
        return [list(d.behavioural_electricity_kwh) for d in self.days]

    def annual_kwh(self, commodity: str) -> float:
        """Annualised total — the level NEED and TDCV judge."""
        daily = self.daily(commodity)
        if not daily:
            raise ValueError("an empty trace has no annual total")
        return sum(daily) / len(daily) * 365.25

    @property
    def away_days(self) -> int:
        return sum(1 for d in self.days if d.is_away)


def generate_premise_trace(
    *,
    premise_id: str,
    household: Household,
    weather: Sequence[TraceWeatherDay],
    seed: int | None = None,
    behaviour: BehaviourProfile | None = None,
    constraint: ComfortConstraint | None = None,
    away_days: Iterable[dt.date] | None = None,
    latitude_deg: float,
    deadband_c: float = DEFAULT_DEADBAND_C,
    initial_state: ThermalState | None = None,
    smart_charging_window: tuple[int, int] | None = None,
) -> PremiseTrace:
    """Generate one premise's half-hourly gas and electricity trace.

    A PURE FUNCTION of its arguments with no shared state, which is why the
    sizing answer above can lean on a process pool: two premises can be generated
    in any order, in any process, with identical results.

    Empty weather RAISES rather than returning an empty trace — a statistic over
    a vacuous trace must fail, never pass (R15 fail-open).
    """
    if not weather:
        raise ValueError("generate_premise_trace needs at least one weather day")
    if not household.is_residential:
        raise ValueError(
            f"the premise trace generator is DOMESTIC; {household.property_type} is not residential"
        )
    for day in weather:
        _require_finite("temperature_mean_c", day.weather.temperature_mean_c)
        _require_finite("temperature_min_c", day.weather.temperature_min_c)
        _require_finite("temperature_max_c", day.weather.temperature_max_c)

    base_seed = _base_seed_for(premise_id, seed)
    profile = behaviour or behaviour_profile_for(premise_id, household, seed=seed)
    comfort = constraint or ComfortConstraint.unconstrained()
    away = (
        frozenset(away_days)
        if away_days is not None
        else away_day_calendar(premise_id, profile, [d.date for d in weather], seed=seed)
    )

    params = fabric_parameters(household)
    base_schedule = heating_schedule_for(premise_id, household, seed=seed, deadband_c=deadband_c)
    # The heat source is sized on the UNCONSTRAINED comfort setpoint: a household
    # that starts rationing does not get a smaller boiler.
    source = heat_source_for(household, params, base_schedule.comfort_setpoint_c)
    state = initial_state or ThermalState(
        indoor_air_c=base_schedule.setback_setpoint_c, mass_c=base_schedule.setback_setpoint_c
    )
    ev_state = EvState(_EV_USABLE_BATTERY_KWH)
    # STRUCTURAL, drawn once per premise: two premises hum out of step with each
    # other because their compressors are out of phase, never because noise was
    # added to either output series.
    cold_phases = cold_appliance_phases(base_seed)

    heating_commodity = "gas" if household.is_gas_heated else "electricity"
    dhw_commodity = heating_commodity if household.heating_system != HeatingSystem.NONE else "electricity"

    days: list[PremiseDayTrace] = []
    for day_index, wx in enumerate(weather):
        is_weekend = wx.is_weekend
        is_away = wx.date in away

        # --- Layer 2: events -------------------------------------------------
        events = draw_appliance_events(
            base_seed, day_index, profile, is_weekend=is_weekend, is_away=is_away
        )
        appliance_kwh = [0.0] * PERIODS_PER_DAY
        appliance_heat_kwh = [0.0] * PERIODS_PER_DAY
        for event in events:
            _spread_event(event, appliance_kwh)
            _spread_event(event, appliance_heat_kwh, scale=event.heat_fraction)

        dhw_events = draw_dhw_events(
            base_seed, day_index, profile, is_weekend=is_weekend, is_away=is_away
        )
        dhw_heat_kwh = [0.0] * PERIODS_PER_DAY
        dhw_gain_kwh = [0.0] * PERIODS_PER_DAY
        for event in dhw_events:
            _spread_event(event, dhw_heat_kwh)
            _spread_event(event, dhw_gain_kwh, scale=event.heat_fraction)

        # Base load: standby is constant, the cold appliances cycle, and lighting
        # and electronics SWITCH. Each bank carries its state across the day, so a
        # lit room stays lit; the day-salted substream keeps any single day
        # replayable without the days before it (C-S2).
        sunrise, sunset = daylight_hours(latitude_deg, wx.weather.day_of_year)
        behavioural = [0.0] * PERIODS_PER_DAY
        cold_kwh = [0.0] * PERIODS_PER_DAY
        switch_rng = _substream(base_seed, f"switched::{day_index}")
        light_units = max(1, int(round(_LIGHTING_UNITS_PER_PERSON * profile.people_count)))
        device_units = max(1, int(round(_ELECTRONICS_UNITS_PER_PERSON * profile.people_count)))
        light_kw_per_unit = _LIGHTING_KW_PER_PERSON * profile.people_count / light_units
        device_kw_per_unit = _ELECTRONICS_KW_PER_PERSON * profile.people_count / device_units
        lights_on = 0
        devices_on = 0
        prev_device_p: float | None = None
        prev_light_p: float | None = None
        for period in range(PERIODS_PER_DAY):
            hour = (period + 0.5) * PERIOD_HOURS
            occupancy = occupancy_at(profile, period, is_weekend=is_weekend, is_away=is_away)
            awake = occupancy > 0.25
            dark = hour < sunrise + 0.5 or hour > sunset - 0.5
            # The always-on load is standby (genuinely constant) PLUS the cycling
            # cold appliances — the deliberate non-constant, per the note on
            # `_STANDBY_KW`. A flat base load here would re-introduce the smooth
            # series this atom exists to remove, and it runs on an away day too:
            # the fridge does not go on holiday.
            kw = _STANDBY_KW
            live = awake and not is_away
            device_p = occupancy if live else 0.0
            light_p = occupancy if live and dark else 0.0
            devices_on = switched_units_on(
                switch_rng, device_units, device_p, devices_on,
                previous_occupancy=prev_device_p,
            )
            lights_on = switched_units_on(
                switch_rng, light_units, light_p, lights_on,
                previous_occupancy=prev_light_p,
            )
            prev_device_p, prev_light_p = device_p, light_p
            kw += devices_on * device_kw_per_unit + lights_on * light_kw_per_unit
            cold_kwh[period] = cold_appliance_kwh(cold_phases, day_index, period)
            behavioural[period] = kw * PERIOD_HOURS + cold_kwh[period] + appliance_kwh[period]

        # --- Layer 2 -> Layer 1: the three arguments, and nothing else -------
        gains = internal_gain_profile(
            profile,
            appliance_kwh,
            # A cold appliance moves heat from its box to the room and its motor
            # dissipates there too, so ALL of its electrical energy lands in the
            # dwelling as gain — the one appliance whose heat fraction is 1.0.
            [a + d + c for a, d, c in zip(appliance_heat_kwh, dhw_gain_kwh, cold_kwh)],
            is_weekend=is_weekend,
            is_away=is_away,
        )
        schedule = daily_schedule(
            base_schedule, profile, comfort, is_weekend=is_weekend, is_away=is_away
        )
        layer_two = LayerTwoInputs(
            schedule=schedule, internal_gain_kw=tuple(gains), constraint=comfort
        )

        ambient = reconstruct_ambient_profile(
            temperature_min_c=wx.weather.temperature_min_c,
            temperature_max_c=wx.weather.temperature_max_c,
            temperature_mean_c=wx.weather.temperature_mean_c,
            day_of_year=wx.weather.day_of_year,
            latitude_deg=latitude_deg,
        )
        irradiance = reconstruct_irradiance_profile(
            cloud_cover_pct=wx.weather.cloud_cover_pct,
            day_of_year=wx.weather.day_of_year,
            latitude_deg=latitude_deg,
        )

        result = simulate_day(
            household=household,
            params=params,
            schedule=layer_two.schedule,
            source=source,
            ambient_profile=ambient,
            irradiance_kw_per_m2=irradiance,
            initial_state=state,
            internal_gain_kw=list(layer_two.internal_gain_kw),
        )
        state = result.end_state

        # --- assets ----------------------------------------------------------
        ev_kwh, ev_state = draw_ev_day(
            base_seed,
            day_index,
            household,
            ev_state,
            is_away=is_away,
            smart_charging_window=smart_charging_window,
        )
        pv_kwh = pv_generation_kwh(
            household,
            irradiance_kw_per_m2=irradiance,
            day_of_year=wx.weather.day_of_year,
            latitude_deg=latitude_deg,
        )

        # --- fuel composition -------------------------------------------------
        dhw_fuel = [
            _dhw_fuel_kwh(household, heat_kwh, ambient.temperatures_c[p])
            for p, heat_kwh in enumerate(dhw_heat_kwh)
        ]
        electricity = list(behavioural)
        gas = [0.0] * PERIODS_PER_DAY
        for period in range(PERIODS_PER_DAY):
            electricity[period] += ev_kwh[period]
            if heating_commodity == "gas":
                gas[period] += result.fuel_kwh[period]
            else:
                electricity[period] += result.fuel_kwh[period]
            if dhw_commodity == "gas":
                gas[period] += dhw_fuel[period]
            else:
                electricity[period] += dhw_fuel[period]

        days.append(
            PremiseDayTrace(
                date=wx.date,
                day_of_year=wx.weather.day_of_year,
                is_weekend=is_weekend,
                is_away=is_away,
                mean_ambient_c=wx.weather.temperature_mean_c,
                setpoint_c=tuple(schedule.setpoint_at(p) for p in range(PERIODS_PER_DAY)),
                indoor_air_c=tuple(result.indoor_air_c),
                heat_delivered_kwh=tuple(result.heat_delivered_kwh),
                heating_fuel_kwh=tuple(result.fuel_kwh),
                behavioural_electricity_kwh=tuple(behavioural),
                dhw_fuel_kwh=tuple(dhw_fuel),
                ev_kwh=tuple(ev_kwh),
                pv_generation_kwh=tuple(pv_kwh),
                electricity_kwh=tuple(electricity),
                gas_kwh=tuple(gas),
                internal_gain_kw=tuple(gains),
            )
        )

    return PremiseTrace(
        premise_id=premise_id,
        heating_commodity=heating_commodity,
        days=tuple(days),
        fabric=params,
        behaviour=profile,
        constraint=comfort,
        source=source,
        base_schedule=base_schedule,
        final_state=state,
    )


def _dhw_fuel_kwh(household: Household, heat_kwh: float, ambient_c: float) -> float:
    """Hot-water HEAT -> metered fuel, by system. A heat pump makes hot water at a
    worse COP than space heat because the cylinder needs a higher flow temperature
    — a real effect that a flat efficiency hides."""
    if heat_kwh <= 0.0:
        return 0.0
    if household.is_gas_heated:
        return heat_kwh / _DHW_COMBI_EFFICIENCY
    if household.is_heat_pump:
        cop = heat_pump_cop(
            ambient_c, ground_source=household.heating_system == HeatingSystem.HEAT_PUMP_GROUND
        )
        return heat_kwh / max(1.3, cop * _DHW_HEAT_PUMP_COP_PENALTY)
    return heat_kwh  # immersion / instantaneous electric: resistive, 1:1


# ---------------------------------------------------------------------------
# Sizing — the FRAME's blocking question, kept re-measurable
# ---------------------------------------------------------------------------


def estimate_book_cost(
    n_premises: int,
    n_days: int,
    *,
    seconds_per_premise_year: float = PREMISE_YEAR_SECONDS_MEASURED,
    workers: int = 1,
) -> dict[str, float]:
    """Projected CPU cost of generating a whole book, from the MEASURED rate.

    Deliberately arithmetic rather than a benchmark: a timing assertion in a test
    suite is flaky and would measure the CI host, not the decision. The decision
    this supports is recorded in the module docstring; this function exists so it
    can be re-derived when the book or the hardware changes, instead of being
    folklore.
    """
    if n_premises <= 0 or n_days <= 0:
        raise ValueError("book cost needs a positive premise count and day count")
    if workers <= 0:
        raise ValueError("workers must be positive")
    _require_finite("seconds_per_premise_year", seconds_per_premise_year)
    if seconds_per_premise_year <= 0:
        raise ValueError("seconds_per_premise_year must be positive")
    premise_years = n_premises * n_days / 365.25
    cpu_seconds = premise_years * seconds_per_premise_year
    return {
        "premise_years": premise_years,
        "cpu_seconds": cpu_seconds,
        "cpu_hours": cpu_seconds / 3600.0,
        "wall_hours_at_workers": cpu_seconds / 3600.0 / workers,
    }


# ---------------------------------------------------------------------------
# R15-failable controls
#
# Every one of these: rejects non-finite values FIRST, RAISES on insufficient
# input rather than passing vacuously, and has a named mutation in
# tests/simulation/test_premise_trace.py that makes it fire.
# ---------------------------------------------------------------------------


def _check_series(series: Sequence[float], *, name: str, minimum: int) -> None:
    if len(series) < minimum:
        raise ValueError(f"{name} needs at least {minimum} values, got {len(series)}")
    for value in series:
        _require_finite(name, value)


def fabric_only_moves_level_and_character(
    trace_a: PremiseTrace,
    trace_b: PremiseTrace,
    *,
    min_level_ratio: float = 1.25,
) -> bool:
    """SEPARABILITY, half one: hold Layer 2 FIXED and vary the fabric, and ONLY
    the level and the thermal character may move.

    Fires when (a) the fabric change leaked into Layer 2 — the behavioural
    electricity series or the setpoint schedule moved, which would mean the
    thermal model is reaching back into behaviour — or (b) the fabric change did
    NOT move the heat level, which would mean the fabric is not doing the work
    the design claims.
    """
    if not trace_a.days or not trace_b.days:
        raise ValueError("separability needs at least one day on each trace")
    if len(trace_a.days) != len(trace_b.days):
        raise ValueError("separability compares traces over the SAME weather days")

    for day_a, day_b in zip(trace_a.days, trace_b.days):
        for va, vb in zip(day_a.behavioural_electricity_kwh, day_b.behavioural_electricity_kwh):
            _require_finite("behavioural electricity", va)
            _require_finite("behavioural electricity", vb)
            if va != vb:
                return False  # fabric leaked into the appliance stream
        for sa, sb in zip(day_a.setpoint_c, day_b.setpoint_c):
            if sa != sb:
                return False  # fabric leaked into the setpoint schedule

    heat_a = sum(d.heat_total_kwh for d in trace_a.days)
    heat_b = sum(d.heat_total_kwh for d in trace_b.days)
    _require_finite("heat total", heat_a)
    _require_finite("heat total", heat_b)
    if min(heat_a, heat_b) <= 0.0:
        return False
    ratio = max(heat_a, heat_b) / min(heat_a, heat_b)
    return ratio >= min_level_ratio


def _free_running_character(trace: PremiseTrace) -> float:
    """A pure Layer 1 statistic: the mean overnight indoor-air fall while the heat
    source is off. It depends on tau_m and the heat-loss coefficient, and on
    nothing Layer 2 supplies."""
    falls: list[float] = []
    for day in trace.days:
        # Periods 0-10 (00:00-05:00): before any morning schedule, heat off.
        window = day.indoor_air_c[0:11]
        if sum(day.heating_fuel_kwh[0:11]) > 1e-9:
            continue
        falls.append(window[0] - window[-1])
    if not falls:
        raise ValueError("no free-running window found — cannot judge fabric character")
    return sum(falls) / len(falls)


def behaviour_only_moves_timing_and_volume(
    trace_a: PremiseTrace,
    trace_b: PremiseTrace,
    *,
    character_tolerance_c: float = 0.02,
) -> bool:
    """SEPARABILITY, half two: hold the FABRIC fixed and vary Layer 2, and ONLY
    the timing and the volume may move.

    Fires when Layer 2 has reached inside the thermal model: the fabric parameter
    vector or the free-running thermal character changed. Also fires when varying
    Layer 2 changed nothing at all, which would mean the seam is dead.
    """
    if not trace_a.days or not trace_b.days:
        raise ValueError("separability needs at least one day on each trace")
    fa, fb = trace_a.fabric, trace_b.fabric
    for attr in ("r_ia_k_per_kw", "r_im_k_per_kw", "c_i_kwh_per_k", "c_m_kwh_per_k", "floor_area_m2"):
        va, vb = getattr(fa, attr), getattr(fb, attr)
        _require_finite(attr, va)
        _require_finite(attr, vb)
        if va != vb:
            return False  # behaviour moved the fabric — contract broken

    char_a = _free_running_character(trace_a)
    char_b = _free_running_character(trace_b)
    _require_finite("free-running character", char_a)
    _require_finite("free-running character", char_b)
    if abs(char_a - char_b) > character_tolerance_c:
        return False

    # ... and the seam must actually DO something: timing or volume must move.
    timing_a = tuple(trace_a.days[0].setpoint_c)
    timing_b = tuple(trace_b.days[0].setpoint_c)
    volume_a = sum(d.heat_total_kwh for d in trace_a.days)
    volume_b = sum(d.heat_total_kwh for d in trace_b.days)
    return timing_a != timing_b or volume_a != volume_b


def away_days_are_representable(
    trace: PremiseTrace,
    *,
    low_period_kwh: float = 0.05,
    min_block_periods: int = 6,
    min_blocks: int = 1,
) -> bool:
    """L1.3: an empty house must be REPRESENTABLE AND PRESENT.

    Fires when the trace never falls to an unoccupied level for a sustained block
    — the shipped generator's defect (no half-hour below 0.05 kWh in ten years).
    """
    if len(trace.days) < 30:
        raise ValueError("trough behaviour needs at least 30 days to be meaningful")
    _require_finite("low_period_kwh", low_period_kwh)
    blocks = 0
    for day in trace.days:
        run = 0
        for value in day.electricity_kwh:
            _require_finite("electricity", value)
            if value < low_period_kwh:
                run += 1
                if run == min_block_periods:
                    blocks += 1
            else:
                run = 0
    return blocks >= min_blocks


def hdd_response_gradient(
    daily_kwh: Sequence[float],
    daily_mean_temp_c: Sequence[float],
    *,
    base_temp_c: float = 15.5,
) -> float:
    """kWh per heating-degree-day for ONE premise — the per-home version of the
    single national constant `GAS_HEATING_KWH_PER_DEGREE_DAY = 8.0`."""
    if len(daily_kwh) != len(daily_mean_temp_c):
        raise ValueError("daily series must be the same length")
    _check_series(daily_kwh, name="daily kwh", minimum=60)
    _check_series(daily_mean_temp_c, name="daily mean temp", minimum=60)
    hdd = [max(0.0, base_temp_c - t) for t in daily_mean_temp_c]
    n = len(hdd)
    mean_h = sum(hdd) / n
    mean_k = sum(daily_kwh) / n
    cov = sum((h - mean_h) * (k - mean_k) for h, k in zip(hdd, daily_kwh))
    var = sum((h - mean_h) ** 2 for h in hdd)
    if var <= 0.0:
        raise ValueError("no heating-degree-day variation in the window — gradient undefined")
    return cov / var


def hdd_response_varies_between_homes(
    gradients: Mapping[str, float], *, min_spread_ratio: float = 1.5
) -> bool:
    """G.3: the HDD response must VARY between homes with fabric.

    Fires on the shipped defect — one national constant applied to every home.
    """
    if len(gradients) < 3:
        raise ValueError("between-home spread needs at least three homes")
    values = list(gradients.values())
    for value in values:
        _require_finite("hdd gradient", value)
    lo, hi = min(values), max(values)
    if lo <= 0.0:
        return False
    return hi / lo >= min_spread_ratio


def seasonal_ratio(daily_kwh: Sequence[float], day_of_year: Sequence[int]) -> float:
    """Winter (Dec–Feb) mean daily kWh divided by summer (Jun–Aug) mean."""
    if len(daily_kwh) != len(day_of_year):
        raise ValueError("daily series must be the same length")
    _check_series(daily_kwh, name="daily kwh", minimum=180)
    winter = [k for k, d in zip(daily_kwh, day_of_year) if d <= 59 or d >= 335]
    summer = [k for k, d in zip(daily_kwh, day_of_year) if 152 <= d <= 243]
    if not winter or not summer:
        raise ValueError("window does not cover both a winter and a summer")
    summer_mean = sum(summer) / len(summer)
    if summer_mean <= 0.0:
        raise ValueError("summer consumption is zero — seasonal ratio undefined")
    return (sum(winter) / len(winter)) / summer_mean


def seasonal_gas_ratio_in_band(
    daily_kwh: Sequence[float],
    day_of_year: Sequence[int],
    *,
    band: tuple[float, float] = (2.5, 9.0),
) -> bool:
    """G.2: the winter/summer gas ratio must stay in its DIAGNOSTIC band.

    The band is a sanity flag anchored on the currently-observed ~4.6x for
    dual-fuel homes, NEVER a target (R12). Drift toward an edge triggers R4
    (diagnose the mechanism), never a tuning pass.
    """
    ratio = seasonal_ratio(daily_kwh, day_of_year)
    _require_finite("seasonal ratio", ratio)
    return band[0] <= ratio <= band[1]


def daily_variability_is_non_degenerate(
    daily_kwh: Sequence[float], *, min_coefficient_of_variation: float = 0.15
) -> bool:
    """G.4: day-to-day variability of daily totals must be non-degenerate.

    Fires on a generator whose daily total is a smooth function of the daily mean
    temperature alone.
    """
    _check_series(daily_kwh, name="daily kwh", minimum=60)
    n = len(daily_kwh)
    mean = sum(daily_kwh) / n
    if mean <= 0.0:
        raise ValueError("cannot judge variability of an all-zero series")
    sd = math.sqrt(sum((k - mean) ** 2 for k in daily_kwh) / n)
    return sd / mean >= min_coefficient_of_variation


def annual_level_spread_is_material(
    annual_kwh: Mapping[str, float], *, min_p90_p10_ratio: float = 1.8
) -> bool:
    """L2.4: annual totals must span a real range across the population.

    Fires on the shipped defect (annual totals within 8% of each other) and on the
    named mutation (set every home to the population mean). Judged against NEED /
    Ofgem TDCV spread, which parameterise nothing here.
    """
    if len(annual_kwh) < 5:
        raise ValueError("scale spread needs at least five homes")
    values = sorted(annual_kwh.values())
    for value in values:
        _require_finite("annual kwh", value)
    p10 = values[max(0, int(0.10 * (len(values) - 1)))]
    p90 = values[min(len(values) - 1, int(math.ceil(0.90 * (len(values) - 1))))]
    if p10 <= 0.0:
        return False
    return p90 / p10 >= min_p90_p10_ratio


def prebound_response_is_live(
    responses: Sequence[ComfortConstraint], *, min_total_movement: float = 0.25
) -> bool:
    """The prebound effect must be a MECHANISM, not a constant.

    `responses` is a sequence ordered by increasing stress (income stress, price,
    bill). The constraint must be MONOTONE NON-DECREASING and must move
    materially end-to-end. Fires on the shipped defect: one hard-coded constant
    ("adjusted 50% toward 1.0") that is the same for every household at every
    price.
    """
    if len(responses) < 3:
        raise ValueError("liveness needs at least three points on the stress axis")
    intensities = [r.rationing_intensity for r in responses]
    for value in intensities:
        _require_finite("rationing intensity", value)
    for earlier, later in zip(intensities, intensities[1:]):
        if later < earlier - 1e-12:
            return False
    return (intensities[-1] - intensities[0]) >= min_total_movement


def implied_cop_series(trace: PremiseTrace) -> list[tuple[float, float]]:
    """(mean ambient, implied COP) per day for a heat-pump premise."""
    if not trace.days:
        raise ValueError("an empty trace has no COP series")
    out: list[tuple[float, float]] = []
    for day in trace.days:
        heat = sum(day.heat_delivered_kwh)
        fuel = sum(day.heating_fuel_kwh)
        if heat <= 0.0 or fuel <= 0.0:
            continue
        _require_finite("heat", heat)
        _require_finite("fuel", fuel)
        out.append((day.mean_ambient_c, heat / fuel))
    if len(out) < 30:
        raise ValueError("too few heating days to judge the COP relationship")
    return out


def heat_pump_cop_falls_with_cold(trace: PremiseTrace, *, min_drop: float = 0.3) -> bool:
    """The LCT rewiring made falsifiable: a heat pump's implied COP must FALL as
    ambient falls, so its electricity rises super-linearly in a cold snap.

    Fires on the mutation that flattens the COP — which is exactly today's flat
    `ELEC_HEATING_KWH_PER_DEGREE_DAY["heat_pump"] = 1.2`.
    """
    series = implied_cop_series(trace)
    series.sort(key=lambda pair: pair[0])
    cut = max(5, len(series) // 4)
    coldest = sum(c for _, c in series[:cut]) / cut
    mildest = sum(c for _, c in series[-cut:]) / cut
    _require_finite("coldest COP", coldest)
    _require_finite("mildest COP", mildest)
    return (mildest - coldest) >= min_drop


def annual_level_in_band(
    annual_kwh: float, band: tuple[float, float], *, label: str = "annual"
) -> bool:
    """G.1 / L2.4 level check against an EXTERNAL anchor (Ofgem TDCV, NEED).

    A DIAGNOSTIC BAND, never a target (R12): a value outside it triggers R4, and
    it may never be closed by tuning the generator toward the anchor.
    """
    _require_finite(label, annual_kwh)
    if band[0] >= band[1] or band[0] <= 0:
        raise ValueError(f"invalid band {band!r}")
    return band[0] <= annual_kwh <= band[1]
