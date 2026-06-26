import datetime as dt
import pytest
from company.regulatory.reporting_calendar import (
    ReportingFrequency, DeadlineStatus, RegulatoryDeadline, RegulatoryCalendar
)


def test_deadline_pending():
    dl = RegulatoryDeadline('D1', 'Ofgem Annual Return', 'Ofgem',
                             ReportingFrequency.ANNUAL, dt.date(2023, 4, 30))
    assert dl.status(dt.date(2023, 3, 1)) == DeadlineStatus.PENDING
    assert dl.days_until_due(dt.date(2023, 3, 1)) == 60


def test_deadline_overdue():
    dl = RegulatoryDeadline('D1', 'Ofgem Annual Return', 'Ofgem',
                             ReportingFrequency.ANNUAL, dt.date(2023, 4, 30))
    assert dl.status(dt.date(2023, 6, 1)) == DeadlineStatus.OVERDUE


def test_deadline_submitted():
    dl = RegulatoryDeadline('D1', 'Ofgem Annual Return', 'Ofgem',
                             ReportingFrequency.ANNUAL, dt.date(2023, 4, 30),
                             submitted_date=dt.date(2023, 4, 15))
    assert dl.status(dt.date(2023, 6, 1)) == DeadlineStatus.SUBMITTED
    assert dl.is_submitted


def test_mark_submitted():
    cal = RegulatoryCalendar()
    cal.add_deadline('AR2022', 'Annual Return', 'Ofgem',
                      ReportingFrequency.ANNUAL, dt.date(2023, 4, 30))
    updated = cal.mark_submitted('AR2022', dt.date(2023, 4, 20))
    assert updated.is_submitted
    assert len(cal.overdue(dt.date(2023, 6, 1))) == 0


def test_overdue_detection():
    cal = RegulatoryCalendar()
    cal.add_deadline('WHD22', 'WHD Core Group Return', 'Ofgem',
                      ReportingFrequency.ANNUAL, dt.date(2022, 12, 31))
    overdue = cal.overdue(dt.date(2023, 2, 1))
    assert len(overdue) == 1
    assert overdue[0].deadline_id == 'WHD22'


def test_due_within_days():
    cal = RegulatoryCalendar()
    cal.add_deadline('Q1', 'Q1 DESNZ Return', 'DESNZ',
                      ReportingFrequency.QUARTERLY, dt.date(2023, 4, 30))
    due_soon = cal.due_within_days(dt.date(2023, 4, 20), 14)
    assert len(due_soon) == 1
    not_yet = cal.due_within_days(dt.date(2023, 3, 1), 14)
    assert len(not_yet) == 0


def test_by_regulator():
    cal = RegulatoryCalendar()
    cal.add_deadline('A1', 'Return A', 'Ofgem',
                      ReportingFrequency.ANNUAL, dt.date(2023, 4, 30))
    cal.add_deadline('B1', 'Return B', 'DESNZ',
                      ReportingFrequency.QUARTERLY, dt.date(2023, 4, 30))
    ofgem_deadlines = cal.by_regulator('Ofgem')
    assert len(ofgem_deadlines) == 1


def test_calendar_summary():
    cal = RegulatoryCalendar()
    cal.add_deadline('A1', 'Annual Return', 'Ofgem',
                      ReportingFrequency.ANNUAL, dt.date(2023, 4, 30))
    cal.add_deadline('B1', 'Q1 Return', 'DESNZ',
                      ReportingFrequency.QUARTERLY, dt.date(2023, 2, 28))
    cal.mark_submitted('A1', dt.date(2023, 4, 20))
    s = cal.calendar_summary(dt.date(2023, 4, 25))
    assert s['submitted'] == 1
    assert s['overdue'] == 1
    assert 'due_within_14_days' in s
