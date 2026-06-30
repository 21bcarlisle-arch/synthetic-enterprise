"""Metering Data Exception Handler (Phase EY).

Metering exceptions occur when actual consumption data is unavailable or
unreliable, requiring the supplier to use estimated reads or substitute data.

BSC (Balancing and Settlement Code) rules govern how suppliers handle:
- No-reads: meter not read in the expected period
- Estimated reads: meter estimator used instead of actual
- Substitutes: D+2 read substituted for actual when actual unavailable
- Objection period: customer can object to an estimated read within 4 months

Ofgem SLC 22: suppliers must issue bills based on actual reads where possible.
SLC 22.3: Estimated bills must be clearly marked; no more than 2 consecutive
estimated bills before a final estimated annual read is triggered.

Key metrics Ofgem monitors (supplier scorecard):
- % bills based on actual reads (target >85%)
- Days outstanding for estimated reads
- Customer objections to estimates
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class ReadType(str, Enum):
    ACTUAL = "actual"
    ESTIMATED = "estimated"
    SUBSTITUTE = "substitute"
    SMART_AMR = "smart_amr"    # smart meter automated read


class ExceptionType(str, Enum):
    NO_READ = "no_read"
    CONSECUTIVE_ESTIMATES = "consecutive_estimates"   # SLC 22.3 trigger
    REJECTED_READ = "rejected_read"                   # failed validation
    OBJECTION = "objection"                           # customer disputes


_MAX_CONSECUTIVE_ESTIMATES = 2
_OBJECTION_WINDOW_DAYS = 120    # 4 months


@dataclass(frozen=True)
class MeterRead:
    mpan: str
    read_date: dt.date
    read_type: ReadType
    read_value_kwh: float
    submitted_by: str = "agent"   # "agent", "customer", "smart", "estimator"

    @property
    def is_actual(self) -> bool:
        return self.read_type in (ReadType.ACTUAL, ReadType.SMART_AMR)

    @property
    def is_estimated(self) -> bool:
        return self.read_type in (ReadType.ESTIMATED, ReadType.SUBSTITUTE)


@dataclass(frozen=True)
class MeteringException:
    exception_id: str
    mpan: str
    exception_type: ExceptionType
    raised_at: dt.date
    resolved_at: Optional[dt.date] = None

    @property
    def is_resolved(self) -> bool:
        return self.resolved_at is not None

    def days_outstanding(self, as_of: dt.date) -> int:
        if self.is_resolved:
            return 0
        return (as_of - self.raised_at).days

    def exception_summary(self) -> str:
        return (
            "MeteringException " + self.exception_id + " (" + self.mpan + "): "
            + self.exception_type.value
            + (" resolved=" + str(self.resolved_at) if self.is_resolved else " OPEN")
        )


class MeteringExceptionBook:

    def __init__(self) -> None:
        self._reads: List[MeterRead] = []
        self._exceptions: List[MeteringException] = []
        self._next_exc_id = 1

    def record_read(self, read: MeterRead) -> MeterRead:
        self._reads.append(read)
        return read

    def reads_for_mpan(self, mpan: str) -> List[MeterRead]:
        return sorted([r for r in self._reads if r.mpan == mpan],
                      key=lambda r: r.read_date)

    def consecutive_estimate_count(self, mpan: str) -> int:
        reads = self.reads_for_mpan(mpan)
        count = 0
        for r in reversed(reads):
            if r.is_estimated:
                count += 1
            else:
                break
        return count

    def raise_exception(
        self, mpan: str, exc_type: ExceptionType, raised_at: dt.date
    ) -> MeteringException:
        exc_id = "EXC-" + str(self._next_exc_id).zfill(5)
        self._next_exc_id += 1
        exc = MeteringException(
            exception_id=exc_id,
            mpan=mpan,
            exception_type=exc_type,
            raised_at=raised_at,
        )
        self._exceptions.append(exc)
        return exc

    def resolve_exception(self, exc_id: str, resolved_at: dt.date) -> Optional[MeteringException]:
        for i, e in enumerate(self._exceptions):
            if e.exception_id == exc_id:
                updated = MeteringException(
                    exception_id=e.exception_id,
                    mpan=e.mpan,
                    exception_type=e.exception_type,
                    raised_at=e.raised_at,
                    resolved_at=resolved_at,
                )
                self._exceptions[i] = updated
                return updated
        return None

    def open_exceptions(self) -> List[MeteringException]:
        return [e for e in self._exceptions if not e.is_resolved]

    def exceptions_for_mpan(self, mpan: str) -> List[MeteringException]:
        return [e for e in self._exceptions if e.mpan == mpan]

    def actual_read_pct(self) -> float:
        if not self._reads:
            return 100.0
        actual = sum(1 for r in self._reads if r.is_actual)
        return 100.0 * actual / len(self._reads)

    def metering_summary(self, as_of: dt.date) -> str:
        n_reads = len(self._reads)
        n_open = len(self.open_exceptions())
        pct_actual = self.actual_read_pct()
        return (
            "Metering Exceptions (" + str(as_of) + "): "
            + str(n_reads) + " reads, actual_pct=" + str(round(pct_actual, 1)) + "%. "
            "Open exceptions: " + str(n_open) + "."
        )
