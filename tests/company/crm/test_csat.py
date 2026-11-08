"""Phase 105: CSAT score tracking tests."""

from company.crm.service_log import ServiceLog, ServiceEvent


def _event(cid="C1", csat=None) -> ServiceEvent:
    return ServiceEvent(
        customer_id=cid, event_date="2026-06-26",
        channel="portal", contact_reason="general",
        outcome="pending", csat_score=csat,
    )


def test_csat_summary_empty_when_no_ratings():
    log = ServiceLog()
    s = log.csat_summary()
    assert s["count"] == 0
    assert s["mean"] is None


def test_csat_summary_with_single_score():
    log = ServiceLog()
    log.record_contact(_event(csat=5))
    s = log.csat_summary()
    assert s["count"] == 1
    assert s["mean"] == 5.0


def test_csat_summary_promoter_pct():
    log = ServiceLog()
    for score in [5, 4, 3, 2]:
        log.record_contact(_event(csat=score))
    s = log.csat_summary()
    assert s["promoter_pct"] == 50.0  # 2 of 4 are 4+ stars


def test_rate_contact_updates_score():
    log = ServiceLog()
    log.record_contact(_event())
    cid = log.latest_contact_id("C1")
    assert cid is not None
    result = log.rate_contact(cid, 4)
    assert result is True
    s = log.csat_summary()
    assert s["mean"] == 4.0


def test_rate_contact_invalid_score():
    log = ServiceLog()
    log.record_contact(_event())
    cid = log.latest_contact_id("C1")
    import pytest
    with pytest.raises(ValueError):
        log.rate_contact(cid, 6)


def test_csat_ignores_unrated_contacts():
    log = ServiceLog()
    log.record_contact(_event(csat=None))
    log.record_contact(_event(csat=5))
    s = log.csat_summary()
    assert s["count"] == 1  # only rated contact counted


# --- Phase KS depth tests ---

def test_customer_id_stored():
    e = _event(cid='CUST_KS', csat=4)
    assert e.customer_id == 'CUST_KS'


def test_channel_stored():
    e = ServiceEvent(customer_id='C1', event_date='2022-01-01',
                     channel='phone', contact_reason='billing', outcome='resolved')
    assert e.channel == 'phone'


def test_contact_reason_stored():
    e = ServiceEvent(customer_id='C1', event_date='2022-01-01',
                     channel='portal', contact_reason='complaint', outcome='open')
    assert e.contact_reason == 'complaint'


def test_outcome_stored():
    e = ServiceEvent(customer_id='C1', event_date='2022-01-01',
                     channel='portal', contact_reason='billing', outcome='resolved')
    assert e.outcome == 'resolved'


def test_csat_score_stored():
    e = _event(csat=3)
    assert e.csat_score == 3


def test_csat_none_when_not_rated():
    e = _event(csat=None)
    assert e.csat_score is None


def test_csat_summary_mean_of_two():
    log = ServiceLog()
    log.record_contact(_event(csat=3))
    log.record_contact(_event(csat=5))
    s = log.csat_summary()
    assert s['mean'] == 4.0


def test_contacts_for_customer_filters():
    log = ServiceLog()
    log.record_contact(_event(cid='C1', csat=4))
    log.record_contact(_event(cid='C2', csat=5))
    contacts_c1 = log.contacts_for_customer('C1')
    assert len(contacts_c1) == 1


def test_complaint_rate_zero_no_complaints():
    log = ServiceLog()
    log.record_contact(_event(csat=4))
    assert log.complaint_rate() == 0.0


def test_latest_contact_id_returns_id():
    log = ServiceLog()
    log.record_contact(_event(cid='C_LCI', csat=5))
    cid = log.latest_contact_id('C_LCI')
    assert cid is not None
