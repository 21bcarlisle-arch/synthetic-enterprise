from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import Enum
from typing import List, Optional

NOTICE_DAYS = 30  # Ofgem SLC 23.1: minimum 30 days notice before rate change


class VariationReason(str, Enum):
    PRICE_CAP_CHANGE = "price_cap_change"
    POLICY_COST_CHANGE = "policy_cost_change"
    NETWORK_COST_CHANGE = "network_cost_change"
    TARIFF_RESTRUCTURE = "tariff_restructure"
    COMMERCIAL_DECISION = "commercial_decision"


class VariationOutcome(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED_SWITCHED_AWAY = "rejected_switched_away"
    REJECTED_STAYED = "rejected_stayed"   # customer objected but did not switch


@dataclass
class TariffVariation:
    variation_id: int
    customer_id: str
    old_unit_rate_ppm: float        # pence per kWh
    new_unit_rate_ppm: float        # pence per kWh
    notice_sent_date: date
    effective_date: date
    reason: VariationReason
    outcome: VariationOutcome = VariationOutcome.PENDING
    response_date: Optional[date] = None

    @property
    def rate_change_pct(self) -> float:
        if self.old_unit_rate_ppm == 0:
            return 0.0
        return (self.new_unit_rate_ppm - self.old_unit_rate_ppm) / self.old_unit_rate_ppm * 100.0

    @property
    def notice_period_days(self) -> int:
        return (self.effective_date - self.notice_sent_date).days

    def is_adequate_notice(self) -> bool:
        return self.notice_period_days >= NOTICE_DAYS

    def has_no_exit_fee_window(self, as_of: date) -> bool:
        """Customer can switch fee-free from notice_sent_date to effective_date."""
        return self.notice_sent_date <= as_of <= self.effective_date

    @property
    def is_pending(self) -> bool:
        return self.outcome == VariationOutcome.PENDING


@dataclass
class TariffVariationBook:
    _variations: List[TariffVariation] = field(default_factory=list)
    _next_id: int = field(default=1)

    def issue_notice(
        self,
        customer_id: str,
        old_unit_rate_ppm: float,
        new_unit_rate_ppm: float,
        notice_sent_date: date,
        effective_date: date,
        reason: VariationReason,
    ) -> TariffVariation:
        v = TariffVariation(
            variation_id=self._next_id,
            customer_id=customer_id,
            old_unit_rate_ppm=old_unit_rate_ppm,
            new_unit_rate_ppm=new_unit_rate_ppm,
            notice_sent_date=notice_sent_date,
            effective_date=effective_date,
            reason=reason,
        )
        self._variations.append(v)
        self._next_id += 1
        return v

    def record_response(
        self,
        variation_id: int,
        outcome: VariationOutcome,
        response_date: date,
    ) -> bool:
        for v in self._variations:
            if v.variation_id == variation_id:
                v.outcome = outcome
                v.response_date = response_date
                return True
        return False

    def pending_variations(self, as_of: date) -> List[TariffVariation]:
        return [v for v in self._variations if v.is_pending and v.effective_date >= as_of]

    def variations_for_customer(self, customer_id: str) -> List[TariffVariation]:
        return [v for v in self._variations if v.customer_id == customer_id]

    def inadequate_notice_violations(self) -> List[TariffVariation]:
        return [v for v in self._variations if not v.is_adequate_notice()]

    def annual_summary(self, year: int) -> dict:
        year_vars = [v for v in self._variations if v.notice_sent_date.year == year]
        if not year_vars:
            result = dict(year=year, total=0, accepted=0, switched_away=0,
                          pending=0, violations=0)
            return result
        accepted = sum(1 for v in year_vars if v.outcome == VariationOutcome.ACCEPTED)
        switched = sum(
            1 for v in year_vars if v.outcome == VariationOutcome.REJECTED_SWITCHED_AWAY
        )
        pending = sum(1 for v in year_vars if v.is_pending)
        violations = sum(1 for v in year_vars if not v.is_adequate_notice())
        result = dict(
            year=year,
            total=len(year_vars),
            accepted=accepted,
            switched_away=switched,
            pending=pending,
            violations=violations,
        )
        return result
