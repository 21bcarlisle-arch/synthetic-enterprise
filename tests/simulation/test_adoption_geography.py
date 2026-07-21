"""Tests for W1_10 L1 — national EV/heat-pump adoption S-curves.

Covers: the logistic fit reproduces the calibration anchors; monotonicity (A2)
holds across and beyond the window; the A2 invariant is R15-FAILABLE (fires on an
injected decrement, fail-closed on empty/short input); the fit is fail-closed on
degenerate calibration; and the adoption_field RNG substream is deterministic and
midpoint-only (C-S2).
"""

from __future__ import annotations

import math

import pytest

from simulation import adoption_geography as ag


# ── The fit reproduces the published anchors (calibration fidelity) ─────────────


def test_curves_fit_all_technologies():
    curves = ag.national_curves()
    assert set(curves) == set(ag.TECHNOLOGIES)
    for tech, curve in curves.items():
        assert curve.rate > 0.0  # monotone by construction
        assert 0.0 < curve.ceiling < 1.0
        assert curve.data_regime == "historical"


@pytest.mark.parametrize("tech", ag.TECHNOLOGIES)
def test_fit_tracks_anchors_within_tolerance(tech):
    # A logistic through real S-curve data should sit near each anchor point.
    anchors = ag._ADOPTION_ANCHORS[tech]
    for year, observed in anchors.items():
        fitted = ag.national_adoption_share(tech, year)
        # Order-of-magnitude agreement: within 40% relative of the anchor. The
        # fit is a smooth curve, not an interpolation, so exact match isn't
        # expected — but it must not be wildly off its own calibration.
        assert fitted == pytest.approx(observed, rel=0.4), (
            f"{tech} {year}: fitted {fitted:.4g} vs anchor {observed:.4g}"
        )


@pytest.mark.parametrize("tech", ag.TECHNOLOGIES)
def test_share_within_zero_and_ceiling(tech):
    curve = ag.national_curves()[tech]
    for year in range(2010, 2060):
        s = curve.share(year)
        assert 0.0 <= s <= curve.ceiling + 1e-12


# ── A2: monotone non-decreasing (across AND beyond the calibration window) ──────


@pytest.mark.parametrize("tech", ag.TECHNOLOGIES)
def test_adoption_series_is_monotone(tech):
    series = ag.adoption_series(tech, list(range(2016, 2041)))
    assert ag.is_monotone_nondecreasing(series)


# ── R15: the A2 invariant is FAILABLE (mutation) and FAIL-CLOSED ────────────────


def test_monotonicity_invariant_fires_on_injected_decrement():
    # Take a real monotone series, inject a single decrement — A2 MUST catch it.
    series = ag.adoption_series("ev", list(range(2016, 2030)))
    assert ag.is_monotone_nondecreasing(series)  # control: passes clean
    mutated = list(series)
    mutated[7] = mutated[6] - 0.001  # un-adoption in one year
    assert ag.is_monotone_nondecreasing(mutated) is False


def test_monotonicity_fails_closed_on_empty_and_singleton():
    with pytest.raises(ValueError):
        ag.is_monotone_nondecreasing([])
    with pytest.raises(ValueError):
        ag.is_monotone_nondecreasing([0.5])


def test_monotonicity_tolerance_absorbs_float_noise_only():
    # A sub-tol wobble passes; a real decrement above tol fails.
    assert ag.is_monotone_nondecreasing([0.10, 0.10 - 1e-12, 0.20])
    assert ag.is_monotone_nondecreasing([0.10, 0.10 - 1e-3, 0.20]) is False


# ── The fit is FAIL-CLOSED on degenerate calibration (R15) ──────────────────────


def test_fit_rejects_decreasing_anchors():
    # A decreasing calibration must NOT yield a silently-flat/valid curve.
    with pytest.raises(ValueError):
        ag.fit_logistic({2016: 0.10, 2020: 0.05, 2024: 0.02}, ceiling=0.9, technology="x")


def test_fit_rejects_too_few_anchors():
    with pytest.raises(ValueError):
        ag.fit_logistic({2016: 0.01}, ceiling=0.9, technology="x")


