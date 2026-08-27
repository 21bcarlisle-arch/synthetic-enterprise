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


def test_is_heat_pump_false_for_gas():
    h = _make_household(heating_system=HeatingSystem.GAS_BOILER_COMBI)
    assert h.is_heat_pump is False


def test_is_heat_pump_true_for_ashp():
    h = _make_household(heating_system=HeatingSystem.HEAT_PUMP_AIR)
    assert h.is_heat_pump is True


def test_is_heat_pump_true_for_gshp():
    h = _make_household(heating_system=HeatingSystem.HEAT_PUMP_GROUND)
    assert h.is_heat_pump is True


def test_seasonal_flatness_factor_a_is_high():
    h = _make_household(epc_rating="A", insulation=InsulationLevel.FULL)
    assert h.seasonal_flatness_factor() >= 0.85


def test_seasonal_flatness_factor_g_is_low():
    h = _make_household(epc_rating="G", insulation=InsulationLevel.POOR)
    assert h.seasonal_flatness_factor() <= 0.15


def test_seasonal_flatness_factor_c_partial():
    h = _make_household(epc_rating="C", insulation=InsulationLevel.PARTIAL)
    assert h.seasonal_flatness_factor() == pytest.approx(0.60)


def test_seasonal_flatness_full_insulation_uplift():
    h_partial = _make_household(epc_rating="C", insulation=InsulationLevel.PARTIAL)
    h_full = _make_household(epc_rating="C", insulation=InsulationLevel.FULL)
    assert h_full.seasonal_flatness_factor() > h_partial.seasonal_flatness_factor()


def test_seasonal_flatness_poor_insulation_penalty():
    h_partial = _make_household(epc_rating="C", insulation=InsulationLevel.PARTIAL)
    h_poor = _make_household(epc_rating="C", insulation=InsulationLevel.POOR)
    assert h_poor.seasonal_flatness_factor() < h_partial.seasonal_flatness_factor()


def test_seasonal_flatness_bounded_0_to_1():
    for epc in ["A", "B", "C", "D", "E", "F", "G"]:
        for insulation in (InsulationLevel.FULL, InsulationLevel.PARTIAL, InsulationLevel.POOR):
            h = _make_household(epc_rating=epc, insulation=insulation)
            assert 0.0 <= h.seasonal_flatness_factor() <= 1.0


# ---------------------------------------------------------------------------
# ONE PROPERTY, ONE HOUSEHOLD -- the gas leg is not a second family
# ---------------------------------------------------------------------------
# `household_of` has said since KNIFE step 28 that `C1` and `C1g` are two registrations
# against one physical property. `build_household_register` did not ask it, and minted a
# separate Household per gas leg -- so every dual-fuel home ran two independent streams of
# life events (babies, divorces, home moves) against one dwelling, with the halves free to
# disagree about whether anybody still lived there.
#
# LATENT, THEN NOT: only C1g-C4g existed until the 2026-08-26 dual-fuel draw took the count
# to 197 of 419 supply points, and the next full suite caught it -- each extra pseudo-household
# is another seed sampled against a known latent generator defect, and one of them landed on it.

from simulation.household import (  # noqa: E402
    ORPHANED_GAS_LEGS,
    build_household_register,
    household_of,
)


def _book():
    return [
        {"customer_id": "C1", "segment": "resi", "home_type": "suburban_semi",
         "epc_rating": "C", "bedrooms": 3},
        {"customer_id": "C1g", "segment": "resi", "home_type": "suburban_semi",
         "epc_rating": "C", "bedrooms": 3},
        {"customer_id": "C5", "segment": "resi", "home_type": "urban_flat",
         "epc_rating": "D", "bedrooms": 1},
    ]


def test_a_gas_leg_shares_its_electricity_points_household_OBJECT():
    """Identity, not equality. Two equal-but-distinct Households would still draw two
    independent event streams, which is the entire defect."""
    reg = build_household_register(_book())
    assert reg["C1g"] is reg["C1"]


def test_the_register_is_still_keyed_by_SUPPLY_POINT():
    """The partner. Consumers look up `register[customer_id]` for whichever point they hold;
    dropping the leg's key would turn a fidelity fix into a KeyError several thousand
    settlement periods deep, which is how the drawn-shape class defect behaved."""
    reg = build_household_register(_book())
    assert set(reg) == {"C1", "C1g", "C5"}


def test_an_electricity_only_home_is_untouched():
    reg = build_household_register(_book())
    assert reg["C5"] is not reg["C1"]
    assert household_of("C5") == "C5"


def test_the_distinct_household_count_is_the_PROPERTY_count():
    reg = build_household_register(_book())
    assert len({id(h) for h in reg.values()}) == 2


def test_the_real_book_has_no_orphaned_gas_leg():
    """A gas point with no electricity point in the same supply book is a real thing to
    notice. On a healthy roster there are none."""
    from simulation.run_phase2b import CUSTOMERS
    ORPHANED_GAS_LEGS.clear()
    build_household_register(CUSTOMERS)
    assert ORPHANED_GAS_LEGS == set()


def test_an_orphaned_leg_gets_its_own_household_and_is_RECORDED():
    """FAIL-VISIBLE, not fail-silent and not fail-closed. Refusing the run would stop a whole
    decade over one malformed registration; silently aliasing it to nothing would hide it.
    It gets a household so the run proceeds, and it is named so a control can see it."""
    ORPHANED_GAS_LEGS.clear()
    reg = build_household_register([
        {"customer_id": "C9g", "segment": "resi", "home_type": "urban_flat",
         "epc_rating": "D", "bedrooms": 1}])
    assert "C9g" in reg
    assert ORPHANED_GAS_LEGS == {"C9g"}
    ORPHANED_GAS_LEGS.clear()
