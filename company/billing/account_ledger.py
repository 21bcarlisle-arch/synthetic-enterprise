"""One ledger, two accounting models — M2 (D5_account_hierarchy_payments).

Both the balance-based world (resi / micro-SME) and the open-item world (SME /
I&C) emit the SAME `LedgerEvent` stream so everything downstream (E-lane
accounts, the three clocks, ageing/dunning) is accounting-model-AGNOSTIC. The
only thing the two models differ on is how a payment MEETS the bills:

  - BALANCE_BASED: bills post debits, payments post credits, the account carries
    a single rolling balance; a partial payment simply reduces the balance; there
    is NO bill-matching.
  - OPEN_ITEM: a payment allocates to SPECIFIC invoices — per the customer's
    remittance advice where given, else OLDEST-FIRST across non-disputed open
    invoices (standard AR practice; anchors in
    docs/market_research/account_hierarchy_payment_allocation.md).

SIGN CONVENTION (documented once, used everywhere): `signed_amount` is POSITIVE
when the event INCREASES what the customer owes us (a bill debit, interest,
a debit adjustment) and NEGATIVE when it REDUCES it (a payment credit, a credit
adjustment, a write-off, a refund reversal). Rolling balance = sum of signed
amounts. balance > 0 ⇒ arrears (they owe us); balance < 0 ⇒ in credit.

BITEMPORALITY: every event carries `valid_time` (the date the fact is ABOUT — a
bill's issue date, a payment's value date) and `transaction_time` (when we could
first have KNOWN it). `emit_to()` writes each event into the shared
company/interfaces/bitemporal_event_log.py so a point-in-time-honest reader can
ask "what did the balance look like as known at decision-time D". The ledger
here is the model-agnostic PRODUCER of those facts.

SCALE (C-S1/C-S2, tested not asserted):
  - Idempotent: `post()` dedups on event_id; posting the same event twice is a
    no-op (returns False). Deterministic replay of a history reproduces identical
    state.
  - Arrival-order-independent: balance() and allocation are PURE FUNCTIONS of the
    event SET, computed over a deterministic (valid_time, event_id) sort — events
    may arrive one at a time, late, or out of order and the answer is unchanged.

Epistemic wall: bills, payments, adjustments and disputes are all things a real
supplier's own systems record. No simulation internals are read.

NAMED SIMPLIFICATIONS (R10 — deliberate L2 gaps, NOT defects, to close at the
seam-crossing atom, never papered over):
  (2) invoice.py's SQLite invoice store is NOT yet migrated onto this event
      model. Bills reach this ledger as BILL_DEBIT events posted by the caller;
      the two stores are reconciled by the caller, not unified. Deliberate.
  (3) Dispute state is PASSED IN to allocate()/ageing as `disputed_refs`, it is
      NOT live-read from company/crm/ic_invoice_dispute_register.py. A stale
      dispute set is therefore possible — the live wiring is a seam-crossing job.
  (5) Oldest-first allocation SIMPLIFIES Clayton's Case (Devaynes v Noble, 1816):
      real appropriation of payments has more doctrine (earmarking, running
      accounts). We implement remittance-else-oldest-first only.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


class LedgerEventType(str, Enum):
    BILL_DEBIT = "bill_debit"                 # a bill/invoice issued (increases owed)
    PAYMENT_CREDIT = "payment_credit"          # a payment received (reduces owed)
    ADJUSTMENT_DEBIT = "adjustment_debit"      # e.g. a correction increasing owed
    ADJUSTMENT_CREDIT = "adjustment_credit"    # e.g. goodwill / dispute credit
    INTEREST_DEBIT = "interest_debit"          # statutory late-payment interest (B2B)
    WRITE_OFF_CREDIT = "write_off_credit"      # bad debt written off (reduces owed, P&L hit)
    REFUND_DEBIT = "refund_debit"              # credit balance refunded to customer

    @property
    def is_debit(self) -> bool:
        return self in (
            LedgerEventType.BILL_DEBIT,
            LedgerEventType.ADJUSTMENT_DEBIT,
            LedgerEventType.INTEREST_DEBIT,
            LedgerEventType.REFUND_DEBIT,
        )


@dataclass(frozen=True)
class LedgerEvent:
    """One dated movement on an account. Same shape for both accounting models."""
    event_id: str                     # STABLE unique id — the idempotency key
    account_id: str
    event_type: LedgerEventType
    amount_gbp: float                 # always a POSITIVE magnitude
    valid_time: dt.date               # the date the fact is about
    transaction_time: dt.datetime     # when it became knowable/recorded
    invoice_ref: Optional[str] = None  # the invoice this bill/allocation concerns
    remittance: Tuple[str, ...] = ()   # payment earmarked to these invoice_refs (open-item)
    reason: str = ""                   # required for write-offs/adjustments (audit + P&L)

    def __post_init__(self) -> None:
        if self.amount_gbp < 0:
            raise ValueError("amount_gbp is a magnitude; must be >= 0")

    @property
    def signed_amount(self) -> float:
        return round(self.amount_gbp if self.event_type.is_debit else -self.amount_gbp, 2)

    @property
    def affects_pnl(self) -> bool:
        """Write-offs are a P&L expense; interest is P&L income. Bills/payments
        move cash/receivables, not P&L directly."""
        return self.event_type in (
            LedgerEventType.WRITE_OFF_CREDIT,
            LedgerEventType.INTEREST_DEBIT,
        )


@dataclass
class InvoiceOpenItem:
    """Open-item view of one invoice: how much of it remains outstanding after
    allocation, and whether it's currently under dispute (excluded from ageing)."""
    invoice_ref: str
    issued_gbp: float
    issue_date: dt.date
    allocated_gbp: float = 0.0
    disputed: bool = False

    @property
    def outstanding_gbp(self) -> float:
        return round(self.issued_gbp - self.allocated_gbp, 2)

    @property
    def is_settled(self) -> bool:
        return self.outstanding_gbp <= 0.005


