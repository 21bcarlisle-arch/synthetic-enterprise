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
