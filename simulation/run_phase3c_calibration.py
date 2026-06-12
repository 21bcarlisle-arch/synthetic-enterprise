"""Phase 3c — weather engine calibration run.

Fits sim.weather_engine's two-pass model (national macro regime-switching
AR1 + regional Cholesky deviations + half-hourly translation) on real
Open-Meteo daily data for the four customer locations (2016-01-01 to
2025-06-07, sim/weather_data/*.csv), generates one synthetic 2016-2025
realisation, and reports distributional fit quality against the real data —
per the Phase 3b precedent, this model is for *distributional* synthetic
generation, not period-by-period reproduction, so the comparison is between
real and synthetic distributions (seasonal means, std dev, regional
correlation, regime frequency), not pointwise error.

The half-hourly translation (diurnal temperature, solar irradiance, wind AR1)
is checked against a real hourly Open-Meteo sample (sim/cache/openmeteo_hourly_c1_2022.json,
London 2022) used during calibration of the constants in weather_engine.py.

Delegation note: hand-written (orchestration-adjacent, schema-defining work
per the Phase 1d delegation lesson).
"""

import csv
import json
from datetime import datetime
from pathlib import Path

import numpy as np

from sim.weather_engine import (
    MACRO_VARS,
    PERIODS_PER_DAY,
    fit_national_macro_model,
    fit_regional_cholesky,
    fit_temperature_range_model,
    half_hourly_solar_irradiance,
    half_hourly_temperature,
    simulate_national_macro,
    simulate_regional_deviations,
    simulate_temperature_range,
    simulate_wind_half_hourly,
)

WEATHER_DIR = Path("sim/weather_data")
LOCATIONS = ["C1", "C2", "C3", "C4"]
LATITUDES = {"C1": 51.5074, "C2": 53.4808, "C3": 55.8642, "C4": 51.8330}
SEED = 42


def _load_location_daily() -> tuple[dict[str, dict[str, np.ndarray]], np.ndarray]:
    location_daily = {}
    day_of_year = None
    for loc in LOCATIONS:
        rows = list(csv.DictReader((WEATHER_DIR / f"{loc}.csv").open()))
        if day_of_year is None:
            day_of_year = np.array(
                [datetime.strptime(r["date"], "%Y-%m-%d").timetuple().tm_yday for r in rows]
            )
        location_daily[loc] = {
            "temperature_mean_c": np.array([float(r["temperature_mean_c"]) for r in rows]),
            "temperature_min_c": np.array([float(r["temperature_min_c"]) for r in rows]),
            "temperature_max_c": np.array([float(r["temperature_max_c"]) for r in rows]),
            "wind_speed_mean_ms": np.array([float(r["wind_speed_mean_ms"]) for r in rows]),
            "cloud_cover_pct": np.array([float(r["cloud_cover_pct"]) for r in rows]),
        }
    return location_daily, day_of_year


def _national_series(location_daily: dict[str, dict[str, np.ndarray]]) -> dict[str, np.ndarray]:
    return {
        var: np.mean([location_daily[loc][var] for loc in LOCATIONS], axis=0)
        for var in MACRO_VARS
    }


def _distribution_report(real: np.ndarray, synthetic: np.ndarray, label: str, unit: str) -> None:
    print(f"  {label:>22}  real: mean={real.mean():7.2f} std={real.std():6.2f}{unit}"
          f"   synthetic: mean={synthetic.mean():7.2f} std={synthetic.std():6.2f}{unit}")


