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
magnitude sitting on the wrong side -- and volatility CLUSTERING -- see
`_vol_clustering`, added 2026-07-27 after a red-team found all four preceding
moments are TEMPORAL-marginal blind: a generator matching the entire return
MARGINAL (mean/std/tail_ratio/tail_skew) plus the return-LEVEL lag-1 autocorr yet
emitting its spikes ISOLATED instead of in multi-day spells passes every check).
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
the reference must PASS. FAIL-OPEN: empty/constant/too-short input -- OR a series with
a material fraction of non-finite values (a generator blow-up: inf/NaN, added 2026-07-28
after a HARDEN red-team found `_clean` SILENTLY FILTERED non-finite values, so a
generator emitting 40% inf/NaN passed the check on its surviving finite minority) --
raises loud rather than returning a passing verdict. Also (added 2026-07-28, a further
HARDEN red-team) a NON-FINITE MOMENT CI: np.corrcoef returns nan on a tiny-but-nonzero
variance resample the exact-`std == 0` guards miss, and `_overlap` is NaN-blind, so a
single such resample silently marked a moment consistent it never computed -- the
bootstrap now drops non-finite moments at the ingress and check_scenario_fidelity
rejects any non-finite CI loud rather than letting the NaN-blind overlap fail-open.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Sequence, Tuple

import numpy as np


class DegenerateSeriesError(ValueError):
    """FAIL-OPEN: an empty/constant/too-short series has no defensible moment CI --
    raised loud rather than returning a passing-looking verdict."""


def _clean(series: Sequence[float], *, min_len: int, max_nonfinite_frac: float = 0.01) -> np.ndarray:
    v = np.asarray(series, dtype=float)
    n_raw = v.size
    finite = np.isfinite(v)
    n_nonfinite = int((~finite).sum())
    # FAIL-OPEN loud (R15, the recurring "reject non-finite FIRST" class): a MATERIAL
    # fraction of non-finite values is a MALFORMED series (a generator overflow/blow-up),
    # not an incidental gap to silently drop. Filtering them away silently lets a grossly
    # defective generator -- e.g. one emitting 40% inf/NaN -- PASS the fidelity sanity
    # check on the surviving finite minority, the exact catastrophic-generator defect this
    # check exists to catch. An incidental stray gap (<= max_nonfinite_frac) is still
    # tolerated (the live real fixture and baseline generator are 100% finite).
    if n_raw > 0 and n_nonfinite > max_nonfinite_frac * n_raw:
        raise DegenerateSeriesError(
            f"{n_nonfinite}/{n_raw} values non-finite (> {max_nonfinite_frac:.0%}) -- "
            "malformed series (generator blow-up), not an incidental gap to silently drop"
        )
    v = v[finite]
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


def _vol_clustering(v: np.ndarray) -> float:
    """Volatility CLUSTERING: the lag-1 autocorrelation of ABSOLUTE deviation from the
    mean -- the ARCH signature ("do big moves follow big moves"). `_lag1_autocorr`
    measures persistence of the SIGNED level; the four preceding moments (mean, std,
    tail_ratio, tail_skew) are functions of the return MARGINAL alone and are all blind
    to how the spikes are ORDERED IN TIME. So a generator can match the entire marginal
    AND the level autocorrelation yet emit its heavy-tailed spikes ISOLATED (i.i.d.
    innovations -- a random shuffle of a real series is the extreme case: identical
    marginal, zero clustering) rather than in the multi-day SPELLS real UK energy stress
    actually arrives in (a Dunkelflaute cold-still regime, a gas-crisis run-up -- both
    persist for days, not one settlement). That temporal difference is risk-relevant
    precisely because sustained consecutive-settlement stress, not an isolated one-day
    spike a hedge rides out, is what broke the under-hedged 2021 UK suppliers -- so a
    fidelity check blind to clustering green-lights a generator that understates exactly
    the sustained-tail exposure this atom's synthetic futures exist to stress. Lag-1
    autocorr of |deviation| is the standard clustering statistic and, like the other
    moments, is stable under the moving-block bootstrap."""
    if v.size < 2:
        raise DegenerateSeriesError("need >= 2 points for volatility-clustering autocorrelation")
    a = np.abs(v - np.mean(v))
    x, y = a[:-1], a[1:]
    sx, sy = x.std(), y.std()
    if sx == 0 or sy == 0:
        raise DegenerateSeriesError("constant |deviation| window -- clustering autocorrelation undefined")
    return float(np.corrcoef(x, y)[0, 1])


MOMENTS: Dict[str, Callable[[np.ndarray], float]] = {
    "mean": _mean,
    "std": _std,
    "lag1_autocorr": _lag1_autocorr,
    "tail_ratio": _tail_ratio,
    "tail_skew": _tail_skew,
    "vol_clustering": _vol_clustering,
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
            m = moment_fn(v[idx])
        except DegenerateSeriesError:
            continue
        # FAIL-OPEN loud (R15, the recurring "reject non-finite FIRST" comparison class):
        # a moment can return non-finite on a NUMERICALLY-degenerate resample the exact-zero
        # `std == 0` guards miss -- np.corrcoef returns nan on a tiny-BUT-NONZERO-variance
        # window (a near-constant spell the moving block happens to land on), so lag1_autocorr /
        # vol_clustering can yield nan even though their `sa == 0` guard passed. A single nan in
        # `vals` makes np.quantile return a non-finite CI, and _overlap is NaN-blind (nan < x is
        # False both ways) -> that moment silently marks within=True and the check FAIL-OPENS on
        # a moment it never actually computed. A non-finite moment IS a degenerate resample --
        # drop it exactly like DegenerateSeriesError rather than letting it poison the CI.
        if np.isfinite(m):
            vals.append(m)
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
        # FAIL-OPEN loud (R15, belt-and-braces to block_bootstrap_moment_ci's non-finite drop):
        # _overlap is a bare comparison and is NaN-blind -- a non-finite CI bound would make it
        # return True (statistically consistent) on a moment that could not be computed. The
        # guarantee that CIs are finite is an EMERGENT property of upstream guards, not a local
        # invariant of this comparison; enforce it HERE so the control cannot silently pass a
        # moment on a malformed CI even if a future moment regresses past the ingress drop.
        if not all(np.isfinite(x) for x in (*ref_ci, *gen_ci)):
            raise DegenerateSeriesError(
                f"non-finite CI for moment '{name}' (ref={ref_ci}, gen={gen_ci}) -- "
                "moment uncomputable, no defensible consistency verdict"
            )
        within = _overlap(ref_ci, gen_ci)
        all_within = all_within and within
        g = fn(_clean(generated, min_len=2))
        checks.append(MomentCheck(moment=name, generated=g, ref_ci=ref_ci, gen_ci=gen_ci, within=within))
    return FidelityVerdict(passed=all_within, checks=tuple(checks), block_len=block_len, alpha=alpha)
