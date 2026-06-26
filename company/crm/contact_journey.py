"""Customer contact preferences and multi-channel communication management."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class ContactChannel(str, Enum):
    EMAIL = 'email'
    SMS = 'sms'
    POST = 'post'
    PHONE = 'phone'
    IN_APP = 'in_app'
    WEB_PORTAL = 'web_portal'


class ContactPurpose(str, Enum):
    BILL = 'bill'
    TARIFF_CHANGE = 'tariff_change'
    MARKETING = 'marketing'
    DEBT_CHASE = 'debt_chase'
    RENEWAL_OFFER = 'renewal_offer'
    SERVICE_UPDATE = 'service_update'
    COMPLAINT_UPDATE = 'complaint_update'


class ContactOutcome(str, Enum):
    DELIVERED = 'delivered'
    OPENED = 'opened'
    CLICKED = 'clicked'
    BOUNCED = 'bounced'
    OPTED_OUT = 'opted_out'
    NO_ANSWER = 'no_answer'
    COMPLETED = 'completed'


@dataclass(frozen=True)
class CustomerContactPrefs:
    customer_id: str
    preferred_channel: ContactChannel
    bill_by_post: bool = False
    marketing_opt_in: bool = False
    sms_alerts: bool = True
    paper_free: bool = True

    @property
    def paper_free_discount_eligible(self) -> bool:
        return self.paper_free and not self.bill_by_post


@dataclass(frozen=True)
class ContactAttempt:
    attempt_id: str
    customer_id: str
    channel: ContactChannel
    purpose: ContactPurpose
    sent_at: dt.datetime
    outcome: ContactOutcome
    cost_pence: float = 0.0

    @property
    def was_successful(self) -> bool:
        return self.outcome in (
            ContactOutcome.DELIVERED, ContactOutcome.OPENED,
            ContactOutcome.CLICKED, ContactOutcome.COMPLETED,
        )


_CHANNEL_COST_PENCE: Dict[ContactChannel, float] = {
    ContactChannel.EMAIL: 0.2,
    ContactChannel.SMS: 4.0,
    ContactChannel.POST: 80.0,
    ContactChannel.PHONE: 350.0,
    ContactChannel.IN_APP: 0.0,
    ContactChannel.WEB_PORTAL: 0.0,
}


class ContactJourney:
    def __init__(self) -> None:
        self._prefs: Dict[str, CustomerContactPrefs] = {}
        self._attempts: List[ContactAttempt] = []
        self._counter = 0

    def set_prefs(self, customer_id: str, preferred_channel: ContactChannel,
                    bill_by_post: bool = False, marketing_opt_in: bool = False,
                    sms_alerts: bool = True, paper_free: bool = True
                    ) -> CustomerContactPrefs:
        p = CustomerContactPrefs(
            customer_id=customer_id, preferred_channel=preferred_channel,
            bill_by_post=bill_by_post, marketing_opt_in=marketing_opt_in,
            sms_alerts=sms_alerts, paper_free=paper_free,
        )
        self._prefs[customer_id] = p
        return p

    def get_prefs(self, customer_id: str) -> Optional[CustomerContactPrefs]:
        return self._prefs.get(customer_id)

    def log_attempt(self, customer_id: str, channel: ContactChannel,
                      purpose: ContactPurpose, sent_at: dt.datetime,
                      outcome: ContactOutcome) -> ContactAttempt:
        self._counter += 1
        a = ContactAttempt(
            attempt_id=f'CA-{self._counter:05d}',
            customer_id=customer_id, channel=channel,
            purpose=purpose, sent_at=sent_at, outcome=outcome,
            cost_pence=_CHANNEL_COST_PENCE.get(channel, 0.0),
        )
        self._attempts.append(a)
        return a

    def delivery_rate_pct(self, channel: ContactChannel, year: int) -> float:
        relevant = [a for a in self._attempts
                     if a.channel == channel and a.sent_at.year == year]
        if not relevant:
            return 0.0
        successes = sum(1 for a in relevant if a.was_successful)
        return round(successes / len(relevant) * 100, 1)

    def total_contact_cost_gbp(self, year: int) -> float:
        return round(sum(
            a.cost_pence / 100 for a in self._attempts if a.sent_at.year == year
        ), 4)

    def opted_out_customers(self) -> List[str]:
        return [
            a.customer_id for a in self._attempts
            if a.outcome == ContactOutcome.OPTED_OUT
        ]

    def contact_summary(self, year: int) -> dict:
        year_att = [a for a in self._attempts if a.sent_at.year == year]
        return {
            'year': year,
            'total_attempts': len(year_att),
            'total_cost_gbp': self.total_contact_cost_gbp(year),
            'paper_free_customers': sum(
                1 for p in self._prefs.values() if p.paper_free
            ),
        }
