"""Phase JA coverage expansion: billing_dispute, back_billing.

TestArrearsBook removed (Phase QD) -- company/billing/arrears_book.py was
confirmed dead code (zero non-test importers) and deleted.
"""
import datetime as dt
import unittest


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
