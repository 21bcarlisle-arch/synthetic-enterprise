import datetime as dt
import pytest
from company.billing.fit_legacy_register import (
    FITLegacyRegister, FITTechnology, FITPaymentType, FITPaymentStatus,
)

COMM_DATE = dt.date(2015, 6, 1)


def _reg():
    r = FITLegacyRegister()
    r.register_fit_customer("ACC-001", "MPAN-1", FITTechnology.SOLAR_PV,
                             4.0, COMM_DATE, 14.90, 5.24)
    return r


def test_term_end_date_twenty_years():
    reg = _reg()
    c = reg.all_customers[0]
    assert c.term_end_date == COMM_DATE.replace(year=COMM_DATE.year + 20)


def test_is_active_within_term():
    reg = _reg()
    c = reg.all_customers[0]
    assert c.is_active_as_of(dt.date(2020, 1, 1)) is True


def test_is_expired_after_term_end():
    reg = _reg()
    c = reg.all_customers[0]
    assert c.is_expired_as_of(dt.date(2040, 1, 1)) is True


def test_commissioning_after_close_raises():
    reg = FITLegacyRegister()
    with pytest.raises(ValueError):
        reg.register_fit_customer("A", "M", FITTechnology.WIND, 2.0,
                                  dt.date(2019, 4, 1), 10.0, 3.0)


def test_negative_capacity_raises():
    reg = FITLegacyRegister()
    with pytest.raises(ValueError):
        reg.register_fit_customer("A", "M", FITTechnology.WIND, -1.0,
                                  COMM_DATE, 10.0, 3.0)


def test_payment_id_prefix():
    reg = _reg()
    p = reg.record_payment("ACC-001", FITPaymentType.GENERATION,
                           dt.date(2022, 1, 1), dt.date(2022, 3, 31), 500.0)
    assert p.payment_id.startswith("FITPAY-")


def test_generation_payment_gbp():
    reg = _reg()
    p = reg.record_payment("ACC-001", FITPaymentType.GENERATION,
                           dt.date(2022, 1, 1), dt.date(2022, 3, 31), 1000.0)
    assert abs(p.payment_gbp - 1000.0 * 14.90 / 100.0) < 0.001


def test_deemed_export_applies_50_pct():
    reg = FITLegacyRegister()
    reg.register_fit_customer("B", "M2", FITTechnology.SOLAR_PV, 3.0,
                               COMM_DATE, 14.90, 5.24, has_export_meter=False)
    p = reg.record_payment("B", FITPaymentType.EXPORT,
                           dt.date(2022, 1, 1), dt.date(2022, 3, 31), 200.0)
    assert abs(p.units_kwh - 100.0) < 0.001


def test_mark_paid_changes_status():
    reg = _reg()
    p = reg.record_payment("ACC-001", FITPaymentType.GENERATION,
                           dt.date(2022, 1, 1), dt.date(2022, 3, 31), 500.0)
    paid = reg.mark_paid(p.payment_id)
    assert paid.status == FITPaymentStatus.PAID


def test_total_generation_payments_paid():
    reg = _reg()
    p1 = reg.record_payment("ACC-001", FITPaymentType.GENERATION,
                            dt.date(2022, 1, 1), dt.date(2022, 3, 31), 500.0)
    reg.mark_paid(p1.payment_id)
    assert reg.total_generation_payments_paid_gbp == pytest.approx(500.0 * 14.90 / 100.0)
