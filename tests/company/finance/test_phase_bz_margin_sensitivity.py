"""Phase BZ: Portfolio Margin Sensitivity tests."""
import pytest
from company.finance.portfolio_margin_sensitivity import (
    PortfolioMarginSensitivityBook, SensitivityFactor
)


def _book(net=100000, n=14, rev=None, whl=None, ncc=None, fixed=6000, bad=5000, cap=5000):
    """Create a simple test book with net margin ~100k."""
    if rev is None:
        rev = 500000
    if whl is None:
        whl = rev - net - (ncc or 200000) - fixed - bad - cap
    return PortfolioMarginSensitivityBook(
        base_revenue_gbp=rev,
        base_wholesale_cost_gbp=whl if whl is not None else 200000,
        base_non_commodity_cost_gbp=ncc if ncc is not None else 200000,
        base_fixed_cost_gbp=fixed,
        base_bad_debt_gbp=bad,
        base_capital_cost_gbp=cap,
        base_active_customers=n,
        base_churn_rate_pct=5.0,
    )


def _std_book():
    return PortfolioMarginSensitivityBook(
        base_revenue_gbp=1_000_000,
        base_wholesale_cost_gbp=400_000,
        base_non_commodity_cost_gbp=300_000,
        base_fixed_cost_gbp=10_000,
        base_bad_debt_gbp=10_000,
        base_capital_cost_gbp=10_000,
        base_active_customers=20,
        base_churn_rate_pct=5.0,
    )


# 1. Base net margin correct (1M - 400k - 300k - 10k - 10k - 10k = 270k)
def test_base_net_margin():
    b = _std_book()
    assert abs(b.base_net_margin_gbp - 270_000) < 1


# 2. Wholesale price shock +10% is adverse
def test_wholesale_shock_adverse():
    b = _std_book()
    s = b.wholesale_price_shock(10)
    assert s.is_adverse
    assert s.delta_gbp < 0


# 3. Wholesale +10% decreases net margin by 10% of wholesale cost
def test_wholesale_shock_magnitude():
    b = _std_book()
    s = b.wholesale_price_shock(10)
    expected_delta = -400_000 * 0.10
    assert abs(s.delta_gbp - expected_delta) < 1


# 4. Demand volume -5% is adverse
def test_demand_shock_adverse():
    b = _std_book()
    s = b.demand_volume_shock(-5)
    assert s.is_adverse


# 5. Demand -5% affects revenue and wholesale proportionally
def test_demand_shock_gm_neutral():
    b = _std_book()
    s_d5 = b.demand_volume_shock(-5)
    # Revenue drops by 5% of 1M = -50k; wholesale drops by 5% of 400k = -20k
    # net delta = -50k + 20k = -30k
    assert abs(s_d5.delta_gbp - (-30_000)) < 1


# 6. Churn +5pp is adverse
def test_churn_shock_adverse():
    b = _std_book()
    s = b.churn_shock(5)
    assert s.is_adverse
    assert s.delta_gbp < 0


# 7. Churn +5pp = loses 5% of customers * margin per customer
def test_churn_shock_magnitude():
    b = _std_book()
    s = b.churn_shock(5)
    # 20 customers, net=270k, margin/cust=13.5k; 5%*20=1 cust; lost=13.5k
    expected_delta = -(270_000 / 20) * (20 * 0.05)
    assert abs(s.delta_gbp - expected_delta) < 1


# 8. NCC +10% is adverse
def test_ncc_shock_adverse():
    b = _std_book()
    s = b.non_commodity_cost_shock(10)
    assert s.is_adverse


# 9. Fixed cost +5k correct
def test_fixed_cost_shock():
    b = _std_book()
    s = b.fixed_cost_shock(5_000)
    assert abs(s.delta_gbp - (-5_000)) < 1


# 10. Standard table has 10 rows
def test_standard_table_length():
    b = _std_book()
    table = b.standard_sensitivity_table()
    assert len(table) == 10


# 11. Most sensitive factor is wholesale_price
def test_most_sensitive_factor():
    b = _std_book()
    # Wholesale +20% = -80k; demand -10% = -60k; churn +10pp = -27k
    # Most sensitive = WHOLESALE_PRICE
    assert b.most_sensitive_factor() == SensitivityFactor.WHOLESALE_PRICE


# 12. Severity: LOW/MEDIUM/HIGH bands
def test_severity_bands():
    b = _std_book()
    fixed_small = b.fixed_cost_shock(5_000)  # delta = -5k on 270k base = -1.9% -> LOW
    assert fixed_small.severity == "LOW"
    whl_10 = b.wholesale_price_shock(10)  # -40k on 270k = -14.8% -> MEDIUM
    assert whl_10.severity == "MEDIUM"
    whl_20 = b.wholesale_price_shock(20)  # -80k on 270k = -29.6% -> HIGH
    assert whl_20.severity == "HIGH"


# --- Phase LW depth tests ---

def test_base_net_margin_stored():
    b = _book(net=100000)
    assert b.base_net_margin_gbp == pytest.approx(100000, rel=0.01)


def test_factor_stored_in_scenario():
    b = _book()
    sc = b.wholesale_price_shock(10.0)
    assert sc.factor == SensitivityFactor.WHOLESALE_PRICE


def test_label_stored_in_scenario():
    b = _book()
    sc = b.wholesale_price_shock(10.0)
    assert '10' in sc.label


def test_shock_magnitude_stored():
    b = _book()
    sc = b.wholesale_price_shock(20.0)
    assert sc.shock_magnitude == pytest.approx(20.0)


def test_base_net_in_scenario():
    b = _book(net=100000)
    sc = b.wholesale_price_shock(10.0)
    assert sc.base_net_margin_gbp == pytest.approx(100000, rel=0.01)


def test_is_adverse_true_for_positive_shock():
    b = _book(net=100000)
    sc = b.wholesale_price_shock(50.0)
    assert sc.is_adverse is True


def test_no_shock_not_adverse():
    b = _book()
    sc = b.wholesale_price_shock(0.0)
    assert sc.is_adverse is False


def test_severity_high_large_shock():
    b = _book()
    sc = b.wholesale_price_shock(100.0)
    assert sc.severity in ('HIGH', 'MEDIUM')


def test_delta_gbp_negative_for_cost_increase():
    b = _book(net=100000)
    sc = b.wholesale_price_shock(30.0)
    assert sc.delta_gbp < 0


def test_sensitivity_factors_count():
    assert len(SensitivityFactor) == 5
