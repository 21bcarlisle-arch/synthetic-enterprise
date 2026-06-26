import datetime as dt
import pytest
from company.market.imbalance_analytics import (
    ImbalanceDirection, ImbalanceRecord, ImbalanceAnalytics
)


def test_direction_long():
    r = ImbalanceRecord(dt.date(2022, 1, 1), 33, 'electricity', 5.0, 200.0)
    assert r.direction == ImbalanceDirection.LONG


def test_direction_short():
    r = ImbalanceRecord(dt.date(2022, 1, 1), 33, 'electricity', -3.0, 300.0)
    assert r.direction == ImbalanceDirection.SHORT


def test_cash_out_cost():
    r = ImbalanceRecord(dt.date(2022, 1, 1), 1, 'electricity', -2.0, 350.0)
    assert r.cash_out_cost_gbp == pytest.approx(700.0)


def test_total_cash_out():
    a = ImbalanceAnalytics()
    a.record(dt.date(2022, 3, 1), 33, 'electricity', -5.0, 200.0)
    a.record(dt.date(2022, 3, 2), 34, 'electricity', 2.0, 180.0)
    total = a.total_cash_out_gbp(2022)
    assert total == pytest.approx(1000.0 + 360.0)


def test_net_imbalance_mwh():
    a = ImbalanceAnalytics()
    a.record(dt.date(2022, 4, 1), 1, 'electricity', -3.0, 200.0)
    a.record(dt.date(2022, 4, 2), 1, 'electricity', 1.0, 180.0)
    assert a.net_imbalance_mwh(2022) == pytest.approx(-2.0)


def test_systematic_bias_short():
    a = ImbalanceAnalytics()
    a.record(dt.date(2022, 1, 1), 1, 'gas', -10.0, 50.0)
    a.record(dt.date(2022, 1, 2), 1, 'gas', -5.0, 55.0)
    assert a.systematic_bias(2022) == ImbalanceDirection.SHORT


def test_worst_period():
    a = ImbalanceAnalytics()
    a.record(dt.date(2022, 2, 1), 33, 'electricity', -1.0, 100.0)
    a.record(dt.date(2022, 2, 2), 34, 'electricity', -5.0, 400.0)
    worst = a.worst_period(2022)
    assert worst is not None
    assert worst.cash_out_cost_gbp == pytest.approx(2000.0)


def test_avg_cash_out_per_mwh():
    a = ImbalanceAnalytics()
    a.record(dt.date(2022, 5, 1), 1, 'electricity', -4.0, 300.0)
    a.record(dt.date(2022, 5, 2), 2, 'electricity', -2.0, 300.0)
    avg = a.avg_cash_out_per_mwh(2022)
    assert avg == pytest.approx(300.0)


def test_imbalance_summary():
    a = ImbalanceAnalytics()
    a.record(dt.date(2022, 6, 1), 1, 'electricity', -3.0, 250.0)
    s = a.imbalance_summary(2022)
    assert s['total_records'] == 1
    assert s['systematic_bias'] == 'short'
    assert s['short_periods'] == 1
