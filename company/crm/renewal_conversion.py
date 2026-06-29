"""Renewal Conversion Rate Book.

Tracks contract renewal outcomes — which customers accepted a renewal offer vs.
switched away or lapsed. Feeds into CAC analysis (higher churn = higher marginal
acquisition cost) and profitability prioritisation (which segments to protect).

Observable-only: outcome is derived from CRM records of offer sent vs. contract
signed (or switch notification received).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import Enum
from typing import Optional


class RenewalOutcome(Enum):
    ACCEPTED = "accepted"       # Customer renewed with us
    SWITCHED = "switched"       # Customer switched to competitor
    LAPSED = "lapsed"           # Contract expired, no action — became deemed
    PENDING = "pending"         # Offer sent, decision not yet made


class RenewalChannel(Enum):
    DIRECT_PHONE = "direct_phone"
    ONLINE = "online"
    BROKER = "broker"
    AUTOMATIC = "automatic"  # auto-rollover terms


# Ofgem SLC 22: minimum 42 days notice before end of fixed term.
MINIMUM_RENEWAL_NOTICE_DAYS: int = 42


@dataclass(frozen=True)
class RenewalRecord:
    """One renewal decision for one customer contract."""
    account_id: str
    fuel: str                           # "electricity" or "gas"
    offer_date: str                     # ISO date: when renewal offer was sent
    term_end_date: str                  # ISO date: when current term expires
    outcome: RenewalOutcome
    channel: RenewalChannel
    segment: str
    decision_date: Optional[str] = None  # ISO date: when decision was made

    @property
    def days_to_decision(self) -> Optional[int]:
        if self.decision_date is None:
            return None
        offer = date.fromisoformat(self.offer_date)
        decision = date.fromisoformat(self.decision_date)
        return (decision - offer).days

    @property
    def days_notice_before_term_end(self) -> int:
        offer = date.fromisoformat(self.offer_date)
        end = date.fromisoformat(self.term_end_date)
        return (end - offer).days

    @property
    def met_notice_obligation(self) -> bool:
        return self.days_notice_before_term_end >= MINIMUM_RENEWAL_NOTICE_DAYS

    @property
    def is_closed(self) -> bool:
        return self.outcome != RenewalOutcome.PENDING

    @property
    def is_retained(self) -> bool:
        return self.outcome == RenewalOutcome.ACCEPTED


class RenewalConversionBook:
    """Tracks and analyses contract renewal outcomes across the portfolio."""

    def __init__(self) -> None:
        self._records: list[RenewalRecord] = []

    def record(self, rec: RenewalRecord) -> RenewalRecord:
        self._records.append(rec)
        return rec

    def outcomes_for(
        self,
        year: Optional[int] = None,
        segment: Optional[str] = None,
        fuel: Optional[str] = None,
    ) -> list[RenewalRecord]:
        recs = [r for r in self._records if r.is_closed]
        if year is not None:
            recs = [r for r in recs if r.offer_date.startswith(str(year))]
        if segment is not None:
            recs = [r for r in recs if r.segment == segment]
        if fuel is not None:
            recs = [r for r in recs if r.fuel == fuel]
        return recs

    def conversion_rate_pct(
        self,
        year: Optional[int] = None,
        segment: Optional[str] = None,
        fuel: Optional[str] = None,
    ) -> Optional[float]:
        closed = self.outcomes_for(year=year, segment=segment, fuel=fuel)
        if not closed:
            return None
        retained = sum(1 for r in closed if r.is_retained)
        return round(retained / len(closed) * 100, 2)

    def avg_days_to_decision(
        self,
        year: Optional[int] = None,
        segment: Optional[str] = None,
    ) -> Optional[float]:
        closed = [r for r in self.outcomes_for(year=year, segment=segment)
                  if r.days_to_decision is not None]
        if not closed:
            return None
        return round(sum(r.days_to_decision for r in closed) / len(closed), 1)

    def notice_obligation_breaches(self, year: Optional[int] = None) -> list[RenewalRecord]:
        return [r for r in self._records
                if not r.met_notice_obligation
                and (year is None or r.offer_date.startswith(str(year)))]

    def pending_decisions(self) -> list[RenewalRecord]:
        return [r for r in self._records if r.outcome == RenewalOutcome.PENDING]

    def best_converting_segment(self, year: Optional[int] = None) -> Optional[str]:
        segments = {r.segment for r in self.outcomes_for(year=year)}
        if not segments:
            return None
        return max(
            segments,
            key=lambda s: self.conversion_rate_pct(year=year, segment=s) or 0.0,
        )

    def conversion_summary(self, year: Optional[int] = None) -> dict:
        closed = self.outcomes_for(year=year)
        if not closed:
            return {"total_decisions": 0}
        retained = sum(1 for r in closed if r.is_retained)
        switched = sum(1 for r in closed if r.outcome == RenewalOutcome.SWITCHED)
        lapsed = sum(1 for r in closed if r.outcome == RenewalOutcome.LAPSED)
        return {
            "total_decisions": len(closed),
            "retained": retained,
            "switched": switched,
            "lapsed": lapsed,
            "conversion_rate_pct": round(retained / len(closed) * 100, 2),
            "pending_count": len(self.pending_decisions()),
            "notice_obligation_breaches": len(self.notice_obligation_breaches(year=year)),
        }
