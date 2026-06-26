"""Phase 300 milestone: Regulatory Compliance Dashboard.

Aggregates all regulatory obligations into a single compliance status view.
Connects: SFRBook, ComplianceScorecard, ConsumerDutyRegister, REMITBook,
PriceCapBook, RenewableObligationBook, FITBook, FuelMixDisclosureBook,
ECOObligationBook, WarmHomeDiscountBook, EBSSBook.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class FilingStatus(str, Enum):
    FILED = "filed"
    DUE = "due"
    OVERDUE = "overdue"
    NOT_APPLICABLE = "not_applicable"


class ComplianceArea(str, Enum):
    FINANCIAL_RESILIENCE = "sfr"
    MARKET_CONDUCT = "remit"
    PRICE_CAP = "price_cap"
    ENVIRONMENTAL = "environmental"
    SOCIAL_OBLIGATIONS = "social"
    CONSUMER_DUTY = "consumer_duty"
    TRADE_REPORTING = "trade_reporting"
    FUEL_MIX = "fuel_mix"


@dataclass(frozen=True)
class ComplianceObligation:
    area: ComplianceArea
    obligation_name: str
    due_date: str
    status: FilingStatus
    rag: str  # "GREEN", "AMBER", "RED"
    notes: Optional[str] = None

    @property
    def is_breach(self) -> bool:
        return self.rag == "RED" or self.status == FilingStatus.OVERDUE

    @property
    def needs_attention(self) -> bool:
        return self.rag in ("RED", "AMBER") or self.status in (FilingStatus.DUE, FilingStatus.OVERDUE)


class RegulatoryDashboard:
    def __init__(self) -> None:
        self._obligations: list[ComplianceObligation] = []

    def add_obligation(self, obligation: ComplianceObligation) -> ComplianceObligation:
        self._obligations.append(obligation)
        return obligation

    def obligations_by_area(self, area: ComplianceArea) -> list[ComplianceObligation]:
        return [o for o in self._obligations if o.area == area]

    def breaches(self) -> list[ComplianceObligation]:
        return [o for o in self._obligations if o.is_breach]

    def attention_items(self) -> list[ComplianceObligation]:
        return [o for o in self._obligations if o.needs_attention]

    def overall_rag(self) -> str:
        if any(o.rag == "RED" or o.status == FilingStatus.OVERDUE for o in self._obligations):
            return "RED"
        if any(o.rag == "AMBER" or o.status == FilingStatus.DUE for o in self._obligations):
            return "AMBER"
        return "GREEN"

    def filed_on_time_rate(self) -> float:
        if not self._obligations:
            return 100.0
        on_time = sum(1 for o in self._obligations if o.status == FilingStatus.FILED)
        applicable = sum(1 for o in self._obligations if o.status != FilingStatus.NOT_APPLICABLE)
        return round(on_time / applicable * 100, 2) if applicable else 100.0

    def area_rag(self) -> dict[str, str]:
        result = {}
        for area in ComplianceArea:
            obs = self.obligations_by_area(area)
            if not obs:
                result[area.value] = "GREEN"
            elif any(o.rag == "RED" for o in obs):
                result[area.value] = "RED"
            elif any(o.rag == "AMBER" for o in obs):
                result[area.value] = "AMBER"
            else:
                result[area.value] = "GREEN"
        return result

    def dashboard_summary(self) -> dict:
        return {
            "total_obligations": len(self._obligations),
            "breaches": len(self.breaches()),
            "attention_items": len(self.attention_items()),
            "overall_rag": self.overall_rag(),
            "filed_on_time_rate_pct": self.filed_on_time_rate(),
            "area_rag": self.area_rag(),
        }