@dataclass
class AllocationResult:
    open_items: List[InvoiceOpenItem]
    unallocated_credit_gbp: float               # customer paid more than invoiced/allocated
    allocations: List[Tuple[str, str, float]]   # (payment_event_id, invoice_ref, amount)

    def outstanding_by_invoice(self, include_disputed: bool = True) -> Dict[str, float]:
        return {
            oi.invoice_ref: oi.outstanding_gbp
            for oi in self.open_items
            if (include_disputed or not oi.disputed) and not oi.is_settled
        }

    @property
    def total_outstanding_gbp(self) -> float:
        return round(sum(oi.outstanding_gbp for oi in self.open_items if not oi.is_settled), 2)

    @property
    def total_undisputed_outstanding_gbp(self) -> float:
        return round(
            sum(oi.outstanding_gbp for oi in self.open_items
                if not oi.is_settled and not oi.disputed),
            2,
        )

    def check_conserved(self, total_payments_gbp: float) -> None:
        """R15 CONTROL — an open-item allocation must (a) never OVER-allocate an
        invoice (outstanding can never go negative) and (b) CONSERVE the cash it
        was handed: every pound of payment credit is either allocated to an
        invoice or left as unallocated credit, none created or destroyed.

        `total_payments_gbp` is supplied by the EXTERNAL cash-received figure (the
        payments subsystem), NOT re-summed from these allocations — so a
        misallocation that drops or duplicates a pound moves the internal total
        away from the external one and this RAISES (independence, not tautology).
        FAIL-CLOSED: a non-zero cash total with no allocations and no unallocated
        credit raises rather than passing.

        Raises AllocationInvariantError on any violation.
        """
        problems: List[str] = []
        for oi in self.open_items:
            if oi.outstanding_gbp < -_ALLOC_TOLERANCE_GBP:
                problems.append(
                    f"invoice {oi.invoice_ref} over-allocated: "
                    f"allocated {oi.allocated_gbp} > issued {oi.issued_gbp}"
                )
        allocated_total = round(sum(a[2] for a in self.allocations), 2)
        accounted = round(allocated_total + self.unallocated_credit_gbp, 2)
        external = round(total_payments_gbp, 2)
        if abs(accounted - external) > _ALLOC_TOLERANCE_GBP:
            problems.append(
                f"cash not conserved: allocated {allocated_total} + unallocated "
                f"{self.unallocated_credit_gbp} = {accounted} != payments {external}"
            )
        if problems:
            raise AllocationInvariantError("; ".join(problems))


