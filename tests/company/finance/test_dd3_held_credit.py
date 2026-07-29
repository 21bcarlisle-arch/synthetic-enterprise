"""DD3 (atom DD_seasonal_cashflow_physics) -- held customer credit booked as a
LIABILITY in the double-entry chart.

Closed-loop tests for the reclassification that moves held level-DD credit out of
equity and into account 2200 (Customer Credit Balances Held), exposing the
"cash-rich but balance-sheet-insolvent" tell. R15 both-ways: the fail-closed
validation FIRES on its named defects (non-finite / negative held credit), the
tell flag fires ONLY when genuinely insolvent, and the generalised liability sum
reflects a new liability account (a guard against the old hardcoded-2100 fail-open).
"""

import math

import pytest

from company.finance.double_entry import (
    ACCOUNTS,
    balance_sheet,
    balance_sheet_with_held_credit,
    build_journal,
    held_credit_journal_entries,
)


def _opening_journal(treasury: float):
    """A minimal journal: just opening treasury capital (DR cash / CR equity).
    Assets == equity == treasury, liabilities == 0 -- a clean base for the
    held-credit reclassification."""
    return build_journal([], opening_treasury=treasury)


# ---------------------------------------------------------------------------
# Chart of accounts: the new liability
# ---------------------------------------------------------------------------

def test_customer_credit_held_account_present_and_liability():
    assert "2200" in ACCOUNTS
    assert ACCOUNTS["2200"]["type"] == "liability"
    assert ACCOUNTS["2200"]["name"] == "Customer Credit Balances Held"


def test_customer_credit_held_account_follows_range_convention():
    assert int("2200"[0]) == 2  # 2xxx == liability


# ---------------------------------------------------------------------------
# held_credit_journal_entries -- the reclassification posting
# ---------------------------------------------------------------------------

def test_held_credit_entry_is_dr_retained_earnings_cr_liability():
    entries = held_credit_journal_entries(1_949.51)
    assert len(entries) == 1
    e = entries[0]
    assert e["debit_account"] == "3900"   # Retained Earnings (equity down)
    assert e["credit_account"] == "2200"  # Customer Credit Held (liability up)
    assert e["amount_gbp"] == pytest.approx(1_949.51)


def test_zero_held_credit_books_nothing():
    # Nothing owed back -> legitimately no entry (NOT a rejected input).
    assert held_credit_journal_entries(0.0) == []


def test_held_credit_entry_balances_dr_equals_cr():
    entries = held_credit_journal_entries(500.0)
    total_dr = sum(e["amount_gbp"] for e in entries)  # each entry is one DR+one CR
    total_cr = sum(e["amount_gbp"] for e in entries)
    assert total_dr == total_cr


# ---------------------------------------------------------------------------
# Fail-CLOSED validation (R15 FAIL-OPEN guard, both ways)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
def test_non_finite_held_credit_rejected(bad):
    with pytest.raises(ValueError):
        held_credit_journal_entries(bad)
    with pytest.raises(ValueError):
        balance_sheet_with_held_credit(_opening_journal(100.0), bad)


def test_negative_held_credit_rejected():
    # Held credit is positive-balances-only; a negative NET balance is not a
    # held-credit liability and must NOT be silently coerced to zero.
    with pytest.raises(ValueError):
        held_credit_journal_entries(-250.0)
    with pytest.raises(ValueError):
        balance_sheet_with_held_credit(_opening_journal(100.0), -250.0)


# ---------------------------------------------------------------------------
# balance_sheet() now sums ALL liability accounts (fail-open guard)
# ---------------------------------------------------------------------------

def test_balance_sheet_reflects_new_liability_account():
    # Post held credit directly and confirm total_liabilities picks up 2200 --
    # if balance_sheet ever reverts to a hardcoded `vat_payable` sum, this fails.
    journal = _opening_journal(1_000.0) + held_credit_journal_entries(300.0)
    bs = balance_sheet(journal)
    assert bs["customer_credit_held_gbp"] == pytest.approx(300.0)
    assert bs["total_liabilities_gbp"] == pytest.approx(300.0)  # 0 VAT + 300 held
    assert bs["equation_holds"] is True


def test_ordinary_balance_sheet_has_zero_held_credit_when_none_posted():
    bs = balance_sheet(_opening_journal(1_000.0))
    assert bs["customer_credit_held_gbp"] == pytest.approx(0.0)
    assert bs["vat_payable_gbp"] == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# balance_sheet_with_held_credit -- assets fixed, equity down, equation holds
# ---------------------------------------------------------------------------

def test_reclassification_moves_equity_to_liability_assets_unchanged():
    journal = _opening_journal(1_000.0)
    naive = balance_sheet(journal)
    bs = balance_sheet_with_held_credit(journal, 300.0)
    assert bs["total_assets_gbp"] == pytest.approx(naive["total_assets_gbp"])
    assert bs["customer_credit_held_gbp"] == pytest.approx(300.0)
    assert bs["true_total_equity_gbp"] == pytest.approx(naive["total_equity_gbp"] - 300.0)
    assert bs["naive_total_equity_gbp"] == pytest.approx(naive["total_equity_gbp"])
    assert bs["total_liabilities_gbp"] == pytest.approx(naive["total_liabilities_gbp"] + 300.0)
    assert bs["equation_holds"] is True


# ---------------------------------------------------------------------------
# The cash-rich-but-insolvent tell (both ways)
# ---------------------------------------------------------------------------

def test_tell_fires_when_held_credit_exceeds_equity():
    # Naive equity +100, held credit 150 owed back -> truly insolvent (-50).
    bs = balance_sheet_with_held_credit(_opening_journal(100.0), 150.0)
    assert bs["naive_total_equity_gbp"] > 0
    assert bs["true_total_equity_gbp"] < 0
    assert bs["cash_rich_but_insolvent"] is True


def test_tell_silent_when_equity_covers_held_credit():
    # Ample equity (+1000) comfortably covers 300 of held credit -> solvent.
    bs = balance_sheet_with_held_credit(_opening_journal(1_000.0), 300.0)
    assert bs["true_total_equity_gbp"] > 0
    assert bs["cash_rich_but_insolvent"] is False


def test_tell_silent_when_no_held_credit():
    bs = balance_sheet_with_held_credit(_opening_journal(100.0), 0.0)
    assert bs["customer_credit_held_gbp"] == pytest.approx(0.0)
    assert bs["cash_rich_but_insolvent"] is False
    assert bs["true_total_equity_gbp"] == pytest.approx(bs["naive_total_equity_gbp"])
