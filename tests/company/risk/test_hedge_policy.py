"""Phase 22b: tests for company/risk/hedge_policy.py."""

from company.risk.hedge_policy import (
    COMPANY_MIN_HEDGE_FLOOR,
    COMPANY_EVOLUTION_STEP,
    COMPANY_MARGIN_TOLERANCE_GBP,
    company_evolve_hedge_fraction,
)


def test_floor_is_85_percent():
    assert COMPANY_MIN_HEDGE_FLOOR == 0.85


def test_hedge_beats_naked_raises_fraction():
    """Actual > naked by more than tolerance → raise hedge fraction."""
    hf, reason = company_evolve_hedge_fraction(0.85, naked_net_gbp=100.0, actual_net_gbp=200.0)
    assert hf == pytest.approx(0.85 + COMPANY_EVOLUTION_STEP)
    assert "raise" in reason


def test_naked_beats_hedge_trims_fraction():
    """Naked > actual by more than tolerance → trim hedge fraction."""
    hf, reason = company_evolve_hedge_fraction(0.95, naked_net_gbp=200.0, actual_net_gbp=100.0)
    assert hf == pytest.approx(0.95 - COMPANY_EVOLUTION_STEP)
    assert "trim" in reason


def test_trim_floored_at_min_hedge():
    """Cannot trim below COMPANY_MIN_HEDGE_FLOOR."""
    hf, _ = company_evolve_hedge_fraction(COMPANY_MIN_HEDGE_FLOOR, naked_net_gbp=200.0, actual_net_gbp=0.0)
    assert hf == pytest.approx(COMPANY_MIN_HEDGE_FLOOR)


def test_raise_capped_at_1():
    """Cannot raise above 1.0."""
    hf, _ = company_evolve_hedge_fraction(1.0, naked_net_gbp=0.0, actual_net_gbp=500.0)
    assert hf == pytest.approx(1.0)


def test_within_tolerance_holds_position():
    """Difference within COMPANY_MARGIN_TOLERANCE_GBP → hold unchanged."""
    small_diff = COMPANY_MARGIN_TOLERANCE_GBP / 2
    hf, reason = company_evolve_hedge_fraction(0.90, naked_net_gbp=100.0, actual_net_gbp=100.0 + small_diff)
    assert hf == pytest.approx(0.90)
    assert "hold" in reason


def test_reason_contains_actual_and_naked_figures():
    """Reason string includes both actual and naked figures."""
    _, reason = company_evolve_hedge_fraction(0.85, naked_net_gbp=150.0, actual_net_gbp=200.0)
    assert "150" in reason
    assert "200" in reason


def test_run_phase2b_imports_from_company_layer():
    """run_phase2b's evolve_hedge_fraction is sourced from company.risk, not sim."""
    import inspect
    from simulation import run_phase2b
    fn = run_phase2b.evolve_hedge_fraction
    module = inspect.getmodule(fn).__name__
    assert module.startswith("company.risk"), f"Expected company.risk, got {module}"


import pytest
