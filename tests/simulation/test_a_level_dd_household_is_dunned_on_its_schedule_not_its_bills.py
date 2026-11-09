"""A level direct debit household is dunned on what it missed of its schedule, not on its bills.

The defect this names (`docs/staging/SEAT_FINDING_A_LEVEL_DIRECT_DEBIT_HOUSEHOLD_IS_DUNNED_PER_BILL_
SO_ITS_PAGE_PRINTS_OVERDUE_WHILE_IN_CREDIT_2026-11-07.md`): on the af31e73fa7 book OCC-226d3bc42b37's
February 2025 electricity bill (GBP 109.73) was drawn "failed" on its due date, 15 Mar 2025, though
the household's bank had paid the level GBP 104.42 on 10 Mar and the account was in credit. The
desk opened a journey on 16 Mar printing GBP 109.73 overdue, and offered a GBP 345.38 arrangement
on 12 Apr (INV_OVERDUE_WITHIN_PAGE_BALANCE, 1,729 steps on that book).

Under a level DD the household owes the scheduled collection. Ofgem counts a DD customer in debt
only "by defaulting on one or more payments", not one "with a debit at the end of a payment scheme"
(letter of 20 Sep 2011, App. 2 para 2.8; payments_and_direct_debit_2026-10-25.md, "What is owed").
So the world presents the level collection (its amount, on its day), a return is that amount, and
the desk opens only on a return, figuring `max(0, min(requested - received, debit balance))`.
"""
from __future__ import annotations

from datetime import date, timedelta

import pytest

import background.live_payment_triad as lpt
import simulation.household_budget as household_budget
from background.live_payment_triad import LivePaymentTriad
from simulation.payment_behaviour_source import DIRECT_DEBIT

H = "OCC-226d3bc42b37"

# The household's electricity leg on af31e73fa7: each month's printed bill, due date, and the level
# collection the run's schedule took (`level_dd_collections`), 10th of the month at GBP 104.42.
AF31_ELEC = [
    ("2024-10", "2024-10-31", date(2024, 11, 14), 16.65),
    ("2024-11", "2024-11-30", date(2024, 12, 14), 120.55),
    ("2024-12", "2024-12-31", date(2025, 1, 14), 124.10),
    ("2025-01", "2025-01-31", date(2025, 2, 14), 131.77),
    ("2025-02", "2025-02-28", date(2025, 3, 15), 109.73),
    ("2025-03", "2025-03-31", date(2025, 4, 14), 114.18),
]


@pytest.fixture
def triad(monkeypatch):
    monkeypatch.setattr(household_budget, "BUDGET_DECIDES_PAYMENT", False)
    monkeypatch.setattr(lpt.early_contact, "EARLY_CONTACT_SHARE", 0.0)
    monkeypatch.setattr(lpt, "later_settlement_date", lambda event, segment="resi": None)
    t = LivePaymentTriad()
    t._method_for = lambda cid, fuel="electricity": DIRECT_DEBIT
    return t


def _fail_months(monkeypatch, months):
    """The period's one outcome draw, forced: failed for `months`, collected for the rest."""
    real = lpt.generate_payment_event
    failed = {lpt._period_index_for(m) for m in months}

    def draw(cid, period_index, due, amount, stress, method, **kw):
        ev = real(cid, period_index, due, amount, stress, method, **kw)
        if period_index in failed:
            return lpt.dataclasses.replace(ev, result="failed", days_late=0, payment_date=None,
                                           dd_failure_reason=lpt.INSUFFICIENT_FUNDS)
        return lpt.dataclasses.replace(ev, result="success", days_late=0,
                                       payment_date=due.isoformat(), dd_failure_reason=None)
    monkeypatch.setattr(lpt, "generate_payment_event", draw)


def _replay(triad, cid, months, level_of):
    for month, period_end, due, bill in months:
        level = level_of(month)
        triad.record_period(
            customer_id=cid, due_date=due, bill_month=month, period_end=period_end,
            amount_gbp=bill, income_stress_value="low", segment="resi",
            level_collection=None if level is None else {
                "month": month, "collection_date": level[0], "amount_gbp": level[1]})
    return triad.collections_journeys(date(2025, 6, 30))


def _stages(journeys):
    return [s for j in journeys for s in j["stages"]]


