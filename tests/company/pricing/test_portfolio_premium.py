"""Tests for company.pricing.tariff_engine.compute_portfolio_premium — Phase 17a."""
import pytest

from company.pricing.tariff_engine import (
    PORTFOLIO_PREMIUM_MAX,
    PORTFOLIO_PREMIUM_MIN,
    PORTFOLIO_TARGET_MARGIN_RATE,
    compute_portfolio_premium,
)


def test_no_history_returns_zero():
    """Empty margin history → no adjustment (no data to learn from)."""
    assert compute_portfolio_premium([]) == 0.0


def test_on_target_returns_zero():
    """Mean margin exactly at target → zero premium (no adjustment needed)."""
    target = PORTFOLIO_TARGET_MARGIN_RATE
    result = compute_portfolio_premium([target, target, target])
    assert abs(result) < 1e-9


def test_below_target_raises_premium():
    """Below-target margins → positive premium (company raises rates)."""
    # All terms at -10% margin — well below 8% target
    result = compute_portfolio_premium([-0.10, -0.10, -0.10])
    assert result > 0.0


def test_above_target_lowers_premium():
    """Above-target margins → negative premium (company can afford to soften rates)."""
    # All terms at 30% margin — well above 8% target
    result = compute_portfolio_premium([0.30, 0.30, 0.30])
    assert result < 0.0


def test_half_life_proportionality():
    """Premium is half_life fraction of shortfall from target."""
    # mean margin = 0.0, target = 0.08, shortfall = 0.08, half_life = 0.5 → premium = 0.04
    result = compute_portfolio_premium([0.0, 0.0, 0.0], target=0.08, half_life=0.5)
    assert abs(result - 0.04) < 1e-9


def test_crisis_level_loss_capped_at_max():
    """Severe crisis losses → premium capped at PORTFOLIO_PREMIUM_MAX."""
    # -80% margin rates → shortfall = 88%, × 0.5 = 44% — must cap at PORTFOLIO_PREMIUM_MAX
    result = compute_portfolio_premium([-0.80, -0.80, -0.80])
    assert result == pytest.approx(PORTFOLIO_PREMIUM_MAX)


def test_excess_profit_capped_at_min():
    """Excessive over-earning → discount capped at PORTFOLIO_PREMIUM_MIN (floor)."""
    # 90% margin rates → shortfall = 8% - 90% = -82%, × 0.5 = -41% — must cap at min
    result = compute_portfolio_premium([0.90, 0.90, 0.90])
    assert result == pytest.approx(PORTFOLIO_PREMIUM_MIN)


def test_mixed_history_uses_mean():
    """Mixed good/bad terms → mean drives the premium."""
    # half at -20%, half at +36% → mean = 8% = target → zero premium
    result = compute_portfolio_premium([-0.20, 0.36, -0.20, 0.36])
    assert abs(result) < 1e-9


def test_premium_always_in_bounds():
    """Premium never exits [PORTFOLIO_PREMIUM_MIN, PORTFOLIO_PREMIUM_MAX]."""
    extreme_cases = [
        [-5.0, -5.0],
        [10.0, 10.0],
        [-1.0, 1.0, -1.0],
        [0.0],
        [0.08],
    ]
    for rates in extreme_cases:
        p = compute_portfolio_premium(rates)
        assert PORTFOLIO_PREMIUM_MIN <= p <= PORTFOLIO_PREMIUM_MAX
