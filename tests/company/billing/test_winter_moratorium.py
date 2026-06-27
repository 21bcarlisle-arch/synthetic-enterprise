import datetime as dt
import pytest
from company.billing.winter_moratorium import (
    MoratoriumRecord, MoratoriumType, DisconnectionRisk,
    WinterMoratoriumRegister, is_winter_period,
)


def make_record(account_id="A1",
                mtype=MoratoriumType.WINTER_DOMESTIC,
                start=dt.date(2023, 11, 1),
                end=dt.date(2024, 3, 31),
                reason="winter protection"):
    return MoratoriumRecord(
        account_id=account_id, moratorium_type=mtype,
        start_date=start, end_date=end, reason=reason,
    )


class TestIsWinterPeriod:
    def test_november_is_winter(self):
        assert is_winter_period(dt.date(2023, 11, 15)) is True

    def test_december_is_winter(self):
        assert is_winter_period(dt.date(2023, 12, 25)) is True

    def test_january_is_winter(self):
        assert is_winter_period(dt.date(2024, 1, 15)) is True

    def test_march_is_winter(self):
        assert is_winter_period(dt.date(2024, 3, 31)) is True

    def test_april_is_not_winter(self):
        assert is_winter_period(dt.date(2024, 4, 1)) is False

    def test_june_is_not_winter(self):
        assert is_winter_period(dt.date(2024, 6, 15)) is False

    def test_october_is_not_winter(self):
        assert is_winter_period(dt.date(2023, 10, 31)) is False


class TestMoratoriumRecord:
    def test_is_active_within_dates(self):
        r = make_record(start=dt.date(2023, 11, 1), end=dt.date(2024, 3, 31))
        assert r.is_active(dt.date(2024, 1, 15)) is True

    def test_is_active_false_before_start(self):
        r = make_record(start=dt.date(2023, 11, 1))
        assert r.is_active(dt.date(2023, 10, 1)) is False

    def test_is_active_false_after_end(self):
        r = make_record(start=dt.date(2023, 11, 1), end=dt.date(2024, 3, 31))
        assert r.is_active(dt.date(2024, 4, 1)) is False

    def test_is_active_true_ongoing_none_end(self):
        r = make_record(end=None, mtype=MoratoriumType.VULNERABLE_YEAR_ROUND)
        assert r.is_active(dt.date(2025, 7, 1)) is True

    def test_protection_status_protected(self):
        r = make_record()
        assert r.protection_status(dt.date(2024, 1, 1)) == DisconnectionRisk.PROTECTED

    def test_protection_status_no_risk_after_end(self):
        r = make_record(end=dt.date(2024, 3, 31))
        assert r.protection_status(dt.date(2024, 5, 1)) == DisconnectionRisk.NO_RISK

    def test_frozen(self):
        r = make_record()
        with pytest.raises((AttributeError, TypeError)):
            r.account_id = "X"


class TestWinterMoratoriumRegister:
    def test_register_and_active(self):
        reg = WinterMoratoriumRegister()
        reg.register(make_record())
        assert len(reg.active_protections(dt.date(2024, 1, 1))) == 1

    def test_end_moratorium(self):
        reg = WinterMoratoriumRegister()
        reg.register(make_record(account_id="A1", end=None,
                                 mtype=MoratoriumType.DEBT_MORATORIUM))
        result = reg.end_moratorium("A1", dt.date(2024, 4, 1))
        assert result is not None
        assert result.end_date == dt.date(2024, 4, 1)
        assert not reg.is_protected("A1", dt.date(2024, 5, 1))

    def test_is_protected_true(self):
        reg = WinterMoratoriumRegister()
        reg.register(make_record(account_id="A1"))
        assert reg.is_protected("A1", dt.date(2024, 1, 1)) is True

    def test_is_protected_false_after_end(self):
        reg = WinterMoratoriumRegister()
        reg.register(make_record(account_id="A1", end=dt.date(2024, 3, 31)))
        assert reg.is_protected("A1", dt.date(2024, 5, 1)) is False

    def test_can_disconnect_false_protected(self):
        reg = WinterMoratoriumRegister()
        reg.register(make_record(account_id="A1"))
        assert reg.can_disconnect("A1", dt.date(2024, 1, 1)) is False

    def test_can_disconnect_false_winter_period(self):
        reg = WinterMoratoriumRegister()
        assert reg.can_disconnect("B1", dt.date(2024, 1, 1)) is False

    def test_can_disconnect_true_summer(self):
        reg = WinterMoratoriumRegister()
        assert reg.can_disconnect("B1", dt.date(2024, 7, 1)) is True

    def test_vulnerable_protections(self):
        reg = WinterMoratoriumRegister()
        reg.register(make_record(account_id="A1", end=None,
                                 mtype=MoratoriumType.VULNERABLE_YEAR_ROUND))
        reg.register(make_record(account_id="A2"))
        assert len(reg.vulnerable_protections(dt.date(2024, 7, 1))) == 1

    def test_winter_protections(self):
        reg = WinterMoratoriumRegister()
        reg.register(make_record(account_id="A1"))
        assert len(reg.winter_protections(dt.date(2024, 1, 1))) == 1
        assert len(reg.winter_protections(dt.date(2024, 7, 1))) == 0

    def test_summary_keys(self):
        reg = WinterMoratoriumRegister()
        s = reg.moratorium_summary(dt.date(2024, 1, 1))
        for k in ("total_records", "active_protections", "vulnerable_year_round",
                  "winter_domestic", "in_winter_period"):
            assert k in s

    def test_summary_winter_flag(self):
        reg = WinterMoratoriumRegister()
        assert reg.moratorium_summary(dt.date(2024, 1, 1))["in_winter_period"] is True
        assert reg.moratorium_summary(dt.date(2024, 7, 1))["in_winter_period"] is False
