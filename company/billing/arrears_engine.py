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
     Residential debt accrues NO statutory interest. The s.5A fixed sum is a
     ONE-OFF per qualifying debt, NOT charged again per accrual period — recurring
     interest accrual passes include_fixed_compensation=False after the first
     accrual (guarded by assert_fixed_compensation_once). Anchors:
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
    """30 / 60 / 90+ day ageing. days_overdue is days PAST the due date, and it
    is SIGNED (atom D24): a bill not yet due reads NEGATIVE, and every negative
    day falls in "current" exactly as day 0 does. The bucketing is unchanged by
    D24 -- no published bucket moved -- but the DOMAIN is now the whole integer
    line, which is why `assert_age_buckets_partition` probes below zero."""
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
    # SIGNED days past the due date (atom D24, 2026-08-10): negative BEFORE the
    # bill falls due, 0 ON the due date, positive after. It was `max(0, days)`,
    # which made "issued today, due in a fortnight" and "due today" ONE reading
    # -- see `assert_overdue_clock_resolves_before_due` for the class and
    # `is_overdue` for the predicate callers should use instead of `> 0`.
    days_overdue: int
    disputed: bool = False

    @property
    def bucket(self) -> str:
        return age_bucket(self.days_overdue)

    @property
    def is_overdue(self) -> bool:
        """Past its due date. The due date itself is the last day to pay, so
        day 0 is NOT yet overdue -- the same convention the dunning path's
        trigger 0 ("reminder" on the due date) already encoded."""
        return self.days_overdue > 0


def age_open_items(
    ledger: AccountLedger,
    as_of: dt.date,
    payment_terms_days: int = 14,
    disputed_refs: Sequence[str] = (),
) -> List[AgedItem]:
    """Open-item ageing: one AgedItem per undisputed open invoice, aged from its
    due date (issue_date + payment_terms_days). Disputed invoices are returned
    with disputed=True but callers exclude them from ageing/dunning.

    THE CLOCK IS SIGNED (atom D24, 2026-08-10). It was `max(0, days)`. A floor
    at zero is not a smaller reading, it is a COLLAPSE: an invoice issued today
    and due in a fortnight published the same `days_overdue` as one due today,
    so nothing downstream could tell "not yet due" from "due now". Two live
    consequences, both measured before the change and both real:

      * `collections_snapshot` selected the dunning path's trigger-0 step from
        the moment a bill was ISSUED -- the company chased a residential
        customer for a bill it had given them 14 days to pay (an SLC-27-shaped
        misstep, and the sort of thing a real supplier is fined for);
      * `PaymentObservationConsumer.expected_collection_misses` compares this
        number against its reconciliation grace, so every company with a grace
        of zero or less fired on the issue date. A -5d detector and a -20d
        detector -- a fortnight apart in fact -- published ONE latency and ONE
        detection gap (`ORGAN_QUERY_GRID`, atom D23, which declared the floor
        as this organ's debt rather than its own grid's).

    Nothing at the SHIPPED parameters moves: a positive grace and a bucket
    scheme whose lowest band is "current" both read a negative day exactly as
    they read zero. What changes is that the organ can now be asked a question
    about the days BEFORE the due date and answer it (R12: the clock was
    repaired, no output was tuned).

    The floor that REMAINS is the company's own and is not this organ's to
    lift: nothing here exists before the invoice is issued, so no detector can
    be dated earlier however fast it reconciles."""
    alloc = ledger.allocate(disputed_refs=disputed_refs, as_of=as_of)
    items: List[AgedItem] = []
    for oi in alloc.open_items:
        if oi.is_settled:
            continue
        due = oi.issue_date + dt.timedelta(days=payment_terms_days)
        items.append(AgedItem(
            reference=oi.invoice_ref,
            outstanding_gbp=oi.outstanding_gbp,
            due_date=due,
            days_overdue=(as_of - due).days,
            disputed=oi.disputed,
        ))
    return items


