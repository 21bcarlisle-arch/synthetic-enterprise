"""Churn waterfall and reason code analysis.

UK energy suppliers track churn reasons to understand portfolio health.
The churn waterfall shows movement in/out of the book:
- Opening book → gains (switching in) → losses (switching out, cancelled)
  → closing book

Reason codes for losses come from service contacts, switching data, and
market intelligence (price comparison, competitor tariffs).

This module models the churn waterfall from observable company data.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


ChurnReason = Literal[
    "price",           # customer found cheaper elsewhere
    "service",         # complaint or poor service experience
    "moving_home",     # change of address
    "switching_broker",# 3rd-party intermediary facilitated switch
    "auto_renewal",    # customer switched at auto-renewal without contacting
    "going_green",     # moved to renewable-focused supplier
    "consolidation",   # multi-site moving all to single supplier
    "unknown",         # reason not captured
]


@dataclass
class ChurnEvent:
    customer_id: str
    direction: Literal["gain", "loss"]
    year: int
    reason: ChurnReason = "unknown"
    retention_attempted: bool = False
    retention_succeeded: bool = False


@dataclass
class ChurnWaterfall:
    year: int
    opening_book: int
    gains: int
    losses: int

    @property
    def closing_book(self) -> int:
        return self.opening_book + self.gains - self.losses

    @property
    def net_change(self) -> int:
        return self.gains - self.losses

    @property
    def churn_rate(self) -> float:
        if self.opening_book == 0:
            return 0.0
        return round(self.losses / self.opening_book, 4)

    @property
    def growth_rate(self) -> float:
        if self.opening_book == 0:
            return 0.0
        return round(self.net_change / self.opening_book, 4)


class ChurnAnalytics:
    """Tracks churn events and produces waterfall + reason analysis."""

    def __init__(self):
        self._events: list[ChurnEvent] = []

    def record(self, event: ChurnEvent) -> None:
        self._events.append(event)

    def losses_by_year(self, year: int) -> list[ChurnEvent]:
        return [e for e in self._events if e.year == year and e.direction == "loss"]

    def gains_by_year(self, year: int) -> list[ChurnEvent]:
        return [e for e in self._events if e.year == year and e.direction == "gain"]

    def reason_breakdown(self, year: int) -> dict[str, int]:
        losses = self.losses_by_year(year)
        reasons: dict[str, int] = {}
        for e in losses:
            reasons[e.reason] = reasons.get(e.reason, 0) + 1
        return dict(sorted(reasons.items(), key=lambda x: -x[1]))

    def retention_rate(self, year: int) -> float:
        losses = self.losses_by_year(year)
        attempted = [e for e in losses if e.retention_attempted]
        if not attempted:
            return 0.0
        succeeded = sum(1 for e in attempted if e.retention_succeeded)
        return round(succeeded / len(attempted), 4)

    def waterfall(self, year: int, opening_book: int) -> ChurnWaterfall:
        gains = len(self.gains_by_year(year))
        losses = len(self.losses_by_year(year))
        return ChurnWaterfall(year=year, opening_book=opening_book, gains=gains, losses=losses)

    def summary(self, year: int, opening_book: int) -> dict:
        wf = self.waterfall(year, opening_book)
        return {
            "year": year,
            "opening_book": wf.opening_book,
            "gains": wf.gains,
            "losses": wf.losses,
            "closing_book": wf.closing_book,
            "churn_rate_pct": round(wf.churn_rate * 100, 2),
            "growth_rate_pct": round(wf.growth_rate * 100, 2),
            "reason_breakdown": self.reason_breakdown(year),
            "retention_rate_pct": round(self.retention_rate(year) * 100, 2),
        }
