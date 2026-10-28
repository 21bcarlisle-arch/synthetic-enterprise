"""The collections desk opens a journey the day after a bill falls due, on the date the billing
ledger gives that bill: issued after the month's last supplied day, payable 14 days later
(`arrears_engine.bill_due_date`, the one home).

The defect this pins: the run posted each month's bill to the company's own ledger, which the desk
walks, as due on the 28th of the month being billed, before the month had ended. On the 2eeb3f0b3
book every one of 7,151 journeys opened on a 29th or a 1st (the day after 28 Feb), and 1,987 opened
where the billing ledger showed every bill then due collected. SYN-2016-356 opened on 29 Oct 2016
against its October bills, which the ledger made due on 17-18 Nov.

One run of phase 4c over the real loop to the end of 2016.
"""
from __future__ import annotations

from datetime import date, timedelta

import pytest

import simulation.run_phase4c_on_phase2b as p4c
from simulation.arrears_engine import bill_due_date
from simulation.household import household_of

REPORT_END = "2016-12-31"


@pytest.fixture(scope="module")
def walked():
    return p4c.main(report_end=REPORT_END)


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


def test_every_journey_opens_the_day_after_a_bill_the_ledger_made_due(walked):
    dues: dict[str, set[date]] = {}
    for b in walked["bills"]:
        dues.setdefault(household_of(b["customer_id"]), set()).add(
            bill_due_date(b["customer_id"], b["period_end"]))
    stray = [(acct, opened) for acct, opened in _openings(walked)
             if opened - timedelta(days=1) not in dues.get(acct, ())]
    assert not stray, (
        f"{len(stray)} journeys open on a day no bill of the account fell due the day before, "
        f"e.g. {stray[:5]}")


def test_no_bill_falls_due_before_its_period_has_ended(walked):
    early = [(b["customer_id"], b["period_end"]) for b in walked["bills"]
             if bill_due_date(b["customer_id"], b["period_end"])
             <= date.fromisoformat(b["period_end"][:10])]
    assert not early, early[:5]