def test_af31_occ_226d3bc42b37_is_not_dunned_while_in_credit(triad, monkeypatch):
    """The named household: the month it missed is February's level collection, returned on 10 Feb,
    and on every day since it is in credit, so no journey opens and nothing is printed overdue."""
    _fail_months(monkeypatch, ["2025-02"])
    journeys = _replay(triad, H, AF31_ELEC, lambda m: (f"{m}-10", 104.42))
    ledger = triad._ledger_book.ledger(lpt.account_of(H))
    for s in _stages(journeys):
        on = date.fromisoformat(s["on"])
        assert (s["overdue_gbp"] or 0.0) <= max(ledger.balance(on), 0.0) + 0.005, (s, ledger.balance(on))
    assert journeys == [], journeys
    # The collection presented was the level amount, so the return was GBP 104.42, not the bill.
    failed = [f for f in triad._consumer._dd_failures.get(lpt.account_of(H), [])]
    assert [(f.value_date, f.amount_gbp) for f in failed] == [(date(2025, 2, 10), 104.42)]


# A winter-heavy leg on a GBP 60 level amount: by February it is in seasonal debit.
SEASONAL = [
    ("2024-10", "2024-10-31", date(2024, 11, 14), 70.00),
    ("2024-11", "2024-11-30", date(2024, 12, 14), 110.00),
    ("2024-12", "2024-12-31", date(2025, 1, 14), 140.00),
    ("2025-01", "2025-01-31", date(2025, 2, 14), 150.00),
    ("2025-02", "2025-02-28", date(2025, 3, 15), 120.00),
    ("2025-03", "2025-03-31", date(2025, 4, 14), 90.00),
]


def test_a_seasonal_debit_with_every_collection_taken_opens_nothing(triad, monkeypatch):
    _fail_months(monkeypatch, [])
    journeys = _replay(triad, "SEAS-ALL-PAID", SEASONAL, lambda m: (f"{m}-05", 60.00))
    ledger = triad._ledger_book.ledger(lpt.account_of("SEAS-ALL-PAID"))
    assert ledger.balance(date(2025, 3, 16)) > 100.0  # in debit: the control can fail
    assert journeys == [], journeys


def test_a_returned_collection_opens_on_the_shortfall_not_the_balance(triad, monkeypatch):
    """The branch the level desk exists to take: a return in seasonal debit opens a journey the day
    after it, at the collection missed (GBP 60), not the debit balance or a bill's face."""
    _fail_months(monkeypatch, ["2025-01"])
    journeys = _replay(triad, "SEAS-RETURN", SEASONAL, lambda m: (f"{m}-05", 60.00))
    assert journeys, "a returned level collection must be able to open a journey"
    first = journeys[0]["stages"][0]
    assert first["stage"] == "missed_payment"
    assert first["on"] == "2025-01-06"
    assert first["overdue_gbp"] == pytest.approx(60.00)
    ledger = triad._ledger_book.ledger(lpt.account_of("SEAS-RETURN"))
    assert ledger.balance(date(2025, 1, 6)) > 60.0


def test_a_repaid_return_cures_though_the_seasonal_debit_stays(triad, monkeypatch):
    """Repaying the missed collection meets the schedule, so the journey cures, though bills the
    level amount has not yet covered are still unpaid past their due dates."""
    _fail_months(monkeypatch, ["2025-01"])
    monkeypatch.setattr(lpt, "later_settlement_date", lambda event, segment="resi": (
        date.fromisoformat(event.due_date) + timedelta(days=20) if event.result == "failed" else None))
    journeys = _replay(triad, "SEAS-REPAID", SEASONAL, lambda m: (f"{m}-05", 60.00))
    assert [j["exit"] for j in journeys] == ["cured"], journeys
    cured_on = date.fromisoformat(journeys[0]["stages"][-1]["on"])
    assert cured_on == date(2025, 1, 25)
    # Still GBP 80 in seasonal debit, with the December bill (GBP 140, due 14 Jan) unpaid.
    assert triad._ledger_book.ledger(lpt.account_of("SEAS-REPAID")).balance(cured_on) == 80.0


def test_no_level_collection_lands_on_a_day_the_desk_has_walked(triad, monkeypatch):
    """A dual-fuel level household: each leg's collection for month m is dated inside m, before
    m's bill falls due. Walked to the other leg's last due date, the desk passed the gas
    collection's day before it posted, and the late cash cleared a debt it had already dunned
    (SYN-2016-452, reminder on 30 Jan 2017 at GBP -7.30). The walk stops at the end of the last month
    every level leg has presented."""
    _fail_months(monkeypatch, [])
    acct = lpt.account_of("DUAL")
    assert lpt.account_of("DUALg") == acct
    desk = triad._consumer.collections_journeys
    walked = []
    for (month, period_end, due, bill) in SEASONAL:
        for leg, day, level in (("DUAL", "25", 60.00), ("DUALg", "03", 90.00)):
            through = desk._through.get(acct)
            walked.append(through)
            collected = date.fromisoformat(f"{month}-{day}")
            assert through is None or collected > through, (leg, month, through)
            triad.record_period(
                customer_id=leg, due_date=due, bill_month=month, period_end=period_end,
                amount_gbp=bill, income_stress_value="low", segment="resi",
                fuel="gas" if leg.endswith("g") else "electricity",
                level_collection={"month": month, "collection_date": collected.isoformat(),
                                  "amount_gbp": level})
    assert any(w is not None for w in walked), "the desk never walked, so this proves nothing"


