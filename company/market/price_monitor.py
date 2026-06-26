"""Wholesale energy price monitor: alerts on spot/forward prices vs trigger levels."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class PriceAlertLevel(str, Enum):
    NORMAL = 'normal'
    ELEVATED = 'elevated'
    HIGH = 'high'
    EXTREME = 'extreme'


class Commodity(str, Enum):
    ELECTRICITY = 'electricity'
    GAS = 'gas'


@dataclass(frozen=True)
class PriceObservation:
    commodity: Commodity
    observation_date: dt.date
    spot_gbp_per_mwh: float
    month_ahead_gbp_per_mwh: float
    quarter_ahead_gbp_per_mwh: Optional[float] = None

    @property
    def term_structure_slope(self) -> float:
        return round(self.month_ahead_gbp_per_mwh - self.spot_gbp_per_mwh, 2)

    @property
    def is_backwardation(self) -> bool:
        return self.term_structure_slope < -2.0

    @property
    def is_contango(self) -> bool:
        return self.term_structure_slope > 2.0


@dataclass
class PriceTrigger:
    trigger_id: str
    commodity: Commodity
    level: PriceAlertLevel
    threshold_gbp_per_mwh: float
    description: str


class WholesalePriceMonitor:
    def __init__(self) -> None:
        self._observations: List[PriceObservation] = []
        self._triggers: Dict[str, PriceTrigger] = {}

    def add_trigger(self, trigger_id: str, commodity: Commodity,
                     level: PriceAlertLevel, threshold_gbp_per_mwh: float,
                     description: str) -> PriceTrigger:
        t = PriceTrigger(trigger_id=trigger_id, commodity=commodity,
                          level=level, threshold_gbp_per_mwh=threshold_gbp_per_mwh,
                          description=description)
        self._triggers[trigger_id] = t
        return t

    def record_observation(self, commodity: Commodity, observation_date: dt.date,
                            spot_gbp_per_mwh: float, month_ahead_gbp_per_mwh: float,
                            quarter_ahead_gbp_per_mwh: Optional[float] = None
                            ) -> PriceObservation:
        obs = PriceObservation(
            commodity=commodity, observation_date=observation_date,
            spot_gbp_per_mwh=spot_gbp_per_mwh, month_ahead_gbp_per_mwh=month_ahead_gbp_per_mwh,
            quarter_ahead_gbp_per_mwh=quarter_ahead_gbp_per_mwh,
        )
        self._observations.append(obs)
        return obs

    def latest_observation(self, commodity: Commodity) -> Optional[PriceObservation]:
        obs = [o for o in self._observations if o.commodity == commodity]
        if not obs:
            return None
        return max(obs, key=lambda o: o.observation_date)

    def active_alerts(self, commodity: Commodity) -> List[PriceTrigger]:
        latest = self.latest_observation(commodity)
        if latest is None:
            return []
        alerts = []
        for t in self._triggers.values():
            if t.commodity == commodity and latest.spot_gbp_per_mwh >= t.threshold_gbp_per_mwh:
                alerts.append(t)
        return sorted(alerts, key=lambda t: t.threshold_gbp_per_mwh, reverse=True)

    def highest_alert_level(self, commodity: Commodity) -> PriceAlertLevel:
        alerts = self.active_alerts(commodity)
        if not alerts:
            return PriceAlertLevel.NORMAL
        level_order = {
            PriceAlertLevel.EXTREME: 3,
            PriceAlertLevel.HIGH: 2,
            PriceAlertLevel.ELEVATED: 1,
            PriceAlertLevel.NORMAL: 0,
        }
        return max(alerts, key=lambda t: level_order[t.level]).level

    def price_history(self, commodity: Commodity, days: int) -> List[PriceObservation]:
        obs = sorted([o for o in self._observations if o.commodity == commodity],
                      key=lambda o: o.observation_date)
        return obs[-days:] if len(obs) > days else obs

    def monitor_summary(self, commodity: Commodity) -> dict:
        latest = self.latest_observation(commodity)
        return {
            'commodity': commodity.value,
            'latest_spot_gbp_per_mwh': latest.spot_gbp_per_mwh if latest else None,
            'latest_date': latest.observation_date.isoformat() if latest else None,
            'highest_alert': self.highest_alert_level(commodity).value,
            'active_alerts': len(self.active_alerts(commodity)),
        }
