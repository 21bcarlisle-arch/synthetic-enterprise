"""Phase IL: deeper coverage for payroll, bad_debt_provision, board_dashboard."""
import datetime as dt
import pytest

# ===== payroll =====
from company.finance.payroll import (
    HeadcountPlan, Department, EmploymentType
)


def _plan():
    p = HeadcountPlan(2023)
    p.add_role("R001", "Customer Advisor", Department.CUSTOMER_SERVICES,
                EmploymentType.PERMANENT, 28_000.0, headcount=5, fte=1.0)
    p.add_role("R002", "Senior Trader", Department.TRADING,
                EmploymentType.CONTRACT, 90_000.0, headcount=2, fte=1.0)
    return p


class TestHeadcountPlan:
    def test_total_annual_salary(self):
        p = _plan()
        role = p._roles[0]
        assert role.total_annual_salary_gbp == pytest.approx(28_000 * 5)

    def test_employer_ni(self):
        p = _plan()
        role = p._roles[0]
        ni = (28_000 - 9_100) * 0.138 * 5
        assert role.employer_ni_gbp == pytest.approx(ni, abs=0.02)

    def test_pension_cost(self):
        p = _plan()
        role = p._roles[0]
        assert role.pension_cost_gbp == pytest.approx(role.total_annual_salary_gbp * 0.05)

    def test_total_employment_cost_includes_ni_and_pension(self):
        p = _plan()
        role = p._roles[0]
        expected = role.total_annual_salary_gbp + role.employer_ni_gbp + role.pension_cost_gbp
        assert role.total_employment_cost_gbp == pytest.approx(expected, abs=0.02)

    def test_total_headcount(self):
        p = _plan()
        assert p.total_headcount == 7

    def test_total_fte(self):
        p = _plan()
        assert p.total_fte == pytest.approx(7.0)

    def test_total_payroll_cost(self):
        p = _plan()
        expected = sum(r.total_employment_cost_gbp for r in p._roles)
        assert p.total_payroll_cost_gbp == pytest.approx(expected, abs=0.02)

    def test_cost_by_department(self):
        p = _plan()
        by_dept = p.cost_by_department()
        assert "customer_services" in by_dept and "trading" in by_dept

    def test_cost_per_customer(self):
        p = _plan()
        cpc = p.cost_per_customer_gbp(1000)
        assert cpc == pytest.approx(p.total_payroll_cost_gbp / 1000, abs=0.01)

    def test_cost_per_customer_none_when_zero(self):
        p = _plan()
        assert p.cost_per_customer_gbp(0) is None


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


# ===== board_dashboard =====
from company.finance.board_dashboard import (
    BoardDashboard, KPIMetric, KPIStatus
)


def _dashboard():
    return BoardDashboard(
        period=dt.date(2023, 3, 31),
        customer_count=5000,
        net_margin_gbp=250_000.0,
        gross_margin_gbp=500_000.0,
        treasury_gbp=800_000.0,
        enterprise_value_gbp=2_000_000.0,
        churn_rate_pct=2.5,
        complaints_per_100=1.5,
        bad_debt_ratio_pct=1.2,
        cash_runway_weeks=12.0,
        hedge_ratio_pct=75.0,
    )


class TestBoardDashboard:
    def test_kpi_green_when_above_target(self):
        kpi = KPIMetric("Net Margin", 300_000, 250_000, "£")
        assert kpi.status == KPIStatus.GREEN

    def test_kpi_amber_within_10pct(self):
        kpi = KPIMetric("Net Margin", 228_000, 250_000, "£")
        assert kpi.status == KPIStatus.AMBER

    def test_kpi_red_when_below_90pct(self):
        kpi = KPIMetric("Net Margin", 200_000, 250_000, "£")
        assert kpi.status == KPIStatus.RED

    def test_lower_is_better_green_below_target(self):
        kpi = KPIMetric("Churn", 2.0, 3.0, "%", lower_is_better=True)
        assert kpi.status == KPIStatus.GREEN

    def test_lower_is_better_red_above_target(self):
        kpi = KPIMetric("Churn", 5.0, 3.0, "%", lower_is_better=True)
        assert kpi.status == KPIStatus.RED

    def test_is_on_target_true_when_green(self):
        kpi = KPIMetric("Margin", 300_000, 250_000, "£")
        assert kpi.is_on_target

    def test_kpis_returns_10_metrics(self):
        d = _dashboard()
        kpis = d.kpis({})
        assert len(kpis) == 10

    def test_rag_summary_keys(self):
        d = _dashboard()
        s = d.rag_summary({"net_margin_gbp": 200_000, "churn_rate_pct": 3.0})
        assert "green" in s and "at_risk_metrics" in s and "overall" in s

    def test_rag_summary_overall_red_when_any_red(self):
        d = _dashboard()
        targets = {"net_margin_gbp": 10_000_000}  # unachievable → RED
        s = d.rag_summary(targets)
        assert s["overall"] == "RED"

    def test_vs_target_pct_positive_when_above(self):
        kpi = KPIMetric("Score", 110, 100, "pts")
        assert kpi.vs_target_pct == pytest.approx(10.0)
