"""Tests for Wholesale Gas Market Monitor (Phase FF)."""
import datetime as dt
import pytest
from company.trading.gas_market_monitor import (
    GasMarketSession, GasMarketSnapshot, GasPurchaseRecord,
    GasMarketMonitor, _THERMS_PER_MWH,
)

DATE = dt.date(2024, 1, 15)


def make_snap(price=70.0, vol=0.0, session=GasMarketSession.DAY_AHEAD, date=DATE):
    return GasMarketSnapshot(settlement_date=date, session=session,
                              price_pence_per_therm=price, volume_therm=vol)


def make_purchase(price=70.0, vol=1000.0, date=DATE):
    return GasPurchaseRecord(purchase_date=date, session=GasMarketSession.DAY_AHEAD,
                              volume_therm=vol, price_pence_per_therm=price)


class TestGasMarketSnapshot:
    def test_price_gbp_per_mwh(self):
        snap = make_snap(price=100.0)
        expected = 100.0 * _THERMS_PER_MWH * 100
        assert snap.price_gbp_per_mwh == pytest.approx(expected)

    def test_is_crisis_price(self):
        assert make_snap(price=300.0).is_crisis_price

    def test_not_crisis_price(self):
        assert not make_snap(price=70.0).is_crisis_price

    def test_below_normal(self):
        assert make_snap(price=20.0).is_below_normal_range

    def test_snapshot_summary(self):
        s = make_snap(price=300.0).snapshot_summary()
        assert "CRISIS" in s


class TestGasPurchaseRecord:
    def test_total_cost(self):
        p = make_purchase(price=70.0, vol=1000.0)
        assert p.total_cost_gbp == pytest.approx(700.0)


class TestGasMarketMonitor:
    def test_record_and_latest_price(self):
        m = GasMarketMonitor()
        m.record_price(make_snap())
        assert m.latest_price(GasMarketSession.DAY_AHEAD) is not None

    def test_latest_price_returns_most_recent(self):
        m = GasMarketMonitor()
        m.record_price(make_snap(price=60.0, date=dt.date(2024, 1, 1)))
        m.record_price(make_snap(price=70.0, date=dt.date(2024, 2, 1)))
        latest = m.latest_price(GasMarketSession.DAY_AHEAD)
        assert latest.price_pence_per_therm == 70.0

    def test_avg_price(self):
        m = GasMarketMonitor()
        m.record_price(make_snap(price=60.0))
        m.record_price(make_snap(price=80.0))
        assert m.avg_price_pence_per_therm() == pytest.approx(70.0)

    def test_crisis_periods(self):
        m = GasMarketMonitor()
        m.record_price(make_snap(price=400.0))
        m.record_price(make_snap(price=70.0))
        assert len(m.crisis_periods()) == 1

    def test_wapp(self):
        m = GasMarketMonitor()
        m.record_purchase(make_purchase(price=70.0, vol=1000.0))
        m.record_purchase(make_purchase(price=80.0, vol=1000.0))
        assert m.wapp_pence_per_therm() == pytest.approx(75.0)

    def test_total_purchases(self):
        m = GasMarketMonitor()
        m.record_purchase(make_purchase(vol=500.0))
        m.record_purchase(make_purchase(vol=300.0))
        assert m.total_purchases_therm() == pytest.approx(800.0)

    def test_gas_market_summary(self):
        m = GasMarketMonitor()
        m.record_price(make_snap())
        s = m.gas_market_summary()
        assert "Gas Market Monitor" in s
