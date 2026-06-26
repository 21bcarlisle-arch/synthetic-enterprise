import datetime as dt
import pytest
from company.market.price_monitor import (
    PriceAlertLevel, Commodity, PriceObservation, PriceTrigger, WholesalePriceMonitor
)


def _setup_monitor() -> WholesalePriceMonitor:
    m = WholesalePriceMonitor()
    m.add_trigger('E_EL', Commodity.ELECTRICITY, PriceAlertLevel.ELEVATED, 100.0, '2x historical avg')
    m.add_trigger('H_EL', Commodity.ELECTRICITY, PriceAlertLevel.HIGH, 200.0, '4x historical avg')
    m.add_trigger('X_EL', Commodity.ELECTRICITY, PriceAlertLevel.EXTREME, 400.0, '8x historical avg')
    return m


def test_record_and_latest_observation():
    m = _setup_monitor()
    m.record_observation(Commodity.ELECTRICITY, dt.date(2022, 8, 1), 180.0, 190.0)
    latest = m.latest_observation(Commodity.ELECTRICITY)
    assert latest.spot_gbp_per_mwh == pytest.approx(180.0)


def test_term_structure_contango():
    obs = PriceObservation(Commodity.ELECTRICITY, dt.date(2022, 1, 1), 80.0, 95.0)
    assert obs.is_contango
    assert not obs.is_backwardation


def test_term_structure_backwardation():
    obs = PriceObservation(Commodity.ELECTRICITY, dt.date(2022, 8, 1), 200.0, 150.0)
    assert obs.is_backwardation
    assert obs.term_structure_slope == pytest.approx(-50.0)


def test_active_alerts_triggered():
    m = _setup_monitor()
    m.record_observation(Commodity.ELECTRICITY, dt.date(2022, 8, 26), 250.0, 260.0)
    alerts = m.active_alerts(Commodity.ELECTRICITY)
    assert len(alerts) == 2
    assert alerts[0].level == PriceAlertLevel.HIGH


def test_highest_alert_level_extreme():
    m = _setup_monitor()
    m.record_observation(Commodity.ELECTRICITY, dt.date(2022, 8, 26), 500.0, 480.0)
    assert m.highest_alert_level(Commodity.ELECTRICITY) == PriceAlertLevel.EXTREME


def test_no_alerts_when_normal():
    m = _setup_monitor()
    m.record_observation(Commodity.ELECTRICITY, dt.date(2022, 1, 10), 50.0, 55.0)
    assert len(m.active_alerts(Commodity.ELECTRICITY)) == 0
    assert m.highest_alert_level(Commodity.ELECTRICITY) == PriceAlertLevel.NORMAL


def test_latest_returns_most_recent():
    m = _setup_monitor()
    m.record_observation(Commodity.ELECTRICITY, dt.date(2022, 8, 1), 100.0, 110.0)
    m.record_observation(Commodity.ELECTRICITY, dt.date(2022, 8, 26), 300.0, 290.0)
    latest = m.latest_observation(Commodity.ELECTRICITY)
    assert latest.spot_gbp_per_mwh == pytest.approx(300.0)


def test_monitor_summary():
    m = _setup_monitor()
    m.record_observation(Commodity.ELECTRICITY, dt.date(2022, 8, 26), 250.0, 260.0)
    s = m.monitor_summary(Commodity.ELECTRICITY)
    assert s['highest_alert'] == 'high'
    assert s['active_alerts'] == 2
