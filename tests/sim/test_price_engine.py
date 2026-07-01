"""Tests for sim/price_engine.py -- Phase 3b merit-order price model."""

import pytest

from sim.price_engine import (
    GAMMA_MAX,
    GAMMA_MIN,
    THERMAL_EFFICIENCY,
    WIND_CUT_IN_MS,
    WIND_CUT_OUT_MS,
    WIND_RATED_MS,
    gas_floor_price,
    synthetic_price,
    system_margin_price,
    wind_power_output_fraction,
)


# --- gas_floor_price ---

def test_gas_floor_price_basic():
    # 50 GBP/MWh(th) at 50% efficiency -> 100 GBP/MWh(e)
    assert gas_floor_price(50.0, 0.50) == pytest.approx(100.0)


def test_gas_floor_price_default_efficiency():
    assert gas_floor_price(40.0) == pytest.approx(40.0 / THERMAL_EFFICIENCY)


def test_gas_floor_price_higher_efficiency_lower_cost():
    low_eff = gas_floor_price(50.0, 0.40)
    high_eff = gas_floor_price(50.0, 0.60)
    assert high_eff < low_eff


# --- system_margin_price ---

def test_system_margin_price_balanced_demand():
    # demand == renewable -> ratio=1 -> result == floor
    price = system_margin_price(100.0, 10_000.0, 10_000.0, gamma=2.0)
    assert price == pytest.approx(100.0)


def test_system_margin_price_tight_margin_raises():
    # demand >> renewable -> price spikes
    price = system_margin_price(100.0, 40_000.0, 10_000.0, gamma=2.0)
    assert price > 100.0


def test_system_margin_price_abundant_renewables_lowers():
    # demand << renewable -> price drops
    price = system_margin_price(100.0, 5_000.0, 20_000.0, gamma=2.0)
    assert price < 100.0


def test_system_margin_invalid_gamma_raises():
    with pytest.raises(ValueError):
        system_margin_price(100.0, 10_000.0, 10_000.0, gamma=0.5)


def test_system_margin_zero_renewable_raises():
    with pytest.raises(ValueError):
        system_margin_price(100.0, 10_000.0, 0.0, gamma=2.0)


# --- wind_power_output_fraction ---

def test_wind_below_cut_in_zero():
    assert wind_power_output_fraction(1.0) == pytest.approx(0.0)


def test_wind_above_cut_out_zero():
    assert wind_power_output_fraction(30.0) == pytest.approx(0.0)


def test_wind_at_rated_speed_full_output():
    assert wind_power_output_fraction(WIND_RATED_MS) == pytest.approx(1.0)


def test_wind_in_ramp_zone_between_zero_and_one():
    frac = wind_power_output_fraction(7.5)
    assert 0.0 < frac < 1.0


def test_wind_cubic_ramp_at_cut_in_zero():
    assert wind_power_output_fraction(WIND_CUT_IN_MS) == pytest.approx(0.0)


# --- synthetic_price ---

def test_synthetic_price_chains_floor_and_margin():
    floor = gas_floor_price(50.0)
    margin = system_margin_price(floor, 10_000.0, 10_000.0, 2.0)
    sp = synthetic_price(50.0, 10_000.0, 10_000.0, 2.0)
    assert sp == pytest.approx(margin)
