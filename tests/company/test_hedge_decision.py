"""Tests for Phase 43b: VaR-constrained hedge decision."""

import pytest
from company.trading.hedge_decision import (
    estimate_price_volatility,
    compute_bid_ask_cost,
    decide_hedge_fraction,
    MIN_VOL_ANNUAL,
    COMPANY_MIN_HEDGE_FLOOR,
)

# Minimal price record helpers
def _flat_records(n_days=100, price=50.0):
    """n_days of flat daily prices at 48 HH periods/day."""
    from datetime import date, timedelta
    start = date(2020, 1, 1)
    records = []
    for i in range(n_days):
        d = (start + timedelta(days=i)).isoformat()
        for p in range(1, 49):
            records.append({"settlementDate": d, "settlementPeriod": p, "systemSellPrice": price})
    return records


def _volatile_records(n_days=100, base_price=50.0, daily_pct_change=0.05):
    """n_days with deterministic daily price changes to create known vol."""
    from datetime import date, timedelta
    import math
    start = date(2020, 1, 1)
    records = []
    price = base_price
    for i in range(n_days):
        d = (start + timedelta(days=i)).isoformat()
        price *= (1 + (daily_pct_change if i % 2 == 0 else -daily_pct_change))
        price = max(1.0, price)
        for p in range(1, 49):
            records.append({"settlementDate": d, "settlementPeriod": p, "systemSellPrice": price})
    return records


class TestEstimatePriceVolatility:
    def test_insufficient_data_returns_floor(self):
        assert estimate_price_volatility([]) == MIN_VOL_ANNUAL
        assert estimate_price_volatility(_flat_records(n_days=3)) == MIN_VOL_ANNUAL

    def test_flat_prices_return_near_floor(self):
        """Zero-return series → vol approaches floor."""
        vol = estimate_price_volatility(_flat_records(n_days=100))
        assert vol == MIN_VOL_ANNUAL or vol < 0.05  # flat prices have near-zero vol

    def test_volatile_prices_return_higher_vol(self):
        """5% daily swings should produce significantly higher vol than flat."""
        flat_vol = estimate_price_volatility(_flat_records(n_days=100))
        high_vol = estimate_price_volatility(_volatile_records(n_days=100, daily_pct_change=0.05))
        assert high_vol > flat_vol * 5

    def test_returns_positive_float(self):
        vol = estimate_price_volatility(_flat_records(n_days=50))
        assert isinstance(vol, float)
        assert vol > 0

    def test_result_is_bounded(self):
        from company.trading.hedge_decision import MAX_VOL_ANNUAL
        very_volatile = _volatile_records(n_days=90, daily_pct_change=0.50)
        vol = estimate_price_volatility(very_volatile)
        assert vol <= MAX_VOL_ANNUAL


class TestComputeBidAskCost:
    def test_basic_spread(self):
        """1-year £60/MWh contract: ~0.7% = £0.42/MWh."""
        cost = compute_bid_ask_cost(60.0, tenor_years=1.0)
        assert 0.3 < cost < 0.9  # 0.5% + 0.2%*1 = 0.7%

    def test_shorter_tenor_cheaper(self):
        short = compute_bid_ask_cost(60.0, tenor_years=0.25)
        long = compute_bid_ask_cost(60.0, tenor_years=2.0)
        assert short < long

    def test_capped_at_max(self):
        from company.trading.hedge_decision import MAX_BID_ASK_PCT
        very_long = compute_bid_ask_cost(100.0, tenor_years=100.0)
        assert very_long <= 100.0 * MAX_BID_ASK_PCT * 1.001  # at or near cap

    def test_scales_with_forward_price(self):
        """Spread cost proportional to forward price."""
        low = compute_bid_ask_cost(40.0, tenor_years=1.0)
        high = compute_bid_ask_cost(120.0, tenor_years=1.0)
        assert abs(high / low - 3.0) < 0.01  # 3x price → 3x cost


class TestDecideHedgeFraction:
    def test_returns_at_least_floor(self):
        """Always returns at least MIN_HEDGE_FLOOR."""
        records = _flat_records(n_days=100)
        hf = decide_hedge_fraction(5_000_000, 60.0, 100.0, records, 365)
        assert hf >= COMPANY_MIN_HEDGE_FLOOR

    def test_returns_at_most_one(self):
        hf = decide_hedge_fraction(5_000_000, 60.0, 100.0, _flat_records(), 365)
        assert hf <= 1.0

    def test_high_volatility_forces_higher_hedge(self):
        """In high-vol regime, VaR constraint forces higher hedge fraction."""
        calm_hf = decide_hedge_fraction(5_000_000, 60.0, 100.0, _flat_records(100), 365)
        crisis_hf = decide_hedge_fraction(5_000_000, 60.0, 100.0,
                                          _volatile_records(100, daily_pct_change=0.10), 365)
        assert crisis_hf >= calm_hf

    def test_zero_eac_returns_floor(self):
        assert decide_hedge_fraction(0, 60.0, 100.0, _flat_records(), 365) == COMPANY_MIN_HEDGE_FLOOR

    def test_zero_fwd_price_returns_floor(self):
        assert decide_hedge_fraction(5_000_000, 0.0, 100.0, _flat_records(), 365) == COMPANY_MIN_HEDGE_FLOOR

    def test_calm_period_near_floor(self):
        """Low volatility → VaR allows near-floor hedge fraction."""
        hf = decide_hedge_fraction(5_000_000, 60.0, 100.0, _flat_records(100), 365)
        # With minimal vol, unhedged VaR is tiny → floor binds
        assert abs(hf - COMPANY_MIN_HEDGE_FLOOR) < 0.15
