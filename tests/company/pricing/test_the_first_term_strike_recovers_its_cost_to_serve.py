"""A first-term fixed strike carries the share of the company's cost to serve that its unit rate must recover.

The defect each test names: `quote_first_term` struck on forward + capital + policy + network + £2 and
recovered no operating cost on the unit rate, so the 2023-24 quote sat 10-18% under the market's
cheapest fix by giving away cost (M2: value transferred, not created). Knowledge:
docs/market_research/cheapest_fix_against_the_default_tariff_gb_2016_2025.md §9 and §10.
"""
from __future__ import annotations

import datetime as dt

import pytest

import company.pricing.renewal_desk as rd
from company.crm.renewal_advice_desk import standing_charge_opex_per_year
from saas.cost_to_serve import fixed_overhead_gbp_per_year


def test_the_line_is_priced_for_both_resi_fuels_and_refused_outside_resi():
    """The partition first: a guard that refuses everything passes every refusal test."""
    elec = rd.first_term_operating_cost_per_mwh("resi", "electricity", "2023-07-01")
    gas = rd.first_term_operating_cost_per_mwh("resi", "gas", "2023-07-01")
    assert elec > 0 and gas > 0
    assert rd.first_term_operating_cost_per_mwh("SME", "electricity", "2023-07-01") is None
    assert rd.first_term_operating_cost_per_mwh("I&C", "gas", "2023-07-01") is None


@pytest.mark.parametrize("fuel", ["electricity", "gas"])
@pytest.mark.parametrize("day", ["2016-07-01", "2023-07-01", "2024-04-01", "2025-07-01", "2026-02-01",
                                 "2026-08-01"])
def test_a_benchmark_household_recovers_exactly_its_cost_to_serve(fuel, day):
    """The unit-rate share at the cap's benchmark volume, plus the standing charge's opex, is the year's
    cost to serve: no more, no less. Keyed to the identity, not to today's figure, so a new cost-to-serve
    row or a new benchmark basis keeps it green and a wrong divisor or a dropped credit turns it red."""
    kwh = dict(rd.FIRST_TERM_OPEX_BENCHMARK_KWH[fuel])
    basis = max(k for k in kwh if k <= day)
    line = rd.first_term_operating_cost_per_mwh("resi", fuel, day)
    recovered = line * kwh[basis] / 1000.0 + standing_charge_opex_per_year(fuel, day)
    assert recovered == pytest.approx(fixed_overhead_gbp_per_year("resi", fuel, day))


def _flat_history(price: float, start: str = "2015-11-01", end: str = "2025-06-01"):
    d, stop, rows = dt.date.fromisoformat(start), dt.date.fromisoformat(end), []
    while d <= stop:
        rows.append((d.isoformat(), 48, price))
        d += dt.timedelta(days=1)
    return rows


@pytest.mark.parametrize("segment", ["resi", "SME"])
def test_the_first_term_quote_carries_the_line_and_only_the_line(segment, monkeypatch):
    """The same prospect, the line on and off: the quote moves by exactly the line for resi, and not at
    all where there is no line."""
    def strike():
        return rd.quote_first_term(
            segment=segment, commodity="electricity", tariff_type="fixed", eac_kwh=2900,
            term_start="2018-06-01", observable_daily_prices=_flat_history(50.0),
            published_policy_cost_per_mwh=20.0, published_network_cost_per_mwh=30.0,
        )[2]

    with_line = strike()
    monkeypatch.setattr(rd, "first_term_operating_cost_per_mwh", lambda *a, **k: None)
    without = strike()
    expected = 0.0 if segment != "resi" else fixed_overhead_gbp_per_year(
        "resi", "electricity", "2018-06-01") / 3.1 - standing_charge_opex_per_year(
        "electricity", "2018-06-01") / 3.1
    assert with_line - without == pytest.approx(expected)
    if segment == "resi":
        assert with_line > without
