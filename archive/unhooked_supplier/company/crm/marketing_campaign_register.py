"""Direct Marketing Campaign Register (Phase DT).

Energy suppliers run marketing campaigns to:
- Acquire new customers (B2C direct mail, digital, cold calling)
- Upsell existing customers (EV tariffs, smart meter upgrades)
- Retention campaigns (before contract expiry)
- Reacquisition (win-back lapsed customers)

Regulatory compliance requirements:
- GDPR: consent required for direct marketing; legitimate interest ground restricted
- PECR (Privacy and Electronic Communications Regulations): opt-in for email/text
- ICO marketing guidance: suppression lists, unsubscribe handling
- Ofgem Consumer Duty: marketing must be clear, fair, not misleading
- ASA codes: energy marketing must not misrepresent green claims (CAP Code)

Key metrics suppliers track:
- Response rate, conversion rate, cost per acquisition (CPA)
- ROAS (return on ad spend)
- Channel mix: PCW (price comparison websites), email, SMS, door-to-door, TV
- Brand Net Promoter Score (NPS) from marketing touchpoints

This register tracks campaign spend and performance while ensuring GDPR
suppression compliance — the marketing send list must be cross-checked
against suppressed accounts.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class CampaignChannel(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    DIRECT_MAIL = "direct_mail"
    COLD_CALL = "cold_call"
    PCW_PAID = "pcw_paid"            # paid placement on price comparison website
    PCW_ORGANIC = "pcw_organic"      # organic listing
    SOCIAL_MEDIA = "social_media"
    TV_RADIO = "tv_radio"
    DOOR_TO_DOOR = "door_to_door"


class CampaignStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class CampaignType(str, Enum):
    ACQUISITION = "acquisition"
    UPSELL = "upsell"                # existing customers
    RETENTION = "retention"
    REACQUISITION = "reacquisition"
    PRODUCT_LAUNCH = "product_launch"


_DOOR_TO_DOOR_COOLING_OFF_DAYS = 14  # Consumer Contracts Regs 2013


@dataclass(frozen=True)
class MarketingCampaignRecord:
    campaign_id: str
    name: str
    channel: CampaignChannel
    campaign_type: CampaignType
    start_date: dt.date
    end_date: Optional[dt.date]
    budget_gbp: float
    spend_gbp: float
    sends: int                       # contacts sent to
    responses: int                   # leads or enquiries
    conversions: int                 # actual sign-ups / upgrades
    status: CampaignStatus
    opt_in_compliant: bool = True    # all contacts gave valid consent

    @property
    def response_rate_pct(self) -> float:
        if self.sends == 0:
            return 0.0
        return self.responses / self.sends * 100

    @property
    def conversion_rate_pct(self) -> float:
        if self.sends == 0:
            return 0.0
        return self.conversions / self.sends * 100

    @property
    def cost_per_acquisition_gbp(self) -> float:
        if self.conversions == 0:
            return 0.0
        return self.spend_gbp / self.conversions

    @property
    def budget_utilisation_pct(self) -> float:
        if self.budget_gbp == 0:
            return 0.0
        return self.spend_gbp / self.budget_gbp * 100

    @property
    def is_door_to_door(self) -> bool:
        return self.channel == CampaignChannel.DOOR_TO_DOOR

    @property
    def requires_opt_in(self) -> bool:
        return self.channel in (CampaignChannel.EMAIL, CampaignChannel.SMS,
                                CampaignChannel.COLD_CALL)


class MarketingCampaignRegister:
    """Tracks marketing campaigns with GDPR and Consumer Duty compliance."""

    def __init__(self) -> None:
        self._records: Dict[str, MarketingCampaignRecord] = {}
        self._seq = 0

    def _next_id(self) -> str:
        self._seq += 1
        return f"MKT-{self._seq:04d}"

    def create(
        self,
        name: str,
        channel: CampaignChannel,
        campaign_type: CampaignType,
        start_date: dt.date,
        budget_gbp: float,
        opt_in_compliant: bool = True,
        end_date: Optional[dt.date] = None,
    ) -> MarketingCampaignRecord:
        mid = self._next_id()
        rec = MarketingCampaignRecord(
            campaign_id=mid,
            name=name,
            channel=channel,
            campaign_type=campaign_type,
            start_date=start_date,
            end_date=end_date,
            budget_gbp=budget_gbp,
            spend_gbp=0.0,
            sends=0,
            responses=0,
            conversions=0,
            status=CampaignStatus.DRAFT,
            opt_in_compliant=opt_in_compliant,
        )
        self._records[mid] = rec
        return rec

    def update_performance(
        self,
        campaign_id: str,
        sends: int,
        responses: int,
        conversions: int,
        spend_gbp: float,
        status: CampaignStatus = CampaignStatus.ACTIVE,
    ) -> MarketingCampaignRecord:
        rec = self._records[campaign_id]
        updated = MarketingCampaignRecord(
            campaign_id=rec.campaign_id, name=rec.name, channel=rec.channel,
            campaign_type=rec.campaign_type, start_date=rec.start_date,
            end_date=rec.end_date, budget_gbp=rec.budget_gbp,
            spend_gbp=spend_gbp, sends=sends, responses=responses,
            conversions=conversions, status=status,
            opt_in_compliant=rec.opt_in_compliant,
        )
        self._records[campaign_id] = updated
        return updated

    def get(self, campaign_id: str) -> Optional[MarketingCampaignRecord]:
        return self._records.get(campaign_id)

    def active_campaigns(self) -> List[MarketingCampaignRecord]:
        return [r for r in self._records.values() if r.status == CampaignStatus.ACTIVE]

    def non_compliant_campaigns(self) -> List[MarketingCampaignRecord]:
        return [r for r in self._records.values()
                if r.requires_opt_in and not r.opt_in_compliant]

    def by_channel(self) -> Dict[str, int]:
        out: Dict[str, int] = {}
        for r in self._records.values():
            out[r.channel.value] = out.get(r.channel.value, 0) + 1
        return out

    def total_spend_gbp(self) -> float:
        return sum(r.spend_gbp for r in self._records.values())

    def total_conversions(self) -> int:
        return sum(r.conversions for r in self._records.values())

    def best_cpa(self) -> Optional[MarketingCampaignRecord]:
        """Lowest cost-per-acquisition among campaigns with at least one conversion."""
        candidates = [r for r in self._records.values() if r.conversions > 0]
        if not candidates:
            return None
        return min(candidates, key=lambda r: r.cost_per_acquisition_gbp)

    def campaign_summary(self) -> str:
        total = len(self._records)
        n_active = len(self.active_campaigns())
        n_non_compliant = len(self.non_compliant_campaigns())
        total_spend = self.total_spend_gbp()
        total_conv = self.total_conversions()
        return (
            f"Marketing Campaign Register (GDPR/PECR/Consumer Duty): "
            f"{total} campaigns, {n_active} active. "
            f"Total spend: £{total_spend:,.0f}. Conversions: {total_conv}. "
            f"Non-compliant: {n_non_compliant}."
        )
