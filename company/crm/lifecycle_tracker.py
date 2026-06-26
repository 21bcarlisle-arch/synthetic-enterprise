"""Customer lifecycle stage tracker: from acquisition through to churn/exit."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class LifecycleStage(str, Enum):
    PROSPECT = 'prospect'
    PENDING_SWITCH = 'pending_switch'
    ACTIVE = 'active'
    AT_RISK = 'at_risk'
    IN_ARREARS = 'in_arrears'
    IN_DEFERRAL = 'in_deferral'
    RENEWAL_DUE = 'renewal_due'
    CHURNED = 'churned'
    MOVED_OUT = 'moved_out'
    DECEASED = 'deceased'


# Stages where the customer is still on supply
_ON_SUPPLY_STAGES = {
    LifecycleStage.PENDING_SWITCH,
    LifecycleStage.ACTIVE,
    LifecycleStage.AT_RISK,
    LifecycleStage.IN_ARREARS,
    LifecycleStage.IN_DEFERRAL,
    LifecycleStage.RENEWAL_DUE,
}


@dataclass
class LifecycleEvent:
    customer_id: str
    from_stage: LifecycleStage
    to_stage: LifecycleStage
    event_date: dt.date
    reason: str = ''


@dataclass
class CustomerLifecycle:
    customer_id: str
    acquisition_date: dt.date
    stage: LifecycleStage = LifecycleStage.PENDING_SWITCH
    _history: List[LifecycleEvent] = field(default_factory=list)

    @property
    def is_on_supply(self) -> bool:
        return self.stage in _ON_SUPPLY_STAGES

    @property
    def is_active_customer(self) -> bool:
        return self.stage in (
            LifecycleStage.ACTIVE, LifecycleStage.AT_RISK,
            LifecycleStage.IN_ARREARS, LifecycleStage.IN_DEFERRAL,
            LifecycleStage.RENEWAL_DUE,
        )

    def transition(self, to_stage: LifecycleStage, event_date: dt.date, reason: str = '') -> None:
        event = LifecycleEvent(
            customer_id=self.customer_id,
            from_stage=self.stage,
            to_stage=to_stage,
            event_date=event_date,
            reason=reason,
        )
        self._history.append(event)
        self.stage = to_stage

    def tenure_days(self, as_of: dt.date) -> int:
        return max(0, (as_of - self.acquisition_date).days)

    def stage_history(self) -> List[LifecycleEvent]:
        return list(self._history)


class CustomerLifecycleTracker:
    def __init__(self) -> None:
        self._customers: Dict[str, CustomerLifecycle] = {}

    def register(self, customer_id: str, acquisition_date: dt.date,
                 initial_stage: LifecycleStage = LifecycleStage.PENDING_SWITCH
                 ) -> CustomerLifecycle:
        lc = CustomerLifecycle(customer_id=customer_id, acquisition_date=acquisition_date,
                               stage=initial_stage)
        self._customers[customer_id] = lc
        return lc

    def get(self, customer_id: str) -> CustomerLifecycle:
        return self._customers[customer_id]

    def transition(self, customer_id: str, to_stage: LifecycleStage,
                   event_date: dt.date, reason: str = '') -> None:
        self._customers[customer_id].transition(to_stage, event_date, reason)

    def customers_in_stage(self, stage: LifecycleStage) -> List[str]:
        return [cid for cid, lc in self._customers.items() if lc.stage == stage]

    def active_customers(self) -> List[str]:
        return [cid for cid, lc in self._customers.items() if lc.is_active_customer]

    def on_supply_count(self) -> int:
        return sum(1 for lc in self._customers.values() if lc.is_on_supply)

    def portfolio_summary(self, as_of: dt.date) -> dict:
        counts: Dict[str, int] = {}
        for lc in self._customers.values():
            counts[lc.stage.value] = counts.get(lc.stage.value, 0) + 1
        return {
            'as_of': as_of.isoformat(),
            'total': len(self._customers),
            'on_supply': self.on_supply_count(),
            'by_stage': counts,
        }
