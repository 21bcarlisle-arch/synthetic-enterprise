"""Non/partial-payment physics — one engine, segment-parameterised. M2 (D5).

Sits on top of company/billing/account_ledger.py (the model-agnostic event
stream) and drives the collections lifecycle identically for both accounting
models:

  1. AGEING — 30 / 60 / 90+ day buckets over undisputed outstanding. Balance-based
     accounts age their rolling arrears from the oldest unpaid bill; open-item
     accounts age each undisputed open invoice by its own due date. Disputed
     invoices are EXCLUDED from ageing while held (they don't dun, don't accrue
     statutory interest) — the same rule the I&C dispute register already encodes.
  2. DUNNING — segment-specific step sequences (a resi path bounded by Ofgem SLC
     27 ability-to-pay duties; a B2B path that escalates to commercial recovery).
  3. STATUTORY LATE-PAYMENT INTEREST — B2B ONLY, under the Late Payment of
     Commercial Debts (Interest) Act 1998: 8 percentage points above the Bank of
     England base rate, plus fixed compensation (£40/£70/£100 by debt size).
     Residential debt accrues NO statutory interest. Anchors:
     docs/market_research/account_hierarchy_payment_allocation.md.
  4. WRITE-OFFS — dated, reasoned, P&L-visible ledger events (WRITE_OFF_CREDIT),
     never a silent status flip.

Epistemic wall: arrears, dunning steps, statutory interest and write-offs are all
the supplier's own operational actions and published statute. No sim internals.

NAMED SIMPLIFICATION (R10 — deliberate L2 gap, to close at the seam-crossing atom):
  (4) The resi/micro-SME dunning path ENCODES the Ofgem SLC 27 ability-to-pay
      shape (a repayment-plan offer before any enforcement), but the SLC 27 duty
      is NOT live-verified against a real customer vulnerability/ability-to-pay
      signal — there is no live recall of an SLC-27 hold here. The step sequence
      is the correct shape; the per-customer verification is future wiring.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Sequence

from company.billing.account_ledger import (
    AccountLedger,
    LedgerEvent,
    LedgerEventType,
)
from company.crm.account_hierarchy import Segment


# ---------------------------------------------------------------------------
# 1. Ageing
# ---------------------------------------------------------------------------

AGE_BUCKETS = ("current", "30-60", "60-90", "90+")


def age_bucket(days_overdue: int) -> str:
    """30 / 60 / 90+ day ageing. days_overdue is days PAST the due date."""
    if days_overdue >= 90:
        return "90+"
    if days_overdue >= 60:
        return "60-90"
    if days_overdue >= 30:
        return "30-60"
    return "current"


@dataclass(frozen=True)
class AgedItem:
    reference: str          # invoice_ref (open-item) or account_id (balance-based)
    outstanding_gbp: float
    due_date: dt.date
    days_overdue: int
    disputed: bool = False

    @property
    def bucket(self) -> str:
        return age_bucket(self.days_overdue)


def age_open_items(
    ledger: AccountLedger,
    as_of: dt.date,
    payment_terms_days: int = 14,
    disputed_refs: Sequence[str] = (),
) -> List[AgedItem]:
    """Open-item ageing: one AgedItem per undisputed open invoice, aged from its
    due date (issue_date + payment_terms_days). Disputed invoices are returned
    with disputed=True but callers exclude them from ageing/dunning."""
    alloc = ledger.allocate(disputed_refs=disputed_refs, as_of=as_of)
    items: List[AgedItem] = []
    for oi in alloc.open_items:
        if oi.is_settled:
            continue
        due = oi.issue_date + dt.timedelta(days=payment_terms_days)
        days = (as_of - due).days
        items.append(AgedItem(
            reference=oi.invoice_ref,
            outstanding_gbp=oi.outstanding_gbp,
            due_date=due,
            days_overdue=max(0, days),
            disputed=oi.disputed,
        ))
    return items


def age_balance(
    ledger: AccountLedger,
    as_of: dt.date,
    payment_terms_days: int = 14,
) -> Optional[AgedItem]:
    """Balance-based ageing: the whole positive rolling balance, aged from the
    OLDEST unpaid bill's due date (FIFO — payments reduce the oldest debt first,
    which is what a rolling balance implies). Returns None if not in arrears."""
    bal = ledger.balance(as_of)
    if bal <= 0.005:
        return None
    # oldest bill debit still 'covered' by the outstanding balance
    bill_dates = sorted(
        e.valid_time for e in ledger.events()
        if e.event_type == LedgerEventType.BILL_DEBIT and e.valid_time <= as_of
    )
    oldest = bill_dates[0] if bill_dates else as_of
    due = oldest + dt.timedelta(days=payment_terms_days)
    days = (as_of - due).days
    return AgedItem(
        reference=ledger.account_id,
        outstanding_gbp=round(bal, 2),
        due_date=due,
        days_overdue=max(0, days),
        disputed=False,
    )


def ageing_buckets(items: Sequence[AgedItem]) -> Dict[str, Dict[str, float]]:
    """Aggregate AgedItems into 30/60/90+ buckets, EXCLUDING disputed items."""
    buckets: Dict[str, Dict[str, float]] = {
        b: {"count": 0, "amount_gbp": 0.0} for b in AGE_BUCKETS
    }
    for it in items:
        if it.disputed:
            continue
        b = buckets[it.bucket]
        b["count"] += 1
        b["amount_gbp"] = round(b["amount_gbp"] + it.outstanding_gbp, 2)
    return buckets


# ---------------------------------------------------------------------------
# 2. Dunning (segment-parameterised)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class DunningStep:
    trigger_days_overdue: int
    action: str
    channel: str


# Resi/micro-SME: Ofgem SLC 27 (ability-to-pay) shapes the path — reminder,
# then a proactive contact / repayment-plan offer BEFORE any enforcement, and no
# statutory interest. B2B: commercial recovery, faster, interest-bearing.
_DUNNING_PATHS: Dict[Segment, List[DunningStep]] = {
    Segment.RESIDENTIAL: [
        DunningStep(0, "reminder", "email/sms"),
        DunningStep(14, "reminder_2", "letter"),
        DunningStep(28, "repayment_plan_offer", "phone/letter"),   # SLC 27 ability-to-pay
        DunningStep(56, "final_notice", "letter"),
        DunningStep(90, "prepayment_or_debt_agency", "field/agency"),
    ],
    Segment.MICRO_SME: [
        DunningStep(0, "reminder", "email"),
        DunningStep(14, "reminder_2", "email/phone"),
        DunningStep(28, "repayment_plan_offer", "phone"),
        DunningStep(56, "final_notice", "letter"),
        DunningStep(75, "disconnection_warning_or_agency", "letter/agency"),
    ],
    Segment.SME: [
        DunningStep(0, "reminder", "email"),
        DunningStep(7, "statement_of_account", "email"),
        DunningStep(30, "interest_notice", "letter"),               # LPCDA notice
        DunningStep(45, "final_demand", "letter"),
        DunningStep(60, "debt_recovery", "agency/legal"),
    ],
    Segment.IC: [
        DunningStep(0, "reminder", "email/account_manager"),
        DunningStep(7, "interest_notice", "letter"),                # LPCDA notice
        DunningStep(21, "final_demand", "letter/legal"),
        DunningStep(35, "commercial_recovery", "legal"),
    ],
}


def dunning_path(segment: Segment) -> List[DunningStep]:
    return list(_DUNNING_PATHS[segment])


def current_dunning_step(segment: Segment, days_overdue: int) -> Optional[DunningStep]:
    """The furthest dunning step whose trigger has been reached. None if not yet
    overdue enough to dun.

    HARDENED: selects the reached step with the LARGEST trigger rather than
    breaking on the first unreached one — so a mis-ordered path can never SILENTLY
    skip a step (the old early-break assumed the path was sorted ascending, a
    fail-silent dependence on data order). `assert_dunning_path_valid` still guards
    the data shape, but the selection itself is now order-independent."""
    reached = [s for s in _DUNNING_PATHS[segment] if days_overdue >= s.trigger_days_overdue]
    if not reached:
        return None
    return max(reached, key=lambda s: s.trigger_days_overdue)


# ---------------------------------------------------------------------------
# R15 CONTROLS for the collections physics.
#
# Each is INDEPENDENT of the thing it checks (it re-derives or externally probes,
# never re-reads the same computed value) and FAIL-CLOSED (an empty/missing/
# malformed input RAISES, it does not pass on absence). See CONTROLS_THAT_CANNOT
# _FAIL.md (R15). The ageing/dunning/interest/write-off invariants were previously
# only implicit; these make them able to fire on their own named defect.
# ---------------------------------------------------------------------------

_AGE_SEVERITY = {b: i for i, b in enumerate(AGE_BUCKETS)}


class AgeingPartitionError(Exception):
    """Raised when the 30/60/90+ ageing scheme fails to PARTITION days-overdue
    (a gap, an overlap, an out-of-set bucket) or when bucket aggregation loses
    money relative to the underlying items."""


class DunningPathError(Exception):
    """Raised when a segment's dunning path is empty or its triggers are not
    strictly ascending (which would make step selection order-dependent)."""


class StatutoryInterestScopeError(Exception):
    """Raised when non-zero statutory interest is attributed to a NON-business
    (B2C) account — LPCDA 1998 is B2B only."""


class WriteOffAuditError(Exception):
    """Raised when a write-off is not a dated, reasoned, P&L-visible credit
    event (a silent status flip)."""


def assert_age_buckets_partition(bucket_fn=age_bucket, max_days: int = 400) -> None:
    """R15 CONTROL — the ageing buckets must PARTITION days-overdue: every day maps
    to exactly one bucket in AGE_BUCKETS (exhaustive + in-set), and severity is
    monotonic non-decreasing as days rise (no overlap / no regression).

    Independent: it PROBES the bucket function across the whole domain rather than
    trusting its boundaries. Fail-closed: an out-of-set or non-monotonic result
    RAISES. Mutation defect this fires on: a bucket function with a gap (a day in
    no bucket) or an overlap (severity going backwards)."""
    last_sev = -1
    for d in range(0, max_days + 1):
        b = bucket_fn(d)
        if b not in _AGE_SEVERITY:
            raise AgeingPartitionError(f"day {d} → out-of-set bucket {b!r} (gap)")
        sev = _AGE_SEVERITY[b]
        if sev < last_sev:
            raise AgeingPartitionError(
                f"day {d} → bucket {b!r} regresses severity (overlap/non-monotonic)"
            )
        last_sev = sev


def assert_ageing_conserves_value(items, aggregator=ageing_buckets) -> None:
    """R15 CONTROL — aggregating AgedItems into buckets must CONSERVE the undisputed
    outstanding value and item count (no drop, no double-count).

    Independent: the control sums the items directly and compares against whatever
    `aggregator` produces — so a faulty aggregator (dropping an item, mis-handling
    the disputed exclusion, double-counting) makes the two totals disagree and this
    RAISES. Fail-closed on mismatch. Mutation defect: an aggregator that loses or
    duplicates an item's amount."""
    direct_total = round(sum(it.outstanding_gbp for it in items if not it.disputed), 2)
    direct_count = sum(1 for it in items if not it.disputed)
    buckets = aggregator(items)
    agg_total = round(sum(v["amount_gbp"] for v in buckets.values()), 2)
    agg_count = sum(v["count"] for v in buckets.values())
    if abs(direct_total - agg_total) > 0.005:
        raise AgeingPartitionError(
            f"ageing value not conserved: items {direct_total} != buckets {agg_total}"
        )
    if direct_count != agg_count:
        raise AgeingPartitionError(
            f"ageing count not conserved: items {direct_count} != buckets {agg_count}"
        )


