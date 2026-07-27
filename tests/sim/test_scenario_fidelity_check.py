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


def _ar1_skewed(n, sd, phi, seed, direction):
    """A heavy-tailed AR(1) with a ONE-SIDED spike tail: direction=+1 gives up-spikes
    (right-skewed, like real UK energy scarcity), direction=-1 gives down-spikes
    (left-skewed, like a negative-price-dominated crash regime). Same magnitude tail
    either way -- only the SIDE differs -- so tail_ratio cannot tell them apart."""
    rng = np.random.default_rng(seed)
    t = rng.standard_t(df=3, size=n)
    t = np.abs(t) * direction * 0.7 + rng.normal(0, 1, size=n) * 0.3  # asymmetric heavy tail
    t = t / np.std(t)
    x = np.zeros(n)
    innov_sd = np.sqrt(1 - phi**2)
    for i in range(1, n):
        x[i] = phi * x[i - 1] + t[i] * innov_sd
    return x / np.std(x, ddof=1) * sd


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


def test_wrong_tail_direction_generator_fires():
    """R15 (2026-07-27 HARDEN red-team): a generator that matches mean, volatility,
    lag-1 persistence AND spike-tail MAGNITUDE (tail_ratio) but puts its heavy tail on
    the WRONG SIDE -- down-spikes (negative-price-dominated) where the reference spikes
    UP (scarcity) -- must FAIL on tail_skew. Before tail_skew was added this mirror-
    imaged generator PASSED every check, because tail_ratio takes |deviation| and is
    blind to direction. Direction is the risk-relevant axis: this atom's two named
    stress features point opposite ways, so inverting them mis-states the risk."""
    ref = _ar1_skewed(4000, sd=1.0, phi=0.6, seed=1, direction=+1)   # right-skewed (up spikes)
    gen = _ar1_skewed(2000, sd=1.0, phi=0.6, seed=2, direction=-1)   # left-skewed (down spikes)
    # match mean AND std to the reference by construction so ONLY the tail SIDE can differ
    gen = (gen - gen.mean()) / np.std(gen, ddof=1) * np.std(ref, ddof=1) + ref.mean()
    v = F.check_scenario_fidelity(gen, ref, n_boot=500, seed=7)
    assert not v.passed, v.diverging()
    assert "tail_skew" in v.diverging()
    # the blind-spot proof: mean, std AND tail_ratio all AGREE by construction (same
    # magnitude tail) -- only the directional moment catches the inverted tail
    assert "mean" not in v.diverging()
    assert "std" not in v.diverging()
    assert "tail_ratio" not in v.diverging()


def test_matching_skew_direction_generator_passes():
    """The directional moment must not false-fire: a generator drawn from the SAME
    one-sided-tail process as the reference agrees on tail_skew too -> passes."""
    ref = _ar1_skewed(4000, sd=1.0, phi=0.6, seed=1, direction=+1)
    gen = _ar1_skewed(2000, sd=1.0, phi=0.6, seed=5, direction=+1)
    v = F.check_scenario_fidelity(gen, ref, n_boot=500, seed=7)
    assert v.passed, v.diverging()


def _regime_switch(n, seed, p_stay=0.92, sd_lo=0.5, sd_hi=2.6):
    """A volatility-CLUSTERED series: a two-state (low-vol / high-vol) Markov chain with
    persistence `p_stay`, drawing N(0, sd_state) each step. High-vol runs persist, so big
    moves cluster into multi-day spells -- the ARCH signature of real UK energy stress
    (Dunkelflaute / gas-crisis regimes). The MARGINAL (a stable two-Gaussian mixture) is
    seed-stable, so a random shuffle of one draw agrees on mean/std/tail with another draw
    while destroying the clustering -- exactly the blind spot the vol_clustering moment locks."""
    rng = np.random.default_rng(seed)
    sds = (sd_lo, sd_hi)
    state = 0
    x = np.zeros(n)
    for t in range(n):
        if rng.random() > p_stay:
            state = 1 - state
        x[t] = rng.normal(0.0, sds[state])
    return x - x.mean()


