"""Phase B — Life events engine.

Generates household-level life events that change physical attributes over time.
Events are timestamped, typed, and immutable — state is reconstructed by replaying
the event log from the household's baseline.

Event types modelled:
- solar_install: customer installs solar PV (typically 1-3 kWp resi, 3-10 kWp SME)
- ev_acquired: customer acquires an electric vehicle
- boiler_replaced: old boiler replaced with new (resets boiler_age to NEW)
- heat_pump_installed: gas boiler replaced with heat pump (changes heating_system)
- battery_installed: battery storage added (typically after solar install)
- smart_meter_installed: smart meter fitted (if not already) -- NOTE: this event type
  is defined and handled by apply_events() but is NOT currently emitted by the
  generator loop below (W2_5 Expert Hour finding, 2026-07-13) -- a real
  smart-meter-rollout event generator is a separate, not-yet-built piece.
- insulation_upgraded: loft or wall insulation improved (upgrades InsulationLevel)
- job_loss / income_recovery: economic life event (income_stress -> HIGH / LOW)
- new_baby: economic life event (income_stress LOW -> MODERATE)
- retirement_starts: economic life event (income_stress LOW -> MODERATE)
- illness: economic life event (income_stress -> HIGH, shares income_recovery's own
  HIGH->LOW transition -- W2_5_life_event_stream, 2026-07-13)
- divorce: economic life event (income_stress LOW -> MODERATE -- W2_5_life_event_stream,
  2026-07-13)

Epistemic constraint: these events are SIM ground truth.  The company layer
cannot read this log directly.  It observes consequences — higher electricity
consumption, change in MPAN metering type, outbound contact from customer, or
EPC rating update from the national register.  The company-side detection/
inference twin (C7_life_event_detection) must recover these events from
observable behaviour; it never reads this stream.

RNG substream discipline (C-S2, CLAUDE.md; W2_5_life_event_stream 2026-07-13):
each event type draws from its OWN named, deterministically-seeded substream
(see `_substream` / `_LIFE_EVENT_SUBSTREAMS`).  A new draw in one subsystem
therefore can NEVER shift the random numbers another subsystem draws — the
structural fix for the real 01:09Z incident where adding illness/divorce draws
to a single shared econ RNG shifted every downstream (job_loss/new_baby/
retirement) draw.  Substream seeds derive from a STABLE hash (sha256/md5), so
replay is deterministic across processes regardless of PYTHONHASHSEED.

Calibration sources: docs/market_research/HUMAN_SIMULATION_RESEARCH.md
- Solar: Finding 5 (DESNZ REPD, 3% 2016 → 5.7% 2025)
- EV: Finding 6 (DfT + EHS, 0.3% 2016 → 7% 2025)
- Heat pump: Finding 4 (EHS AT4, ~0.8% 2022 → ~2% 2025)
"""

from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Literal

from simulation.household import (
    BoilerAge,
    BuildEra,
    HeatingSystem,
    Household,
    IncomeStress,
    InsulationLevel,
    PropertyType,
)


EventType = Literal[
    "solar_install",
    "ev_acquired",
    "boiler_replaced",
    "heat_pump_installed",
    "battery_installed",
    "smart_meter_installed",
    "insulation_upgraded",
    "job_loss",
    "income_recovery",
    "new_baby",
    "retirement_starts",
    "illness",
    "divorce",
]


@dataclass(frozen=True)
class LifeEvent:
    """An immutable event that changes a household's physical state."""

    customer_id: str
    event_date: str          # YYYY-MM-DD
    event_type: EventType
    payload: dict            # event-specific attributes (e.g. solar_kwp=3.8)


# ---------------------------------------------------------------------------
# Annual probability tables — calibrated to UK-wide penetration curves
# ---------------------------------------------------------------------------

