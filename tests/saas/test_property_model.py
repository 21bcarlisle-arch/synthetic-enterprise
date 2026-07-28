from saas.customers import CUSTOMERS
from saas.property_model import build_properties


def test_build_properties_covers_all_resi_electricity_customers():
    properties = build_properties(CUSTOMERS)
    # C7-C9 are Phase 6a HH (smart meter) resi electricity customers.
    assert set(properties) == {"C1", "C2", "C3", "C4", "C7", "C8", "C9"}


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


def test_all_properties_have_customer_id_key():
    properties = build_properties(CUSTOMERS)
    for cid, prop in properties.items():
        assert prop["customer_id"] == cid


def test_epc_c9_is_a_class():
    properties = build_properties(CUSTOMERS)
    assert properties["C9"]["epc_rating"] in list("ABCDEFG")


def test_build_properties_empty_input_returns_empty():
    properties = build_properties([])
    assert properties == {}


# --- SYN-shape property derivation (generator_draw_wiring remaining build #1) ---
# R15 BOTH WAYS: the derivation must FIRE on a SYN dict (no `home_type`) AND the
# static roster must stay byte-identical (the derivation branch is load-bearing,
# not decorative).

def _syn_customer(band, cid="SYN-0001"):
    """A saas-shaped SYN acquisition dict (as `to_customer_dict()` renders it):
    carries `consumption_band`, NOT the static `home_type`/`epc_rating`/`bedrooms`."""
    return {
        "customer_id": cid,
        "acquisition_date": "2023-05-01",
        "acquisition_type": "synthetic_draw",
        "segment": "resi",
        "commodity": "electricity",
        "payment_method": "direct_debit",
        "consumption_band": band,
        "eac_kwh": 2500.0,
        "location": {"lat": None, "lon": None, "region": "London"},
        "tariff_type": None,
        "data_regime": "synthetic",
    }


def test_syn_dict_gets_a_property_record_without_keyerror():
    # DIRECTION 1 (wiring present): a SYN dict lacking home_type/epc/bedrooms must
    # still yield a record. A mutant that reverts to `c["home_type"]`/`c["epc_rating"]`
    # /`c["bedrooms"]` raises KeyError here — proving the derivation branch is
    # load-bearing.
    properties = build_properties([_syn_customer("MEDIUM")])
    assert "SYN-0001" in properties
    rec = properties["SYN-0001"]
    assert rec["property_type"] == "semi"      # MEDIUM band
    assert rec["bedrooms"] == 3                 # MEDIUM band
    assert rec["epc_rating"] == "D"            # modal-band fallback
    # shared fields still resolve via the existing `.get()` defaults
    assert rec["occupancy_pattern"] == "single"
    assert rec["assets"] == {"ev": False, "solar": False, "smart_meter": False}
    assert rec["heating_system"] == "electric_storage"


def test_syn_bedrooms_and_type_track_consumption_band():
    props = build_properties([
        _syn_customer("LOW", "SYN-L"),
        _syn_customer("MEDIUM", "SYN-M"),
        _syn_customer("HIGH", "SYN-H"),
    ])
    assert (props["SYN-L"]["bedrooms"], props["SYN-L"]["property_type"]) == (2, "flat")
    assert (props["SYN-M"]["bedrooms"], props["SYN-M"]["property_type"]) == (3, "semi")
    assert (props["SYN-H"]["bedrooms"], props["SYN-H"]["property_type"]) == (4, "detached")


def test_syn_dict_missing_band_falls_to_honest_defaults():
    c = _syn_customer("MEDIUM", "SYN-NB")
    del c["consumption_band"]
    rec = build_properties([c])["SYN-NB"]
    assert rec["property_type"] == "semi"
    assert rec["bedrooms"] == 3
    assert rec["epc_rating"] == "D"


def test_static_roster_byte_identical_after_syn_branch():
    # DIRECTION 2 (mutation guard): adding the SYN branch must NOT perturb the static
    # path. A mutant that routed static dicts through the SYN derivation would flip
    # these authored values (C4 detached/E/4-bed derives to whatever its band implies).
    props = build_properties(CUSTOMERS)
    assert props["C1"]["property_type"] == "flat" and props["C1"]["bedrooms"] == 2
    assert props["C4"]["property_type"] == "detached"
    assert props["C3"]["epc_rating"] == "E"    # authored, NOT the modal "D" default
    assert props["C4"]["epc_rating"] == "E"
