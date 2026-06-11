import pytest

from sim.price_engine import (
    THERMAL_EFFICIENCY,
    WIND_CUT_IN_MS,
    WIND_CUT_OUT_MS,
    WIND_RATED_MS,
    gas_floor_price,
    synthetic_price,
    system_margin_price,
    wind_power_output_fraction,
)


def test_gas_floor_price_default_efficiency():
    assert gas_floor_price(25.0) == 25.0 / THERMAL_EFFICIENCY


def test_gas_floor_price_custom_efficiency():
    assert gas_floor_price(30.0, thermal_efficiency=0.60) == 50.0


def test_system_margin_price_at_unity_ratio_returns_floor():
    floor = 50.0
    assert system_margin_price(floor, demand_mw=1000, renewable_generation_mw=1000, gamma=2.0) == floor


def test_system_margin_price_increases_with_tighter_margin():
    floor = 50.0
    loose = system_margin_price(floor, demand_mw=1000, renewable_generation_mw=2000, gamma=2.0)
    tight = system_margin_price(floor, demand_mw=2000, renewable_generation_mw=1000, gamma=2.0)
    assert tight > floor > loose


def test_system_margin_price_higher_gamma_amplifies_tight_margin():
    floor = 50.0
    demand_mw, renewable_mw = 2000, 1000
    low_gamma = system_margin_price(floor, demand_mw, renewable_mw, gamma=1.5)
    high_gamma = system_margin_price(floor, demand_mw, renewable_mw, gamma=2.5)
    assert high_gamma > low_gamma > floor


def test_system_margin_price_rejects_gamma_out_of_range():
    with pytest.raises(ValueError):
        system_margin_price(50.0, 1000, 1000, gamma=1.0)
    with pytest.raises(ValueError):
        system_margin_price(50.0, 1000, 1000, gamma=3.0)


def test_system_margin_price_rejects_zero_renewable_generation():
    with pytest.raises(ValueError):
        system_margin_price(50.0, demand_mw=1000, renewable_generation_mw=0, gamma=2.0)


def test_wind_power_below_cut_in_is_zero():
    assert wind_power_output_fraction(WIND_CUT_IN_MS - 0.1, rated_power_mw=10) == 0.0


def test_wind_power_at_cut_in_is_zero():
    assert wind_power_output_fraction(WIND_CUT_IN_MS, rated_power_mw=10) == 0.0


def test_wind_power_at_rated_speed_is_full_output():
    assert wind_power_output_fraction(WIND_RATED_MS, rated_power_mw=10) == 10


def test_wind_power_in_rated_plateau_is_full_output():
    assert wind_power_output_fraction(20.0, rated_power_mw=10) == 10


def test_wind_power_at_cut_out_is_still_full_output():
    assert wind_power_output_fraction(WIND_CUT_OUT_MS, rated_power_mw=10) == 10


def test_wind_power_above_cut_out_is_zero():
    assert wind_power_output_fraction(WIND_CUT_OUT_MS + 0.1, rated_power_mw=10) == 0.0


def test_wind_power_ramp_is_cubic_and_monotonic():
    p1 = wind_power_output_fraction(5.0, rated_power_mw=10)
    p2 = wind_power_output_fraction(8.0, rated_power_mw=10)
    p3 = wind_power_output_fraction(11.0, rated_power_mw=10)
    assert 0 < p1 < p2 < p3 < 10

    # Doubling from 5 -> 10 m/s within the ramp should roughly 8x the
    # fractional output (cubic), modulo the cut-in offset.
    expected_p1 = ((5.0**3 - WIND_CUT_IN_MS**3) / (WIND_RATED_MS**3 - WIND_CUT_IN_MS**3)) * 10
    assert p1 == pytest.approx(expected_p1)


def test_synthetic_price_chains_gas_floor_and_margin():
    gas_price = 25.0
    demand_mw, renewable_mw, gamma = 1500, 1000, 2.0
    expected_floor = gas_floor_price(gas_price)
    expected = system_margin_price(expected_floor, demand_mw, renewable_mw, gamma)
    assert synthetic_price(gas_price, demand_mw, renewable_mw, gamma) == expected
