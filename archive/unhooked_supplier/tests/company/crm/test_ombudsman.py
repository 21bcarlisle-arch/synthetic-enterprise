# ARCHIVED LEGS of tests/company/crm/test_ombudsman.py (archive increment 4). The tests here reach a module
# under archive/unhooked_supplier/; the live legs stay at tests/company/crm/test_ombudsman.py.
from datetime import date, timedelta
from company.crm.service_log import ServiceLog, ServiceEvent


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

