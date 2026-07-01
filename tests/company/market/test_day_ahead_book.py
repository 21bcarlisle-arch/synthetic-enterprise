import datetime as dt
import pytest
from company.market.day_ahead_book import DayAheadDirection, DayAheadAuction, DayAheadBook


D0 = dt.date(2022, 1, 15)  # delivery date
D_PREV = dt.datetime(2022, 1, 14, 11, 0)  # auctioned at (day before)


def _book_with_auctions():
    book = DayAheadBook()
    book.submit_auction("A1", D0, DayAheadDirection.BUY, 100.0, 50.0, 55.0, D_PREV)
    book.submit_auction("A2", D0, DayAheadDirection.SELL, 20.0, 50.0, 52.0, D_PREV)
    book.submit_auction("A3", dt.date(2022, 1, 16), DayAheadDirection.BUY, 80.0, 60.0, 400.0,
                        dt.datetime(2022, 1, 15, 11, 0))
    return book


def test_direction_enum_values():
    assert DayAheadDirection.BUY.value == "buy"
    assert DayAheadDirection.SELL.value == "sell"


def test_cost_gbp_buy_is_positive():
    a = DayAheadAuction("A1", D0, DayAheadDirection.BUY, 100.0, 50.0, 55.0, D_PREV)
    assert a.cost_gbp == pytest.approx(5500.0)


def test_cost_gbp_sell_is_negative():
    a = DayAheadAuction("A2", D0, DayAheadDirection.SELL, 20.0, 50.0, 52.0, D_PREV)
    assert a.cost_gbp == pytest.approx(-1040.0)


def test_vs_forward_spread_positive_and_negative():
    a_over = DayAheadAuction("X", D0, DayAheadDirection.BUY, 10.0, 50.0, 60.0, D_PREV)
    assert a_over.vs_forward_spread_gbp_per_mwh == pytest.approx(10.0)
    a_under = DayAheadAuction("Y", D0, DayAheadDirection.BUY, 10.0, 55.0, 50.0, D_PREV)
    assert a_under.vs_forward_spread_gbp_per_mwh == pytest.approx(-5.0)


def test_is_crisis_price():
    normal = DayAheadAuction("N", D0, DayAheadDirection.BUY, 10.0, 50.0, 280.0, D_PREV)
    crisis = DayAheadAuction("C", D0, DayAheadDirection.BUY, 10.0, 50.0, 450.0, D_PREV)
    assert not normal.is_crisis_price
    assert crisis.is_crisis_price


def test_submit_auction_raises_on_zero_volume():
    book = DayAheadBook()
    with pytest.raises(ValueError, match="positive"):
        book.submit_auction("X", D0, DayAheadDirection.BUY, 0.0, 50.0, 55.0, D_PREV)


def test_submit_auction_raises_when_auction_not_before_delivery():
    book = DayAheadBook()
    same_day = dt.datetime(2022, 1, 15, 11, 0)  # same day as delivery
    with pytest.raises(ValueError, match="before delivery_date"):
        book.submit_auction("X", D0, DayAheadDirection.BUY, 100.0, 50.0, 55.0, same_day)


def test_net_position_mwh():
    book = _book_with_auctions()
    net = book.net_position_mwh(D0)
    assert net == pytest.approx(80.0)  # 100 buy - 20 sell


def test_total_volume_and_cost_with_year_filter():
    book = _book_with_auctions()
    assert book.total_volume_mwh(2022) == pytest.approx(200.0)
    cost = book.total_cost_gbp(2022)
    # A1: 100*55=5500, A2: -20*52=-1040, A3: 80*400=32000
    assert cost == pytest.approx(5500.0 - 1040.0 + 32000.0)


