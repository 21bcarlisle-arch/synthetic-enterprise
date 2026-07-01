import datetime as dt
import pytest
from company.regulatory.annual_obligations import (
    ObligationStatus, ObligationLineItem, AnnualObligationsReport, build_obligations_report
)


def test_obligation_delivery_pct():
    o = ObligationLineItem(
        name='WHD', obligation_value=200, delivered_value=180,
        unit='customers', status=ObligationStatus.AT_RISK,
    )
    assert o.delivery_pct == pytest.approx(90.0)
    assert o.shortfall == pytest.approx(20.0)


def test_build_all_met():
    r = build_obligations_report(
        year=2023, report_date=dt.date(2024, 4, 1),
        whd_obligation_customers=150, whd_delivered_customers=155,
        eco4_obligation_mwh=500.0, eco4_delivered_mwh=520.0,
        gsop_breaches=0, gsop_payments_gbp=0.0,
        ofgem_return_submitted=True,
    )
    assert r.overall_status == ObligationStatus.MET
    assert r.met_count == 4
    assert r.breached_count == 0
    assert r.total_penalty_estimate_gbp == pytest.approx(0.0)


def test_whd_shortfall_penalty():
    r = build_obligations_report(
        year=2022, report_date=dt.date(2023, 4, 1),
        whd_obligation_customers=200, whd_delivered_customers=160,
        eco4_obligation_mwh=0.0, eco4_delivered_mwh=0.0,
        gsop_breaches=0, gsop_payments_gbp=0.0,
        ofgem_return_submitted=True,
    )
    whd = r.get('WHD')
    assert whd.status == ObligationStatus.BREACHED
    assert whd.penalty_estimate_gbp == pytest.approx(40 * 150.0)


def test_eco4_at_risk():
    r = build_obligations_report(
        year=2023, report_date=dt.date(2024, 4, 1),
        whd_obligation_customers=0, whd_delivered_customers=0,
        eco4_obligation_mwh=1000.0, eco4_delivered_mwh=900.0,
        gsop_breaches=0, gsop_payments_gbp=0.0,
        ofgem_return_submitted=True,
    )
    eco = r.get('ECO4')
    assert eco.status == ObligationStatus.AT_RISK
    assert eco.shortfall == pytest.approx(100.0)


def test_gsop_breaches():
    r = build_obligations_report(
        year=2022, report_date=dt.date(2023, 4, 1),
        whd_obligation_customers=0, whd_delivered_customers=0,
        eco4_obligation_mwh=0.0, eco4_delivered_mwh=0.0,
        gsop_breaches=5, gsop_payments_gbp=375.0,
        ofgem_return_submitted=True,
    )
    gsop = r.get('GSOP')
    assert gsop.status == ObligationStatus.BREACHED
    assert gsop.penalty_estimate_gbp == pytest.approx(375.0)
    assert r.overall_status == ObligationStatus.BREACHED


def test_ofgem_return_overdue():
    r = build_obligations_report(
        year=2022, report_date=dt.date(2023, 6, 1),
        whd_obligation_customers=0, whd_delivered_customers=0,
        eco4_obligation_mwh=0.0, eco4_delivered_mwh=0.0,
        gsop_breaches=0, gsop_payments_gbp=0.0,
        ofgem_return_submitted=False,
        ofgem_return_due_date=dt.date(2023, 4, 30),
    )
    ret = r.get('Ofgem_annual_return')
    assert ret.status == ObligationStatus.BREACHED


def test_rego_coverage_breach():
    r = build_obligations_report(
        year=2023, report_date=dt.date(2024, 4, 1),
        whd_obligation_customers=0, whd_delivered_customers=0,
        eco4_obligation_mwh=0.0, eco4_delivered_mwh=0.0,
        gsop_breaches=0, gsop_payments_gbp=0.0,
        ofgem_return_submitted=True,
        rego_obligation_mwh=2000.0, rego_held_mwh=1500.0,
    )
    rego = r.get('REGO')
    assert rego.status == ObligationStatus.BREACHED
    assert rego.penalty_estimate_gbp == pytest.approx(500.0 * 50.0)


def test_summary_dict():
    r = build_obligations_report(
        year=2023, report_date=dt.date(2024, 4, 1),
        whd_obligation_customers=100, whd_delivered_customers=100,
        eco4_obligation_mwh=0.0, eco4_delivered_mwh=0.0,
        gsop_breaches=0, gsop_payments_gbp=0.0,
        ofgem_return_submitted=True,
    )
    s = r.summary()
    assert s['year'] == 2023
    assert s['overall_status'] == 'met'
    assert 'total_penalty_estimate_gbp' in s


# --- Phase KE depth tests ---

