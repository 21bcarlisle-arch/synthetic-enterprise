"""Tests for simulation/volume_tolerance.py -- Phase 27c."""

import pytest

from simulation.volume_tolerance import (
    VOLUME_TOLERANCE_FRACTION,
    compute_term_volume_tolerance,
)


def test_tolerance_fraction_is_ten_pct():
    assert VOLUME_TOLERANCE_FRACTION == 0.10


def test_within_band_exact_contracted():
    result = compute_term_volume_tolerance(
        actual_kwh=100_000.0,
        contracted_kwh=100_000.0,
        avg_spot_gbp_per_mwh=60.0,
        hedge_price_gbp_per_mwh=55.0,
        hedge_fraction=0.5,
    )
    assert result["within_band"] is True
    assert result["excess_kwh"] == 0.0
    assert result["deficit_kwh"] == 0.0


def test_within_band_plus_five_pct():
    result = compute_term_volume_tolerance(
        actual_kwh=105_000.0,
        contracted_kwh=100_000.0,
        avg_spot_gbp_per_mwh=60.0,
        hedge_price_gbp_per_mwh=55.0,
        hedge_fraction=0.5,
    )
    assert result["within_band"] is True
    assert result["excess_kwh"] == 0.0


def test_within_band_minus_five_pct():
    result = compute_term_volume_tolerance(
        actual_kwh=95_000.0,
        contracted_kwh=100_000.0,
        avg_spot_gbp_per_mwh=60.0,
        hedge_price_gbp_per_mwh=55.0,
        hedge_fraction=0.5,
    )
    assert result["within_band"] is True
    assert result["deficit_kwh"] == 0.0


def test_excess_above_band():
    result = compute_term_volume_tolerance(
        actual_kwh=115_000.0,
        contracted_kwh=100_000.0,
        avg_spot_gbp_per_mwh=60.0,
        hedge_price_gbp_per_mwh=55.0,
        hedge_fraction=0.5,
    )
    assert result["within_band"] is False
    assert result["excess_kwh"] == 5_000.0
    assert result["deficit_kwh"] == 0.0


def test_deficit_below_band():
    result = compute_term_volume_tolerance(
        actual_kwh=85_000.0,
        contracted_kwh=100_000.0,
        avg_spot_gbp_per_mwh=60.0,
        hedge_price_gbp_per_mwh=55.0,
        hedge_fraction=0.5,
    )
    assert result["within_band"] is False
    assert result["deficit_kwh"] == 5_000.0
    assert result["excess_kwh"] == 0.0


def test_band_high_equals_contracted_plus_ten_pct():
    result = compute_term_volume_tolerance(
        actual_kwh=100_000.0,
        contracted_kwh=100_000.0,
        avg_spot_gbp_per_mwh=60.0,
        hedge_price_gbp_per_mwh=55.0,
        hedge_fraction=0.5,
    )
    assert result["band_high_kwh"] == pytest.approx(110_000.0)


def test_band_low_equals_contracted_minus_ten_pct():
    result = compute_term_volume_tolerance(
        actual_kwh=100_000.0,
        contracted_kwh=100_000.0,
        avg_spot_gbp_per_mwh=60.0,
        hedge_price_gbp_per_mwh=55.0,
        hedge_fraction=0.5,
    )
    assert result["band_low_kwh"] == pytest.approx(90_000.0)


def test_excess_spot_cost_computed():
    # excess 5000 kWh at spot £60/MWh = 5000/1000 * 60 = £300
    result = compute_term_volume_tolerance(
        actual_kwh=115_000.0,
        contracted_kwh=100_000.0,
        avg_spot_gbp_per_mwh=60.0,
        hedge_price_gbp_per_mwh=55.0,
        hedge_fraction=1.0,
    )
    assert result["excess_spot_cost_gbp"] == pytest.approx(300.0)


def test_deficit_unwind_spot_above_hedge_positive():
    # spot(70) > hedge(55): unwind is profitable
    # deficit=10000, hedge_fraction=0.5 -> hedged_deficit=5000
    # unwind = 5000 * (70-55) / 1000 = 5000*15/1000 = 75.0
    result = compute_term_volume_tolerance(
        actual_kwh=80_000.0,
        contracted_kwh=100_000.0,
        avg_spot_gbp_per_mwh=70.0,
        hedge_price_gbp_per_mwh=55.0,
        hedge_fraction=0.5,
    )
    assert result["deficit_kwh"] == pytest.approx(10_000.0)
    assert result["deficit_unwind_gbp"] == pytest.approx(75.0)


def test_deficit_unwind_spot_below_hedge_negative():
    # spot(40) < hedge(55): unwind is a loss
    result = compute_term_volume_tolerance(
        actual_kwh=80_000.0,
        contracted_kwh=100_000.0,
        avg_spot_gbp_per_mwh=40.0,
        hedge_price_gbp_per_mwh=55.0,
        hedge_fraction=1.0,
    )
    assert result["deficit_unwind_gbp"] < 0.0


def test_zero_contracted_returns_zero_variance():
    result = compute_term_volume_tolerance(
        actual_kwh=0.0,
        contracted_kwh=0.0,
        avg_spot_gbp_per_mwh=60.0,
        hedge_price_gbp_per_mwh=55.0,
        hedge_fraction=0.5,
    )
    assert result["variance_pct"] == 0.0


def test_variance_pct_computed():
    # actual=115k, contracted=100k -> +15%
    result = compute_term_volume_tolerance(
        actual_kwh=115_000.0,
        contracted_kwh=100_000.0,
        avg_spot_gbp_per_mwh=60.0,
        hedge_price_gbp_per_mwh=55.0,
        hedge_fraction=0.5,
    )
    assert result["variance_pct"] == pytest.approx(15.0)


def test_all_keys_present():
    result = compute_term_volume_tolerance(
        actual_kwh=100_000.0,
        contracted_kwh=100_000.0,
        avg_spot_gbp_per_mwh=60.0,
        hedge_price_gbp_per_mwh=55.0,
        hedge_fraction=0.5,
    )
    expected_keys = {
        "contracted_kwh", "actual_kwh", "variance_pct",
        "band_high_kwh", "band_low_kwh", "excess_kwh", "deficit_kwh",
        "excess_spot_cost_gbp", "deficit_unwind_gbp", "within_band",
    }
    assert set(result.keys()) == expected_keys


def test_boundary_exactly_at_band_high():
    # actual == band_high => within_band
    result = compute_term_volume_tolerance(
        actual_kwh=110_000.0,
        contracted_kwh=100_000.0,
        avg_spot_gbp_per_mwh=60.0,
        hedge_price_gbp_per_mwh=55.0,
        hedge_fraction=0.5,
    )
    assert result["within_band"] is True
    assert result["excess_kwh"] == 0.0