def test_isolated_spike_generator_fires():
    """R15 (2026-07-27 HARDEN red-team): a generator matching the entire return MARGINAL
    (mean, std, tail_ratio, tail_skew) AND the level lag-1 autocorrelation but emitting its
    spikes ISOLATED instead of in multi-day SPELLS must FAIL on vol_clustering. The four
    marginal moments are functions of the return distribution alone and blind to temporal
    ORDER; a random shuffle of a clustered series is the extreme case -- identical marginal,
    zero clustering. Sustained consecutive-settlement stress (not a one-day spike a hedge
    rides out) is what broke the under-hedged 2021 UK suppliers, so this ordering matters."""
    ref = _regime_switch(4000, seed=1)
    gen = np.random.default_rng(9).permutation(_regime_switch(2000, seed=2))  # shuffle kills clustering
    # match mean AND std to the reference by construction so ONLY the temporal ordering differs
    gen = (gen - gen.mean()) / np.std(gen, ddof=1) * np.std(ref, ddof=1) + ref.mean()
    v = F.check_scenario_fidelity(gen, ref, n_boot=500, seed=7)
    assert not v.passed, v.diverging()
    assert "vol_clustering" in v.diverging()
    # the blind-spot proof: the whole marginal AGREES by construction (shuffle preserves it)
    # -- only the clustering moment catches the isolated-spike generator; before it was added
    # nothing did, because every other moment is a function of the marginal alone
    assert "mean" not in v.diverging()
    assert "std" not in v.diverging()
    assert "tail_ratio" not in v.diverging()
    assert "tail_skew" not in v.diverging()


def test_matching_clustered_generator_passes():
    """The clustering moment must not false-fire: a generator drawn from the SAME
    regime-switching (volatility-clustered) process as the reference agrees on
    vol_clustering too -> passes every moment."""
    ref = _regime_switch(4000, seed=1)
    gen = _regime_switch(2000, seed=2)
    gen = (gen - gen.mean()) / np.std(gen, ddof=1) * np.std(ref, ddof=1) + ref.mean()
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


def test_contaminated_generator_raises_not_silently_filtered():
    """R15 (2026-07-28 HARDEN red-team): a generator emitting a MATERIAL fraction of
    non-finite values (an overflow/blow-up: 40% inf/NaN) is a MALFORMED series. Before
    the fix, `_clean` SILENTLY FILTERED the non-finite values and the check PASSED on
    the surviving finite minority -- the classic NaN-blind fail-open. It must now raise
    loud (fail-open), never return a passing verdict, on that gross a defect."""
    rng = np.random.default_rng(1)
    ref = _ar1(3000, 0.0, 10.0, 0.5, 7)
    good = rng.normal(0, 10, 1800)
    bad = np.concatenate([np.full(600, np.inf), np.full(600, np.nan)])
    gen = rng.permutation(np.concatenate([good, bad]))  # 40% non-finite
    with pytest.raises(F.DegenerateSeriesError):
        F.check_scenario_fidelity(gen, ref)


def test_contaminated_reference_raises():
    """R15: the same malformed-series guard applies to the REFERENCE side."""
    rng = np.random.default_rng(2)
    gen = _ar1(3000, 0.0, 10.0, 0.5, 8)
    ref = rng.permutation(np.concatenate([rng.normal(0, 10, 1800), np.full(1200, np.nan)]))
    with pytest.raises(F.DegenerateSeriesError):
        F.check_scenario_fidelity(gen, ref)


def test_incidental_nonfinite_gap_still_tolerated():
    """The OTHER direction (a control that cannot pass legitimate input is useless): an
    INCIDENTAL stray gap (<= 1% non-finite) is still silently filtered, not raised --
    the live real fixture and baseline generator are 100% finite, and a rare gap must
    not false-fire this non-blocking diagnostic."""
    ref = _ar1(3000, 0.0, 10.0, 0.5, 3)
    gen = _ar1(3000, 0.0, 10.0, 0.5, 4).copy()
    gen[17] = np.nan  # one stray value, 0.03% -- well under the 1% tolerance
    v = F.check_scenario_fidelity(gen, ref)  # must not raise
    assert isinstance(v.passed, bool)
