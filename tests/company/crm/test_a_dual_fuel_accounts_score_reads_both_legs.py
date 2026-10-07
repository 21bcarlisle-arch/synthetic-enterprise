"""A decision about a dual-fuel account reads the payment record of BOTH its legs.

The defect (2026-10-07, `SEAT_RESULT_THE_CHOSEN_BOOKS_EXCESS_BAD_DEBT_IS_TWO_ZERO_WEIGHT_ACCOUNTS...`
§3): a household's departure is rolled on one leg, and the company's beliefs at that roll read that
leg's score alone. PROS-2020-0002's gas leg was CRITICAL and the belief saw its electricity leg's
FAIR. Each test names the defect it catches.
"""
from __future__ import annotations

import ast
import pathlib
from datetime import date

import simulation.run_phase2b as _run
from company.crm.customer_experience_desk import CustomerExperienceDesk, PaymentOutcome
from company.crm.payment_behaviour_analytics import (
    BehaviourScore,
    PaymentBehaviourAnalytics,
    score_payment_history,
)

_RUN = pathlib.Path(_run.__file__)


def _book(**legs: list[str]) -> PaymentBehaviourAnalytics:
    book = PaymentBehaviourAnalytics()
    for leg, results in legs.items():
        for month, result in enumerate(results, start=1):
            book.record_payment(leg, {"customer_id": leg, "due_date": date(2020, month, 28),
                                      "result": result, "days_late": 0, "amount_gbp": 50.0})
    return book


_CLEAN = ["ON_TIME"] * 12
_DEBTOR = ["DD_FAILED"] * 4 + ["LATE"] * 4 + ["ON_TIME"] * 4


def test_a_planted_critical_gas_leg_moves_the_account_score_off_the_clean_electricity_one():
    """Catches: the account score reading only the decision leg."""
    book = _book(C1=_CLEAN, C1g=_DEBTOR)
    assert book.get_score("C1") is BehaviourScore.EXCELLENT
    assert book.get_score("C1g") is BehaviourScore.CRITICAL
    assert book.get_account_score(("C1", "C1g")) is score_payment_history(
        book._records["C1"] + book._records["C1g"])
    assert book.get_account_score(("C1", "C1g")) is not BehaviourScore.EXCELLENT


def test_a_single_leg_account_reads_exactly_its_legs_score():
    """Catches: pooling that changes the answer where there is nothing to pool (the null arm)."""
    for results in (_CLEAN, _DEBTOR, ["LATE"] * 3 + ["ON_TIME"] * 9):
        book = _book(C5=results)
        assert book.get_account_score(("C5",)) is book.get_score("C5")


def test_the_partition_both_moves_and_holds():
    """Catches: an account score that ALWAYS differs from the leg (e.g. worst-of-unknown) or NEVER
    does (the one-leg read restored). Both branches must be reachable on one predicate."""
    moved = _book(C1=_CLEAN, C1g=_DEBTOR)
    held = _book(C1=_CLEAN, C1g=_CLEAN)
    outcomes = {
        m.get_account_score(("C1", "C1g")) != m.get_score("C1") for m in (moved, held)
    }
    assert outcomes == {True, False}


def test_no_history_on_any_leg_is_none_and_a_missing_leg_is_skipped():
    """Catches: an absent record read as a clean one, and a leg with no bills yet poisoning the
    read with a KeyError."""
    book = _book(C1g=_DEBTOR)
    assert book.get_account_score(("C9", "C9g")) is None
    assert book.get_account_score(("C1", "C1g")) is BehaviourScore.CRITICAL


def test_the_desk_exposes_the_account_read():
    """Catches: the desk method not reaching the analytics it wraps."""
    desk = CustomerExperienceDesk()
    for month, result in enumerate(_DEBTOR, start=1):
        desk.observe_payment(PaymentOutcome(customer_id="C1g", due_date=date(2020, month, 28),
                                            result=result, days_late=0, amount_gbp=50.0))
    for month in range(1, 13):
        desk.observe_payment(PaymentOutcome(customer_id="C1", due_date=date(2020, month, 28),
                                            result="ON_TIME", days_late=0, amount_gbp=50.0))
    assert desk.payment_behaviour_score("C1") is BehaviourScore.EXCELLENT
    assert desk.account_payment_behaviour_score(("C1", "C1g")) is not BehaviourScore.EXCELLENT


def test_the_run_reads_the_account_score_at_its_decision_leg_sites():
    """Catches: the run going back to a one-leg read. Asked of the AST, so a comment naming the
    old call cannot satisfy or red it."""
    tree = ast.parse(_RUN.read_bytes())
    called = [n.func.attr for n in ast.walk(tree)
              if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
              and isinstance(n.func.value, ast.Name) and n.func.value.id == "_cx_desk"]
    assert called.count("account_payment_behaviour_score") >= 2
    assert "payment_behaviour_score" not in called
