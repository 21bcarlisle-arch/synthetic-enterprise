"""Tests: Phase DB — ICO Data Breach Notification Register (UK GDPR / DPA 2018)."""
import datetime as dt
import pytest
from company.regulatory.ico_breach_register import (
    ICOBreachRegister, BreachType, DataCategory, BreachSeverity,
    ICONotificationStatus, IndividualNotificationStatus, DataBreachRecord,
    _assess_severity, _ICO_NOTIFICATION_HOURS, _MAX_FINE_ARTICLE_83_5, _MAX_FINE_ARTICLE_83_4,
)

_NOW = dt.datetime(2023, 6, 15, 9, 0, 0, tzinfo=dt.timezone.utc)
_OCCURRED = dt.datetime(2023, 6, 15, 8, 0, 0, tzinfo=dt.timezone.utc)


def _register():
    return ICOBreachRegister()


def _minor_breach(reg):
    return reg.record_breach(
        breach_type=BreachType.AVAILABILITY,
        data_categories=(DataCategory.CONTACT_DETAILS,),
        detected_at=_NOW,
        occurred_at=_OCCURRED,
        accounts_affected=3,
        description="Email address visible in error log for 1 hour",
    )


def _critical_breach(reg):
    return reg.record_breach(
        breach_type=BreachType.CONFIDENTIALITY,
        data_categories=(DataCategory.BANK_DETAILS, DataCategory.BILLING),
        detected_at=_NOW,
        occurred_at=_OCCURRED,
        accounts_affected=500,
        description="Portal bug exposed bank details to other logged-in users",
    )


def _high_breach(reg):
    return reg.record_breach(
        breach_type=BreachType.CONFIDENTIALITY,
        data_categories=(DataCategory.SMART_METER,),
        detected_at=_NOW,
        occurred_at=_OCCURRED,
        accounts_affected=50,
        description="HH consumption data sent to wrong account holder",
    )


# ── severity assessment ──────────────────────────────────────────────────────

def test_severity_minor_few_contacts():
    assert _assess_severity((DataCategory.CONTACT_DETAILS,), 3) == BreachSeverity.MINOR

def test_severity_moderate_many_contacts():
    assert _assess_severity((DataCategory.CONTACT_DETAILS,), 50) == BreachSeverity.MODERATE

def test_severity_high_sensitive_few():
    assert _assess_severity((DataCategory.SMART_METER,), 10) == BreachSeverity.HIGH

def test_severity_critical_bank_details_many():
    assert _assess_severity((DataCategory.BANK_DETAILS,), 200) == BreachSeverity.CRITICAL

def test_severity_critical_vulnerability_flags():
    assert _assess_severity((DataCategory.VULNERABILITY_FLAGS,), 100) == BreachSeverity.CRITICAL

def test_severity_zero_accounts_always_minor():
    assert _assess_severity((DataCategory.BANK_DETAILS,), 0) == BreachSeverity.MINOR

def test_severity_high_many_non_sensitive():
    assert _assess_severity((DataCategory.USAGE_HISTORY,), 1000) == BreachSeverity.HIGH


# ── record_breach ────────────────────────────────────────────────────────────

def test_record_assigns_id():
    reg = _register()
    b = _minor_breach(reg)
    assert b.breach_id == "IDB-0001"

def test_record_minor_status_none_required():
    reg = _register()
    b = _minor_breach(reg)
    assert b.severity == BreachSeverity.MINOR
    assert b.ico_status == ICONotificationStatus.NONE_REQUIRED
    assert b.individual_status == IndividualNotificationStatus.NOT_REQUIRED

def test_record_critical_status_pending():
    reg = _register()
    b = _critical_breach(reg)
    assert b.severity == BreachSeverity.CRITICAL
    assert b.ico_status == ICONotificationStatus.PENDING
    assert b.individual_status == IndividualNotificationStatus.PENDING

def test_record_high_individual_notification_required():
    reg = _register()
    b = _high_breach(reg)
    assert b.individual_status == IndividualNotificationStatus.PENDING

def test_record_increments_ids():
    reg = _register()
    b1 = _minor_breach(reg)
    b2 = _minor_breach(reg)
    assert b1.breach_id == "IDB-0001"
    assert b2.breach_id == "IDB-0002"


# ── notify_ico ───────────────────────────────────────────────────────────────

def test_notify_ico_within_72h():
    reg = _register()
    b = _critical_breach(reg)
    notified = _NOW + dt.timedelta(hours=48)
    updated = reg.notify_ico(b.breach_id, notified_at=notified, ico_reference="DP-2023-001")
    assert updated.ico_status == ICONotificationStatus.NOTIFIED
    assert updated.ico_reference == "DP-2023-001"
    assert updated.is_within_72h is True

def test_notify_ico_late():
    reg = _register()
    b = _critical_breach(reg)
    notified = _NOW + dt.timedelta(hours=80)
    updated = reg.notify_ico(b.breach_id, notified_at=notified)
    assert updated.ico_status == ICONotificationStatus.LATE_NOTIFICATION
    assert updated.is_within_72h is False

