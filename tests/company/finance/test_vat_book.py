"""Tests for company/finance/vat_book.py -- Phase 317."""
from __future__ import annotations

import datetime as dt

import pytest

from company.finance.vat_book import (
    VATBook,
    VATQuarterlyReturn,
    VATRateCategory,
    VATTransaction,
    classify_vat_category,
)


def _txn(
    account_id: str = "A001",
    date: dt.date = dt.date(2023, 1, 15),
    net: float = 100.0,
    category: VATRateCategory = VATRateCategory.DOMESTIC_REDUCED,
) -> VATTransaction:
    return VATTransaction(account_id, date, net, category)


class TestClassifyVATCategory:
    def test_residential_is_reduced(self):
        assert classify_vat_category(is_residential=True) == VATRateCategory.DOMESTIC_REDUCED

    def test_large_business_is_standard(self):
        assert classify_vat_category(is_residential=False, daily_consumption_kwh=500.0) == VATRateCategory.STANDARD

    def test_sme_below_threshold_is_reduced(self):
        assert classify_vat_category(is_residential=False, daily_consumption_kwh=30.0) == VATRateCategory.DOMESTIC_REDUCED


class TestVATTransaction:
    def test_domestic_vat_rate(self):
        t = _txn(category=VATRateCategory.DOMESTIC_REDUCED)
        assert t.vat_rate == 0.05

    def test_standard_vat_rate(self):
        t = _txn(category=VATRateCategory.STANDARD)
        assert t.vat_rate == 0.20

    def test_zero_vat_rate(self):
        t = _txn(category=VATRateCategory.ZERO)
        assert t.vat_rate == 0.0

    def test_vat_gbp_domestic(self):
        t = _txn(net=200.0, category=VATRateCategory.DOMESTIC_REDUCED)
        assert t.vat_gbp == 10.0  # 5% of 200

    def test_vat_gbp_standard(self):
        t = _txn(net=100.0, category=VATRateCategory.STANDARD)
        assert t.vat_gbp == 20.0  # 20% of 100

    def test_gross_amount(self):
        t = _txn(net=100.0, category=VATRateCategory.DOMESTIC_REDUCED)
        assert t.gross_amount_gbp == 105.0

    def test_zero_vat_gross_equals_net(self):
        t = _txn(net=50.0, category=VATRateCategory.ZERO)
        assert t.gross_amount_gbp == 50.0


class TestVATQuarterlyReturn:
    def test_net_vat_due(self):
        r = VATQuarterlyReturn(
            period_start=dt.date(2023, 1, 1),
            period_end=dt.date(2023, 3, 31),
            output_vat_gbp=10000.0,
            input_vat_gbp=800.0,
        )
        assert r.net_vat_due_gbp == 9200.0

    def test_is_repayment_false(self):
        r = VATQuarterlyReturn(dt.date(2023, 1, 1), dt.date(2023, 3, 31), 10000.0, 800.0)
        assert not r.is_repayment

    def test_is_repayment_true(self):
        r = VATQuarterlyReturn(dt.date(2023, 1, 1), dt.date(2023, 3, 31), 100.0, 500.0)
        assert r.is_repayment


class TestVATBook:
    def _book(self) -> VATBook:
        return VATBook()

    def test_record_transaction(self):
        book = self._book()
        book.record_transaction(_txn())
        assert len(book._transactions) == 1

    def test_transactions_for_period(self):
        book = self._book()
        book.record_transaction(_txn(date=dt.date(2023, 1, 15)))
        book.record_transaction(_txn(date=dt.date(2023, 4, 15)))
        result = book.transactions_for_period(dt.date(2023, 1, 1), dt.date(2023, 3, 31))
        assert len(result) == 1

    def test_quarterly_return_q1(self):
        book = self._book()
        book.record_transaction(_txn(date=dt.date(2023, 2, 1), net=1000.0))
        ret = book.quarterly_return(2023, 1)
        assert ret.output_vat_gbp == 50.0  # 5% of 1000
        assert ret.input_vat_gbp == round(50.0 * 0.08, 2)

    def test_total_output_vat_gbp(self):
        book = self._book()
        book.record_transaction(_txn(net=200.0, category=VATRateCategory.DOMESTIC_REDUCED))
        book.record_transaction(_txn(net=100.0, category=VATRateCategory.STANDARD))
        # 5% of 200 = 10; 20% of 100 = 20
        assert book.total_output_vat_gbp() == 30.0

    def test_total_output_vat_filtered_by_year(self):
        book = self._book()
        book.record_transaction(_txn(date=dt.date(2022, 6, 1), net=200.0))
        book.record_transaction(_txn(date=dt.date(2023, 6, 1), net=200.0))
        assert book.total_output_vat_gbp(year=2023) == 10.0

    def test_vat_summary_keys(self):
        book = self._book()
        book.record_transaction(_txn())
        s = book.vat_summary()
        assert "total_transactions" in s
        assert "total_output_vat_gbp" in s
        assert "by_category" in s

    def test_empty_book(self):
        book = self._book()
        s = book.vat_summary()
        assert s["total_transactions"] == 0
        assert s["total_output_vat_gbp"] == 0.0