def test_average_clearing_price_volume_weighted():
    book = DayAheadBook()
    book.submit_auction("A", D0, DayAheadDirection.BUY, 100.0, 50.0, 50.0, D_PREV)
    book.submit_auction("B", D0, DayAheadDirection.BUY, 100.0, 50.0, 100.0, D_PREV)
    avg = book.average_clearing_price()
    assert avg == pytest.approx(75.0)


def test_average_clearing_price_none_when_empty():
    book = DayAheadBook()
    assert book.average_clearing_price() is None


def test_crisis_auctions_returns_above_threshold():
    book = _book_with_auctions()  # A3 cleared at 400
    crises = book.crisis_auctions(300.0)
    assert len(crises) == 1
    assert crises[0].auction_id == "A3"


def test_monthly_summary_keys_and_values():
    book = _book_with_auctions()
    summary = book.monthly_summary(2022, 1)
    assert summary["month"] == "2022-01"
    assert summary["auction_count"] == 3
    assert summary["buy_volume_mwh"] == pytest.approx(180.0)
    assert summary["sell_volume_mwh"] == pytest.approx(20.0)
    assert summary["net_volume_mwh"] == pytest.approx(160.0)
    assert summary["crisis_count"] == 1


def test_day_ahead_summary_empty_book():
    book = DayAheadBook()
    s = book.day_ahead_summary()
    assert s["total_auctions"] == 0
    assert s["avg_clearing_price"] is None
    assert s["years_active"] == []


def test_day_ahead_summary_populated():
    book = _book_with_auctions()
    s = book.day_ahead_summary()
    assert s["total_auctions"] == 3
    assert s["total_buy_volume_mwh"] == pytest.approx(180.0)
    assert s["total_sell_volume_mwh"] == pytest.approx(20.0)
    assert s["years_active"] == [2022]
    assert s["crisis_auctions_count"] == 1


# --- Phase MQ depth tests ---

def test_auction_id_stored():
    a = DayAheadAuction("A99", D0, DayAheadDirection.BUY, 100.0, 50.0, 55.0, D_PREV)
    assert a.auction_id == "A99"


def test_delivery_date_stored():
    a = DayAheadAuction("A1", D0, DayAheadDirection.BUY, 100.0, 50.0, 55.0, D_PREV)
    assert a.delivery_date == D0


def test_direction_stored():
    a = DayAheadAuction("A1", D0, DayAheadDirection.SELL, 100.0, 50.0, 55.0, D_PREV)
    assert a.direction == DayAheadDirection.SELL


def test_volume_mwh_stored():
    a = DayAheadAuction("A1", D0, DayAheadDirection.BUY, 150.0, 50.0, 55.0, D_PREV)
    assert a.volume_mwh == pytest.approx(150.0)


def test_bid_price_stored():
    a = DayAheadAuction("A1", D0, DayAheadDirection.BUY, 100.0, 48.0, 55.0, D_PREV)
    assert a.bid_price_gbp_per_mwh == pytest.approx(48.0)


def test_cleared_price_stored():
    a = DayAheadAuction("A1", D0, DayAheadDirection.BUY, 100.0, 48.0, 57.0, D_PREV)
    assert a.cleared_price_gbp_per_mwh == pytest.approx(57.0)


def test_auctioned_at_stored():
    a = DayAheadAuction("A1", D0, DayAheadDirection.BUY, 100.0, 50.0, 55.0, D_PREV)
    assert a.auctioned_at == D_PREV


def test_day_ahead_direction_count():
    assert len(list(DayAheadDirection)) == 2


def test_submit_auction_returns_day_ahead_auction():
    book = DayAheadBook()
    result = book.submit_auction("A1", D0, DayAheadDirection.BUY, 100.0, 50.0, 55.0, D_PREV)
    assert isinstance(result, DayAheadAuction)


def test_auctions_for_month_filters_correctly():
    book = _book_with_auctions()
    jan = book.auctions_for_month(2022, 1)
    assert len(jan) == 3
    feb = book.auctions_for_month(2022, 2)
    assert len(feb) == 0
