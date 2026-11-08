from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Optional


class ExitFeeWaiveReason(str, Enum):
    WITHIN_NOTICE_PERIOD = "within_notice_period"   # <=42 days before contract end
    CONTRACT_EXPIRED = "contract_expired"            # exit date >= contract end
    SUPPLIER_BREACH = "supplier_breach"              # supplier increased price without notice
    CUSTOMER_DEATH = "customer_death"
    PROPERTY_EMERGENCY = "property_emergency"        # flood/fire/rebuild


# Ofgem licence: fixed-term exit fees must not apply within 42 days of end date
NOTICE_PERIOD_DAYS = 42

# Exit fee rate per kWh (elec/gas) — typical market value circa 2016-2025
# Source: published tariff schedules; varies but ~1-3p/kWh is market norm
_EXIT_FEE_PENCE_PER_KWH: dict[str, float] = {
    "electricity": 1.5,
    "gas": 1.0,
}


@dataclass(frozen=True)
class ExitFeeResult:
    customer_id: str
    contract_end_date: date
    exit_date: date
    days_remaining: int
    fee_gbp: float
    waived: bool
    waive_reason: Optional[ExitFeeWaiveReason] = None


def calculate_exit_fee(
    customer_id: str,
    contract_end_date: date,
    exit_date: date,
    annual_consumption_kwh: float,
    commodity: str = "electricity",
    waive_reason: Optional[ExitFeeWaiveReason] = None,
) -> ExitFeeResult:
    """
    Compute fixed-term contract exit fee.

    Fee = days_remaining/365 * annual_consumption_kwh * rate.
    Waived within 42-day notice period or if contract already expired.
    """
    days_remaining = max(0, (contract_end_date - exit_date).days)

    # Determine if fee should be waived
    auto_waive_reason: Optional[ExitFeeWaiveReason] = None
    if exit_date >= contract_end_date:
        auto_waive_reason = ExitFeeWaiveReason.CONTRACT_EXPIRED
    elif days_remaining <= NOTICE_PERIOD_DAYS:
        auto_waive_reason = ExitFeeWaiveReason.WITHIN_NOTICE_PERIOD

    effective_waive = waive_reason or auto_waive_reason
    waived = effective_waive is not None

    if waived:
        fee = 0.0
    else:
        rate_ppm = _EXIT_FEE_PENCE_PER_KWH.get(commodity, 1.5)
        fee = round(days_remaining / 365.0 * annual_consumption_kwh * rate_ppm / 100.0, 2)

    return ExitFeeResult(
        customer_id=customer_id,
        contract_end_date=contract_end_date,
        exit_date=exit_date,
        days_remaining=days_remaining,
        fee_gbp=fee,
        waived=waived,
        waive_reason=effective_waive,
    )
