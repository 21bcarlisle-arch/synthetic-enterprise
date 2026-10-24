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

WHAT ENDS A JOURNEY. `cured` is reached from the company's own records: the overdue balance is
cleared on the ledger. `arrangement` is reached when the household AGREES an offered plan, a fact
the world answers through the seam. `prepayment` is reached when the world changes the meter on the
Consent offer the 90-day rung makes (W2_42). The other exits the atom names are listed in `UNREACHED_EXITS`
with the reason each cannot happen yet. A journey still open at the run's end carries `exit: None`
-- "we cannot tell how it ends" -- and is never coerced into an exit.

THE HOUSEHOLD ANSWERS THE OFFER, THROUGH THE SEAM. When the selector reaches the plan-offer step
the desk puts an offer on its `PaymentPlanBook`, asks `plan_offers.answer_plan_offer` (the
SimInterface), and records `arrangement_offered` straight after the step with the answer:
  * agreed -- the plan goes ACTIVE at the household's instalment, and the journey ends on the
    `arrangement` exit: the debt has left the dunning ladder for an agreed plan, which is also the
    line Ofgem draws between "in arrears" and "in debt";
  * declined, or no answer (`household_acceptance: None` with the WORLD's reason) -- the journey
    goes on exactly as the ledger dictates.
While a plan is ACTIVE no new journey opens on the account. Each instalment is read from the seam
once its date has passed, and a plan the company's own rule defaults (`payment_plan
._DEFAULT_THRESHOLD` misses) stops holding the account, so the next missed bill opens a new
journey: a broken plan sends the household back into collections.

PLAN CASH IS CASH. Each instalment the seam reports PAID is posted to the company ledger as an
ordinary received payment, through the consumer's own cash seam (`post_cash`), on the instalment's
due date and for the amount the plan book took. A domestic account is balance-based and ages FIFO
(`docs/market_research/account_hierarchy_payment_allocation.md` s1), so plan cash discharges the
oldest arrears first -- the debt the plan was agreed against -- with no matching to the plan needed.
A plan repaid in full therefore leaves the ledger showing that debt cleared, stops holding the
account, and only a bill missed since can open a new journey. A missed instalment posts nothing.

TODAY EVERY ANSWER IS None: no published rate of take-up or keeping exists
(`docs/market_research/domestic_repayment_plan_take_up_and_keep_rates.md`), so the world answers
None and names why. The agreed branch is reachable through an injected world only.

NAMED SIMPLIFICATIONS.
  (1) Value time, not knowledge time: the ledger's existing reads filter on `valid_time` only, so a
      payment the bank reported late is known on its value date. That is `collections_snapshot`'s
      reading and this desk inherits it rather than forking a second one.
  (2) A moratorium starting between two evaluation dates is seen at the next one. No Secretary of
      State notification crosses the seam yet (`PaymentObservationConsumer.__init__`), so no live
      account can enter `moratorium_hold`; the stage is reachable at unit level only.
  (3) A plan instalment is read at the next evaluation date on or after it falls due, not on the
      day, so a default is seen up to one ladder-trigger later than a daily batch would see it.
  (4) The plan's debt is fixed at the overdue sum on the offer date and is not re-stated when
      other payments land meanwhile. A household that also pays down the same arrears by its
      ordinary payments ends its plan with the ledger in credit; a real desk would re-state the plan.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from company.billing.account_ledger import AccountLedger, LedgerEventType
from company.billing.arrears_engine import MORATORIUM_HOLD, dunning_path
from company.billing.payment_plan import PaymentPlanBook, PaymentPlanStatus
from company.crm.account_hierarchy import AccountingModel, Segment, default_accounting_model

MISSED_PAYMENT = "missed_payment"
CURED = "cured"
#: The ladder step on which SLC 27.8 has the company offer an affordable arrangement.
PLAN_OFFER_STEP = "repayment_plan_offer"
#: The residential rung on which the company asks for a prepayment meter by Consent (W2_42), the offer
#: it records straight after, and the exit taken when the world changes the meter.
PREPAYMENT_STEP = "prepayment_or_debt_agency"
PREPAYMENT_OFFERED = "prepayment_offered"
PREPAYMENT = "prepayment"
#: Why a prepayment offer is recorded unanswered when the desk has no seam to ask.
PREPAYMENT_ANSWER_GAP = "this desk was built with no seam to ask, so no meter change can be requested"
#: The arrangement stage in the only state the company can reach alone: OFFERED. Entered on the
#: same date as `PLAN_OFFER_STEP` and only straight after it, with the offer kept in the desk's
#: `PaymentPlanBook`. The household's acceptance is not observed -- see ARRANGEMENT_ACCEPTANCE_GAP.
ARRANGEMENT_OFFERED = "arrangement_offered"
#: The exit taken when the household agrees an offered plan: the debt leaves the dunning ladder.
ARRANGEMENT = "arrangement"
#: Why an offered arrangement carries `household_acceptance: None` when the desk has no seam to ask.
#: With one, the reason recorded is the world's own.
ARRANGEMENT_ACCEPTANCE_GAP = (
    "this desk was built with no seam to ask, so no household answer to the offer reaches the "
    "company: neither the instalment it can afford (SLC 27.8) nor whether it agrees")


#: THE STEP AFTER THE OFFER (2026-10-24). Once a journey stands on the plan-offer rung or above it
#: (first: the last rung only; widened with `climbs_per_case`), each further bill that falls overdue
#: re-offers an affordable arrangement through the same door: every
#: missed bill is a fresh SLC 27.5 "reason to believe", so the 27.6 offer is owed again. Keyed to the
#: missed bill, never to an interval, because no published cadence exists (GAP A1).
#: `docs/market_research/company_debt_management.md`, "After the last rung".
PLAN_REOFFER_STEP = "repayment_plan_reoffer"
#: The one rule that writes off a LIVE account's debt: Limitation Act 1980 s.5, restarted by any
#: payment (s.29(5)). A bill is barred once it is six years past due AND nothing has been paid on the
#: account for six years. The exit is taken when the write-off leaves nothing overdue.
WRITE_OFF = "write_off"
STATUTE_BAR_YEARS = 6
STATUTE_BAR_RULE = "limitation_act_1980_s5_six_years_from_due_and_from_the_last_payment"


def climbs_per_case(segment: Segment) -> bool:
    """Whether this segment's rung never falls inside an open journey (2026-10-24). On a balance-based
    account FIFO payment makes the oldest bill younger, so a rung chosen from its age walks back down
    ("final notice, then second reminder"). The case keeps its highest rung until it cures.
    Open-item accounts are dunned invoice by invoice and are left as they were (GAP C2).
    `docs/market_research/company_debt_management.md`, "One case, one climb"."""
    return default_accounting_model(segment) == AccountingModel.BALANCE_BASED


def _reoffer_rungs(segment: Segment) -> frozenset:
    """The rungs on which a newly missed bill re-makes the SLC 27.6 offer: the plan-offer rung and
    every rung above it, once the offer has been made once in the case."""
    ladder = ladder_actions(segment)
    if PLAN_OFFER_STEP not in ladder:
        return frozenset()
    return frozenset(ladder[ladder.index(PLAN_OFFER_STEP):])


def _years_after(d: dt.date, years: int) -> dt.date:
    try:
        return d.replace(year=d.year + years)
    except ValueError:  # 29 Feb
        return d.replace(year=d.year + years, day=28)


def statute_barred_gbp(ledger: AccountLedger, on: dt.date, payment_terms_days: int = 14) -> float:
    """What this account owes on `on` that is statute-barred: the FIFO-unpaid bills due at least six
    years before `on`, and only if no payment has landed on the account in those six years. Read off
    the company's own ledger only."""
    from company.billing.arrears_engine import _fifo_unpaid
    events = ledger.events_through(on)
    bar = _years_after(on, -STATUTE_BAR_YEARS)
    paid = [e.valid_time for e in events if e.event_type == LedgerEventType.PAYMENT_CREDIT]
    if paid and max(paid) > bar:
        return 0.0
    return round(sum(g for billed, g in _fifo_unpaid(events)
                     if billed + dt.timedelta(days=payment_terms_days) <= bar), 2)


#: The exits the atom names that the company's own records cannot reach yet, and why. A journey is
#: never closed on one of these by inference.
UNREACHED_EXITS = {
    "arrangement": ("reachable when the world agrees an offer, and unreached live: the world answers "
                    "every offer None, because no published rate of plan take-up exists (simulation/"
                    "plan_offer_response.py)"),
    "disconnection_equivalent": ("no prepayment-under-warrant or agency hand-over is taken live; a "
                                 "meter changed by Consent is the separate `prepayment` exit"),
    "prepayment": ("reachable when the world changes the meter on a Consent offer, and unreached "
                   "live: the take-up share ships at 0, so the household cannot answer "
                   "(simulation/payment_method_dynamics.py)"),
}


def ladder_actions(segment: Segment) -> tuple:
    """The dunning actions of this segment's path, in trigger order."""
    return tuple(s.action for s in dunning_path(segment))


def lawful_successors(segment: Segment) -> Dict[Optional[str], frozenset]:
    """Which stage may follow which, for one segment. `None` is the journey's start.

    A journey opens on a missed payment; it then moves between ladder steps, into and out of a
    moratorium hold, and ends on a cure. On an open-item segment a step may go DOWN as well as up (a
    payment that clears the oldest invoice re-ages from a younger one); on a balance-based segment
    the order check refuses a fall (`climbs_per_case`), which this pairwise table cannot express. Nothing follows a cure: a later miss opens a NEW
    journey, so a cured account is never dunned inside the journey that recorded its cure.

    The offered arrangement follows the plan-offer step and nothing else, and is followed by what
    could have followed that step -- the journey resumes on the ladder, holds, or cures -- or by
    the `arrangement` exit when the household agrees. Nothing follows that exit."""
    ladder = frozenset(ladder_actions(segment))
    working = ladder | {MORATORIUM_HOLD.action, CURED}
    table: Dict[Optional[str], frozenset] = {None: frozenset({MISSED_PAYMENT}),
                                             MISSED_PAYMENT: working, CURED: frozenset()}
    for stage in ladder | {MORATORIUM_HOLD.action}:
        table[stage] = working - {stage}
    if PLAN_OFFER_STEP in ladder:
        table[PLAN_OFFER_STEP] = table[PLAN_OFFER_STEP] | {ARRANGEMENT_OFFERED}
        table[ARRANGEMENT_OFFERED] = (working - {PLAN_OFFER_STEP}) | {ARRANGEMENT}
        table[ARRANGEMENT] = frozenset()
    if PREPAYMENT_STEP in ladder:
        table[PREPAYMENT_STEP] = table[PREPAYMENT_STEP] | {PREPAYMENT_OFFERED}
        table[PREPAYMENT_OFFERED] = (working - {PREPAYMENT_STEP}) | {PREPAYMENT}
        table[PREPAYMENT] = frozenset()
    if PLAN_OFFER_STEP in ladder:
        # The re-offer follows any rung from the plan offer up, the offer such a rung made, or an
        # earlier re-offer's offer, and is followed by the offer it made.
        rungs = _reoffer_rungs(segment)
        for before in rungs | {ARRANGEMENT_OFFERED} | (
                {PREPAYMENT_OFFERED} if PREPAYMENT_STEP in rungs else frozenset()):
            table[before] = table[before] | {PLAN_REOFFER_STEP}
        table[PLAN_REOFFER_STEP] = frozenset({ARRANGEMENT_OFFERED})
    # A write-off may follow any open stage. When debt younger than the bar is still owed, the
    # journey goes on from it (to the ladder, or to another write-off a year on); otherwise it is
    # the exit, and the exit is the last stage.
    for stage in list(table):
        if stage not in (None, CURED, ARRANGEMENT, PREPAYMENT, PLAN_REOFFER_STEP):
            table[stage] = table[stage] | {WRITE_OFF}
    table[WRITE_OFF] = working | {WRITE_OFF} | (
        {PLAN_REOFFER_STEP} if PLAN_OFFER_STEP in ladder else frozenset())
    return table


class UnlawfulJourneyOrderError(Exception):
    """A journey's stages are not a walk the collections road allows."""


def assert_journey_order_lawful(journey: dict, segment: Segment) -> None:
    """R15 CONTROL -- every stage of `journey` is a lawful successor of the one before it, dates
    never run backwards, an exit is the last stage, and every plan-offer step is followed by the
    offer it made (a step that SAYS a plan was offered with no offer on the book is the SLC 27.8
    failure this stage exists to rule out). FAIL-CLOSED on an empty journey: a journey with no
    stages is not a journey that took no wrong turn."""
    stages = journey.get("stages") or []
    if not stages:
        raise UnlawfulJourneyOrderError(f"{journey.get('account_id')}: a journey with no stages")
    table = lawful_successors(segment)
    for s, following in zip(stages, list(stages[1:]) + [None]):
        if s["stage"] == PLAN_OFFER_STEP and (
                following is None or following["stage"] != ARRANGEMENT_OFFERED):
            raise UnlawfulJourneyOrderError(
                f"{journey.get('account_id')}: {PLAN_OFFER_STEP} on {s['on']} with no "
                f"{ARRANGEMENT_OFFERED} recorded after it")
        if s["stage"] == PLAN_REOFFER_STEP and (
                following is None or following["stage"] != ARRANGEMENT_OFFERED):
            raise UnlawfulJourneyOrderError(
                f"{journey.get('account_id')}: {PLAN_REOFFER_STEP} on {s['on']} with no "
                f"{ARRANGEMENT_OFFERED} recorded after it")
        if s["stage"] == PREPAYMENT_STEP and (
                following is None or following["stage"] != PREPAYMENT_OFFERED):
            raise UnlawfulJourneyOrderError(
                f"{journey.get('account_id')}: {PREPAYMENT_STEP} on {s['on']} with no "
                f"{PREPAYMENT_OFFERED} recorded after it")
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
    if climbs_per_case(segment):
        ladder, highest = ladder_actions(segment), -1
        for s in stages:
            if s["stage"] not in ladder:
                continue
            if ladder.index(s["stage"]) < highest:
                raise UnlawfulJourneyOrderError(
                    f"{journey['account_id']}: {s['stage']!r} on {s['on']} walks back down from "
                    f"{ladder[highest]!r} inside one open case")
            highest = ladder.index(s["stage"])
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
    def current_step(self) -> Optional[str]:
        """The stage the SELECTOR last put this journey in. An offered arrangement is recorded
        beside its plan-offer step, not instead of it, so it is skipped: reading it as the current
        step would make the next read of the same step look like a new one, and re-offer daily."""
        steps = [s["stage"] for s in self.stages
                 if s["stage"] not in (ARRANGEMENT_OFFERED, PREPAYMENT_OFFERED, PLAN_REOFFER_STEP,
                                       WRITE_OFF)]
        return steps[-1] if steps else None

    @property
    def highest_rung(self) -> Optional[str]:
        """The highest ladder rung this journey has entered, or None before the first."""
        ladder = ladder_actions(self.segment)
        reached = [ladder.index(s["stage"]) for s in self.stages if s["stage"] in ladder]
        return ladder[max(reached)] if reached else None

    def enter(self, stage: str, on: dt.date, decision: str, view: dict, **extra) -> None:
        self.stages.append({
            "stage": stage,
            "on": on.isoformat(),
            "decision": decision,
            "overdue_gbp": view.get("undisputed_overdue_gbp"),
            "days_overdue": view.get("max_days_overdue"),
            **extra,
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
                 refuse_dunning_of_cleared_debt: Callable[[dict, str], None],
                 plan_offers: Optional[Any] = None,
                 post_cash: Optional[Callable[[str, float, dt.date, str], None]] = None,
                 post_write_off: Optional[Callable[[str, float, dt.date, str], None]] = None
                 ) -> None:
        if plan_offers is not None and post_cash is None:
            raise ValueError(
                "a desk that can agree plans needs the cash seam to post their instalments: "
                "without it a repaid plan's debt would still read overdue and be dunned")
        self._view_at = view_at
        self._refuse = refuse_dunning_of_cleared_debt
        #: The seam a plan offer is answered through (`SimInterface.answer_plan_offer` and
        #: `get_plan_instalments`). None: offers are recorded unanswered, ARRANGEMENT_ACCEPTANCE_GAP.
        self._plan_offers = plan_offers
        #: `post_cash(account_id, amount_gbp, value_date, reference)`: the consumer's received-cash
        #: seam, idempotent on `reference`. Every paid plan instalment goes through it.
        self._post_cash = post_cash
        #: `post_write_off(account_id, amount_gbp, on, note)`: posts a STATUTE_BARRED write-off to the
        #: company ledger. None: a barred debt is still recorded as a `write_off` stage, unposted.
        self._post_write_off = post_write_off
        #: Every arrangement this desk has offered, and what became of each.
        self.arrangements = PaymentPlanBook()
        self._instalments_read: Dict[int, int] = {}
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
        missed = {d + dt.timedelta(days=1) for d in bill_dues}
        openers = missed | {
            e.valid_time for e in events
            if e.event_type.is_debit and e.event_type != LedgerEventType.BILL_DEBIT}
        # A bar can only fall six years after a due date or after a payment.
        bars = {_years_after(e.valid_time, STATUTE_BAR_YEARS) for e in events
                if e.event_type == LedgerEventType.PAYMENT_CREDIT} | {
            _years_after(d, STATUTE_BAR_YEARS) for d in bill_dues}
        movers = openers | bars | {e.valid_time for e in events} | {
            d + dt.timedelta(days=t) for d in bill_dues for t in triggers}

        def _in_window(d: dt.date) -> bool:
            return (after is None or d > after) and d <= through

        for on in sorted(d for d in movers if _in_window(d)):
            if account_id not in self._open and on not in openers:
                continue
            self._step(account_id, segment, on, ledger=ledger, bill_missed=on in missed,
                       payment_terms_days=payment_terms_days)
        self._through[account_id] = through

    def _step(self, account_id: str, segment: Segment, on: dt.date, *,
              ledger: Optional[AccountLedger] = None, bill_missed: bool = False,
              payment_terms_days: int = 14) -> None:
        held_by_plan = self._read_instalments(account_id, on)
        view = self._view_at(account_id, segment, on)
        overdue = (view.get("max_days_overdue") or 0) > 0 and (
            view.get("undisputed_overdue_gbp") or 0.0) > 0
        journey = self._open.get(account_id)
        if journey is None:
            if not overdue or held_by_plan:
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
        if ledger is not None and self._write_off_if_barred(journey, ledger, on, view,
                                                            payment_terms_days):
            return
        action = view.get("dunning_action")
        ladder = ladder_actions(segment)
        highest = journey.highest_rung
        # No rung at all is a fall too: once FIFO has cleared every older bill, the bill just missed
        # is a day overdue and below the first trigger, yet the case is still open.
        if (climbs_per_case(segment) and highest is not None
                and (action is None or (action in ladder
                                        and ladder.index(action) < ladder.index(highest)))):
            action = highest
        if action is not None and action != journey.current_step:
            journey.enter(action, on, f"{action} by {view.get('dunning_channel')}", view)
            if action == PLAN_OFFER_STEP:
                self._offer_arrangement(journey, on, view)
            elif action == PREPAYMENT_STEP:
                self._offer_prepayment(journey, on, view)
        elif (bill_missed and action is not None and action == journey.current_step
              and action in _reoffer_rungs(segment)):
            journey.enter(PLAN_REOFFER_STEP, on,
                          "a further bill missed once the plan was offered: the SLC 27.6 offer again",
                          view)
            self._offer_arrangement(journey, on, view)
        self._refuse(journey.as_record(), account_id)
        if journey.exit in (ARRANGEMENT, PREPAYMENT):
            self._closed.append(self._open.pop(account_id))

    def _write_off_if_barred(self, journey: _Journey, ledger: AccountLedger, on: dt.date,
                             view: dict, payment_terms_days: int) -> bool:
        """Write off, on the company ledger, what the statute bar covers. Bills younger than the bar
        stay owed and the journey goes on; it ends on the `write_off` exit only when nothing is left
        overdue. Returns whether it ended. A desk with no ledger seam writes nothing off."""
        if self._post_write_off is None:
            return False
        barred = statute_barred_gbp(ledger, on, payment_terms_days)
        if barred <= 0.005:
            return False
        self._post_write_off(journey.account_id, barred, on, STATUTE_BAR_RULE)
        journey.enter(WRITE_OFF, on, f"written off by rule {STATUTE_BAR_RULE}", view,
                      written_off_gbp=barred, rule=STATUTE_BAR_RULE)
        after = self._view_at(journey.account_id, journey.segment, on)
        if (after.get("max_days_overdue") or 0) > 0 and (after.get("undisputed_overdue_gbp") or 0) > 0:
            return False
        journey.exit = WRITE_OFF
        self._closed.append(self._open.pop(journey.account_id))
        return True

    def _read_instalments(self, account_id: str, on: dt.date) -> bool:
        """Post every instalment of this account's ACTIVE plans that fell due by `on` to the plan
        book, each once, and each PAID one to the ledger as cash. Returns whether an ACTIVE plan
        still holds the account."""
        held = False
        for plan in self.arrangements.plans_for_customer(account_id):
            if plan.status != PaymentPlanStatus.ACTIVE:
                continue
            due = self._plan_offers.get_plan_instalments(account_id, plan.start_date, on)
            already = self._instalments_read.get(plan.plan_id, 0)
            for n, instalment in enumerate(due[already:], already + 1):
                if instalment["paid"]:
                    paid_on = dt.date.fromisoformat(instalment["due"])
                    before = plan.total_paid_gbp
                    self.arrangements.record_payment(plan.plan_id, paid_on)
                    self._post_cash(account_id, round(plan.total_paid_gbp - before, 2), paid_on,
                                    f"plan:{account_id}:{plan.plan_id}:{n}")
                else:
                    self.arrangements.record_missed(plan.plan_id)
                if plan.status != PaymentPlanStatus.ACTIVE:
                    break
            self._instalments_read[plan.plan_id] = len(due)
            held = held or plan.status == PaymentPlanStatus.ACTIVE
        return held

    def _offer_arrangement(self, journey: _Journey, on: dt.date, view: dict) -> None:
        """SLC 27.8: the plan-offer step makes an offer, and the offer goes on the plan book.

        What the company knows here is what it did: the date, the overdue sum it offered against,
        the plan id. The instalment and the household's answer are carried as None with the reason
        -- they are the household's, and nothing brings them back across the wall today."""
        debt = view.get("undisputed_overdue_gbp") or 0.0
        plan = self.arrangements.offer_plan(journey.account_id, debt, on)
        if self._plan_offers is None:
            answer = {"accepted": None, "instalment": None,
                      "reason": ARRANGEMENT_ACCEPTANCE_GAP}
        else:
            answer = self._plan_offers.answer_plan_offer(journey.account_id, on, debt)
        accepted = answer["accepted"]
        journey.enter(ARRANGEMENT_OFFERED, on, "affordable arrangement offered (SLC 27.8)", view,
                      plan_id=plan.plan_id, instalment_gbp=answer["instalment"],
                      household_acceptance=accepted,
                      acceptance_gap=answer["reason"] if accepted is None else None)
        if accepted is True:
            self.arrangements.accept_offer(plan.plan_id, answer["instalment"])
            journey.enter(ARRANGEMENT, on, answer["reason"], view, plan_id=plan.plan_id)
            journey.exit = ARRANGEMENT
        elif accepted is False:
            self.arrangements.cancel_plan(plan.plan_id)

    def _offer_prepayment(self, journey: _Journey, on: dt.date, view: dict) -> None:
        """W2_42: the 90-day rung asks for a prepayment meter by the household's explicit Consent
        (SLC 28.22), never involuntarily, and records the world's answer. A changed meter ends the
        journey on the `prepayment` exit. Life on the meter (debt recovered from top-ups) is not
        built: `company_debt_management.md`, "What reaches it"."""
        debt = view.get("undisputed_overdue_gbp") or 0.0
        days = view.get("max_days_overdue") or 0
        if self._plan_offers is None:
            answer = {"moved": False, "reason": PREPAYMENT_ANSWER_GAP}
        else:
            answer = self._plan_offers.request_prepayment_move(
                journey.account_id, on.isoformat(), debt, days // 30)
        journey.enter(PREPAYMENT_OFFERED, on, "prepayment meter offered by Consent (SLC 28.22)",
                      view, meter_moved=answer["moved"], move_reason=answer["reason"])
        if answer["moved"]:
            journey.enter(PREPAYMENT, on, answer["reason"], view)
            journey.exit = PREPAYMENT

    def journeys(self) -> List[dict]:
        """Every journey this desk has recorded, closed first then open, as plain records."""
        return [j.as_record() for j in self._closed] + [
            self._open[a].as_record() for a in sorted(self._open)]
