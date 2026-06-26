"""Phase 86: Account statement tests."""

from starlette.testclient import TestClient

from company.portal.app import app

client = TestClient(app, raise_server_exceptions=True)


def test_statement_route_returns_200():
    r = client.get("/account/C1/statement")
    assert r.status_code == 200


def test_statement_unknown_account_returns_404():
    r = client.get("/account/ZZZZ/statement")
    assert r.status_code == 404


def test_statement_shows_account_id():
    r = client.get("/account/C1/statement")
    assert "C1" in r.text


def test_statement_shows_balance_section():
    r = client.get("/account/C1/statement")
    assert "Outstanding balance" in r.text or "balance" in r.text.lower()


def test_statement_shows_total_billed():
    r = client.get("/account/C1/statement")
    assert "Total billed" in r.text


def test_statement_shows_total_paid():
    r = client.get("/account/C1/statement")
    assert "Total paid" in r.text


def test_statement_has_print_button():
    r = client.get("/account/C1/statement")
    assert "Print" in r.text or "print" in r.text


def test_statement_template_has_balance_section():
    with open("company/portal/templates/statement.html") as f:
        html = f.read()
    assert "Outstanding balance" in html
    assert "Total billed" in html
    assert "Total paid" in html


def test_statement_template_has_print_css():
    with open("company/portal/templates/statement.html") as f:
        html = f.read()
    assert "@media print" in html


def test_dashboard_has_statement_link():
    with open("company/portal/templates/dashboard.html") as f:
        html = f.read()
    assert "/statement" in html


def test_bills_has_statement_link():
    with open("company/portal/templates/bills.html") as f:
        html = f.read()
    assert "/statement" in html
