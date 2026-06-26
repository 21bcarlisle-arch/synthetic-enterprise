import datetime as dt
import pytest
from company.billing.whd_register import (
    WHDEligibilityReason, WHDStatus, WHDApplication, WHDRegister, WHD_REBATE_GBP
)

D = dt.date


def test_apply_core_group():
    reg = WHDRegister()
    app = reg.apply('C001', 2022, WHDEligibilityReason.CORE_GROUP, D(2022, 12, 1))
    assert app.status == WHDStatus.APPLIED
    assert app.rebate_gbp == WHD_REBATE_GBP
    assert app.scheme_year == 2022


def test_duplicate_application_raises():
    reg = WHDRegister()
    reg.apply('C001', 2022, WHDEligibilityReason.CORE_GROUP, D(2022, 12, 1))
    with pytest.raises(ValueError):
        reg.apply('C001', 2022, WHDEligibilityReason.CORE_GROUP, D(2022, 12, 5))


def test_same_customer_different_year_ok():
    reg = WHDRegister()
    reg.apply('C001', 2022, WHDEligibilityReason.CORE_GROUP, D(2022, 12, 1))
    app2 = reg.apply('C001', 2023, WHDEligibilityReason.CORE_GROUP, D(2023, 11, 1))
    assert app2.scheme_year == 2023


def test_mark_rebated():
    reg = WHDRegister()
    app = reg.apply('C002', 2023, WHDEligibilityReason.BROADER_GROUP_LIHC, D(2023, 11, 1))
    updated = reg.mark_rebated(app.application_id, D(2024, 2, 1))
    assert updated.status == WHDStatus.REBATED
    assert updated.rebated_date == D(2024, 2, 1)


def test_pending_rebates():
    reg = WHDRegister()
    a1 = reg.apply('C001', 2023, WHDEligibilityReason.CORE_GROUP, D(2023, 11, 1))
    a2 = reg.apply('C002', 2023, WHDEligibilityReason.BROADER_GROUP_PSR, D(2023, 11, 1))
    reg.mark_rebated(a1.application_id, D(2024, 1, 15))
    pending = reg.pending_rebates()
    assert len(pending) == 1
    assert pending[0].customer_id == 'C002'


def test_total_rebated_gbp_by_year():
    reg = WHDRegister()
    a1 = reg.apply('C001', 2023, WHDEligibilityReason.CORE_GROUP, D(2023, 11, 1))
    a2 = reg.apply('C002', 2023, WHDEligibilityReason.BROADER_GROUP_LIHC, D(2023, 11, 1))
    a3 = reg.apply('C003', 2022, WHDEligibilityReason.CORE_GROUP, D(2022, 11, 1))
    reg.mark_rebated(a1.application_id, D(2024, 1, 15))
    reg.mark_rebated(a2.application_id, D(2024, 1, 16))
    reg.mark_rebated(a3.application_id, D(2023, 1, 15))
    assert reg.total_rebated_gbp(2023) == pytest.approx(300.0)
    assert reg.total_rebated_gbp(2022) == pytest.approx(150.0)


def test_applications_for_customer():
    reg = WHDRegister()
    reg.apply('C001', 2021, WHDEligibilityReason.CORE_GROUP, D(2021, 12, 1))
    reg.apply('C001', 2022, WHDEligibilityReason.CORE_GROUP, D(2022, 12, 1))
    reg.apply('C002', 2022, WHDEligibilityReason.BROADER_GROUP_LIHC, D(2022, 12, 1))
    assert len(reg.applications_for_customer('C001')) == 2
    assert len(reg.applications_for_customer('C002')) == 1


def test_annual_summary():
    reg = WHDRegister()
    a1 = reg.apply('C001', 2023, WHDEligibilityReason.CORE_GROUP, D(2023, 11, 1))
    reg.apply('C002', 2023, WHDEligibilityReason.BROADER_GROUP_LIHC, D(2023, 11, 1))
    reg.mark_rebated(a1.application_id, D(2024, 1, 15))
    s = reg.annual_summary(2023)
    assert s['total_applications'] == 2
    assert s['total_rebated'] == 1
    assert s['pending'] == 1
    assert s['total_rebated_gbp'] == pytest.approx(150.0)


def test_annual_summary_by_reason():
    reg = WHDRegister()
    reg.apply('C001', 2023, WHDEligibilityReason.CORE_GROUP, D(2023, 11, 1))
    reg.apply('C002', 2023, WHDEligibilityReason.BROADER_GROUP_LIHC, D(2023, 11, 1))
    reg.apply('C003', 2023, WHDEligibilityReason.BROADER_GROUP_LIHC, D(2023, 11, 1))
    s = reg.annual_summary(2023)
    assert s['by_eligibility_reason']['core_group'] == 1
    assert s['by_eligibility_reason']['broader_group_lihc'] == 2


def test_application_id_unique():
    reg = WHDRegister()
    a1 = reg.apply('C001', 2022, WHDEligibilityReason.CORE_GROUP, D(2022, 12, 1))
    a2 = reg.apply('C002', 2022, WHDEligibilityReason.CORE_GROUP, D(2022, 12, 1))
    assert a1.application_id != a2.application_id


def test_custom_rebate_amount():
    reg = WHDRegister()
    app = reg.apply('C001', 2024, WHDEligibilityReason.INDUSTRY_INITIATIVE,
                    D(2024, 10, 1), rebate_gbp=200.0)
    assert app.rebate_gbp == 200.0
