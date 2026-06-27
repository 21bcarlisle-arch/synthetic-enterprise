"""Smart Export Guarantee (SEG) Book — Phase 310.

The Smart Export Guarantee replaced the FIT export tariff on 2020-01-01.
Any supplier with 150,000+ domestic customers must offer at least one
SEG tariff. Unlike FIT, SEG rates are set competitively by each supplier
(not government-mandated) but must be >0p/kWh at all times.

SEG costs are paid directly by the supplier to micro-generators and are NOT
recoverable via Ofgem levelisation (unlike FIT which had a levelisation fund).
This means SEG is a direct cost on the supplier's P&L.

2022: Energy crisis saw some suppliers offering 10-15p/kWh spot-linked SEG
rates to attract cheap micro-generation when wholesale was >50p/kWh. Octopus
"Agile Outgoing" became market-leading at Agile spot price. Most traditional
suppliers remained at 3-7p/kWh fixed rates.

Connects to: fit_book.py (Ph286 -- historical export, ended 2019-03-31),
  property_improvement.py, eep_book.py (SEG scheme type),
  decarbonisation_score.py (Ph279), rego_portfolio.py.
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

# Supplier-set SEG rates (illustrative competitive rates, p/kWh)
# Based on publicly available SEG rate comparisons 2020-2024.
_SEG_RATE_P_PER_KWH_BY_YEAR: dict[int, float] = {
    2020: 4.0,   # Market launch -- Octopus/E.ON/British Gas initial offers
    2021: 4.5,   # Steady growth in SEG penetration
    2022: 7.5,   # Energy crisis: high wholesale -> high export value
    2023: 5.5,   # Normalisation post-crisis
    2024: 4.8,
    2025: 4.5,
}
_SEG_RATE_FALLBACK = 4.5


class SEGTechnology(str, Enum):
    SOLAR_PV = "solar_pv"
    WIND      = "wind"
    MICRO_CHP = "micro_chp"
    HYDRO     = "hydro"


@dataclass(frozen=True)
class SEGContract:
    customer_id: str
    mpan: str
    technology: SEGTechnology
    rate_p_per_kwh: float
    contract_start: str   # ISO date YYYY-MM-DD
    contract_end: str | None = None   # None = still active

    @property
    def is_active(self) -> bool:
        return self.contract_end is None


@dataclass(frozen=True)
class SEGPayment:
    customer_id: str
    period_start: str
    period_end: str
    export_kwh: float
    rate_p_per_kwh: float

    @property
    def payment_gbp(self) -> float:
        return round(self.export_kwh * self.rate_p_per_kwh / 100.0, 4)


class SEGBook:
    def __init__(self) -> None:
        self._contracts: list[SEGContract] = []
        self._payments: list[SEGPayment] = []

    def seg_rate_for_year(self, year: int) -> float:
        return _SEG_RATE_P_PER_KWH_BY_YEAR.get(year, _SEG_RATE_FALLBACK)

    def register_contract(self, contract: SEGContract) -> SEGContract:
        self._contracts.append(contract)
        return contract

    def terminate_contract(self, mpan: str, end_date: str) -> SEGContract | None:
        for i, c in enumerate(self._contracts):
            if c.mpan == mpan and c.is_active:
                terminated = SEGContract(
                    customer_id=c.customer_id,
                    mpan=c.mpan,
                    technology=c.technology,
                    rate_p_per_kwh=c.rate_p_per_kwh,
                    contract_start=c.contract_start,
                    contract_end=end_date,
                )
                self._contracts[i] = terminated
                return terminated
        return None

    def record_payment(self, payment: SEGPayment) -> SEGPayment:
        self._payments.append(payment)
        return payment

    def active_contracts(self) -> list[SEGContract]:
        return [c for c in self._contracts if c.is_active]

    def payments_for_customer(self, customer_id: str) -> list[SEGPayment]:
        return [p for p in self._payments if p.customer_id == customer_id]

    def payments_for_year(self, year: int) -> list[SEGPayment]:
        return [p for p in self._payments if p.period_start.startswith(str(year))]

    def total_paid_gbp(self, year: int | None = None) -> float:
        payments = self.payments_for_year(year) if year else self._payments
        return round(sum(p.payment_gbp for p in payments), 2)

    def total_export_kwh(self, year: int | None = None) -> float:
        payments = self.payments_for_year(year) if year else self._payments
        return round(sum(p.export_kwh for p in payments), 2)

    def seg_summary(self, year: int | None = None) -> dict:
        payments = self.payments_for_year(year) if year else self._payments
        return {
            "active_contracts": len(self.active_contracts()),
            "total_contracts": len(self._contracts),
            "total_payments": len(payments),
            "total_export_kwh": self.total_export_kwh(year),
            "total_paid_gbp": self.total_paid_gbp(year),
            "mean_rate_p_per_kwh": (
                round(sum(p.rate_p_per_kwh for p in payments) / len(payments), 2)
                if payments else 0.0
            ),
        }