# Solar PV: year → marginal annual install probability for a resi home without solar.
# Derived from DESNZ REPD cumulative domestic installs / 28.4M households.
# Finding 5: 3.0% stock in 2016, rising to 5.7% by 2025 (~0.3% annual new installs/yr).
_SOLAR_INSTALL_PROB_BY_YEAR: dict[int, float] = {
    2016: 0.0030,
    2017: 0.0028,
    2018: 0.0025,
    2019: 0.0023,
    2020: 0.0025,
    2021: 0.0030,
    2022: 0.0035,   # energy crisis drove installs
    2023: 0.0040,
    2024: 0.0038,
    2025: 0.0035,
}

# EV acquisition: year → annual probability for a household without EV.
# Finding 6: stock 0.3% (2016) → 7% (2025); annual new penetration 0.1%→1.0%.
_EV_ACQUIRED_PROB_BY_YEAR: dict[int, float] = {
    2016: 0.001,
    2017: 0.002,
    2018: 0.003,
    2019: 0.005,
    2020: 0.007,
    2021: 0.010,
    2022: 0.013,
    2023: 0.015,
    2024: 0.016,
    2025: 0.016,
}

# Heat pump: year → annual probability for a gas-heated home.
# Finding 4: ~0.1% 2016, ~0.3% 2022, ~0.4% 2025; BUF target 600k/yr by 2028.
_HEAT_PUMP_INSTALL_PROB_BY_YEAR: dict[int, float] = {
    2016: 0.001,
    2017: 0.001,
    2018: 0.002,
    2019: 0.002,
    2020: 0.002,
    2021: 0.003,
    2022: 0.003,
    2023: 0.004,
    2024: 0.005,
    2025: 0.006,
}

# Boiler replacement: annual probability for homes with an OLD boiler (~14-year life).
# Source: Valiant / Worcester Bosch industry data — average UK boiler lifespan 12-15 yrs.
_BOILER_REPLACE_PROB_OLD = 0.09    # ~11yr expected remaining life for OLD boiler
_BOILER_REPLACE_PROB_MID = 0.04    # ~25yr for MID
_BOILER_REPLACE_PROB_NEW = 0.01    # almost never replaced when new

# Insulation upgrade: resi customers with POOR insulation, annual ECO scheme eligibility.
# Source: ECO4 budget allocation — ~400k homes/yr in 2022-25.
_INSULATION_UPGRADE_PROB_POOR = 0.03
_INSULATION_UPGRADE_PROB_PARTIAL = 0.01

# Battery storage: conditional on solar install; annual probability of adding battery.
# BEIS: ~15% of solar homes have batteries as of 2024; growing.
_BATTERY_INSTALL_PROB_WITH_SOLAR_BY_YEAR: dict[int, float] = {
    2016: 0.002,
    2017: 0.004,
    2018: 0.006,
    2019: 0.008,
    2020: 0.012,
    2021: 0.018,
    2022: 0.025,
    2023: 0.035,
    2024: 0.040,
    2025: 0.045,
}


# Economic life events: income stress
# Job loss: UK annual unemployment entry rate ~2.2% of working-age employed
# Source: ONS Labour Market Statistics 2016-2025
_JOB_LOSS_ANNUAL_PROB = 0.022

# Income recovery: conditional on HIGH stress; median UK unemployment spell ~6 months
_INCOME_RECOVERY_ANNUAL_PROB = 0.50

# New baby: UK birth rate ~10.7/1,000 population ≈ 1.1% per resi household/year
# Source: ONS Birth Summary Tables
_NEW_BABY_ANNUAL_PROB = 0.011

# Retirement: calibrated to build era. Typical UK retirement age ~65.
# ERA_1945_1964 occupants: born 1945–64, aged 52–71 in 2016 — peak cohort.
# Source: ONS Labour Force Survey — economic inactivity by age
_RETIREMENT_PROB_BY_ERA: dict[str, float] = {
    "pre_1919":   0.000,  # already retired pre-simulation
    "1919_1944":  0.000,  # already retired pre-simulation
    "1945_1964":  0.035,  # peak retirement cohort 2016-2025
    "1965_1980":  0.008,  # approaching retirement by 2025
    "1981_2000":  0.000,  # too young
    "post_2000":  0.000,  # too young
}

