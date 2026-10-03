"""EP4 -- debt as a dated journey per account, and the R10 refusal to dun a cleared debt.

What each control names as its own defect:

  * `test_a_journey_walks_miss_to_ladder_to_cure_and_the_open_branch_is_reachable_too` -- the desk
    records nothing, records stages out of order, or can only ever end one way. Both exits of the
    partition (cured, still open) are asserted in ONE control before what either looks like.
  * `test_the_desk_refuses_a_step_issued_against_a_cleared_ledger` -- the R10 obligation is wired
    to nothing: a view that duns a household whose ledger reads zero goes through.
  * `test_the_obligation_*` -- the invariant refuses everything (lawful journey must pass) or
    nothing (a step on a cleared balance, a step after the cure).
  * `test_the_order_check_*` -- the lawful-order table accepts any walk.
  * `test_a_short_live_run_*` -- the journey is not reached by a production run, or a run decides
    steps after its own last day.
"""
from __future__ import annotations

import datetime as dt

import pytest

from company.billing.account_ledger import LedgerBook, LedgerEvent, LedgerEventType
from company.billing.collections_journey import (
    CURED,
    MISSED_PAYMENT,
    CollectionsJourneyDesk,
    UnlawfulJourneyOrderError,
    assert_journey_order_lawful,
)
from company.billing.payment_observation_consumer import PaymentObservationConsumer
from company.compliance import obligations_register as orr
from company.compliance.domain_invariants import (
    ALL_INVARIANTS,
    DUNNING_REQUIRES_AN_UNCLEARED_DEBT,
    DunningOfAClearedDebtError,
    dunning_of_a_cleared_debt,
    refuse_dunning_of_a_cleared_debt,
)
from company.crm.account_hierarchy import Segment

ISSUE = dt.date(2024, 1, 1)  # due 2024-01-15 on the 14-day terms


def _event(kind, account, gbp, on, n):
    return LedgerEvent(event_id=f"{kind.value}:{account}:{n}", account_id=account,
                       event_type=kind, amount_gbp=gbp, valid_time=on,
                       transaction_time=dt.datetime.combine(on, dt.time(0, 0)),
                       invoice_ref=f"{account}::{n}")


def _consumer_with(account, *events):
    consumer = PaymentObservationConsumer(ledger_book=LedgerBook())
    for e in events:
        consumer.ledger_book.post(e)
    return consumer


def test_a_journey_walks_miss_to_ladder_to_cure_and_the_open_branch_is_reachable_too():
    paid_late = _consumer_with(
        "ACC-LATE",
        _event(LedgerEventType.BILL_DEBIT, "ACC-LATE", 100.0, ISSUE, 1),
        _event(LedgerEventType.PAYMENT_CREDIT, "ACC-LATE", 100.0, dt.date(2024, 2, 20), 1),
    )
    paid_late.advance_collections_journey("ACC-LATE", dt.date(2024, 3, 1))
    never_paid = _consumer_with(
        "ACC-NEVER", _event(LedgerEventType.BILL_DEBIT, "ACC-NEVER", 100.0, ISSUE, 1))
    never_paid.advance_collections_journey("ACC-NEVER", dt.date(2024, 3, 1))

    (cured,) = paid_late.collections_journeys.journeys()
    (still_open,) = never_paid.collections_journeys.journeys()
    assert cured["exit"] == CURED and still_open["exit"] is None
    assert [(s["stage"], s["on"]) for s in cured["stages"]] == [
        (MISSED_PAYMENT, "2024-01-16"), ("reminder", "2024-01-16"),
        ("reminder_2", "2024-01-29"), ("repayment_plan_offer", "2024-02-12"),
        (CURED, "2024-02-20"),
    ]
    for journey in (cured, still_open):
        assert_journey_order_lawful(journey, Segment.RESIDENTIAL)


def test_a_bill_paid_on_its_due_date_opens_no_journey():
    on_time = _consumer_with(
        "ACC-OK",
        _event(LedgerEventType.BILL_DEBIT, "ACC-OK", 100.0, ISSUE, 1),
        _event(LedgerEventType.PAYMENT_CREDIT, "ACC-OK", 100.0, dt.date(2024, 1, 15), 1),
    )
    on_time.advance_collections_journey("ACC-OK", dt.date(2024, 3, 1))
    assert on_time.collections_journeys.journeys() == []


def test_the_desk_refuses_a_step_issued_against_a_cleared_ledger():
    """A view that keeps escalating after the cash landed on 01-20 (it never re-reads the
    ledger): its next step, on the 01-29 trigger, must raise, not be recorded."""
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


