"""Tests for company.pricing.margin_feedback — Phase 16c realized-margin feedback."""
import pytest

from company.pricing.margin_feedback import (
    FEEDBACK_LOSS_THRESHOLD,
    FEEDBACK_MAX_SURCHARGE,
    compute_margin_surcharge,
)


def test_no_surcharge_for_profitable_term():
    """Positive prior-term margin → zero surcharge."""
    surcharge = compute_margin_surcharge(prev_margin_gbp=50.0, prev_revenue_gbp=500.0)
    assert surcharge == 0.0


def test_no_surcharge_for_break_even():
    """Zero margin → zero surcharge (not a loss)."""
    surcharge = compute_margin_surcharge(prev_margin_gbp=0.0, prev_revenue_gbp=500.0)
    assert surcharge == 0.0


def test_no_surcharge_below_threshold():
    """Small loss (3% of revenue, below 5% threshold) → zero surcharge."""
    # £15 loss on £500 revenue = 3%
    surcharge = compute_margin_surcharge(prev_margin_gbp=-15.0, prev_revenue_gbp=500.0)
    assert surcharge == 0.0


def test_surcharge_at_threshold():
    """Loss exactly at threshold (5%) → zero surcharge (threshold is exclusive floor)."""
    surcharge = compute_margin_surcharge(prev_margin_gbp=-25.0, prev_revenue_gbp=500.0)
    assert surcharge == 0.0


def test_surcharge_proportional_above_threshold():
    """Loss of 15% → surcharge of 10% (15% - 5% threshold)."""
    # £75 loss on £500 revenue = 15%
    surcharge = compute_margin_surcharge(prev_margin_gbp=-75.0, prev_revenue_gbp=500.0)
    expected = 0.15 - FEEDBACK_LOSS_THRESHOLD  # 10%
    assert abs(surcharge - expected) < 1e-9


def test_surcharge_capped_at_max():
    """Large loss (50%+ of revenue) → surcharge capped at FEEDBACK_MAX_SURCHARGE."""
    # £400 loss on £500 revenue = 80% — should cap at 20%
    surcharge = compute_margin_surcharge(prev_margin_gbp=-400.0, prev_revenue_gbp=500.0)
    assert surcharge == FEEDBACK_MAX_SURCHARGE


def test_zero_revenue_returns_zero():
    """Zero or negative revenue → zero surcharge (guards divide-by-zero)."""
    assert compute_margin_surcharge(-100.0, 0.0) == 0.0
    assert compute_margin_surcharge(-100.0, -50.0) == 0.0


def test_surcharge_never_exceeds_max():
    """Surcharge is always within [0.0, FEEDBACK_MAX_SURCHARGE]."""
    for margin in [-10000.0, -500.0, -100.0, -1.0, 0.0, 50.0]:
        for revenue in [100.0, 500.0, 10000.0]:
            s = compute_margin_surcharge(margin, revenue)
            assert 0.0 <= s <= FEEDBACK_MAX_SURCHARGE


# --- Phase KN depth tests ---

def test_threshold_is_float():
    assert isinstance(FEEDBACK_LOSS_THRESHOLD, float)


def test_max_surcharge_is_float():
    assert isinstance(FEEDBACK_MAX_SURCHARGE, float)


def test_threshold_positive():
    assert FEEDBACK_LOSS_THRESHOLD > 0.0


def test_max_surcharge_positive():
    assert FEEDBACK_MAX_SURCHARGE > 0.0


def test_surcharge_is_float():
    result = compute_margin_surcharge(-50.0, 500.0)
    assert isinstance(result, float)


def test_loss_exactly_at_threshold_zero():
    # exactly at threshold (5%) -> zero
    loss = FEEDBACK_LOSS_THRESHOLD * 500.0
    result = compute_margin_surcharge(-loss, 500.0)
    assert result == 0.0


def test_loss_6pct_gives_1pct_surcharge():
    # 6% - 5% threshold = 1% surcharge
    result = compute_margin_surcharge(-30.0, 500.0)  # 6% of 500
    assert result == pytest.approx(0.01, abs=1e-9)


def test_surcharge_increases_with_loss():
    s1 = compute_margin_surcharge(-50.0, 500.0)   # 10%
    s2 = compute_margin_surcharge(-75.0, 500.0)   # 15%
    assert s2 > s1


def test_extreme_loss_capped():
    s = compute_margin_surcharge(-999_999.0, 1000.0)
    assert s == pytest.approx(FEEDBACK_MAX_SURCHARGE)


def test_max_surcharge_greater_than_threshold():
    assert FEEDBACK_MAX_SURCHARGE > FEEDBACK_LOSS_THRESHOLD
