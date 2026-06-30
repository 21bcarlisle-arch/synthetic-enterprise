"""Mandatory Social Obligation Spend Register (Phase DI).

UK energy suppliers are required to spend on social obligations including:

1. Warm Home Discount (WHD) — mandatory levy per customer (~£150/customer/year)
   Funded by all electricity suppliers with 250k+ customers.
   Smaller suppliers pay proportionally via the WHD levy mechanism.

2. Priority Services Register — no direct spend, but service costs (extra contacts,
   welfare checks, adapted communications) are tracked here.

3. Energy Efficiency Obligations (ECO) — larger suppliers (>250k customers) must fund
   energy efficiency upgrades for fuel-poor households. Smaller suppliers can buy
   obligation from larger ones.

4. Carbon Offsetting (voluntary, but tracked for ESG reporting).

Key regulatory refs:
- Warm Home Discount Scheme (WHDS) Regulations 2011 (as amended)
- Energy Company Obligation (ECO4) 2022-2026
- Ofgem requires annual reporting on social spending

Epistemic: company can observe its own spend. Cannot see competitor spend or
aggregate levy calculations (that's Ofgem's remit).
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class SocialObligationType(str, Enum):
    WARM_HOME_DISCOUNT = "warm_home_discount"         # WHD levy
    PRIORITY_SERVICES = "priority_services"           # PSR service costs
    ENERGY_EFFICIENCY = "energy_efficiency"           # ECO obligation
    FUEL_POVERTY_SUPPORT = "fuel_poverty_support"    # voluntary / debt write-off
    CARBON_OFFSET = "carbon_offset"                   # voluntary


class ObligationStatus(str, Enum):
    PROJECTED = "projected"
    COMMITTED = "committed"
    PAID = "paid"
    UNDERPERFORMING = "underperforming"               # behind target
    COMPLIANT = "compliant"


_WHD_LEVY_PER_CUSTOMER_GBP = 18.0    # Ofgem WHD levy per electricity customer (~£150 benefit / 8 suppliers)
_WHD_BENEFIT_GBP = 150.0              # WHD benefit to recipient


@dataclass(frozen=True)
class SocialObligationRecord:
    obligation_id: str
    year: int
    obligation_type: SocialObligationType
    target_gbp: float
    actual_spend_gbp: float
    status: ObligationStatus
    beneficiaries_count: int = 0
    description: Optional[str] = None

    @property
    def variance_gbp(self) -> float:
        return self.actual_spend_gbp - self.target_gbp

    @property
    def is_underspend(self) -> bool:
        return self.actual_spend_gbp < self.target_gbp

    @property
    def spend_rate(self) -> float:
        if self.target_gbp == 0:
            return 1.0
        return self.actual_spend_gbp / self.target_gbp

    @property
    def cost_per_beneficiary_gbp(self) -> Optional[float]:
        if self.beneficiaries_count == 0:
            return None
        return self.actual_spend_gbp / self.beneficiaries_count

    @property
    def is_compliant(self) -> bool:
        return self.status in (ObligationStatus.PAID, ObligationStatus.COMPLIANT)


class SocialObligationSpendRegister:
    """Tracks mandatory and voluntary social obligation spending."""

    def __init__(self) -> None:
        self._records: List[SocialObligationRecord] = []
        self._seq = 0

    def _next_id(self) -> str:
        self._seq += 1
        return f"SOB-{self._seq:04d}"

    @staticmethod
    def estimate_whd_levy(customer_count: int) -> float:
        return customer_count * _WHD_LEVY_PER_CUSTOMER_GBP

    def record_obligation(
        self,
        year: int,
        obligation_type: SocialObligationType,
        target_gbp: float,
        actual_spend_gbp: float,
        status: ObligationStatus = ObligationStatus.COMMITTED,
        beneficiaries_count: int = 0,
        description: Optional[str] = None,
    ) -> SocialObligationRecord:
        rec = SocialObligationRecord(
            obligation_id=self._next_id(),
            year=year,
            obligation_type=obligation_type,
            target_gbp=target_gbp,
            actual_spend_gbp=actual_spend_gbp,
            status=status,
            beneficiaries_count=beneficiaries_count,
            description=description,
        )
        self._records.append(rec)
        return rec

    def for_year(self, year: int) -> List[SocialObligationRecord]:
        return [r for r in self._records if r.year == year]

    def by_type(self, obligation_type: SocialObligationType) -> List[SocialObligationRecord]:
        return [r for r in self._records if r.obligation_type == obligation_type]

    def non_compliant(self) -> List[SocialObligationRecord]:
        return [r for r in self._records if not r.is_compliant
                and r.status != ObligationStatus.PROJECTED]

    def underspend_records(self) -> List[SocialObligationRecord]:
        return [r for r in self._records if r.is_underspend]

    def total_spend_gbp(self, year: Optional[int] = None) -> float:
        records = self.for_year(year) if year else self._records
        return sum(r.actual_spend_gbp for r in records)

    def total_target_gbp(self, year: Optional[int] = None) -> float:
        records = self.for_year(year) if year else self._records
        return sum(r.target_gbp for r in records)

    def total_beneficiaries(self, year: Optional[int] = None) -> int:
        records = self.for_year(year) if year else self._records
        return sum(r.beneficiaries_count for r in records)

    def annual_summary(self, year: int) -> Dict:
        records = self.for_year(year)
        by_type: Dict[str, float] = {}
        for r in records:
            by_type[r.obligation_type.value] = by_type.get(r.obligation_type.value, 0) + r.actual_spend_gbp
        return {
            "year": year,
            "total_spend_gbp": self.total_spend_gbp(year),
            "total_target_gbp": self.total_target_gbp(year),
            "total_beneficiaries": self.total_beneficiaries(year),
            "by_type": by_type,
            "compliant_count": sum(1 for r in records if r.is_compliant),
            "non_compliant_count": sum(1 for r in records if not r.is_compliant),
        }

    def whd_levy_constant(self) -> float:
        return _WHD_LEVY_PER_CUSTOMER_GBP

    def whd_benefit_constant(self) -> float:
        return _WHD_BENEFIT_GBP

    def social_obligation_summary(self) -> str:
        years = sorted({r.year for r in self._records})
        total = self.total_spend_gbp()
        target = self.total_target_gbp()
        non_comp = len(self.non_compliant())
        bens = self.total_beneficiaries()
        return (
            f"Social Obligation Register (WHD/PSR/ECO): {len(self._records)} records, "
            f"years {years}. Total spend: £{total:,.0f} vs target £{target:,.0f}. "
            f"Beneficiaries: {bens:,}. Non-compliant: {non_comp}."
        )
