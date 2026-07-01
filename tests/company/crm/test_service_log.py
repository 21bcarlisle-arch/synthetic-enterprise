"""Tests for C4: CRM service interaction log (Phase 69)."""

import pytest
from company.crm.service_log import ServiceEvent, ServiceLog, VulnerabilityFlag


def _contact(customer_id="C1", date="2016-06-01", reason="billing_query",
              complaint=False, vulnerability=False, outcome="resolved"):
    return ServiceEvent(
        customer_id=customer_id,
        event_date=date,
        channel="phone",
        contact_reason=reason,
        outcome=outcome,
        complaint_flag=complaint,
        vulnerability_flag=vulnerability,
    )


def test_record_contact_and_retrieve():
    log = ServiceLog()
    log.record_contact(_contact())
    assert len(log.all_contacts()) == 1
    assert log.all_contacts()[0].customer_id == "C1"


def test_contacts_for_customer_filters_correctly():
    log = ServiceLog()
    log.record_contact(_contact("C1"))
    log.record_contact(_contact("C2"))
    log.record_contact(_contact("C1"))
    assert len(log.contacts_for_customer("C1")) == 2
    assert len(log.contacts_for_customer("C2")) == 1
    assert len(log.contacts_for_customer("C99")) == 0


def test_complaints_filter():
    log = ServiceLog()
    log.record_contact(_contact(complaint=False))
    log.record_contact(_contact(complaint=True))
    log.record_contact(_contact(complaint=True))
    assert len(log.complaints()) == 2


def test_complaint_rate_zero_when_no_contacts():
    log = ServiceLog()
    assert log.complaint_rate() == 0.0


def test_complaint_rate_calculates_correctly():
    log = ServiceLog()
    log.record_contact(_contact(complaint=True))
    log.record_contact(_contact(complaint=False))
    log.record_contact(_contact(complaint=False))
    log.record_contact(_contact(complaint=False))
    assert log.complaint_rate() == 0.25


def test_complaint_stats_returns_all_keys():
    log = ServiceLog()
    log.record_contact(_contact(complaint=True))
    log.record_contact(_contact())
    stats = log.complaint_stats()
    assert set(stats.keys()) == {"total_contacts", "total_complaints", "complaint_rate"}
    assert stats["total_contacts"] == 2
    assert stats["total_complaints"] == 1


def test_complaint_stats_year_filter():
    log = ServiceLog()
    log.record_contact(_contact(date="2016-03-01", complaint=True))
    log.record_contact(_contact(date="2017-03-01", complaint=False))
    stats_2016 = log.complaint_stats(year=2016)
    assert stats_2016["total_contacts"] == 1
    assert stats_2016["total_complaints"] == 1


def test_vulnerability_flag_added_on_contact():
    log = ServiceLog()
    log.record_contact(_contact(vulnerability=True))
    register = log.vulnerability_register()
    assert len(register) == 1
    assert register[0].customer_id == "C1"
    assert register[0].active is True


def test_vulnerability_not_flagged_on_normal_contact():
    log = ServiceLog()
    log.record_contact(_contact(vulnerability=False))
    assert len(log.vulnerability_register()) == 0


def test_resolve_vulnerability_marks_inactive():
    log = ServiceLog()
    log.record_contact(_contact(vulnerability=True))
    count = log.resolve_vulnerability("C1", "2016-12-01")
    assert count == 1
    assert len(log.vulnerability_register()) == 0


def test_as_dicts_returns_correct_structure():
    log = ServiceLog()
    log.record_contact(_contact(complaint=True))
    dicts = log.as_dicts()
    assert len(dicts) == 1
    assert dicts[0]["event_type"] == "service_contact"
    assert dicts[0]["complaint_flag"] is True
    assert "channel" in dicts[0]
    assert "contact_reason" in dicts[0]


def test_multiple_contacts_same_customer_separate_records():
    log = ServiceLog()
    for i in range(5):
        log.record_contact(ServiceEvent(
            customer_id="C3", event_date=f"2016-0{i+1}-01",
            channel="email", contact_reason="billing_query",
            outcome="resolved",
        ))
    assert len(log.contacts_for_customer("C3")) == 5


# --- Phase LV depth tests ---

def test_customer_id_stored():
    ev = _contact(customer_id='CUST_LV')
    assert ev.customer_id == 'CUST_LV'


def test_event_date_stored():
    ev = _contact(date='2022-07-01')
    assert ev.event_date == '2022-07-01'


def test_channel_stored():
    ev = ServiceEvent(
        customer_id='C1', event_date='2022-01-01', channel='sms',
        contact_reason='billing_query', outcome='resolved',
    )
    assert ev.channel == 'sms'


def test_contact_reason_stored():
    ev = _contact(reason='meter_read')
    assert ev.contact_reason == 'meter_read'


def test_outcome_stored():
    ev = _contact(outcome='escalated')
    assert ev.outcome == 'escalated'


def test_complaint_flag_default_false():
    ev = _contact()
    assert ev.complaint_flag is False


def test_vulnerability_flag_default_false():
    ev = _contact()
    assert ev.vulnerability_flag is False


def test_agent_type_default_ai():
    ev = _contact()
    assert ev.agent_type == 'ai'


def test_notes_default_empty():
    ev = _contact()
    assert ev.notes == ''


def test_csat_score_default_none():
    ev = _contact()
    assert ev.csat_score is None