def test_the_consumers_desk_is_wired_to_the_refusal():
    """The same stale view, put behind the consumer's own desk: the refusal the consumer wired
    (its ledger's balance) must fire. Guards the wiring, not only the invariant."""
    consumer = _consumer_with(
        "ACC-Y",
        _event(LedgerEventType.BILL_DEBIT, "ACC-Y", 100.0, ISSUE, 1),
        _event(LedgerEventType.PAYMENT_CREDIT, "ACC-Y", 100.0, dt.date(2024, 1, 20), 1),
    )

    def stale_view(account, segment, on):
        days = (on - dt.date(2024, 1, 15)).days
        return {"undisputed_overdue_gbp": 100.0, "max_days_overdue": days,
                "dunning_action": "reminder" if days < 14 else "final_notice",
                "dunning_channel": "letter"}

    consumer.collections_journeys._view_at = stale_view
    with pytest.raises(DunningOfAClearedDebtError):
        consumer.advance_collections_journey("ACC-Y", dt.date(2024, 3, 1))


def _journey(*stages, exit=None):
    return {"account_id": "ACC-J", "segment": "residential", "exit": exit,
            "stages": [{"stage": s, "on": on} for s, on in stages]}


def test_the_obligation_passes_a_lawful_journey_and_refuses_both_wrongful_shapes():
    owes = lambda acc, on: 100.0 if on < dt.date(2024, 2, 20) else 0.0  # noqa: E731
    lawful = _journey((MISSED_PAYMENT, "2024-01-16"), ("reminder", "2024-01-16"),
                      (CURED, "2024-02-20"), exit=CURED)
    assert dunning_of_a_cleared_debt(lawful, owes) == []
    on_a_cleared_balance = _journey((MISSED_PAYMENT, "2024-01-16"),
                                    ("final_notice", "2024-03-01"))
    after_its_cure = _journey((MISSED_PAYMENT, "2024-01-16"), (CURED, "2024-01-20"),
                              ("reminder_2", "2024-01-29"))
    assert [f["stage"] for f in dunning_of_a_cleared_debt(on_a_cleared_balance, owes)] == [
        "final_notice"]
    assert [f["stage"] for f in dunning_of_a_cleared_debt(after_its_cure, owes)] == ["reminder_2"]
    with pytest.raises(DunningOfAClearedDebtError):
        refuse_dunning_of_a_cleared_debt(on_a_cleared_balance, owes)


def test_the_obligation_is_registered_and_enforced_by_its_invariant():
    row = next(o for o in orr.REGISTER if o.id == "no_dunning_of_a_paid_debt")
    assert row.enforcing_invariant_key == DUNNING_REQUIRES_AN_UNCLEARED_DEBT.id
    assert DUNNING_REQUIRES_AN_UNCLEARED_DEBT in ALL_INVARIANTS
    assert "company/billing/collections_journey.py" in row.tracker_paths


@pytest.mark.parametrize("stages, exit, why", [
    ((("reminder", "2024-01-16"),), None, "a ladder step before any missed payment"),
    (((MISSED_PAYMENT, "2024-01-16"), ("reminder", "2024-01-10")), None, "dates backwards"),
    (((MISSED_PAYMENT, "2024-01-16"), (CURED, "2024-01-20"), ("reminder", "2024-01-29")),
     None, "a step after the cure"),
    (((MISSED_PAYMENT, "2024-01-16"), ("reminder", "2024-01-16")), CURED, "exit not last"),
    ((), None, "no stages"),
])
def test_the_order_check_refuses_an_unlawful_walk(stages, exit, why):
    with pytest.raises(UnlawfulJourneyOrderError):
        assert_journey_order_lawful(_journey(*stages, exit=exit), Segment.RESIDENTIAL)


#: The shortest window found with a missed payment AND a cure: January 2016 has no miss on any
#: account; February's first misses are observable on 2016-02-29, and the earliest cure is 03-02.
LIVE_WINDOW_END = "2016-03-02"


@pytest.fixture(scope="module")
def live_journeys():
    from simulation.run_phase2b import main

    return main(report_end=LIVE_WINDOW_END)["collections_journeys"]


def test_a_short_live_run_records_journeys_in_lawful_order_and_reaches_both_exits(live_journeys):
    assert live_journeys, "no account missed a payment -- the journey branch was never taken"
    assert any(len(j["stages"]) >= 2 for j in live_journeys)
    assert {j["exit"] for j in live_journeys} >= {CURED, None}
    for journey in live_journeys:
        assert_journey_order_lawful(journey, Segment(journey["segment"]))
        assert all(s["on"] <= LIVE_WINDOW_END for s in journey["stages"]), (
            f"{journey['account_id']} has a step decided after the run's last day")
