"""Tests for Wholesale Power Auction Monitor (Phase FM)."""
import datetime as dt
import pytest
from company.trading.power_auction_monitor import (
    AuctionType, MarketCondition, AuctionResult, PowerAuctionMonitor,
)

DATE = dt.date(2024, 1, 15)


def make_result(price=80.0, sp=20, vol=100.0, date=DATE):
    return AuctionResult(
        delivery_date=date, settlement_period=sp,
        auction_type=AuctionType.DAY_AHEAD,
        clearing_price_gbp_per_mwh=price, volume_mwh=vol,
    )


class TestAuctionResult:
    def test_is_peak_sp20(self):
        r = make_result(sp=20)  # SP20 = 09:30-10:00 -> peak
        assert r.is_peak

    def test_not_peak_sp5(self):
        r = make_result(sp=5)  # SP5 = 02:00-02:30 -> off-peak
        assert not r.is_peak

    def test_market_condition_normal(self):
        assert make_result(price=80.0).market_condition == MarketCondition.NORMAL

    def test_market_condition_elevated(self):
        assert make_result(price=180.0).market_condition == MarketCondition.ELEVATED

    def test_market_condition_crisis(self):
        assert make_result(price=300.0).market_condition == MarketCondition.CRISIS

    def test_market_condition_negative(self):
        assert make_result(price=-5.0).market_condition == MarketCondition.NEGATIVE

    def test_is_crisis(self):
        assert make_result(price=300.0).is_crisis_price

    def test_total_value(self):
        r = make_result(price=100.0, vol=50.0)
        assert r.total_value_gbp == pytest.approx(5000.0)

    def test_result_summary(self):
        s = make_result().result_summary()
        assert "GBP/MWh" in s


class TestPowerAuctionMonitor:
    def test_record_and_avg(self):
        m = PowerAuctionMonitor()
        m.record(make_result(price=80.0))
        m.record(make_result(price=120.0))
        assert m.avg_clearing_price() == pytest.approx(100.0)

    def test_results_for_date(self):
        m = PowerAuctionMonitor()
        m.record(make_result(date=DATE))
        m.record(make_result(date=dt.date(2024, 2, 1)))
        assert len(m.results_for_date(DATE)) == 1

    def test_daily_avg_price(self):
        m = PowerAuctionMonitor()
        m.record(make_result(price=80.0))
        m.record(make_result(price=100.0))
        assert m.daily_avg_price(DATE) == pytest.approx(90.0)

    def test_crisis_results(self):
        m = PowerAuctionMonitor()
        m.record(make_result(price=300.0))
        m.record(make_result(price=80.0))
        assert len(m.crisis_results()) == 1

    def test_negative_price(self):
        m = PowerAuctionMonitor()
        m.record(make_result(price=-10.0))
        assert len(m.negative_price_results()) == 1

    def test_max_price(self):
        m = PowerAuctionMonitor()
        m.record(make_result(price=80.0))
        m.record(make_result(price=300.0))
        assert m.max_clearing_price() == pytest.approx(300.0)

    def test_auction_monitor_summary(self):
        m = PowerAuctionMonitor()
        m.record(make_result())
        s = m.auction_monitor_summary()
        assert "Power Auction Monitor" in s
