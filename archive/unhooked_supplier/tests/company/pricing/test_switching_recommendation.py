# ARCHIVED LEGS of tests/company/pricing/test_switching_recommendation.py (archive increment 4). The tests here reach a module
# under archive/unhooked_supplier/; the live legs stay at tests/company/pricing/test_switching_recommendation.py.
from datetime import date
from company.pricing.switching_recommendation import switching_recommendation, _cap_p_per_kwh
from company.pricing.switching_recommendation import _cap_p_per_kwh


def test_dashboard_route_returns_200():
    from starlette.testclient import TestClient
    from company.portal.app import app
    client = TestClient(app, raise_server_exceptions=True)
    r = client.get("/account/C1")
    assert r.status_code == 200


def test_dashboard_template_has_switch_widget():
    with open("company/portal/templates/dashboard.html") as f:
        html = f.read()
    assert "switch_rec" in html
    assert "Tariff advice" in html