def _sort_key(e: LedgerEvent) -> Tuple[dt.date, str]:
    # deterministic, arrival-order-independent ordering (C-S2 replay determinism)
    return (e.valid_time, e.event_id)


# ---------------------------------------------------------------------------
# R15 CONTROLS — invariant checks that MUST be able to FAIL on their own defect.
#
# Design note (R15): the balance/allocation invariants were previously only
# IMPLICIT (correct code, but nothing that raises when they are violated) — an
# unchecked invariant cannot fire, which R15 ranks as worse than no control.
# These two controls make the invariants FAILABLE and are deliberately
# INDEPENDENT of the value they check (they reconcile against a total supplied by
# an EXTERNAL source — the GL control account / cash-received subsystem — not one
# re-derived from the very same event set), so they are not tautologies, and they
# FAIL-CLOSED (a missing/dropped event or empty set with a non-zero external
# expectation RAISES, it does not pass silently).
# ---------------------------------------------------------------------------

_RECON_TOLERANCE_GBP = 0.005
_ALLOC_TOLERANCE_GBP = 0.005


class LedgerReconciliationError(Exception):
    """Raised when a ledger's own debit/credit/balance totals disagree with the
    externally-held control totals (a dropped/duplicated/tampered event)."""


class AllocationInvariantError(Exception):
    """Raised when an open-item allocation over-allocates an invoice or fails to
    conserve the cash it was handed (a misallocated remittance)."""


