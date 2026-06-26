"""Phase 129: Customer notification preferences tests."""

import pytest
from company.crm.notification_prefs import NotificationPreferences


def _prefs():
    p = NotificationPreferences()
    p.set("C1", "email", "service", True, "2024-01-01")
    p.set("C1", "sms", "service", False, "2024-01-01")
    p.set("C1", "email", "marketing", True, "2024-01-01")
    p.set("C1", "post", "paper_bills", True, "2024-01-01")
    p.set("C2", "email", "service", True, "2024-01-01")
    p.set("C2", "email", "marketing", False, "2024-06-01")
    return p


def test_set_and_get():
    p = _prefs()
    assert p.get("C1", "email", "service") is True
    assert p.get("C1", "sms", "service") is False


def test_unknown_channel_raises():
    p = NotificationPreferences()
    with pytest.raises(ValueError, match="Unknown channel"):
        p.set("C1", "pigeon", "service", True, "2024-01-01")


def test_unknown_pref_type_raises():
    p = NotificationPreferences()
    with pytest.raises(ValueError, match="Unknown pref_type"):
        p.set("C1", "email", "promo", True, "2024-01-01")


def test_enabled_channels_for_service():
    p = _prefs()
    assert "email" in p.enabled_channels_for("C1", "service")
    assert "sms" not in p.enabled_channels_for("C1", "service")


def test_can_contact_explicit_true():
    p = _prefs()
    assert p.can_contact("C1", "email", "marketing") is True


def test_can_contact_explicit_false():
    p = _prefs()
    assert p.can_contact("C2", "email", "marketing") is False


def test_can_contact_default_service_email():
    p = NotificationPreferences()
    # No preferences set — default: service email allowed
    assert p.can_contact("UNKNOWN", "email", "service") is True


def test_can_contact_default_marketing_denied():
    p = NotificationPreferences()
    assert p.can_contact("UNKNOWN", "email", "marketing") is False


def test_opted_out_marketing():
    p = _prefs()
    assert p.opted_out_marketing("C1") is False
    assert p.opted_out_marketing("C2") is True


def test_paper_bill_customers():
    p = _prefs()
    assert "C1" in p.paper_bill_customers()
    assert "C2" not in p.paper_bill_customers()


def test_summary_structure():
    p = _prefs()
    s = p.summary("C1")
    assert "service_channels" in s
    assert "marketing_opted_out" in s
    assert s["paper_bills"] is True
