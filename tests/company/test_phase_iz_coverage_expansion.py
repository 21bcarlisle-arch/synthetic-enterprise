"""Phase IZ coverage expansion: switch_analytics, risk_appetite, credit_rating_book."""
import datetime as dt
import unittest


class TestRiskAppetite(unittest.TestCase):

    def _raf(self):
        from company.risk.risk_appetite import RiskAppetiteFramework, RiskCategory, RiskRAG
        raf = RiskAppetiteFramework(approved_date=dt.date(2023, 1, 1))
        return raf, RiskCategory, RiskRAG

    def test_warning_value(self):
        raf, C, _ = self._raf()
        lim = raf.add_limit("L1", C.MARKET, "test", 100.0, "MWh", warning_threshold_pct=80.0)
        self.assertAlmostEqual(lim.warning_value, 80.0)

    def test_utilisation_pct(self):
        raf, C, _ = self._raf()
        raf.add_limit("L1", C.MARKET, "test", 200.0, "MWh")
        m = raf.record_measurement("L1", 150.0, dt.date(2023, 6, 1))
        self.assertAlmostEqual(m.utilisation_pct, 75.0)

    def test_rag_within_appetite(self):
        raf, C, R = self._raf()
        raf.add_limit("L1", C.MARKET, "test", 100.0, "MWh", warning_threshold_pct=80.0)
        m = raf.record_measurement("L1", 50.0, dt.date(2023, 6, 1))
        self.assertEqual(m.rag, R.WITHIN_APPETITE)
        self.assertFalse(m.is_breach)

    def test_rag_approaching_limit(self):
        raf, C, R = self._raf()
        raf.add_limit("L1", C.MARKET, "test", 100.0, "MWh", warning_threshold_pct=80.0)
        m = raf.record_measurement("L1", 85.0, dt.date(2023, 6, 1))
        self.assertEqual(m.rag, R.APPROACHING_LIMIT)
        self.assertFalse(m.is_breach)

    def test_rag_limit_breach(self):
        raf, C, R = self._raf()
        raf.add_limit("L1", C.MARKET, "test", 100.0, "MWh")
        m = raf.record_measurement("L1", 110.0, dt.date(2023, 6, 1))
        self.assertEqual(m.rag, R.LIMIT_BREACH)
        self.assertTrue(m.is_breach)

    def test_latest_measurement_returns_most_recent(self):
        raf, C, _ = self._raf()
        raf.add_limit("L1", C.CREDIT, "credit test", 500.0, "GBP")
        raf.record_measurement("L1", 100.0, dt.date(2023, 1, 1))
        raf.record_measurement("L1", 200.0, dt.date(2023, 6, 1))
        latest = raf.latest_measurement("L1")
        self.assertEqual(latest.measured_value, 200.0)

    def test_latest_measurement_none_when_no_measurements(self):
        raf, C, _ = self._raf()
        raf.add_limit("L1", C.CREDIT, "credit test", 500.0, "GBP")
        self.assertIsNone(raf.latest_measurement("L1"))

    def test_active_breaches(self):
        raf, C, _ = self._raf()
        raf.add_limit("L1", C.MARKET, "market", 100.0, "MWh")
        raf.add_limit("L2", C.CREDIT, "credit", 1000.0, "GBP")
        raf.record_measurement("L1", 120.0, dt.date(2023, 6, 1))
        raf.record_measurement("L2", 500.0, dt.date(2023, 6, 1))
        breaches = raf.active_breaches()
        self.assertEqual(len(breaches), 1)
        self.assertEqual(breaches[0].limit_id, "L1")

    def test_risk_dashboard_structure(self):
        raf, C, _ = self._raf()
        raf.add_limit("L1", C.MARKET, "market", 100.0, "MWh")
        raf.record_measurement("L1", 50.0, dt.date(2023, 6, 1))
        dash = raf.risk_dashboard(dt.date(2023, 12, 31))
        self.assertIn("total_limits", dash)
        self.assertIn("measured_limits", dash)
        self.assertIn("breaches", dash)
        self.assertIn("items", dash)
        self.assertEqual(dash["total_limits"], 1)
        self.assertEqual(len(dash["items"]), 1)

    def test_risk_dashboard_excludes_future_measurements(self):
        raf, C, _ = self._raf()
        raf.add_limit("L1", C.MARKET, "market", 100.0, "MWh")
        raf.record_measurement("L1", 110.0, dt.date(2024, 1, 1))
        dash = raf.risk_dashboard(dt.date(2023, 12, 31))
        self.assertEqual(dash["measured_limits"], 0)
        self.assertEqual(dash["breaches"], 0)


if __name__ == "__main__":
    unittest.main()
