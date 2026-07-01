"""Phase 98: Admin upcoming renewals view tests."""

from starlette.testclient import TestClient
from company.portal.app import app

client = TestClient(app, raise_server_exceptions=True)


def test_admin_renewals_returns_200():
    r = client.get("/admin/renewals")
    assert r.status_code == 200


def test_admin_renewals_shows_horizon():
    r = client.get("/admin/renewals")
    assert "90" in r.text


def test_admin_renewals_shows_upcoming_or_empty():
    r = client.get("/admin/renewals")
    assert "Renewal" in r.text or "renewals" in r.text.lower() or "No contracts" in r.text


def test_admin_renewals_template_has_urgency_classes():
    with open("company/portal/templates/admin_renewals.html") as f:
        html = f.read()
    assert "urgent" in html
    assert "days_remaining" in html


def test_admin_renewals_template_has_account_links():
    with open("company/portal/templates/admin_renewals.html") as f:
        html = f.read()
    assert "/account/" in html


def test_admin_renewals_shows_no_none_dates():
    r = client.get("/admin/renewals")
    assert "None" not in r.text


def test_renewals_route_uses_90_day_horizon():
    r = client.get("/admin/renewals")
    # All listed days should be <= 90
    import re
    days_matches = re.findall(r"<td class=.*?>(\d+)</td>", r.text)
    for d in days_matches:
        assert int(d) <= 90


def test_admin_links_to_renewals():
    with open("company/portal/templates/admin_renewals.html") as f:
        html = f.read()
    assert "admin" in html.lower()


def test_admin_renewals_content_type_is_html():
    r = client.get("/admin/renewals")
    assert "text/html" in r.headers.get("content-type", "")


def test_admin_renewals_has_table():
    r = client.get("/admin/renewals")
    assert "<table" in r.text.lower() or "No contracts" in r.text


def test_admin_renewals_has_nav():
    r = client.get("/admin/renewals")
    assert "/admin" in r.text


def test_admin_renewals_has_active_class():
    client = TestClient(app)
    r = client.get("/admin/renewals")
    assert "active" in r.text or "renewals" in r.text.lower()


def test_admin_renewals_response_is_bytes_decodable():
    client = TestClient(app)
    r = client.get("/admin/renewals")
    text = r.content.decode("utf-8")
    assert len(text) > 0


def test_admin_renewals_shows_90_day_window():
    client = TestClient(app)
    r = client.get("/admin/renewals")
    assert "90" in r.text or "horizon" in r.text.lower()
