"""Ofgem reporting obligations tracker.

UK energy suppliers have mandatory reporting obligations to Ofgem.
These differ from the DESNZ returns — they are performance and compliance
reports rather than market monitoring data:

  - Monthly: Price cap compliance (SLC 21C)
  - Monthly: Billing accuracy sample audit (SLC 7)
  - Quarterly: Complaint volume and resolution rates (SLC 14C)
  - Annual: Annual report of business activities (SLC 36D)
  - Annual: Smart meter installation progress (SLC 22)
  - Annual: Debt and payment difficulty cases (SLC 27)

Each obligation has a defined frequency, submission deadline offset from
the reference period end, and a maximum penalty for late/non-submission.

Tracking evidences the supplier's compliance posture for Ofgem inspections.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Literal


_OBLIGATIONS = {
    "price_cap_compliance":   ("monthly",  15,   "SLC 21C",  250_000),
    "billing_accuracy_audit": ("monthly",  20,   "SLC 7",    100_000),
    "complaint_report":       ("quarterly", 30,  "SLC 14C",  500_000),
    "annual_business_report": ("annual",   90,   "SLC 36D",  10_000_000),
    "smart_meter_progress":   ("annual",   60,   "SLC 22",   1_000_000),
    "debt_difficulty_report": ("annual",   60,   "SLC 27",   500_000),
}
# Format: (frequency, deadline_days_after_period, slc_ref, max_penalty_gbp)


@dataclass
class ReportingObligation:
    name: str
    slc_ref: str
    frequency: Literal["monthly", "quarterly", "annual"]
    deadline_days: int
    max_penalty_gbp: float


@dataclass
class ObligationSubmission:
    obligation_name: str
    reference_period: str   # e.g. "2024-M03", "2024-Q1", "2024"
    submission_date: str    # ISO date when submitted
    deadline_date: str      # ISO date of deadline
    submitted_by: str = ""
    notes: str = ""

    @property
    def is_on_time(self) -> bool:
        s = date.fromisoformat(self.submission_date)
        d = date.fromisoformat(self.deadline_date)
        return s <= d

    @property
    def days_late(self) -> int:
        s = date.fromisoformat(self.submission_date)
        d = date.fromisoformat(self.deadline_date)
        return max(0, (s - d).days)


class OfgemObligationsTracker:
    """Tracks submission records against all Ofgem reporting obligations."""

    def __init__(self):
        self._submissions: list[ObligationSubmission] = []
        self._obligations: dict[str, ReportingObligation] = {
            name: ReportingObligation(name, slc, freq, days, penalty)
            for name, (freq, days, slc, penalty) in _OBLIGATIONS.items()
        }

    def record_submission(self, sub: ObligationSubmission) -> ObligationSubmission:
        self._submissions.append(sub)
        return sub

    def obligation(self, name: str) -> ReportingObligation | None:
        return self._obligations.get(name)

    def all_obligations(self) -> list[ReportingObligation]:
        return list(self._obligations.values())

    def submissions_for(self, obligation_name: str) -> list[ObligationSubmission]:
        return [s for s in self._submissions if s.obligation_name == obligation_name]

    def late_submissions(self) -> list[ObligationSubmission]:
        return [s for s in self._submissions if not s.is_on_time]

    def on_time_rate_pct(self) -> float:
        if not self._submissions:
            return 100.0
        on_time = sum(1 for s in self._submissions if s.is_on_time)
        return round(100.0 * on_time / len(self._submissions), 1)

    def total_potential_penalty_gbp(self) -> float:
        """Sum of max penalties for any late submission."""
        total = 0.0
        for s in self.late_submissions():
            ob = self._obligations.get(s.obligation_name)
            if ob:
                total += ob.max_penalty_gbp
        return total

    def summary(self) -> dict:
        return {
            "obligations_count": len(self._obligations),
            "total_submissions": len(self._submissions),
            "late_submissions": len(self.late_submissions()),
            "on_time_rate_pct": self.on_time_rate_pct(),
            "potential_penalty_gbp": self.total_potential_penalty_gbp(),
        }
