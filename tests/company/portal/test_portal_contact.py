"""Phase 90: Contact Us form + ServiceEvent capture tests."""

from starlette.testclient import TestClient

from company.portal.app import app

client = TestClient(app, raise_server_exceptions=True)


def test_contact_route_returns_200():
    r = client.get("/account/C1/contact")
    assert r.status_code == 200


def test_contact_unknown_account_returns_404():
    r = client.get("/account/ZZZZ/contact")
    assert r.status_code == 404


def test_contact_shows_form():
    r = client.get("/account/C1/contact")
    assert "contact_reason" in r.text
    assert "notes" in r.text


def test_contact_post_shows_success():
    r = client.post(
        "/account/C1/contact",
        data={"contact_reason": "billing_query", "notes": "Test query"},
    )
    assert r.status_code == 200
    assert "received" in r.text or "submitted" in r.text.lower()


def test_contact_complaint_post_shows_complaint_message():
    r = client.post(
        "/account/C1/contact",
        data={"contact_reason": "complaint", "notes": "I am unhappy", "complaint": "yes"},
    )
    assert r.status_code == 200
    assert "complaint" in r.text.lower()


def test_contact_unknown_account_post_returns_404():
    r = client.post(
        "/account/ZZZZ/contact",
        data={"contact_reason": "general", "notes": ""},
    )
    assert r.status_code == 404


def test_contact_template_has_reason_dropdown():
    with open("company/portal/templates/contact.html") as f:
        html = f.read()
    assert "contact_reason" in html
    assert "billing_query" in html
    assert "complaint" in html


def test_contact_template_has_complaint_checkbox():
    with open("company/portal/templates/contact.html") as f:
        html = f.read()
    assert "formal complaint" in html
    assert "checkbox" in html or "type=\"checkbox\"" in html


def test_dashboard_has_contact_link():
    with open("company/portal/templates/dashboard.html") as f:
        html = f.read()
    assert "/contact" in html


def test_contact_records_service_event():
    from company.portal.app import _SERVICE_LOG
    initial = len(_SERVICE_LOG.all_contacts())
    client.post(
        "/account/C1/contact",
        data={"contact_reason": "general", "notes": "Phase 90 test"},
    )
    assert len(_SERVICE_LOG.all_contacts()) == initial + 1


def test_complaint_flag_set_correctly():
    from company.portal.app import _SERVICE_LOG
    initial = len(_SERVICE_LOG.complaints())
    client.post(
        "/account/C2/contact",
        data={"contact_reason": "complaint", "notes": "Bad service", "complaint": "yes"},
    )
    assert len(_SERVICE_LOG.complaints()) == initial + 1
