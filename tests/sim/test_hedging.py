"""Tests for sim/hedging.py -- Phase 1d hedge economics."""

import pytest

from sim.hedging import settle_hedged_period


def _settle(
    consumption_kwh=1000.0,
    tariff=100.0,
    hedge_price=80.0,
    hedge_fraction=0.5,
    spot=90.0,
):
    return settle_hedged_period(
        consumption_kwh=consumption_kwh,
        fixed_tariff_rate_gbp_per_mwh=tariff,
        hedge_price_gbp_per_mwh=hedge_price,
        hedge_fraction=hedge_fraction,
        spot_price_gbp_per_mwh=spot,
    )


def test_all_keys_present():
    result = _settle()
    assert set(result.keys()) == {
        "hedged_volume_kwh", "unhedged_volume_kwh",
        "revenue_gbp", "wholesale_cost_gbp", "margin_gbp",
    }


def test_revenue_from_tariff():
    # 1000 kWh / 1000 * £100/MWh = £100
    result = _settle(consumption_kwh=1000.0, tariff=100.0)
    assert result["revenue_gbp"] == pytest.approx(100.0)


def test_fully_hedged_no_spot_exposure():
    # When fully hedged, spot price should not affect wholesale cost
    r1 = settle_hedged_period(1000.0, 100.0, 80.0, 1.0, spot_price_gbp_per_mwh=60.0)
    r2 = settle_hedged_period(1000.0, 100.0, 80.0, 1.0, spot_price_gbp_per_mwh=500.0)
    assert r1["wholesale_cost_gbp"] == pytest.approx(r2["wholesale_cost_gbp"])


def test_fully_naked_no_hedge_exposure():
    # When fully naked, hedge price should not affect wholesale cost
    r1 = settle_hedged_period(1000.0, 100.0, 50.0, 0.0, spot_price_gbp_per_mwh=90.0)
    r2 = settle_hedged_period(1000.0, 100.0, 999.0, 0.0, spot_price_gbp_per_mwh=90.0)
    assert r1["wholesale_cost_gbp"] == pytest.approx(r2["wholesale_cost_gbp"])


def test_fully_hedged_wholesale_cost():
    # 1000 kWh at hedge_price=80 -> 1000/1000 * 80 = £80
    result = settle_hedged_period(1000.0, 100.0, 80.0, 1.0, 90.0)
    assert result["wholesale_cost_gbp"] == pytest.approx(80.0)


def test_fully_naked_wholesale_cost():
    # 1000 kWh at spot=90 -> £90
    result = settle_hedged_period(1000.0, 100.0, 80.0, 0.0, 90.0)
    assert result["wholesale_cost_gbp"] == pytest.approx(90.0)


def test_margin_equals_revenue_minus_cost():
    result = _settle()
    assert result["margin_gbp"] == pytest.approx(
        result["revenue_gbp"] - result["wholesale_cost_gbp"]
    )


def test_hedged_volume_split():
    result = settle_hedged_period(1000.0, 100.0, 80.0, 0.4, 90.0)
    assert result["hedged_volume_kwh"] == pytest.approx(400.0)
    assert result["unhedged_volume_kwh"] == pytest.approx(600.0)


def test_zero_consumption_all_zeros():
    result = settle_hedged_period(0.0, 100.0, 80.0, 0.5, 90.0)
    assert result["revenue_gbp"] == pytest.approx(0.0)
    assert result["wholesale_cost_gbp"] == pytest.approx(0.0)
    assert result["margin_gbp"] == pytest.approx(0.0)


def test_high_spot_naked_negative_margin():
    # tariff=50, spot=200 -> revenue 50 but cost 200 per MWh -> loss
    result = settle_hedged_period(1000.0, 50.0, 40.0, 0.0, 200.0)
    assert result["margin_gbp"] < 0.0


def test_hedging_reduces_spot_exposure():
    # Spot spikes: fully hedged should have better margin than fully naked
    r_hedged = settle_hedged_period(1000.0, 100.0, 60.0, 1.0, 200.0)
    r_naked = settle_hedged_period(1000.0, 100.0, 60.0, 0.0, 200.0)
    assert r_hedged["margin_gbp"] > r_naked["margin_gbp"]


def test_partial_hedge_intermediate_margin():
    r_full = settle_hedged_period(1000.0, 100.0, 60.0, 1.0, 200.0)
    r_half = settle_hedged_period(1000.0, 100.0, 60.0, 0.5, 200.0)
    r_none = settle_hedged_period(1000.0, 100.0, 60.0, 0.0, 200.0)
    assert r_none["margin_gbp"] < r_half["margin_gbp"] < r_full["margin_gbp"]