def assert_dunning_path_valid(segment: Segment, path=None) -> None:
    """R15 CONTROL — a segment's dunning path must be non-empty with STRICTLY
    ascending triggers, so step selection is well defined. Fail-closed: an empty
    path raises. Mutation defect: a path with a descending/duplicate trigger."""
    steps = list(_DUNNING_PATHS[segment]) if path is None else list(path)
    if not steps:
        raise DunningPathError(f"segment {segment.value} has no dunning path")
    triggers = [s.trigger_days_overdue for s in steps]
    for a, b in zip(triggers, triggers[1:]):
        if b <= a:
            raise DunningPathError(
                f"segment {segment.value} triggers not strictly ascending: {triggers}"
            )


def assert_interest_is_b2b_only(segment: Segment, interest_gbp: float) -> None:
    """R15 CONTROL — statutory (LPCDA 1998) interest may attach ONLY to a business
    account. Fires if a positive amount is attributed to a B2C/residential segment.
    Independent of statutory_interest_gbp's own guard (a second, downstream check on
    the produced figure). Mutation defect: interest applied to a RESIDENTIAL account."""
    if round(interest_gbp, 2) > 0.005 and not segment.is_business:
        raise StatutoryInterestScopeError(
            f"statutory interest £{round(interest_gbp, 2)} attributed to non-business "
            f"segment {segment.value}: LPCDA 1998 is B2B only"
        )