def main():
    print("=== Phase 3c — Weather Engine Calibration ===\n")

    location_daily, day_of_year = _load_location_daily()
    national = _national_series(location_daily)
    n_days = len(day_of_year)
    print(f"{n_days:,} days of real data (2016-01-01..2025-06-07), 4 locations\n")

    # --- Pass 1: national macro model ---
    macro_params = fit_national_macro_model(national, day_of_year)
    print(f"Regime frequency (real, 'stressed' days): {macro_params['regime_frequency']:.1%}")
    for var in MACRO_VARS:
        print(f"  AR1 phi[{var}] = {macro_params['phi'][var]:.3f}")
    print()

    # --- Pass 2: regional Cholesky ---
    regional_params = fit_regional_cholesky(location_daily, national)

    # --- Temperature range model (per location) ---
    range_params = {
        loc: fit_temperature_range_model(
            location_daily[loc]["temperature_max_c"] - location_daily[loc]["temperature_min_c"],
            day_of_year,
        )
        for loc in LOCATIONS
    }

    # --- Simulate one synthetic 2016-2025 realisation ---
    rng = np.random.default_rng(SEED)
    synthetic_national = simulate_national_macro(macro_params, day_of_year, rng)
    synthetic_regional = simulate_regional_deviations(regional_params, n_days, rng)
    synthetic_range = {
        loc: simulate_temperature_range(range_params[loc], day_of_year, rng) for loc in LOCATIONS
    }

    synthetic_location = {}
    for loc in LOCATIONS:
        synthetic_location[loc] = {
            var: synthetic_national[var] + synthetic_regional[var][loc] for var in MACRO_VARS
        }
        synthetic_location[loc]["temperature_range_c"] = synthetic_range[loc]

    print("--- National macro: real vs synthetic distribution ---")
    for var, unit in zip(MACRO_VARS, ["C", "m/s", "%"]):
        _distribution_report(national[var], synthetic_national[var], var, unit)
    print()

    print("--- Per-location temperature_mean_c: real vs synthetic distribution ---")
    for loc in LOCATIONS:
        _distribution_report(
            location_daily[loc]["temperature_mean_c"],
            synthetic_location[loc]["temperature_mean_c"],
            loc, "C",
        )
    print()

    print("--- Per-location temperature_range_c (max-min): real vs synthetic distribution ---")
    for loc in LOCATIONS:
        real_range = location_daily[loc]["temperature_max_c"] - location_daily[loc]["temperature_min_c"]
        _distribution_report(real_range, synthetic_location[loc]["temperature_range_c"], loc, "C")
    print()

    print("--- Cross-location correlation (temperature_mean_c) ---")
    real_matrix = np.column_stack([location_daily[loc]["temperature_mean_c"] for loc in LOCATIONS])
    synth_matrix = np.column_stack([synthetic_location[loc]["temperature_mean_c"] for loc in LOCATIONS])
    real_corr = np.corrcoef(real_matrix.T)
    synth_corr = np.corrcoef(synth_matrix.T)
    print(f"  real mean off-diagonal corr:      {_mean_offdiag(real_corr):.3f}")
    print(f"  synthetic mean off-diagonal corr: {_mean_offdiag(synth_corr):.3f}\n")

    # --- Half-hourly translation check against real hourly sample ---
    print("--- Half-hourly translation vs real hourly sample (C1, 2022) ---")
    hourly = json.loads(Path("sim/cache/openmeteo_hourly_c1_2022.json").read_text())
    _check_half_hourly(hourly)

    return {
        "macro_params": macro_params,
        "regional_params": regional_params,
        "synthetic_location": synthetic_location,
    }


def _mean_offdiag(matrix: np.ndarray) -> float:
    n = matrix.shape[0]
    mask = ~np.eye(n, dtype=bool)
    return float(matrix[mask].mean())


def _check_half_hourly(hourly: dict) -> None:
    times = hourly["time"]
    real_sw = np.array(hourly["shortwave_radiation"])
    real_temp = np.array(hourly["temperature_2m"])
    real_wind = np.array(hourly["wind_speed_10m"])

    n_days = len(times) // 24
    real_temp_by_day = real_temp[: n_days * 24].reshape(n_days, 24)
    real_sw_by_day = real_sw[: n_days * 24].reshape(n_days, 24)
    real_wind_by_day = real_wind[: n_days * 24].reshape(n_days, 24)

    rng = np.random.default_rng(SEED)

    temp_errors = []
    sw_errors = []
    wind_stationary_stds = []
    for d in range(n_days):
        doy = datetime.fromisoformat(times[d * 24]).timetuple().tm_yday
        daily_min, daily_max = real_temp_by_day[d].min(), real_temp_by_day[d].max()
        for hour in range(24):
            period = hour * 2
            synth_temp = half_hourly_temperature(daily_min, daily_max, period)
            temp_errors.append(synth_temp - real_temp_by_day[d, hour])

            cloud_pct = 50.0  # not available per-hour here; use a fixed mid value for shape check
            synth_sw = half_hourly_solar_irradiance(doy, period, 51.5074, cloud_pct)
            sw_errors.append(synth_sw - real_sw_by_day[d, hour])

        daily_mean_wind = real_wind_by_day[d].mean()
        synth_wind = simulate_wind_half_hourly(daily_mean_wind, rng, n_periods=PERIODS_PER_DAY)
        wind_stationary_stds.append(synth_wind.std())

    real_wind_within_day_std = (real_wind_by_day - real_wind_by_day.mean(axis=1, keepdims=True)).std()

    print(f"  diurnal temperature shape MAE: {np.mean(np.abs(temp_errors)):.2f}C "
          f"(real hourly temp std: {real_temp.std():.2f}C)")
    print(f"  solar irradiance MAE: {np.mean(np.abs(sw_errors)):.1f} W/m^2 "
          f"(real shortwave_radiation mean: {real_sw.mean():.1f} W/m^2, "
          f"note: real comparison uses actual cloud cover, synthetic uses fixed 50%)")
    print(f"  synthetic within-day wind std: {np.mean(wind_stationary_stds):.2f} m/s "
          f"(real within-day wind std: {real_wind_within_day_std:.2f} m/s)")


if __name__ == "__main__":
    main()
