"""Phase IX -- Coverage Depth Sprint XXI: ancillary_products, tariff_notification, service_log."""

import datetime as dt
import unittest

from company.crm.ancillary_products import (
    AncillaryRevenueTracker, AncillaryProduct, ProductSubscription,
)
from company.crm.tariff_notification import (
    TariffNotificationLog, NotificationChannel, TariffChangeReason,
    NotificationStatus, ADVANCE_NOTICE_DAYS,
)
from company.crm.service_log import ServiceLog, ServiceEvent

D1 = dt.date(2024, 1, 1)
D2 = dt.date(2024, 12, 31)


class TestAncillaryProducts(unittest.TestCase):
    def test_subscribe_creates_active_sub(self):
        tracker = AncillaryRevenueTracker()
        sub = tracker.subscribe("C1", AncillaryProduct.BOILER_COVER, D1)
        self.assertTrue(sub.is_active)
        self.assertEqual(sub.product, AncillaryProduct.BOILER_COVER)

    def test_default_monthly_price_from_table(self):
        tracker = AncillaryRevenueTracker()
        sub = tracker.subscribe("C1", AncillaryProduct.BOILER_COVER, D1)
        self.assertAlmostEqual(sub.monthly_price_gbp, 18.0, places=2)

    def test_custom_monthly_price_override(self):
        tracker = AncillaryRevenueTracker()
        sub = tracker.subscribe("C1", AncillaryProduct.BOILER_COVER, D1, monthly_price_gbp=20.0)
        self.assertAlmostEqual(sub.monthly_price_gbp, 20.0, places=2)

    def test_cancel_sets_end_date(self):
        tracker = AncillaryRevenueTracker()
        tracker.subscribe("C1", AncillaryProduct.BOILER_COVER, D1)
        tracker.cancel("C1", AncillaryProduct.BOILER_COVER, dt.date(2024, 6, 30))
        subs = tracker.active_subscriptions("C1")
        self.assertEqual(len(subs), 0)

    def test_active_subscriptions_after_cancel(self):
        tracker = AncillaryRevenueTracker()
        tracker.subscribe("C1", AncillaryProduct.BOILER_COVER, D1)
        tracker.subscribe("C1", AncillaryProduct.BROADBAND, D1)
        tracker.cancel("C1", AncillaryProduct.BOILER_COVER, dt.date(2024, 6, 30))
        active = tracker.active_subscriptions("C1")
        self.assertEqual(len(active), 1)
        self.assertEqual(active[0].product, AncillaryProduct.BROADBAND)

    def test_products_per_customer(self):
        tracker = AncillaryRevenueTracker()
        tracker.subscribe("C1", AncillaryProduct.BOILER_COVER, D1)
        tracker.subscribe("C1", AncillaryProduct.BROADBAND, D1)
        self.assertEqual(tracker.products_per_customer("C1"), 2)

    def test_avg_products_per_customer(self):
        tracker = AncillaryRevenueTracker()
        tracker.subscribe("A", AncillaryProduct.BOILER_COVER, D1)
        tracker.subscribe("A", AncillaryProduct.BROADBAND, D1)
        tracker.subscribe("B", AncillaryProduct.CARBON_OFFSET, D1)
        avg = tracker.avg_products_per_customer()
        self.assertAlmostEqual(avg, 1.5, places=1)

    def test_total_annual_revenue_gbp(self):
        tracker = AncillaryRevenueTracker()
        tracker.subscribe("C1", AncillaryProduct.CARBON_OFFSET, D1)
        rev = tracker.total_annual_revenue_gbp(2024)
        self.assertGreater(rev, 0)

    def test_revenue_by_product(self):
        tracker = AncillaryRevenueTracker()
        tracker.subscribe("C1", AncillaryProduct.BOILER_COVER, D1)
        tracker.subscribe("C2", AncillaryProduct.BOILER_COVER, D1)
        by_prod = tracker.revenue_by_product(2024)
        self.assertIn("boiler_cover", by_prod)
        self.assertGreater(by_prod["boiler_cover"], 0)

    def test_portfolio_summary_structure(self):
        tracker = AncillaryRevenueTracker()
        tracker.subscribe("C1", AncillaryProduct.BROADBAND, D1)
        s = tracker.portfolio_summary(2024)
        self.assertIn("total_active_subscriptions", s)
        self.assertIn("unique_customers", s)
        self.assertIn("by_product", s)