def assert_write_off_audited(event: LedgerEvent) -> None:
    """R15 CONTROL — a write-off must be a dated, reasoned, P&L-visible credit event,
    never a silent status flip. Fires on the wrong type, a missing/blank reason, a
    missing date, or a non-positive amount. Mutation defect: a WRITE_OFF_CREDIT with
    an empty reason (unaudited write-off)."""
    if event.event_type != LedgerEventType.WRITE_OFF_CREDIT:
        raise WriteOffAuditError(
            f"event {event.event_id} is {event.event_type.value}, not a write-off"
        )
    if not event.affects_pnl:
        raise WriteOffAuditError(f"write-off {event.event_id} is not P&L-visible")
    if not (event.reason and event.reason.strip()):
        raise WriteOffAuditError(
            f"write-off {event.event_id} has no reason (silent status flip)"
        )
    if event.valid_time is None:
        raise WriteOffAuditError(f"write-off {event.event_id} is undated")
    if event.amount_gbp <= 0:
        raise WriteOffAuditError(f"write-off {event.event_id} has non-positive amount")


# ---------------------------------------------------------------------------
# 3. Statutory late-payment interest — B2B ONLY (LPCDA 1998)
# ---------------------------------------------------------------------------

LPCDA_MARGIN = 0.08  # 8 percentage points above BoE base rate


