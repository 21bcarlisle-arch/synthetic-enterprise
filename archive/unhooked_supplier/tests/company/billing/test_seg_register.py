import datetime as dt
import pytest
from company.billing.seg_register import (
    SEGRegister, MicroGenerationType, SEGTariffType, SEGEligibilityStatus, SEGPaymentStatus,
)

COMM = dt.date(2021, 3, 15)


def _reg():
    r = SEGRegister()
    r.enrol_account("MPAN-E01", MicroGenerationType.SOLAR_PV, 4.0, COMM, 5.5, SEGTariffType.FIXED)
    return r


def test_account_id_prefix():
    reg = _reg()
    assert reg._accounts[0].account_id.startswith("SEG-")


def test_status_default_pending_verification():
    reg = _reg()
    assert reg._accounts[0].eligibility_status == SEGEligibilityStatus.PENDING_VERIFICATION


def test_mark_eligible_changes_status():
    reg = _reg()
    aid = reg._accounts[0].account_id
    updated = reg.mark_eligible(aid)
    assert updated.eligibility_status == SEGEligibilityStatus.ELIGIBLE


def test_before_2020_raises():
    reg = SEGRegister()
    with pytest.raises(ValueError):
        reg.enrol_account("M", MicroGenerationType.WIND, 1.0,
                          dt.date(2019, 12, 31), 4.0, SEGTariffType.FIXED)


def test_capacity_over_5mw_raises():
    reg = SEGRegister()
    with pytest.raises(ValueError):
        reg.enrol_account("M", MicroGenerationType.WIND, 5001.0, COMM, 4.0, SEGTariffType.FIXED)


def test_payment_id_prefix():
    reg = _reg()
    aid = reg._accounts[0].account_id
    reg.mark_eligible(aid)
    p = reg.record_payment(aid, dt.date(2022, 1, 1), dt.date(2022, 3, 31), 200.0)
    assert p.payment_id.startswith("SEGPAY-")


def test_payment_gbp_computed():
    reg = _reg()
    aid = reg._accounts[0].account_id
    reg.mark_eligible(aid)
    p = reg.record_payment(aid, dt.date(2022, 1, 1), dt.date(2022, 3, 31), 100.0)
    assert p.payment_gbp == pytest.approx(100.0 * 5.5 / 100.0)


def test_payment_on_ineligible_raises():
    reg = _reg()
    aid = reg._accounts[0].account_id
    with pytest.raises(ValueError):
        reg.record_payment(aid, dt.date(2022, 1, 1), dt.date(2022, 3, 31), 100.0)


def test_total_enrolled_capacity_sums_eligible():
    reg = _reg()
    aid = reg._accounts[0].account_id
    reg.mark_eligible(aid)
    assert reg.total_enrolled_capacity_kw == pytest.approx(4.0)


def test_average_tariff_rate_none_empty():
    reg = SEGRegister()
    assert reg.average_tariff_rate_pence() is None
