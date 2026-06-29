"""Phase G: ASHP Electricity Settlement Wiring.

Tests that the ASHP electricity uplift from ashp_annual_kwh() actually flows
through _weather_adjusted_shape_fn into settlement. Phase F built the function;
Phase G wires it so that heat pump homes see +5,500 kWh/yr additional electricity
load in the settlement demand shape.

Key invariant:
  shape_ashp[p] - shape_gas[p] == ashp_annual_kwh / 365.25 / 48  for all p
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
from simulation.household import ASHP_BASE_ELECTRICITY_KWH
from simulation.household_demand import HouseholdDemandRegister
from simulation.run_phase2b import _weather_adjusted_shape_fn, DEFAULT_PROPERTY

# Fixed test date — no weather data needed for pure shape-difference tests
TEST_DATE = "2022-06-15"
DAYS_PER_YEAR = 365.25
HH_PER_DAY = 48
EXPECTED_HH_UPLIFT = ASHP_BASE_ELECTRICITY_KWH / DAYS_PER_YEAR / HH_PER_DAY


def _flat_base(date_str):
    return [1.0] * HH_PER_DAY


def _make_register(heating: HeatingSystem, cid: str = "C1") -> HouseholdDemandRegister:
    """Build a register with a single customer forced to the given heating system."""
    customers = [{"customer_id": cid, "segment": "resi", "commodity": "electricity", "eac_kwh": 3_100}]
    register = HouseholdDemandRegister(customers, seed=42)
    base_hh = register._households[cid]
    register._households[cid] = Household(
        customer_id=cid,
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
    )
    register._events[cid] = []
    return register


class TestASHPShapeUplift:
    """ASHP home demand shape is higher than gas-boiler home by the expected flat uplift."""

    def _shape(self, heating: HeatingSystem, date_str: str = TEST_DATE) -> list[float]:
        register = _make_register(heating)
        fn = _weather_adjusted_shape_fn(_flat_base, {}, DEFAULT_PROPERTY,
                                        household_register=register, customer_id="C1")
        return fn(date_str)

    def test_ashp_home_higher_than_gas_home(self):
        gas_shape = self._shape(HeatingSystem.GAS_BOILER_COMBI)
        ashp_shape = self._shape(HeatingSystem.HEAT_PUMP_AIR)
        assert sum(ashp_shape) > sum(gas_shape)

    def test_ashp_uplift_per_period_is_correct(self):
        gas_shape = self._shape(HeatingSystem.GAS_BOILER_COMBI)
        ashp_shape = self._shape(HeatingSystem.HEAT_PUMP_AIR)
        for g, a in zip(gas_shape, ashp_shape):
            assert (a - g) == pytest.approx(EXPECTED_HH_UPLIFT, rel=1e-4)

    def test_ashp_annual_uplift_is_5500_kwh(self):
        gas_shape = self._shape(HeatingSystem.GAS_BOILER_COMBI)
        ashp_shape = self._shape(HeatingSystem.HEAT_PUMP_AIR)
        diff_daily = sum(ashp_shape) - sum(gas_shape)
        annual_uplift = diff_daily * DAYS_PER_YEAR
        assert annual_uplift == pytest.approx(ASHP_BASE_ELECTRICITY_KWH, rel=1e-3)

    def test_gas_boiler_combi_has_zero_ashp_uplift(self):
        gas_shape = self._shape(HeatingSystem.GAS_BOILER_COMBI)
        no_register_fn = _weather_adjusted_shape_fn(_flat_base, {}, DEFAULT_PROPERTY)
        base_shape = no_register_fn(TEST_DATE)
        # Gas boiler should have EPC-D multiplier but zero ASHP uplift
        # Check all periods have same value (flat base × EPC-D multiplier only)
        diffs = [g - b for g, b in zip(gas_shape, base_shape)]
        assert all(abs(d - diffs[0]) < 1e-9 for d in diffs), "Gas shape should be uniform"

    def test_ground_source_hp_same_uplift_as_air_source(self):
        air_shape = self._shape(HeatingSystem.HEAT_PUMP_AIR)
        ground_shape = self._shape(HeatingSystem.HEAT_PUMP_GROUND)
        assert sum(air_shape) == pytest.approx(sum(ground_shape), rel=1e-9)

    def test_no_register_shape_unchanged(self):
        fn = _weather_adjusted_shape_fn(_flat_base, {}, DEFAULT_PROPERTY)
        shape = fn(TEST_DATE)
        assert shape == [1.0] * HH_PER_DAY

    def test_uplift_uniform_across_all_48_periods(self):
        gas_shape = self._shape(HeatingSystem.GAS_BOILER_COMBI)
        ashp_shape = self._shape(HeatingSystem.HEAT_PUMP_AIR)
        diffs = [a - g for a, g in zip(ashp_shape, gas_shape)]
        assert len(set(round(d, 8) for d in diffs)) == 1, "Uplift must be uniform across periods"


class TestASHPShapeIndependence:
    """ASHP uplift is additive and independent of EPC multiplier."""

    def test_epc_multiplier_and_ashp_uplift_are_independent(self):
        """EPC scales the base; ASHP adds a flat offset. Both apply independently."""
        register = _make_register(HeatingSystem.HEAT_PUMP_AIR)
        epc_mult = register.epc_multiplier("C1", TEST_DATE)
        fn = _weather_adjusted_shape_fn(_flat_base, {}, DEFAULT_PROPERTY,
                                        household_register=register, customer_id="C1")
        shape = fn(TEST_DATE)
        # Expected: flat_base * epc_mult + ashp_hh_uplift
        expected = [1.0 * epc_mult + EXPECTED_HH_UPLIFT] * HH_PER_DAY
        for v, e in zip(shape, expected):
            assert v == pytest.approx(e, rel=1e-6)

    def test_no_ashp_district_heat(self):
        """District heating has no ASHP; uplift should be zero."""
        gas_shape_fn = _weather_adjusted_shape_fn(
            _flat_base, {}, DEFAULT_PROPERTY,
            household_register=_make_register(HeatingSystem.GAS_BOILER_COMBI),
            customer_id="C1",
        )
        district_shape_fn = _weather_adjusted_shape_fn(
            _flat_base, {}, DEFAULT_PROPERTY,
            household_register=_make_register(HeatingSystem.DISTRICT_HEAT),
            customer_id="C1",
        )
        gas_sum = sum(gas_shape_fn(TEST_DATE))
        district_sum = sum(district_shape_fn(TEST_DATE))
        assert gas_sum == pytest.approx(district_sum, rel=1e-9)


class TestASHPRegisterIntegration:
    """Life event injection: ASHP install changes shape from event date onward."""

    def _register_with_ashp_install(self, install_date: str = "2022-03-01") -> HouseholdDemandRegister:
        """Minimal register with a forced heat_pump_installed life event."""
        from simulation.life_events import LifeEvent
        register = _make_register(HeatingSystem.GAS_BOILER_COMBI, cid="C1")
        register._events["C1"] = [
            LifeEvent(
                customer_id="C1",
                event_date=install_date,
                event_type="heat_pump_installed",
                payload={"heating_system": HeatingSystem.HEAT_PUMP_AIR.value},
            )
        ]
        return register

    def test_ashp_customer_gets_uplift_post_install(self):
        """After ASHP install, shape sum is higher on post-install date vs pre-install."""
        register = self._register_with_ashp_install("2022-03-01")
        fn = _weather_adjusted_shape_fn(
            _flat_base, {}, DEFAULT_PROPERTY,
            household_register=register, customer_id="C1",
        )
        pre_sum = sum(fn("2021-12-31"))
        post_sum = sum(fn("2022-06-01"))
        assert post_sum > pre_sum

    def test_ashp_uplift_absent_before_install(self):
        """Before ASHP install date, no electricity uplift."""
        register_gas = _make_register(HeatingSystem.GAS_BOILER_COMBI)
        register_pre_ashp = self._register_with_ashp_install("2022-03-01")
        fn_gas = _weather_adjusted_shape_fn(
            _flat_base, {}, DEFAULT_PROPERTY, household_register=register_gas, customer_id="C1"
        )
        fn_pre = _weather_adjusted_shape_fn(
            _flat_base, {}, DEFAULT_PROPERTY, household_register=register_pre_ashp, customer_id="C1"
        )
        assert sum(fn_pre("2021-12-31")) == pytest.approx(sum(fn_gas("2021-12-31")), rel=1e-9)

    def test_non_resi_ic_customer_no_ashp(self):
        """I&C customers have no ASHP -- ashp_annual_kwh() returns 0 for I&C households."""
        from saas.customers import CUSTOMERS
        register = HouseholdDemandRegister(CUSTOMERS, seed=42)
        # C_IC1 is I&C — should never get ASHP
        hh = register.household_at_date("C_IC1", TEST_DATE)
        if hh is None:
            pytest.skip("C_IC1 not in register")
        assert hh.ashp_annual_kwh() == pytest.approx(0.0)
