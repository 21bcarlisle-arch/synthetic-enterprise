import pytest
from company.crm.home_registry import HomeRegistry
from company.crm.property_model import EPCRating, Property, PropertyType, TenureType


def _make_prop(epc=EPCRating.D, tenure=TenureType.OWNER_OCCUPIED, has_gas=True,
               property_type=PropertyType.SEMI_DETACHED, uprn="UPRN001"):
    return Property(
        uprn=uprn,
        property_type=property_type,
        tenure=tenure,
        epc_rating=epc,
        floor_area_m2=90.0,
        bedrooms=3,
        occupants=2,
        has_gas=has_gas,
    )


def test_register_and_get():
    reg = HomeRegistry()
    prop = _make_prop()
    reg.register("C1", prop)
    assert reg.get_profile("C1") is prop


def test_get_unknown_raises():
    reg = HomeRegistry()
    with pytest.raises(KeyError, match="C99"):
        reg.get_profile("C99")


def test_get_profile_or_none_missing():
    reg = HomeRegistry()
    assert reg.get_profile_or_none("C99") is None


def test_register_bad_type_raises():
    reg = HomeRegistry()
    with pytest.raises(TypeError):
        reg.register("C1", "not a property")


def test_upgrade_epc():
    reg = HomeRegistry()
    reg.register("C1", _make_prop(epc=EPCRating.E))
    upgraded = reg.upgrade_epc("C1", EPCRating.C)
    assert reg.get_profile("C1").epc_rating == EPCRating.C
    assert upgraded.epc_rating == EPCRating.C


def test_profiles_by_epc():
    reg = HomeRegistry()
    reg.register("C1", _make_prop(epc=EPCRating.D))
    reg.register("C2", _make_prop(epc=EPCRating.E, uprn="U2"))
    reg.register("C3", _make_prop(epc=EPCRating.D, uprn="U3"))
    assert sorted(reg.profiles_by_epc(EPCRating.D)) == ["C1", "C3"]
    assert reg.profiles_by_epc(EPCRating.E) == ["C2"]
    assert reg.profiles_by_epc(EPCRating.A) == []


def test_fuel_distribution():
    reg = HomeRegistry()
    reg.register("C1", _make_prop(has_gas=True))
    reg.register("C2", _make_prop(has_gas=False, uprn="U2"))
    reg.register("C3", _make_prop(has_gas=True, uprn="U3"))
    dist = reg.fuel_distribution()
    assert dist["gas"] == 2
    assert dist["electric"] == 1


def test_epc_distribution():
    reg = HomeRegistry()
    reg.register("C1", _make_prop(epc=EPCRating.D))
    reg.register("C2", _make_prop(epc=EPCRating.D, uprn="U2"))
    reg.register("C3", _make_prop(epc=EPCRating.F, uprn="U3"))
    dist = reg.epc_distribution()
    assert dist["D"] == 2
    assert dist["F"] == 1
    assert "A" not in dist


def test_eco4_eligible_count():
    reg = HomeRegistry()
    reg.register("C1", _make_prop(epc=EPCRating.D))
    reg.register("C2", _make_prop(epc=EPCRating.C, uprn="U2"))
    reg.register("C3", _make_prop(epc=EPCRating.F, uprn="U3"))
    assert sorted(reg.eco4_eligible_accounts()) == ["C1", "C3"]


def test_fuel_poor_count():
    reg = HomeRegistry()
    reg.register("C1", _make_prop(epc=EPCRating.F, tenure=TenureType.PRIVATE_RENTED))
    reg.register("C2", _make_prop(epc=EPCRating.F, tenure=TenureType.OWNER_OCCUPIED, uprn="U2"))
    reg.register("C3", _make_prop(epc=EPCRating.G, tenure=TenureType.SOCIAL_RENTED, uprn="U3"))
    assert sorted(reg.fuel_poor_accounts()) == ["C1", "C3"]


def test_registry_summary_keys():
    reg = HomeRegistry()
    reg.register("C1", _make_prop())
    s = reg.registry_summary()
    for key in ("total_accounts", "epc_distribution", "fuel_distribution",
                "tenure_distribution", "eco4_eligible", "fuel_poor",
                "psr_priority", "total_estimated_elec_kwh", "total_estimated_gas_kwh"):
        assert key in s, "missing key: {}".format(key)
    assert s["total_accounts"] == 1


def test_registry_summary_empty():
    reg = HomeRegistry()
    s = reg.registry_summary()
    assert s["total_accounts"] == 0
    assert s["eco4_eligible"] == 0
    assert s["total_estimated_elec_kwh"] == 0



# --- Phase LS depth tests ---
from company.crm.property_model import EPCRating, Property, PropertyType, TenureType

def _prop(**kw):
    defaults = dict(uprn='UPRN001', property_type=PropertyType.SEMI_DETACHED,
                    tenure=TenureType.OWNER_OCCUPIED, epc_rating=EPCRating.D,
                    floor_area_m2=90.0, bedrooms=3, occupants=2)
    defaults.update(kw)
    return Property(**defaults)


def test_uprn_stored():
    p = _prop(uprn='UPRN_LS')
    assert p.uprn == 'UPRN_LS'


