"""Direct Debit mandate and payment schedule management.

UK energy suppliers collect recurring payments via BACS Direct Debit.
This module manages DD mandates, payment schedules, and failed-payment
tracking — all from company-observable data (no SIM internals).

Mandate lifecycle: active → cancelled | failed → reinstated.
Failed DDs trigger debt escalation after 2 missed payments.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Literal


_DD_SCHEDULE_DAYS = 28  # standard BACS cycle


@dataclass
class DirectDebitMandate:
    customer_id: str
    mandate_reference: str
    bank_sort_code: str  # masked, e.g. "12-34-**"
    bank_account_last4: str
    monthly_amount_gbp: float
    status: Literal["active", "cancelled", "suspended"] = "active"
    setup_date: str = ""
    next_collection_date: str = ""
    failed_attempts: int = 0


@dataclass
class DDPaymentAttempt:
    mandate_reference: str
    customer_id: str
    attempt_date: str
    amount_gbp: float
    outcome: Literal["collected", "failed", "cancelled"]
    failure_reason: str = ""


class DirectDebitBook:
    """In-memory mandate + attempt store for the company billing layer."""

    def __init__(self):
        self._mandates: dict[str, DirectDebitMandate] = {}
        self._attempts: list[DDPaymentAttempt] = []

    def create_mandate(
        self,
        customer_id: str,
        sort_code: str,
        account_last4: str,
        monthly_amount_gbp: float,
        setup_date: str,
    ) -> DirectDebitMandate:
        """Register a new DD mandate and return it."""
        ref = f"DD-{customer_id}-{setup_date.replace('-', '')}"
        next_collect = _add_days(setup_date, _DD_SCHEDULE_DAYS)
        m = DirectDebitMandate(
            customer_id=customer_id,
            mandate_reference=ref,
            bank_sort_code=sort_code,
            bank_account_last4=account_last4,
            monthly_amount_gbp=monthly_amount_gbp,
            setup_date=setup_date,
            next_collection_date=next_collect,
        )
        self._mandates[customer_id] = m
        return m

    def get_mandate(self, customer_id: str) -> DirectDebitMandate | None:
        return self._mandates.get(customer_id)

    def active_mandates(self) -> list[DirectDebitMandate]:
        return [m for m in self._mandates.values() if m.status == "active"]

    def record_attempt(self, attempt: DDPaymentAttempt) -> None:
        """Record a collection attempt and update mandate state."""
        self._attempts.append(attempt)
        m = self._mandates.get(attempt.customer_id)
        if m is None:
            return
        if attempt.outcome == "collected":
            m.failed_attempts = 0
            m.next_collection_date = _add_days(attempt.attempt_date, _DD_SCHEDULE_DAYS)
        elif attempt.outcome == "failed":
            m.failed_attempts += 1
            if m.failed_attempts >= 2:
                m.status = "suspended"

    def cancel_mandate(self, customer_id: str) -> bool:
        m = self._mandates.get(customer_id)
        if m is None:
            return False
        m.status = "cancelled"
        return True

    def reinstate_mandate(self, customer_id: str) -> bool:
        m = self._mandates.get(customer_id)
        if m is None:
            return False
        m.status = "active"
        m.failed_attempts = 0
        return True

    def failed_mandates(self) -> list[DirectDebitMandate]:
        return [m for m in self._mandates.values() if m.status == "suspended"]

    def attempts_for_customer(self, customer_id: str) -> list[DDPaymentAttempt]:
        return [a for a in self._attempts if a.customer_id == customer_id]

    def failed_attempts_for_customer(self, customer_id: str) -> list[DDPaymentAttempt]:
        return [a for a in self.attempts_for_customer(customer_id) if a.outcome == "failed"]

    def dd_summary(self) -> dict:
        all_m = list(self._mandates.values())
        return {
            "total": len(all_m),
            "active": sum(1 for m in all_m if m.status == "active"),
            "suspended": sum(1 for m in all_m if m.status == "suspended"),
            "cancelled": sum(1 for m in all_m if m.status == "cancelled"),
            "total_monthly_gbp": round(
                sum(m.monthly_amount_gbp for m in all_m if m.status == "active"), 2
            ),
        }


def _add_days(date_str: str, days: int) -> str:
    d = date.fromisoformat(date_str)
    return (d + timedelta(days=days)).isoformat()
