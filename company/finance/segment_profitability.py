"""Customer Segment Profitability Analysis (Phase ES).

The company tracks P&L by customer segment to identify where to allocate:
- Sales and marketing budget
- Retention effort and offers
- Product development

Segments:
- DOMESTIC: residential customers, price cap applies, high volume
- SME: small/medium business, simpler contracts, mid-margin
- IC_MHH: industrial & commercial half-hourly metered, high margin, high risk

Each segment has different:
- CAC (customer acquisition cost)
- Churn rate
- Regulatory cost-to-serve
- Margin profile
- CLV distribution

This module computes segment P&L from observable inputs and provides
strategic recommendations (grow/maintain/harvest/exit).
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class CustomerSegment(str, Enum):
    DOMESTIC = "domestic"
    SME = "sme"
    IC_MHH = "ic_mhh"


class SegmentStrategy(str, Enum):
    GROW = "grow"           # positive CLV, below penetration, target for growth
    MAINTAIN = "maintain"   # profitable, at target penetration
    HARVEST = "harvest"     # positive but declining; extract value, limit spend
    EXIT = "exit"           # negative contribution margin; managed exit


_CLV_POSITIVE_THRESHOLD_GBP = 50.0   # below this -> harvest/exit
_CHURN_HIGH_THRESHOLD_PCT = 30.0     # above this -> harvest even if CLV positive
_MARGIN_LOW_THRESHOLD_PCT = 3.0      # margin pct below this -> harvest


@dataclass(frozen=True)
class SegmentProfitabilitySnapshot:
    segment: CustomerSegment
    as_of: dt.date
    customer_count: int
    total_annual_revenue_gbp: float
    total_annual_cost_gbp: float      # cost to serve (billing, ops, regulatory)
    total_cac_spend_gbp: float        # acquisition cost in period
    avg_churn_rate_pct: float
    avg_clv_gbp: float                # Gordon Growth model output

    @property
    def total_annual_margin_gbp(self) -> float:
        return self.total_annual_revenue_gbp - self.total_annual_cost_gbp

    @property
    def margin_pct(self) -> float:
        if self.total_annual_revenue_gbp == 0:
            return 0.0
        return 100.0 * self.total_annual_margin_gbp / self.total_annual_revenue_gbp

    @property
    def revenue_per_customer_gbp(self) -> float:
        if self.customer_count == 0:
            return 0.0
        return self.total_annual_revenue_gbp / self.customer_count

    @property
    def margin_per_customer_gbp(self) -> float:
        if self.customer_count == 0:
            return 0.0
        return self.total_annual_margin_gbp / self.customer_count

    @property
    def strategy(self) -> SegmentStrategy:
        if self.total_annual_margin_gbp < 0:
            return SegmentStrategy.EXIT
        if self.avg_clv_gbp < _CLV_POSITIVE_THRESHOLD_GBP:
            return SegmentStrategy.EXIT
        if self.avg_churn_rate_pct >= _CHURN_HIGH_THRESHOLD_PCT:
            return SegmentStrategy.HARVEST
        if self.margin_pct < _MARGIN_LOW_THRESHOLD_PCT:
            return SegmentStrategy.HARVEST
        if self.avg_clv_gbp > 500.0 and self.margin_pct > 10.0:
            return SegmentStrategy.GROW
        return SegmentStrategy.MAINTAIN

    def segment_summary(self) -> str:
        return (
            self.segment.value + " (" + str(self.as_of) + "): "
            "n=" + str(self.customer_count) + " "
            "margin=GBP" + str(round(self.total_annual_margin_gbp)) + " "
            "(" + str(round(self.margin_pct, 1)) + "%) "
            "clv=GBP" + str(round(self.avg_clv_gbp)) + " "
            "churn=" + str(round(self.avg_churn_rate_pct, 1)) + "% "
            "strategy=" + self.strategy.value
        )


class SegmentProfitabilityBook:

    def __init__(self) -> None:
        self._snapshots: List[SegmentProfitabilitySnapshot] = []

    def record(self, snapshot: SegmentProfitabilitySnapshot) -> SegmentProfitabilitySnapshot:
        self._snapshots.append(snapshot)
        return snapshot

    def latest_for(self, segment: CustomerSegment) -> Optional[SegmentProfitabilitySnapshot]:
        matching = [s for s in self._snapshots if s.segment == segment]
        if not matching:
            return None
        return max(matching, key=lambda s: s.as_of)

    def all_latest(self, as_of: dt.date) -> List[SegmentProfitabilitySnapshot]:
        result = []
        for seg in CustomerSegment:
            snap = self.latest_for(seg)
            if snap and snap.as_of == as_of:
                result.append(snap)
        return result

    def grow_segments(self) -> List[SegmentProfitabilitySnapshot]:
        return [s for s in self._snapshots if s.strategy == SegmentStrategy.GROW]

    def exit_segments(self) -> List[SegmentProfitabilitySnapshot]:
        return [s for s in self._snapshots if s.strategy == SegmentStrategy.EXIT]

    def total_portfolio_margin_gbp(self) -> float:
        latest = [self.latest_for(s) for s in CustomerSegment]
        return sum(s.total_annual_margin_gbp for s in latest if s is not None)

    def portfolio_segment_summary(self, as_of: dt.date) -> str:
        total_margin = self.total_portfolio_margin_gbp()
        total_customers = sum(
            (s.customer_count for s in [self.latest_for(seg) for seg in CustomerSegment]
             if s is not None), 0
        )
        n_grow = len(self.grow_segments())
        n_exit = len(self.exit_segments())
        return (
            "Segment Profitability (" + str(as_of) + "): "
            + str(total_customers) + " customers. "
            "Portfolio margin: GBP" + str(round(total_margin)) + ". "
            "Grow: " + str(n_grow) + " Exit: " + str(n_exit) + "."
        )
