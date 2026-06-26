from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional


_ANNUAL_TARGETS: dict[int, float] = {
    2016: 0.10, 2017: 0.20, 2018: 0.30, 2019: 0.40,
    2020: 0.50, 2021: 0.55, 2022: 0.60, 2023: 0.70,
    2024: 0.80, 2025: 0.85,
}


class MeterGeneration(str, Enum):
    SMETS1 = "smets1"
    SMETS2 = "smets2"
    TRADITIONAL = "traditional"


class RolloutStatus(str, Enum):
    ON_TRACK = "on_track"
    BEHIND = "behind"
    SIGNIFICANTLY_BEHIND = "significantly_behind"

_SMETS1_REMOTE_READ_RATE = 0.75
_SMETS2_REMOTE_READ_RATE = 0.95
_MANUAL_READ_COST_GBP = 15.0


@dataclass(frozen=True)
class MeterPortfolioSnapshot:
    year: int
    traditional_count: int
    smets1_count: int
    smets2_count: int

    @property
    def total_meters(self) -> int:
        return self.traditional_count + self.smets1_count + self.smets2_count

    @property
    def smart_count(self) -> int:
        return self.smets1_count + self.smets2_count

    @property
    def smart_penetration_pct(self) -> float:
        if self.total_meters == 0:
            return 0.0
        return round(self.smart_count / self.total_meters * 100, 2)

    @property
    def remote_reads_pct(self) -> float:
        if self.smart_count == 0:
            return 0.0
        s1_reads = self.smets1_count * _SMETS1_REMOTE_READ_RATE
        s2_reads = self.smets2_count * _SMETS2_REMOTE_READ_RATE
        return round((s1_reads + s2_reads) / self.smart_count * 100, 2)

    @property
    def annual_manual_read_cost_gbp(self) -> float:
        manual_reads = self.traditional_count + self.smets1_count * (1 - _SMETS1_REMOTE_READ_RATE)
        return round(manual_reads * _MANUAL_READ_COST_GBP, 2)


class SmartMeterRolloutBook:
    def __init__(self) -> None:
        self._snapshots: list[MeterPortfolioSnapshot] = []

    def record_snapshot(self, snapshot: MeterPortfolioSnapshot) -> MeterPortfolioSnapshot:
        self._snapshots.append(snapshot)
        return snapshot

    def snapshot_for_year(self, year: int) -> Optional[MeterPortfolioSnapshot]:
        for s in self._snapshots:
            if s.year == year:
                return s
        return None

    def rollout_status(self, year: int) -> RolloutStatus:
        snap = self.snapshot_for_year(year)
        if snap is None:
            return RolloutStatus.BEHIND
        target = _ANNUAL_TARGETS.get(year, 0.85)
        actual = snap.smart_penetration_pct / 100
        if actual >= target:
            return RolloutStatus.ON_TRACK
        if actual >= target * 0.8:
            return RolloutStatus.BEHIND
        return RolloutStatus.SIGNIFICANTLY_BEHIND

    def annual_progress(self) -> list[dict]:
        result = []
        for snap in sorted(self._snapshots, key=lambda s: s.year):
            target = _ANNUAL_TARGETS.get(snap.year, 0.85)
            result.append({
                "year": snap.year,
                "smart_penetration_pct": snap.smart_penetration_pct,
                "target_pct": round(target * 100, 1),
                "status": self.rollout_status(snap.year).value,
                "remote_reads_pct": snap.remote_reads_pct,
                "annual_manual_read_cost_gbp": snap.annual_manual_read_cost_gbp,
            })
        return result

    def rollout_summary(self) -> dict:
        if not self._snapshots:
            return {"years_tracked": 0, "latest_penetration_pct": 0.0}
        latest = max(self._snapshots, key=lambda s: s.year)
        return {
            "years_tracked": len(self._snapshots),
            "latest_year": latest.year,
            "latest_penetration_pct": latest.smart_penetration_pct,
            "latest_status": self.rollout_status(latest.year).value,
            "total_meters": latest.total_meters,
            "smets2_share_pct": round(latest.smets2_count / latest.smart_count * 100, 2)
                if latest.smart_count > 0 else 0.0,
        }
