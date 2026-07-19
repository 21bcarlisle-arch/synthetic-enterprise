"""Tests for the cascade correlation estimation method (Epoch-2 atom D).

The portable statistic `L(u)` is a CONTROL spine: per R15 the killer mutation for
ANY link is to CUT its coupling (draw the series independently) -> L collapses to
the independence null 1.0 -> `assert_coupling_present` MUST fire. These tests
construct that exact mutation and the degeneracy/unavailability defects the
FAIL-OPEN / FAIL-SILENT / TAUTOLOGY guards exist to catch.
"""

from __future__ import annotations

import numpy as np
import pytest

from background import cascade_correlation_estimation as D


def _tail_coupled_pair(n=4000, rho_tail=0.85, seed=1):
    """A pair with genuine UPPER-tail dependence: a shared latent factor drives
    both, so extremes co-occur far more than independence predicts."""
    rng = np.random.default_rng(seed)
    z = rng.normal(size=n)              # common factor
    a = rho_tail * z + np.sqrt(1 - rho_tail**2) * rng.normal(size=n)
    b = rho_tail * z + np.sqrt(1 - rho_tail**2) * rng.normal(size=n)
    return a, b


def _independent_pair(n=4000, seed=2):
    rng = np.random.default_rng(seed)
    return rng.normal(size=n), rng.normal(size=n)


# ── the portable spine: L=1 at independence, L>1 in a coupled tail ──────────
def test_independent_series_lift_near_one():
    """Independent extremes -> lift near the null 1.0 (within finite-decile
    sampling noise) and the coupling control does NOT fire. The quintile has more
    power (~2x the tail count) so it sits closer to 1 than the noisier decile."""
    a, b = _independent_pair(n=20000)
    est = D.joint_tail_lift(a, b, D.QUINTILE_U)
    assert not est.coupled                      # the control must not fire on independence
    assert abs(est.lift - D.INDEPENDENCE_NULL) < 0.2


def test_tail_coupled_series_lift_above_one():
    a, b = _tail_coupled_pair()
    est = D.joint_tail_lift(a, b, D.DECILE_U)
    assert est.lift > 1.0 + D._COUPLING_COLLAPSE_BAND
    assert est.coupled
    # reported WITH its u, and lambda ~ L*(1-u)
    assert est.u == D.DECILE_U
    assert est.lam == pytest.approx(est.lift * (1 - D.DECILE_U))


# ── THE killer mutation (S4 R15): cut the coupling -> L->1 -> control fires ──
def test_cut_coupling_collapses_lift_and_control_fires():
    a, b = _tail_coupled_pair()
    intact = D.assert_coupling_present(a, b)
    assert intact.present, "a genuinely coupled link must read present"

    b_cut = D.cut_coupling(b, seed=7)          # identical marginal, destroyed joint structure
    cut = D.assert_coupling_present(a, b_cut)
    assert not cut.present, "a CUT coupling must FIRE the control (L collapsed to independence)"
    assert cut.lift < intact.lift               # the joint tail thinned toward independence
    assert cut.lift < 1.0 + D._COUPLING_COLLAPSE_BAND


def test_cut_coupling_preserves_the_marginal():
    _, b = _tail_coupled_pair()
    b_cut = D.cut_coupling(b, seed=3)
    assert np.allclose(np.sort(b), np.sort(b_cut))  # same values, only order (joint structure) changed


# ── FAIL-OPEN: degenerate input fails loud, never a passing 1.0/0.0 ─────────
def test_empty_series_raises():
    with pytest.raises(D.DegenerateSeriesError):
        D.joint_tail_lift([], [])


def test_constant_series_raises():
    with pytest.raises(D.DegenerateSeriesError):
        D.joint_tail_lift([3.0] * 100, np.random.default_rng(0).normal(size=100))


def test_length_mismatch_raises():
    with pytest.raises(D.DegenerateSeriesError):
        D.joint_tail_lift([1.0, 2.0, 3.0], [1.0, 2.0])


