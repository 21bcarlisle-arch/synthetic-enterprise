"""Phase HU: coverage expansion for tariff_notification, ancillary_products, price_monitor."""
import datetime as dt
import pytest

# ===== tariff_notification =====
from company.crm.tariff_notification import (
    ADVANCE_NOTICE_DAYS, NotificationChannel, NotificationStatus,
    TariffChangeReason, TariffNotification, TariffNotificationLog
)

class TestTariffNotificationExpanded:
    def _log(self):
        log = TariffNotificationLog()
        log.send("N001","C1",NotificationChannel.EMAIL,
                 dt.date(2022,11,1), dt.date(2023,1,1),
                 TariffChangeReason.PRICE_CAP_CHANGE, 28.5, 35.0, 25.0, 28.0)
        return log

    def test_notice_days(self):
        log = self._log()
        n = log.get("N001")
        assert n.notice_days == 61

    def test_meets_advance_notice(self):
        log = self._log()
        n = log.get("N001")
        assert n.meets_advance_notice

    def test_breach_when_under_42_days(self):
        log = TariffNotificationLog()
        log.send("N002","C2",NotificationChannel.SMS,
                 dt.date(2022,12,10), dt.date(2023,1,1),
                 TariffChangeReason.MARKET_PRICE_CHANGE, 28.5, 35.0, 25.0, 28.0)
        assert len(log.compliance_breaches()) == 1

    def test_unit_rate_change_pct(self):
        log = self._log()
        n = log.get("N001")
        expected = (35.0 - 28.5) / 28.5 * 100
        assert n.unit_rate_change_pct == pytest.approx(round(expected, 1))

    def test_is_price_increase(self):
        log = self._log()
        n = log.get("N001")
        assert n.is_price_increase

    def test_price_decrease_not_increase(self):
        log = TariffNotificationLog()
        log.send("N003","C3",NotificationChannel.EMAIL,
                 dt.date(2022,11,1), dt.date(2023,1,1),
                 TariffChangeReason.PRICE_CAP_CHANGE, 35.0, 28.0, 28.0, 25.0)
        n = log.get("N003")
        assert not n.is_price_increase

    def test_mark_confirmed(self):
        log = self._log()
        log.mark_confirmed("N001")
        n = log.get("N001")
        assert n.status == NotificationStatus.CONFIRMED_READ

    def test_customer_notifications_filter(self):
        log = self._log()
        assert len(log.customer_notifications("C1")) == 1
        assert len(log.customer_notifications("C9")) == 0

    def test_price_increases_by_year(self):
        log = self._log()
        assert len(log.price_increases(2022)) == 1

    def test_notification_summary_keys(self):
        log = self._log()
        s = log.notification_summary(2022)
        assert "compliance_breaches" in s and "price_increases" in s


# ===== ancillary_products =====
from company.crm.ancillary_products import (
    AncillaryProduct, ProductSubscription, AncillaryRevenueTracker,
    _MONTHLY_REVENUE_GBP,
)

class TestAncillaryProductsExpanded:
    def _tracker(self):
        t = AncillaryRevenueTracker()
        t.subscribe("C1",AncillaryProduct.BOILER_COVER,dt.date(2022,1,1))
        t.subscribe("C1",AncillaryProduct.SMART_HOME_CONTROLS,dt.date(2022,1,1))
        t.subscribe("C2",AncillaryProduct.HOME_INSURANCE,dt.date(2022,6,1))
        return t

    def test_default_price_set(self):
        t = AncillaryRevenueTracker()
        sub = t.subscribe("C1",AncillaryProduct.BOILER_COVER,dt.date(2022,1,1))
        assert sub.monthly_price_gbp == pytest.approx(18.0)

    def test_custom_price_override(self):
        t = AncillaryRevenueTracker()
        sub = t.subscribe("C1",AncillaryProduct.BOILER_COVER,dt.date(2022,1,1), monthly_price_gbp=15.0)
        assert sub.monthly_price_gbp == pytest.approx(15.0)

    def test_is_active_when_no_end_date(self):
        t = self._tracker()
        subs = t.active_subscriptions("C1")
        assert all(s.is_active for s in subs)

    def test_cancel_sets_end_date(self):
        t = self._tracker()
        t.cancel("C1",AncillaryProduct.BOILER_COVER,dt.date(2022,6,30))
        active = t.active_subscriptions("C1")
        assert all(s.product != AncillaryProduct.BOILER_COVER for s in active)

    def test_products_per_customer(self):
        t = self._tracker()
        assert t.products_per_customer("C1") == 2

    def test_total_annual_revenue(self):
        t = AncillaryRevenueTracker()
        t.subscribe("C1",AncillaryProduct.BOILER_COVER,dt.date(2022,1,1))
        rev = t.total_annual_revenue_gbp(2022)
        assert rev > 0

    def test_revenue_by_product(self):
        t = self._tracker()
        by_p = t.revenue_by_product(2022)
        assert "boiler_cover" in by_p and by_p["boiler_cover"] > 0

    def test_avg_products_per_customer(self):
        t = self._tracker()
        avg = t.avg_products_per_customer()
        assert avg == pytest.approx(1.5)

    def test_avg_products_none_when_empty(self):
        t = AncillaryRevenueTracker()
        assert t.avg_products_per_customer() is None

    def test_portfolio_summary_keys(self):
        t = self._tracker()
        s = t.portfolio_summary(2022)
        assert "total_active_subscriptions" in s and "unique_customers" in s


