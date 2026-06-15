from sim.hedging_strategy import (
    MIN_HEDGE_FLOOR,
    decide_initial_hedge_fraction,
    evolve_hedge_fraction,
)


def test_initial_hedge_fraction_is_mandate_floor():
    hedge_fraction, reasoning = decide_initial_hedge_fraction()
    assert hedge_fraction == MIN_HEDGE_FLOOR
    assert "0.85" in reasoning or "85%" in reasoning


def test_evolve_never_drops_below_mandate_floor():
    # Hedge underperformed naked by well over tolerance, starting at the floor.
    new_hf, reasoning = evolve_hedge_fraction(MIN_HEDGE_FLOOR, naked_margin_gbp=100.0, actual_margin_gbp=50.0)
    assert new_hf == MIN_HEDGE_FLOOR
    assert "mandate floor" in reasoning


def test_evolve_can_rise_above_mandate_floor():
    # Hedge beat naked by well over tolerance — agent leans further into hedging.
    new_hf, _ = evolve_hedge_fraction(MIN_HEDGE_FLOOR, naked_margin_gbp=50.0, actual_margin_gbp=100.0)
    assert new_hf > MIN_HEDGE_FLOOR


def test_evolve_capped_at_full_hedge():
    new_hf, _ = evolve_hedge_fraction(1.0, naked_margin_gbp=50.0, actual_margin_gbp=100.0)
    assert new_hf == 1.0
