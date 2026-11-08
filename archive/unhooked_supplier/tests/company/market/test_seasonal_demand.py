import datetime as dt
import pytest
from company.market.seasonal_demand import (
    Season, DemandScenario, MonthlyDemandForecast, SeasonalDemandModel, get_season
)


def test_get_season_winter():
    assert get_season(1) == Season.WINTER
    assert get_season(12) == Season.WINTER


def test_get_season_summer():
    assert get_season(6) == Season.SUMMER
    assert get_season(9) == Season.SUMMER


def test_seasonal_index_january():
    f = MonthlyDemandForecast(2022, 1, 'electricity', 1000.0)
    assert f.seasonal_index == pytest.approx(1.35)


def test_forecast_mwh_base():
    f = MonthlyDemandForecast(2022, 7, 'electricity', 1000.0)
    assert f.forecast_mwh == pytest.approx(800.0, rel=0.01)


def test_forecast_mwh_high_scenario():
    f = MonthlyDemandForecast(2022, 1, 'electricity', 1000.0, DemandScenario.HIGH)
    assert f.forecast_mwh == pytest.approx(1000.0 * 1.35 * 1.15, rel=0.01)


def test_annual_demand():
    model = SeasonalDemandModel()
    for month in range(1, 13):
        model.set_monthly_forecast(2022, month, 'electricity', 1000.0)
    total = model.annual_demand_mwh(2022, 'electricity')
    assert total > 0


def test_seasonal_demand():
    model = SeasonalDemandModel()
    for month in range(1, 13):
        model.set_monthly_forecast(2022, month, 'gas', 500.0)
    winter = model.seasonal_demand_mwh(2022, 'gas', Season.WINTER)
    summer = model.seasonal_demand_mwh(2022, 'gas', Season.SUMMER)
    assert winter > summer


def test_peak_month():
    model = SeasonalDemandModel()
    for month in range(1, 13):
        model.set_monthly_forecast(2022, month, 'electricity', 1000.0)
    peak = model.peak_month(2022, 'electricity')
    assert peak is not None
    assert peak.month == 1


def test_winter_summer_ratio():
    model = SeasonalDemandModel()
    for month in range(1, 13):
        model.set_monthly_forecast(2022, month, 'electricity', 1000.0)
    ratio = model.winter_summer_ratio(2022, 'electricity')
    assert ratio is not None
    assert ratio > 1.0


def test_demand_summary():
    model = SeasonalDemandModel()
    model.set_monthly_forecast(2022, 6, 'electricity', 800.0)
    s = model.demand_summary(2022)
    assert s['total_months'] == 1
    assert 'electricity' in s['by_commodity']


def test_get_season_november_winter():
    assert get_season(11) == Season.WINTER


def test_get_season_april_summer():
    assert get_season(4) == Season.SUMMER


def test_seasonal_index_july():
    f = MonthlyDemandForecast(2022, 7, 'electricity', 1000.0)
    assert f.seasonal_index == pytest.approx(0.80)


def test_forecast_mwh_low_scenario():
    f = MonthlyDemandForecast(2022, 1, 'electricity', 1000.0, DemandScenario.LOW)
    assert f.forecast_mwh == pytest.approx(1000.0 * 1.35 * 0.85, rel=0.01)


def test_get_month_found():
    model = SeasonalDemandModel()
    model.set_monthly_forecast(2022, 3, 'gas', 600.0)
    f = model.get_month(2022, 3, 'gas')
    assert f is not None
    assert f.base_mwh == pytest.approx(600.0)


def test_get_month_not_found():
    model = SeasonalDemandModel()
    assert model.get_month(2022, 3, 'gas') is None


def test_peak_month_returns_none_when_empty():
    model = SeasonalDemandModel()
    assert model.peak_month(2022, 'electricity') is None


def test_winter_summer_ratio_none_when_no_summer():
    model = SeasonalDemandModel()
    # Only set winter months — summer=0 → ratio=None
    for month in (11, 12, 1, 2, 3):
        model.set_monthly_forecast(2022, month, 'electricity', 1000.0)
    assert model.winter_summer_ratio(2022, 'electricity') is None


def test_annual_demand_excludes_wrong_year():
    model = SeasonalDemandModel()
    model.set_monthly_forecast(2021, 6, 'electricity', 800.0)
    model.set_monthly_forecast(2022, 6, 'electricity', 900.0)
    assert model.annual_demand_mwh(2022, 'electricity') == pytest.approx(900.0 * 0.80, rel=0.01)


def test_demand_summary_winter_summer_ratio_included():
    model = SeasonalDemandModel()
    for month in range(1, 13):
        model.set_monthly_forecast(2022, month, 'electricity', 1000.0)
    s = model.demand_summary(2022)
    assert 'winter_summer_ratio' in s
    assert 'electricity' in s['winter_summer_ratio']
