import numpy as np
import pytest

from sim.weather_engine import (
    MACRO_VARS,
    PERIODS_PER_DAY,
    TEMP_PEAK_PERIOD,
    TEMP_TROUGH_PERIOD,
    clear_sky_irradiance,
    diurnal_temperature_shape,
    fit_national_macro_model,
    fit_regional_cholesky,
    fit_seasonal_harmonics,
    fit_temperature_range_model,
    half_hourly_solar_irradiance,
    half_hourly_temperature,
    seasonal_value,
    simulate_national_macro,
    simulate_regional_deviations,
    simulate_temperature_range,
    simulate_wind_half_hourly,
)


def test_seasonal_harmonics_recovers_known_sinusoid():
    doy = np.arange(1, 366, dtype=float)
    omega = 2 * np.pi / 365.25
    values = 10.0 + 5.0 * np.cos(omega * doy)
    coeffs = fit_seasonal_harmonics(values, doy)
    fitted = seasonal_value(coeffs, doy)
    assert fitted == pytest.approx(values, abs=1e-6)


def test_diurnal_temperature_shape_peak_and_trough():
    assert diurnal_temperature_shape(TEMP_PEAK_PERIOD) == pytest.approx(1.0)
    assert diurnal_temperature_shape(TEMP_TROUGH_PERIOD) == pytest.approx(-1.0)


def test_half_hourly_temperature_bounds_at_peak_and_trough():
    daily_min, daily_max = 5.0, 15.0
    peak = half_hourly_temperature(daily_min, daily_max, TEMP_PEAK_PERIOD)
    trough = half_hourly_temperature(daily_min, daily_max, TEMP_TROUGH_PERIOD)
    mean = (daily_min + daily_max) / 2
    assert peak > mean > trough


def test_clear_sky_irradiance_zero_at_night_positive_at_noon():
    night = clear_sky_irradiance(day_of_year=172, period=0, latitude_deg=51.5)  # midnight
    noon = clear_sky_irradiance(day_of_year=172, period=24, latitude_deg=51.5)  # 12:00
    assert night == 0.0
    assert noon > 0.0


def test_half_hourly_solar_irradiance_cloud_attenuation():
    clear = half_hourly_solar_irradiance(172, 24, 51.5, cloud_cover_pct=0.0)
    cloudy = half_hourly_solar_irradiance(172, 24, 51.5, cloud_cover_pct=100.0)
    assert cloudy < clear
    assert cloudy >= 0.0


def test_simulate_wind_half_hourly_is_nonnegative_and_correct_length():
    rng = np.random.default_rng(0)
    series = simulate_wind_half_hourly(daily_mean_wind_ms=5.0, rng=rng)
    assert len(series) == PERIODS_PER_DAY
    assert (series >= 0.0).all()


def _synthetic_macro_dataset(n_days=1000, seed=0):
    rng = np.random.default_rng(seed)
    doy = np.arange(n_days) % 365 + 1
    omega = 2 * np.pi / 365.25
    national = {
        "temperature_mean_c": 10 + 8 * np.cos(omega * (doy - 200)) + rng.normal(0, 1, n_days),
        "wind_speed_mean_ms": np.clip(4 + rng.normal(0, 1.5, n_days), 0, None),
        "cloud_cover_pct": np.clip(70 + rng.normal(0, 15, n_days), 0, 100),
    }
    return national, doy


def test_fit_and_simulate_national_macro_model_respects_bounds():
    national, doy = _synthetic_macro_dataset()
    params = fit_national_macro_model(national, doy)

    for var in MACRO_VARS:
        assert var in params["seasonal"]
        assert var in params["phi"]
    assert params["regime_transition"].shape == (2, 2)

    rng = np.random.default_rng(1)
    synthetic = simulate_national_macro(params, doy, rng)
    assert (synthetic["wind_speed_mean_ms"] >= 0).all()
    assert (synthetic["cloud_cover_pct"] >= 0).all()
    assert (synthetic["cloud_cover_pct"] <= 100).all()
    for var in MACRO_VARS:
        assert len(synthetic[var]) == len(doy)


def test_fit_and_simulate_regional_cholesky():
    national, doy = _synthetic_macro_dataset()
    rng = np.random.default_rng(2)
    location_daily = {
        loc: {
            var: national[var] + rng.normal(0, 0.5, len(doy))
            for var in MACRO_VARS
        }
        for loc in ["C1", "C2", "C3", "C4"]
    }

    regional_params = fit_regional_cholesky(location_daily, national)
    for var in MACRO_VARS:
        chol = regional_params[var]["cholesky"]
        assert chol.shape == (4, 4)

    deviations = simulate_regional_deviations(regional_params, n_days=100, rng=np.random.default_rng(3))
    for var in MACRO_VARS:
        assert set(deviations[var].keys()) == {"C1", "C2", "C3", "C4"}
        for series in deviations[var].values():
            assert len(series) == 100


def test_fit_and_simulate_temperature_range_is_positive():
    doy = np.arange(1, 366, dtype=float)
    range_values = 6 + 3 * np.cos(2 * np.pi / 365.25 * (doy - 180)) + np.random.default_rng(4).normal(0, 0.5, len(doy))
    params = fit_temperature_range_model(range_values, doy)
    synthetic = simulate_temperature_range(params, doy, np.random.default_rng(5))
    assert (synthetic > 0).all()
    assert len(synthetic) == len(doy)
