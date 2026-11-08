# ARCHIVED LEGS of tests/company/billing/test_carbon_footprint.py (archive increment 4). The tests here reach a module
# under archive/unhooked_supplier/; the live legs stay at tests/company/billing/test_carbon_footprint.py.
from company.billing.carbon_footprint import electricity_intensity, estimate_carbon, carbon_trend
from company.billing.carbon_footprint import electricity_intensity, estimate_carbon, _GAS_KG_CO2E_PER_KWH


def test_consumption_template_has_carbon():
    with open("company/portal/templates/consumption.html") as f:
        html = f.read()
    assert "carbon" in html
    assert "CO" in html


def test_consumption_route_returns_200():
    from starlette.testclient import TestClient
    from company.portal.app import app
    client = TestClient(app, raise_server_exceptions=True)
    r = client.get("/account/C1/consumption")
    assert r.status_code == 200

