"""Agreed Capacity Register (Phase GS).

For half-hourly metered (HH) I&C customers, the agreed capacity (kVA)
determines the demand charge component of DUoS (Distribution Use of System).
Suppliers monitor and manage agreed capacity on behalf of I&C customers.

Agreed capacity mechanics:
  - DNOs assign an agreed capacity (kVA) per supply point
  - DUoS capacity charges are levied per kVA of agreed capacity
  - Exceeding agreed capacity triggers excess capacity charges (typically
    3x the standard rate for the excess kVA band)
  - Under-utilised capacity is wasted spend; over-capacity triggers penalties
  - Capacity may be reduced on 3 months notice; increases require DNO approval
  - Domestic customers do not have agreed capacity (fixed per-day DUoS)

Reduction rights (Engineering Recommendation P2/6):
  - Supplier or customer may apply for capacity reduction on 3 months notice
  - DNO must accept if metered demand supports the reduction
  - Reductions are permanent; increases require DNO assessment

Distinct from: duos_ledger.py (DUoS charges), llf_register.py (LLF),
interruptible_supply_register.py (interruptible supply agreements).
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

_REDUCTION_NOTICE_MONTHS = 3
_EXCESS_CAPACITY_MULTIPLIER = 3.0


class CapacityChangeType(str, Enum):
    INITIAL_REGISTRATION = "initial_registration"
    CUSTOMER_REDUCTION = "customer_reduction"
    CUSTOMER_INCREASE = "customer_increase"
    DNO_REVISION = "dno_revision"
    CORRECTION = "correction"


class CapacityChangeStatus(str, Enum):
    PENDING = "pending"
    APPLIED = "applied"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


@dataclass(frozen=True)
class AgreedCapacityRecord:
    record_id: str
    mpan: str
    dno_code: str
    effective_date: dt.date
    agreed_capacity_kva: float
    change_type: CapacityChangeType
    change_status: CapacityChangeStatus = CapacityChangeStatus.APPLIED
    previous_capacity_kva: Optional[float] = None
    applied_date: Optional[dt.date] = None
    notes: str = ""

    @property
    def is_applied(self) -> bool:
        return self.change_status == CapacityChangeStatus.APPLIED

    @property
    def capacity_change_kva(self) -> Optional[float]:
        if self.previous_capacity_kva is None:
            return None
        return round(self.agreed_capacity_kva - self.previous_capacity_kva, 2)

    @property
    def is_reduction(self) -> bool:
        chg = self.capacity_change_kva
        return chg is not None and chg < 0

    def excess_capacity_charge_multiplier(self) -> float:
        return _EXCESS_CAPACITY_MULTIPLIER

    def capacity_summary(self) -> str:
        return (
            "AgreedCap " + self.record_id + " mpan=" + self.mpan
            + " dno=" + self.dno_code
            + " capacity=" + str(self.agreed_capacity_kva) + "kVA"
            + " [" + self.change_type.value + "/" + self.change_status.value + "]"
        )


@dataclass(frozen=True)
class CapacityExceedanceRecord:
    exceedance_id: str
    mpan: str
    measurement_date: dt.date
    agreed_capacity_kva: float
    measured_demand_kva: float
    excess_kva: float
    dnos_rate_gbp_per_kva: float

    @property
    def excess_charge_gbp(self) -> float:
        return round(self.excess_kva * self.dnos_rate_gbp_per_kva * _EXCESS_CAPACITY_MULTIPLIER, 2)

    @property
    def utilisation_pct(self) -> float:
        if self.agreed_capacity_kva == 0:
            return 0.0
        return round(self.measured_demand_kva / self.agreed_capacity_kva * 100, 1)


class AgreedCapacityRegister:

    def __init__(self) -> None:
        self._records: List[AgreedCapacityRecord] = []
        self._exceedances: List[CapacityExceedanceRecord] = []
        self._counter: int = 0
        self._exc_counter: int = 0

    def _next_id(self) -> str:
        self._counter += 1
        return "AGCAP-" + str(self._counter).zfill(5)

    def _next_exc_id(self) -> str:
        self._exc_counter += 1
        return "AGCAP-EXC-" + str(self._exc_counter).zfill(5)

    def register_capacity(
        self,
        mpan: str,
        dno_code: str,
        effective_date: dt.date,
        agreed_capacity_kva: float,
        change_type: CapacityChangeType,
        previous_capacity_kva: Optional[float] = None,
        notes: str = "",
    ) -> AgreedCapacityRecord:
        if agreed_capacity_kva <= 0:
            raise ValueError("agreed_capacity_kva must be positive")
        record = AgreedCapacityRecord(
            record_id=self._next_id(), mpan=mpan, dno_code=dno_code,
            effective_date=effective_date, agreed_capacity_kva=agreed_capacity_kva,
            change_type=change_type, previous_capacity_kva=previous_capacity_kva,
            notes=notes,
        )
        self._records.append(record)
        return record

    def _update(self, record_id: str, **kwargs) -> AgreedCapacityRecord:
        for i, r in enumerate(self._records):
            if r.record_id == record_id:
                updated = AgreedCapacityRecord(
                    record_id=r.record_id, mpan=r.mpan, dno_code=r.dno_code,
                    effective_date=r.effective_date,
                    agreed_capacity_kva=r.agreed_capacity_kva,
                    change_type=r.change_type,
                    change_status=kwargs.get("change_status", r.change_status),
                    previous_capacity_kva=r.previous_capacity_kva,
                    applied_date=kwargs.get("applied_date", r.applied_date),
                    notes=kwargs.get("notes", r.notes),
                )
                self._records[i] = updated
                return updated
        raise KeyError("Capacity record " + record_id + " not found")

    def apply_change(self, record_id: str, applied_date: dt.date) -> AgreedCapacityRecord:
        return self._update(record_id, change_status=CapacityChangeStatus.APPLIED,
                            applied_date=applied_date)

    def reject_change(self, record_id: str) -> AgreedCapacityRecord:
        return self._update(record_id, change_status=CapacityChangeStatus.REJECTED)

    def record_exceedance(
        self,
        mpan: str,
        measurement_date: dt.date,
        agreed_capacity_kva: float,
        measured_demand_kva: float,
        dnos_rate_gbp_per_kva: float,
    ) -> CapacityExceedanceRecord:
        excess = max(0.0, measured_demand_kva - agreed_capacity_kva)
        if excess <= 0:
            raise ValueError("measured_demand_kva must exceed agreed_capacity_kva")
        record = CapacityExceedanceRecord(
            exceedance_id=self._next_exc_id(), mpan=mpan,
            measurement_date=measurement_date, agreed_capacity_kva=agreed_capacity_kva,
            measured_demand_kva=measured_demand_kva, excess_kva=round(excess, 2),
            dnos_rate_gbp_per_kva=dnos_rate_gbp_per_kva,
        )
        self._exceedances.append(record)
        return record

    def current_capacity_for(self, mpan: str) -> Optional[float]:
        candidates = [r for r in self._records if r.mpan == mpan and r.is_applied]
        if not candidates:
            return None
        return max(candidates, key=lambda r: r.effective_date).agreed_capacity_kva

    def exceedances_for(self, mpan: str) -> List[CapacityExceedanceRecord]:
        return [e for e in self._exceedances if e.mpan == mpan]

    def mpans_with_exceedances(self) -> List[str]:
        return list(dict.fromkeys(e.mpan for e in self._exceedances))

    def total_excess_charge_gbp(self) -> float:
        return round(sum(e.excess_charge_gbp for e in self._exceedances), 2)

    def reduction_candidates(self, as_of: dt.date) -> List[str]:
        seen = set()
        result = []
        for e in self._exceedances:
            if (as_of - e.measurement_date).days <= 90 and e.mpan not in seen:
                seen.add(e.mpan)
                result.append(e.mpan)
        return result

    def capacity_summary(self, as_of: dt.date) -> str:
        n_mpans = len({r.mpan for r in self._records if r.is_applied})
        n_exc = len(self._exceedances)
        total_exc = self.total_excess_charge_gbp()
        return (
            "Agreed Capacity Register (" + str(as_of) + "): "
            + str(n_mpans) + " supply points. "
            + str(n_exc) + " exceedances (GBP" + str(total_exc) + " excess charges)."
        )
