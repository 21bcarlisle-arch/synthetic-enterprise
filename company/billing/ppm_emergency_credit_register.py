"""PPM Emergency Credit Register (Phase GG).

Prepayment meter (PPM) customers pay for energy upfront. When their credit
reaches zero, their supply is automatically disconnected (self-disconnection).

Ofgem/SLC 27A requirements for PPM emergency credit:
  - Emergency Credit: typically £5-10, auto-available when credit hits £0
    Repaid on next top-up(s) at a fixed rate per £ topped up
  - Friendly Credit (Discretionary): available at evenings/weekends when
    top-up facilities are limited; prevents overnight self-disconnection
  - Smart PPM Extra Credit: available remotely via app; emerging standard

Supplier obligations:
  - Emergency credit must be available 24/7 (SLC 27A)
  - No disconnection of vulnerable customers (SLC 26B) without welfare check
  - Welfare check if self-disconnected >28 days (Consumer Vulnerability Duty)
  - MPAS notification if customer has been self-disconnected >7 days (smart only)

The emergency credit is a form of micro-debt: customer owes supplier the
emergency credit amount until next top-up. It must be tracked separately
from contracted debt (which goes through debt_collection pipeline).

Distinct from ppm_debt_loading.py (which tracks how debt is recovered
at a rate per kWh billed through the PPM).
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

_DEFAULT_EMERGENCY_CREDIT_GBP = 5.0
_DEFAULT_FRIENDLY_CREDIT_GBP = 10.0
_SELF_DISCONNECT_WELFARE_CHECK_DAYS = 28


class EmergencyCreditType(str, Enum):
    EMERGENCY = "emergency"          # standard auto-issued at £0 credit
    FRIENDLY = "friendly"            # discretionary: evenings/weekends
    EXTRA_CREDIT = "extra_credit"    # smart PPM remote top-up


class EmergencyCreditStatus(str, Enum):
    ACTIVE = "active"               # outstanding; being repaid at next top-ups
    REPAID = "repaid"               # fully recovered
    WRITTEN_OFF = "written_off"     # debt forgiven (hardship / welfare)


@dataclass(frozen=True)
class PPMEmergencyCreditRecord:
    record_id: str                      # PPME-NNNNN
    account_id: str
    issued_date: dt.date
    credit_type: EmergencyCreditType
    amount_gbp: float
    repayment_rate_pct: float           # % of each top-up used to repay
    status: EmergencyCreditStatus = EmergencyCreditStatus.ACTIVE
    repaid_date: Optional[dt.date] = None
    amount_repaid_gbp: float = 0.0

    @property
    def is_active(self) -> bool:
        return self.status == EmergencyCreditStatus.ACTIVE

    @property
    def is_fully_repaid(self) -> bool:
        return self.status == EmergencyCreditStatus.REPAID

    @property
    def outstanding_gbp(self) -> float:
        return max(0.0, self.amount_gbp - self.amount_repaid_gbp)

    def days_outstanding(self, as_of: dt.date) -> int:
        if self.repaid_date is not None:
            return (self.repaid_date - self.issued_date).days
        return (as_of - self.issued_date).days

    def is_welfare_check_due(self, as_of: dt.date) -> bool:
        return (
            self.is_active
            and self.days_outstanding(as_of) >= _SELF_DISCONNECT_WELFARE_CHECK_DAYS
        )

    def record_summary(self) -> str:
        return (
            f"PPME {self.record_id} acct={self.account_id} "
            f"({self.credit_type.value}): £{self.amount_gbp:.2f} "
            f"outstanding=£{self.outstanding_gbp:.2f} [{self.status.value}]"
        )


class PPMEmergencyCreditRegister:

    def __init__(self) -> None:
        self._records: List[PPMEmergencyCreditRecord] = []
        self._counter: int = 0

    def _next_id(self) -> str:
        self._counter += 1
        return f"PPME-{self._counter:05d}"

    def issue_credit(
        self,
        account_id: str,
        issued_date: dt.date,
        credit_type: EmergencyCreditType = EmergencyCreditType.EMERGENCY,
        amount_gbp: float = _DEFAULT_EMERGENCY_CREDIT_GBP,
        repayment_rate_pct: float = 50.0,
    ) -> PPMEmergencyCreditRecord:
        if amount_gbp <= 0:
            raise ValueError(f"amount_gbp must be positive; got {amount_gbp}")
        if not (0 < repayment_rate_pct <= 100):
            raise ValueError(f"repayment_rate_pct must be 1-100; got {repayment_rate_pct}")
        record = PPMEmergencyCreditRecord(
            record_id=self._next_id(),
            account_id=account_id,
            issued_date=issued_date,
            credit_type=credit_type,
            amount_gbp=amount_gbp,
            repayment_rate_pct=repayment_rate_pct,
        )
        self._records.append(record)
        return record

    def _update(self, record_id: str, **kwargs) -> PPMEmergencyCreditRecord:
        for i, r in enumerate(self._records):
            if r.record_id == record_id:
                updated = PPMEmergencyCreditRecord(
                    record_id=r.record_id,
                    account_id=r.account_id,
                    issued_date=r.issued_date,
                    credit_type=r.credit_type,
                    amount_gbp=r.amount_gbp,
                    repayment_rate_pct=r.repayment_rate_pct,
                    status=kwargs.get("status", r.status),
                    repaid_date=kwargs.get("repaid_date", r.repaid_date),
                    amount_repaid_gbp=kwargs.get("amount_repaid_gbp", r.amount_repaid_gbp),
                )
                self._records[i] = updated
                return updated
        raise KeyError(f"PPM emergency credit record {record_id} not found")

    def record_partial_repayment(
        self, record_id: str, repayment_amount: float
    ) -> PPMEmergencyCreditRecord:
        for r in self._records:
            if r.record_id == record_id:
                new_total = min(r.amount_gbp, r.amount_repaid_gbp + repayment_amount)
                fully_repaid = new_total >= r.amount_gbp
                return self._update(
                    record_id,
                    amount_repaid_gbp=new_total,
                    status=EmergencyCreditStatus.REPAID if fully_repaid else r.status,
                )
        raise KeyError(f"PPM emergency credit record {record_id} not found")

    def mark_written_off(self, record_id: str) -> PPMEmergencyCreditRecord:
        return self._update(record_id, status=EmergencyCreditStatus.WRITTEN_OFF)

    def active_credit_for(self, account_id: str) -> List[PPMEmergencyCreditRecord]:
        return [r for r in self._records if r.account_id == account_id and r.is_active]

    def welfare_check_due(self, as_of: dt.date) -> List[PPMEmergencyCreditRecord]:
        return [r for r in self._records if r.is_welfare_check_due(as_of)]

    def total_outstanding_gbp(self) -> float:
        return sum(r.outstanding_gbp for r in self._records if r.is_active)

    def total_written_off_gbp(self) -> float:
        return sum(
            r.outstanding_gbp for r in self._records
            if r.status == EmergencyCreditStatus.WRITTEN_OFF
        )

    def accounts_with_active_credit(self) -> List[str]:
        return list({r.account_id for r in self._records if r.is_active})

    def written_off_records(self) -> List[PPMEmergencyCreditRecord]:
        return [r for r in self._records if r.status == EmergencyCreditStatus.WRITTEN_OFF]

    def emergency_credit_summary(self, as_of: dt.date) -> str:
        n = len(self._records)
        n_active = sum(1 for r in self._records if r.is_active)
        n_welfare = len(self.welfare_check_due(as_of))
        outstanding = self.total_outstanding_gbp()
        written_off = self.total_written_off_gbp()
        return (
            f"PPM Emergency Credit Register ({as_of}): {n} records "
            f"({n_active} active, {n_welfare} welfare check due). "
            f"Outstanding: £{outstanding:,.2f}. Written off: £{written_off:,.2f}."
        )
