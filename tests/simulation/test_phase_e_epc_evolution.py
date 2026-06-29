"""Phase E: EPC Band Evolution via Insulation Upgrades.

Tests that insulation_upgraded life events reduce energy consumption
by capping epc_consumption_multiplier() at insulation-level equivalents.

FULL insulation -> cap at 1.00 (EPC-C equivalent)
PARTIAL insulation -> cap at 1.25 (EPC-D equivalent)
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
from simulation.life_events import LifeEvent, apply_events, generate_life_events
from simulation.household_demand import HouseholdDemandRegister


def _make_hh(epc: str, insulation: InsulationLevel) -> Household:
    return Household(
        customer_id="test",
        property_type=PropertyType.FLAT,
        build_era=BuildEra.PRE_1919,
        epc_rating=epc,
        bedrooms=2,
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
        insulation=insulation,
        has_driveway=False,
        roof_aspect="na",
    )


class TestEPCMultiplierBaseValues:
    """Static EPC rating with no insulation upgrade."""

    def test_epc_e_poor_insulation(self):
        assert _make_hh("E", InsulationLevel.POOR).epc_consumption_multiplier() == pytest.approx(1.55)

    def test_epc_d_partial_insulation_no_cap(self):
        assert _make_hh("D", InsulationLevel.PARTIAL).epc_consumption_multiplier() == pytest.approx(1.25)

    def test_epc_c_full_insulation_unchanged(self):
        assert _make_hh("C", InsulationLevel.FULL).epc_consumption_multiplier() == pytest.approx(1.00)

    def test_epc_a_poor_not_capped(self):
        # A/B are already better than 1.00 so caps do not apply
        assert _make_hh("A", InsulationLevel.POOR).epc_consumption_multiplier() == pytest.approx(0.75)

    def test_epc_b_poor_not_capped(self):
        assert _make_hh("B", InsulationLevel.POOR).epc_consumption_multiplier() == pytest.approx(0.75)


class TestPartialInsulationCap:
    """PARTIAL insulation caps multiplier at EPC-D equivalent (1.25)."""

    def test_epc_e_partial_capped_at_d(self):
        assert _make_hh("E", InsulationLevel.PARTIAL).epc_consumption_multiplier() == pytest.approx(1.25)

    def test_epc_f_partial_capped_at_d(self):
        assert _make_hh("F", InsulationLevel.PARTIAL).epc_consumption_multiplier() == pytest.approx(1.25)

    def test_epc_g_partial_capped_at_d(self):
        assert _make_hh("G", InsulationLevel.PARTIAL).epc_consumption_multiplier() == pytest.approx(1.25)

    def test_epc_d_partial_already_at_cap(self):
        # EPC-D with PARTIAL = 1.25; cap is 1.25, so no change
        assert _make_hh("D", InsulationLevel.PARTIAL).epc_consumption_multiplier() == pytest.approx(1.25)


class TestFullInsulationCap:
    """FULL insulation caps multiplier at EPC-C equivalent (1.00)."""

    def test_epc_e_full_capped_at_c(self):
        assert _make_hh("E", InsulationLevel.FULL).epc_consumption_multiplier() == pytest.approx(1.00)

    def test_epc_d_full_capped_at_c(self):
        assert _make_hh("D", InsulationLevel.FULL).epc_consumption_multiplier() == pytest.approx(1.00)

    def test_epc_f_full_capped_at_c(self):
        assert _make_hh("F", InsulationLevel.FULL).epc_consumption_multiplier() == pytest.approx(1.00)

    def test_epc_g_full_capped_at_c(self):
        assert _make_hh("G", InsulationLevel.FULL).epc_consumption_multiplier() == pytest.approx(1.00)


class TestInsulationUpgradeLifeEvent:
    """insulation_upgraded events reduce epc_consumption_multiplier via apply_events."""

    def test_poor_to_partial_reduces_multiplier(self):
        hh = _make_hh("E", InsulationLevel.POOR)
        assert hh.epc_consumption_multiplier() == pytest.approx(1.55)
        event = LifeEvent(
            customer_id="test",
            event_date="2021-06-01",
            event_type="insulation_upgraded",
            payload={"insulation": "partial"},
        )
        evolved = apply_events(hh, [event])
        assert evolved.epc_consumption_multiplier() == pytest.approx(1.25)

    def test_partial_to_full_reduces_multiplier(self):
        hh = _make_hh("E", InsulationLevel.PARTIAL)
        assert hh.epc_consumption_multiplier() == pytest.approx(1.25)
        event = LifeEvent(
            customer_id="test",
            event_date="2023-03-01",
            event_type="insulation_upgraded",
            payload={"insulation": "full"},
        )
        evolved = apply_events(hh, [event])
        assert evolved.epc_consumption_multiplier() == pytest.approx(1.00)

    def test_poor_direct_to_full_reduces_multiplier(self):
        hh = _make_hh("G", InsulationLevel.POOR)
        event = LifeEvent(
            customer_id="test",
            event_date="2020-01-01",
            event_type="insulation_upgraded",
            payload={"insulation": "full"},
        )
        evolved = apply_events(hh, [event])
        assert evolved.epc_consumption_multiplier() == pytest.approx(1.00)

    def test_epc_d_to_full_reduces_multiplier(self):
        hh = _make_hh("D", InsulationLevel.PARTIAL)
        event = LifeEvent(
            customer_id="test",
            event_date="2022-01-01",
            event_type="insulation_upgraded",
            payload={"insulation": "full"},
        )
        evolved = apply_events(hh, [event])
        assert evolved.epc_consumption_multiplier() == pytest.approx(1.00)


class TestHouseholdDemandRegisterEPCEvolution:
    """Demand register eac_multiplier_for_date reflects insulation upgrades over time."""

    def test_register_epc_evolution_after_upgrade(self):
        customers = [
            {
                "customer_id": "C3",
                "segment": "resi",
                "commodity": "electricity",
                "eac_kwh": 4_200,
            }
        ]
        register = HouseholdDemandRegister(customers, seed=42)
        # epc_multiplier is the pure insulation-cap factor — strictly non-increasing
        # over time (insulation upgrades only ever reduce or hold it, never raise it).
        # eac_multiplier_for_date also includes EV and solar effects so is NOT monotonic.
        epc_2016 = register.epc_multiplier("C3", "2016-01-01")
        epc_2025 = register.epc_multiplier("C3", "2025-01-01")
        assert epc_2016 > 0
        assert epc_2025 > 0
        assert epc_2025 <= epc_2016

    def test_gas_multiplier_reduces_after_insulation(self):
        customers = [
            {
                "customer_id": "C3g",
                "segment": "resi",
                "commodity": "gas",
                "eac_kwh": 14_000,
            }
        ]
        register = HouseholdDemandRegister(customers, seed=42)
        gas_2016 = register.gas_eac_multiplier_for_date("C3g", "2016-01-01")
        gas_2025 = register.gas_eac_multiplier_for_date("C3g", "2025-01-01")
        # Gas multiplier should not increase over time (only insulation upgrades allowed)
        assert gas_2025 <= gas_2016 + 0.001
