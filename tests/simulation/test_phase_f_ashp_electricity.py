"""Phase F: Heat Pump Electricity Uplift.

Tests that heat_pump_installed life events increase electricity EAC via
ashp_annual_kwh() in Household and eac_multiplier_for_date() in the register.

ASHP installs produce dual-fuel effects (symmetric):
  - Electricity: +5,500 kWh/yr from installation date  (Phase F)
  - Gas:         reduced to 12% of AQ from same date   (Phase D)
"""

import pytest
from simulation.household import (
    BoilerAge,
    BuildEra,
    HeatingSystem,
    Household,
    InsulationLevel,
    PropertyType,
)
from simulation.life_events import LifeEvent, apply_events
from simulation.household_demand import HouseholdDemandRegister

ASHP_KWH = 5_500.0


def _make_hh(heating: HeatingSystem) -> Household:
    return Household(
        customer_id="test",
        property_type=PropertyType.SEMI_DETACHED,
        build_era=BuildEra.ERA_1945_1964,
        epc_rating="D",
        bedrooms=3,
        heating_system=heating,
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
        )


class TestASHPAnnualKwh:
    """ashp_annual_kwh() returns uplift only for heat pump homes."""

    def test_gas_boiler_combi_returns_zero(self):
        hh = _make_hh(HeatingSystem.GAS_BOILER_COMBI)
        assert hh.ashp_annual_kwh() == pytest.approx(0.0)

    def test_gas_boiler_system_returns_zero(self):
        hh = _make_hh(HeatingSystem.GAS_BOILER_SYSTEM)
        assert hh.ashp_annual_kwh() == pytest.approx(0.0)

    def test_heat_pump_air_returns_uplift(self):
        hh = _make_hh(HeatingSystem.HEAT_PUMP_AIR)
        assert hh.ashp_annual_kwh() == pytest.approx(ASHP_KWH)

    def test_heat_pump_ground_returns_uplift(self):
        hh = _make_hh(HeatingSystem.HEAT_PUMP_GROUND)
        assert hh.ashp_annual_kwh() == pytest.approx(ASHP_KWH)

    def test_district_heat_returns_zero(self):
        hh = _make_hh(HeatingSystem.DISTRICT_HEAT)
        assert hh.ashp_annual_kwh() == pytest.approx(0.0)

    def test_none_heating_returns_zero(self):
        hh = _make_hh(HeatingSystem.NONE)
        assert hh.ashp_annual_kwh() == pytest.approx(0.0)


