"""Tests for company/billing/account_closure.py -- Phase 312."""
from __future__ import annotations

import datetime as dt

import pytest

from company.billing.account_closure import (
    AccountClosure,
    AccountClosureBook,
    ClosureReason,
    ClosureStatus,
)


def _book() -> AccountClosureBook:
    return AccountClosureBook()


def _initiate(book: AccountClosureBook, account_id: str = "A001",
              deposit: float = 150.0, debt: float = 0.0) -> AccountClosure:
    return book.initiate(
        account_id=account_id,
        supply_point_id="S001",
        reason=ClosureReason.CUSTOMER_SWITCH,
        closure_date=dt.date(2023, 1, 15),
        deposit_held_gbp=deposit,
        debt_balance_gbp=debt,
    )


class TestAccountClosure:
    def test_net_balance_no_bill(self):
        book = _book()
        r = _initiate(book, deposit=150.0, debt=50.0)
        # No final bill yet: net = 0 + 50 - 150 = -100
        assert r.net_balance_gbp == -100.0

    def test_net_balance_with_bill_positive(self):
        book = _book()
        _initiate(book, deposit=50.0, debt=0.0)
        r = book.issue_final_bill("A001", 200.0)
        # 200 + 0 - 50 = 150 (customer owes)
        assert r.net_balance_gbp == 150.0

    def test_net_balance_with_bill_negative(self):
        book = _book()
        _initiate(book, deposit=200.0, debt=0.0)
        r = book.issue_final_bill("A001", 50.0)
        # 50 + 0 - 200 = -150 (we owe customer)
        assert r.net_balance_gbp == -150.0

    def test_requires_debt_referral_true(self):
        book = _book()
        _initiate(book, deposit=50.0, debt=0.0)
        book.issue_final_bill("A001", 300.0)
        r = book.active_closures()[0]
        assert r.requires_debt_referral

    def test_requires_debt_referral_false_when_referred(self):
        book = _book()
        _initiate(book, deposit=50.0, debt=0.0)
        book.issue_final_bill("A001", 300.0)
        book.refer_to_debt_collection("A001")
        r = book._records["A001"]
        assert not r.requires_debt_referral

    def test_days_since_closure(self):
        book = _book()
        r = _initiate(book)
        assert r.days_since_closure(dt.date(2023, 2, 14)) == 30

    def test_is_final_bill_overdue_true(self):
        book = _book()
        r = _initiate(book)
        assert r.is_final_bill_overdue(dt.date(2023, 3, 15))  # 59 days

    def test_is_final_bill_overdue_false_within_deadline(self):
        book = _book()
        r = _initiate(book)
        assert not r.is_final_bill_overdue(dt.date(2023, 2, 1))  # 17 days

    def test_is_final_bill_overdue_false_when_billed(self):
        book = _book()
        _initiate(book)
        book.issue_final_bill("A001", 100.0)
        r = book._records["A001"]
        assert not r.is_final_bill_overdue(dt.date(2023, 4, 1))  # 75 days but bill exists


class TestAccountClosureBook:
    def test_initiate_status(self):
        book = _book()
        r = _initiate(book)
        assert r.status == ClosureStatus.INITIATED

    def test_receive_final_read_updates_kwh(self):
        book = _book()
        _initiate(book)
        r = book.receive_final_read("A001", 12345.0)
        assert r.final_read_kwh == 12345.0
        assert r.status == ClosureStatus.FINAL_READ_RECEIVED

    def test_issue_final_bill_updates_bill(self):
        book = _book()
        _initiate(book)
        r = book.issue_final_bill("A001", 280.0)
        assert r.final_bill_gbp == 280.0
        assert r.status == ClosureStatus.FINAL_BILL_ISSUED

    def test_return_deposit_status(self):
        book = _book()
        _initiate(book)
        r = book.return_deposit("A001")
        assert r.status == ClosureStatus.DEPOSIT_RETURNED

    def test_apply_deposit_to_debt_status(self):
        book = _book()
        _initiate(book, deposit=50.0, debt=0.0)
        book.issue_final_bill("A001", 300.0)
        r = book.apply_deposit_to_debt("A001")
        assert r.status == ClosureStatus.DEPOSIT_APPLIED

    def test_refer_to_debt_collection_status(self):
        book = _book()
        _initiate(book)
        book.issue_final_bill("A001", 300.0)
        r = book.refer_to_debt_collection("A001")
        assert r.status == ClosureStatus.DEBT_REFERRED

    def test_close_removes_from_active(self):
        book = _book()
        _initiate(book, account_id="A001")
        _initiate(book, account_id="A002")
        book.close("A001")
        active = book.active_closures()
        assert len(active) == 1
        assert active[0].account_id == "A002"

    def test_overdue_final_bills(self):
        book = _book()
        _initiate(book, account_id="A001")       # no bill, overdue
        _initiate(book, account_id="A002")
        book.issue_final_bill("A002", 100.0)     # billed, not overdue
        overdue = book.overdue_final_bills(dt.date(2023, 4, 1))  # 75 days
        assert len(overdue) == 1
        assert overdue[0].account_id == "A001"

    def test_deposits_to_return(self):
        book = _book()
        _initiate(book, account_id="A001", deposit=200.0, debt=0.0)
        _initiate(book, account_id="A002", deposit=50.0, debt=0.0)
        book.issue_final_bill("A001", 50.0)
        book.issue_final_bill("A002", 300.0)
        book.return_deposit("A001")
        book.refer_to_debt_collection("A002")
        assert len(book.deposits_to_return()) == 1

    def test_debt_referrals(self):
        book = _book()
        _initiate(book, account_id="A001")
        book.issue_final_bill("A001", 500.0)
        book.refer_to_debt_collection("A001")
        assert len(book.debt_referrals()) == 1

    def test_requiring_debt_referral(self):
        book = _book()
        _initiate(book, account_id="A001", deposit=50.0)
        _initiate(book, account_id="A002", deposit=200.0)
        book.issue_final_bill("A001", 300.0)  # net +250, needs referral
        book.issue_final_bill("A002", 100.0)  # net -100, return deposit
        assert len(book.requiring_debt_referral()) == 1

    def test_vacant_property_reason(self):
        book = AccountClosureBook()
        r = book.initiate("V001", "SP001", ClosureReason.VACANT_PROPERTY,
                           dt.date(2023, 1, 1), deposit_held_gbp=0.0)
        assert r.reason == ClosureReason.VACANT_PROPERTY

    def test_closure_summary_keys(self):
        book = _book()
        _initiate(book)
        summary = book.closure_summary()
        assert "total_closures" in summary
        assert "active" in summary
        assert "overdue_final_bills" in summary
        assert "deposits_to_return" in summary
        assert "debt_referrals" in summary
        assert "requiring_debt_referral" in summary
        assert "by_status" in summary

    def test_closure_summary_empty(self):
        book = _book()
        summary = book.closure_summary()
        assert summary["total_closures"] == 0
        assert summary["active"] == 0
