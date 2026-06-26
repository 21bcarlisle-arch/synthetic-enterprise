"""Phase 85: Admin overview portal tests."""

from starlette.testclient import TestClient

from company.portal.app import app, _load_admin_data

client = TestClient(app, raise_server_exceptions=True)


def test_admin_route_returns_200():
    r = client.get("/admin")
    assert r.status_code == 200


def test_admin_shows_all_customers():
    r = client.get("/admin")
    from saas.customers import CUSTOMERS
    for c in CUSTOMERS:
        assert c["customer_id"] in r.text


def test_admin_shows_segment():
    r = client.get("/admin")
    assert "resi" in r.text or "SME" in r.text or "I&C" in r.text


def test_admin_shows_summary_cards():
    r = client.get("/admin")
    assert "Outstanding" in r.text
    assert "Active accounts" in r.text


def test_admin_shows_customer_links():
    r = client.get("/admin")
    assert "/account/C1" in r.text


def test_load_admin_data_structure():
    data = _load_admin_data()
    assert "customers" in data
    assert "total_customers" in data
    assert "total_outstanding_gbp" in data
    assert "total_bad_debt_gbp" in data


def test_load_admin_data_customer_count():
    from saas.customers import CUSTOMERS
    data = _load_admin_data()
    assert data["total_customers"] == len(CUSTOMERS)


def test_load_admin_data_each_customer_has_required_fields():
    data = _load_admin_data()
    for c in data["customers"]:
        assert "customer_id" in c
        assert "segment" in c
        assert "outstanding_gbp" in c
        assert "paid_gbp" in c
        assert "invoices" in c


def test_load_admin_data_financial_consistency():
    data = _load_admin_data()
    # Sum of per-customer outstanding must equal total
    per_cust_outstanding = sum(c["outstanding_gbp"] for c in data["customers"])
    assert abs(per_cust_outstanding - data["total_outstanding_gbp"]) < 0.01


def test_admin_template_has_smart_meter_column():
    with open("company/portal/templates/admin.html") as f:
        html = f.read()
    assert "smart_meter" in html or "Smart meter" in html


def test_admin_template_has_summary_cards():
    with open("company/portal/templates/admin.html") as f:
        html = f.read()
    assert "card" in html
    assert "Outstanding" in html
