"""Portfolio Churn Risk Book — Phase AD.

Aggregates individual churn probability estimates (churn_model.py) across the
customer portfolio to produce a 12-month forward churn forecast. Segments by
dominant risk driver to guide retention targeting.

Observable inputs only — unit rates, consumption, tenure all derivable from
billing history and CRM records. Epistemic-compliant.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from company.crm.churn_model import estimate_churn_probability


# Revenue-at-risk bucket labels
class ChurnRiskBand(str, Enum):
    CRITICAL = "critical"   # churn_prob >= 0.50
    HIGH = "high"           # churn_prob >= 0.30
    MEDIUM = "medium"       # churn_prob >= 0.15
    LOW = "low"             # churn_prob < 0.15


class ChurnRiskDriver(str, Enum):
    RATE_SHOCK = "rate_shock"          # new rate >> old rate
    BILL_STRESS = "bill_stress"        # high annual bill vs income
    TENURE_SHORT = "tenure_short"      # < 2 years, no loyalty discount
    BASELINE = "baseline"              # no single dominant driver


def _classify_band(p: float) -> ChurnRiskBand:
    if p >= 0.50:
        return ChurnRiskBand.CRITICAL
    if p >= 0.30:
        return ChurnRiskBand.HIGH
    if p >= 0.15:
        return ChurnRiskBand.MEDIUM
    return ChurnRiskBand.LOW


def _classify_driver(
    rate_increase_pct: float,
    annual_bill_gbp: float,
    tenure_years: float,
) -> ChurnRiskDriver:
    """Identify the single dominant churn driver for a customer."""
    if rate_increase_pct >= 0.20:
        return ChurnRiskDriver.RATE_SHOCK
    if annual_bill_gbp >= 3000.0:
        return ChurnRiskDriver.BILL_STRESS
    if tenure_years < 2.0:
        return ChurnRiskDriver.TENURE_SHORT
    return ChurnRiskDriver.BASELINE


@dataclass(frozen=True)
class CustomerChurnRisk:
    """Churn risk assessment for a single customer.

    annual_revenue_gbp: used to compute revenue_at_risk (what we lose if they churn).
    expected_loss_gbp: churn_probability × annual_revenue_gbp
    """
    account_id: str
    churn_probability: float
    risk_band: ChurnRiskBand
    dominant_driver: ChurnRiskDriver
    annual_revenue_gbp: float
    tenure_years: float
    segment: str

    @property
    def expected_loss_gbp(self) -> float:
        return round(self.churn_probability * self.annual_revenue_gbp, 2)

    @property
    def is_at_risk(self) -> bool:
        return self.risk_band in (ChurnRiskBand.CRITICAL, ChurnRiskBand.HIGH)


class PortfolioChurnRiskBook:
    """Builds and queries the portfolio churn risk register.

    Usage::
        book = PortfolioChurnRiskBook()
        risk = book.assess(
            account_id="C1",
            old_rate_gbp_per_mwh=180.0,
            new_rate_gbp_per_mwh=250.0,
            tenure_years=1.5,
            annual_consumption_kwh=3500.0,
            annual_revenue_gbp=875.0,
            segment="resi",
        )
    """

    def __init__(self) -> None:
        self._risks: list[CustomerChurnRisk] = []

    def assess(
        self,
        account_id: str,
        old_rate_gbp_per_mwh: float,
        new_rate_gbp_per_mwh: float,
        tenure_years: float,
        annual_consumption_kwh: float,
        annual_revenue_gbp: float,
        segment: str = "resi",
        fuel: str = "electricity",
        hedge_fraction: float = 0.0,
    ) -> CustomerChurnRisk:
        p = estimate_churn_probability(
            old_rate_gbp_per_mwh=old_rate_gbp_per_mwh,
            new_rate_gbp_per_mwh=new_rate_gbp_per_mwh,
            tenure_years=tenure_years,
            annual_consumption_kwh=annual_consumption_kwh,
            fuel=fuel,
            segment=segment,
            hedge_fraction=hedge_fraction,
        )
        rate_increase_pct = (
            (new_rate_gbp_per_mwh - old_rate_gbp_per_mwh) / old_rate_gbp_per_mwh
            if old_rate_gbp_per_mwh > 0 else 0.0
        )
        annual_bill_gbp = old_rate_gbp_per_mwh * annual_consumption_kwh / 1000.0
        risk = CustomerChurnRisk(
            account_id=account_id,
            churn_probability=p,
            risk_band=_classify_band(p),
            dominant_driver=_classify_driver(rate_increase_pct, annual_bill_gbp, tenure_years),
            annual_revenue_gbp=annual_revenue_gbp,
            tenure_years=tenure_years,
            segment=segment,
        )
        self._risks.append(risk)
        return risk

    @property
    def all_risks(self) -> list[CustomerChurnRisk]:
        return list(self._risks)

    def at_risk_customers(self) -> list[CustomerChurnRisk]:
        return [r for r in self._risks if r.is_at_risk]

    def by_band(self, band: ChurnRiskBand) -> list[CustomerChurnRisk]:
        return [r for r in self._risks if r.risk_band == band]

    def by_driver(self, driver: ChurnRiskDriver) -> list[CustomerChurnRisk]:
        return [r for r in self._risks if r.dominant_driver == driver]

    @property
    def total_revenue_at_risk_gbp(self) -> float:
        return round(sum(r.annual_revenue_gbp for r in self.at_risk_customers()), 2)

    @property
    def total_expected_loss_gbp(self) -> float:
        return round(sum(r.expected_loss_gbp for r in self._risks), 2)

    @property
    def portfolio_churn_rate_pct(self) -> float:
        if not self._risks:
            return 0.0
        return round(sum(r.churn_probability for r in self._risks) / len(self._risks) * 100.0, 2)

    def top_n_by_expected_loss(self, n: int = 5) -> list[CustomerChurnRisk]:
        return sorted(self._risks, key=lambda r: r.expected_loss_gbp, reverse=True)[:n]

    def driver_breakdown(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for r in self._risks:
            counts[r.dominant_driver.value] = counts.get(r.dominant_driver.value, 0) + 1
        return counts

    def churn_risk_summary(self) -> dict:
        return {
            "customers_assessed": len(self._risks),
            "at_risk_count": len(self.at_risk_customers()),
            "critical_count": len(self.by_band(ChurnRiskBand.CRITICAL)),
            "high_count": len(self.by_band(ChurnRiskBand.HIGH)),
            "portfolio_churn_rate_pct": self.portfolio_churn_rate_pct,
            "total_revenue_at_risk_gbp": self.total_revenue_at_risk_gbp,
            "total_expected_loss_gbp": self.total_expected_loss_gbp,
            "driver_breakdown": self.driver_breakdown(),
        }