# The missed instalment must be made good before a level journey cures (SYN-2016-549 on 298149a1fc:
# its 4 Apr 2018 GBP 45 failed, 4 May's was collected, and the desk cured on 4 May with April never
# re-collected). Oldest-first, May's cash meets April's request and the shortfall moves onto the
# request presented that day, which ages 0 days and read as nothing overdue.

def _journey_state(triad, cid, on):
    """(open?, cure dates) for the household's account, walked through `on`."""
    journeys = triad.collections_journeys(on)
    cured = [s["on"] for j in journeys for s in j["stages"] if s["stage"] == "cured"]
    return any(j.get("exit") is None for j in journeys), cured, journeys


def test_a_missed_instalment_not_made_good_holds_the_journey_and_a_made_good_one_cures(
        triad, monkeypatch):
    """Both branches in one control, the cure first so a desk that never cures cannot pass.

    Made good: January's GBP 60 returns on 5 Jan and is re-collected on 25 Jan, so the journey cures.
    Not made good: January's GBP 60 returns, February's GBP 60 is collected on 5 Feb, and nothing
    else is paid. The household is one instalment behind on every day after, so the journey stays
    open with GBP 60 owed."""
    _fail_months(monkeypatch, ["2025-01"])
    repaid = LivePaymentTriad()
    repaid._method_for = lambda cid, fuel="electricity": DIRECT_DEBIT
    monkeypatch.setattr(lpt, "later_settlement_date", lambda event, segment="resi": (
        date.fromisoformat(event.due_date) + timedelta(days=20) if event.result == "failed" else None))
    good = _replay(repaid, "SEAS-MADE-GOOD", SEASONAL, lambda m: (f"{m}-05", 60.00))
    assert [j["exit"] for j in good] == ["cured"], good

    monkeypatch.setattr(lpt, "later_settlement_date", lambda event, segment="resi": None)
    _replay(triad, "SEAS-NEVER-GOOD", SEASONAL, lambda m: (f"{m}-05", 60.00))
    still_open, cured, journeys = _journey_state(triad, "SEAS-NEVER-GOOD", date(2025, 6, 30))
    assert journeys, "the return must open a journey, or the hold below proves nothing"
    assert cured == [], f"cured over the unmade-good January instalment on {cured}"
    assert still_open, journeys
    last = journeys[-1]["stages"][-1]
    assert last["overdue_gbp"] == pytest.approx(60.00), last


def test_an_account_that_left_level_dd_is_dunned_on_its_bills(triad, monkeypatch):
    """Level for October to December (GBP 60 against GBP 320 of bills), then each bill collected at
    its face. January's bill (GBP 150) fails and is paid 20 days late. Read on the stopped schedule,
    that met everything asked and the journey cured on 6 Mar, with GBP 260 owed on bills past their
    due dates. Walked on its bills, it does not cure while a bill due is unpaid."""
    _fail_months(monkeypatch, ["2025-01"])
    monkeypatch.setattr(lpt, "later_settlement_date", lambda event, segment="resi": (
        date.fromisoformat(event.due_date) + timedelta(days=20) if event.result == "failed" else None))
    level_months = {"2024-10", "2024-11", "2024-12"}
    _replay(triad, "SEAS-LEFT", SEASONAL,
            lambda m: (f"{m}-05", 60.00) if m in level_months else None)
    ledger = triad._ledger_book.ledger(lpt.account_of("SEAS-LEFT"))
    _open, cured, journeys = _journey_state(triad, "SEAS-LEFT", date(2025, 6, 30))
    assert journeys, "January's failed bill must open a journey"
    # The view reads what the bills owe once the schedule has stopped, not the stopped schedule's
    # shortfall. Corrected 9 Nov 2026: this asserted the whole balance (GBP 290) overdue on 15 Feb,
    # the scheme's GBP 140 debit included. That debit is demanded on the closing statement of
    # 31 Jan, due 28 Feb (`arrears_engine.left_level_asks`), so on 15 Feb only January's GBP 150 is.
    first = journeys[0]["stages"][0]
    assert first["on"] == "2025-02-15" and first["overdue_gbp"] == pytest.approx(150.00), first
    assert ledger.balance(date(2025, 2, 15)) == pytest.approx(290.00)
    assert date(2025, 3, 6) not in [date.fromisoformat(c) for c in cured], cured
    for c in cured:
        on = date.fromisoformat(c)
        assert ledger.balance(on) <= 0.005 or not lpt_owes(ledger, on), (c, ledger.balance(on))


