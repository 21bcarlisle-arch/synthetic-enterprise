import datetime as dt
import pytest
from company.market.intraday_book import (
    TradeDirection, TradeReason, IntradayTrade, IntradayBook
)

DATE = dt.date(2022, 11, 1)
AT = dt.datetime(2022, 11, 1, 8, 30)


def _book_with_trades():
    book = IntradayBook()
    book.record_trade("T001", DATE, 10, TradeDirection.BUY, 2.0, 80.0, AT)
    book.record_trade("T002", DATE, 10, TradeDirection.SELL, 1.5, 95.0, AT)
    book.record_trade("T003", DATE, 20, TradeDirection.BUY, 3.0, 75.0, AT)
    return book


def test_trade_volume_mwh():
    t = IntradayTrade(
        trade_id="T", settlement_date=DATE, settlement_period=1,
        direction=TradeDirection.BUY, volume_mw=4.0, price_gbp_per_mwh=100.0,
        traded_at=AT,
    )
    assert t.volume_mwh == pytest.approx(2.0)


def test_trade_value_gbp_buy_is_positive_cost():
    t = IntradayTrade(
        trade_id="T", settlement_date=DATE, settlement_period=5,
        direction=TradeDirection.BUY, volume_mw=2.0, price_gbp_per_mwh=100.0,
        traded_at=AT,
    )
    assert t.trade_value_gbp == pytest.approx(100.0)   # 1 MWh * £100


def test_trade_value_gbp_sell_is_negative():
    t = IntradayTrade(
        trade_id="T", settlement_date=DATE, settlement_period=5,
        direction=TradeDirection.SELL, volume_mw=2.0, price_gbp_per_mwh=100.0,
        traded_at=AT,
    )
    assert t.trade_value_gbp == pytest.approx(-100.0)  # revenue


def test_trade_is_crisis_price():
    t = IntradayTrade(
        trade_id="T", settlement_date=DATE, settlement_period=33,
        direction=TradeDirection.BUY, volume_mw=1.0, price_gbp_per_mwh=4500.0,
        traded_at=AT,
    )
    assert t.is_crisis_price is True


def test_trade_not_crisis_price():
    t = IntradayTrade(
        trade_id="T", settlement_date=DATE, settlement_period=33,
        direction=TradeDirection.BUY, volume_mw=1.0, price_gbp_per_mwh=85.0,
        traded_at=AT,
    )
    assert t.is_crisis_price is False


def test_book_rejects_invalid_period():
    book = IntradayBook()
    with pytest.raises(ValueError):
        book.record_trade("T", DATE, 0, TradeDirection.BUY, 1.0, 80.0, AT)
    with pytest.raises(ValueError):
        book.record_trade("T", DATE, 49, TradeDirection.BUY, 1.0, 80.0, AT)


def test_book_trades_for_date():
    book = _book_with_trades()
    other_date = dt.date(2022, 11, 2)
    book.record_trade("T099", other_date, 1, TradeDirection.BUY, 1.0, 70.0, AT)
    assert len(book.trades_for_date(DATE)) == 3
    assert len(book.trades_for_date(other_date)) == 1


def test_net_position_mwh_all_periods():
    book = _book_with_trades()
    # T001: SELL perspective: bought 1 MWh, sold 0.75 MWh, bought 1.5 MWh
    # net_position = sold - bought = 0.75 - 2.5 = -1.75 (net short)
    net = book.net_position_mwh(DATE)
    # buy T001: 2.0MW * 0.5 = 1 MWh, buy T003: 3.0MW * 0.5 = 1.5 MWh
    # sell T002: 1.5MW * 0.5 = 0.75 MWh
    assert net == pytest.approx(0.75 - 1.0 - 1.5, abs=1e-4)


def test_net_position_mwh_by_period():
    book = _book_with_trades()
    # period 10: T001 buy 1 MWh, T002 sell 0.75 MWh -> net = 0.75 - 1.0 = -0.25
    net = book.net_position_mwh(DATE, settlement_period=10)
    assert net == pytest.approx(-0.25, abs=1e-4)


def test_daily_pnl_gbp():
    book = IntradayBook()
    book.record_trade("T1", DATE, 5, TradeDirection.BUY, 2.0, 80.0, AT)   # cost: 1 MWh * 80 = £80
    book.record_trade("T2", DATE, 5, TradeDirection.SELL, 2.0, 100.0, AT)  # revenue: 1 MWh * 100 = £100
    pnl = book.daily_pnl_gbp(DATE)
    assert pnl == pytest.approx(20.0)   # sold 100 - bought 80


def test_crisis_trades_filter():
    book = IntradayBook()
    book.record_trade("T1", DATE, 35, TradeDirection.BUY, 1.0, 4500.0, AT)  # crisis
    book.record_trade("T2", DATE, 36, TradeDirection.BUY, 1.0, 90.0, AT)    # normal
    crisis = book.crisis_trades()
    assert len(crisis) == 1
    assert crisis[0].trade_id == "T1"


def test_intraday_summary():
    book = _book_with_trades()
    s = book.intraday_summary(DATE)
    assert s["total_trades"] == 3
    assert s["buy_trades"] == 2
    assert s["sell_trades"] == 1
    assert s["buy_volume_mwh"] == pytest.approx(2.5)   # (2.0 + 3.0) * 0.5
    assert s["sell_volume_mwh"] == pytest.approx(0.75)
    assert "daily_pnl_gbp" in s
    assert "net_position_mwh" in s
