# Increment 3: the legs of tests/company/test_phase_iv_coverage_expansion.py that test archived modules. Its live legs stay there.
"""Phase IV -- Coverage Depth Sprint XIX: revenue_accruals, renewals_book, switch_governance."""

import datetime as dt
import unittest

from company.finance.revenue_accruals import (
    RevenueAccrualsLedger, RevenueEntry, RevenueType, RecognitionBasis,
)
from company.crm.renewals_book import (
    RenewalsBook, RenewalOutcome, OfferType,
)

D1 = dt.date(2024, 1, 1)
D2 = dt.date(2024, 1, 31)


class TestRevenueAccrualsLedger(unittest.TestCase):
    def _post(self, ledger, amount=1000.0, basis=RecognitionBasis.BILLED,
              rev_type=RevenueType.COMMODITY):
        return ledger.post("CUST1", D1, D2, rev_type, basis, amount)

    def test_post_creates_entry(self):
        ledger = RevenueAccrualsLedger()
        e = self._post(ledger)
        self.assertIsInstance(e, RevenueEntry)
        self.assertAlmostEqual(e.amount_gbp, 1000.0)

    def test_period_days(self):
        ledger = RevenueAccrualsLedger()
        e = self._post(ledger)
        self.assertEqual(e.period_days, 31)

    def test_daily_revenue_gbp(self):
        ledger = RevenueAccrualsLedger()
        e = self._post(ledger, amount=310.0)
        self.assertAlmostEqual(e.daily_revenue_gbp, round(310.0 / 31, 4), places=4)

    def test_billed_revenue_only_billed(self):
        ledger = RevenueAccrualsLedger()
        self._post(ledger, amount=500.0, basis=RecognitionBasis.BILLED)
        self._post(ledger, amount=300.0, basis=RecognitionBasis.ACCRUED)
        self.assertAlmostEqual(ledger.billed_revenue_gbp(D1, D2), 500.0, places=2)

    def test_accrued_revenue_only_accrued(self):
        ledger = RevenueAccrualsLedger()
        self._post(ledger, amount=500.0, basis=RecognitionBasis.BILLED)
        self._post(ledger, amount=300.0, basis=RecognitionBasis.ACCRUED)
        self.assertAlmostEqual(ledger.accrued_revenue_gbp(D1, D2), 300.0, places=2)

    def test_total_revenue_gbp(self):
        ledger = RevenueAccrualsLedger()
        self._post(ledger, amount=500.0, basis=RecognitionBasis.BILLED)
        self._post(ledger, amount=300.0, basis=RecognitionBasis.ACCRUED)
        self.assertAlmostEqual(ledger.total_revenue_gbp(D1, D2), 800.0, places=2)

    def test_accrual_ratio_pct(self):
        ledger = RevenueAccrualsLedger()
        self._post(ledger, amount=300.0, basis=RecognitionBasis.BILLED)
        self._post(ledger, amount=700.0, basis=RecognitionBasis.ACCRUED)
        self.assertAlmostEqual(ledger.accrual_ratio(D1, D2), 70.0, places=1)

    def test_by_type_groups(self):
        ledger = RevenueAccrualsLedger()
        self._post(ledger, amount=900.0, rev_type=RevenueType.COMMODITY)
        self._post(ledger, amount=100.0, rev_type=RevenueType.STANDING_CHARGE)
        by_type = ledger.by_type(D1, D2)
        self.assertIn("commodity", by_type)
        self.assertIn("standing_charge", by_type)
        self.assertAlmostEqual(by_type["commodity"], 900.0, places=2)

    def test_monthly_summary_structure(self):
        ledger = RevenueAccrualsLedger()
        self._post(ledger, amount=1000.0)
        s = ledger.monthly_summary(2024, 1)
        self.assertEqual(s["year"], 2024)
        self.assertIn("billed_gbp", s)
        self.assertIn("accrued_gbp", s)
        self.assertIn("total_gbp", s)

    def test_entries_in_period_overlap(self):
        ledger = RevenueAccrualsLedger()
        self._post(ledger, amount=100.0)
        outside = dt.date(2024, 3, 1)
        self.assertEqual(len(ledger.entries_in_period(outside, outside)), 0)


