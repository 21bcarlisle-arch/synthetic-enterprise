import datetime as dt
import pytest
from company.market.interconnector_monitor import (
    Interconnector, FlowDirection, InterconnectorObservation,
    InterconnectorPriceMonitor
)


def test_record_observation():
    monitor = InterconnectorPriceMonitor()
    obs = monitor.record(
        Interconnector.IFA1, dt.date(2022, 3, 1),
        flow_mw=1200.0, gb_price=400.0, foreign_price=200.0,
        direction=FlowDirection.IMPORT
    )
    assert obs.price_differential_gbp_per_mwh == pytest.approx(200.0)


def test_capacity_and_utilisation():
    obs = InterconnectorObservation(
        Interconnector.IFA1, dt.date(2022, 3, 1),
        1000.0, 300.0, 250.0, FlowDirection.IMPORT
    )
    assert obs.capacity_mw == 2000
    assert obs.utilisation_pct == pytest.approx(50.0)


def test_avg_price_differential():
    monitor = InterconnectorPriceMonitor()
    monitor.record(Interconnector.BRITNED, dt.date(2022, 1, 1),
                   800.0, 350.0, 300.0, FlowDirection.IMPORT)
    monitor.record(Interconnector.BRITNED, dt.date(2022, 1, 2),
                   900.0, 370.0, 300.0, FlowDirection.IMPORT)
    avg = monitor.avg_price_differential(Interconnector.BRITNED)
    assert avg == pytest.approx(60.0)


def test_highest_differential():
    monitor = InterconnectorPriceMonitor()
    monitor.record(Interconnector.NEMO, dt.date(2022, 6, 1),
                   500.0, 250.0, 200.0, FlowDirection.IMPORT)
    monitor.record(Interconnector.IFA1, dt.date(2022, 6, 2),
                   1500.0, 600.0, 100.0, FlowDirection.IMPORT)
    hd = monitor.highest_differential()
    assert hd.interconnector == Interconnector.IFA1
    assert hd.price_differential_gbp_per_mwh == pytest.approx(500.0)


def test_import_days_count():
    monitor = InterconnectorPriceMonitor()
    monitor.record(Interconnector.NORTHSEALINK, dt.date(2022, 1, 1),
                   1000.0, 200.0, 180.0, FlowDirection.IMPORT)
    monitor.record(Interconnector.NORTHSEALINK, dt.date(2022, 1, 2),
                   0.0, 200.0, 220.0, FlowDirection.EXPORT)
    assert monitor.import_days(Interconnector.NORTHSEALINK) == 1


def test_total_import_mwh():
    monitor = InterconnectorPriceMonitor()
    monitor.record(Interconnector.ELECLINK, dt.date(2022, 5, 1),
                   500.0, 280.0, 250.0, FlowDirection.IMPORT)
    total = monitor.total_import_mwh(Interconnector.ELECLINK)
    assert total == pytest.approx(500.0 * 24, rel=0.01)


def test_none_for_missing():
    monitor = InterconnectorPriceMonitor()
    assert monitor.avg_price_differential(Interconnector.VIKINGLINK) is None
    assert monitor.highest_differential() is None


def test_monitor_summary():
    monitor = InterconnectorPriceMonitor()
    monitor.record(Interconnector.IFA2, dt.date(2022, 9, 1),
                   800.0, 350.0, 300.0, FlowDirection.IMPORT)
    s = monitor.monitor_summary(dt.date(2022, 12, 31))
    assert s['year'] == 2022
    assert s['observations'] == 1
    assert s['interconnectors_active'] == 1
