"""Phase HT: coverage expansion for credit_rating_book, risk_appetite, renewals_book."""
import datetime as dt
import pytest


# ===== risk_appetite =====
from company.risk.risk_appetite import (
    RiskCategory, RiskRAG, RiskLimit, RiskMeasurement, RiskAppetiteFramework
)

class TestRiskAppetiteExpanded:
    def _framework(self):
        f = RiskAppetiteFramework(dt.date(2022,1,1))
        f.add_limit("VAR",RiskCategory.MARKET,"Value at Risk",5_000_000.0,"GBP")
        return f

    def test_add_limit_returns_limit(self):
        f = self._framework()
        l = f._limits["VAR"]
        assert l.limit_value == pytest.approx(5_000_000.0)
        assert l.warning_value == pytest.approx(4_000_000.0)

    def test_measurement_within_appetite(self):
        f = self._framework()
        m = f.record_measurement("VAR", 2_000_000.0, dt.date(2022,3,31))
        assert m.rag == RiskRAG.WITHIN_APPETITE
        assert not m.is_breach

    def test_measurement_approaching_limit(self):
        f = self._framework()
        m = f.record_measurement("VAR", 4_500_000.0, dt.date(2022,3,31))
        assert m.rag == RiskRAG.APPROACHING_LIMIT

    def test_measurement_limit_breach(self):
        f = self._framework()
        m = f.record_measurement("VAR", 6_000_000.0, dt.date(2022,3,31))
        assert m.rag == RiskRAG.LIMIT_BREACH
        assert m.is_breach

    def test_utilisation_pct(self):
        f = self._framework()
        m = f.record_measurement("VAR", 2_500_000.0, dt.date(2022,3,31))
        assert m.utilisation_pct == pytest.approx(50.0)

    def test_latest_measurement_most_recent(self):
        f = self._framework()
        f.record_measurement("VAR", 2_000_000.0, dt.date(2022,1,31))
        f.record_measurement("VAR", 3_500_000.0, dt.date(2022,3,31))
        latest = f.latest_measurement("VAR")
        assert latest.measured_value == pytest.approx(3_500_000.0)

    def test_active_breaches_uses_latest(self):
        f = self._framework()
        f.record_measurement("VAR", 6_000_000.0, dt.date(2022,1,31))
        f.record_measurement("VAR", 3_000_000.0, dt.date(2022,3,31))
        assert f.active_breaches() == []

    def test_risk_dashboard_keys(self):
        f = self._framework()
        f.record_measurement("VAR", 2_000_000.0, dt.date(2022,3,31))
        s = f.risk_dashboard(dt.date(2022,3,31))
        assert "breaches" in s and "items" in s

    def test_latest_measurement_none_for_unknown(self):
        f = self._framework()
        assert f.latest_measurement("MISSING") is None

    def test_multiple_categories(self):
        f = self._framework()
        f.add_limit("BAD_DEBT",RiskCategory.CREDIT,"Bad Debt",100_000.0,"GBP")
        assert len(f._limits) == 2
