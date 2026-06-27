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
- smart_meter_installed: smart meter fitted (if not already)
- insulation_upgraded: loft or wall insulation improved (upgrades InsulationLevel)

Epistemic constraint: these events are SIM ground truth.  The company layer
cannot read this log directly.  It observes consequences — higher electricity
consumption, change in MPAN metering type, outbound contact from customer, or
EPC rating update from the national register.

Calibration sources: docs/market_research/HUMAN_SIMULATION_RESEARCH.md
- Solar: Finding 5 (DESNZ REPD, 3% 2016 → 5.7% 2025)
- EV: Finding 6 (DfT + EHS, 0.3% 2016 → 7% 2025)
- Heat pump: Finding 4 (EHS AT4, ~0.8% 2022 → ~2% 2025)
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Literal

from simulation.household import (
    BoilerAge,
    BuildEra,
    HeatingSystem,
    Household,
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
    if seed is None:
        seed = hash(household.customer_id) % (2**31)
    rng = random.Random(seed)

    events: list[LifeEvent] = []

    # Track mutable state for conditional logic (e.g. battery only if solar)
    has_solar = household.has_solar
    has_battery = household.has_battery
    has_ev = household.has_ev
    boiler_age = household.boiler_age
    insulation = household.insulation
    heating = household.heating_system

    for year in range(sim_start_year, sim_end_year + 1):

        # -- Solar PV install --
        if (not has_solar
                and household.is_residential
                and household.property_type != PropertyType.FLAT):
            prob = _annual_prob(_SOLAR_INSTALL_PROB_BY_YEAR, year)
            if rng.random() < prob:
                kwp = round(rng.uniform(2.5, 4.5), 1)
                events.append(LifeEvent(
                    customer_id=household.customer_id,
                    event_date=_random_date_in_year(year, rng),
                    event_type="solar_install",
                    payload={"solar_kwp": kwp},
                ))
                has_solar = True

        # -- Battery install (conditional on solar) --
        if has_solar and not has_battery:
            prob = _annual_prob(_BATTERY_INSTALL_PROB_WITH_SOLAR_BY_YEAR, year)
            if rng.random() < prob:
                kwh = round(rng.uniform(4.0, 13.5), 1)
                events.append(LifeEvent(
                    customer_id=household.customer_id,
                    event_date=_random_date_in_year(year, rng),
                    event_type="battery_installed",
                    payload={"battery_kwh": kwh},
                ))
                has_battery = True

        # -- EV acquisition --
        if not has_ev and household.is_residential:
            prob = _annual_prob(_EV_ACQUIRED_PROB_BY_YEAR, year)
            if rng.random() < prob:
                charger_kw = rng.choice([3.7, 7.0, 7.0, 22.0])  # weighted toward 7kW
                events.append(LifeEvent(
                    customer_id=household.customer_id,
                    event_date=_random_date_in_year(year, rng),
                    event_type="ev_acquired",
                    payload={"ev_charger_kw": charger_kw},
                ))
                has_ev = True

        # -- Heat pump installation (gas-heated resi) --
        if (household.is_residential
                and heating in (HeatingSystem.GAS_BOILER_COMBI, HeatingSystem.GAS_BOILER_SYSTEM)):
            prob = _annual_prob(_HEAT_PUMP_INSTALL_PROB_BY_YEAR, year)
            if rng.random() < prob:
                events.append(LifeEvent(
                    customer_id=household.customer_id,
                    event_date=_random_date_in_year(year, rng),
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
            if prob and rng.random() < prob:
                events.append(LifeEvent(
                    customer_id=household.customer_id,
                    event_date=_random_date_in_year(year, rng),
                    event_type="boiler_replaced",
                    payload={"boiler_age": BoilerAge.NEW.value},
                ))
                boiler_age = BoilerAge.NEW

        # -- Insulation upgrade --
        if insulation == InsulationLevel.POOR:
            if rng.random() < _INSULATION_UPGRADE_PROB_POOR:
                events.append(LifeEvent(
                    customer_id=household.customer_id,
                    event_date=_random_date_in_year(year, rng),
                    event_type="insulation_upgraded",
                    payload={"insulation": InsulationLevel.PARTIAL.value},
                ))
                insulation = InsulationLevel.PARTIAL
        elif insulation == InsulationLevel.PARTIAL:
            if rng.random() < _INSULATION_UPGRADE_PROB_PARTIAL:
                events.append(LifeEvent(
                    customer_id=household.customer_id,
                    event_date=_random_date_in_year(year, rng),
                    event_type="insulation_upgraded",
                    payload={"insulation": InsulationLevel.FULL.value},
                ))
                insulation = InsulationLevel.FULL

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
