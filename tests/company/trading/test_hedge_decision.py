import pytest
import math
from company.trading.hedge_decision import (
    estimate_price_volatility,
    compute_bid_ask_cost,
    decide_hedge_fraction,
    compute_realized_var,
    MIN_VOL_ANNUAL,
    MAX_VOL_ANNUAL,
    BID_ASK_BASE_PCT,
    MAX_BID_ASK_PCT,
    VAR_REVENUE_LIMIT,
)
from company.risk.hedge_policy import COMPANY_MIN_HEDGE_FLOOR


def _price_records(n=100, start=50.0, drift=0.0, noise=2.0):
    """Generate synthetic price records with controlled vol."""
    import random
    random.seed(42)
    records = []
    price = start
    for i in range(n):
        price = max(1.0, price + drift + random.gauss(0, noise))
        records.append({
            "settlementDate": f"2022-{(i % 12) + 1:02d}-{(i % 28) + 1:02d}",
            "systemSellPrice": round(price, 2),
        })
    return records


class TestEstimatePriceVolatility:
    def test_fewer_than_5_returns_floor(self):
        assert estimate_price_volatility([]) == MIN_VOL_ANNUAL
        assert estimate_price_volatility([{"settlementDate": "2022-01-01", "systemSellPrice": 50.0}]) == MIN_VOL_ANNUAL

    def test_returns_within_bounds(self):
        records = _price_records(120, noise=5.0)
        vol = estimate_price_volatility(records)
        assert MIN_VOL_ANNUAL <= vol <= MAX_VOL_ANNUAL

    def test_higher_noise_gives_higher_vol(self):
        low_vol = estimate_price_volatility(_price_records(100, noise=0.1))
        high_vol = estimate_price_volatility(_price_records(100, noise=20.0))
        assert high_vol > low_vol

    def test_constant_price_returns_floor(self):
        records = [{"settlementDate": f"2022-01-{i+1:02d}", "systemSellPrice": 50.0} for i in range(30)]
        assert estimate_price_volatility(records) == MIN_VOL_ANNUAL

    def test_filters_zero_prices(self):
        records = _price_records(50)
        records.append({"settlementDate": "2022-06-01", "systemSellPrice": 0.0})
        vol = estimate_price_volatility(records)
        assert vol >= MIN_VOL_ANNUAL

    def test_filters_missing_date(self):
        records = _price_records(50)
        records.append({"systemSellPrice": 50.0})  # no date key
        vol = estimate_price_volatility(records)
        assert vol >= MIN_VOL_ANNUAL


class TestComputeBidAskCost:
    def test_zero_tenor_uses_base_pct(self):
        cost = compute_bid_ask_cost(100.0, 0.0)
        assert cost == pytest.approx(100.0 * BID_ASK_BASE_PCT)

    def test_long_tenor_capped(self):
        cost = compute_bid_ask_cost(100.0, tenor_years=100.0)
        assert cost == pytest.approx(100.0 * MAX_BID_ASK_PCT)

    def test_proportional_to_price(self):
        c1 = compute_bid_ask_cost(100.0, 1.0)
        c2 = compute_bid_ask_cost(200.0, 1.0)
        assert c2 == pytest.approx(2 * c1, rel=0.01)


class TestDecideHedgeFraction:
    def test_returns_at_least_floor(self):
        records = _price_records(100)
        hf = decide_hedge_fraction(10000.0, 80.0, 90.0, records, 365)
        assert hf >= COMPANY_MIN_HEDGE_FLOOR

    def test_returns_at_most_one(self):
        records = _price_records(100, noise=50.0)  # very high vol
        hf = decide_hedge_fraction(10000.0, 80.0, 90.0, records, 365)
        assert hf <= 1.0

    def test_zero_eac_returns_floor(self):
        hf = decide_hedge_fraction(0.0, 80.0, 90.0, [], 365)
        assert hf == COMPANY_MIN_HEDGE_FLOOR

    def test_zero_fwd_price_returns_floor(self):
        hf = decide_hedge_fraction(10000.0, 0.0, 90.0, _price_records(50), 365)
        assert hf == COMPANY_MIN_HEDGE_FLOOR

    def test_zero_term_returns_floor(self):
        hf = decide_hedge_fraction(10000.0, 80.0, 90.0, _price_records(50), 0)
        assert hf == COMPANY_MIN_HEDGE_FLOOR

    def test_no_price_records_returns_floor(self):
        hf = decide_hedge_fraction(10000.0, 80.0, 90.0, [], 365)
        assert hf == COMPANY_MIN_HEDGE_FLOOR

    def test_very_high_vol_gives_high_hedge(self):
        # When vol is extreme, VaR constraint forces near-full hedge
        records = _price_records(100, noise=100.0)
        hf = decide_hedge_fraction(10000.0, 80.0, 90.0, records, 365)
        assert hf >= 0.9  # should be very high

    def test_result_is_float(self):
        records = _price_records(60)
        hf = decide_hedge_fraction(10000.0, 80.0, 90.0, records, 180)
        assert isinstance(hf, float)


class TestComputeRealizedVar:
    def test_zero_eac_returns_zero(self):
        result = compute_realized_var(0.0, 80.0, 90.0, _price_records(50), 365, 0.8)
        assert result == {"var_gbp": 0.0, "var_pct_of_term_revenue": 0.0}

    def test_zero_fwd_price_returns_zero(self):
        result = compute_realized_var(10000.0, 0.0, 90.0, _price_records(50), 365, 0.8)
        assert result["var_gbp"] == 0.0

    def test_zero_term_returns_zero(self):
        result = compute_realized_var(10000.0, 80.0, 90.0, _price_records(50), 0, 0.8)
        assert result["var_gbp"] == 0.0

    def test_fully_hedged_gives_zero_var(self):
        records = _price_records(100)
        result = compute_realized_var(10000.0, 80.0, 90.0, records, 365, 1.0)
        assert result["var_gbp"] == pytest.approx(0.0, abs=1e-6)
        assert result["var_pct_of_term_revenue"] == pytest.approx(0.0, abs=1e-6)

    def test_naked_position_has_positive_var(self):
        records = _price_records(100)
        result = compute_realized_var(10000.0, 80.0, 90.0, records, 365, 0.0)
        assert result["var_gbp"] > 0.0
        assert result["var_pct_of_term_revenue"] > 0.0

    def test_lower_hedge_fraction_gives_higher_var(self):
        records = _price_records(100)
        low_hf = compute_realized_var(10000.0, 80.0, 90.0, records, 365, 0.9)
        high_hf = compute_realized_var(10000.0, 80.0, 90.0, records, 365, 0.2)
        assert high_hf["var_gbp"] > low_hf["var_gbp"]

    def test_matches_decide_hedge_fraction_constraint_at_solved_hf(self):
        # At the hf that decide_hedge_fraction() solves for, realized VaR should sit
        # at (or just under, due to the floor/ceiling clamp) the VAR_REVENUE_LIMIT.
        records = _price_records(100, noise=8.0)
        hf = decide_hedge_fraction(10000.0, 80.0, 90.0, records, 365)
        result = compute_realized_var(10000.0, 80.0, 90.0, records, 365, hf)
        assert result["var_pct_of_term_revenue"] <= VAR_REVENUE_LIMIT + 1e-6