def test_fit_rejects_anchor_at_or_above_ceiling():
    with pytest.raises(ValueError):
        ag.fit_logistic({2016: 0.5, 2020: 0.95}, ceiling=0.9, technology="x")


def test_fit_rejects_bad_ceiling():
    with pytest.raises(ValueError):
        ag.fit_logistic({2016: 0.01, 2020: 0.05}, ceiling=1.5, technology="x")


def test_unknown_technology_raises():
    with pytest.raises(ValueError):
        ag.national_adoption_share("hydrogen_boiler", 2024)


def test_adoption_series_rejects_empty_years():
    with pytest.raises(ValueError):
        ag.adoption_series("ev", [])


# ── C-S2: the adoption_field substream is deterministic and midpoint-only ───────


def test_jitter_is_deterministic_in_base_seed():
    curve = ag.national_curves()["ev"]
    a = ag.jittered_curve(curve, base_seed=12345)
    b = ag.jittered_curve(curve, base_seed=12345)
    assert a.midpoint == b.midpoint  # same seed -> identical draw (replay)


def test_jitter_varies_with_seed_but_only_shifts_midpoint():
    curve = ag.national_curves()["ev"]
    a = ag.jittered_curve(curve, base_seed=1)
    b = ag.jittered_curve(curve, base_seed=2)
    assert a.midpoint != b.midpoint
    # Only the midpoint moves — rate/ceiling (hence monotonicity) are untouched.
    assert a.rate == curve.rate == b.rate
    assert a.ceiling == curve.ceiling == b.ceiling


def test_jittered_curve_stays_monotone():
    curve = ag.national_curves()["heat_pump"]
    jittered = ag.jittered_curve(curve, base_seed=999)
    series = [jittered.share(y) for y in range(2016, 2041)]
    assert ag.is_monotone_nondecreasing(series)


def test_substream_is_stable_across_call_sites():
    # The named substream must be a pure function of (base_seed, name) — the
    # C-S2 cross-process-replay requirement.
    r1 = ag._substream(42).random()
    r2 = ag._substream(42).random()
    assert r1 == r2


def test_jitter_sd_is_reasonable_band():
    # Sanity: the timing jitter is a season-or-two band, not decades — averaged
    # over many seeds the midpoint shift stays small.
    curve = ag.national_curves()["ev"]
    shifts = [ag.jittered_curve(curve, s).midpoint - curve.midpoint for s in range(200)]
    assert abs(sum(shifts) / len(shifts)) < 0.2  # ~zero-mean
    assert max(abs(s) for s in shifts) < 3.0  # no wild outliers


# ════════════════════════════════════════════════════════════════════════════
# L2 — regional adoption field
# ════════════════════════════════════════════════════════════════════════════
#
# Covers: the region_set is well-formed (weights sum to 1); the field builds for
# every technology; A1 aggregation-consistency holds EXACTLY and is R15-FAILABLE
# (fires on an offset multiplier / a swapped weight vector); A2 monotonicity is
# inherited by every region; spatial correlation is real (near regions covary
# more than far ones); the build is deterministic and C-S2-independent of L1; and
# the fail-closed guards fire on unknown technology / region / bad region_set.

import numpy as np


# ── region_set well-formed ──────────────────────────────────────────────────────


def test_gb_region_weights_sum_to_one():
    total = sum(r.household_weight for r in ag._GB_REGIONS)
    assert total == pytest.approx(1.0, abs=1e-9)


def test_gb_region_ids_unique():
    ids = [r.region_id for r in ag._GB_REGIONS]
    assert len(set(ids)) == len(ids) == 14


# ── the field builds for every technology ───────────────────────────────────────


@pytest.mark.parametrize("tech", ag.TECHNOLOGIES)
def test_regional_field_builds(tech):
    fieldObj = ag.build_regional_field(tech, base_seed=7)
    assert fieldObj.technology == tech
    assert set(fieldObj.multipliers) == {r.region_id for r in ag._GB_REGIONS}
    # Every multiplier is strictly positive (floored + projected).
    assert all(m > 0.0 for m in fieldObj.multipliers.values())
    # The multipliers are NOT all identical — the field actually varies in space.
    assert len(set(round(m, 6) for m in fieldObj.multipliers.values())) > 1


