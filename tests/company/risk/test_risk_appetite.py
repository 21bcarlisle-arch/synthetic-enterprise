import datetime as dt
import pytest
from company.risk.risk_appetite import (
    RiskCategory, RiskRAG, RiskLimit, RiskMeasurement, RiskAppetiteFramework
)


def _raf():
    raf = RiskAppetiteFramework(approved_date=dt.date(2022, 1, 1))
    raf.add_limit('MKT01', RiskCategory.MARKET, 'Open position MWh', 5000.0, 'MWh')
    raf.add_limit('LIQ01', RiskCategory.LIQUIDITY, '13-week cash min', 500_000.0, 'GBP')
    raf.add_limit('REG01', RiskCategory.REGULATORY, 'Bad debt % revenue', 3.0, '%')
    return raf


def test_add_and_retrieve_limit():
    raf = _raf()
    assert 'MKT01' in raf._limits
    assert raf._limits['MKT01'].limit_value == 5000.0


def test_warning_value():
    raf = _raf()
    limit = raf._limits['MKT01']
    assert limit.warning_value == pytest.approx(4000.0)


def test_within_appetite():
    raf = _raf()
    m = raf.record_measurement('MKT01', 2000.0, dt.date(2022, 3, 1))
    assert m.rag == RiskRAG.WITHIN_APPETITE
    assert m.utilisation_pct == pytest.approx(40.0)


def test_approaching_limit():
    raf = _raf()
    m = raf.record_measurement('MKT01', 4200.0, dt.date(2022, 3, 1))
    assert m.rag == RiskRAG.APPROACHING_LIMIT


def test_limit_breach():
    raf = _raf()
    m = raf.record_measurement('MKT01', 6000.0, dt.date(2022, 10, 1))
    assert m.rag == RiskRAG.LIMIT_BREACH
    assert m.is_breach is True


def test_active_breaches():
    raf = _raf()
    raf.record_measurement('MKT01', 6000.0, dt.date(2022, 10, 1))
    raf.record_measurement('REG01', 1.5, dt.date(2022, 10, 1))
    assert len(raf.active_breaches()) == 1


def test_latest_measurement():
    raf = _raf()
    raf.record_measurement('MKT01', 2000.0, dt.date(2022, 1, 1))
    raf.record_measurement('MKT01', 5500.0, dt.date(2022, 6, 1))
    latest = raf.latest_measurement('MKT01')
    assert latest.measured_value == pytest.approx(5500.0)
    assert latest.is_breach is True


def test_risk_dashboard():
    raf = _raf()
    raf.record_measurement('MKT01', 4500.0, dt.date(2022, 10, 1))
    raf.record_measurement('REG01', 5.0, dt.date(2022, 10, 1))
    d = raf.risk_dashboard(dt.date(2022, 10, 31))
    assert d['breaches'] == 1
    assert d['measured_limits'] == 2
    assert 'items' in d
