"""Board Meeting Minutes Register (Phase DR).

UK law (Companies Act 2006) requires the board to:
- Hold regular board meetings (typically monthly for a small supplier)
- Keep minutes of all board resolutions (CA 2006 s248)
- Minutes are prima facie evidence of proceedings at meeting
- Must be retained for 10 years at registered office
- Ofgem may request board minutes as part of compliance evidence
  (e.g., FRA, Consumer Duty sign-off, licence condition breaches)

For an energy supplier, typical agenda items:
- Financial performance vs budget (monthly)
- Risk committee report and VaR review
- Ofgem regulatory updates
- Settlement and imbalance review
- Capital adequacy / FRA compliance sign-off
- Customer satisfaction / NPS report
- Health & safety (if field workers)

Resolution types:
- FINANCIAL: P&L sign-off, budget approval, credit facility drawdown
- REGULATORY: licence obligations, Ofgem compliance, enforcement
- OPERATIONAL: procurement, staffing, IT
- GOVERNANCE: director appointments, company secretary matters
- RISK: hedge policy changes, VaR limit changes, stress scenarios
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class MeetingType(str, Enum):
    BOARD = "board"
    AUDIT_COMMITTEE = "audit_committee"
    RISK_COMMITTEE = "risk_committee"
    REMUNERATION = "remuneration"
    EMERGENCY = "emergency"


class ResolutionType(str, Enum):
    FINANCIAL = "financial"
    REGULATORY = "regulatory"
    OPERATIONAL = "operational"
    GOVERNANCE = "governance"
    RISK = "risk"


class MeetingStatus(str, Enum):
    SCHEDULED = "scheduled"
    HELD = "held"
    QUORUM_FAILED = "quorum_failed"     # insufficient directors attended
    CANCELLED = "cancelled"


_MIN_BOARD_FREQUENCY_DAYS = 60          # boards should meet at least every 2 months
_MINUTES_RETENTION_YEARS = 10           # CA 2006 s248


@dataclass(frozen=True)
class BoardResolution:
    resolution_id: str
    resolution_type: ResolutionType
    description: str
    passed: bool                         # unanimous or majority vote
    dissenting_directors: int = 0        # number of dissenting votes


@dataclass(frozen=True)
class BoardMeetingRecord:
    meeting_id: str
    meeting_type: MeetingType
    scheduled_date: dt.date
    directors_present: int
    directors_total: int
    status: MeetingStatus
    resolutions: tuple                   # tuple of BoardResolution
    chair: str = ""
    minutes_signed_off: bool = False
    minutes_signoff_date: Optional[dt.date] = None

    @property
    def quorum_met(self) -> bool:
        if self.directors_total == 0:
            return False
        return self.directors_present / self.directors_total >= 0.5

    @property
    def was_held(self) -> bool:
        return self.status == MeetingStatus.HELD

    @property
    def resolution_count(self) -> int:
        return len(self.resolutions)

    @property
    def passed_resolutions(self) -> List[BoardResolution]:
        return [r for r in self.resolutions if r.passed]


class BoardMeetingRegister:
    """Tracks board meeting minutes for CA 2006 compliance."""

    def __init__(self) -> None:
        self._records: Dict[str, BoardMeetingRecord] = {}
        self._seq = 0

    def _next_id(self) -> str:
        self._seq += 1
        return f"BM-{self._seq:04d}"

    def schedule(
        self,
        meeting_type: MeetingType,
        scheduled_date: dt.date,
        directors_total: int,
        chair: str = "",
    ) -> BoardMeetingRecord:
        mid = self._next_id()
        rec = BoardMeetingRecord(
            meeting_id=mid,
            meeting_type=meeting_type,
            scheduled_date=scheduled_date,
            directors_present=0,
            directors_total=directors_total,
            status=MeetingStatus.SCHEDULED,
            resolutions=(),
            chair=chair,
        )
        self._records[mid] = rec
        return rec

    def record_held(
        self,
        meeting_id: str,
        directors_present: int,
        resolutions: List[BoardResolution],
    ) -> BoardMeetingRecord:
        rec = self._records[meeting_id]
        status = (MeetingStatus.HELD
                  if directors_present >= rec.directors_total * 0.5
                  else MeetingStatus.QUORUM_FAILED)
        updated = BoardMeetingRecord(
            meeting_id=rec.meeting_id,
            meeting_type=rec.meeting_type,
            scheduled_date=rec.scheduled_date,
            directors_present=directors_present,
            directors_total=rec.directors_total,
            status=status,
            resolutions=tuple(resolutions),
            chair=rec.chair,
            minutes_signed_off=rec.minutes_signed_off,
        )
        self._records[meeting_id] = updated
        return updated

    def sign_off_minutes(
        self, meeting_id: str, signoff_date: dt.date
    ) -> BoardMeetingRecord:
        rec = self._records[meeting_id]
        updated = BoardMeetingRecord(
            meeting_id=rec.meeting_id,
            meeting_type=rec.meeting_type,
            scheduled_date=rec.scheduled_date,
            directors_present=rec.directors_present,
            directors_total=rec.directors_total,
            status=rec.status,
            resolutions=rec.resolutions,
            chair=rec.chair,
            minutes_signed_off=True,
            minutes_signoff_date=signoff_date,
        )
        self._records[meeting_id] = updated
        return updated

    def get(self, meeting_id: str) -> Optional[BoardMeetingRecord]:
        return self._records.get(meeting_id)

    def held_meetings(self) -> List[BoardMeetingRecord]:
        return [r for r in self._records.values() if r.was_held]

    def unsigned_minutes(self) -> List[BoardMeetingRecord]:
        return [r for r in self.held_meetings() if not r.minutes_signed_off]

    def by_type(self, meeting_type: MeetingType) -> List[BoardMeetingRecord]:
        return [r for r in self._records.values() if r.meeting_type == meeting_type]

    def resolutions_of_type(self, resolution_type: ResolutionType) -> List[BoardResolution]:
        result = []
        for rec in self.held_meetings():
            for res in rec.resolutions:
                if res.resolution_type == resolution_type:
                    result.append(res)
        return result

    def overdue_frequency(self, as_of: dt.date) -> bool:
        """True if no board meeting in the past 60 days."""
        held = [r for r in self.held_meetings()
                if r.scheduled_date <= as_of]
        if not held:
            return True
        latest = max(r.scheduled_date for r in held)
        return (as_of - latest).days > _MIN_BOARD_FREQUENCY_DAYS

    def board_register_summary(self) -> str:
        total = len(self._records)
        held = len(self.held_meetings())
        n_unsigned = len(self.unsigned_minutes())
        all_res = sum(r.resolution_count for r in self.held_meetings())
        return (
            f"Board Meeting Register (CA2006 s248): {total} meetings total. "
            f"Held: {held}. Unsigned minutes: {n_unsigned}. "
            f"Total resolutions: {all_res}. "
            f"Retention: {_MINUTES_RETENTION_YEARS} years."
        )
