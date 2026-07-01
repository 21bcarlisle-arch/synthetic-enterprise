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


# --- Phase KO depth tests ---

def test_commodity_stored_on_observation():
    obs = PriceObservation(Commodity.GAS, dt.date(2022, 1, 1), 50.0, 55.0)
    assert obs.commodity == Commodity.GAS


def test_date_stored_on_observation():
    obs = PriceObservation(Commodity.ELECTRICITY, dt.date(2022, 6, 15), 100.0, 110.0)
    assert obs.observation_date == dt.date(2022, 6, 15)


def test_spot_price_stored():
    obs = PriceObservation(Commodity.ELECTRICITY, dt.date(2022, 1, 1), 95.0, 100.0)
    assert obs.spot_gbp_per_mwh == pytest.approx(95.0)


def test_month_ahead_price_stored():
    obs = PriceObservation(Commodity.GAS, dt.date(2022, 1, 1), 50.0, 60.0)
    assert obs.month_ahead_gbp_per_mwh == pytest.approx(60.0)


def test_flat_price_neither_contango_nor_backwardation():
    obs = PriceObservation(Commodity.ELECTRICITY, dt.date(2022, 1, 1), 100.0, 100.0)
    assert not obs.is_contango
    assert not obs.is_backwardation


def test_term_structure_slope_contango_positive():
    obs = PriceObservation(Commodity.ELECTRICITY, dt.date(2022, 1, 1), 80.0, 100.0)
    assert obs.term_structure_slope == pytest.approx(20.0)


def test_latest_observation_none_when_empty():
    m = WholesalePriceMonitor()
    assert m.latest_observation(Commodity.ELECTRICITY) is None


def test_highest_alert_normal_when_no_observations():
    m = _setup_monitor()
    assert m.highest_alert_level(Commodity.ELECTRICITY) == PriceAlertLevel.NORMAL


def test_no_alerts_for_price_below_all_triggers():
    m = _setup_monitor()
    m.record_observation(Commodity.ELECTRICITY, dt.date(2022, 1, 1), 50.0, 55.0)
    alerts = m.active_alerts(Commodity.ELECTRICITY)
    assert alerts == []


def test_highest_alert_elevated_at_trigger_threshold():
    m = _setup_monitor()
    m.record_observation(Commodity.ELECTRICITY, dt.date(2022, 1, 1), 150.0, 160.0)
    assert m.highest_alert_level(Commodity.ELECTRICITY) == PriceAlertLevel.ELEVATED
