"""MHHS Readiness Tracker: Market-wide Half Hourly Settlement programme milestones."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class MHHSMilestoneStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    AT_RISK = "at_risk"
    FAILED = "failed"


class MHHSMilestone(str, Enum):
    DCC_CONNECTIVITY = "dcc_connectivity"
    HH_DATA_INGESTION = "hh_data_ingestion"
    NHH_PROFILE_MIGRATION = "nhh_profile_migration"
    SETTLEMENT_SYSTEM_UPGRADE = "settlement_system_upgrade"
    CUSTOMER_COMMUNICATION = "customer_communication"
    ELEXON_REGISTRATION = "elexon_registration"
    GO_LIVE_SHADOW_RUNNING = "go_live_shadow_running"
    GO_LIVE_PRODUCTION = "go_live_production"


_MHHS_GO_LIVE_TARGET = dt.date(2025, 6, 5)  # Ofgem MHHS Programme target date
_MHHS_SHADOW_RUNNING_START = dt.date(2024, 11, 1)


@dataclass(frozen=True)
class MHHSMilestoneRecord:
    milestone: MHHSMilestone
    target_date: dt.date
    status: MHHSMilestoneStatus
    completion_date: Optional[dt.date] = None
    notes: str = ""

    def is_overdue(self, as_of: dt.date) -> bool:
        if self.status in (MHHSMilestoneStatus.COMPLETE, MHHSMilestoneStatus.FAILED):
            return False
        return as_of > self.target_date

    def days_to_target(self, as_of: dt.date) -> int:
        return (self.target_date - as_of).days


@dataclass(frozen=True)
class MHHSReadinessSnapshot:
    snapshot_date: dt.date
    pct_customers_hh_settled: float
    pct_smets2_dcc_connected: float
    nhh_profiles_migrated: int
    total_nhh_customers: int

    @property
    def migration_completion_pct(self) -> float:
        if self.total_nhh_customers == 0:
            return 100.0
        return round(self.nhh_profiles_migrated / self.total_nhh_customers * 100, 1)

    @property
    def is_on_track(self) -> bool:
        days_left = (_MHHS_GO_LIVE_TARGET - self.snapshot_date).days
        if days_left <= 0:
            return self.pct_customers_hh_settled >= 95.0
        return self.migration_completion_pct >= min(100, (365 - days_left) / 365 * 120)


class MHHSReadinessTracker:
    """Tracks supplier readiness for MHHS go-live.

    Real calibration:
    - MHHS programme: Ofgem Significant Code Review (SCR) 2020; BSC Modification P272.
    - Biggest electricity market reform since NETA (2001): moves all customers from
      profile-based (NHH) settlement to actual half-hourly metered data.
    - Timeline: Shadow running Nov 2024; Production June 2025 target.
    - DCC (Data Communications Company): central infrastructure for SMETS2 data flow.
    - Requires suppliers to: connect to DCC for HH reads; update settlement systems;
      migrate NHH customers to HH profiles; register HH meter points with Elexon/BSC.
    - Impact: suppliers without SMETS2 base will rely on SDP (Settlement Data Provider)
      proxy for non-communicating meters -- adds cost and uncertainty.
    """

    def __init__(self) -> None:
        self._milestones: Dict[MHHSMilestone, MHHSMilestoneRecord] = {}
        self._snapshots: List[MHHSReadinessSnapshot] = []

    def record_milestone(self, record: MHHSMilestoneRecord) -> MHHSMilestoneRecord:
        self._milestones[record.milestone] = record
        return record

    def update_milestone(self, milestone: MHHSMilestone,
                         status: MHHSMilestoneStatus,
                         completion_date: Optional[dt.date] = None) -> MHHSMilestoneRecord:
        import dataclasses
        existing = self._milestones.get(milestone)
        if existing is None:
            raise ValueError(f"Milestone not registered: {milestone}")
        updated = dataclasses.replace(existing, status=status,
                                       completion_date=completion_date)
        self._milestones[milestone] = updated
        return updated

    def record_snapshot(self, snapshot: MHHSReadinessSnapshot) -> MHHSReadinessSnapshot:
        self._snapshots.append(snapshot)
        return snapshot

    def overdue_milestones(self, as_of: dt.date) -> List[MHHSMilestoneRecord]:
        return [m for m in self._milestones.values() if m.is_overdue(as_of)]

    def complete_milestones(self) -> List[MHHSMilestoneRecord]:
        return [m for m in self._milestones.values()
                if m.status == MHHSMilestoneStatus.COMPLETE]

    def at_risk_milestones(self) -> List[MHHSMilestoneRecord]:
        return [m for m in self._milestones.values()
                if m.status == MHHSMilestoneStatus.AT_RISK]

    def latest_snapshot(self) -> Optional[MHHSReadinessSnapshot]:
        if not self._snapshots:
            return None
        return sorted(self._snapshots, key=lambda s: s.snapshot_date)[-1]

    def readiness_rag(self, as_of: dt.date) -> str:
        overdue = len(self.overdue_milestones(as_of))
        at_risk = len(self.at_risk_milestones())
        if overdue > 0:
            return "RED"
        if at_risk > 0:
            return "AMBER"
        return "GREEN"

    def mhhs_summary(self, as_of: dt.date) -> dict:
        snap = self.latest_snapshot()
        return {
            "total_milestones": len(self._milestones),
            "complete": len(self.complete_milestones()),
            "overdue": len(self.overdue_milestones(as_of)),
            "at_risk": len(self.at_risk_milestones()),
            "readiness_rag": self.readiness_rag(as_of),
            "hh_settled_pct": snap.pct_customers_hh_settled if snap else 0.0,
        }
