"""W1_5 (L2): premise demand off LOCAL weather, reconciled to national.

The load-bearing tests are the R15 mutation controls: the aggregation-consistency
invariant must PASS for the real (demand-weight-reconciling) regional field and
FIRE when a region is perturbed off-manifold or the national reference is wrong.
"""

import pytest

from simulation.demand_model import PERIODS_PER_DAY, build_demand_shape
from simulation.premise_demand import (
    NOISE_BIAS_TOL,
    RECONCILIATION_TOL,
    aggregate_reconciles,
    demand_weighted_aggregate,
    demand_weighted_mean_factor,
    idiosyncratic_factor,
    local_mean_temp_c,
    national_reference_shape,
    noise_is_unbiased,
    premise_demand_shape,
    reconciliation_residual,
    reconcile_to_national,
)

FLAT_BASE = [1.0] * PERIODS_PER_DAY


def gas_property():
    return {
        "heating_system": "gas_boiler",
        "occupancy_pattern": "single",
        "assets": {"ev": False, "solar": False, "smart_meter": True},
    }


# Four regions whose DEMAND-WEIGHTED deviations sum to ~0 (the W1_4 reconciling
# manifold): 0.4*1.0 + 0.3*(-1.0) + 0.2*0.5 + 0.1*(-2.0) = 0.
REGION_WEIGHTS = [0.4, 0.3, 0.2, 0.1]
REGION_DEVIATIONS = [1.0, -1.0, 0.5, -2.0]


def _premise_shapes(national_temp_c, deviations):
    return [
        premise_demand_shape(FLAT_BASE, national_temp_c, dev, "gas", gas_property())
        for dev in deviations
    ]


def _national_ref(national_temp_c):
    return national_reference_shape(
        [FLAT_BASE] * 4,
        national_temp_c,
        REGION_WEIGHTS,
        ["gas"] * 4,
        [gas_property()] * 4,
    )


# --- local weather wiring ---------------------------------------------------

def test_local_temp_is_national_plus_deviation():
    assert local_mean_temp_c(5.0, -2.0) == 3.0


def test_zero_deviation_is_byte_identical_to_national_path():
    """The forward extension must not perturb the shipped L1 path."""
    got = premise_demand_shape(FLAT_BASE, 5.0, 0.0, "gas", gas_property())
    want = build_demand_shape(FLAT_BASE, 5.0, "gas", gas_property())
    assert got == want


def test_colder_region_draws_strictly_more_heating():
    """A premise in a colder-than-national region genuinely consumes more."""
    national_temp = 5.0  # well inside the heating regime
    colder = sum(premise_demand_shape(FLAT_BASE, national_temp, -3.0, "gas", gas_property()))
    at_national = sum(premise_demand_shape(FLAT_BASE, national_temp, 0.0, "gas", gas_property()))
    assert colder > at_national


# --- aggregation-consistency invariant (R15 mutation controls) --------------

def test_reconciles_exactly_when_all_premises_in_one_regime():
    """All local temps below the heating base -> HDD is linear -> the demand-
    weighted aggregate equals national demand exactly (residual ~0)."""
    national_temp = 5.0
    agg = demand_weighted_aggregate(_premise_shapes(national_temp, REGION_DEVIATIONS), REGION_WEIGHTS)
    residual = reconciliation_residual(agg, _national_ref(national_temp))
    assert residual == pytest.approx(0.0, abs=1e-9)
    assert aggregate_reconciles(agg, _national_ref(national_temp))


def test_convexity_residual_is_small_but_nonzero_across_the_kink():
    """National temp near the HDD base with deviations straddling it: aggregating
    the CONVEX per-premise heating response over dispersed weather gives MORE
    demand than the national-average weather would (Jensen) -- a real, small,
    within-tolerance residual (the winter-risk-under-pricing physics)."""
    national_temp = 15.0  # base is 15.5C; deviations push some regions either side
    agg = demand_weighted_aggregate(_premise_shapes(national_temp, REGION_DEVIATIONS), REGION_WEIGHTS)
    residual = reconciliation_residual(agg, _national_ref(national_temp))
    assert 0.0 < residual < RECONCILIATION_TOL
    assert aggregate_reconciles(agg, _national_ref(national_temp))


def test_invariant_FIRES_when_a_region_is_perturbed_off_manifold():
    """R15 mutation: push one region far off the reconciling manifold (uncompensated)
    -> the demand-weighted deviations no longer sum to ~0 -> the aggregate drifts
    from national -> the invariant must FIRE (return False)."""
    national_temp = 5.0
    mutated = list(REGION_DEVIATIONS)
    mutated[0] = 8.0  # region 0 far warmer, nothing compensates it
    agg = demand_weighted_aggregate(_premise_shapes(national_temp, mutated), REGION_WEIGHTS)
    residual = reconciliation_residual(agg, _national_ref(national_temp))
    assert residual > RECONCILIATION_TOL
    assert not aggregate_reconciles(agg, _national_ref(national_temp))


def test_invariant_FIRES_on_a_wrong_national_reference_not_a_tautology():
    """The check compares against an INDEPENDENT national reference, not the premise
    sum. A deliberately-wrong reference must make it fire -- proof the control is a
    real comparison and cannot be satisfied tautologically."""
    national_temp = 5.0
    agg = demand_weighted_aggregate(_premise_shapes(national_temp, REGION_DEVIATIONS), REGION_WEIGHTS)
    good_ref = _national_ref(national_temp)
    wrong_ref = [v * 1.5 for v in good_ref]
    assert aggregate_reconciles(agg, good_ref)  # sanity: real reference passes
    assert not aggregate_reconciles(agg, wrong_ref)  # tautology guard: wrong one fires


