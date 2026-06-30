"""Phase JA coverage expansion: arrears_book, billing_dispute, back_billing."""
import datetime as dt
import unittest


class TestArrearsBook(unittest.TestCase):

    def _book(self):
        from company.billing.arrears_book import ArrearsBook, ArrearsStage
        return ArrearsBook(), ArrearsStage

    def test_sequential_ids(self):
        book, _ = self._book()
        c1 = book.open_case("C1", 150.0, dt.date(2023, 1, 1))
        c2 = book.open_case("C2", 200.0, dt.date(2023, 2, 1))
        self.assertEqual(c1.case_id, "ARR-0001")
        self.assertEqual(c2.case_id, "ARR-0002")

    def test_is_open_true_for_active_stage(self):
        book, S = self._book()
        c = book.open_case("C1", 100.0, dt.date(2023, 1, 1))
        self.assertTrue(c.is_open)

    def test_is_open_false_after_resolve(self):
        book, _ = self._book()
        c = book.open_case("C1", 100.0, dt.date(2023, 1, 1))
        book.resolve(c.case_id, dt.date(2023, 2, 1))
        self.assertFalse(c.is_open)

    def test_outstanding_gbp(self):
        book, _ = self._book()
        c = book.open_case("C1", 200.0, dt.date(2023, 1, 1))
        book.record_recovery(c.case_id, 75.0)
        self.assertAlmostEqual(c.outstanding_gbp, 125.0)

    def test_advance_stage(self):
        book, S = self._book()
        c = book.open_case("C1", 100.0, dt.date(2023, 1, 1))
        book.advance_stage(c.case_id, S.FIRST_NOTICE, dt.date(2023, 1, 15))
        self.assertEqual(c.stage, S.FIRST_NOTICE)
        self.assertEqual(c.stage_date, dt.date(2023, 1, 15))

    def test_advance_stage_raises_on_terminal(self):
        book, S = self._book()
        c = book.open_case("C1", 100.0, dt.date(2023, 1, 1))
        book.write_off(c.case_id, dt.date(2023, 3, 1))
        with self.assertRaises(ValueError):
            book.advance_stage(c.case_id, S.FIRST_NOTICE, dt.date(2023, 4, 1))

    def test_write_off(self):
        book, S = self._book()
        c = book.open_case("C1", 100.0, dt.date(2023, 1, 1))
        book.write_off(c.case_id, dt.date(2023, 6, 1))
        self.assertEqual(c.stage, S.WRITTEN_OFF)
        self.assertFalse(c.is_open)

    def test_open_cases(self):
        book, _ = self._book()
        c1 = book.open_case("C1", 100.0, dt.date(2023, 1, 1))
        c2 = book.open_case("C2", 200.0, dt.date(2023, 2, 1))
        book.resolve(c1.case_id, dt.date(2023, 3, 1))
        open_ids = {c.case_id for c in book.open_cases()}
        self.assertNotIn(c1.case_id, open_ids)
        self.assertIn(c2.case_id, open_ids)

    def test_total_arrears_outstanding_gbp(self):
        book, _ = self._book()
        c1 = book.open_case("C1", 200.0, dt.date(2023, 1, 1))
        c2 = book.open_case("C2", 300.0, dt.date(2023, 2, 1))
        book.record_recovery(c1.case_id, 50.0)
        book.resolve(c2.case_id, dt.date(2023, 5, 1))
        self.assertAlmostEqual(book.total_arrears_outstanding_gbp(), 150.0)

    def test_annual_summary_structure(self):
        book, _ = self._book()
        book.open_case("C1", 100.0, dt.date(2023, 1, 1))
        s = book.annual_summary()
        self.assertIn("total_cases", s)
        self.assertIn("open_cases", s)
        self.assertIn("total_outstanding_gbp", s)
        self.assertIn("by_stage", s)


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


