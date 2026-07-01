import json
import pathlib
import pytest
from tools.generate_dashboard_data import extract_management_accounts


def _make_data(years_range=(2016, 2018), rev=500000.0, wholesale=300000.0,
               non_comm=50000.0, capital=20000.0, bad_debt=5000.0,
               cts=10000.0, fixed=15000.0, acq=8000.0):
    gross = rev - wholesale - non_comm
    total_opex = capital + bad_debt + cts + fixed + acq
    net = gross - total_opex
    ma = {}
    for yr in range(years_range[0], years_range[1] + 1):
        ma[str(yr)] = {"income_statement": {
            "revenue_gbp": rev,
            "wholesale_cost_gbp": wholesale,
            "non_commodity_cost_gbp": non_comm,
            "gross_margin_gbp": gross,
            "capital_cost_gbp": capital,
            "bad_debt_gbp": bad_debt,
            "cost_to_serve_gbp": cts,
            "fixed_cost_gbp": fixed,
            "acquisition_spend_gbp": acq,
            "total_opex_gbp": total_opex,
            "net_margin_gbp": net,
        }}
    return {"management_accounts": ma}


def test_extract_mgmt_accounts_keys():
    result = extract_management_accounts(_make_data())
    assert "annual" in result
    row = result["annual"][0]
    expected = ["year", "revenue_gbp", "wholesale_cost_gbp", "non_commodity_cost_gbp",
                "gross_margin_gbp", "capital_cost_gbp", "bad_debt_gbp",
                "cost_to_serve_gbp", "fixed_cost_gbp", "acquisition_spend_gbp",
                "total_opex_gbp", "net_margin_gbp", "net_margin_pct"]
    for k in expected:
        assert k in row, f"missing key: {k}"


def test_extract_mgmt_accounts_annual_length():
    data = _make_data(years_range=(2016, 2025))
    result = extract_management_accounts(data)
    assert len(result["annual"]) == 10


def test_extract_mgmt_accounts_years_ordered():
    data = _make_data(years_range=(2016, 2025))
    result = extract_management_accounts(data)
    years = [r["year"] for r in result["annual"]]
    assert years == list(range(2016, 2026))


def test_net_margin_pct_computed():
    data = _make_data(rev=1000000.0)
    result = extract_management_accounts(data)
    row = result["annual"][0]
    expected_pct = round(row["net_margin_gbp"] / row["revenue_gbp"] * 100, 2)
    assert abs(row["net_margin_pct"] - expected_pct) < 0.01


def test_empty_management_accounts():
    result = extract_management_accounts({})
    assert result == {"annual": []}


def test_zero_revenue_no_crash():
    data = {"management_accounts": {"2022": {"income_statement": {"revenue_gbp": 0}}}}
    result = extract_management_accounts(data)
    assert result["annual"][0]["net_margin_pct"] == 0.0


def test_revenue_positive():
    data = _make_data(years_range=(2016, 2025), rev=500000.0)
    result = extract_management_accounts(data)
    for row in result["annual"]:
        assert row["revenue_gbp"] > 0


def test_gross_margin_relationship():
    result = extract_management_accounts(_make_data())
    row = result["annual"][0]
    implied = row["revenue_gbp"] - row["wholesale_cost_gbp"] - row["non_commodity_cost_gbp"]
    assert abs(row["gross_margin_gbp"] - implied) < 1.0


def test_net_margin_positive_in_good_year():
    data = _make_data(rev=1000000.0, wholesale=400000.0)
    result = extract_management_accounts(data)
    assert result["annual"][0]["net_margin_gbp"] > 0


def test_mgmt_accounts_in_dashboard_json():
    rj = pathlib.Path("docs/reports/run_output_latest.json")
    if not rj.exists():
        pytest.skip("run_output_latest.json not present")
    from tools.generate_dashboard_data import generate
    ok = generate(rj)
    assert ok
    db = json.loads(pathlib.Path("site/data/dashboard.json").read_text())
    assert "management_accounts" in db
    assert len(db["management_accounts"]["annual"]) >= 1


def test_extract_mgmt_accounts_single_year():
    data = _make_data(years_range=(2022, 2022))
    result = extract_management_accounts(data)
    assert len(result["annual"]) == 1
    assert result["annual"][0]["year"] == 2022


def test_total_opex_positive():
    result = extract_management_accounts(_make_data())
    for row in result["annual"]:
        assert row.get("total_opex_gbp", 0) > 0


def test_net_margin_below_gross():
    result = extract_management_accounts(_make_data())
    row = result["annual"][0]
    assert row["net_margin_gbp"] < row["gross_margin_gbp"]
