"""Reg 6D's refund clock starts on the day the final bill is issued, the day the ledger prints
(`arrears_engine.bill_issue_date`), not at the bill's period end (home_moves.md s.8.8 choice 2,
corrected 2026-11-12). From the period end, 134 of 176 clocks on the N29 replay started before the bill
existed, and SYN-2016-096g was refunded on 14 Jul 2020, two days before its final bill was issued."""
from __future__ import annotations

import datetime as dt

from simulation.arrears_engine import bill_generation_delay_days, bill_issue_date
from simulation.credit_refund_events import generate_credit_refund_log

_PERIOD_ENDS = [f"20{yy}-{mm:02d}-28" for yy in range(17, 25) for mm in (1, 4, 7, 10)]


def _leavers() -> list[tuple[str, str]]:
    return [(f"L{i}", pe) for i, pe in enumerate(_PERIOD_ENDS)]


def test_the_refund_clock_starts_on_the_issue_day_the_ledger_prints():
    leavers = _leavers()
    # The defect is only visible where the bill is issued after its period end. Assert this
    # fixture holds such a bill before asserting what the clock does on it.
    assert any(bill_generation_delay_days(cid, pe) > 0 for cid, pe in leavers)
    bills = [{"customer_id": cid, "period_end": pe, "total_amount_gbp": 50.0} for cid, pe in leavers]
    log = generate_credit_refund_log(bills, {}, {cid: -20.0 for cid, _ in leavers})
    assert len(log) == len(leavers)
    for event, (cid, pe) in zip(sorted(log, key=lambda e: e["customer_id"]),
                                sorted(leavers), strict=True):
        issued = bill_issue_date(cid, pe)
        assert event["request_date"] == issued.isoformat(), (cid, pe, event)
        assert dt.date.fromisoformat(event["paid_date"]) >= issued, (cid, event)


def test_the_issue_day_is_the_due_day_less_the_payment_terms():
    from simulation.arrears_engine import PAYMENT_TERMS_DAYS, bill_due_date
    for cid, pe in _leavers():
        assert bill_due_date(cid, pe) - dt.timedelta(days=PAYMENT_TERMS_DAYS) == bill_issue_date(cid, pe)
