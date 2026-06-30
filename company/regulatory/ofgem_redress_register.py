"""Ofgem Redress Payment Register (Phase FZ).

Ofgem's redress scheme allows enforcement actions to be resolved by
directing a supplier to make payments to specified beneficiaries rather
than (or in addition to) financial penalties. Redress payments:

- Are directed to charities, consumer bodies, or community funds —
  NOT to the government or Ofgem itself
- Are agreed as part of a consent order or undertaking
- Must be paid within a specified deadline (typically 30-90 days)
- Are published on Ofgem\'s website for transparency
- Do NOT reduce the supplier\'s licence penalty exposure separately

Common recipients specified by Ofgem:
  - Energy Saving Trust (energy efficiency advice)
  - National Energy Action (fuel poverty charity)
  - Citizens Advice (consumer advice and advocacy)
  - Community energy funds (local energy projects)
  - Vulnerable Customer Fund (direct customer compensation)

Redress is distinct from:
  - Financial penalties (s.30 Electricity Act / gas equivalent)
  - Customer-specific compensation (GSOP payments)
  - Back-billing credits (returned to individual customers)

Notable recent cases: Avro (2020 £650k), Utilita (2021 £250k),
Opus (2019 £4.5M), nPower (2018 £26M).
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

_PAYMENT_DEADLINE_DAYS_DEFAULT = 30


class RedressPaymentRecipient(str, Enum):
    ENERGY_SAVING_TRUST = "energy_saving_trust"
    NATIONAL_ENERGY_ACTION = "national_energy_action"
    CITIZENS_ADVICE = "citizens_advice"
    COMMUNITY_ENERGY_FUND = "community_energy_fund"
    VULNERABLE_CUSTOMER_FUND = "vulnerable_customer_fund"
    OTHER_SPECIFIED = "other_specified"


class RedressPaymentStatus(str, Enum):
    AGREED = "agreed"          # consent order / undertaking signed
    PAID = "paid"              # payment made and confirmed
    OVERDUE = "overdue"        # deadline passed, not paid
    CANCELLED = "cancelled"    # enforcement action withdrawn


@dataclass(frozen=True)
class RedressPaymentRecord:
    redress_id: str               # RD-NNNNN
    agreed_date: dt.date          # date of consent order / undertaking
    recipient: RedressPaymentRecipient
    amount_gbp: float
    related_breach_description: str
    payment_deadline: dt.date
    status: RedressPaymentStatus = RedressPaymentStatus.AGREED
    payment_date: Optional[dt.date] = None

    @property
    def is_paid(self) -> bool:
        return self.status == RedressPaymentStatus.PAID

    @property
    def is_overdue(self) -> bool:
        return self.status == RedressPaymentStatus.OVERDUE

    def is_overdue_as_of(self, as_of: dt.date) -> bool:
        if self.status in (RedressPaymentStatus.PAID, RedressPaymentStatus.CANCELLED):
            return False
        return as_of > self.payment_deadline

    @property
    def days_to_deadline(self) -> Optional[int]:
        if self.status != RedressPaymentStatus.AGREED:
            return None
        delta = (self.payment_deadline - dt.date.today()).days
        return delta

    def record_summary(self) -> str:
        return (
            f"Redress {self.redress_id}: £{self.amount_gbp:,.2f} → "
            f"{self.recipient.value} (status={self.status.value}) "
            f"deadline={self.payment_deadline}"
        )


class OfgemRedressRegister:

    def __init__(self) -> None:
        self._records: List[RedressPaymentRecord] = []
        self._counter: int = 0

    def _next_id(self) -> str:
        self._counter += 1
        return f"RD-{self._counter:05d}"

    def record_redress(
        self,
        agreed_date: dt.date,
        recipient: RedressPaymentRecipient,
        amount_gbp: float,
        related_breach_description: str,
        deadline_days: int = _PAYMENT_DEADLINE_DAYS_DEFAULT,
    ) -> RedressPaymentRecord:
        if amount_gbp <= 0:
            raise ValueError(f"Redress amount must be positive; got £{amount_gbp}")
        payment_deadline = agreed_date + dt.timedelta(days=deadline_days)
        record = RedressPaymentRecord(
            redress_id=self._next_id(),
            agreed_date=agreed_date,
            recipient=recipient,
            amount_gbp=amount_gbp,
            related_breach_description=related_breach_description,
            payment_deadline=payment_deadline,
        )
        self._records.append(record)
        return record

    def _update(self, redress_id: str, **kwargs) -> RedressPaymentRecord:
        for i, r in enumerate(self._records):
            if r.redress_id == redress_id:
                updated = RedressPaymentRecord(
                    redress_id=r.redress_id,
                    agreed_date=r.agreed_date,
                    recipient=r.recipient,
                    amount_gbp=r.amount_gbp,
                    related_breach_description=r.related_breach_description,
                    payment_deadline=r.payment_deadline,
                    status=kwargs.get("status", r.status),
                    payment_date=kwargs.get("payment_date", r.payment_date),
                )
                self._records[i] = updated
                return updated
        raise KeyError(f"Redress record {redress_id} not found")

    def mark_paid(
        self, redress_id: str, payment_date: dt.date
    ) -> RedressPaymentRecord:
        return self._update(
            redress_id, status=RedressPaymentStatus.PAID, payment_date=payment_date
        )

    def mark_overdue(self, redress_id: str) -> RedressPaymentRecord:
        return self._update(redress_id, status=RedressPaymentStatus.OVERDUE)

    def cancel(self, redress_id: str) -> RedressPaymentRecord:
        return self._update(redress_id, status=RedressPaymentStatus.CANCELLED)

    def pending_payments(self, as_of: dt.date) -> List[RedressPaymentRecord]:
        return [
            r for r in self._records
            if r.status == RedressPaymentStatus.AGREED and not r.is_overdue_as_of(as_of)
        ]

    def overdue_payments(self, as_of: dt.date) -> List[RedressPaymentRecord]:
        return [r for r in self._records if r.is_overdue_as_of(as_of)]

    def by_recipient(
        self, recipient: RedressPaymentRecipient
    ) -> List[RedressPaymentRecord]:
        return [r for r in self._records if r.recipient == recipient]

    def total_paid_gbp(self) -> float:
        return sum(r.amount_gbp for r in self._records if r.is_paid)

    def total_outstanding_gbp(self, as_of: dt.date) -> float:
        return sum(
            r.amount_gbp for r in self._records
            if r.status not in (RedressPaymentStatus.PAID, RedressPaymentStatus.CANCELLED)
        )

    def all_paid(self) -> bool:
        return all(
            r.status in (RedressPaymentStatus.PAID, RedressPaymentStatus.CANCELLED)
            for r in self._records
        )

    def redress_register_summary(self, as_of: dt.date) -> str:
        n = len(self._records)
        n_paid = sum(1 for r in self._records if r.is_paid)
        n_overdue = len(self.overdue_payments(as_of))
        total = sum(r.amount_gbp for r in self._records)
        outstanding = self.total_outstanding_gbp(as_of)
        return (
            f"Ofgem Redress Register ({as_of}): {n} orders "
            f"({n_paid} paid, {n_overdue} overdue). "
            f"Total agreed: £{total:,.2f}. Outstanding: £{outstanding:,.2f}."
        )
