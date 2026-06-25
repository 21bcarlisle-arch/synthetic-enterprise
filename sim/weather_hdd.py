"""HDD (heating degree day) model for gas consumption weather-adjustment.

UK standard base temperature 15.5°C (DECC/Ofgem domestic gas standard).
Reference monthly HDD: UK Met Office 1991-2020 climate normals (England & Wales).
"""
from __future__ import annotations

import csv
from calendar import monthrange
from datetime import date, timedelta

WEATHER_DATA_DIR = "sim/weather_data"
HDD_BASE_TEMP_C = 15.5

# UK 1991-2020 HDD climate normals (base 15.5°C, England & Wales).
# Sourced from Met Office HDD/CDD tabulations and Ofgem annual consumption data.
REFERENCE_MONTHLY_HDD: dict[int, float] = {
    1: 350.0,
    2: 315.0,
    3: 275.0,
    4: 200.0,
    5: 118.0,
    6:  30.0,
    7:   5.0,
    8:   5.0,
    9:  38.0,
    10: 140.0,
    11: 249.0,
    12: 341.0,
}

_WEATHER_CACHE: dict[str, dict[str, float]] = {}


def _load_weather_means(customer_id: str) -> dict[str, float]:
    if customer_id in _WEATHER_CACHE:
        return _WEATHER_CACHE[customer_id]
    path = f"{WEATHER_DATA_DIR}/{customer_id}.csv"
    try:
        with open(path, newline="") as f:
            result = {row["date"]: float(row["temperature_mean_c"]) for row in csv.DictReader(f)}
    except FileNotFoundError:
        result = {}
    _WEATHER_CACHE[customer_id] = result
    return result


def _resolve_source_cid(customer_id: str) -> str:
    """Map gas customer IDs to their weather-data counterpart.

    C1g -> C1 (shares location with dual-fuel electricity customer).
    Non-gas customers and unrecognised IDs pass through unchanged.
    """
    if customer_id.endswith("g") and len(customer_id) > 1:
        return customer_id[:-1]
    return customer_id


def get_hdd(date_str: str, customer_id: str) -> float:
    """HDD for one day at customer's location. max(0, 15.5 - mean_temp)."""
    source_cid = _resolve_source_cid(customer_id)
    means = _load_weather_means(source_cid)
    if date_str in means:
        return max(0.0, HDD_BASE_TEMP_C - means[date_str])
    month = int(date_str[5:7])
    return REFERENCE_MONTHLY_HDD[month] / 30.0


def get_monthly_hdd(year: int, month: int, customer_id: str) -> float:
    """Sum of daily HDD for one calendar month."""
    _, days = monthrange(year, month)
    return sum(
        get_hdd(f"{year:04d}-{month:02d}-{day:02d}", customer_id)
        for day in range(1, days + 1)
    )


def get_weather_factor(year: int, month: int, customer_id: str) -> float:
    """Ratio of actual to reference monthly HDD, clipped to [0.3, 2.0].

    < 1.0 -> warmer than normal -> less gas consumed.
    > 1.0 -> colder than normal -> more gas consumed.
    """
    ref = REFERENCE_MONTHLY_HDD.get(month, 30.0)
    if ref <= 0:
        return 1.0
    actual = get_monthly_hdd(year, month, customer_id)
    return max(0.3, min(2.0, actual / ref))


def weather_factor_for_term(term_start: str, term_end: str, customer_id: str) -> float:
    """Day-weighted average weather factor across all months in [term_start, term_end)."""
    start = date.fromisoformat(term_start)
    end = date.fromisoformat(term_end)

    total_days = 0
    weighted_sum = 0.0
    current = date(start.year, start.month, 1)

    while current < end:
        yr, mo = current.year, current.month
        _, mdays = monthrange(yr, mo)
        month_start = max(start, current)
        month_end_date = date(yr, mo, mdays)
        month_end = min(end, month_end_date + timedelta(days=1))
        days_in_period = (month_end - month_start).days
        if days_in_period > 0:
            factor = get_weather_factor(yr, mo, customer_id)
            weighted_sum += factor * days_in_period
            total_days += days_in_period
        if mo == 12:
            current = date(yr + 1, 1, 1)
        else:
            current = date(yr, mo + 1, 1)

    return weighted_sum / total_days if total_days > 0 else 1.0