def oldest_unpaid_bill_date(
    ledger: AccountLedger,
    as_of: dt.date,
) -> Optional[dt.date]:
    """FIFO appropriation for a balance-based (rolling) account: apply every credit
    (payments, write-offs, credit adjustments) against bill debits OLDEST-FIRST, and
    return the valid_time of the oldest bill NOT yet fully covered — the oldest bill
    the outstanding balance actually still owes. Returns None if every bill is
    covered (any residual balance is non-bill: interest/debit-adjustment).

    This is the FIFO a rolling balance IMPLIES: a payment reduces the oldest debt
    first, so once early bills are settled the arrears age from a LATER bill, not
    from the account's first-ever bill. Pure function of the event set (C-S2)."""
    bills = sorted(
        (e for e in ledger.events()
         if e.event_type == LedgerEventType.BILL_DEBIT and e.valid_time <= as_of),
        key=lambda e: (e.valid_time, e.event_id),
    )
    if not bills:
        return None
    # Total credit magnitude available to appropriate against bills, oldest-first.
    credit = round(sum(
        e.amount_gbp for e in ledger.events()
        if not e.event_type.is_debit and e.valid_time <= as_of
    ), 2)
    for b in bills:
        if credit >= round(b.amount_gbp, 2) - 0.005:
            credit = round(credit - b.amount_gbp, 2)
            continue
        # this bill is only partially (or not) covered → oldest unpaid
        return b.valid_time
    return None  # every bill fully covered by credits


