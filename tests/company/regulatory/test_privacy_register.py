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
