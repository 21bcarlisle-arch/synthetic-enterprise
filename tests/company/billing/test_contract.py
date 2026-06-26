"""Phase 95: Contract end date and renewal countdown tests."""

from datetime import date
from company.billing.contract import (
    contract_end_date, days_until_renewal, is_in_notice_window, renewal_summary
)
from starlette.testclient import TestClient
from company.portal.app import app

client = TestClient(app, raise_server_exceptions=True)

_PIVOT = date(2026, 6, 26)


def _customer(ct, acquired="2016-01-01"):
    return {"contract_type": ct, "acquired_date": acquired}


def test_fixed_1yr_next_renewal():
    # Acquired 2016-01-01, 1yr contract, pivot 2026-06-26 → next renewal 2027-01-01
    end = contract_end_date(_customer("fixed_1yr"), as_of=_PIVOT)
    assert end == date(2027, 1, 1)


def test_fixed_2yr_next_renewal():
    # Acquired 2016-01-01, 2yr contract → renewals 2018, 2020, 2022, 2024, 2026 (past), 2028
    end = contract_end_date(_customer("fixed_2yr"), as_of=_PIVOT)
    assert end == date(2028, 1, 1)


def test_variable_returns_none():
    assert contract_end_date(_customer("variable"), as_of=_PIVOT) is None


def test_svt_returns_none():
    assert contract_end_date(_customer("svt"), as_of=_PIVOT) is None


def test_days_until_fixed_1yr():
    days = days_until_renewal(_customer("fixed_1yr"), as_of=_PIVOT)
    assert days == (date(2027, 1, 1) - _PIVOT).days


def test_in_notice_window_false_for_distant():
    # 189 days away — not in 30-day window
    assert not is_in_notice_window(_customer("fixed_1yr"), as_of=_PIVOT)


def test_in_notice_window_true_when_close():
    # Acquired 2026-06-10 → next renewal 2027-06-10 (distant), so use a near pivot
    # Acquired 2016-01-01, pivot set to 2026-12-25 (7 days before 2027-01-01)
    near_pivot = date(2026, 12, 25)
    assert is_in_notice_window(_customer("fixed_1yr"), as_of=near_pivot)


def test_renewal_summary_structure():
    s = renewal_summary(_customer("fixed_1yr"), as_of=_PIVOT)
    assert s["is_fixed"] is True
    assert s["end_date"] is not None
    assert isinstance(s["days_until_renewal"], int)
    assert isinstance(s["in_notice_window"], bool)


def test_renewal_summary_variable():
    s = renewal_summary(_customer("variable"), as_of=_PIVOT)
    assert s["is_fixed"] is False
    assert s["end_date"] is None


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
