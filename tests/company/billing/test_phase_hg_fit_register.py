"""Tests for FiT Legacy Register -- Phase HG (FIT Regulations 2010)."""
import datetime as dt
import pytest
from company.billing.fit_legacy_register import (
    FITTechnology, FITPaymentType, FITPaymentStatus,
    FITLegacyRecord, FITPaymentRecord, FITLegacyRegister,
    _FIT_SCHEME_CLOSE, _FIT_TERM_YEARS, _DEEMED_EXPORT_FRACTION,
)

TODAY = dt.date(2024, 6, 10)
COMMISSIONING = dt.date(2012, 4, 1)
MPAN = "1000000000001"
ACC = "A001"
PERIOD_START = dt.date(2024, 1, 1)
PERIOD_END = dt.date(2024, 3, 31)


def make_reg():
    return FITLegacyRegister()


def register(reg=None, account=ACC, mpan=MPAN, tech=FITTechnology.SOLAR_PV,
             capacity=4.0, commissioning=COMMISSIONING, gen_rate=14.38,
             exp_rate=5.24, has_meter=True):
    if reg is None:
        reg = make_reg()
    return reg, reg.register_fit_customer(
        account, mpan, tech, capacity, commissioning, gen_rate, exp_rate, has_meter
    )


class TestFITLegacyRecord:
    def test_is_active_within_term(self):
        _, rec = register()
        assert rec.is_active_as_of(TODAY)

    def test_is_not_active_before_commissioning(self):
        _, rec = register()
        assert not rec.is_active_as_of(dt.date(2011, 1, 1))

    def test_is_expired_after_term(self):
        _, rec = register()
        far_future = dt.date(2045, 1, 1)
        assert rec.is_expired_as_of(far_future)

    def test_is_not_expired_within_term(self):
        _, rec = register()
        assert not rec.is_expired_as_of(TODAY)

    def test_term_end_is_20_years(self):
        _, rec = register(commissioning=dt.date(2015, 6, 1))
        assert rec.term_end_date == dt.date(2035, 6, 1)

    def test_years_remaining_positive_within_term(self):
        _, rec = register()
        assert rec.years_remaining(TODAY) > 0

    def test_years_remaining_zero_when_expired(self):
        _, rec = register()
        assert rec.years_remaining(dt.date(2045, 1, 1)) == 0.0

    def test_is_deemed_export_when_no_meter(self):
        _, rec = register(has_meter=False)
        assert rec.is_deemed_export

    def test_is_not_deemed_export_with_meter(self):
        _, rec = register(has_meter=True)
        assert not rec.is_deemed_export

    def test_annual_generation_estimate(self):
        _, rec = register(gen_rate=14.38)
        est = rec.annual_generation_payment_estimate_gbp(3500.0)
        assert abs(est - 3500.0 * 14.38 / 100.0) < 0.01

    def test_fit_summary_contains_account_id(self):
        _, rec = register()
        assert rec.account_id in rec.fit_summary()

    def test_frozen(self):
        _, rec = register()
        with pytest.raises((AttributeError, TypeError)):
            rec.account_id = "other"


