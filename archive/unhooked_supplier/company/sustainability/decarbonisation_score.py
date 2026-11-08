from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class DScoreBand(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"


@dataclass(frozen=True)
class DScoreBreakdown:
    rego_coverage_pts: float
    epc_improvement_pts: float
    heat_pump_pts: float
    carbon_reduction_pts: float

    @property
    def total(self) -> float:
        return round(
            self.rego_coverage_pts + self.epc_improvement_pts
            + self.heat_pump_pts + self.carbon_reduction_pts,
            2,
        )

    @property
    def band(self) -> DScoreBand:
        t = self.total
        if t >= 80:
            return DScoreBand.A
        if t >= 60:
            return DScoreBand.B
        if t >= 40:
            return DScoreBand.C
        return DScoreBand.D

    def to_dict(self) -> dict:
        return {
            "total": self.total,
            "band": self.band.value,
            "rego_coverage_pts": self.rego_coverage_pts,
            "epc_improvement_pts": self.epc_improvement_pts,
            "heat_pump_pts": self.heat_pump_pts,
            "carbon_reduction_pts": self.carbon_reduction_pts,
        }


class DecarbScorer:
    MAX_REGO = 25.0
    MAX_EPC = 25.0
    MAX_HEAT_PUMP = 25.0
    MAX_CARBON = 25.0

    def score_rego_coverage(self, covered_mwh: float, total_retail_mwh: float) -> float:
        if total_retail_mwh <= 0:
            return 0.0
        pct = covered_mwh / total_retail_mwh
        return round(min(pct, 1.0) * self.MAX_REGO, 2)

    def score_epc_improvement(self, properties_improved: int, total_properties: int) -> float:
        if total_properties <= 0:
            return 0.0
        rate = properties_improved / total_properties
        return round(min(rate, 1.0) * self.MAX_EPC, 2)

    def score_heat_pump_adoption(self, heat_pump_properties: int, total_properties: int) -> float:
        if total_properties <= 0:
            return 0.0
        rate = heat_pump_properties / total_properties
        return round(min(rate * 5, 1.0) * self.MAX_HEAT_PUMP, 2)

    def score_carbon_reduction(self, prior_carbon_t: float, current_carbon_t: float) -> float:
        if prior_carbon_t <= 0:
            return 0.0
        reduction_pct = max(0.0, (prior_carbon_t - current_carbon_t) / prior_carbon_t)
        return round(min(reduction_pct * 5, 1.0) * self.MAX_CARBON, 2)

    def compute(
        self,
        covered_mwh: float,
        total_retail_mwh: float,
        properties_improved: int,
        total_properties: int,
        heat_pump_properties: int,
        prior_carbon_t: float,
        current_carbon_t: float,
    ) -> DScoreBreakdown:
        return DScoreBreakdown(
            rego_coverage_pts=self.score_rego_coverage(covered_mwh, total_retail_mwh),
            epc_improvement_pts=self.score_epc_improvement(properties_improved, total_properties),
            heat_pump_pts=self.score_heat_pump_adoption(heat_pump_properties, total_properties),
            carbon_reduction_pts=self.score_carbon_reduction(prior_carbon_t, current_carbon_t),
        )


class DScoreBook:
    def __init__(self) -> None:
        self._records: list[tuple[int, DScoreBreakdown]] = []

    def record(self, year: int, breakdown: DScoreBreakdown) -> DScoreBreakdown:
        self._records.append((year, breakdown))
        return breakdown

    def latest(self) -> Optional[DScoreBreakdown]:
        return self._records[-1][1] if self._records else None

    def score_for_year(self, year: int) -> Optional[DScoreBreakdown]:
        for yr, bd in self._records:
            if yr == year:
                return bd
        return None

    def trend(self) -> list[dict]:
        return [
            {"year": yr, "total": bd.total, "band": bd.band.value}
            for yr, bd in sorted(self._records, key=lambda x: x[0])
        ]

    def improving(self) -> bool:
        if len(self._records) < 2:
            return False
        sorted_recs = sorted(self._records, key=lambda x: x[0])
        return sorted_recs[-1][1].total > sorted_recs[-2][1].total

    def summary(self) -> dict:
        if not self._records:
            return {"years_recorded": 0, "latest_score": None, "latest_band": None}
        latest = self.latest()
        assert latest is not None
        return {
            "years_recorded": len(self._records),
            "latest_score": latest.total,
            "latest_band": latest.band.value,
            "improving": self.improving(),
            "trend": self.trend(),
        }