# Illness (serious/long-term, income_stress -> HIGH, W2_5_life_event_stream 2026-07-13):
# no direct UK annual NEW-ONSET incidence rate was found (2026-07-13 DISCOVER pass,
# two search attempts) -- ONS/Health Foundation data gives disability PREVALENCE
# growth of ~0.9 percentage points/year (2019-2023), used here as an honestly-caveated
# proxy. This is a NET figure (new onset minus recovery/death already netted out), so
# it likely UNDERSTATES true gross onset incidence -- a real, named limitation, not
# hidden. Recovery shares job_loss's own income_recovery transition (income_stress is
# a single state variable in this model, not tracked per-cause).
_ILLNESS_ANNUAL_PROB = 0.009

# Divorce (income_stress LOW -> MODERATE, W2_5_life_event_stream 2026-07-13):
# 102,678 divorces in England & Wales, 2023 (ONS) / 28.4 million UK households, 2023
# (ONS Families and Households) =~ 0.36% per household/year. Applied to ALL households
# (not conditioned on marital status, which this model does not track) -- same
# simplification level as new_baby's own per-household (not per-fertile-age-woman) rate.
_DIVORCE_ANNUAL_PROB = 0.0036


# ---------------------------------------------------------------------------
# Named RNG substreams — one per emitted event type (C-S2 substream discipline)
# ---------------------------------------------------------------------------
# Every event type the generator can EMIT draws from its own named substream.
# Order is irrelevant to isolation (each substream is an independent function of
# (base_seed, name)); this tuple exists so tests can enumerate the contract and
# so a future event type is added by APPENDING a name, never by threading a new
# draw through an existing stream.
_LIFE_EVENT_SUBSTREAMS: tuple[str, ...] = (
    "solar_install",
    "battery_installed",
    "ev_acquired",
    "heat_pump_installed",
    "boiler_replaced",
    "insulation_upgraded",
    "job_loss",
    "income_recovery",
    "new_baby",
    "retirement_starts",
    "illness",
    "divorce",
)


def _substream(base_seed: int, name: str) -> random.Random:
    """Return an independent RNG for a named event-type substream.

    Derived from a STABLE sha256 of ``base_seed:name`` (not Python's
    per-process-salted ``hash()``), so the same (base_seed, name) always yields
    the same stream across processes — a hard requirement for C-S2 deterministic
    replay.  Because each name seeds an independent generator, introducing a new
    named substream can never consume from, or shift, any existing substream's
    sequence.
    """
    digest = hashlib.sha256(f"{base_seed}:{name}".encode()).digest()
    return random.Random(int.from_bytes(digest[:8], "big"))


def _base_seed_for(household: Household, seed: int | None) -> int:
    """Resolve the base seed for a household's event streams.

    Uses a STABLE md5 of the customer_id when no explicit seed is given (the
    built-in ``hash()`` is salted per process and would break replay).
    """
    if seed is not None:
        return seed
    return int(hashlib.md5(household.customer_id.encode()).hexdigest()[:8], 16)


def _annual_prob(table: dict[int, float], year: int) -> float:
    """Look up annual probability, clamping to table bounds."""
    if year <= min(table):
        return table[min(table)]
    if year >= max(table):
        return table[max(table)]
    return table[year]


def _random_date_in_year(year: int, rng: random.Random) -> str:
    """Return a random date within the calendar year."""
    start = date(year, 1, 1)
    day_of_year = rng.randint(0, 364)
    return (start + timedelta(days=day_of_year)).isoformat()


