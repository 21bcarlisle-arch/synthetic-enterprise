"""Tests for T3: Mark-to-market valuation (Phase 71)."""

import pytest
from company.trading.forward_book import ForwardContract, TradingBook


def _contract(customer_id="C1", term_start="2016-01-01",
               agreed_price=50.0, notional_mwh=10.0, hf=0.85):
    return ForwardContract(
        customer_id=customer_id,
        term_start=term_start,
        term_end="2016-12-31",
        notional_mwh=notional_mwh,
        agreed_price_gbp_per_mwh=agreed_price,
        hedge_fraction=hf,
    )


def test_mark_to_market_in_the_money():
    book = TradingBook()
    c = _contract(agreed_price=50.0, notional_mwh=10.0)
    book.open_hedge(c)
    result = book.mark_to_market(c, current_price_gbp_per_mwh=70.0)
    assert result["mtm_pnl_gbp"] == pytest.approx(200.0)
    assert result["in_the_money"] is True


def test_mark_to_market_out_of_the_money():
    book = TradingBook()
    c = _contract(agreed_price=80.0, notional_mwh=10.0)
    book.open_hedge(c)
    result = book.mark_to_market(c, current_price_gbp_per_mwh=60.0)
    assert result["mtm_pnl_gbp"] == pytest.approx(-200.0)
    assert result["in_the_money"] is False


def test_mark_to_market_at_par():
    book = TradingBook()
    c = _contract(agreed_price=50.0, notional_mwh=5.0)
    book.open_hedge(c)
    result = book.mark_to_market(c, current_price_gbp_per_mwh=50.0)
    assert result["mtm_pnl_gbp"] == pytest.approx(0.0)
    assert result["in_the_money"] is False


def test_mark_to_market_structure():
    book = TradingBook()
    c = _contract()
    book.open_hedge(c)
    result = book.mark_to_market(c, 60.0)
    required = {"customer_id", "term_start", "notional_mwh", "agreed_price",
                "market_price", "mtm_pnl_gbp", "in_the_money"}
    assert set(result.keys()) == required
    assert result["customer_id"] == "C1"
    assert result["notional_mwh"] == 10.0


def test_portfolio_mtm_aggregates():
    book = TradingBook()
    book.open_hedge(_contract("C1", agreed_price=50.0, notional_mwh=10.0))
    book.open_hedge(_contract("C2", agreed_price=80.0, notional_mwh=5.0))
    prices = {"C1": 70.0, "C2": 60.0}
    result = book.portfolio_mtm(prices)
    assert result["total_mtm_pnl_gbp"] == pytest.approx(100.0)
    assert result["positions_priced"] == 2
    assert result["positions_in_the_money"] == 1
    assert result["positions_out_of_money"] == 1


def test_portfolio_mtm_skips_missing_prices():
    book = TradingBook()
    book.open_hedge(_contract("C1", agreed_price=50.0, notional_mwh=10.0))
    book.open_hedge(_contract("C2", agreed_price=50.0, notional_mwh=10.0))
    result = book.portfolio_mtm({"C1": 70.0})
    assert result["positions_priced"] == 1
    assert result["total_mtm_pnl_gbp"] == pytest.approx(200.0)


def test_portfolio_mtm_structure():
    book = TradingBook()
    book.open_hedge(_contract())
    result = book.portfolio_mtm({"C1": 60.0})
    assert "total_mtm_pnl_gbp" in result
    assert "positions_priced" in result
    assert "positions_in_the_money" in result
    assert "positions_out_of_money" in result
    assert "positions" in result
    assert isinstance(result["positions"], list)


def test_portfolio_mtm_empty_book():
    book = TradingBook()
    result = book.portfolio_mtm({"C1": 60.0})
    assert result["total_mtm_pnl_gbp"] == 0.0
    assert result["positions_priced"] == 0


def test_mtm_positive_when_market_rises():
    book = TradingBook()
    c = _contract(agreed_price=50.0, notional_mwh=100.0)
    book.open_hedge(c)
    r_low = book.mark_to_market(c, 55.0)
    r_high = book.mark_to_market(c, 75.0)
    assert r_high["mtm_pnl_gbp"] > r_low["mtm_pnl_gbp"]


def test_summary_still_works_after_mtm():
    book = TradingBook()
    book.open_hedge(_contract())
    book.portfolio_mtm({"C1": 70.0})
    s = book.summary()
    assert "contract_count" in s
    assert s["contract_count"] == 1


# --- Phase LF depth tests ---

def test_contract_customer_id_stored():
    c = _contract(customer_id='C_LF')
    assert c.customer_id == 'C_LF'


def test_contract_term_start_stored():
    c = _contract(term_start='2022-01-01')
    assert c.term_start == '2022-01-01'


def test_contract_agreed_price_stored():
    c = _contract(agreed_price=75.0)
    assert c.agreed_price_gbp_per_mwh == pytest.approx(75.0)


def test_contract_notional_mwh_stored():
    c = _contract(notional_mwh=20.0)
    assert c.notional_mwh == pytest.approx(20.0)


def test_contract_hedge_fraction_stored():
    c = _contract(hf=0.90)
    assert c.hedge_fraction == pytest.approx(0.90)


def test_contract_bid_ask_default_zero():
    c = _contract()
    assert c.bid_ask_cost_gbp == pytest.approx(0.0)


def test_trading_book_open_position_initially_empty():
    book = TradingBook()
    assert len(book.open_contracts()) == 0


def test_trading_book_mark_to_market_empty_zero():
    book = TradingBook()
    result = book.portfolio_mtm({})
    assert result['total_mtm_pnl_gbp'] == pytest.approx(0.0)


def test_forward_contract_term_end_stored():
    c = _contract()
    assert c.term_end == '2016-12-31'


def test_open_hedge_adds_to_positions():
    book = TradingBook()
    c = _contract()
    book.open_hedge(c)
    assert len(book.open_contracts()) == 1
