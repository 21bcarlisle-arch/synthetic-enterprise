from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Dict, List, Optional


class COTType(str, Enum):
    MOVE_OUT = "move_out"
    MOVE_IN = "move_in"


@dataclass
class COTEvent:
    customer_id: str
    meter_point: str
    cot_type: COTType
    date: date
    meter_read_kwh: float
    new_occupant_id: Optional[str] = None


_SVT_ELEC_PENCE: Dict[int, float] = {
    2016: 13.0, 2017: 13.5, 2018: 14.0, 2019: 15.5, 2020: 15.5,
    2021: 17.0, 2022: 28.0, 2023: 24.0, 2024: 20.0, 2025: 22.0,
}
_CAP_ELEC_PENCE: Dict[int, float] = {
    2016: 14.0, 2017: 14.0, 2018: 14.0, 2019: 16.0, 2020: 16.0,
    2021: 18.0, 2022: 34.0, 2023: 29.0, 2024: 22.0, 2025: 24.0,
}
_VOID_UPLIFT = 0.20
_OVERDUE_DAYS = 28


def deemed_rate_gbp_per_kwh(as_of: date) -> float:
    """SVT + 20% uplift, capped at Ofgem domestic price cap."""
    svt = _SVT_ELEC_PENCE.get(as_of.year, 15.5)
    cap = _CAP_ELEC_PENCE.get(as_of.year, 16.0)
    return min(svt * (1.0 + _VOID_UPLIFT), cap) / 100.0


@dataclass
class COTBook:
    """Tracks change-of-tenancy events and void (unoccupied) meter points."""

    _events: List[COTEvent] = field(default_factory=list)
    # meter_point -> date of most recent move-out (void start)
    _voids: Dict[str, date] = field(default_factory=dict)

    def record_move_out(
        self,
        customer_id: str,
        meter_point: str,
        event_date: date,
        final_read_kwh: float,
    ) -> COTEvent:
        ev = COTEvent(
            customer_id=customer_id,
            meter_point=meter_point,
            cot_type=COTType.MOVE_OUT,
            date=event_date,
            meter_read_kwh=final_read_kwh,
        )
        self._events.append(ev)
        self._voids[meter_point] = event_date
        return ev

    def record_move_in(
        self,
        new_customer_id: str,
        meter_point: str,
        event_date: date,
        opening_read_kwh: float,
    ) -> COTEvent:
        ev = COTEvent(
            customer_id=new_customer_id,
            meter_point=meter_point,
            cot_type=COTType.MOVE_IN,
            date=event_date,
            meter_read_kwh=opening_read_kwh,
            new_occupant_id=new_customer_id,
        )
        self._events.append(ev)
        self._voids.pop(meter_point, None)
        return ev

    def void_properties(self) -> List[str]:
        return list(self._voids.keys())

    def void_days(self, meter_point: str, as_of: date) -> int:
        if meter_point not in self._voids:
            return 0
        return (as_of - self._voids[meter_point]).days

    def overdue_for_nomination(self, as_of: date) -> List[str]:
        """Void meter points exceeding 28 days — regulatory trigger to place on named SVT."""
        return [
            mp for mp, start in self._voids.items()
            if (as_of - start).days > _OVERDUE_DAYS
        ]

    def portfolio_summary(self, as_of: date) -> dict:
        n = len(self._voids)
        avg_days = (
            sum((as_of - d).days for d in self._voids.values()) / n
            if n > 0 else 0.0
        )
        return {
            "total_voids": n,
            "avg_void_days": round(avg_days, 1),
            "overdue_for_nomination": len(self.overdue_for_nomination(as_of)),
            "total_events": len(self._events),
        }

    def events_for(self, meter_point: str) -> List[COTEvent]:
        return [e for e in self._events if e.meter_point == meter_point]
