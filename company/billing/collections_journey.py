"""The collections journey: debt as a dated road per account, not a balance (atom EP4).

WHAT THIS ADDS AND WHAT IT DOES NOT. Before this module the company already chose a dunning step
on every collections read (`arrears_engine.collections_snapshot`, live since e0370bf94) -- but only
as a READ, taken at a renewal to feed the churn and pricing beliefs, and thrown away. Nothing kept
the step, its date, or what happened next, so no run could say "this account was reminded on the
1st, sent a final notice on the 26th and paid on the 30th". This desk keeps that record. It decides
nothing new: every step is the one `collections_snapshot` selects, Breathing Space hold included.

WHEN THE DESK LOOKS. A real supplier runs its collections batch daily. Stepping every account every
day is the honest cadence and too slow for a ten-year book, so the desk evaluates only on the dates
the ladder CAN change -- which, for a ledger-driven selector, are fully enumerable from the ledger:

  * every ledger event's value date (a payment landing can cure; a reversal can reopen);
  * every bill's due date plus each trigger of the segment's dunning path (a trigger crossing is
    the only way a step advances), with the day-0 trigger read as due + 1, because the due date is
    the last day to pay and the journey opens on a MISSED payment, not on one still in time.

Between two such dates the selector's inputs do not move, so nothing is lost. An account with no
open journey is evaluated only where it could open one (each bill's due + 1, and any non-bill debit).

WHAT ENDS A JOURNEY. Only `cured` is reachable from the company's own records today: the overdue
balance is cleared on the ledger. The other exits the atom names are listed in `UNREACHED_EXITS`
with the reason each cannot happen yet. A journey still open at the run's end carries `exit: None`
-- "we cannot tell how it ends" -- and is never coerced into an exit.

NAMED SIMPLIFICATIONS.
  (1) Value time, not knowledge time: the ledger's existing reads filter on `valid_time` only, so a
      payment the bank reported late is known on its value date. That is `collections_snapshot`'s
      reading and this desk inherits it rather than forking a second one.
  (2) A moratorium starting between two evaluation dates is seen at the next one. No Secretary of
      State notification crosses the seam yet (`PaymentObservationConsumer.__init__`), so no live
      account can enter `moratorium_hold`; the stage is reachable at unit level only.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from company.billing.account_ledger import AccountLedger, LedgerEventType
from company.billing.arrears_engine import MORATORIUM_HOLD, dunning_path
from company.crm.account_hierarchy import Segment

MISSED_PAYMENT = "missed_payment"
CURED = "cured"

#: The exits the atom names that the company's own records cannot reach yet, and why. A journey is
#: never closed on one of these by inference.
UNREACHED_EXITS = {
    "arrangement": "company/billing/payment_plan.py has no production caller; no plan is offered",
    "disconnection_equivalent": "no prepayment-under-warrant or agency hand-over is taken live",
    "write_off": "arrears_engine.build_write_off_event has no production caller",
}


def ladder_actions(segment: Segment) -> tuple:
    """The dunning actions of this segment's path, in trigger order."""
    return tuple(s.action for s in dunning_path(segment))


def lawful_successors(segment: Segment) -> Dict[Optional[str], frozenset]:
    """Which stage may follow which, for one segment. `None` is the journey's start.

    A journey opens on a missed payment; it then moves between ladder steps (DOWN as well as up: a
    part-payment that clears the oldest bill re-ages the balance from a younger one), into and out
    of a moratorium hold, and ends on a cure. Nothing follows a cure: a later miss opens a NEW
    journey, so a cured account is never dunned inside the journey that recorded its cure."""
    ladder = frozenset(ladder_actions(segment))
    working = ladder | {MORATORIUM_HOLD.action, CURED}
    table: Dict[Optional[str], frozenset] = {None: frozenset({MISSED_PAYMENT}),
                                             MISSED_PAYMENT: working, CURED: frozenset()}
    for stage in ladder | {MORATORIUM_HOLD.action}:
        table[stage] = working - {stage}
    return table


class UnlawfulJourneyOrderError(Exception):
    """A journey's stages are not a walk the collections road allows."""


def assert_journey_order_lawful(journey: dict, segment: Segment) -> None:
    """R15 CONTROL -- every stage of `journey` is a lawful successor of the one before it, dates
    never run backwards, and an exit is the last stage. FAIL-CLOSED on an empty journey: a journey
    with no stages is not a journey that took no wrong turn."""
    stages = journey.get("stages") or []
    if not stages:
        raise UnlawfulJourneyOrderError(f"{journey.get('account_id')}: a journey with no stages")
    table = lawful_successors(segment)
    previous, previous_on = None, None
    for s in stages:
        if s["stage"] not in table.get(previous, frozenset()):
            raise UnlawfulJourneyOrderError(
                f"{journey['account_id']}: {s['stage']!r} cannot follow {previous!r}")
        if previous_on is not None and s["on"] < previous_on:
            raise UnlawfulJourneyOrderError(
                f"{journey['account_id']}: {s['stage']!r} on {s['on']} is dated before "
                f"{previous!r} on {previous_on}")
        previous, previous_on = s["stage"], s["on"]
    if journey.get("exit") is not None and journey["exit"] != previous:
        raise UnlawfulJourneyOrderError(
            f"{journey['account_id']}: exit {journey['exit']!r} is not its last stage {previous!r}")


