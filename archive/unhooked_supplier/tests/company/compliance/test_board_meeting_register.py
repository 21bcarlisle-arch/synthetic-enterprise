"""Tests for Board Meeting Minutes Register (Phase DR)."""
import datetime as dt
import pytest
from company.compliance.board_meeting_register import (
    MeetingType, ResolutionType, MeetingStatus,
    BoardResolution, BoardMeetingRecord, BoardMeetingRegister,
    _MIN_BOARD_FREQUENCY_DAYS, _MINUTES_RETENTION_YEARS,
)


@pytest.fixture
def reg():
    return BoardMeetingRegister()


DATE = dt.date(2024, 3, 15)


def schedule_board(reg, date=DATE, directors_total=4, chair="CEO"):
    return reg.schedule(MeetingType.BOARD, date, directors_total, chair)


def make_resolution(rtype=ResolutionType.FINANCIAL, passed=True, desc="P&L sign-off"):
    import random
    return BoardResolution(
        resolution_id=f"R-{id(object())}",
        resolution_type=rtype,
        description=desc,
        passed=passed,
    )


class TestBoardResolution:
    def test_passed(self):
        r = make_resolution(passed=True)
        assert r.passed

    def test_failed(self):
        r = make_resolution(passed=False)
        assert not r.passed

    def test_type(self):
        r = make_resolution(rtype=ResolutionType.RISK)
        assert r.resolution_type == ResolutionType.RISK


class TestBoardMeetingRecord:
    def test_schedule_creates_scheduled(self, reg):
        rec = schedule_board(reg)
        assert rec.status == MeetingStatus.SCHEDULED
        assert rec.directors_present == 0

    def test_quorum_met_at_50pct(self, reg):
        rec = schedule_board(reg, directors_total=4)
        reg.record_held(rec.meeting_id, directors_present=2, resolutions=[])
        updated = reg.get(rec.meeting_id)
        assert updated.quorum_met

    def test_quorum_failed_below_50pct(self, reg):
        rec = schedule_board(reg, directors_total=4)
        reg.record_held(rec.meeting_id, directors_present=1, resolutions=[])
        updated = reg.get(rec.meeting_id)
        assert not updated.quorum_met
        assert updated.status == MeetingStatus.QUORUM_FAILED

    def test_was_held_property(self, reg):
        rec = schedule_board(reg)
        reg.record_held(rec.meeting_id, 3, [])
        assert reg.get(rec.meeting_id).was_held

    def test_resolution_count(self, reg):
        rec = schedule_board(reg)
        resolutions = [make_resolution(), make_resolution(rtype=ResolutionType.RISK)]
        reg.record_held(rec.meeting_id, 3, resolutions)
        updated = reg.get(rec.meeting_id)
        assert updated.resolution_count == 2

    def test_passed_resolutions(self, reg):
        rec = schedule_board(reg)
        r1 = make_resolution(passed=True)
        r2 = make_resolution(passed=False)
        reg.record_held(rec.meeting_id, 3, [r1, r2])
        updated = reg.get(rec.meeting_id)
        assert len(updated.passed_resolutions) == 1


class TestBoardMeetingRegister:
    def test_unique_ids(self, reg):
        r1 = schedule_board(reg)
        r2 = schedule_board(reg)
        assert r1.meeting_id != r2.meeting_id

    def test_get_missing(self, reg):
        assert reg.get("MISSING") is None

    def test_sign_off_minutes(self, reg):
        rec = schedule_board(reg)
        reg.record_held(rec.meeting_id, 3, [])
        reg.sign_off_minutes(rec.meeting_id, dt.date(2024, 3, 30))
        updated = reg.get(rec.meeting_id)
        assert updated.minutes_signed_off
        assert updated.minutes_signoff_date == dt.date(2024, 3, 30)

    def test_held_meetings(self, reg):
        r1 = schedule_board(reg, date=dt.date(2024, 1, 15))
        r2 = schedule_board(reg, date=dt.date(2024, 2, 15))
        reg.record_held(r1.meeting_id, 3, [])
        # r2 still scheduled
        assert len(reg.held_meetings()) == 1

    def test_unsigned_minutes(self, reg):
        r1 = schedule_board(reg)
        r2 = schedule_board(reg, date=dt.date(2024, 4, 15))
        reg.record_held(r1.meeting_id, 3, [])
        reg.record_held(r2.meeting_id, 3, [])
        reg.sign_off_minutes(r1.meeting_id, dt.date(2024, 4, 1))
        assert len(reg.unsigned_minutes()) == 1

    def test_by_type(self, reg):
        schedule_board(reg)
        reg.schedule(MeetingType.AUDIT_COMMITTEE, dt.date(2024, 4, 1), 3)
        board_meetings = reg.by_type(MeetingType.BOARD)
        assert len(board_meetings) == 1

    def test_resolutions_of_type(self, reg):
        rec = schedule_board(reg)
        r1 = make_resolution(rtype=ResolutionType.FINANCIAL)
        r2 = make_resolution(rtype=ResolutionType.REGULATORY)
        r3 = make_resolution(rtype=ResolutionType.FINANCIAL)
        reg.record_held(rec.meeting_id, 3, [r1, r2, r3])
        fin = reg.resolutions_of_type(ResolutionType.FINANCIAL)
        assert len(fin) == 2

    def test_overdue_frequency_no_meetings(self, reg):
        assert reg.overdue_frequency(dt.date(2024, 6, 1))

    def test_not_overdue_recent_meeting(self, reg):
        rec = schedule_board(reg, date=dt.date(2024, 5, 1))
        reg.record_held(rec.meeting_id, 3, [])
        # 30 days later = not overdue
        assert not reg.overdue_frequency(dt.date(2024, 5, 31))

    def test_overdue_frequency_after_60_days(self, reg):
        rec = schedule_board(reg, date=dt.date(2024, 1, 1))
        reg.record_held(rec.meeting_id, 3, [])
        # 90 days later
        assert reg.overdue_frequency(dt.date(2024, 4, 1))

    def test_constants(self):
        assert _MIN_BOARD_FREQUENCY_DAYS == 60
        assert _MINUTES_RETENTION_YEARS == 10

    def test_board_register_summary(self, reg):
        rec = schedule_board(reg)
        reg.record_held(rec.meeting_id, 3, [make_resolution()])
        s = reg.board_register_summary()
        assert "Board Meeting Register" in s
        assert "CA2006" in s