def test_property_type_stored():
    p = _prop(property_type=PropertyType.DETACHED)
    assert p.property_type == PropertyType.DETACHED


def test_tenure_stored():
    p = _prop(tenure=TenureType.PRIVATE_RENTED)
    assert p.tenure == TenureType.PRIVATE_RENTED


def test_epc_rating_stored():
    p = _prop(epc_rating=EPCRating.B)
    assert p.epc_rating == EPCRating.B


def test_has_gas_default_true():
    p = _prop()
    assert p.has_gas is True


def test_has_solar_pv_default_false():
    p = _prop()
    assert p.has_solar_pv is False


def test_eco4_eligible_d_rating():
    p = _prop(epc_rating=EPCRating.D)
    assert p.eco4_eligible is True


def test_eco4_not_eligible_a_rating():
    p = _prop(epc_rating=EPCRating.A)
    assert p.eco4_eligible is False


def test_psr_priority_f_rating():
    p = _prop(epc_rating=EPCRating.F)
    assert p.psr_priority_property is True


def test_get_profile_or_none_found():
    reg = HomeRegistry()
    p = _prop()
    reg.register('C1', p)
    assert reg.get_profile_or_none('C1') is p


# --- C2 discovery-through-interfaces: HomeRegistry wired to observable events,
# never to sim/saas ground truth ---

import datetime as dt


def test_register_from_signup_opens_belief_not_ground_truth():
    reg = HomeRegistry()
    prop = reg.register_from_signup(
        "C1", "UPRN500", dt.date(2024, 1, 1),
        property_type=PropertyType.TERRACED, bedrooms=2,
    )
    assert reg.get_profile("C1") is prop
    assert prop.property_type == PropertyType.TERRACED
    assert prop.source_for("property_type") == "self_disclosed_signup"
    # epc_rating was never disclosed at signup -- must remain a low-confidence default
    assert prop.confidence_for("epc_rating") < 0.5


def test_record_epc_lookup_updates_registered_profile_with_provenance():
    reg = HomeRegistry()
    reg.register_from_signup("C1", "UPRN501", dt.date(2024, 1, 1))
    updated = reg.record_epc_lookup("C1", EPCRating.B, dt.date(2024, 2, 1))
    assert reg.get_profile("C1").epc_rating == EPCRating.B
    assert updated.source_for("epc_rating") == "epc_certificate_lookup"
    assert updated.confidence_for("epc_rating") > 0.9


def test_record_tariff_registration_updates_solar_and_ev():
    reg = HomeRegistry()
    reg.register_from_signup("C1", "UPRN502", dt.date(2024, 1, 1))
    updated = reg.record_tariff_registration(
        "C1", dt.date(2024, 3, 1), has_solar_pv=True, electric_vehicle=True,
    )
    assert reg.get_profile("C1").has_solar_pv is True
    assert updated.source_for("has_solar_pv") == "tariff_registration"


def test_record_engineer_visit_corrects_floor_area():
    reg = HomeRegistry()
    reg.register_from_signup("C1", "UPRN503", dt.date(2024, 1, 1))
    updated = reg.record_engineer_visit("C1", dt.date(2024, 5, 1), floor_area_m2=120.0)
    assert reg.get_profile("C1").floor_area_m2 == pytest.approx(120.0)
    assert updated.source_for("floor_area_m2") == "engineer_visit"


def test_upgrade_epc_still_works_and_now_stamps_provenance():
    reg = HomeRegistry()
    reg.register("C1", _prop(epc_rating=EPCRating.E))
    upgraded = reg.upgrade_epc("C1", EPCRating.C, as_of=dt.date(2024, 6, 1))
    assert reg.get_profile("C1").epc_rating == EPCRating.C
    assert upgraded.epc_rating == EPCRating.C
    assert upgraded.source_for("epc_rating") == "epc_certificate_lookup"


def test_belief_confidence_reports_source_and_confidence_per_attribute():
    reg = HomeRegistry()
    reg.register_from_signup(
        "C1", "UPRN504", dt.date(2024, 1, 1),
        property_type=PropertyType.FLAT, bedrooms=1,
    )
    reg.record_epc_lookup("C1", EPCRating.A, dt.date(2024, 1, 10))
    summary = reg.belief_confidence("C1")
    assert "overall_confidence" in summary
    assert summary["attributes"]["property_type"]["source"] == "self_disclosed_signup"
    assert summary["attributes"]["epc_rating"]["source"] == "epc_certificate_lookup"
    assert summary["attributes"]["epc_rating"]["value"] == "A"
    assert summary["attributes"]["occupants"]["source"] == "unconfirmed_default"


def test_belief_may_differ_from_a_hypothetical_ground_truth_home():
    """The discovered belief for an under-disclosed signup need not match
    any particular real home -- it is an assumption until proven otherwise,
    and record_epc_lookup only ever updates what was actually observed."""
    reg = HomeRegistry()
    prop = reg.register_from_signup("C1", "UPRN505", dt.date(2024, 1, 1))
    # Undisclosed EPC defaults to the population-modal band, which is very
    # likely wrong for any specific real home -- that is the honest, expected
    # behaviour of a belief built from partial observation.
    assert prop.epc_rating is not None
    assert prop.confidence_for("epc_rating") == pytest.approx(0.1)
