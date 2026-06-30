"""Phase JC coverage expansion: capacity_market, company_pl, credit_limits."""
import datetime as dt
import unittest


class TestCapacityMarket(unittest.TestCase):

    def _book(self):
        from company.market.capacity_market import CapacityMarketBook, CMUnitType, AuctionType
        return CapacityMarketBook(), CMUnitType, AuctionType

    def test_register_unit(self):
        book, T, _ = self._book()
        u = book.register_unit("U1", T.DEMAND_RESPONSE, 500.0, dt.date(2023, 1, 1))
        self.assertEqual(u.unit_id, "U1")
        self.assertEqual(u.unit_type, T.DEMAND_RESPONSE)
        self.assertAlmostEqual(u.derated_capacity_kw, 500.0)

    def test_add_obligation_uses_default_price(self):
        from company.market.capacity_market import get_cm_price
        book, T, A = self._book()
        u = book.register_unit("U1", T.DEMAND_RESPONSE, 500.0, dt.date(2023, 1, 1))
        o = book.add_obligation(u, 2023, A.T4)
        self.assertAlmostEqual(o.clearing_price_gbp_per_kw, get_cm_price(2023))

    def test_add_obligation_custom_price(self):
        book, T, A = self._book()
        u = book.register_unit("U1", T.DEMAND_RESPONSE, 500.0, dt.date(2023, 1, 1))
        o = book.add_obligation(u, 2023, A.T4, clearing_price=45.0)
        self.assertAlmostEqual(o.clearing_price_gbp_per_kw, 45.0)

    def test_annual_revenue(self):
        book, T, A = self._book()
        u = book.register_unit("U1", T.DEMAND_RESPONSE, 1000.0, dt.date(2023, 1, 1))
        o = book.add_obligation(u, 2023, A.T4, clearing_price=50.0)
        self.assertAlmostEqual(o.annual_revenue_gbp, 50_000.0)

    def test_apply_penalty_reduces_net_revenue(self):
        book, T, A = self._book()
        u = book.register_unit("U1", T.DEMAND_RESPONSE, 1000.0, dt.date(2023, 1, 1))
        o = book.add_obligation(u, 2023, A.T4, clearing_price=50.0)
        o.apply_penalty(5000.0)
        self.assertAlmostEqual(o.net_revenue_gbp, 45_000.0)

    def test_obligations_for_year_filters(self):
        book, T, A = self._book()
        u = book.register_unit("U1", T.DEMAND_RESPONSE, 500.0, dt.date(2023, 1, 1))
        book.add_obligation(u, 2023, A.T4)
        book.add_obligation(u, 2024, A.T4)
        self.assertEqual(len(book.obligations_for_year(2023)), 1)

    def test_total_revenue_gbp(self):
        book, T, A = self._book()
        u1 = book.register_unit("U1", T.DEMAND_RESPONSE, 500.0, dt.date(2023, 1, 1))
        u2 = book.register_unit("U2", T.BATTERY, 300.0, dt.date(2023, 1, 1))
        book.add_obligation(u1, 2023, A.T4, clearing_price=50.0)
        book.add_obligation(u2, 2023, A.T4, clearing_price=50.0)
        self.assertAlmostEqual(book.total_revenue_gbp(2023), 40_000.0)

    def test_total_derated_kw(self):
        book, T, A = self._book()
        u1 = book.register_unit("U1", T.DEMAND_RESPONSE, 500.0, dt.date(2023, 1, 1))
        u2 = book.register_unit("U2", T.BATTERY, 300.0, dt.date(2023, 1, 1))
        book.add_obligation(u1, 2023, A.T4)
        book.add_obligation(u2, 2023, A.T4)
        self.assertAlmostEqual(book.total_derated_kw(2023), 800.0)

    def test_cm_summary_structure(self):
        book, T, A = self._book()
        u = book.register_unit("U1", T.DEMAND_RESPONSE, 500.0, dt.date(2023, 1, 1))
        book.add_obligation(u, 2023, A.T4, clearing_price=50.0)
        s = book.cm_summary(2023)
        self.assertIn("delivery_year", s)
        self.assertIn("total_revenue_gbp", s)
        self.assertEqual(s["obligations"], 1)

    def test_net_revenue_no_penalty(self):
        book, T, A = self._book()
        u = book.register_unit("U1", T.DEMAND_RESPONSE, 1000.0, dt.date(2023, 1, 1))
        o = book.add_obligation(u, 2023, A.T4, clearing_price=50.0)
        self.assertAlmostEqual(o.net_revenue_gbp, o.annual_revenue_gbp)


