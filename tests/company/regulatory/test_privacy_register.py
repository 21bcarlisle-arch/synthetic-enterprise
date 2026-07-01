import datetime as dt
import pytest
from company.regulatory.privacy_register import (
    ConsentPurpose, DSRType, DSRStatus, ConsentRecord,
    DataSubjectRequest, PrivacyConsentRegister
)


def test_active_consent():
    r = ConsentRecord('C1', ConsentPurpose.MARKETING_EMAIL, True, dt.date(2022, 1, 1))
    assert r.is_active


def test_withdrawn_consent_inactive():
    r = ConsentRecord('C1', ConsentPurpose.MARKETING_EMAIL, True,
                       dt.date(2022, 1, 1), dt.date(2022, 6, 1))
    assert not r.is_active


def test_dsr_deadline_standard():
    d = DataSubjectRequest('DSR-0001', 'C1', DSRType.ACCESS, dt.date(2022, 1, 1))
    assert d.deadline() == dt.date(2022, 1, 31)


def test_dsr_deadline_extended():
    d = DataSubjectRequest('DSR-0001', 'C1', DSRType.ACCESS, dt.date(2022, 1, 1))
    d.extend()
    assert d.deadline() == dt.date(2022, 3, 2)


def test_dsr_overdue():
    d = DataSubjectRequest('DSR-0001', 'C1', DSRType.ERASURE, dt.date(2022, 1, 1))
    assert d.is_overdue(dt.date(2022, 2, 15))


def test_dsr_not_overdue_when_completed():
    d = DataSubjectRequest('DSR-0001', 'C1', DSRType.ACCESS, dt.date(2022, 1, 1))
    d.complete(dt.date(2022, 1, 20))
    assert not d.is_overdue(dt.date(2022, 3, 1))


def test_has_active_consent_true():
    reg = PrivacyConsentRegister()
    reg.record_consent('C1', ConsentPurpose.MARKETING_SMS, True, dt.date(2022, 1, 1))
    assert reg.has_active_consent('C1', ConsentPurpose.MARKETING_SMS)


def test_has_active_consent_false_after_denial():
    reg = PrivacyConsentRegister()
    reg.record_consent('C1', ConsentPurpose.ANALYTICS, False, dt.date(2022, 1, 1))
    assert not reg.has_active_consent('C1', ConsentPurpose.ANALYTICS)


def test_raise_dsr_and_overdue():
    reg = PrivacyConsentRegister()
    reg.raise_dsr('C1', DSRType.ACCESS, dt.date(2022, 1, 1))
    assert len(reg.overdue_requests(dt.date(2022, 3, 1))) == 1


def test_privacy_summary():
    reg = PrivacyConsentRegister()
    reg.record_consent('C1', ConsentPurpose.MARKETING_EMAIL, True, dt.date(2022, 1, 1))
    reg.raise_dsr('C1', DSRType.ACCESS, dt.date(2022, 1, 1))
    s = reg.privacy_summary(dt.date(2022, 3, 1))
    assert s['total_dsr'] == 1
    assert s['marketing_email_opt_ins'] == 1
    assert s['overdue_dsr'] == 1


def test_dsr_sequential_ids():
    reg = PrivacyConsentRegister()
    d1 = reg.raise_dsr('C1', DSRType.ACCESS, dt.date(2022, 1, 1))
    d2 = reg.raise_dsr('C2', DSRType.ERASURE, dt.date(2022, 1, 5))
    assert d1.request_id == 'DSR-0001'
    assert d2.request_id == 'DSR-0002'


def test_get_dsr_found():
    reg = PrivacyConsentRegister()
    dsr = reg.raise_dsr('C1', DSRType.PORTABILITY, dt.date(2022, 2, 1))
    found = reg.get_dsr(dsr.request_id)
    assert found is not None
    assert found.customer_id == 'C1'


def test_get_dsr_not_found():
    reg = PrivacyConsentRegister()
    assert reg.get_dsr('DSR-9999') is None


def test_customers_without_consent():
    reg = PrivacyConsentRegister()
    reg.record_consent('C1', ConsentPurpose.MARKETING_EMAIL, True, dt.date(2022, 1, 1))
    result = reg.customers_without_consent(ConsentPurpose.MARKETING_EMAIL, ['C1', 'C2', 'C3'])
    assert 'C1' not in result
    assert 'C2' in result
    assert 'C3' in result


def test_customers_without_consent_excludes_opted_in():
    reg = PrivacyConsentRegister()
    reg.record_consent('C1', ConsentPurpose.ANALYTICS, True, dt.date(2022, 1, 1))
    result = reg.customers_without_consent(ConsentPurpose.ANALYTICS, ['C1'])
    assert result == []


def test_dsr_not_overdue_on_deadline_day():
    d = DataSubjectRequest('DSR-0001', 'C1', DSRType.RECTIFICATION, dt.date(2022, 1, 1))
    # deadline = 2022-01-31; as_of == deadline is NOT overdue (> not >=)
    assert not d.is_overdue(dt.date(2022, 1, 31))


def test_dsr_latest_consent_wins():
    reg = PrivacyConsentRegister()
    # Earlier grant, later withdrawal
    reg.record_consent('C1', ConsentPurpose.SMART_METER_DATA, True, dt.date(2021, 1, 1))
    reg.record_consent('C1', ConsentPurpose.SMART_METER_DATA, False, dt.date(2022, 6, 1))
    assert not reg.has_active_consent('C1', ConsentPurpose.SMART_METER_DATA)


def test_overdue_requests_excludes_refused():
    reg = PrivacyConsentRegister()
    dsr = reg.raise_dsr('C1', DSRType.ERASURE, dt.date(2022, 1, 1))
    dsr.status = DSRStatus.REFUSED
    assert len(reg.overdue_requests(dt.date(2022, 3, 1))) == 0


def test_dsr_refused_not_overdue():
    d = DataSubjectRequest('DSR-0001', 'C1', DSRType.ACCESS, dt.date(2022, 1, 1))
    d.status = DSRStatus.REFUSED
    assert not d.is_overdue(dt.date(2022, 6, 1))


def test_privacy_summary_total_consent_records():
    reg = PrivacyConsentRegister()
    reg.record_consent('C1', ConsentPurpose.BILLING, True, dt.date(2022, 1, 1))
    reg.record_consent('C2', ConsentPurpose.ANALYTICS, False, dt.date(2022, 2, 1))
    s = reg.privacy_summary(dt.date(2022, 6, 1))
    assert s['total_consent_records'] == 2
