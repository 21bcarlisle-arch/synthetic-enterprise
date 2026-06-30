"""Phase CZ: Revenue Protection Register tests."""
import pytest
from datetime import date
from company.billing.revenue_protection_register import (
    RevenueProtectionRegister, RPCaseType, RPCaseStatus
)

_D = date(2022, 6, 1)


def _reg_with_case():
    r = RevenueProtectionRegister()
    c = r.open_case("RP001", "C_IC1", RPCaseType.METER_TAMPERING, _D, 15_000, 3_000.0)
    return r, c


# 1. open_case creates SUSPECTED case
def test_open_case():
    r, c = _reg_with_case()
    assert c.status == RPCaseStatus.SUSPECTED
    assert c.is_active


# 2. confirm changes status
def test_confirm():
    r, c = _reg_with_case()
    confirmed = r.confirm("RP001", backbill_start_date=date(2021, 6, 1))
    assert confirmed.status == RPCaseStatus.CONFIRMED
    assert confirmed.backbill_start_date == date(2021, 6, 1)


# 3. raise_estimated_bill
def test_raise_bill():
    r, c = _reg_with_case()
    billed = r.raise_estimated_bill("RP001")
    assert billed.status == RPCaseStatus.ESTIMATED_BILL_RAISED
    assert billed.is_recoverable


# 4. recover
def test_recover():
    r, c = _reg_with_case()
    recovered = r.recover("RP001")
    assert not recovered.is_active


# 5. write_off
def test_write_off():
    r, c = _reg_with_case()
    written_off = r.write_off("RP001")
    assert not written_off.is_active


# 6. active_cases excludes recovered and written_off
def test_active_cases():
    r = RevenueProtectionRegister()
    r.open_case("RP001", "A1", RPCaseType.METER_TAMPERING, _D, 5_000, 1_000)
    r.open_case("RP002", "A2", RPCaseType.ILLEGAL_RECONNECTION, _D, 3_000, 600)
    r.recover("RP001")
    assert len(r.active_cases) == 1


# 7. total_estimated_loss_gbp sums active only
def test_total_loss_gbp():
    r = RevenueProtectionRegister()
    r.open_case("RP001", "A1", RPCaseType.METER_TAMPERING, _D, 5_000, 1_000.0)
    r.open_case("RP002", "A2", RPCaseType.METER_BYPASS, _D, 3_000, 600.0)
    r.write_off("RP001")
    assert abs(r.total_estimated_loss_gbp - 600.0) < 0.01


# 8. total_estimated_loss_kwh
def test_total_loss_kwh():
    r, c = _reg_with_case()
    assert r.total_estimated_loss_kwh == 15_000


# 9. confirmed_cases filtered
def test_confirmed_cases():
    r, c = _reg_with_case()
    r.confirm("RP001")
    assert len(r.confirmed_cases) == 1


# 10. cases_by_type counts correctly
def test_cases_by_type():
    r = RevenueProtectionRegister()
    r.open_case("RP001", "A", RPCaseType.METER_TAMPERING, _D, 1_000, 200)
    r.open_case("RP002", "B", RPCaseType.METER_TAMPERING, _D, 1_000, 200)
    r.open_case("RP003", "C", RPCaseType.ILLEGAL_RECONNECTION, _D, 1_000, 200)
    by_type = r.cases_by_type()
    assert by_type["meter_tampering"] == 2
    assert by_type["illegal_reconnection"] == 1


# 11. supply_diversion case type accepted
def test_supply_diversion():
    r = RevenueProtectionRegister()
    c = r.open_case("RP001", "A", RPCaseType.SUPPLY_DIVERSION, _D, 20_000, 4_000)
    assert c.case_type == RPCaseType.SUPPLY_DIVERSION


# 12. revenue_protection_summary contains key fields
def test_summary():
    r, c = _reg_with_case()
    summary = r.revenue_protection_summary()
    assert "Revenue Protection" in summary
    assert "Active" in summary
