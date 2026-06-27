import pytest
import math
from company.trading.forward_book import (
    ForwardContract,
    HedgePnL,
    HedgeAmendment,
    PositionClosure,
    TradingBook,
)


def _contract(cid="C1", term="2022-01-01", notional=10.0, agreed=80.0, hf=0.9, ba=0.0):
    return ForwardContract(
        customer_id=cid,
        term_start=term,
        term_end="2023-01-01",
        notional_mwh=notional,
        agreed_price_gbp_per_mwh=agreed,
        hedge_fraction=hf,
        bid_ask_cost_gbp=ba,
    )


class TestForwardContract:
    def test_fields(self):
        c = _contract()
        assert c.customer_id == "C1"
        assert c.notional_mwh == 10.0
        assert c.hedge_fraction == 0.9

    def test_bid_ask_default_zero(self):
        c = ForwardContract("C1", "2022-01-01", "2023-01-01", 10.0, 80.0, 0.9)
        assert c.bid_ask_cost_gbp == 0.0

    def test_frozen(self):
        c = _contract()
        with pytest.raises((AttributeError, TypeError)):
            c.notional_mwh = 99.0


class TestTradingBook:
    def _book_with_one(self):
        book = TradingBook()
        book.open_hedge(_contract("C1", "2022-01-01", notional=10.0, agreed=80.0, hf=0.9, ba=5.0))
        return book

    def test_contract_count_after_open(self):
        book = self._book_with_one()
        assert book.contract_count == 1

    def test_total_bid_ask_cost_added(self):
        book = self._book_with_one()
        assert book.total_bid_ask_cost_gbp == pytest.approx(5.0)

    def test_settle_period_profit(self):
        book = self._book_with_one()
        # agreed=80, spot=60: hedged well, pnl positive
        result = book.settle_period("C1", "2022-01-01", consumed_kwh=1000.0, actual_spot_gbp_per_mwh=60.0)
        # hedged_mwh = 1000/1000 * 0.9 = 0.9; pnl = (80-60)*0.9 = 18
        assert isinstance(result, HedgePnL)
        assert result.pnl_gbp == pytest.approx(18.0)
        assert result.hedged_mwh == pytest.approx(0.9)

    def test_settle_period_loss(self):
        book = self._book_with_one()
        # agreed=80, spot=100: hedge lost money (locked in above spot)
        result = book.settle_period("C1", "2022-01-01", consumed_kwh=1000.0, actual_spot_gbp_per_mwh=100.0)
        assert result.pnl_gbp == pytest.approx(-18.0)

    def test_settle_period_no_contract_returns_zero(self):
        book = TradingBook()
        result = book.settle_period("UNKNOWN", "2022-01-01", 1000.0, 80.0)
        assert result.hedged_mwh == 0.0
        assert result.pnl_gbp == 0.0

    def test_total_pnl_accumulates(self):
        book = self._book_with_one()
        book.settle_period("C1", "2022-01-01", 1000.0, 60.0)  # +18
        book.settle_period("C1", "2022-01-01", 1000.0, 60.0)  # +18
        assert book.total_pnl_gbp == pytest.approx(36.0)

    def test_total_hedged_mwh_accumulates(self):
        book = self._book_with_one()
        book.settle_period("C1", "2022-01-01", 1000.0, 80.0)
        book.settle_period("C1", "2022-01-01", 2000.0, 80.0)
        assert book.total_hedged_mwh == pytest.approx(2.7)

    def test_open_contracts_excludes_closed(self):
        book = self._book_with_one()
        book.close_position("C1", "2022-01-01", "2023-01-01", 90.0)
        assert len(book.open_contracts()) == 0
        assert len(book.closed_contracts()) == 1

    def test_amend_hedge_records_old_and_new(self):
        book = self._book_with_one()
        amendment = book.amend_hedge("C1", "2022-01-01", 0.95, "2022-06-01", "risk limit")
        assert isinstance(amendment, HedgeAmendment)
        assert amendment.old_hedge_fraction == pytest.approx(0.9)
        assert amendment.new_hedge_fraction == pytest.approx(0.95)

    def test_close_position_realised_pnl(self):
        book = self._book_with_one()
        closure = book.close_position("C1", "2022-01-01", "2023-01-01", close_price_gbp_per_mwh=90.0)
        assert isinstance(closure, PositionClosure)
        # realised = (close_price - agreed) * notional = (90-80)*10 = 100
        assert closure.realised_pnl_gbp == pytest.approx(100.0)

    def test_mark_to_market_in_the_money(self):
        book = self._book_with_one()
        c = book.open_contracts()[0]
        mtm = book.mark_to_market(c, current_price_gbp_per_mwh=100.0)
        # (100-80)*10 = 200 -> in the money
        assert mtm["mtm_pnl_gbp"] == pytest.approx(200.0)
        assert mtm["in_the_money"] is True

    def test_mark_to_market_out_of_the_money(self):
        book = self._book_with_one()
        c = book.open_contracts()[0]
        mtm = book.mark_to_market(c, current_price_gbp_per_mwh=70.0)
        # (70-80)*10 = -100 -> out of the money
        assert mtm["mtm_pnl_gbp"] == pytest.approx(-100.0)
        assert mtm["in_the_money"] is False

    def test_portfolio_mtm_aggregates(self):
        book = TradingBook()
        book.open_hedge(_contract("C1", "2022-01-01", notional=10.0, agreed=80.0))
        book.open_hedge(_contract("C2", "2022-01-01", notional=5.0, agreed=80.0))
        result = book.portfolio_mtm({"C1": 90.0, "C2": 70.0})
        # C1: (90-80)*10=100, C2: (70-80)*5=-50, total=50
        assert result["total_mtm_pnl_gbp"] == pytest.approx(50.0)
        assert result["positions_in_the_money"] == 1
        assert result["positions_out_of_money"] == 1

    def test_portfolio_mtm_skips_missing_price(self):
        book = TradingBook()
        book.open_hedge(_contract("C1", "2022-01-01"))
        result = book.portfolio_mtm({})  # no prices
        assert result["positions_priced"] == 0

    def test_summary_keys(self):
        book = self._book_with_one()
        s = book.summary()
        for k in ("contract_count", "total_hedged_mwh", "total_hedge_pnl_gbp", "total_bid_ask_cost_gbp"):
            assert k in s

    def test_multiple_customers_independent(self):
        book = TradingBook()
        book.open_hedge(_contract("C1", "2022-01-01", agreed=80.0))
        book.open_hedge(_contract("C2", "2022-01-01", agreed=50.0))
        r1 = book.settle_period("C1", "2022-01-01", 1000.0, 60.0)
        r2 = book.settle_period("C2", "2022-01-01", 1000.0, 60.0)
        assert r1.pnl_gbp == pytest.approx(18.0)   # (80-60)*0.9
        assert r2.pnl_gbp == pytest.approx(-9.0)   # (50-60)*0.9