# --- fail-open guards (R15: an unavailable/empty check is a FAILED check) ----

def test_empty_aggregate_raises_not_silently_passes():
    with pytest.raises(ValueError):
        demand_weighted_aggregate([], [])


def test_zero_total_weight_raises():
    with pytest.raises(ValueError):
        demand_weighted_aggregate([FLAT_BASE, FLAT_BASE], [0.0, 0.0])


def test_zero_national_reference_raises_not_reconciles():
    with pytest.raises(ValueError):
        reconciliation_residual(FLAT_BASE, [0.0] * PERIODS_PER_DAY)


def test_mismatched_lengths_raise():
    with pytest.raises(ValueError):
        demand_weighted_aggregate([FLAT_BASE, FLAT_BASE], [1.0])


# --- summed+SCALED enforcement ----------------------------------------------

def test_reconcile_to_national_makes_residual_zero_by_construction():
    """The 'summed+scaled' step: after scaling, the demand-weighted aggregate
    matches the national total exactly."""
    national_temp = 15.0  # a case with a real pre-scale residual
    shapes = _premise_shapes(national_temp, REGION_DEVIATIONS)
    national = _national_ref(national_temp)
    scaled, factor = reconcile_to_national(shapes, REGION_WEIGHTS, national)
    scaled_agg = demand_weighted_aggregate(scaled, REGION_WEIGHTS)
    assert sum(scaled_agg) == pytest.approx(sum(national), rel=1e-9)
    assert factor == pytest.approx(sum(national) / sum(demand_weighted_aggregate(shapes, REGION_WEIGHTS)))


def test_reconcile_to_national_scales_every_premise_by_the_same_factor():
    national_temp = 15.0
    shapes = _premise_shapes(national_temp, REGION_DEVIATIONS)
    national = _national_ref(national_temp)
    scaled, factor = reconcile_to_national(shapes, REGION_WEIGHTS, national)
    for original, s in zip(shapes, scaled):
        for a, b in zip(original, s):
            assert b == pytest.approx(a * factor)


# ---------------------------------------------------------------------------
# L2→L3: idiosyncratic per-property noise (C-S2 substream + R15 mutation controls).
# ---------------------------------------------------------------------------
def _book_ids(n):
    return [f"premise-{i:05d}" for i in range(n)]


def test_idiosyncratic_factor_is_deterministic_replay():
    """C-S2: the same premise draws the same factor on replay (idempotent)."""
    a = idiosyncratic_factor("premise-00042", seed=7)
    b = idiosyncratic_factor("premise-00042", seed=7)
    assert a == b


def test_idiosyncratic_factor_differs_across_premises():
    """Two different premises get different draws (not a constant)."""
    factors = {idiosyncratic_factor(pid, seed=1) for pid in _book_ids(50)}
    assert len(factors) > 1


def test_idiosyncratic_factor_is_strictly_positive():
    """A premise cannot meter negative energy — the lognormal is strictly > 0."""
    assert all(idiosyncratic_factor(pid, seed=3) > 0.0 for pid in _book_ids(200))


def test_cv_zero_turns_noise_off_exactly():
    assert idiosyncratic_factor("premise-00001", seed=1, cv=0.0) == 1.0


def test_default_factor_leaves_premise_shape_byte_identical():
    """idiosyncratic_factor default 1.0 keeps the L2 shape byte-identical (zero
    blast radius, same discipline as regional_deviation == 0)."""
    prop = gas_property()
    base = premise_demand_shape(FLAT_BASE, 5.0, -1.0, "electricity", prop)
    with_default = premise_demand_shape(
        FLAT_BASE, 5.0, -1.0, "electricity", prop, idiosyncratic_factor=1.0
    )
    assert with_default == base


def test_noise_scales_the_whole_shape_by_the_factor():
    prop = gas_property()
    base = premise_demand_shape(FLAT_BASE, 5.0, -1.0, "electricity", prop)
    noised = premise_demand_shape(
        FLAT_BASE, 5.0, -1.0, "electricity", prop, idiosyncratic_factor=1.3
    )
    for a, b in zip(base, noised):
        assert b == pytest.approx(a * 1.3)


def test_mean_factor_converges_to_one_over_a_large_book():
    """Mean-1 by construction: the demand-weighted mean factor of a large book is
    ~1.0, so the noised aggregate reconciles to national just as the noise-free one."""
    ids = _book_ids(5000)
    weights = [1.0] * len(ids)
    assert demand_weighted_mean_factor(ids, weights, seed=11) == pytest.approx(1.0, abs=0.01)


def test_noise_is_unbiased_passes_for_a_real_draw():
    ids = _book_ids(5000)
    weights = [1.0] * len(ids)
    assert noise_is_unbiased(ids, weights, seed=11) is True


def test_noise_is_unbiased_FIRES_on_biased_factors():
    """R15 mutation: monkeypatch the factor to a biased (mean != 1) draw and the
    control must FIRE — a bias would silently inflate/deflate national demand."""
    import simulation.premise_demand as pd

    ids = _book_ids(2000)
    weights = [1.0] * len(ids)
    original = pd.idiosyncratic_factor
    try:
        pd.idiosyncratic_factor = lambda pid, *, seed=None, cv=pd._DEFAULT_CV: original(
            pid, seed=seed, cv=cv
        ) * 1.10  # inject a +10% systematic bias
        assert pd.noise_is_unbiased(ids, weights, seed=11) is False
    finally:
        pd.idiosyncratic_factor = original


def test_noise_is_unbiased_raises_on_empty_book_not_fail_open():
    with pytest.raises(ValueError):
        noise_is_unbiased([], [])


def test_noise_bias_tol_is_a_small_positive_band():
    assert 0.0 < NOISE_BIAS_TOL < 0.1