def generate_life_events(
    household: Household,
    sim_start_year: int,
    sim_end_year: int,
    seed: int | None = None,
) -> list[LifeEvent]:
    """Generate all life events for a household over the simulation period.

    Events are generated independently per year via Bernoulli trials on
    annual probability tables calibrated to UK government statistics.

    Args:
        household: The household's baseline physical state at sim_start_year.
        sim_start_year: First year to generate events for (inclusive).
        sim_end_year: Last year to generate events for (inclusive).
        seed: Optional RNG seed for reproducibility. Derived from customer_id
              if None, ensuring deterministic per-customer event streams.

    Returns:
        Sorted list of LifeEvents. Empty list if no events occur.
    """
    base_seed = _base_seed_for(household, seed)
    # One independent, named substream per emitted event type (C-S2). A draw in
    # any one of these can never shift the sequence any other one produces, so a
    # future event type is added by APPENDING a substream, not by threading a new
    # draw through a shared stream (the 01:09Z incident's root cause).
    sub = {name: _substream(base_seed, name) for name in _LIFE_EVENT_SUBSTREAMS}

    events: list[LifeEvent] = []

    # Track mutable state for conditional logic (e.g. battery only if solar)
    has_solar = household.has_solar
    has_battery = household.has_battery
    has_ev = household.has_ev
    boiler_age = household.boiler_age
    insulation = household.insulation
    heating = household.heating_system
    income_stress = household.income_stress
    is_retired = False

    for year in range(sim_start_year, sim_end_year + 1):

        # -- Solar PV install --
        if (not has_solar
                and household.is_residential
                and household.property_type != PropertyType.FLAT
                and household.roof_aspect not in ("north", "na")):
            prob = _annual_prob(_SOLAR_INSTALL_PROB_BY_YEAR, year)
            _s = sub["solar_install"]
            if _s.random() < prob:
                kwp = round(_s.uniform(2.5, 4.5), 1)
                events.append(LifeEvent(
                    customer_id=household.customer_id,
                    event_date=_random_date_in_year(year, _s),
                    event_type="solar_install",
                    payload={"solar_kwp": kwp},
                ))
                has_solar = True

        # -- Battery install (conditional on solar) --
        if has_solar and not has_battery:
            prob = _annual_prob(_BATTERY_INSTALL_PROB_WITH_SOLAR_BY_YEAR, year)
            _s = sub["battery_installed"]
            if _s.random() < prob:
                kwh = round(_s.uniform(4.0, 13.5), 1)
                events.append(LifeEvent(
                    customer_id=household.customer_id,
                    event_date=_random_date_in_year(year, _s),
                    event_type="battery_installed",
                    payload={"battery_kwh": kwh},
                ))
                has_battery = True

        # -- EV acquisition --
        if not has_ev and household.is_residential and household.has_driveway:
            prob = _annual_prob(_EV_ACQUIRED_PROB_BY_YEAR, year)
            _s = sub["ev_acquired"]
            if _s.random() < prob:
                charger_kw = _s.choice([3.7, 7.0, 7.0, 22.0])  # weighted toward 7kW
                events.append(LifeEvent(
                    customer_id=household.customer_id,
                    event_date=_random_date_in_year(year, _s),
                    event_type="ev_acquired",
                    payload={"ev_charger_kw": charger_kw},
                ))
                has_ev = True

        # -- Heat pump installation (gas-heated resi, physically eligible) --
        if (household.hp_eligible
                and heating in (HeatingSystem.GAS_BOILER_COMBI, HeatingSystem.GAS_BOILER_SYSTEM)):
            prob = _annual_prob(_HEAT_PUMP_INSTALL_PROB_BY_YEAR, year)
            _s = sub["heat_pump_installed"]
            if _s.random() < prob:
                events.append(LifeEvent(
                    customer_id=household.customer_id,
                    event_date=_random_date_in_year(year, _s),
                    event_type="heat_pump_installed",
                    payload={"heating_system": HeatingSystem.HEAT_PUMP_AIR.value},
                ))
                heating = HeatingSystem.HEAT_PUMP_AIR
                boiler_age = BoilerAge.NA

        # -- Boiler replacement (gas-heated only, no heat pump installed yet) --
        elif heating in (HeatingSystem.GAS_BOILER_COMBI, HeatingSystem.GAS_BOILER_SYSTEM):
            prob = {
                BoilerAge.OLD: _BOILER_REPLACE_PROB_OLD,
                BoilerAge.MID: _BOILER_REPLACE_PROB_MID,
                BoilerAge.NEW: _BOILER_REPLACE_PROB_NEW,
                BoilerAge.NA: 0.0,
            }.get(boiler_age, 0.0)
            _s = sub["boiler_replaced"]
            if prob and _s.random() < prob:
                events.append(LifeEvent(
                    customer_id=household.customer_id,
                    event_date=_random_date_in_year(year, _s),
                    event_type="boiler_replaced",
                    payload={"boiler_age": BoilerAge.NEW.value},
                ))
                boiler_age = BoilerAge.NEW

        # -- Insulation upgrade --
        _s = sub["insulation_upgraded"]
        if insulation == InsulationLevel.POOR:
            if _s.random() < _INSULATION_UPGRADE_PROB_POOR:
                events.append(LifeEvent(
                    customer_id=household.customer_id,
                    event_date=_random_date_in_year(year, _s),
                    event_type="insulation_upgraded",
                    payload={"insulation": InsulationLevel.PARTIAL.value},
                ))
                insulation = InsulationLevel.PARTIAL
        elif insulation == InsulationLevel.PARTIAL:
            if _s.random() < _INSULATION_UPGRADE_PROB_PARTIAL:
                events.append(LifeEvent(
                    customer_id=household.customer_id,
                    event_date=_random_date_in_year(year, _s),
                    event_type="insulation_upgraded",
                    payload={"insulation": InsulationLevel.FULL.value},
                ))
                insulation = InsulationLevel.FULL

        # -- Economic life events (residential only) --
        # Each event type draws from its OWN named substream (C-S2): adding or
        # removing any one of them cannot shift the random draws of the others,
        # the structural fix for the 01:09Z shared-econ-RNG incident.
        if household.is_residential:
            # Job loss (only when not already in high stress)
            if income_stress != IncomeStress.HIGH:
                _s = sub["job_loss"]
                if _s.random() < _JOB_LOSS_ANNUAL_PROB:
                    events.append(LifeEvent(
                        customer_id=household.customer_id,
                        event_date=_random_date_in_year(year, _s),
                        event_type="job_loss",
                        payload={},
                    ))
                    income_stress = IncomeStress.HIGH

            # Income recovery (only when in high stress)
            elif income_stress == IncomeStress.HIGH:
                _s = sub["income_recovery"]
                if _s.random() < _INCOME_RECOVERY_ANNUAL_PROB:
                    events.append(LifeEvent(
                        customer_id=household.customer_id,
                        event_date=_random_date_in_year(year, _s),
                        event_type="income_recovery",
                        payload={},
                    ))
                    income_stress = IncomeStress.LOW

            # New baby (only when stable income)
            if income_stress == IncomeStress.LOW:
                _s = sub["new_baby"]
                if _s.random() < _NEW_BABY_ANNUAL_PROB:
                    events.append(LifeEvent(
                        customer_id=household.customer_id,
                        event_date=_random_date_in_year(year, _s),
                        event_type="new_baby",
                        payload={},
                    ))
                    income_stress = IncomeStress.MODERATE

            # Retirement (era-calibrated, only fires once)
            if not is_retired:
                retire_prob = _RETIREMENT_PROB_BY_ERA.get(household.build_era.value, 0.0)
                _s = sub["retirement_starts"]
                if retire_prob > 0 and _s.random() < retire_prob:
                    events.append(LifeEvent(
                        customer_id=household.customer_id,
                        event_date=_random_date_in_year(year, _s),
                        event_type="retirement_starts",
                        payload={},
                    ))
                    is_retired = True
                    if income_stress == IncomeStress.LOW:
                        income_stress = IncomeStress.MODERATE

            # Illness (serious/long-term; only when not already in high stress --
            # shares job_loss's own HIGH-stress gate and income_recovery's own
            # recovery transition, since income_stress is a single state variable
            # not tracked per-cause)
            if income_stress != IncomeStress.HIGH:
                _s = sub["illness"]
                if _s.random() < _ILLNESS_ANNUAL_PROB:
                    events.append(LifeEvent(
                        customer_id=household.customer_id,
                        event_date=_random_date_in_year(year, _s),
                        event_type="illness",
                        payload={},
                    ))
                    income_stress = IncomeStress.HIGH

            # Divorce (only when stable income, same gate as new_baby/retirement)
            if income_stress == IncomeStress.LOW:
                _s = sub["divorce"]
                if _s.random() < _DIVORCE_ANNUAL_PROB:
                    events.append(LifeEvent(
                        customer_id=household.customer_id,
                        event_date=_random_date_in_year(year, _s),
                        event_type="divorce",
                        payload={},
                    ))
                    income_stress = IncomeStress.MODERATE

    events.sort(key=lambda e: e.event_date)
    return events


