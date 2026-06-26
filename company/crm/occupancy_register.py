from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class TenancyEndReason(str, Enum):
    MOVED_OUT = 'moved_out'
    DECEASED = 'deceased'
    SWITCHED_SUPPLIER = 'switched_supplier'
    EVICTED = 'evicted'
    VOID = 'void'


@dataclass
class OccupancyPeriod:
    mpan: str
    customer_id: str
    move_in_date: dt.date
    move_out_date: Optional[dt.date] = None
    end_reason: Optional[TenancyEndReason] = None

    @property
    def is_current(self) -> bool:
        return self.move_out_date is None

    @property
    def duration_days(self) -> Optional[int]:
        if self.move_out_date is None:
            return None
        return (self.move_out_date - self.move_in_date).days


class PremisesOccupancyRegister:
    def __init__(self) -> None:
        self._history: List[OccupancyPeriod] = []

    def record_move_in(self, mpan: str, customer_id: str, move_in_date: dt.date) -> OccupancyPeriod:
        existing = self.current_occupant(mpan)
        if existing is not None:
            raise ValueError(f'MPAN {mpan} already has occupant {existing.customer_id}')
        period = OccupancyPeriod(mpan=mpan, customer_id=customer_id, move_in_date=move_in_date)
        self._history.append(period)
        return period

    def record_move_out(self, mpan: str, customer_id: str, move_out_date: dt.date,
                        end_reason: TenancyEndReason) -> OccupancyPeriod:
        for period in self._history:
            if period.mpan == mpan and period.customer_id == customer_id and period.is_current:
                period.move_out_date = move_out_date
                period.end_reason = end_reason
                return period
        raise ValueError(f'No active occupancy for MPAN {mpan} / customer {customer_id}')

    def current_occupant(self, mpan: str) -> Optional[OccupancyPeriod]:
        return next((p for p in self._history if p.mpan == mpan and p.is_current), None)

    def occupancy_history_for_mpan(self, mpan: str) -> List[OccupancyPeriod]:
        return [p for p in self._history if p.mpan == mpan]

    def occupancy_history_for_customer(self, customer_id: str) -> List[OccupancyPeriod]:
        return [p for p in self._history if p.customer_id == customer_id]

    def void_mpans(self) -> List[str]:
        all_mpans = set(p.mpan for p in self._history)
        return [m for m in all_mpans if self.current_occupant(m) is None]

    def occupancy_at_date(self, mpan: str, as_of: dt.date) -> Optional[OccupancyPeriod]:
        for p in self._history:
            if p.mpan != mpan:
                continue
            after_move_in = p.move_in_date <= as_of
            before_move_out = p.move_out_date is None or p.move_out_date > as_of
            if after_move_in and before_move_out:
                return p
        return None

    def portfolio_summary(self) -> dict:
        all_mpans = set(p.mpan for p in self._history)
        occupied = [m for m in all_mpans if self.current_occupant(m) is not None]
        void = [m for m in all_mpans if self.current_occupant(m) is None]
        return {
            'total_mpans': len(all_mpans),
            'occupied': len(occupied),
            'void': len(void),
            'total_occupancy_records': len(self._history),
        }
