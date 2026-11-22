"""The growth campaign asks the company for its quote before the world decides the win.

Finding `SEAT_FINDING_THE_FIRST_TERM_QUOTE_NEEDS_THE_MARKETS_PRICE_NOT_THE_CAP_...`, increment 2.
The offer either declines (no quote, nothing spent), prices the prospect against the market's
cheapest deal, or cannot read a position (None, so the funnel stays at the run level). One control
over the whole partition; then the direction the position moves in.
"""

from __future__ import annotations

import datetime as dt
from types import SimpleNamespace

import pytest

from company.interfaces.growth_desk import quote_first_term
from simulation.live_population import first_term_offer_fn, market_cheapest_ex_vat


def _flat_history(price: float, start: str = "2015-11-01", end: str = "2025-06-01"):
    """One row per day at a flat spot price: `(date, count, mean)`, 48 periods a day."""
    d, stop, rows = dt.date.fromisoformat(start), dt.date.fromisoformat(end), []
    while d <= stop:
        rows.append((d.isoformat(), 48, price))
        d += dt.timedelta(days=1)
    return rows


def _prospect(tariff_type=None, commodity="electricity"):
    return SimpleNamespace(segment="resi", commodity=commodity, tariff_type=tariff_type,
                           eac_kwh=2900.0)


def test_every_outcome_of_the_quote_is_reachable_and_tellable_apart():
    cheap = first_term_offer_fn(elec_daily=_flat_history(40.0), gas_daily=None)
    dear = first_term_offer_fn(elec_daily=_flat_history(400.0), gas_daily=None)
    priced = cheap(_prospect(), dt.date(2017, 6, 1))
    declined = dear(_prospect(), dt.date(2022, 3, 1))
    default_tariff = cheap(_prospect("svt"), dt.date(2017, 6, 1))
    no_gas_history = cheap(_prospect(commodity="gas"), dt.date(2017, 6, 1))

    assert priced["quoted"] and isinstance(priced["price_differential_pct"], float)
    assert declined["quoted"] is False and declined["reason"].startswith("cap_constrained")
    assert default_tariff is None and no_gas_history is None


def test_a_dearer_forward_reads_as_a_dearer_position_against_the_same_market():
    day = dt.date(2018, 6, 1)
    positions = [
        first_term_offer_fn(elec_daily=_flat_history(p), gas_daily=None)(_prospect(), day)
        ["price_differential_pct"]
        for p in (30.0, 50.0, 70.0)
    ]
    assert positions == sorted(positions) and positions[0] < positions[-1]


def test_the_company_without_a_forward_neither_quotes_a_rate_nor_declines():
    thin = [("2017-05-30", 5, 40.0)]  # five periods: under the engine's 30-record floor
    q = quote_first_term(
        segment="resi", commodity="electricity", tariff_type="fixed", eac_kwh=2900,
        term_start="2017-06-01", observable_daily_prices=thin,
        published_policy_cost_per_mwh=20.0, published_network_cost_per_mwh=30.0,
    )
    assert (q.quoted, q.reason, q.unit_rate_per_mwh) == (True, "no_forward", None)


@pytest.mark.parametrize("day", ["2016-06-01", "2020-06-01", "2024-06-01"])
def test_the_market_reference_sits_below_the_default_by_the_published_gap(day):
    from simulation.competitor_reference import best_deal_gap_share
    from simulation.price_cap_enforcement import DOMESTIC_VAT_RATE
    from simulation.svt_rates import get_svt_elec_rate_charged_to_household_gbp_per_mwh

    default_ex_vat = get_svt_elec_rate_charged_to_household_gbp_per_mwh(day) / (1 + DOMESTIC_VAT_RATE)
    assert market_cheapest_ex_vat("electricity", day) == pytest.approx(
        default_ex_vat * (1 - best_deal_gap_share(day)))
