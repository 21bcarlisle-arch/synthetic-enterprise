import datetime as dt
import pytest
from company.crm.contact_journey import (
    ContactChannel, ContactPurpose, ContactOutcome,
    CustomerContactPrefs, ContactAttempt, ContactJourney
)


T1 = dt.datetime(2022, 3, 1, 10, 0)


def test_paper_free_eligible():
    p = CustomerContactPrefs('C1', ContactChannel.EMAIL, paper_free=True, bill_by_post=False)
    assert p.paper_free_discount_eligible


def test_paper_free_not_eligible_if_post():
    p = CustomerContactPrefs('C1', ContactChannel.POST, paper_free=True, bill_by_post=True)
    assert not p.paper_free_discount_eligible


def test_contact_attempt_successful():
    a = ContactAttempt('A1', 'C1', ContactChannel.EMAIL,
                         ContactPurpose.BILL, T1, ContactOutcome.OPENED)
    assert a.was_successful


def test_contact_attempt_bounced_not_successful():
    a = ContactAttempt('A2', 'C1', ContactChannel.EMAIL,
                         ContactPurpose.BILL, T1, ContactOutcome.BOUNCED)
    assert not a.was_successful


def test_channel_cost_email():
    j = ContactJourney()
    j.log_attempt('C1', ContactChannel.EMAIL, ContactPurpose.BILL, T1, ContactOutcome.DELIVERED)
    assert j.total_contact_cost_gbp(2022) == pytest.approx(0.002)


def test_channel_cost_post():
    j = ContactJourney()
    j.log_attempt('C1', ContactChannel.POST, ContactPurpose.BILL, T1, ContactOutcome.DELIVERED)
    assert j.total_contact_cost_gbp(2022) == pytest.approx(0.80)


def test_delivery_rate():
    j = ContactJourney()
    j.log_attempt('C1', ContactChannel.SMS, ContactPurpose.TARIFF_CHANGE, T1, ContactOutcome.DELIVERED)
    j.log_attempt('C2', ContactChannel.SMS, ContactPurpose.TARIFF_CHANGE, T1, ContactOutcome.BOUNCED)
    rate = j.delivery_rate_pct(ContactChannel.SMS, 2022)
    assert rate == pytest.approx(50.0)


def test_opted_out_customers():
    j = ContactJourney()
    j.log_attempt('C1', ContactChannel.EMAIL, ContactPurpose.MARKETING, T1, ContactOutcome.OPTED_OUT)
    j.log_attempt('C2', ContactChannel.EMAIL, ContactPurpose.MARKETING, T1, ContactOutcome.DELIVERED)
    assert 'C1' in j.opted_out_customers()
    assert 'C2' not in j.opted_out_customers()


def test_contact_summary():
    j = ContactJourney()
    j.set_prefs('C1', ContactChannel.EMAIL, paper_free=True)
    j.log_attempt('C1', ContactChannel.EMAIL, ContactPurpose.BILL, T1, ContactOutcome.OPENED)
    s = j.contact_summary(2022)
    assert s['total_attempts'] == 1
    assert s['paper_free_customers'] == 1
