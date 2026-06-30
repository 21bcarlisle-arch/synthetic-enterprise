"""MPAS Standing Data Correction Register.

MPAS (Meter Point Administration Service) holds standing data for each supply
point: Profile Class (PC), SSC, MTC, LLFC, Measurement Class. Errors cause
incorrect billing and settlement discrepancies. Suppliers submit D0019 flows
to correct errors; MPAS must respond within defined SLAs (2 WD acknowledge,
10 WD resolve).

Distinct from mpas_registry.py (registrations/gain/loss) and llf_register.py
(LLF values for calculation).
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


class StandingDataField(str, Enum):
    PROFILE_CLASS = "profile_class"
    SSC = "ssc"
    MTC = "mtc"
    LLFC = "llfc"
    MEASUREMENT_CLASS = "measurement_class"
    DA_ID = "da_id"
    DC_ID = "dc_id"
    DISTRIBUTOR_ID = "distributor_id"


_SETTLEMENT_IMPACTING = frozenset({
    StandingDataField.PROFILE_CLASS,
    StandingDataField.LLFC,
    StandingDataField.SSC,
    StandingDataField.MEASUREMENT_CLASS,
})

_ACK_WORKING_DAYS = 2
_RESOLUTION_WORKING_DAYS = 10


class CorrectionStatus(str, Enum):
    RAISED = "raised"
    ACKNOWLEDGED = "acknowledged"
    APPLIED = "applied"
    REJECTED = "rejected"
    ESCALATED = "escalated"


_OPEN = frozenset({CorrectionStatus.RAISED, CorrectionStatus.ACKNOWLEDGED})


@dataclass(frozen=True)
class MPASCorrectionRecord:
    correction_id: str
    mpan: str
    account_id: str
    field: StandingDataField
    current_value: str
    correct_value: str
    raised_date: dt.date
    status: CorrectionStatus
    acknowledgement_date: Optional[dt.date] = None
    applied_date: Optional[dt.date] = None
    rejected_reason: Optional[str] = None
    financial_impact_gbp: Optional[float] = None

    @property
    def is_open(self) -> bool:
        return self.status in _OPEN

    @property
    def is_settlement_impacting(self) -> bool:
        return self.field in _SETTLEMENT_IMPACTING

    @property
    def acknowledgement_due(self) -> dt.date:
        return _add_working_days(self.raised_date, _ACK_WORKING_DAYS)

    @property
    def resolution_due(self) -> Optional[dt.date]:
        if self.acknowledgement_date is None:
            return None
        return _add_working_days(self.acknowledgement_date, _RESOLUTION_WORKING_DAYS)

    def is_acknowledgement_overdue(self, as_of: dt.date) -> bool:
        return self.status == CorrectionStatus.RAISED and as_of > self.acknowledgement_due

    def is_resolution_overdue(self, as_of: dt.date) -> bool:
        if self.status != CorrectionStatus.ACKNOWLEDGED:
            return False
        rd = self.resolution_due
        return rd is not None and as_of > rd

    def correction_summary(self) -> str:
        parts = [
            f"MPAS-COR {self.correction_id}: {self.mpan} "
            f"{self.field.value} [{self.current_value}->{self.correct_value}] "
            f"[{self.status.value}]"
        ]
        if self.financial_impact_gbp is not None:
            parts.append(f"impact=GBP{self.financial_impact_gbp:,.2f}")
        return " | ".join(parts)


class MPASStandingDataCorrectionRegister:
    """Register of formal MPAS standing data correction requests (D0019 flows)."""

    def __init__(self) -> None:
        self._records: List[MPASCorrectionRecord] = []
        self._counter: int = 0

    def _next_id(self) -> str:
        self._counter += 1
        return "MPAS-COR-" + str(self._counter).zfill(5)

    def _update(self, correction_id: str, **kwargs) -> MPASCorrectionRecord:
        for i, rec in enumerate(self._records):
            if rec.correction_id == correction_id:
                updated = MPASCorrectionRecord(**{**rec.__dict__, **kwargs})
                self._records[i] = updated
                return updated
        raise KeyError(f"Correction not found: {correction_id}")

    def raise_correction(
        self,
        mpan: str,
        account_id: str,
        field: StandingDataField,
        current_value: str,
        correct_value: str,
        raised_date: dt.date,
        financial_impact_gbp: Optional[float] = None,
    ) -> MPASCorrectionRecord:
        if current_value == correct_value:
            raise ValueError("current_value and correct_value must differ")
        rec = MPASCorrectionRecord(
            correction_id=self._next_id(),
            mpan=mpan,
            account_id=account_id,
            field=field,
            current_value=current_value,
            correct_value=correct_value,
            raised_date=raised_date,
            status=CorrectionStatus.RAISED,
            financial_impact_gbp=financial_impact_gbp,
        )
        self._records.append(rec)
        return rec

    def acknowledge(self, correction_id: str, acknowledgement_date: dt.date) -> MPASCorrectionRecord:
        rec = next((r for r in self._records if r.correction_id == correction_id), None)
        if rec is None:
            raise KeyError(f"Correction not found: {correction_id}")
        if rec.status != CorrectionStatus.RAISED:
            raise ValueError(f"Cannot acknowledge {rec.status.value} correction")
        return self._update(correction_id, status=CorrectionStatus.ACKNOWLEDGED,
                            acknowledgement_date=acknowledgement_date)

    def apply(self, correction_id: str, applied_date: dt.date) -> MPASCorrectionRecord:
        rec = next((r for r in self._records if r.correction_id == correction_id), None)
        if rec is None:
            raise KeyError(f"Correction not found: {correction_id}")
        if rec.status not in _OPEN:
            raise ValueError(f"Cannot apply {rec.status.value} correction")
        return self._update(correction_id, status=CorrectionStatus.APPLIED, applied_date=applied_date)

    def reject(self, correction_id: str, reason: str) -> MPASCorrectionRecord:
        rec = next((r for r in self._records if r.correction_id == correction_id), None)
        if rec is None:
            raise KeyError(f"Correction not found: {correction_id}")
        if rec.status not in _OPEN:
            raise ValueError(f"Cannot reject {rec.status.value} correction")
        return self._update(correction_id, status=CorrectionStatus.REJECTED, rejected_reason=reason)

    def escalate(self, correction_id: str) -> MPASCorrectionRecord:
        rec = next((r for r in self._records if r.correction_id == correction_id), None)
        if rec is None:
            raise KeyError(f"Correction not found: {correction_id}")
        if rec.status not in _OPEN:
            raise ValueError(f"Cannot escalate {rec.status.value} correction")
        return self._update(correction_id, status=CorrectionStatus.ESCALATED)

    @property
    def all_records(self) -> List[MPASCorrectionRecord]:
        return list(self._records)

    @property
    def open_corrections(self) -> List[MPASCorrectionRecord]:
        return [r for r in self._records if r.is_open]

    def overdue_acknowledgements(self, as_of: dt.date) -> List[MPASCorrectionRecord]:
        return [r for r in self._records if r.is_acknowledgement_overdue(as_of)]

    def overdue_resolutions(self, as_of: dt.date) -> List[MPASCorrectionRecord]:
        return [r for r in self._records if r.is_resolution_overdue(as_of)]

    def corrections_for_account(self, account_id: str) -> List[MPASCorrectionRecord]:
        return [r for r in self._records if r.account_id == account_id]

    def corrections_for_mpan(self, mpan: str) -> List[MPASCorrectionRecord]:
        return [r for r in self._records if r.mpan == mpan]

    def by_field(self, field: StandingDataField) -> List[MPASCorrectionRecord]:
        return [r for r in self._records if r.field == field]

    def by_status(self, status: CorrectionStatus) -> List[MPASCorrectionRecord]:
        return [r for r in self._records if r.status == status]

    @property
    def settlement_impacting_corrections(self) -> List[MPASCorrectionRecord]:
        return [r for r in self._records if r.is_settlement_impacting and r.is_open]

    @property
    def total_financial_impact_gbp(self) -> float:
        return sum(
            r.financial_impact_gbp
            for r in self._records
            if r.is_open and r.financial_impact_gbp is not None
        )

    def correction_register_summary(self, as_of: dt.date) -> str:
        total = len(self._records)
        open_count = len(self.open_corrections)
        overdue_ack = len(self.overdue_acknowledgements(as_of))
        overdue_res = len(self.overdue_resolutions(as_of))
        settlement = len(self.settlement_impacting_corrections)
        impact = self.total_financial_impact_gbp
        return (
            f"MPAS Corrections: {total} total | {open_count} open "
            f"| {overdue_ack} overdue ack | {overdue_res} overdue resolution "
            f"| {settlement} settlement-impacting open "
            f"| GBP{impact:,.2f} financial impact"
        )
