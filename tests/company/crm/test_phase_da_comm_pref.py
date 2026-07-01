"""Phase DA: Customer Communication Preference Register tests."""
import pytest
from datetime import date
from company.crm.customer_comm_preferences import (
    CustomerCommPreferenceRegister, CommChannel, CommPurpose
)

_D = date(2022, 1, 1)


def _reg():
    return CustomerCommPreferenceRegister()


# 1. billing can always be contacted (essential)
def test_essential_billing_always():
    r = _reg()
    assert r.can_contact("C1", CommChannel.EMAIL, CommPurpose.BILLING)


# 2. service notice is essential (cannot be blocked)
def test_essential_service_notice():
    r = _reg()
    r.set_preference("C1", CommChannel.EMAIL, opted_in=False, preference_date=_D, purpose=CommPurpose.SERVICE_NOTICE)
    assert r.can_contact("C1", CommChannel.EMAIL, CommPurpose.SERVICE_NOTICE)


# 3. marketing blocked without opt-in
def test_marketing_blocked_without_opt_in():
    r = _reg()
    assert not r.can_contact("C1", CommChannel.EMAIL, CommPurpose.MARKETING)


# 4. marketing allowed after opt-in
def test_marketing_allowed_after_opt_in():
    r = _reg()
    r.set_marketing_opt_in("C1", True, _D)
    assert r.can_contact("C1", CommChannel.EMAIL, CommPurpose.MARKETING)


# 5. marketing blocked after opt-out
def test_marketing_blocked_after_opt_out():
    r = _reg()
    r.set_marketing_opt_in("C1", True, _D)
    r.set_marketing_opt_in("C1", False, date(2022, 6, 1))
    assert not r.can_contact("C1", CommChannel.EMAIL, CommPurpose.MARKETING)


# 6. sms opt-out respected for non-essential
def test_sms_opt_out():
    r = _reg()
    r.set_preference("C1", CommChannel.SMS, opted_in=False, preference_date=_D, purpose=CommPurpose.TARIFF_ALERT)
    assert not r.can_contact("C1", CommChannel.SMS, CommPurpose.TARIFF_ALERT)


# 7. suppressed account: only essential channels
def test_suppressed_billing():
    r = _reg()
    r.suppress_account("C1")
    assert r.can_contact("C1", CommChannel.EMAIL, CommPurpose.BILLING)


# 8. suppressed account: non-essential blocked
def test_suppressed_no_marketing():
    r = _reg()
    r.suppress_account("C1")
    r.set_marketing_opt_in("C1", True, _D)
    assert not r.can_contact("C1", CommChannel.EMAIL, CommPurpose.MARKETING)


# 9. marketing_opt_in_accounts list
def test_marketing_opt_in_accounts():
    r = _reg()
    r.set_marketing_opt_in("C1", True, _D)
    r.set_marketing_opt_in("C2", False, _D)
    assert "C1" in r.marketing_opt_in_accounts
    assert "C2" not in r.marketing_opt_in_accounts


# 10. suppressed_accounts list
def test_suppressed_accounts():
    r = _reg()
    r.suppress_account("C1")
    assert "C1" in r.suppressed_accounts


# 11. paperless_accounts (opted out of paper bill)
def test_paperless_accounts():
    r = _reg()
    r.set_preference("C1", CommChannel.PAPER_BILL, opted_in=False, preference_date=_D, purpose=CommPurpose.BILLING)
    assert "C1" in r.paperless_accounts


# 12. comm_preference_summary contains GDPR
def test_summary():
    r = _reg()
    r.set_marketing_opt_in("C1", True, _D)
    summary = r.comm_preference_summary()
    assert "GDPR" in summary
    assert "PECR" in summary


# --- Phase LT depth tests ---

def test_unknown_customer_billing_allowed():
    r = _reg()
    assert r.can_contact('UNKNOWN_LT', CommChannel.EMAIL, CommPurpose.BILLING) is True


def test_unknown_customer_marketing_blocked():
    r = _reg()
    assert r.can_contact('UNKNOWN_LT', CommChannel.EMAIL, CommPurpose.MARKETING) is False


def test_marketing_opt_in_enables_marketing():
    r = _reg()
    r.set_marketing_opt_in('C1', True, _D)
    assert r.can_contact('C1', CommChannel.EMAIL, CommPurpose.MARKETING) is True


def test_marketing_opt_out_blocks_after_optin():
    r = _reg()
    r.set_marketing_opt_in('C1', True, _D)
    r.set_marketing_opt_in('C1', False, date(_D.year, _D.month + 1, 1))
    assert r.can_contact('C1', CommChannel.EMAIL, CommPurpose.MARKETING) is False


def test_suppressed_account_blocks_marketing():
    r = _reg()
    r.set_marketing_opt_in('C1', True, _D)
    r.suppress_account('C1')
    assert r.can_contact('C1', CommChannel.EMAIL, CommPurpose.MARKETING) is False


def test_suppressed_account_allows_billing():
    r = _reg()
    r.suppress_account('C1')
    assert r.can_contact('C1', CommChannel.EMAIL, CommPurpose.BILLING) is True


def test_marketing_opt_in_accounts_list():
    r = _reg()
    r.set_marketing_opt_in('C1', True, _D)
    r.set_marketing_opt_in('C2', False, _D)
    assert 'C1' in r.marketing_opt_in_accounts
    assert 'C2' not in r.marketing_opt_in_accounts


def test_suppressed_accounts_list():
    r = _reg()
    r.suppress_account('C1')
    assert 'C1' in r.suppressed_accounts


def test_tariff_alert_allowed_unknown_email():
    r = _reg()
    # tariff_alert is not essential and not marketing → default: email/post/portal allowed
    assert r.can_contact('UNKNOWN', CommChannel.EMAIL, CommPurpose.TARIFF_ALERT) is True


def test_tariff_alert_blocked_sms_unknown():
    r = _reg()
    # Unknown customer, non-essential, SMS not in default allowed channels
    assert r.can_contact('UNKNOWN', CommChannel.SMS, CommPurpose.TARIFF_ALERT) is False
