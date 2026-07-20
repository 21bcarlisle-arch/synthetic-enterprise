"""Phase 3c — two-pass synthetic weather engine.

Pass 1 (national macro): a 2016-2025 daily national series (temperature,
wind speed, cloud cover — averaged across the four customer locations) is
deseasonalised via harmonic regression, then modelled as a mean-reverting
(AR1) process on the residuals with regime-switching innovation covariance
("standard" vs "stressed" — stressed days are those with unusually large
wind-residual magnitude, calibrated from real data). The regime-switching
covariance *is* the jump mechanism: a transition into the stressed regime
produces a much larger innovation than the standard regime, which is the
practical effect a separate compound-Poisson jump term would add — see
docs/calibration/weather-engine.md for the design rationale.

Pass 2 (regional micro-climates): each location's daily deviation from the
national series is modelled via a Cholesky-decomposed cross-location
covariance matrix, so synthetic regional deviations preserve the real
correlation structure between London/Manchester/Glasgow/Cotswolds while
remaining "physically bound" to the national front (Pass 1 sets the level,
Pass 2 adds correlated local variation around it).

Half-hourly translation turns a day's (mean, min, max temperature; mean wind;
cloud cover) into 48 half-hourly values:
  - temperature: asymmetric diurnal cosine, calibrated against real hourly
    data to peak at period 30 (15:00) and trough at period 10 (05:00)
  - solar irradiance: an astronomical clear-sky envelope (solar elevation
    angle from latitude/day-of-year/time) attenuated by cloud cover
  - wind: an AR1 (discretised Ornstein-Uhlenbeck) process around the day's
    mean wind speed

All calibration constants below were fitted against real Open-Meteo data
(see docs/calibration/weather-engine.md) — Historical Ground Truth law.
"""

import numpy as np

PERIODS_PER_DAY = 48

# --- Diurnal temperature shape (calibrated against C1 2022 hourly data:
# mean hourly deviation from the daily mean troughs at 05:00, peaks at 15:00,
# matching the spec'd "peak period 30/15:00, trough period 10/05:00") ---
TEMP_TROUGH_PERIOD = 10
TEMP_PEAK_PERIOD = 30
# Diurnal amplitude (half the daily max-min range) is scaled down — the
# observed hourly deviation range (~6.66C) is ~80% of the daily max-min
# range (~8.28C) for C1 2022.
TEMP_DIURNAL_AMPLITUDE_SCALE = 0.8

# --- Solar irradiance clear-sky envelope (astronomical formula) + cloud
# attenuation, fitted against C1 2022 hourly shortwave_radiation ---
SOLAR_I0 = 1000.0  # W/m^2, simplified top-of-envelope constant
SOLAR_CLOUD_ATTENUATION_K = 0.446

# --- Wind half-hourly AR1 (discretised Ornstein-Uhlenbeck), fitted against
# C1 2022 hourly wind_speed_10m deviations from the daily mean (lag-1
# autocorrelation 0.823 -> half-hourly AR1 coefficient = sqrt(0.823)) ---
WIND_AR1_COEFF = 0.906
WIND_INNOVATION_STD = 0.522  # m/s, gives stationary std ~1.23 m/s

MACRO_VARS = ["temperature_mean_c", "wind_speed_mean_ms", "cloud_cover_pct"]

_SEASONAL_PERIOD_DAYS = 365.25


# ---------------------------------------------------------------------------
# Seasonal harmonic regression (annual + semi-annual cycle)
# ---------------------------------------------------------------------------

def fit_seasonal_harmonics(values: np.ndarray, day_of_year: np.ndarray) -> np.ndarray:
    """Fit y ~ c0 + c1*cos(w*d) + c2*sin(w*d) + c3*cos(2w*d) + c4*sin(2w*d),
    w = 2*pi/365.25. Returns the 5 fitted coefficients."""
    omega = 2 * np.pi / _SEASONAL_PERIOD_DAYS
    doy = np.asarray(day_of_year, dtype=float)
    design = np.column_stack([
        np.ones_like(doy),
        np.cos(omega * doy), np.sin(omega * doy),
        np.cos(2 * omega * doy), np.sin(2 * omega * doy),
    ])
    coeffs, *_ = np.linalg.lstsq(design, np.asarray(values, dtype=float), rcond=None)
    return coeffs


