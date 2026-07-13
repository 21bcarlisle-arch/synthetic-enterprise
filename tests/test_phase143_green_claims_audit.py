"""Phase 143: Green tariff REGO compliance audit tests.

Tests that GreenClaimsAuditor correctly bridges TariffCatalogue (Ph 142) and
RegoPortfolio (Ph 139) to produce Ofgem-style compliance audit results.
"""
import pytest

from company.compliance.green_claims_audit import GreenClaimsAuditor, GreenClaimsAuditResult
from company.market.rego_portfolio import RegoPortfolio, RegoPurchase


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_portfolio_with_mwh(year: int, mwh: float) -> RegoPortfolio:
    p = RegoPortfolio()
    p.buy(RegoPurchase(
        purchase_id=f"R{year}-001",
        purchase_date=f"{year}-01-15",
        scheme_year=year,
        mwh=mwh,
        price_per_mwh=1.00,
        generator="Test Wind Farm",
        technology="wind_onshore",
    ))
    return p


def _auditor(year: int, mwh: float) -> GreenClaimsAuditor:
    return GreenClaimsAuditor(_make_portfolio_with_mwh(year, mwh))


# GREEN_FIX_1YR launched 2018-04-01, rego_required_pct=1.0
# Supplying 10,000 kWh on GREEN_FIX_1YR => obligation = 10 MWh


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_auditor_construction():
    portfolio = RegoPortfolio()
    auditor = GreenClaimsAuditor(portfolio)
    assert auditor is not None


def test_compliant_when_coverage_exactly_100pct():
    # 10,000 kWh on GREEN_FIX_1YR (100% REGO) = 10 MWh obligation; hold 10 MWh
    auditor = _auditor(2020, 10.0)
    result = auditor.audit(2020, {"GREEN_FIX_1YR": 10_000.0}, date_str="2020-12-31")
    assert result.status == "COMPLIANT"
    assert result.shortfall_mwh == 0.0
    assert result.coverage_pct == 100.0
    assert result.penalty_estimate_gbp == 0.0


def test_compliant_when_coverage_exceeds_100pct():
    # Hold more than needed
    auditor = _auditor(2020, 20.0)
    result = auditor.audit(2020, {"GREEN_FIX_1YR": 10_000.0}, date_str="2020-12-31")
    assert result.status == "COMPLIANT"
    assert result.coverage_pct == 100.0   # capped at 100
    assert result.shortfall_mwh == 0.0


def test_at_risk_when_coverage_between_90_and_100pct():
    # Obligation 10 MWh, hold 9.5 MWh => 95% coverage
    auditor = _auditor(2020, 9.5)
    result = auditor.audit(2020, {"GREEN_FIX_1YR": 10_000.0}, date_str="2020-12-31")
    assert result.status == "AT_RISK"
    assert result.shortfall_mwh == pytest.approx(0.5, abs=0.01)
    assert result.penalty_estimate_gbp == pytest.approx(0.5 * 50.0, abs=0.01)


def test_non_compliant_when_coverage_below_90pct():
    # Obligation 10 MWh, hold 8 MWh => 80% coverage
    auditor = _auditor(2020, 8.0)
    result = auditor.audit(2020, {"GREEN_FIX_1YR": 10_000.0}, date_str="2020-12-31")
    assert result.status == "NON_COMPLIANT"
    assert result.shortfall_mwh == pytest.approx(2.0, abs=0.01)
    assert result.penalty_estimate_gbp == pytest.approx(100.0, abs=0.01)


def test_non_green_product_contributes_zero_obligation():
    # STD_FIX_1YR is not green -- no obligation even with large consumption.
    # R15 (KL-7 fix): no green claim made -> NOT_APPLICABLE (distinct from
    # COMPLIANT), not a false "compliant".
    auditor = _auditor(2020, 0.0)
    result = auditor.audit(2020, {"STD_FIX_1YR": 100_000.0}, date_str="2020-12-31")
    assert result.obligation_mwh == 0.0
    assert result.status == "NOT_APPLICABLE"
    assert result.green_products_active == 0


