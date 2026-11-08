# ARCHIVED LEGS of tests/company/crm/test_complaint_deadlines.py (archive increment 4). The tests here reach a module
# under archive/unhooked_supplier/; the live legs stay at tests/company/crm/test_complaint_deadlines.py.
from datetime import date, timedelta
from company.compliance.working_days import add_working_days as _add_working_days
from company.crm.service_log import ServiceLog, ServiceEvent
from starlette.testclient import TestClient
from company.portal.app import app


client = TestClient(app, raise_server_exceptions=True)


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

