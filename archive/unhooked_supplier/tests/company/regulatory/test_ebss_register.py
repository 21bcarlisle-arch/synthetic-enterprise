"""Tests: Phase DE — Energy Bills Support Scheme (EBSS) Register."""
import datetime as dt
import pytest
from company.regulatory.ebss_register import (
    EBSSRegister, EBSSInstalment, EBSSDeliveryMethod, EBSSRedemptionStatus,
    _EBSS_INSTALMENT_SCHEDULE, _EBSS_TOTAL_GBP, _EBSS_MONTHS,
    _instalment_amount, _delivery_method_for,
)

_APPLIED = dt.date(2022, 10, 15)


def _reg():
    return EBSSRegister()


def _apply_standard(reg, customer_id="C1", year=2022, month=10):
    return reg.apply_instalment(customer_id, year, month, _APPLIED)


def _apply_ppm(reg, customer_id="C2", year=2022, month=10):
    return reg.apply_instalment(customer_id, year, month, _APPLIED, is_ppm=True)


def _apply_smart_ppm(reg, customer_id="C3", year=2022, month=10):
    return reg.apply_instalment(customer_id, year, month, _APPLIED, is_ppm=True, is_smart_ppm=True)


# ── schedule ─────────────────────────────────────────────────────────────────

def test_schedule_6_months():
    assert len(_EBSS_MONTHS) == 6

def test_october_amount():
    assert _instalment_amount(10) == 66.0

def test_november_amount():
    assert _instalment_amount(11) == 67.0

def test_total_instalment_sum():
    total = sum(_instalment_amount(m) for (_, m) in _EBSS_MONTHS)
    assert total == 397.0  # 66*5 + 67

def test_outside_schedule_raises():
    reg = _reg()
    with pytest.raises(ValueError):
        reg.apply_instalment("C1", 2023, 4, _APPLIED)

def test_outside_schedule_2022_sep_raises():
    reg = _reg()
    with pytest.raises(ValueError):
        reg.apply_instalment("C1", 2022, 9, _APPLIED)


# ── delivery methods ─────────────────────────────────────────────────────────

def test_standard_delivery_automatic():
    assert _delivery_method_for(False, False) == EBSSDeliveryMethod.AUTOMATIC_CREDIT

def test_legacy_ppm_delivery_voucher():
    assert _delivery_method_for(True, False) == EBSSDeliveryMethod.VOUCHER

def test_smart_ppm_delivery():
    assert _delivery_method_for(True, True) == EBSSDeliveryMethod.SMART_PPM_CREDIT


# ── apply_instalment ─────────────────────────────────────────────────────────

def test_standard_status_applied():
    reg = _reg()
    i = _apply_standard(reg)
    assert i.redemption_status == EBSSRedemptionStatus.APPLIED
    assert i.delivery_method == EBSSDeliveryMethod.AUTOMATIC_CREDIT

def test_ppm_status_voucher_issued():
    reg = _reg()
    i = _apply_ppm(reg)
    assert i.redemption_status == EBSSRedemptionStatus.VOUCHER_ISSUED
    assert i.delivery_method == EBSSDeliveryMethod.VOUCHER

def test_smart_ppm_status():
    reg = _reg()
    i = _apply_smart_ppm(reg)
    assert i.redemption_status == EBSSRedemptionStatus.SMART_PPM_CREDIT

def test_amount_assigned():
    reg = _reg()
    i = _apply_standard(reg, month=11)  # November = 67
    assert i.amount_gbp == 67.0

def test_assigns_ids():
    reg = _reg()
    i1 = _apply_standard(reg)
    i2 = _apply_standard(reg, month=11)
    assert i1.instalment_id == "EBSS-00001"
    assert i2.instalment_id == "EBSS-00002"

def test_billing_month_property():
    reg = _reg()
    i = _apply_standard(reg, year=2022, month=10)
    assert i.billing_month == dt.date(2022, 10, 1)


# ── is_delivered / is_unredeemed ─────────────────────────────────────────────

def test_standard_is_delivered():
    reg = _reg()
    i = _apply_standard(reg)
    assert i.is_delivered is True

def test_voucher_issued_not_delivered():
    reg = _reg()
    i = _apply_ppm(reg)
    assert i.is_delivered is False
    assert i.is_unredeemed_voucher is True


# ── redeem / expire voucher ──────────────────────────────────────────────────

def test_redeem_voucher():
    reg = _reg()
    i = _apply_ppm(reg)
    updated = reg.redeem_voucher(i.instalment_id)
    assert updated.redemption_status == EBSSRedemptionStatus.VOUCHER_REDEEMED
    assert updated.is_delivered is True

def test_expire_voucher():
    reg = _reg()
    i = _apply_ppm(reg)
    updated = reg.expire_voucher(i.instalment_id)
    assert updated.redemption_status == EBSSRedemptionStatus.VOUCHER_EXPIRED
    assert updated.is_unredeemed_voucher is True


# ── mark_recovered ───────────────────────────────────────────────────────────

def test_mark_recovered():
    reg = _reg()
    i = _apply_standard(reg)
    updated = reg.mark_recovered(i.instalment_id, government_ref="DESNZ-001")
    assert updated.is_recovered_from_government is True
    assert updated.government_recovery_ref == "DESNZ-001"


# ── queries ──────────────────────────────────────────────────────────────────

def test_total_applied_gbp():
    reg = _reg()
    _apply_standard(reg, month=10)  # 66
    _apply_standard(reg, month=11)  # 67
    assert abs(reg.total_applied_gbp - 133.0) < 0.01

def test_total_recovered():
    reg = _reg()
    i = _apply_standard(reg)
    reg.mark_recovered(i.instalment_id, "GOV-001")
    assert abs(reg.total_recovered_gbp - 66.0) < 0.01

def test_unredeemed_vouchers():
    reg = _reg()
    _apply_standard(reg)   # auto credit - not a voucher
    _apply_ppm(reg)        # voucher issued - unredeemed
    assert len(reg.unredeemed_vouchers) == 1

def test_expired_vouchers():
    reg = _reg()
    i = _apply_ppm(reg)
    reg.expire_voucher(i.instalment_id)
    assert len(reg.expired_vouchers) == 1

def test_instalments_for_customer():
    reg = _reg()
    _apply_standard(reg, customer_id="C1", month=10)
    _apply_standard(reg, customer_id="C1", month=11)
    _apply_standard(reg, customer_id="C2", month=10)
    assert len(reg.instalments_for_customer("C1")) == 2
    assert len(reg.instalments_for_customer("C2")) == 1

def test_total_for_customer():
    reg = _reg()
    _apply_standard(reg, customer_id="C1", month=10)   # 66
    _apply_standard(reg, customer_id="C1", month=11)   # 67
    assert abs(reg.total_for_customer("C1") - 133.0) < 0.01

def test_by_delivery_method():
    reg = _reg()
    _apply_standard(reg)
    _apply_ppm(reg)
    _apply_smart_ppm(reg)
    by_method = reg.by_delivery_method()
    assert by_method["automatic_credit"] == 1
    assert by_method["voucher"] == 1
    assert by_method["smart_ppm_credit"] == 1

def test_ebss_summary_format():
    reg = _reg()
    _apply_standard(reg)
    s = reg.ebss_summary()
    assert "EBSS" in s
    assert "Oct22" in s
    assert "Unredeemed" in s
    assert "GBP66" in s
