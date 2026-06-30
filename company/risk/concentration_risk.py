"""Portfolio Concentration Risk Monitor (Phase EQ).

Concentration risk occurs when:
1. A small number of large customers represent disproportionate revenue
2. A single tariff type represents most of the portfolio
3. A single geographic region dominates (supply network failure risk)
4. Over-reliance on one acquisition channel

For energy suppliers, the key regulatory concern (Ofgem post-2022) is:
- If one large I&C customer leaves, does the supplier remain viable?
- Is the supplier's hedging aligned with the customer concentration?
- Single large I&C can represent 5-15% of a small supplier's total revenue

This module uses the Herfindahl-Hirschman Index (HHI) as the primary metric:
HHI = sum(s_i^2) where s_i = revenue share of customer i (as a fraction)
HHI near 1.0 = monopoly; HHI < 0.15 = diverse; UK competition law: 0.25 threshold

For energy: regulators expect no single customer > 20% of total revenue.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class ConcentrationRiskLevel(str, Enum):
    LOW = "low"           # HHI < 0.10
    MODERATE = "moderate" # 0.10 <= HHI < 0.18
    HIGH = "high"         # 0.18 <= HHI < 0.25
    CRITICAL = "critical" # HHI >= 0.25


class ConcentrationDimension(str, Enum):
    CUSTOMER = "customer"
    TARIFF_TYPE = "tariff_type"
    FUEL_TYPE = "fuel_type"
    SEGMENT = "segment"  # domestic/sme/ic


_HHI_THRESHOLDS = {
    ConcentrationRiskLevel.LOW: 0.10,
    ConcentrationRiskLevel.MODERATE: 0.18,
    ConcentrationRiskLevel.HIGH: 0.25,
}

_SINGLE_ENTITY_MAX_PCT = 20.0  # Ofgem guidance: no single customer > 20%


@dataclass(frozen=True)
class ConcentrationSnapshot:
    dimension: ConcentrationDimension
    as_of: dt.date
    shares: Dict[str, float]  # entity_id -> revenue share (0.0 to 1.0)

    @property
    def hhi(self) -> float:
        return sum(s ** 2 for s in self.shares.values())

    @property
    def risk_level(self) -> ConcentrationRiskLevel:
        h = self.hhi
        if h >= _HHI_THRESHOLDS[ConcentrationRiskLevel.HIGH]:
            return ConcentrationRiskLevel.CRITICAL
        if h >= _HHI_THRESHOLDS[ConcentrationRiskLevel.MODERATE]:
            return ConcentrationRiskLevel.HIGH
        if h >= _HHI_THRESHOLDS[ConcentrationRiskLevel.LOW]:
            return ConcentrationRiskLevel.MODERATE
        return ConcentrationRiskLevel.LOW

    @property
    def top_entity(self) -> Optional[str]:
        if not self.shares:
            return None
        return max(self.shares, key=lambda k: self.shares[k])

    @property
    def top_entity_pct(self) -> float:
        if not self.shares:
            return 0.0
        return max(self.shares.values()) * 100.0

    @property
    def breaches_single_entity_cap(self) -> bool:
        return self.top_entity_pct > _SINGLE_ENTITY_MAX_PCT

    @property
    def n_entities(self) -> int:
        return len(self.shares)

    def concentration_summary(self) -> str:
        return (
            "Concentration (" + self.dimension.value + ", " + str(self.as_of) + "): "
            "HHI=" + str(round(self.hhi, 4)) + " "
            "[" + self.risk_level.value + "] "
            "top=" + (self.top_entity or "none") + " "
            + str(round(self.top_entity_pct, 1)) + "%"
            + (" BREACH" if self.breaches_single_entity_cap else "") + "."
        )


class ConcentrationRiskMonitor:

    def __init__(self) -> None:
        self._snapshots: List[ConcentrationSnapshot] = []

    def record(self, snapshot: ConcentrationSnapshot) -> ConcentrationSnapshot:
        self._snapshots.append(snapshot)
        return snapshot

    def latest_for(self, dimension: ConcentrationDimension) -> Optional[ConcentrationSnapshot]:
        matching = [s for s in self._snapshots if s.dimension == dimension]
        if not matching:
            return None
        return max(matching, key=lambda s: s.as_of)

    def high_risk_dimensions(self, as_of: dt.date) -> List[ConcentrationSnapshot]:
        recent = []
        for dim in ConcentrationDimension:
            snap = self.latest_for(dim)
            if snap and snap.risk_level in (
                ConcentrationRiskLevel.HIGH, ConcentrationRiskLevel.CRITICAL
            ):
                recent.append(snap)
        return recent

    def entity_breaches(self) -> List[ConcentrationSnapshot]:
        return [s for s in self._snapshots if s.breaches_single_entity_cap]

    def portfolio_concentration_summary(self, as_of: dt.date) -> str:
        n_high = len(self.high_risk_dimensions(as_of))
        n_breaches = len(self.entity_breaches())
        return (
            "Concentration Risk Monitor (" + str(as_of) + "): "
            + str(n_high) + " high/critical dimensions. "
            + str(n_breaches) + " entity cap breaches."
        )
