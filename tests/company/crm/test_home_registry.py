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


# --- C2 discovery-through-interfaces: HomeRegistry wired to observable events,
# never to sim/saas ground truth ---


