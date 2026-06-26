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
