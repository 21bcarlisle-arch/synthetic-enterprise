"""Switching cooling-off and objection management: 14-day right, ET resolution."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


COOLING_OFF_DAYS = 14
OBJECTION_WINDOW_DAYS = 15


class ObjectionReason(str, Enum):
    DEBT = 'debt'
    CONTRACT_IN_TERM = 'contract_in_term'
    CUSTOMER_REQUEST = 'customer_request'
    IDENTITY_MISMATCH = 'identity_mismatch'


class ObjectionOutcome(str, Enum):
    UPHELD = 'upheld'
    REJECTED = 'rejected'
    WITHDRAWN = 'withdrawn'


class ErroneousTransferStatus(str, Enum):
    REPORTED = 'reported'
    UNDER_INVESTIGATION = 'under_investigation'
    CUSTOMER_RETURNED = 'customer_returned'
    CLOSED_NO_ACTION = 'closed_no_action'


@dataclass(frozen=True)
class CoolingOffCancellation:
    customer_id: str
    mpan: str
    sale_date: dt.date
    cancellation_date: dt.date

    @property
    def days_after_sale(self) -> int:
        return (self.cancellation_date - self.sale_date).days

    @property
    def within_cooling_off(self) -> bool:
        return self.days_after_sale <= COOLING_OFF_DAYS


@dataclass
class SwitchObjection:
    objection_id: str
    mpan: str
    objecting_supplier_id: str
    switch_requested_date: dt.date
    objection_date: dt.date
    reason: ObjectionReason
    outcome: Optional[ObjectionOutcome] = None
    outcome_date: Optional[dt.date] = None

    @property
    def within_objection_window(self) -> bool:
        return (self.objection_date - self.switch_requested_date).days <= OBJECTION_WINDOW_DAYS

    @property
    def is_resolved(self) -> bool:
        return self.outcome is not None


@dataclass
class ErroneousTransfer:
    et_id: str
    mpan: str
    losing_supplier_id: str
    gaining_supplier_id: str
    transfer_date: dt.date
    reported_date: dt.date
    status: ErroneousTransferStatus = ErroneousTransferStatus.REPORTED
    resolution_date: Optional[dt.date] = None

    @property
    def days_to_report(self) -> int:
        return (self.reported_date - self.transfer_date).days

    @property
    def is_resolved(self) -> bool:
        return self.status in {
            ErroneousTransferStatus.CUSTOMER_RETURNED,
            ErroneousTransferStatus.CLOSED_NO_ACTION,
        }


class SwitchGovernanceBook:
    def __init__(self) -> None:
        self._cancellations: List[CoolingOffCancellation] = []
        self._objections: dict[str, SwitchObjection] = {}
        self._ets: dict[str, ErroneousTransfer] = {}
        self._next_obj = 1
        self._next_et = 1

    def record_cancellation(self, customer_id: str, mpan: str,
                             sale_date: dt.date, cancellation_date: dt.date
                             ) -> CoolingOffCancellation:
        c = CoolingOffCancellation(customer_id=customer_id, mpan=mpan,
                                    sale_date=sale_date, cancellation_date=cancellation_date)
        self._cancellations.append(c)
        return c

    def raise_objection(self, mpan: str, objecting_supplier_id: str,
                         switch_requested_date: dt.date, objection_date: dt.date,
                         reason: ObjectionReason) -> SwitchObjection:
        oid = f'OBJ-{self._next_obj:04d}'
        self._next_obj += 1
        obj = SwitchObjection(
            objection_id=oid, mpan=mpan, objecting_supplier_id=objecting_supplier_id,
            switch_requested_date=switch_requested_date, objection_date=objection_date,
            reason=reason,
        )
        self._objections[oid] = obj
        return obj

    def resolve_objection(self, objection_id: str, outcome: ObjectionOutcome,
                           outcome_date: dt.date) -> None:
        obj = self._objections[objection_id]
        obj.outcome = outcome
        obj.outcome_date = outcome_date

    def report_et(self, mpan: str, losing_supplier_id: str, gaining_supplier_id: str,
                   transfer_date: dt.date, reported_date: dt.date) -> ErroneousTransfer:
        et_id = f'ET-{self._next_et:04d}'
        self._next_et += 1
        et = ErroneousTransfer(
            et_id=et_id, mpan=mpan, losing_supplier_id=losing_supplier_id,
            gaining_supplier_id=gaining_supplier_id, transfer_date=transfer_date,
            reported_date=reported_date,
        )
        self._ets[et_id] = et
        return et

    def resolve_et(self, et_id: str, status: ErroneousTransferStatus,
                    resolution_date: dt.date) -> None:
        et = self._ets[et_id]
        et.status = status
        et.resolution_date = resolution_date

    def cancellations_in_cooling_off(self) -> int:
        return sum(1 for c in self._cancellations if c.within_cooling_off)

    def open_objections(self) -> List[SwitchObjection]:
        return [o for o in self._objections.values() if not o.is_resolved]

    def open_ets(self) -> List[ErroneousTransfer]:
        return [e for e in self._ets.values() if not e.is_resolved]

    def annual_summary(self, year: int) -> dict:
        yr_cancellations = [c for c in self._cancellations
                             if c.cancellation_date.year == year]
        yr_objections = [o for o in self._objections.values()
                          if o.objection_date.year == year]
        yr_ets = [e for e in self._ets.values() if e.reported_date.year == year]
        return {
            'year': year,
            'cooling_off_cancellations': len(yr_cancellations),
            'cooling_off_rate_pct': round(
                sum(1 for c in yr_cancellations if c.within_cooling_off)
                / max(1, len(yr_cancellations)) * 100, 1
            ),
            'objections_raised': len(yr_objections),
            'objections_upheld': sum(1 for o in yr_objections if o.outcome == ObjectionOutcome.UPHELD),
            'erroneous_transfers': len(yr_ets),
            'ets_resolved': sum(1 for e in yr_ets if e.is_resolved),
        }
