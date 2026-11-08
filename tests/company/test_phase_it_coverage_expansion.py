"""Phase IT -- Coverage Depth Sprint XVII: contact_centre_metrics, complaint_register, conversation_log."""

import datetime as dt
import unittest
from company.crm.complaint_register import Complaint, ComplaintCategory, ComplaintRegister, ComplaintStatus

D1 = dt.date(2024, 1, 1)
D2 = dt.date(2024, 1, 31)


class TestComplaintRegister(unittest.TestCase):
    def test_raise_complaint_creates_open(self):
        reg = ComplaintRegister()
        c = reg.raise_complaint('C001', 'CUST1', D1, ComplaintCategory.BILLING)
        self.assertEqual(c.status, ComplaintStatus.OPEN)

    def test_deadline_is_56_days(self):
        reg = ComplaintRegister()
        c = reg.raise_complaint('C002', 'CUST1', D1, ComplaintCategory.SWITCH)
        self.assertEqual(c.deadline(), D1 + dt.timedelta(days=56))

    def test_overdue_when_open_and_past_deadline(self):
        reg = ComplaintRegister()
        c = reg.raise_complaint('C003', 'CUST1', dt.date(2024, 1, 1), ComplaintCategory.BILLING)
        self.assertTrue(c.is_overdue(dt.date(2024, 3, 15)))

    def test_not_overdue_when_resolved(self):
        reg = ComplaintRegister()
        c = reg.raise_complaint('C004', 'CUST1', dt.date(2024, 1, 1), ComplaintCategory.BILLING)
        c.resolve(dt.date(2024, 1, 20), upheld=True)
        self.assertFalse(c.is_overdue(dt.date(2024, 3, 15)))

    def test_resolve_upheld(self):
        reg = ComplaintRegister()
        c = reg.raise_complaint('C005', 'CUST1', D1, ComplaintCategory.TARIFF)
        c.resolve(D2, upheld=True, goodwill_gbp=25.0)
        self.assertEqual(c.status, ComplaintStatus.UPHELD)
        self.assertAlmostEqual(c.goodwill_payment_gbp, 25.0)

    def test_resolve_not_upheld(self):
        reg = ComplaintRegister()
        c = reg.raise_complaint('C006', 'CUST1', D1, ComplaintCategory.CUSTOMER_SERVICE)
        c.resolve(D2, upheld=False)
        self.assertEqual(c.status, ComplaintStatus.NOT_UPHELD)

    def test_refer_to_ombudsman(self):
        reg = ComplaintRegister()
        c = reg.raise_complaint('C007', 'CUST1', D1, ComplaintCategory.METER_READS)
        c.refer_to_ombudsman(D2)
        self.assertEqual(c.status, ComplaintStatus.OMBUDSMAN_REFERRED)

    def test_overdue_complaints_list(self):
        reg = ComplaintRegister()
        reg.raise_complaint('C008', 'CUST1', dt.date(2024, 1, 1), ComplaintCategory.BILLING)
        reg.raise_complaint('C009', 'CUST2', dt.date(2024, 3, 1), ComplaintCategory.SWITCH)
        overdue = reg.overdue_complaints(dt.date(2024, 3, 15))
        self.assertEqual(len(overdue), 1)
        self.assertEqual(overdue[0].complaint_id, 'C008')

    def test_upheld_rate_pct(self):
        reg = ComplaintRegister()
        c1 = reg.raise_complaint('C010', 'CUST1', dt.date(2024, 2, 1), ComplaintCategory.BILLING)
        c2 = reg.raise_complaint('C011', 'CUST2', dt.date(2024, 2, 1), ComplaintCategory.BILLING)
        c1.resolve(dt.date(2024, 2, 20), upheld=True)
        c2.resolve(dt.date(2024, 2, 20), upheld=False)
        self.assertAlmostEqual(reg.upheld_rate_pct(2024), 50.0, places=1)

    def test_complaints_per_100_customers(self):
        reg = ComplaintRegister()
        for i in range(5):
            reg.raise_complaint(f'X{i}', 'CUST', dt.date(2024, 1, 10), ComplaintCategory.TARIFF)
        self.assertAlmostEqual(reg.complaints_per_100_customers(200, 2024), 2.5, places=1)


if __name__ == "__main__":
    unittest.main()
