from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

_DNO_RESPONSE_DAYS = 28


class DUoSDisputeGround(str, Enum):
    WRONG_LLFC = "wrong_llfc"
    WRONG_PC = "wrong_pc"
    METERING_ERROR = "metering_error"
    MISAPPLIED_DISCOUNT = "misapplied_discount"
    CALCULATION_ERROR = "calculation_error"
    CHARGE_PERIOD_ERROR = "charge_period_error"


class DUoSDisputeStatus(str, Enum):
    RAISED = "raised"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED_CREDIT = "resolved_credit"
    RESOLVED_NO_CREDIT = "resolved_no_credit"
    ESCALATED_GEMA = "escalated_gema"
    WITHDRAWN = "withdrawn"


_OPEN = frozenset({DUoSDisputeStatus.RAISED, DUoSDisputeStatus.ACKNOWLEDGED})
_RESOLVED = frozenset({
    DUoSDisputeStatus.RESOLVED_CREDIT,
    DUoSDisputeStatus.RESOLVED_NO_CREDIT,
    DUoSDisputeStatus.WITHDRAWN,
})


@dataclass(frozen=True)
class DUoSDisputeRecord:
    dispute_id: str
    mpan: str
    dno_code: str
    invoice_ref: str
    raised_date: dt.date
    ground: DUoSDisputeGround
    disputed_amount_gbp: float
    status: DUoSDisputeStatus = DUoSDisputeStatus.RAISED
    dno_response_date: Optional[dt.date] = None
    credit_received_gbp: float = 0.0
    resolution_date: Optional[dt.date] = None
    notes: str = ""

    @property
    def is_open(self) -> bool:
        return self.status in _OPEN

    @property
    def dno_response_due(self) -> dt.date:
        return self.raised_date + dt.timedelta(days=_DNO_RESPONSE_DAYS)

    def is_dno_response_overdue(self, as_of: dt.date) -> bool:
        return self.is_open and as_of > self.dno_response_due

    @property
    def outstanding_recovery_gbp(self) -> float:
        if self.status == DUoSDisputeStatus.RESOLVED_CREDIT:
            return max(0.0, self.disputed_amount_gbp - self.credit_received_gbp)
        if self.status in _RESOLVED:
            return 0.0
        return self.disputed_amount_gbp

    def dispute_summary(self) -> str:
        return (
            "DUoS " + self.dispute_id + " mpan=" + self.mpan
            + " dno=" + self.dno_code
            + " disputed=GBP" + str(round(self.disputed_amount_gbp, 2))
            + " [" + self.ground.value + "/" + self.status.value + "]"
        )


class DNONetworkChargeDisputeRegister:

    def __init__(self) -> None:
        self._records: List[DUoSDisputeRecord] = []
        self._counter: int = 0

    def _next_id(self) -> str:
        self._counter += 1
        return "DUOS-DISP-" + str(self._counter).zfill(5)

    def raise_dispute(
        self, mpan: str, dno_code: str, invoice_ref: str,
        raised_date: dt.date, ground: DUoSDisputeGround,
        disputed_amount_gbp: float, notes: str = "",
    ) -> DUoSDisputeRecord:
        if disputed_amount_gbp <= 0:
            raise ValueError("disputed_amount_gbp must be positive")
        record = DUoSDisputeRecord(
            dispute_id=self._next_id(),
            mpan=mpan, dno_code=dno_code, invoice_ref=invoice_ref,
            raised_date=raised_date, ground=ground,
            disputed_amount_gbp=disputed_amount_gbp, notes=notes,
        )
        self._records.append(record)
        return record

    def _update(self, dispute_id: str, **kwargs) -> DUoSDisputeRecord:
        for i, r in enumerate(self._records):
            if r.dispute_id == dispute_id:
                updated = DUoSDisputeRecord(
                    dispute_id=r.dispute_id, mpan=r.mpan, dno_code=r.dno_code,
                    invoice_ref=r.invoice_ref, raised_date=r.raised_date,
                    ground=r.ground, disputed_amount_gbp=r.disputed_amount_gbp,
                    status=kwargs.get("status", r.status),
                    dno_response_date=kwargs.get("dno_response_date", r.dno_response_date),
                    credit_received_gbp=kwargs.get("credit_received_gbp", r.credit_received_gbp),
                    resolution_date=kwargs.get("resolution_date", r.resolution_date),
                    notes=kwargs.get("notes", r.notes),
                )
                self._records[i] = updated
                return updated
        raise KeyError("DUoS dispute " + dispute_id + " not found")

    def acknowledge(self, dispute_id: str, response_date: dt.date) -> DUoSDisputeRecord:
        return self._update(dispute_id, status=DUoSDisputeStatus.ACKNOWLEDGED,
                            dno_response_date=response_date)

    def resolve_with_credit(
        self, dispute_id: str, credit_gbp: float, resolution_date: dt.date,
    ) -> DUoSDisputeRecord:
        return self._update(dispute_id, status=DUoSDisputeStatus.RESOLVED_CREDIT,
                            credit_received_gbp=credit_gbp, resolution_date=resolution_date)

    def resolve_no_credit(self, dispute_id: str, resolution_date: dt.date) -> DUoSDisputeRecord:
        return self._update(dispute_id, status=DUoSDisputeStatus.RESOLVED_NO_CREDIT,
                            resolution_date=resolution_date)

    def escalate_gema(self, dispute_id: str) -> DUoSDisputeRecord:
        return self._update(dispute_id, status=DUoSDisputeStatus.ESCALATED_GEMA)

    def withdraw(self, dispute_id: str) -> DUoSDisputeRecord:
        return self._update(dispute_id, status=DUoSDisputeStatus.WITHDRAWN)

    def open_disputes(self) -> List[DUoSDisputeRecord]:
        return [r for r in self._records if r.is_open]

    def overdue_dno_responses(self, as_of: dt.date) -> List[DUoSDisputeRecord]:
        return [r for r in self._records if r.is_dno_response_overdue(as_of)]

    def by_dno(self, dno_code: str) -> List[DUoSDisputeRecord]:
        return [r for r in self._records if r.dno_code == dno_code]

    def by_ground(self, ground: DUoSDisputeGround) -> List[DUoSDisputeRecord]:
        return [r for r in self._records if r.ground == ground]

    def total_open_disputed_gbp(self) -> float:
        return sum(r.disputed_amount_gbp for r in self._records if r.is_open)

    def total_credits_received_gbp(self) -> float:
        return sum(r.credit_received_gbp for r in self._records)

    def success_rate_pct(self) -> Optional[float]:
        resolved = [r for r in self._records if r.status in _RESOLVED]
        if not resolved:
            return None
        credited = sum(1 for r in resolved if r.status == DUoSDisputeStatus.RESOLVED_CREDIT)
        return round(credited / len(resolved) * 100, 1)

    def duos_dispute_summary(self, as_of: dt.date) -> str:
        n = len(self._records)
        n_open = len(self.open_disputes())
        n_overdue = len(self.overdue_dno_responses(as_of))
        total_disp = round(self.total_open_disputed_gbp(), 2)
        return (
            "DUoS Dispute Register (" + str(as_of) + "): "
            + str(n) + " disputes ("
            + str(n_open) + " open, " + str(n_overdue) + " overdue). "
            + "Open disputed: GBP" + str(total_disp) + "."
        )
