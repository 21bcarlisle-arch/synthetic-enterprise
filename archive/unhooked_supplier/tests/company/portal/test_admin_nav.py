"""Phase 102: Admin navigation / portal integration tests."""

from starlette.testclient import TestClient
from company.portal.app import app

client = TestClient(app, raise_server_exceptions=True)


def test_admin_has_complaints_link():
    r = client.get("/admin")
    assert r.status_code == 200
    assert "/admin/complaints" in r.text


def test_admin_has_collections_link():
    r = client.get("/admin")
    assert "/admin/collections" in r.text


def test_admin_has_renewals_link():
    r = client.get("/admin")
    assert "/admin/renewals" in r.text


def test_admin_complaints_reachable():
    r = client.get("/admin/complaints")
    assert r.status_code == 200


def test_admin_collections_reachable():
    r = client.get("/admin/collections")
    assert r.status_code == 200


def test_admin_renewals_reachable():
    r = client.get("/admin/renewals")
    assert r.status_code == 200


def test_admin_regulatory_link():
    r = client.get("/admin")
    assert "/regulatory" in r.text


def test_regulatory_reachable():
    r = client.get("/regulatory")
    assert r.status_code == 200


def test_trading_reachable():
    r = client.get("/trading")
    assert r.status_code == 200


def test_admin_template_has_nav_block():
    with open("company/portal/templates/admin.html") as f:
        html = f.read()
    assert "admin/complaints" in html
    assert "admin/collections" in html
    assert "admin/renewals" in html


def test_admin_has_trading_link():
    r = client.get("/admin")
    assert "/trading" in r.text or "Trading" in r.text


def test_admin_content_type_is_html():
    r = client.get("/admin")
    assert "text/html" in r.headers.get("content-type", "")


def test_admin_template_has_vulnerability_link():
    with open("company/portal/templates/admin.html") as f:
        html = f.read()
    assert "vulnerability" in html.lower()
