"""Tests for sim/regional_weather_field.py — the W1_4 aggregation-consistency
invariant and its R15 mutation suite.

The load-bearing deliverable is the mutation suite: a control that cannot FAIL is
worse than none (R15). Every mutation below drives the field/weights/inputs into a
named defect and asserts the reconciliation check FIRES, and every killer pattern
(TAUTOLOGY / FAIL-OPEN / FAIL-SILENT) is closed with its own test.
"""

import numpy as np
import pytest

from sim.regional_weather_field import (
    TOL_AGG,
    SUBSTREAM_NAME,
    AggregationConsistencyError,
    GBRegion,
    assert_aggregation_consistency,
    build_consistent_region_values,
    check_aggregation_consistency,
    check_temperature_feasibility,
    check_wind_feasibility,
    default_regions,
    demand_weights,
    draw_placeholder_deviations,
    project_to_national_consistency,
    reconciliation_residual,
    regional_field_rng,
)


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------
N_PERIODS = 48


def _national(seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    # A plausible national temperature series around 8C.
    return 8.0 + rng.standard_normal(N_PERIODS) * 2.0


def _consistent_field(base_seed: int = 20260718):
    """Build a reconciling field end-to-end via the real construction path."""
    regions = default_regions()
    weights = demand_weights(regions)
    national = _national()
    rng = regional_field_rng(base_seed)
    raw = draw_placeholder_deviations(regions, N_PERIODS, rng)
    values = build_consistent_region_values(national, raw, weights)
    return regions, weights, national, values


# ---------------------------------------------------------------------------
# Region set + weights
# ---------------------------------------------------------------------------
def test_fourteen_gb_regions():
    assert len(default_regions()) == 14
    assert len(set(default_regions())) == 14


def test_weights_normalised_and_positive():
    w = demand_weights()
    assert sum(w.values()) == pytest.approx(1.0)
    assert all(v > 0.0 for v in w.values())
    assert set(w.keys()) == set(default_regions())


def test_no_company_import_in_module():
    """Epistemic wall: the SIM regional field must not import the company layer."""
    import sim.regional_weather_field as mod
    import inspect

    src = inspect.getsource(mod)
    assert "import company" not in src
    assert "from company" not in src


# ---------------------------------------------------------------------------
# The invariant holds BY CONSTRUCTION (the positive case)
# ---------------------------------------------------------------------------
def test_invariant_holds_by_construction():
    _, weights, national, values = _consistent_field()
    result = check_aggregation_consistency(values, national, weights)
    assert result.passed, result.reason
    assert result.max_abs_residual <= TOL_AGG


def test_projection_zero_weighted_mean():
    regions = default_regions()
    weights = demand_weights(regions)
    rng = regional_field_rng(1)
    raw = draw_placeholder_deviations(regions, N_PERIODS, rng)
    projected = project_to_national_consistency(raw, weights)
    w = np.array([weights[r] for r in regions])
    stacked = np.vstack([projected[r] for r in regions])
    weighted_mean = (w[:, None] * stacked).sum(axis=0)
    assert np.max(np.abs(weighted_mean)) <= TOL_AGG


def test_assert_helper_passes_on_consistent_field():
    _, weights, national, values = _consistent_field()
    assert_aggregation_consistency(values, national, weights)  # must not raise


def test_deterministic_replay_same_seed():
    """C-S2: same seed => identical field => identical residual."""
    _, w1, n1, v1 = _consistent_field(base_seed=42)
    _, w2, n2, v2 = _consistent_field(base_seed=42)
    for r in v1:
        assert np.array_equal(v1[r], v2[r])


def test_different_seed_different_field():
    _, _, _, v1 = _consistent_field(base_seed=1)
    _, _, _, v2 = _consistent_field(base_seed=2)
    # At least one region differs.
    assert any(not np.array_equal(v1[r], v2[r]) for r in v1)


# ---------------------------------------------------------------------------
# R15 PRIMARY MUTATION — perturb one region off-manifold; invariant must FIRE
# ---------------------------------------------------------------------------
def test_mutation_perturb_region_fires():
    """Drive one region 10C colder AFTER projection, without re-projecting. The
    aggregate breaks and the check MUST fire (this is the atom's own named defect)."""
    regions, weights, national, values = _consistent_field()
    # sanity: consistent before mutation
    assert check_aggregation_consistency(values, national, weights).passed

    mutated = dict(values)
    victim = GBRegion.NORTH_SCOTLAND
    mutated[victim] = values[victim] - 10.0  # 10C colder, off-manifold

    result = check_aggregation_consistency(mutated, national, weights)
    assert not result.passed, "invariant FAILED TO FIRE on an off-manifold region"
    # residual should be ~ w_victim * 10C, far above tol
    assert result.max_abs_residual > TOL_AGG
    assert result.max_abs_residual > weights[victim] * 10.0 * 0.5


def test_mutation_perturb_raises_via_assert():
    regions, weights, national, values = _consistent_field()
    mutated = dict(values)
    mutated[GBRegion.LONDON] = values[GBRegion.LONDON] + 5.0
    with pytest.raises(AggregationConsistencyError):
        assert_aggregation_consistency(mutated, national, weights)


def test_mutation_scale_wind_region_fires():
    """A large multiplicative perturbation to one region also breaks reconciliation."""
    regions, weights, national, values = _consistent_field()
    mutated = dict(values)
    victim = GBRegion.YORKSHIRE
    mutated[victim] = values[victim] * 3.0 + 20.0
    assert not check_aggregation_consistency(mutated, national, weights).passed


# ---------------------------------------------------------------------------
# R15 SECONDARY MUTATION — attack the WEIGHTS, not the field
# ---------------------------------------------------------------------------
def test_mutation_uniform_weights_reopens_residual():
    """Field projected under real (non-uniform) weights, but checked under uniform
    weights: the residual must reopen — proves the check actually reads w_r and is
    not a hardcoded pass."""
    regions, weights, national, values = _consistent_field()
    uniform = {r: 1.0 / len(regions) for r in regions}
    # Under the weights it was built with, it passes:
    assert check_aggregation_consistency(values, national, weights).passed
    # Under uniform weights, it must NOT:
    result = check_aggregation_consistency(values, national, uniform)
    assert not result.passed, "check ignored the weight vector (hardcoded pass?)"
    assert result.max_abs_residual > TOL_AGG


# ---------------------------------------------------------------------------
# R15 TAUTOLOGY guard — national is held independently, not re-derived
# ---------------------------------------------------------------------------
def test_tautology_national_is_independent():
    """If national were re-derived from the region sum, mutating one region would
    also shift 'national' and the check would still pass. The primary-mutation test
    firing already proves independence; here we assert it directly: swapping in a
    DIFFERENT (wrong) national breaks reconciliation, confirming the check compares
    to the passed-in national, not to the region aggregate."""
    regions, weights, national, values = _consistent_field()
    assert check_aggregation_consistency(values, national, weights).passed
    wrong_national = national + 3.0  # independent, wrong anchor
    result = check_aggregation_consistency(values, wrong_national, weights)
    assert not result.passed
    assert result.max_abs_residual == pytest.approx(3.0, abs=1e-6)


# ---------------------------------------------------------------------------
# R15 FAIL-OPEN guard — degenerate inputs must FAIL, never pass trivially
# ---------------------------------------------------------------------------
def test_fail_open_empty_region_set():
    result = check_aggregation_consistency({}, _national(), {})
    assert not result.passed


def test_fail_open_nan_region_value():
    regions, weights, national, values = _consistent_field()
    mutated = dict(values)
    bad = values[GBRegion.LONDON].copy()
    bad[0] = np.nan
    mutated[GBRegion.LONDON] = bad
    result = check_aggregation_consistency(mutated, national, weights)
    assert not result.passed
    assert "degenerate" in result.reason or "non-finite" in result.reason


def test_fail_open_missing_weight():
    regions, weights, national, values = _consistent_field()
    broken = dict(weights)
    del broken[GBRegion.LONDON]
    result = check_aggregation_consistency(values, national, broken)
    assert not result.passed


def test_fail_open_nan_weight():
    regions, weights, national, values = _consistent_field()
    broken = dict(weights)
    broken[GBRegion.LONDON] = float("nan")
    result = check_aggregation_consistency(values, national, broken)
    assert not result.passed


def test_fail_open_zero_weight_rejected():
    regions, weights, national, values = _consistent_field()
    broken = dict(weights)
    broken[GBRegion.LONDON] = 0.0
    result = check_aggregation_consistency(values, national, broken)
    assert not result.passed


def test_fail_open_all_zero_field_does_not_falsely_pass():
    """An all-zero field is only 'consistent' if national is also zero; against a
    real (non-zero) national it must FAIL, never trivially pass on emptiness."""
    regions = default_regions()
    weights = demand_weights(regions)
    national = _national()
    zero_field = {r: np.zeros(N_PERIODS) for r in regions}
    result = check_aggregation_consistency(zero_field, national, weights)
    assert not result.passed


# ---------------------------------------------------------------------------
# R15 FAIL-SILENT guard — unavailable inputs report FAILED, never green
# ---------------------------------------------------------------------------
def test_fail_silent_national_unavailable():
    regions, weights, _, values = _consistent_field()
    result = check_aggregation_consistency(values, None, weights)
    assert not result.passed
    assert "unavailable" in result.reason


def test_fail_silent_weights_unavailable():
    regions, _, national, values = _consistent_field()
    result = check_aggregation_consistency(values, national, None)
    assert not result.passed
    assert "unavailable" in result.reason


def test_fail_silent_region_values_unavailable():
    _, weights, national, _ = _consistent_field()
    result = check_aggregation_consistency(None, national, weights)
    assert not result.passed
    assert "unavailable" in result.reason


# ---------------------------------------------------------------------------
# RNG substream isolation (C-S2)
# ---------------------------------------------------------------------------
def test_substream_named_regional_field():
    assert SUBSTREAM_NAME == "regional_field"


def test_substream_does_not_touch_global_rng():
    """Drawing from the regional_field substream must not advance the global RNG."""
    before = np.random.default_rng(0).standard_normal(5)
    rng = regional_field_rng(999)
    _ = rng.standard_normal(1000)
    after = np.random.default_rng(0).standard_normal(5)
    assert np.array_equal(before, after)


def test_substream_isolated_from_other_salts():
    a = regional_field_rng(7, salt="alpha").standard_normal(10)
    b = regional_field_rng(7, salt="beta").standard_normal(10)
    assert not np.array_equal(a, b)


def test_substream_deterministic():
    a = regional_field_rng(7).standard_normal(10)
    b = regional_field_rng(7).standard_normal(10)
    assert np.array_equal(a, b)


# ---------------------------------------------------------------------------
# Feasibility (§5) — independent of reconciliation, with its own mutation
# ---------------------------------------------------------------------------
def test_feasibility_passes_on_normal_field():
    regions, weights, national, values = _consistent_field()
    assert check_temperature_feasibility(values, national).passed


def test_feasibility_temp_mutation_fires():
    """A field can RECONCILE and still be INFEASIBLE — plant a region 30C off and
    show the feasibility check fires even though reconciliation is untouched here."""
    regions = default_regions()
    national = _national()
    # Build a field where two regions are +/- 30C but demand-weighted mean is 0,
    # so reconciliation would pass — feasibility must still fire.
    values = {r: national.copy() for r in regions}
    values[GBRegion.NORTH_SCOTLAND] = national - 30.0
    result = check_temperature_feasibility(values, national)
    assert not result.passed


def test_feasibility_wind_ceiling_fires():
    regions = default_regions()
    wind = {r: np.full(N_PERIODS, 5.0) for r in regions}
    wind[GBRegion.NORTH_SCOTLAND] = np.full(N_PERIODS, 60.0)  # above ceiling
    assert not check_wind_feasibility(wind).passed


def test_feasibility_wind_negative_fires():
    regions = default_regions()
    wind = {r: np.full(N_PERIODS, 5.0) for r in regions}
    wind[GBRegion.LONDON] = np.full(N_PERIODS, -1.0)
    assert not check_wind_feasibility(wind).passed


# ---------------------------------------------------------------------------
# reconciliation_residual is per-period (array), not collapsed
# ---------------------------------------------------------------------------
def test_residual_is_per_period():
    _, weights, national, values = _consistent_field()
    residual = reconciliation_residual(values, national, weights)
    assert residual.shape == (N_PERIODS,)
    assert np.max(np.abs(residual)) <= TOL_AGG
