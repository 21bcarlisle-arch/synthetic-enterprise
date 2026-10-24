"""A household whose account closed pays no later lump dated after its final bill.

Defect each control names:

  * `test_a_closed_accounts_late_lump_is_lost_and_a_stayers_crosses` -- a gone household repays
    its arrears at the stayer's rate after its final bill, so the P&L writes off too little (the
    5-7x gap, `debt_realism_three_world_fidelity_gaps.md` s.1a); or the rule fires on everyone
    and a stayer's lump is lost too. Both partitions are asserted reachable first.
  * `test_a_lump_before_the_final_bill_still_crosses` -- the cut is at the departure, not at the
    final bill's due date, so a lump the household paid while still billed is lost.
  * `test_switched_off_the_late_lumps_cross_and_are_counted` -- the switch is decorative, or the
    off book hides what it would have lost.
  * `test_a_closure_told_as_it_happens_cuts_lumps_a_reader_forces_mid_run` -- the queue learns
    of closures only at the run's end, so readers inside the run (renewals forcing `arrears_state`
    and `default_belief_rate`) cross a gone household's late lumps first: 12 of 14 on the 24 Oct
    book. Both partitions (lost, and a stayer's crossed) are asserted reachable first.
  * `test_the_run_tells_the_queue_at_each_departure_and_unfollowed_move` -- `run_phase2b` keeps
    only the end-of-run backstop, so the in-run cut is never reached on a real book.
"""
from __future__ import annotations

from datetime import date

import pytest

import simulation.world_payment_truth as wpt
from background.live_payment_triad import LivePaymentTriad

_LEAVER, _STAYER = "RESI00001", "RESI00002"


def _run(leaver_last_month: int = 3, customers: int = 60) -> LivePaymentTriad:
    """High-stress households billed monthly through 2020. Every one with an odd index leaves
    after `leaver_last_month`; the rest stay billed to December."""
    triad = LivePaymentTriad()
    leavers = {f"RESI{i:05d}" for i in range(customers) if i % 2}
    for m in range(1, 13):
        for i in range(customers):
            cid = f"RESI{i:05d}"
            if cid in leavers and m > leaver_last_month:
                continue
            triad.record_period(customer_id=cid, due_date=date(2020, m, 28), amount_gbp=120.0,
                                income_stress_value="high", segment="resi")
    triad.close_accounts(leavers)
    triad.collections_journeys(date(2023, 12, 31))
    return triad


def _crossed_by(triad, odd: bool):
    return [c for c in triad._crossed_settlements if (int(c[0][-5:]) % 2 == 1) == odd]


def test_a_closed_accounts_late_lump_is_lost_and_a_stayers_crosses():
    triad = _run()
    assert triad.settlements_lost_at_close > 0, "no leaver's lump was ever lost: the rule never fires"
    assert [c for c in _crossed_by(triad, odd=False) if c[2] > date(2020, 12, 28)], (
        "no stayer's lump crossed after its last bill: the rule fires on accounts that never closed")
    final_due = date(2020, 3, 28)
    late = [c for c in _crossed_by(triad, odd=True) if c[2] > final_due]
    assert late == [], f"a gone household paid {len(late)} lump(s) after its final bill"
    assert triad.later_settlements()["lost_at_close"] == triad.settlements_lost_at_close


def test_a_lump_before_the_final_bill_still_crosses():
    """The cut is the final bill's due date, on a closed account only: the day itself crosses."""
    triad = _run()
    final_due = date(2020, 3, 28)
    leaver, stayer = "ACC-RESI00001", "ACC-RESI00002"
    assert triad._after_final_bill(leaver, date(2020, 3, 29)), "the rule never fires"
    assert not triad._after_final_bill(leaver, final_due), (
        "a lump on the final bill's own due date is lost: the cut is too early")
    assert not triad._after_final_bill(leaver, date(2020, 2, 1))
    assert not triad._after_final_bill(stayer, date(2023, 1, 1)), "a stayer's lump is lost"


def test_switched_off_the_late_lumps_cross_and_are_counted(monkeypatch):
    on = _run()
    monkeypatch.setattr(wpt, "GONE_HOUSEHOLD_PAYS_NO_LUMP", False)
    off = _run()
    assert off.settlements_lost_at_close == 0
    assert off.later_settlements()["crossed_after_close"] == on.settlements_lost_at_close > 0, (
        "switched off, the lumps the rule withholds must cross, and be counted as crossing")
    assert off.settlements_delivered == on.settlements_delivered + on.settlements_lost_at_close


def test_closing_after_a_forced_reader_is_seen_not_hidden():
    """A run that tells the queue of its closures only after a reader forced the late lumps across
    publishes them as `crossed_after_close`, rather than reading clean."""
    triad = LivePaymentTriad()
    leavers = {f"RESI{i:05d}" for i in range(60) if i % 2}
    for m in range(1, 13):
        for i in range(60):
            cid = f"RESI{i:05d}"
            if not (cid in leavers and m > 3):
                triad.record_period(customer_id=cid, due_date=date(2020, m, 28), amount_gbp=120.0,
                                    income_stress_value="high", segment="resi")
    triad.collections_journeys(date(2023, 12, 31))
    triad.close_accounts(leavers)
    assert triad.settlements_lost_at_close == 0
    assert triad.later_settlements()["crossed_after_close"] > 0, (
        "lumps a gone household paid after its final bill crossed before the closure was known, "
        "and the summary does not say so")


def test_a_closure_told_as_it_happens_cuts_lumps_a_reader_forces_mid_run():
    """The run's order: leavers stop being billed after March and are told closed then; a reader
    forces every account across in mid-2021, before the end-of-run backstop is ever called."""
    triad = LivePaymentTriad()
    leavers = {f"RESI{i:05d}" for i in range(60) if i % 2}
    for m in range(1, 13):
        for i in range(60):
            cid = f"RESI{i:05d}"
            if not (cid in leavers and m > 3):
                triad.record_period(customer_id=cid, due_date=date(2020, m, 28), amount_gbp=120.0,
                                    income_stress_value="high", segment="resi")
        if m == 4:
            for leaver in leavers:
                triad.close_account(leaver, date(2020, 3, 28))
    triad._deliver_settlements_through(date(2021, 6, 30), force=True)
    assert triad.settlements_lost_at_close > 0, "no late lump was cut mid-run: the closure is inert"
    assert [c for c in _crossed_by(triad, odd=False) if c[2] > date(2020, 12, 28)], (
        "no stayer's lump crossed after its last bill: the in-run cut fires on accounts never closed")
    assert triad.settlements_crossed_after_close == 0, (
        f"{triad.settlements_crossed_after_close} late lump(s) crossed though the closure was told "
        "before the reader forced them")


def test_the_run_tells_the_queue_at_each_departure_and_unfollowed_move():
    """Reachability on the real loop: `close_account` is called where a registration loss is
    filed and where a move that did not follow closes the account, ahead of the backstop."""
    import inspect

    import simulation.run_phase2b as run
    src = inspect.getsource(run._main)
    calls = [i for i in range(len(src)) if src.startswith("_payment_triad.close_account(", i)]
    backstop = src.index("_payment_triad.close_accounts(")
    notify = src.index("def _notify_registration_loss(")
    assert len(calls) == 2, f"{len(calls)} in-run closure call(s); a departure and a move each need one"
    assert any(notify < c < src.index("_pending = [] if pending_already_sent", notify)
               for c in calls), "a departure is not told to the queue when its loss is filed"
    assert all(c < backstop for c in calls), "an in-run closure is told only after the run ends"