def lpt_owes(ledger, on):
    from company.billing.collections_journey import _owes_a_bill_due_by
    return _owes_a_bill_due_by(ledger, on, 14)


# Level for October to December at the bills' own GBP 100, so the account leaves level DD square.
# Then each bill is collected at its face on its due date (all weekdays).
LEFT_SQUARE = [
    ("2024-10", "2024-10-31", date(2024, 11, 14), 100.00),
    ("2024-11", "2024-11-29", date(2024, 12, 13), 100.00),
    ("2024-12", "2024-12-31", date(2025, 1, 14), 100.00),
    ("2025-01", "2025-01-31", date(2025, 2, 14), 100.00),
    ("2025-02", "2025-02-28", date(2025, 3, 14), 100.00),
    ("2025-03", "2025-03-31", date(2025, 4, 14), 100.00),
]


def _left_square(m):
    return (f"{m}-05", 100.00) if m in {"2024-10", "2024-11", "2024-12"} else None


def test_a_left_level_household_one_bill_behind_does_not_cure_on_each_due_date(triad, monkeypatch):
    """A household that has left level DD misses January's bill and then pays each later bill on its
    due date. On every due date, the cash goes to the oldest bill first. The GBP 100 still owed moves
    onto the bill due that day, so the view reads it 0 days overdue. The stopped schedule asks
    nothing and has been met. Only the bill walk (`_owes_a_bill_due_by`) sees a bill due that is
    still unpaid. A desk that kept this account on its schedule cured on 14 Mar and 14 Apr 2025,
    each time with GBP 100 owed (mutation M2 on d8264b525e, which no other test here reds).

    Partition first: the same household with January re-collected 20 days late is square, so the
    desk must be able to cure it."""
    _fail_months(monkeypatch, ["2025-01"])
    made_good = LivePaymentTriad()
    made_good._method_for = lambda cid, fuel="electricity": DIRECT_DEBIT
    monkeypatch.setattr(lpt, "later_settlement_date", lambda event, segment="resi": (
        date.fromisoformat(event.due_date) + timedelta(days=20) if event.result == "failed" else None))
    _replay(made_good, "LEFT-MADE-GOOD", LEFT_SQUARE, _left_square)
    _open, cured_good, _j = _journey_state(made_good, "LEFT-MADE-GOOD", date(2025, 6, 30))
    assert cured_good, "a left-level household that made its missed bill good must be able to cure"

    monkeypatch.setattr(lpt, "later_settlement_date", lambda event, segment="resi": None)
    _replay(triad, "LEFT-BEHIND", LEFT_SQUARE, _left_square)
    ledger = triad._ledger_book.ledger(lpt.account_of("LEFT-BEHIND"))
    still_open, cured, journeys = _journey_state(triad, "LEFT-BEHIND", date(2025, 6, 30))
    assert journeys, "January's failed bill must open a journey, or the hold below proves nothing"
    # The shape the hold is about: on each due date the household owes, yet the view reads 0 days.
    for due in (date(2025, 3, 14), date(2025, 4, 14)):
        assert ledger.balance(due) == pytest.approx(100.00) and lpt_owes(ledger, due), due
    assert cured == [], f"cured one bill behind on {cured}"
    assert still_open, journeys


def test_a_level_month_of_nothing_is_not_read_as_leaving_level_dd(triad, monkeypatch):
    """December's level amount is GBP 0, so nothing is presented and no level request is recorded.
    Read as a leaver from its GBP 140 December bill, the leg was dunned on that bill on 15 Jan, though
    every collection the schedule asked was taken and January's level collection follows. The
    company set the ask, so it records that December asked nothing (`note_bill_asked`) and the leg
    stays on level (`arrears_engine._shows_how_it_pays`)."""
    _fail_months(monkeypatch, [])
    _replay(triad, "SEAS-NIL", SEASONAL,
            lambda m: (f"{m}-05", 0.0 if m == "2024-12" else 60.00))
    ledger = triad._ledger_book.ledger(lpt.account_of("SEAS-NIL"))
    assert ledger.balance(date(2025, 1, 16)) > 100.0  # in debit, with December's bill unpaid: it can fail
    _open, _cured, journeys = _journey_state(triad, "SEAS-NIL", date(2025, 6, 30))
    assert journeys == [], journeys
