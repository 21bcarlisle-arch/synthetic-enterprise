"""Phase IX -- Coverage Depth Sprint XXI: ancillary_products, tariff_notification, service_log."""

import datetime as dt
import unittest
from company.crm.service_log import ServiceLog, ServiceEvent

D1 = dt.date(2024, 1, 1)
D2 = dt.date(2024, 12, 31)


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
