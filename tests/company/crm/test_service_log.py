"""Tests for C4: CRM service interaction log (Phase 69)."""

import pytest

from company.crm.service_log import ServiceEvent, ServiceLog, VulnerabilityFlag
from company.crm.vulnerability_register import VulnerabilityFlag as OperationalFlag


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


# --- The register's term is the ONE operational vocabulary (atom C32) ---
#
# `flag_type` was `str`, and the live store is what that cost: 4,557 active rows, one distinct
# value, `financial_difficulty`, which is a member of NONE of the four vocabularies this
# obligation was spelled in. It was written as a hardcoded literal from `vulnerability_flag`, a
# BOOLEAN — a term invented at the point a term was needed and no term existed.


def _stored_flag_types(log):
    return [r["flag_type"] for r in log._c().execute("SELECT flag_type FROM vulnerability_flags")]


def test_a_flagged_contact_with_no_term_stores_no_term():
    """The boolean carries no term, so the row must not claim one.

    This is the leg that would have caught the original defect on its first write, and it is
    keyed to the property (an absence stays an absence) rather than to `!= 'financial_difficulty'`,
    which the next invented literal would pass.
    """
    log = ServiceLog()
    log.record_contact(_contact(vulnerability=True))
    assert _stored_flag_types(log) == [""]
    flag = log.vulnerability_register()[0]
    assert flag.flag_type is None
    assert flag.term_display == "Not recorded"


def test_a_caller_that_knows_the_term_round_trips_it():
    """Without this the test above is satisfied by a register that can never hold a term at
    all — which is the fail-closed drift a rewrite of this shape falls into.
    """
    log = ServiceLog()
    log.record_contact(
        _contact(vulnerability=True), vulnerability_term=OperationalFlag.PPM_SELF_DISCONNECTED
    )
    flag = log.vulnerability_register()[0]
    assert flag.flag_type is OperationalFlag.PPM_SELF_DISCONNECTED
    assert flag.recorded_as == "ppm_self_disconnected"
    assert flag.term_display == "Ppm Self Disconnected"


def test_a_legacy_row_reads_as_no_term_and_keeps_what_it_said():
    """THE BACK-COMPAT READ PATH, over the value 4,557 live rows actually hold.

    Nothing is coerced. `financial_difficulty` is NOT `payment_difficulty`: it was written from
    a boolean, so it named no state, and `fuel_poverty`, `payment_difficulty` and `job_loss` are
    three different operational terms it could equally have stood for. Mapping it would move the
    guess from the column into a dict, where it would read as established.
    """
    log = ServiceLog()
    log._c().execute(
        "INSERT INTO vulnerability_flags (customer_id, flagged_date, flag_type)"
        " VALUES ('C1', '2026-06-26', 'financial_difficulty')"
    )
    flag = log.vulnerability_register()[0]
    assert flag.flag_type is None
    assert flag.recorded_as == "financial_difficulty"
    assert flag.term_display == "Not recorded (stored as 'financial_difficulty')"
    # ...and the surface does not render an off-vocabulary string as a confident English label,
    # which is what `flag_type.replace('_', ' ').title()` did for every one of those rows.
    assert "Financial Difficulty" not in flag.term_display


def test_a_stored_term_that_is_in_the_vocabulary_still_reads_back():
    """The legacy path must not swallow good rows: a control that answered `None` to everything
    would pass the two tests above and lose the register.
    """
    log = ServiceLog()
    log._c().execute(
        "INSERT INTO vulnerability_flags (customer_id, flagged_date, flag_type)"
        " VALUES ('C2', '2026-06-26', 'medical_equipment')"
    )
    assert log.vulnerability_register()[0].flag_type is OperationalFlag.MEDICAL_EQUIPMENT
