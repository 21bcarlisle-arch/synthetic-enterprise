"""Gas supply interruption risk: interruptibility, UK gas emergency, IGEM procedures."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class InterruptClass(str, Enum):
    FIRM = 'firm'
    INTERRUPTIBLE = 'interruptible'
    EMERGENCY_ONLY = 'emergency_only'


class InterruptionReason(str, Enum):
    SUPPLY_EMERGENCY = 'supply_emergency'
    NETWORK_CONSTRAINT = 'network_constraint'
    PLANNED_MAINTENANCE = 'planned_maintenance'
    NON_PAYMENT = 'non_payment'
    HEALTH_SAFETY = 'health_safety'


class InterruptionStatus(str, Enum):
    NOTICE_GIVEN = 'notice_given'
    ACTIVE = 'active'
    RESTORED = 'restored'
    CANCELLED = 'cancelled'


_INTERRUPTIBLE_DISCOUNT_PCT: dict = {
    InterruptClass.FIRM: 0.0,
    InterruptClass.INTERRUPTIBLE: 8.0,  # Typical interruptible gas discount
    InterruptClass.EMERGENCY_ONLY: 15.0,
}


@dataclass
class GasInterruption:
    interruption_id: str
    customer_id: str
    mprn: str
    reason: InterruptionReason
    notice_date: dt.date
    start_date: dt.date
    expected_end_date: dt.date
    status: InterruptionStatus = InterruptionStatus.NOTICE_GIVEN
    actual_end_date: Optional[dt.date] = None
    is_vulnerable: bool = False

    @property
    def notice_days(self) -> int:
        return (self.start_date - self.notice_date).days

    @property
    def expected_duration_days(self) -> int:
        return (self.expected_end_date - self.start_date).days

    @property
    def actual_duration_days(self) -> Optional[int]:
        if not self.actual_end_date:
            return None
        return (self.actual_end_date - self.start_date).days

    def restore(self, restore_date: dt.date) -> None:
        self.actual_end_date = restore_date
        self.status = InterruptionStatus.RESTORED


@dataclass(frozen=True)
class InterruptibilityContract:
    customer_id: str
    mprn: str
    interrupt_class: InterruptClass
    max_interruptions_per_year: int
    min_notice_hours: int

    @property
    def discount_pct(self) -> float:
        return _INTERRUPTIBLE_DISCOUNT_PCT.get(self.interrupt_class, 0.0)


class GasInterruptionManager:
    def __init__(self) -> None:
        self._interruptions: List[GasInterruption] = []
        self._contracts: List[InterruptibilityContract] = []

    def register_contract(self, customer_id: str, mprn: str,
                            interrupt_class: InterruptClass,
                            max_per_year: int, min_notice_hours: int
                            ) -> InterruptibilityContract:
        c = InterruptibilityContract(
            customer_id=customer_id, mprn=mprn,
            interrupt_class=interrupt_class,
            max_interruptions_per_year=max_per_year,
            min_notice_hours=min_notice_hours,
        )
        self._contracts.append(c)
        return c

    def issue_interruption(self, interruption_id: str, customer_id: str,
                             mprn: str, reason: InterruptionReason,
                             notice_date: dt.date, start_date: dt.date,
                             expected_end: dt.date,
                             is_vulnerable: bool = False) -> GasInterruption:
        gi = GasInterruption(
            interruption_id=interruption_id, customer_id=customer_id,
            mprn=mprn, reason=reason, notice_date=notice_date,
            start_date=start_date, expected_end_date=expected_end,
            is_vulnerable=is_vulnerable,
        )
        self._interruptions.append(gi)
        return gi

    def active_interruptions(self) -> List[GasInterruption]:
        return [i for i in self._interruptions
                if i.status in (InterruptionStatus.NOTICE_GIVEN,
                                 InterruptionStatus.ACTIVE)]

    def interruptions_for_customer(self, customer_id: str, year: int) -> List[GasInterruption]:
        return [i for i in self._interruptions
                if i.customer_id == customer_id and i.start_date.year == year]

    def vulnerable_customers_affected(self) -> List[str]:
        return list(set(i.customer_id for i in self.active_interruptions()
                        if i.is_vulnerable))

    def interruption_summary(self, year: int) -> dict:
        yr = [i for i in self._interruptions if i.start_date.year == year]
        return {
            'year': year,
            'total': len(yr),
            'active': len([i for i in yr if i.status == InterruptionStatus.ACTIVE]),
            'restored': len([i for i in yr if i.status == InterruptionStatus.RESTORED]),
            'vulnerable_affected': len([i for i in yr if i.is_vulnerable]),
        }
