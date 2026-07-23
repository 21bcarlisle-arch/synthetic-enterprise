"""Tests for the scenario fidelity-check mode (W1_2 L1->L2).

The check is a CONTROL: per R15 it must FIRE when the generator diverges from real
history on a shared moment, and PASS when it matches. These tests build both cases
plus the FAIL-OPEN degeneracies.
"""

from __future__ import annotations

import numpy as np
import pytest

from sim.scenario import fidelity_check as F


def _ar1(n, mean, sd, phi, seed, tdf=None):
    """A stationary AR(1) return series (autocorrelated, like real energy returns).
    `tdf` (Student-t degrees of freedom) makes the innovations HEAVY-TAILED -- a
    spike-prone series like real UK energy returns -- while keeping the target sd."""
    rng = np.random.default_rng(seed)
    x = np.zeros(n)
    innov_sd = sd * np.sqrt(1 - phi**2)
    if tdf is not None:
        innov = rng.standard_t(df=tdf, size=n)
        innov = innov / np.std(innov) * innov_sd  # heavy-tailed, unit-scaled to target sd
    else:
        innov = rng.normal(0, innov_sd, size=n)
    for t in range(1, n):
        x[t] = phi * x[t - 1] + innov[t]
    return x + mean


def test_matching_generator_passes():
    """A generated series drawn from the SAME process as the reference agrees on
    every moment -> passes."""
    ref = _ar1(3000, mean=0.0, sd=1.0, phi=0.6, seed=1)
    gen = _ar1(1500, mean=0.0, sd=1.0, phi=0.6, seed=2)
    v = F.check_scenario_fidelity(gen, ref, n_boot=300, seed=7)
    assert v.passed, v.diverging()


def test_wrong_mean_generator_fires():
    """R15: a generator with a clearly wrong mean must FAIL (the mean moment
    diverges from the reference CI)."""
    ref = _ar1(3000, mean=0.0, sd=1.0, phi=0.6, seed=1)
    gen = _ar1(1500, mean=5.0, sd=1.0, phi=0.6, seed=2)   # mean shifted 5 sigma
    v = F.check_scenario_fidelity(gen, ref, n_boot=300, seed=7)
    assert not v.passed
    assert "mean" in v.diverging()


def test_wrong_volatility_generator_fires():
    """R15: a generator with clearly wrong volatility must FAIL on the std moment."""
    ref = _ar1(3000, mean=0.0, sd=1.0, phi=0.6, seed=1)
    gen = _ar1(1500, mean=0.0, sd=4.0, phi=0.6, seed=2)   # 4x volatility
    v = F.check_scenario_fidelity(gen, ref, n_boot=300, seed=7)
    assert not v.passed
    assert "std" in v.diverging()


def test_wrong_autocorrelation_generator_fires():
    """R15: a memoryless generator against an autocorrelated reference must FAIL on
    the lag-1 autocorrelation moment (persistence is what the block bootstrap is for)."""
    ref = _ar1(3000, mean=0.0, sd=1.0, phi=0.7, seed=1)
    gen = _ar1(1500, mean=0.0, sd=1.0, phi=0.0, seed=2)   # no persistence
    v = F.check_scenario_fidelity(gen, ref, n_boot=300, seed=7)
    assert not v.passed
    assert "lag1_autocorr" in v.diverging()


def test_flat_tail_generator_fires():
    """R15 (2026-07-24 HARDEN red-team): a generator that matches mean, volatility AND
    lag-1 persistence but FLATTENS the spike tail (Gaussian innovations against a
    heavy-tailed reference) must FAIL on the tail_ratio moment. Before tail_ratio was
    added this exact generator PASSED every check -- the blind spot this test locks."""
    ref = _ar1(4000, mean=0.0, sd=1.0, phi=0.6, seed=1, tdf=3)   # heavy-tailed, spike-prone
    gen = _ar1(2000, mean=0.0, sd=1.0, phi=0.6, seed=2)          # Gaussian, flat tail
    # match mean AND std to the reference by construction, so ONLY the tail can differ
    gen = (gen - gen.mean()) / np.std(gen, ddof=1) * np.std(ref, ddof=1) + ref.mean()
    v = F.check_scenario_fidelity(gen, ref, n_boot=500, seed=7)
    assert not v.passed
    assert "tail_ratio" in v.diverging()
    # the blind-spot proof: with mean+std matched by construction, mean/std do NOT fire --
    # only the tail moment catches this generator (before it was added, nothing did)
    assert "mean" not in v.diverging()
    assert "std" not in v.diverging()


def test_matching_heavy_tailed_generator_passes():
    """The tail moment must not false-fire: a generator drawn from the SAME
    heavy-tailed process as the reference agrees on tail_ratio too -> passes."""
    ref = _ar1(4000, mean=0.0, sd=1.0, phi=0.6, seed=1, tdf=3)
    gen = _ar1(2000, mean=0.0, sd=1.0, phi=0.6, seed=5, tdf=3)
    v = F.check_scenario_fidelity(gen, ref, n_boot=500, seed=7)
    assert v.passed, v.diverging()


def test_deterministic_given_seed():
    ref = _ar1(2000, 0.0, 1.0, 0.5, seed=1)
    gen = _ar1(1000, 0.0, 1.0, 0.5, seed=2)
    a = F.check_scenario_fidelity(gen, ref, n_boot=200, seed=11)
    b = F.check_scenario_fidelity(gen, ref, n_boot=200, seed=11)
    assert [c.ref_ci for c in a.checks] == [c.ref_ci for c in b.checks]  # C-S2 replay
    assert [c.gen_ci for c in a.checks] == [c.gen_ci for c in b.checks]


def test_every_moment_reported_with_both_cis():
    ref = _ar1(2000, 0.0, 1.0, 0.5, seed=1)
    gen = _ar1(1000, 0.0, 1.0, 0.5, seed=2)
    v = F.check_scenario_fidelity(gen, ref, n_boot=200, seed=3)
    assert {c.moment for c in v.checks} == set(F.MOMENTS)
    for c in v.checks:
        assert c.ref_ci[0] <= c.ref_ci[1]
        assert c.gen_ci[0] <= c.gen_ci[1]
        assert c.within == F._overlap(c.ref_ci, c.gen_ci)  # within == CI overlap


# ── FAIL-OPEN degeneracies ───────────────────────────────────────────────────
def test_empty_series_raises():
    with pytest.raises(F.DegenerateSeriesError):
        F.check_scenario_fidelity([], _ar1(500, 0, 1, 0.5, 1))


def test_constant_reference_raises():
    with pytest.raises(F.DegenerateSeriesError):
        F.check_scenario_fidelity(_ar1(500, 0, 1, 0.5, 1), [2.0] * 500)


def test_too_short_for_block_raises():
    with pytest.raises(F.DegenerateSeriesError):
        F.block_bootstrap_moment_ci([0.1, 0.2, 0.3], F._mean, block_len=20)
