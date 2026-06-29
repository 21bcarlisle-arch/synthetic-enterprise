"""Tests for Phase Z: Smart Meter Consumption Reconciliation Book."""
from __future__ import annotations

import datetime as dt

import pytest

from company.billing.smart_meter_reconciliation import (
    ReconciliationAdjustment,
    ReconciliationType,
    SmartMeterReconciliationBook,
)


def _adj(
    estimated=3000.0, actual=3400.0, rate=0.285,
    period_start=None, period_end=None, as_of=None,
    domestic=True, account="C1",
) -> ReconciliationAdjustment:
    start = period_start or dt.date(2024, 1, 1)
    end = period_end or dt.date(2024, 12, 31)
    as_of = as_of or dt.date(2025, 1, 15)
    book = SmartMeterReconciliationBook()
    return book.reconcile(account, start, end, estimated, actual, rate, as_of, domestic)


class TestReconciliationAdjustment:
    def test_underbilled_type(self):
        a = _adj(estimated=3000, actual=3400)
        assert a.reconciliation_type == ReconciliationType.UNDERBILLED

    def test_overbilled_type(self):
        a = _adj(estimated=3400, actual=3000)
        assert a.reconciliation_type == ReconciliationType.OVERBILLED

    def test_no_adjustment_when_equal(self):
        a = _adj(estimated=3000, actual=3000)
        assert a.reconciliation_type == ReconciliationType.NO_ADJUSTMENT

    def test_adjustment_kwh(self):
        a = _adj(estimated=3000, actual=3400)
        assert abs(a.adjustment_kwh - 400.0) < 0.01

    def test_credit_debit_gbp_positive_for_undercharge(self):
        a = _adj(estimated=3000, actual=3400, rate=0.285)
        assert abs(a.credit_debit_gbp - 114.0) < 0.01

    def test_credit_debit_gbp_negative_for_overcharge(self):
        a = _adj(estimated=3400, actual=3000, rate=0.285)
        assert a.credit_debit_gbp < 0

    def test_back_billing_not_protected_within_12_months(self):
        a = _adj(
            period_end=dt.date(2024, 6, 30),
            as_of=dt.date(2025, 1, 15),
        )
        assert a.is_back_billing_protected is False

    def test_back_billing_protected_over_12_months(self):
        a = _adj(
            estimated=3000, actual=3400,
            period_end=dt.date(2023, 1, 1),
            as_of=dt.date(2025, 1, 15),
        )
        assert a.is_back_billing_protected is True

    def test_back_billing_not_protected_for_non_domestic(self):
        a = _adj(
            estimated=3000, actual=3400,
            period_end=dt.date(2023, 1, 1),
            as_of=dt.date(2025, 1, 15),
            domestic=False,
        )
        assert a.is_back_billing_protected is False

    def test_recoverable_gbp_zero_when_protected(self):
        a = _adj(
            estimated=3000, actual=3400,
            period_end=dt.date(2023, 1, 1),
            as_of=dt.date(2025, 1, 15),
        )
        assert a.recoverable_gbp == 0.0

    def test_recoverable_gbp_full_when_not_protected(self):
        a = _adj(estimated=3000, actual=3400, rate=0.285)
        assert abs(a.recoverable_gbp - 114.0) < 0.01

    def test_is_material_above_five_pounds(self):
        a = _adj(estimated=3000, actual=3100, rate=0.285)
        assert a.is_material is True

    def test_is_not_material_below_five_pounds(self):
        a = _adj(estimated=3000, actual=3005, rate=0.285)
        assert a.is_material is False

    def test_adjustment_is_frozen(self):
        a = _adj()
        with pytest.raises((AttributeError, TypeError)):
            a.account_id = "other"


class TestSmartMeterReconciliationBook:
    def _book_with_adjustments(self) -> SmartMeterReconciliationBook:
        book = SmartMeterReconciliationBook()
        book.reconcile("C1", dt.date(2024,1,1), dt.date(2024,12,31),
                       3000, 3400, 0.285, dt.date(2025,1,15))
        book.reconcile("C2", dt.date(2024,1,1), dt.date(2024,12,31),
                       4000, 3600, 0.285, dt.date(2025,1,15))
        return book

    def test_adjustments_for_customer(self):
        book = self._book_with_adjustments()
        assert len(book.adjustments_for("C1")) == 1
        assert len(book.adjustments_for("C2")) == 1

    def test_credits_owed_to_customers(self):
        book = self._book_with_adjustments()
        credits = book.credits_owed_to_customers()
        assert len(credits) == 1
        assert credits[0].account_id == "C2"

    def test_charges_owed_by_customers(self):
        book = self._book_with_adjustments()
        charges = book.charges_owed_by_customers()
        assert len(charges) == 1
        assert charges[0].account_id == "C1"

    def test_back_billing_protected_adjustments(self):
        book = SmartMeterReconciliationBook()
        book.reconcile("C1", dt.date(2022,1,1), dt.date(2022,12,31),
                       3000, 3400, 0.285, dt.date(2025,1,15))
        protected = book.back_billing_protected_adjustments()
        assert len(protected) == 1

    def test_total_credit_exposure(self):
        book = self._book_with_adjustments()
        expected_credit = abs((3600 - 4000) * 0.285)
        assert abs(book.total_credit_exposure_gbp - expected_credit) < 0.01

    def test_total_recoverable(self):
        book = self._book_with_adjustments()
        expected_recoverable = (3400 - 3000) * 0.285
        assert abs(book.total_recoverable_gbp - expected_recoverable) < 0.01

    def test_total_unrecoverable_back_billing(self):
        book = SmartMeterReconciliationBook()
        book.reconcile("C1", dt.date(2022,1,1), dt.date(2022,12,31),
                       3000, 3400, 0.285, dt.date(2025,1,15))
        assert book.total_unrecoverable_gbp > 0

    def test_reconciliation_summary_keys(self):
        book = self._book_with_adjustments()
        s = book.reconciliation_summary()
        expected_keys = [
            "total_adjustments", "overbilled_count", "underbilled_count",
            "back_billing_protected_count", "total_credit_exposure_gbp",
            "total_recoverable_gbp", "total_unrecoverable_gbp",
            "material_adjustment_count",
        ]
        for key in expected_keys:
            assert key in s

    def test_empty_book_summary(self):
        book = SmartMeterReconciliationBook()
        s = book.reconciliation_summary()
        assert s["total_adjustments"] == 0
        assert s["total_credit_exposure_gbp"] == 0.0
