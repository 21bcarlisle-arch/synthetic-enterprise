from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Optional

MICROBUSINESS_ELEC_THRESHOLD_KWH = 100_000   # Ofgem: <100 MWh/yr electricity
MICROBUSINESS_GAS_THRESHOLD_KWH = 293_000    # Ofgem: <293 MWh/yr gas (~10,000 therms)
MICROBUSINESS_STAFF_MAX = 10
MICROBUSINESS_TURNOVER_MAX_GBP = 2_000_000


class MicrobusinessStatus(str, Enum):
    MICRO = "micro"
    NON_MICRO = "non_micro"
    UNCLASSIFIED = "unclassified"


@dataclass(frozen=True)
class MicrobusinessProfile:
    customer_id: str
    annual_elec_kwh: Optional[float] = None
    annual_gas_kwh: Optional[float] = None
    staff_count: Optional[int] = None
    annual_turnover_gbp: Optional[float] = None
    as_of_date: Optional[date] = None

    @property
    def status(self) -> MicrobusinessStatus:
        if self.annual_elec_kwh is None and self.annual_gas_kwh is None:
            return MicrobusinessStatus.UNCLASSIFIED
        elec_ok = (
            self.annual_elec_kwh is None
            or self.annual_elec_kwh < MICROBUSINESS_ELEC_THRESHOLD_KWH
        )
        gas_ok = (
            self.annual_gas_kwh is None
            or self.annual_gas_kwh < MICROBUSINESS_GAS_THRESHOLD_KWH
        )
        staff_ok = (
            self.staff_count is None
            or self.staff_count <= MICROBUSINESS_STAFF_MAX
        )
        turnover_ok = (
            self.annual_turnover_gbp is None
            or self.annual_turnover_gbp <= MICROBUSINESS_TURNOVER_MAX_GBP
        )
        if elec_ok and gas_ok and staff_ok and turnover_ok:
            return MicrobusinessStatus.MICRO
        return MicrobusinessStatus.NON_MICRO

    @property
    def is_micro(self) -> bool:
        return self.status == MicrobusinessStatus.MICRO

    def eligible_protections(self) -> list:
        if not self.is_micro:
            return []
        return [
            "price_comparison_enabled",
            "42_day_renewal_notice",
            "no_rollover_without_consent",
            "complaints_to_ombudsman",
            "deemed_contract_exit_right",
        ]


def classify_customer(
    customer_id: str,
    annual_elec_kwh: Optional[float] = None,
    annual_gas_kwh: Optional[float] = None,
    staff_count: Optional[int] = None,
    annual_turnover_gbp: Optional[float] = None,
    as_of_date: Optional[date] = None,
) -> MicrobusinessProfile:
    return MicrobusinessProfile(
        customer_id=customer_id,
        annual_elec_kwh=annual_elec_kwh,
        annual_gas_kwh=annual_gas_kwh,
        staff_count=staff_count,
        annual_turnover_gbp=annual_turnover_gbp,
        as_of_date=as_of_date,
    )
