"""Outbound contact campaign tracker: retention, renewal, and collections campaigns."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class CampaignType(str, Enum):
    RENEWAL_CHASE = 'renewal_chase'
    RETENTION_WINBACK = 'retention_winback'
    DEBT_COLLECTION = 'debt_collection'
    SMART_METER_INSTALL = 'smart_meter_install'
    EEP_REFERRAL = 'eep_referral'
    WHD_OUTREACH = 'whd_outreach'
    SURVEY = 'survey'


class ContactOutcome(str, Enum):
    CONVERTED = 'converted'
    NO_ANSWER = 'no_answer'
    REFUSED = 'refused'
    CALLBACK_ARRANGED = 'callback_arranged'
    WRONG_NUMBER = 'wrong_number'
    UNCONTACTABLE = 'uncontactable'


class ContactChannel(str, Enum):
    PHONE = 'phone'
    EMAIL = 'email'
    SMS = 'sms'
    POST = 'post'


@dataclass(frozen=True)
class CampaignContact:
    contact_id: str
    campaign_id: str
    customer_id: str
    contact_date: dt.date
    channel: ContactChannel
    outcome: ContactOutcome
    agent_id: Optional[str] = None

    @property
    def is_converted(self) -> bool:
        return self.outcome == ContactOutcome.CONVERTED

    @property
    def is_reached(self) -> bool:
        return self.outcome not in {
            ContactOutcome.NO_ANSWER,
            ContactOutcome.WRONG_NUMBER,
            ContactOutcome.UNCONTACTABLE,
        }


@dataclass
class Campaign:
    campaign_id: str
    campaign_type: CampaignType
    start_date: dt.date
    target_count: int
    channel: ContactChannel
    end_date: Optional[dt.date] = None
    _contacts: List[CampaignContact] = field(default_factory=list)

    @property
    def is_active(self) -> bool:
        return self.end_date is None

    @property
    def contacts_made(self) -> int:
        return len(self._contacts)

    @property
    def conversion_rate(self) -> Optional[float]:
        reached = [c for c in self._contacts if c.is_reached]
        if not reached:
            return None
        return round(sum(1 for c in reached if c.is_converted) / len(reached) * 100, 1)

    @property
    def contact_rate(self) -> Optional[float]:
        if not self._contacts:
            return None
        return round(sum(1 for c in self._contacts if c.is_reached) / len(self._contacts) * 100, 1)

    def summary(self) -> dict:
        converted = sum(1 for c in self._contacts if c.is_converted)
        return {
            'campaign_id': self.campaign_id,
            'campaign_type': self.campaign_type.value,
            'target_count': self.target_count,
            'contacts_made': self.contacts_made,
            'converted': converted,
            'conversion_rate_pct': self.conversion_rate,
            'contact_rate_pct': self.contact_rate,
            'is_active': self.is_active,
        }


class CampaignTracker:
    def __init__(self) -> None:
        self._campaigns: Dict[str, Campaign] = {}
        self._next_contact = 1

    def create_campaign(self, campaign_id: str, campaign_type: CampaignType,
                         start_date: dt.date, target_count: int,
                         channel: ContactChannel) -> Campaign:
        c = Campaign(campaign_id=campaign_id, campaign_type=campaign_type,
                     start_date=start_date, target_count=target_count, channel=channel)
        self._campaigns[campaign_id] = c
        return c

    def record_contact(self, campaign_id: str, customer_id: str,
                        contact_date: dt.date, outcome: ContactOutcome,
                        agent_id: Optional[str] = None) -> CampaignContact:
        campaign = self._campaigns[campaign_id]
        contact = CampaignContact(
            contact_id=f'CTT-{self._next_contact:04d}',
            campaign_id=campaign_id, customer_id=customer_id,
            contact_date=contact_date, channel=campaign.channel,
            outcome=outcome, agent_id=agent_id,
        )
        self._next_contact += 1
        campaign._contacts.append(contact)
        return contact

    def close_campaign(self, campaign_id: str, end_date: dt.date) -> None:
        self._campaigns[campaign_id].end_date = end_date

    def get(self, campaign_id: str) -> Campaign:
        return self._campaigns[campaign_id]

    def active_campaigns(self) -> List[Campaign]:
        return [c for c in self._campaigns.values() if c.is_active]

    def campaigns_by_type(self, campaign_type: CampaignType) -> List[Campaign]:
        return [c for c in self._campaigns.values() if c.campaign_type == campaign_type]