def seasonal_value(coeffs: np.ndarray, day_of_year: np.ndarray) -> np.ndarray:
    """Evaluate the fitted seasonal cycle at the given day(s)-of-year."""
    omega = 2 * np.pi / _SEASONAL_PERIOD_DAYS
    doy = np.asarray(day_of_year, dtype=float)
    design = np.column_stack([
        np.ones_like(doy),
        np.cos(omega * doy), np.sin(omega * doy),
        np.cos(2 * omega * doy), np.sin(2 * omega * doy),
    ])
    return design @ coeffs


# W1_3 gap-1: the innovation covariance is SEASON-conditioned. Cold season =
# meteorological winter (Dec-Feb), where the real temp/wind innovation correlation
# is +0.53 vs +0.18 outside it. `day_of_year` boundaries: Dec 1 ~ 335, Feb 28 ~ 59.
_COLD_SEASON_DOY_START = 335  # ~Dec 1
_COLD_SEASON_DOY_END = 59     # ~Feb 28


def _is_cold_season(day_of_year: np.ndarray) -> np.ndarray:
    """Boolean mask: True on cold-season (Dec-Feb) days, by day-of-year. The
    season the elevated temp/wind (cold-and-still) coupling lives in (W1_3 gap-1)."""
    doy = np.asarray(day_of_year)
    return (doy >= _COLD_SEASON_DOY_START) | (doy <= _COLD_SEASON_DOY_END)


# ---------------------------------------------------------------------------
# Pass 1 — national macro: regime-switching mean-reverting (AR1) model
# ---------------------------------------------------------------------------

def fit_national_macro_model(national_daily: dict[str, np.ndarray], day_of_year: np.ndarray) -> dict:
    """Fit the national macro model from real daily national series.

    national_daily: {var: array of shape (n_days,)} for each var in MACRO_VARS.
    Returns a params dict consumed by simulate_national_macro().
    """
    seasonal = {}
    residuals = {}
    phi = {}
    for var in MACRO_VARS:
        coeffs = fit_seasonal_harmonics(national_daily[var], day_of_year)
        resid = national_daily[var] - seasonal_value(coeffs, day_of_year)
        seasonal[var] = coeffs
        residuals[var] = resid
        phi[var] = float(np.corrcoef(resid[:-1], resid[1:])[0, 1])

    # AR1 innovations: innovation_t = resid_t - phi*resid_{t-1}
    innovations = np.column_stack([
        residuals[var][1:] - phi[var] * residuals[var][:-1] for var in MACRO_VARS
    ])

    # W1_3 gap-1 fix: the temp/wind innovation correlation is SEASON-DEPENDENT
    # (measured on the real record: +0.53 in winter vs +0.18 outside it), so a
    # SINGLE innovation covariance under-produces the winter cold-and-still joint
    # tail. Fit the covariance CONDITIONALLY on season -- a cold-season ("stressed")
    # covariance carrying the elevated winter coupling, a warm-season ("standard")
    # covariance otherwise -- and (in simulate_national_macro) select it by the
    # day's ACTUAL season. R13 BASELINE FIDELITY change, decided blind to company
    # P&L: validated to reproduce the real winter joint-tail lift (simulated D1
    # decile lift ~2.88 vs real 2.37, within the real block-bootstrap CI
    # [1.54, 3.38]); the prior wind-magnitude single-corner covariance gave ~1.77.
    # Three hypotheses were measured (trigger + symmetric-t both REFUTED, this one
    # validated) -- docs/design/frame/W1_3_gap1_regime_trigger_REFUTED_FRAME.md.
    cold = _is_cold_season(np.asarray(day_of_year))[1:]  # aligned to innovations (days[1:])
    cov_standard = np.cov(innovations[~cold].T)   # warm season
    cov_stressed = np.cov(innovations[cold].T)    # cold season -- elevated temp/wind coupling

    # regime_transition retained (from the season sequence) for inspection/back-compat;
    # simulate now switches covariance by CALENDAR season, not this Markov matrix.
    season = _is_cold_season(np.asarray(day_of_year)).astype(int)
    transition = np.zeros((2, 2))
    for t in range(len(season) - 1):
        transition[season[t], season[t + 1]] += 1
    transition = transition / transition.sum(axis=1, keepdims=True)

    return {
        "seasonal": seasonal,
        "phi": phi,
        "regime_transition": transition,
        "regime_frequency": float(season.mean()),
        "cov": {"standard": cov_standard, "stressed": cov_stressed},
    }


