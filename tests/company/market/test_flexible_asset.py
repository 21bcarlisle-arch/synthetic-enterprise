import datetime as dt
import pytest
from company.market.flexible_asset import (
    AssetType, DispatchMode, AssetDispatchInterval, FlexibleAsset
)


DATE = dt.date(2022, 1, 10)


def _bat() -> FlexibleAsset:
    return FlexibleAsset('BAT-001', AssetType.BATTERY_STORAGE, 10.0, 20.0)


def test_energy_mwh():
    i = AssetDispatchInterval(DATE, 30, DispatchMode.DISCHARGE, 10.0, 200.0)
    assert i.energy_mwh == pytest.approx(5.0)


def test_discharge_revenue_positive():
    i = AssetDispatchInterval(DATE, 30, DispatchMode.DISCHARGE, 10.0, 200.0)
    assert i.revenue_gbp == pytest.approx(1000.0)


def test_charge_revenue_negative():
    i = AssetDispatchInterval(DATE, 30, DispatchMode.CHARGE, 10.0, 50.0)
    assert i.revenue_gbp == pytest.approx(-250.0)


def test_standby_zero_revenue():
    i = AssetDispatchInterval(DATE, 30, DispatchMode.STANDBY, 0.0, 0.0)
    assert i.revenue_gbp == 0.0


def test_is_evening_peak():
    peak = AssetDispatchInterval(DATE, 36, DispatchMode.DISCHARGE, 10.0, 300.0)
    off_peak = AssetDispatchInterval(DATE, 10, DispatchMode.CHARGE, 10.0, 50.0)
    assert peak.is_evening_peak
    assert not off_peak.is_evening_peak


def test_charge_increases_soc():
    bat = _bat()
    bat.dispatch(DATE, 10, DispatchMode.CHARGE, 10.0, 50.0)
    assert bat.current_soc_mwh > 0


def test_roundtrip_efficiency():
    bat = _bat()
    bat.dispatch(DATE, 10, DispatchMode.CHARGE, 10.0, 50.0)
    expected_soc = 5.0 * 0.85
    assert bat.current_soc_mwh == pytest.approx(expected_soc, rel=0.01)


def test_discharge_reduces_soc():
    bat = _bat()
    bat.current_soc_mwh = 10.0
    bat.dispatch(DATE, 36, DispatchMode.DISCHARGE, 10.0, 200.0)
    assert bat.current_soc_mwh == pytest.approx(5.0)


def test_total_revenue():
    bat = _bat()
    bat.current_soc_mwh = 15.0
    bat.dispatch(DATE, 10, DispatchMode.CHARGE, 10.0, 50.0)
    bat.dispatch(DATE, 36, DispatchMode.DISCHARGE, 10.0, 200.0)
    revenue = bat.total_revenue_gbp(2022)
    assert revenue == pytest.approx(5.0 * 200.0 - 5.0 * 50.0)
