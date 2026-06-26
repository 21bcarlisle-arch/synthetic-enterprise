"""Phase 114: MPAN/MPRN meter point registry tests."""

from company.billing.meter_points import (
    MeterPoint, MeterPointRegistry, validate_mpan, validate_mprn,
    infer_profile_class, PROFILE_CLASS_LABELS,
)


def test_validate_mpan_13_digits():
    assert validate_mpan("1012345678901") is True


def test_validate_mpan_wrong_length():
    assert validate_mpan("10123456789") is False


def test_validate_mprn_10_digits():
    assert validate_mprn("1234567890") is True


def test_validate_mprn_6_digits_ok():
    assert validate_mprn("123456") is True


def test_infer_profile_class_resi():
    assert infer_profile_class("resi") == 1


def test_infer_profile_class_resi_e7():
    assert infer_profile_class("resi", "economy 7") == 2


def test_infer_profile_class_sme():
    assert infer_profile_class("sme") == 3


def test_infer_profile_class_ic():
    assert infer_profile_class("ic") == 5


def test_register_and_retrieve():
    r = MeterPointRegistry()
    mp = MeterPoint("C1", "electricity", mpan="1012345678901", profile_class=1)
    r.register(mp)
    assert r.electricity("C1") is mp


def test_register_gas():
    r = MeterPointRegistry()
    mp = MeterPoint("C1", "gas", mprn="1234567890")
    r.register(mp)
    assert r.gas("C1").mprn == "1234567890"


def test_replace_existing_same_commodity():
    r = MeterPointRegistry()
    r.register(MeterPoint("C1", "electricity", mpan="1012345678901"))
    r.register(MeterPoint("C1", "electricity", mpan="9999999999999"))
    assert r.electricity("C1").mpan == "9999999999999"


def test_all_for_customer_both_commodities():
    r = MeterPointRegistry()
    r.register(MeterPoint("C1", "electricity", mpan="1012345678901"))
    r.register(MeterPoint("C1", "gas", mprn="1234567890"))
    assert len(r.all_for_customer("C1")) == 2


def test_unregistered_includes_unregistered():
    r = MeterPointRegistry()
    r.register(MeterPoint("C1", "electricity", mpan="1012345678901", registered=False))
    r.register(MeterPoint("C2", "electricity", mpan="9999999999999", registered=True))
    unregd = r.unregistered()
    assert any(p.customer_id == "C1" for p in unregd)
    assert not any(p.customer_id == "C2" for p in unregd)


def test_summary_totals():
    r = MeterPointRegistry()
    r.register(MeterPoint("C1", "electricity", mpan="1012345678901", registered=True))
    r.register(MeterPoint("C1", "gas", mprn="1234567890", registered=False))
    s = r.summary()
    assert s["total"] == 2
    assert s["electricity"] == 1
    assert s["gas"] == 1
    assert s["registered"] == 1
    assert s["unregistered"] == 1


def test_profile_class_label():
    mp = MeterPoint("C1", "electricity", profile_class=1)
    assert "Domestic" in mp.profile_class_label


def test_reference_property_electricity():
    mp = MeterPoint("C1", "electricity", mpan="1012345678901")
    assert mp.reference == "1012345678901"


def test_reference_property_gas():
    mp = MeterPoint("C1", "gas", mprn="9876543210")
    assert mp.reference == "9876543210"
