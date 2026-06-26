import pytest
from company.crm.household_profile import (
    HouseholdType, HeatingSystem, HouseholdBehaviourProfile,
)


@pytest.fixture
def retired_couple():
    return HouseholdBehaviourProfile(
        household_type=HouseholdType.RETIRED_COUPLE,
        heating_system=HeatingSystem.GAS_BOILER,
        occupants=2,
    )


@pytest.fixture
def wfh_single():
    return HouseholdBehaviourProfile(
        household_type=HouseholdType.WORK_FROM_HOME,
        heating_system=HeatingSystem.HEAT_PUMP,
        occupants=1,
        wfh_days_per_week=5,
    )


def test_family_higher_peak_than_single():
    fam = HouseholdBehaviourProfile(
        HouseholdType.FAMILY_WITH_CHILDREN, HeatingSystem.GAS_BOILER, 4
    )
    single = HouseholdBehaviourProfile(
        HouseholdType.SINGLE_OCCUPANT, HeatingSystem.GAS_BOILER, 1
    )
    assert fam.peak_load_factor > single.peak_load_factor


def test_wfh_boosts_peak_load(wfh_single):
    base = HouseholdBehaviourProfile(
        HouseholdType.WORK_FROM_HOME, HeatingSystem.HEAT_PUMP, 1, wfh_days_per_week=0
    )
    assert wfh_single.peak_load_factor > base.peak_load_factor


def test_retired_high_daytime_consumption(retired_couple):
    assert retired_couple.daytime_consumption_pct >= 0.65


def test_student_low_daytime_consumption():
    s = HouseholdBehaviourProfile(
        HouseholdType.STUDENT_HOUSEHOLD, HeatingSystem.STORAGE_HEATER, 3
    )
    assert s.daytime_consumption_pct < 0.50


def test_day_plus_evening_sums_to_one(retired_couple):
    total = retired_couple.daytime_consumption_pct + retired_couple.evening_consumption_pct
    assert total == pytest.approx(1.0)


def test_tou_price_sensitivity_retired_is_low(retired_couple):
    assert retired_couple.tou_price_sensitivity == "low"


def test_tou_price_sensitivity_wfh_is_high(wfh_single):
    assert wfh_single.tou_price_sensitivity == "high"


def test_smart_meter_benefit_higher_for_high_sensitivity(wfh_single, retired_couple):
    assert wfh_single.smart_meter_benefit_score > retired_couple.smart_meter_benefit_score


def test_heat_pump_not_eligible_if_already_has_heat_pump(wfh_single):
    assert wfh_single.heat_pump_eligible is False


def test_gas_boiler_household_is_heat_pump_eligible(retired_couple):
    assert retired_couple.heat_pump_eligible is True


def test_profile_is_frozen(retired_couple):
    with pytest.raises(Exception):
        retired_couple.occupants = 5