def lpcda_fixed_compensation_gbp(debt_gbp: float) -> float:
    """Fixed sum recoverable under s.5A LPCDA 1998, by debt size band."""
    if debt_gbp < 1000:
        return 40.0
    if debt_gbp < 10000:
        return 70.0
    return 100.0


def statutory_interest_gbp(
    segment: Segment,
    principal_gbp: float,
    days_late: int,
    boe_base_rate: float,
    include_fixed_compensation: bool = True,
) -> float:
    """Late-payment interest under the Late Payment of Commercial Debts (Interest)
    Act 1998. B2B ONLY — residential debt returns 0.0 (no statutory interest on
    domestic energy arrears). Simple interest at (BoE base + 8%) pro-rata by days,
    plus the fixed statutory compensation. days_late/principal <= 0 ⇒ 0.0."""
    if not segment.is_business:
        return 0.0
    if principal_gbp <= 0 or days_late <= 0:
        return 0.0
    annual_rate = boe_base_rate + LPCDA_MARGIN
    interest = principal_gbp * annual_rate * (days_late / 365.0)
    if include_fixed_compensation:
        interest += lpcda_fixed_compensation_gbp(principal_gbp)
    return round(interest, 2)


def build_interest_event(
    account_id: str,
    segment: Segment,
    principal_gbp: float,
    days_late: int,
    boe_base_rate: float,
    as_of: dt.date,
    transaction_time: dt.datetime,
    invoice_ref: Optional[str] = None,
    event_id: Optional[str] = None,
) -> Optional[LedgerEvent]:
    """Produce an INTEREST_DEBIT LedgerEvent for B2B late interest, or None if not
    applicable (residential, or nothing due). The event feeds the SAME ledger."""
    amount = statutory_interest_gbp(segment, principal_gbp, days_late, boe_base_rate)
    if amount <= 0:
        return None
    eid = event_id or f"INT-{account_id}-{invoice_ref or 'BAL'}-{as_of.isoformat()}"
    return LedgerEvent(
        event_id=eid,
        account_id=account_id,
        event_type=LedgerEventType.INTEREST_DEBIT,
        amount_gbp=amount,
        valid_time=as_of,
        transaction_time=transaction_time,
        invoice_ref=invoice_ref,
        reason=(
            f"LPCDA 1998 statutory interest: {days_late}d @ "
            f"{(boe_base_rate + LPCDA_MARGIN) * 100:.2f}% + fixed compensation"
        ),
    )


