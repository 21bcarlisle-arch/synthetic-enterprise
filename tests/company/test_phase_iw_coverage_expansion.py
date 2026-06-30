"""Phase IW -- Coverage Depth Sprint XX: portal_analytics, dsr_book, licence_health."""

import datetime as dt
import unittest

from company.crm.portal_analytics import PortalAnalytics, PortalAction, PortalEvent
from company.market.dsr_book import DSRBook, DispatchResult
from company.regulatory.licence_health import (
    build_licence_health_report, LicenceCheckStatus, LicenceCheck,
)

TS = dt.datetime(2024, 3, 15, 10, 0, 0)
TS_END = dt.datetime(2024, 3, 15, 12, 0, 0)


class TestPortalAnalytics(unittest.TestCase):
    def test_record_creates_sequential_id(self):
        pa = PortalAnalytics()
        e = pa.record("C1", PortalAction.LOGIN, TS, "S1")
        self.assertEqual(e.event_id, "PE-000001")

    def test_sequential_ids(self):
        pa = PortalAnalytics()
        e1 = pa.record("C1", PortalAction.LOGIN, TS, "S1")
        e2 = pa.record("C2", PortalAction.VIEW_BILL, TS, "S2")
        self.assertEqual(e1.event_id, "PE-000001")
        self.assertEqual(e2.event_id, "PE-000002")

    def test_is_self_serve_true_for_submit_meter_read(self):
        pa = PortalAnalytics()
        e = pa.record("C1", PortalAction.SUBMIT_METER_READ, TS, "S1")
        self.assertTrue(e.is_self_serve)

    def test_is_self_serve_false_for_view_bill(self):
        pa = PortalAnalytics()
        e = pa.record("C1", PortalAction.VIEW_BILL, TS, "S1")
        self.assertFalse(e.is_self_serve)

    def test_events_in_period_range(self):
        pa = PortalAnalytics()
        pa.record("C1", PortalAction.LOGIN, TS, "S1")
        outside = dt.datetime(2024, 6, 1, 10, 0, 0)
        self.assertEqual(len(pa.events_in_period(outside, outside)), 0)
        self.assertEqual(len(pa.events_in_period(TS, TS)), 1)

    def test_unique_users(self):
        pa = PortalAnalytics()
        pa.record("A", PortalAction.LOGIN, TS, "S1")
        pa.record("A", PortalAction.VIEW_BILL, TS, "S1")
        pa.record("B", PortalAction.LOGIN, TS, "S2")
        self.assertEqual(pa.unique_users(TS, TS), 2)

    def test_self_serve_rate(self):
        pa = PortalAnalytics()
        pa.record("C1", PortalAction.SUBMIT_METER_READ, TS, "S1")
        pa.record("C1", PortalAction.VIEW_BILL, TS, "S1")
        rate = pa.self_serve_rate(TS, TS)
        self.assertAlmostEqual(rate, 50.0, places=1)

    def test_self_serve_rate_none_if_no_events(self):
        pa = PortalAnalytics()
        self.assertIsNone(pa.self_serve_rate(TS, TS))

    def test_action_counts(self):
        pa = PortalAnalytics()
        pa.record("C1", PortalAction.LOGIN, TS, "S1")
        pa.record("C2", PortalAction.LOGIN, TS, "S2")
        pa.record("C3", PortalAction.VIEW_BILL, TS, "S3")
        counts = pa.action_counts(TS, TS)
        self.assertEqual(counts.get("login"), 2)
        self.assertEqual(counts.get("view_bill"), 1)

    def test_monthly_summary_structure(self):
        pa = PortalAnalytics()
        pa.record("C1", PortalAction.LOGIN, TS, "S1")
        s = pa.monthly_summary(2024, 3)
        self.assertEqual(s["year"], 2024)
        self.assertIn("total_events", s)
        self.assertIn("unique_users", s)