class AccountLedger:
    """Append-only event store for ONE account, computing either a rolling
    balance (balance-based) or an open-item allocation (open-item) from the SAME
    events. Which view is 'authoritative' is the account's accounting model, but
    BOTH views are always computable — the events don't change."""

    def __init__(self, account_id: str) -> None:
        self.account_id = account_id
        self._events: Dict[str, LedgerEvent] = {}   # event_id -> event (dedup store)

    # --- ingest (idempotent, order-independent) ---
    def post(self, event: LedgerEvent) -> bool:
        """Post an event. Returns True if newly stored, False if a duplicate
        event_id was already present (C-S2 idempotency — harmless double-post)."""
        if event.account_id != self.account_id:
            raise ValueError(
                f"event {event.event_id} is for account {event.account_id}, "
                f"not {self.account_id}"
            )
        if event.event_id in self._events:
            return False
        self._events[event.event_id] = event
        return True

    def events(self) -> List[LedgerEvent]:
        return sorted(self._events.values(), key=_sort_key)

    # --- balance-based view ---
    def balance(self, as_of: Optional[dt.date] = None) -> float:
        """Rolling balance as of a date (inclusive). Positive ⇒ arrears; negative
        ⇒ in credit. Pure function of the event set — order of arrival irrelevant."""
        total = 0.0
        for e in self._events.values():
            if as_of is not None and e.valid_time > as_of:
                continue
            total += e.signed_amount
        return round(total, 2)

    def is_in_credit(self, as_of: Optional[dt.date] = None) -> bool:
        return self.balance(as_of) < 0

    def balance_summary(self, as_of: Optional[dt.date] = None) -> dict:
        bal = self.balance(as_of)
        debits = round(sum(e.amount_gbp for e in self._events.values()
                           if e.event_type.is_debit
                           and (as_of is None or e.valid_time <= as_of)), 2)
        credits = round(sum(e.amount_gbp for e in self._events.values()
                            if not e.event_type.is_debit
                            and (as_of is None or e.valid_time <= as_of)), 2)
        return {
            "account_id": self.account_id,
            "as_of": as_of.isoformat() if as_of else None,
            "balance_gbp": bal,
            "total_debits_gbp": debits,
            "total_credits_gbp": credits,
            "in_arrears": bal > 0,
            "in_credit": bal < 0,
            "arrears_gbp": bal if bal > 0 else 0.0,
            "credit_gbp": round(-bal, 2) if bal < 0 else 0.0,
        }

    def reconcile(
        self,
        expected_debits_gbp: float,
        expected_credits_gbp: float,
        as_of: Optional[dt.date] = None,
    ) -> dict:
        """R15 CONTROL — reconcile this ledger against EXTERNAL control totals.

        A real supplier reconciles its AR ledger against an independently-held
        control account (total billed by the invoicing subsystem; total cash
        received by the payments subsystem). This control does the same: it
        recomputes the ledger's own debit and credit sums and asserts they match
        the externally-supplied expectations, and that balance == debits - credits.

        INDEPENDENT (not a tautology): the expectations come from OUTSIDE the event
        set, so dropping/duplicating an event moves the ledger's own sum away from
        the unchanged external total and this RAISES. FAIL-CLOSED: an empty ledger
        with a non-zero expectation raises rather than passing on emptiness.

        Returns a reconciliation dict on success; raises LedgerReconciliationError
        on any mismatch (basis: settled — these are ledger-posted facts, R14).
        """
        actual_debits = round(sum(
            e.amount_gbp for e in self._events.values()
            if e.event_type.is_debit and (as_of is None or e.valid_time <= as_of)
        ), 2)
        actual_credits = round(sum(
            e.amount_gbp for e in self._events.values()
            if not e.event_type.is_debit and (as_of is None or e.valid_time <= as_of)
        ), 2)
        bal = self.balance(as_of)
        exp_debits = round(expected_debits_gbp, 2)
        exp_credits = round(expected_credits_gbp, 2)
        problems: List[str] = []
        if abs(actual_debits - exp_debits) > _RECON_TOLERANCE_GBP:
            problems.append(
                f"debit total {actual_debits} != control {exp_debits}"
            )
        if abs(actual_credits - exp_credits) > _RECON_TOLERANCE_GBP:
            problems.append(
                f"credit total {actual_credits} != control {exp_credits}"
            )
        # Internal consistency: the rolling balance must equal debits - credits
        # computed via the SEPARATE amount_gbp/is_debit path (catches a sign bug in
        # signed_amount independently of the drop-detection above).
        if abs(bal - round(actual_debits - actual_credits, 2)) > _RECON_TOLERANCE_GBP:
            problems.append(
                f"balance {bal} != debits-credits {round(actual_debits - actual_credits, 2)}"
            )
        if problems:
            raise LedgerReconciliationError(
                f"account {self.account_id} reconciliation failed: " + "; ".join(problems)
            )
        return {
            "account_id": self.account_id,
            "as_of": as_of.isoformat() if as_of else None,
            "debits_gbp": actual_debits,
            "credits_gbp": actual_credits,
            "balance_gbp": bal,
            "basis": "settled",
        }

    # --- R15 WIRING: run the reconcile controls on the LIVE ledger against the
    #     INDEPENDENT invoicing subsystem (company/billing/invoice.py). These make
    #     the dormant controls ACTIVE: a real operation now surfaces a violation
    #     (raises) instead of the invariant only being checkable on demand. The
    #     `invoice_source` is duck-typed (InvoiceControlSource) — the ledger never
    #     reads the invoice store itself, preserving both independence and the
    #     typed-seam preference. ---
    def verify_against_invoicing(self, invoice_source, as_of: Optional[dt.date] = None) -> dict:
        """R15 CONTROL (wired) — reconcile this ledger's billed/paid movements
        against the INDEPENDENT invoicing register + cash book.

        Pulls the issued-invoice total and the cash-received total from
        `invoice_source` (NOT re-summed from these events) and asserts the ledger's
        own BILL_DEBIT / PAYMENT_CREDIT totals equal them. A dropped, duplicated or
        tampered bill/payment in the ledger moves its own total away from the
        unchanged external control and this RAISES (independence, not tautology).

        FAIL-CLOSED / FAIL-SILENT (R15): if the source cannot answer (missing
        accessor, or returns None) that is a FAILED control, not a free pass — it
        RAISES. When the ledger holds ONLY bills+payments the full reconcile()
        control (incl. its balance-consistency leg) is run directly against the
        external totals; when it also holds interest/adjustment/write-off journals
        (separate control accounts, each guarded by its own control), only the two
        invoicing-authoritative movements are tied out (the classic AR three-way
        match: sub-ledger ↔ invoice register ↔ cash book).

        Raises LedgerReconciliationError on any mismatch. Basis: settled (R14).
        """
        aid = self.account_id
        try:
            expected_debits = invoice_source.issued_debits_gbp(aid, as_of=as_of)
            expected_credits = invoice_source.cash_received_gbp(aid, as_of=as_of)
        except AttributeError as exc:
            raise LedgerReconciliationError(
                f"account {aid}: invoice control source cannot supply totals "
                f"({exc}) — an unavailable control is a FAILED control (R15)"
            ) from exc
        if expected_debits is None or expected_credits is None:
            raise LedgerReconciliationError(
                f"account {aid}: invoice control source returned no total "
                f"(debits={expected_debits!r}, credits={expected_credits!r}) — fail-closed"
            )
        other = [
            e for e in self._events.values()
            if e.event_type not in (LedgerEventType.BILL_DEBIT, LedgerEventType.PAYMENT_CREDIT)
            and (as_of is None or e.valid_time <= as_of)
        ]
        if not other:
            # Pure bills+payments — run the full existing reconcile() control.
            return self.reconcile(expected_debits, expected_credits, as_of)
        # Mixed ledger — tie out only the invoicing-authoritative movements.
        actual_bill_debits = round(sum(
            e.amount_gbp for e in self._events.values()
            if e.event_type == LedgerEventType.BILL_DEBIT
            and (as_of is None or e.valid_time <= as_of)
        ), 2)
        actual_payments = round(sum(
            e.amount_gbp for e in self._events.values()
            if e.event_type == LedgerEventType.PAYMENT_CREDIT
            and (as_of is None or e.valid_time <= as_of)
        ), 2)
        problems: List[str] = []
        if abs(actual_bill_debits - round(expected_debits, 2)) > _RECON_TOLERANCE_GBP:
            problems.append(
                f"billed total {actual_bill_debits} != invoicing register {round(expected_debits, 2)}"
            )
        if abs(actual_payments - round(expected_credits, 2)) > _RECON_TOLERANCE_GBP:
            problems.append(
                f"cash total {actual_payments} != cash book {round(expected_credits, 2)}"
            )
        if problems:
            raise LedgerReconciliationError(
                f"account {aid} invoicing reconciliation failed: " + "; ".join(problems)
            )
        return {
            "account_id": aid,
            "as_of": as_of.isoformat() if as_of else None,
            "billed_gbp": actual_bill_debits,
            "cash_received_gbp": actual_payments,
            "basis": "settled",
            "scope": "invoicing_movements",
        }

    def verify_allocation_conserved(
        self,
        invoice_source,
        disputed_refs: Iterable[str] = (),
        as_of: Optional[dt.date] = None,
    ) -> "AllocationResult":
        """R15 CONTROL (wired) — run the LIVE open-item allocation and assert it
        CONSERVES the INDEPENDENT cash-received total from the cash book (invoice.py),
        never a figure re-summed from the ledger's own events.

        Raises AllocationInvariantError on any misallocation (over-allocation or
        cash created/destroyed). FAIL-CLOSED: if the cash total is unavailable the
        control fails rather than silently passing. Returns the AllocationResult.
        """
        aid = self.account_id
        try:
            cash = invoice_source.cash_received_gbp(aid, as_of=as_of)
        except AttributeError as exc:
            raise AllocationInvariantError(
                f"account {aid}: cash control source unavailable ({exc}) — "
                f"a FAILED control (R15)"
            ) from exc
        if cash is None:
            raise AllocationInvariantError(
                f"account {aid}: cash control source returned no total — fail-closed"
            )
        result = self.allocate(disputed_refs=disputed_refs, as_of=as_of)
        result.check_conserved(total_payments_gbp=cash)
        return result

    # --- open-item view ---
    def allocate(
        self,
        disputed_refs: Iterable[str] = (),
        as_of: Optional[dt.date] = None,
    ) -> AllocationResult:
        """Allocate payment credits to invoices per remittance-else-oldest-first.

        Pure function of the event set (deterministic replay, C-S2): invoices are
        opened in (issue_date, invoice_ref) order and payments applied in
        (valid_time, event_id) order, regardless of the order they were posted.
        Disputed invoices are NOT allocated against by oldest-first and are
        excluded from undisputed-outstanding — matching the rule that a disputed
        invoice is held out of ageing/dunning while the dispute is open.
        """
        disputed = set(disputed_refs)
        events = [e for e in self.events() if as_of is None or e.valid_time <= as_of]

        # 1. Build open items from bill debits (+ debit adjustments carrying an invoice_ref).
        items: Dict[str, InvoiceOpenItem] = {}
        for e in events:
            if e.event_type in (LedgerEventType.BILL_DEBIT, LedgerEventType.ADJUSTMENT_DEBIT) \
                    and e.invoice_ref:
                oi = items.get(e.invoice_ref)
                if oi is None:
                    items[e.invoice_ref] = InvoiceOpenItem(
                        invoice_ref=e.invoice_ref,
                        issued_gbp=round(e.amount_gbp, 2),
                        issue_date=e.valid_time,
                        disputed=e.invoice_ref in disputed,
                    )
                else:
                    oi.issued_gbp = round(oi.issued_gbp + e.amount_gbp, 2)

        # Credit adjustments / write-offs carrying an invoice_ref reduce that invoice.
        for e in events:
            if e.event_type in (LedgerEventType.ADJUSTMENT_CREDIT, LedgerEventType.WRITE_OFF_CREDIT) \
                    and e.invoice_ref and e.invoice_ref in items:
                items[e.invoice_ref].allocated_gbp = round(
                    items[e.invoice_ref].allocated_gbp + e.amount_gbp, 2
                )

        allocations: List[Tuple[str, str, float]] = []
        unallocated_credit = 0.0

        def _open_oldest_first(exclude_disputed: bool) -> List[InvoiceOpenItem]:
            pool = [
                oi for oi in sorted(items.values(), key=lambda o: (o.issue_date, o.invoice_ref))
                if not oi.is_settled and (not exclude_disputed or not oi.disputed)
            ]
            return pool

        # 2. Apply payment credits (and refund debits reduce available credit).
        for e in events:
            if e.event_type == LedgerEventType.PAYMENT_CREDIT:
                remaining = round(e.amount_gbp, 2)
                # 2a. remittance-directed first (may include disputed refs — customer's call)
                for ref in e.remittance:
                    if remaining <= 0.005:
                        break
                    oi = items.get(ref)
                    if oi is None or oi.is_settled:
                        continue
                    apply = min(remaining, oi.outstanding_gbp)
                    oi.allocated_gbp = round(oi.allocated_gbp + apply, 2)
                    allocations.append((e.event_id, ref, round(apply, 2)))
                    remaining = round(remaining - apply, 2)
                # 2b. oldest-first over non-disputed open items
                if remaining > 0.005:
                    for oi in _open_oldest_first(exclude_disputed=True):
                        if remaining <= 0.005:
                            break
                        apply = min(remaining, oi.outstanding_gbp)
                        if apply <= 0:
                            continue
                        oi.allocated_gbp = round(oi.allocated_gbp + apply, 2)
                        allocations.append((e.event_id, oi.invoice_ref, round(apply, 2)))
                        remaining = round(remaining - apply, 2)
                # 2c. anything left is an unallocated credit on the account
                if remaining > 0.005:
                    unallocated_credit = round(unallocated_credit + remaining, 2)

        return AllocationResult(
            open_items=list(items.values()),
            unallocated_credit_gbp=round(unallocated_credit, 2),
            allocations=allocations,
        )

    # --- bitemporal emission (model-agnostic downstream) ---
    def emit_to(self, log, entity_prefix: str = "account") -> int:
        """Write every ledger event into a BitemporalEventLog (the shared seam,
        company/interfaces/bitemporal_event_log.py). Returns the count emitted.
        Downstream E-lane/three-clocks consume these bitemporal facts without ever
        needing to know which accounting model produced them."""
        n = 0
        for e in self.events():
            log.record(
                entity_id=f"{entity_prefix}:{e.account_id}",
                fact_type=f"ledger:{e.event_type.value}",
                valid_time=e.valid_time,
                transaction_time=e.transaction_time,
                value={
                    "event_id": e.event_id,
                    "account_id": e.account_id,
                    "event_type": e.event_type.value,
                    "amount_gbp": round(e.amount_gbp, 2),
                    "signed_amount_gbp": e.signed_amount,
                    "invoice_ref": e.invoice_ref,
                    "remittance": list(e.remittance),
                    "reason": e.reason,
                },
            )
            n += 1
        return n