class TestFITLegacyRegister:
    def setup_method(self):
        self.reg = make_reg()

    def _register(self, account=ACC, mpan=MPAN, tech=FITTechnology.SOLAR_PV,
                  capacity=4.0, commissioning=COMMISSIONING, gen_rate=14.38,
                  exp_rate=5.24, has_meter=True):
        return self.reg.register_fit_customer(
            account, mpan, tech, capacity, commissioning, gen_rate, exp_rate, has_meter
        )

    def test_post_close_date_raises(self):
        with pytest.raises(ValueError):
            self._register(commissioning=dt.date(2019, 4, 1))

    def test_zero_capacity_raises(self):
        with pytest.raises(ValueError):
            self._register(capacity=0.0)

    def test_negative_gen_rate_raises(self):
        with pytest.raises(ValueError):
            self._register(gen_rate=-1.0)

    def test_term_end_calculated(self):
        rec = self._register(commissioning=dt.date(2014, 3, 15))
        assert rec.term_end_date == dt.date(2034, 3, 15)

    def test_record_generation_payment(self):
        rec = self._register(gen_rate=14.38)
        p = self.reg.record_payment(rec.account_id, FITPaymentType.GENERATION,
                                    PERIOD_START, PERIOD_END, 875.0)
        assert abs(p.payment_gbp - 875.0 * 14.38 / 100.0) < 0.01

    def test_record_export_payment_with_meter(self):
        rec = self._register(exp_rate=5.24, has_meter=True)
        p = self.reg.record_payment(rec.account_id, FITPaymentType.EXPORT,
                                    PERIOD_START, PERIOD_END, 400.0)
        assert abs(p.payment_gbp - 400.0 * 5.24 / 100.0) < 0.01

    def test_record_export_payment_deemed(self):
        rec = self._register(exp_rate=5.24, has_meter=False)
        p = self.reg.record_payment(rec.account_id, FITPaymentType.EXPORT,
                                    PERIOD_START, PERIOD_END, 1000.0)
        expected = 1000.0 * _DEEMED_EXPORT_FRACTION * 5.24 / 100.0
        assert abs(p.payment_gbp - expected) < 0.01

    def test_record_payment_unknown_account_raises(self):
        with pytest.raises(KeyError):
            self.reg.record_payment("UNKNOWN", FITPaymentType.GENERATION,
                                    PERIOD_START, PERIOD_END, 500.0)

    def test_record_payment_negative_kwh_raises(self):
        rec = self._register()
        with pytest.raises(ValueError):
            self.reg.record_payment(rec.account_id, FITPaymentType.GENERATION,
                                    PERIOD_START, PERIOD_END, -100.0)

    def test_mark_paid(self):
        rec = self._register()
        p = self.reg.record_payment(rec.account_id, FITPaymentType.GENERATION,
                                    PERIOD_START, PERIOD_END, 500.0)
        paid = self.reg.mark_paid(p.payment_id)
        assert paid.status == FITPaymentStatus.PAID

    def test_dispute_payment(self):
        rec = self._register()
        p = self.reg.record_payment(rec.account_id, FITPaymentType.GENERATION,
                                    PERIOD_START, PERIOD_END, 500.0)
        disputed = self.reg.dispute_payment(p.payment_id)
        assert disputed.status == FITPaymentStatus.DISPUTED

    def test_active_customers(self):
        r1 = self._register(account=ACC, commissioning=dt.date(2015, 1, 1))
        r2 = self._register(account="A002", mpan="2000000000001",
                            commissioning=dt.date(2001, 1, 1))
        # r2 term_end = 2021, so expired by TODAY
        active = self.reg.active_customers(TODAY)
        assert any(c.account_id == ACC for c in active)

    def test_expired_customers(self):
        self._register(account=ACC, commissioning=dt.date(2001, 1, 1))
        expired = self.reg.expired_customers(TODAY)
        assert len(expired) == 1

    def test_expiring_within(self):
        # Expires in 2032 - 8 years away, not within 1yr
        self._register(account=ACC, commissioning=dt.date(2012, 4, 1))
        expiring = self.reg.expiring_within(TODAY, 365)
        assert len(expiring) == 0

    def test_customers_by_technology(self):
        self._register(account=ACC, tech=FITTechnology.SOLAR_PV)
        self._register(account="A002", mpan="2000000000001", tech=FITTechnology.WIND)
        assert len(self.reg.customers_by_technology(FITTechnology.WIND)) == 1

    def test_total_generation_payments_paid(self):
        rec = self._register(gen_rate=10.0)
        p1 = self.reg.record_payment(rec.account_id, FITPaymentType.GENERATION,
                                     PERIOD_START, PERIOD_END, 500.0)
        p2 = self.reg.record_payment(rec.account_id, FITPaymentType.GENERATION,
                                     PERIOD_START, PERIOD_END, 300.0)
        self.reg.mark_paid(p1.payment_id)
        # p2 not paid
        assert abs(self.reg.total_generation_payments_paid_gbp - 500.0 * 10.0 / 100.0) < 0.01

    def test_total_export_payments_paid(self):
        rec = self._register(exp_rate=5.0)
        p = self.reg.record_payment(rec.account_id, FITPaymentType.EXPORT,
                                    PERIOD_START, PERIOD_END, 200.0)
        self.reg.mark_paid(p.payment_id)
        assert abs(self.reg.total_export_payments_paid_gbp - 200.0 * 5.0 / 100.0) < 0.01

    def test_payments_for_account(self):
        r1 = self._register(account=ACC)
        r2 = self._register(account="A002", mpan="2000000000001")
        self.reg.record_payment(r1.account_id, FITPaymentType.GENERATION,
                                PERIOD_START, PERIOD_END, 500.0)
        self.reg.record_payment(r2.account_id, FITPaymentType.GENERATION,
                                PERIOD_START, PERIOD_END, 300.0)
        assert len(self.reg.payments_for_account(ACC)) == 1

    def test_fit_register_summary(self):
        self._register()
        s = self.reg.fit_register_summary(TODAY)
        assert "1 customers" in s

    def test_empty_summary(self):
        s = self.reg.fit_register_summary(TODAY)
        assert "0 customers" in s
