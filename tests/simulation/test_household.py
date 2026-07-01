"""Tests for simulation/household.py -- Phase A physical model."""

import pytest

from simulation.household import (
    ASHP_BASE_ELECTRICITY_KWH,
    BoilerAge,
    BuildEra,
    HeatingSystem,
    Household,
    InsulationLevel,
    PropertyType,
)


def _make_household(**overrides) -> Household:
    defaults = dict(
        customer_id="C_TEST",
        property_type=PropertyType.SEMI_DETACHED,
        build_era=BuildEra.ERA_1945_1964,
        epc_rating="C",
        bedrooms=3,
        heating_system=HeatingSystem.GAS_BOILER_COMBI,
        boiler_age=BoilerAge.MID,
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
    )
    defaults.update(overrides)
    return Household(**defaults)


# EPC multiplier tests
def test_epc_c_multiplier_is_one():
    h = _make_household(epc_rating="C", insulation=InsulationLevel.PARTIAL)
    assert h.epc_consumption_multiplier() == pytest.approx(1.00)


def test_epc_e_multiplier_is_1p55():
    h = _make_household(epc_rating="E", insulation=InsulationLevel.POOR)
    assert h.epc_consumption_multiplier() == pytest.approx(1.55)


def test_epc_g_multiplier_is_2p2():
    h = _make_household(epc_rating="G", insulation=InsulationLevel.POOR)
    assert h.epc_consumption_multiplier() == pytest.approx(2.20)


def test_epc_a_multiplier_is_0p75():
    h = _make_household(epc_rating="A", insulation=InsulationLevel.FULL)
    assert h.epc_consumption_multiplier() == pytest.approx(0.75)


def test_full_insulation_caps_epc_e_to_one():
    h = _make_household(epc_rating="E", insulation=InsulationLevel.FULL)
    assert h.epc_consumption_multiplier() == pytest.approx(1.00)


def test_partial_insulation_caps_epc_g_to_1p25():
    h = _make_household(epc_rating="G", insulation=InsulationLevel.PARTIAL)
    assert h.epc_consumption_multiplier() == pytest.approx(1.25)


def test_full_insulation_no_uplift_when_already_low():
    # EPC C with FULL insulation: base=1.00, full cap only applies if >1.0
    h = _make_household(epc_rating="C", insulation=InsulationLevel.FULL)
    assert h.epc_consumption_multiplier() == pytest.approx(1.00)


# Property classification
def test_is_residential_flat_true():
    h = _make_household(property_type=PropertyType.FLAT)
    assert h.is_residential is True


def test_is_residential_industrial_false():
    h = _make_household(property_type=PropertyType.INDUSTRIAL)
    assert h.is_residential is False


def test_is_gas_heated_combi():
    h = _make_household(heating_system=HeatingSystem.GAS_BOILER_COMBI)
    assert h.is_gas_heated is True


def test_is_not_gas_heated_heat_pump():
    h = _make_household(heating_system=HeatingSystem.HEAT_PUMP_AIR)
    assert h.is_gas_heated is False


def test_hp_eligible_detached_two_bed():
    h = _make_household(
        property_type=PropertyType.DETACHED,
        bedrooms=3,
        heating_system=HeatingSystem.GAS_BOILER_SYSTEM,
    )
    assert h.hp_eligible is True


def test_hp_eligible_flat_false():
    h = _make_household(property_type=PropertyType.FLAT)
    assert h.hp_eligible is False


# EV and ASHP methods
def test_ev_annual_kwh_no_ev_zero():
    h = _make_household(has_ev=False, ev_charger_kw=0.0)
    assert h.ev_annual_kwh() == pytest.approx(0.0)


def test_ev_annual_kwh_with_ev():
    h = _make_household(has_ev=True, ev_charger_kw=7.0)
    assert h.ev_annual_kwh() == pytest.approx(7500 / 3.5)


def test_ashp_annual_kwh_gas_boiler_zero():
    h = _make_household(heating_system=HeatingSystem.GAS_BOILER_COMBI)
    assert h.ashp_annual_kwh() == pytest.approx(0.0)


def test_ashp_annual_kwh_heat_pump():
    h = _make_household(heating_system=HeatingSystem.HEAT_PUMP_AIR)
    assert h.ashp_annual_kwh() == pytest.approx(ASHP_BASE_ELECTRICITY_KWH)


def test_solar_generation_no_solar_zero():
    h = _make_household(has_solar=False, solar_kwp=0.0)
    assert h.solar_annual_generation_kwh() == pytest.approx(0.0)


def test_solar_generation_3kwp():
    h = _make_household(has_solar=True, solar_kwp=3.0, solar_install_year=2020)
    assert h.solar_annual_generation_kwh() == pytest.approx(3.0 * 850.0)
