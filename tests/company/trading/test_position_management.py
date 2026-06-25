"""Tests for T2: Position management -- amendment and closure (Phase 72)."""

import pytest
from company.trading.forward_book import (
    ForwardContract,
    HedgeAmendment,
    PositionClosure,
    TradingBook,
)


def _c(customer_id="C1", agreed_price=50.0, notional_mwh=10.0, hf=0.85):
    return ForwardContract(
        customer_id=customer_id,
        term_start="2016-01-01",
        term_end="2016-12-31",
        notional_mwh=notional_mwh,
        agreed_price_gbp_per_mwh=agreed_price,
        hedge_fraction=hf,
    )


def test_amend_hedge_creates_amendment_record():
    book = TradingBook()
    book.open_hedge(_c())
    a = book.amend_hedge("C1", "2016-01-01", 0.95, "2016-06-01", "risk review")
    assert isinstance(a, HedgeAmendment)
    assert a.new_hedge_fraction == 0.95
    assert a.old_hedge_fraction == pytest.approx(0.85)


def test_amend_hedge_records_old_fraction():
    book = TradingBook()
    book.open_hedge(_c(hf=0.70))
    a = book.amend_hedge("C1", "2016-01-01", 0.90, "2016-06-01")
    assert a.old_hedge_fraction == pytest.approx(0.70)


def test_amend_creates_audit_trail():
    book = TradingBook()
    book.open_hedge(_c())
    book.amend_hedge("C1", "2016-01-01", 0.90, "2016-03-01")
    book.amend_hedge("C1", "2016-01-01", 1.00, "2016-06-01")
    assert len(book.amendments()) == 2


def test_amend_tracks_sequential_fractions():
    book = TradingBook()
    book.open_hedge(_c(hf=0.85))
    book.amend_hedge("C1", "2016-01-01", 0.90, "2016-03-01")
    a2 = book.amend_hedge("C1", "2016-01-01", 1.00, "2016-06-01")
    assert a2.old_hedge_fraction == pytest.approx(0.90)


def test_close_position_moves_to_closed():
    book = TradingBook()
    book.open_hedge(_c())
    assert len(book.open_contracts()) == 1
    book.close_position("C1", "2016-01-01", "2016-09-01", 70.0)
    assert len(book.open_contracts()) == 0
    assert len(book.closed_contracts()) == 1


def test_close_position_creates_closure_record():
    book = TradingBook()
    book.open_hedge(_c(agreed_price=50.0, notional_mwh=10.0))
    cl = book.close_position("C1", "2016-01-01", "2016-09-01", 70.0)
    assert isinstance(cl, PositionClosure)
    assert cl.realised_pnl_gbp == pytest.approx(200.0)


def test_close_position_itm():
    book = TradingBook()
    book.open_hedge(_c(agreed_price=40.0, notional_mwh=5.0))
    cl = book.close_position("C1", "2016-01-01", "2016-09-01", 60.0)
    assert cl.realised_pnl_gbp == pytest.approx(100.0)


def test_close_position_otm():
    book = TradingBook()
    book.open_hedge(_c(agreed_price=80.0, notional_mwh=5.0))
    cl = book.close_position("C1", "2016-01-01", "2016-09-01", 60.0)
    assert cl.realised_pnl_gbp == pytest.approx(-100.0)


def test_open_contracts_excludes_closed():
    book = TradingBook()
    book.open_hedge(_c("C1"))
    book.open_hedge(_c("C2"))
    book.close_position("C1", "2016-01-01", "2016-09-01", 70.0)
    open_ids = [c.customer_id for c in book.open_contracts()]
    assert "C1" not in open_ids
    assert "C2" in open_ids


def test_mtm_skips_closed_positions():
    book = TradingBook()
    book.open_hedge(_c("C1", agreed_price=50.0, notional_mwh=10.0))
    book.close_position("C1", "2016-01-01", "2016-09-01", 70.0)
    result = book.portfolio_mtm({"C1": 80.0})
    assert result["positions_priced"] == 0
    assert result["total_mtm_pnl_gbp"] == 0.0
