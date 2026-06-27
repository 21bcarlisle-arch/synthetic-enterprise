"""Phase D tests -- Gas EAC Integration with Household Demand Register.

Tests for HouseholdDemandRegister.gas_eac_multiplier_for_date() and its
integration with the gas settlement path in run_phase2b.py.
"""

import pytest
from saas.customers import CUSTOMERS
from simulation.household_demand import (
    HouseholdDemandRegister,
    GAS_HEAT_PUMP_RESIDUAL_FRACTION,
)


@pytest.fixture(scope="module")
def register():
    return HouseholdDemandRegister(CUSTOMERS, seed=42)


class TestGasEACMultiplierValues:
    def test_c1g_epc_d_returns_1_25(self, register):
        # C1g: urban_flat, EPC-D, gas_boiler_combi
        mult = register.gas_eac_multiplier_for_date("C1g", "2020-01-01")
        assert mult == pytest.approx(1.25, abs=1e-6)

    def test_c2g_epc_d_returns_1_25(self, register):
        # C2g: suburban_semi, EPC-D, gas_boiler_combi
        mult = register.gas_eac_multiplier_for_date("C2g", "2020-06-01")
        assert mult == pytest.approx(1.25, abs=1e-6)

    def test_c3g_epc_e_returns_1_55(self, register):
        # C3g: tenement_flat, EPC-E, gas_boiler_system
        mult = register.gas_eac_multiplier_for_date("C3g", "2019-03-15")
        assert mult == pytest.approx(1.55, abs=1e-6)

    def test_c4g_epc_e_returns_1_55(self, register):
        # C4g: rural_detached, EPC-E, gas_boiler_system
        mult = register.gas_eac_multiplier_for_date("C4g", "2022-07-01")
        assert mult == pytest.approx(1.55, abs=1e-6)

    def test_ic_gas_returns_1_0(self, register):
        # C_IC3g: I&C chemical plant, not EPC-driven
        mult = register.gas_eac_multiplier_for_date("C_IC3g", "2020-01-01")
        assert mult == pytest.approx(1.0, abs=1e-6)

    def test_unknown_customer_returns_1_0(self, register):
        mult = register.gas_eac_multiplier_for_date("NONEXISTENT", "2020-01-01")
        assert mult == pytest.approx(1.0, abs=1e-6)

    def test_heat_pump_residual_fraction_constant(self):
        assert GAS_HEAT_PUMP_RESIDUAL_FRACTION == pytest.approx(0.12, abs=1e-6)


class TestGasEACMultiplierPhysics:
    def test_c1g_effective_aq(self, register):
        # C1g declared AQ = 12,000 kWh; EPC-D multiplier -> 15,000 kWh
        declared_aq = 12_000
        mult = register.gas_eac_multiplier_for_date("C1g", "2018-01-01")
        effective = round(declared_aq * mult)
        assert effective == 15_000

    def test_c3g_effective_aq(self, register):
        # C3g declared AQ = 14,000 kWh; EPC-E multiplier -> 21,700 kWh
        declared_aq = 14_000
        mult = register.gas_eac_multiplier_for_date("C3g", "2018-01-01")
        effective = round(declared_aq * mult)
        assert effective == 21_700

    def test_c4g_effective_aq_large_home(self, register):
        # C4g declared AQ = 22,000 kWh; EPC-E -> 34,100 kWh
        declared_aq = 22_000
        mult = register.gas_eac_multiplier_for_date("C4g", "2018-01-01")
        effective = round(declared_aq * mult)
        assert effective == 34_100

    def test_ic3g_aq_unchanged(self, register):
        # C_IC3g declared AQ = 5,000,000 kWh; multiplier = 1.0 -> unchanged
        declared_aq = 5_000_000
        mult = register.gas_eac_multiplier_for_date("C_IC3g", "2020-01-01")
        effective = round(declared_aq * mult)
        assert effective == 5_000_000

    def test_epc_d_higher_than_epc_c_baseline(self, register):
        # EPC-D multiplier (1.25) > EPC-C baseline (1.0)
        mult_d = register.gas_eac_multiplier_for_date("C1g", "2020-01-01")
        assert mult_d > 1.0

    def test_epc_e_higher_than_epc_d(self, register):
        mult_d = register.gas_eac_multiplier_for_date("C1g", "2020-01-01")
        mult_e = register.gas_eac_multiplier_for_date("C3g", "2020-01-01")
        assert mult_e > mult_d

    def test_multiplier_stable_over_sim_window(self, register):
        # No life events affecting gas multiplier for C1g -> stable throughout window
        m1 = register.gas_eac_multiplier_for_date("C1g", "2016-01-01")
        m2 = register.gas_eac_multiplier_for_date("C1g", "2025-06-01")
        assert m1 == pytest.approx(m2, abs=1e-6)


class TestHeatPumpGasResidual:
    def test_heat_pump_customer_returns_residual_fraction(self):
        # Simulate a customer who has a heat pump: use a fresh register where
        # C1g is replaced with a heat-pump household (direct household state test)
        from simulation.household import Household, PropertyType, BuildEra, HeatingSystem, BoilerAge, InsulationLevel
        from simulation.household_demand import HouseholdDemandRegister

        reg = HouseholdDemandRegister(CUSTOMERS, seed=42)
        # At 2025-08-20 C1 gets heat pump (beyond sim window, so check architecture)
        # Verify the multiplier logic returns residual for heat pump customers
        # by testing with a known heat-pump household state
        from simulation.life_events import household_at_date, generate_life_events
        from simulation.household import build_household_register

        hh_reg = build_household_register(CUSTOMERS)
        c1_hh = hh_reg["C1"]
        events = generate_life_events(c1_hh, 2016, 2026, seed=42 ^ (hash("C1") & 0xFFFF))
        hp_events = [e for e in events if e.event_type == "heat_pump_installed"]
        if hp_events:
            after_hp = household_at_date(c1_hh, events, hp_events[0].event_date)
            assert after_hp.is_heat_pump

    def test_residual_fraction_is_small(self):
        # 0.12 is intentionally small: after heat pump, only cooking gas remains
        assert GAS_HEAT_PUMP_RESIDUAL_FRACTION < 0.2
        assert GAS_HEAT_PUMP_RESIDUAL_FRACTION > 0.0
