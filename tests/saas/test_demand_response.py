"""Tests for saas/demand_response.py -- Phase 52."""

import pytest

from saas.demand_response import (
    BASE_SHIFT_FRACTION,
    EV_BOOST,
    HEAT_PUMP_BOOST,
    OFFPEAK_PERIODS,
    PEAK_PERIODS,
    apply_demand_shift,
    compute_shift_fraction,
    make_shifted_shape_fn,
)


def _flat_profile(value: float = 1.0) -> list[float]:
    return [value] * 48


def test_base_shift_fraction_no_assets():
    assert compute_shift_fraction() == pytest.approx(BASE_SHIFT_FRACTION)


def test_shift_fraction_ev_adds_ev_boost():
    result = compute_shift_fraction({"ev": True})
    assert result == pytest.approx(BASE_SHIFT_FRACTION + EV_BOOST)


def test_shift_fraction_heat_pump_adds_boost():
    result = compute_shift_fraction({"heat_pump": True})
    assert result == pytest.approx(BASE_SHIFT_FRACTION + HEAT_PUMP_BOOST)


def test_shift_fraction_both_adds_both():
    result = compute_shift_fraction({"ev": True, "heat_pump": True})
    assert result == pytest.approx(BASE_SHIFT_FRACTION + EV_BOOST + HEAT_PUMP_BOOST)


def test_shift_fraction_none_assets_dict_is_base():
    result = compute_shift_fraction({})
    assert result == pytest.approx(BASE_SHIFT_FRACTION)


def test_shift_fraction_capped_at_one():
    # Even with both boosts, must not exceed 1.0
    result = compute_shift_fraction({"ev": True, "heat_pump": True})
    assert result <= 1.0


def test_peak_periods_contains_sp32_to_38():
    assert frozenset(range(32, 39)).issubset(PEAK_PERIODS)


def test_offpeak_periods_contains_sp1_to_14():
    assert frozenset(range(1, 15)).issubset(OFFPEAK_PERIODS)


def test_apply_demand_shift_conserves_total():
    profile = _flat_profile(2.0)
    shifted, _ = apply_demand_shift(profile, 0.15)
    assert sum(shifted) == pytest.approx(sum(profile), rel=1e-9)


def test_apply_demand_shift_reduces_peak():
    profile = _flat_profile(1.0)
    from saas.demand_response import _PEAK_INDICES
    shifted, _ = apply_demand_shift(profile, 0.15)
    assert all(shifted[i] < 1.0 for i in _PEAK_INDICES)


def test_apply_demand_shift_increases_offpeak():
    profile = _flat_profile(1.0)
    from saas.demand_response import _OFFPEAK_INDICES
    shifted, _ = apply_demand_shift(profile, 0.15)
    assert all(shifted[i] > 1.0 for i in _OFFPEAK_INDICES)


def test_apply_demand_shift_zero_fraction_unchanged():
    profile = list(range(48))
    shifted, moved = apply_demand_shift(profile, 0.0)
    assert shifted == profile
    assert moved == 0.0


def test_apply_demand_shift_wrong_length_unchanged():
    profile = [1.0] * 24
    shifted, moved = apply_demand_shift(profile, 0.15)
    assert shifted == profile
    assert moved == 0.0


def test_apply_demand_shift_returns_shifted_kwh():
    # Flat profile: 48 × 1.0 kWh, peak indices are 7 periods (SP32-38)
    profile = _flat_profile(1.0)
    from saas.demand_response import PEAK_PERIODS
    n_peak = len(PEAK_PERIODS)
    _, moved = apply_demand_shift(profile, BASE_SHIFT_FRACTION)
    expected = n_peak * 1.0 * BASE_SHIFT_FRACTION
    assert moved == pytest.approx(expected, rel=1e-6)


def test_make_shifted_shape_fn_conserves_energy():
    base_fn = lambda date_str: _flat_profile(3.0)
    shifted_fn = make_shifted_shape_fn(base_fn, 0.20)
    result = shifted_fn("2022-01-15")
    assert len(result) == 48
    assert sum(result) == pytest.approx(48 * 3.0, rel=1e-9)
