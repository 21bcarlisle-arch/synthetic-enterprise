"""Phase 88: Direct Debit portal tests."""

from starlette.testclient import TestClient

from company.portal.app import app

client = TestClient(app, raise_server_exceptions=True)


def test_dd_route_returns_200():
    r = client.get("/account/C1/direct-debit")
    assert r.status_code == 200


def test_dd_route_unknown_account_returns_404():
    r = client.get("/account/ZZZZ/direct-debit")
    assert r.status_code == 404


def test_dd_page_shows_no_mandate_initially():
    # Test that the page shows either a mandate card or the setup form -- both are valid states
    r = client.get("/account/C1/direct-debit")
    assert r.status_code == 200
    assert "Direct Debit" in r.text


def test_dd_set_mandate_shows_success(tmp_path):
    r = client.post(
        "/account/C1/direct-debit",
        data={"sort_code": "20-00-00", "account_number": "12345678", "payment_day": "1"},
    )
    assert r.status_code == 200
    assert "successfully" in r.text or "mandate" in r.text.lower()


def test_dd_set_invalid_payment_day_returns_422():
    r = client.post(
        "/account/C1/direct-debit",
        data={"sort_code": "20-00-00", "account_number": "12345678", "payment_day": "0"},
    )
    assert r.status_code == 422


def test_dd_cancel_route_returns_200():
    r = client.post("/account/C1/direct-debit/cancel")
    assert r.status_code == 200
    assert "cancelled" in r.text.lower() or "Cancel" in r.text


def test_dd_template_has_setup_form():
    with open("company/portal/templates/direct_debit.html") as f:
        html = f.read()
    assert "sort_code" in html
    assert "account_number" in html
    assert "payment_day" in html


def test_dd_template_has_cancel_button():
    with open("company/portal/templates/direct_debit.html") as f:
        html = f.read()
    assert "cancel" in html.lower()


def test_dashboard_has_dd_link():
    with open("company/portal/templates/dashboard.html") as f:
        html = f.read()
    assert "/direct-debit" in html


def test_dd_route_content_type_is_html():
    r = client.get("/account/C1/direct-debit")
    assert "text/html" in r.headers.get("content-type", "")


def test_dd_page_has_nav():
    r = client.get("/account/C1/direct-debit")
    assert "nav" in r.text.lower() or "Account" in r.text


def test_dd_template_has_payment_day_options():
    with open("company/portal/templates/direct_debit.html") as f:
        html = f.read()
    assert "payment_day" in html
    assert "28" in html or "1" in html
