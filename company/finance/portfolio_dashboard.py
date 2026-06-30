"""Customer Portfolio Profitability Dashboard (Phase EG).

A management reporting view connecting the key portfolio metrics into a single
board-ready snapshot. Answers the MD's question: "How is the portfolio performing
right now?"

Aggregates:
- Total active customer count by segment
- Total annual margin (£) and per-customer average
- Portfolio churn rate and expected revenue at risk
- Average CLV (H3 forecast) vs H1 commitment
- Net Promoter Score proxy (from complaint resolution rate)
- Concentration risk (% revenue from top 20% of customers)

This is the integration layer that connects Phase EA (resentment), EB (GRI),
EC (3-horizon CLV), ED (activation energy) into a coherent management pack.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class PortfolioHealthStatus(str, Enum):
    STRONG = "strong"
    HEALTHY = "healthy"
    UNDER_PRESSURE = "under_pressure"
    CRITICAL = "critical"


@dataclass(frozen=True)
class SegmentSummary:
    segment: str
    customer_count: int
    total_annual_margin_gbp: float
    avg_annual_margin_gbp: float
    churn_rate_pct: float

    @property
    def revenue_at_risk_gbp(self) -> float:
        return self.total_annual_margin_gbp * self.churn_rate_pct / 100

    @property
    def avg_clv_gbp(self) -> float:
        retention = 1 - self.churn_rate_pct / 100
        denom = 1 + 0.08 - retention
        return self.avg_annual_margin_gbp * retention / denom if denom > 0 else 0.0


@dataclass(frozen=True)
class PortfolioProfitabilitySnapshot:
    snapshot_date: dt.date
    supplier_name: str
    segments: tuple                   # tuple of SegmentSummary
    gri_score: float
    complaint_resolution_pct: float   # proxy for NPS
    smart_meter_pct: float
    hedge_fraction_pct: float

    @property
    def total_customers(self) -> int:
        return sum(s.customer_count for s in self.segments)

    @property
    def total_annual_margin_gbp(self) -> float:
        return sum(s.total_annual_margin_gbp for s in self.segments)

    @property
    def avg_annual_margin_gbp(self) -> float:
        if self.total_customers == 0:
            return 0.0
        return self.total_annual_margin_gbp / self.total_customers

    @property
    def portfolio_churn_rate_pct(self) -> float:
        if self.total_customers == 0:
            return 0.0
        weighted = sum(s.customer_count * s.churn_rate_pct for s in self.segments)
        return weighted / self.total_customers

    @property
    def total_revenue_at_risk_gbp(self) -> float:
        return sum(s.revenue_at_risk_gbp for s in self.segments)

    @property
    def concentration_risk_pct(self) -> float:
        if not self.segments:
            return 0.0
        margins = sorted([s.total_annual_margin_gbp for s in self.segments], reverse=True)
        top_count = max(1, len(margins) // 5)
        top_margin = sum(margins[:top_count])
        total = sum(margins)
        return (top_margin / total * 100) if total > 0 else 0.0

    @property
    def health_status(self) -> PortfolioHealthStatus:
        churn = self.portfolio_churn_rate_pct
        gri = self.gri_score
        if churn < 10 and gri >= 60:
            return PortfolioHealthStatus.STRONG
        if churn < 20 and gri >= 45:
            return PortfolioHealthStatus.HEALTHY
        if churn < 30 and gri >= 30:
            return PortfolioHealthStatus.UNDER_PRESSURE
        return PortfolioHealthStatus.CRITICAL

    def segment(self, name: str) -> Optional[SegmentSummary]:
        for s in self.segments:
            if s.segment == name:
                return s
        return None

    def dashboard_summary(self) -> str:
        status = self.health_status.value
        churn = self.portfolio_churn_rate_pct
        margin = self.total_annual_margin_gbp
        return (
            f"Portfolio Dashboard ({self.snapshot_date}): {self.total_customers} customers. "
            f"Total margin: £{margin:,.0f}. Churn: {churn:.1f}%. "
            f"GRI: {self.gri_score:.0f}. Status: {status.upper()}."
        )
