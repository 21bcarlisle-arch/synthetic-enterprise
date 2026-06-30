"""Customer Service Ticket Book (Phase EW).

Customer contacts are a primary input to:
- Resentment Ledger (friction events)
- Ofgem Scorecard (complaints per 100k, 8-week resolution)
- Consumer Duty assessment (fair outcomes)

This module models the lifecycle of customer service tickets:
1. OPEN: contact received, ticket raised
2. IN_PROGRESS: agent handling
3. RESOLVED: customer satisfied, ticket closed
4. ESCALATED: referred to specialist/ombudsman
5. CLOSED_UNRESOLVED: customer gave up or time-boxed out

Key regulatory obligations:
- SLC 18.7: acknowledge complaints within 3 working days
- SLC 18.9: full response within 8 weeks or deadlock letter
- Ofgem: complaint upheld at ombudsman = 3x cost + GRI damage
- Consumer Duty: evidence fair treatment outcomes
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class TicketCategory(str, Enum):
    BILLING_QUERY = "billing_query"
    METER_READING = "meter_reading"
    TARIFF_COMPLAINT = "tariff_complaint"
    DEBT_NEGOTIATION = "debt_negotiation"
    SMART_METER = "smart_meter"
    SWITCHING = "switching"
    VULNERABILITY = "vulnerability"
    COMPENSATION_CLAIM = "compensation_claim"
    OTHER = "other"


class TicketStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    ESCALATED = "escalated"
    CLOSED_UNRESOLVED = "closed_unresolved"


_ACKNOWLEDGEMENT_DEADLINE_WD = 3     # SLC 18.7
_FULL_RESPONSE_DEADLINE_DAYS = 56    # 8 weeks, SLC 18.9


def _add_working_days(date: dt.date, wd: int) -> dt.date:
    current = date
    added = 0
    while added < wd:
        current += dt.timedelta(days=1)
        if current.weekday() < 5:
            added += 1
    return current


@dataclass(frozen=True)
class ServiceTicket:
    ticket_id: str
    account_id: str
    category: TicketCategory
    opened_at: dt.date
    status: TicketStatus
    resolved_at: Optional[dt.date] = None
    escalated_at: Optional[dt.date] = None
    acknowledged_at: Optional[dt.date] = None
    compensation_offered_gbp: float = 0.0

    @property
    def acknowledgement_deadline(self) -> dt.date:
        return _add_working_days(self.opened_at, _ACKNOWLEDGEMENT_DEADLINE_WD)

    @property
    def full_response_deadline(self) -> dt.date:
        return self.opened_at + dt.timedelta(days=_FULL_RESPONSE_DEADLINE_DAYS)

    def is_acknowledgement_overdue(self, as_of: dt.date) -> bool:
        if self.acknowledged_at is not None:
            return False
        return as_of > self.acknowledgement_deadline

    def is_response_overdue(self, as_of: dt.date) -> bool:
        if self.status in (TicketStatus.RESOLVED, TicketStatus.CLOSED_UNRESOLVED):
            return False
        return as_of > self.full_response_deadline

    def is_escalated(self) -> bool:
        return self.status == TicketStatus.ESCALATED

    def days_to_resolve(self) -> Optional[int]:
        if self.resolved_at is None:
            return None
        return (self.resolved_at - self.opened_at).days

    def ticket_summary(self) -> str:
        return (
            "Ticket " + self.ticket_id + " (" + self.account_id + "): "
            + self.category.value + " " + self.status.value
            + (" resolved in " + str(self.days_to_resolve()) + "d" if self.resolved_at else "")
        )


class ServiceTicketBook:

    def __init__(self) -> None:
        self._tickets: List[ServiceTicket] = []
        self._next_id = 1

    def open_ticket(
        self,
        account_id: str,
        category: TicketCategory,
        opened_at: dt.date,
    ) -> ServiceTicket:
        ticket_id = "TKT-" + str(self._next_id).zfill(6)
        self._next_id += 1
        ticket = ServiceTicket(
            ticket_id=ticket_id,
            account_id=account_id,
            category=category,
            opened_at=opened_at,
            status=TicketStatus.OPEN,
        )
        self._tickets.append(ticket)
        return ticket

    def update_status(
        self,
        ticket_id: str,
        new_status: TicketStatus,
        as_of: dt.date,
        compensation_gbp: float = 0.0,
    ) -> Optional[ServiceTicket]:
        for i, t in enumerate(self._tickets):
            if t.ticket_id == ticket_id:
                resolved = as_of if new_status == TicketStatus.RESOLVED else t.resolved_at
                escalated = as_of if new_status == TicketStatus.ESCALATED else t.escalated_at
                updated = ServiceTicket(
                    ticket_id=t.ticket_id,
                    account_id=t.account_id,
                    category=t.category,
                    opened_at=t.opened_at,
                    status=new_status,
                    resolved_at=resolved,
                    escalated_at=escalated,
                    acknowledged_at=t.acknowledged_at,
                    compensation_offered_gbp=compensation_gbp if compensation_gbp else t.compensation_offered_gbp,
                )
                self._tickets[i] = updated
                return updated
        return None

    def tickets_for(self, account_id: str) -> List[ServiceTicket]:
        return [t for t in self._tickets if t.account_id == account_id]

    def open_tickets(self) -> List[ServiceTicket]:
        return [t for t in self._tickets
                if t.status in (TicketStatus.OPEN, TicketStatus.IN_PROGRESS)]

    def overdue_acknowledgements(self, as_of: dt.date) -> List[ServiceTicket]:
        return [t for t in self._tickets if t.is_acknowledgement_overdue(as_of)]

    def overdue_responses(self, as_of: dt.date) -> List[ServiceTicket]:
        return [t for t in self._tickets if t.is_response_overdue(as_of)]

    def escalated_tickets(self) -> List[ServiceTicket]:
        return [t for t in self._tickets if t.is_escalated()]

    def total_compensation_gbp(self) -> float:
        return sum(t.compensation_offered_gbp for t in self._tickets)

    def avg_resolution_days(self) -> Optional[float]:
        resolved = [t for t in self._tickets if t.days_to_resolve() is not None]
        if not resolved:
            return None
        return sum(t.days_to_resolve() for t in resolved) / len(resolved)

    def service_summary(self, as_of: dt.date) -> str:
        n = len(self._tickets)
        n_open = len(self.open_tickets())
        n_overdue = len(self.overdue_responses(as_of))
        n_esc = len(self.escalated_tickets())
        return (
            "Service Tickets (" + str(as_of) + "): "
            + str(n) + " total, " + str(n_open) + " open. "
            "Overdue: " + str(n_overdue) + ". "
            "Escalated: " + str(n_esc) + "."
        )