@dataclass
class _Journey:
    account_id: str
    segment: Segment
    stages: List[dict] = field(default_factory=list)
    exit: Optional[str] = None

    @property
    def current(self) -> Optional[str]:
        return self.stages[-1]["stage"] if self.stages else None

    def enter(self, stage: str, on: dt.date, decision: str, view: dict) -> None:
        self.stages.append({
            "stage": stage,
            "on": on.isoformat(),
            "decision": decision,
            "overdue_gbp": view.get("undisputed_overdue_gbp"),
            "days_overdue": view.get("max_days_overdue"),
        })

    def as_record(self) -> dict:
        return {"account_id": self.account_id, "segment": self.segment.value,
                "stages": list(self.stages), "exit": self.exit}


class CollectionsJourneyDesk:
    """Per-account collections journeys, advanced on the company's own ledger.

    `view_at(account_id, segment, as_of)` is the company's collections view -- in a run, the
    consumer's own `collections_snapshot` read, with the Breathing Space register asked. The desk
    is handed it rather than building one so there is ONE collections view in the company.

    `refuse_dunning_of_cleared_debt(journey_record, account_id)` is the R10 obligation check, run
    on every journey each time a stage is entered (domain_invariants
    `DUNNING_REQUIRES_AN_UNCLEARED_DEBT`). It RAISES: dunning a household whose ledger shows the
    debt cleared is a real-world harm, and a run that did it must not report a result.
    """

    def __init__(self, view_at: Callable[[str, Segment, dt.date], dict],
                 refuse_dunning_of_cleared_debt: Callable[[dict, str], None]) -> None:
        self._view_at = view_at
        self._refuse = refuse_dunning_of_cleared_debt
        self._open: Dict[str, _Journey] = {}
        self._closed: List[_Journey] = []
        self._through: Dict[str, dt.date] = {}

    def advance(self, ledger: AccountLedger, segment: Segment, through: dt.date,
                payment_terms_days: int = 14) -> None:
        """Walk this account's journey forward to `through`, inclusive, on every date its ladder
        could have changed since the last call. The caller guarantees the ledger is complete for
        value dates up to `through`."""
        account_id = ledger.account_id
        after = self._through.get(account_id)
        if after is not None and through <= after:
            return
        triggers = sorted({max(s.trigger_days_overdue, 1) for s in dunning_path(segment)})
        events = ledger.events()
        bill_dues = [e.valid_time + dt.timedelta(days=payment_terms_days)
                     for e in events if e.event_type == LedgerEventType.BILL_DEBIT]
        openers = {d + dt.timedelta(days=1) for d in bill_dues} | {
            e.valid_time for e in events
            if e.event_type.is_debit and e.event_type != LedgerEventType.BILL_DEBIT}
        movers = openers | {e.valid_time for e in events} | {
            d + dt.timedelta(days=t) for d in bill_dues for t in triggers}

        def _in_window(d: dt.date) -> bool:
            return (after is None or d > after) and d <= through

        for on in sorted(d for d in movers if _in_window(d)):
            if account_id not in self._open and on not in openers:
                continue
            self._step(account_id, segment, on)
        self._through[account_id] = through

    def _step(self, account_id: str, segment: Segment, on: dt.date) -> None:
        view = self._view_at(account_id, segment, on)
        overdue = (view.get("max_days_overdue") or 0) > 0 and (
            view.get("undisputed_overdue_gbp") or 0.0) > 0
        journey = self._open.get(account_id)
        if journey is None:
            if not overdue:
                return
            journey = self._open[account_id] = _Journey(account_id, segment)
            journey.enter(MISSED_PAYMENT, on, "journey opened: a bill is unpaid past its due date",
                          view)
        elif not overdue:
            journey.enter(CURED, on, "overdue balance cleared on the ledger", view)
            journey.exit = CURED
            self._refuse(journey.as_record(), account_id)
            self._closed.append(self._open.pop(account_id))
            return
        action = view.get("dunning_action")
        if action is not None and action != journey.current:
            journey.enter(action, on, f"{action} by {view.get('dunning_channel')}", view)
        self._refuse(journey.as_record(), account_id)

    def journeys(self) -> List[dict]:
        """Every journey this desk has recorded, closed first then open, as plain records."""
        return [j.as_record() for j in self._closed] + [
            self._open[a].as_record() for a in sorted(self._open)]