def age_balance(
    ledger: AccountLedger,
    as_of: dt.date,
    payment_terms_days: int = 14,
) -> Optional[AgedItem]:
    """Balance-based ageing: the whole positive rolling balance, aged from the
    OLDEST unpaid bill's due date (FIFO — payments reduce the oldest debt first,
    which is what a rolling balance implies). Returns None if not in arrears.

    HARDENED (D5 red-team): the anchor is the oldest bill still UNPAID under FIFO
    appropriation, NOT the account's oldest bill ever. Anchoring to the first-ever
    bill OVER-AGED a recent arrears whose earlier bills had been paid off (a £X
    balance from last month's bill was aged into 90+ and over-dunned — an SLC-27
    hazard for resi). If the residual balance owes no bill (all bills covered by
    credits; the balance is interest/adjustment), it ages from as_of (current)."""
    bal = ledger.balance(as_of)
    if bal <= 0.005:
        return None
    oldest = oldest_unpaid_bill_date(ledger, as_of)
    if oldest is None:
        oldest = as_of  # residual is non-bill (interest/adjustment); not an aged bill
    due = oldest + dt.timedelta(days=payment_terms_days)
    return AgedItem(
        reference=ledger.account_id,
        outstanding_gbp=round(bal, 2),
        due_date=due,
        # SIGNED, the same clock as `age_open_items` (atom D24) -- a balance
        # whose oldest unpaid bill is not yet due is not "0 days overdue".
        days_overdue=(as_of - due).days,
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


class OverdueClockFloorError(Exception):
    """Raised when the organ's overdue clock FLOORS -- when two `as_of` dates a
    day apart publish one `days_overdue`, so two companies whose collections
    differ by a day are one reading (atom D24)."""


class DunningWithoutAnItemError(Exception):
    """Raised when a dunning step is selected with no overdue item behind it --
    the sentinel-zero shape, where "nothing here" and "due today" are both 0 and
    the trigger-0 step fires on an account that owes nothing yet (atom D24)."""


class DunningPathError(Exception):
    """Raised when a segment's dunning path is empty or its triggers are not
    strictly ascending (which would make step selection order-dependent)."""


class StatutoryInterestScopeError(Exception):
    """Raised when non-zero statutory interest is attributed to a NON-business
    (B2C) account — LPCDA 1998 is B2B only."""


class DunningScopeError(Exception):
    """Raised when a B2C (non-business) segment's dunning path ADVERTISES a
    statutory late-payment-interest action — LPCDA 1998 is B2B only, and serving a
    domestic customer an interest notice is a compliance misstatement even when no
    interest £ is charged (the money side is separately guarded by
    assert_interest_is_b2b_only)."""


class WriteOffAuditError(Exception):
    """Raised when a write-off is not a dated, reasoned, P&L-visible credit
    event (a silent status flip)."""


def assert_age_buckets_partition(
    bucket_fn=age_bucket, max_days: int = 400, min_days: int = -400,
) -> None:
    """R15 CONTROL — the ageing buckets must PARTITION days-overdue: every day maps
    to exactly one bucket in AGE_BUCKETS (exhaustive + in-set), and severity is
    monotonic non-decreasing as days rise (no overlap / no regression).

    Independent: it PROBES the bucket function across the whole domain rather than
    trusting its boundaries. Fail-closed: an out-of-set or non-monotonic result
    RAISES. Mutation defect this fires on: a bucket function with a gap (a day in
    no bucket) or an overlap (severity going backwards).

    THE DOMAIN NOW STARTS BELOW ZERO (atom D24, R10 — the class, not the
    instance). Until the clock was signed this control could only ever be handed
    non-negative days, so a bucket function that fell off the end of the world on
    a not-yet-due invoice (a `KeyError`, an out-of-set label, a severity that
    regressed below zero) was unreachable BY CONSTRUCTION rather than by proof.
    The clamp was the only thing holding that domain shut; lifting it without
    widening this probe would have moved an untested region into production."""
    last_sev = -1
    for d in range(min_days, max_days + 1):
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


_CLOCK_PROBE_ISSUE_DATE = dt.date(2024, 1, 1)   # fixed: the probe is deterministic (C-S2)


def assert_overdue_clock_resolves_before_due(
    clock=age_open_items, payment_terms_days: int = 14, span_days: int = 3,
) -> None:
    """R15 CONTROL — the organ's overdue clock must RESOLVE ONE DAY EVERYWHERE in
    its domain: a day of elapsed time moves `days_overdue` by exactly one day on
    the days BEFORE the bill falls due as much as on the days after (atom D24).

    THE DEFECT IT FIRES ON, which shipped: `days_overdue=max(0, days)`. Under a
    floor the pre-due deltas are all ZERO, so every `as_of` from the issue date to
    the due date publishes one number and no consumer can tell a bill issued today
    from a bill due today. That collapse reached the dunning selector (the
    trigger-0 step fired from the ISSUE date) and `expected_collection_misses`
    (every grace <= 0 fired from the issue date, so detectors a fortnight apart
    published one latency and one detection gap).

    INDEPENDENT, and this is the whole reason the control is shaped as a
    DIFFERENCE: it never re-derives `due = issue + terms` or the day count -- a
    harness copy of the organ's arithmetic is R15's TAUTOLOGY pattern and could
    not fail if the organ's rule changed. It asserts the reading against ELAPSED
    CALENDAR TIME, which it holds independently, so it fires on any floor, cap,
    rounding or quantisation the clock might grow, not just on this `max(0, …)`.

    FAIL-CLOSED: a probe that yields no aged item, or a domain with fewer than two
    pre-due sample points (which would make the pre-due claim vacuous), RAISES --
    an unrunnable check is a FAILED check, never a pass.

    WHAT IT DOES NOT ASSERT, because the company genuinely cannot: anything before
    the invoice EXISTS. The probe starts at the issue date, and no organ can be
    dated earlier however fast it reconciles -- that floor is a bound on the
    company's knowledge, not a defect in its clock."""
    issue = _CLOCK_PROBE_ISSUE_DATE
    due = issue + dt.timedelta(days=payment_terms_days)
    ledger = AccountLedger("__clock_probe__")
    ledger.post(LedgerEvent(
        "__clock_probe_bill__", "__clock_probe__", LedgerEventType.BILL_DEBIT,
        100.0, issue, dt.datetime(2024, 1, 1, 0, 0, 0), invoice_ref="__PROBE__",
    ))
    sweep = [issue + dt.timedelta(days=i)
             for i in range(payment_terms_days + span_days + 1)]
    readings: List[int] = []
    for as_of in sweep:
        items = [it for it in clock(ledger, as_of, payment_terms_days) if not it.disputed]
        if len(items) != 1:
            raise OverdueClockFloorError(
                f"overdue-clock probe yielded {len(items)} open items at {as_of} "
                "-- the probe cannot evidence a floor either way (fail-closed)"
            )
        readings.append(items[0].days_overdue)
    pre_due = [i for i, as_of in enumerate(sweep) if as_of < due]
    if len(pre_due) < 2:
        raise OverdueClockFloorError(
            f"overdue-clock probe has {len(pre_due)} sample point(s) before the "
            "due date -- the pre-due claim would be vacuous (fail-closed)"
        )
    for (a, b), as_of in zip(zip(readings, readings[1:]), sweep):
        if b - a != 1:
            raise OverdueClockFloorError(
                f"the overdue clock does not resolve a day at {as_of}: one day of "
                f"elapsed time moved it {a} -> {b}. Two companies whose "
                "collections differ by a day are ONE reading here"
            )


def select_dunning_step(
    items: Sequence[AgedItem], segment: Segment,
) -> tuple:
    """The dunning selection, as ONE function of the aged items rather than an
    expression inside `collections_snapshot` -- so it can be PROBED by a control
    (atom D24). Returns `(max_days_overdue, step)`, both None when no undisputed
    item is present.

    NONE, NOT ZERO, when there is nothing to dun. `max(..., default=0)` made
    "this account has no open items" indistinguishable from "an item falls due
    today", and the trigger-0 step then fired on an account that owed nothing --
    the same sentinel collision D24 lifted out of the clock itself, one layer up.
    """
    undisputed = [it for it in items if not it.disputed]
    if not undisputed:
        return None, None
    max_overdue = max(it.days_overdue for it in undisputed)
    return max_overdue, current_dunning_step(segment, max_overdue)


def assert_dunning_requires_an_item(
    selector=select_dunning_step, segment: Segment = Segment.RESIDENTIAL,
) -> None:
    """R15 CONTROL — a dunning step must never be selected without an undisputed
    item that has actually reached its trigger (atom D24).

    Three defects it fires on, each of which has been live in this module:
      * NO items at all selecting the trigger-0 step (the `default=0` sentinel);
      * only DISPUTED items selecting a step (a held dispute does not dun);
      * a NOT-YET-DUE item selecting the trigger-0 step (the clamped clock).

    Independent: it constructs its own aged items and probes the selector, rather
    than re-reading a selection made elsewhere. FAIL-CLOSED, with a VACUITY GUARD
    that is the point of the last check -- a selector that returned `(None, None)`
    for everything would satisfy the three negatives trivially, so a genuinely
    overdue item MUST select a step or this raises."""
    due = _CLOCK_PROBE_ISSUE_DATE + dt.timedelta(days=14)

    def _item(days: int, disputed: bool = False) -> AgedItem:
        return AgedItem("__PROBE__", 100.0, due, days, disputed)

    for label, items in (
        ("no items at all", []),
        ("only a disputed item", [_item(120, disputed=True)]),
        ("an item that is not yet due", [_item(-1)]),
    ):
        max_overdue, step = selector(items, segment)
        if step is not None:
            raise DunningWithoutAnItemError(
                f"dunning step {step.action!r} selected with {label} "
                f"(max_days_overdue={max_overdue!r})"
            )
    max_overdue, step = selector([_item(120)], segment)
    if step is None:
        raise DunningWithoutAnItemError(
            "the dunning selector returned NO step for an item 120 days overdue "
            "-- an inert selector passes the negative checks vacuously"
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


# A dunning action naming statutory interest advertises an LPCDA 1998 charge. Kept
# as one marker so the B2C-scope control cannot drift from how actions are named.
_INTEREST_ACTION_MARKER = "interest"


def assert_dunning_path_scope_valid(segment: Segment, path=None) -> None:
    """R15 CONTROL — the SIBLING half of assert_interest_is_b2b_only: a B2C
    (non-business) segment's dunning path must not ADVERTISE a statutory-interest
    action. LPCDA 1998 is B2B only; a residential path that duns via an
    'interest_notice' misstates the law to a domestic customer (and is an SLC-27
    hazard) even though statutory_interest_gbp separately returns 0 for B2C — the
    money guard alone leaves the MESSAGING half unprotected.

    Independent: it inspects the path's own actions, not the interest figure.
    Fail-closed: an empty path RAISES (an unformed path is a failed check, not a
    silent pass). Mutation defect this fires on: an 'interest_notice' step inserted
    into a residential/B2C dunning path."""
    steps = list(_DUNNING_PATHS[segment]) if path is None else list(path)
    if not steps:
        raise DunningScopeError(f"segment {segment.value} has no dunning path")
    if segment.is_business:
        return
    for s in steps:
        if _INTEREST_ACTION_MARKER in (s.action or "").lower():
            raise DunningScopeError(
                f"B2C segment {segment.value} dunning step {s.action!r} advertises "
                f"statutory interest: LPCDA 1998 is B2B only"
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


def assert_fixed_compensation_once(interest_events) -> None:
    """R15 CONTROL — the LPCDA 1998 s.5A fixed statutory sum is recoverable ONCE per
    qualifying debt, never per accrual period. Given the INTEREST_DEBIT events for a
    SINGLE debt, fires if more than one carries the fixed sum.

    Independent: it inspects the EMITTED events' reason markers (what actually
    posted to the ledger), not the include_fixed_compensation flag the producer was
    handed — so a caller that forgets to suppress the fixed sum on a re-accrual is
    caught from the ledger side. FAIL-CLOSED: a non-INTEREST_DEBIT event in the set
    RAISES (a mis-scoped input is a failed check, not a silent pass). Mutation
    defect: a recurring accrual that re-charges the £40/£70/£100 fixed sum every
    period (multiplying a statutory one-off)."""
    charged = 0
    for e in interest_events:
        if e.event_type != LedgerEventType.INTEREST_DEBIT:
            raise FixedCompensationError(
                f"event {e.event_id} is {e.event_type.value}, not an interest accrual "
                f"— assert_fixed_compensation_once needs one debt's interest events"
            )
        if _FIXED_COMP_MARKER in (e.reason or ""):
            charged += 1
    if charged > 1:
        raise FixedCompensationError(
            f"s.5A fixed compensation charged {charged} times on one debt "
            f"(LPCDA 1998 allows the fixed sum once per qualifying debt)"
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

# Stable marker written into an interest event's reason WHENEVER the s.5A fixed
# sum is included — used by assert_fixed_compensation_once to detect a debt whose
# one-off statutory sum has been charged more than once. Kept as one constant so
# the producer (build_interest_event) and the control cannot drift apart.
_FIXED_COMP_MARKER = "s.5A fixed compensation"


class FixedCompensationError(Exception):
    """Raised when the LPCDA 1998 s.5A fixed statutory sum — recoverable ONCE per
    qualifying debt — is charged on more than one of a debt's interest accruals."""


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
    include_fixed_compensation: bool = True,
) -> Optional[LedgerEvent]:
    """Produce an INTEREST_DEBIT LedgerEvent for B2B late interest, or None if not
    applicable (residential, or nothing due). The event feeds the SAME ledger.

    The s.5A fixed statutory sum (£40/£70/£100) is recoverable ONCE per qualifying
    debt, not per accrual period. A caller that accrues interest across multiple
    as_of dates for the SAME debt must pass include_fixed_compensation=False on
    every accrual after the first, or it re-charges the one-off sum each period
    (assert_fixed_compensation_once catches that across the debt's events)."""
    amount = statutory_interest_gbp(
        segment, principal_gbp, days_late, boe_base_rate,
        include_fixed_compensation=include_fixed_compensation,
    )
    # R15 WIRING — the scope control now RUNS on every live interest calculation:
    # a positive figure on a non-business segment RAISES here (fail-closed), rather
    # than the invariant only being checkable on demand. Independent of the
    # producer's own guard (a second check on the produced figure).
    assert_interest_is_b2b_only(segment, amount)
    if amount <= 0:
        return None
    eid = event_id or f"INT-{account_id}-{invoice_ref or 'BAL'}-{as_of.isoformat()}"
    rate_pct = (boe_base_rate + LPCDA_MARGIN) * 100
    if include_fixed_compensation:
        reason = (
            f"LPCDA 1998 statutory interest: {days_late}d @ {rate_pct:.2f}% + "
            f"{_FIXED_COMP_MARKER} £{lpcda_fixed_compensation_gbp(principal_gbp):.2f}"
        )
    else:
        reason = (
            f"LPCDA 1998 statutory interest: {days_late}d @ {rate_pct:.2f}% "
            f"(interest only — s.5A fixed sum already charged on this debt)"
        )
    return LedgerEvent(
        event_id=eid,
        account_id=account_id,
        event_type=LedgerEventType.INTEREST_DEBIT,
        amount_gbp=amount,
        valid_time=as_of,
        transaction_time=transaction_time,
        invoice_ref=invoice_ref,
        reason=reason,
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
    event = LedgerEvent(
        event_id=eid,
        account_id=account_id,
        event_type=LedgerEventType.WRITE_OFF_CREDIT,
        amount_gbp=round(amount_gbp, 2),
        valid_time=as_of,
        transaction_time=transaction_time,
        invoice_ref=invoice_ref,
        reason=detail,
    )
    # R15 WIRING — the audit control now RUNS on every write-off the engine mints:
    # an undated/unreasoned/not-P&L-visible write-off RAISES here (fail-closed), so
    # a silent status flip can never leave this factory unaudited.
    assert_write_off_audited(event)
    return event


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

    # R15 WIRING — the collections controls now RUN on every live snapshot, so an
    # ageing/dunning defect surfaces (raises) at read time rather than the
    # invariants only being checkable on demand:
    #   - the 30/60/90+ scheme still PARTITIONS days-overdue (no gap/overlap);
    #   - bucketing these very items CONSERVES their undisputed value + count;
    #   - this segment's dunning path is well-formed before a step is selected;
    #   - a B2C segment's path advertises NO statutory-interest action (LPCDA B2B-only);
    #   - the overdue clock still RESOLVES A DAY before the due date (atom D24);
    #   - no dunning step is selected without an item that reached its trigger (D24).
    assert_age_buckets_partition(age_bucket)
    assert_ageing_conserves_value(items, aggregator=ageing_buckets)
    assert_dunning_path_valid(segment)
    assert_dunning_path_scope_valid(segment)
    assert_overdue_clock_resolves_before_due(
        age_open_items, payment_terms_days=payment_terms_days)
    assert_dunning_requires_an_item(select_dunning_step, segment=segment)

    undisputed = [it for it in items if not it.disputed]
    max_overdue, step = select_dunning_step(items, segment)
    total_undisputed_overdue = round(
        sum(it.outstanding_gbp for it in undisputed if it.is_overdue), 2
    )
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
