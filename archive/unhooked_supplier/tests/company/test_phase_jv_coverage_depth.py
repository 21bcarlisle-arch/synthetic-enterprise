# Increment 3: the legs of tests/company/test_phase_jv_coverage_depth.py that test archived modules. Its live legs stay there.
"""Phase JV: Coverage Depth Sprint XLIV -- 30 tests.

Modules: risk_appetite · hedging_schedule · annual_obligations
"""
import datetime as dt
import pytest
from company.regulatory.annual_obligations import (
    ObligationStatus, build_obligations_report,
)


def _bkw(**overrides):
    kw = dict(year=2023, report_date=dt.date(2024, 4, 1),
              whd_obligation_customers=0, whd_delivered_customers=0,
              eco4_obligation_mwh=0.0, eco4_delivered_mwh=0.0,
              gsop_breaches=0, gsop_payments_gbp=0.0,
              ofgem_return_submitted=True)
    kw.update(overrides)
    return kw


# annual_obligations

def test_ao_whd_at_risk_95pct():
    r = build_obligations_report(**_bkw(
        whd_obligation_customers=200, whd_delivered_customers=190))
    assert r.get("WHD").status == ObligationStatus.AT_RISK


def test_ao_eco4_met_exact_100pct():
    r = build_obligations_report(**_bkw(
        eco4_obligation_mwh=500.0, eco4_delivered_mwh=500.0))
    eco = r.get("ECO4")
    assert eco.status == ObligationStatus.MET
    assert eco.penalty_estimate_gbp == pytest.approx(0.0)


def test_ao_eco4_breached_below_85pct():
    r = build_obligations_report(**_bkw(
        eco4_obligation_mwh=1000.0, eco4_delivered_mwh=800.0))
    eco = r.get("ECO4")
    assert eco.status == ObligationStatus.BREACHED
    assert eco.penalty_estimate_gbp == pytest.approx(200.0 * 10.0)


def test_ao_rego_at_risk_92pct():
    r = build_obligations_report(**_bkw(
        rego_obligation_mwh=1000.0, rego_held_mwh=920.0))
    assert r.get("REGO").status == ObligationStatus.AT_RISK


def test_ao_overall_at_risk_no_breach():
    r = build_obligations_report(**_bkw(
        whd_obligation_customers=200, whd_delivered_customers=190,
        eco4_obligation_mwh=1000.0, eco4_delivered_mwh=1000.0))
    assert r.overall_status == ObligationStatus.AT_RISK
    assert r.breached_count == 0


def test_ao_total_penalty_accumulates():
    r = build_obligations_report(**_bkw(
        whd_obligation_customers=200, whd_delivered_customers=160,
        eco4_obligation_mwh=1000.0, eco4_delivered_mwh=800.0))
    expected = (200 - 160) * 150.0 + (1000.0 - 800.0) * 10.0
    assert r.total_penalty_estimate_gbp == pytest.approx(expected)


def test_ao_get_returns_none_for_unknown():
    r = build_obligations_report(**_bkw())
    assert r.get("UNKNOWN") is None


def test_ao_ofgem_at_risk_before_due_date():
    r = build_obligations_report(**_bkw(
        ofgem_return_submitted=False,
        ofgem_return_due_date=dt.date(2024, 6, 30),
        report_date=dt.date(2024, 4, 1)))
    assert r.get("Ofgem_annual_return").status == ObligationStatus.AT_RISK


def test_ao_no_rego_item_when_obligation_zero():
    r = build_obligations_report(**_bkw(rego_obligation_mwh=0.0, rego_held_mwh=0.0))
    assert r.get("REGO") is None


def test_ao_summary_has_expected_keys():
    r = build_obligations_report(**_bkw())
    s = r.summary()
    for key in ("year", "report_date", "total_obligations", "met",
                "at_risk", "breached", "overall_status", "total_penalty_estimate_gbp"):
        assert key in s
