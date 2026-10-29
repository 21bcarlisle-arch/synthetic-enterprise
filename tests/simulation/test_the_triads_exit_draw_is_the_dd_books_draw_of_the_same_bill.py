"""The triad draws a mover's exit as the DD book draws the same bill: keyed by the bill's period end.

`arrears_engine.mover_final_bill_outcome` takes the period end, and the DD book, the arrears engine and
the pay-on-receipt path all pass it. The triad passed the bill's DUE date, which is in the next month,
so (a) the bill for the month before a move, due in the move month, was drawn as an exit (SYN-2016-083's
Jan 2019 bill on the 209c3350ab book, part paid as if it were the final one), and (b) the final bill's
draw was seeded by a different string from the DD book's, so the two disagreed on 71 of the book's 211
final bills. Found by 156f8dfd6; `docs/staging/SEAT_FINDING_THE_PAGE_PRINTS_MORE_OVERDUE_THAN_IT_SAYS_
IS_OWED_ON_493_OF_752_HOUSEHOLDS_2026-10-28.md`, "What this exposes", item 2.
"""
from __future__ import annotations

from datetime import date

import simulation.arrears_engine as ae
import simulation.world_payment_truth as wpt
from background.live_payment_triad import LivePaymentTriad

# SYN-2016-083 on the 209c3350ab book: left on 18 Feb 2019, so its last supplied day is the 17th.
CID, MOVED = "SYN-2016-083", "2019-02-18"


def _spy(monkeypatch):
    monkeypatch.setattr(wpt, "UNIFIED", True)
    seen = []
    real = ae.mover_final_bill_outcome

    def spy(behavioral, cid, period_end, *a, **k):
        out = real(behavioral, cid, period_end, *a, **k)
        seen.append((cid, period_end, out))
        return out

    monkeypatch.setattr("background.live_payment_triad.mover_final_bill_outcome", spy)
    return seen


def test_syn_2016_083s_jan_2019_bill_is_not_its_exit_and_its_final_is_keyed_by_its_period_end(
        monkeypatch):
    """Defect: the Jan 2019 bill (due 14 Feb, in the move month) was drawn as the exit, and the Feb
    bill's draw was keyed by its due date."""
    seen = _spy(monkeypatch)
    triad = LivePaymentTriad()
    jan = triad.record_period(customer_id=CID, due_date=ae.bill_due_date(CID, "2019-01-31"),
                              amount_gbp=118.33, income_stress_value="low", bill_month="2019-01",
                              period_end="2019-01-31", moved_out_on=MOVED)
    triad.record_period(customer_id=CID, due_date=ae.bill_due_date(CID, "2019-02-17"),
                        amount_gbp=60.0, income_stress_value="low", bill_month="2019-02",
                        period_end="2019-02-17", moved_out_on=MOVED)
    exits = [(pe, out) for _, pe, out in seen if out is not None]
    assert [pe for pe, _ in exits] == ["2019-02-17"], seen
    assert (CID, "2019-01") not in triad._final_bill_part_share, jan


def test_every_exit_the_triad_draws_is_keyed_as_the_dd_book_keys_it(monkeypatch):
    """Over a population: every exit draw the triad makes is asked with the bill's period end, the
    key the DD book's draw of the same bill uses, so the two agree bill for bill."""
    seen = _spy(monkeypatch)
    triad = LivePaymentTriad()
    for i in range(60):
        cid = f"RESI{i:05d}"
        for month, pe in (("2022-05", "2022-05-31"), ("2022-06", "2022-06-19")):
            triad.record_period(customer_id=cid, due_date=ae.bill_due_date(cid, pe),
                                amount_gbp=150.0, income_stress_value="high", bill_month=month,
                                period_end=pe, moved_out_on="2022-06-20")
    exits = [(cid, pe) for cid, pe, out in seen if out is not None]
    # The branch is taken: a household paying by DD or on receipt has its final bill drawn.
    assert len(exits) >= 30, seen[:5]
    assert {pe for _, pe in exits} == {"2022-06-19"}, sorted(set(exits))[:5]
