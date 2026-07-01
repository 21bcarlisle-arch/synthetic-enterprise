"""Phase 141: CLV calculator tests."""

import pytest
from company.crm.clv_calculator import compute_clv, clv_to_cac_ratio, portfolio_clv_summary


def test_positive_margin_positive_clv():
    r = compute_clv("C1", 200.0)
    assert r.clv_gbp > 0


def test_negative_margin_negative_clv():
    r = compute_clv("C2", -50.0)
    assert r.clv_gbp < 0
    assert r.margin_tier == "NET_NEGATIVE"


def test_tenure_from_churn():
    r = compute_clv("C3", 100.0, churn_rate=0.25)
    assert abs(r.expected_tenure_years - 4.0) < 0.01  # 1/0.25 = 4 years


def test_explicit_tenure_overrides_churn():
    r = compute_clv("C4", 100.0, tenure_years=5.0)
    assert abs(r.expected_tenure_years - 5.0) < 0.01


def test_premium_tier():
    r = compute_clv("C5", 300.0)
    assert r.margin_tier == "PREMIUM"


def test_low_tier():
    r = compute_clv("C6", 30.0)
    assert r.margin_tier == "LOW"


def test_cac_ratio_healthy():
    result = clv_to_cac_ratio(1500.0, 400.0)
    assert result["verdict"] == "HEALTHY"
    assert result["ratio"] >= 3.0


def test_cac_ratio_loss_making():
    result = clv_to_cac_ratio(50.0, 200.0)
    assert result["verdict"] == "LOSS_MAKING"


def test_portfolio_summary():
    results = [
        compute_clv("C1", 200.0),
        compute_clv("C2", 50.0),
        compute_clv("C3", -30.0),
    ]
    s = portfolio_clv_summary(results)
    assert s["count"] == 3
    assert "NET_NEGATIVE" in s["tiers"]
    assert s["mean_clv_gbp"] == pytest.approx(s["total_clv_gbp"] / 3, abs=0.01)


# --- Phase KR depth tests ---

def test_customer_id_stored():
    r = compute_clv('CUST_X', 150.0)
    assert r.customer_id == 'CUST_X'


def test_annual_margin_stored():
    r = compute_clv('C1', 150.0)
    assert r.annual_net_margin_gbp == pytest.approx(150.0)


def test_discount_rate_positive():
    r = compute_clv('C1', 100.0)
    assert r.discount_rate > 0.0


def test_standard_tier():
    r = compute_clv('C1', 80.0)
    assert r.margin_tier == 'STANDARD'


def test_clv_is_float():
    r = compute_clv('C1', 100.0)
    assert isinstance(r.clv_gbp, float)


def test_higher_margin_higher_clv():
    r1 = compute_clv('C1', 100.0)
    r2 = compute_clv('C2', 200.0)
    assert r2.clv_gbp > r1.clv_gbp


def test_cac_ratio_uncapped_zero_cac():
    result = clv_to_cac_ratio(200.0, 0.0)
    assert result['verdict'] == 'UNCAPPED'


def test_cac_ratio_break_even():
    # CLV == CAC -> ratio = 1.0 -> BREAK_EVEN
    result = clv_to_cac_ratio(200.0, 200.0)
    assert result['verdict'] == 'BREAK_EVEN'


def test_portfolio_summary_mean_positive():
    results = [compute_clv('C1', 100.0), compute_clv('C2', 200.0)]
    s = portfolio_clv_summary(results)
    assert s['mean_clv_gbp'] > 0.0


def test_portfolio_summary_total_clv():
    results = [compute_clv('C1', 100.0), compute_clv('C2', 200.0)]
    s = portfolio_clv_summary(results)
    assert s['total_clv_gbp'] == pytest.approx(results[0].clv_gbp + results[1].clv_gbp)
