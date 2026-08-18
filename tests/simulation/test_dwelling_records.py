"""The WORLD's dwelling record builder — `simulation.dwelling_records`.

These tests were `tests/saas/test_property_model.py`'s until the 2026-08-18 B12
split (KNIFE3 step 35) moved `build_properties` world-side. They test the same
behaviour on the same roster, with ONE deliberate change of subject: the world no
longer falls back to the supplier's approximation for a drawn customer with no
world dwelling, so the cases that used to assert the fallback's VALUES now assert
that it RAISES. The supplier's derivation itself is unchanged and is still tested,
on the supplier's side, in `tests/saas/test_property_model.py`.
"""
import pytest

from saas.customers import CUSTOMERS
from simulation.dwelling_records import DwellingNotDrawn, build_properties


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
    from simulation.dwelling_records import ASSET_PROFILE_BY_CUSTOMER

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


# --- The drawn cohort: the world's dwelling, or nothing --------------------
# B12/KNIFE3 step 35. Before the split this builder answered a drawn customer with
# `saas.property_model._derive_syn_property_fields` — the SUPPLIER's guess — stamped
# `saas_approximation`. Step 31 chose that to be "deliberately silent-but-labelled
# rather than" fatal, which was right while ONE function served both sides. The
# split separates the two behaviours, and the world's half takes the other branch:
# it knows every home it drew, so a drawn customer it has no dwelling for is an
# upstream inconsistency, not an occasion to guess.

def _syn_customer(band, cid="SYN-0001"):
    """A SYN acquisition dict (as `to_customer_dict()` renders it): carries
    `consumption_band`, NOT the static `home_type`/`epc_rating`/`bedrooms`."""
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


def test_a_drawn_customer_with_the_worlds_dwelling_gets_it_verbatim():
    # DIRECTION 1 (the wiring is live): the handed-in dwelling is used as-is, and it
    # is NOT the supplier's band derivation — a MEDIUM band derives to semi/3-bed/D,
    # and this world dwelling is deliberately none of those.
    dwelling = {"property_type": "detached", "epc_rating": "B", "bedrooms": 5}
    rec = build_properties([_syn_customer("MEDIUM")], dwellings={"SYN-0001": dwelling})["SYN-0001"]
    assert (rec["property_type"], rec["epc_rating"], rec["bedrooms"]) == ("detached", "B", 5)
    assert rec["dwelling_basis"] == "world_draw"
    # shared fields still resolve via the existing `.get()` defaults
    assert rec["occupancy_pattern"] == "single"
    assert rec["assets"] == {"ev": False, "solar": False, "smart_meter": False}
    assert rec["heating_system"] == "electric_storage"


def test_a_drawn_customer_with_no_world_dwelling_raises_rather_than_guessing():
    # DIRECTION 2 (the fallback is gone): this is the case that used to return a
    # record built from the supplier's `consumption_band` guess. A mutant that
    # restored that fallback passes the test above and fails here.
    with pytest.raises(DwellingNotDrawn):
        build_properties([_syn_customer("MEDIUM")])
    with pytest.raises(DwellingNotDrawn):
        build_properties([_syn_customer("MEDIUM")], dwellings={"SOMEONE-ELSE": {}})


def test_the_raise_is_specific_to_the_drawn_customer_not_the_whole_call():
    """A roster mixing authored and drawn customers must not be sunk by an unrelated
    authored record — and equally, one undrawn customer must not be quietly dropped
    from the result while the others build. It raises, naming the customer."""
    book = list(CUSTOMERS) + [_syn_customer("HIGH", "SYN-ORPHAN")]
    with pytest.raises(DwellingNotDrawn, match="SYN-ORPHAN"):
        build_properties(book)


def test_static_roster_byte_identical_after_the_split():
    # The authored path must be untouched by everything above. A mutant that routed
    # static dicts through the drawn branch would raise here rather than flip values.
    props = build_properties(CUSTOMERS)
    assert props["C1"]["property_type"] == "flat" and props["C1"]["bedrooms"] == 2
    assert props["C4"]["property_type"] == "detached"
    assert props["C3"]["epc_rating"] == "E"    # authored, NOT the modal "D" default
    assert props["C4"]["epc_rating"] == "E"
    assert all(r["dwelling_basis"] == "authored_roster" for r in props.values())
