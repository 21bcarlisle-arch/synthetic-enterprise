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
