import datetime as dt
import pytest
from company.market.gas_otc_book import (
    GasTenor, GasTradeDirection, Season, GasOTCTrade, GasOTCBook, _season_from_month
)

TRADE_DATE = dt.date(2022, 7, 1)
DELIVERY = dt.date(2022, 8, 1)


def _trade(**kwargs):
    defaults = dict(
        trade_id="GT001",
        trade_date=TRADE_DATE,
        delivery_date=DELIVERY,
        tenor=GasTenor.MONTH_AHEAD,
        direction=GasTradeDirection.BUY,
        volume_therms=10_000.0,
        price_p_per_therm=250.0,
    )
    defaults.update(kwargs)
    return GasOTCTrade(**defaults)


def test_season_winter_months():
    assert _season_from_month(10) == Season.WINTER
    assert _season_from_month(1) == Season.WINTER
    assert _season_from_month(3) == Season.WINTER


def test_season_summer_months():
    assert _season_from_month(4) == Season.SUMMER
    assert _season_from_month(9) == Season.SUMMER


def test_trade_volume_mwh():
    t = _trade(volume_therms=1000.0)
    assert t.volume_mwh == pytest.approx(1000.0 * 0.02931, rel=0.001)


def test_trade_value_gbp_buy():
    t = _trade(volume_therms=1000.0, price_p_per_therm=100.0)
    assert t.trade_value_gbp == pytest.approx(1000.0)   # 1000 therms * 100p / 100


def test_trade_value_gbp_sell_negative():
    t = _trade(direction=GasTradeDirection.SELL, volume_therms=1000.0,
               price_p_per_therm=100.0)
    assert t.trade_value_gbp == pytest.approx(-1000.0)


def test_trade_is_crisis_price():
    t = _trade(price_p_per_therm=350.0)
    assert t.is_crisis_price is True


def test_trade_not_crisis_price():
    t = _trade(price_p_per_therm=65.0)
    assert t.is_crisis_price is False


def test_trade_delivery_season_summer():
    t = _trade(delivery_date=dt.date(2022, 7, 1))
    assert t.delivery_season == Season.SUMMER


def test_trade_delivery_season_winter():
    t = _trade(delivery_date=dt.date(2022, 11, 1))
    assert t.delivery_season == Season.WINTER


def test_book_net_position_long():
    book = GasOTCBook()
    book.record_trade("GT1", TRADE_DATE, DELIVERY, GasTenor.MONTH_AHEAD,
                      GasTradeDirection.BUY, 10_000.0, 250.0)
    book.record_trade("GT2", TRADE_DATE, DELIVERY, GasTenor.MONTH_AHEAD,
                      GasTradeDirection.SELL, 3_000.0, 260.0)
    net = book.net_position_therms(DELIVERY)
    assert net == pytest.approx(7_000.0)


def test_book_average_buy_price():
    book = GasOTCBook()
    book.record_trade("GT1", TRADE_DATE, DELIVERY, GasTenor.MONTH_AHEAD,
                      GasTradeDirection.BUY, 5_000.0, 200.0)
    book.record_trade("GT2", TRADE_DATE, DELIVERY, GasTenor.MONTH_AHEAD,
                      GasTradeDirection.BUY, 5_000.0, 300.0)
    avg = book.average_buy_price_p_th(2022, 8)
    assert avg == pytest.approx(250.0)


def test_book_seasonal_exposure():
    book = GasOTCBook()
    book.record_trade("GT1", TRADE_DATE, dt.date(2022, 7, 1),
                      GasTenor.SEASON_AHEAD, GasTradeDirection.BUY, 50_000.0, 200.0)
    book.record_trade("GT2", TRADE_DATE, dt.date(2022, 11, 1),
                      GasTenor.SEASON_AHEAD, GasTradeDirection.BUY, 80_000.0, 350.0)
    exp = book.seasonal_exposure_therms(2022)
    assert exp["summer"] == pytest.approx(50_000.0)
    assert exp["winter"] == pytest.approx(80_000.0)


def test_book_gas_book_summary():
    book = GasOTCBook()
    book.record_trade("GT1", dt.date(2022, 3, 1), dt.date(2022, 4, 1),
                      GasTenor.MONTH_AHEAD, GasTradeDirection.BUY, 20_000.0, 60.0)
    book.record_trade("GT2", dt.date(2022, 8, 1), dt.date(2022, 11, 1),
                      GasTenor.SEASON_AHEAD, GasTradeDirection.BUY, 100_000.0, 400.0)
    s = book.gas_book_summary(2022)
    assert s["total_trades"] == 2
    assert s["buy_volume_therms"] == pytest.approx(120_000.0)
    assert s["crisis_price_trades"] == 1
    assert "seasonal_exposure" in s
