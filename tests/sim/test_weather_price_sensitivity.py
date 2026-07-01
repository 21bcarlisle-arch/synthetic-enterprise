import pytest

from sim.weather_price_sensitivity import (
    COLD_SPELL_PRICE_MULTIPLIER,
    average_heating_degree_days,
    weather_sensitivity_multiplier,
)


def test_average_heating_degree_days_basic():
    # HEATING_BASE_TEMP_C is 15.5; HDD = max(0, 15.5 - temp)
    temps = [15.5, 10.5, 5.5]  # HDD = 0, 5, 10 -> mean 5
    assert average_heating_degree_days(temps) == pytest.approx(5.0)


def test_average_heating_degree_days_empty_raises():
    with pytest.raises(ValueError):
        average_heating_degree_days([])


def test_no_multiplier_for_mild_lookback_window():
    mild_temps = [10.0] * 90  # HDD = 5.5, below threshold
    assert weather_sensitivity_multiplier(mild_temps) == 1.0


def test_cold_spell_multiplier_applied():
    cold_temps = [0.0] * 90  # HDD = 15.5, above threshold
    assert weather_sensitivity_multiplier(cold_temps) == COLD_SPELL_PRICE_MULTIPLIER


from sim.weather_price_sensitivity import (
    COLD_SPELL_HDD_THRESHOLD,
    BASELINE_HEATING_DEGREE_DAYS,
)


def test_hdd_threshold_constant():
    assert COLD_SPELL_HDD_THRESHOLD == 8.0


def test_baseline_hdd_constant():
    assert BASELINE_HEATING_DEGREE_DAYS == 5.5


def test_cold_spell_price_multiplier_constant():
    assert COLD_SPELL_PRICE_MULTIPLIER == pytest.approx(1.10)


def test_hdd_zero_above_base_temp():
    temps = [20.0, 25.0, 30.0]
    assert average_heating_degree_days(temps) == 0.0


def test_hdd_very_cold_temp():
    result = average_heating_degree_days([-10.0])
    assert result == pytest.approx(15.5 - (-10.0))


def test_hdd_boundary_at_threshold_no_multiplier():
    boundary_temp = 15.5 - COLD_SPELL_HDD_THRESHOLD
    assert weather_sensitivity_multiplier([boundary_temp] * 90) == 1.0


def test_hdd_just_above_threshold_applies_multiplier():
    above_temp = 15.5 - COLD_SPELL_HDD_THRESHOLD - 0.1
    assert weather_sensitivity_multiplier([above_temp] * 90) == COLD_SPELL_PRICE_MULTIPLIER


def test_known_mixed_temps():
    temps = [15.5, 10.5, 5.5]
    result = average_heating_degree_days(temps)
    assert result == pytest.approx(5.0)


def test_single_warm_day_no_multiplier():
    assert weather_sensitivity_multiplier([20.0]) == 1.0