def test_get_unknown_returns_none():
    r = build_obligations_report(
        year=2023, report_date=dt.date(2024, 4, 1),
        whd_obligation_customers=0, whd_delivered_customers=0,
        eco4_obligation_mwh=0.0, eco4_delivered_mwh=0.0,
        gsop_breaches=0, gsop_payments_gbp=0.0,
        ofgem_return_submitted=True,
    )
    assert r.get('UNKNOWN_OBL') is None


def test_at_risk_no_breach_overall():
    r = build_obligations_report(
        year=2023, report_date=dt.date(2024, 4, 1),
        whd_obligation_customers=0, whd_delivered_customers=0,
        eco4_obligation_mwh=1000.0, eco4_delivered_mwh=900.0,
        gsop_breaches=0, gsop_payments_gbp=0.0,
        ofgem_return_submitted=True,
    )
    assert r.overall_status == ObligationStatus.AT_RISK
    assert r.breached_count == 0


def test_total_penalty_accumulates():
    r = build_obligations_report(
        year=2022, report_date=dt.date(2023, 4, 1),
        whd_obligation_customers=200, whd_delivered_customers=0,
        eco4_obligation_mwh=0.0, eco4_delivered_mwh=0.0,
        gsop_breaches=1, gsop_payments_gbp=50.0,
        ofgem_return_submitted=True,
        rego_obligation_mwh=0.0, rego_held_mwh=0.0,
    )
    # WHD: 200*150=30000; GSOP: 50
    assert r.total_penalty_estimate_gbp == pytest.approx(30050.0)


def test_whd_zero_obligation_not_in_report():
    r = build_obligations_report(
        year=2023, report_date=dt.date(2024, 4, 1),
        whd_obligation_customers=0, whd_delivered_customers=0,
        eco4_obligation_mwh=0.0, eco4_delivered_mwh=0.0,
        gsop_breaches=0, gsop_payments_gbp=0.0,
        ofgem_return_submitted=True,
    )
    assert r.get('WHD') is None


def test_no_rego_obligation_no_rego_item():
    r = build_obligations_report(
        year=2023, report_date=dt.date(2024, 4, 1),
        whd_obligation_customers=0, whd_delivered_customers=0,
        eco4_obligation_mwh=0.0, eco4_delivered_mwh=0.0,
        gsop_breaches=0, gsop_payments_gbp=0.0,
        ofgem_return_submitted=True,
        rego_obligation_mwh=0.0, rego_held_mwh=0.0,
    )
    assert r.get('REGO') is None


def test_report_date_isoformat():
    r = build_obligations_report(
        year=2023, report_date=dt.date(2024, 4, 1),
        whd_obligation_customers=0, whd_delivered_customers=0,
        eco4_obligation_mwh=0.0, eco4_delivered_mwh=0.0,
        gsop_breaches=0, gsop_payments_gbp=0.0,
        ofgem_return_submitted=True,
    )
    assert r.summary()['report_date'] == '2024-04-01'


def test_ofgem_at_risk_before_due_date():
    r = build_obligations_report(
        year=2022, report_date=dt.date(2023, 3, 1),
        whd_obligation_customers=0, whd_delivered_customers=0,
        eco4_obligation_mwh=0.0, eco4_delivered_mwh=0.0,
        gsop_breaches=0, gsop_payments_gbp=0.0,
        ofgem_return_submitted=False,
        ofgem_return_due_date=dt.date(2023, 4, 30),
    )
    ret = r.get('Ofgem_annual_return')
    assert ret.status == ObligationStatus.AT_RISK


def test_eco4_100_pct_met():
    r = build_obligations_report(
        year=2023, report_date=dt.date(2024, 4, 1),
        whd_obligation_customers=0, whd_delivered_customers=0,
        eco4_obligation_mwh=1000.0, eco4_delivered_mwh=1000.0,
        gsop_breaches=0, gsop_payments_gbp=0.0,
        ofgem_return_submitted=True,
    )
    assert r.get('ECO4').status == ObligationStatus.MET


def test_eco4_80_pct_breached():
    r = build_obligations_report(
        year=2023, report_date=dt.date(2024, 4, 1),
        whd_obligation_customers=0, whd_delivered_customers=0,
        eco4_obligation_mwh=1000.0, eco4_delivered_mwh=800.0,
        gsop_breaches=0, gsop_payments_gbp=0.0,
        ofgem_return_submitted=True,
    )
    assert r.get('ECO4').status == ObligationStatus.BREACHED


def test_summary_keys_present():
    r = build_obligations_report(
        year=2023, report_date=dt.date(2024, 4, 1),
        whd_obligation_customers=0, whd_delivered_customers=0,
        eco4_obligation_mwh=0.0, eco4_delivered_mwh=0.0,
        gsop_breaches=0, gsop_payments_gbp=0.0,
        ofgem_return_submitted=True,
    )
    s = r.summary()
    for k in ('year', 'report_date', 'met', 'at_risk', 'breached', 'overall_status', 'total_penalty_estimate_gbp'):
        assert k in s
