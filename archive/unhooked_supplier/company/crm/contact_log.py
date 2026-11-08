from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import List, Optional


class ContactChannel(str, Enum):
    PHONE = 'phone'
    WEBCHAT = 'webchat'
    EMAIL = 'email'
    LETTER = 'letter'
    PORTAL = 'portal'


class ContactReason(str, Enum):
    BILLING_QUERY = 'billing_query'
    METER_READ = 'meter_read'
    PAYMENT_DIFFICULTY = 'payment_difficulty'
    SWITCH_QUERY = 'switch_query'
    TARIFF_QUERY = 'tariff_query'
    COMPLAINT = 'complaint'
    FAULT_SUPPLY_ISSUE = 'fault_supply_issue'
    DEBT_ADVICE = 'debt_advice'
    SMART_METER = 'smart_meter'
    CHANGE_DETAILS = 'change_details'
    BEREAVEMENT = 'bereavement'
    OTHER = 'other'


_AVG_HANDLE_MINUTES: dict[str, float] = {
    'billing_query': 8.0,
    'meter_read': 5.0,
    'payment_difficulty': 15.0,
    'switch_query': 7.0,
    'tariff_query': 9.0,
    'complaint': 18.0,
    'fault_supply_issue': 12.0,
    'debt_advice': 20.0,
    'smart_meter': 10.0,
    'change_details': 4.0,
    'bereavement': 25.0,
    'other': 6.0,
}

_ESCALATION_RATE: dict[str, float] = {
    'billing_query': 0.10,
    'meter_read': 0.05,
    'payment_difficulty': 0.25,
    'switch_query': 0.05,
    'tariff_query': 0.08,
    'complaint': 0.40,
    'fault_supply_issue': 0.15,
    'debt_advice': 0.30,
    'smart_meter': 0.12,
    'change_details': 0.02,
    'bereavement': 0.20,
    'other': 0.08,
}


@dataclass
class ContactInteraction:
    interaction_id: int
    customer_id: str
    channel: ContactChannel
    reason: ContactReason
    contact_date: date
    handle_minutes: float
    resolved: bool = True
    escalated: bool = False
    notes: str = ''


@dataclass
class ContactLog:
    _interactions: List[ContactInteraction] = field(default_factory=list)
    _next_id: int = field(default=1)

    def record(self,
               customer_id: str,
               channel: ContactChannel,
               reason: ContactReason,
               contact_date: date,
               handle_minutes: Optional[float] = None,
               resolved: bool = True,
               escalated: bool = False,
               notes: str = '',
               ) -> ContactInteraction:
        minutes = handle_minutes if handle_minutes is not None else _AVG_HANDLE_MINUTES.get(reason.value, 8.0)
        interaction = ContactInteraction(
            interaction_id=self._next_id,
            customer_id=customer_id,
            channel=channel,
            reason=reason,
            contact_date=contact_date,
            handle_minutes=minutes,
            resolved=resolved,
            escalated=escalated,
            notes=notes,
        )
        self._interactions.append(interaction)
        self._next_id += 1
        return interaction

    def contacts_for_customer(self, customer_id: str) -> List[ContactInteraction]:
        return [i for i in self._interactions if i.customer_id == customer_id]

    def avg_handle_minutes_for_reason(self, reason: ContactReason) -> float:
        interactions = [i for i in self._interactions if i.reason == reason]
        if not interactions:
            return _AVG_HANDLE_MINUTES.get(reason.value, 8.0)
        return sum(i.handle_minutes for i in interactions) / len(interactions)

    def annual_summary(self, year: int) -> dict:
        year_interactions = [i for i in self._interactions if i.contact_date.year == year]
        if not year_interactions:
            result = dict(year=year, total=0, escalated=0, unresolved=0,
                          total_handle_minutes=0.0, by_reason=dict())
            return result
        escalated = sum(1 for i in year_interactions if i.escalated)
        unresolved = sum(1 for i in year_interactions if not i.resolved)
        total_minutes = sum(i.handle_minutes for i in year_interactions)
        by_reason: dict[str, int] = {}
        for i in year_interactions:
            by_reason[i.reason.value] = by_reason.get(i.reason.value, 0) + 1
        result = dict(
            year=year,
            total=len(year_interactions),
            escalated=escalated,
            unresolved=unresolved,
            total_handle_minutes=round(total_minutes, 1),
            by_reason=by_reason,
        )
        return result
