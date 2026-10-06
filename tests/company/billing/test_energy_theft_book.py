import datetime as dt

import pytest

from company.billing.energy_theft_book import (
    _BACKBILL_LIMIT_YEARS,
    _DNO_NOTIFICATION_DEADLINE_WORKING_DAYS,
    EnergyTheftBook,
    TheftCase,
    TheftCaseStatus,
    TheftType,
)

#: A TEST FIXTURE for the working-day count. The module's own deadline is unsourced and None
#: (DCUSA Clause 30.9's deadline was not read), so every overdue verdict here is caller-supplied.
DEADLINE = 2


def make_case(case_id="T1", account_id="A1", sp_id="MPAN1",
              suspected=dt.date(2022, 6, 1),
              theft_type=TheftType.METER_TAMPERING,
              loss_kwh=2500.0,
              status=TheftCaseStatus.SUSPECTED,
              confirmed=None, dno_notified=None, bill_gbp=None):
    return TheftCase(
        case_id=case_id, account_id=account_id, supply_point_id=sp_id,
        suspected_date=suspected, theft_type=theft_type,
        estimated_loss_kwh=loss_kwh, status=status,
        confirmed_date=confirmed, dno_notification_date=dno_notified,
        estimated_bill_gbp=bill_gbp,
    )


class TestTheftCase:
    def test_is_active_suspected(self):
        c = make_case()
        assert c.is_active() is True

    def test_is_active_false_closed(self):
        c = make_case(status=TheftCaseStatus.CLOSED_THEFT_CONFIRMED)
        assert c.is_active() is False

    def test_is_active_false_no_theft(self):
        c = make_case(status=TheftCaseStatus.CLOSED_NO_THEFT)
        assert c.is_active() is False

    def test_dno_overdue_false_not_confirmed(self):
        c = make_case()
        assert c.is_dno_notification_overdue(dt.date(2022, 7, 1)) is False

    def test_dno_overdue_false_if_notified(self):
        c = make_case(status=TheftCaseStatus.CONFIRMED,
                      confirmed=dt.date(2022, 6, 1),
                      dno_notified=dt.date(2022, 6, 2))
        assert c.is_dno_notification_overdue(dt.date(2022, 7, 1)) is False

    def test_dno_overdue_false_within_2_working_days(self):
        c = make_case(status=TheftCaseStatus.CONFIRMED,
                      confirmed=dt.date(2022, 6, 6))
        assert c.is_dno_notification_overdue(dt.date(2022, 6, 7), DEADLINE) is False

    def test_dno_overdue_true_after_2_working_days(self):
        c = make_case(status=TheftCaseStatus.CONFIRMED,
                      confirmed=dt.date(2022, 6, 6))
        assert c.is_dno_notification_overdue(dt.date(2022, 6, 10), DEADLINE) is True

    def test_frozen(self):
        c = make_case()
        with pytest.raises((AttributeError, TypeError)):
            c.case_id = "X"


