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
    """D3 Expert-Hour finding (2026-07-12): compares ORGANIC (market/
    consumption-driven) shocks, not the raw bill_shock_count -- a real
    account-closure catch-up correction is a genuine shock but lands in
    whatever year that customer happens to churn, independent of whether the
    market itself was in crisis that year. Confirmed by direct diagnosis: the
    raw count flips this comparison in exactly 2 cases (C3/C5's own account-
    closure catch-up bills landing in calm-year 2020), which is precisely the
    confound organic_bill_shock_count exists to exclude.

    SECOND CONFOUND FOUND AND FIXED (W2_5_life_event_stream, 2026-07-13):
    adding real illness/divorce economic events (simulation/life_events.py)
    legitimately shifted per-customer churn timing (a real, expected
    consequence of adding new baseline-fidelity stochastic draws to a shared
    RNG stream -- R13), which changes how many customers are ACTIVE in the
    book in a given year independent of market severity. Confirmed by direct
    diagnosis: a fresh run showed 18 active accounts in 2020 vs 13 in 2022 --
    a real, legitimate population-composition difference this run produced,
    which flips a RAW organic-shock-count comparison even though the
    underlying per-customer crisis severity relationship still holds. Fixed
    by comparing the organic shock RATE per active account (organic count /
    active accounts) rather than the raw count -- robust to population-size
    differences between years, which are a genuine, expected feature of this
    project's own churn-timing model, not a bug to suppress."""
    ann = {r["year"]: r for r in dash["financial"]["annual"]}
    book = {r["year"]: r for r in dash["customers"]["book_annual"]}
    row_2022, row_2020 = book[2022], book[2020]
    active_2022 = row_2022["active_elec"] + row_2022["active_gas"]
    active_2020 = row_2020["active_elec"] + row_2020["active_gas"]
    rate_2022 = row_2022["organic_bill_shock_count"] / active_2022
    rate_2020 = row_2020["organic_bill_shock_count"] / active_2020
    assert rate_2022 >= rate_2020



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


def test_book_annual_all_rows_have_year(dash):
    for row in dash["customers"]["book_annual"]:
        assert "year" in row


def test_operations_monthly_has_is_crisis_key(dash):
    if dash.get("operations") and dash["operations"].get("monthly"):
        for row in dash["operations"]["monthly"][:5]:
            assert "is_crisis" in row


def test_trading_hedge_annual_has_hf_key(dash):
    for row in dash["trading"]["hedge_annual"]:
        assert "avg_hf" in row
