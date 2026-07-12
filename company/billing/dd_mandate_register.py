"""Direct Debit Mandate Register (Phase GD).

OPEN DUPLICATION, NOT RESOLVED (2026-07-12, W5_1_banking_payment_rails,
M2 payments-maturity audit's "duplicated-register pair" finding,
docs/design/M2_PAYMENTS_AUDIT_DD_RAILS.md; corrected after an Expert Hour
review found an earlier version of this note wrongly claimed the
duplication was resolved/superseded): this module has ZERO live callers
anywhere in the codebase (confirmed by exhaustive grep) -- built and tested
in isolation (Phase GD), never wired to anything. `company/billing/
direct_debit.py::DirectDebitBook` is the one WITH a live caller
(`simulation/dd_collection_book.py`) and is therefore the practical,
de-facto mandate store in the actual simulation today. That is a fact about
which one runs, not a judgement that DirectDebitBook is the better design --
this module's `as_of`-parameterised API is, if anything, the more
epistemically disciplined of the two (DirectDebitBook's `create_mandate()`
takes a plain date string with no as_of/point-in-time framing). The
duplication itself is REAL and UNRESOLVED: nothing in the codebase prevents
a second module from also writing mandate state, no merge or migration has
happened, and the M2 audit's own instruction ("consolidation needed before
further wiring compounds the duplication") has not been carried out.
Registered here per R10 (nothing may be simplified silently) as an OPEN gap
for a future pass -- not closed by this note.

UK energy suppliers collect most domestic bills via BACS Direct Debit.
The Direct Debit Guarantee (DDG) scheme, administered by Pay.UK/BACS,
requires suppliers to:

  - Hold a valid mandate (instruction) for each DD payer
  - Give advance notice of amount and collection date (typically 10 working
    days, though suppliers may agree a shorter advance notice period with
    customers)
  - Allow customers to cancel mandates at any time (via bank or supplier)
  - Process indemnity claims within 2 working days if customer requests refund
    of an incorrect DD collection

Mandate lifecycle:
  ACTIVE → can be suspended or cancelled
  SUSPENDED → temporarily halted (e.g., customer requested pause); re-activated by reinstate
  FAILED → bank returned the DD instruction (insufficient funds, account closed)
  CANCELLED → mandate terminated; customer must set up a new one to resume DD
  REINSTATED → re-activated from SUSPENDED; ACTIVE again

Variable DD: most energy suppliers adjust the monthly collection amount to
match estimated annual consumption. Changes require advance notice.

Failed DD handling:
  - Bank returns within 3 working days of presentation date
  - Supplier may attempt 1 re-presentation within 8 days
  - After 2 failures: mandate auto-cancels in many schemes
  - Failed DD triggers a missed payment record in the payment_ledger

This module tracks the mandate, not individual payments.
See payment_ledger.py for individual payment records.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

_BACS_ADVANCE_NOTICE_DAYS = 10
_MAX_PAYMENT_DAY = 28   # no DD collected on day 29/30/31 (month-end variance)
_MIN_PAYMENT_DAY = 1


class DDMandateStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REINSTATED = "reinstated"   # treated as ACTIVE operationally


@dataclass(frozen=True)
class DDMandateRecord:
    mandate_ref: str            # DDM-NNNNN
    account_id: str
    setup_date: dt.date
    payment_day: int            # day of month (1–28)
    amount_gbp: float           # monthly collection amount
    status: DDMandateStatus = DDMandateStatus.ACTIVE
    last_updated: Optional[dt.date] = None
    cancellation_date: Optional[dt.date] = None
    failed_count: int = 0       # number of BACS returns

    @property
    def is_active(self) -> bool:
        return self.status in (DDMandateStatus.ACTIVE, DDMandateStatus.REINSTATED)

    @property
    def is_suspended(self) -> bool:
        return self.status == DDMandateStatus.SUSPENDED

    @property
    def is_failed(self) -> bool:
        return self.status == DDMandateStatus.FAILED

    @property
    def is_cancelled(self) -> bool:
        return self.status == DDMandateStatus.CANCELLED

    @property
    def is_collectable(self) -> bool:
        return self.status in (DDMandateStatus.ACTIVE, DDMandateStatus.REINSTATED)

    @property
    def next_collection_due(self) -> Optional[int]:
        if not self.is_collectable:
            return None
        return self.payment_day

    def mandate_summary(self) -> str:
        return (
            f"Mandate {self.mandate_ref} acct={self.account_id}: "
            f"£{self.amount_gbp:.2f}/mo day={self.payment_day} "
            f"status={self.status.value} fails={self.failed_count}"
        )


class DDMandateRegister:

    def __init__(self) -> None:
        self._records: List[DDMandateRecord] = []
        self._counter: int = 0
        # index: account_id → list of mandate_refs
        self._account_index: Dict[str, List[str]] = {}

    def _next_ref(self) -> str:
        self._counter += 1
        return f"DDM-{self._counter:05d}"

    def setup_mandate(
        self,
        account_id: str,
        payment_day: int,
        amount_gbp: float,
        setup_date: dt.date,
    ) -> DDMandateRecord:
        if not (_MIN_PAYMENT_DAY <= payment_day <= _MAX_PAYMENT_DAY):
            raise ValueError(
                f"payment_day must be 1–{_MAX_PAYMENT_DAY}; got {payment_day}"
            )
        if amount_gbp <= 0:
            raise ValueError(f"amount_gbp must be positive; got {amount_gbp}")
        ref = self._next_ref()
        record = DDMandateRecord(
            mandate_ref=ref,
            account_id=account_id,
            setup_date=setup_date,
            payment_day=payment_day,
            amount_gbp=amount_gbp,
        )
        self._records.append(record)
        self._account_index.setdefault(account_id, []).append(ref)
        return record

    def _get(self, mandate_ref: str) -> Optional[DDMandateRecord]:
        for r in self._records:
            if r.mandate_ref == mandate_ref:
                return r
        return None

    def _replace(self, i: int, updated: DDMandateRecord) -> None:
        self._records[i] = updated

    def _update(self, mandate_ref: str, **kwargs) -> DDMandateRecord:
        for i, r in enumerate(self._records):
            if r.mandate_ref == mandate_ref:
                updated = DDMandateRecord(
                    mandate_ref=r.mandate_ref,
                    account_id=r.account_id,
                    setup_date=r.setup_date,
                    payment_day=kwargs.get("payment_day", r.payment_day),
                    amount_gbp=kwargs.get("amount_gbp", r.amount_gbp),
                    status=kwargs.get("status", r.status),
                    last_updated=kwargs.get("last_updated", r.last_updated),
                    cancellation_date=kwargs.get("cancellation_date", r.cancellation_date),
                    failed_count=kwargs.get("failed_count", r.failed_count),
                )
                self._records[i] = updated
                return updated
        raise KeyError(f"Mandate {mandate_ref} not found")

    def update_amount(
        self, mandate_ref: str, new_amount: float, as_of: dt.date
    ) -> DDMandateRecord:
        if new_amount <= 0:
            raise ValueError(f"amount_gbp must be positive; got {new_amount}")
        return self._update(mandate_ref, amount_gbp=new_amount, last_updated=as_of)

    def suspend(self, mandate_ref: str, as_of: dt.date) -> DDMandateRecord:
        return self._update(
            mandate_ref, status=DDMandateStatus.SUSPENDED, last_updated=as_of
        )

    def reinstate(self, mandate_ref: str, as_of: dt.date) -> DDMandateRecord:
        return self._update(
            mandate_ref, status=DDMandateStatus.REINSTATED, last_updated=as_of
        )

    def cancel(self, mandate_ref: str, as_of: dt.date) -> DDMandateRecord:
        return self._update(
            mandate_ref,
            status=DDMandateStatus.CANCELLED,
            cancellation_date=as_of,
            last_updated=as_of,
        )

    def record_failure(self, mandate_ref: str, as_of: dt.date) -> DDMandateRecord:
        r = self._get(mandate_ref)
        if r is None:
            raise KeyError(f"Mandate {mandate_ref} not found")
        new_failed = r.failed_count + 1
        # Auto-cancel after 2 failures (standard bank scheme rule)
        new_status = DDMandateStatus.FAILED if new_failed < 2 else DDMandateStatus.CANCELLED
        return self._update(
            mandate_ref,
            status=new_status,
            failed_count=new_failed,
            last_updated=as_of,
        )

    def active_mandates(self) -> List[DDMandateRecord]:
        return [r for r in self._records if r.is_active]

    def failed_mandates(self) -> List[DDMandateRecord]:
        return [r for r in self._records if r.is_failed]

    def cancelled_mandates(self) -> List[DDMandateRecord]:
        return [r for r in self._records if r.is_cancelled]

    def mandate_for_account(self, account_id: str) -> Optional[DDMandateRecord]:
        refs = self._account_index.get(account_id, [])
        if not refs:
            return None
        # Return the most recently added active mandate for the account
        for ref in reversed(refs):
            r = self._get(ref)
            if r and r.is_active:
                return r
        # Fallback: return last mandate regardless of status
        return self._get(refs[-1])

    def total_monthly_collection_gbp(self) -> float:
        return sum(r.amount_gbp for r in self._records if r.is_collectable)

    def accounts_without_active_mandate(
        self, account_ids: List[str]
    ) -> List[str]:
        accounts_with_dd = {r.account_id for r in self._records if r.is_active}
        return [a for a in account_ids if a not in accounts_with_dd]

    def dd_mandate_summary(self) -> str:
        n = len(self._records)
        n_active = len(self.active_mandates())
        n_failed = len(self.failed_mandates())
        n_cancelled = len(self.cancelled_mandates())
        monthly = self.total_monthly_collection_gbp()
        return (
            f"DD Mandate Register: {n} mandates "
            f"({n_active} active, {n_failed} failed, {n_cancelled} cancelled). "
            f"Monthly collection: £{monthly:,.2f}."
        )
