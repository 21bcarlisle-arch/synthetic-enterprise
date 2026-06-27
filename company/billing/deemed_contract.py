"""Deemed Contract Register: tracks uncontracted supply; Ofgem notification obligations."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class DeemedSupplyReason(str, Enum):
    NEW_TENANT = "new_tenant"              # move-in without contract
    VOID_PERIOD_ENDED = "void_period_ended"  # supplier inherits when property re-occupied
    ACQUISITION_DEFAULT = "acquisition_default"  # customer acquired by SoLR/default
    SUPPLIER_SWITCH_FAIL = "supplier_switch_fail"  # switch fell through; no contract active


class DeemedContractStatus(str, Enum):
    ACTIVE_DEEMED = "active_deemed"
    NOTIFIED = "notified"
    CONVERTED = "converted"   # moved to fixed-term or SVT contract
    VACATED = "vacated"        # property vacated; supply ended


_NOTIFICATION_DEADLINE_WORKING_DAYS = 5
_EXTENDED_DEEMED_MONTHS = 12  # after 12m on deemed: additional Ofgem obligations


def _working_days_between(start: dt.date, end: dt.date) -> int:
    days = 0
    current = start
    while current < end:
        current += dt.timedelta(days=1)
        if current.weekday() < 5:
            days += 1
    return days


@dataclass(frozen=True)
class DeemedContractRecord:
    account_id: str
    supply_point_id: str
    start_date: dt.date
    reason: DeemedSupplyReason
    status: DeemedContractStatus = DeemedContractStatus.ACTIVE_DEEMED
    notification_date: Optional[dt.date] = None
    converted_date: Optional[dt.date] = None

    def is_notification_overdue(self, as_of: dt.date) -> bool:
        if self.notification_date is not None:
            return False
        if self.status in (DeemedContractStatus.CONVERTED, DeemedContractStatus.VACATED):
            return False
        return _working_days_between(self.start_date, as_of) > _NOTIFICATION_DEADLINE_WORKING_DAYS

    def months_on_deemed(self, as_of: dt.date) -> float:
        end = self.converted_date or as_of
        return round((end - self.start_date).days / 30.44, 1)

    def is_extended_deemed(self, as_of: dt.date) -> bool:
        return (self.status in (DeemedContractStatus.ACTIVE_DEEMED, DeemedContractStatus.NOTIFIED)
                and self.months_on_deemed(as_of) >= _EXTENDED_DEEMED_MONTHS)


class DeemedContractRegister:
    """Tracks uncontracted supply across the portfolio.

    Real calibration:
    - Deemed contracts arise when a customer takes supply without signing a formal
      contract -- most commonly at move-in (change of tenancy) or via SoLR transfer.
    - Ofgem SLC 2B (amended 2019): supplier must notify within 5 working days that
      a deemed supply relationship has begun, explaining rights and deemed rate.
    - After 12 months on deemed: additional obligations apply (proactive outreach,
      enhanced consumer protection, right to switch without exit fee).
    - Deemed rate: SVT + uplift, subject to Ofgem price cap (see cot.py).
    - Failure to notify: Ofgem enforcement -- systemic breaches attract GBP100k+ fines.
    """

    def __init__(self) -> None:
        self._records: List[DeemedContractRecord] = []

    def register(self, record: DeemedContractRecord) -> DeemedContractRecord:
        self._records.append(record)
        return record

    def _update(self, account_id: str, **kwargs) -> DeemedContractRecord:
        import dataclasses
        for i, r in enumerate(self._records):
            if r.account_id == account_id and r.status not in (
                DeemedContractStatus.CONVERTED, DeemedContractStatus.VACATED
            ):
                updated = dataclasses.replace(r, **kwargs)
                self._records[i] = updated
                return updated
        raise ValueError(f"No active deemed contract for {account_id}")

    def notify(self, account_id: str, notification_date: dt.date) -> DeemedContractRecord:
        return self._update(account_id, status=DeemedContractStatus.NOTIFIED,
                            notification_date=notification_date)

    def convert(self, account_id: str, converted_date: dt.date) -> DeemedContractRecord:
        return self._update(account_id, status=DeemedContractStatus.CONVERTED,
                            converted_date=converted_date)

    def vacate(self, account_id: str) -> DeemedContractRecord:
        return self._update(account_id, status=DeemedContractStatus.VACATED)

    def active_deemed(self) -> List[DeemedContractRecord]:
        return [r for r in self._records
                if r.status in (DeemedContractStatus.ACTIVE_DEEMED, DeemedContractStatus.NOTIFIED)]

    def overdue_notifications(self, as_of: dt.date) -> List[DeemedContractRecord]:
        return [r for r in self._records if r.is_notification_overdue(as_of)]

    def extended_deemed(self, as_of: dt.date) -> List[DeemedContractRecord]:
        return [r for r in self._records if r.is_extended_deemed(as_of)]

    def records_by_reason(self, reason: DeemedSupplyReason) -> List[DeemedContractRecord]:
        return [r for r in self._records if r.reason == reason]

    def deemed_summary(self) -> dict:
        return {
            "total_records": len(self._records),
            "active": len(self.active_deemed()),
            "converted": sum(1 for r in self._records
                             if r.status == DeemedContractStatus.CONVERTED),
        }
