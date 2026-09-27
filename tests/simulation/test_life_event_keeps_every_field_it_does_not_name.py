"""A life event changes the fields it names and nothing else.

The defect this refuses: `apply_events` rebuilt the household from a hand-written field list that
stopped at `income_stress`, so every field added after it -- NEED's floor-area band, loft and
cavity flags, mains-gas supply -- went back to `None` at the first event, a job loss included.
The list now comes from `dataclasses.fields(Household)`; restoring the hand list reds this file.
"""

from __future__ import annotations

import dataclasses
import typing

from simulation.household import (
    BoilerAge,
    BuildEra,
    HeatingSystem,
    Household,
    IncomeStress,
    InsulationLevel,
    PropertyType,
)
from simulation.life_events import EventType, LifeEvent, apply_events

# What each event is allowed to write, and a payload that makes it write.
_WRITES: dict[str, tuple[set[str], dict]] = {
    "solar_install": ({"has_solar", "solar_kwp", "solar_install_year"}, {"solar_kwp": 3.5}),
    "battery_installed": ({"has_battery", "battery_kwh"}, {"battery_kwh": 5.0}),
    "ev_acquired": ({"has_ev", "ev_charger_kw"}, {"ev_charger_kw": 7.0}),
    "heat_pump_installed": (
        {"heating_system", "boiler_age"}, {"heating_system": HeatingSystem.HEAT_PUMP_AIR.value}
    ),
    "boiler_replaced": ({"boiler_age"}, {"boiler_age": BoilerAge.NEW.value}),
    "insulation_upgraded": ({"insulation"}, {"insulation": InsulationLevel.FULL.value}),
    "smart_meter_installed": ({"has_smart_meter", "smart_meter_install_year"}, {}),
    "job_loss": ({"income_stress"}, {}),
    "income_recovery": ({"income_stress"}, {}),
    "new_baby": ({"income_stress"}, {}),
    "retirement_starts": ({"income_stress"}, {}),
    "illness": ({"income_stress"}, {}),
    "divorce": ({"income_stress"}, {}),
}


def _base() -> Household:
    return Household(
        customer_id="C1",
        property_type=PropertyType.SEMI_DETACHED,
        build_era=BuildEra.ERA_1945_1964,
        epc_rating="D",
        bedrooms=3,
        heating_system=HeatingSystem.GAS_BOILER_COMBI,
        boiler_age=BoilerAge.OLD,
        has_solar=False,
        solar_kwp=0.0,
        solar_install_year=None,
        has_battery=False,
        battery_kwh=0.0,
        has_ev=False,
        ev_charger_kw=0.0,
        has_smart_meter=False,
        smart_meter_install_year=None,
        insulation=InsulationLevel.PARTIAL,
        has_driveway=True,
        roof_aspect="south",
        income_stress=IncomeStress.MODERATE,
        floor_area_band="3",
        has_loft_insulation=True,
        has_cavity_wall_insulation=False,
        has_mains_gas_supply=True,
        output_area="E00000001",
    )


def test_the_base_sets_every_defaulted_field_off_its_default():
    """Without this a field added later with a `None` default would be dropped and the survival
    test below would compare `None` with `None` and pass."""
    base = _base()
    left_at_default = [
        f.name
        for f in dataclasses.fields(Household)
        if f.default is not dataclasses.MISSING and getattr(base, f.name) == f.default
    ]
    assert left_at_default == [], f"set these off their default in _base(): {left_at_default}"


def test_every_event_type_has_its_writes_declared():
    assert set(_WRITES) == set(typing.get_args(EventType))


def test_every_event_changes_what_it_names_and_keeps_everything_else():
    base = _base()
    changed_anything = []
    for event_type, (writes, payload) in _WRITES.items():
        after = apply_events(base, [LifeEvent("C1", "2020-06-01", event_type, payload)])
        moved = {
            f.name for f in dataclasses.fields(Household)
            if getattr(after, f.name) != getattr(base, f.name)
        }
        assert moved <= writes, f"{event_type} moved fields it does not name: {sorted(moved - writes)}"
        changed_anything.append(bool(moved))
    # The comparison can fail: at least one event must actually move something, or an
    # apply_events that returned its input untouched would pass the loop above.
    assert any(changed_anything)


def test_a_job_loss_keeps_the_need_fabric_fields():
    after = apply_events(_base(), [LifeEvent("C1", "2020-06-01", "job_loss", {})])
    assert after.income_stress is IncomeStress.HIGH
    assert (
        after.floor_area_band, after.has_loft_insulation,
        after.has_cavity_wall_insulation, after.has_mains_gas_supply, after.output_area,
    ) == ("3", True, False, True, "E00000001")