def test_hours_to_notification_none_before_notification():
    reg = _register()
    b = _critical_breach(reg)
    assert b.hours_to_ico_notification is None

def test_hours_to_notification_correct():
    reg = _register()
    b = _critical_breach(reg)
    notified = _NOW + dt.timedelta(hours=36)
    updated = reg.notify_ico(b.breach_id, notified_at=notified)
    assert abs(updated.hours_to_ico_notification - 36.0) < 0.01


# ── individual notification ──────────────────────────────────────────────────

def test_complete_individual_notification():
    reg = _register()
    b = _critical_breach(reg)
    updated = reg.complete_individual_notification(b.breach_id)
    assert updated.individual_status == IndividualNotificationStatus.COMPLETED


# ── investigation / close ────────────────────────────────────────────────────

def test_open_investigation():
    reg = _register()
    b = _critical_breach(reg)
    updated = reg.open_investigation(b.breach_id)
    assert updated.ico_status == ICONotificationStatus.INVESTIGATION_OPEN

def test_close_with_fine():
    reg = _register()
    b = _critical_breach(reg)
    closed_at = _NOW + dt.timedelta(days=90)
    updated = reg.close(b.breach_id, closed_at=closed_at, estimated_fine_gbp=500_000.0)
    assert updated.ico_status == ICONotificationStatus.CLOSED
    assert updated.estimated_fine_gbp == 500_000.0
    assert updated.is_active is False


# ── fine exposure ────────────────────────────────────────────────────────────

def test_fine_exposure_critical():
    reg = _register()
    b = _critical_breach(reg)
    assert b.maximum_fine_exposure_gbp == _MAX_FINE_ARTICLE_83_5

def test_fine_exposure_moderate():
    reg = _register()
    b = reg.record_breach(
        breach_type=BreachType.CONFIDENTIALITY,
        data_categories=(DataCategory.CONTACT_DETAILS,),
        detected_at=_NOW, occurred_at=_OCCURRED,
        accounts_affected=50, description="Moderate breach",
    )
    assert b.maximum_fine_exposure_gbp == _MAX_FINE_ARTICLE_83_4

def test_total_fine_exposure_active_only():
    reg = _register()
    b = _critical_breach(reg)
    _ = _high_breach(reg)
    assert reg.total_fine_exposure_gbp == _MAX_FINE_ARTICLE_83_5 * 2


# ── sensitive data ───────────────────────────────────────────────────────────

def test_contains_sensitive_data_smart_meter():
    reg = _register()
    b = _high_breach(reg)
    assert b.contains_sensitive_data is True

def test_not_sensitive_data_billing_only():
    reg = _register()
    b = reg.record_breach(
        breach_type=BreachType.CONFIDENTIALITY,
        data_categories=(DataCategory.BILLING,),
        detected_at=_NOW, occurred_at=_OCCURRED,
        accounts_affected=5, description="Billing only",
    )
    assert b.contains_sensitive_data is False


# ── queries ──────────────────────────────────────────────────────────────────

def test_active_breaches_excludes_closed():
    reg = _register()
    b1 = _critical_breach(reg)
    _minor_breach(reg)
    reg.close(b1.breach_id, closed_at=_NOW + dt.timedelta(days=10))
    active = reg.active_breaches
    assert not any(b.breach_id == b1.breach_id for b in active)

def test_active_breaches_excludes_none_required():
    reg = _register()
    _ = _minor_breach(reg)
    assert len(reg.active_breaches) == 0

def test_sensitive_data_breaches_query():
    reg = _register()
    _minor_breach(reg)
    _high_breach(reg)
    assert len(reg.sensitive_data_breaches) == 1

def test_breaches_by_severity():
    reg = _register()
    _minor_breach(reg)
    _critical_breach(reg)
    _high_breach(reg)
    by_sev = reg.breaches_by_severity()
    assert by_sev["minor"] == 1
    assert by_sev["critical"] == 1
    assert by_sev["high"] == 1

def test_total_accounts_affected():
    reg = _register()
    _minor_breach(reg)   # 3
    _critical_breach(reg)  # 500
    assert reg.total_accounts_affected == 503

def test_ico_breach_summary_format():
    reg = _register()
    _critical_breach(reg)
    s = reg.ico_breach_summary()
    assert "ICO Breach Register" in s
    assert "overdue" in s
    assert "17,500,000" in s


# ── is_active flag ──────────────────────────────────────────────────────────

def test_is_active_pending():
    reg = _register()
    b = _critical_breach(reg)
    assert b.is_active is True

def test_is_active_notified_still_active():
    reg = _register()
    b = _critical_breach(reg)
    updated = reg.notify_ico(b.breach_id, notified_at=_NOW + dt.timedelta(hours=24))
    assert updated.is_active is True

def test_is_active_false_when_closed():
    reg = _register()
    b = _critical_breach(reg)
    updated = reg.close(b.breach_id, closed_at=_NOW + dt.timedelta(days=30))
    assert updated.is_active is False
