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
import re
from pathlib import Path

import pytest

from company.billing.account_ledger import LedgerBook, LedgerEvent, LedgerEventType
from company.billing.arrears_engine import dunning_path
from company.billing.collections_journey import (
    ARRANGEMENT_ACCEPTANCE_GAP,
    ARRANGEMENT_OFFERED,
    CURED,
    MISSED_PAYMENT,
    PLAN_OFFER_STEP,
    UNREACHED_EXITS,
    CollectionsJourneyDesk,
    UnlawfulJourneyOrderError,
    assert_journey_order_lawful,
)
from company.billing.payment_observation_consumer import PaymentObservationConsumer
from company.billing.payment_plan import PaymentPlanStatus
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
        (MISSED_PAYMENT, "2024-01-16"), ("reminder", "2024-01-22"),
        ("reminder_2", "2024-01-29"), ("repayment_plan_offer", "2024-02-12"),
        (ARRANGEMENT_OFFERED, "2024-02-12"), (CURED, "2024-02-20"),
    ]
    for journey in (cured, still_open):
        assert_journey_order_lawful(journey, Segment.RESIDENTIAL)


def test_the_first_reminder_waits_for_day_seven_and_a_bill_paid_inside_it_is_never_dunned():
    """The partition in ONE control: a household paying six days late opens a journey and cures
    with no reminder; one paying eight days late is reminded on day 7 exactly. Defects: the old
    day-0 trigger (the first account gets reminded), or a trigger that never fires (the second
    is not)."""
    six_late = _consumer_with(
        "ACC-6",
        _event(LedgerEventType.BILL_DEBIT, "ACC-6", 100.0, ISSUE, 1),
        _event(LedgerEventType.PAYMENT_CREDIT, "ACC-6", 100.0, dt.date(2024, 1, 21), 1),
    )
    eight_late = _consumer_with(
        "ACC-8",
        _event(LedgerEventType.BILL_DEBIT, "ACC-8", 100.0, ISSUE, 1),
        _event(LedgerEventType.PAYMENT_CREDIT, "ACC-8", 100.0, dt.date(2024, 1, 23), 1),
    )
    for consumer, account in ((six_late, "ACC-6"), (eight_late, "ACC-8")):
        consumer.advance_collections_journey(account, dt.date(2024, 3, 1))
    (unreminded,) = six_late.collections_journeys.journeys()
    (reminded,) = eight_late.collections_journeys.journeys()
    assert [s["stage"] for s in unreminded["stages"]] == [MISSED_PAYMENT, CURED]
    assert [(s["stage"], s["days_overdue"]) for s in reminded["stages"]][:2] == [
        (MISSED_PAYMENT, 1), ("reminder", _cited_first_reminder_day())]
    assert reminded["exit"] == CURED


def _cited_first_reminder_day() -> int:
    """The lower bound of "Overdue / first reminder | T+7-14d post-due", read from the research
    file the constant cites -- so the controls below are keyed to the source, not to the constant
    they check (a control reading the constant passes a mutated constant: seen, day 6 survived)."""
    table = Path(__file__).resolve().parents[3] / "docs" / "market_research" / (
        "company_debt_management.md")
    row = next(line for line in table.read_text().splitlines()
               if line.startswith("| Overdue / first reminder"))
    return int(re.search(r"T\+(\d+)[–-]\d+d post-due", row).group(1))


def test_the_first_reminder_day_is_the_research_tables_lower_bound():
    assert dunning_path(Segment.RESIDENTIAL)[0].trigger_days_overdue == _cited_first_reminder_day()


def test_a_plan_offer_puts_an_OFFERED_plan_on_the_book_and_never_an_agreed_one():
    # The 02-20 part payment is an evaluation date INSIDE the plan-offer step (still 36 days
    # overdue), so the desk re-reads the same step there and must not take it for a new one.
    never_paid = _consumer_with(
        "ACC-P", _event(LedgerEventType.BILL_DEBIT, "ACC-P", 100.0, ISSUE, 1),
        _event(LedgerEventType.PAYMENT_CREDIT, "ACC-P", 10.0, dt.date(2024, 2, 20), 1))
    never_paid.advance_collections_journey("ACC-P", dt.date(2024, 3, 1))
    (journey,) = never_paid.collections_journeys.journeys()
    stages = [s["stage"] for s in journey["stages"]]
    offered = journey["stages"][stages.index(ARRANGEMENT_OFFERED)]
    assert stages[stages.index(ARRANGEMENT_OFFERED) - 1] == PLAN_OFFER_STEP
    assert stages.count(ARRANGEMENT_OFFERED) == 1, "the same step re-read must not re-offer"
    assert offered["household_acceptance"] is None and offered["instalment_gbp"] is None
    assert offered["acceptance_gap"] == ARRANGEMENT_ACCEPTANCE_GAP
    book = never_paid.collections_journeys.arrangements
    (plan,) = book.plans_for_customer("ACC-P")
    assert plan.plan_id == offered["plan_id"] and plan.original_debt_gbp == 100.0
    assert plan.status == PaymentPlanStatus.OFFERED and book.active_plans() == []
    assert "arrangement" in UNREACHED_EXITS


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