class TestRenewalsBook(unittest.TestCase):
    def _add(self, book, cid="C1", seg="domestic", year=2024,
             outcome=RenewalOutcome.RENEWED, offer=OfferType.BETTER_TARIFF,
             outbound=False):
        return book.add(cid, seg, dt.date(year, 6, 1), outcome,
                        offer_type=offer, was_outbound_contact=outbound)

    def test_add_creates_record(self):
        book = RenewalsBook()
        r = self._add(book)
        self.assertEqual(r.customer_id, "C1")
        self.assertTrue(r.accepted)

    def test_accepted_only_for_renewed(self):
        book = RenewalsBook()
        r = book.add("C2", "domestic", dt.date(2024, 6, 1), RenewalOutcome.LAPSED)
        self.assertFalse(r.accepted)

    def test_renewal_rate_excludes_moved_out(self):
        book = RenewalsBook()
        self._add(book, cid="A", outcome=RenewalOutcome.RENEWED)
        self._add(book, cid="B", outcome=RenewalOutcome.LAPSED)
        self._add(book, cid="C", outcome=RenewalOutcome.MOVED_OUT)
        rate = book.renewal_rate(2024)
        self.assertAlmostEqual(rate, 50.0, places=1)

    def test_lapse_rate_complement(self):
        book = RenewalsBook()
        self._add(book, cid="A", outcome=RenewalOutcome.RENEWED)
        self._add(book, cid="B", outcome=RenewalOutcome.LAPSED)
        self.assertAlmostEqual(book.lapse_rate(2024), 50.0, places=1)

    def test_renewal_rate_none_if_no_eligible(self):
        book = RenewalsBook()
        self._add(book, cid="A", outcome=RenewalOutcome.MOVED_OUT)
        self.assertIsNone(book.renewal_rate(2024))

    def test_renewal_rate_segment_filter(self):
        book = RenewalsBook()
        self._add(book, cid="A", seg="domestic", outcome=RenewalOutcome.RENEWED)
        self._add(book, cid="B", seg="sme", outcome=RenewalOutcome.LAPSED)
        rate = book.renewal_rate(2024, segment="domestic")
        self.assertAlmostEqual(rate, 100.0, places=1)

    def test_outbound_lift_calculated(self):
        book = RenewalsBook()
        book.add("A", "domestic", dt.date(2024, 6, 1), RenewalOutcome.RENEWED,
                 was_outbound_contact=True)
        book.add("B", "domestic", dt.date(2024, 6, 1), RenewalOutcome.LAPSED,
                 was_outbound_contact=False)
        lift = book.outbound_lift(2024)
        self.assertIsNotNone(lift)
        self.assertGreater(lift, 0)

    def test_outbound_lift_none_if_no_outbound(self):
        book = RenewalsBook()
        self._add(book, outbound=False)
        self.assertIsNone(book.outbound_lift(2024))

    def test_by_offer_type_includes_renewal_rate(self):
        book = RenewalsBook()
        self._add(book, cid="A", offer=OfferType.LOYALTY_DISCOUNT, outcome=RenewalOutcome.RENEWED)
        self._add(book, cid="B", offer=OfferType.LOYALTY_DISCOUNT, outcome=RenewalOutcome.LAPSED)
        by_offer = book.by_offer_type(2024)
        self.assertIn("loyalty_discount", by_offer)
        self.assertAlmostEqual(by_offer["loyalty_discount"]["renewal_rate"], 50.0, places=1)

    def test_annual_summary_structure(self):
        book = RenewalsBook()
        self._add(book)
        s = book.annual_summary(2024)
        self.assertIn("renewal_rate_pct", s)
        self.assertIn("lapse_rate_pct", s)
        self.assertIn("by_offer_type", s)