def test_regional_fields_returns_all_technologies():
    fields = ag.regional_fields(base_seed=7)
    assert set(fields) == set(ag.TECHNOLOGIES)


# ── A1: aggregation consistency holds EXACTLY ───────────────────────────────────


@pytest.mark.parametrize("tech", ag.TECHNOLOGIES)
def test_a1_aggregation_consistency_holds(tech):
    fieldObj = ag.build_regional_field(tech, base_seed=13)
    years = list(range(2016, 2036))
    for y in years:
        assert ag.aggregation_consistency_error(fieldObj, y) <= ag.A1_TOL
    assert ag.check_aggregation_consistency(fieldObj, years)


def test_a1_weighted_mean_equals_national():
    # The demand-weighted regional aggregate reconstructs the national curve.
    fieldObj = ag.build_regional_field("ev", base_seed=21)
    for y in (2016, 2020, 2025, 2030):
        assert fieldObj.national_from_field(y) == pytest.approx(
            ag.national_adoption_share("ev", y), abs=1e-9
        )


# ── A1 is R15-FAILABLE (mutation tests) ─────────────────────────────────────────


def test_a1_fires_on_offset_multiplier():
    # Mutation: offset ONE region's multiplier by ε ≫ tol → Σ w_r m_r ≠ 1, the
    # check must FIRE (this is the invariant's whole point).
    fieldObj = ag.build_regional_field("heat_pump", base_seed=5)
    broken = dict(fieldObj.multipliers)
    victim = next(iter(broken))
    broken[victim] += 0.5
    mutated = ag.RegionalAdoptionField(
        technology=fieldObj.technology,
        curve=fieldObj.curve,
        regions=fieldObj.regions,
        multipliers=broken,
        weights=fieldObj.weights,
    )
    # At a year where national adoption is non-trivial, the error exceeds tol.
    assert ag.aggregation_consistency_error(mutated, 2024) > ag.A1_TOL
    assert not ag.check_aggregation_consistency(mutated, [2024])


def test_a1_fires_on_swapped_weight_vector():
    # Mutation: swap the weight vector for a uniform one (≠ the true w_r) → the
    # weighted aggregate no longer reconstructs the national curve.
    fieldObj = ag.build_regional_field("ev", base_seed=5)
    n = len(fieldObj.multipliers)
    uniform = {r: 1.0 / n for r in fieldObj.multipliers}
    mutated = ag.RegionalAdoptionField(
        technology=fieldObj.technology,
        curve=fieldObj.curve,
        regions=fieldObj.regions,
        multipliers=fieldObj.multipliers,
        weights=uniform,
    )
    assert ag.aggregation_consistency_error(mutated, 2024) > ag.A1_TOL


# ── A1 check is FAIL-CLOSED ──────────────────────────────────────────────────────


def test_a1_check_raises_on_empty_field():
    empty = ag.RegionalAdoptionField(
        technology="ev", curve=ag.national_curves()["ev"], regions=(), multipliers={}, weights={}
    )
    with pytest.raises(ValueError):
        ag.aggregation_consistency_error(empty, 2024)


def test_a1_check_raises_on_bad_weight_sum():
    fieldObj = ag.build_regional_field("ev", base_seed=5)
    bad = ag.RegionalAdoptionField(
        technology=fieldObj.technology,
        curve=fieldObj.curve,
        regions=fieldObj.regions,
        multipliers=fieldObj.multipliers,
        weights={r: 0.5 for r in fieldObj.multipliers},  # sums to n/2, not 1
    )
    with pytest.raises(ValueError):
        ag.aggregation_consistency_error(bad, 2024)


def test_a1_predicate_raises_on_empty_years():
    fieldObj = ag.build_regional_field("ev", base_seed=5)
    with pytest.raises(ValueError):
        ag.check_aggregation_consistency(fieldObj, [])


# ── A2: monotonicity is inherited by every region ───────────────────────────────


