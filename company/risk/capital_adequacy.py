"""Regulatory Capital Adequacy Assessment (Phase EV).

Ofgem's Financial Resilience Assessment (FRA) framework post-2022 crisis requires
suppliers to demonstrate capital adequacy. This is different from the FRA book
(Phase 318 which was about liquidity ratios) — this module focuses on:

1. Regulatory capital ratio (equity / risk-weighted assets)
2. Stress-test capital depletion (worst-case scenario)
3. Wind-down reserve (can we return customer credit balances?)
4. Margin call buffer (do we have headroom for collateral demands?)

Key thresholds (Ofgem FRA 2023 consultation):
- Wind-down reserve: min 1.5% of annual revenue
- Margin call buffer: min 10% of gross notional exposure
- Stress-test: survive 1-in-20 year VaR event without insolvency
- Regulatory equity ratio: min 10% of risk-weighted assets

Post-2022: 28 failures were partly attributable to insufficient capital buffers.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class CapitalAdequacyStatus(str, Enum):
    ADEQUATE = "adequate"
    MARGINAL = "marginal"        # borderline, requires monitoring
    INADEQUATE = "inadequate"    # below minimum, regulatory concern
    CRITICAL = "critical"        # immediate action required


_WIND_DOWN_RESERVE_MIN_PCT = 1.5        # of annual revenue
_MARGIN_CALL_BUFFER_MIN_PCT = 10.0     # of gross notional exposure
_EQUITY_RATIO_MIN_PCT = 10.0           # of risk-weighted assets


@dataclass(frozen=True)
class CapitalAdequacyAssessment:
    as_of: dt.date
    annual_revenue_gbp: float
    wind_down_reserve_gbp: float
    gross_notional_exposure_gbp: float
    margin_call_buffer_gbp: float
    total_equity_gbp: float
    risk_weighted_assets_gbp: float
    stress_var_gbp: float               # 1-in-20 year VaR

    @property
    def wind_down_reserve_pct(self) -> float:
        if self.annual_revenue_gbp <= 0:
            return 0.0
        return 100.0 * self.wind_down_reserve_gbp / self.annual_revenue_gbp

    @property
    def margin_call_buffer_pct(self) -> float:
        if self.gross_notional_exposure_gbp <= 0:
            return 100.0  # no exposure = no requirement
        return 100.0 * self.margin_call_buffer_gbp / self.gross_notional_exposure_gbp

    @property
    def equity_ratio_pct(self) -> float:
        if self.risk_weighted_assets_gbp <= 0:
            return 100.0
        return 100.0 * self.total_equity_gbp / self.risk_weighted_assets_gbp

    @property
    def stress_test_passes(self) -> bool:
        return self.total_equity_gbp > self.stress_var_gbp

    @property
    def wind_down_compliant(self) -> bool:
        return self.wind_down_reserve_pct >= _WIND_DOWN_RESERVE_MIN_PCT

    @property
    def margin_buffer_compliant(self) -> bool:
        return self.margin_call_buffer_pct >= _MARGIN_CALL_BUFFER_MIN_PCT

    @property
    def equity_ratio_compliant(self) -> bool:
        return self.equity_ratio_pct >= _EQUITY_RATIO_MIN_PCT

    @property
    def status(self) -> CapitalAdequacyStatus:
        n_fail = sum([
            not self.wind_down_compliant,
            not self.margin_buffer_compliant,
            not self.equity_ratio_compliant,
            not self.stress_test_passes,
        ])
        if n_fail == 0:
            return CapitalAdequacyStatus.ADEQUATE
        if n_fail == 1:
            return CapitalAdequacyStatus.MARGINAL
        if n_fail == 2:
            return CapitalAdequacyStatus.INADEQUATE
        return CapitalAdequacyStatus.CRITICAL

    def assessment_summary(self) -> str:
        return (
            "Capital Adequacy (" + str(self.as_of) + "): "
            "status=" + self.status.value + " "
            "wind_down=" + str(round(self.wind_down_reserve_pct, 1)) + "% "
            "margin_buf=" + str(round(self.margin_call_buffer_pct, 1)) + "% "
            "equity_ratio=" + str(round(self.equity_ratio_pct, 1)) + "% "
            "stress_ok=" + str(self.stress_test_passes)
        )


class CapitalAdequacyBook:

    def __init__(self) -> None:
        self._assessments: List[CapitalAdequacyAssessment] = []

    def record(self, assessment: CapitalAdequacyAssessment) -> CapitalAdequacyAssessment:
        self._assessments.append(assessment)
        return assessment

    def latest(self) -> Optional[CapitalAdequacyAssessment]:
        if not self._assessments:
            return None
        return max(self._assessments, key=lambda a: a.as_of)

    def inadequate_assessments(self) -> List[CapitalAdequacyAssessment]:
        return [a for a in self._assessments
                if a.status in (CapitalAdequacyStatus.INADEQUATE, CapitalAdequacyStatus.CRITICAL)]

    def trend_is_deteriorating(self) -> bool:
        if len(self._assessments) < 2:
            return False
        sorted_a = sorted(self._assessments, key=lambda a: a.as_of)
        return sorted_a[-1].equity_ratio_pct < sorted_a[-2].equity_ratio_pct

    def capital_adequacy_summary(self, as_of: dt.date) -> str:
        latest = self.latest()
        if latest is None:
            return "No capital assessments recorded."
        n_inadequate = len(self.inadequate_assessments())
        return (
            "Capital Adequacy (" + str(as_of) + "): "
            "latest_status=" + latest.status.value + ". "
            "Inadequate periods: " + str(n_inadequate) + ". "
            "Deteriorating: " + str(self.trend_is_deteriorating()) + "."
        )
