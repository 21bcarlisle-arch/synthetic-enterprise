"""Phase JD coverage expansion: contract_manager, dsr_portfolio, curve_monitor."""
import datetime as dt
import unittest


class TestContractManager(unittest.TestCase):

    def _mgr(self):
        from company.billing.contract_manager import ContractManager, ContractType, ContractStatus
        return ContractManager(), ContractType, ContractStatus

    def _reg(self, mgr, ct, cid="C1", mpan="M1", start=None, end=None,
              rate=12.0, standing=30.0, aqk=10_000.0):
        if start is None:
            start = dt.date(2023, 1, 1)
        if end is None:
            end = dt.date(2024, 1, 1)
        return mgr.register(cid + "_" + mpan, cid, mpan, ct, start, end, rate, standing, aqk)

    def test_register_and_get(self):
        mgr, T, _ = self._mgr()
        c = self._reg(mgr, T.FIXED_TERM)
        got = mgr.get(c.contract_id)
        self.assertIs(c, got)

    def test_notice_period_fixed_term_42d(self):
        mgr, T, _ = self._mgr()
        c = self._reg(mgr, T.FIXED_TERM)
        self.assertEqual(c.notice_period_days, 42)

    def test_notice_period_evergreen_90d(self):
        mgr, T, _ = self._mgr()
        c = self._reg(mgr, T.EVERGREEN)
        self.assertEqual(c.notice_period_days, 90)

    def test_days_to_expiry(self):
        mgr, T, _ = self._mgr()
        c = self._reg(mgr, T.FIXED_TERM, start=dt.date(2023, 1, 1), end=dt.date(2023, 7, 1))
        self.assertEqual(c.days_to_expiry(dt.date(2023, 6, 1)), 30)

    def test_annual_cost_estimate_gbp(self):
        mgr, T, _ = self._mgr()
        c = self._reg(mgr, T.FIXED_TERM, rate=10.0, standing=0.0, aqk=10_000.0)
        # 10000 kwh * 10p / 100 = £1000
        self.assertAlmostEqual(c.annual_cost_estimate_gbp(), 1000.0)

    def test_serve_notice_sets_in_notice(self):
        mgr, T, S = self._mgr()
        c = self._reg(mgr, T.FIXED_TERM)
        mgr.serve_notice(c.contract_id, dt.date(2023, 11, 1))
        self.assertEqual(c.status, S.IN_NOTICE)
        self.assertEqual(c.notice_served_date, dt.date(2023, 11, 1))

    def test_expire_contract(self):
        mgr, T, S = self._mgr()
        c = self._reg(mgr, T.FIXED_TERM)
        mgr.expire_contract(c.contract_id)
        self.assertEqual(c.status, S.EXPIRED)

    def test_active_contracts_excludes_expired(self):
        mgr, T, _ = self._mgr()
        c1 = self._reg(mgr, T.FIXED_TERM, cid="C1", mpan="M1")
        c2 = self._reg(mgr, T.FIXED_TERM, cid="C2", mpan="M2")
        mgr.expire_contract(c1.contract_id)
        active = mgr.active_contracts()
        self.assertEqual(len(active), 1)
        self.assertEqual(active[0].contract_id, c2.contract_id)

    def test_expiring_within(self):
        mgr, T, _ = self._mgr()
        c1 = self._reg(mgr, T.FIXED_TERM, cid="C1", mpan="M1",
                        start=dt.date(2023, 1, 1), end=dt.date(2023, 1, 20))
        self._reg(mgr, T.FIXED_TERM, cid="C2", mpan="M2",
                   start=dt.date(2023, 1, 1), end=dt.date(2023, 6, 1))
        expiring = mgr.expiring_within(dt.date(2023, 1, 1), 30)
        self.assertEqual(len(expiring), 1)

    def test_portfolio_summary_structure(self):
        mgr, T, _ = self._mgr()
        self._reg(mgr, T.FIXED_TERM)
        s = mgr.portfolio_summary(dt.date(2023, 6, 1))
        self.assertIn("total_contracts", s)
        self.assertIn("active", s)
        self.assertIn("expiring_30d", s)
        self.assertIn("by_type", s)


