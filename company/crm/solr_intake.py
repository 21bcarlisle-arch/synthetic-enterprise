from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class SoLRIntakeStatus(str, Enum):
    NOTIFIED = 'notified'
    CONTACTED = 'contacted'
    ONBOARDED = 'onboarded'
    SWITCHED_AWAY = 'switched_away'
    UNRESPONSIVE = 'unresponsive'


@dataclass(frozen=True)
class SoLRBatch:
    batch_id: str
    failed_supplier: str
    appointment_date: dt.date
    customer_count: int
    deemed_tariff_rate_pct_above_cap: float

    @property
    def is_priced_above_cap(self) -> bool:
        return self.deemed_tariff_rate_pct_above_cap > 0


@dataclass
class SoLRCustomer:
    customer_id: str
    batch_id: str
    mpan: str
    segment: str
    status: SoLRIntakeStatus = SoLRIntakeStatus.NOTIFIED
    contacted_date: Optional[dt.date] = None
    onboarded_date: Optional[dt.date] = None
    switched_away_date: Optional[dt.date] = None

    @property
    def is_retained(self) -> bool:
        return self.status == SoLRIntakeStatus.ONBOARDED

    @property
    def days_to_contact(self) -> Optional[int]:
        if self.contacted_date is None:
            return None
        batch = None
        return None


class SoLRBook:
    def __init__(self, our_supplier_id: str) -> None:
        self._supplier_id = our_supplier_id
        self._batches: dict[str, SoLRBatch] = {}
        self._customers: list[SoLRCustomer] = []

    def register_batch(self, batch_id: str, failed_supplier: str,
                       appointment_date: dt.date, customer_count: int,
                       deemed_tariff_rate_pct_above_cap: float = 0.0) -> SoLRBatch:
        batch = SoLRBatch(
            batch_id=batch_id, failed_supplier=failed_supplier,
            appointment_date=appointment_date, customer_count=customer_count,
            deemed_tariff_rate_pct_above_cap=deemed_tariff_rate_pct_above_cap,
        )
        self._batches[batch_id] = batch
        return batch

    def add_customer(self, customer_id: str, batch_id: str, mpan: str,
                     segment: str) -> SoLRCustomer:
        cust = SoLRCustomer(
            customer_id=customer_id, batch_id=batch_id,
            mpan=mpan, segment=segment,
        )
        self._customers.append(cust)
        return cust

    def _get_customer(self, customer_id: str) -> SoLRCustomer:
        for c in self._customers:
            if c.customer_id == customer_id:
                return c
        raise KeyError(customer_id)

    def mark_contacted(self, customer_id: str, contacted_date: dt.date) -> SoLRCustomer:
        c = self._get_customer(customer_id)
        c.status = SoLRIntakeStatus.CONTACTED
        c.contacted_date = contacted_date
        return c

    def mark_onboarded(self, customer_id: str, onboarded_date: dt.date) -> SoLRCustomer:
        c = self._get_customer(customer_id)
        c.status = SoLRIntakeStatus.ONBOARDED
        c.onboarded_date = onboarded_date
        return c

    def mark_switched_away(self, customer_id: str, switch_date: dt.date) -> SoLRCustomer:
        c = self._get_customer(customer_id)
        c.status = SoLRIntakeStatus.SWITCHED_AWAY
        c.switched_away_date = switch_date
        return c

    def customers_in_batch(self, batch_id: str) -> List[SoLRCustomer]:
        return [c for c in self._customers if c.batch_id == batch_id]

    def retention_rate(self, batch_id: str) -> float:
        batch_custs = self.customers_in_batch(batch_id)
        if not batch_custs:
            return 0.0
        retained = sum(1 for c in batch_custs if c.is_retained)
        return round(retained / len(batch_custs) * 100, 1)

    def contact_rate(self, batch_id: str) -> float:
        batch_custs = self.customers_in_batch(batch_id)
        if not batch_custs:
            return 0.0
        contacted = sum(1 for c in batch_custs
                        if c.status != SoLRIntakeStatus.NOTIFIED)
        return round(contacted / len(batch_custs) * 100, 1)

    def batch_summary(self, batch_id: str) -> dict:
        batch = self._batches[batch_id]
        custs = self.customers_in_batch(batch_id)
        by_status: dict[str, int] = {}
        for c in custs:
            by_status[c.status.value] = by_status.get(c.status.value, 0) + 1
        return {
            'batch_id': batch_id,
            'failed_supplier': batch.failed_supplier,
            'appointment_date': str(batch.appointment_date),
            'declared_customer_count': batch.customer_count,
            'actual_customers_received': len(custs),
            'retention_rate_pct': self.retention_rate(batch_id),
            'contact_rate_pct': self.contact_rate(batch_id),
            'by_status': by_status,
        }
