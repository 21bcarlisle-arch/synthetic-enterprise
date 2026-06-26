from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class WHDEligibilityReason(str, Enum):
    CORE_GROUP = 'core_group'            # pension credit – automatic
    BROADER_GROUP_LIHC = 'broader_group_lihc'  # LIHC fuel poverty
    BROADER_GROUP_PSR = 'broader_group_psr'    # PSR + low income
    INDUSTRY_INITIATIVE = 'industry_initiative'  # supplier discretion


class WHDStatus(str, Enum):
    ELIGIBLE = 'eligible'
    APPLIED = 'applied'
    REBATED = 'rebated'
    INELIGIBLE = 'ineligible'


WHD_REBATE_GBP: float = 150.0


@dataclass(frozen=True)
class WHDApplication:
    application_id: str
    customer_id: str
    scheme_year: int
    eligibility_reason: WHDEligibilityReason
    applied_date: dt.date
    rebate_gbp: float = WHD_REBATE_GBP
    rebated_date: Optional[dt.date] = None

    @property
    def status(self) -> WHDStatus:
        if self.rebated_date is not None:
            return WHDStatus.REBATED
        return WHDStatus.APPLIED


class WHDRegister:
    def __init__(self) -> None:
        self._applications: Dict[str, WHDApplication] = {}
        self._next_id = 1

    def apply(self, customer_id: str, scheme_year: int,
              eligibility_reason: WHDEligibilityReason,
              applied_date: dt.date,
              rebate_gbp: float = WHD_REBATE_GBP) -> WHDApplication:
        existing = [a for a in self._applications.values()
                    if a.customer_id == customer_id and a.scheme_year == scheme_year]
        if existing:
            raise ValueError(f'Customer {customer_id} already applied for WHD {scheme_year}')
        app_id = f'WHD-{scheme_year}-{self._next_id:04d}'
        self._next_id += 1
        app = WHDApplication(
            application_id=app_id,
            customer_id=customer_id,
            scheme_year=scheme_year,
            eligibility_reason=eligibility_reason,
            applied_date=applied_date,
            rebate_gbp=rebate_gbp,
        )
        self._applications[app_id] = app
        return app

    def mark_rebated(self, application_id: str, rebated_date: dt.date) -> WHDApplication:
        app = self._applications[application_id]
        updated = WHDApplication(
            application_id=app.application_id,
            customer_id=app.customer_id,
            scheme_year=app.scheme_year,
            eligibility_reason=app.eligibility_reason,
            applied_date=app.applied_date,
            rebate_gbp=app.rebate_gbp,
            rebated_date=rebated_date,
        )
        self._applications[application_id] = updated
        return updated

    def pending_rebates(self) -> List[WHDApplication]:
        return [a for a in self._applications.values() if a.status == WHDStatus.APPLIED]

    def total_rebated_gbp(self, scheme_year: Optional[int] = None) -> float:
        apps = self._applications.values()
        if scheme_year is not None:
            apps = [a for a in apps if a.scheme_year == scheme_year]
        return sum(a.rebate_gbp for a in apps if a.status == WHDStatus.REBATED)

    def applications_for_customer(self, customer_id: str) -> List[WHDApplication]:
        return [a for a in self._applications.values() if a.customer_id == customer_id]

    def annual_summary(self, scheme_year: int) -> dict:
        apps = [a for a in self._applications.values() if a.scheme_year == scheme_year]
        rebated = [a for a in apps if a.status == WHDStatus.REBATED]
        by_reason: dict = {}
        for a in apps:
            by_reason[a.eligibility_reason.value] = by_reason.get(a.eligibility_reason.value, 0) + 1
        return {
            'scheme_year': scheme_year,
            'total_applications': len(apps),
            'total_rebated': len(rebated),
            'pending': len(apps) - len(rebated),
            'total_rebated_gbp': round(sum(a.rebate_gbp for a in rebated), 2),
            'by_eligibility_reason': by_reason,
        }