@pytest.mark.parametrize("tech", ag.TECHNOLOGIES)
def test_regional_series_monotone_every_region(tech):
    fieldObj = ag.build_regional_field(tech, base_seed=33)
    years = list(range(2016, 2041))
    for region_id in fieldObj.multipliers:
        series = ag.regional_series(fieldObj, region_id, years)
        assert ag.is_monotone_nondecreasing(series)


# ── the covariate tilt points the right way (heat pumps lead off the gas grid) ──


def test_heat_pump_multiplier_higher_off_gas_grid():
    # North Scotland (off_gas 0.45) should carry a higher heat-pump multiplier
    # than London (off_gas 0.02) once the covariate tilt dominates the modest
    # spatial noise. Average over seeds to isolate the covariate signal.
    diffs = []
    for seed in range(40):
        f = ag.build_regional_field("heat_pump", base_seed=seed)
        diffs.append(f.multipliers["north_scotland"] - f.multipliers["london"])
    assert sum(diffs) / len(diffs) > 0.0


# ── spatial correlation is real: near regions covary more than far ones ─────────


def test_spatial_field_near_covaries_more_than_far():
    # Draw the tilt across many seeds; the correlation between two ADJACENT
    # regions should exceed that between two DISTANT ones.
    near_a, near_b, far = "london", "south_east_england", "north_scotland"
    la, lb, fa = [], [], []
    for seed in range(300):
        f = ag.build_regional_field("ev", base_seed=seed)
        la.append(f.multipliers[near_a])
        lb.append(f.multipliers[near_b])
        fa.append(f.multipliers[far])
    corr_near = float(np.corrcoef(la, lb)[0, 1])
    corr_far = float(np.corrcoef(la, fa)[0, 1])
    assert corr_near > corr_far


# ── C-S2: deterministic and independent of the L1 national stream ───────────────


def test_regional_field_deterministic():
    a = ag.build_regional_field("ev", base_seed=99)
    b = ag.build_regional_field("ev", base_seed=99)
    assert a.multipliers == b.multipliers


def test_regional_field_seed_sensitive():
    a = ag.build_regional_field("ev", base_seed=1)
    b = ag.build_regional_field("ev", base_seed=2)
    assert a.multipliers != b.multipliers


def test_regional_seed_independent_of_national_jitter():
    # The regional spatial draw uses its own :regional:<tech> namespaced seed, so
    # it must differ from the national timing-jitter draw for the same base_seed
    # (independent substreams — the 01:09Z shared-RNG lesson).
    seed = 7
    national_draw = ag._substream(seed).gauss(0.0, 1.0)
    regional_seed = ag._regional_rng_seed(seed, "ev")
    # Different derivation → the two RNG seeds are not the same integer stream.
    assert regional_seed != int.from_bytes(
        __import__("hashlib").sha256(f"{seed}:{ag.ADOPTION_SUBSTREAM}".encode()).digest()[:8],
        "big",
    )
    assert isinstance(national_draw, float)


# ── fail-closed guards (R15) ────────────────────────────────────────────────────


def test_build_raises_on_unknown_technology():
    with pytest.raises(ValueError):
        ag.build_regional_field("hydrogen_boiler", base_seed=1)


def test_share_raises_on_unknown_region():
    fieldObj = ag.build_regional_field("ev", base_seed=1)
    with pytest.raises(ValueError):
        fieldObj.share("atlantis", 2024)


def test_validate_region_set_raises_on_bad_weights():
    bad = (
        ag.Region("a", "A", 51.0, -1.0, 0.4, 0.1, 0.5),
        ag.Region("b", "B", 52.0, -1.0, 0.4, 0.1, 0.5),  # sums to 0.8, not 1
    )
    with pytest.raises(ValueError):
        ag.build_regional_field("ev", base_seed=1, regions=bad)


def test_validate_region_set_raises_on_duplicate_ids():
    dup = (
        ag.Region("a", "A", 51.0, -1.0, 0.5, 0.1, 0.5),
        ag.Region("a", "A2", 52.0, -1.0, 0.5, 0.1, 0.5),
    )
    with pytest.raises(ValueError):
        ag.build_regional_field("ev", base_seed=1, regions=dup)


def test_validate_region_set_raises_on_empty():
    with pytest.raises(ValueError):
        ag.build_regional_field("ev", base_seed=1, regions=())