# ===== price_monitor =====
from company.market.price_monitor import (
    PriceAlertLevel, Commodity, PriceObservation, PriceTrigger, WholesalePriceMonitor
)

class TestPriceMonitorExpanded:
    def _monitor(self):
        m = WholesalePriceMonitor()
        m.add_trigger("T1",Commodity.ELECTRICITY,PriceAlertLevel.ELEVATED,80.0,"Normal elevated")
        m.add_trigger("T2",Commodity.ELECTRICITY,PriceAlertLevel.HIGH,200.0,"High threshold")
        m.add_trigger("T3",Commodity.ELECTRICITY,PriceAlertLevel.EXTREME,500.0,"Crisis level")
        return m

    def test_record_observation(self):
        m = self._monitor()
        obs = m.record_observation(Commodity.ELECTRICITY,dt.date(2022,6,1),75.0,80.0,85.0)
        assert obs.spot_gbp_per_mwh == 75.0

    def test_term_structure_contango(self):
        obs = PriceObservation(Commodity.ELECTRICITY,dt.date(2022,6,1),70.0,80.0)
        assert obs.is_contango
        assert not obs.is_backwardation

    def test_term_structure_backwardation(self):
        obs = PriceObservation(Commodity.ELECTRICITY,dt.date(2022,6,1),90.0,75.0)
        assert obs.is_backwardation
        assert not obs.is_contango

    def test_no_alerts_below_threshold(self):
        m = self._monitor()
        m.record_observation(Commodity.ELECTRICITY,dt.date(2022,6,1),60.0,65.0)
        assert m.active_alerts(Commodity.ELECTRICITY) == []
        assert m.highest_alert_level(Commodity.ELECTRICITY) == PriceAlertLevel.NORMAL

    def test_elevated_alert_triggered(self):
        m = self._monitor()
        m.record_observation(Commodity.ELECTRICITY,dt.date(2022,6,1),100.0,110.0)
        alerts = m.active_alerts(Commodity.ELECTRICITY)
        assert len(alerts) == 1
        assert alerts[0].level == PriceAlertLevel.ELEVATED

    def test_extreme_alert_at_crisis_price(self):
        m = self._monitor()
        m.record_observation(Commodity.ELECTRICITY,dt.date(2022,10,1),600.0,580.0)
        assert m.highest_alert_level(Commodity.ELECTRICITY) == PriceAlertLevel.EXTREME

    def test_latest_observation_is_most_recent(self):
        m = self._monitor()
        m.record_observation(Commodity.ELECTRICITY,dt.date(2022,1,1),60.0,65.0)
        m.record_observation(Commodity.ELECTRICITY,dt.date(2022,6,1),80.0,90.0)
        latest = m.latest_observation(Commodity.ELECTRICITY)
        assert latest.observation_date == dt.date(2022,6,1)

    def test_latest_observation_none_when_no_records(self):
        m = WholesalePriceMonitor()
        assert m.latest_observation(Commodity.GAS) is None

    def test_price_history_limit(self):
        m = self._monitor()
        for i in range(10):
            m.record_observation(Commodity.ELECTRICITY,dt.date(2022,1,1)+dt.timedelta(i),50.0+i,55.0+i)
        history = m.price_history(Commodity.ELECTRICITY, 5)
        assert len(history) == 5

    def test_monitor_summary_keys(self):
        m = self._monitor()
        m.record_observation(Commodity.ELECTRICITY,dt.date(2022,6,1),100.0,110.0)
        s = m.monitor_summary(Commodity.ELECTRICITY)
        assert "highest_alert" in s and "active_alerts" in s
