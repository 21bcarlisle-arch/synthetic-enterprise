"""The level schedule the page reads holds only the collections the world presented.

The defect this names: on the 4dee9854a4 book C7 (single-fuel electricity, level GBP 108) churned on
1 Jul 2019. Phase 2b asked the in-loop schedule for June, which recorded GBP 108 on 12 Jun. The triad
was then told the month had left, so it presented the June bill's face, GBP 89.88, on its 15 Jul due
date. The page and `closing_balances` read the schedule (48.55 owed). The desk's ledger read what
was presented (66.67 owed), and the desk wrote off 66.67. 108 - 89.88 = 18.12. A replay of C7 alone
through the triad reproduces the run's 66.67 to the penny (finding:
`docs/staging/WORKER_FINDING_A_LEVEL_DD_JOURNEY_CURES_ON_THE_NEXT_INSTALMENT_WHILE_THE_MISSED_ONE_IS_NEVER_MADE_GOOD_2026-11-09.md`).

The triad settles a month on the bill's face for a churned leg's final month, a mover's final month,
and a stopped or cancelled mandate. In each of those cases the schedule must give the row back.

Not reached here: run_phase2b's wiring of `withdraw` sits inside the run's closure. The control for
that wiring is the next book (C7 closes on 66.67 on the page and on the desk).
"""
from __future__ import annotations

from datetime import date

import pytest

import background.live_payment_triad as lpt
import simulation.household_budget as household_budget
from background.live_payment_triad import LivePaymentTriad
from simulation.dd_review_in_loop import InLoopLevelCollection
from simulation.payment_behaviour_source import DIRECT_DEBIT

CID = "LEVEL-STOPPED-LAST"
# A GBP 108 level leg whose last month is settled on its face: the mandate is stopped by then.
MONTHS = [
    ("2019-03", "2019-03-31", date(2019, 4, 14), 161.93),
    ("2019-04", "2019-04-30", date(2019, 5, 14), 151.15),
    ("2019-05", "2019-05-31", date(2019, 6, 14), 120.63),
    ("2019-06", "2019-06-30", date(2019, 7, 15), 89.88),
]
STOPPED_FROM = date(2019, 7, 1)


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


def _post(triad, loop):
    presented = {}
    for month, period_end, due, bill in MONTHS:
        row = {"month": month, "scheduled_date": f"{month}-12", "collection_date": f"{month}-12",
               "amount_gbp": 108.0}
        loop.collected.setdefault(CID, []).append(row)
        triad.record_period(
            customer_id=CID, due_date=due, bill_month=month, period_end=period_end,
            amount_gbp=bill, income_stress_value="low", segment="resi", level_collection=row,
            dd_stopped_by=lambda _cid, d: d >= STOPPED_FROM)
        presented[month] = triad.last_level_presented is row
        if not presented[month]:
            loop.withdraw(CID, row)
    return presented


def test_a_month_settled_on_its_face_leaves_the_schedule_and_the_page_meets_the_desk(triad):
    loop = InLoopLevelCollection(board=None, customer_of=lambda _cid: None)
    presented = _post(triad, loop)
    # The partition: the branch is taken both ways, or the control proves nothing.
    assert presented == {"2019-03": True, "2019-04": True, "2019-05": True, "2019-06": False}
    assert [r["month"] for r in loop.collected[CID]] == ["2019-03", "2019-04", "2019-05"]

    # The page's walk: every bill, less the schedule's collections, less the faces paid off it.
    faces_paid = sum(bill for month, _, _, bill in MONTHS if not presented[month])
    page = round(sum(b for *_, b in MONTHS) - sum(r["amount_gbp"] for r in loop.collected[CID])
                 - faces_paid, 2)
    triad._deliver_settlements_through(date(2019, 12, 31))
    desk = round(triad._ledger_book.ledger(lpt.account_of(CID)).balance(), 2)
    assert page == desk == pytest.approx(109.71), (page, desk)


def test_withdraw_takes_back_that_row_and_no_other():
    loop = InLoopLevelCollection(board=None, customer_of=lambda _cid: None)
    a = {"month": "2019-05", "amount_gbp": 108.0}
    b = {"month": "2019-06", "amount_gbp": 108.0}
    twin = dict(b)
    loop.collected[CID] = [a, twin, b]
    loop.withdraw(CID, b)
    assert loop.collected[CID] == [a, twin] and loop.collected[CID][1] is twin
