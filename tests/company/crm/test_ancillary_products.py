import datetime as dt
import pytest
from company.crm.ancillary_products import (
    AncillaryProduct, ProductSubscription, AncillaryRevenueTracker
)


def test_subscription_active():
    t = AncillaryRevenueTracker()
    s = t.subscribe('C001', AncillaryProduct.BOILER_COVER, dt.date(2022, 1, 1))
    assert s.is_active
    assert s.monthly_price_gbp == pytest.approx(18.0)


def test_cancel_deactivates():
    t = AncillaryRevenueTracker()
    t.subscribe('C001', AncillaryProduct.BOILER_COVER, dt.date(2022, 1, 1))
    t.cancel('C001', AncillaryProduct.BOILER_COVER, dt.date(2022, 6, 1))
    assert len(t.active_subscriptions('C001')) == 0


def test_products_per_customer():
    t = AncillaryRevenueTracker()
    t.subscribe('C001', AncillaryProduct.BOILER_COVER, dt.date(2022, 1, 1))
    t.subscribe('C001', AncillaryProduct.EV_TARIFF, dt.date(2022, 1, 1))
    t.subscribe('C001', AncillaryProduct.SMART_HOME_CONTROLS, dt.date(2022, 1, 1))
    assert t.products_per_customer('C001') == 3


def test_annual_revenue_full_year():
    t = AncillaryRevenueTracker()
    t.subscribe('C001', AncillaryProduct.HOME_INSURANCE, dt.date(2022, 1, 1))
    rev = t.total_annual_revenue_gbp(2022)
    assert rev == pytest.approx(32.0 * 12, rel=0.05)


def test_annual_revenue_partial_year():
    t = AncillaryRevenueTracker()
    t.subscribe('C001', AncillaryProduct.BROADBAND, dt.date(2022, 7, 1))
    rev = t.total_annual_revenue_gbp(2022)
    assert rev == pytest.approx(28.0 * 6, rel=0.1)


def test_revenue_by_product():
    t = AncillaryRevenueTracker()
    t.subscribe('C001', AncillaryProduct.BOILER_COVER, dt.date(2022, 1, 1))
    t.subscribe('C002', AncillaryProduct.BOILER_COVER, dt.date(2022, 1, 1))
    t.subscribe('C003', AncillaryProduct.CARBON_OFFSET, dt.date(2022, 1, 1))
    by_prod = t.revenue_by_product(2022)
    assert by_prod['boiler_cover'] == pytest.approx(18.0 * 12 * 2, rel=0.05)
    assert 'carbon_offset' in by_prod


def test_avg_products_per_customer():
    t = AncillaryRevenueTracker()
    t.subscribe('C001', AncillaryProduct.BOILER_COVER, dt.date(2022, 1, 1))
    t.subscribe('C001', AncillaryProduct.EV_TARIFF, dt.date(2022, 1, 1))
    t.subscribe('C002', AncillaryProduct.SMART_HOME_CONTROLS, dt.date(2022, 1, 1))
    avg = t.avg_products_per_customer()
    assert avg == pytest.approx(1.5)


def test_portfolio_summary():
    t = AncillaryRevenueTracker()
    t.subscribe('C001', AncillaryProduct.BROADBAND, dt.date(2022, 1, 1))
    s = t.portfolio_summary(2022)
    assert s['total_active_subscriptions'] == 1
    assert 'avg_products_per_customer' in s
    assert 'by_product' in s
