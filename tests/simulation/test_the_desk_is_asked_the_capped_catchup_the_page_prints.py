"""The collections desk is posted the bill the page prints, when N14's second pass caps a catch-up.

On the 4669d77ddd book, 78 of the 128 INV_OVERDUE_WITHIN_PAGE_BALANCE breaches were exactly a
back-billing write-off: OCC-75d17c23c1da's desk printed GBP 336.84 overdue against a page balance of
273.62 on 16 Jul 2022, the 63.22 its June gas bill wrote off under SLC 21BA. The published run
re-bills a catch-up on a bill paid on receipt (`rebill_catchups_off_direct_debit`); the in-loop
board that asks the desk's bills (`StopNoticeBoard.issued_bills_before`) never did, so the desk
chased the uncapped first pass.
"""
import simulation.dd_collection_book as dcb
from simulation.arrears_engine import payer_ask_gbp
from simulation.run_phase4c_on_phase2b import build_monthly_bills, rebill_catchups_off_direct_debit
from tests.simulation.test_a_catchup_on_a_cancelled_direct_debit_is_capped_at_twelve_months import (  # noqa: F401
    sixteen_month_run,
)
from tests.simulation.test_run_phase4c_on_phase2b import force_estimated_reads  # noqa: F401


def test_the_desk_asks_what_the_published_bill_asks(sixteen_month_run, monkeypatch):  # noqa: F811
    """Both arms over one board: C1's DD ended (catch-up capped), C2's did not (catch-up deferred
    whole to a DD recovery action). Defect caught: the board's bill for C1 still carried the
    uncapped catch-up, so the desk's overdue exceeded the page's balance by the write-off. A board
    that capped every DD catch-up reds on C2."""
    records = sixteen_month_run + [dict(r, customer_id="C2") for r in sixteen_month_run]
    monkeypatch.setattr(dcb, "supplier_dd_spells",
                        lambda bills, behavioral, seed=42: {"C1": [("2022-06-30", None)]})
    events: list = []
    first = build_monthly_bills(records, churned_ids={"C1", "C2"}, read_events_out=events)
    published, _ = rebill_catchups_off_direct_debit(records, first, events, {},
                                                    churned_ids={"C1", "C2"})
    last = max(b["period_end"] for b in published)[:7]

    board = dcb.StopNoticeBoard(lambda _sp: [])
    board.observe(records)
    asked = {sp: payer_ask_gbp(board.issued_bill_for(sp, last, churned=True)) for sp in ("C1", "C2")}
    printed = {sp: payer_ask_gbp(next(b for b in published if b["customer_id"] == sp
                                      and b["period_end"][:7] == last)) for sp in ("C1", "C2")}

    uncapped = {sp: payer_ask_gbp(next(b for b in first if b["customer_id"] == sp
                                       and b["period_end"][:7] == last)) for sp in ("C1", "C2")}

    assert printed["C1"] < uncapped["C1"]             # the capped branch is taken ...
    assert printed["C2"] == uncapped["C2"]            # ... and the deferred one still is
    assert asked == printed
