"""Phase IL: deeper coverage for payroll, bad_debt_provision, board_dashboard."""
import datetime as dt
import pytest


# ===== bad_debt_provision =====
from company.finance.bad_debt_provision import (
    ArrearsLedgerItem, BadDebtProvision, build_provision, classify_age, AgingBucket
)


def _provision():
    items = [
        ArrearsLedgerItem("C1", 1000.0, 15),           # CURRENT 0.5%
        ArrearsLedgerItem("C2", 500.0, 45),             # DAYS_30 5%
        ArrearsLedgerItem("C3", 800.0, 75),             # DAYS_60 20%
        ArrearsLedgerItem("C4", 300.0, 200, True),      # DAYS_180_PLUS 90%
    ]
    return build_provision(dt.date(2022, 6, 30), items)


class TestBadDebtProvision:
    def test_classify_age_current(self):
        assert classify_age(20) == AgingBucket.CURRENT

    def test_classify_age_180_plus(self):
        assert classify_age(200) == AgingBucket.DAYS_180_PLUS

    def test_provision_rate_current(self):
        item = ArrearsLedgerItem("C1", 1000.0, 15)
        assert item.provision_rate == pytest.approx(0.005)

    def test_provision_gbp(self):
        item = ArrearsLedgerItem("C1", 1000.0, 15)
        assert item.provision_gbp == pytest.approx(5.0)

    def test_total_arrears(self):
        p = _provision()
        assert p.total_arrears_gbp == pytest.approx(2600.0)

    def test_total_provision(self):
        p = _provision()
        expected = 5.0 + 25.0 + 160.0 + 270.0  # 0.5%+5%+20%+90% of respective amounts
        assert p.total_provision_gbp == pytest.approx(expected)

    def test_provision_coverage_pct(self):
        p = _provision()
        expected = round(p.total_provision_gbp / p.total_arrears_gbp * 100, 1)
        assert p.provision_coverage_pct == pytest.approx(expected)

    def test_vulnerable_provision(self):
        p = _provision()
        assert p.vulnerable_provision_gbp() == pytest.approx(270.0)  # 300*90%

    def test_by_bucket_has_keys(self):
        p = _provision()
        buckets = p.by_bucket()
        assert "current" in buckets and "180_plus_days" in buckets

    def test_summary_keys(self):
        p = _provision()
        s = p.summary()
        assert "provision_coverage_pct" in s and "vulnerable_provision_gbp" in s
