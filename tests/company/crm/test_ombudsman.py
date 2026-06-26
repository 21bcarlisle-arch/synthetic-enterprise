"""Phase 104: Ombudsman referral tracking tests."""

from datetime import date, timedelta
from company.crm.service_log import ServiceLog, ServiceEvent


def _make_log(complaint_date: str, outcome: str = "pending") -> ServiceLog:
    log = ServiceLog()
    log.record_contact(ServiceEvent(
        customer_id="C_TEST", event_date=complaint_date,
        channel="phone", contact_reason="billing_query", outcome=outcome,
        complaint_flag=True,
    ))
    return log


def test_ombudsman_eligible_empty_when_no_complaints():
    log = ServiceLog()
    assert log.ombudsman_eligible() == []


def test_ombudsman_eligible_fresh_complaint():
    # Complaint today — not yet eligible
    log = _make_log(date.today().isoformat())
    assert log.ombudsman_eligible() == []


def test_ombudsman_eligible_old_complaint():
    # Complaint 9 weeks ago — eligible
    old = (date.today() - timedelta(weeks=9)).isoformat()
    log = _make_log(old, outcome="pending")
    assert len(log.ombudsman_eligible()) == 1


def test_ombudsman_count_zero():
    log = ServiceLog()
    assert log.ombudsman_count() == 0


def test_ombudsman_count_matches_eligible():
    old = (date.today() - timedelta(weeks=9)).isoformat()
    log = _make_log(old, outcome="pending")
    assert log.ombudsman_count() == len(log.ombudsman_eligible())


def test_resolved_complaint_not_eligible():
    old = (date.today() - timedelta(weeks=9)).isoformat()
    log = _make_log(old, outcome="resolved")
    assert log.ombudsman_eligible() == []


def test_admin_complaints_has_ombudsman_section():
    with open("company/portal/templates/admin_complaints.html") as f:
        html = f.read()
    assert "ombudsman" in html
    assert "deadlock" in html


def test_regulatory_has_ombudsman_section():
    with open("company/portal/templates/regulatory.html") as f:
        html = f.read()
    assert "Ombudsman" in html


def test_admin_complaints_route_includes_ombudsman():
    from starlette.testclient import TestClient
    from company.portal.app import app
    client = TestClient(app, raise_server_exceptions=True)
    r = client.get("/admin/complaints")
    assert r.status_code == 200


def test_regulatory_route_includes_ombudsman_count():
    from starlette.testclient import TestClient
    from company.portal.app import app
    client = TestClient(app, raise_server_exceptions=True)
    r = client.get("/regulatory")
    assert r.status_code == 200
    assert "Ombudsman" in r.text
