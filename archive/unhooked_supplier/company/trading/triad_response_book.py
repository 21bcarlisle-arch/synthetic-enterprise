"""Triad Demand Response Book (Phase FU).

I&C customers enrolled in Triad notification receive alerts (see triad_notification_book.py)
before suspected Triad windows. This module tracks whether they actually reduced demand,
by how much, and what TNUoS saving was achieved vs. the counterfactual.

The three National Grid Triads each winter are the half-hours of peak GB-wide demand
(Nov-Feb, excluding the 10 days either side of the other Triads). TNUoS charges for
I&C customers are proportional to their average demand during these 3 half-hours.

Epistemic: baseline demand is the company\'s own EAC-based forecast (observable).
Actual demand during Triad periods is from the company\'s metered HH data (observable).
TNUoS rate is published by NESO each March for the following year (observable).
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

_FULL_RESPONSE_REDUCTION_PCT = 20.0   # >=20% reduction = full response
_PARTIAL_RESPONSE_REDUCTION_PCT = 5.0  # 5-20% = partial response
_DEFAULT_TNUOS_RATE_GBP_PER_KW = 80.0  # typical Zone 14 rate


class TriadResponseOutcome(str, Enum):
    FULL_RESPONSE = "full_response"
    PARTIAL_RESPONSE = "partial_response"
    NO_RESPONSE = "no_response"
    NOT_ALERTED = "not_alerted"


@dataclass(frozen=True)
class TriadDemandEvent:
    """Recorded demand at a Triad half-hour for one I&C customer."""

    customer_id: str
    triad_season: str           # e.g. "2022/23"
    triad_number: int           # 1, 2, or 3
    settlement_date: dt.date
    settlement_period: int      # 1-48 (half-hours)
    baseline_demand_mw: float   # company forecast without response
    actual_demand_mw: float     # metered HH demand during the window
    was_alerted: bool
    tnuos_rate_gbp_per_kw: float = _DEFAULT_TNUOS_RATE_GBP_PER_KW

    @property
    def demand_reduction_mw(self) -> float:
        return max(0.0, self.baseline_demand_mw - self.actual_demand_mw)

    @property
    def reduction_pct(self) -> float:
        if self.baseline_demand_mw <= 0:
            return 0.0
        return self.demand_reduction_mw / self.baseline_demand_mw * 100.0

    @property
    def outcome(self) -> TriadResponseOutcome:
        if not self.was_alerted:
            return TriadResponseOutcome.NOT_ALERTED
        if self.reduction_pct >= _FULL_RESPONSE_REDUCTION_PCT:
            return TriadResponseOutcome.FULL_RESPONSE
        if self.reduction_pct >= _PARTIAL_RESPONSE_REDUCTION_PCT:
            return TriadResponseOutcome.PARTIAL_RESPONSE
        return TriadResponseOutcome.NO_RESPONSE

    @property
    def tnuos_saving_gbp(self) -> float:
        """TNUoS saving = reduction in average demand × annual tariff rate.

        Average demand across all 3 Triads is what matters for TNUoS billing.
        This records the saving for ONE Triad event; the full-season saving
        aggregates across all 3 events and divides by 3.
        """
        reduction_kw = self.demand_reduction_mw * 1000.0
        return reduction_kw * self.tnuos_rate_gbp_per_kw

    def event_summary(self) -> str:
        return (
            "Triad " + self.triad_season + " #" + str(self.triad_number) + " "
            + self.customer_id + " "
            + str(self.settlement_date) + " SP" + str(self.settlement_period) + ": "
            "baseline=" + str(round(self.baseline_demand_mw, 2)) + "MW "
            "actual=" + str(round(self.actual_demand_mw, 2)) + "MW "
            "reduction=" + str(round(self.demand_reduction_mw, 2)) + "MW "
            "(" + self.outcome.value + ")"
        )


class TriadDemandResponseBook:
    """Tracks I&C customer demand response during Triad risk windows."""

    def __init__(self) -> None:
        self._events: List[TriadDemandEvent] = []

    def record_event(self, event: TriadDemandEvent) -> TriadDemandEvent:
        self._events.append(event)
        return event

    def events_for_customer(self, customer_id: str) -> List[TriadDemandEvent]:
        return [e for e in self._events if e.customer_id == customer_id]

    def events_for_season(self, season: str) -> List[TriadDemandEvent]:
        return [e for e in self._events if e.triad_season == season]

    def full_response_events(self) -> List[TriadDemandEvent]:
        return [e for e in self._events if e.outcome == TriadResponseOutcome.FULL_RESPONSE]

    def no_response_events(self) -> List[TriadDemandEvent]:
        return [e for e in self._events if e.outcome == TriadResponseOutcome.NO_RESPONSE]

    def total_demand_reduction_mw_for_season(self, season: str) -> float:
        return sum(e.demand_reduction_mw for e in self.events_for_season(season))

    def total_tnuos_saving_gbp(self) -> float:
        """Total TNUoS saving across all recorded events (approximate)."""
        return sum(e.tnuos_saving_gbp for e in self._events)

    def response_rate_pct(self) -> float:
        """Fraction of alerted events that achieved full response."""
        alerted = [e for e in self._events if e.was_alerted]
        if not alerted:
            return 0.0
        full = sum(1 for e in alerted if e.outcome == TriadResponseOutcome.FULL_RESPONSE)
        return round(full / len(alerted) * 100.0, 1)

    def saving_by_customer(self) -> Dict[str, float]:
        """Total TNUoS saving per customer across all seasons."""
        savings: Dict[str, float] = {}
        for e in self._events:
            savings[e.customer_id] = savings.get(e.customer_id, 0.0) + e.tnuos_saving_gbp
        return savings

    def top_responders(self, n: int = 3) -> List[str]:
        """Customer IDs with the highest total TNUoS saving, best first."""
        by_saving = self.saving_by_customer()
        return sorted(by_saving, key=lambda cid: by_saving[cid], reverse=True)[:n]

    def demand_response_summary(self) -> str:
        n = len(self._events)
        if n == 0:
            return "Triad Demand Response: no events recorded."
        total_saving = self.total_tnuos_saving_gbp()
        full = len(self.full_response_events())
        rr = self.response_rate_pct()
        return (
            "Triad Demand Response: " + str(n) + " events. "
            "Full-response events: " + str(full) + ". "
            "Response rate: " + str(rr) + "%. "
            "Total TNUoS saving approx: GBP" + str(round(total_saving, 0)) + "."
        )
