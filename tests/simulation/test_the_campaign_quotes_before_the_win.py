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


def _weekly_forward(price: float, first: str = "2021-02-08", last: str = "2025-06-02"):
    """One published row a week, `(knowable_from, GBP/MWh)`, at a flat price."""
    d, stop, rows = dt.date.fromisoformat(first), dt.date.fromisoformat(last), []
    while d <= stop:
        rows.append((d.isoformat(), price))
        d += dt.timedelta(days=7)
    return rows


def test_the_ladder_prices_only_where_it_is_whole_and_current():
    """The partition first: a ladder is struck, refused for a short series, refused for a stale one.
    A ladder that refuses everything passes every refusal test, so the priced leg is asserted too."""
    from company.pricing.renewal_desk import laddered_forward

    rows = _weekly_forward(80.0)
    whole = laddered_forward(rows, "2023-07-15")
    too_early = laddered_forward(rows, "2021-05-01")  # the series is under three months old
    ended = laddered_forward(rows, "2025-07-01")  # newest row four weeks stale
    assert whole == pytest.approx(80.0)
    assert too_early is None and ended is None


def test_the_ladder_is_the_mean_of_the_window_and_reads_nothing_after_the_day():
    from company.pricing.renewal_desk import laddered_forward

    rows = [(k, 100.0 if k > "2023-07-15" else (60.0 if k > "2023-04-15" else 40.0))
            for k, _ in _weekly_forward(0.0)]
    ladder = laddered_forward(rows, "2023-07-15", months=6)
    in_window = [p for k, p in rows if "2023-01-14" < k <= "2023-07-15"]
    assert ladder == pytest.approx(sum(in_window) / len(in_window))
    assert 40.0 < ladder < 60.0  # both halves weigh in; the later 100s do not


def test_a_fixed_first_term_is_struck_on_the_ladder_where_one_exists():
    """The same spot history, with and without the published forward: the strike moves with the
    ladder where it covers, and is untouched before the series does."""
    spot = _flat_history(60.0)

    def strike(day, forward):
        return quote_first_term(
            segment="resi", commodity="electricity", tariff_type="fixed", eac_kwh=2900,
            term_start=day, observable_daily_prices=spot,
            published_policy_cost_per_mwh=20.0, published_network_cost_per_mwh=30.0,
            observable_published_forward=forward,
        ).unit_rate_per_mwh

    cheap, dear = _weekly_forward(40.0), _weekly_forward(120.0)
    assert strike("2023-07-15", cheap) < strike("2023-07-15", None) < strike("2023-07-15", dear)
    assert strike("2018-07-15", dear) == strike("2018-07-15", None)


def test_the_world_hands_over_no_published_week_a_trader_could_not_yet_read():
    from sim.forward_curve import published_forward_knowable_by, published_forward_quote

    for day in ("2021-02-07", "2021-02-08", "2023-07-15", "2024-01-01"):
        rows = published_forward_knowable_by(day)
        assert all(k <= day for k, _ in rows)
        if published_forward_quote(day) is not None:
            assert rows and rows[-1][1] == published_forward_quote(day)
    assert published_forward_knowable_by("2021-02-07") == []
    assert len(published_forward_knowable_by("2023-07-15")) > 100
