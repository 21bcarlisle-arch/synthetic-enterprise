"""A dunning step is judged on the ledger the desk held when it issued it, never re-judged on history
a later, back-valued credit rewrote -- and an account still in arrears is still dunned.

DEFECT (ACC-SYN-2016-239 on book 61118 at the s.12g pin, 22 Nov; ACC-OCC-a8040dab0992 on seed 61106,
11 Oct): the desk issued reminder_2 on 2020-12-15 and its refusal, run straight after the step,
passed -- the ledger then owed. A credit value-dated on or before 12-15 was posted after the walk
had passed that day, so the ledger now read GBP -22.53 for 12-15. At the next step (the cure, 12-16)
the desk handed the WHOLE journey to the refusal again, which re-read 12-15 on the revised ledger
and stopped a 2h21m run. A supplier's ledger takes back-valued cash routinely (a bank's value date
precedes the day the file arrives); the reminder was lawful on what the company held.

What each control names as its own defect:

  * `test_a_back_valued_credit_does_not_re_judge_a_step_already_issued` -- the desk re-judges
    stages it already judged at issuance (the guard removed): it raises at the cure. It also names
    the silent form of the fix: the retro-cleared step must be RECORDED, not dropped.
  * `test_an_account_still_in_arrears_is_still_dunned` -- the guard over-reaches: the same account
    without the late credit must still climb to reminder_2 and stay open.
  * `test_a_step_issued_on_a_ledger_that_already_reads_cleared_is_still_refused` -- the guard
    stops judging new steps too: a step issued when the ledger already reads cleared must raise.
"""
from __future__ import annotations

import datetime as dt

import pytest

from company.billing.account_ledger import LedgerBook, LedgerEvent, LedgerEventType
from company.billing.collections_journey import CURED, CollectionsJourneyDesk
from company.billing.payment_observation_consumer import PaymentObservationConsumer
from company.compliance.domain_invariants import (
    DunningOfAClearedDebtError,
    refuse_dunning_of_a_cleared_debt,
)
from company.crm.account_hierarchy import Segment

ISSUE = dt.date(2024, 1, 1)  # due 01-15, missed 01-16, reminder 01-22, reminder_2 01-29
REMINDER_2 = dt.date(2024, 1, 29)


def _event(kind, account, gbp, on, n, posted=None):
    return LedgerEvent(event_id=f"{kind.value}:{account}:{n}", account_id=account,
                       event_type=kind, amount_gbp=gbp, valid_time=on,
                       transaction_time=dt.datetime.combine(posted or on, dt.time(0, 0)),
                       invoice_ref=f"{account}::{n}")


def _walked_past_reminder_2(account):
    consumer = PaymentObservationConsumer(ledger_book=LedgerBook())
    consumer.ledger_book.post(_event(LedgerEventType.BILL_DEBIT, account, 100.0, ISSUE, 1))
    consumer.advance_collections_journey(account, dt.date(2024, 1, 30))
    (journey,) = consumer.collections_journeys.journeys()
    assert ("reminder_2", REMINDER_2.isoformat()) in [(s["stage"], s["on"])
                                                       for s in journey["stages"]]
    return consumer


def test_a_back_valued_credit_does_not_re_judge_a_step_already_issued():
    consumer = _walked_past_reminder_2("ACC-LATE-CREDIT")
    # The household paid on 01-29, the reminder_2 day; the company learns of it on 02-02, after the
    # walk passed 01-29. The ledger now reads 01-29 at GBP -22.53, as ACC-SYN-2016-239 did.
    consumer.ledger_book.post(_event(LedgerEventType.PAYMENT_CREDIT, "ACC-LATE-CREDIT", 122.53,
                                     REMINDER_2, 1, posted=dt.date(2024, 2, 2)))
    consumer.advance_collections_journey("ACC-LATE-CREDIT", dt.date(2024, 3, 1))

    (journey,) = consumer.collections_journeys.journeys()
    assert journey["exit"] == CURED
    # Recorded, not dropped: the step a later credit cleared is named with what the ledger now reads.
    assert consumer.collections_journeys.steps_cleared_after_issue == [{
        "account_id": "ACC-LATE-CREDIT", "stage": "reminder_2", "on": REMINDER_2.isoformat(),
        "ledger_balance_gbp": -22.53, "found_on": journey["stages"][-1]["on"]}]


def test_an_account_still_in_arrears_is_still_dunned():
    consumer = _walked_past_reminder_2("ACC-STILL-OWES")
    consumer.advance_collections_journey("ACC-STILL-OWES", dt.date(2024, 3, 1))
    (journey,) = consumer.collections_journeys.journeys()
    stages = [s["stage"] for s in journey["stages"]]
    assert journey["exit"] is None and CURED not in stages
    assert "reminder_2" in stages and "repayment_plan_offer" in stages
    assert consumer.collections_journeys.steps_cleared_after_issue == []


def test_a_step_issued_on_a_ledger_that_already_reads_cleared_is_still_refused():
    ledger = LedgerBook()
    for e in (_event(LedgerEventType.BILL_DEBIT, "ACC-X", 100.0, ISSUE, 1),
              _event(LedgerEventType.PAYMENT_CREDIT, "ACC-X", 100.0, dt.date(2024, 1, 20), 1)):
        ledger.post(e)

    def stale_view(account, segment, on):
        days = (on - dt.date(2024, 1, 15)).days
        return {"undisputed_overdue_gbp": 100.0, "max_days_overdue": days,
                "dunning_action": "reminder" if days < 14 else "final_notice",
                "dunning_channel": "letter"}

    desk = CollectionsJourneyDesk(
        view_at=stale_view,
        refuse_dunning_of_cleared_debt=lambda journey, account: refuse_dunning_of_a_cleared_debt(
            journey, lambda acc, on: ledger.ledger(acc).balance(on)),
    )
    with pytest.raises(DunningOfAClearedDebtError, match="final_notice"):
        desk.advance(ledger.ledger("ACC-X"), Segment.RESIDENTIAL, dt.date(2024, 3, 1))
