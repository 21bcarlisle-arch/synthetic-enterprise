from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CompanyPL:
    year: int
    revenue_gbp: float
    wholesale_cost_gbp: float
    policy_cost_gbp: float
    network_cost_gbp: float
    operating_cost_gbp: float
    marketing_cost_gbp: float
    bad_debt_gbp: float
    whd_rebates_gbp: float
    gsop_payments_gbp: float

    @property
    def gross_margin_gbp(self) -> float:
        return round(
            self.revenue_gbp - self.wholesale_cost_gbp - self.policy_cost_gbp - self.network_cost_gbp,
            2
        )

    @property
    def total_operating_cost_gbp(self) -> float:
        return round(
            self.operating_cost_gbp + self.marketing_cost_gbp + self.bad_debt_gbp
            + self.whd_rebates_gbp + self.gsop_payments_gbp,
            2
        )

    @property
    def ebitda_gbp(self) -> float:
        return round(self.gross_margin_gbp - self.total_operating_cost_gbp, 2)

    @property
    def gross_margin_pct(self) -> float:
        if self.revenue_gbp <= 0:
            return 0.0
        return round(self.gross_margin_gbp / self.revenue_gbp * 100, 2)

    @property
    def ebitda_margin_pct(self) -> float:
        if self.revenue_gbp <= 0:
            return 0.0
        return round(self.ebitda_gbp / self.revenue_gbp * 100, 2)

    @property
    def bad_debt_as_pct_revenue(self) -> float:
        if self.revenue_gbp <= 0:
            return 0.0
        return round(self.bad_debt_gbp / self.revenue_gbp * 100, 2)

    @property
    def is_profitable(self) -> bool:
        return self.ebitda_gbp > 0

    def summary(self) -> dict:
        return {
            'year': self.year,
            'revenue_gbp': round(self.revenue_gbp, 2),
            'gross_margin_gbp': self.gross_margin_gbp,
            'gross_margin_pct': self.gross_margin_pct,
            'total_operating_cost_gbp': self.total_operating_cost_gbp,
            'ebitda_gbp': self.ebitda_gbp,
            'ebitda_margin_pct': self.ebitda_margin_pct,
            'bad_debt_as_pct_revenue': self.bad_debt_as_pct_revenue,
            'is_profitable': self.is_profitable,
        }


def build_company_pl(
    year: int,
    revenue_gbp: float,
    wholesale_cost_gbp: float,
    policy_cost_gbp: float,
    network_cost_gbp: float,
    operating_cost_gbp: float,
    marketing_cost_gbp: float = 0.0,
    bad_debt_gbp: float = 0.0,
    whd_rebates_gbp: float = 0.0,
    gsop_payments_gbp: float = 0.0,
) -> CompanyPL:
    return CompanyPL(
        year=year,
        revenue_gbp=revenue_gbp,
        wholesale_cost_gbp=wholesale_cost_gbp,
        policy_cost_gbp=policy_cost_gbp,
        network_cost_gbp=network_cost_gbp,
        operating_cost_gbp=operating_cost_gbp,
        marketing_cost_gbp=marketing_cost_gbp,
        bad_debt_gbp=bad_debt_gbp,
        whd_rebates_gbp=whd_rebates_gbp,
        gsop_payments_gbp=gsop_payments_gbp,
    )
