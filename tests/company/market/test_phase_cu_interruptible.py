"""Phase CU: Interruptible Gas Supply Register tests."""
import pytest
from datetime import date
from company.market.interruptible_supply_register import (
    InterruptibleSupplyRegister, InterruptionReason, SupplyFirmness
)

_D = date(2022, 1, 15)


def _reg_with_contract():
    r = InterruptibleSupplyRegister()
    c = r.register("C_IC1g", date(2020, 1, 1), annual_kwh=500_000)
    return r, c


# 1. register creates contract
def test_register():
    r, c = _reg_with_contract()
    assert c.account_id == "C_IC1g"
    assert c.annual_kwh == 500_000


# 2. interruptible_accounts returns IDs
def test_interruptible_accounts():
    r, c = _reg_with_contract()
    assert "C_IC1g" in r.interruptible_accounts


# 3. saving_vs_firm_gbp_pa at 15% discount
def test_saving():
    r, c = _reg_with_contract()
    # 500,000 * 0.04 * 0.15 = 3,000
    assert abs(c.saving_vs_firm_gbp_pa - 3_000) < 1


# 4. record_interruption creates event
def test_record_interruption():
    r, c = _reg_with_contract()
    ev = r.record_interruption(_D, "C_IC1g", InterruptionReason.COLD_WEATHER, 10_000, 4.0)
    assert ev.curtailment_kwh == 10_000


# 5. notice_compliant True when notice >= 2h
def test_notice_compliant():
    r, c = _reg_with_contract()
    ev = r.record_interruption(_D, "C_IC1g", InterruptionReason.NGT_INSTRUCTION, 5_000, 2.0)
    assert ev.notice_compliant


# 6. notice_compliant False when notice < 2h
def test_notice_violation():
    r, c = _reg_with_contract()
    ev = r.record_interruption(_D, "C_IC1g", InterruptionReason.SUPPLIER_DISCRETION, 5_000, 1.5)
    assert not ev.notice_compliant


# 7. notice_violations property
def test_notice_violations_property():
    r, c = _reg_with_contract()
    r.record_interruption(_D, "C_IC1g", InterruptionReason.COLD_WEATHER, 5_000, 4.0)  # ok
    r.record_interruption(date(2022, 1, 16), "C_IC1g", InterruptionReason.COLD_WEATHER, 5_000, 1.0)  # violation
    assert len(r.notice_violations) == 1


# 8. annual_curtailment_days counts distinct days
def test_annual_curtailment_days():
    r, c = _reg_with_contract()
    r.record_interruption(date(2022, 1, 5), "C_IC1g", InterruptionReason.COLD_WEATHER, 5_000, 2.0)
    r.record_interruption(date(2022, 1, 5), "C_IC1g", InterruptionReason.COLD_WEATHER, 2_000, 2.0)  # same day
    r.record_interruption(date(2022, 1, 6), "C_IC1g", InterruptionReason.COLD_WEATHER, 5_000, 2.0)
    assert r.annual_curtailment_days("C_IC1g", 2022) == 2


# 9. over_cap_accounts returns accounts exceeding 30 days
def test_over_cap():
    r = InterruptibleSupplyRegister()
    r.register("A1", date(2020, 1, 1), 100_000)
    for day in range(1, 32):  # 31 days
        r.record_interruption(date(2022, 1, day), "A1", InterruptionReason.COLD_WEATHER, 100, 2.0)
    assert "A1" in r.over_cap_accounts(2022)


# 10. over_cap_accounts empty when within 30 days
def test_within_cap():
    r, c = _reg_with_contract()
    for day in range(1, 29):
        r.record_interruption(date(2022, 1, day), "C_IC1g", InterruptionReason.COLD_WEATHER, 100, 2.0)
    assert len(r.over_cap_accounts(2022)) == 0


# 11. total_portfolio_annual_kwh
def test_total_portfolio():
    r = InterruptibleSupplyRegister()
    r.register("A", date(2020, 1, 1), 200_000)
    r.register("B", date(2020, 1, 1), 300_000)
    assert r.total_portfolio_annual_kwh == 500_000


# 12. events_for_account filters correctly
def test_events_for_account():
    r = InterruptibleSupplyRegister()
    r.register("A", date(2020, 1, 1), 100_000)
    r.register("B", date(2020, 1, 1), 100_000)
    r.record_interruption(_D, "A", InterruptionReason.COLD_WEATHER, 500, 2.0)
    r.record_interruption(_D, "B", InterruptionReason.COLD_WEATHER, 500, 2.0)
    assert len(r.events_for_account("A")) == 1


# 13. interruptible_summary contains UNC
def test_summary():
    r, c = _reg_with_contract()
    summary = r.interruptible_summary()
    assert "UNC" in summary
    assert "INT" in summary
