import datetime as dt
import pytest
from company.crm.behaviour_segment import (
    PaymentBehaviour, EngagementLevel, SwitchingRisk, CustomerSegment,
    BehaviourProfile, BehaviourSegmentBook
)

DATE = dt.date(2023, 6, 30)


def _profile(**kwargs):
    defaults = dict(
        customer_id="C1",
        as_of_date=DATE,
        payment_on_time_rate=0.97,
        portal_logins_per_month=3.0,
        inbound_contacts_per_quarter=0.5,
        months_since_last_switch=None,
        paper_free=False,
    )
    defaults.update(kwargs)
    return BehaviourProfile(**defaults)


def test_payment_behaviour_exemplary():
    p = _profile(payment_on_time_rate=0.98)
    assert p.payment_behaviour == PaymentBehaviour.EXEMPLARY


def test_payment_behaviour_chronic_late():
    p = _profile(payment_on_time_rate=0.45)
    assert p.payment_behaviour == PaymentBehaviour.CHRONIC_LATE


def test_engagement_highly_engaged_paper_free():
    p = _profile(paper_free=True, portal_logins_per_month=1.0)
    assert p.engagement_level == EngagementLevel.HIGHLY_ENGAGED


def test_engagement_disengaged_no_logins():
    p = _profile(portal_logins_per_month=0.0)
    assert p.engagement_level == EngagementLevel.DISENGAGED


def test_switching_risk_high_recent():
    p = _profile(months_since_last_switch=8)
    assert p.switching_risk == SwitchingRisk.HIGH


def test_switching_risk_low_never():
    p = _profile(months_since_last_switch=None)
    assert p.switching_risk == SwitchingRisk.LOW


def test_segment_champion():
    p = _profile(
        payment_on_time_rate=0.99, portal_logins_per_month=5.0,
        months_since_last_switch=None,
    )
    assert p.segment == CustomerSegment.CHAMPION
    assert p.recommended_intervention == "loyalty_reward"


def test_segment_at_risk():
    p = _profile(
        payment_on_time_rate=0.92, portal_logins_per_month=2.0,
        months_since_last_switch=10,
    )
    assert p.segment == CustomerSegment.AT_RISK
    assert p.recommended_intervention == "proactive_outreach"


def test_segment_struggling():
    p = _profile(
        payment_on_time_rate=0.55, portal_logins_per_month=1.0,
        months_since_last_switch=None,
    )
    assert p.segment == CustomerSegment.STRUGGLING
    assert p.recommended_intervention == "debt_support"


def test_segment_churner_bad_payer_high_risk():
    p = _profile(
        payment_on_time_rate=0.40, months_since_last_switch=6,
    )
    assert p.segment == CustomerSegment.CHURNER


def test_segment_disengaged_stable():
    p = _profile(
        payment_on_time_rate=0.98, portal_logins_per_month=0.0,
        months_since_last_switch=None,
    )
    assert p.segment == CustomerSegment.DISENGAGED_STABLE


def test_book_latest_profile():
    book = BehaviourSegmentBook()
    book.record_profile("C1", dt.date(2023, 3, 31), 0.95, 2.0, 0.5, None)
    book.record_profile("C1", DATE, 0.98, 3.0, 0.2, None)
    latest = book.latest_profile("C1")
    assert latest.as_of_date == DATE
    assert latest.payment_on_time_rate == pytest.approx(0.98)


def test_book_segment_counts():
    book = BehaviourSegmentBook()
    book.record_profile("C1", DATE, 0.98, 5.0, 0.1, None)   # champion
    book.record_profile("C2", DATE, 0.88, 2.0, 0.5, 20)     # loyal (medium risk)
    book.record_profile("C3", DATE, 0.90, 2.0, 0.5, 8)      # at_risk
    counts = book.segment_counts(DATE)
    assert counts.get("champion", 0) >= 1
    assert counts.get("at_risk", 0) >= 1


def test_book_segment_summary():
    book = BehaviourSegmentBook()
    book.record_profile("C1", DATE, 0.40, 0.0, 3.0, 10)     # churner
    book.record_profile("C2", DATE, 0.55, 1.0, 2.0, None)   # struggling
    book.record_profile("C3", DATE, 0.97, 4.0, 0.2, None)   # champion
    s = book.segment_summary(DATE)
    assert s["total_profiled"] == 3
    assert s["at_risk_count"] >= 1
    assert s["struggling_count"] >= 1
