from __future__ import annotations

import dataclasses
from datetime import date
from enum import Enum
from typing import Dict, List, Optional


class GSoPStandard(Enum):
    BILLING_DELAY = "billing_delay"
    COMPLAINT_NO_RESPONSE = "complaint_no_response"
    COMPLAINT_UNRESOLVED = "complaint_unresolved"
    RECONNECTION_DELAY = "reconnection_delay"
    APPOINTMENT_MISSED = "appointment_missed"
    FINAL_BILL_DELAY = "final_bill_delay"
    METER_READ_DISPUTE = "meter_read_dispute"
    DIRECT_DEBIT_ERROR = "direct_debit_error"
    SWITCHING_DELAY = "switching_delay"
    DEBT_QUERY_DELAY = "debt_query_delay"


class GSoPBreachStatus(Enum):
    OPEN = "open"
    COMPENSATED = "compensated"
    WAIVED = "waived"
    DISPUTED = "disputed"


@dataclasses.dataclass(frozen=True)
class GSoPBreach:
    breach_id: str
    account_id: str
    standard: GSoPStandard
    breach_date: date
    compensation_gbp: float
    status: GSoPBreachStatus
    resolution_date: Optional[date] = None
    notes: str = ""

    @property
    def is_open(self) -> bool:
        return self.status == GSoPBreachStatus.OPEN

    @property
    def is_compensated(self) -> bool:
        return self.status == GSoPBreachStatus.COMPENSATED

    @property
    def working_days_open(self) -> int:
        end = self.resolution_date or date.today()
        count = 0
        current = self.breach_date
        while current < end:
            if current.weekday() < 5:
                count += 1
            current = date.fromordinal(current.toordinal() + 1)
        return count


class GSoPTracker:
    """Tracks Guaranteed Standards of Performance breaches and compensation.

    Statutory basis: Gas Act 1986 / Electricity Act 1989 (as amended); Ofgem
    Guaranteed Standards Regulations.  Compensation is fixed at 30.0 GBP per breach.
    """

    def __init__(self) -> None:
        self._breaches: Dict[str, GSoPBreach] = {}

    def record_breach(
        self,
        account_id: str,
        standard: GSoPStandard,
        breach_date: date,
        notes: str = "",
    ) -> GSoPBreach:
        breach_id = "GSOP-{:04d}".format(len(self._breaches) + 1)
        breach = GSoPBreach(
            breach_id=breach_id,
            account_id=account_id,
            standard=standard,
            breach_date=breach_date,
            compensation_gbp=30.0,
            status=GSoPBreachStatus.OPEN,
            notes=notes,
        )
        self._breaches[breach_id] = breach
        return breach

    def compensate_breach(self, breach_id: str, resolution_date: date) -> GSoPBreach:
        breach = self._breaches[breach_id]
        updated = dataclasses.replace(
            breach,
            status=GSoPBreachStatus.COMPENSATED,
            resolution_date=resolution_date,
        )
        self._breaches[breach_id] = updated
        return updated

    def waive_breach(self, breach_id: str) -> GSoPBreach:
        breach = self._breaches[breach_id]
        updated = dataclasses.replace(breach, status=GSoPBreachStatus.WAIVED)
        self._breaches[breach_id] = updated
        return updated

    def open_breaches(self) -> List[GSoPBreach]:
        return [b for b in self._breaches.values() if b.is_open]

    def breaches_for_standard(self, standard: GSoPStandard) -> List[GSoPBreach]:
        return [b for b in self._breaches.values() if b.standard == standard]

    def total_compensation_paid_gbp(self) -> float:
        return sum(
            b.compensation_gbp for b in self._breaches.values() if b.is_compensated
        )

    def total_compensation_outstanding_gbp(self) -> float:
        return sum(
            b.compensation_gbp for b in self._breaches.values() if b.is_open
        )

    def breach_rate_per_100_customers(self, total_customers: int) -> float:
        if total_customers == 0:
            return 0.0
        return len(self._breaches) / total_customers * 100.0

    def breaches_by_standard(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for b in self._breaches.values():
            counts[b.standard.value] = counts.get(b.standard.value, 0) + 1
        return counts

    def is_systemic(self, standard: GSoPStandard) -> bool:
        return len(self.breaches_for_standard(standard)) > 5

    def gsop_summary(self) -> dict:
        all_breaches = list(self._breaches.values())
        open_count = sum(1 for b in all_breaches if b.status == GSoPBreachStatus.OPEN)
        compensated_count = sum(
            1 for b in all_breaches if b.status == GSoPBreachStatus.COMPENSATED
        )
        waived_count = sum(
            1 for b in all_breaches if b.status == GSoPBreachStatus.WAIVED
        )
        systemic = [
            s.value for s in GSoPStandard if len(self.breaches_for_standard(s)) > 5
        ]
        return {
            "total_breaches": len(all_breaches),
            "open_count": open_count,
            "compensated_count": compensated_count,
            "waived_count": waived_count,
            "outstanding_gbp": self.total_compensation_outstanding_gbp(),
            "paid_gbp": self.total_compensation_paid_gbp(),
            "systemic_standards": systemic,
            "breach_rate_note": (
                "Use breach_rate_per_100_customers(total_customers) for rate calculation"
            ),
        }
