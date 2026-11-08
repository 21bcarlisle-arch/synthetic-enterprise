# Increment 3: the legs of tests/company/test_phase_ja_coverage_expansion.py that test archived modules. Its live legs stay there.
"""Phase JA coverage expansion: billing_dispute, back_billing.

TestArrearsBook removed (Phase QD) -- company/billing/arrears_book.py was
confirmed dead code (zero non-test importers) and deleted.
"""
import datetime as dt
import unittest


class TestBillingDisputeBook(unittest.TestCase):

    def _book(self):
        from company.billing.billing_dispute import (
            BillingDisputeBook, DisputeReason, DisputeStatus,
        )
        return BillingDisputeBook(), DisputeReason, DisputeStatus

    def test_sequential_ids(self):
        book, R, _ = self._book()
        d1 = book.raise_dispute("A1", R.ESTIMATED_BILL, 120.0, dt.date(2023, 1, 10))
        d2 = book.raise_dispute("A2", R.TARIFF_ERROR, 50.0, dt.date(2023, 2, 1))
        self.assertEqual(d1.dispute_id, "DISP-00001")
        self.assertEqual(d2.dispute_id, "DISP-00002")

    def test_is_open_on_raised(self):
        book, R, _ = self._book()
        d = book.raise_dispute("A1", R.METER_ERROR, 80.0, dt.date(2023, 1, 1))
        self.assertTrue(d.is_open)

    def test_can_disconnect_false_while_open(self):
        book, R, _ = self._book()
        d = book.raise_dispute("A1", R.TARIFF_ERROR, 200.0, dt.date(2023, 1, 1))
        self.assertFalse(d.can_disconnect)

    def test_net_disputed_amount(self):
        book, R, S = self._book()
        d = book.raise_dispute("A1", R.TARIFF_ERROR, 300.0, dt.date(2023, 1, 1))
        book.update_dispute(d.dispute_id, S.CREDIT_ISSUED, dt.date(2023, 1, 15),
                            credit_applied_gbp=100.0)
        updated = book.disputes_for_account("A1")[0]
        self.assertAlmostEqual(updated.net_disputed_amount_gbp, 200.0)

    def test_is_final_response_overdue(self):
        book, R, _ = self._book()
        d = book.raise_dispute("A1", R.BACK_BILLING, 500.0, dt.date(2023, 1, 1))
        # 57 days later = overdue (>56)
        self.assertTrue(d.is_final_response_overdue(dt.date(2023, 2, 27)))

    def test_is_final_response_not_overdue(self):
        book, R, _ = self._book()
        d = book.raise_dispute("A1", R.BACK_BILLING, 500.0, dt.date(2023, 1, 1))
        self.assertFalse(d.is_final_response_overdue(dt.date(2023, 2, 25)))

    def test_update_dispute_to_resolved(self):
        book, R, S = self._book()
        d = book.raise_dispute("A1", R.PAYMENT_NOT_CREDITED, 100.0, dt.date(2023, 1, 1))
        updated = book.update_dispute(d.dispute_id, S.RESOLVED_IN_CUSTOMER_FAVOUR,
                                      dt.date(2023, 1, 20))
        self.assertEqual(updated.status, S.RESOLVED_IN_CUSTOMER_FAVOUR)
        self.assertFalse(updated.is_open)

    def test_accounts_blocked_from_disconnection(self):
        book, R, S = self._book()
        d1 = book.raise_dispute("A1", R.METER_ERROR, 100.0, dt.date(2023, 1, 1))
        book.raise_dispute("A2", R.TARIFF_ERROR, 200.0, dt.date(2023, 1, 1))
        # Resolve one
        book.update_dispute(d1.dispute_id, S.RESOLVED_IN_SUPPLIER_FAVOUR, dt.date(2023, 2, 1))
        blocked = book.accounts_blocked_from_disconnection()
        self.assertNotIn("A1", blocked)
        self.assertIn("A2", blocked)

    def test_overdue_final_responses(self):
        book, R, _ = self._book()
        book.raise_dispute("A1", R.ESTIMATED_BILL, 100.0, dt.date(2023, 1, 1))
        book.raise_dispute("A2", R.TARIFF_ERROR, 200.0, dt.date(2023, 3, 1))
        overdue = book.overdue_final_responses(dt.date(2023, 3, 10))
        self.assertEqual(len(overdue), 1)
        self.assertEqual(overdue[0].account_id, "A1")

    def test_total_disputed_amount_gbp(self):
        book, R, S = self._book()
        d1 = book.raise_dispute("A1", R.METER_ERROR, 150.0, dt.date(2023, 1, 1))
        book.raise_dispute("A2", R.TARIFF_ERROR, 250.0, dt.date(2023, 1, 1))
        # Resolve one
        book.update_dispute(d1.dispute_id, S.RESOLVED_IN_SUPPLIER_FAVOUR, dt.date(2023, 2, 1))
        self.assertAlmostEqual(book.total_disputed_amount_gbp(), 250.0)
