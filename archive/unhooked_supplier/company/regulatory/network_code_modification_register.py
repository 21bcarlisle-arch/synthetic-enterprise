"""Network Code Modification Register (Phase GU).

The UK energy industry operates under a set of legally binding codes
(BSC, UNC, REC, DCUSA, SEC, MRA) that govern how the market operates.
Modifications to these codes are proposed, consulted on, and voted on
by industry parties including suppliers.

Supplier obligations:
  1. Monitor active modifications via the relevant code administrator
  2. Participate in consultation for modifications with material impact
  3. Vote at ballot (for significant modifications)
  4. Implement required system/process changes by the effective date
  5. Track approved modifications awaiting implementation

Key codes:
  BSC (Balancing and Settlement Code): Elexon; settlement, imbalance
  UNC (Uniform Network Code): Xoserve; gas transportation
  REC (Retail Energy Code): Gemserv; switching, data flows, smart
  DCUSA (Distribution Connection and Use of System Agreement): DNOs
  SEC (Smart Energy Code): DCC; SMETS2 communications
  MRA (Master Registration Agreement): meter registration (legacy)

Impact assessment categories:
  HIGH/CRITICAL: system changes required, IT/ops spend, deadline risk
  MEDIUM: process changes, staff training
  LOW/NONE: monitoring only

Distinct from: slc_compliance_tracker.py (SLC obligations),
remit_book.py (REMIT compliance), bsc_settlement_run_register.py.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

_IMPLEMENTATION_WARNING_DAYS = 90


class IndustryCode(str, Enum):
    BSC = "bsc"
    UNC = "unc"
    REC = "rec"
    DCUSA = "dcusa"
    SEC = "sec"
    MRA = "mra"


class ModificationStatus(str, Enum):
    RAISED = "raised"
    CONSULTATION = "consultation"
    BALLOT = "ballot"
    IMPLEMENTATION_DATE_SET = "implementation_date_set"
    IMPLEMENTED = "implemented"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class ImpactLevel(str, Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class BallotPosition(str, Enum):
    SUPPORT = "support"
    OPPOSE = "oppose"
    ABSTAIN = "abstain"
    NOT_VOTED = "not_voted"
    NOT_ELIGIBLE = "not_eligible"


_ACTIVE = frozenset({
    ModificationStatus.RAISED, ModificationStatus.CONSULTATION,
    ModificationStatus.BALLOT, ModificationStatus.IMPLEMENTATION_DATE_SET,
})
_TERMINAL = frozenset({
    ModificationStatus.IMPLEMENTED, ModificationStatus.REJECTED,
    ModificationStatus.WITHDRAWN,
})
_HIGH_IMPACT = frozenset({ImpactLevel.HIGH, ImpactLevel.CRITICAL})


@dataclass(frozen=True)
class NetworkCodeModificationRecord:
    record_id: str
    code: IndustryCode
    modification_ref: str
    short_title: str
    raised_date: dt.date
    status: ModificationStatus = ModificationStatus.RAISED
    impact_level: ImpactLevel = ImpactLevel.NONE
    ballot_position: BallotPosition = BallotPosition.NOT_ELIGIBLE
    implementation_date: Optional[dt.date] = None
    implemented_date: Optional[dt.date] = None
    notes: str = ""

    @property
    def is_active(self) -> bool:
        return self.status in _ACTIVE

    @property
    def is_high_impact(self) -> bool:
        return self.impact_level in _HIGH_IMPACT

    def is_implementation_due_soon(self, as_of: dt.date) -> bool:
        if self.implementation_date is None:
            return False
        if not self.is_active:
            return False
        return (self.implementation_date - as_of).days <= _IMPLEMENTATION_WARNING_DAYS

    def days_to_implementation(self, as_of: dt.date) -> Optional[int]:
        if self.implementation_date is None:
            return None
        return (self.implementation_date - as_of).days

    def modification_summary(self) -> str:
        return (
            "Mod " + self.record_id + " [" + self.code.value + "] "
            + self.modification_ref + ": " + self.short_title
            + " [" + self.impact_level.value + "/" + self.status.value + "]"
        )


class NetworkCodeModificationRegister:

    def __init__(self) -> None:
        self._records: List[NetworkCodeModificationRecord] = []
        self._counter: int = 0

    def _next_id(self) -> str:
        self._counter += 1
        return "NCM-" + str(self._counter).zfill(5)

    def track_modification(
        self,
        code: IndustryCode,
        modification_ref: str,
        short_title: str,
        raised_date: dt.date,
        notes: str = "",
    ) -> NetworkCodeModificationRecord:
        record = NetworkCodeModificationRecord(
            record_id=self._next_id(),
            code=code, modification_ref=modification_ref,
            short_title=short_title, raised_date=raised_date, notes=notes,
        )
        self._records.append(record)
        return record

    def _update(self, record_id: str, **kwargs) -> NetworkCodeModificationRecord:
        for i, r in enumerate(self._records):
            if r.record_id == record_id:
                updated = NetworkCodeModificationRecord(
                    record_id=r.record_id, code=r.code,
                    modification_ref=r.modification_ref, short_title=r.short_title,
                    raised_date=r.raised_date,
                    status=kwargs.get("status", r.status),
                    impact_level=kwargs.get("impact_level", r.impact_level),
                    ballot_position=kwargs.get("ballot_position", r.ballot_position),
                    implementation_date=kwargs.get("implementation_date", r.implementation_date),
                    implemented_date=kwargs.get("implemented_date", r.implemented_date),
                    notes=kwargs.get("notes", r.notes),
                )
                self._records[i] = updated
                return updated
        raise KeyError("Modification " + record_id + " not found")

    def assess_impact(self, record_id: str, impact_level: ImpactLevel) -> NetworkCodeModificationRecord:
        return self._update(record_id, impact_level=impact_level)

    def record_ballot_position(
        self, record_id: str, position: BallotPosition,
    ) -> NetworkCodeModificationRecord:
        return self._update(record_id, status=ModificationStatus.BALLOT,
                            ballot_position=position)

    def set_implementation_date(
        self, record_id: str, implementation_date: dt.date,
    ) -> NetworkCodeModificationRecord:
        return self._update(record_id, status=ModificationStatus.IMPLEMENTATION_DATE_SET,
                            implementation_date=implementation_date)

    def mark_implemented(self, record_id: str, implemented_date: dt.date) -> NetworkCodeModificationRecord:
        return self._update(record_id, status=ModificationStatus.IMPLEMENTED,
                            implemented_date=implemented_date)

    def reject(self, record_id: str) -> NetworkCodeModificationRecord:
        return self._update(record_id, status=ModificationStatus.REJECTED)

    def active_modifications(self) -> List[NetworkCodeModificationRecord]:
        return [r for r in self._records if r.is_active]

    def high_impact(self) -> List[NetworkCodeModificationRecord]:
        return [r for r in self._records if r.is_high_impact and r.is_active]

    def due_soon(self, as_of: dt.date) -> List[NetworkCodeModificationRecord]:
        return [r for r in self._records if r.is_implementation_due_soon(as_of)]

    def by_code(self, code: IndustryCode) -> List[NetworkCodeModificationRecord]:
        return [r for r in self._records if r.code == code]

    def pending_ballot(self) -> List[NetworkCodeModificationRecord]:
        return [r for r in self._records if r.status == ModificationStatus.BALLOT]

    def modification_summary(self, as_of: dt.date) -> str:
        n = len(self._records)
        n_active = len(self.active_modifications())
        n_high = len(self.high_impact())
        n_due = len(self.due_soon(as_of))
        return (
            "Network Code Modification Register (" + str(as_of) + "): "
            + str(n) + " modifications ("
            + str(n_active) + " active, "
            + str(n_high) + " high-impact, "
            + str(n_due) + " due within 90d)."
        )
