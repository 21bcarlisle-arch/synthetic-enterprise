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


# --- Phase MM depth tests ---

def test_settlement_date_stored():
    snap = make_snap(date=dt.date(2022, 12, 1))
    assert snap.settlement_date == dt.date(2022, 12, 1)


def test_session_stored_in_snapshot():
    snap = make_snap(session=GasMarketSession.SEASON_AHEAD)
    assert snap.session == GasMarketSession.SEASON_AHEAD


def test_price_pence_per_therm_stored():
    snap = make_snap(price=350.0)
    assert snap.price_pence_per_therm == pytest.approx(350.0)


def test_volume_therm_default_zero():
    snap = GasMarketSnapshot(settlement_date=DATE, session=GasMarketSession.DAY_AHEAD, price_pence_per_therm=70.0)
    assert snap.volume_therm == pytest.approx(0.0)


def test_gas_market_session_has_5_members():
    assert len(list(GasMarketSession)) == 5


def test_record_price_returns_snapshot():
    monitor = GasMarketMonitor()
    snap = make_snap()
    result = monitor.record_price(snap)
    assert isinstance(result, GasMarketSnapshot)


def test_purchase_date_stored():
    p = make_purchase(date=dt.date(2022, 11, 1))
    assert p.purchase_date == dt.date(2022, 11, 1)


def test_purchase_session_stored():
    p = GasPurchaseRecord(purchase_date=DATE, session=GasMarketSession.WITHIN_DAY, volume_therm=500.0, price_pence_per_therm=80.0)
    assert p.session == GasMarketSession.WITHIN_DAY


def test_purchase_volume_therm_stored():
    p = make_purchase(vol=3000.0)
    assert p.volume_therm == pytest.approx(3000.0)


def test_purchase_price_pence_per_therm_stored():
    p = make_purchase(price=125.0)
    assert p.price_pence_per_therm == pytest.approx(125.0)
