import datetime as dt
import pytest
from company.billing.smart_meter_analytics import (
    HHReading, ConsumptionProfile, SmartMeterAnalytics, build_consumption_profile
)


def _make_analytics() -> SmartMeterAnalytics:
    a = SmartMeterAnalytics()
    base = dt.date(2022, 6, 1)
    # Add 48 half-hourly readings for one full day
    for sp in range(48):
        hour, minute = divmod(sp * 30, 60)
        ts = dt.datetime(2022, 6, 1, hour, minute)
        kwh = 0.5 if 32 <= sp <= 39 else 0.1  # evening peak higher
        a.ingest('C001', ts, kwh)
    return a


def test_settlement_period():
    r = HHReading('C001', dt.datetime(2022, 6, 1, 16, 0), 0.5)
    assert r.settlement_period == 33


def test_is_evening_peak():
    r = HHReading('C001', dt.datetime(2022, 6, 1, 17, 30), 0.5)
    assert r.is_evening_peak
    r2 = HHReading('C001', dt.datetime(2022, 6, 1, 10, 0), 0.1)
    assert not r2.is_evening_peak


def test_build_profile():
    a = _make_analytics()
    p = a.profile('C001')
    assert p is not None
    assert p.customer_id == 'C001'
    assert p.reading_count == 48


def test_total_kwh():
    a = _make_analytics()
    p = a.profile('C001')
    # 8 peak periods at 0.5 + 40 off-peak at 0.1
    expected = 8 * 0.5 + 40 * 0.1
    assert p.total_kwh == pytest.approx(expected, rel=0.01)


def test_peak_share():
    a = _make_analytics()
    p = a.profile('C001')
    assert p.peak_share_pct > 30.0


def test_max_demand_kw():
    a = _make_analytics()
    p = a.profile('C001')
    # max HH = 0.5 kWh -> 1.0 kW
    assert p.max_demand_kw == pytest.approx(1.0)


def test_no_data_returns_none():
    a = SmartMeterAnalytics()
    assert a.profile('C999') is None


def test_evening_peak_customers():
    a = _make_analytics()
    high_peak = a.evening_peak_customers(threshold_pct=30.0)
    assert 'C001' in high_peak


def test_high_demand_customers():
    a = _make_analytics()
    hd = a.high_demand_customers(threshold_kw=0.8)
    assert 'C001' in hd
    no_hd = a.high_demand_customers(threshold_kw=2.0)
    assert 'C001' not in no_hd
