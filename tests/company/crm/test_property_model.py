import pytest
from company.crm.property_model import (
    PropertyType, TenureType, EPCRating, Property,
    UK_AVG_DOMESTIC_ELEC_KWH, UK_AVG_DOMESTIC_GAS_KWH,
)


@pytest.fixture
def average_semi():
    return Property(
        uprn="UPRN001",
        property_type=PropertyType.SEMI_DETACHED,
        tenure=TenureType.OWNER_OCCUPIED,
        epc_rating=EPCRating.D,
        floor_area_m2=90.0,
        bedrooms=3,
        occupants=3,
    )


def test_epc_d_consumption_multiplier(average_semi):
    assert average_semi.consumption_multiplier == pytest.approx(1.00)


def test_epc_a_uses_lower_multiplier():
    p = Property(
        uprn="A001",
        property_type=PropertyType.FLAT,
        tenure=TenureType.OWNER_OCCUPIED,
        epc_rating=EPCRating.A,
        floor_area_m2=55.0,
        bedrooms=1,
        occupants=1,
    )
    assert p.consumption_multiplier == pytest.approx(0.60)


def test_estimated_elec_kwh_average_semi(average_semi):
    kwh = average_semi.estimated_annual_elec_kwh
    assert kwh > 2000 and kwh < 6000


def test_ev_increases_elec_consumption():
    base = Property(
        uprn="B001", property_type=PropertyType.DETACHED,
        tenure=TenureType.OWNER_OCCUPIED, epc_rating=EPCRating.C,
        floor_area_m2=130.0, bedrooms=4, occupants=4,
    )
    ev = Property(
        uprn="B002", property_type=PropertyType.DETACHED,
        tenure=TenureType.OWNER_OCCUPIED, epc_rating=EPCRating.C,
        floor_area_m2=130.0, bedrooms=4, occupants=4, electric_vehicle=True,
    )
    assert ev.estimated_annual_elec_kwh > base.estimated_annual_elec_kwh + 2000


def test_solar_pv_reduces_elec_consumption():
    base = Property(
        uprn="C001", property_type=PropertyType.DETACHED,
        tenure=TenureType.OWNER_OCCUPIED, epc_rating=EPCRating.B,
        floor_area_m2=130.0, bedrooms=4, occupants=3,
    )
    solar = Property(
        uprn="C002", property_type=PropertyType.DETACHED,
        tenure=TenureType.OWNER_OCCUPIED, epc_rating=EPCRating.B,
        floor_area_m2=130.0, bedrooms=4, occupants=3, has_solar_pv=True,
    )
    assert solar.estimated_annual_elec_kwh < base.estimated_annual_elec_kwh


def test_no_gas_returns_zero_gas_kwh():
    p = Property(
        uprn="D001", property_type=PropertyType.FLAT,
        tenure=TenureType.PRIVATE_RENTED, epc_rating=EPCRating.D,
        floor_area_m2=50.0, bedrooms=1, occupants=2, has_gas=False,
    )
    assert p.estimated_annual_gas_kwh == pytest.approx(0.0)


def test_epc_g_higher_gas_than_epc_b():
    good = Property(
        uprn="E001", property_type=PropertyType.TERRACED,
        tenure=TenureType.OWNER_OCCUPIED, epc_rating=EPCRating.B,
        floor_area_m2=75.0, bedrooms=2, occupants=2,
    )
    poor = Property(
        uprn="E002", property_type=PropertyType.TERRACED,
        tenure=TenureType.OWNER_OCCUPIED, epc_rating=EPCRating.G,
        floor_area_m2=75.0, bedrooms=2, occupants=2,
    )
    assert poor.estimated_annual_gas_kwh > good.estimated_annual_gas_kwh


def test_fuel_poor_flag_epc_f_private_rented():
    p = Property(
        uprn="F001", property_type=PropertyType.TERRACED,
        tenure=TenureType.PRIVATE_RENTED, epc_rating=EPCRating.F,
        floor_area_m2=70.0, bedrooms=2, occupants=3,
    )
    assert p.is_fuel_poor is True


def test_fuel_poor_flag_false_for_owner_occupied_epc_f():
    p = Property(
        uprn="F002", property_type=PropertyType.DETACHED,
        tenure=TenureType.OWNER_OCCUPIED, epc_rating=EPCRating.F,
        floor_area_m2=100.0, bedrooms=3, occupants=2,
    )
    assert p.is_fuel_poor is False


def test_eco4_eligible_epc_d_through_g(average_semi):
    assert average_semi.eco4_eligible is True


def test_eco4_not_eligible_epc_b():
    p = Property(
        uprn="G001", property_type=PropertyType.FLAT,
        tenure=TenureType.OWNER_OCCUPIED, epc_rating=EPCRating.B,
        floor_area_m2=55.0, bedrooms=1, occupants=1,
    )
    assert p.eco4_eligible is False


def test_property_is_frozen(average_semi):
    with pytest.raises(Exception):
        average_semi.uprn = "CHANGED"


# --- Phase LU depth tests ---

def test_uprn_stored(average_semi):
    assert average_semi.uprn == 'UPRN001'


def test_bedrooms_stored(average_semi):
    assert average_semi.bedrooms == 3


def test_occupants_stored(average_semi):
    assert average_semi.occupants == 3


def test_floor_area_stored(average_semi):
    assert average_semi.floor_area_m2 == pytest.approx(90.0)


def test_electric_vehicle_default_false(average_semi):
    assert average_semi.electric_vehicle is False


def test_is_fuel_poor_false_owner_occupied(average_semi):
    assert average_semi.is_fuel_poor is False


def test_is_fuel_poor_true_f_private_rented():
    p = Property(
        uprn='X', property_type=PropertyType.TERRACED,
        tenure=TenureType.PRIVATE_RENTED, epc_rating=EPCRating.F,
        floor_area_m2=60.0, bedrooms=2, occupants=2,
    )
    assert p.is_fuel_poor is True


def test_no_gas_gives_zero_gas_kwh():
    p = Property(
        uprn='X', property_type=PropertyType.FLAT,
        tenure=TenureType.OWNER_OCCUPIED, epc_rating=EPCRating.C,
        floor_area_m2=50.0, bedrooms=1, occupants=1, has_gas=False,
    )
    assert p.estimated_annual_gas_kwh == pytest.approx(0.0)


def test_ev_increases_elec_kwh(average_semi):
    p_ev = Property(
        uprn='X', property_type=PropertyType.SEMI_DETACHED,
        tenure=TenureType.OWNER_OCCUPIED, epc_rating=EPCRating.D,
        floor_area_m2=90.0, bedrooms=3, occupants=3, electric_vehicle=True,
    )
    assert p_ev.estimated_annual_elec_kwh > average_semi.estimated_annual_elec_kwh


def test_uk_avg_domestic_elec_kwh():
    assert UK_AVG_DOMESTIC_ELEC_KWH == pytest.approx(3100.0)


def test_uk_avg_domestic_gas_kwh():
    assert UK_AVG_DOMESTIC_GAS_KWH == pytest.approx(12000.0)
