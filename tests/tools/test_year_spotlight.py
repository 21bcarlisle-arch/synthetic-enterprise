"""Tests for Phase 261 Year Spotlight -- dashboard annual data completeness."""
import json
from pathlib import Path
import pytest


@pytest.fixture
def dash():
    p = Path("site/data/dashboard.json")
    if not p.exists():
        pytest.skip("dashboard.json not found")
    return json.loads(p.read_text())


def test_financial_annual_has_all_years(dash):
    years = [r["year"] for r in dash["financial"]["annual"]]
    for yr in range(2016, 2026):
        assert yr in years


def test_customers_book_annual_has_crisis_years(dash):
    years = [r["year"] for r in dash["customers"]["book_annual"]]
    assert 2021 in years
    assert 2022 in years


def test_book_annual_has_bill_shock_count(dash):
    row_2022 = next((r for r in dash["customers"]["book_annual"] if r["year"] == 2022), None)
    assert row_2022 is not None
    assert "bill_shock_count" in row_2022
    assert row_2022["bill_shock_count"] > 0


def test_trading_hedge_annual_has_all_years(dash):
    years = [r["year"] for r in dash["trading"]["hedge_annual"]]
    for yr in range(2016, 2026):
        assert yr in years


def test_crisis_year_2022_worse_than_2020(dash):
    ann = {r["year"]: r for r in dash["financial"]["annual"]}
    shocks_2022 = next((r["bill_shock_count"] for r in dash["customers"]["book_annual"] if r["year"] == 2022), 0)
    shocks_2020 = next((r["bill_shock_count"] for r in dash["customers"]["book_annual"] if r["year"] == 2020), 0)
    assert shocks_2022 >= shocks_2020



def test_financial_annual_includes_net_gbp(dash):
    for row in dash["financial"]["annual"]:
        assert "net_gbp" in row


def test_financial_annual_revenue_positive_all_years(dash):
    for row in dash["financial"]["annual"]:
        assert row["revenue_gbp"] > 0


def test_portfolio_has_bills_total(dash):
    assert "bills_total" in dash["portfolio"]
    assert dash["portfolio"]["bills_total"] > 0


def test_trading_spot_monthly_has_entries(dash):
    assert len(dash["trading"]["spot_monthly"]) > 0


def test_meta_has_generated_at(dash):
    assert "generated_at" in dash["meta"] or "generated_at" in str(dash.get("build", ""))


def test_financial_annual_has_10_years(dash):
    assert len(dash["financial"]["annual"]) == 10