def test_obligation_from_ic_green_cert_is_half():
    # IC_GREEN_CERT rego_required_pct=0.5; 20,000 kWh => 10 MWh obligation
    # IC_GREEN_CERT active until 2023-12-31
    auditor = _auditor(2022, 10.0)
    result = auditor.audit(2022, {"IC_GREEN_CERT": 20_000.0}, date_str="2022-12-31")
    assert result.obligation_mwh == pytest.approx(10.0, abs=0.01)
    assert result.status == "COMPLIANT"


def test_withdrawn_product_not_counted_after_withdrawal():
    # IC_GREEN_CERT withdrawn 2023-12-31; audit date 2024-06-30 => excluded
    auditor = _auditor(2024, 0.0)
    result = auditor.audit(2024, {"IC_GREEN_CERT": 20_000.0}, date_str="2024-06-30")
    assert result.obligation_mwh == 0.0
    assert result.green_products_active == 0
    # R15 (KL-7 fix): the product is withdrawn, so no active green claim ->
    # NOT_APPLICABLE, not a false "compliant".
    assert result.status == "NOT_APPLICABLE"


def test_multiple_green_products_aggregate_obligation():
    # GREEN_FIX_1YR: 10,000 kWh => 10 MWh; GREEN_FIX_2YR: 5,000 kWh => 5 MWh
    # Total obligation = 15 MWh; hold 15 MWh => COMPLIANT
    auditor = _auditor(2020, 15.0)
    result = auditor.audit(
        2020,
        {"GREEN_FIX_1YR": 10_000.0, "GREEN_FIX_2YR": 5_000.0},
        date_str="2020-12-31",
    )
    assert result.obligation_mwh == pytest.approx(15.0, abs=0.01)
    assert result.green_products_active == 2
    assert result.status == "COMPLIANT"


def test_green_products_active_count_correct():
    auditor = _auditor(2020, 100.0)
    result = auditor.audit(
        2020,
        {
            "GREEN_FIX_1YR": 5_000.0,
            "GREEN_FIX_2YR": 5_000.0,
            "STD_FIX_1YR": 10_000.0,   # non-green, should not count
        },
        date_str="2020-12-31",
    )
    assert result.green_products_active == 2


def test_summary_lines_compliant():
    auditor = _auditor(2021, 10.0)
    result = auditor.audit(2021, {"GREEN_FIX_1YR": 10_000.0}, date_str="2021-12-31")
    lines = auditor.summary_lines(result)
    assert any("COMPLIANT" in l for l in lines)
    assert len(lines) == 3   # status + obligation + held; no shortfall line


def test_summary_lines_non_compliant_includes_shortfall():
    auditor = _auditor(2022, 5.0)
    result = auditor.audit(2022, {"GREEN_FIX_1YR": 10_000.0}, date_str="2022-12-31")
    lines = auditor.summary_lines(result)
    assert any("Shortfall" in l for l in lines)
    assert any("penalty" in l.lower() for l in lines)


def test_retired_regos_count_toward_coverage():
    # Buy 10 MWh, retire them -- they still count toward coverage
    portfolio = RegoPortfolio()
    purchase = portfolio.buy(RegoPurchase(
        purchase_id="R2020-001",
        purchase_date="2020-01-15",
        scheme_year=2020,
        mwh=10.0,
        price_per_mwh=1.00,
        generator="Humber Wind",
        technology="wind_offshore",
    ))
    portfolio.retire("R2020-001", "2020-03-31")
    auditor = GreenClaimsAuditor(portfolio)
    result = auditor.audit(2020, {"GREEN_FIX_1YR": 10_000.0}, date_str="2020-12-31")
    assert result.status == "COMPLIANT"
    assert result.rego_held_mwh == pytest.approx(10.0, abs=0.01)
