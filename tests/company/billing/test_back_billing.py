"""Tests for company/billing/back_billing.py -- Phase 314."""
from __future__ import annotations

import datetime as dt

import pytest

from company.billing.back_billing import (
    BackBillingAssessment,
    BackBillingBook,
    BackBillingReason,
)


def _assessment(
    account_id: str = "A001",
    billing_date: dt.date = dt.date(2023, 6, 1),
    period_start: dt.date = dt.date(2020, 1, 1),
    period_end: dt.date = dt.date(2023, 1, 1),
    amount: float = 600.0,
    is_domestic: bool = True,
) -> BackBillingAssessment:
    return BackBillingAssessment(
        account_id=account_id,
        billing_date=billing_date,
        consumption_period_start=period_start,
        consumption_period_end=period_end,
        billed_amount_gbp=amount,
        reason=BackBillingReason.SMART_METER_INSTALL_REVEALED,
        is_domestic=is_domestic,
    )


class TestBackBillingAssessment:
    def test_cap_applies_old_period(self):
        a = _assessment(
            billing_date=dt.date(2023, 6, 1),
            period_start=dt.date(2020, 1, 1),
            period_end=dt.date(2023, 1, 1),
        )
        assert a.cap_applies

    def test_cap_not_apply_recent_period(self):
        # All consumption within last 12 months
        a = _assessment(
            billing_date=dt.date(2023, 6, 1),
            period_start=dt.date(2022, 8, 1),
            period_end=dt.date(2023, 5, 1),
        )
        assert not a.cap_applies

    def test_cap_not_apply_non_domestic(self):
        a = _assessment(
            billing_date=dt.date(2023, 6, 1),
            period_start=dt.date(2020, 1, 1),
            period_end=dt.date(2023, 1, 1),
            is_domestic=False,
        )
        assert not a.cap_applies

    def test_cap_not_apply_before_rules_start(self):
        # Billing before SLC 31A effective date (May 2018)
        a = _assessment(
            billing_date=dt.date(2017, 12, 1),
            period_start=dt.date(2014, 1, 1),
            period_end=dt.date(2017, 1, 1),
        )
        assert not a.cap_applies

    def test_capped_amount_less_than_billed(self):
        a = _assessment(
            billing_date=dt.date(2023, 6, 1),
            period_start=dt.date(2020, 1, 1),  # 3.4 years total
            period_end=dt.date(2023, 6, 1),
            amount=600.0,
        )
        # Only 12 months out of ~3.4 years allowed
        assert a.capped_amount_gbp < a.billed_amount_gbp

    def test_written_off_is_difference(self):
        a = _assessment(amount=600.0)
        assert abs(a.written_off_gbp - (a.billed_amount_gbp - a.capped_amount_gbp)) < 0.01

    def test_no_written_off_when_cap_not_applies(self):
        a = _assessment(
            billing_date=dt.date(2023, 6, 1),
            period_start=dt.date(2022, 8, 1),
            period_end=dt.date(2023, 5, 1),
            amount=200.0,
        )
        assert a.written_off_gbp == 0.0

    def test_capped_amount_equals_billed_when_no_cap(self):
        a = _assessment(
            billing_date=dt.date(2023, 6, 1),
            period_start=dt.date(2022, 8, 1),
            period_end=dt.date(2023, 5, 1),
            amount=200.0,
        )
        assert a.capped_amount_gbp == 200.0

    def test_fully_pre_window_zero_capped(self):
        # Entire period more than 12 months before billing date
        a = _assessment(
            billing_date=dt.date(2023, 6, 1),
            period_start=dt.date(2018, 1, 1),
            period_end=dt.date(2021, 1, 1),
            amount=500.0,
        )
        # consumption_period_end (2021-01-01) < protected_start (2022-06-01)
        assert a.capped_amount_gbp == 0.0
        assert a.written_off_gbp == 500.0


class TestBackBillingBook:
    def _book(self) -> BackBillingBook:
        return BackBillingBook()

    def test_record_stores_assessment(self):
        book = self._book()
        book.record(_assessment())
        assert len(book._assessments) == 1

    def test_assessments_for_account(self):
        book = self._book()
        book.record(_assessment("A001"))
        book.record(_assessment("A001"))
        book.record(_assessment("A002"))
        assert len(book.assessments_for("A001")) == 2
        assert len(book.assessments_for("A002")) == 1

    def test_capped_assessments_filter(self):
        book = self._book()
        # capped (old period)
        book.record(_assessment(period_start=dt.date(2020, 1, 1)))
        # not capped (recent period)
        book.record(_assessment(
            billing_date=dt.date(2023, 6, 1),
            period_start=dt.date(2022, 8, 1),
            period_end=dt.date(2023, 5, 1),
        ))
        assert len(book.capped_assessments()) == 1

    def test_total_written_off_gbp(self):
        book = self._book()
        book.record(_assessment(amount=600.0))  # will be partially written off
        off = book.total_written_off_gbp()
        assert off > 0

    def test_non_domestic_not_written_off(self):
        book = self._book()
        book.record(_assessment(
            period_start=dt.date(2020, 1, 1),
            amount=400.0,
            is_domestic=False,
        ))
        assert book.total_written_off_gbp() == 0.0

    def test_back_billing_summary_keys(self):
        book = self._book()
        book.record(_assessment())
        s = book.back_billing_summary()
        assert "total_assessments" in s
        assert "capped_count" in s
        assert "total_billed_gbp" in s
        assert "total_written_off_gbp" in s
        assert "non_domestic_count" in s

    def test_empty_book_summary(self):
        book = self._book()
        s = book.back_billing_summary()
        assert s["total_assessments"] == 0
        assert s["total_written_off_gbp"] == 0.0
