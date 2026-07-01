"""Phase 271 tests: fetch_weather_data tool."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.fetch_weather_data import (
    _compute_monthly,
    _compute_annual,
    _decadal_avg_hdd,
    HDD_BASE,
)


def _make_daily(year=2022):
    import datetime, random
    random.seed(42)
    daily = {}
    d = datetime.date(year, 1, 1)
    end = datetime.date(year, 12, 31)
    while d <= end:
        m = d.month
        if m in (12, 1, 2):
            t = random.uniform(2.0, 6.0)
        elif m in (6, 7, 8):
            t = random.uniform(17.0, 22.0)
        else:
            t = random.uniform(8.0, 14.0)
        daily[d.isoformat()] = t
        d += datetime.timedelta(days=1)
    return daily


def _multi_year_daily(start=2016, end=2025):
    daily = {}
    for yr in range(start, end + 1):
        daily.update(_make_daily(yr))
    return daily


def test_hdd_non_negative():
    daily = _make_daily(2022)
    monthly = _compute_monthly(daily)
    for row in monthly:
        assert row["hdd"] >= 0


def test_mean_temp_in_plausible_range():
    daily = _make_daily(2022)
    monthly = _compute_monthly(daily)
    for row in monthly:
        assert -5 <= row["mean_temp_c"] <= 30


def test_all_months_2016_to_2025():
    daily = _multi_year_daily(2016, 2025)
    monthly = _compute_monthly(daily)
    months = {r["month"] for r in monthly}
    assert len(months) == 120
    assert "2016-01" in months
    assert "2025-12" in months


def test_annual_hdd_plausible():
    daily = _make_daily(2022)
    monthly = _compute_monthly(daily)
    annual = _compute_annual(monthly)
    assert len(annual) == 1
    assert annual[0]["annual_hdd"] > 0


def test_hdd_highest_in_winter():
    daily = _multi_year_daily(2016, 2025)
    monthly = _compute_monthly(daily)
    winter = [r["hdd"] for r in monthly if r["month"][5:7] in ("12", "01", "02")]
    summer = [r["hdd"] for r in monthly if r["month"][5:7] in ("06", "07", "08")]
    assert sum(winter) / len(winter) > sum(summer) / len(summer)


def test_decadal_avg_hdd():
    daily = _multi_year_daily(2016, 2025)
    monthly = _compute_monthly(daily)
    annual = _compute_annual(monthly)
    avg = _decadal_avg_hdd(annual)
    manual = sum(r["annual_hdd"] for r in annual) / len(annual)
    assert abs(avg - manual) < 1.0


def test_hdd_base_is_15_5():
    assert HDD_BASE == 15.5


def test_coldest_months_in_winter():
    daily = _multi_year_daily(2016, 2025)
    monthly = _compute_monthly(daily)
    coldest = min(monthly, key=lambda r: r["mean_temp_c"])
    assert coldest["month"][5:7] in ("01", "02", "12")


def test_weather_json_structure(tmp_path, monkeypatch):
    import tools.fetch_weather_data as fwd
    daily = _multi_year_daily(2016, 2025)
    monkeypatch.setattr(fwd, "_fetch_daily_temps", lambda s, e: daily)
    result = fwd.generate_weather_data(output_path=tmp_path / "weather.json")
    assert "monthly" in result
    assert "annual" in result
    assert "kpis" in result
    assert "metadata" in result
    assert len(result["monthly"]) == 120
    assert len(result["annual"]) == 10


def test_is_cold_winter_flag(tmp_path, monkeypatch):
    import tools.fetch_weather_data as fwd
    daily = _multi_year_daily(2016, 2025)
    monkeypatch.setattr(fwd, "_fetch_daily_temps", lambda s, e: daily)
    result = fwd.generate_weather_data(output_path=tmp_path / "weather.json")
    for row in result["annual"]:
        assert "is_cold_winter" in row
        assert isinstance(row["is_cold_winter"], bool)


def test_annual_year_range():
    daily = _multi_year_daily(2016, 2025)
    monthly = _compute_monthly(daily)
    annual = _compute_annual(monthly)
    years = [r["year"] for r in annual]
    assert min(years) == "2016"
    assert max(years) == "2025"


def test_monthly_has_required_keys():
    daily = _make_daily(2022)
    monthly = _compute_monthly(daily)
    assert len(monthly) > 0
    row = monthly[0]
    for key in ("month", "mean_temp_c", "hdd"):
        assert key in row


def test_hdd_formula_matches_base():
    import datetime
    daily_one = {"2022-01-01": 5.0}
    monthly = _compute_monthly(daily_one)
    expected_hdd = max(0, HDD_BASE - 5.0)
    assert abs(monthly[0]["hdd"] - expected_hdd) < 0.01