class TestDSRPortfolio(unittest.TestCase):

    def _portfolio(self):
        from company.market.dsr_portfolio import DSRPortfolio, DSREventType, CurtailmentStatus
        return DSRPortfolio(), DSREventType, CurtailmentStatus

    def _event(self, port, etype, eid="EV1", target_mw=10.0, notice_min=60,
                start=None, end=None):
        if start is None:
            start = dt.datetime(2023, 6, 1, 16, 0)
        if end is None:
            end = dt.datetime(2023, 6, 1, 18, 0)
        return port.create_event(eid, etype, start, end, target_mw, notice_min)

    def test_event_duration_hours(self):
        port, T, _ = self._portfolio()
        ev = self._event(port, T.FREQUENCY_RESPONSE)
        self.assertAlmostEqual(ev.duration_hours, 2.0)

    def test_event_target_mwh(self):
        port, T, _ = self._portfolio()
        ev = self._event(port, T.FREQUENCY_RESPONSE, target_mw=10.0)
        self.assertAlmostEqual(ev.target_mwh, 20.0)

    def test_event_is_short_notice_true(self):
        port, T, _ = self._portfolio()
        ev = self._event(port, T.FREQUENCY_RESPONSE, notice_min=15)
        self.assertTrue(ev.is_short_notice)

    def test_event_is_short_notice_false(self):
        port, T, _ = self._portfolio()
        ev = self._event(port, T.FREQUENCY_RESPONSE, notice_min=60)
        self.assertFalse(ev.is_short_notice)

    def test_record_curtailment_complied(self):
        port, T, S = self._portfolio()
        self._event(port, T.FREQUENCY_RESPONSE)
        c = port.record_curtailment("CUST1", "EV1", 1000.0, 980.0, revenue_gbp=50.0)
        self.assertEqual(c.status, S.COMPLIED)

    def test_record_curtailment_partial(self):
        port, T, S = self._portfolio()
        self._event(port, T.FREQUENCY_RESPONSE)
        c = port.record_curtailment("CUST1", "EV1", 1000.0, 500.0, revenue_gbp=25.0)
        self.assertEqual(c.status, S.PARTIAL)

    def test_record_curtailment_non_compliant(self):
        port, T, S = self._portfolio()
        self._event(port, T.FREQUENCY_RESPONSE)
        c = port.record_curtailment("CUST1", "EV1", 1000.0, 0.0)
        self.assertEqual(c.status, S.NON_COMPLIANT)

    def test_compliance_pct(self):
        port, T, _ = self._portfolio()
        self._event(port, T.FREQUENCY_RESPONSE)
        c = port.record_curtailment("CUST1", "EV1", 1000.0, 800.0)
        self.assertAlmostEqual(c.compliance_pct, 80.0)

    def test_compliance_rate_pct(self):
        port, T, _ = self._portfolio()
        self._event(port, T.FREQUENCY_RESPONSE)
        port.record_curtailment("CUST1", "EV1", 1000.0, 1000.0)  # complied
        port.record_curtailment("CUST2", "EV1", 1000.0, 0.0)      # non-compliant
        self.assertAlmostEqual(port.compliance_rate_pct("EV1"), 50.0)

    def test_annual_revenue_gbp(self):
        port, T, _ = self._portfolio()
        self._event(port, T.FREQUENCY_RESPONSE)
        port.record_curtailment("CUST1", "EV1", 1000.0, 1000.0, revenue_gbp=100.0)
        port.record_curtailment("CUST2", "EV1", 500.0, 500.0, revenue_gbp=50.0)
        self.assertAlmostEqual(port.annual_revenue_gbp(2023), 150.0)


class TestForwardCurveMonitor(unittest.TestCase):

    def _monitor(self, window=10):
        from company.market.curve_monitor import ForwardCurveMonitor, PricePoint
        return ForwardCurveMonitor(window=window), PricePoint

    def _prices(self, n, price=100.0, Monitor_cls=None, PricePoint_cls=None):
        return [PricePoint_cls(str(i), price) for i in range(n)]

    def test_add_returns_none_before_min_window(self):
        mon, PP = self._monitor()
        result = mon.add(PP("p1", 100.0))
        self.assertIsNone(result)

    def test_add_returns_result_after_min_window(self):
        mon, PP = self._monitor()
        for i in range(9):
            mon.add(PP(str(i), 100.0))
        result = mon.add(PP("p10", 100.0))
        self.assertIsNotNone(result)

    def test_normal_price_returns_normal_severity(self):
        mon, PP = self._monitor()
        for i in range(9):
            mon.add(PP(str(i), 100.0))
        result = mon.add(PP("p10", 101.0))  # tiny deviation
        self.assertEqual(result.severity, "normal")

    def test_extreme_price_returns_critical_severity(self):
        mon, PP = self._monitor()
        for i in range(9):
            mon.add(PP(str(i), 100.0))
        result = mon.add(PP("p10", 1000.0))  # massive spike
        self.assertIn(result.severity, ["alert", "critical"])

    def test_screen_series_returns_non_none_only(self):
        mon, PP = self._monitor()
        prices = [PP(str(i), 100.0) for i in range(15)]
        results = mon.screen_series(prices)
        # Points 9-14 (10th price onward) produce results
        self.assertEqual(len(results), 6)

    def test_summary_structure_all_normal(self):
        mon, PP = self._monitor()
        prices = [PP(str(i), 100.0) for i in range(15)]
        results = mon.screen_series(prices)
        s = mon.summary(results)
        self.assertIn("total", s)
        self.assertIn("critical", s)
        self.assertIn("normal", s)
        self.assertEqual(s["total"], 6)

    def test_summary_empty(self):
        mon, PP = self._monitor()
        s = mon.summary([])
        self.assertEqual(s["total"], 0)

    def test_anomaly_result_fields(self):
        mon, PP = self._monitor()
        for i in range(9):
            mon.add(PP(str(i), 100.0))
        result = mon.add(PP("p10", 100.5))
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result.price_gbp_mwh, 100.5)
        self.assertIsNotNone(result.mean_gbp_mwh)
        self.assertIsNotNone(result.z_score)

    def test_price_point_commodity_default_electricity(self):
        from company.market.curve_monitor import PricePoint
        pp = PricePoint("2023-01-01", 150.0)
        self.assertEqual(pp.commodity, "electricity")

    def test_price_point_gas_commodity(self):
        from company.market.curve_monitor import PricePoint
        pp = PricePoint("2023-01-01", 80.0, "gas")
        self.assertEqual(pp.commodity, "gas")


if __name__ == "__main__":
    unittest.main()
