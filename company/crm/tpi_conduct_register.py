"""TPI Conduct Compliance Register (Phase GY).

Third-party intermediaries (TPIs) — energy brokers, aggregators, and
comparison sites — act on behalf of I&C customers to arrange supply.
Suppliers using TPIs must monitor TPI conduct and report misconduct.

TPI regulatory framework:
  Ofgem TPI Code 2021: requires TPIs to be transparent, honest, fair
  SMICR (Micro Business): Ofgem rules on micro business sales practices
  SLC 14 (indirect): suppliers share responsibility for TPI mis-selling
  Ofgem consultation 2022-24: formal TPI licensing under consideration

TPI misconduct categories:
  MIS_SELLING: false claims about tariff, contract terms, or savings
  EXCESSIVE_COMMISSION: undisclosed or disproportionate commission
  DATA_MISUSE: customer data shared without consent
  PRESSURE_SELLING: high-pressure sales tactics (SLC 14 / Consumer Duty)
  CONTRACT_FORGERY: contract signed without customer knowledge/consent
  CHERRY_PICKING: presenting only selected tariffs, hiding cheaper options

Supplier obligations on misconduct:
  1. Investigate complaint within 10 working days
  2. Notify Ofgem if systemic misconduct (repeat complaints)
  3. May suspend or terminate TPI relationship
  4. Must keep records for 6 years (Ofgem audit risk)

Distinct from: tpi_commission_book.py (financial arrangements),
marketing_campaign_register.py (campaign tracking).
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

_INVESTIGATION_DAYS = 10


class TPIMisconductType(str, Enum):
    MIS_SELLING = "mis_selling"
    EXCESSIVE_COMMISSION = "excessive_commission"
    DATA_MISUSE = "data_misuse"
    PRESSURE_SELLING = "pressure_selling"
    CONTRACT_FORGERY = "contract_forgery"
    CHERRY_PICKING = "cherry_picking"
    OTHER = "other"


class TPIComplaintStatus(str, Enum):
    RECEIVED = "received"
    UNDER_INVESTIGATION = "under_investigation"
    UPHELD = "upheld"
    NOT_UPHELD = "not_upheld"
    ESCALATED_OFGEM = "escalated_ofgem"
    CLOSED = "closed"


class TPISanction(str, Enum):
    NONE = "none"
    WARNING_ISSUED = "warning_issued"
    RELATIONSHIP_SUSPENDED = "relationship_suspended"
    RELATIONSHIP_TERMINATED = "relationship_terminated"
    REPORTED_TO_OFGEM = "reported_to_ofgem"


_OPEN = frozenset({TPIComplaintStatus.RECEIVED, TPIComplaintStatus.UNDER_INVESTIGATION})
_TERMINAL = frozenset({
    TPIComplaintStatus.UPHELD, TPIComplaintStatus.NOT_UPHELD,
    TPIComplaintStatus.ESCALATED_OFGEM, TPIComplaintStatus.CLOSED,
})
_SERIOUS = frozenset({TPIMisconductType.CONTRACT_FORGERY, TPIMisconductType.DATA_MISUSE})


@dataclass(frozen=True)
class TPIComplaintRecord:
    complaint_id: str
    tpi_id: str
    customer_account_id: str
    received_date: dt.date
    misconduct_type: TPIMisconductType
    status: TPIComplaintStatus = TPIComplaintStatus.RECEIVED
    sanction: TPISanction = TPISanction.NONE
    investigation_date: Optional[dt.date] = None
    resolution_date: Optional[dt.date] = None
    customer_remedy_gbp: float = 0.0
    notes: str = ""

    @property
    def investigation_due(self) -> dt.date:
        return self.received_date + dt.timedelta(days=_INVESTIGATION_DAYS)

    def is_overdue(self, as_of: dt.date) -> bool:
        return self.status in _OPEN and as_of > self.investigation_due

    @property
    def is_serious(self) -> bool:
        return self.misconduct_type in _SERIOUS

    @property
    def is_open(self) -> bool:
        return self.status in _OPEN

    def complaint_summary(self) -> str:
        return (
            "TPI Complaint " + self.complaint_id + " tpi=" + self.tpi_id
            + " [" + self.misconduct_type.value + "/" + self.status.value + "]"
        )


class TPIConductRegister:

    def __init__(self) -> None:
        self._records: List[TPIComplaintRecord] = []
        self._counter: int = 0

    def _next_id(self) -> str:
        self._counter += 1
        return "TPIC-" + str(self._counter).zfill(5)

    def receive_complaint(
        self,
        tpi_id: str,
        customer_account_id: str,
        received_date: dt.date,
        misconduct_type: TPIMisconductType,
        notes: str = "",
    ) -> TPIComplaintRecord:
        record = TPIComplaintRecord(
            complaint_id=self._next_id(), tpi_id=tpi_id,
            customer_account_id=customer_account_id, received_date=received_date,
            misconduct_type=misconduct_type, notes=notes,
        )
        self._records.append(record)
        return record

    def _update(self, complaint_id: str, **kwargs) -> TPIComplaintRecord:
        for i, r in enumerate(self._records):
            if r.complaint_id == complaint_id:
                updated = TPIComplaintRecord(
                    complaint_id=r.complaint_id, tpi_id=r.tpi_id,
                    customer_account_id=r.customer_account_id,
                    received_date=r.received_date, misconduct_type=r.misconduct_type,
                    status=kwargs.get("status", r.status),
                    sanction=kwargs.get("sanction", r.sanction),
                    investigation_date=kwargs.get("investigation_date", r.investigation_date),
                    resolution_date=kwargs.get("resolution_date", r.resolution_date),
                    customer_remedy_gbp=kwargs.get("customer_remedy_gbp", r.customer_remedy_gbp),
                    notes=kwargs.get("notes", r.notes),
                )
                self._records[i] = updated
                return updated
        raise KeyError("TPI complaint " + complaint_id + " not found")

    def start_investigation(self, complaint_id: str, investigation_date: dt.date) -> TPIComplaintRecord:
        return self._update(complaint_id, status=TPIComplaintStatus.UNDER_INVESTIGATION,
                            investigation_date=investigation_date)

    def uphold(
        self, complaint_id: str, resolution_date: dt.date,
        sanction: TPISanction, customer_remedy_gbp: float = 0.0,
    ) -> TPIComplaintRecord:
        return self._update(complaint_id, status=TPIComplaintStatus.UPHELD,
                            resolution_date=resolution_date, sanction=sanction,
                            customer_remedy_gbp=customer_remedy_gbp)

    def not_uphold(self, complaint_id: str, resolution_date: dt.date) -> TPIComplaintRecord:
        return self._update(complaint_id, status=TPIComplaintStatus.NOT_UPHELD,
                            resolution_date=resolution_date)

    def escalate_to_ofgem(self, complaint_id: str) -> TPIComplaintRecord:
        return self._update(complaint_id, status=TPIComplaintStatus.ESCALATED_OFGEM,
                            sanction=TPISanction.REPORTED_TO_OFGEM)

    def open_complaints(self) -> List[TPIComplaintRecord]:
        return [r for r in self._records if r.is_open]

    def overdue_investigations(self, as_of: dt.date) -> List[TPIComplaintRecord]:
        return [r for r in self._records if r.is_overdue(as_of)]

    def complaints_for_tpi(self, tpi_id: str) -> List[TPIComplaintRecord]:
        return [r for r in self._records if r.tpi_id == tpi_id]

    def serious_complaints(self) -> List[TPIComplaintRecord]:
        return [r for r in self._records if r.is_serious]

    def upheld_complaints(self) -> List[TPIComplaintRecord]:
        return [r for r in self._records if r.status == TPIComplaintStatus.UPHELD]

    def uphold_rate_pct(self) -> Optional[float]:
        terminal = [r for r in self._records if r.status in _TERMINAL]
        if not terminal:
            return None
        upheld = sum(1 for r in terminal if r.status == TPIComplaintStatus.UPHELD)
        return round(upheld / len(terminal) * 100, 1)

    def total_customer_remedy_gbp(self) -> float:
        return sum(r.customer_remedy_gbp for r in self._records
                   if r.status == TPIComplaintStatus.UPHELD)

    def tpis_with_repeat_complaints(self, threshold: int = 3) -> List[str]:
        from collections import Counter
        counts = Counter(r.tpi_id for r in self._records)
        return [tpi_id for tpi_id, count in counts.items() if count >= threshold]

    def conduct_summary(self, as_of: dt.date) -> str:
        n = len(self._records)
        n_open = len(self.open_complaints())
        n_overdue = len(self.overdue_investigations(as_of))
        n_serious = len(self.serious_complaints())
        return (
            "TPI Conduct Register (" + str(as_of) + "): "
            + str(n) + " complaints ("
            + str(n_open) + " open, " + str(n_overdue) + " overdue, "
            + str(n_serious) + " serious)."
        )
