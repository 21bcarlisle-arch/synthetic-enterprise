"""Meter Asset Provider (MAP) Contract Register (Phase GJ).

Meter Asset Providers (MAPs) own, install, and maintain smart meters under
contract with energy suppliers. This is a UK-specific contractual structure:
smart meters (SMETS2) are not owned by suppliers or customers — they remain
the property of the MAP for the duration of the supply contract.

Key UK context:
  - The Code of Practice for Smart Metering (2012) defines the MAP role
  - MAPs register their meters with the DCC (Data Communications Company)
  - Meter rental is paid monthly by the supplier to the MAP
  - Installation, maintenance and exchange visits are charged separately
  - When a customer switches supplier, meter ownership stays with the MAP
  - Meter Operators (MOPs) are the pre-smart equivalent for legacy meters

Typical MAP charges (approximate industry values):
  - SMETS2 meter rental: ~£3-6/meter/month
  - SMETS2 new installation: ~£80-140/appointment
  - SMETS2-to-SMETS2 exchange: ~£60-100

Regulatory: MAP must register with Ofgem; comply with Smart Energy Code (SEC);
SEC requires 10-working-day window for DCC registration post-install.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class MAPServiceType(str, Enum):
    SMETS2_NEW_INSTALL = "smets2_new_install"
    SMETS2_EXCHANGE = "smets2_exchange"
    SMETS1_TO_SMETS2 = "smets1_to_smets2"
    EMERGENCY_REPLACEMENT = "emergency_replacement"
    PLANNED_MAINTENANCE = "planned_maintenance"
    LEGACY_MOP_SERVICE = "legacy_mop_service"
    METER_REMOVAL = "meter_removal"


class MAPContractStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    UNDER_RENEGOTIATION = "under_renegotiation"


@dataclass(frozen=True)
class MAPServiceRate:
    service_type: MAPServiceType
    unit_cost_gbp: float
    unit: str

    def annual_cost_estimate_gbp(self, volume: float) -> float:
        return round(self.unit_cost_gbp * volume, 2)


@dataclass(frozen=True)
class MAPContractRecord:
    contract_id: str
    provider_name: str
    contract_start: dt.date
    contract_end: dt.date
    meter_count_at_start: int
    monthly_rental_rate_gbp_per_meter: float
    service_rates: tuple
    status: MAPContractStatus = MAPContractStatus.ACTIVE
    termination_date: Optional[dt.date] = None

    @property
    def is_active(self) -> bool:
        return self.status == MAPContractStatus.ACTIVE

    def is_current_as_of(self, as_of: dt.date) -> bool:
        return self.contract_start <= as_of <= self.contract_end and self.is_active

    def months_remaining(self, as_of: dt.date) -> int:
        if as_of >= self.contract_end:
            return 0
        return max(0, (self.contract_end - as_of).days // 30)

    def monthly_rental_cost_gbp(self, meter_count: Optional[int] = None) -> float:
        count = meter_count if meter_count is not None else self.meter_count_at_start
        return round(self.monthly_rental_rate_gbp_per_meter * count, 2)

    def annual_rental_cost_gbp(self, meter_count: Optional[int] = None) -> float:
        return round(self.monthly_rental_cost_gbp(meter_count) * 12, 2)

    def service_rate_for(self, service_type: MAPServiceType) -> Optional[MAPServiceRate]:
        for rate in self.service_rates:
            if rate.service_type == service_type:
                return rate
        return None

    def contract_summary(self) -> str:
        return (
            f"MAPCON {self.contract_id} provider={self.provider_name} "
            f"{self.contract_start}\u2013{self.contract_end} "
            f"rental=\u00a3{self.monthly_rental_rate_gbp_per_meter:.2f}/m/month "
            f"[{self.status.value}]"
        )


class MAPContractRegister:

    def __init__(self) -> None:
        self._contracts: List[MAPContractRecord] = []
        self._counter: int = 0

    def _next_id(self) -> str:
        self._counter += 1
        return f"MAPCON-{self._counter:05d}"

    def register_contract(
        self,
        provider_name: str,
        contract_start: dt.date,
        contract_end: dt.date,
        meter_count_at_start: int,
        monthly_rental_rate_gbp_per_meter: float,
        service_rates: tuple = (),
    ) -> MAPContractRecord:
        if contract_end <= contract_start:
            raise ValueError("contract_end must be after contract_start")
        if monthly_rental_rate_gbp_per_meter < 0:
            raise ValueError("monthly_rental_rate_gbp_per_meter must be non-negative")
        if meter_count_at_start < 0:
            raise ValueError("meter_count_at_start must be non-negative")
        record = MAPContractRecord(
            contract_id=self._next_id(),
            provider_name=provider_name,
            contract_start=contract_start,
            contract_end=contract_end,
            meter_count_at_start=meter_count_at_start,
            monthly_rental_rate_gbp_per_meter=monthly_rental_rate_gbp_per_meter,
            service_rates=service_rates,
        )
        self._contracts.append(record)
        return record

    def _update(self, contract_id: str, **kwargs) -> MAPContractRecord:
        for i, c in enumerate(self._contracts):
            if c.contract_id == contract_id:
                updated = MAPContractRecord(
                    contract_id=c.contract_id,
                    provider_name=c.provider_name,
                    contract_start=c.contract_start,
                    contract_end=c.contract_end,
                    meter_count_at_start=c.meter_count_at_start,
                    monthly_rental_rate_gbp_per_meter=c.monthly_rental_rate_gbp_per_meter,
                    service_rates=c.service_rates,
                    status=kwargs.get("status", c.status),
                    termination_date=kwargs.get("termination_date", c.termination_date),
                )
                self._contracts[i] = updated
                return updated
        raise KeyError(f"MAP contract {contract_id} not found")

    def mark_expired(self, contract_id: str) -> MAPContractRecord:
        return self._update(contract_id, status=MAPContractStatus.EXPIRED)

    def terminate(self, contract_id: str, termination_date: dt.date) -> MAPContractRecord:
        return self._update(
            contract_id,
            status=MAPContractStatus.TERMINATED,
            termination_date=termination_date,
        )

    def mark_under_renegotiation(self, contract_id: str) -> MAPContractRecord:
        return self._update(contract_id, status=MAPContractStatus.UNDER_RENEGOTIATION)

    def active_contracts(self, as_of: dt.date) -> List[MAPContractRecord]:
        return [c for c in self._contracts if c.is_current_as_of(as_of)]

    def contracts_expiring_within(self, as_of: dt.date, days: int) -> List[MAPContractRecord]:
        deadline = as_of + dt.timedelta(days=days)
        return [
            c for c in self._contracts
            if c.is_active and as_of <= c.contract_end <= deadline
        ]

    def total_monthly_rental_gbp(self, as_of: dt.date, meter_count: Optional[int] = None) -> float:
        return sum(c.monthly_rental_cost_gbp(meter_count) for c in self.active_contracts(as_of))

    def by_provider(self, provider_name: str) -> List[MAPContractRecord]:
        return [c for c in self._contracts if c.provider_name == provider_name]

    def map_contract_summary(self, as_of: dt.date) -> str:
        n = len(self._contracts)
        n_active = len(self.active_contracts(as_of))
        monthly = self.total_monthly_rental_gbp(as_of)
        return (
            f"MAP Contract Register ({as_of}): {n} contracts "
            f"({n_active} active). Monthly rental: \u00a3{monthly:,.2f}."
        )
