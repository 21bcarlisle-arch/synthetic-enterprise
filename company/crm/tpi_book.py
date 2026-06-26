from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class TPITier(str, Enum):
    PREFERRED = 'preferred'
    STANDARD = 'standard'
    PROBATION = 'probation'
    SUSPENDED = 'suspended'


class TPICommissionBasis(str, Enum):
    FIXED_PER_CUSTOMER = 'fixed_per_customer'
    PCT_OF_ANNUAL_REVENUE = 'pct_of_annual_revenue'
    PCT_OF_ANNUAL_CONSUMPTION = 'pct_of_annual_consumption'


@dataclass(frozen=True)
class TPI:
    tpi_id: str
    name: str
    tier: TPITier
    commission_basis: TPICommissionBasis
    commission_rate: float
    registered_date: dt.date
    accredited: bool = True


@dataclass(frozen=True)
class TPIDeal:
    deal_id: str
    tpi_id: str
    customer_id: str
    annual_consumption_mwh: float
    annual_revenue_gbp: float
    deal_date: dt.date
    commission_basis: TPICommissionBasis
    commission_rate: float

    @property
    def commission_gbp(self) -> float:
        if self.commission_basis == TPICommissionBasis.FIXED_PER_CUSTOMER:
            return round(self.commission_rate, 2)
        if self.commission_basis == TPICommissionBasis.PCT_OF_ANNUAL_REVENUE:
            return round(self.annual_revenue_gbp * self.commission_rate / 100, 2)
        return round(self.annual_consumption_mwh * self.commission_rate, 2)


class TPIBook:
    def __init__(self) -> None:
        self._tpis: dict[str, TPI] = {}
        self._deals: list[TPIDeal] = []
        self._next_deal = 1

    def register(self, tpi_id: str, name: str, tier: TPITier,
                 commission_basis: TPICommissionBasis, commission_rate: float,
                 registered_date: dt.date, accredited: bool = True) -> TPI:
        tpi = TPI(
            tpi_id=tpi_id, name=name, tier=tier,
            commission_basis=commission_basis, commission_rate=commission_rate,
            registered_date=registered_date, accredited=accredited,
        )
        self._tpis[tpi_id] = tpi
        return tpi

    def suspend(self, tpi_id: str) -> TPI:
        old = self._tpis[tpi_id]
        suspended = TPI(
            tpi_id=old.tpi_id, name=old.name, tier=TPITier.SUSPENDED,
            commission_basis=old.commission_basis, commission_rate=old.commission_rate,
            registered_date=old.registered_date, accredited=old.accredited,
        )
        self._tpis[tpi_id] = suspended
        return suspended

    def record_deal(self, tpi_id: str, customer_id: str, annual_consumption_mwh: float,
                    annual_revenue_gbp: float, deal_date: dt.date) -> TPIDeal:
        tpi = self._tpis[tpi_id]
        if tpi.tier == TPITier.SUSPENDED:
            raise ValueError(f'TPI {tpi_id} is suspended; cannot record deal')
        deal_id = f'DEAL-{self._next_deal:04d}'
        self._next_deal += 1
        deal = TPIDeal(
            deal_id=deal_id, tpi_id=tpi_id, customer_id=customer_id,
            annual_consumption_mwh=annual_consumption_mwh,
            annual_revenue_gbp=annual_revenue_gbp, deal_date=deal_date,
            commission_basis=tpi.commission_basis, commission_rate=tpi.commission_rate,
        )
        self._deals.append(deal)
        return deal

    def deals_for_tpi(self, tpi_id: str) -> List[TPIDeal]:
        return [d for d in self._deals if d.tpi_id == tpi_id]

    def total_commission_gbp(self, tpi_id: Optional[str] = None) -> float:
        deals = self._deals if tpi_id is None else self.deals_for_tpi(tpi_id)
        return round(sum(d.commission_gbp for d in deals), 2)

    def active_tpis(self) -> List[TPI]:
        return [t for t in self._tpis.values() if t.tier != TPITier.SUSPENDED]

    def annual_summary(self, year: int) -> dict:
        year_deals = [d for d in self._deals if d.deal_date.year == year]
        return {
            'year': year,
            'deal_count': len(year_deals),
            'total_commission_gbp': round(sum(d.commission_gbp for d in year_deals), 2),
            'total_annual_revenue_gbp': round(sum(d.annual_revenue_gbp for d in year_deals), 2),
            'tpi_count': len(set(d.tpi_id for d in year_deals)),
        }
