"""Multisite I&C account management: corporate customer with multiple supply points."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class SiteCategory(str, Enum):
    HEAD_OFFICE = 'head_office'
    MANUFACTURING = 'manufacturing'
    WAREHOUSE = 'warehouse'
    RETAIL_UNIT = 'retail_unit'
    DATA_CENTRE = 'data_centre'
    REMOTE_OFFICE = 'remote_office'


class BillingFrequency(str, Enum):
    MONTHLY = 'monthly'
    QUARTERLY = 'quarterly'
    CONSOLIDATED = 'consolidated'


@dataclass(frozen=True)
class SupplyPoint:
    mpan: str
    site_name: str
    postcode: str
    category: SiteCategory
    annual_kwh: float
    max_demand_kva: float
    connection_voltage_kv: float = 11.0

    @property
    def is_hv(self) -> bool:
        return self.connection_voltage_kv >= 11.0

    @property
    def annual_mwh(self) -> float:
        return self.annual_kwh / 1000


@dataclass
class MultisiteAccount:
    account_id: str
    company_name: str
    billing_frequency: BillingFrequency
    account_manager: str
    credit_limit_gbp: float
    supply_points: List[SupplyPoint] = field(default_factory=list)

    def add_site(self, mpan: str, site_name: str, postcode: str,
                   category: SiteCategory, annual_kwh: float,
                   max_demand_kva: float, connection_voltage_kv: float = 11.0) -> SupplyPoint:
        sp = SupplyPoint(
            mpan=mpan, site_name=site_name, postcode=postcode,
            category=category, annual_kwh=annual_kwh,
            max_demand_kva=max_demand_kva,
            connection_voltage_kv=connection_voltage_kv,
        )
        self.supply_points.append(sp)
        return sp

    def remove_site(self, mpan: str) -> bool:
        original_count = len(self.supply_points)
        self.supply_points = [sp for sp in self.supply_points if sp.mpan != mpan]
        return len(self.supply_points) < original_count

    @property
    def site_count(self) -> int:
        return len(self.supply_points)

    @property
    def total_annual_kwh(self) -> float:
        return sum(sp.annual_kwh for sp in self.supply_points)

    @property
    def total_annual_mwh(self) -> float:
        return round(self.total_annual_kwh / 1000, 1)

    @property
    def peak_site(self) -> Optional[SupplyPoint]:
        if not self.supply_points:
            return None
        return max(self.supply_points, key=lambda sp: sp.annual_kwh)

    def sites_by_category(self) -> Dict[str, List[SupplyPoint]]:
        result: Dict[str, List[SupplyPoint]] = {}
        for sp in self.supply_points:
            k = sp.category.value
            result.setdefault(k, []).append(sp)
        return result

    def hv_sites(self) -> List[SupplyPoint]:
        return [sp for sp in self.supply_points if sp.is_hv]

    def account_summary(self) -> dict:
        return {
            'account_id': self.account_id,
            'company_name': self.company_name,
            'site_count': self.site_count,
            'total_annual_mwh': self.total_annual_mwh,
            'hv_sites': len(self.hv_sites()),
            'credit_limit_gbp': self.credit_limit_gbp,
            'billing_frequency': self.billing_frequency.value,
            'categories': list(self.sites_by_category().keys()),
        }


class MultisitePortfolio:
    def __init__(self) -> None:
        self._accounts: List[MultisiteAccount] = []

    def create_account(self, account_id: str, company_name: str,
                         billing_frequency: BillingFrequency,
                         account_manager: str, credit_limit_gbp: float
                         ) -> MultisiteAccount:
        acc = MultisiteAccount(
            account_id=account_id, company_name=company_name,
            billing_frequency=billing_frequency,
            account_manager=account_manager, credit_limit_gbp=credit_limit_gbp,
        )
        self._accounts.append(acc)
        return acc

    def get(self, account_id: str) -> Optional[MultisiteAccount]:
        return next((a for a in self._accounts if a.account_id == account_id), None)

    def total_portfolio_mwh(self) -> float:
        return round(sum(a.total_annual_mwh for a in self._accounts), 1)

    def accounts_by_manager(self, manager: str) -> List[MultisiteAccount]:
        return [a for a in self._accounts if a.account_manager == manager]

    def largest_accounts(self, n: int = 5) -> List[MultisiteAccount]:
        return sorted(self._accounts,
                       key=lambda a: a.total_annual_kwh, reverse=True)[:n]