def simulate_national_macro(params: dict, day_of_year: np.ndarray, rng: np.random.Generator) -> dict[str, np.ndarray]:
    """Simulate a synthetic national daily macro series of length len(day_of_year)."""
    n = len(day_of_year)
    chol = {
        "standard": np.linalg.cholesky(params["cov"]["standard"]),
        "stressed": np.linalg.cholesky(params["cov"]["stressed"]),
    }
    # W1_3 gap-1: select the innovation covariance by the day's ACTUAL season
    # (calendar-determined), so the elevated cold-and-still coupling lands in real
    # winter -- not a Markov-random block that could fall in simulated summer.
    cold = _is_cold_season(np.asarray(day_of_year))

    resid = {var: np.zeros(n) for var in MACRO_VARS}
    for t in range(1, n):
        label = "stressed" if cold[t] else "standard"
        innovation = chol[label] @ rng.standard_normal(len(MACRO_VARS))
        for i, var in enumerate(MACRO_VARS):
            resid[var][t] = params["phi"][var] * resid[var][t - 1] + innovation[i]

    result = {}
    for var in MACRO_VARS:
        values = seasonal_value(params["seasonal"][var], day_of_year) + resid[var]
        if var == "wind_speed_mean_ms":
            values = np.clip(values, 0.0, None)
        elif var == "cloud_cover_pct":
            values = np.clip(values, 0.0, 100.0)
        result[var] = values
    return result


# ---------------------------------------------------------------------------
# Pass 2 — regional micro-climates: Cholesky-correlated deviations
# ---------------------------------------------------------------------------

def fit_regional_cholesky(location_daily: dict[str, dict[str, np.ndarray]],
                            national_daily: dict[str, np.ndarray]) -> dict[str, dict]:
    """Fit the cross-location covariance of (location - national) deviations
    for each macro variable, returning a Cholesky factor per variable.

    location_daily: {location_id: {var: array}}. national_daily: {var: array}.
    """
    location_ids = sorted(location_daily.keys())
    result = {}
    for var in MACRO_VARS:
        deviations = np.column_stack([
            location_daily[loc][var] - national_daily[var] for loc in location_ids
        ])
        mean = deviations.mean(axis=0)
        cov = np.cov(deviations.T)
        # tiny jitter for numerical stability of the Cholesky factorisation
        cov = cov + np.eye(len(location_ids)) * 1e-9
        result[var] = {
            "locations": location_ids,
            "mean": mean,
            "cholesky": np.linalg.cholesky(cov),
        }
    return result


def simulate_regional_deviations(regional_params: dict[str, dict], n_days: int,
                                   rng: np.random.Generator) -> dict[str, dict[str, np.ndarray]]:
    """Simulate correlated per-location daily deviations for each macro variable.

    Returns {var: {location_id: array of shape (n_days,)}}.
    """
    result = {}
    for var, params in regional_params.items():
        chol = params["cholesky"]
        n_loc = chol.shape[0]
        z = rng.standard_normal((n_days, n_loc))
        deviations = z @ chol.T + params["mean"]
        result[var] = {loc: deviations[:, i] for i, loc in enumerate(params["locations"])}
    return result


