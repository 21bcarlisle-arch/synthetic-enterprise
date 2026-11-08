"""Customer gain/loss switching analytics: market share movement, churn tracking."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class SwitchDirection(str, Enum):
    GAIN = 'gain'
    LOSS = 'loss'


class SwitchReason(str, Enum):
    PRICE = 'price'
    SERVICE = 'service'
    GREEN_TARIFF = 'green_tariff'
    SMART_METER = 'smart_meter'
    DEAL = 'deal'
    COMPLAINT_DISSATISFACTION = 'complaint_dissatisfaction'
    MOVING_HOME = 'moving_home'
    UNKNOWN = 'unknown'


@dataclass(frozen=True)
class SwitchRecord:
    switch_id: str
    customer_id: str
    switch_date: dt.date
    direction: SwitchDirection
    from_supplier: str
    to_supplier: str
    annual_kwh: float
    reason: SwitchReason = SwitchReason.UNKNOWN

    @property
    def annual_mwh(self) -> float:
        return self.annual_kwh / 1000

    @property
    def is_gain(self) -> bool:
        return self.direction == SwitchDirection.GAIN


class SwitchingReport:
    def __init__(self, supplier_name: str) -> None:
        self.supplier_name = supplier_name
        self._switches: List[SwitchRecord] = []

    def record(self, switch_id: str, customer_id: str, switch_date: dt.date,
                 direction: SwitchDirection, counterparty: str,
                 annual_kwh: float, reason: SwitchReason = SwitchReason.UNKNOWN
                 ) -> SwitchRecord:
        from_s = counterparty if direction == SwitchDirection.GAIN else self.supplier_name
        to_s = self.supplier_name if direction == SwitchDirection.GAIN else counterparty
        rec = SwitchRecord(
            switch_id=switch_id, customer_id=customer_id,
            switch_date=switch_date, direction=direction,
            from_supplier=from_s, to_supplier=to_s,
            annual_kwh=annual_kwh, reason=reason,
        )
        self._switches.append(rec)
        return rec

    def gains(self, year: int) -> List[SwitchRecord]:
        return [s for s in self._switches
                if s.switch_date.year == year and s.direction == SwitchDirection.GAIN]

    def losses(self, year: int) -> List[SwitchRecord]:
        return [s for s in self._switches
                if s.switch_date.year == year and s.direction == SwitchDirection.LOSS]

    def net_customer_movement(self, year: int) -> int:
        return len(self.gains(year)) - len(self.losses(year))

    def net_mwh_movement(self, year: int) -> float:
        gain_mwh = sum(s.annual_mwh for s in self.gains(year))
        loss_mwh = sum(s.annual_mwh for s in self.losses(year))
        return round(gain_mwh - loss_mwh, 1)

    def churn_rate_pct(self, year: int, avg_customer_count: int) -> Optional[float]:
        if avg_customer_count <= 0:
            return None
        return round(len(self.losses(year)) / avg_customer_count * 100, 2)

    def loss_reasons(self, year: int) -> Dict[str, int]:
        result: Dict[str, int] = {}
        for s in self.losses(year):
            k = s.reason.value
            result[k] = result.get(k, 0) + 1
        return result

    def top_gaining_from(self, year: int) -> Optional[str]:
        gain_list = self.gains(year)
        if not gain_list:
            return None
        counts: Dict[str, int] = {}
        for s in gain_list:
            counts[s.from_supplier] = counts.get(s.from_supplier, 0) + 1
        return max(counts, key=lambda k: counts[k])

    def switching_summary(self, year: int, avg_customers: int) -> dict:
        return {
            'year': year,
            'gains': len(self.gains(year)),
            'losses': len(self.losses(year)),
            'net_movement': self.net_customer_movement(year),
            'net_mwh': self.net_mwh_movement(year),
            'churn_rate_pct': self.churn_rate_pct(year, avg_customers),
            'loss_reasons': self.loss_reasons(year),
        }
