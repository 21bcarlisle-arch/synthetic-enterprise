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