class TestEnergyTheftBook:
    def test_raise_case(self):
        book = EnergyTheftBook()
        book.raise_case(make_case())
        assert len(book.active_cases()) == 1

    def test_start_investigation(self):
        book = EnergyTheftBook()
        book.raise_case(make_case(case_id="T1"))
        result = book.start_investigation("T1")
        assert result.status == TheftCaseStatus.UNDER_INVESTIGATION

    def test_confirm_theft(self):
        book = EnergyTheftBook()
        book.raise_case(make_case(case_id="T1"))
        result = book.confirm_theft("T1", dt.date(2022, 7, 1))
        assert result.status == TheftCaseStatus.CONFIRMED
        assert result.confirmed_date == dt.date(2022, 7, 1)

    def test_notify_dno(self):
        book = EnergyTheftBook()
        book.raise_case(make_case(case_id="T1"))
        book.confirm_theft("T1", dt.date(2022, 7, 1))
        result = book.notify_dno("T1", dt.date(2022, 7, 2))
        assert result.status == TheftCaseStatus.DNO_NOTIFIED

    def test_raise_estimated_bill(self):
        book = EnergyTheftBook()
        book.raise_case(make_case(case_id="T1"))
        result = book.raise_estimated_bill("T1", 450.0)
        assert result.estimated_bill_gbp == 450.0
        assert result.status == TheftCaseStatus.ESTIMATED_BILL_RAISED

    def test_close_theft_confirmed(self):
        book = EnergyTheftBook()
        book.raise_case(make_case(case_id="T1"))
        result = book.close("T1", theft_confirmed=True)
        assert result.status == TheftCaseStatus.CLOSED_THEFT_CONFIRMED

    def test_close_no_theft(self):
        book = EnergyTheftBook()
        book.raise_case(make_case(case_id="T1"))
        result = book.close("T1", theft_confirmed=False)
        assert result.status == TheftCaseStatus.CLOSED_NO_THEFT

    def test_active_excludes_closed(self):
        book = EnergyTheftBook()
        book.raise_case(make_case(case_id="T1"))
        book.raise_case(make_case(case_id="T2"))
        book.close("T1", theft_confirmed=True)
        assert len(book.active_cases()) == 1

    def test_confirmed_cases(self):
        book = EnergyTheftBook()
        book.raise_case(make_case(case_id="T1"))
        book.confirm_theft("T1", dt.date(2022, 7, 1))
        book.raise_case(make_case(case_id="T2"))
        assert len(book.confirmed_cases()) == 1

    def test_overdue_dno_notifications(self):
        book = EnergyTheftBook()
        book.raise_case(make_case(case_id="T1"))
        book.confirm_theft("T1", dt.date(2022, 6, 6))
        assert len(book.overdue_dno_notifications(dt.date(2022, 6, 10), DEADLINE)) == 1
        assert len(book.overdue_dno_notifications(dt.date(2022, 6, 7), DEADLINE)) == 0

    def test_total_estimated_loss(self):
        book = EnergyTheftBook()
        book.raise_case(make_case(case_id="T1", loss_kwh=2500.0))
        book.confirm_theft("T1", dt.date(2022, 7, 1))
        book.raise_case(make_case(case_id="T2", loss_kwh=1000.0))
        assert book.total_estimated_loss_kwh() == 2500.0

    def test_update_raises_missing(self):
        book = EnergyTheftBook()
        with pytest.raises(ValueError):
            book.start_investigation("MISSING")

    def test_summary_keys(self):
        book = EnergyTheftBook()
        s = book.theft_summary()
        for k in ("total_cases", "active", "confirmed",
                  "total_estimated_loss_kwh", "total_estimated_bill_gbp"):
            assert k in s


class TestTheUnsourcedTheftPeriodsAreNone:
    """Corrected 2026-10-06 (read_access_and_theft_duties.md §2.4, §3.1, §5): the 2-working-day
    "GS(SS)5" DNO notice and the "3-year theft back-bill" have no source."""

    def test_the_gs_ss_5_two_day_dno_deadline_is_none(self):
        assert _DNO_NOTIFICATION_DEADLINE_WORKING_DAYS is None

    def test_the_three_year_theft_back_bill_is_none(self):
        assert _BACKBILL_LIMIT_YEARS is None

    def test_an_owed_notice_with_no_deadline_is_cannot_tell_not_a_verdict(self):
        """The partition over one confirmed, un-notified case: with a supplied deadline both
        verdicts are reachable; without, the answer is None, and a settled case is still False."""
        owed = make_case(status=TheftCaseStatus.CONFIRMED, confirmed=dt.date(2022, 6, 6))
        assert owed.is_dno_notification_overdue(dt.date(2022, 6, 7), DEADLINE) is False
        assert owed.is_dno_notification_overdue(dt.date(2022, 6, 10), DEADLINE) is True
        assert owed.is_dno_notification_overdue(dt.date(2022, 6, 10)) is None
        assert make_case().is_dno_notification_overdue(dt.date(2022, 6, 10)) is False

    def test_the_book_reports_none_not_an_empty_list_when_the_deadline_is_unknown(self):
        book = EnergyTheftBook()
        book.raise_case(make_case(case_id="T1"))
        assert book.overdue_dno_notifications(dt.date(2022, 6, 10)) == []   # nothing owed
        book.confirm_theft("T1", dt.date(2022, 6, 6))
        assert book.overdue_dno_notifications(dt.date(2022, 6, 10)) is None
