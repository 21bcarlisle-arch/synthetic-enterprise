"""Tests for company/finance/debt_collection.py -- Phase 311."""
from __future__ import annotations

import datetime as dt

import pytest

from company.finance.debt_collection import (
    DebtCollectionBook,
    DebtRecord,
    DebtStage,
)


def _record(
    account_id: str = "A001",
    amount_gbp: float = 380.0,
    stage: DebtStage = DebtStage.INITIAL_REMINDER,
    stage_date: dt.date = dt.date(2022, 1, 1),
    initial_date: dt.date = dt.date(2022, 1, 1),
    is_vulnerable: bool = False,
) -> DebtRecord:
    return DebtRecord(
        account_id=account_id,
        amount_gbp=amount_gbp,
        stage=stage,
        stage_date=stage_date,
        initial_date=initial_date,
        is_vulnerable_customer=is_vulnerable,
    )


class TestDebtRecord:
    def test_initial_reminder_recovery_probability(self):
        r = _record(stage=DebtStage.INITIAL_REMINDER)
        assert r.recovery_probability == 0.95

    def test_warning_letter_recovery_probability(self):
        r = _record(stage=DebtStage.WARNING_LETTER)
        assert r.recovery_probability == 0.85

    def test_pre_legal_recovery_probability(self):
        r = _record(stage=DebtStage.PRE_LEGAL)
        assert r.recovery_probability == 0.70

    def test_debt_agency_recovery_probability(self):
        r = _record(stage=DebtStage.DEBT_AGENCY)
        assert r.recovery_probability == 0.65

    def test_legal_action_recovery_probability(self):
        r = _record(stage=DebtStage.LEGAL_ACTION)
        assert r.recovery_probability == 0.40

    def test_write_off_recovery_probability_zero(self):
        r = _record(stage=DebtStage.WRITE_OFF)
        assert r.recovery_probability == 0.0

    def test_expected_recovery_gbp(self):
        r = _record(amount_gbp=200.0, stage=DebtStage.PRE_LEGAL)
        assert r.expected_recovery_gbp == round(200.0 * 0.70, 2)

    def test_expected_recovery_write_off_is_zero(self):
        r = _record(amount_gbp=500.0, stage=DebtStage.WRITE_OFF)
        assert r.expected_recovery_gbp == 0.0

    def test_days_in_stage(self):
        r = _record(stage_date=dt.date(2022, 1, 1))
        assert r.days_in_stage(dt.date(2022, 1, 31)) == 30

    def test_is_statute_barred_false_within_6_years(self):
        r = _record(initial_date=dt.date(2020, 1, 1))
        assert not r.is_statute_barred(dt.date(2024, 1, 1))

    def test_is_statute_barred_true_after_6_years(self):
        r = _record(initial_date=dt.date(2015, 1, 1))
        assert r.is_statute_barred(dt.date(2022, 6, 1))


