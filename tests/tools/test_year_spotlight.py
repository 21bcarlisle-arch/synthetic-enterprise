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


@pytest.mark.xfail(strict=True, reason=(
    "MEASURED FALSE, 2026-08-27, and recorded rather than tuned: docs/staging/done/"
    "WORKER_FINDING_THE_2022_CRISIS_IS_NOT_VISIBLE_IN_DOMESTIC_BILL_SHOCK_2026-08-27.md. "
    "THREE independent denominators agree that 2022 is not worse than 2020 on shock frequency "
    "-- per active account 3.57 vs 4.72, per active ELECTRICITY account 6.56 vs 8.57 (ruling "
    "out the dual-fuel gas legs, which dilute both years alike), and per BILL 0.366 vs 0.398, "
    "the denominator a shock actually belongs to and the one invariant to book size AND "
    "tenure. `avg_bill_shock_pct` agrees and drifts DOWN across the decade. "
    "THE WHOLESALE CRISIS IS REAL AND THE PRICE CAP STANDS BETWEEN IT AND A DOMESTIC BILL -- a "
    "capped tariff cannot pass a spike through when it happens, so a flat avg_bill_shock_pct "
    "across 2021-2023 is the cap working, not the world failing. "
    "R12 is why the metric was not normalised a fourth time until it passed, and R13 is why no "
    "world parameter was touched to make 2022 harsher. "
    "STRICT so an XPASS alarms: if 2022 ever does become the worse year, the cap modelling or "
    "the pass-through has changed and this seat wants telling."))
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


def test_bill_shock_stays_in_a_plausible_band_across_the_decade(dash):
    """THE CLAIM THAT REPLACES the 2022-vs-2020 one (2026-08-27).

    `test_crisis_year_2022_worse_than_2020` is xfail-strict against
    `docs/staging/done/WORKER_FINDING_THE_2022_CRISIS_IS_NOT_VISIBLE_IN_DOMESTIC_BILL_SHOCK_2026-08-27.md`:
    measured three ways, 2022 is simply not the worse year, and the reason is that a capped
    domestic tariff cannot pass a wholesale spike through at the moment it happens.

    Retiring a claim must not retire the COVERAGE. What the old assertion really stood guard
    over was that bill shock is a live, bounded quantity -- so that is asserted directly here,
    on every year rather than on two. A run where shock vanished (the company stopped billing,
    or the detector broke) or exploded (pass-through unbounded, the cap ignored) still reds.

    BOUNDS, NOT AN EQUALITY, and deliberately wide: the measured decade runs 0.35 to 0.46, and
    pinning that would make this a change-detector for the population draw -- the mistake this
    file already made once with a raw shock COUNT.
    """
    annual = {r["year"]: r for r in dash["financial"]["annual"]}
    measured = {y: r["avg_bill_shock_pct"] for y, r in annual.items()
                if r.get("avg_bill_shock_pct") is not None}
    assert len(measured) >= 8, "fewer than eight years carry a shock figure: {}".format(
        sorted(measured))
    for year, pct in sorted(measured.items()):
        assert 0.05 <= pct <= 5.0, (
            "{} average bill shock is {:.2f}% -- at the floor the detector or the billing has "
            "stopped, at the ceiling the price cap is no longer bounding pass-through"
            .format(year, pct))
