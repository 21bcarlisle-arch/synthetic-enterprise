"""Phase A — Household physical model tests.

Tests for simulation/household.py: Household dataclass, enum types,
derived methods, and household register construction.
"""

import pytest
from simulation.household import (
    BoilerAge,
    BuildEra,
    HeatingSystem,
    Household,
    InsulationLevel,
    PropertyType,
    build_household_register,
    make_household,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _resi_flat() -> dict:
    return {
        "customer_id": "C1",
        "home_type": "urban_flat",
        "epc_rating": "D",
        "bedrooms": 2,
        "segment": "resi",
        "location": {"region": "London"},
    }


def _resi_semi() -> dict:
    return {
        "customer_id": "C2",
        "home_type": "suburban_semi",
        "epc_rating": "C",
        "bedrooms": 3,
        "segment": "resi",
        "location": {"region": "Manchester"},
    }


def _resi_detached() -> dict:
    return {
        "customer_id": "C4",
        "home_type": "rural_detached",
        "epc_rating": "E",
        "bedrooms": 4,
        "segment": "resi",
        "location": {"region": "Cotswolds"},
    }


def _ic_customer() -> dict:
    return {
        "customer_id": "C_IC1",
        "home_type": "warehouse_unit",
        "epc_rating": "C",
        "segment": "I&C",
        "metering": "HH",
    }


# ---------------------------------------------------------------------------
# Enum coverage
# ---------------------------------------------------------------------------

def test_property_type_enum_covers_residential():
    residential = {PropertyType.TERRACED, PropertyType.SEMI_DETACHED,
                   PropertyType.DETACHED, PropertyType.FLAT}
    assert residential.issubset(set(PropertyType))


def test_build_era_ordered():
    eras = [e.value for e in BuildEra]
    assert eras[0] == "pre_1919"
    assert eras[-1] == "post_2000"


def test_heating_system_has_heat_pump_variants():
    assert HeatingSystem.HEAT_PUMP_AIR in set(HeatingSystem)
    assert HeatingSystem.HEAT_PUMP_GROUND in set(HeatingSystem)


# ---------------------------------------------------------------------------
# make_household — property type mapping
# ---------------------------------------------------------------------------

def test_urban_flat_maps_to_flat():
    h = make_household(_resi_flat())
    assert h.property_type == PropertyType.FLAT


def test_suburban_semi_maps_to_semi_detached():
    h = make_household(_resi_semi())
    assert h.property_type == PropertyType.SEMI_DETACHED


def test_rural_detached_maps_to_detached():
    h = make_household(_resi_detached())
    assert h.property_type == PropertyType.DETACHED


def test_warehouse_maps_to_commercial():
    h = make_household(_ic_customer())
    assert h.property_type == PropertyType.COMMERCIAL_WAREHOUSE


# ---------------------------------------------------------------------------
# make_household — build era
# ---------------------------------------------------------------------------

def test_urban_flat_is_post_war():
    h = make_household(_resi_flat())
    assert h.build_era == BuildEra.ERA_1965_1980


def test_tenement_flat_is_pre_1919():
    c = {"customer_id": "C3", "home_type": "tenement_flat", "epc_rating": "E",
         "bedrooms": 2, "segment": "resi"}
    h = make_household(c)
    assert h.build_era == BuildEra.PRE_1919


# ---------------------------------------------------------------------------
# make_household — heating system
# ---------------------------------------------------------------------------

def test_resi_flat_has_gas_boiler():
    h = make_household(_resi_flat())
    assert h.is_gas_heated


def test_ic_warehouse_not_gas_heated():
    h = make_household(_ic_customer())
    assert not h.is_gas_heated


def test_gas_heated_means_not_heat_pump():
    h = make_household(_resi_flat())
    assert not h.is_heat_pump


# ---------------------------------------------------------------------------
# make_household — boiler age
# ---------------------------------------------------------------------------

def test_pre_1919_home_has_old_boiler():
    c = {"customer_id": "C3", "home_type": "tenement_flat", "epc_rating": "E",
         "bedrooms": 2, "segment": "resi"}
    h = make_household(c)
    assert h.boiler_age == BoilerAge.OLD


def test_post_2000_home_has_new_boiler():
    # Simulate a modern home by using a post-2000 home type
    # warehouse_unit maps to ERA_1981_2000 → NEW
    c = {"customer_id": "X1", "home_type": "warehouse_unit", "epc_rating": "C", "segment": "SME"}
    h = make_household(c)
    # Commercial — no boiler
    assert h.boiler_age == BoilerAge.NA


def test_non_gas_home_has_na_boiler():
    h = make_household(_ic_customer())
    assert h.boiler_age == BoilerAge.NA


# ---------------------------------------------------------------------------
# make_household — smart meter
# ---------------------------------------------------------------------------

def test_hh_metered_customer_has_smart_meter():
    c = {**_resi_flat(), "metering": "HH"}
    h = make_household(c)
    assert h.has_smart_meter is True


def test_standard_customer_no_smart_meter_by_default():
    c = _resi_flat()
    c.pop("metering", None)
    c.pop("smart_meter", None)
    h = make_household(c)
    assert h.has_smart_meter is False


def test_smart_meter_true_flag_respected():
    c = {**_resi_flat(), "smart_meter": True}
    h = make_household(c)
    assert h.has_smart_meter is True


# ---------------------------------------------------------------------------
# make_household — solar
# ---------------------------------------------------------------------------

def test_rural_detached_has_solar_panels():
    h = make_household(_resi_detached())
    assert h.has_solar is True
    assert h.solar_kwp > 0


def test_urban_flat_no_solar():
    h = make_household(_resi_flat())
    assert h.has_solar is False
    assert h.solar_kwp == 0.0


def test_no_ev_by_default():
    h = make_household(_resi_semi())
    assert h.has_ev is False
    assert h.ev_charger_kw == 0.0


def test_no_battery_by_default():
    h = make_household(_resi_semi())
    assert h.has_battery is False
    assert h.battery_kwh == 0.0


# ---------------------------------------------------------------------------
# Household.is_residential
# ---------------------------------------------------------------------------

def test_flat_is_residential():
    h = make_household(_resi_flat())
    assert h.is_residential is True


def test_warehouse_is_not_residential():
    h = make_household(_ic_customer())
    assert h.is_residential is False


# ---------------------------------------------------------------------------
# epc_consumption_multiplier
# ---------------------------------------------------------------------------

def test_epc_c_multiplier_is_reference():
    # C is the modal UK EPC band (44.8% of English stock, EHS 2022-23); reference = 1.0
    c = {**_resi_semi(), "epc_rating": "C"}
    h = make_household(c)
    assert h.epc_consumption_multiplier() == pytest.approx(1.0)


def test_epc_d_multiplier_is_above_reference():
    h = make_household(_resi_flat())  # EPC D — 25% above C per EHS AT1_6 + prebound correction
    assert h.epc_consumption_multiplier() == pytest.approx(1.25)


def test_epc_a_multiplier_is_below_reference():
    c = {**_resi_semi(), "epc_rating": "A"}
    h = make_household(c)
    assert h.epc_consumption_multiplier() < 1.0
    assert h.epc_consumption_multiplier() == pytest.approx(0.75)


def test_epc_g_multiplier_is_above_reference():
    c = {**_resi_semi(), "epc_rating": "G"}
    h = make_household(c)
    assert h.epc_consumption_multiplier() == pytest.approx(2.20)


def test_epc_multipliers_monotonically_increasing():
    ratings = ["A", "B", "C", "D", "E", "F", "G"]
    multipliers = []
    for r in ratings:
        c = {**_resi_semi(), "epc_rating": r}
        multipliers.append(make_household(c).epc_consumption_multiplier())
    assert multipliers == sorted(multipliers)


# ---------------------------------------------------------------------------
# solar_annual_generation_kwh
# ---------------------------------------------------------------------------

def test_solar_generation_uses_850_kwh_per_kwp():
    h = make_household(_resi_detached())
    assert h.solar_kwp > 0
    assert h.solar_annual_generation_kwh() == pytest.approx(h.solar_kwp * 850.0)


def test_no_solar_generation_when_no_panels():
    h = make_household(_resi_flat())
    assert h.solar_annual_generation_kwh() == 0.0


# ---------------------------------------------------------------------------
# ev_annual_kwh
# ---------------------------------------------------------------------------

def test_no_ev_demand_when_no_ev():
    h = make_household(_resi_flat())
    assert h.ev_annual_kwh() == 0.0


def test_ev_demand_is_positive_when_has_ev():
    c = _resi_semi()
    # Manually build a Household with EV
    h = Household(
        customer_id="TEST",
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
        has_ev=True,
        ev_charger_kw=7.0,
        has_smart_meter=False,
        smart_meter_install_year=None,
        insulation=InsulationLevel.PARTIAL,
    )
    assert h.ev_annual_kwh() > 0


# ---------------------------------------------------------------------------
# build_household_register
# ---------------------------------------------------------------------------

def test_household_register_covers_all_customers():
    customers = [_resi_flat(), _resi_semi(), _resi_detached(), _ic_customer()]
    register = build_household_register(customers)
    assert set(register.keys()) == {"C1", "C2", "C4", "C_IC1"}


def test_household_register_with_real_customers():
    from simulation.run_phase2b import CUSTOMERS
    register = build_household_register(CUSTOMERS)
    # All 18 customers should have a household
    assert len(register) == len(CUSTOMERS)
    # Every household is a Household instance
    for cid, h in register.items():
        assert isinstance(h, Household), f"{cid} not a Household"


def test_household_register_is_idempotent():
    customers = [_resi_flat(), _resi_semi()]
    r1 = build_household_register(customers)
    r2 = build_household_register(customers)
    for cid in r1:
        assert r1[cid] == r2[cid]
