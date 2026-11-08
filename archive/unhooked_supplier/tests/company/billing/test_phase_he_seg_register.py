"""Tests for Smart Export Guarantee (SEG) Register -- Phase HE (SI 2020/1297)."""
import datetime as dt
import pytest
from company.billing.seg_register import (
    MicroGenerationType, SEGTariffType, SEGEligibilityStatus, SEGPaymentStatus,
    SEGAccount, SEGPaymentRecord, SEGRegister,
    _SEG_START_DATE, _MAX_CAPACITY_KW,
)

COMMISSIONING = dt.date(2021, 3, 15)
PERIOD_START = dt.date(2024, 1, 1)
PERIOD_END = dt.date(2024, 3, 31)
MPAN = "1900000000001"


def make_reg():
    return SEGRegister()


def enrol(reg=None, mpan=MPAN, gen_type=MicroGenerationType.SOLAR_PV, capacity=4.0,
          date=COMMISSIONING, rate=5.5, tariff=SEGTariffType.FIXED, smets2=True):
    if reg is None:
        reg = make_reg()
    return reg, reg.enrol_account(mpan, gen_type, capacity, date, rate, tariff, smets2)


class TestSEGAccount:
    def test_is_not_eligible_when_pending(self):
        _, a = enrol()
        assert not a.is_eligible

    def test_is_eligible_after_mark(self):
        reg, a = enrol()
        reg.mark_eligible(a.account_id)
        result = reg.eligible_accounts[0]
        assert result.is_eligible

    def test_is_capacity_compliant_within_range(self):
        _, a = enrol(capacity=3.5)
        assert a.is_capacity_compliant

    def test_is_not_capacity_compliant_above_5mw(self):
        with pytest.raises(ValueError):
            enrol(capacity=5001.0)

    def test_annual_estimated_export_gbp_when_eligible(self):
        reg, a = enrol(rate=5.0)
        reg.mark_eligible(a.account_id)
        result = reg.eligible_accounts[0]
        assert abs(result.annual_estimated_export_gbp(1000.0) - 50.0) < 1e-9

    def test_annual_estimated_export_zero_when_not_eligible(self):
        _, a = enrol(rate=5.0)
        assert a.annual_estimated_export_gbp(1000.0) == 0.0

    def test_account_summary_contains_id(self):
        _, a = enrol()
        assert a.account_id in a.account_summary()

    def test_frozen(self):
        _, a = enrol()
        with pytest.raises((AttributeError, TypeError)):
            a.export_mpan = "other"


class TestSEGPaymentRecord:
    def test_is_not_paid_when_pending(self):
        reg, a = enrol()
        reg.mark_eligible(a.account_id)
        p = reg.record_payment(a.account_id, PERIOD_START, PERIOD_END, 500.0)
        assert not p.is_paid

    def test_is_paid_after_mark(self):
        reg, a = enrol()
        reg.mark_eligible(a.account_id)
        p = reg.record_payment(a.account_id, PERIOD_START, PERIOD_END, 500.0)
        paid = reg.mark_payment_paid(p.payment_id)
        assert paid.is_paid

    def test_frozen(self):
        reg, a = enrol()
        reg.mark_eligible(a.account_id)
        p = reg.record_payment(a.account_id, PERIOD_START, PERIOD_END, 500.0)
        with pytest.raises((AttributeError, TypeError)):
            p.account_id = "other"


