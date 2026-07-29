"""Account closure process: final bill, deposit, debt referral under Ofgem SLC 21B.

W2_12 (2026-07-29) added the OBSERVATION side of the change-of-tenancy credit-risk
exit. Before this, `DEBT_REFERRED` was a status the company could set but nothing
ever decided: no mechanism answered "did this final bill actually get paid?".

That decision is not ours to make. Whether a departing occupant pays is a function
of their true tenure, payment channel, affordability and traceability — simulation
ground truth that no real UK supplier can read. It is decided on the WORLD side
(`simulation/final_bill_outcome.py`) and arrives here as an OUTCOME EVENT: paid /
paid late / partially paid / unpaid, plus the money and whether post came back
"gone away" (which a real supplier genuinely does observe). We never see the
probability, and never the archetype behind it.

`assert_observable_final_bill_event()` enforces that split fail-CLOSED on every
inbound event, with a strict ALLOWLIST of keys — a denylist would fail open the
moment the world side grew a new hidden field.

C-S3: the outcome arrives LATER than the closure (Ofgem SLC 21B's 42-day final
bill window plus a 28-day payment window). `awaiting_final_bill_outcome()` is the
company's queue of exits whose answer has not come back yet — that pending state
is real, not a modelling gap.
"""
from __future__ import annotations

import datetime as dt
import math
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class ClosureReason(str, Enum):
    CUSTOMER_SWITCH = "customer_switch"       # gained by another supplier
    VACANT_PROPERTY = "vacant_property"       # no new occupant yet
    CUSTOMER_DECEASED = "customer_deceased"   # estate settlement
    BUSINESS_CLOSURE = "business_closure"     # SME ceased trading
    CHANGE_OF_TENANCY = "change_of_tenancy"   # occupant moved out, property re-let/sold


class ClosureStatus(str, Enum):
    INITIATED = "initiated"
    FINAL_READ_RECEIVED = "final_read_received"
    FINAL_BILL_ISSUED = "final_bill_issued"
    DEPOSIT_RETURNED = "deposit_returned"     # net_balance <= 0: owe customer money
    DEPOSIT_APPLIED = "deposit_applied"       # net_balance > 0: deposit offset debt
    DEBT_REFERRED = "debt_referred"           # outstanding balance sent to collections
    CLOSED = "closed"


_FINAL_BILL_DEADLINE_DAYS = 42  # Ofgem SLC 21B: 6 weeks
_FINAL_BILL_PAYMENT_WINDOW_DAYS = 28  # matches company/billing/cot.py::_OVERDUE_DAYS


class FinalBillOutcome(str, Enum):
    """What the company OBSERVES happened to a closing account's final bill.

    These five values mirror `simulation.final_bill_outcome.FinalBillOutcome`
    by VALUE, deliberately without importing it — the wall is crossed by a
    typed message, not by a shared object (`typed-flow seam preference`,
    CLAUDE.md). A mismatch surfaces as a rejected event, not a silent coupling.
    """

    CREDIT_DUE = "credit_due"
    PAID_ON_TIME = "paid_on_time"
    PAID_LATE = "paid_late"
    PARTIALLY_PAID = "partially_paid"
    UNPAID = "unpaid"

    @property
    def is_shortfall(self) -> bool:
        return self in (FinalBillOutcome.PARTIALLY_PAID, FinalBillOutcome.UNPAID)


# The COMPLETE set of fields a real supplier can see about a closed account's
# final bill. This is an ALLOWLIST on purpose: a denylist of "forbidden" fields
# would fail open the instant the world side grew a new hidden attribute.
_OBSERVABLE_FINAL_BILL_KEYS = frozenset({
    "schema", "account_id", "supply_point_id", "fuel", "resolved_on",
    "outcome", "billed_gbp", "recovered_gbp", "gone_away", "days_late",
})
_REQUIRED_FINAL_BILL_KEYS = frozenset({
    "account_id", "resolved_on", "outcome", "billed_gbp", "recovered_gbp",
})


class EpistemicWallBreach(ValueError):
    """A final-bill event carried something a real supplier could not observe."""