class TestTariffNotification(unittest.TestCase):
    def _send(self, log, nid="N001", cid="C1",
              sent=dt.date(2024, 1, 1), effective=dt.date(2024, 2, 20),
              old_unit=28.0, new_unit=30.0):
        return log.send(nid, cid, NotificationChannel.EMAIL, sent, effective,
                        TariffChangeReason.MARKET_PRICE_CHANGE,
                        old_unit, new_unit, 50.0, 50.0)

    def test_send_creates_notification(self):
        log = TariffNotificationLog()
        n = self._send(log)
        self.assertEqual(n.notification_id, "N001")
        self.assertEqual(n.status, NotificationStatus.SENT)

    def test_notice_days(self):
        log = TariffNotificationLog()
        sent = dt.date(2024, 1, 1)
        effective = dt.date(2024, 2, 20)
        n = self._send(log, sent=sent, effective=effective)
        self.assertEqual(n.notice_days, (effective - sent).days)

    def test_meets_advance_notice(self):
        log = TariffNotificationLog()
        n = self._send(log, sent=dt.date(2024, 1, 1), effective=dt.date(2024, 2, 20))
        self.assertTrue(n.meets_advance_notice)

    def test_fails_advance_notice(self):
        log = TariffNotificationLog()
        n = self._send(log, sent=dt.date(2024, 1, 1), effective=dt.date(2024, 1, 15))
        self.assertFalse(n.meets_advance_notice)

    def test_is_price_increase(self):
        log = TariffNotificationLog()
        n = self._send(log, old_unit=28.0, new_unit=30.0)
        self.assertTrue(n.is_price_increase)

    def test_unit_rate_change_pct(self):
        log = TariffNotificationLog()
        n = self._send(log, old_unit=28.0, new_unit=29.4)
        self.assertAlmostEqual(n.unit_rate_change_pct, 5.0, places=0)

    def test_compliance_breaches_filter(self):
        log = TariffNotificationLog()
        self._send(log, nid="N1", sent=dt.date(2024, 1, 1), effective=dt.date(2024, 2, 20))
        self._send(log, nid="N2", sent=dt.date(2024, 1, 1), effective=dt.date(2024, 1, 15))
        breaches = log.compliance_breaches()
        self.assertEqual(len(breaches), 1)
        self.assertEqual(breaches[0].notification_id, "N2")

    def test_mark_confirmed(self):
        log = TariffNotificationLog()
        n = self._send(log)
        log.mark_confirmed("N001")
        self.assertEqual(n.status, NotificationStatus.CONFIRMED_READ)

    def test_price_increases_for_year(self):
        log = TariffNotificationLog()
        self._send(log, nid="N1", old_unit=28.0, new_unit=30.0)
        self._send(log, nid="N2", old_unit=30.0, new_unit=28.0)
        increases = log.price_increases(2024)
        self.assertEqual(len(increases), 1)

    def test_notification_summary_structure(self):
        log = TariffNotificationLog()
        self._send(log)
        s = log.notification_summary(2024)
        self.assertIn("total_sent", s)
        self.assertIn("compliance_breaches", s)
        self.assertIn("price_increases", s)


class TestServiceLog(unittest.TestCase):
    def _event(self, cid="C1", channel="portal", complaint=False):
        return ServiceEvent(
            customer_id=cid, event_date="2024-06-01",
            channel=channel, contact_reason="billing",
            outcome="resolved", complaint_flag=complaint,
        )

    def test_record_contact_creates_event(self):
        log = ServiceLog()
        ev = self._event()
        log.record_contact(ev)
        recs = log.contacts_for_customer("C1")
        self.assertEqual(len(recs), 1)

    def test_multiple_events_for_customer(self):
        log = ServiceLog()
        log.record_contact(self._event(cid="C1"))
        log.record_contact(self._event(cid="C1"))
        log.record_contact(self._event(cid="C2"))
        self.assertEqual(len(log.contacts_for_customer("C1")), 2)
        self.assertEqual(len(log.contacts_for_customer("C2")), 1)

    def test_unknown_customer_returns_empty(self):
        log = ServiceLog()
        self.assertEqual(len(log.contacts_for_customer("UNKNOWN")), 0)

    def test_event_channel_stored(self):
        log = ServiceLog()
        ev = ServiceEvent(customer_id="C1", event_date="2024-06-01",
                          channel="phone", contact_reason="meter_read", outcome="resolved")
        log.record_contact(ev)
        retrieved = log.contacts_for_customer("C1")[0]
        self.assertEqual(retrieved.channel, "phone")

    def test_complaint_rate(self):
        log = ServiceLog()
        log.record_contact(self._event(complaint=True))
        log.record_contact(self._event(complaint=False))
        log.record_contact(self._event(complaint=False))
        rate = log.complaint_rate()
        self.assertAlmostEqual(rate, 1/3, places=2)


if __name__ == "__main__":
    unittest.main()
