"""Phase IU -- Coverage Depth Sprint XVIII: customer_profitability, forward_book, hedge_decision."""

import unittest

from company.crm.customer_profitability import (
    CustomerProfitabilityRecord, CustomerProfitabilityBook,
    estimate_prior_term_net_margin, compute_profitability_uplift,
    NET_NEGATIVE_UPLIFT_GBP_PER_MWH, MIN_RECORDS_FOR_JUDGEMENT,
)
from company.trading.forward_book import ForwardContract, TradingBook
from company.trading.hedge_decision import (
    estimate_price_volatility, compute_bid_ask_cost, decide_hedge_fraction,
    MIN_VOL_ANNUAL, MAX_BID_ASK_PCT, BID_ASK_BASE_PCT,
)
from company.risk.hedge_policy import COMPANY_MIN_HEDGE_FLOOR


def _rec(account="A1", year=2024, rev=1000.0, whl=600.0, levy=100.0, ops=80.0):
    return CustomerProfitabilityRecord(
        account_id=account, year=year,
        annual_revenue_gbp=rev, annual_wholesale_cost_gbp=whl,
        annual_levy_cost_gbp=levy, annual_operating_cost_gbp=ops,
    )


class TestCustomerProfitabilityRecord(unittest.TestCase):
    def test_gross_margin_gbp(self):
        r = _rec(rev=1000.0, whl=600.0)
        self.assertAlmostEqual(r.gross_margin_gbp, 400.0, places=2)

    def test_net_contribution_gbp(self):
        r = _rec(rev=1000.0, whl=600.0, levy=100.0, ops=80.0)
        self.assertAlmostEqual(r.net_contribution_gbp, 220.0, places=2)

    def test_is_net_negative(self):
        r = _rec(rev=500.0, whl=400.0, levy=100.0, ops=50.0)
        self.assertTrue(r.is_net_negative)

    def test_gross_margin_pct(self):
        r = _rec(rev=1000.0, whl=600.0)
        self.assertAlmostEqual(r.gross_margin_pct, 40.0, places=1)

    def test_zero_revenue_returns_zero_pcts(self):
        r = _rec(rev=0.0, whl=0.0, levy=0.0, ops=0.0)
        self.assertEqual(r.gross_margin_pct, 0.0)
        self.assertEqual(r.net_margin_pct, 0.0)


class TestCustomerProfitabilityBook(unittest.TestCase):
    def test_latest_for_returns_most_recent_year(self):
        book = CustomerProfitabilityBook()
        book.record(_rec(account="A", year=2022))
        book.record(_rec(account="A", year=2024))
        book.record(_rec(account="A", year=2023))
        latest = book.latest_for("A")
        self.assertEqual(latest.year, 2024)

    def test_net_negative_accounts(self):
        book = CustomerProfitabilityBook()
        book.record(_rec(account="A", rev=500.0, whl=400.0, levy=100.0, ops=50.0))
        book.record(_rec(account="B", rev=1000.0, whl=400.0, levy=100.0, ops=80.0))
        nn = book.net_negative_accounts(year=2024)
        self.assertIn("A", nn)
        self.assertNotIn("B", nn)

    def test_total_net_contribution_gbp(self):
        book = CustomerProfitabilityBook()
        book.record(_rec(account="A", rev=1000.0, whl=600.0, levy=100.0, ops=80.0))
        book.record(_rec(account="B", rev=800.0, whl=500.0, levy=80.0, ops=60.0))
        total = book.total_net_contribution_gbp(year=2024)
        self.assertAlmostEqual(total, 220.0 + 160.0, places=2)

    def test_net_negative_rate_pct(self):
        book = CustomerProfitabilityBook()
        book.record(_rec(account="A", rev=500.0, whl=400.0, levy=100.0, ops=50.0))
        book.record(_rec(account="B", rev=1000.0, whl=400.0, levy=80.0, ops=60.0))
        rate = book.net_negative_rate_pct(year=2024)
        self.assertAlmostEqual(rate, 50.0, places=1)

    def test_estimate_prior_term_insufficient_records_returns_none(self):
        records = [
            {"customer_id": "A", "commodity": "electricity",
             "settlement_date": "2023-06-01", "term_start": "2023-01-01",
             "net_margin_gbp": -100.0},
            {"customer_id": "A", "commodity": "electricity",
             "settlement_date": "2023-07-01", "term_start": "2023-01-01",
             "net_margin_gbp": -80.0},
        ]
        result = estimate_prior_term_net_margin("A", "2024-01-01", records)
        self.assertIsNone(result)


