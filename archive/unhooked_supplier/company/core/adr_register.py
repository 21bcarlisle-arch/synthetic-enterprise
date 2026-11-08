"""Architectural Decision Record (ADR) Register (Phase EE).

The CTO Architecture Guidance mandates: "For every structural architectural
decision, write a brief Architectural Decision Record in docs/architecture/.
State the context (what failure mode triggered this?), the proposed fix,
and the trade-offs accepted. This becomes the permanent record of why the
system is shaped the way it is."

This module manages the ADR registry: tracking, numbering, and querying
decisions that have shaped the architecture. ADRs are immutable once accepted
(they record history, not current state).

ADR Status lifecycle: PROPOSED → ACCEPTED → DEPRECATED (if superseded)
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class ADRStatus(str, Enum):
    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    DEPRECATED = "deprecated"      # superseded by later ADR
    REJECTED = "rejected"


class ADRCategory(str, Enum):
    EPISTEMIC_AIR_GAP = "epistemic_air_gap"
    EVENT_DRIVEN = "event_driven"
    DATA_ARCHITECTURE = "data_architecture"
    MODULE_SEAM = "module_seam"
    BEHAVIORAL_PHYSICS = "behavioral_physics"
    COMPLIANCE = "compliance"
    TESTING = "testing"
    INFRASTRUCTURE = "infrastructure"


@dataclass(frozen=True)
class ArchitecturalDecisionRecord:
    adr_id: str                       # ADR-NNN format
    title: str
    category: ADRCategory
    status: ADRStatus
    decided_at: dt.date
    context: str                      # what failure mode or need triggered this?
    decision: str                     # what we decided to do
    consequences: str                 # trade-offs accepted
    superseded_by: Optional[str] = None

    @property
    def is_active(self) -> bool:
        return self.status == ADRStatus.ACCEPTED

    @property
    def is_superseded(self) -> bool:
        return self.status == ADRStatus.DEPRECATED and self.superseded_by is not None


class ADRRegister:
    """Registry of all Architectural Decision Records."""

    def __init__(self) -> None:
        self._adrs: Dict[str, ArchitecturalDecisionRecord] = {}
        self._next_id = 1

    def _auto_id(self) -> str:
        adr_id = f"ADR-{self._next_id:03d}"
        self._next_id += 1
        return adr_id

    def record(
        self,
        title: str,
        category: ADRCategory,
        decided_at: dt.date,
        context: str,
        decision: str,
        consequences: str,
        status: ADRStatus = ADRStatus.ACCEPTED,
        adr_id: Optional[str] = None,
    ) -> ArchitecturalDecisionRecord:
        if adr_id is None:
            adr_id = self._auto_id()
        adr = ArchitecturalDecisionRecord(
            adr_id=adr_id,
            title=title,
            category=category,
            status=status,
            decided_at=decided_at,
            context=context,
            decision=decision,
            consequences=consequences,
        )
        self._adrs[adr_id] = adr
        return adr

    def deprecate(self, adr_id: str, superseded_by: str) -> Optional[ArchitecturalDecisionRecord]:
        adr = self._adrs.get(adr_id)
        if adr is None:
            return None
        import dataclasses
        updated = dataclasses.replace(
            adr,
            status=ADRStatus.DEPRECATED,
            superseded_by=superseded_by,
        )
        self._adrs[adr_id] = updated
        return updated

    def get(self, adr_id: str) -> Optional[ArchitecturalDecisionRecord]:
        return self._adrs.get(adr_id)

    def all_adrs(self) -> List[ArchitecturalDecisionRecord]:
        return list(self._adrs.values())

    def active_adrs(self) -> List[ArchitecturalDecisionRecord]:
        return [a for a in self._adrs.values() if a.is_active]

    def by_category(self, category: ADRCategory) -> List[ArchitecturalDecisionRecord]:
        return [a for a in self._adrs.values() if a.category == category]

    def adr_summary(self) -> str:
        n = len(self._adrs)
        n_active = len(self.active_adrs())
        categories = {a.category for a in self._adrs.values()}
        return (
            f"ADR Register: {n} total records, {n_active} active. "
            f"{len(categories)} categories. "
            f"CTO mandate: ADR required for every structural architectural decision."
        )