def assert_observable_final_bill_event(event: dict) -> dict:
    """Fail CLOSED on any final-bill event that is not purely observable.

    Rejects, in this order:
      1. a non-dict / empty payload (a missing check is a FAILED check, never a
         pass — R15 fail-open pattern);
      2. any key outside `_OBSERVABLE_FINAL_BILL_KEYS` — this is what catches a
         leaked `gone_away_probability`, `debt_archetype`, tenure, payment
         channel or fuel-poverty flag;
      3. a missing required key;
      4. a non-finite or negative money figure (NaN/inf compare False against
         every bound, so they are rejected BEFORE any comparison — R15
         NaN-blind-guard pattern);
      5. an `outcome` outside `FinalBillOutcome`.

    Returns the event unchanged on success so it can be used inline.
    """
    if not isinstance(event, dict) or not event:
        raise EpistemicWallBreach("final-bill event missing or not a mapping")

    leaked = set(event) - _OBSERVABLE_FINAL_BILL_KEYS
    if leaked:
        raise EpistemicWallBreach(
            "final-bill event carries non-observable field(s): "
            + ", ".join(sorted(leaked))
        )

    missing = _REQUIRED_FINAL_BILL_KEYS - set(event)
    if missing:
        raise EpistemicWallBreach(
            "final-bill event missing required field(s): " + ", ".join(sorted(missing))
        )

    for money_key in ("billed_gbp", "recovered_gbp"):
        value = event[money_key]
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise EpistemicWallBreach(money_key + " is not numeric")
        if not math.isfinite(float(value)) or float(value) < 0:
            raise EpistemicWallBreach(money_key + " is not a finite, non-negative amount")

    try:
        FinalBillOutcome(event["outcome"])
    except ValueError:
        raise EpistemicWallBreach("unknown final-bill outcome: " + repr(event["outcome"]))

    return event


@dataclass(frozen=True)
class FinalBillPaymentEvent:
    """The company's own typed record of an observed final-bill outcome."""

    account_id: str
    outcome: FinalBillOutcome
    resolved_on: dt.date
    billed_gbp: float
    recovered_gbp: float
    gone_away: bool = False
    days_late: int = 0

    @property
    def shortfall_gbp(self) -> float:
        return round(max(0.0, self.billed_gbp - self.recovered_gbp), 2)

    @classmethod
    def from_observation(cls, event: dict) -> "FinalBillPaymentEvent":
        """Build from a world-side observable event, wall-guard first."""
        assert_observable_final_bill_event(event)
        return cls(
            account_id=event["account_id"],
            outcome=FinalBillOutcome(event["outcome"]),
            resolved_on=dt.date.fromisoformat(event["resolved_on"]),
            billed_gbp=float(event["billed_gbp"]),
            recovered_gbp=float(event["recovered_gbp"]),
            gone_away=bool(event.get("gone_away", False)),
            days_late=int(event.get("days_late", 0)),
        )


@dataclass(frozen=True)
class AccountClosure:
    account_id: str
    supply_point_id: str
    closure_date: dt.date
    reason: ClosureReason
    status: ClosureStatus
    deposit_held_gbp: float
    debt_balance_gbp: float
    final_read_kwh: Optional[float] = None
    final_bill_gbp: Optional[float] = None
    # --- observed later (C-S3); None means "we do not know yet", not "paid".
    final_bill_outcome: Optional[FinalBillOutcome] = None
    final_bill_resolved_on: Optional[dt.date] = None
    final_bill_recovered_gbp: Optional[float] = None
    gone_away: bool = False

    @property
    def net_balance_gbp(self) -> float:
        bill = self.final_bill_gbp or 0.0
        return round(bill + self.debt_balance_gbp - self.deposit_held_gbp, 2)

    @property
    def requires_debt_referral(self) -> bool:
        return (
            self.net_balance_gbp > 0
            and self.status not in (ClosureStatus.DEBT_REFERRED, ClosureStatus.CLOSED)
        )

    def days_since_closure(self, as_of: dt.date) -> int:
        return (as_of - self.closure_date).days

    def is_final_bill_overdue(self, as_of: dt.date) -> bool:
        return (
            self.final_bill_gbp is None
            and self.days_since_closure(as_of) > _FINAL_BILL_DEADLINE_DAYS
        )

    @property
    def final_bill_outcome_due(self) -> dt.date:
        """Earliest date the paid-or-not question can be answered (C-S3): the
        SLC 21B six-week final-bill window plus the 28-day payment window."""
        return self.closure_date + dt.timedelta(
            days=_FINAL_BILL_DEADLINE_DAYS + _FINAL_BILL_PAYMENT_WINDOW_DAYS
        )

    def is_awaiting_final_bill_outcome(self, as_of: dt.date) -> bool:
        """True while the exit is exposed but unanswered. Note this stays True
        PAST the due date — an answer that has not arrived is not an answer."""
        return self.final_bill_outcome is None and self.net_balance_gbp > 0

    @property
    def final_bill_shortfall_gbp(self) -> float:
        """Money billed at the exit and not recovered. 0.0 while unresolved —
        callers wanting "unknown" must check `final_bill_outcome is None`."""
        if self.final_bill_outcome is None:
            return 0.0
        recovered = self.final_bill_recovered_gbp or 0.0
        return round(max(0.0, max(0.0, self.net_balance_gbp) - recovered), 2)


