"""Debt Respite (Breathing Space) Register (Phase FY).

The Debt Respite Scheme (Breathing Space Moratorium and Mental Health
Crisis Moratorium) Regulations 2020 (SI 2020/1311) came into force
4 May 2021 in England and Wales.

When a customer enters Breathing Space (via a debt adviser / money
adviser approved by the Insolvency Service), the supplier must:

  1. Stop all debt collection contact (calls, letters, emails about debt)
  2. Freeze interest and charges on qualifying debts
  3. Halt enforcement action (disconnection, court proceedings)
  4. Cancel any pending disconnection orders

Standard Breathing Space: 60 calendar days (no renewable).
Mental Health Crisis Moratorium: no fixed end — continues for duration
of MH crisis treatment plus 30 days after treatment ends. The money
adviser (not the customer) notifies the supplier of start/end.

At end of Breathing Space, collection may resume. Frozen interest/
charges are NOT cancelled — they resume accruing from day 1 post-BS.
The Breathing Space period is NOT a write-off.

Observable: Insolvency Service notification (companies receive via the
Breathing Space online service, forwarded by the debt adviser).
Supplier cannot contact customer about debt during active period.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

_BREATHING_SPACE_START_DATE = dt.date(2021, 5, 4)   # scheme commencement
_STANDARD_DURATION_DAYS = 60
_MH_POST_TREATMENT_DAYS = 30                          # extra days after MH treatment


class BreathingSpaceType(str, Enum):
    STANDARD = "standard"                  # 60-day moratorium
    MENTAL_HEALTH_CRISIS = "mental_health_crisis"  # open-ended (treatment + 30d)


class BreathingSpaceStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"             # ran its full course
    CANCELLED_BY_ADVISER = "cancelled_by_adviser"  # midway review cancellation
    EXPIRED = "expired"                 # standard 60d elapsed without formal close


@dataclass(frozen=True)
class BreathingSpaceRecord:
    record_id: str                       # BS-NNNNN
    account_id: str
    bs_type: BreathingSpaceType
    start_date: dt.date
    debt_frozen_gbp: float               # qualifying debt balance at entry
    interest_frozen_gbp: float           # interest frozen for period
    status: BreathingSpaceStatus = BreathingSpaceStatus.ACTIVE
    end_date: Optional[dt.date] = None   # set on completion or cancellation

    @property
    def expected_end_date(self) -> Optional[dt.date]:
        if self.bs_type == BreathingSpaceType.STANDARD:
            return self.start_date + dt.timedelta(days=_STANDARD_DURATION_DAYS)
        return None  # MH: no fixed expected end

    def is_active_as_of(self, as_of: dt.date) -> bool:
        if self.status != BreathingSpaceStatus.ACTIVE:
            return False
        if self.bs_type == BreathingSpaceType.STANDARD:
            return as_of <= self.start_date + dt.timedelta(days=_STANDARD_DURATION_DAYS)
        return True  # MH: active until adviser closes

    def days_elapsed(self, as_of: dt.date) -> int:
        return max(0, (as_of - self.start_date).days)

    def days_remaining(self, as_of: dt.date) -> Optional[int]:
        if self.bs_type == BreathingSpaceType.MENTAL_HEALTH_CRISIS:
            return None  # indefinite
        if not self.is_active_as_of(as_of):
            return 0
        end = self.start_date + dt.timedelta(days=_STANDARD_DURATION_DAYS)
        return max(0, (end - as_of).days)

    def record_summary(self) -> str:
        return (
            f"BreathingSpace {self.record_id} [{self.bs_type.value}] "
            f"{self.account_id}: start={self.start_date} "
            f"debt=£{self.debt_frozen_gbp:.2f} "
            f"status={self.status.value}"
        )


class BreathingSpaceRegister:

    def __init__(self) -> None:
        self._records: List[BreathingSpaceRecord] = []
        self._counter: int = 0

    def _next_id(self) -> str:
        self._counter += 1
        return f"BS-{self._counter:05d}"

    def register_entry(
        self,
        account_id: str,
        bs_type: BreathingSpaceType,
        start_date: dt.date,
        debt_frozen_gbp: float,
        interest_frozen_gbp: float = 0.0,
    ) -> BreathingSpaceRecord:
        if start_date < _BREATHING_SPACE_START_DATE:
            raise ValueError(
                f"Breathing Space scheme started {_BREATHING_SPACE_START_DATE}; "
                f"cannot register entry for {start_date}"
            )
        record = BreathingSpaceRecord(
            record_id=self._next_id(),
            account_id=account_id,
            bs_type=bs_type,
            start_date=start_date,
            debt_frozen_gbp=debt_frozen_gbp,
            interest_frozen_gbp=interest_frozen_gbp,
        )
        self._records.append(record)
        return record

    def _update(self, record_id: str, **kwargs) -> BreathingSpaceRecord:
        for i, r in enumerate(self._records):
            if r.record_id == record_id:
                updated = BreathingSpaceRecord(
                    record_id=r.record_id,
                    account_id=r.account_id,
                    bs_type=r.bs_type,
                    start_date=r.start_date,
                    debt_frozen_gbp=r.debt_frozen_gbp,
                    interest_frozen_gbp=r.interest_frozen_gbp,
                    status=kwargs.get("status", r.status),
                    end_date=kwargs.get("end_date", r.end_date),
                )
                self._records[i] = updated
                return updated
        raise KeyError(f"Breathing Space record {record_id} not found")

    def complete(self, record_id: str, end_date: dt.date) -> BreathingSpaceRecord:
        return self._update(record_id, status=BreathingSpaceStatus.COMPLETED, end_date=end_date)

    def cancel_by_adviser(self, record_id: str, cancel_date: dt.date) -> BreathingSpaceRecord:
        return self._update(
            record_id, status=BreathingSpaceStatus.CANCELLED_BY_ADVISER, end_date=cancel_date
        )

    def records_for_account(self, account_id: str) -> List[BreathingSpaceRecord]:
        return [r for r in self._records if r.account_id == account_id]

    def active_records(self, as_of: dt.date) -> List[BreathingSpaceRecord]:
        return [r for r in self._records if r.is_active_as_of(as_of)]

    def mental_health_crisis_records(self) -> List[BreathingSpaceRecord]:
        return [r for r in self._records if r.bs_type == BreathingSpaceType.MENTAL_HEALTH_CRISIS]

    def standard_records(self) -> List[BreathingSpaceRecord]:
        return [r for r in self._records if r.bs_type == BreathingSpaceType.STANDARD]

    def total_debt_frozen_gbp(self) -> float:
        return sum(r.debt_frozen_gbp for r in self._records)

    def total_interest_frozen_gbp(self) -> float:
        return sum(r.interest_frozen_gbp for r in self._records)

    def active_debt_frozen_gbp(self, as_of: dt.date) -> float:
        return sum(r.debt_frozen_gbp for r in self.active_records(as_of))

    def breathing_space_summary(self, as_of: dt.date) -> str:
        n = len(self._records)
        n_active = len(self.active_records(as_of))
        n_mh = len(self.mental_health_crisis_records())
        total_frozen = self.active_debt_frozen_gbp(as_of)
        return (
            f"Breathing Space Register ({as_of}): {n} total ({n_active} active, "
            f"{n_mh} MH crisis). Active debt frozen: £{total_frozen:.2f}."
        )
