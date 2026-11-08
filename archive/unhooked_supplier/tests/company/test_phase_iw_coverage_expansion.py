# Increment 3: the legs of tests/company/test_phase_iw_coverage_expansion.py that test archived modules. Its live legs stay there.
"""Phase IW -- Coverage Depth Sprint XX: portal_analytics, dsr_book, licence_health."""

import datetime as dt
import unittest

from company.crm.portal_analytics import PortalAnalytics, PortalAction, PortalEvent

TS = dt.datetime(2024, 3, 15, 10, 0, 0)


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


# ==== archive increment 3b: the legs that stayed live in 3a, archived now (the live file is still at its path) ====

# ARCHIVED LEGS of tests/company/test_phase_iw_coverage_expansion.py (archive increment 3b). The tests here reach a module
# under archive/unhooked_supplier/; the live legs stay at tests/company/test_phase_iw_coverage_expansion.py.
"""Phase IW -- Coverage Depth Sprint XX: portal_analytics, dsr_book, licence_health."""

import datetime as dt
import unittest
from company.market.dsr_book import DSRBook, DispatchResult
from company.regulatory.licence_health import (
    build_licence_health_report, LicenceCheckStatus, LicenceCheck,
)

TS = dt.datetime(2024, 3, 15, 10, 0, 0)
TS_END = dt.datetime(2024, 3, 15, 12, 0, 0)


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




if __name__ == "__main__":
    unittest.main()
