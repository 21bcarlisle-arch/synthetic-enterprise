from saas.customers import CUSTOMERS
from saas.property_model import build_properties


def test_build_properties_covers_all_resi_electricity_customers():
    properties = build_properties(CUSTOMERS)
    assert set(properties) == {"C1", "C2", "C3", "C4"}


def test_excludes_sme_and_gas_records():
    properties = build_properties(CUSTOMERS)
    assert "C5" not in properties
    assert "C6" not in properties
    assert "C1g" not in properties


def test_property_type_mapped_from_home_type():
    properties = build_properties(CUSTOMERS)
    assert properties["C1"]["property_type"] == "flat"  # urban_flat
    assert properties["C2"]["property_type"] == "semi"  # suburban_semi
    assert properties["C3"]["property_type"] == "flat"  # tenement_flat
    assert properties["C4"]["property_type"] == "detached"  # rural_detached


def test_unknown_home_type_maps_to_default():
    customers = [
        {
            "customer_id": "CX",
            "segment": "resi",
            "commodity": "electricity",
            "home_type": "houseboat",
            "epc_rating": "D",
            "bedrooms": 1,
        }
    ]
    properties = build_properties(customers)
    assert properties["CX"]["property_type"] == "other"


def test_dual_fuel_customers_get_gas_boiler():
    properties = build_properties(CUSTOMERS)
    for cid in ("C1", "C2", "C3", "C4"):
        assert properties[cid]["heating_system"] == "gas_boiler"


def test_electric_only_customer_gets_default_heating():
    customers = [
        {
            "customer_id": "CX",
            "segment": "resi",
            "commodity": "electricity",
            "home_type": "urban_flat",
            "epc_rating": "D",
            "bedrooms": 1,
        }
    ]
    properties = build_properties(customers)
    assert properties["CX"]["heating_system"] == "electric_storage"


def test_epc_rating_and_bedrooms_passed_through():
    properties = build_properties(CUSTOMERS)
    assert properties["C2"]["epc_rating"] == "D"
    assert properties["C2"]["bedrooms"] == 3


def test_occupancy_pattern_and_assets_present_for_known_customers():
    properties = build_properties(CUSTOMERS)
    assert properties["C1"]["occupancy_pattern"] == "single"
    assert properties["C4"]["occupancy_pattern"] == "family"
    assert properties["C4"]["assets"] == {"ev": True, "solar": True, "smart_meter": True}


def test_unknown_customer_gets_default_occupancy_and_assets():
    customers = [
        {
            "customer_id": "CX",
            "segment": "resi",
            "commodity": "electricity",
            "home_type": "urban_flat",
            "epc_rating": "D",
            "bedrooms": 1,
        }
    ]
    properties = build_properties(customers)
    assert properties["CX"]["occupancy_pattern"] == "single"
    assert properties["CX"]["assets"] == {"ev": False, "solar": False, "smart_meter": False}


def test_assets_dict_is_a_copy_not_shared_with_constant():
    from saas.property_model import ASSET_PROFILE_BY_CUSTOMER

    properties = build_properties(CUSTOMERS)
    properties["C1"]["assets"]["ev"] = True
    assert ASSET_PROFILE_BY_CUSTOMER["C1"]["ev"] is False
