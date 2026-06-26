"""Half-hourly (HH) meter data quality checker.

UK HH settlement data from meters and the DTN can contain:
- Missing periods (gaps in the 48 HH periods per day)
- Estimated reads (substituted when the meter fails to communicate)
- Zero consumption (unexpected zero that may indicate meter fault)
- Negative consumption (physically impossible, indicates meter fault or CT ratio error)
- Implausibly high consumption (outlier check against customer EAC)

Data quality flags align with BSCP505 (BSC Procedure for HH data quality).
The company applies these checks before billing to prevent estimated-read disputes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


_EXPECTED_PERIODS_PER_DAY = 48


@dataclass
class HHRecord:
    period_id: str        # e.g. "2024-01-01:01" (date:period 1-48)
    kwh: float
    data_type: Literal["actual", "estimated", "substituted"] = "actual"
    flag: str = ""        # BSC flag code (e.g. "E" estimated, "D" disputed)


@dataclass
class DataQualityResult:
    period_id: str
    issue: str            # description of the problem
    severity: Literal["info", "warning", "error"]
    kwh: float


class HHDataQualityChecker:
    """Validates HH meter data quality before billing."""

    def __init__(self, customer_eac_kwh: float = 3500.0):
        # EAC used to calibrate implausible threshold: max half-hour = EAC / 365 / 48 * 10
        self.customer_eac_kwh = customer_eac_kwh
        self._max_kwh_per_period = max(2.0, customer_eac_kwh / 365.0 / 48.0 * 10.0)

    def check_record(self, record: HHRecord) -> list[DataQualityResult]:
        issues = []
        pid = record.period_id
        kwh = record.kwh

        if kwh < 0:
            issues.append(DataQualityResult(pid, "Negative consumption — possible meter fault or CT error", "error", kwh))
        elif kwh == 0.0 and record.data_type == "actual":
            issues.append(DataQualityResult(pid, "Zero consumption on actual read — check meter comms", "warning", kwh))
        elif kwh > self._max_kwh_per_period:
            issues.append(DataQualityResult(pid, f"Implausibly high: {kwh:.2f} kWh (>{self._max_kwh_per_period:.2f} threshold)", "warning", kwh))

        if record.data_type == "estimated":
            issues.append(DataQualityResult(pid, "Estimated read — meter not communicating", "info", kwh))
        elif record.data_type == "substituted":
            issues.append(DataQualityResult(pid, "Substituted read — manual intervention applied", "warning", kwh))

        return issues

    def check_day(self, records: list[HHRecord]) -> dict:
        """Check a full day's 48 HH records."""
        all_issues: list[DataQualityResult] = []
        for r in records:
            all_issues.extend(self.check_record(r))

        missing = _EXPECTED_PERIODS_PER_DAY - len(records)
        if missing > 0:
            all_issues.append(DataQualityResult("?", f"{missing} HH period(s) missing from day", "error", 0))

        errors = [i for i in all_issues if i.severity == "error"]
        warnings = [i for i in all_issues if i.severity == "warning"]
        infos = [i for i in all_issues if i.severity == "info"]

        return {
            "period_count": len(records),
            "missing_periods": missing,
            "total_kwh": round(sum(r.kwh for r in records), 4),
            "estimated_kwh": round(sum(r.kwh for r in records if r.data_type == "estimated"), 4),
            "quality_ok": len(errors) == 0,
            "errors": len(errors),
            "warnings": len(warnings),
            "infos": len(infos),
            "issues": all_issues,
        }
