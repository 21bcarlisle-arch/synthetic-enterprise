"""Tests for company/billing/ppm_debt_loading.py -- Phase 313."""
from __future__ import annotations

import datetime as dt

import pytest

from company.billing.ppm_debt_loading import (
    PPMDebtLoad,
    PPMDebtLoadStatus,
    PPMDebtLoadingBook,
)


def _load(
    account_id: str = "A001",
    debt: float = 200.0,
    rate: float = 5.0,
    is_smart: bool = False,
    consented: bool = False,
    is_domestic: bool = True,
    status: PPMDebtLoadStatus = PPMDebtLoadStatus.ACTIVE,
) -> PPMDebtLoad:
    return PPMDebtLoad(
        account_id=account_id,
        mprn_or_mpan="MP001",
        debt_amount_gbp=debt,
        load_date=dt.date(2023, 1, 1),
        recovery_rate_pct=rate,
        is_domestic=is_domestic,
        is_smart_meter=is_smart,
        customer_consented=consented,
        status=status,
    )


class TestPPMDebtLoad:
    def test_is_compliant_standard(self):
        r = _load(debt=200.0, rate=5.0)
        assert r.is_compliant

    def test_non_compliant_exceeds_250(self):
        r = _load(debt=300.0, rate=5.0)
        assert not r.is_compliant

    def test_non_compliant_rate_over_5pct(self):
        r = _load(debt=200.0, rate=6.0)
        assert not r.is_compliant

    def test_smart_meter_non_compliant_without_consent(self):
        r = _load(debt=200.0, rate=5.0, is_smart=True, consented=False)
        assert not r.is_compliant

    def test_smart_meter_compliant_with_consent(self):
        r = _load(debt=200.0, rate=5.0, is_smart=True, consented=True)
        assert r.is_compliant

    def test_max_load_domestic(self):
        r = _load(debt=200.0, is_domestic=True)
        assert r.max_load_gbp == 250.0

    def test_expected_recovery_days(self):
        r = _load(debt=100.0, rate=5.0)
        # monthly spend 200 GBP; daily 6.67; daily recovery 5% = 0.333; days = 100/0.333 = 300
        result = r.expected_recovery_days(200.0)
        assert result is not None
        assert result > 0

    def test_expected_recovery_days_zero_spend(self):
        r = _load(debt=100.0)
        assert r.expected_recovery_days(0.0) is None

    def test_expected_recovery_days_zero_rate(self):
        r = _load(debt=100.0, rate=0.0)
        assert r.expected_recovery_days(200.0) is None

    def test_at_limit_compliant(self):
        r = _load(debt=250.0, rate=5.0)
        assert r.is_compliant


class TestPPMDebtLoadingBook:
    def _book(self) -> PPMDebtLoadingBook:
        return PPMDebtLoadingBook()

    def test_record_load_stores_entry(self):
        book = self._book()
        book.record_load(_load("A001"))
        assert len(book.active_loads()) == 1

    def test_suspend_sets_status(self):
        book = self._book()
        book.record_load(_load("A001"))
        r = book.suspend("A001")
        assert r.status == PPMDebtLoadStatus.SUSPENDED
        assert len(book.active_loads()) == 0

    def test_complete_sets_status(self):
        book = self._book()
        book.record_load(_load("A001"))
        r = book.complete("A001")
        assert r.status == PPMDebtLoadStatus.COMPLETED

    def test_non_compliant_loads_filter(self):
        book = self._book()
        book.record_load(_load("A001", debt=200.0, rate=5.0))  # compliant
        book.record_load(_load("A002", debt=300.0, rate=5.0))  # over limit
        book.record_load(_load("A003", debt=200.0, rate=7.0))  # rate too high
        assert len(book.non_compliant_loads()) == 2

    def test_smart_meter_consents_missing(self):
        book = self._book()
        book.record_load(_load("A001", is_smart=True, consented=False))
        book.record_load(_load("A002", is_smart=True, consented=True))
        book.record_load(_load("A003", is_smart=False))
        assert len(book.smart_meter_consents_missing()) == 1
        assert book.smart_meter_consents_missing()[0].account_id == "A001"

    def test_smart_consent_missing_excluded_if_not_active(self):
        book = self._book()
        book.record_load(_load("A001", is_smart=True, consented=False))
        book.suspend("A001")
        assert len(book.smart_meter_consents_missing()) == 0

    def test_total_loaded_gbp(self):
        book = self._book()
        book.record_load(_load("A001", debt=100.0))
        book.record_load(_load("A002", debt=200.0))
        book.record_load(_load("A003", debt=50.0))
        book.complete("A003")
        assert book.total_loaded_gbp() == 300.0  # A003 excluded

    def test_loading_summary_keys(self):
        book = self._book()
        book.record_load(_load("A001"))
        book.record_load(_load("A002"))
        book.suspend("A002")
        summary = book.loading_summary()
        assert summary["total_accounts"] == 2
        assert summary["active_loads"] == 1
        assert summary["suspended"] == 1
        assert summary["completed"] == 0
        assert "non_compliant" in summary
        assert "smart_meter_consents_missing" in summary
        assert "total_loaded_gbp" in summary

    def test_empty_book_summary(self):
        book = self._book()
        s = book.loading_summary()
        assert s["total_accounts"] == 0
        assert s["total_loaded_gbp"] == 0.0
