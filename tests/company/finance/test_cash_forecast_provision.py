"""The expected-loss provision from a forward cash forecast (`company/finance/cash_forecast_provision.py`).

Each test names the defect it fires on. The book is synthetic and small: a stayer who always pays, a
household that stops paying and stays, and a household that stops paying and leaves.
"""
from __future__ import annotations

import ast
import datetime as dt
import subprocess
import sys
from pathlib import Path

import pytest

from company.billing.account_ledger import LedgerBook, LedgerEvent, LedgerEventType
from company.finance import cash_forecast_provision as cfp

ROOT = Path(__file__).resolve().parents[3]
MODULE = ROOT / "company" / "finance" / "cash_forecast_provision.py"
TT = dt.datetime(2020, 1, 1)
START = dt.date(2018, 1, 10)


def _post_month(book, acct, k, bill, paid):
    day = START + dt.timedelta(days=30 * k)
    book.post(LedgerEvent(f"{acct}-b{k}", acct, LedgerEventType.BILL_DEBIT, bill, day, TT))
    if paid:
        book.post(LedgerEvent(f"{acct}-p{k}", acct, LedgerEventType.PAYMENT_CREDIT, paid,
                              day + dt.timedelta(days=5), TT))


def _book(n_payers=6, n_stoppers=3, n_leavers=3, months=36, stop_at=14, leave_at=18):
    """Payers pay every bill; stoppers stop paying at `stop_at` and keep being billed; leavers stop
    paying at `stop_at` and are not billed after `leave_at`."""
    book = LedgerBook()
    for i in range(n_payers):
        for k in range(months):
            _post_month(book, f"PAY{i}", k, 60.0, 60.0)
    for i in range(n_stoppers):
        for k in range(months):
            _post_month(book, f"STOP{i}", k, 60.0, 60.0 if k < stop_at else 0.0)
    for i in range(n_leavers):
        for k in range(leave_at):
            _post_month(book, f"LEAVE{i}", k, 60.0, 60.0 if k < stop_at else 0.0)
    return book


def _method(acct, on):
    return "direct_debit" if acct.startswith("PAY") else "standard_credit"


AS_OF = START + dt.timedelta(days=30 * 30)


def test_a_household_that_stopped_paying_is_provisioned_above_one_that_pays_defect_track_record_ignored():
    book = _book()
    prov = cfp.book_provision(book, as_of=AS_OF, payment_method_of=_method)
    by = {a.account_id: a for a in prov.accounts}
    payer, stopper = by["PAY0"], by["STOP0"]
    assert stopper.owed_gbp > 0 and stopper.missed_state == 3
    assert stopper.expected_loss_gbp > 0.5 * stopper.owed_gbp
    assert payer.expected_loss_gbp <= 0.01 * max(payer.owed_gbp, 1.0)


def test_the_chain_reaches_pay_miss_and_close_defect_a_branch_that_can_never_be_taken():
    """Partition control: every outcome a month can have is one the book can learn."""
    rr = cfp.learn(_book(), as_of=AS_OF, payment_method_of=_method)
    seen = {k for cell in rr.counts.values() for k, v in cell.items() if v > 0}
    assert seen == {"pay", "miss", "close"}
    assert rr.closed_accounts == 3


def test_a_closed_balance_is_provisioned_at_one_minus_the_learned_recovery_defect_recovery_dropped():
    book = _book()
    prov = cfp.book_provision(book, as_of=START + dt.timedelta(days=30 * 18 + 90),
                              payment_method_of=_method)
    leaver = {a.account_id: a for a in prov.accounts}["LEAVE0"]
    assert leaver.closed
    # No closed account has resolved its recovery window yet, so the published prior stands.
    assert leaver.expected_loss_gbp == pytest.approx(
        leaver.owed_gbp * (1 - cfp.PRIOR_POST_CLOSE_RECOVERY), abs=0.02)


def test_a_month_whose_payment_has_not_yet_arrived_is_not_learned_defect_look_ahead_as_a_miss():
    """A book of payers only, read the day after a bill and before its payment: the open month must
    not be learned (as a miss, or at all). Every read inside `learn` is windowed to dates the
    company has passed, so this guard is the look-ahead control; truncating the ledger at the
    forecast date as well changes nothing (an equivalence, measured 2026-10-11)."""
    book = _book(n_stoppers=0, n_leavers=0)
    as_of = START + dt.timedelta(days=30 * 35 + 1)
    rr = cfp.learn(book, as_of=as_of, payment_method_of=_method)
    assert rr.transitions > 0
    assert all(cell["miss"] == 0 and cell["close"] == 0 for cell in rr.counts.values())


def test_a_book_with_no_resolved_month_cannot_tell_defect_a_prior_dressed_as_an_answer():
    book = _book()
    prov = cfp.book_provision(book, as_of=START + dt.timedelta(days=20), payment_method_of=_method)
    assert prov.expected_loss_gbp is None and "cannot tell" in prov.reason


def test_the_book_provision_is_the_sum_of_its_accounts_defect_roll_up_drops_an_account():
    prov = cfp.book_provision(_book(), as_of=AS_OF, payment_method_of=_method)
    assert prov.expected_loss_gbp == pytest.approx(
        sum(a.expected_loss_gbp for a in prov.accounts), abs=0.01)
    assert prov.expected_loss_gbp > 0


def test_future_bills_are_not_provisioned_defect_next_years_billing_added_to_the_provision():
    """IFRS 9: the allowance is held against money owed today. A household owing nothing is
    provisioned at zero however risky its future."""
    as_of = START + dt.timedelta(days=30 * 29 + 6)  # the day after the payers' last payment
    prov = cfp.book_provision(_book(), as_of=as_of, payment_method_of=_method)
    assert any(a.owed_gbp == 0 for a in prov.accounts), "no account owes nothing: the branch is untested"
    for a in prov.accounts:
        assert a.expected_loss_gbp <= a.owed_gbp + 0.01
        if a.owed_gbp == 0:
            assert a.expected_loss_gbp == 0


_WORLD = ("sim", "simulation", "background", "tools")  # saas/ is the supplier side


def test_the_forecaster_imports_nothing_from_the_world_defect_wall_crossing():
    """Direct imports by AST, and the transitive closure by importing it in a clean interpreter."""
    tree = ast.parse(MODULE.read_text())
    names = [a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names]
    names += [n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module]
    assert names, "the census found no import at all, so it read nothing"
    assert not [n for n in names if n.split(".")[0] in _WORLD]
    out = subprocess.run(
        [sys.executable, "-c",
         "import sys; import company.finance.cash_forecast_provision; "
         f"print(sorted({{m.split('.')[0] for m in sys.modules}} & set({list(_WORLD)!r})))"],
        cwd=ROOT, capture_output=True, text=True, check=True)
    assert out.stdout.strip() == "[]", out.stdout
