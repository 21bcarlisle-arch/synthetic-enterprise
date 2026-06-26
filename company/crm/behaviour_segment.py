"""Customer behaviour segmentation model.

Real UK energy suppliers segment their residential customer book by observable
behaviour patterns (payment reliability, portal engagement, contact frequency,
switching propensity). These segments drive CRM strategy: which customers get
proactive outreach, debt intervention, loyalty rewards, or win-back campaigns.

Segments are derived from a rolling 12-month window of observable actions —
no simulation internals are used, only company-layer data (bills, payments,
portal logins, contacts, switching history).

Segmentation dimensions:
1. Payment reliability: on-time rate over 12m
2. Portal engagement: login frequency per month
3. Contact propensity: inbound contacts per quarter
4. Switching risk: switcher in prior 2 years (external) or quote-request events

Segment names are deliberately commercial/CRM-style, not technical.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class PaymentBehaviour(str, Enum):
    EXEMPLARY = "exemplary"          # 95-100% on-time
    RELIABLE = "reliable"            # 80-95% on-time
    OCCASIONAL_MISS = "occasional_miss"  # 60-80% on-time
    CHRONIC_LATE = "chronic_late"    # <60% on-time


class EngagementLevel(str, Enum):
    HIGHLY_ENGAGED = "highly_engaged"   # >4 portal logins/mo or paper-free
    ENGAGED = "engaged"                 # 2-4 logins/mo
    PASSIVE = "passive"                 # <2 logins/mo
    DISENGAGED = "disengaged"           # no logins in 6+ months


class SwitchingRisk(str, Enum):
    HIGH = "high"          # switched in prior 12m or 2+ quote requests
    MEDIUM = "medium"      # switched 1-2 years ago
    LOW = "low"            # 3+ years with supplier; no recent quotes


class CustomerSegment(str, Enum):
    CHAMPION = "champion"          # exemplary payer, highly engaged, low switching risk
    LOYAL = "loyal"                # reliable payer, engaged/passive, low risk
    AT_RISK = "at_risk"            # reliable payer but high switching risk
    STRUGGLING = "struggling"      # payment difficulties; engagement irrelevant
    DISENGAGED_STABLE = "disengaged_stable"   # pays reliably but no engagement
    CHURNER = "churner"            # high switching risk + payment problems


_INTERVENTION_MAP: dict[str, str] = {
    "champion": "loyalty_reward",
    "loyal": "retention_check",
    "at_risk": "proactive_outreach",
    "struggling": "debt_support",
    "disengaged_stable": "re-engagement_campaign",
    "churner": "win-back",
}


@dataclass(frozen=True)
class BehaviourProfile:
    customer_id: str
    as_of_date: dt.date
    payment_on_time_rate: float      # 0.0-1.0, 12-month rolling
    portal_logins_per_month: float
    inbound_contacts_per_quarter: float
    months_since_last_switch: Optional[int]  # None if never switched
    paper_free: bool = False

    @property
    def payment_behaviour(self) -> PaymentBehaviour:
        r = self.payment_on_time_rate
        if r >= 0.95:
            return PaymentBehaviour.EXEMPLARY
        if r >= 0.80:
            return PaymentBehaviour.RELIABLE
        if r >= 0.60:
            return PaymentBehaviour.OCCASIONAL_MISS
        return PaymentBehaviour.CHRONIC_LATE

    @property
    def engagement_level(self) -> EngagementLevel:
        if self.paper_free or self.portal_logins_per_month > 4:
            return EngagementLevel.HIGHLY_ENGAGED
        if self.portal_logins_per_month >= 2:
            return EngagementLevel.ENGAGED
        if self.portal_logins_per_month > 0:
            return EngagementLevel.PASSIVE
        return EngagementLevel.DISENGAGED

    @property
    def switching_risk(self) -> SwitchingRisk:
        if self.months_since_last_switch is not None and self.months_since_last_switch <= 12:
            return SwitchingRisk.HIGH
        if self.months_since_last_switch is not None and self.months_since_last_switch <= 24:
            return SwitchingRisk.MEDIUM
        return SwitchingRisk.LOW

    @property
    def segment(self) -> CustomerSegment:
        pay = self.payment_behaviour
        risk = self.switching_risk
        eng = self.engagement_level
        if pay == PaymentBehaviour.CHRONIC_LATE:
            if risk == SwitchingRisk.HIGH:
                return CustomerSegment.CHURNER
            return CustomerSegment.STRUGGLING
        if pay in (PaymentBehaviour.EXEMPLARY, PaymentBehaviour.RELIABLE):
            if risk == SwitchingRisk.HIGH:
                return CustomerSegment.AT_RISK
            if eng == EngagementLevel.DISENGAGED:
                return CustomerSegment.DISENGAGED_STABLE
            if pay == PaymentBehaviour.EXEMPLARY and risk == SwitchingRisk.LOW:
                return CustomerSegment.CHAMPION
            return CustomerSegment.LOYAL
        # occasional miss
        if risk == SwitchingRisk.HIGH:
            return CustomerSegment.AT_RISK
        return CustomerSegment.STRUGGLING

    @property
    def recommended_intervention(self) -> str:
        return _INTERVENTION_MAP[self.segment.value]


class BehaviourSegmentBook:
    """Record and query customer behaviour profiles."""

    def __init__(self) -> None:
        self._profiles: List[BehaviourProfile] = []

    def record_profile(
        self,
        customer_id: str,
        as_of_date: dt.date,
        payment_on_time_rate: float,
        portal_logins_per_month: float,
        inbound_contacts_per_quarter: float,
        months_since_last_switch: Optional[int],
        paper_free: bool = False,
    ) -> BehaviourProfile:
        p = BehaviourProfile(
            customer_id=customer_id,
            as_of_date=as_of_date,
            payment_on_time_rate=payment_on_time_rate,
            portal_logins_per_month=portal_logins_per_month,
            inbound_contacts_per_quarter=inbound_contacts_per_quarter,
            months_since_last_switch=months_since_last_switch,
            paper_free=paper_free,
        )
        self._profiles.append(p)
        return p

    def latest_profile(self, customer_id: str) -> Optional[BehaviourProfile]:
        matches = [p for p in self._profiles if p.customer_id == customer_id]
        return sorted(matches, key=lambda p: p.as_of_date)[-1] if matches else None

    def segment_counts(self, as_of_date: dt.date) -> Dict[str, int]:
        latest: dict[str, BehaviourProfile] = {}
        for p in self._profiles:
            if p.as_of_date <= as_of_date:
                if p.customer_id not in latest or p.as_of_date > latest[p.customer_id].as_of_date:
                    latest[p.customer_id] = p
        counts: dict[str, int] = {}
        for p in latest.values():
            seg = p.segment.value
            counts[seg] = counts.get(seg, 0) + 1
        return counts

    def at_risk_customers(self, as_of_date: dt.date) -> List[str]:
        return [
            cid for cid, p in {
                p.customer_id: p for p in self._profiles
                if p.as_of_date <= as_of_date
            }.items()
            if p.segment in (CustomerSegment.AT_RISK, CustomerSegment.CHURNER)
        ]

    def segment_summary(self, as_of_date: dt.date) -> dict:
        counts = self.segment_counts(as_of_date)
        total = sum(counts.values())
        return {
            "as_of_date": str(as_of_date),
            "total_profiled": total,
            "segment_counts": counts,
            "at_risk_count": counts.get("at_risk", 0) + counts.get("churner", 0),
            "struggling_count": counts.get("struggling", 0),
        }
