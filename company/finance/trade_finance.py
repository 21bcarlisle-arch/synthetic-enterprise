"""Trade finance instrument registry: letters of credit, bank guarantees, parent guarantees."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class InstrumentType(str, Enum):
    LETTER_OF_CREDIT = 'letter_of_credit'
    BANK_GUARANTEE = 'bank_guarantee'
    PARENT_GUARANTEE = 'parent_guarantee'
    SURETY_BOND = 'surety_bond'
    CASH_DEPOSIT = 'cash_deposit'


class InstrumentStatus(str, Enum):
    ACTIVE = 'active'
    EXPIRING_SOON = 'expiring_soon'  # within 30 days
    EXPIRED = 'expired'
    CALLED = 'called'
    CANCELLED = 'cancelled'


@dataclass
class CreditInstrument:
    instrument_id: str
    customer_id: str
    instrument_type: InstrumentType
    issuer: str
    face_value_gbp: float
    issue_date: dt.date
    expiry_date: dt.date
    status: InstrumentStatus = InstrumentStatus.ACTIVE
    call_date: Optional[dt.date] = None
    call_amount_gbp: Optional[float] = None

    def days_to_expiry(self, as_of: dt.date) -> int:
        return (self.expiry_date - as_of).days

    def refresh_status(self, as_of: dt.date) -> None:
        if self.status in (InstrumentStatus.CALLED, InstrumentStatus.CANCELLED):
            return
        days = self.days_to_expiry(as_of)
        if days < 0:
            self.status = InstrumentStatus.EXPIRED
        elif days <= 30:
            self.status = InstrumentStatus.EXPIRING_SOON
        else:
            self.status = InstrumentStatus.ACTIVE

    def call(self, call_date: dt.date, amount_gbp: float) -> None:
        self.call_date = call_date
        self.call_amount_gbp = amount_gbp
        self.status = InstrumentStatus.CALLED


class TradeFinanceLedger:
    def __init__(self) -> None:
        self._instruments: List[CreditInstrument] = []

    def register(self, instrument_id: str, customer_id: str,
                   instrument_type: InstrumentType, issuer: str,
                   face_value_gbp: float, issue_date: dt.date,
                   expiry_date: dt.date) -> CreditInstrument:
        inst = CreditInstrument(
            instrument_id=instrument_id, customer_id=customer_id,
            instrument_type=instrument_type, issuer=issuer,
            face_value_gbp=face_value_gbp, issue_date=issue_date,
            expiry_date=expiry_date,
        )
        self._instruments.append(inst)
        return inst

    def get(self, instrument_id: str) -> Optional[CreditInstrument]:
        return next((i for i in self._instruments if i.instrument_id == instrument_id), None)

    def call_instrument(self, instrument_id: str, call_date: dt.date,
                          amount_gbp: float) -> None:
        inst = self.get(instrument_id)
        if inst:
            inst.call(call_date, amount_gbp)

    def total_credit_support_gbp(self, customer_id: str, as_of: dt.date) -> float:
        total = 0.0
        for inst in self._instruments:
            if inst.customer_id != customer_id:
                continue
            inst.refresh_status(as_of)
            if inst.status == InstrumentStatus.ACTIVE:
                total += inst.face_value_gbp
        return round(total, 2)

    def expiring_within(self, as_of: dt.date, days: int) -> List[CreditInstrument]:
        result = []
        for inst in self._instruments:
            inst.refresh_status(as_of)
            if inst.status in (InstrumentStatus.ACTIVE, InstrumentStatus.EXPIRING_SOON):
                if 0 <= inst.days_to_expiry(as_of) <= days:
                    result.append(inst)
        return result

    def instruments_by_type(self, as_of: dt.date) -> Dict[str, float]:
        result: Dict[str, float] = {}
        for inst in self._instruments:
            inst.refresh_status(as_of)
            if inst.status in (InstrumentStatus.ACTIVE, InstrumentStatus.EXPIRING_SOON):
                k = inst.instrument_type.value
                result[k] = round(result.get(k, 0.0) + inst.face_value_gbp, 2)
        return result

    def portfolio_summary(self, as_of: dt.date) -> dict:
        active = [i for i in self._instruments
                  if i.status not in (InstrumentStatus.EXPIRED, InstrumentStatus.CALLED,
                                       InstrumentStatus.CANCELLED)]
        for i in active:
            i.refresh_status(as_of)
        return {
            'total_instruments': len(self._instruments),
            'active_count': len([i for i in self._instruments
                                  if i.status == InstrumentStatus.ACTIVE]),
            'expiring_soon': len(self.expiring_within(as_of, 30)),
            'total_coverage_gbp': sum(
                i.face_value_gbp for i in self._instruments
                if i.status in (InstrumentStatus.ACTIVE, InstrumentStatus.EXPIRING_SOON)
            ),
            'by_type': self.instruments_by_type(as_of),
        }
