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

