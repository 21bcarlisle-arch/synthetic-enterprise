import pytest
from company.compliance.green_claims_audit import GreenClaimsAuditor, GreenClaimsAuditResult
from company.market.rego_portfolio import RegoPortfolio, RegoPurchase


def _make_portfolio(year=2022, mwh=500.0):
    p = RegoPortfolio()
    p.buy(RegoPurchase(
        purchase_id="R001",
        purchase_date=str(year) + "-01-15",
        scheme_year=year,
        mwh=mwh,
        price_per_mwh=6.50,
        generator="Humber Wind Farm",
        technology="wind_onshore",
    ))
    return p


def test_compliant_when_rego_exceeds_obligation():
    a = GreenClaimsAuditor(_make_portfolio(2022, mwh=500.0))
    result = a.audit(2022, {"GREEN_FIX_1YR": 200_000})
    assert result.status == "COMPLIANT"
    assert result.shortfall_mwh == 0.0
    assert result.penalty_estimate_gbp == 0.0


def test_non_compliant_when_no_rego():
    a = GreenClaimsAuditor(RegoPortfolio())
    result = a.audit(2022, {"GREEN_FIX_1YR": 500_000})
    assert result.status == "NON_COMPLIANT"
    assert result.shortfall_mwh > 0
    assert result.penalty_estimate_gbp > 0


def test_non_green_products_ignored():
    # R15 (KL-7 fix): no green product in use -> a genuine "no green claims made"
    # is NOT_APPLICABLE (distinct from COMPLIANT), never a false "compliant".
    a = GreenClaimsAuditor(RegoPortfolio())
    result = a.audit(2022, {"STD1": 1_000_000})
    assert result.status == "NOT_APPLICABLE"
    assert result.obligation_mwh == 0.0
    assert result.green_products_active == 0


def test_audit_result_year():
    a = GreenClaimsAuditor(_make_portfolio())
    result = a.audit(2022, {"GREEN_FIX_1YR": 100_000})
    assert isinstance(result, GreenClaimsAuditResult)
    assert result.year == 2022


def test_compute_obligation_green_product():
    a = GreenClaimsAuditor(RegoPortfolio())
    ob, count = a.compute_obligation({"GREEN_FIX_1YR": 200_000}, "2022-06-01")
    assert ob > 0
    assert count >= 1


def test_compute_obligation_zero_consumption():
    a = GreenClaimsAuditor(RegoPortfolio())
    ob, count = a.compute_obligation({"GREEN_FIX_1YR": 0.0}, "2022-06-01")
    assert ob == 0.0
    assert count == 0


def test_shortfall_relationship():
    a = GreenClaimsAuditor(_make_portfolio(2022, mwh=100.0))
    result = a.audit(2022, {"GREEN_FIX_1YR": 500_000})
    if result.shortfall_mwh > 0:
        delta = abs(result.shortfall_mwh - (result.obligation_mwh - result.rego_held_mwh))
        assert delta < 0.01


def test_coverage_capped_at_100():
    a = GreenClaimsAuditor(_make_portfolio(2022, mwh=10_000.0))
    result = a.audit(2022, {"GREEN_FIX_1YR": 10_000})
    assert result.coverage_pct <= 100.0


def test_summary_lines_contain_year_and_status():
    a = GreenClaimsAuditor(_make_portfolio())
    result = a.audit(2022, {"GREEN_FIX_1YR": 100_000})
    combined = " ".join(a.summary_lines(result))
    assert "2022" in combined
    assert any(s in combined for s in ("COMPLIANT", "AT_RISK", "NON_COMPLIANT"))


def test_wrong_year_rego_not_counted():
    a = GreenClaimsAuditor(_make_portfolio(2021, mwh=1000.0))
    result = a.audit(2022, {"GREEN_FIX_1YR": 500_000})
    assert result.rego_held_mwh == 0.0
    assert result.status != "COMPLIANT"


def test_empty_consumption_is_not_applicable():
    # R15 (KL-7 fix): no consumption -> no claims made -> NOT_APPLICABLE, a
    # distinct state from COMPLIANT (a zero obligation is not evidence of a
    # backed claim).
    a = GreenClaimsAuditor(RegoPortfolio())
    result = a.audit(2022, {})
    assert result.status == "NOT_APPLICABLE"
    assert result.obligation_mwh == 0.0


def test_at_risk_partial_coverage():
    a = GreenClaimsAuditor(_make_portfolio(2022, mwh=280.0))
    result = a.audit(2022, {"GREEN_FIX_1YR": 330_000})
    assert result.status in ("AT_RISK", "NON_COMPLIANT")
    assert result.coverage_pct < 100.0


# --- Phase LQ depth tests ---

def _result(**kwargs):
    defaults = dict(year=2022, obligation_mwh=200.0, rego_held_mwh=200.0,
                    coverage_pct=100.0, status="COMPLIANT", shortfall_mwh=0.0,
                    green_products_active=1, penalty_estimate_gbp=0.0)
    defaults.update(kwargs)
    return GreenClaimsAuditResult(**defaults)


def test_result_year_stored():
    r = _result(year=2023)
    assert r.year == 2023


def test_result_obligation_stored():
    r = _result(obligation_mwh=350.0)
    assert r.obligation_mwh == pytest.approx(350.0)


def test_result_rego_held_stored():
    r = _result(rego_held_mwh=280.0)
    assert r.rego_held_mwh == pytest.approx(280.0)


def test_result_coverage_stored():
    r = _result(coverage_pct=92.5)
    assert r.coverage_pct == pytest.approx(92.5)


def test_result_status_stored():
    r = _result(status="AT_RISK")
    assert r.status == "AT_RISK"


def test_result_shortfall_stored():
    r = _result(shortfall_mwh=50.0)
    assert r.shortfall_mwh == pytest.approx(50.0)


def test_result_green_products_stored():
    r = _result(green_products_active=3)
    assert r.green_products_active == 3


def test_result_penalty_stored():
    r = _result(penalty_estimate_gbp=2500.0)
    assert r.penalty_estimate_gbp == pytest.approx(2500.0)


def test_at_risk_threshold():
    assert GreenClaimsAuditor._AT_RISK_THRESHOLD == pytest.approx(90.0)


def test_compliant_threshold():
    assert GreenClaimsAuditor._COMPLIANT_THRESHOLD == pytest.approx(100.0)
