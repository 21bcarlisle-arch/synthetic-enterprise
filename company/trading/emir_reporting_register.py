"""EMIR Trade Repository Reporting Register.

UK EMIR (retained via SI 2019/335) requires reporting of OTC/ETD commodity
derivatives to an FCA-authorised trade repository within T+1 working days.

Key rules:
- Dual-sided reporting: both counterparties report independently
- Unique Trade Identifier (UTI): agreed between counterparties pre-report
- LEI (Legal Entity Identifier): both sides must hold valid LEI
- Deadline: T+1 working day of execution (FCA EMIR Art.9)
- Late reporting is a breach; FCA fine up to GBP 7.2M

Epistemic: company knows trades it executed and their reporting status.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class CounterpartyType(str, Enum):
    FINANCIAL_COUNTERPARTY = "fc"
    NON_FINANCIAL_COUNTERPARTY = "nfc"
    NON_FINANCIAL_COUNTERPARTY_PLUS = "nfc_plus"


class ReportingStatus(str, Enum):
    PENDING = "pending"
    REPORTED = "reported"
    LATE_REPORTED = "late_reported"
    AMENDED = "amended"
    CANCELLED = "cancelled"
    FAILED = "failed"


class ProductType(str, Enum):
    ELECTRICITY_FORWARD = "elec_forward"
    GAS_FORWARD = "gas_forward"
    ELECTRICITY_OPTION = "elec_option"
    GAS_OPTION = "gas_option"
    ELECTRICITY_SWAP = "elec_swap"


_FCA_EMIR_MAX_FINE_GBP = 7_200_000.0


def _add_working_days(from_dt: dt.datetime, days: int) -> dt.datetime:
    d = from_dt.date()
    added = 0
    while added < days:
        d += dt.timedelta(days=1)
        if d.weekday() < 5:
            added += 1
    return dt.datetime(d.year, d.month, d.day, 17, 0, 0, tzinfo=from_dt.tzinfo)


@dataclass(frozen=True)
class EMIRTradeRecord:
    trade_id: str
    uti: str
    product_type: ProductType
    counterparty_id: str
    counterparty_type: CounterpartyType
    counterparty_lei: str
    our_lei: str
    notional_gbp: float
    price_gbp_per_mwh: float
    delivery_start: dt.date
    delivery_end: dt.date
    execution_date: dt.date
    reporting_deadline: dt.datetime
    status: ReportingStatus
    reported_at: Optional[dt.datetime] = None
    trade_repository_ref: Optional[str] = None
    amendment_reason: Optional[str] = None

    @property
    def is_reported(self) -> bool:
        return self.status in (ReportingStatus.REPORTED, ReportingStatus.LATE_REPORTED,
                               ReportingStatus.AMENDED, ReportingStatus.CANCELLED)

    @property
    def is_late(self) -> bool:
        if self.reported_at is None:
            return False
        return self.reported_at > self.reporting_deadline

    def is_overdue(self, as_of: dt.datetime) -> bool:
        if self.is_reported:
            return False
        return as_of > self.reporting_deadline and self.status == ReportingStatus.PENDING

class EMIRReportingRegister:
    """Central register for EMIR trade reporting obligations."""

    def __init__(self, our_lei: str = "213800SYNTH00000001") -> None:
        self._trades: Dict[str, EMIRTradeRecord] = {}
        self._our_lei = our_lei
        self._seq = 0

    def _next_id(self) -> str:
        self._seq += 1
        return f"TRD-{self._seq:05d}"

    def _make_uti(self, trade_id: str, execution_date: dt.date) -> str:
        return f"GB{self._our_lei[:6]}{execution_date.strftime("%Y%m%d")}{trade_id}"

    def record_trade(
        self,
        product_type: ProductType,
        counterparty_id: str,
        counterparty_type: CounterpartyType,
        counterparty_lei: str,
        notional_gbp: float,
        price_gbp_per_mwh: float,
        delivery_start: dt.date,
        delivery_end: dt.date,
        execution_date: dt.date,
    ) -> EMIRTradeRecord:
        tid = self._next_id()
        uti = self._make_uti(tid, execution_date)
        exec_dt = dt.datetime.combine(execution_date, dt.time(9, 0), tzinfo=dt.timezone.utc)
        deadline = _add_working_days(exec_dt, 1)
        rec = EMIRTradeRecord(
            trade_id=tid, uti=uti, product_type=product_type,
            counterparty_id=counterparty_id, counterparty_type=counterparty_type,
            counterparty_lei=counterparty_lei, our_lei=self._our_lei,
            notional_gbp=notional_gbp, price_gbp_per_mwh=price_gbp_per_mwh,
            delivery_start=delivery_start, delivery_end=delivery_end,
            execution_date=execution_date, reporting_deadline=deadline,
            status=ReportingStatus.PENDING,
        )
        self._trades[tid] = rec
        return rec

    def _replace(self, rec: EMIRTradeRecord, **kwargs) -> EMIRTradeRecord:
        fields = {
            "trade_id": rec.trade_id, "uti": rec.uti, "product_type": rec.product_type,
            "counterparty_id": rec.counterparty_id, "counterparty_type": rec.counterparty_type,
            "counterparty_lei": rec.counterparty_lei, "our_lei": rec.our_lei,
            "notional_gbp": rec.notional_gbp, "price_gbp_per_mwh": rec.price_gbp_per_mwh,
            "delivery_start": rec.delivery_start, "delivery_end": rec.delivery_end,
            "execution_date": rec.execution_date, "reporting_deadline": rec.reporting_deadline,
            "status": rec.status, "reported_at": rec.reported_at,
            "trade_repository_ref": rec.trade_repository_ref,
            "amendment_reason": rec.amendment_reason,
        }
        fields.update(kwargs)
        return EMIRTradeRecord(**fields)

    def report(
        self, trade_id: str, reported_at: dt.datetime,
        trade_repository_ref: Optional[str] = None,
    ) -> EMIRTradeRecord:
        rec = self._trades[trade_id]
        is_late = reported_at > rec.reporting_deadline
        status = ReportingStatus.LATE_REPORTED if is_late else ReportingStatus.REPORTED
        updated = self._replace(rec, status=status, reported_at=reported_at,
                                 trade_repository_ref=trade_repository_ref)
        self._trades[trade_id] = updated
        return updated

    def amend(self, trade_id: str, reported_at: dt.datetime, reason: str) -> EMIRTradeRecord:
        rec = self._trades[trade_id]
        updated = self._replace(rec, status=ReportingStatus.AMENDED,
                                 reported_at=reported_at, amendment_reason=reason)
        self._trades[trade_id] = updated
        return updated

    def cancel(self, trade_id: str, reported_at: dt.datetime) -> EMIRTradeRecord:
        rec = self._trades[trade_id]
        updated = self._replace(rec, status=ReportingStatus.CANCELLED,
                                 reported_at=reported_at)
        self._trades[trade_id] = updated
        return updated

    def mark_failed(self, trade_id: str) -> EMIRTradeRecord:
        rec = self._trades[trade_id]
        updated = self._replace(rec, status=ReportingStatus.FAILED)
        self._trades[trade_id] = updated
        return updated

    def overdue(self, as_of: dt.datetime) -> List[EMIRTradeRecord]:
        return [t for t in self._trades.values() if t.is_overdue(as_of)]

    def pending(self) -> List[EMIRTradeRecord]:
        return [t for t in self._trades.values() if t.status == ReportingStatus.PENDING]

    def late_reports(self) -> List[EMIRTradeRecord]:
        return [t for t in self._trades.values() if t.is_late]

    def failed_reports(self) -> List[EMIRTradeRecord]:
        return [t for t in self._trades.values() if t.status == ReportingStatus.FAILED]

    def by_product(self) -> Dict[str, int]:
        out: Dict[str, int] = {}
        for t in self._trades.values():
            out[t.product_type.value] = out.get(t.product_type.value, 0) + 1
        return out

    @property
    def total_notional_gbp(self) -> float:
        return sum(t.notional_gbp for t in self._trades.values()
                   if t.status != ReportingStatus.CANCELLED)

    @property
    def reporting_compliance_rate(self) -> float:
        reported = [t for t in self._trades.values() if t.is_reported]
        total = len(self._trades)
        return len(reported) / total if total else 1.0

    def emir_reporting_summary(self) -> str:
        total = len(self._trades)
        pend = len(self.pending())
        late = len(self.late_reports())
        failed = len(self.failed_reports())
        notional = self.total_notional_gbp
        rate = self.reporting_compliance_rate
        by_prod = self.by_product()
        return (
            f"EMIR Reporting: {total} trades, {pend} pending, {late} late, {failed} failed. "
            f"Compliance: {rate:.1%}. Notional: GBP{notional:,.0f}. Products: {by_prod}."
        )