class TestSEGRegister:
    def setup_method(self):
        self.reg = make_reg()

    def _enrol(self, mpan=MPAN, gen_type=MicroGenerationType.SOLAR_PV, capacity=4.0,
               date=COMMISSIONING, rate=5.5, tariff=SEGTariffType.FIXED, smets2=True):
        return self.reg.enrol_account(mpan, gen_type, capacity, date, rate, tariff, smets2)

    def test_enrol_returns_pending(self):
        a = self._enrol()
        assert a.eligibility_status == SEGEligibilityStatus.PENDING_VERIFICATION

    def test_auto_id_prefix(self):
        a = self._enrol()
        assert a.account_id.startswith("SEG-")

    def test_auto_id_increments(self):
        a1 = self._enrol(mpan=MPAN)
        a2 = self._enrol(mpan="1900000000002")
        assert a1.account_id != a2.account_id

    def test_pre_seg_date_raises(self):
        with pytest.raises(ValueError):
            self._enrol(date=dt.date(2019, 12, 31))

    def test_zero_capacity_raises(self):
        with pytest.raises(ValueError):
            self._enrol(capacity=0.0)

    def test_above_5mw_raises(self):
        with pytest.raises(ValueError):
            self._enrol(capacity=5001.0)

    def test_negative_rate_raises(self):
        with pytest.raises(ValueError):
            self._enrol(rate=-1.0)

    def test_mark_eligible(self):
        a = self._enrol()
        eligible = self.reg.mark_eligible(a.account_id)
        assert eligible.eligibility_status == SEGEligibilityStatus.ELIGIBLE

    def test_mark_ineligible(self):
        a = self._enrol()
        ineligible = self.reg.mark_ineligible(a.account_id)
        assert ineligible.eligibility_status == SEGEligibilityStatus.INELIGIBLE

    def test_suspend_eligible(self):
        a = self._enrol()
        self.reg.mark_eligible(a.account_id)
        suspended = self.reg.suspend(a.account_id)
        assert suspended.eligibility_status == SEGEligibilityStatus.SUSPENDED

    def test_suspend_non_eligible_raises(self):
        a = self._enrol()
        with pytest.raises(ValueError):
            self.reg.suspend(a.account_id)

    def test_record_payment_computes_amount(self):
        a = self._enrol(rate=5.0)
        self.reg.mark_eligible(a.account_id)
        p = self.reg.record_payment(a.account_id, PERIOD_START, PERIOD_END, 1000.0)
        assert abs(p.payment_gbp - 50.0) < 1e-9

    def test_record_payment_ineligible_raises(self):
        a = self._enrol()
        with pytest.raises(ValueError):
            self.reg.record_payment(a.account_id, PERIOD_START, PERIOD_END, 500.0)

    def test_record_payment_negative_kwh_raises(self):
        a = self._enrol()
        self.reg.mark_eligible(a.account_id)
        with pytest.raises(ValueError):
            self.reg.record_payment(a.account_id, PERIOD_START, PERIOD_END, -1.0)

    def test_record_payment_custom_rate(self):
        a = self._enrol(rate=5.0)
        self.reg.mark_eligible(a.account_id)
        p = self.reg.record_payment(a.account_id, PERIOD_START, PERIOD_END, 1000.0, 6.0)
        assert abs(p.payment_gbp - 60.0) < 1e-9

    def test_mark_payment_paid(self):
        a = self._enrol(rate=5.0)
        self.reg.mark_eligible(a.account_id)
        p = self.reg.record_payment(a.account_id, PERIOD_START, PERIOD_END, 500.0)
        paid = self.reg.mark_payment_paid(p.payment_id)
        assert paid.is_paid

    def test_dispute_payment(self):
        a = self._enrol(rate=5.0)
        self.reg.mark_eligible(a.account_id)
        p = self.reg.record_payment(a.account_id, PERIOD_START, PERIOD_END, 500.0)
        disputed = self.reg.dispute_payment(p.payment_id)
        assert disputed.status == SEGPaymentStatus.DISPUTED

    def test_eligible_accounts(self):
        a1 = self._enrol(mpan=MPAN)
        a2 = self._enrol(mpan="1900000000002")
        self.reg.mark_eligible(a1.account_id)
        assert len(self.reg.eligible_accounts) == 1

    def test_pending_verification_accounts(self):
        self._enrol()
        self._enrol(mpan="1900000000002")
        assert len(self.reg.pending_verification_accounts) == 2

    def test_accounts_by_generation_type(self):
        self._enrol(gen_type=MicroGenerationType.SOLAR_PV)
        self._enrol(mpan="1900000000002", gen_type=MicroGenerationType.WIND)
        assert len(self.reg.accounts_by_generation_type(MicroGenerationType.WIND)) == 1

    def test_total_enrolled_capacity_kw(self):
        a1 = self._enrol(mpan=MPAN, capacity=3.0)
        a2 = self._enrol(mpan="1900000000002", capacity=2.0)
        self.reg.mark_eligible(a1.account_id)
        self.reg.mark_eligible(a2.account_id)
        assert abs(self.reg.total_enrolled_capacity_kw - 5.0) < 1e-9

    def test_total_export_payments_gbp_paid_only(self):
        a = self._enrol(rate=5.0)
        self.reg.mark_eligible(a.account_id)
        p1 = self.reg.record_payment(a.account_id, PERIOD_START, PERIOD_END, 1000.0)
        self.reg.record_payment(a.account_id, PERIOD_START, PERIOD_END, 2000.0)
        self.reg.mark_payment_paid(p1.payment_id)
        assert abs(self.reg.total_export_payments_gbp() - 50.0) < 1e-9

    def test_average_tariff_rate_pence_none_when_empty(self):
        assert self.reg.average_tariff_rate_pence() is None

    def test_average_tariff_rate_pence(self):
        a1 = self._enrol(mpan=MPAN, rate=4.0)
        a2 = self._enrol(mpan="1900000000002", rate=6.0)
        self.reg.mark_eligible(a1.account_id)
        self.reg.mark_eligible(a2.account_id)
        assert abs(self.reg.average_tariff_rate_pence() - 5.0) < 1e-9

    def test_seg_summary_contains_total(self):
        self._enrol()
        s = self.reg.seg_summary()
        assert "1 enrolled" in s

    def test_empty_summary(self):
        s = self.reg.seg_summary()
        assert "0 enrolled" in s
