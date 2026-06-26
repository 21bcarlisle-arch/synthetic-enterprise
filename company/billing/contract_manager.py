"""Supply contract lifecycle management: terms, break clauses, price protection."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class ContractStatus(str, Enum):
    ACTIVE = 'active'
    IN_NOTICE = 'in_notice'
    EXPIRED = 'expired'
    CANCELLED = 'cancelled'
    RENEWED = 'renewed'


class ContractType(str, Enum):
    FIXED_TERM = 'fixed_term'
    VARIABLE = 'variable'
    DEEMED = 'deemed'
    EVERGREEN = 'evergreen'


_NOTICE_PERIOD_DAYS = {
    ContractType.FIXED_TERM: 42,
    ContractType.VARIABLE: 28,
    ContractType.DEEMED: 14,
    ContractType.EVERGREEN: 90,
}


@dataclass
class SupplyContract:
    contract_id: str
    customer_id: str
    mpan: str
    contract_type: ContractType
    start_date: dt.date
    end_date: dt.date
    unit_rate_pence_per_kwh: float
    standing_charge_pence_per_day: float
    status: ContractStatus = ContractStatus.ACTIVE
    notice_served_date: Optional[dt.date] = None
    annual_quantity_kwh: float = 0.0

    @property
    def notice_period_days(self) -> int:
        return _NOTICE_PERIOD_DAYS[self.contract_type]

    @property
    def term_months(self) -> int:
        delta = (self.end_date - self.start_date).days
        return round(delta / 30.4375)

    def notice_deadline(self) -> dt.date:
        import datetime as _dt
        return self.end_date - _dt.timedelta(days=self.notice_period_days)

    def is_in_notice_window(self, as_of: dt.date) -> bool:
        return as_of >= self.notice_deadline() and as_of <= self.end_date

    def days_to_expiry(self, as_of: dt.date) -> int:
        return (self.end_date - as_of).days

    def annual_cost_estimate_gbp(self) -> float:
        if self.annual_quantity_kwh <= 0:
            return 0.0
        commodity = self.annual_quantity_kwh * self.unit_rate_pence_per_kwh / 100
        standing = self.standing_charge_pence_per_day / 100 * 365
        return round(commodity + standing, 2)


class ContractManager:
    def __init__(self) -> None:
        self._contracts: List[SupplyContract] = []

    def register(self, contract_id: str, customer_id: str, mpan: str,
                  contract_type: ContractType, start_date: dt.date, end_date: dt.date,
                  unit_rate_pence_per_kwh: float, standing_charge_pence_per_day: float,
                  annual_quantity_kwh: float = 0.0) -> SupplyContract:
        c = SupplyContract(
            contract_id=contract_id, customer_id=customer_id, mpan=mpan,
            contract_type=contract_type, start_date=start_date, end_date=end_date,
            unit_rate_pence_per_kwh=unit_rate_pence_per_kwh,
            standing_charge_pence_per_day=standing_charge_pence_per_day,
            annual_quantity_kwh=annual_quantity_kwh,
        )
        self._contracts.append(c)
        return c

    def get(self, contract_id: str) -> Optional[SupplyContract]:
        return next((c for c in self._contracts if c.contract_id == contract_id), None)

    def serve_notice(self, contract_id: str, notice_date: dt.date) -> None:
        c = self.get(contract_id)
        if c:
            c.notice_served_date = notice_date
            c.status = ContractStatus.IN_NOTICE

    def expire_contract(self, contract_id: str) -> None:
        c = self.get(contract_id)
        if c:
            c.status = ContractStatus.EXPIRED

    def contracts_for_customer(self, customer_id: str) -> List[SupplyContract]:
        return [c for c in self._contracts if c.customer_id == customer_id]

    def active_contracts(self) -> List[SupplyContract]:
        return [c for c in self._contracts if c.status == ContractStatus.ACTIVE]

    def expiring_within(self, as_of: dt.date, days: int) -> List[SupplyContract]:
        return [c for c in self.active_contracts()
                if 0 <= c.days_to_expiry(as_of) <= days]

    def contracts_in_notice_window(self, as_of: dt.date) -> List[SupplyContract]:
        return [c for c in self.active_contracts() if c.is_in_notice_window(as_of)]

    def portfolio_summary(self, as_of: dt.date) -> dict:
        by_type: Dict[str, int] = {}
        for c in self._contracts:
            k = c.contract_type.value
            by_type[k] = by_type.get(k, 0) + 1
        return {
            'total_contracts': len(self._contracts),
            'active': len(self.active_contracts()),
            'expiring_30d': len(self.expiring_within(as_of, 30)),
            'in_notice_window': len(self.contracts_in_notice_window(as_of)),
            'by_type': by_type,
        }
