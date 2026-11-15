"""The collections desk opens a journey the day after a bill falls due, on the date the billing
ledger gives that bill: issued after the month's last supplied day, payable 14 days later
(`arrears_engine.bill_due_date`, the one home).

The defect this pins: the run posted each month's bill to the company's own ledger, which the desk
walks, as due on the 28th of the month being billed, before the month had ended. On the 2eeb3f0b3
book every one of 7,151 journeys opened on a 29th or a 1st (the day after 28 Feb), and 1,987 opened
where the billing ledger showed every bill then due collected. SYN-2016-356 opened on 29 Oct 2016
against its October bills, which the ledger made due on 17-18 Nov.

The property, keyed to what the desk dunns rather than to bills alone: a journey opens the day
after the last day to pay of an obligation the ledger made due. There are three kinds:
- a bill, due 14 days after issue. A DIRECT DEBIT bill due on a weekend or bank holiday is
  collected, on time, the next Bacs day, so it falls missed the day after THAT (c915067a8d);
- a scheduled level-DD collection, while the household is on level DD (a3136e29f);
- the closing statement a household leaving level DD is sent, due `CLOSING_STATEMENT_TERM_DAYS`
  after it left, or a leaving leg's own statement (8e73c52356, b8da2eed18).
Keyed to bills alone, this went red on f50286c8a with four journeys, all rightly opened. Three are
the Bacs roll: PROS-2016-0020 (a DD gas bill due Sat 16 Jul 2016, opened Tue 19), SYN-2016-325 (a
DD electricity bill due Sun 23 Oct, opened Tue 25), SYN-2016-024 (left level DD 6 Nov; its next DD
electricity bill, GBP 18.73 due Sun 20 Nov, collected short at GBP 5.23, opened Tue 22). One is a
closing statement: SYN-2016-005 (left level DD 2 Jul; its leg's statement, GBP 36.32 due 28 Jul,
opened 29). Mutations that fire: the desk's `last_day_to_pay` without the roll reds those three;
`leg_statement_asks` a day late reds SYN-2016-005.

One run of phase 4c over the real loop to the end of 2016.
"""
from __future__ import annotations

from datetime import date, timedelta

import pytest

import company.billing.collections_journey as cj
import simulation.run_phase4c_on_phase2b as p4c
from company.billing.arrears_engine import (
    CLOSING_STATEMENT_TERM_DAYS,
    leg_statement_asks,
    level_leave_dates,
)
from company.compliance.working_days import is_working_day
from simulation.arrears_engine import bill_due_date
from simulation.household import household_of

REPORT_END = "2016-12-31"


@pytest.fixture(scope="module")
def walked():
    """The run, plus each account's ledger and level schedule as the desk last walked them: the
    closing statements are dated on the company's ledger, which no run output carries."""
    seen: dict[str, tuple] = {}
    advance = cj.CollectionsJourneyDesk.advance

    def _advance(self, ledger, segment, through, payment_terms_days=14):
        level = self._level_of(ledger.account_id) if self._level_of is not None else None
        seen[ledger.account_id] = (ledger, level)
        return advance(self, ledger, segment, through, payment_terms_days)

    cj.CollectionsJourneyDesk.advance = _advance
    try:
        result = p4c.main(report_end=REPORT_END)
    finally:
        cj.CollectionsJourneyDesk.advance = advance
    result["_desk_ledgers"] = seen
    return result


def _openings(result) -> list[tuple[str, date]]:
    out = []
    for j in result["phase2b"]["collections_journeys"]:
        opened = next((s["on"] for s in j["stages"] if s["stage"] == "missed_payment"), None)
        if opened is not None:
            out.append((str(j["account_id"]).removeprefix("ACC-"), date.fromisoformat(opened)))
    return out


def test_the_run_opens_journeys_at_all(walked):
    # The partition's other side: a run whose desk never opened a journey passes the test below.
    assert len(_openings(walked)) >= 20


def _last_days_to_pay(walked) -> dict[str, dict[date, str]]:
    """Per account, each obligation's last day to pay -> its kind."""
    out: dict[str, dict[date, str]] = {}

    def _add(acct, day, kind):
        out.setdefault(acct, {}).setdefault(day, kind)

    for b in walked["bills"]:
        due = bill_due_date(b["customer_id"], b["period_end"])
        last = due
        # Read off the calendar, not the desk's `last_day_to_pay`, so a mutation there is seen.
        while b.get("payment_channel") == "direct_debit" and not is_working_day(last):
            last += timedelta(days=1)
        _add(household_of(b["customer_id"]), last, "bill" if last == due else "bill, Bacs roll")
    # A level DD household owes its schedule: a returned collection is missed the day after it.
    for cid, rows in (walked.get("level_dd_collections") or {}).items():
        for r in rows:
            _add(household_of(cid), date.fromisoformat(r["collection_date"]), "level collection")
    through = date.fromisoformat(REPORT_END)
    for account_id, (ledger, level) in walked["_desk_ledgers"].items():
        if level is None:
            continue
        acct = str(account_id).removeprefix("ACC-")
        for left in level_leave_dates(ledger, level[0], through):
            if left is not None:
                _add(acct, left + timedelta(days=CLOSING_STATEMENT_TERM_DAYS), "closing statement")
        for due, _gbp in leg_statement_asks(ledger, level[0], through):
            _add(acct, due, "closing statement")
    return out


def test_every_journey_opens_the_day_after_an_obligation_the_ledger_made_due(walked):
    owed = _last_days_to_pay(walked)
    kinds, stray = [], []
    for acct, opened in _openings(walked):
        kind = owed.get(acct, {}).get(opened - timedelta(days=1))
        (kinds if kind else stray).append(kind or (acct, opened))
    assert not stray, (
        f"{len(stray)} journeys open on a day no obligation of the account (a bill, a level "
        f"collection or a closing statement) fell due the day before, e.g. {stray[:5]}")
    # The rare legs must be reachable, or a property that only admits bills passes too.
    assert "bill, Bacs roll" in kinds and "closing statement" in kinds, sorted(set(kinds))


def test_no_bill_falls_due_before_its_period_has_ended(walked):
    early = [(b["customer_id"], b["period_end"]) for b in walked["bills"]
             if bill_due_date(b["customer_id"], b["period_end"])
             <= date.fromisoformat(b["period_end"][:10])]
    assert not early, early[:5]
