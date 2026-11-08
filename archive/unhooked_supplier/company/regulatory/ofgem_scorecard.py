"""Ofgem Supplier Performance Scorecard (Phase EF).

Ofgem publishes quarterly supplier performance scorecards comparing suppliers
on key metrics. These are used to:
- Monitor SLC compliance
- Trigger enhanced oversight for underperformers
- Inform consumer switching decisions
- Identify systemic sector issues

Key metrics assessed quarterly:
1. Complaint volume per 100k customers (industry benchmark: <400)
2. Complaint resolution within 8 weeks (Ofgem target: >85%)
3. Gas/electricity network complaint response time
4. Switching satisfaction score
5. Billing accuracy rate
6. Debt level as % of revenue
7. Customer service wait times

Suppliers scoring RED on 3+ metrics trigger Ofgem enhanced monitoring.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class MetricRAG(str, Enum):
    GREEN = "green"
    AMBER = "amber"
    RED = "red"


class ScoreMetric(str, Enum):
    COMPLAINTS_PER_100K = "complaints_per_100k"
    COMPLAINT_RESOLUTION_8W_PCT = "complaint_resolution_8w_pct"
    BILLING_ACCURACY_PCT = "billing_accuracy_pct"
    SWITCHING_SATISFACTION_PCT = "switching_satisfaction_pct"
    DEBT_AS_PCT_REVENUE = "debt_as_pct_revenue"
    CALL_WAIT_SECONDS = "call_wait_seconds"
    SMART_METER_INSTALLATION_PCT = "smart_meter_installation_pct"


_METRIC_GREEN_AMBER_RED = {
    ScoreMetric.COMPLAINTS_PER_100K: (400.0, 700.0),         # < 400 green; 400-700 amber; > 700 red
    ScoreMetric.COMPLAINT_RESOLUTION_8W_PCT: (85.0, 70.0),   # > 85 green; 70-85 amber; < 70 red (inverted)
    ScoreMetric.BILLING_ACCURACY_PCT: (97.0, 94.0),           # > 97 green; 94-97 amber
    ScoreMetric.SWITCHING_SATISFACTION_PCT: (80.0, 65.0),     # > 80 green
    ScoreMetric.DEBT_AS_PCT_REVENUE: (3.0, 6.0),              # < 3% green; 3-6 amber; > 6 red
    ScoreMetric.CALL_WAIT_SECONDS: (120.0, 300.0),            # < 120s green; 120-300 amber
    ScoreMetric.SMART_METER_INSTALLATION_PCT: (80.0, 60.0),   # > 80% green
}

_RED_TRIGGER_COUNT = 3


def _classify_metric(metric: ScoreMetric, value: float) -> MetricRAG:
    thresholds = _METRIC_GREEN_AMBER_RED[metric]
    g, a = thresholds
    inverted = metric in (ScoreMetric.COMPLAINTS_PER_100K, ScoreMetric.DEBT_AS_PCT_REVENUE, ScoreMetric.CALL_WAIT_SECONDS)
    if inverted:
        if value <= g:
            return MetricRAG.GREEN
        if value <= a:
            return MetricRAG.AMBER
        return MetricRAG.RED
    else:
        if value >= g:
            return MetricRAG.GREEN
        if value >= a:
            return MetricRAG.AMBER
        return MetricRAG.RED


@dataclass(frozen=True)
class MetricResult:
    metric: ScoreMetric
    value: float
    rag: MetricRAG
    industry_benchmark: float


@dataclass(frozen=True)
class SupplierPerformanceScorecard:
    supplier_name: str
    quarter: str                    # e.g. "Q1 2024"
    assessed_at: dt.date
    customer_count: int
    results: tuple                  # tuple of MetricResult (frozen-compatible)

    @property
    def red_count(self) -> int:
        return sum(1 for r in self.results if r.rag == MetricRAG.RED)

    @property
    def amber_count(self) -> int:
        return sum(1 for r in self.results if r.rag == MetricRAG.AMBER)

    @property
    def is_enhanced_monitoring_triggered(self) -> bool:
        return self.red_count >= _RED_TRIGGER_COUNT

    @property
    def overall_rag(self) -> MetricRAG:
        if self.red_count >= 2:
            return MetricRAG.RED
        if self.red_count >= 1 or self.amber_count >= 3:
            return MetricRAG.AMBER
        return MetricRAG.GREEN

    def get_metric(self, metric: ScoreMetric) -> Optional[MetricResult]:
        for r in self.results:
            if r.metric == metric:
                return r
        return None


class OfgemScorecardBuilder:
    """Builds quarterly supplier performance scorecards."""

    def __init__(self, supplier_name: str, customer_count: int) -> None:
        self.supplier_name = supplier_name
        self.customer_count = customer_count
        self._inputs: Dict[ScoreMetric, float] = {}

    def record(self, metric: ScoreMetric, value: float) -> None:
        self._inputs[metric] = value

    def build(self, quarter: str, assessed_at: dt.date) -> SupplierPerformanceScorecard:
        benchmarks = {
            ScoreMetric.COMPLAINTS_PER_100K: 400.0,
            ScoreMetric.COMPLAINT_RESOLUTION_8W_PCT: 85.0,
            ScoreMetric.BILLING_ACCURACY_PCT: 97.0,
            ScoreMetric.SWITCHING_SATISFACTION_PCT: 80.0,
            ScoreMetric.DEBT_AS_PCT_REVENUE: 3.0,
            ScoreMetric.CALL_WAIT_SECONDS: 120.0,
            ScoreMetric.SMART_METER_INSTALLATION_PCT: 80.0,
        }
        results = tuple(
            MetricResult(
                metric=m,
                value=v,
                rag=_classify_metric(m, v),
                industry_benchmark=benchmarks.get(m, 0.0),
            )
            for m, v in self._inputs.items()
        )
        return SupplierPerformanceScorecard(
            supplier_name=self.supplier_name,
            quarter=quarter,
            assessed_at=assessed_at,
            customer_count=self.customer_count,
            results=results,
        )