class TestBackBilling(unittest.TestCase):

    def _assessment(self, billing_date, period_start, period_end,
                    amount=500.0, is_domestic=True,
                    reason=None):
        from company.billing.back_billing import BackBillingAssessment, BackBillingReason
        if reason is None:
            reason = BackBillingReason.ESTIMATED_READ_CORRECTED
        return BackBillingAssessment(
            account_id="ACC1",
            billing_date=billing_date,
            consumption_period_start=period_start,
            consumption_period_end=period_end,
            billed_amount_gbp=amount,
            reason=reason,
            is_domestic=is_domestic,
        )

    def test_cap_applies_when_period_predates_window(self):
        # billing_date=2023-01-01, protected_start=2022-01-01
        # consumption from 2020-01-01 to 2023-01-01 → starts before protected window
        a = self._assessment(dt.date(2023, 1, 1), dt.date(2020, 1, 1), dt.date(2023, 1, 1))
        self.assertTrue(a.cap_applies)

    def test_cap_does_not_apply_before_rules_start(self):
        # billing before 2018-05-01
        a = self._assessment(dt.date(2017, 1, 1), dt.date(2014, 1, 1), dt.date(2017, 1, 1))
        self.assertFalse(a.cap_applies)

    def test_cap_does_not_apply_for_non_domestic(self):
        a = self._assessment(dt.date(2023, 1, 1), dt.date(2020, 1, 1), dt.date(2023, 1, 1),
                              is_domestic=False)
        self.assertFalse(a.cap_applies)

    def test_cap_does_not_apply_within_12_months(self):
        # consumption entirely within the 12-month window
        a = self._assessment(dt.date(2023, 6, 1), dt.date(2022, 8, 1), dt.date(2023, 6, 1))
        self.assertFalse(a.cap_applies)

    def test_capped_amount_reduces_when_cap_applies(self):
        # 3-year period, only last 12 months billable → ~1/3 of 3yr period
        a = self._assessment(dt.date(2023, 1, 1), dt.date(2020, 1, 1), dt.date(2023, 1, 1),
                              amount=1095.0)
        # total_days ~1096, allowed_days ~365 → ~1/3
        self.assertLess(a.capped_amount_gbp, a.billed_amount_gbp)
        self.assertGreater(a.capped_amount_gbp, 0)

    def test_written_off_gbp_equals_difference(self):
        a = self._assessment(dt.date(2023, 1, 1), dt.date(2020, 1, 1), dt.date(2023, 1, 1),
                              amount=1095.0)
        self.assertAlmostEqual(a.written_off_gbp,
                               round(a.billed_amount_gbp - a.capped_amount_gbp, 2))

    def test_no_cap_capped_equals_billed(self):
        a = self._assessment(dt.date(2023, 1, 1), dt.date(2022, 6, 1), dt.date(2023, 1, 1))
        self.assertAlmostEqual(a.capped_amount_gbp, a.billed_amount_gbp)

    def test_book_record_and_total_written_off(self):
        from company.billing.back_billing import BackBillingBook
        book = BackBillingBook()
        a1 = self._assessment(dt.date(2023, 1, 1), dt.date(2019, 1, 1), dt.date(2023, 1, 1),
                               amount=1200.0)
        a2 = self._assessment(dt.date(2023, 6, 1), dt.date(2022, 9, 1), dt.date(2023, 6, 1),
                               amount=300.0)
        book.record(a1)
        book.record(a2)
        expected_written_off = round(a1.written_off_gbp + a2.written_off_gbp, 2)
        self.assertAlmostEqual(book.total_written_off_gbp(), expected_written_off)

    def test_book_capped_assessments(self):
        from company.billing.back_billing import BackBillingBook
        book = BackBillingBook()
        a_cap = self._assessment(dt.date(2023, 1, 1), dt.date(2019, 1, 1), dt.date(2023, 1, 1))
        a_ok = self._assessment(dt.date(2023, 1, 1), dt.date(2022, 6, 1), dt.date(2023, 1, 1))
        book.record(a_cap)
        book.record(a_ok)
        capped = book.capped_assessments()
        self.assertEqual(len(capped), 1)
        self.assertEqual(capped[0], a_cap)

    def test_back_billing_summary_structure(self):
        from company.billing.back_billing import BackBillingBook
        book = BackBillingBook()
        book.record(self._assessment(dt.date(2023, 1, 1), dt.date(2019, 1, 1), dt.date(2023, 1, 1)))
        s = book.back_billing_summary()
        self.assertIn("total_assessments", s)
        self.assertIn("capped_count", s)
        self.assertIn("total_billed_gbp", s)
        self.assertIn("total_written_off_gbp", s)
        self.assertEqual(s["total_assessments"], 1)
        self.assertEqual(s["capped_count"], 1)


if __name__ == "__main__":
    unittest.main()
