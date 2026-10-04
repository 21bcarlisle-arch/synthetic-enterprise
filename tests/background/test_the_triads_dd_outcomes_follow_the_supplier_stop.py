"""The company's own ledger stops filing a stopped household as direct debit.

Defect it names: `LivePaymentTriad` posted every month of a drawn-DD supply point as a DD collection
-- a request, a remittance keyed to the invoice, an ARUDD line -- after the supplier had cancelled the
mandate and told the household. The money side (`arrears_engine.paying_method`) and the seam
(`SimInterface.get_payment_method(as_of=)`) already paid it on receipt, and the renewal price reads
this ledger.

And the ordering the wiring depends on: the run asks the stop board at each month bill's due date,
and the board can only answer from every month before it. Posted inside the term's record loop, a
bill asked before the board had seen the term, and the board cached a false "clear".
"""
from __future__ import annotations

from datetime import date

import pytest

import background.live_payment_triad as triad_module
import simulation.dd_collection_book as dcb
from background.live_payment_triad import LivePaymentTriad
from simulation.arrears_engine import PAY_ON_RECEIPT_METHOD
from simulation.payment_behaviour_source import DIRECT_DEBIT

NOTICE = date(2022, 6, 10)
DUES = [date(2022, m, 28) for m in range(3, 10)]


def _household(want_dd: bool) -> str:
    triad = LivePaymentTriad()
    return next(cid for cid in (f"TRIADSTOP-{i:02d}" for i in range(80))
                if (triad._method_for(cid) == DIRECT_DEBIT) is want_dd)


def _post(cid: str, stopped_by) -> list:
    triad = LivePaymentTriad()
    for due in DUES:
        triad.record_period(customer_id=cid, due_date=due, amount_gbp=60.0,
                            income_stress_value="low", dd_stopped_by=stopped_by)
    return triad._records


def test_a_dd_household_is_collected_before_the_notice_and_pays_on_receipt_after_it():
    records = _post(_household(True), lambda _cid, due: due >= NOTICE)
    methods = [r.payment_method for r in records]
    assert DIRECT_DEBIT in methods and PAY_ON_RECEIPT_METHOD in methods, methods
    for r in records:
        assert r.payment_method == (PAY_ON_RECEIPT_METHOD if r.due_date >= NOTICE else DIRECT_DEBIT)
        # A bill paid on receipt carries no remittance keyed to the invoice: no DD pulled it.
        assert (r.correlation_id == r.invoice_ref) is (r.payment_method == DIRECT_DEBIT)


def test_a_household_that_never_held_a_mandate_is_not_moved_by_a_stop():
    cid = _household(False)
    assert ([r.payment_method for r in _post(cid, lambda _cid, _due: True)]
            == [r.payment_method for r in _post(cid, None)])


#: Past the first renewals, so terms split months and a term's later months are asked about while
#: its earlier months are still unobserved if the posting runs inside the loop.
REPORT_END = "2017-02-28"


def test_the_board_holds_every_earlier_month_whenever_the_ledger_asks_it():
    """SURVIVOR: posting a month's bill inside the record loop, before the board observes the term.
    Every answer is checked against the board's own final store, cut at the same month."""
    asked: list[tuple[str, str, int]] = []
    boards: list = []
    real_install = dcb.install_stop_notice_board
    real_record = LivePaymentTriad.record_period

    def record(self, **kw):
        stopped_by = kw.get("dd_stopped_by")
        assert stopped_by is not None, "the run posts a month bill without asking about the stop"

        def counted(cid, due):
            cutoff = due.replace(day=1).isoformat()
            board = boards[-1]
            asked.append((cid, cutoff, sum(1 for r in board._records.get(cid, [])
                                           if r["settlement_date"] < cutoff)))
            return stopped_by(cid, due)
        return real_record(self, **{**kw, "dd_stopped_by": counted})

    def install(board):
        if board is not None:
            boards.append(board)
        real_install(board)

    mp = pytest.MonkeyPatch()
    mp.setattr(triad_module.LivePaymentTriad, "record_period", record)
    mp.setattr(dcb, "install_stop_notice_board", install)
    try:
        from simulation.run_phase2b import main as run_phase2b
        run_phase2b(report_end=REPORT_END)
    finally:
        mp.undo()
    final = boards[-1]._records
    assert len(asked) > 100, f"the run asked the board {len(asked)} times; nothing was tested"
    short = [(cid, cut, held) for cid, cut, held in asked
             if held != sum(1 for r in final.get(cid, []) if r["settlement_date"] < cut)]
    assert not short, (
        f"{len(short)} of {len(asked)} questions were asked before the board had the months they "
        f"depend on, e.g. {short[:3]}")