class LedgerBook:
    """Portfolio of per-account ledgers. Routes an event to its account's ledger
    (creating it on first sight) — tolerant of events arriving interleaved across
    accounts, one at a time, in any order (C-S1)."""

    def __init__(self) -> None:
        self._ledgers: Dict[str, AccountLedger] = {}

    def ledger(self, account_id: str) -> AccountLedger:
        led = self._ledgers.get(account_id)
        if led is None:
            led = AccountLedger(account_id)
            self._ledgers[account_id] = led
        return led

    def post(self, event: LedgerEvent) -> bool:
        return self.ledger(event.account_id).post(event)

    def accounts(self) -> List[str]:
        return sorted(self._ledgers)

    def portfolio_balance_gbp(self, as_of: Optional[dt.date] = None) -> float:
        return round(sum(l.balance(as_of) for l in self._ledgers.values()), 2)

    def total_arrears_gbp(self, as_of: Optional[dt.date] = None) -> float:
        return round(sum(max(0.0, l.balance(as_of)) for l in self._ledgers.values()), 2)

    def verify_against_invoicing(
        self, invoice_source, as_of: Optional[dt.date] = None
    ) -> Dict[str, dict]:
        """R15 WIRING — portfolio reconciliation checkpoint. Reconciles EVERY
        account's ledger against the independent invoicing subsystem. FAIL-CLOSED:
        propagates (raises) on the first account whose ledger disagrees with its
        control totals — a single tampered account fails the whole checkpoint rather
        than being averaged away. Returns per-account reconciliation dicts on a fully
        clean portfolio."""
        results: Dict[str, dict] = {}
        for aid in self.accounts():
            results[aid] = self._ledgers[aid].verify_against_invoicing(invoice_source, as_of)
        return results