class TestDebtCollectionBook:
    def _book(self) -> DebtCollectionBook:
        return DebtCollectionBook()

    def test_record_debt_adds_entry(self):
        book = self._book()
        rec = book.record_debt(_record("A001"))
        assert rec.account_id == "A001"
        assert len(book.active_debts()) == 1

    def test_escalate_updates_stage(self):
        book = self._book()
        book.record_debt(_record("A001", stage=DebtStage.INITIAL_REMINDER, stage_date=dt.date(2022, 1, 1)))
        updated = book.escalate("A001", DebtStage.WARNING_LETTER, dt.date(2022, 1, 8))
        assert updated.stage == DebtStage.WARNING_LETTER
        assert updated.stage_date == dt.date(2022, 1, 8)

    def test_escalate_preserves_initial_date(self):
        book = self._book()
        initial = dt.date(2022, 1, 1)
        book.record_debt(_record("A001", initial_date=initial))
        updated = book.escalate("A001", DebtStage.PRE_LEGAL, dt.date(2022, 1, 29))
        assert updated.initial_date == initial

    def test_escalate_preserves_amount(self):
        book = self._book()
        book.record_debt(_record("A001", amount_gbp=450.0))
        updated = book.escalate("A001", DebtStage.DEBT_AGENCY, dt.date(2022, 2, 28))
        assert updated.amount_gbp == 450.0

    def test_write_off_sets_write_off_stage(self):
        book = self._book()
        book.record_debt(_record("A001"))
        result = book.write_off("A001", dt.date(2022, 6, 1))
        assert result.stage == DebtStage.WRITE_OFF

    def test_active_debts_excludes_written_off(self):
        book = self._book()
        book.record_debt(_record("A001"))
        book.record_debt(_record("A002"))
        book.write_off("A001", dt.date(2022, 6, 1))
        active = book.active_debts()
        assert len(active) == 1
        assert active[0].account_id == "A002"

    def test_debts_by_stage_filter(self):
        book = self._book()
        book.record_debt(_record("A001", stage=DebtStage.WARNING_LETTER))
        book.record_debt(_record("A002", stage=DebtStage.PRE_LEGAL))
        book.record_debt(_record("A003", stage=DebtStage.WARNING_LETTER))
        assert len(book.debts_by_stage(DebtStage.WARNING_LETTER)) == 2
        assert len(book.debts_by_stage(DebtStage.PRE_LEGAL)) == 1

    def test_total_outstanding_gbp_sums_active(self):
        book = self._book()
        book.record_debt(_record("A001", amount_gbp=200.0))
        book.record_debt(_record("A002", amount_gbp=350.0))
        book.record_debt(_record("A003", amount_gbp=100.0))
        book.write_off("A003", dt.date(2022, 6, 1))
        assert book.total_outstanding_gbp() == 550.0

    def test_expected_recovery_gbp_sum(self):
        book = self._book()
        book.record_debt(_record("A001", amount_gbp=200.0, stage=DebtStage.PRE_LEGAL))
        book.record_debt(_record("A002", amount_gbp=100.0, stage=DebtStage.DEBT_AGENCY))
        expected = round(200.0 * 0.70 + 100.0 * 0.65, 2)
        assert book.expected_recovery_gbp() == expected

    def test_vulnerable_accounts_filter(self):
        book = self._book()
        book.record_debt(_record("A001", is_vulnerable=True))
        book.record_debt(_record("A002", is_vulnerable=False))
        book.record_debt(_record("A003", is_vulnerable=True))
        assert len(book.vulnerable_accounts()) == 2

    def test_vulnerable_accounts_excludes_written_off(self):
        book = self._book()
        book.record_debt(_record("A001", is_vulnerable=True))
        book.write_off("A001", dt.date(2022, 6, 1))
        assert len(book.vulnerable_accounts()) == 0

    def test_statute_barred_check_returns_barred(self):
        book = self._book()
        book.record_debt(_record("A001", initial_date=dt.date(2015, 1, 1)))
        book.record_debt(_record("A002", initial_date=dt.date(2021, 1, 1)))
        barred = book.statute_barred_check(dt.date(2022, 6, 1))
        assert len(barred) == 1
        assert barred[0].account_id == "A001"

    def test_statute_barred_excludes_written_off(self):
        book = self._book()
        book.record_debt(_record("A001", initial_date=dt.date(2015, 1, 1)))
        book.write_off("A001", dt.date(2022, 1, 1))
        assert book.statute_barred_check(dt.date(2022, 6, 1)) == []

    def test_debt_summary_keys_and_counts(self):
        book = self._book()
        book.record_debt(_record("A001"))
        book.record_debt(_record("A002", is_vulnerable=True))
        book.record_debt(_record("A003"))
        book.write_off("A003", dt.date(2022, 6, 1))
        summary = book.debt_summary()
        assert summary["total_accounts"] == 3
        assert summary["active_accounts"] == 2
        assert summary["written_off"] == 1
        assert summary["vulnerable_accounts"] == 1
        assert "total_outstanding_gbp" in summary
        assert "expected_recovery_gbp" in summary
        assert "by_stage" in summary
        assert DebtStage.INITIAL_REMINDER.value in summary["by_stage"]

    def test_empty_book_summary(self):
        book = self._book()
        summary = book.debt_summary()
        assert summary["total_accounts"] == 0
        assert summary["total_outstanding_gbp"] == 0.0
        assert summary["expected_recovery_gbp"] == 0.0
