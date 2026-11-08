# ARCHIVED LEGS of tests/company/billing/test_fuel_mix.py (archive increment 4). The tests here reach a module
# under archive/unhooked_supplier/; the live legs stay at tests/company/billing/test_fuel_mix.py.
import pytest
from company.billing.fuel_mix import get_fuel_mix, fuel_mix_summary


def test_regulatory_route_has_fuel_mix():
    from starlette.testclient import TestClient
    from company.portal.app import app
    client = TestClient(app, raise_server_exceptions=True)
    r = client.get("/regulatory")
    assert r.status_code == 200
    assert "Fuel Mix" in r.text


def test_regulatory_template_has_fuel_section():
    with open("company/portal/templates/regulatory.html") as f:
        html = f.read()
    assert "fuel_mix" in html
    assert "Renewable" in html