def _update(record: AccountClosure, **kwargs) -> AccountClosure:
    fields = {
        "account_id": record.account_id,
        "supply_point_id": record.supply_point_id,
        "closure_date": record.closure_date,
        "reason": record.reason,
        "status": record.status,
        "deposit_held_gbp": record.deposit_held_gbp,
        "debt_balance_gbp": record.debt_balance_gbp,
        "final_read_kwh": record.final_read_kwh,
        "final_bill_gbp": record.final_bill_gbp,
        "final_bill_outcome": record.final_bill_outcome,
        "final_bill_resolved_on": record.final_bill_resolved_on,
        "final_bill_recovered_gbp": record.final_bill_recovered_gbp,
        "gone_away": record.gone_away,
    }
    fields.update(kwargs)
    return AccountClosure(**fields)


class AccountClosureBook:
    """Manages account closure pipeline: switch/vacancy through to settled or debt-referred.

    Real calibration:
    - Ofgem target: final bill within 42 days of supply end (SLC 21B)
    - Final bill delays were #1 switch complaint category in 2022 Ofgem survey
    - Deposit return mandatory within 14 days of final bill (SLC 12)
    - ~8-12% of closures have a net debt balance at final bill
    - Vacant properties: standing charge continues until de-energised or new supplier
    """

    def __init__(self) -> None:
        self._records: Dict[str, AccountClosure] = {}

    def initiate(
        self,
        account_id: str,
        supply_point_id: str,
        reason: ClosureReason,
        closure_date: dt.date,
        deposit_held_gbp: float = 0.0,
        debt_balance_gbp: float = 0.0,
    ) -> AccountClosure:
        record = AccountClosure(
            account_id=account_id,
            supply_point_id=supply_point_id,
            closure_date=closure_date,
            reason=reason,
            status=ClosureStatus.INITIATED,
            deposit_held_gbp=deposit_held_gbp,
            debt_balance_gbp=debt_balance_gbp,
        )
        self._records[account_id] = record
        return record

    def receive_final_read(self, account_id: str, kwh: float) -> AccountClosure:
        r = _update(
            self._records[account_id],
            final_read_kwh=kwh,
            status=ClosureStatus.FINAL_READ_RECEIVED,
        )
        self._records[account_id] = r
        return r

    def issue_final_bill(self, account_id: str, bill_gbp: float) -> AccountClosure:
        r = _update(
            self._records[account_id],
            final_bill_gbp=bill_gbp,
            status=ClosureStatus.FINAL_BILL_ISSUED,
        )
        self._records[account_id] = r
        return r

    def return_deposit(self, account_id: str) -> AccountClosure:
        r = _update(self._records[account_id], status=ClosureStatus.DEPOSIT_RETURNED)
        self._records[account_id] = r
        return r

    def apply_deposit_to_debt(self, account_id: str) -> AccountClosure:
        r = _update(self._records[account_id], status=ClosureStatus.DEPOSIT_APPLIED)
        self._records[account_id] = r
        return r

    def refer_to_debt_collection(self, account_id: str) -> AccountClosure:
        r = _update(self._records[account_id], status=ClosureStatus.DEBT_REFERRED)
        self._records[account_id] = r
        return r

    def close(self, account_id: str) -> AccountClosure:
        r = _update(self._records[account_id], status=ClosureStatus.CLOSED)
        self._records[account_id] = r
        return r

    def active_closures(self) -> List[AccountClosure]:
        return [r for r in self._records.values() if r.status != ClosureStatus.CLOSED]

    def overdue_final_bills(self, as_of: dt.date) -> List[AccountClosure]:
        return [r for r in self._records.values() if r.is_final_bill_overdue(as_of)]

    def deposits_to_return(self) -> List[AccountClosure]:
        return [r for r in self._records.values() if r.status == ClosureStatus.DEPOSIT_RETURNED]

    def debt_referrals(self) -> List[AccountClosure]:
        return [r for r in self._records.values() if r.status == ClosureStatus.DEBT_REFERRED]

    def requiring_debt_referral(self) -> List[AccountClosure]:
        return [r for r in self._records.values() if r.requires_debt_referral]

    # ------------------------------------------------------------------
    # W2_12 — the credit-risk exit, OBSERVATION side only.
    # ------------------------------------------------------------------

    def record_final_bill_outcome(self, event: dict) -> AccountClosure:
        """Consume a world-side final-bill outcome event.

        The event is wall-guarded first: anything carrying a probability, an
        archetype or a household attribute is REJECTED, not sanitised. We learn
        the outcome, the money and whether the customer went away — nothing
        about why.

        The status transition is the company's own reading of what it observed:
        a shortfall is referred to collections (SLC-consistent), anything else
        settles. Idempotent (C-S2): replaying the same event is a no-op.
        """
        payment = FinalBillPaymentEvent.from_observation(event)
        record = self._records[payment.account_id]

        if (record.final_bill_outcome == payment.outcome
                and record.final_bill_resolved_on == payment.resolved_on):
            return record

        if payment.outcome.is_shortfall:
            status = ClosureStatus.DEBT_REFERRED
        elif payment.outcome == FinalBillOutcome.CREDIT_DUE:
            status = ClosureStatus.DEPOSIT_RETURNED
        else:
            status = ClosureStatus.CLOSED

        updated = _update(
            record,
            status=status,
            final_bill_outcome=payment.outcome,
            final_bill_resolved_on=payment.resolved_on,
            final_bill_recovered_gbp=payment.recovered_gbp,
            gone_away=payment.gone_away,
        )
        self._records[payment.account_id] = updated
        return updated

    def awaiting_final_bill_outcome(self, as_of: dt.date) -> List[AccountClosure]:
        """Exits that are exposed to credit risk and still unanswered (C-S3)."""
        return [r for r in self._records.values() if r.is_awaiting_final_bill_outcome(as_of)]

    def gone_away_closures(self) -> List[AccountClosure]:
        return [r for r in self._records.values() if r.gone_away]

    def exit_debt_summary(self, as_of: dt.date) -> dict:
        """The credit-risk-exit view of the closure book.

        `exposed_gbp` is money at risk on exits whose outcome has NOT come back
        yet; it is deliberately kept separate from `shortfall_gbp` (money we
        have observed we did not get) so an unresolved exit is never quietly
        counted as either a loss or a recovery.
        """
        awaiting = self.awaiting_final_bill_outcome(as_of)
        resolved = [r for r in self._records.values() if r.final_bill_outcome is not None]
        return {
            "as_of": as_of.isoformat(),
            "resolved": len(resolved),
            "awaiting_outcome": len(awaiting),
            "exposed_gbp": round(sum(max(0.0, r.net_balance_gbp) for r in awaiting), 2),
            "shortfall_gbp": round(sum(r.final_bill_shortfall_gbp for r in resolved), 2),
            "gone_away": len(self.gone_away_closures()),
            "unpaid": sum(1 for r in resolved if r.final_bill_outcome == FinalBillOutcome.UNPAID),
            "partially_paid": sum(
                1 for r in resolved if r.final_bill_outcome == FinalBillOutcome.PARTIALLY_PAID
            ),
        }

    def closure_summary(self) -> dict:
        by_status = {s.value: 0 for s in ClosureStatus}
        for r in self._records.values():
            by_status[r.status.value] += 1
        return {
            "total_closures": len(self._records),
            "active": len(self.active_closures()),
            "overdue_final_bills": len(self.overdue_final_bills(dt.date.today())),
            "deposits_to_return": len(self.deposits_to_return()),
            "debt_referrals": len(self.debt_referrals()),
            "requiring_debt_referral": len(self.requiring_debt_referral()),
            "by_status": by_status,
        }
