"""Risk Committee Decision Ledger — tracks and assesses risk committee interventions.

Company-observable: the company knows its own committee decisions, their triggers,
and subsequent treasury outcomes. Does NOT see simulation churn parameters.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class InterventionTrigger(str, Enum):
    VAR_THRESHOLD = "var_threshold"       # Stressed VaR exceeds mandate
    TREASURY_STRESS = "treasury_stress"   # Treasury falls below floor
    PRICE_SPIKE = "price_spike"           # Wholesale price move >20%
    MARGIN_DETERIORATION = "margin_deterioration"  # Margin below floor
    SCHEDULED_REVIEW = "scheduled_review" # Annual mandate review


class InterventionOutcome(str, Enum):
    EFFECTIVE = "effective"       # Treasury improved / VaR reduced
    NEUTRAL = "neutral"           # No material change
    COUNTERPRODUCTIVE = "counterproductive"  # Worse outcome
    PENDING = "pending"           # Not yet assessed


@dataclass(frozen=True)
class CommitteeSession:
    session_date: str           # ISO date
    trigger: InterventionTrigger
    treasury_at_session_gbp: float
    portfolio_var_current_gbp: float
    portfolio_var_stressed_gbp: float
    customers_adjusted: list[str]  # Account IDs with hedge fraction changes
    adjustment_summary: str    # e.g. "6 accounts set to max hedge (1.0)"
    post_session_treasury_gbp: Optional[float] = None  # Set when next period data available

    @property
    def var_ratio(self) -> Optional[float]:
        if self.portfolio_var_stressed_gbp <= 0:
            return None
        return round(self.portfolio_var_current_gbp / self.portfolio_var_stressed_gbp, 3)

    @property
    def outcome(self) -> InterventionOutcome:
        if self.post_session_treasury_gbp is None:
            return InterventionOutcome.PENDING
        delta = self.post_session_treasury_gbp - self.treasury_at_session_gbp
        if delta > 1000:
            return InterventionOutcome.EFFECTIVE
        elif delta < -1000:
            return InterventionOutcome.COUNTERPRODUCTIVE
        return InterventionOutcome.NEUTRAL

    @property
    def treasury_delta_gbp(self) -> Optional[float]:
        if self.post_session_treasury_gbp is None:
            return None
        return round(self.post_session_treasury_gbp - self.treasury_at_session_gbp, 2)


class RiskCommitteeDecisionLedger:
    """Tracks risk committee sessions and assesses intervention effectiveness."""

    def __init__(self) -> None:
        self._sessions: list[CommitteeSession] = []

    def record_session(self, session: CommitteeSession) -> CommitteeSession:
        self._sessions.append(session)
        return session

    def sessions_for_year(self, year: int) -> list[CommitteeSession]:
        return [s for s in self._sessions if s.session_date.startswith(str(year))]

    def sessions_by_trigger(self, trigger: InterventionTrigger) -> list[CommitteeSession]:
        return [s for s in self._sessions if s.trigger == trigger]

    def effective_interventions(self) -> list[CommitteeSession]:
        return [s for s in self._sessions if s.outcome == InterventionOutcome.EFFECTIVE]

    def counterproductive_interventions(self) -> list[CommitteeSession]:
        return [s for s in self._sessions if s.outcome == InterventionOutcome.COUNTERPRODUCTIVE]

    def intervention_effectiveness_rate(self) -> Optional[float]:
        assessed = [s for s in self._sessions if s.outcome != InterventionOutcome.PENDING]
        if not assessed:
            return None
        effective = sum(1 for s in assessed if s.outcome == InterventionOutcome.EFFECTIVE)
        return round(effective / len(assessed) * 100, 1)

    def most_active_trigger(self) -> Optional[InterventionTrigger]:
        if not self._sessions:
            return None
        from collections import Counter
        c = Counter(s.trigger for s in self._sessions)
        return c.most_common(1)[0][0]

    def busiest_year(self) -> Optional[int]:
        if not self._sessions:
            return None
        from collections import Counter
        c = Counter(s.session_date[:4] for s in self._sessions)
        return int(c.most_common(1)[0][0])

    def peak_stressed_var_gbp(self) -> float:
        if not self._sessions:
            return 0.0
        return max(s.portfolio_var_stressed_gbp for s in self._sessions)

    def governance_summary(self) -> str:
        if not self._sessions:
            return "No risk committee sessions recorded."
        total = len(self._sessions)
        effective = len(self.effective_interventions())
        counterproductive = len(self.counterproductive_interventions())
        pending = sum(1 for s in self._sessions if s.outcome == InterventionOutcome.PENDING)
        busiest = self.busiest_year()
        lines = [
            f"Risk Committee Decision Ledger: {total} sessions recorded",
            f"Outcomes: {effective} effective / {counterproductive} counterproductive / {pending} pending",
            f"Busiest year: {busiest} | Peak stressed VaR: £{self.peak_stressed_var_gbp():,.0f}",
        ]
        rate = self.intervention_effectiveness_rate()
        if rate is not None:
            lines.append(f"Intervention effectiveness rate: {rate:.0f}%")
        top_trigger = self.most_active_trigger()
        if top_trigger:
            lines.append(f"Most common trigger: {top_trigger.value}")
        return "\n".join(lines)
