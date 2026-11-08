"""Phase HZ: coverage expansion for revenue_protection_register, interruptible_supply_register, otc_margin_book."""
import datetime as dt
import pytest

from company.billing.revenue_protection_register import (
    RevenueProtectionRegister, RPCaseType, RPCaseStatus
)

def _case(reg, cid="RP001", account="C1", ctype=RPCaseType.METER_TAMPERING, kwh=5000.0, gbp=800.0):
    return reg.open_case(cid, account, ctype, dt.date(2023, 3, 1), kwh, gbp)

class TestRevenueProtectionRegister:
    def test_open_case_suspected_status(self):
        reg = RevenueProtectionRegister()
        case = _case(reg)
        assert case.status == RPCaseStatus.SUSPECTED and case.is_active

    def test_confirm_sets_status(self):
        reg = RevenueProtectionRegister()
        _case(reg, "RP001")
        confirmed = reg.confirm("RP001", dt.date(2023, 3, 10))
        assert confirmed.status == RPCaseStatus.CONFIRMED

    def test_raise_estimated_bill(self):
        reg = RevenueProtectionRegister()
        _case(reg, "RP001")
        reg.confirm("RP001")
        billed = reg.raise_estimated_bill("RP001")
        assert billed.status == RPCaseStatus.ESTIMATED_BILL_RAISED and billed.is_recoverable

    def test_recover_closes_case(self):
        reg = RevenueProtectionRegister()
        _case(reg, "RP001")
        assert not reg.recover("RP001").is_active

    def test_write_off_closes_case(self):
        reg = RevenueProtectionRegister()
        _case(reg, "RP001")
        assert not reg.write_off("RP001").is_active

    def test_active_cases_excludes_closed(self):
        reg = RevenueProtectionRegister()
        _case(reg, "RP001"); _case(reg, "RP002")
        reg.recover("RP001")
        assert len(reg.active_cases) == 1

    def test_total_estimated_loss_gbp(self):
        reg = RevenueProtectionRegister()
        _case(reg, "RP001", gbp=800.0); _case(reg, "RP002", gbp=500.0)
        reg.recover("RP001")
        assert reg.total_estimated_loss_gbp == pytest.approx(500.0)

    def test_cases_by_type(self):
        reg = RevenueProtectionRegister()
        _case(reg, "RP001", ctype=RPCaseType.METER_TAMPERING)
        _case(reg, "RP002", ctype=RPCaseType.ILLEGAL_RECONNECTION)
        _case(reg, "RP003", ctype=RPCaseType.METER_TAMPERING)
        bd = reg.cases_by_type()
        assert bd["meter_tampering"] == 2 and bd["illegal_reconnection"] == 1

    def test_confirmed_cases_filter(self):
        reg = RevenueProtectionRegister()
        _case(reg, "RP001"); reg.confirm("RP001")
        _case(reg, "RP002")
        assert len(reg.confirmed_cases) == 1

    def test_revenue_protection_summary_keys(self):
        reg = RevenueProtectionRegister()
        _case(reg)
        s = reg.revenue_protection_summary()
        assert "Revenue Protection" in s and "Active" in s
