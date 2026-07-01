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


from sim.hedging_strategy import EVOLUTION_STEP, MARGIN_TOLERANCE_GBP


def test_evolution_step_constant():
    assert EVOLUTION_STEP == 0.1


def test_margin_tolerance_constant():
    assert MARGIN_TOLERANCE_GBP == 5.0


def test_min_hedge_floor_is_085():
    assert MIN_HEDGE_FLOOR == 0.85


def test_hold_at_exact_tolerance_boundary_positive():
    new_hf, reasoning = evolve_hedge_fraction(
        MIN_HEDGE_FLOOR, naked_margin_gbp=100.0, actual_margin_gbp=105.0
    )
    assert new_hf == MIN_HEDGE_FLOOR
    assert "noise" in reasoning.lower() or "tolerance" in reasoning.lower()


def test_hold_at_exact_tolerance_boundary_negative():
    new_hf, _ = evolve_hedge_fraction(
        MIN_HEDGE_FLOOR, naked_margin_gbp=100.0, actual_margin_gbp=95.0
    )
    assert new_hf == MIN_HEDGE_FLOOR


def test_raise_from_floor_when_hedge_beats_naked():
    new_hf, _ = evolve_hedge_fraction(
        MIN_HEDGE_FLOOR, naked_margin_gbp=50.0, actual_margin_gbp=100.0
    )
    assert new_hf == MIN_HEDGE_FLOOR + EVOLUTION_STEP


def test_floor_clamp_when_hf_above_floor_and_naked_wins():
    new_hf, _ = evolve_hedge_fraction(
        0.9, naked_margin_gbp=100.0, actual_margin_gbp=50.0
    )
    assert new_hf == MIN_HEDGE_FLOOR


def test_noise_hold_position_unchanged():
    new_hf, reasoning = evolve_hedge_fraction(
        0.9, naked_margin_gbp=100.0, actual_margin_gbp=103.0
    )
    assert new_hf == 0.9
    assert "noise" in reasoning.lower() or "tolerance" in reasoning.lower()


def test_reasoning_contains_mandate_floor_text():
    _, reasoning = evolve_hedge_fraction(
        MIN_HEDGE_FLOOR, naked_margin_gbp=100.0, actual_margin_gbp=50.0
    )
    assert "85%" in reasoning or "0.85" in reasoning or "mandate" in reasoning.lower()
