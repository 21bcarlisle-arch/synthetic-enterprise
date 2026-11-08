"""Phase CW: Licence Application Register tests."""
import pytest
from datetime import date
from company.regulatory.licence_application_register import (
    LicenceApplicationRegister, LicenceType, LicenceTier,
    ApplicationStatus, VariationReason
)

_D = date(2016, 1, 1)


def _reg_with_licence():
    r = LicenceApplicationRegister()
    lic = r.register_licence("EL-001", LicenceType.ELECTRICITY_DOMESTIC, LicenceTier.TIER_1, _D)
    return r, lic


# 1. register_licence creates active record
def test_register_licence():
    r, lic = _reg_with_licence()
    assert lic.is_active
    assert lic.licence_type == LicenceType.ELECTRICITY_DOMESTIC


# 2. active_licences includes new licence
def test_active_licences():
    r, lic = _reg_with_licence()
    assert lic in r.active_licences


# 3. licence with special conditions detected
def test_special_conditions():
    r = LicenceApplicationRegister()
    lic = r.register_licence("GL-002", LicenceType.GAS_DOMESTIC, LicenceTier.TIER_1, _D, special_conditions=("SpC1",))
    assert lic.has_special_conditions
    assert lic in r.licences_with_special_conditions


# 4. no special conditions by default
def test_no_special_conditions():
    r, lic = _reg_with_licence()
    assert not lic.has_special_conditions
    assert lic not in r.licences_with_special_conditions


# 5. submit_application creates PENDING
def test_submit_application():
    r, lic = _reg_with_licence()
    app = r.submit_application("APP-001", LicenceType.ELECTRICITY_NON_DOMESTIC, date(2020, 1, 1), VariationReason.NEW_CATEGORY)
    assert app.status == ApplicationStatus.PENDING
    assert app.is_open


# 6. decide APPROVED
def test_decide_approved():
    r, lic = _reg_with_licence()
    r.submit_application("APP-001", LicenceType.ELECTRICITY_NON_DOMESTIC, date(2020, 1, 1), VariationReason.NEW_CATEGORY)
    result = r.decide("APP-001", approved=True, decision_date=date(2020, 3, 1))
    assert result.is_approved
    assert not result.is_open


# 7. decide REJECTED
def test_decide_rejected():
    r, lic = _reg_with_licence()
    r.submit_application("APP-001", LicenceType.GAS_NON_DOMESTIC, date(2020, 1, 1), VariationReason.FINANCIAL_CONDITION)
    result = r.decide("APP-001", approved=False, decision_date=date(2020, 4, 1))
    assert result.status == ApplicationStatus.REJECTED


# 8. open_applications includes pending but not decided
def test_open_applications():
    r, lic = _reg_with_licence()
    r.submit_application("APP-001", LicenceType.ELECTRICITY_NON_DOMESTIC, date(2020, 1, 1), VariationReason.NEW_CATEGORY)
    r.submit_application("APP-002", LicenceType.GAS_DOMESTIC, date(2020, 1, 1), VariationReason.CHANGE_OF_CONTROL)
    r.decide("APP-001", True, date(2020, 3, 1))
    assert len(r.open_applications) == 1


# 9. approved_applications filtered correctly
def test_approved_applications():
    r, lic = _reg_with_licence()
    r.submit_application("APP-001", LicenceType.ELECTRICITY_NON_DOMESTIC, date(2020, 1, 1), VariationReason.NEW_CATEGORY)
    r.decide("APP-001", True, date(2020, 3, 1))
    assert len(r.approved_applications) == 1


# 10. multiple licence types tracked
def test_multiple_licences():
    r = LicenceApplicationRegister()
    r.register_licence("EL-001", LicenceType.ELECTRICITY_DOMESTIC, LicenceTier.TIER_1, _D)
    r.register_licence("GL-001", LicenceType.GAS_DOMESTIC, LicenceTier.TIER_1, _D)
    r.register_licence("EN-001", LicenceType.ELECTRICITY_NON_DOMESTIC, LicenceTier.TIER_1, _D)
    assert len(r.active_licences) == 3


# 11. CHANGE_OF_CONTROL reason available
def test_change_of_control_reason():
    r, lic = _reg_with_licence()
    app = r.submit_application("APP-001", LicenceType.ELECTRICITY_DOMESTIC, date(2021, 1, 1), VariationReason.CHANGE_OF_CONTROL)
    assert app.reason == VariationReason.CHANGE_OF_CONTROL


# 12. licence_summary contains Ofgem
def test_summary():
    r, lic = _reg_with_licence()
    summary = r.licence_summary()
    assert "Ofgem" in summary
    assert "Active" in summary


# --- Phase MC depth tests ---

def test_licence_id_stored():
    r = LicenceApplicationRegister()
    lic = r.register_licence('EL-MC', LicenceType.GAS_DOMESTIC, LicenceTier.TIER_1, _D)
    assert lic.licence_id == 'EL-MC'


def test_licence_type_stored():
    r = LicenceApplicationRegister()
    lic = r.register_licence('EL-MC', LicenceType.GAS_NON_DOMESTIC, LicenceTier.TIER_1, _D)
    assert lic.licence_type == LicenceType.GAS_NON_DOMESTIC


def test_tier_stored():
    r = LicenceApplicationRegister()
    lic = r.register_licence('EL-MC', LicenceType.ELECTRICITY_DOMESTIC, LicenceTier.TIER_2, _D)
    assert lic.tier == LicenceTier.TIER_2


def test_grant_date_stored():
    r = LicenceApplicationRegister()
    d = date(2018, 3, 15)
    lic = r.register_licence('EL-MC', LicenceType.ELECTRICITY_DOMESTIC, LicenceTier.TIER_1, d)
    assert lic.grant_date == d


def test_is_active_true_default():
    r = LicenceApplicationRegister()
    lic = r.register_licence('EL-MC', LicenceType.ELECTRICITY_DOMESTIC, LicenceTier.TIER_1, _D)
    assert lic.is_active is True


def test_special_conditions_empty_default():
    r = LicenceApplicationRegister()
    lic = r.register_licence('EL-MC', LicenceType.ELECTRICITY_DOMESTIC, LicenceTier.TIER_1, _D)
    assert lic.special_conditions == ()


def test_has_special_conditions_false_empty():
    r = LicenceApplicationRegister()
    lic = r.register_licence('EL-MC', LicenceType.ELECTRICITY_DOMESTIC, LicenceTier.TIER_1, _D)
    assert lic.has_special_conditions is False


def test_register_licence_returns_licence_record():
    from company.regulatory.licence_application_register import LicenceRecord
    r = LicenceApplicationRegister()
    result = r.register_licence('EL-MC', LicenceType.ELECTRICITY_DOMESTIC, LicenceTier.TIER_1, _D)
    assert isinstance(result, LicenceRecord)


def test_licence_type_has_4_members():
    assert len(list(LicenceType)) == 4


def test_application_status_has_5_members():
    assert len(list(ApplicationStatus)) == 5
