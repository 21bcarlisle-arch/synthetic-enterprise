"""Customer acquisition cohort CLV analysis: cohort tracking, payback period."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class AcquisitionChannel(str, Enum):
    PRICE_COMPARISON = 'price_comparison'
    DIRECT_ONLINE = 'direct_online'
    REFERRAL = 'referral'
    RETENTION = 'retention'
    DOOR_TO_DOOR = 'door_to_door'
    TPI = 'tpi'


@dataclass
class CohortCustomer:
    customer_id: str
    acquisition_date: dt.date
    acquisition_cost_gbp: float
    annual_revenue_gbp: float
    churn_date: Optional[dt.date] = None

    @property
    def is_active(self) -> bool:
        return self.churn_date is None

    def lifetime_months(self, as_of: dt.date) -> float:
        end = self.churn_date if self.churn_date else as_of
        days = (end - self.acquisition_date).days
        return round(days / 30.4375, 1)

    def lifetime_revenue_gbp(self, as_of: dt.date) -> float:
        months = self.lifetime_months(as_of)
        return round(self.annual_revenue_gbp / 12 * months, 2)

    def net_clv_gbp(self, as_of: dt.date) -> float:
        return round(self.lifetime_revenue_gbp(as_of) - self.acquisition_cost_gbp, 2)


@dataclass
class AcquisitionCohort:
    cohort_id: str
    cohort_year: int
    cohort_month: int
    channel: AcquisitionChannel
    customers: List[CohortCustomer] = field(default_factory=list)

    def add_customer(self, customer_id: str, acquisition_date: dt.date,
                       acquisition_cost_gbp: float,
                       annual_revenue_gbp: float) -> CohortCustomer:
        c = CohortCustomer(
            customer_id=customer_id, acquisition_date=acquisition_date,
            acquisition_cost_gbp=acquisition_cost_gbp,
            annual_revenue_gbp=annual_revenue_gbp,
        )
        self.customers.append(c)
        return c

    def churn_customer(self, customer_id: str, churn_date: dt.date) -> None:
        c = next((c for c in self.customers if c.customer_id == customer_id), None)
        if c:
            c.churn_date = churn_date

    @property
    def initial_size(self) -> int:
        return len(self.customers)

    def active_count(self) -> int:
        return sum(1 for c in self.customers if c.is_active)

    def retention_rate_pct(self) -> float:
        if not self.customers:
            return 0.0
        return round(self.active_count() / self.initial_size * 100, 1)

    def total_acquisition_cost_gbp(self) -> float:
        return round(sum(c.acquisition_cost_gbp for c in self.customers), 2)

    def avg_net_clv_gbp(self, as_of: dt.date) -> float:
        if not self.customers:
            return 0.0
        return round(
            sum(c.net_clv_gbp(as_of) for c in self.customers) / len(self.customers), 2
        )

    def payback_months(self, as_of: dt.date) -> Optional[float]:
        avg_revenue_per_month = sum(
            c.annual_revenue_gbp / 12 for c in self.customers
        ) / max(1, len(self.customers))
        avg_cac = self.total_acquisition_cost_gbp() / max(1, len(self.customers))
        if avg_revenue_per_month <= 0:
            return None
        return round(avg_cac / avg_revenue_per_month, 1)

    def cohort_summary(self, as_of: dt.date) -> dict:
        return {
            'cohort_id': self.cohort_id,
            'channel': self.channel.value,
            'initial_size': self.initial_size,
            'retention_rate_pct': self.retention_rate_pct(),
            'avg_net_clv_gbp': self.avg_net_clv_gbp(as_of),
            'payback_months': self.payback_months(as_of),
            'total_cac_gbp': self.total_acquisition_cost_gbp(),
        }
