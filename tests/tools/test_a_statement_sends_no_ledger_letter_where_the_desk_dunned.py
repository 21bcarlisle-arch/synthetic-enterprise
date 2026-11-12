"""A statement prints no per-bill ledger letter where the collections desk ran.

The defect: the billing ledger dated FIRST/SECOND_NOTICE per failed bill, whatever the account's
balance, and the statement printed them. SYN-2016-253 was GBP 155.55 in credit on 24 Jun 2024 and
its statement said "First overdue notice -- GBP52.89 outstanding" (42 such lines on level legs on
the 6fe7827ab2 book). One supplier has one dunning run per account, and in a run that carries the
desk, the desk's letters are the only ones sent (company_debt_management.md, "The statement's
notice lines yield too").
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.generate_payment_ledger_data import book_carries_the_desk, build_account_ledger

_JOURNEY = {"account_id": "ACC-SYN-1", "segment": "resi",
            "stages": [{"stage": "missed_payment", "on": "2020-02-15", "overdue_gbp": 40.0}]}


def _leg(journeys, *, dispute=False):
    stages = [{"stage": "DD_FAILED", "date": "2020-02-14", "note": "Direct debit returned"},
              {"stage": "FIRST_NOTICE", "date": "2020-02-21", "note": "First overdue notice -- GBP40.00"},
              {"stage": "SECOND_NOTICE", "date": "2020-03-13", "note": "Second notice"}]
    if dispute:
        stages.append({"stage": "DISPUTE_NOTICE", "date": "2020-02-28", "note": "Dispute notice"})
    return {"invoices": [{"invoice_number": 1, "issue_date": "2020-01-31", "total_amount_gbp": 40.0}],
            "payments": [{"invoice_number": 1, "payment_date": "2020-02-14", "amount_gbp": 40.0,
                          "method": "direct_debit", "outcome": "failed"}],
            "arrears_history": [{"invoice_number": 1, "arrears_gbp": 40.0,
                                 "opened_date": "2020-02-14", "stages": stages}],
            "collections_desk_journeys": journeys}


def _notices(cust, **kw):
    return [e["description"] for e in build_account_ledger(cust, "2025-01-01", **kw)["entries"]
            if e["type"] == "notice"]


def test_both_partitions_are_reachable():
    # A guard that dropped every letter would pass the tests below; this one says it keeps some.
    assert _notices(_leg([])) and not _notices(_leg([_JOURNEY]))


def test_a_leg_the_desk_dunned_prints_no_ledger_letter():
    assert _notices(_leg([_JOURNEY])) == []


def test_in_a_book_with_the_desk_an_account_it_never_opened_prints_none():
    # SYN-2016-310 at GBP 0.00 on 6 Aug 2017: the desk walked it and found nothing to chase.
    book = {"SYN-1": _leg([_JOURNEY]), "SYN-2": _leg([])}
    assert book_carries_the_desk(book)
    assert _notices(book["SYN-2"], desk_in_book=True) == []


def test_a_book_without_the_desk_keeps_the_ledgers_letters():
    book = {"SYN-1": _leg([]), "SYN-2": _leg([])}
    assert not book_carries_the_desk(book)
    assert len(_notices(book["SYN-2"], desk_in_book=book_carries_the_desk(book))) == 2


def test_the_ic_dispute_notice_is_no_desk_rung_and_stays():
    assert _notices(_leg([_JOURNEY], dispute=True)) == ["Dispute notice"]


def test_no_money_moves():
    before = [(e["date"], e["running_balance_gbp"]) for e in
              build_account_ledger(_leg([]), "2025-01-01")["entries"] if e["type"] != "notice"]
    after = [(e["date"], e["running_balance_gbp"]) for e in
             build_account_ledger(_leg([_JOURNEY]), "2025-01-01")["entries"] if e["type"] != "notice"]
    assert before == after