def _contract(cid="C1", ts="2024-01-01", te="2025-01-01",
              notional=10.0, price=80.0, hf=0.5, ba=0.0):
    return ForwardContract(customer_id=cid, term_start=ts, term_end=te,
                           notional_mwh=notional, agreed_price_gbp_per_mwh=price,
                           hedge_fraction=hf, bid_ask_cost_gbp=ba)


class TestTradingBook(unittest.TestCase):
    def test_open_hedge_increments_count(self):
        book = TradingBook()
        book.open_hedge(_contract())
        self.assertEqual(book.contract_count, 1)

    def test_settle_period_correct_pnl(self):
        book = TradingBook()
        book.open_hedge(_contract(price=80.0, hf=1.0))
        result = book.settle_period("C1", "2024-01-01", consumed_kwh=1000.0, actual_spot_gbp_per_mwh=70.0)
        self.assertAlmostEqual(result.hedged_mwh, 1.0, places=3)
        self.assertAlmostEqual(result.pnl_gbp, 10.0, places=2)

    def test_settle_period_zero_hedge_fraction(self):
        book = TradingBook()
        book.open_hedge(_contract(hf=0.0))
        result = book.settle_period("C1", "2024-01-01", consumed_kwh=2000.0, actual_spot_gbp_per_mwh=80.0)
        self.assertAlmostEqual(result.hedged_mwh, 0.0, places=3)
        self.assertAlmostEqual(result.pnl_gbp, 0.0, places=2)

    def test_settle_period_no_matching_contract(self):
        book = TradingBook()
        result = book.settle_period("UNKNOWN", "2024-01-01", consumed_kwh=500.0, actual_spot_gbp_per_mwh=60.0)
        self.assertEqual(result.hedged_mwh, 0.0)
        self.assertEqual(result.pnl_gbp, 0.0)

    def test_total_pnl_accumulates(self):
        book = TradingBook()
        book.open_hedge(_contract(price=80.0, hf=1.0))
        book.settle_period("C1", "2024-01-01", 1000.0, 70.0)
        book.settle_period("C1", "2024-01-01", 1000.0, 70.0)
        self.assertAlmostEqual(book.total_pnl_gbp, 20.0, places=2)

    def test_amend_hedge_records_amendment(self):
        book = TradingBook()
        book.open_hedge(_contract(hf=0.5))
        amend = book.amend_hedge("C1", "2024-01-01", 0.8, "2024-06-01", reason="risk increase")
        self.assertAlmostEqual(amend.old_hedge_fraction, 0.5, places=2)
        self.assertAlmostEqual(amend.new_hedge_fraction, 0.8, places=2)
        self.assertEqual(len(book.amendments()), 1)

    def test_close_position_realised_pnl(self):
        book = TradingBook()
        book.open_hedge(_contract(price=80.0, notional=10.0))
        closure = book.close_position("C1", "2024-01-01", "2024-06-01", close_price_gbp_per_mwh=85.0)
        self.assertAlmostEqual(closure.realised_pnl_gbp, (85.0 - 80.0) * 10.0, places=2)

    def test_close_position_moves_to_closed(self):
        book = TradingBook()
        book.open_hedge(_contract())
        self.assertEqual(len(book.open_contracts()), 1)
        book.close_position("C1", "2024-01-01", "2024-06-01", 80.0)
        self.assertEqual(len(book.open_contracts()), 0)
        self.assertEqual(len(book.closed_contracts()), 1)

    def test_mark_to_market_in_the_money(self):
        book = TradingBook()
        c = _contract(price=70.0, notional=5.0)
        mtm = book.mark_to_market(c, current_price_gbp_per_mwh=80.0)
        self.assertTrue(mtm["in_the_money"])
        self.assertAlmostEqual(mtm["mtm_pnl_gbp"], 50.0, places=2)

    def test_summary_structure(self):
        book = TradingBook()
        book.open_hedge(_contract())
        s = book.summary()
        self.assertIn("contract_count", s)
        self.assertIn("total_hedge_pnl_gbp", s)


