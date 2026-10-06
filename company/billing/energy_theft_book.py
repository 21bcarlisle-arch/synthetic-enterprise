"""Energy Theft Reporting Book: confirmed-theft cases and the DNO notification after them.

Corrected 2026-10-06 against `docs/market_research/read_access_and_theft_duties.md` (§3.1, §5):
this module cited "GS(SS)5 / TP(SS)3" for a 2-working-day DNO notice. No such instrument was found
in any source read. The real notification hook is DCUSA Clause 30.9 (Damage or Interference),
brought in by SLC 12A.3, and its deadline was not read -- so the deadline here is None, not 2.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from company.compliance.working_days import working_days_between


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


#: UNSOURCED, so None. The duty to notify is DCUSA Clause 30.9 (via SLC 12A.3); its deadline is
#: a named GAP in read_access_and_theft_duties.md §3.1/§6 item 8. The 2 working days this held was
#: cited to "GS(SS)5", which exists in no source read. A caller that has read Clause 30.9 passes
#: the deadline in; without one, overdue is "cannot tell" (None), never a guessed verdict.
_DNO_NOTIFICATION_DEADLINE_WORKING_DAYS: Optional[int] = None
#: UNSOURCED, so None. Theft is obstruction under SLC 21BA.2(c), which REMOVES the 12-month
#: back-billing limit and sets no replacement; payment instead requires evidence of intent or
#: culpable negligence (SLC 12A.11(g)). The "3-year theft back-bill" this held has no source; a
#: general limitation period applies but was not read (read_access_and_theft_duties.md §2.4).
_BACKBILL_LIMIT_YEARS: Optional[int] = None


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

    def is_dno_notification_overdue(
        self, as_of: dt.date, deadline_working_days: Optional[int] = None,
    ) -> Optional[bool]:
        """False where no notice is owed or it was given; None where one is owed and the deadline
        is unknown (no caller-supplied deadline, and the module's own is an unsourced None)."""
        if self.dno_notification_date is not None:
            return False
        if self.confirmed_date is None:
            return False
        if self.status not in (TheftCaseStatus.CONFIRMED,):
            return False
        deadline = (deadline_working_days if deadline_working_days is not None
                    else _DNO_NOTIFICATION_DEADLINE_WORKING_DAYS)
        if deadline is None:
            return None
        return working_days_between(self.confirmed_date, as_of) > deadline

    def is_active(self) -> bool:
        return self.status not in (
            TheftCaseStatus.CLOSED_THEFT_CONFIRMED,
            TheftCaseStatus.CLOSED_NO_THEFT,
        )


class EnergyTheftBook:
    """Tracks energy theft cases from suspicion through DNO notification.

    What is established (read_access_and_theft_duties.md, read in the primary texts):
    - Duties: SLC 12A -- detect, investigate where there are reasonable grounds, enter the theft
      into settlement, and be party to REC Schedule 7 (TRAS, ETTOS, TDIS). DCUSA Clause 30.9 is
      the notification duty; its deadline is a GAP.
    - Back-billing: theft falls under SLC 21BA.2(c) (obstructive behaviour), which lifts the
      12-month limit. No licence cap replaces it. (This said "SLC 31A" and "3 years"; both wrong.)
    - Scale: the RECCo/Capgemini TEM (2023) puts GB electricity theft at 1,703-2,837 GWh a year
      across all sectors, with no published domestic split. (This said "~2.6 TWh, residential
      ~60%", unsourced.)
    NOT ESTABLISHED: a "UKRN annual return" of theft volume -- no source was read for it.
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

    def overdue_dno_notifications(
        self, as_of: dt.date, deadline_working_days: Optional[int] = None,
    ) -> Optional[List[TheftCase]]:
        """None when a notice is owed and the deadline is unknown: "we cannot tell" is the
        result, not an empty list that reads as "nothing overdue"."""
        verdicts = [(c, c.is_dno_notification_overdue(as_of, deadline_working_days))
                    for c in self._cases]
        if any(v is None for _, v in verdicts):
            return None
        return [c for c, v in verdicts if v]

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