# ---------------------------------------------------------------------------
# Temperature daily range (max - min), modelled per-location for the
# half-hourly translation (seasonal cycle + i.i.d. residual noise)
# ---------------------------------------------------------------------------

def fit_temperature_range_model(range_values: np.ndarray, day_of_year: np.ndarray) -> dict:
    coeffs = fit_seasonal_harmonics(range_values, day_of_year)
    resid_std = float(np.std(range_values - seasonal_value(coeffs, day_of_year)))
    return {"seasonal": coeffs, "resid_std": resid_std}


def simulate_temperature_range(params: dict, day_of_year: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    seasonal = seasonal_value(params["seasonal"], day_of_year)
    noise = rng.normal(0.0, params["resid_std"], size=len(day_of_year))
    return np.clip(seasonal + noise, 0.5, None)


# ---------------------------------------------------------------------------
# Half-hourly translation
# ---------------------------------------------------------------------------

def diurnal_temperature_shape(period: int) -> float:
    """Asymmetric diurnal shape in [-1, 1], trough at TEMP_TROUGH_PERIOD
    (05:00), peak at TEMP_PEAK_PERIOD (15:00)."""
    p = period % PERIODS_PER_DAY
    if TEMP_TROUGH_PERIOD <= p <= TEMP_PEAK_PERIOD:
        frac = (p - TEMP_TROUGH_PERIOD) / (TEMP_PEAK_PERIOD - TEMP_TROUGH_PERIOD)
        return -np.cos(np.pi * frac)
    p2 = p if p >= TEMP_PEAK_PERIOD else p + PERIODS_PER_DAY
    span = (PERIODS_PER_DAY + TEMP_TROUGH_PERIOD) - TEMP_PEAK_PERIOD
    frac = (p2 - TEMP_PEAK_PERIOD) / span
    return np.cos(np.pi * frac)


def half_hourly_temperature(daily_min_c: float, daily_max_c: float, period: int) -> float:
    mean = (daily_min_c + daily_max_c) / 2.0
    amplitude = (daily_max_c - daily_min_c) / 2.0 * TEMP_DIURNAL_AMPLITUDE_SCALE
    return mean + amplitude * diurnal_temperature_shape(period)


def clear_sky_irradiance(day_of_year: int, period: int, latitude_deg: float) -> float:
    """Astronomical clear-sky solar irradiance envelope (W/m^2)."""
    lat = np.radians(latitude_deg)
    declination = np.radians(23.45) * np.sin(np.radians(360.0 / 365.0 * (284 + day_of_year)))
    hour = period / 2.0
    hour_angle = np.radians(15.0 * (hour - 12.0))
    sin_elevation = (np.sin(lat) * np.sin(declination)
                      + np.cos(lat) * np.cos(declination) * np.cos(hour_angle))
    return SOLAR_I0 * max(float(sin_elevation), 0.0)


def half_hourly_solar_irradiance(day_of_year: int, period: int, latitude_deg: float,
                                   cloud_cover_pct: float) -> float:
    clear_sky = clear_sky_irradiance(day_of_year, period, latitude_deg)
    cloud_fraction = cloud_cover_pct / 100.0
    return max(clear_sky * (1.0 - SOLAR_CLOUD_ATTENUATION_K * cloud_fraction), 0.0)


def simulate_wind_half_hourly(daily_mean_wind_ms: float, rng: np.random.Generator,
                                n_periods: int = PERIODS_PER_DAY) -> np.ndarray:
    """AR1 (discretised Ornstein-Uhlenbeck) half-hourly wind speed series,
    mean-reverting to daily_mean_wind_ms."""
    deviations = np.zeros(n_periods)
    stationary_std = WIND_INNOVATION_STD / np.sqrt(1.0 - WIND_AR1_COEFF ** 2)
    deviations[0] = rng.normal(0.0, stationary_std)
    for t in range(1, n_periods):
        deviations[t] = WIND_AR1_COEFF * deviations[t - 1] + rng.normal(0.0, WIND_INNOVATION_STD)
    return np.clip(daily_mean_wind_ms + deviations, 0.0, None)
