"""ToU Product Launch Decision Engine -- Phase X.

Combines Phase T (profitability), Phase U (cross-subsidy register), and
Phase V (migration scenarios) into a board-level decision: should the
company launch a ToU tariff, and if so when?

All inputs are company-observable. Epistemic-compliant.

Key finding from T/U/V: for an EV-heavy portfolio on flat-rate tariffs,
ToU launch is often HOLD -- EV customers are the most profitable under
flat rate (overnight wholesale cheap; billed at flat rate). Launching ToU
lets them arbitrage away the cross-subsidy.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from company.pricing.ev_cross_subsidy import CrossSubsidyRegister
from company.pricing.tou_migration_scenario import ToUMigrationScenarioBook


class LaunchReadinessSignal(Enum):
    """Board-level ToU launch recommendation."""
    LAUNCH = "launch"
    HOLD = "hold"
    MONITOR = "monitor"


@dataclass(frozen=True)
class ToULaunchThreshold:
    """Configurable thresholds that govern when ToU launch is recommended.

    year: calendar year this threshold applies to
    min_ev_penetration_pct: EV share of portfolio must exceed this before
        ToU is a viable mass-market product (too few EVs = no addressable market)
    max_margin_loss_gbp: maximum acceptable worst-case margin loss if all
        cross-subsidy customers migrate to ToU
    """
    year: int
    min_ev_penetration_pct: float
    max_margin_loss_gbp: float

    @classmethod
    def default_for(cls, year: int) -> "ToULaunchThreshold":
        """Industry-calibrated thresholds.

        EV penetration in UK:
          2020: ~1% of cars electric -> ~0.5% of resi customers
          2024: ~4% of cars -> ~2% of resi customers
          2030 target: 50%+
        Viable ToU product needs at least 5% EV share in portfolio.
        Max margin loss: supplier will accept up to £500 annual P&L hit to test product.
        """
        return cls(
            year=year,
            min_ev_penetration_pct=5.0,
            max_margin_loss_gbp=500.0,
        )


@dataclass(frozen=True)
class ToULaunchAssessment:
    """Board-level ToU product launch assessment for one year.

    Combines cross-subsidy exposure (Ph U) and migration risk (Ph V)
    to recommend LAUNCH / HOLD / MONITOR.
    """
    year: int
    ev_customer_count: int
    total_customers: int
    total_cross_subsidy_gbp: float
    worst_case_margin_delta_gbp: float
    signal: LaunchReadinessSignal
    threshold: ToULaunchThreshold

    @property
    def ev_penetration_pct(self) -> float:
        if self.total_customers == 0:
            return 0.0
        return round(self.ev_customer_count / self.total_customers * 100.0, 2)

    @property
    def margin_at_risk_gbp(self) -> float:
        """Maximum supplier margin that could be lost if all EV customers migrate."""
        return round(self.total_cross_subsidy_gbp, 2)

    @property
    def is_launch_viable(self) -> bool:
        """True when margin-at-risk is within acceptable threshold."""
        return self.margin_at_risk_gbp <= self.threshold.max_margin_loss_gbp

    @property
    def is_market_ready(self) -> bool:
        """True when EV penetration is high enough for a viable ToU product."""
        return self.ev_penetration_pct >= self.threshold.min_ev_penetration_pct


def _determine_signal(
    assessment_partial: dict,
    threshold: ToULaunchThreshold,
) -> LaunchReadinessSignal:
    ev_pct = assessment_partial["ev_penetration_pct"]
    margin_risk = assessment_partial["margin_at_risk_gbp"]
    if ev_pct < threshold.min_ev_penetration_pct:
        return LaunchReadinessSignal.MONITOR
    if margin_risk > threshold.max_margin_loss_gbp:
        return LaunchReadinessSignal.HOLD
    return LaunchReadinessSignal.LAUNCH


class ToUProductLaunchBook:
    """Integrates T/U/V analytics to produce board-level ToU launch decisions.

    Usage::
        book = ToUProductLaunchBook()
        assessment = book.assess(
            register=cross_subsidy_register,
            year=2024,
            total_customers=1000,
        )
    """

    def __init__(self) -> None:
        self._history: list[ToULaunchAssessment] = []

    def assess(
        self,
        register: CrossSubsidyRegister,
        year: int,
        total_customers: int,
        threshold: Optional[ToULaunchThreshold] = None,
    ) -> ToULaunchAssessment:
        """Produce a launch assessment for the given year.

        register: CrossSubsidyRegister from Phase U (holds EV records)
        year: calendar year to assess
        total_customers: total active accounts in portfolio that year
        threshold: optional override; defaults to ToULaunchThreshold.default_for(year)
        """
        if threshold is None:
            threshold = ToULaunchThreshold.default_for(year)

        records = [r for r in register._records if r.year == year]
        ev_customer_count = len({r.account_id for r in records})
        total_cross_subsidy = sum(r.cross_subsidy_gbp for r in records if r.cross_subsidy_gbp > 0)

        ev_pct = (ev_customer_count / total_customers * 100.0) if total_customers > 0 else 0.0
        partial = {
            "ev_penetration_pct": round(ev_pct, 2),
            "margin_at_risk_gbp": round(total_cross_subsidy, 2),
        }
        signal = _determine_signal(partial, threshold)

        worst_case = -total_cross_subsidy if signal != LaunchReadinessSignal.MONITOR else 0.0

        result = ToULaunchAssessment(
            year=year,
            ev_customer_count=ev_customer_count,
            total_customers=total_customers,
            total_cross_subsidy_gbp=round(total_cross_subsidy, 2),
            worst_case_margin_delta_gbp=round(worst_case, 2),
            signal=signal,
            threshold=threshold,
        )
        self._history.append(result)
        return result

    @property
    def launch_history(self) -> list[ToULaunchAssessment]:
        return list(self._history)

    def readiness_trend(self) -> str:
        """Based on EV penetration trajectory across assessed years."""
        if len(self._history) < 2:
            return "insufficient_data"
        pcts = [h.ev_penetration_pct for h in sorted(self._history, key=lambda h: h.year)]
        deltas = [pcts[i+1] - pcts[i] for i in range(len(pcts)-1)]
        avg_delta = sum(deltas) / len(deltas)
        if avg_delta > 0.1:
            return "improving"
        if avg_delta < -0.1:
            return "deteriorating"
        return "stable"

    def years_until_viable(self, current_year: int) -> Optional[int]:
        """Estimate years until EV penetration crosses the min threshold.

        Returns None if the trend is flat/declining or if already viable.
        Extrapolates linearly from the last two data points.
        """
        sorted_history = sorted(self._history, key=lambda h: h.year)
        if len(sorted_history) < 2:
            return None
        last = sorted_history[-1]
        prev = sorted_history[-2]
        if last.is_market_ready:
            return 0
        delta_per_year = last.ev_penetration_pct - prev.ev_penetration_pct
        if delta_per_year <= 0:
            return None
        gap = last.threshold.min_ev_penetration_pct - last.ev_penetration_pct
        return max(1, round(gap / delta_per_year))

    def launch_summary(self) -> dict:
        if not self._history:
            return {"years_assessed": 0, "signals": {}}
        signals = {h.year: h.signal.value for h in self._history}
        latest = sorted(self._history, key=lambda h: h.year)[-1]
        return {
            "years_assessed": len(self._history),
            "signals": signals,
            "latest_signal": latest.signal.value,
            "latest_ev_penetration_pct": latest.ev_penetration_pct,
            "latest_margin_at_risk_gbp": latest.margin_at_risk_gbp,
            "readiness_trend": self.readiness_trend(),
        }
