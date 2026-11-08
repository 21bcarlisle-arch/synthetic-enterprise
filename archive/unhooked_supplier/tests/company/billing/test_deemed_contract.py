import datetime as dt
import pytest
from company.billing.deemed_contract import (
    DeemedContractRecord, DeemedContractRegister, DeemedContractStatus, DeemedSupplyReason,
)


def make_record(account_id="A1", sp_id="MPAN1",
                start=dt.date(2023, 3, 1),
                reason=DeemedSupplyReason.NEW_TENANT,
                status=DeemedContractStatus.ACTIVE_DEEMED,
                notified=None, converted=None):
    return DeemedContractRecord(
        account_id=account_id,
        supply_point_id=sp_id,
        start_date=start,
        reason=reason,
        status=status,
        notification_date=notified,
        converted_date=converted,
    )


class TestDeemedContractRecord:
    def test_notification_overdue_false_if_notified(self):
        r = make_record(notified=dt.date(2023, 3, 3))
        assert r.is_notification_overdue(dt.date(2023, 3, 20)) is False

    def test_notification_overdue_false_within_5_days(self):
        r = make_record(start=dt.date(2023, 3, 1))
        assert r.is_notification_overdue(dt.date(2023, 3, 4)) is False

    def test_notification_overdue_true_after_5_working_days(self):
        r = make_record(start=dt.date(2023, 3, 1))
        assert r.is_notification_overdue(dt.date(2023, 3, 10)) is True

    def test_notification_overdue_false_if_converted(self):
        r = make_record(status=DeemedContractStatus.CONVERTED)
        assert r.is_notification_overdue(dt.date(2023, 4, 1)) is False

    def test_months_on_deemed_active(self):
        r = make_record(start=dt.date(2023, 1, 1))
        months = r.months_on_deemed(dt.date(2023, 7, 1))
        assert months > 5.5 and months < 6.5

    def test_months_on_deemed_converted(self):
        r = make_record(start=dt.date(2023, 1, 1), converted=dt.date(2023, 4, 1),
                        status=DeemedContractStatus.CONVERTED)
        months = r.months_on_deemed(dt.date(2024, 1, 1))
        assert months < 4.0

    def test_is_extended_deemed_false_short_duration(self):
        r = make_record(start=dt.date(2023, 1, 1))
        assert r.is_extended_deemed(dt.date(2023, 6, 1)) is False

    def test_is_extended_deemed_true_after_12_months(self):
        r = make_record(start=dt.date(2022, 1, 1))
        assert r.is_extended_deemed(dt.date(2023, 3, 1)) is True

    def test_is_extended_deemed_false_if_converted(self):
        r = make_record(start=dt.date(2022, 1, 1), status=DeemedContractStatus.CONVERTED)
        assert r.is_extended_deemed(dt.date(2023, 3, 1)) is False

    def test_frozen(self):
        r = make_record()
        with pytest.raises((AttributeError, TypeError)):
            r.account_id = "X"


class TestDeemedContractRegister:
    def test_register_and_active(self):
        reg = DeemedContractRegister()
        reg.register(make_record(account_id="A1"))
        assert len(reg.active_deemed()) == 1

    def test_notify(self):
        reg = DeemedContractRegister()
        reg.register(make_record(account_id="A1"))
        result = reg.notify("A1", dt.date(2023, 3, 3))
        assert result.status == DeemedContractStatus.NOTIFIED
        assert result.notification_date == dt.date(2023, 3, 3)

    def test_convert(self):
        reg = DeemedContractRegister()
        reg.register(make_record(account_id="A1"))
        result = reg.convert("A1", dt.date(2023, 6, 1))
        assert result.status == DeemedContractStatus.CONVERTED
        assert result.converted_date == dt.date(2023, 6, 1)

    def test_vacate(self):
        reg = DeemedContractRegister()
        reg.register(make_record(account_id="A1"))
        result = reg.vacate("A1")
        assert result.status == DeemedContractStatus.VACATED

    def test_active_excludes_converted(self):
        reg = DeemedContractRegister()
        reg.register(make_record(account_id="A1"))
        reg.register(make_record(account_id="A2"))
        reg.convert("A1", dt.date(2023, 6, 1))
        assert len(reg.active_deemed()) == 1

    def test_overdue_notifications(self):
        reg = DeemedContractRegister()
        reg.register(make_record(account_id="A1", start=dt.date(2023, 3, 1)))
        assert len(reg.overdue_notifications(dt.date(2023, 3, 10))) == 1
        assert len(reg.overdue_notifications(dt.date(2023, 3, 3))) == 0

    def test_overdue_clears_after_notification(self):
        reg = DeemedContractRegister()
        reg.register(make_record(account_id="A1", start=dt.date(2023, 3, 1)))
        reg.notify("A1", dt.date(2023, 3, 10))
        assert len(reg.overdue_notifications(dt.date(2023, 3, 15))) == 0

    def test_extended_deemed(self):
        reg = DeemedContractRegister()
        reg.register(make_record(account_id="A1", start=dt.date(2022, 1, 1)))
        assert len(reg.extended_deemed(dt.date(2023, 3, 1))) == 1
        assert len(reg.extended_deemed(dt.date(2022, 6, 1))) == 0

    def test_records_by_reason(self):
        reg = DeemedContractRegister()
        reg.register(make_record(account_id="A1", reason=DeemedSupplyReason.NEW_TENANT))
        reg.register(make_record(account_id="A2", reason=DeemedSupplyReason.ACQUISITION_DEFAULT))
        assert len(reg.records_by_reason(DeemedSupplyReason.NEW_TENANT)) == 1

    def test_update_raises_for_missing(self):
        reg = DeemedContractRegister()
        with pytest.raises(ValueError):
            reg.notify("MISSING", dt.date(2023, 3, 3))

    def test_summary_keys(self):
        reg = DeemedContractRegister()
        reg.register(make_record())
        s = reg.deemed_summary()
        assert "total_records" in s
        assert "active" in s
        assert "converted" in s

    def test_summary_counts(self):
        reg = DeemedContractRegister()
        reg.register(make_record(account_id="A1"))
        reg.register(make_record(account_id="A2"))
        reg.convert("A1", dt.date(2023, 6, 1))
        s = reg.deemed_summary()
        assert s["active"] == 1
        assert s["converted"] == 1
