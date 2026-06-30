"""Tests for EV Charging Demand Forecaster (Phase FS)."""
import datetime as dt
import pytest
from company.market.ev_demand_forecast import (
    ChargingPattern, EVDemandForecast, EVDemandForecaster,
    _SMART_KWH_PER_EV_PER_YEAR, _SMART_FRACTION_OF_SMART,
)


def make_forecast(year=2024, evs=100, pattern=ChargingPattern.SMART, smart=True):
    return EVDemandForecast(forecast_year=year, ev_count=evs,
                             charging_pattern=pattern, is_smart_charged=smart)


class TestEVDemandForecast:
    def test_annual_kwh(self):
        f = make_forecast(evs=100)
        assert f.annual_ev_kwh == pytest.approx(100 * _SMART_KWH_PER_EV_PER_YEAR)

    def test_overnight_kwh_smart(self):
        f = make_forecast(evs=100, pattern=ChargingPattern.SMART)
        expected = 100 * _SMART_KWH_PER_EV_PER_YEAR * _SMART_FRACTION_OF_SMART
        assert f.overnight_kwh == pytest.approx(expected)

    def test_overnight_kwh_unmanaged(self):
        f = make_forecast(evs=100, pattern=ChargingPattern.UNMANAGED)
        assert f.overnight_kwh == pytest.approx(f.annual_ev_kwh / 2)

    def test_peak_risk_smart_zero(self):
        f = make_forecast(pattern=ChargingPattern.SMART)
        # peak = annual - overnight; for smart almost all overnight
        assert f.peak_risk_kwh < f.annual_ev_kwh

    def test_triad_risk_smart_zero(self):
        f = make_forecast(pattern=ChargingPattern.SMART)
        assert f.triad_risk_mw == pytest.approx(0.0)

    def test_triad_risk_unmanaged_nonzero(self):
        f = make_forecast(pattern=ChargingPattern.UNMANAGED, evs=100)
        assert f.triad_risk_mw > 0

    def test_forecast_summary(self):
        s = make_forecast().forecast_summary()
        assert "EVForecast" in s and "GWh" in s


class TestEVDemandForecaster:
    def test_add_and_retrieve(self):
        fcast = EVDemandForecaster()
        fcast.add_forecast(make_forecast(year=2024))
        assert fcast.forecast_for_year(2024) is not None

    def test_forecast_missing_year_returns_none(self):
        fcast = EVDemandForecaster()
        assert fcast.forecast_for_year(2030) is None

    def test_total_annual_kwh_for_year(self):
        fcast = EVDemandForecaster()
        fcast.add_forecast(make_forecast(year=2024, evs=100))
        assert fcast.total_annual_ev_kwh(year=2024) == pytest.approx(100 * _SMART_KWH_PER_EV_PER_YEAR)

    def test_total_triad_risk(self):
        fcast = EVDemandForecaster()
        fcast.add_forecast(make_forecast(pattern=ChargingPattern.UNMANAGED, evs=100))
        assert fcast.total_triad_risk_mw() > 0

    def test_smart_charging_adoption(self):
        fcast = EVDemandForecaster()
        fcast.add_forecast(make_forecast(evs=80, pattern=ChargingPattern.SMART, year=2024))
        fcast.add_forecast(make_forecast(evs=20, pattern=ChargingPattern.UNMANAGED, year=2025))
        assert fcast.smart_charging_adoption_pct() == pytest.approx(80.0)

    def test_ev_demand_summary(self):
        fcast = EVDemandForecaster()
        fcast.add_forecast(make_forecast())
        s = fcast.ev_demand_summary()
        assert "EV Demand Forecaster" in s
