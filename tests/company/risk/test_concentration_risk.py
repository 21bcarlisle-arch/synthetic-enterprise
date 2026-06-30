"""Tests for Portfolio Concentration Risk Monitor (Phase EQ)."""
import datetime as dt
import pytest
from company.risk.concentration_risk import (
    ConcentrationRiskLevel, ConcentrationDimension, ConcentrationSnapshot,
    ConcentrationRiskMonitor,
)

DATE = dt.date(2024, 1, 15)


def make_snap(shares=None, dim=ConcentrationDimension.CUSTOMER, date=DATE):
    if shares is None:
        shares = {"C1": 0.5, "C2": 0.3, "C3": 0.2}
    return ConcentrationSnapshot(dimension=dim, as_of=date, shares=shares)


class TestConcentrationSnapshot:
    def test_hhi_equal_distribution(self):
        snap = make_snap({"A": 0.5, "B": 0.5})
        assert snap.hhi == pytest.approx(0.5)

    def test_hhi_monopoly(self):
        snap = make_snap({"A": 1.0})
        assert snap.hhi == pytest.approx(1.0)

    def test_hhi_diverse(self):
        shares = dict((str(i), 0.1) for i in range(10))
        snap = make_snap(shares)
        assert snap.hhi == pytest.approx(0.10, abs=0.001)

    def test_risk_level_critical(self):
        snap = make_snap({"A": 0.6, "B": 0.4})
        assert snap.risk_level == ConcentrationRiskLevel.CRITICAL

    def test_risk_level_low(self):
        shares = dict((str(i), 1/20) for i in range(20))
        snap = make_snap(shares)
        assert snap.risk_level == ConcentrationRiskLevel.LOW

    def test_top_entity(self):
        snap = make_snap({"A": 0.6, "B": 0.4})
        assert snap.top_entity == "A"

    def test_top_entity_none_when_empty(self):
        snap = make_snap({})
        assert snap.top_entity is None

    def test_top_entity_pct(self):
        snap = make_snap({"A": 0.25, "B": 0.75})
        assert snap.top_entity_pct == pytest.approx(75.0)

    def test_breaches_single_entity_cap(self):
        snap = make_snap({"A": 0.25, "B": 0.75})
        assert snap.breaches_single_entity_cap

    def test_no_breach(self):
        shares = dict((str(i), 0.10) for i in range(10))
        snap = make_snap(shares)
        assert not snap.breaches_single_entity_cap

    def test_n_entities(self):
        snap = make_snap({"A": 0.5, "B": 0.5})
        assert snap.n_entities == 2

    def test_concentration_summary(self):
        snap = make_snap()
        s = snap.concentration_summary()
        assert "Concentration" in s
        assert "HHI=" in s


class TestConcentrationRiskMonitor:
    def test_record_and_retrieve(self):
        monitor = ConcentrationRiskMonitor()
        monitor.record(make_snap())
        snap = monitor.latest_for(ConcentrationDimension.CUSTOMER)
        assert snap is not None

    def test_latest_returns_most_recent(self):
        monitor = ConcentrationRiskMonitor()
        monitor.record(make_snap(date=dt.date(2024, 1, 1)))
        monitor.record(make_snap(date=dt.date(2024, 6, 1)))
        snap = monitor.latest_for(ConcentrationDimension.CUSTOMER)
        assert snap.as_of == dt.date(2024, 6, 1)

    def test_high_risk_dimensions(self):
        monitor = ConcentrationRiskMonitor()
        monitor.record(make_snap({"A": 0.9, "B": 0.1}))
        result = monitor.high_risk_dimensions(DATE)
        assert len(result) == 1

    def test_entity_breaches(self):
        monitor = ConcentrationRiskMonitor()
        monitor.record(make_snap({"A": 0.3, "B": 0.7}))
        assert len(monitor.entity_breaches()) == 1

    def test_portfolio_concentration_summary(self):
        monitor = ConcentrationRiskMonitor()
        monitor.record(make_snap())
        s = monitor.portfolio_concentration_summary(DATE)
        assert "Concentration Risk Monitor" in s