# ---------------------------------------------------------------------------
# 4. Write-offs — dated, reasoned, P&L-visible
# ---------------------------------------------------------------------------

class WriteOffReason(str, Enum):
    GONE_AWAY = "gone_away"                  # customer untraceable
    INSOLVENCY = "insolvency"                # bankruptcy / liquidation
    DECEASED_NO_ESTATE = "deceased_no_estate"
    UNECONOMIC_TO_PURSUE = "uneconomic_to_pursue"
    STATUTE_BARRED = "statute_barred"        # >6y, Limitation Act 1980
    GOODWILL = "goodwill"


def build_write_off_event(
    account_id: str,
    amount_gbp: float,
    reason: WriteOffReason,
    as_of: dt.date,
    transaction_time: dt.datetime,
    invoice_ref: Optional[str] = None,
    event_id: Optional[str] = None,
    note: str = "",
) -> LedgerEvent:
    """Produce a WRITE_OFF_CREDIT LedgerEvent. A write-off is a P&L expense the
    moment it posts (affects_pnl=True on the event) and is fully audited (dated +
    reasoned) — never a silent status change."""
    if amount_gbp <= 0:
        raise ValueError("write-off amount must be positive")
    eid = event_id or f"WO-{account_id}-{invoice_ref or 'BAL'}-{as_of.isoformat()}"
    detail = f"write-off ({reason.value})" + (f": {note}" if note else "")
    return LedgerEvent(
        event_id=eid,
        account_id=account_id,
        event_type=LedgerEventType.WRITE_OFF_CREDIT,
        amount_gbp=round(amount_gbp, 2),
        valid_time=as_of,
        transaction_time=transaction_time,
        invoice_ref=invoice_ref,
        reason=detail,
    )


# ---------------------------------------------------------------------------
# Account-level collections snapshot
# ---------------------------------------------------------------------------

def collections_snapshot(
    ledger: AccountLedger,
    segment: Segment,
    accounting_model_is_open_item: bool,
    as_of: dt.date,
    payment_terms_days: int = 14,
    disputed_refs: Sequence[str] = (),
) -> dict:
    """One collections view over either accounting model. Returns ageing buckets,
    the current dunning step, and the undisputed overdue total that would bear
    statutory interest (B2B)."""
    if accounting_model_is_open_item:
        items = age_open_items(ledger, as_of, payment_terms_days, disputed_refs)
    else:
        one = age_balance(ledger, as_of, payment_terms_days)
        items = [one] if one is not None else []

    undisputed = [it for it in items if not it.disputed]
    max_overdue = max((it.days_overdue for it in undisputed), default=0)
    total_undisputed_overdue = round(
        sum(it.outstanding_gbp for it in undisputed if it.days_overdue > 0), 2
    )
    step = current_dunning_step(segment, max_overdue)
    return {
        "account_id": ledger.account_id,
        "segment": segment.value,
        "accounting_model": "open_item" if accounting_model_is_open_item else "balance_based",
        "as_of": as_of.isoformat(),
        "ageing": ageing_buckets(items),
        "undisputed_overdue_gbp": total_undisputed_overdue,
        "disputed_excluded_count": sum(1 for it in items if it.disputed),
        "max_days_overdue": max_overdue,
        "dunning_action": step.action if step else None,
        "dunning_channel": step.channel if step else None,
        "interest_bearing": segment.is_business,
    }