class TestDSRBook(unittest.TestCase):
    def test_enroll_creates_active_participant(self):
        book = DSRBook()
        p = book.enroll("C1", "MPAN1", contracted_mw=2.0,
                        enrolled_date=dt.date(2024, 1, 1), payment_per_mwh_gbp=50.0)
        self.assertEqual(p.customer_id, "C1")
        self.assertAlmostEqual(p.contracted_mw, 2.0)

    def test_dispatch_delivered_result(self):
        book = DSRBook()
        book.enroll("C1", "MPAN1", 2.0, dt.date(2024, 1, 1))
        ev = book.dispatch("C1", requested_mw=2.0, dispatch_start=TS,
                           dispatch_end=TS_END, delivered_mw=2.0)
        self.assertEqual(ev.result, DispatchResult.DELIVERED)
        self.assertEqual(ev.event_id, "DSR-0001")

    def test_dispatch_partial_result(self):
        book = DSRBook()
        book.enroll("C1", "MPAN1", 2.0, dt.date(2024, 1, 1))
        ev = book.dispatch("C1", 2.0, TS, TS_END, delivered_mw=0.5)
        self.assertEqual(ev.result, DispatchResult.PARTIAL)

    def test_dispatch_payment_gbp(self):
        book = DSRBook()
        book.enroll("C1", "MPAN1", 2.0, dt.date(2024, 1, 1), payment_per_mwh_gbp=50.0)
        ev = book.dispatch("C1", 2.0, TS, TS_END, delivered_mw=2.0)
        expected_mwh = 2.0 * 2.0
        expected_payment = round(expected_mwh * 50.0, 2)
        self.assertAlmostEqual(ev.payment_gbp, expected_payment, places=2)

    def test_dispatch_raises_for_inactive(self):
        book = DSRBook()
        book.enroll("C1", "MPAN1", 2.0, dt.date(2024, 1, 1))
        p = book._participants["C1"]
        from dataclasses import replace
        book._participants["C1"] = replace(p, status="suspended")
        with self.assertRaises((ValueError, AttributeError)):
            book.dispatch("C1", 2.0, TS, TS_END, 2.0)

    def test_dispatch_event_duration_hours(self):
        book = DSRBook()
        book.enroll("C1", "MPAN1", 2.0, dt.date(2024, 1, 1))
        ev = book.dispatch("C1", 2.0, TS, TS_END, delivered_mw=2.0)
        self.assertAlmostEqual(ev.duration_hours, 2.0, places=2)

    def test_dispatch_event_delivered_mwh(self):
        book = DSRBook()
        book.enroll("C1", "MPAN1", 2.0, dt.date(2024, 1, 1))
        ev = book.dispatch("C1", 2.0, TS, TS_END, delivered_mw=3.0)
        self.assertAlmostEqual(ev.delivered_mwh, 3.0 * 2.0, places=2)

    def test_delivery_rate(self):
        book = DSRBook()
        book.enroll("C1", "MPAN1", 2.0, dt.date(2024, 1, 1))
        ev = book.dispatch("C1", 2.0, TS, TS_END, delivered_mw=1.5)
        self.assertAlmostEqual(ev.delivery_rate, 75.0, places=1)

    def test_total_contracted_mw(self):
        book = DSRBook()
        book.enroll("A", "M1", 3.0, dt.date(2024, 1, 1))
        book.enroll("B", "M2", 2.0, dt.date(2024, 1, 1))
        self.assertAlmostEqual(book.total_contracted_mw(), 5.0, places=2)

    def test_annual_summary_structure(self):
        book = DSRBook()
        book.enroll("C1", "MPAN1", 2.0, dt.date(2024, 1, 1))
        book.dispatch("C1", 2.0, TS, TS_END, delivered_mw=2.0)
        s = book.annual_summary(2024)
        self.assertEqual(s["dispatch_events"], 1)
        self.assertIn("total_payments_gbp", s)


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
