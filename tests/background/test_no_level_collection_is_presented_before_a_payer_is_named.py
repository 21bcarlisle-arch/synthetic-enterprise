"""A month whose bill names no payer presents no level collection (home_moves.md s.8.8g choice 31).

The defect this names: on the f2c6979d01 book, OCC-3c914ee8cef5g's January to March 2016 bills lie wholly
inside the unnamed-occupier window (occupier share 1.0), so `payer_ask_gbp` asks nobody for them. The world
still presented the GBP 39.55 level direct debit in each of those months. That gave a world ledger credit of
162.66 at the switch-away final bill, while the page held 44.01. The difference, 118.65, is 3 x 39.55. The
final bill took its whole 56.45 face from that credit, where the page collected 12.44. Book-wide, 137 legs
paid GBP 27,134.55 this way, and the page never counted it.

With no payer named there is no Direct Debit Instruction to collect under. The world was the side in the
wrong.
"""
from __future__ import annotations

from datetime import date

import pytest

import background.live_payment_triad as lpt
import simulation.household_budget as household_budget
from background.live_payment_triad import LivePaymentTriad
from simulation.arrears_engine import names_no_payer, payer_ask_gbp
from simulation.dd_review_in_loop import InLoopLevelCollection
from simulation.payment_behaviour_source import DIRECT_DEBIT

CID = "OCC-WINDOW-LEVEL"
LEVEL = 39.55
# (month, period_end, due, occupier share, face). The first two months are wholly the unnamed occupier's.
MONTHS = [
    ("2016-01", "2016-01-31", date(2016, 2, 14), 1.0, 5.47),
    ("2016-02", "2016-02-29", date(2016, 3, 14), 1.0, 59.33),
    ("2016-03", "2016-03-31", date(2016, 4, 14), 0.0, 55.35),
    ("2016-04", "2016-04-30", date(2016, 5, 14), 0.0, 46.82),
]


@pytest.fixture
def triad(monkeypatch):
    monkeypatch.setattr(household_budget, "BUDGET_DECIDES_PAYMENT", False)
    monkeypatch.setattr(lpt.early_contact, "EARLY_CONTACT_SHARE", 0.0)
    monkeypatch.setattr(lpt, "later_settlement_date", lambda event, segment="resi": None)
    real = lpt.generate_payment_event

    def collected(cid, period_index, due, amount, stress, method, **kw):
        ev = real(cid, period_index, due, amount, stress, method, **kw)
        return lpt.dataclasses.replace(ev, result="success", days_late=0,
                                       payment_date=due.isoformat(), dd_failure_reason=None)
    monkeypatch.setattr(lpt, "generate_payment_event", collected)
    t = LivePaymentTriad()
    t._method_for = lambda cid, fuel="electricity": DIRECT_DEBIT
    return t


def _bill(share, face, period_end):
    return {"customer_id": CID, "period_end": period_end, "total_amount_gbp": face,
            "occupier_share": share, "segment": "resi", "commodity": "electricity"}


def test_the_predicate_is_the_one_payer_ask_uses():
    for share in (0.0, 0.4, 1.0):
        bill = _bill(share, 50.0, "2016-05-31")
        assert names_no_payer(bill) is (payer_ask_gbp(bill) is None), share
    assert names_no_payer({"void_owner_share": 0.5, "occupier_share": 0.5})
    assert not names_no_payer(None)


def test_the_window_months_present_nothing_and_the_ledger_holds_only_named_cash(triad):
    loop = InLoopLevelCollection(board=None, customer_of=lambda _cid: None)
    presented = {}
    for month, period_end, due, share, face in MONTHS:
        bill = _bill(share, face, period_end)
        row = {"month": month, "scheduled_date": f"{month}-02", "collection_date": f"{month}-02",
               "amount_gbp": LEVEL}
        loop.collected.setdefault(CID, []).append(row)
        ask = payer_ask_gbp(bill)
        triad.record_period(
            customer_id=CID, due_date=due, bill_month=month, period_end=period_end,
            amount_gbp=max(0.0, ask or 0.0), income_stress_value="low", segment="resi",
            level_collection=row, names_a_payer=not names_no_payer(bill))
        presented[month] = triad.last_level_presented is row
        if not presented[month]:
            loop.withdraw(CID, row)
    # The partition: both branches taken, or a guard that refuses everything passes.
    assert presented == {"2016-01": False, "2016-02": False, "2016-03": True, "2016-04": True}
    assert [r["month"] for r in loop.collected[CID]] == ["2016-03", "2016-04"]
    # The unfixed writer collected 4 x 39.55 against 102.17 of named bills: -56.03, a credit the page never
    # holds. Fixed: 102.17 - 2 x 39.55 = 23.07 owed, which is what the page's walk reads.
    triad._deliver_settlements_through(date(2016, 12, 31))
    desk = round(triad._ledger_book.ledger(lpt.account_of(CID)).balance(), 2)
    page = round(sum(f for *_, s, f in MONTHS if s < 1.0) - LEVEL * len(loop.collected[CID]), 2)
    assert desk == page == pytest.approx(23.07), (desk, page)


def test_the_run_tells_the_triad_from_the_bill_before_the_gate():
    """The run's wiring sits inside the phase 2b closure, so it is read rather than run. The month's
    `record_period` must pass `names_a_payer`, from `names_no_payer` over the board's pre-gate bill.
    The book is the behavioural control: no level row in a no-payer month."""
    import ast
    import inspect

    import simulation.run_phase2b as rp
    tree = ast.parse(inspect.getsource(rp))
    post = next(n for n in ast.walk(tree)
                if isinstance(n, ast.FunctionDef) and n.name == "_post_month_bill")
    call = next(n for n in ast.walk(post) if isinstance(n, ast.Call)
                and getattr(n.func, "attr", "") == "record_period")
    kw = next((k for k in call.keywords if k.arg == "names_a_payer"), None)
    assert kw is not None, "the run's month is never told whether its bill names a payer"
    src = ast.unparse(kw.value)
    assert "names_no_payer" in src and "bill_for" in src, src
