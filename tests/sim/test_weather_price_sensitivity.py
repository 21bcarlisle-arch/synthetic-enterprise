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
