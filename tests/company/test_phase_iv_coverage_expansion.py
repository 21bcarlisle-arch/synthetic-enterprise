"""Phase IV -- Coverage Depth Sprint XIX: revenue_accruals, renewals_book, switch_governance."""

import datetime as dt
import unittest
from company.market.switch_governance import (
    SwitchGovernanceBook, ObjectionReason, ObjectionOutcome,
    ErroneousTransferStatus, COOLING_OFF_DAYS, OBJECTION_WINDOW_DAYS,
)

D1 = dt.date(2024, 1, 1)
D2 = dt.date(2024, 1, 31)


class TestSwitchGovernanceBook(unittest.TestCase):
    def test_record_cancellation_within_cooling_off(self):
        book = SwitchGovernanceBook()
        c = book.record_cancellation("C1", "MPAN1", dt.date(2024, 1, 1), dt.date(2024, 1, 10))
        self.assertTrue(c.within_cooling_off)
        self.assertEqual(c.days_after_sale, 9)

    def test_cancellation_outside_cooling_off(self):
        book = SwitchGovernanceBook()
        c = book.record_cancellation("C1", "MPAN1", dt.date(2024, 1, 1), dt.date(2024, 1, 20))
        self.assertFalse(c.within_cooling_off)

    def test_raise_objection_creates_id(self):
        book = SwitchGovernanceBook()
        obj = book.raise_objection("MPAN1", "SUP-A", dt.date(2024, 1, 1), dt.date(2024, 1, 5),
                                    ObjectionReason.DEBT)
        self.assertEqual(obj.objection_id, "OBJ-0001")
        self.assertFalse(obj.is_resolved)

    def test_objection_within_window(self):
        book = SwitchGovernanceBook()
        obj = book.raise_objection("MPAN1", "SUP-A", dt.date(2024, 1, 1), dt.date(2024, 1, 10),
                                    ObjectionReason.CONTRACT_IN_TERM)
        self.assertTrue(obj.within_objection_window)

    def test_resolve_objection_sets_outcome(self):
        book = SwitchGovernanceBook()
        obj = book.raise_objection("MPAN2", "SUP-B", dt.date(2024, 1, 1), dt.date(2024, 1, 5),
                                    ObjectionReason.DEBT)
        book.resolve_objection(obj.objection_id, ObjectionOutcome.UPHELD, dt.date(2024, 1, 15))
        self.assertTrue(obj.is_resolved)
        self.assertEqual(obj.outcome, ObjectionOutcome.UPHELD)

    def test_open_objections_excludes_resolved(self):
        book = SwitchGovernanceBook()
        obj1 = book.raise_objection("A", "S", dt.date(2024, 1, 1), dt.date(2024, 1, 5),
                                     ObjectionReason.DEBT)
        obj2 = book.raise_objection("B", "S", dt.date(2024, 1, 1), dt.date(2024, 1, 5),
                                     ObjectionReason.CUSTOMER_REQUEST)
        book.resolve_objection(obj1.objection_id, ObjectionOutcome.REJECTED, dt.date(2024, 1, 15))
        self.assertEqual(len(book.open_objections()), 1)

    def test_report_et_creates_id(self):
        book = SwitchGovernanceBook()
        et = book.report_et("MPAN3", "LOSING", "GAINING", dt.date(2024, 2, 1), dt.date(2024, 2, 5))
        self.assertEqual(et.et_id, "ET-0001")
        self.assertFalse(et.is_resolved)
        self.assertEqual(et.days_to_report, 4)

    def test_resolve_et_marks_resolved(self):
        book = SwitchGovernanceBook()
        et = book.report_et("MPAN4", "L", "G", dt.date(2024, 2, 1), dt.date(2024, 2, 5))
        book.resolve_et(et.et_id, ErroneousTransferStatus.CUSTOMER_RETURNED, dt.date(2024, 2, 20))
        self.assertTrue(et.is_resolved)

    def test_open_ets_excludes_resolved(self):
        book = SwitchGovernanceBook()
        et = book.report_et("M1", "L", "G", dt.date(2024, 2, 1), dt.date(2024, 2, 5))
        book.report_et("M2", "L", "G", dt.date(2024, 2, 1), dt.date(2024, 2, 5))
        book.resolve_et(et.et_id, ErroneousTransferStatus.CLOSED_NO_ACTION, dt.date(2024, 2, 20))
        self.assertEqual(len(book.open_ets()), 1)

    def test_annual_summary(self):
        book = SwitchGovernanceBook()
        book.record_cancellation("C", "M", dt.date(2024, 1, 1), dt.date(2024, 1, 5))
        book.raise_objection("M", "S", dt.date(2024, 1, 1), dt.date(2024, 1, 3), ObjectionReason.DEBT)
        s = book.annual_summary(2024)
        self.assertEqual(s["cooling_off_cancellations"], 1)
        self.assertEqual(s["objections_raised"], 1)
        self.assertEqual(s["year"], 2024)


if __name__ == "__main__":
    unittest.main()