def apply_events(household: Household, events: list[LifeEvent]) -> Household:
    """Reconstruct household state at a point in time by replaying events.

    Returns a new Household with all events applied (up to and including
    the last event in the list). Events should be filtered to the desired
    date range before calling this function.
    """
    state = {
        "customer_id": household.customer_id,
        "property_type": household.property_type,
        "build_era": household.build_era,
        "epc_rating": household.epc_rating,
        "bedrooms": household.bedrooms,
        "heating_system": household.heating_system,
        "boiler_age": household.boiler_age,
        "has_solar": household.has_solar,
        "solar_kwp": household.solar_kwp,
        "solar_install_year": household.solar_install_year,
        "has_battery": household.has_battery,
        "battery_kwh": household.battery_kwh,
        "has_ev": household.has_ev,
        "ev_charger_kw": household.ev_charger_kw,
        "has_smart_meter": household.has_smart_meter,
        "smart_meter_install_year": household.smart_meter_install_year,
        "insulation": household.insulation,
        "has_driveway": household.has_driveway,
        "roof_aspect": household.roof_aspect,
        "income_stress": household.income_stress,
    }

    for event in events:
        if event.event_type == "solar_install":
            state["has_solar"] = True
            state["solar_kwp"] = event.payload["solar_kwp"]
            state["solar_install_year"] = int(event.event_date[:4])

        elif event.event_type == "battery_installed":
            state["has_battery"] = True
            state["battery_kwh"] = event.payload["battery_kwh"]

        elif event.event_type == "ev_acquired":
            state["has_ev"] = True
            state["ev_charger_kw"] = event.payload["ev_charger_kw"]

        elif event.event_type == "heat_pump_installed":
            state["heating_system"] = HeatingSystem(event.payload["heating_system"])
            state["boiler_age"] = BoilerAge.NA

        elif event.event_type == "boiler_replaced":
            state["boiler_age"] = BoilerAge(event.payload["boiler_age"])

        elif event.event_type == "insulation_upgraded":
            state["insulation"] = InsulationLevel(event.payload["insulation"])

        elif event.event_type == "smart_meter_installed":
            state["has_smart_meter"] = True
            state["smart_meter_install_year"] = int(event.event_date[:4])

        elif event.event_type == "job_loss":
            state["income_stress"] = IncomeStress.HIGH

        elif event.event_type == "income_recovery":
            state["income_stress"] = IncomeStress.LOW

        elif event.event_type == "new_baby":
            if state["income_stress"] == IncomeStress.LOW:
                state["income_stress"] = IncomeStress.MODERATE

        elif event.event_type == "retirement_starts":
            if state["income_stress"] == IncomeStress.LOW:
                state["income_stress"] = IncomeStress.MODERATE

        elif event.event_type == "illness":
            state["income_stress"] = IncomeStress.HIGH

        elif event.event_type == "divorce":
            if state["income_stress"] == IncomeStress.LOW:
                state["income_stress"] = IncomeStress.MODERATE

    return Household(**state)


def household_at_date(
    household: Household,
    events: list[LifeEvent],
    as_of_date: str,
) -> Household:
    """Return the household state as of a specific date (YYYY-MM-DD).

    Filters events to those on or before as_of_date, then applies them.
    This is the canonical way to get a point-in-time household state.
    """
    applicable = [e for e in events if e.event_date <= as_of_date]
    return apply_events(household, applicable)
