# ARCHIVED LEGS of tests/company/crm/test_csat.py (archive increment 4). The tests here reach a module
# under archive/unhooked_supplier/; the live legs stay at tests/company/crm/test_csat.py.
from company.crm.service_log import ServiceLog, ServiceEvent


def test_contact_success_page_has_csat_widget():
    with open("company/portal/templates/contact.html") as f:
        html = f.read()
    assert "csat" in html.lower() or "rating" in html.lower()
    assert "/contact/rate" in html


def test_contact_route_returns_contact_id():
    from starlette.testclient import TestClient
    from company.portal.app import app
    client = TestClient(app, raise_server_exceptions=True)
    r = client.post("/account/C1/contact", data={
        "contact_reason": "general",
        "notes": "test csat",
        "complaint": "",
    })
    assert r.status_code == 200
    assert "contact/rate" in r.text


def test_csat_rate_route_accepts_score():
    from starlette.testclient import TestClient
    from company.portal.app import app, _SERVICE_LOG
    client = TestClient(app, raise_server_exceptions=True)
    # First submit a contact
    client.post("/account/C1/contact", data={
        "contact_reason": "billing_query", "notes": "", "complaint": ""})
    cid = _SERVICE_LOG.latest_contact_id("C1")
    assert cid is not None
    r = client.post("/account/C1/contact/rate", data={"contact_id": str(cid), "score": "5"})
    assert r.status_code == 200

