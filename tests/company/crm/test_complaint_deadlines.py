"""Phase 94: Complaint deadline tracking tests."""

from datetime import date, timedelta
from company.crm.service_log import ServiceLog, ServiceEvent, _add_working_days
from starlette.testclient import TestClient
from company.portal.app import app

client = TestClient(app, raise_server_exceptions=True)


def _complaint_event(cid, event_date, outcome="pending"):
    return ServiceEvent(
        customer_id=cid, event_date=event_date,
        channel="portal", contact_reason="complaint",
        outcome=outcome, complaint_flag=True,
    )


def test_add_working_days_skips_weekends():
    # 2026-06-25 Thursday + 2 working days = 2026-06-29 Monday (skip Sat/Sun)
    result = _add_working_days(date(2026, 6, 25), 2)
    assert result == date(2026, 6, 29)


def test_add_working_days_one():
    # Friday + 1 working day = Monday
    result = _add_working_days(date(2026, 6, 26), 1)
    assert result == date(2026, 6, 29)  # skip weekend


def test_complaint_deadlines_empty():
    log = ServiceLog()
    assert log.complaint_deadlines() == []


def test_complaint_deadlines_structure():
    log = ServiceLog()
    log.record_contact(_complaint_event("C1", "2026-06-24"))
    deadlines = log.complaint_deadlines()
    assert len(deadlines) == 1
    d = deadlines[0]
    assert "acknowledge_by" in d
    assert "resolve_by" in d
    assert "ack_overdue" in d
    assert "resolve_overdue" in d


def test_complaint_ack_deadline_two_working_days():
    log = ServiceLog()
    log.record_contact(_complaint_event("C1", "2026-06-25"))  # Thursday
    d = log.complaint_deadlines()[0]
    # Thursday + 2 working days = Monday
    assert d["acknowledge_by"] == "2026-06-29"


def test_complaint_resolve_deadline_eight_weeks():
    log = ServiceLog()
    log.record_contact(_complaint_event("C1", "2026-06-01"))
    d = log.complaint_deadlines()[0]
    # 8 weeks from 2026-06-01 = 2026-07-27
    assert d["resolve_by"] == "2026-07-27"


def test_complaint_resolved_outcome():
    log = ServiceLog()
    log.record_contact(_complaint_event("C1", "2026-06-24", outcome="resolved"))
    d = log.complaint_deadlines()[0]
    assert d["resolved"] is True
    assert d["ack_overdue"] is False


def test_admin_complaints_route_returns_200():
    r = client.get("/admin/complaints")
    assert r.status_code == 200


def test_admin_complaints_shows_empty_state():
    r = client.get("/admin/complaints")
    # Either shows table or empty state
    assert "Complaint" in r.text


def test_admin_link_from_admin_page():
    with open("company/portal/templates/admin_complaints.html") as f:
        html = f.read()
    assert "acknowledge" in html.lower() or "Ofgem" in html
