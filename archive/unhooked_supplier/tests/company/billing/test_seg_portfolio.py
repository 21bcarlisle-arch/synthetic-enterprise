import datetime as dt
import pytest
from company.billing.seg_portfolio import (
    SEGTariffTier, SEGCustomer, SEGPortfolio, get_seg_rate
)


def test_seg_rate_2022():
    assert get_seg_rate(2022) == pytest.approx(12.0)


def test_seg_rate_2020():
    assert get_seg_rate(2020) == pytest.approx(5.5)


def test_has_battery():
    c = SEGCustomer('C1', 'MPAN001', 4.0, dt.date(2022, 1, 1), battery_capacity_kwh=10.0)
    assert c.has_battery


def test_no_battery():
    c = SEGCustomer('C1', 'MPAN001', 4.0, dt.date(2022, 1, 1))
    assert not c.has_battery


def test_estimated_export_higher_without_battery():
    c_no_bat = SEGCustomer('C1', 'MPAN001', 4.0, dt.date(2022, 1, 1))
    c_bat = SEGCustomer('C2', 'MPAN002', 4.0, dt.date(2022, 1, 1), battery_capacity_kwh=10.0)
    assert c_no_bat.estimated_annual_export_kwh(2022) > c_bat.estimated_annual_export_kwh(2022)


def test_annual_seg_income():
    c = SEGCustomer('C1', 'MPAN001', 4.0, dt.date(2022, 1, 1))
    export = c.estimated_annual_export_kwh(2022)
    rate = get_seg_rate(2022)
    expected = export * rate / 100
    assert c.annual_seg_income_gbp(2022) == pytest.approx(expected, rel=0.01)


def test_portfolio_register_and_total():
    p = SEGPortfolio()
    p.register('C1', 'MPAN001', 4.0, dt.date(2022, 1, 1))
    p.register('C2', 'MPAN002', 6.0, dt.date(2022, 3, 1))
    assert p.total_solar_capacity_kwp() == pytest.approx(10.0)


def test_portfolio_export_payments():
    p = SEGPortfolio()
    p.register('C1', 'MPAN001', 4.0, dt.date(2022, 1, 1))
    p.record_export('C1', dt.date(2022, 6, 1), 200.0)
    assert p.total_export_kwh(2022) == pytest.approx(200.0)
    expected = 200.0 * 12.0 / 100
    assert p.total_seg_payments_gbp(2022) == pytest.approx(expected)


def test_customers_with_battery():
    p = SEGPortfolio()
    p.register('C1', 'MPAN001', 4.0, dt.date(2022, 1, 1), battery_kwh=10.0)
    p.register('C2', 'MPAN002', 4.0, dt.date(2022, 1, 1))
    assert len(p.customers_with_battery()) == 1


def test_seg_summary():
    p = SEGPortfolio()
    p.register('C1', 'MPAN001', 4.0, dt.date(2022, 1, 1))
    p.record_export('C1', dt.date(2022, 6, 1), 500.0)
    s = p.seg_summary(2022)
    assert s['registered_customers'] == 1
    assert s['seg_rate_pence'] == 12.0
    assert s['total_export_kwh'] == pytest.approx(500.0)


# --- Phase KZ depth tests ---

def test_customer_id_stored():
    c = SEGCustomer('C_KZ', 'MP001', 4.0, dt.date(2022, 3, 1))
    assert c.customer_id == 'C_KZ'


def test_mpan_stored():
    c = SEGCustomer('C1', 'MP_KZ', 4.0, dt.date(2022, 3, 1))
    assert c.mpan == 'MP_KZ'


def test_solar_capacity_stored():
    c = SEGCustomer('C1', 'MP001', 5.5, dt.date(2022, 3, 1))
    assert c.solar_capacity_kwp == pytest.approx(5.5)


def test_registration_date_stored():
    d = dt.date(2021, 6, 15)
    c = SEGCustomer('C1', 'MP001', 4.0, d)
    assert c.registration_date == d


def test_tariff_tier_default_fixed():
    c = SEGCustomer('C1', 'MP001', 4.0, dt.date(2022, 1, 1))
    assert c.tariff_tier == SEGTariffTier.FIXED


def test_battery_capacity_default_zero():
    c = SEGCustomer('C1', 'MP001', 4.0, dt.date(2022, 1, 1))
    assert c.battery_capacity_kwh == pytest.approx(0.0)


def test_has_battery_true_when_nonzero():
    c = SEGCustomer('C1', 'MP001', 4.0, dt.date(2022, 1, 1), battery_capacity_kwh=10.0)
    assert c.has_battery is True


def test_seg_rate_2023():
    assert get_seg_rate(2023) == pytest.approx(15.0)


def test_seg_rate_2025():
    assert get_seg_rate(2025) == pytest.approx(10.0)


def test_portfolio_register_returns_seg_customer():
    p = SEGPortfolio()
    c = p.register('C1', 'MP001', 4.0, dt.date(2022, 1, 1))
    assert isinstance(c, SEGCustomer)
