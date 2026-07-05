"""
Phase 271: Fetch UK weather data (temperature + HDD) from Open-Meteo historical archive.

London (51.51N, 0.13W) daily mean temperature for 2016-2025.
HDD base = 15.5C (UK National Grid standard for demand forecasting).
Stores site/data/weather.json used by the /sim/ Weather tab.
"""
from __future__ import annotations

import json
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

try:
    import urllib.request as _urlreq
except ImportError:
    _urlreq = None

SITE_DATA = Path(__file__).resolve().parents[1] / "site" / "data"
WEATHER_JSON = SITE_DATA / "weather.json"
BUILD_INFO_PATH = Path(__file__).resolve().parents[1] / "docs" / "observability" / "build_info.json"

HDD_BASE = 15.5
LATITUDE = 51.51
LONGITUDE = -0.13
START_YEAR = 2016
END_YEAR = 2025


def _load_build_phase():
    if BUILD_INFO_PATH.exists():
        try:
            return json.loads(BUILD_INFO_PATH.read_text()).get("phase", "unknown")
        except (json.JSONDecodeError, ValueError):
            pass
    return "unknown"


def _fetch_daily_temps(start, end):
    url = (
        "https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={LATITUDE}&longitude={LONGITUDE}"
        f"&start_date={start}&end_date={end}"
        "&daily=temperature_2m_mean&timezone=Europe%2FLondon"
    )
    with _urlreq.urlopen(url, timeout=30) as resp:
        payload = json.loads(resp.read().decode())
    dates = payload["daily"]["time"]
    temps = payload["daily"]["temperature_2m_mean"]
    return {d: t for d, t in zip(dates, temps) if t is not None}


def _compute_monthly(daily):
    monthly_temps = defaultdict(list)
    for date_str, temp in daily.items():
        month = date_str[:7]
        monthly_temps[month].append(temp)

    rows = []
    for month in sorted(monthly_temps):
        temps = monthly_temps[month]
        mean_temp = sum(temps) / len(temps)
        hdd = sum(max(0.0, HDD_BASE - t) for t in temps)
        cdd = sum(max(0.0, t - HDD_BASE) for t in temps)
        rows.append({
            "month": month,
            "mean_temp_c": round(mean_temp, 2),
            "hdd": round(hdd, 1),
            "cdd": round(cdd, 1),
            "days": len(temps),
        })
    return rows


def _compute_annual(monthly):
    annual = {}
    for row in monthly:
        year = row["month"][:4]
        if year not in annual:
            annual[year] = {"year": year, "hdd": 0.0, "cdd": 0.0, "mean_temps": []}
        annual[year]["hdd"] += row["hdd"]
        annual[year]["cdd"] += row["cdd"]
        annual[year]["mean_temps"].append(row["mean_temp_c"])

    rows = []
    for year in sorted(annual):
        d = annual[year]
        mean_temp = sum(d["mean_temps"]) / len(d["mean_temps"])
        rows.append({
            "year": year,
            "annual_hdd": round(d["hdd"], 0),
            "annual_cdd": round(d["cdd"], 0),
            "mean_temp_c": round(mean_temp, 2),
        })
    return rows


def _decadal_avg_hdd(annual):
    hdds = [r["annual_hdd"] for r in annual]
    return round(sum(hdds) / len(hdds), 0) if hdds else 0.0


def _daily_out(daily):
    """Per-day mean temp + HDD -- feeds the Weather tab's physics-chain panel,
    which needs day-level resolution to trace a chosen cold-snap episode
    (e.g. Feb-Mar 2018 Beast from the East) against daily price/short%."""
    return {
        d: {"mean_temp_c": round(t, 2), "hdd": round(max(0.0, HDD_BASE - t), 1)}
        for d, t in daily.items()
    }


def generate_weather_data(start_year=START_YEAR, end_year=END_YEAR, output_path=None, git_hash="unknown"):
    start = f"{start_year}-01-01"
    end = f"{end_year}-12-31"
    daily = _fetch_daily_temps(start, end)

    monthly = _compute_monthly(daily)
    annual = _compute_annual(monthly)
    avg_hdd = _decadal_avg_hdd(annual)

    for row in annual:
        row["is_cold_winter"] = row["annual_hdd"] > avg_hdd

    coldest = min(monthly, key=lambda r: r["mean_temp_c"])
    warmest = max(monthly, key=lambda r: r["mean_temp_c"])
    highest_hdd_month = max(monthly, key=lambda r: r["hdd"])

    yr2022 = next((r for r in annual if r["year"] == "2022"), None)
    hdd_2022_vs_avg_pct = (
        round((yr2022["annual_hdd"] - avg_hdd) / avg_hdd * 100, 1)
        if yr2022 and avg_hdd
        else None
    )

    result = {
        "monthly": monthly,
        "annual": annual,
        "daily": _daily_out(daily),
        "kpis": {
            "coldest_month": coldest["month"],
            "coldest_temp_c": coldest["mean_temp_c"],
            "warmest_month": warmest["month"],
            "warmest_temp_c": warmest["mean_temp_c"],
            "highest_hdd_month": highest_hdd_month["month"],
            "highest_hdd": highest_hdd_month["hdd"],
            "decadal_avg_annual_hdd": avg_hdd,
            "hdd_base_c": HDD_BASE,
            "hdd_2022_vs_avg_pct": hdd_2022_vs_avg_pct,
        },
        "metadata": {
            "source": "Open-Meteo Historical Archive API",
            "location": "London (51.51N, 0.13W)",
            "start_year": start_year,
            "end_year": end_year,
            "hdd_base_c": HDD_BASE,
            "months": len(monthly),
            "years": len(annual),
            "git_hash": git_hash,
            "phase": _load_build_phase(),
        },
    }

    out = output_path or WEATHER_JSON
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2))
    print(f"Generated {out} ({len(monthly)} months, {len(annual)} years)")
    return result


if __name__ == "__main__":
    generate_weather_data()
