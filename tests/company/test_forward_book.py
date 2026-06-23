"""Tests for Phase 43a: Company Trading Desk — Forward Position Lifecycle."""

import pytest
from company.trading.forward_book import ForwardContract, TradingBook, HedgePnL


def _make_contract(**kwargs):
    defaults = dict(
        customer_id="C1",
        term_start="2020-01-01",
        term_end="2021-01-01",
        notional_mwh=100.0,
        agreed_price_gbp_per_mwh=60.0,
        hedge_fraction=0.85,
    )
    defaults.update(kwargs)
    return ForwardContract(**defaults)


class TestForwardContract:
    def test_frozen_fields(self):
        c = _make_contract()
        with pytest.raises(Exception):
            c.customer_id = "C2"  # frozen dataclass

    def test_fields_accessible(self):
        c = _make_contract(
            customer_id="C5",
            agreed_price_gbp_per_mwh=75.0,
            notional_mwh=50.0,
            hedge_fraction=0.9,
        )
        assert c.customer_id == "C5"
        assert c.agreed_price_gbp_per_mwh == 75.0
        assert c.notional_mwh == 50.0
        assert c.hedge_fraction == 0.9


class TestTradingBookLifecycle:
    def test_empty_book_summary(self):
        book = TradingBook()
        s = book.summary()
        assert s["contract_count"] == 0
        assert s["total_hedged_mwh"] == 0.0
        assert s["total_hedge_pnl_gbp"] == 0.0

    def test_open_hedge_increments_contract_count(self):
        book = TradingBook()
        book.open_hedge(_make_contract())
        assert book.contract_count == 1

    def test_two_contracts_tracked(self):
        book = TradingBook()
        book.open_hedge(_make_contract(customer_id="C1", term_start="2020-01-01"))
        book.open_hedge(_make_contract(customer_id="C1", term_start="2021-01-01"))
        assert book.contract_count == 2

    def test_open_contracts_returns_copy(self):
        book = TradingBook()
        book.open_hedge(_make_contract())
        contracts = book.open_contracts()
        contracts.clear()
        assert book.contract_count == 1  # internal state unchanged


class TestSettlePeriod:
    def test_hedge_pnl_forward_above_spot_positive(self):
        """When agreed_price > spot, hedge won — positive P&L."""
        book = TradingBook()
        book.open_hedge(_make_contract(
            agreed_price_gbp_per_mwh=60.0,
            hedge_fraction=1.0,
        ))
        result = book.settle_period("C1", "2020-01-01", consumed_kwh=1000.0, actual_spot_gbp_per_mwh=50.0)
        # hedged_mwh = 1.0 × 1.0 = 1.0 MWh; pnl = (60-50) × 1.0 = £10
        assert isinstance(result, HedgePnL)
        assert abs(result.pnl_gbp - 10.0) < 0.001

    def test_hedge_pnl_forward_below_spot_negative(self):
        """When agreed_price < spot, hedge lost — negative P&L (opportunity cost)."""
        book = TradingBook()
        book.open_hedge(_make_contract(
            agreed_price_gbp_per_mwh=60.0,
            hedge_fraction=1.0,
        ))
        result = book.settle_period("C1", "2020-01-01", consumed_kwh=1000.0, actual_spot_gbp_per_mwh=80.0)
        # hedged_mwh = 1.0; pnl = (60-80) × 1.0 = -£20
        assert abs(result.pnl_gbp - (-20.0)) < 0.001

    def test_partial_hedge_fraction(self):
        """Hedge P&L scales with hedge_fraction."""
        book = TradingBook()
        book.open_hedge(_make_contract(
            agreed_price_gbp_per_mwh=60.0,
            hedge_fraction=0.85,
        ))
        result = book.settle_period("C1", "2020-01-01", consumed_kwh=2000.0, actual_spot_gbp_per_mwh=50.0)
        # hedged_mwh = 2.0 × 0.85 = 1.7 MWh; pnl = (60-50) × 1.7 = £17
        assert abs(result.pnl_gbp - 17.0) < 0.001
        assert abs(result.hedged_mwh - 1.7) < 0.001

    def test_no_matching_contract_returns_zero(self):
        """settle_period returns zero P&L if no matching contract."""
        book = TradingBook()
        book.open_hedge(_make_contract(customer_id="C1", term_start="2020-01-01"))
        result = book.settle_period("C2", "2020-01-01", consumed_kwh=1000.0, actual_spot_gbp_per_mwh=50.0)
        assert result.pnl_gbp == 0.0
        assert result.hedged_mwh == 0.0

    def test_cumulative_pnl_across_periods(self):
        """Total P&L accumulates correctly across multiple settlement periods."""
        book = TradingBook()
        book.open_hedge(_make_contract(
            agreed_price_gbp_per_mwh=60.0,
            hedge_fraction=1.0,
        ))
        book.settle_period("C1", "2020-01-01", consumed_kwh=1000.0, actual_spot_gbp_per_mwh=50.0)  # +£10
        book.settle_period("C1", "2020-01-01", consumed_kwh=1000.0, actual_spot_gbp_per_mwh=70.0)  # -£10
        assert abs(book.total_pnl_gbp) < 0.001  # net zero: one period up, one period down

    def test_two_customers_separate_contracts(self):
        """Two customers' hedge positions are tracked independently."""
        book = TradingBook()
        book.open_hedge(_make_contract(customer_id="C1", agreed_price_gbp_per_mwh=60.0, hedge_fraction=1.0))
        book.open_hedge(_make_contract(customer_id="C2", agreed_price_gbp_per_mwh=70.0, hedge_fraction=1.0))
        r1 = book.settle_period("C1", "2020-01-01", consumed_kwh=1000.0, actual_spot_gbp_per_mwh=50.0)
        r2 = book.settle_period("C2", "2020-01-01", consumed_kwh=1000.0, actual_spot_gbp_per_mwh=50.0)
        assert abs(r1.pnl_gbp - 10.0) < 0.001   # C1: (60-50)×1
        assert abs(r2.pnl_gbp - 20.0) < 0.001   # C2: (70-50)×1

    def test_zero_consumption_period(self):
        """Zero consumption period returns zero P&L."""
        book = TradingBook()
        book.open_hedge(_make_contract())
        result = book.settle_period("C1", "2020-01-01", consumed_kwh=0.0, actual_spot_gbp_per_mwh=50.0)
        assert result.pnl_gbp == 0.0

    def test_summary_reflects_settled_positions(self):
        """summary() correctly reports total hedged MWh and P&L after settlement."""
        book = TradingBook()
        book.open_hedge(_make_contract(
            agreed_price_gbp_per_mwh=60.0,
            hedge_fraction=1.0,
        ))
        book.settle_period("C1", "2020-01-01", consumed_kwh=1000.0, actual_spot_gbp_per_mwh=50.0)
        s = book.summary()
        assert s["contract_count"] == 1
        assert abs(s["total_hedged_mwh"] - 1.0) < 0.001
        assert abs(s["total_hedge_pnl_gbp"] - 10.0) < 0.01
