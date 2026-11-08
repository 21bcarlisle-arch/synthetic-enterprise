"""Supplier Financial Resilience (SFR) framework.

Ofgem introduced mandatory SFR requirements in 2023 following the 2021-22 crisis
that saw 29 suppliers fail. Key obligations under Ofgem's Retail Market Review:

- **Minimum Liquidity Requirement (MLR)**: suppliers must hold at least 30 days'
  worth of projected customer payments in unencumbered cash.
- **Ringfenced Customer Credit Balances**: credit balances held by customers
  (e.g. direct debit overpayments) must be ringfenced or insured.
- **Hedging Policy**: suppliers must maintain a documented hedging policy and
  evidence 60%+ of supply obligations hedged 6 months forward.
- **Quarterly SFR Returns**: filed to Ofgem within 30 days of quarter-end.
  Breach triggers supervisory investigation; repeated breach = licence review.

Pre-2023 context: the MLR was not a hard requirement; many failed suppliers held
negative cash positions by relying on customer credit balances as working capital.

Source: Ofgem SFR Decision Document (March 2023) + Licence Condition SLC 4C.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class SFRStatus(str, Enum):
    PASS = "PASS"             # all requirements met
    WATCH = "WATCH"           # borderline; one metric near breach
    BREACH = "BREACH"         # one or more hard thresholds breached
    INVESTIGATION = "INVESTIGATION"  # Ofgem has opened a review


class SFRMetric(str, Enum):
    LIQUIDITY = "liquidity"
    CREDIT_BALANCE_COVER = "credit_balance_cover"
    HEDGE_RATIO = "hedge_ratio"
    QUARTERLY_RETURN_FILED = "quarterly_return_filed"


# Regulatory thresholds
_MIN_LIQUIDITY_DAYS = 30            # minimum unencumbered cash (days of payments)
_MIN_HEDGE_RATIO = 0.60             # 6 months forward minimum
_WATCH_LIQUIDITY_DAYS = 40          # amber zone: 30-40 days
_WATCH_HEDGE_RATIO = 0.70           # amber zone: 60-70%


@dataclass(frozen=True)
class SFRAssessment:
    quarter_end: dt.date
    liquidity_days: float           # unencumbered cash / daily_receipts
    credit_balance_cover_pct: float  # % of customer credit balances ringfenced
    hedge_ratio_pct: float           # % of 6m forward supply obligation hedged
    return_filed: bool

    @property
    def liquidity_status(self) -> str:
        if self.liquidity_days >= _WATCH_LIQUIDITY_DAYS:
            return "GREEN"
        if self.liquidity_days >= _MIN_LIQUIDITY_DAYS:
            return "AMBER"
        return "RED"

    @property
    def hedge_status(self) -> str:
        if self.hedge_ratio_pct >= _WATCH_HEDGE_RATIO:
            return "GREEN"
        if self.hedge_ratio_pct >= _MIN_HEDGE_RATIO:
            return "AMBER"
        return "RED"

    @property
    def credit_cover_status(self) -> str:
        return "GREEN" if self.credit_balance_cover_pct >= 1.0 else "RED"

    @property
    def overall_status(self) -> SFRStatus:
        if (self.liquidity_status == "RED"
                or self.hedge_status == "RED"
                or self.credit_cover_status == "RED"
                or not self.return_filed):
            return SFRStatus.BREACH
        if self.liquidity_status == "AMBER" or self.hedge_status == "AMBER":
            return SFRStatus.WATCH
        return SFRStatus.PASS

    @property
    def breach_metrics(self) -> List[SFRMetric]:
        breaches = []
        if self.liquidity_status == "RED":
            breaches.append(SFRMetric.LIQUIDITY)
        if self.hedge_status == "RED":
            breaches.append(SFRMetric.HEDGE_RATIO)
        if self.credit_cover_status == "RED":
            breaches.append(SFRMetric.CREDIT_BALANCE_COVER)
        if not self.return_filed:
            breaches.append(SFRMetric.QUARTERLY_RETURN_FILED)
        return breaches


@dataclass
class SFRBook:
    """Track SFR assessments and return filings over time."""

    _assessments: List[SFRAssessment] = field(default_factory=list)

    def record_assessment(
        self,
        quarter_end: dt.date,
        liquidity_days: float,
        credit_balance_cover_pct: float,
        hedge_ratio_pct: float,
        return_filed: bool = False,
    ) -> SFRAssessment:
        assessment = SFRAssessment(
            quarter_end=quarter_end,
            liquidity_days=liquidity_days,
            credit_balance_cover_pct=credit_balance_cover_pct,
            hedge_ratio_pct=hedge_ratio_pct,
            return_filed=return_filed,
        )
        self._assessments.append(assessment)
        return assessment

    def file_return(self, quarter_end: dt.date) -> Optional[SFRAssessment]:
        """Mark a quarterly return as filed. Returns updated assessment or None."""
        for i, a in enumerate(self._assessments):
            if a.quarter_end == quarter_end:
                updated = SFRAssessment(
                    quarter_end=a.quarter_end,
                    liquidity_days=a.liquidity_days,
                    credit_balance_cover_pct=a.credit_balance_cover_pct,
                    hedge_ratio_pct=a.hedge_ratio_pct,
                    return_filed=True,
                )
                self._assessments[i] = updated
                return updated
        return None

    def latest_assessment(self) -> Optional[SFRAssessment]:
        if not self._assessments:
            return None
        return sorted(self._assessments, key=lambda a: a.quarter_end)[-1]

    def breach_quarters(self) -> List[SFRAssessment]:
        return [a for a in self._assessments
                if a.overall_status == SFRStatus.BREACH]

    def sfr_summary(self) -> dict:
        assessments = sorted(self._assessments, key=lambda a: a.quarter_end)
        latest = assessments[-1] if assessments else None
        return {
            "total_quarters": len(assessments),
            "breach_quarters": len(self.breach_quarters()),
            "watch_quarters": sum(
                1 for a in assessments if a.overall_status == SFRStatus.WATCH
            ),
            "latest_status": latest.overall_status.value if latest else None,
            "latest_liquidity_days": latest.liquidity_days if latest else None,
            "latest_hedge_ratio_pct": latest.hedge_ratio_pct if latest else None,
        }