# ── FAIL-SILENT: an unavailable series is a FAILED check, never present=True ─
def test_unavailable_series_is_a_failed_check():
    a, _ = _tail_coupled_pair()
    with pytest.raises(D.SeriesUnavailableError):
        D.assert_coupling_present(a, None)


# ── the anti-pooling step (S3.1) ────────────────────────────────────────────
def test_condition_restricts_to_the_regime():
    series = np.arange(10.0)
    mask = np.array([True, False] * 5)
    out = D.condition(series, mask)
    assert list(out) == [0.0, 2.0, 4.0, 6.0, 8.0]


def test_pooling_can_flip_the_sign_conditioning_recovers_it():
    """The D1 lesson made concrete: a coupling that lives only in winter is
    diluted/flipped when pooled across all seasons; conditioning first recovers
    it. Here summer is anti-coupled noise, winter is tail-coupled; pooled lift is
    muddied, the winter-conditioned lift is clearly > 1."""
    aw, bw = _tail_coupled_pair(n=1000, seed=11)          # winter: coupled
    rng = np.random.default_rng(12)
    asu, bsu = rng.normal(size=3000), rng.normal(size=3000)  # summer: independent, dominates by count
    a = np.concatenate([aw, asu]); b = np.concatenate([bw, bsu])
    is_winter = np.concatenate([np.ones(1000, bool), np.zeros(3000, bool)])
    pooled = D.joint_tail_lift(a, b).lift
    winter = D.joint_tail_lift(D.condition(a, is_winter), D.condition(b, is_winter)).lift
    assert winter > pooled  # conditioning surfaces the coupling the pool hides


# ── block bootstrap CI: deterministic, brackets the point estimate ──────────
def test_block_bootstrap_ci_deterministic_and_brackets():
    a, b = _tail_coupled_pair(n=1500, seed=5)
    lo1, hi1 = D.block_bootstrap_lift_ci(a, b, block_len=5, n_boot=200, seed=42)
    lo2, hi2 = D.block_bootstrap_lift_ci(a, b, block_len=5, n_boot=200, seed=42)
    assert (lo1, hi1) == (lo2, hi2)          # C-S2 deterministic replay
    assert lo1 <= hi1
    point = D.joint_tail_lift(a, b).lift
    assert lo1 <= point <= hi1 + 1e-6        # CI brackets the point estimate


# ── compounding inequality (S4, D6) ─────────────────────────────────────────
def test_compounding_holds_when_end_amplifies():
    assert D.compounding_holds(3.0, [1.5, 1.8])          # 3.0 >= 2.7
    assert not D.compounding_holds(2.0, [1.5, 1.8])      # 2.0 <  2.7 -> a finding


def test_compounding_no_links_raises():
    with pytest.raises(D.DegenerateSeriesError):
        D.compounding_holds(2.0, [])


# ── R10 honesty: an asserted dependence must state reason AND grounding ─────
def test_asserted_dependence_requires_reason_and_grounding():
    rec = D.asserted_dependence(
        "D7", assumed_lift=0.4, assumed_sign="anti",
        reason="interconnector flow series unavailable this session",
        grounding="ENTSO-E cross-border flow vs GB residual demand, joint-tail L at u=0.1",
    )
    assert rec.link_id == "D7" and rec.assumed_sign == "anti"
    with pytest.raises(ValueError):
        D.asserted_dependence("D7", assumed_lift=0.4, assumed_sign="anti", reason="", grounding="x")
    with pytest.raises(ValueError):
        D.asserted_dependence("D7", assumed_lift=0.4, assumed_sign="bad", reason="r", grounding="g")


# ── the L(u) curve ──────────────────────────────────────────────────────────
def test_lift_curve_rises_into_the_tail_for_coupled_series():
    a, b = _tail_coupled_pair()
    curve = dict(D.lift_curve(a, b, us=(0.30, 0.10, 0.05)))
    # asymptotic dependence: the corner fattens (lift rises) as u shrinks into the tail
    assert curve[0.05] >= curve[0.30]
