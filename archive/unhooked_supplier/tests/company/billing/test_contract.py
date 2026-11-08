# ARCHIVED LEGS of tests/company/billing/test_contract.py (archive increment 4). The tests here reach a module
# under archive/unhooked_supplier/; the live legs stay at tests/company/billing/test_contract.py.
from datetime import date
from company.billing.contract import (
    contract_end_date, days_until_renewal, is_in_notice_window, renewal_summary
)
from starlette.testclient import TestClient
from company.portal.app import app


client = TestClient(app, raise_server_exceptions=True)


def test_dashboard_renders_for_fixed_customer():
    r = client.get("/account/C1")
    assert r.status_code == 200
    # C1 is fixed_1yr — should see contract renewal info
    assert "renewal" in r.text.lower() or "Contract" in r.text


def test_dashboard_template_has_renewal_block():
    with open("company/portal/templates/dashboard.html") as f:
        html = f.read()
    assert "renewal" in html
    assert "days_until_renewal" in html or "days" in html

