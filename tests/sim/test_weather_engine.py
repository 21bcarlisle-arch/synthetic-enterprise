"""Tests for sim/weather_engine.py constants and pure calculation functions."""

import numpy as np
import pytest

from sim.weather_engine import (
    PERIODS_PER_DAY,
    TEMP_TROUGH_PERIOD,
    TEMP_PEAK_PERIOD,
    TEMP_DIURNAL_AMPLITUDE_SCALE,
    WIND_AR1_COEFF,
    WIND_INNOVATION_STD,
    SOLAR_I0,
    SOLAR_CLOUD_ATTENUATION_K,
    clear_sky_irradiance,
    diurnal_temperature_shape,
    fit_seasonal_harmonics,
    half_hourly_solar_irradiance,
    half_hourly_temperature,
    seasonal_value,
)


def test_periods_per_day():
    assert PERIODS_PER_DAY == 48


def test_temp_trough_period():
    assert TEMP_TROUGH_PERIOD == 10


def test_temp_peak_period():
    assert TEMP_PEAK_PERIOD == 30


def test_temp_diurnal_amplitude_scale():
    assert TEMP_DIURNAL_AMPLITUDE_SCALE == pytest.approx(0.8)


def test_wind_ar1_coeff():
    assert WIND_AR1_COEFF == pytest.approx(0.906)


def test_wind_innovation_std():
    assert WIND_INNOVATION_STD == pytest.approx(0.522)


def test_solar_i0():
    assert SOLAR_I0 == pytest.approx(1000.0)


def test_diurnal_trough_at_period_10():
    assert diurnal_temperature_shape(TEMP_TROUGH_PERIOD) == pytest.approx(-1.0)


def test_diurnal_peak_at_period_30():
    assert diurnal_temperature_shape(TEMP_PEAK_PERIOD) == pytest.approx(1.0)


def test_diurnal_mid_ascending_is_zero():
    assert diurnal_temperature_shape(20) == pytest.approx(0.0, abs=1e-10)


def test_diurnal_wraps_at_48():
    assert diurnal_temperature_shape(0) == pytest.approx(diurnal_temperature_shape(48))


def test_diurnal_range_bounded():
    for p in range(48):
        val = diurnal_temperature_shape(p)
        assert -1.0 <= val <= 1.0


def test_half_hourly_temp_at_trough():
    result = half_hourly_temperature(0.0, 10.0, TEMP_TROUGH_PERIOD)
    assert result == pytest.approx(1.0)


def test_half_hourly_temp_at_peak():
    result = half_hourly_temperature(0.0, 10.0, TEMP_PEAK_PERIOD)
    assert result == pytest.approx(9.0)


def test_half_hourly_temp_at_midpoint_is_mean():
    result = half_hourly_temperature(0.0, 10.0, 20)
    assert result == pytest.approx(5.0, abs=1e-10)


def test_half_hourly_temp_equal_min_max():
    assert half_hourly_temperature(5.0, 5.0, 20) == pytest.approx(5.0)


def test_clear_sky_midnight_is_zero():
    assert clear_sky_irradiance(172, 0, 51.5) == pytest.approx(0.0)


def test_clear_sky_noon_summer_solstice_positive():
    result = clear_sky_irradiance(172, 24, 51.5)
    assert result > 0.0


def test_clear_sky_summer_greater_than_winter():
    summer = clear_sky_irradiance(172, 24, 51.5)
    winter = clear_sky_irradiance(355, 24, 51.5)
    assert summer > winter


def test_clear_sky_always_non_negative():
    for doy in [1, 90, 172, 265, 355]:
        for period in [0, 6, 12, 24, 36, 47]:
            assert clear_sky_irradiance(doy, period, 51.5) >= 0.0


def test_solar_irradiance_zero_cloud_equals_clear_sky():
    clear = clear_sky_irradiance(172, 24, 51.5)
    hh = half_hourly_solar_irradiance(172, 24, 51.5, 0.0)
    assert hh == pytest.approx(clear)


def test_solar_irradiance_full_cloud_less_than_clear():
    clear = clear_sky_irradiance(172, 24, 51.5)
    hh = half_hourly_solar_irradiance(172, 24, 51.5, 100.0)
    assert hh < clear
    assert hh > 0.0


def test_solar_irradiance_nighttime_is_zero():
    assert half_hourly_solar_irradiance(172, 0, 51.5, 50.0) == pytest.approx(0.0)


def test_fit_seasonal_harmonics_returns_5_coeffs():
    doy = np.arange(1, 366)
    vals = np.full(365, 10.0)
    coeffs = fit_seasonal_harmonics(vals, doy)
    assert coeffs.shape == (5,)


def test_fit_seasonal_harmonics_constant_series():
    doy = np.arange(1, 366)
    vals = np.full(365, 10.0)
    coeffs = fit_seasonal_harmonics(vals, doy)
    assert coeffs[0] == pytest.approx(10.0, abs=1e-8)
    for c in coeffs[1:]:
        assert abs(c) < 1e-10


def test_seasonal_value_reconstructs_signal():
    doy = np.arange(1, 366)
    vals = np.cos(2 * np.pi / 365.25 * doy) * 5.0
    coeffs = fit_seasonal_harmonics(vals, doy)
    reconstructed = seasonal_value(coeffs, doy)
    assert np.max(np.abs(reconstructed - vals)) < 1e-10


def test_seasonal_value_constant_series():
    doy = np.arange(1, 366)
    vals = np.full(365, 10.0)
    coeffs = fit_seasonal_harmonics(vals, doy)
    result = seasonal_value(coeffs, np.array([1.0, 91.0, 182.0, 275.0, 365.0]))
    assert np.allclose(result, 10.0, atol=1e-8)


def test_season_conditioned_cov_reproduces_winter_joint_tail():
    """W1_3 gap-1 (R15, both directions): the SEASON-CONDITIONED innovation
    covariance makes the engine reproduce the REAL winter cold-and-still joint
    tail (D1 decile lift, real 2.365, block-bootstrap CI [1.54, 3.38]). The
    fitted engine's simulated lift lands in the band; MUTATING the cold-season
    covariance back to the warm-season one (removing the seasonal coupling)
    collapses it well below -- proving the seasonal covariance is load-bearing,
    not decorative (this is the mechanism that closed the gap the joint-regime
    trigger and the symmetric-t innovations both failed to close)."""
    import copy
    from sim.weather_engine import fit_national_macro_model, simulate_national_macro
    from sim.weather_tail_demonstration import load_national_daily
    from background.cascade_correlation_estimation import condition, joint_tail_lift

    national, doy, dates = load_national_daily()
    winter = np.array([d.month in (12, 1, 2) for d in dates])

    def sim_lift(mp, n=12):
        vals = []
        for s in range(n):
            sim = simulate_national_macro(mp, doy, np.random.default_rng(s))
            vals.append(joint_tail_lift(
                condition(sim["temperature_mean_c"], winter),
                condition(sim["wind_speed_mean_ms"], winter),
                u=0.10, upper=False).lift)
        return float(np.mean(vals))

    mp = fit_national_macro_model(national, doy)
    assert 1.9 < sim_lift(mp) < 3.4            # FIRES: reproduces the real winter joint tail

    muted = copy.deepcopy(mp)
    muted["cov"]["stressed"] = muted["cov"]["standard"]  # remove the seasonal coupling
    assert sim_lift(muted) < 1.9               # MUTATION: collapses back to under-production
