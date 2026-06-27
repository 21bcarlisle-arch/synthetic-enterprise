"""Energy Theft Reporting Book: GS(SS)5 DNO notification obligations post-investigation."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class TheftCaseStatus(str, Enum):
    SUSPECTED = "suspected"
    UNDER_INVESTIGATION = "under_investigation"
    CONFIRMED = "confirmed"
    DNO_NOTIFIED = "dno_notified"
    ESTIMATED_BILL_RAISED = "estimated_bill_raised"
    CLOSED_THEFT_CONFIRMED = "closed_theft_confirmed"
    CLOSED_NO_THEFT = "closed_no_theft"


class TheftType(str, Enum):
    METER_TAMPERING = "meter_tampering"
    BYPASSED_METER = "bypassed_meter"
    FRAUDULENT_READS = "fraudulent_reads"
    COMMUNICATION_INTERFERENCE = "communication_interference"


_DNO_NOTIFICATION_DEADLINE_WORKING_DAYS = 2  # GS(SS)5: 2 working days from confirmation
_BACKBILL_LIMIT_YEARS = 3                    # theft: 3-year estimated back-bill


def _working_days_between(start: dt.date, end: dt.date) -> int:
    days = 0
    current = start
    while current < end:
        current += dt.timedelta(days=1)
        if current.weekday() < 5:
            days += 1
    return days


@dataclass(frozen=True)
class TheftCase:
    case_id: str
    account_id: str
    supply_point_id: str
    suspected_date: dt.date
    theft_type: TheftType
    estimated_loss_kwh: float
    status: TheftCaseStatus = TheftCaseStatus.SUSPECTED
    confirmed_date: Optional[dt.date] = None
    dno_notification_date: Optional[dt.date] = None
    estimated_bill_gbp: Optional[float] = None

    def is_dno_notification_overdue(self, as_of: dt.date) -> bool:
        if self.dno_notification_date is not None:
            return False
        if self.confirmed_date is None:
            return False
        if self.status not in (TheftCaseStatus.CONFIRMED,):
            return False
        return _working_days_between(self.confirmed_date, as_of) > _DNO_NOTIFICATION_DEADLINE_WORKING_DAYS

    def is_active(self) -> bool:
        return self.status not in (
            TheftCaseStatus.CLOSED_THEFT_CONFIRMED,
            TheftCaseStatus.CLOSED_NO_THEFT,
        )


class EnergyTheftBook:
    """Tracks energy theft cases from suspicion through DNO notification.

    Real calibration:
    - GS(SS)5 (Gas Shipper Standards) / TP(SS)3 (Electricity): obligates suppliers to
      notify the relevant DNO (electricity) or gas transporter within 2 working days
      of confirming energy theft.
    - Estimated back-bill: suppliers may issue back-bills for up to 3 years for theft
      (exception to the 12-month back-billing rule SLC 31A -- theft is exempt).
    - UKRN annual reporting: theft volume (kWh) must be included in annual return.
    - Sector estimate: ~2.6 TWh stolen annually in UK; residential tampering accounts
      for ~60% of cases; commercial metering fraud ~40%.
    """

    def __init__(self) -> None:
        self._cases: List[TheftCase] = []

    def raise_case(self, case: TheftCase) -> TheftCase:
        self._cases.append(case)
        return case

    def _update(self, case_id: str, **kwargs) -> TheftCase:
        import dataclasses
        for i, c in enumerate(self._cases):
            if c.case_id == case_id:
                updated = dataclasses.replace(c, **kwargs)
                self._cases[i] = updated
                return updated
        raise ValueError(f"Case not found: {case_id}")

    def start_investigation(self, case_id: str) -> TheftCase:
        return self._update(case_id, status=TheftCaseStatus.UNDER_INVESTIGATION)

    def confirm_theft(self, case_id: str, confirmed_date: dt.date) -> TheftCase:
        return self._update(case_id, status=TheftCaseStatus.CONFIRMED,
                            confirmed_date=confirmed_date)

    def notify_dno(self, case_id: str, notification_date: dt.date) -> TheftCase:
        return self._update(case_id, status=TheftCaseStatus.DNO_NOTIFIED,
                            dno_notification_date=notification_date)

    def raise_estimated_bill(self, case_id: str, amount_gbp: float) -> TheftCase:
        return self._update(case_id, status=TheftCaseStatus.ESTIMATED_BILL_RAISED,
                            estimated_bill_gbp=amount_gbp)

    def close(self, case_id: str, theft_confirmed: bool) -> TheftCase:
        status = (TheftCaseStatus.CLOSED_THEFT_CONFIRMED if theft_confirmed
                  else TheftCaseStatus.CLOSED_NO_THEFT)
        return self._update(case_id, status=status)

    def active_cases(self) -> List[TheftCase]:
        return [c for c in self._cases if c.is_active()]

    def confirmed_cases(self) -> List[TheftCase]:
        return [c for c in self._cases
                if c.status in (TheftCaseStatus.CONFIRMED,
                                TheftCaseStatus.DNO_NOTIFIED,
                                TheftCaseStatus.ESTIMATED_BILL_RAISED,
                                TheftCaseStatus.CLOSED_THEFT_CONFIRMED)]

    def overdue_dno_notifications(self, as_of: dt.date) -> List[TheftCase]:
        return [c for c in self._cases if c.is_dno_notification_overdue(as_of)]

    def total_estimated_loss_kwh(self) -> float:
        return round(sum(c.estimated_loss_kwh for c in self.confirmed_cases()), 1)

    def theft_summary(self) -> dict:
        confirmed = self.confirmed_cases()
        return {
            "total_cases": len(self._cases),
            "active": len(self.active_cases()),
            "confirmed": len(confirmed),
            "total_estimated_loss_kwh": self.total_estimated_loss_kwh(),
            "total_estimated_bill_gbp": round(
                sum(c.estimated_bill_gbp or 0 for c in confirmed), 2
            ),
        }
