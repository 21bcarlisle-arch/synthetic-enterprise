"""Back-billing compliance: Ofgem SLC 31A 12-month cap on retrospective charges."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


# Ofgem SLC 31A: domestic customers cannot be back-billed for energy consumed
# more than 12 months before the billing date where the supplier failed to bill.
# Applies from 01 May 2018.
_BACK_BILLING_LIMIT_DAYS = 365
_BACK_BILLING_RULES_START = dt.date(2018, 5, 1)


class BackBillingReason(str, Enum):
    ESTIMATED_READ_CORRECTED = "estimated_read_corrected"
    SMART_METER_INSTALL_REVEALED = "smart_meter_install_revealed"
    BILLING_SYSTEM_ERROR = "billing_system_error"
    SUPPLIER_ERROR = "supplier_error"


@dataclass(frozen=True)
class BackBillingAssessment:
    account_id: str
    billing_date: dt.date
    consumption_period_start: dt.date  # when the unbilled energy was consumed
    consumption_period_end: dt.date    # end of unbilled period
    billed_amount_gbp: float
    reason: BackBillingReason
    is_domestic: bool = True

    @property
    def _protected_start(self) -> dt.date:
        return self.billing_date - dt.timedelta(days=_BACK_BILLING_LIMIT_DAYS)

    @property
    def cap_applies(self) -> bool:
        if not self.is_domestic:
            return False
        if self.billing_date < _BACK_BILLING_RULES_START:
            return False
        # Cap applies if any part of the consumption period pre-dates the 12-month window
        return self.consumption_period_start < self._protected_start

    @property
    def capped_amount_gbp(self) -> float:
        if not self.cap_applies:
            return self.billed_amount_gbp
        total_days = (self.consumption_period_end - self.consumption_period_start).days
        if total_days <= 0:
            return 0.0
        allowed_days = max(0, (self.consumption_period_end - self._protected_start).days)
        fraction = min(1.0, allowed_days / total_days)
        return round(self.billed_amount_gbp * fraction, 2)

    @property
    def written_off_gbp(self) -> float:
        return round(self.billed_amount_gbp - self.capped_amount_gbp, 2)


class BackBillingBook:
    """Tracks back-billing assessments and compliance with Ofgem SLC 31A.

    Real context:
    - Ofgem SLC 31A effective 01 May 2018: domestic-only rule
    - Triggered most often when SMETS2 install reveals years of estimated reads
    - Estimated: suppliers collectively waived ~GBP90M in back-billing 2018-2022
    - Non-compliance: Ofgem enforcement action, restitution order
    - Non-domestic customers NOT protected (B2B commercial terms apply)
    """

    def __init__(self) -> None:
        self._assessments: List[BackBillingAssessment] = []

    def record(self, assessment: BackBillingAssessment) -> BackBillingAssessment:
        self._assessments.append(assessment)
        return assessment

    def assessments_for(self, account_id: str) -> List[BackBillingAssessment]:
        return [a for a in self._assessments if a.account_id == account_id]

    def capped_assessments(self) -> List[BackBillingAssessment]:
        return [a for a in self._assessments if a.cap_applies]

    def non_compliant_if_charged_full(self) -> List[BackBillingAssessment]:
        return [a for a in self._assessments if a.cap_applies and a.written_off_gbp > 0]

    def total_written_off_gbp(self) -> float:
        return round(sum(a.written_off_gbp for a in self._assessments), 2)

    def total_billed_gbp(self) -> float:
        return round(sum(a.capped_amount_gbp for a in self._assessments), 2)

    def back_billing_summary(self) -> dict:
        capped = self.capped_assessments()
        return {
            "total_assessments": len(self._assessments),
            "capped_count": len(capped),
            "total_billed_gbp": self.total_billed_gbp(),
            "total_written_off_gbp": self.total_written_off_gbp(),
            "non_domestic_count": sum(1 for a in self._assessments if not a.is_domestic),
        }