def _price_records(n=30, base_price=60.0):
    import datetime as dt
    recs = []
    d = dt.date(2024, 1, 1)
    for i in range(n):
        recs.append({"settlementDate": str(d), "systemSellPrice": base_price + (i % 5)})
        d = d + dt.timedelta(days=1)
    return recs


class TestHedgeDecision(unittest.TestCase):
    def test_estimate_vol_empty_returns_min(self):
        vol = estimate_price_volatility([])
        self.assertAlmostEqual(vol, MIN_VOL_ANNUAL, places=4)

    def test_estimate_vol_few_records_returns_min(self):
        recs = [{"settlementDate": "2024-01-01", "systemSellPrice": 60.0}]
        vol = estimate_price_volatility(recs)
        self.assertAlmostEqual(vol, MIN_VOL_ANNUAL, places=4)

    def test_estimate_vol_valid_records_returns_float(self):
        recs = _price_records(n=30)
        vol = estimate_price_volatility(recs)
        self.assertGreaterEqual(vol, MIN_VOL_ANNUAL)
        self.assertIsInstance(vol, float)

    def test_bid_ask_cost_short_tenor(self):
        cost = compute_bid_ask_cost(forward_price_gbp_per_mwh=80.0, tenor_years=0.5)
        expected = 80.0 * (BID_ASK_BASE_PCT + 0.002 * 0.5)
        self.assertAlmostEqual(cost, expected, places=4)

    def test_bid_ask_cost_capped_at_max(self):
        cost = compute_bid_ask_cost(forward_price_gbp_per_mwh=100.0, tenor_years=100.0)
        max_cost = 100.0 * MAX_BID_ASK_PCT
        self.assertAlmostEqual(cost, max_cost, places=4)

    def test_decide_hedge_fraction_zero_eac_returns_floor(self):
        hf = decide_hedge_fraction(0.0, 80.0, 90.0, [], 365)
        self.assertAlmostEqual(hf, COMPANY_MIN_HEDGE_FLOOR, places=4)

    def test_decide_hedge_fraction_zero_fwd_price_returns_floor(self):
        hf = decide_hedge_fraction(10000.0, 0.0, 90.0, [], 365)
        self.assertAlmostEqual(hf, COMPANY_MIN_HEDGE_FLOOR, places=4)

    def test_decide_hedge_fraction_in_valid_range(self):
        recs = _price_records(n=30)
        hf = decide_hedge_fraction(10000.0, 80.0, 90.0, recs, 365)
        self.assertGreaterEqual(hf, COMPANY_MIN_HEDGE_FLOOR)
        self.assertLessEqual(hf, 1.0)

    def test_decide_hedge_fraction_high_vol_drives_higher_hf(self):
        import math
        high_vol_recs = []
        import datetime as dt
        d = dt.date(2022, 1, 1)
        p = 60.0
        for i in range(30):
            high_vol_recs.append({"settlementDate": str(d), "systemSellPrice": max(1.0, p)})
            p *= (1.5 if i % 2 == 0 else 0.6)
            d += dt.timedelta(days=1)
        hf_high = decide_hedge_fraction(10000.0, 80.0, 90.0, high_vol_recs, 365)
        low_vol_recs = _price_records(n=30, base_price=60.0)
        hf_low = decide_hedge_fraction(10000.0, 80.0, 90.0, low_vol_recs, 365)
        self.assertGreaterEqual(hf_high, hf_low)

    def test_compute_profitability_uplift_net_negative(self):
        records = [
            {"customer_id": "A", "commodity": "electricity",
             "settlement_date": f"2023-0{i+1}-01", "term_start": "2023-01-01",
             "net_margin_gbp": -200.0}
            for i in range(4)
        ]
        uplift = compute_profitability_uplift("A", "2024-01-01", records)
        self.assertAlmostEqual(uplift, NET_NEGATIVE_UPLIFT_GBP_PER_MWH, places=2)


if __name__ == "__main__":
    unittest.main()
