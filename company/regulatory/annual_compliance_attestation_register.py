"""Annual Compliance Attestation Register (Phase GM).

Annual self-reporting of SLC compliance to Ofgem. Since 2022,
suppliers must submit an Annual Compliance Statement (ACS) covering
all SLCs within 3 months of financial year end, signed by a director.
Distinct from slc_compliance_tracker.py (day-to-day observations).
"""
from __future__ import annotations
import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple

_QUERY_RESPONSE_WD = 20


class AttestationStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    ACKNOWLEDGED = "acknowledged"
    QUERIED = "queried"
    SUPERSEDED = "superseded"


class AttestationOutcome(str, Enum):
    COMPLIANT = "compliant"
    COMPLIANT_WITH_MITIGATIONS = "compliant_with_mitigations"
    MINOR_BREACH = "minor_breach"
    MATERIAL_BREACH = "material_breach"


_BREACH = frozenset({AttestationOutcome.MINOR_BREACH, AttestationOutcome.MATERIAL_BREACH})


def _add_wd(start: dt.date, n: int) -> dt.date:
    cur = start
    added = 0
    while added < n:
        cur += dt.timedelta(days=1)
        if cur.weekday() < 5:
            added += 1
    return cur


@dataclass(frozen=True)
class SLCAttestationRecord:
    record_id: str
    slc_reference: str
    assessment_year: int
    period_start: dt.date
    period_end: dt.date
    outcome: AttestationOutcome
    status: AttestationStatus = AttestationStatus.DRAFT
    evidence_refs: Tuple[str, ...] = ()
    submission_date: Optional[dt.date] = None
    ofgem_ref: Optional[str] = None
    query_date: Optional[dt.date] = None
    query_response_due: Optional[dt.date] = None
    notes: str = ""

    @property
    def is_submitted(self) -> bool:
        return self.status in (AttestationStatus.SUBMITTED, AttestationStatus.ACKNOWLEDGED)

    @property
    def is_breach(self) -> bool:
        return self.outcome in _BREACH

    @property
    def is_material_breach(self) -> bool:
        return self.outcome == AttestationOutcome.MATERIAL_BREACH

    @property
    def is_queried(self) -> bool:
        return self.status == AttestationStatus.QUERIED

    def attestation_summary(self) -> str:
        return (
            "ATTEST " + self.record_id + " SLC=" + self.slc_reference
            + " year=" + str(self.assessment_year)
            + " [" + self.outcome.value + "/" + self.status.value + "]"
        )


class AnnualComplianceAttestationRegister:

    def __init__(self) -> None:
        self._records: List[SLCAttestationRecord] = []
        self._counter: int = 0

    def _next_id(self) -> str:
        self._counter += 1
        return "ATTEST-" + str(self._counter).zfill(5)

    def create_attestation(
        self, slc_reference: str, assessment_year: int,
        period_start: dt.date, period_end: dt.date,
        outcome: AttestationOutcome,
        evidence_refs: Tuple[str, ...] = (), notes: str = "",
    ) -> SLCAttestationRecord:
        if period_end <= period_start:
            raise ValueError("period_end must be after period_start")
        record = SLCAttestationRecord(
            record_id=self._next_id(), slc_reference=slc_reference,
            assessment_year=assessment_year, period_start=period_start,
            period_end=period_end, outcome=outcome,
            evidence_refs=evidence_refs, notes=notes,
        )
        self._records.append(record)
        return record

    def _update(self, record_id: str, **kwargs) -> SLCAttestationRecord:
        for i, r in enumerate(self._records):
            if r.record_id == record_id:
                updated = SLCAttestationRecord(
                    record_id=r.record_id, slc_reference=r.slc_reference,
                    assessment_year=r.assessment_year, period_start=r.period_start,
                    period_end=r.period_end,
                    outcome=kwargs.get("outcome", r.outcome),
                    status=kwargs.get("status", r.status),
                    evidence_refs=kwargs.get("evidence_refs", r.evidence_refs),
                    submission_date=kwargs.get("submission_date", r.submission_date),
                    ofgem_ref=kwargs.get("ofgem_ref", r.ofgem_ref),
                    query_date=kwargs.get("query_date", r.query_date),
                    query_response_due=kwargs.get("query_response_due", r.query_response_due),
                    notes=kwargs.get("notes", r.notes),
                )
                self._records[i] = updated
                return updated
        raise KeyError("Attestation record " + record_id + " not found")

    def submit(self, record_id: str, submission_date: dt.date, ofgem_ref: Optional[str] = None) -> SLCAttestationRecord:
        return self._update(record_id, status=AttestationStatus.SUBMITTED,
                           submission_date=submission_date, ofgem_ref=ofgem_ref)

    def mark_acknowledged(self, record_id: str) -> SLCAttestationRecord:
        return self._update(record_id, status=AttestationStatus.ACKNOWLEDGED)

    def mark_queried(self, record_id: str, query_date: dt.date) -> SLCAttestationRecord:
        return self._update(record_id, status=AttestationStatus.QUERIED,
                           query_date=query_date,
                           query_response_due=_add_wd(query_date, _QUERY_RESPONSE_WD))

    def supersede(self, record_id: str) -> SLCAttestationRecord:
        return self._update(record_id, status=AttestationStatus.SUPERSEDED)

    def for_year(self, year: int) -> List[SLCAttestationRecord]:
        return [r for r in self._records if r.assessment_year == year]

    def for_slc(self, slc_reference: str) -> List[SLCAttestationRecord]:
        return [r for r in self._records if r.slc_reference == slc_reference]

    def outstanding_queries(self) -> List[SLCAttestationRecord]:
        return [r for r in self._records if r.is_queried]

    def material_breaches(self) -> List[SLCAttestationRecord]:
        return [r for r in self._records if r.is_material_breach]

    def breaches(self) -> List[SLCAttestationRecord]:
        return [r for r in self._records if r.is_breach]

    def unsubmitted(self) -> List[SLCAttestationRecord]:
        return [r for r in self._records if r.status == AttestationStatus.DRAFT]

    def compliance_rate_pct(self, year: Optional[int] = None) -> Optional[float]:
        pool = self.for_year(year) if year is not None else list(self._records)
        if not pool:
            return None
        compliant = sum(1 for r in pool if not r.is_breach)
        return round(compliant / len(pool) * 100, 1)

    def attestation_summary(self, year: Optional[int] = None) -> str:
        pool = self.for_year(year) if year is not None else list(self._records)
        n = len(pool)
        n_breach = sum(1 for r in pool if r.is_breach)
        n_material = sum(1 for r in pool if r.is_material_breach)
        n_query = len(self.outstanding_queries())
        year_str = str(year) if year is not None else "all"
        return (
            "Compliance Attestation (" + year_str + "): "
            + str(n) + " attestations, "
            + str(n_breach) + " breaches ("
            + str(n_material) + " material), "
            + str(n_query) + " queries."
        )
