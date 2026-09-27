"""Every domestic, non-HH electricity premise in the live book reads a COMPLETE stored weather cell.

WHY THIS EXISTS. The per-cell store is pulled for the cells the book occupies, and nothing re-pulls
it when a home moves. `d9374ae9e` re-sited 75% of homes; 30 premises landed >5 km from any stored
cell, `fabric_eligibility` refused them honestly, and book fabric kWh fell 28% with no control red
anywhere (`docs/staging/SEAT_FINDING_THE_SITING_REBUILD_MOVED_30_PREMISES_OFF_THE_WEATHER_STORE_AND_28_PERCENT_OF_FABRIC_VOLUME_ONTO_THE_LEGACY_SHAPE_2026-09-27.md`).
The refusal is correct per premise; what was missing was anyone asking it of the whole book.

KEYED TO THE PROPERTY, not to a count: the offender list is the premises the runner's own predicate
refuses for want of weather, and it must be empty. The remedy the failure prints is the refusal's
own sentence -- extend the store, never pull a single property.
"""
from __future__ import annotations

import datetime as dt

import pytest

from simulation import fabric_demand_path as fdp
from simulation.household_demand import HouseholdDemandRegister
from simulation.live_population import live_drawn_households
from simulation.run_phase2b import CUSTOMERS, ELEC_CUSTOMERS, REPORT_START, is_hh_customer


@pytest.fixture(scope="module")
def book():
    register = HouseholdDemandRegister(CUSTOMERS, drawn_households=live_drawn_households())
    return register, fdp.WeatherWorldSource.load()


def _verdicts(register, weather) -> list[fdp.FabricEligibility]:
    """The runner's eligibility pass (`fabric_providers_for_book`) without trace generation."""
    start = dt.date.fromisoformat(REPORT_START).isoformat()
    out = []
    for customer in ELEC_CUSTOMERS:
        site = weather.site_for(customer)
        out.append(fdp.fabric_eligibility(
            customer,
            register.household_at_date(str(customer["customer_id"]), start),
            is_half_hourly_metered=is_hh_customer(customer),
            weather_available=weather.available(site),
            weather_site=site,
        ))
    return out


def _off_store(verdicts) -> list[str]:
    return [f"{v.customer_id}: {v.reason}" for v in verdicts
            if not v.is_eligible and v.reason.startswith(fdp.NO_ARCHIVE_REFUSAL)]


@pytest.mark.xfail(strict=True, reason=(
    "OWED, 2026-09-27: 42 premises off-store at HEAD. The re-pull stopped on Open-Meteo's DAILY "
    "quota after 8 of 118 cells; a half-built store is WORSE (100 off), because the HadUK pass "
    "stores every new cell temperature-only and a premise then resolves to its own incomplete cell "
    "instead of a complete neighbour. Land the store only when complete, and delete this marker in "
    "that commit -- strict, so the completing commit cannot forget."))
def test_every_domestic_non_hh_premise_resolves_to_a_complete_stored_cell(book):
    register, weather = book
    verdicts = _verdicts(register, weather)
    # Not vacuous: the population this asks about is non-empty and mostly fabric-driven.
    assert sum(v.is_eligible for v in verdicts) > 0, "no premise is fabric-driven: nothing was asked"
    offenders = _off_store(verdicts)
    assert not offenders, (
        f"{len(offenders)} domestic premise(s) settle on the legacy shape for want of stored "
        f"weather -- run `python3 -m tools.build_weather_world --build`:\n  "
        + "\n  ".join(offenders))


def test_the_control_names_a_premise_whose_cell_the_store_does_not_hold(book):
    """The rare branch CAN be taken: withdraw one fabric-driven premise's cell and it is named."""
    register, weather = book
    victim = next(v.customer_id for v in _verdicts(register, weather) if v.is_eligible)
    victim_site = weather.site_for(next(c for c in ELEC_CUSTOMERS if c["customer_id"] == victim))

    class Withdrawn(fdp.WeatherWorldSource):
        def available(self, site: str) -> bool:
            return site != victim_site and super().available(site)

    named = _off_store(_verdicts(register, Withdrawn(weather.world)))
    assert any(line.startswith(f"{victim}: ") for line in named), named
