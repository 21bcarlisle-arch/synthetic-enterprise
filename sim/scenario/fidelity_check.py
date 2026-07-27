"""Scenario fidelity-check mode (W1_2 L1->L2, the block-bootstrap sanity baseline).

WHAT. A fidelity SANITY CHECK for the synthetic-futures generator: on the scenario
where the generated distribution is *expected to agree* with real history (the
`baseline_2025`-style preset), the generated return series must not statistically
diverge from real 2016-2025 returns on shared distributional moments (mean,
volatility, lag-1 autocorrelation, spike-tail heaviness -- see `_tail_ratio`,
added 2026-07-24 after a HARDEN red-team found the mean/std/autocorr set PASSES a
Gaussian generator whose spike tail is grossly flat vs a heavy-tailed reference --
and spike-tail DIRECTION -- see `_tail_skew`, added 2026-07-27 after a further
red-team found the |deviation| tail_ratio PASSES a mirror-imaged tail of the same
magnitude sitting on the wrong side).
Design: SYNTHETIC_FUTURES_GENERATION_FRAME.md
S3/S8 -- "reconcile to real distributional moments", using a BLOCK BOOTSTRAP of the
real returns as the *reference*, not as a second generator to maintain.

WHY block bootstrap. Daily energy returns are autocorrelated (regime persistence),
so an i.i.d. resample would give too-tight reference bands and the check would
false-fire. Resampling contiguous BLOCKS (spells) honours that autocorrelation, so
the reference CI on each moment reflects the real effective sample.

R13. This is BASELINE fidelity machinery (calibration-to-reality, blind to company
P&L) -- it may evolve for fidelity reasons without director sign-off. It does NOT
author or alter any curriculum content: it only MEASURES agreement on the baseline
scenario. The named difficulty presets stay director-authored.

R12. The verdict is a DIAGNOSTIC. It is never tuned to pass; a divergence is a
finding (drives R4 -- diagnose the generator), never a cue to move the tolerance.

R15. This is a CONTROL and must FIRE on its named defect: a generator whose mean or
volatility is clearly wrong must FAIL the check; a generator statistically matching
the reference must PASS. FAIL-OPEN: empty/constant/too-short input raises loud
rather than returning a passing verdict.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Sequence, Tuple

import numpy as np


class DegenerateSeriesError(ValueError):
    """FAIL-OPEN: an empty/constant/too-short series has no defensible moment CI --
    raised loud rather than returning a passing-looking verdict."""


def _clean(series: Sequence[float], *, min_len: int) -> np.ndarray:
    v = np.asarray(series, dtype=float)
    v = v[np.isfinite(v)]
    if v.size < min_len:
        raise DegenerateSeriesError(f"need >= {min_len} finite observations, got {v.size}")
    if np.all(v == v[0]):
        raise DegenerateSeriesError("constant series has no dispersion -- moments undefined")
    return v


# ── the shared moments (the axes real and generated must agree on) ──────────
def _mean(v: np.ndarray) -> float:
    return float(np.mean(v))


def _std(v: np.ndarray) -> float:
    return float(np.std(v, ddof=1))


def _lag1_autocorr(v: np.ndarray) -> float:
    if v.size < 2:
        raise DegenerateSeriesError("need >= 2 points for lag-1 autocorrelation")
    a, b = v[:-1], v[1:]
    sa, sb = a.std(), b.std()
    if sa == 0 or sb == 0:
        raise DegenerateSeriesError("zero-variance window -- autocorrelation undefined")
    return float(np.corrcoef(a, b)[0, 1])


def _tail_ratio(v: np.ndarray) -> float:
    """Spike heaviness: the 99th percentile of |deviation| expressed in std units --
    "how many sigma does the worst 1% of moves reach". A dimensionless tail moment
    the first two (mean/std) are STRUCTURALLY BLIND to: a generator can match mean,
    volatility AND lag-1 persistence yet flatten the spike/negative-price tail (draw
    Gaussian innovations where real UK energy returns are heavy-tailed) and pass every
    other check. That flattened tail is exactly the risk-relevant feature this atom's
    synthetic futures exist to stress the company with (Dunkelflaute scarcity spikes,
    negative-price days), so a fidelity SANITY check blind to it green-lights the one
    defect that matters most. Robust under the moving-block bootstrap (a high quantile,
    not the 4th moment -- kurtosis CIs are too wide to fire on anything but the extreme)."""
    s = float(np.std(v, ddof=1))
    if s == 0:
        raise DegenerateSeriesError("zero std -- tail ratio undefined")
    return float(np.quantile(np.abs(v - np.mean(v)), 0.99) / s)


def _tail_skew(v: np.ndarray) -> float:
    """Spike DIRECTION: the signed tail asymmetry (99th-pct up-move + 1st-pct down-move)
    in std units. `_tail_ratio` takes the ABSOLUTE deviation, so it is STRUCTURALLY BLIND
    to which side the heavy tail sits on: a generator can match mean, volatility, lag-1
    persistence AND tail_ratio magnitude yet put its extreme mass on the WRONG side
    (mostly negative-price crashes where real UK energy returns spike UPWARD on scarcity,
    or vice versa) and pass every other check -- the 2026-07-24 tail_ratio fix caught a
    flattened tail but a mirror-imaged tail of the same magnitude still slips through.
    Direction is risk-relevant precisely because this atom's two named stress features
    point OPPOSITE ways (Dunkelflaute scarcity = up-spikes, negative-price days = down),
    so a generator that inverts them mis-states the risk while matching every magnitude.
    Dimensionless, sign-carrying: >0 right-skewed (up-spike dominated, like real energy),
    <0 left-skewed, ~0 symmetric. High-quantile based for the same block-bootstrap
    robustness rationale as tail_ratio (not raw 3rd-moment skewness, whose CIs are wide)."""
    s = float(np.std(v, ddof=1))
    if s == 0:
        raise DegenerateSeriesError("zero std -- tail skew undefined")
    dev = v - np.mean(v)
    up = float(np.quantile(dev, 0.99))     # worst 1% up-move (positive)
    down = float(np.quantile(dev, 0.01))   # worst 1% down-move (negative)
    return (up + down) / s                 # cancels to ~0 if the two tails mirror


MOMENTS: Dict[str, Callable[[np.ndarray], float]] = {
    "mean": _mean,
    "std": _std,
    "lag1_autocorr": _lag1_autocorr,
    "tail_ratio": _tail_ratio,
    "tail_skew": _tail_skew,
}


def block_bootstrap_moment_ci(
    reference: Sequence[float],
    moment_fn: Callable[[np.ndarray], float],
    *,
    block_len: int = 20,
    n_boot: int = 500,
    alpha: float = 0.05,
    seed: int = 0,
) -> Tuple[float, float]:
    """A (1-alpha) CI on a moment of `reference`, by MOVING-BLOCK bootstrap
    (resample contiguous spells of length `block_len`, honouring autocorrelation).
    Deterministic given `seed` (C-S2 replay). Returns (lo, hi)."""
    v = _clean(reference, min_len=block_len)
    n = v.size
    rng = np.random.default_rng(seed)
    n_blocks = int(np.ceil(n / block_len))
    max_start = n - block_len
    vals = []
    for _ in range(n_boot):
        starts = rng.integers(0, max_start + 1, size=n_blocks)
        idx = np.concatenate([np.arange(s, s + block_len) for s in starts])[:n]
        try:
            vals.append(moment_fn(v[idx]))
        except DegenerateSeriesError:
            continue
    if not vals:
        raise DegenerateSeriesError("every bootstrap resample was degenerate -- CI undefined")
    return float(np.quantile(vals, alpha / 2.0)), float(np.quantile(vals, 1.0 - alpha / 2.0))


@dataclass(frozen=True)
class MomentCheck:
    moment: str
    generated: float
    ref_ci: Tuple[float, float]        # real reference's block-bootstrap CI for this moment
    gen_ci: Tuple[float, float]        # generated series' own block-bootstrap CI
    within: bool                       # the two CIs OVERLAP -> statistically consistent


@dataclass(frozen=True)
class FidelityVerdict:
    passed: bool                       # generated agrees with real on EVERY shared moment
    checks: Tuple[MomentCheck, ...]
    block_len: int
    alpha: float

    def diverging(self) -> Tuple[str, ...]:
        return tuple(c.moment for c in self.checks if not c.within)


def _overlap(a: Tuple[float, float], b: Tuple[float, float]) -> bool:
    return not (a[1] < b[0] or b[1] < a[0])


def check_scenario_fidelity(
    generated: Sequence[float],
    reference: Sequence[float],
    *,
    block_len: int = 20,
    n_boot: int = 500,
    alpha: float = 0.05,
    seed: int = 0,
) -> FidelityVerdict:
    """On the agree-expected (baseline) scenario, is each shared moment of the
    GENERATED series statistically CONSISTENT with real history? For each moment we
    block-bootstrap BOTH the reference and the generated series and test whether
    their CIs OVERLAP -- so the verdict accounts for the sampling noise on *both*
    sides (two finite autocorrelated samples legitimately differ), and fires only on
    GROSS divergence (a wrong mean/volatility/persistence), which is what a sanity
    check is for (not a 5%-level equality test that false-fires on normal noise).
    `passed` iff every moment is consistent. FAIL-OPEN on degenerate input."""
    _clean(generated, min_len=block_len)  # generated needs enough for its own bootstrap
    checks = []
    all_within = True
    for name, fn in MOMENTS.items():
        ref_ci = block_bootstrap_moment_ci(
            reference, fn, block_len=block_len, n_boot=n_boot, alpha=alpha, seed=seed
        )
        gen_ci = block_bootstrap_moment_ci(
            generated, fn, block_len=block_len, n_boot=n_boot, alpha=alpha, seed=seed + 1
        )
        within = _overlap(ref_ci, gen_ci)
        all_within = all_within and within
        g = fn(_clean(generated, min_len=2))
        checks.append(MomentCheck(moment=name, generated=g, ref_ci=ref_ci, gen_ci=gen_ci, within=within))
    return FidelityVerdict(passed=all_within, checks=tuple(checks), block_len=block_len, alpha=alpha)
