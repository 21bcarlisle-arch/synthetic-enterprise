"""BSC Settlement Dispute Register.

When a BSP (Balancing and Settlement Code Party) believes a settlement run
contains errors, they may raise a Settlement Query (SQ) through the BSC
dispute resolution process. Elexon's Settlement Administration Agent (SAA)
investigates and either corrects the run or rejects the query.

BSC Section T Settlement Disputes:
  - SQ must be raised within 20 working days of the settlement run.
  - The SAA has 40 working days to investigate.
  - If rejected, the party may appeal to the Panel within a further 20 WD.
  - Successful disputes trigger a re-run or offset payment.

Distinct from:
  - bsc_settlement_run_register.py: tracks run outcomes and adjustments
  - settlement_reconciler.py: reconciliation of meter reads to settlement
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


def _add_working_days(date: dt.date, days: int) -> dt.date:
    current = date
    added = 0
    while added < days:
        current += dt.timedelta(days=1)
        if current.weekday() < 5:
            added += 1
    return current


class DisputeGround(str, Enum):
    METER_READ_ERROR = "meter_read_error"
    WRONG_BM_UNIT = "wrong_bm_unit"
    LLF_ERROR = "llf_error"
    PROFILE_CLASS_ERROR = "profile_class_error"
    DATA_COLLECTION_FAILURE = "data_collection_failure"
    CALCULATION_ERROR = "calculation_error"
    DUPLICATE_VOLUME = "duplicate_volume"


class SQStatus(str, Enum):
    RAISED = "raised"
    UNDER_INVESTIGATION = "under_investigation"
    UPHELD = "upheld"
    REJECTED = "rejected"
    APPEALED = "appealed"
    APPEAL_UPHELD = "appeal_upheld"
    APPEAL_REJECTED = "appeal_rejected"
    WITHDRAWN = "withdrawn"


_OPEN = frozenset({SQStatus.RAISED, SQStatus.UNDER_INVESTIGATION, SQStatus.APPEALED})
_UPHELD = frozenset({SQStatus.UPHELD, SQStatus.APPEAL_UPHELD})
_TERMINAL = frozenset({
    SQStatus.UPHELD, SQStatus.REJECTED, SQStatus.APPEAL_UPHELD,
    SQStatus.APPEAL_REJECTED, SQStatus.WITHDRAWN
})

# BSC SLA windows
_SQ_RAISE_WD = 20         # must raise within 20WD of settlement run
_SAA_INVESTIGATE_WD = 40  # SAA has 40WD to investigate
_APPEAL_WD = 20           # party has 20WD to appeal after rejection


@dataclass(frozen=True)
class SettlementDisputeRecord:
    dispute_id: str
    settlement_date: dt.date       # the settlement date being disputed
    run_type: str                  # SF/R1/R2/R3/RF
    ground: DisputeGround
    claimed_error_gwh: float       # absolute error in GWh
    financial_impact_gbp: float    # estimated financial impact
    raised_date: dt.date
    status: SQStatus
    investigation_start_date: Optional[dt.date] = None
    resolution_date: Optional[dt.date] = None
    recovery_amount_gbp: float = 0.0  # amount recovered if upheld
    appeal_date: Optional[dt.date] = None

    @property
    def is_open(self) -> bool:
        return self.status in _OPEN

    @property
    def is_upheld(self) -> bool:
        return self.status in _UPHELD

    @property
    def raise_deadline(self) -> dt.date:
        return _add_working_days(self.raised_date - dt.timedelta(days=1), _SQ_RAISE_WD)

    @property
    def saa_response_due(self) -> Optional[dt.date]:
        if self.investigation_start_date is None:
            return None
        return _add_working_days(self.investigation_start_date, _SAA_INVESTIGATE_WD)

    def is_saa_response_overdue(self, as_of: dt.date) -> bool:
        due = self.saa_response_due
        if due is None:
            return False
        return self.status == SQStatus.UNDER_INVESTIGATION and as_of > due

    def dispute_summary(self) -> str:
        parts = [
            f"SQ {self.dispute_id}: {self.settlement_date} {self.run_type} "
            f"{self.ground.value} {self.claimed_error_gwh:.3f}GWh "
            f"GBP{self.financial_impact_gbp:,.0f} [{self.status.value}]"
        ]
        if self.recovery_amount_gbp:
            parts.append(f"recovered=GBP{self.recovery_amount_gbp:,.0f}")
        return " | ".join(parts)


class BSCSettlementDisputeRegister:
    """Register of Settlement Queries raised against Elexon settlement runs."""

    def __init__(self) -> None:
        self._records: List[SettlementDisputeRecord] = []
        self._counter: int = 0

    def _next_id(self) -> str:
        self._counter += 1
        return "SQ-" + str(self._counter).zfill(5)

    def _update(self, dispute_id: str, **kwargs) -> SettlementDisputeRecord:
        for i, rec in enumerate(self._records):
            if rec.dispute_id == dispute_id:
                updated = SettlementDisputeRecord(**{**rec.__dict__, **kwargs})
                self._records[i] = updated
                return updated
        raise KeyError(f"Dispute not found: {dispute_id}")

    def _get(self, dispute_id: str) -> SettlementDisputeRecord:
        rec = next((r for r in self._records if r.dispute_id == dispute_id), None)
        if rec is None:
            raise KeyError(f"Dispute not found: {dispute_id}")
        return rec

    def raise_dispute(
        self,
        settlement_date: dt.date,
        run_type: str,
        ground: DisputeGround,
        claimed_error_gwh: float,
        financial_impact_gbp: float,
        raised_date: dt.date,
    ) -> SettlementDisputeRecord:
        if claimed_error_gwh <= 0:
            raise ValueError("claimed_error_gwh must be positive")
        if financial_impact_gbp < 0:
            raise ValueError("financial_impact_gbp cannot be negative")
        rec = SettlementDisputeRecord(
            dispute_id=self._next_id(),
            settlement_date=settlement_date,
            run_type=run_type,
            ground=ground,
            claimed_error_gwh=claimed_error_gwh,
            financial_impact_gbp=financial_impact_gbp,
            raised_date=raised_date,
            status=SQStatus.RAISED,
        )
        self._records.append(rec)
        return rec

    def start_investigation(
        self, dispute_id: str, investigation_start_date: dt.date
    ) -> SettlementDisputeRecord:
        rec = self._get(dispute_id)
        if rec.status != SQStatus.RAISED:
            raise ValueError(f"Cannot start investigation on {rec.status.value} dispute")
        return self._update(dispute_id, status=SQStatus.UNDER_INVESTIGATION,
                            investigation_start_date=investigation_start_date)

    def uphold(
        self, dispute_id: str, resolution_date: dt.date, recovery_amount_gbp: float
    ) -> SettlementDisputeRecord:
        rec = self._get(dispute_id)
        if rec.status not in (SQStatus.UNDER_INVESTIGATION, SQStatus.APPEALED):
            raise ValueError(f"Cannot uphold {rec.status.value} dispute")
        if recovery_amount_gbp < 0:
            raise ValueError("recovery_amount_gbp cannot be negative")
        return self._update(dispute_id, status=SQStatus.UPHELD,
                            resolution_date=resolution_date,
                            recovery_amount_gbp=recovery_amount_gbp)

    def reject(
        self, dispute_id: str, resolution_date: dt.date
    ) -> SettlementDisputeRecord:
        rec = self._get(dispute_id)
        if rec.status != SQStatus.UNDER_INVESTIGATION:
            raise ValueError(f"Cannot reject {rec.status.value} dispute")
        return self._update(dispute_id, status=SQStatus.REJECTED,
                            resolution_date=resolution_date)

    def appeal(
        self, dispute_id: str, appeal_date: dt.date
    ) -> SettlementDisputeRecord:
        rec = self._get(dispute_id)
        if rec.status != SQStatus.REJECTED:
            raise ValueError(f"Cannot appeal {rec.status.value} dispute")
        return self._update(dispute_id, status=SQStatus.APPEALED,
                            appeal_date=appeal_date)

    def uphold_appeal(
        self, dispute_id: str, resolution_date: dt.date, recovery_amount_gbp: float
    ) -> SettlementDisputeRecord:
        rec = self._get(dispute_id)
        if rec.status != SQStatus.APPEALED:
            raise ValueError(f"Cannot uphold appeal on {rec.status.value} dispute")
        if recovery_amount_gbp < 0:
            raise ValueError("recovery_amount_gbp cannot be negative")
        return self._update(dispute_id, status=SQStatus.APPEAL_UPHELD,
                            resolution_date=resolution_date,
                            recovery_amount_gbp=recovery_amount_gbp)

    def reject_appeal(
        self, dispute_id: str, resolution_date: dt.date
    ) -> SettlementDisputeRecord:
        rec = self._get(dispute_id)
        if rec.status != SQStatus.APPEALED:
            raise ValueError(f"Cannot reject appeal on {rec.status.value} dispute")
        return self._update(dispute_id, status=SQStatus.APPEAL_REJECTED,
                            resolution_date=resolution_date)

    def withdraw(self, dispute_id: str) -> SettlementDisputeRecord:
        rec = self._get(dispute_id)
        if rec.status not in _OPEN:
            raise ValueError(f"Cannot withdraw {rec.status.value} dispute")
        return self._update(dispute_id, status=SQStatus.WITHDRAWN)

    # ── Queries ──────────────────────────────────────────────────────────────

    @property
    def all_records(self) -> List[SettlementDisputeRecord]:
        return list(self._records)

    @property
    def open_disputes(self) -> List[SettlementDisputeRecord]:
        return [r for r in self._records if r.is_open]

    @property
    def upheld_disputes(self) -> List[SettlementDisputeRecord]:
        return [r for r in self._records if r.is_upheld]

    def overdue_saa_responses(self, as_of: dt.date) -> List[SettlementDisputeRecord]:
        return [r for r in self._records if r.is_saa_response_overdue(as_of)]

    def by_ground(self, ground: DisputeGround) -> List[SettlementDisputeRecord]:
        return [r for r in self._records if r.ground == ground]

    def by_run_type(self, run_type: str) -> List[SettlementDisputeRecord]:
        return [r for r in self._records if r.run_type == run_type]

    @property
    def total_financial_impact_gbp(self) -> float:
        return sum(r.financial_impact_gbp for r in self._records if r.is_open)

    @property
    def total_recovered_gbp(self) -> float:
        return sum(r.recovery_amount_gbp for r in self._records if r.is_upheld)

    def uphold_rate_pct(self) -> Optional[float]:
        decided = [r for r in self._records if r.status in _TERMINAL - {SQStatus.WITHDRAWN}]
        if not decided:
            return None
        return 100.0 * sum(1 for r in decided if r.is_upheld) / len(decided)

    def dispute_register_summary(self) -> str:
        total = len(self._records)
        open_count = len(self.open_disputes)
        upheld = len(self.upheld_disputes)
        total_impact = self.total_financial_impact_gbp
        recovered = self.total_recovered_gbp
        return (
            f"Settlement Disputes: {total} total | {open_count} open "
            f"| {upheld} upheld "
            f"| GBP{total_impact:,.0f} open exposure "
            f"| GBP{recovered:,.0f} recovered"
        )
