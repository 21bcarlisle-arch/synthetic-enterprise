import pytest
from company.finance.board_kpis import KPIStatus, KPIValue, BoardKPIDashboard, build_board_dashboard


def _make_dashboard(bad_debt=1.5, csat=4.2, gsop=100.0):
    return build_board_dashboard(
        year=2023, quarter=2,
        customer_count=5000, customer_target=5000,
        gross_margin_pct=12.0, gm_target_pct=10.0,
        ebitda_margin_pct=5.0, ebitda_target_pct=4.0,
        bad_debt_pct=bad_debt, bad_debt_target_pct=1.5,
        complaint_resolution_days=14.0, crt_target_days=14.0,
        csat_score=csat, csat_target=4.0,
        gsop_compliance_pct=gsop, gsop_target_pct=100.0,
    )


def test_all_green_at_target():
    d = _make_dashboard()
    assert d.overall_status == KPIStatus.GREEN
    assert d.red_count == 0


def test_kpi_value_green_above_target():
    kpi = KPIValue('margin', 12.0, '%', 10.0)
    assert kpi.status == KPIStatus.GREEN


def test_kpi_value_amber():
    kpi = KPIValue('margin', 8.2, '%', 10.0)
    assert kpi.status == KPIStatus.AMBER


def test_kpi_value_red():
    kpi = KPIValue('margin', 6.0, '%', 10.0)
    assert kpi.status == KPIStatus.RED


def test_lower_is_better_green():
    kpi = KPIValue('bad_debt', 1.0, '%', 2.0, lower_is_better=True)
    assert kpi.status == KPIStatus.GREEN


def test_lower_is_better_red():
    kpi = KPIValue('bad_debt', 5.0, '%', 1.5, lower_is_better=True)
    assert kpi.status == KPIStatus.RED


def test_bad_debt_crisis_triggers_red():
    d = _make_dashboard(bad_debt=5.0)
    assert d.red_count >= 1
    assert d.overall_status == KPIStatus.RED


def test_get_kpi_by_name():
    d = _make_dashboard()
    kpi = d.get_kpi('CSAT score')
    assert kpi is not None
    assert kpi.value == pytest.approx(4.2)


def test_summary_includes_rag_counts():
    d = _make_dashboard()
    s = d.summary()
    assert 'green' in s
    assert 'red' in s
    assert 'overall_status' in s
    assert len(s['kpis']) == 7
