from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class RiskCategory(str, Enum):
    MARKET = 'market'
    CREDIT = 'credit'
    LIQUIDITY = 'liquidity'
    OPERATIONAL = 'operational'
    REGULATORY = 'regulatory'


class RiskRAG(str, Enum):
    WITHIN_APPETITE = 'within_appetite'
    APPROACHING_LIMIT = 'approaching_limit'
    LIMIT_BREACH = 'limit_breach'


@dataclass(frozen=True)
class RiskLimit:
    limit_id: str
    category: RiskCategory
    description: str
    limit_value: float
    unit: str
    warning_threshold_pct: float = 80.0

    @property
    def warning_value(self) -> float:
        return round(self.limit_value * self.warning_threshold_pct / 100, 2)


@dataclass(frozen=True)
class RiskMeasurement:
    limit_id: str
    measured_value: float
    measured_date: dt.date
    limit: RiskLimit

    @property
    def utilisation_pct(self) -> float:
        if self.limit.limit_value == 0:
            return 0.0
        return round(self.measured_value / self.limit.limit_value * 100, 1)

    @property
    def rag(self) -> RiskRAG:
        if self.measured_value > self.limit.limit_value:
            return RiskRAG.LIMIT_BREACH
        if self.measured_value >= self.limit.warning_value:
            return RiskRAG.APPROACHING_LIMIT
        return RiskRAG.WITHIN_APPETITE

    @property
    def is_breach(self) -> bool:
        return self.rag == RiskRAG.LIMIT_BREACH


class RiskAppetiteFramework:
    def __init__(self, approved_date: dt.date) -> None:
        self.approved_date = approved_date
        self._limits: dict[str, RiskLimit] = {}
        self._measurements: list[RiskMeasurement] = []

    def add_limit(self, limit_id: str, category: RiskCategory, description: str,
                  limit_value: float, unit: str,
                  warning_threshold_pct: float = 80.0) -> RiskLimit:
        limit = RiskLimit(
            limit_id=limit_id, category=category, description=description,
            limit_value=limit_value, unit=unit,
            warning_threshold_pct=warning_threshold_pct,
        )
        self._limits[limit_id] = limit
        return limit

    def record_measurement(self, limit_id: str, measured_value: float,
                           measured_date: dt.date) -> RiskMeasurement:
        limit = self._limits[limit_id]
        m = RiskMeasurement(
            limit_id=limit_id, measured_value=measured_value,
            measured_date=measured_date, limit=limit,
        )
        self._measurements.append(m)
        return m

    def latest_measurement(self, limit_id: str) -> Optional[RiskMeasurement]:
        relevant = [m for m in self._measurements if m.limit_id == limit_id]
        if not relevant:
            return None
        return max(relevant, key=lambda m: m.measured_date)

    def active_breaches(self) -> List[RiskMeasurement]:
        seen: dict[str, RiskMeasurement] = {}
        for m in self._measurements:
            if m.limit_id not in seen or m.measured_date >= seen[m.limit_id].measured_date:
                seen[m.limit_id] = m
        return [m for m in seen.values() if m.is_breach]

    def risk_dashboard(self, as_of: dt.date) -> dict:
        latest = {}
        for m in self._measurements:
            if m.measured_date <= as_of:
                if m.limit_id not in latest or m.measured_date > latest[m.limit_id].measured_date:
                    latest[m.limit_id] = m
        items = []
        for lid, m in sorted(latest.items()):
            items.append({
                'limit_id': lid,
                'category': m.limit.category.value,
                'description': m.limit.description,
                'limit_value': m.limit.limit_value,
                'measured_value': m.measured_value,
                'utilisation_pct': m.utilisation_pct,
                'rag': m.rag.value,
            })
        breaches = sum(1 for i in items if i['rag'] == 'limit_breach')
        return {
            'as_of': str(as_of),
            'total_limits': len(self._limits),
            'measured_limits': len(items),
            'breaches': breaches,
            'items': items,
        }
