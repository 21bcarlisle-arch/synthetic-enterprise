import pytest
from datetime import date
from company.crm.property_model import Property, PropertyType, TenureType, EPCRating
from company.crm.household_profile import HouseholdBehaviourProfile, HouseholdType, HeatingSystem
from company.crm.energy_profile import CustomerEnergyProfile


@pytest.fixture
def mid_range_profile():
    prop = Property(
        uprn="U001",
        property_type=PropertyType.SEMI_DETACHED,
        tenure=TenureType.OWNER_OCCUPIED,
        epc_rating=EPCRating.D,
        floor_area_m2=90.0,
        bedrooms=3,
        occupants=3,
    )
    beh = HouseholdBehaviourProfile(
        HouseholdType.FAMILY_WITH_CHILDREN, HeatingSystem.GAS_BOILER, 3
    )
    return CustomerEnergyProfile("C001", date(2022, 1, 1), prop, beh)


def test_estimated_elec_kwh_positive(mid_range_profile):
    assert mid_range_profile.estimated_annual_elec_kwh > 0


def test_estimated_gas_kwh_positive(mid_range_profile):
    assert mid_range_profile.estimated_annual_gas_kwh > 0


def test_eco4_eligible_epc_d(mid_range_profile):
    assert mid_range_profile.eco4_eligible is True


def test_tou_candidate_family(mid_range_profile):
    assert mid_range_profile.tou_candidate is True


def test_heat_pump_candidate_gas_boiler_epc_d(mid_range_profile):
    assert mid_range_profile.heat_pump_candidate is True


def test_heat_pump_not_candidate_if_epc_f():
    prop = Property(
        uprn="U002",
        property_type=PropertyType.TERRACED,
        tenure=TenureType.PRIVATE_RENTED,
        epc_rating=EPCRating.F,
        floor_area_m2=70.0, bedrooms=2, occupants=3,
    )
    beh = HouseholdBehaviourProfile(HouseholdType.RETIRED_COUPLE, HeatingSystem.GAS_BOILER, 2)
    ep = CustomerEnergyProfile("C002", date(2022, 1, 1), prop, beh)
    assert ep.heat_pump_candidate is False


def test_decarbonisation_score_higher_for_epc_g_than_a():
    prop_a = Property("U1", PropertyType.FLAT, TenureType.OWNER_OCCUPIED, EPCRating.A, 55.0, 1, 1, has_solar_pv=True)
    prop_g = Property("U2", PropertyType.TERRACED, TenureType.SOCIAL_RENTED, EPCRating.G, 75.0, 2, 3)
    beh = HouseholdBehaviourProfile(HouseholdType.SINGLE_OCCUPANT, HeatingSystem.GAS_BOILER, 1)
    ep_a = CustomerEnergyProfile("C1", date(2022, 1, 1), prop_a, beh)
    ep_g = CustomerEnergyProfile("C2", date(2022, 1, 1), prop_g, beh)
    assert ep_g.decarbonisation_priority_score > ep_a.decarbonisation_priority_score


def test_fuel_poor_flag_epc_f_private_rented():
    prop = Property(
        uprn="U003",
        property_type=PropertyType.TERRACED,
        tenure=TenureType.PRIVATE_RENTED,
        epc_rating=EPCRating.F,
        floor_area_m2=70.0, bedrooms=2, occupants=3,
    )
    beh = HouseholdBehaviourProfile(HouseholdType.FAMILY_WITH_CHILDREN, HeatingSystem.STORAGE_HEATER, 3)
    ep = CustomerEnergyProfile("C003", date(2022, 1, 1), prop, beh)
    assert ep.is_fuel_poor is True


def test_summary_contains_expected_keys(mid_range_profile):
    summary = mid_range_profile.summary()
    required_keys = ["customer_id", "epc_rating", "tenure", "household_type",
                     "estimated_annual_elec_kwh", "is_fuel_poor",
                     "tou_candidate", "decarbonisation_priority_score"]
    for k in required_keys:
        assert k in summary


def test_profile_is_frozen(mid_range_profile):
    with pytest.raises(Exception):
        mid_range_profile.customer_id = "CHANGED"
