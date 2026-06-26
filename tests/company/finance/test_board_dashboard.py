import datetime as dt
import pytest
from company.finance.board_dashboard import KPIStatus, KPIMetric, BoardDashboard


_TARGETS = {
    'customer_count': 500,
    'net_margin_gbp': 1_000_000.0,
    'gross_margin_gbp': 5_000_000.0,
    'treasury_gbp': 200_000.0,
    'enterprise_value_gbp': 4_000_000.0,
    'churn_rate_pct': 3.0,
    'complaints_per_100': 2.0,
    'bad_debt_ratio_pct': 2.0,
    'cash_runway_weeks': 8.0,
    'hedge_ratio_pct': 70.0,
}


def _make_dashboard() -> BoardDashboard:
    return BoardDashboard(
        period=dt.date(2022, 12, 31),
        customer_count=520,
        net_margin_gbp=1_200_000.0,
        gross_margin_gbp=5_500_000.0,
        treasury_gbp=350_000.0,
        enterprise_value_gbp=4_500_000.0,
        churn_rate_pct=2.5,
        complaints_per_100=1.8,
        bad_debt_ratio_pct=1.5,
        cash_runway_weeks=12.0,
        hedge_ratio_pct=75.0,
    )


def test_kpi_count():
    d = _make_dashboard()
    assert len(d.kpis(_TARGETS)) == 10


def test_green_kpi():
    metric = KPIMetric('Net Margin', 1_200_000.0, 1_000_000.0, '£')
    assert metric.status == KPIStatus.GREEN
    assert metric.is_on_target


def test_amber_kpi():
    metric = KPIMetric('Churn', 3.2, 3.0, '%', lower_is_better=True)
    assert metric.status == KPIStatus.AMBER


def test_red_kpi():
    metric = KPIMetric('Bad Debt', 4.0, 2.0, '%', lower_is_better=True)
    assert metric.status == KPIStatus.RED


def test_lower_is_better_green():
    metric = KPIMetric('Complaints', 1.5, 2.0, '/100', lower_is_better=True)
    assert metric.status == KPIStatus.GREEN


def test_vs_target_pct():
    metric = KPIMetric('Margin', 1_100_000.0, 1_000_000.0, '£')
    assert metric.vs_target_pct == pytest.approx(10.0)


def test_rag_summary_all_green():
    d = _make_dashboard()
    s = d.rag_summary(_TARGETS)
    assert s['red'] == 0
    assert s['overall'] == 'GREEN'


def test_rag_summary_with_red():
    d = BoardDashboard(
        period=dt.date(2022, 6, 30),
        customer_count=300,
        net_margin_gbp=-200_000.0,
        gross_margin_gbp=2_000_000.0,
        treasury_gbp=80_000.0,
        enterprise_value_gbp=1_000_000.0,
        churn_rate_pct=8.0,
        complaints_per_100=5.0,
        bad_debt_ratio_pct=6.0,
        cash_runway_weeks=4.0,
        hedge_ratio_pct=20.0,
    )
    s = d.rag_summary(_TARGETS)
    assert s['red'] > 0
    assert s['overall'] == 'RED'
    assert len(s['at_risk_metrics']) > 0
