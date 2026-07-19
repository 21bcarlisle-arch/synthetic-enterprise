"""Tests for the scenario fidelity-check mode (W1_2 L1->L2).

The check is a CONTROL: per R15 it must FIRE when the generator diverges from real
history on a shared moment, and PASS when it matches. These tests build both cases
plus the FAIL-OPEN degeneracies.
"""

from __future__ import annotations

import numpy as np
import pytest

from sim.scenario import fidelity_check as F


def _ar1(n, mean, sd, phi, seed):
    """A stationary AR(1) return series (autocorrelated, like real energy returns)."""
    rng = np.random.default_rng(seed)
    x = np.zeros(n)
    innov_sd = sd * np.sqrt(1 - phi**2)
    for t in range(1, n):
        x[t] = phi * x[t - 1] + rng.normal(0, innov_sd)
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
