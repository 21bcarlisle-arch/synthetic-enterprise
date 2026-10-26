"""The overlay's arrears term, read off the company's own book (`company/finance/bad_debt_provision.
arrears_overlay_share`; bad_debt_provisioning.md, "The arrears-per-account signal", 2026-10-24).

The book below has one account whose arrears over 91 days grow 5% a year, then 30% in 2023: a
pre-crisis baseline of 5%, a calm 2020-22 and a 2023 intensity step past the published high.

Each test names the defect it fires on.
"""
from __future__ import annotations

import ast
import datetime as dt
import inspect

import pytest

from company.billing.account_ledger import LedgerBook, LedgerEvent, LedgerEventType
from company.billing.payment_observation_consumer import PaymentObservationConsumer
from company.finance import bad_debt_provision as bdp
from company.policy.decision_policy import CURRENT_POLICY

TT = dt.datetime(2026, 1, 1)
GROWTH = {2017: 0.05, 2018: 0.05, 2019: 0.05, 2020: 0.05, 2021: 0.05, 2022: 0.05, 2023: 0.30, 2024: 0.05}


def _book(first_year: int = 2016) -> LedgerBook:
    """Unpaid bills on 1 June each year, sized so the year-end arrears follow GROWTH from GBP 1,000."""
    book, level = LedgerBook(), 1000.0
    for year in range(first_year, 2025):
        nxt = level if year == first_year else level * (1 + GROWTH[year])
        amount = nxt if year == first_year else nxt - level
        book.post(LedgerEvent(f"A-{year}", "A", LedgerEventType.BILL_DEBIT, round(amount, 2),
                              dt.date(year, 6, 1), TT))
        level = nxt
    return book


def _shares(book):
    memo = {}
    return {y: bdp.arrears_overlay_share(book, dt.date(y, 12, 31), memo) for y in range(2017, 2025)}


def test_the_term_fires_on_the_2023_step_is_zero_when_calm_and_unread_before_its_baseline():
    """Defect: a term that never fires, or one that is always on. One control over the partition:
    the step year carries the published high, a year at baseline growth carries nothing, and a date
    before the baseline is complete carries None with a reason, never zero."""
    by_year = _shares(_book())
    high = dict(bdp.OVERLAY_SHARE_ENDS)["published_high"]
    fired = {y for y, r in by_year.items() if r["share"]}
    calm = {y for y, r in by_year.items() if r["share"] == 0}
    unread = {y for y, r in by_year.items() if r["share"] is None and r["reason"]}
    assert fired and calm and unread, by_year
    assert by_year[2023]["share"] == pytest.approx(high)
    assert by_year[2023]["growth"] == pytest.approx(0.30, abs=1e-3)
    assert by_year[2023]["baseline_growth"] == pytest.approx(0.05, abs=1e-3)
    assert {2020, 2021, 2022} <= calm, by_year
    assert unread == {2017, 2018}, by_year
    assert by_year[2024]["share"] == 0  # back at baseline: the term releases on its own signal


def test_a_book_younger_than_three_years_has_no_baseline_and_says_so():
    """Defect: a young book read as calm (K2: zero asserted where nothing is known)."""
    r = bdp.arrears_overlay_share(_book(first_year=2018), dt.date(2023, 12, 31))
    assert r["share"] is None and "younger than three years" in r["reason"], r


def test_the_two_terms_are_taken_as_the_larger_never_the_sum():
    """Defect: one shock counted twice. At end-2022 the cap term is the published high, so an
    arrears share under it must leave the total share at the cap's; at end-2023 the cap term is zero
    and the arrears term drives."""
    stock = {"provision_gbp": 100.0}
    small = {"share": 0.05, "reason": None}
    y22 = bdp.with_crisis_overlay(stock, dt.date(2022, 12, 31), small)["crisis_overlay"]
    assert y22["share"] == pytest.approx(y22["cap_share"]) and y22["driver"] == "cap", y22
    big = {"share": 0.134, "reason": None}
    y23 = bdp.with_crisis_overlay(stock, dt.date(2023, 12, 31), big)["crisis_overlay"]
    assert y23["cap_share"] == 0 and y23["share"] == pytest.approx(0.134) and y23["driver"] == "arrears"
    both = bdp.with_crisis_overlay(stock, dt.date(2021, 12, 31), big)["crisis_overlay"]
    assert 0 < both["cap_share"] < 0.134 and both["share"] == pytest.approx(0.134), both
    unread = bdp.with_crisis_overlay(stock, dt.date(2022, 12, 31), {"share": None, "reason": "x"})
    assert unread["crisis_overlay"]["driver"] == "cap"


def test_the_reading_on_a_date_ignores_every_later_bill():
    """Defect: look-ahead. A bill valued after the date may not move the date's arrears."""
    book = _book()
    before = bdp.arrears_overlay_share(book, dt.date(2023, 12, 31))
    book.post(LedgerEvent("A-late", "A", LedgerEventType.BILL_DEBIT, 5000.0, dt.date(2024, 1, 2), TT))
    assert bdp.arrears_overlay_share(book, dt.date(2023, 12, 31)) == before


def test_the_switch_publishes_the_series_beside_the_overlay_and_leaves_the_matrix():
    """Defect: a switch that does nothing when on, or that moves the matrix stock it grosses."""
    consumer = PaymentObservationConsumer(ledger_book=_book())
    on, method = dt.date(2023, 12, 31), (lambda a, d: "direct_debit")
    off = consumer.provision_stock(on, payment_method_of=method)
    lit = consumer.provision_stock(on, payment_method_of=method, arrears_overlay=True)
    assert "crisis_overlay" not in off
    overlay = lit["crisis_overlay"]
    assert overlay["arrears"]["indebted_accounts"] == 1 and overlay["arrears"]["per_account_gbp"] > 0
    assert overlay["driver"] == "arrears" and lit["matrix_provision_gbp"] == off["provision_gbp"]


def test_the_policy_switch_is_off_by_default_and_reaches_the_runs_read():
    """Defect: a switch the run never passes, so turning it on changes nothing that is published.
    Off since the 2026-10-26 second seed failed leg (c) of the switch-on rule in the crisis finding."""
    assert CURRENT_POLICY.provision_arrears_overlay is False
    import simulation.run_phase2b as rp
    tree = ast.parse(inspect.getsource(rp))
    calls = [c for c in ast.walk(tree) if isinstance(c, ast.Call)
             and getattr(c.func, "id", None) == "_company_provision_by_year_end"]
    assert calls and all(any(k.arg == "arrears_overlay" and ast.unparse(k.value)
                             == "policy.provision_arrears_overlay" for k in c.keywords)
                         for c in calls)


def test_a_bill_younger_than_91_days_is_not_arrears():
    """Defect: the receivable read as arrears. Ofgem's arrears are owed more than 91 days; a bill
    sent last month is not yet behind."""
    book = LedgerBook()
    book.post(LedgerEvent("B-old", "B", LedgerEventType.BILL_DEBIT, 200.0, dt.date(2023, 6, 1), TT))
    book.post(LedgerEvent("B-new", "B", LedgerEventType.BILL_DEBIT, 300.0, dt.date(2023, 12, 1), TT))
    assert bdp.arrears_per_indebted_account(book, dt.date(2023, 12, 31)) == (200.0, 1)