class TestCompanyPL(unittest.TestCase):

    def _pl(self, revenue=1_000_000.0, wholesale=600_000.0, policy=80_000.0,
             network=120_000.0, opex=100_000.0, marketing=20_000.0,
             bad_debt=10_000.0, whd=5_000.0, gsop=2_000.0):
        from company.finance.company_pl import CompanyPL
        return CompanyPL(2023, revenue, wholesale, policy, network,
                          opex, marketing, bad_debt, whd, gsop)

    def test_gross_margin_gbp(self):
        pl = self._pl()
        # 1M - 600k - 80k - 120k = 200k
        self.assertAlmostEqual(pl.gross_margin_gbp, 200_000.0)

    def test_total_operating_cost_gbp(self):
        pl = self._pl()
        # 100k + 20k + 10k + 5k + 2k = 137k
        self.assertAlmostEqual(pl.total_operating_cost_gbp, 137_000.0)

    def test_ebitda_gbp(self):
        pl = self._pl()
        # 200k - 137k = 63k
        self.assertAlmostEqual(pl.ebitda_gbp, 63_000.0)

    def test_gross_margin_pct(self):
        pl = self._pl()
        self.assertAlmostEqual(pl.gross_margin_pct, 20.0)

    def test_ebitda_margin_pct(self):
        pl = self._pl()
        self.assertAlmostEqual(pl.ebitda_margin_pct, 6.3)

    def test_bad_debt_as_pct_revenue(self):
        pl = self._pl(revenue=1_000_000.0, bad_debt=10_000.0)
        self.assertAlmostEqual(pl.bad_debt_as_pct_revenue, 1.0)

    def test_is_profitable_true(self):
        pl = self._pl()
        self.assertTrue(pl.is_profitable)

    def test_is_profitable_false_loss(self):
        from company.finance.company_pl import CompanyPL
        pl = CompanyPL(2023, 100_000.0, 90_000.0, 10_000.0, 10_000.0, 20_000.0, 0.0, 0.0, 0.0, 0.0)
        self.assertFalse(pl.is_profitable)

    def test_summary_structure(self):
        pl = self._pl()
        s = pl.summary()
        self.assertIn("revenue_gbp", s)
        self.assertIn("gross_margin_gbp", s)
        self.assertIn("ebitda_gbp", s)
        self.assertIn("is_profitable", s)

    def test_build_company_pl(self):
        from company.finance.company_pl import build_company_pl
        pl = build_company_pl(2023, 500_000.0, 300_000.0, 50_000.0, 80_000.0, 60_000.0)
        self.assertEqual(pl.year, 2023)
        self.assertAlmostEqual(pl.gross_margin_gbp, 70_000.0)


class TestCreditLimits(unittest.TestCase):

    def _mgr(self):
        from company.trading.credit_limits import CounterpartyCreditManager, CounterpartyLimit
        mgr = CounterpartyCreditManager()
        return mgr, CounterpartyLimit

    def test_set_and_get_limit(self):
        mgr, L = self._mgr()
        lim = L("CP1", "Shell", "A", 1_000_000.0, "generator")
        mgr.set_limit(lim)
        got = mgr.get_limit("CP1")
        self.assertIs(got, lim)

    def test_get_limit_returns_none_when_not_set(self):
        mgr, _ = self._mgr()
        self.assertIsNone(mgr.get_limit("UNKNOWN"))

    def test_update_exposure_accumulates(self):
        mgr, L = self._mgr()
        mgr.set_limit(L("CP1", "Shell", "A", 1_000_000.0))
        mgr.update_exposure("CP1", 200_000.0)
        mgr.update_exposure("CP1", 150_000.0)
        self.assertAlmostEqual(mgr.current_exposure("CP1"), 350_000.0)

    def test_current_exposure_zero_when_not_set(self):
        mgr, _ = self._mgr()
        self.assertAlmostEqual(mgr.current_exposure("UNKNOWN"), 0.0)

    def test_check_trade_green(self):
        mgr, L = self._mgr()
        mgr.set_limit(L("CP1", "Shell", "A", 1_000_000.0))
        result = mgr.check_trade("CP1", 500_000.0)  # 50% util < 70%
        self.assertEqual(result.status, "GREEN")
        self.assertTrue(result.approved)

    def test_check_trade_amber(self):
        mgr, L = self._mgr()
        mgr.set_limit(L("CP1", "Shell", "A", 1_000_000.0))
        mgr.update_exposure("CP1", 700_000.0)
        result = mgr.check_trade("CP1", 100_000.0)  # 80% util, >=70% <90%
        self.assertEqual(result.status, "AMBER")
        self.assertTrue(result.approved)

    def test_check_trade_red_not_approved(self):
        mgr, L = self._mgr()
        mgr.set_limit(L("CP1", "Shell", "A", 1_000_000.0))
        mgr.update_exposure("CP1", 850_000.0)
        result = mgr.check_trade("CP1", 200_000.0)  # 105% util >= 90%
        self.assertEqual(result.status, "RED")
        self.assertFalse(result.approved)

    def test_check_trade_no_limit(self):
        mgr, _ = self._mgr()
        result = mgr.check_trade("UNKNOWN", 100_000.0)
        self.assertEqual(result.status, "NO_LIMIT")
        self.assertFalse(result.approved)

    def test_breached_limits(self):
        mgr, L = self._mgr()
        mgr.set_limit(L("CP1", "Shell", "A", 1_000_000.0))
        mgr.set_limit(L("CP2", "Vitol", "BB", 500_000.0))
        mgr.update_exposure("CP1", 100_000.0)  # 10% - not breached
        mgr.update_exposure("CP2", 450_000.0)  # 90% - breached
        breached = mgr.breached_limits()
        self.assertEqual(len(breached), 1)
        self.assertEqual(breached[0][0], "CP2")

    def test_summary_structure(self):
        mgr, L = self._mgr()
        mgr.set_limit(L("CP1", "Shell", "A", 1_000_000.0))
        mgr.update_exposure("CP1", 200_000.0)
        s = mgr.summary()
        self.assertIn("total_limits", s)
        self.assertIn("breached", s)
        self.assertIn("total_exposure_gbp", s)
        self.assertAlmostEqual(s["total_exposure_gbp"], 200_000.0)


if __name__ == "__main__":
    unittest.main()