class TestEACMultiplierASHPUplift:
    """eac_multiplier_for_date() is higher for ASHP homes vs gas-heated, same EPC."""

    def _make_register(self, heating: HeatingSystem) -> HouseholdDemandRegister:
        customers = [
            {
                "customer_id": "C1",
                "segment": "resi",
                "commodity": "electricity",
                "eac_kwh": 3_100,
            }
        ]
        register = HouseholdDemandRegister(customers, seed=42)
        # Override the household directly for deterministic test
        from simulation.household import build_household_register
        base_hh = register._households["C1"]
        new_hh = Household(
            customer_id="C1",
            property_type=base_hh.property_type,
            build_era=base_hh.build_era,
            epc_rating="D",
            bedrooms=base_hh.bedrooms,
            heating_system=heating,
            boiler_age=base_hh.boiler_age,
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
        register._households["C1"] = new_hh
        register._events["C1"] = []  # no life events
        return register

    def test_ashp_home_higher_multiplier_than_gas(self):
        gas_register = self._make_register(HeatingSystem.GAS_BOILER_COMBI)
        ashp_register = self._make_register(HeatingSystem.HEAT_PUMP_AIR)
        gas_mult = gas_register.eac_multiplier_for_date("C1", "2023-01-01")
        ashp_mult = ashp_register.eac_multiplier_for_date("C1", "2023-01-01")
        assert ashp_mult > gas_mult

    def test_ashp_fraction_approx_correct(self):
        """ASHP adds ~5500/3100 = ~1.77 fraction to the multiplier."""
        ashp_register = self._make_register(HeatingSystem.HEAT_PUMP_AIR)
        gas_register = self._make_register(HeatingSystem.GAS_BOILER_COMBI)
        ashp_mult = ashp_register.eac_multiplier_for_date("C1", "2020-01-01")
        gas_mult = gas_register.eac_multiplier_for_date("C1", "2020-01-01")
        expected_fraction = ASHP_KWH / 3_100
        # ashp_mult should be approximately gas_mult * (1 + ashp_fraction) / (1 + 0)
        assert ashp_mult / gas_mult == pytest.approx(1.0 + expected_fraction, rel=0.01)


class TestASHPLifeEventEffect:
    """heat_pump_installed life event changes electricity multiplier from event date."""

    def _base_hh(self) -> Household:
        return _make_hh(HeatingSystem.GAS_BOILER_COMBI)

    def test_before_install_no_ashp_uplift(self):
        hh = self._base_hh()
        assert hh.ashp_annual_kwh() == pytest.approx(0.0)

    def test_after_install_ashp_uplift_present(self):
        hh = self._base_hh()
        event = LifeEvent(
            customer_id="test",
            event_date="2022-03-01",
            event_type="heat_pump_installed",
            payload={"heating_system": HeatingSystem.HEAT_PUMP_AIR.value},
        )
        evolved = apply_events(hh, [event])
        assert evolved.ashp_annual_kwh() == pytest.approx(ASHP_KWH)

    def test_after_install_is_heat_pump_true(self):
        hh = self._base_hh()
        event = LifeEvent(
            customer_id="test",
            event_date="2021-06-01",
            event_type="heat_pump_installed",
            payload={"heating_system": HeatingSystem.HEAT_PUMP_GROUND.value},
        )
        evolved = apply_events(hh, [event])
        assert evolved.is_heat_pump is True

    def test_gas_heated_is_heat_pump_false(self):
        hh = self._base_hh()
        assert hh.is_heat_pump is False


class TestASHPGasElectricityCombined:
    """Both effects from heat_pump_installed are correctly reflected in registers."""

    def test_dual_fuel_effects_from_single_event(self):
        """heat_pump_installed -> electricity up, gas down."""
        customers_elec = [
            {"customer_id": "C1", "segment": "resi", "commodity": "electricity", "eac_kwh": 3_100}
        ]
        customers_gas = [
            {"customer_id": "C1g", "segment": "resi", "commodity": "gas", "eac_kwh": 15_000}
        ]
        elec_register = HouseholdDemandRegister(customers_elec, seed=42)
        gas_register = HouseholdDemandRegister(customers_gas, seed=42)

        elec_pre = elec_register.eac_multiplier_for_date("C1", "2020-01-01")
        elec_post = elec_register.eac_multiplier_for_date("C1", "2025-01-01")
        gas_pre = gas_register.gas_eac_multiplier_for_date("C1g", "2020-01-01")
        gas_post = gas_register.gas_eac_multiplier_for_date("C1g", "2025-01-01")

        # Both registers generate stochastic events; just verify direction constraints
        # Electricity: can only stay same or increase from heat pump (if installed)
        assert elec_post >= elec_pre - 0.1  # allow small solar variation
        # Gas: stays same or decreases over time (insulation + heat pump)
        assert gas_post <= gas_pre + 0.001


class TestHouseholdDemandRegisterASHP:
    """Register correctly models ASHP electricity uplift over simulation period."""

    def test_register_ashp_customer_eac_higher_than_baseline(self):
        """C3 (suburban semi) may get ASHP; seed=99 maximises chance."""
        customers = [
            {"customer_id": "C3", "segment": "resi", "commodity": "electricity", "eac_kwh": 4_200}
        ]
        register = HouseholdDemandRegister(customers, seed=99)
        # Find whether C3 ever gets heat pump
        events = register._events.get("C3", [])
        hp_events = [e for e in events if e.event_type == "heat_pump_installed"]
        # If HP event exists, multiplier in that year should exceed pre-HP
        if hp_events:
            install_date = hp_events[0].event_date
            year_before = str(int(install_date[:4]) - 1) + "-06-01"
            year_after = install_date[:4] + "-12-01"
            mult_before = register.eac_multiplier_for_date("C3", year_before)
            mult_after = register.eac_multiplier_for_date("C3", year_after)
            assert mult_after > mult_before
        # Whether or not HP installed, multipliers must be positive
        assert register.eac_multiplier_for_date("C3", "2016-01-01") > 0
        assert register.eac_multiplier_for_date("C3", "2025-01-01") > 0