def test_a_lawful_offer_walk_passes_the_order_check_and_an_offer_after_the_cure_is_refused():
    """The order table must ACCEPT the shape the desk writes (else a table refusing every offer
    passes the refusal cases above), and R10 must still fire on a step after the cure -- the
    offered arrangement included, since an offer to a household that has paid is a demand for
    money not owed."""
    lawful = _journey((MISSED_PAYMENT, "2024-01-16"), (PLAN_OFFER_STEP, "2024-02-12"),
                      (ARRANGEMENT_OFFERED, "2024-02-12"), ("final_notice", "2024-03-11"),
                      (CURED, "2024-03-20"), exit=CURED)
    assert_journey_order_lawful(lawful, Segment.RESIDENTIAL)
    owes = lambda acc, on: 100.0 if on < dt.date(2024, 2, 20) else 0.0  # noqa: E731
    after_its_cure = _journey((MISSED_PAYMENT, "2024-01-16"), (PLAN_OFFER_STEP, "2024-02-12"),
                              (CURED, "2024-02-20"), (ARRANGEMENT_OFFERED, "2024-02-21"))
    assert [f["stage"] for f in dunning_of_a_cleared_debt(after_its_cure, owes)] == [
        ARRANGEMENT_OFFERED]
    after_cure_ladder = _journey((MISSED_PAYMENT, "2024-01-16"), ("reminder", "2024-01-22"),
                                 (CURED, "2024-02-20"), ("final_notice", "2024-03-11"))
    with pytest.raises(DunningOfAClearedDebtError, match="final_notice"):
        refuse_dunning_of_a_cleared_debt(after_cure_ladder, owes)


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
    (((MISSED_PAYMENT, "2024-01-16"), ("reminder_2", "2024-01-29"),
      (ARRANGEMENT_OFFERED, "2024-01-29")), None, "an arrangement offered off the plan step"),
    (((MISSED_PAYMENT, "2024-01-16"), (ARRANGEMENT_OFFERED, "2024-01-16")),
     None, "an arrangement offered before any ladder step"),
    (((MISSED_PAYMENT, "2024-01-16"), (PLAN_OFFER_STEP, "2024-02-12"),
      ("final_notice", "2024-03-11")), None, "a plan-offer step that offered no plan"),
    (((MISSED_PAYMENT, "2024-01-16"), (PLAN_OFFER_STEP, "2024-02-12"),
      (ARRANGEMENT_OFFERED, "2024-02-12"), (PLAN_OFFER_STEP, "2024-02-13"),
      (ARRANGEMENT_OFFERED, "2024-02-13")), None, "the same step re-entered to re-offer"),
])
def test_the_order_check_refuses_an_unlawful_walk(stages, exit, why):
    with pytest.raises(UnlawfulJourneyOrderError):
        assert_journey_order_lawful(_journey(*stages, exit=exit), Segment.RESIDENTIAL)


#: A window holding every branch the controls below need: February's first misses are observable
#: on 2016-02-29, so a cure, a day-7 reminder, a cure with no reminder and a day-28 plan offer all
#: fall inside it. Measured 2016-10-04 at this end: 12 journeys, 5 cured (4 with no reminder),
#: 5 reminded, 5 arrangements offered. The old end (03-02) predates any day-7 reminder.
LIVE_WINDOW_END = "2016-05-31"


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


def test_a_live_run_reminds_nobody_before_day_seven_and_takes_both_sides_of_that_wait(
        live_journeys):
    """On every live residential journey: no ladder step before the cited first-reminder day.
    And the partition first -- at least one journey cured inside the wait (the rare branch the
    old day-0 trigger made unreachable: 0 of 305 cures on the 2017 run) and at least one
    reminded, so a trigger that never fires cannot pass by reminding nobody."""
    residential = [j for j in live_journeys if j["segment"] == Segment.RESIDENTIAL.value]
    ladder = {s.action for s in dunning_path(Segment.RESIDENTIAL)}
    cured_unreminded = [j for j in residential if j["exit"] == CURED
                        and not any(s["stage"] in ladder for s in j["stages"])]
    reminded = [j for j in residential if any(s["stage"] == "reminder" for s in j["stages"])]
    assert cured_unreminded and reminded, (len(cured_unreminded), len(reminded))
    early = [(j["account_id"], s["stage"], s["days_overdue"]) for j in residential
             for s in j["stages"] if s["stage"] in ladder
             and s["days_overdue"] < _cited_first_reminder_day()]
    assert early == []


def test_a_live_run_offers_arrangements_only_straight_after_the_plan_offer_step(live_journeys):
    offered = [(j, i) for j in live_journeys for i, s in enumerate(j["stages"])
               if s["stage"] == ARRANGEMENT_OFFERED]
    assert offered, "no live journey reached the plan offer -- the arrangement stage is unreached"
    for journey, i in offered:
        assert journey["stages"][i - 1]["stage"] == PLAN_OFFER_STEP
        assert journey["stages"][i]["household_acceptance"] is None
    assert all(j["exit"] in (CURED, None) for j in live_journeys), (
        "an exit other than cured/open was recorded with no world answer behind it")
