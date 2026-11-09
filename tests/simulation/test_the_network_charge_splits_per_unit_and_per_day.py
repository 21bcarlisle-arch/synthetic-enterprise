"""W3_3: domestic electricity network cost is charged as Ofgem's cap model builds it.

The cap splits its network allowance (NC) into a per-kWh part, charged on volume, and a
nil-consumption part, charged per supply point per day and recovered through the standing charge.
Before this atom settlement charged the WHOLE allowance / 3.1 MWh on volume: right only at
exactly 3,100 kWh, and after the TCR (DUoS residual fixed from Apr 2022, TNUoS from Apr 2023) it
over-charged a high user by ~GBP 150/yr and under-charged a low one by ~GBP 70.
Knowledge: docs/market_research/network_charges_uk_2016_2024.md section 7d.

Each test names the defect it catches.
"""

import json
from pathlib import Path

import pytest

from simulation import policy_costs
from simulation.hedged_settlement import run_deemed_term, run_hedged_term
from simulation.policy_costs import (
    get_electricity_network_cost_per_mwh,
    get_electricity_network_fixed_per_day,
    get_electricity_standing_charge_per_day,
)

_ARTEFACT = (Path(__file__).resolve().parents[2] / "docs" / "domain_artefact_library"
             / "regulatory" / "ofgem_cap_network_allowance.json")


def _prices(day, price=60.0):
    return [{"settlementDate": day, "settlementPeriod": p, "systemSellPrice": price}
            for p in range(1, 49)]


def _hedged(day, kwh_per_period, *, segment="resi", pass_through=False):
    return run_hedged_term(
        customer_id="C1", term_start_date=day,
        term_end_date=f"{day[:8]}{int(day[8:]) + 1:02d}",
        fixed_tariff_rate_gbp_per_mwh=200.0, hedge_price_gbp_per_mwh=80.0, hedge_fraction=1.0,
        monthly_cost_of_capital_gbp=0.0, consumption_shape=lambda _d: [kwh_per_period] * 48,
        system_price_records=_prices(day), segment=segment, pass_through=pass_through,
    )


def test_the_split_can_be_taken_and_only_for_a_domestic_supply_point():
    """Catches a split that charges nothing fixed (every guard test passes) or charges SME/I&C
    the domestic nil allowance, which no commons table establishes for them."""
    day = "2024-06-01"
    assert get_electricity_network_fixed_per_day(day, "resi") > 0
    assert get_electricity_network_fixed_per_day(day, "SME") == 0.0
    assert get_electricity_network_fixed_per_day(day, "I&C") == 0.0


def test_a_domestic_day_with_no_consumption_still_bears_the_fixed_network_share():
    """Catches network charged on volume only: a nil-consumption day cost the supplier nothing."""
    rows = _hedged("2024-06-01", 0.0)
    assert len(rows) == 48
    total = sum(r["network_cost_gbp"] for r in rows)
    assert total == pytest.approx(get_electricity_network_fixed_per_day("2024-06-01"))


def test_the_deemed_writer_bears_the_fixed_share_too():
    """Catches the split landing in one writer of three."""
    rows = run_deemed_term("C1", "2024-06-01", "2024-06-02", 0.2, lambda _d: [0.0] * 48,
                           _prices("2024-06-01"))
    assert sum(r["network_cost_gbp"] for r in rows) == pytest.approx(
        get_electricity_network_fixed_per_day("2024-06-01"))


def test_network_cost_per_mwh_falls_with_consumption_after_the_tcr():
    """Catches the fixed share being charged on volume: per MWh, a low user must pay more."""
    def per_mwh(kwh_per_period):
        rows = _hedged("2024-06-01", kwh_per_period)
        return sum(r["network_cost_gbp"] for r in rows) / (kwh_per_period * 48 / 1000)

    low, high = per_mwh(1500 / 365 / 48), per_mwh(8000 / 365 / 48)
    assert low > high * 1.5, (low, high)


def test_pass_through_does_not_recover_the_fixed_share_twice():
    """Catches a pass-through tariff charging the fixed network on volume AND in the standing
    charge: on a nil-consumption day its revenue must be the standing charge alone."""
    day = "2024-06-01"
    rows = _hedged(day, 0.0, pass_through=True)
    assert sum(r["revenue_gbp"] for r in rows) == pytest.approx(
        get_electricity_standing_charge_per_day(day))


def test_at_the_benchmark_the_split_keeps_the_caps_annual_total():
    """Catches a split that loses (or double counts) part of the allowance: at 3,100 kWh a year
    the per-kWh part plus 365 days of the fixed part must match the pre-split whole-allowance
    table (NC benchmark / 3.1 MWh, from Annex 9) within 10% in every Apr-Mar year it covers."""
    for year, whole_per_mwh in policy_costs._NETWORK_COST_RESI_SME_BY_YEAR.items():
        day = f"{year}-06-01"
        split = (get_electricity_network_cost_per_mwh(day) * 3.1
                 + get_electricity_network_fixed_per_day(day) * 365)
        assert split == pytest.approx(whole_per_mwh * 3.1, rel=0.10), (year, split)


def test_the_tcr_moves_the_residual_into_the_fixed_share_on_its_published_dates():
    """Catches a split read on an Apr-Mar year or a calendar year: the DUoS residual step lands on
    1 April 2022 and the TNUoS step on 1 April 2023, and the per-kWh part does not rise with it."""
    fixed = get_electricity_network_fixed_per_day
    assert fixed("2022-04-01") > 4 * fixed("2022-03-31")
    assert fixed("2023-04-01") > fixed("2023-03-31")
    assert get_electricity_network_cost_per_mwh("2022-04-01") <= get_electricity_network_cost_per_mwh(
        "2022-03-31")


def test_the_artefact_has_no_hole_and_names_its_source():
    """Catches a period missing from the commons, which the reader would serve from the period
    before it without saying so."""
    doc = json.loads(_ARTEFACT.read_text())
    assert doc["source_check"]["version_token"] == "v1.31"
    periods = sorted(doc["periods"], key=lambda r: r["starts"])
    for prev, nxt in zip(periods, periods[1:]):
        assert nxt["starts"] <= prev["ends_before"], (prev["cap_period"], nxt["cap_period"])
