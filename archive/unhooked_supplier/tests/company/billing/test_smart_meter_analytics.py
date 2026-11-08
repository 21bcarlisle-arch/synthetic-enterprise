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


def test_is_morning_peak_true():
    # 07:00 -> period (7*60)//30+1 = 14+1 = 15 -> within 15-18
    r = HHReading('C001', dt.datetime(2022, 6, 1, 7, 0), 0.3)
    assert r.settlement_period == 15
    assert r.is_morning_peak


def test_is_morning_peak_false():
    # 12:00 -> period 25, outside morning range
    r = HHReading('C001', dt.datetime(2022, 6, 1, 12, 0), 0.3)
    assert not r.is_morning_peak


def test_morning_peak_boundary_upper():
    # 08:30 -> period (8*60+30)//30+1 = 17+1 = 18 -> within 15-18
    r = HHReading('C001', dt.datetime(2022, 6, 1, 8, 30), 0.3)
    assert r.settlement_period == 18
    assert r.is_morning_peak


def test_morning_peak_just_outside():
    # 09:00 -> period 19, just outside morning range
    r = HHReading('C001', dt.datetime(2022, 6, 1, 9, 0), 0.3)
    assert r.settlement_period == 19
    assert not r.is_morning_peak


def test_days_covered_single_day():
    a = SmartMeterAnalytics()
    a.ingest('C001', dt.datetime(2022, 6, 1, 10, 0), 0.3)
    p = a.profile('C001')
    assert p.days_covered == 1


def test_days_covered_multi_day():
    a = SmartMeterAnalytics()
    a.ingest('C001', dt.datetime(2022, 6, 1, 10, 0), 0.3)
    a.ingest('C001', dt.datetime(2022, 6, 3, 10, 0), 0.3)
    p = a.profile('C001')
    assert p.days_covered == 3  # June 1-3 inclusive


def test_off_peak_kwh():
    a = _make_analytics()
    p = a.profile('C001')
    assert p.off_peak_kwh == pytest.approx(p.total_kwh - p.peak_kwh, rel=0.01)


def test_avg_daily_kwh():
    a = SmartMeterAnalytics()
    a.ingest('C001', dt.datetime(2022, 6, 1, 10, 0), 2.0)
    a.ingest('C001', dt.datetime(2022, 6, 1, 14, 0), 3.0)
    p = a.profile('C001')
    assert p.avg_daily_kwh == pytest.approx(5.0, rel=0.01)


def test_load_factor_pct_within_range():
    a = _make_analytics()
    p = a.profile('C001')
    assert 0.0 <= p.load_factor_pct <= 100.0


def test_load_factor_zero_when_no_demand():
    a = SmartMeterAnalytics()
    a.ingest('C001', dt.datetime(2022, 6, 1, 12, 0), 0.0)
    p = a.profile('C001')
    assert p.load_factor_pct == 0.0


def test_customers_with_data_multiple():
    a = SmartMeterAnalytics()
    a.ingest('C001', dt.datetime(2022, 6, 1, 10, 0), 0.3)
    a.ingest('C002', dt.datetime(2022, 6, 1, 10, 0), 0.2)
    customers = a.customers_with_data()
    assert 'C001' in customers
    assert 'C002' in customers
    assert len(customers) == 2


def test_multi_customer_profile_isolation():
    a = SmartMeterAnalytics()
    a.ingest('C001', dt.datetime(2022, 6, 1, 10, 0), 1.0)
    a.ingest('C002', dt.datetime(2022, 6, 1, 10, 0), 5.0)
    p1 = a.profile('C001')
    assert p1.total_kwh == pytest.approx(1.0)
    assert p1.reading_count == 1


def test_peak_share_pct_zero_total():
    p = ConsumptionProfile(
        customer_id='CX', period_start=dt.date(2022, 1, 1), period_end=dt.date(2022, 1, 1),
        total_kwh=0.0, reading_count=0, peak_kwh=0.0, off_peak_kwh=0.0,
        avg_daily_kwh=0.0, max_demand_kw=0.0, load_factor_pct=0.0,
    )
    assert p.peak_share_pct == 0.0
