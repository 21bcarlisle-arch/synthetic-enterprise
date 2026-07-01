"""Phase 100: Switching recommendation engine tests."""

from datetime import date
from company.pricing.switching_recommendation import switching_recommendation, _cap_p_per_kwh


_BASE_CUSTOMER = {
    "customer_id": "C1",
    "segment": "resi",
    "contract_type": "fixed_1yr",
    "acquired_date": "2016-01-01",
}


def test_cap_p_per_kwh_2023():
    cap = _cap_p_per_kwh(2023)
    assert cap is not None
    assert 20.0 < cap < 50.0  # ballpark Ofgem 2023 cap range


def test_cap_p_per_kwh_pre_2019():
    assert _cap_p_per_kwh(2018) is None


def test_not_applicable_for_ic_customer():
    customer = {**_BASE_CUSTOMER, "segment": "IC"}
    result = switching_recommendation(customer)
    assert result["action"] == "not_applicable"


def test_fixed_protected_stays():
    rate_cmp = {"contracted_p": 10.0, "market_p": 20.0, "protected": True}
    pivot = date(2026, 6, 26)
    result = switching_recommendation(_BASE_CUSTOMER, rate_cmp, as_of=pivot)
    assert result["action"] == "stay"


def test_fixed_in_notice_window_and_protected():
    # Customer renewing in 10 days, protected — stay (renew fixed)
    customer = {**_BASE_CUSTOMER, "acquired_date": "2026-01-07"}  # end 2027-01-07
    pivot = date(2026, 12, 28)  # 10 days before renewal 2027-01-07
    rate_cmp = {"contracted_p": 10.0, "market_p": 25.0, "protected": True}
    result = switching_recommendation(customer, rate_cmp, as_of=pivot)
    assert result["action"] == "stay"
    assert result["urgency"] == "medium"


def test_fixed_in_notice_window_and_exposed():
    customer = {**_BASE_CUSTOMER, "acquired_date": "2026-01-07"}
    pivot = date(2026, 12, 28)
    rate_cmp = {"contracted_p": 25.0, "market_p": 15.0, "protected": False}
    result = switching_recommendation(customer, rate_cmp, as_of=pivot)
    assert result["action"] == "switch"
    assert result["urgency"] == "high"


def test_variable_customer_with_lower_market():
    customer = {**_BASE_CUSTOMER, "contract_type": "variable"}
    rate_cmp = {"contracted_p": 25.0, "market_p": 15.0, "protected": False}
    result = switching_recommendation(customer, rate_cmp)
    assert result["action"] == "switch"


def test_variable_customer_no_rate_cmp():
    customer = {**_BASE_CUSTOMER, "contract_type": "variable"}
    result = switching_recommendation(customer)
    assert result["action"] == "consider_switching"


def test_recommendation_has_required_fields():
    result = switching_recommendation(_BASE_CUSTOMER)
    assert "action" in result
    assert "reason" in result
    assert "urgency" in result


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


from company.pricing.switching_recommendation import _cap_p_per_kwh


def test_cap_p_per_kwh_2024():
    # 2024 should have a defined cap
    result = _cap_p_per_kwh(2024)
    assert result is not None
    assert result > 0


def test_cap_p_per_kwh_is_one_tenth_of_mwh_rate():
    from company.pricing.ofgem_price_cap import get_cap_unit_rate_gbp_per_mwh
    rate_mwh = get_cap_unit_rate_gbp_per_mwh("electricity", 2023)
    if rate_mwh is not None:
        assert _cap_p_per_kwh(2023) == round(rate_mwh / 10.0, 2)


def test_cap_p_per_kwh_2022_is_high():
    # 2022 energy crisis year: cap higher than 2020
    cap_2022 = _cap_p_per_kwh(2022)
    cap_2020 = _cap_p_per_kwh(2020)
    if cap_2022 is not None and cap_2020 is not None:
        assert cap_2022 > cap_2020
