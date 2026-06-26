"""Energy Company Obligation (ECO) tracker.

UK suppliers with more than 250,000 domestic accounts (fuel-adjusted) are
obligated to deliver energy efficiency measures to low-income households
under the ECO scheme (currently ECO4, running 2022-2026).

Smaller suppliers (≤150k accounts) are exempt. Those between 150k-250k pay
a contribution fee instead of delivering measures directly.

Obligation is set in TWhd (thermal whole-house equivalent, a scoring metric).
Failure to meet obligation by the scheme year-end triggers Ofgem enforcement.

Source: DESNZ / Ofgem ECO4 Supplier Guidance.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


_SMALL_SUPPLIER_THRESHOLD = 150_000       # exempt below this
_CONTRIBUTION_FEE_THRESHOLD = 250_000     # direct delivery above this
_ECO4_OBLIGATION_RATE_TWHD_PER_1K_ACCS = 0.042  # approx 2022-2026 rate

# Typical ECO4 measure scores in kWhd (unit: carbon-weighted kWh heating)
_MEASURE_SCORES: dict[str, float] = {
    "loft_insulation_100mm": 65.0,
    "loft_insulation_270mm": 80.0,
    "cavity_wall_insulation": 95.0,
    "solid_wall_insulation_internal": 260.0,
    "solid_wall_insulation_external": 290.0,
    "heat_pump_air_source": 350.0,
    "boiler_replacement_condensing": 120.0,
    "first_time_central_heating": 450.0,
    "smart_heating_controls": 22.0,
}


@dataclass
class EcoMeasure:
    measure_id: str
    measure_type: str
    customer_id: str
    property_address: str
    completion_date: str
    score_twhd: float
    cost_gbp: float
    verified: bool = False


class EcoTracker:
    """Tracks ECO obligation and delivered measures for the supplier."""

    def __init__(self, account_count: int, scheme_year: int = 2024):
        self._account_count = account_count
        self._scheme_year = scheme_year
        self._measures: list[EcoMeasure] = []

    @property
    def is_exempt(self) -> bool:
        return self._account_count < _SMALL_SUPPLIER_THRESHOLD

    @property
    def pays_contribution(self) -> bool:
        return _SMALL_SUPPLIER_THRESHOLD <= self._account_count < _CONTRIBUTION_FEE_THRESHOLD

    @property
    def must_deliver_directly(self) -> bool:
        return self._account_count >= _CONTRIBUTION_FEE_THRESHOLD

    @property
    def annual_obligation_twhd(self) -> float:
        if self.is_exempt:
            return 0.0
        return round(self._account_count / 1000.0 * _ECO4_OBLIGATION_RATE_TWHD_PER_1K_ACCS, 2)

    def record_measure(self, measure: EcoMeasure) -> EcoMeasure:
        self._measures.append(measure)
        return measure

    def delivered_twhd(self) -> float:
        return round(sum(m.score_twhd for m in self._measures if m.verified), 2)

    def delivered_twhd_unverified(self) -> float:
        return round(sum(m.score_twhd for m in self._measures), 2)

    def shortfall_twhd(self) -> float:
        return max(0.0, round(self.annual_obligation_twhd - self.delivered_twhd(), 2))

    def completion_pct(self) -> float:
        if self.annual_obligation_twhd == 0:
            return 100.0
        return round(100.0 * self.delivered_twhd() / self.annual_obligation_twhd, 1)

    def status(self) -> Literal["EXEMPT", "ON_TRACK", "AT_RISK", "BREACH"]:
        if self.is_exempt:
            return "EXEMPT"
        pct = self.completion_pct()
        if pct >= 100.0:
            return "ON_TRACK"
        elif pct >= 75.0:
            return "ON_TRACK"
        elif pct >= 50.0:
            return "AT_RISK"
        return "BREACH"

    def measure_scores(self) -> dict[str, float]:
        return dict(_MEASURE_SCORES)

    def summary(self) -> dict:
        return {
            "account_count": self._account_count,
            "exempt": self.is_exempt,
            "pays_contribution": self.pays_contribution,
            "must_deliver_directly": self.must_deliver_directly,
            "annual_obligation_twhd": self.annual_obligation_twhd,
            "delivered_twhd": self.delivered_twhd(),
            "shortfall_twhd": self.shortfall_twhd(),
            "completion_pct": self.completion_pct(),
            "status": self.status(),
            "measures_count": len(self._measures),
        }
