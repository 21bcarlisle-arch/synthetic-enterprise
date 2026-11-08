"""Phase IW -- Coverage Depth Sprint XX: portal_analytics, dsr_book, licence_health."""

import datetime as dt
import unittest
from company.regulatory.licence_health import (
    build_licence_health_report, LicenceCheckStatus, LicenceCheck,
)

TS = dt.datetime(2024, 3, 15, 10, 0, 0)
TS_END = dt.datetime(2024, 3, 15, 12, 0, 0)




class TestLicenceHealth(unittest.TestCase):
    def _build(self, customers=200, net_assets=500000.0, treasury=200000.0,
               runway=12.0, bad_debt=1.5, complaints=0.5):
        return build_licence_health_report(
            as_of=dt.date(2024, 3, 31),
            active_customer_count=customers,
            net_assets_gbp=net_assets,
            treasury_gbp=treasury,
            weeks_cash_runway=runway,
            bad_debt_ratio_pct=bad_debt,
            complaints_per_100=complaints,
        )

    def test_build_returns_report(self):
        r = self._build()
        self.assertIsNotNone(r)
        self.assertGreater(r.pass_count, 0)

    def test_overall_pass_when_all_good(self):
        r = self._build()
        self.assertEqual(r.overall_status, LicenceCheckStatus.PASS)

    def test_overall_breach_when_treasury_low(self):
        r = self._build(treasury=50000.0)
        self.assertEqual(r.overall_status, LicenceCheckStatus.BREACH)

    def test_is_going_concern_false_when_breach(self):
        r = self._build(treasury=0.0)
        self.assertFalse(r.is_going_concern)

    def test_watch_when_close_to_threshold(self):
        r = self._build(treasury=115000.0)
        check = r.get("treasury_gbp")
        self.assertIsNotNone(check)
        self.assertEqual(check.status, LicenceCheckStatus.WATCH)

    def test_headroom_calculation(self):
        r = self._build(treasury=200000.0)
        check = r.get("treasury_gbp")
        self.assertAlmostEqual(check.headroom, 200000.0 - 100000.0, places=2)

    def test_bad_debt_breach_above_5pct(self):
        r = self._build(bad_debt=6.0)
        check = r.get("bad_debt_ratio")
        self.assertEqual(check.status, LicenceCheckStatus.BREACH)

    def test_bad_debt_watch_between_3_and_5pct(self):
        r = self._build(bad_debt=4.0)
        check = r.get("bad_debt_ratio")
        self.assertEqual(check.status, LicenceCheckStatus.WATCH)

    def test_complaints_breach_above_3(self):
        r = self._build(complaints=4.0)
        check = r.get("complaints_per_100")
        self.assertEqual(check.status, LicenceCheckStatus.BREACH)

    def test_summary_structure(self):
        r = self._build()
        s = r.summary()
        self.assertIn("overall_status", s)
        self.assertIn("is_going_concern", s)
        self.assertIn("breach", s)


if __name__ == "__main__":
    unittest.main()
