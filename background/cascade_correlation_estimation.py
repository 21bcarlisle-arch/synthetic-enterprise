"""Cascade correlation ESTIMATION method (Epoch-2 campaign atom D).

WHAT THIS IS. The reusable protocol for estimating the *nature* AND *strength*
of every dependence in the coupled weather->demand->generation->price->imbalance
cascade, with **joint-tail emphasis** (the joint tail is the killing quantity,
not the average), plus **the single portable statistic** that makes every link
comparable and every coupling control R15-mutation-testable. Design:
EPOCH2_D_CASCADE_CORRELATION_ESTIMATION_DISCOVER.md (6a47b1172). It generalises
W1_3's worked example (one link, one estimator) into one recipe for the chain.

THE PORTABLE SPINE -- joint-tail lift `L(u)` (S4):

    L(u) = P(A in tail_u & B in tail_u) / [ P(A in tail_u) * P(B in tail_u) ]

the observed joint-corner mass divided by the mass INDEPENDENCE would give it,
at a declared tail quantile `u`, on the conditioned (e.g. winter) sample.
  * L = 1  -> extremes independent (the null / a broken coupling).
  * L > 1  -> corner fatter than independent -- the killing signature (D1 decile L=2.34x).
  * L < 1  -> anti-coupled in the tail (e.g. interconnector relief withdrawn -- a hazard flag).
Scale-free and marginal-free (a ratio of probabilities at matched quantiles), so
the SAME number is comparable across every link, which a raw Pearson rho is not.
Relation to the tail-dependence coefficient: with p_A=p_B=(1-u), lambda ~ L*(1-u).

WHY POOLING IS FORBIDDEN (S3.1, the anti-pooling step): pooling across regimes is
not a smaller effect, it is a SIGN-AND-EXISTENCE error -- D1 winter temp/wind is
+0.507 but the pooled Pearson is -0.06, which actively lies. Every estimate
CONDITIONS on its regime first; `L` is computed on the conditioned subset.

R10 HONESTY (asserted != estimated). Where a link's (nature, strength) is not
estimated from data (series unavailable, sample too thin to resolve nature, or a
structural assumption), it is REGISTERED as a named simplification via
`asserted_dependence` -- never dressed as estimated. That is the exact defect
requirement 4 forbids.

R12 anti-goal-seek. `L`, lambda, the CIs are DIAGNOSTICS. Nothing here is tuned
toward a reading; the tail quantile `u` is DECLARED and reported WITH every
statistic (a lift without its `u` is meaningless), never chosen to flatter.

R15. `L` makes every coupling control able to FAIL: the killer mutation for ANY
link is to CUT its coupling (draw the two series independently) -> L -> 1 -> the
`assert_coupling_present` control MUST fire. Guards: TAUTOLOGY (L recomputed from
the series, never a stored 'designed lift'); FAIL-OPEN (empty/degenerate/NaN/
zero-denominator fails loud, never passes); FAIL-SILENT (an unavailable series is
a FAILED check, never skipped-green).

C-S2. The block bootstrap draws from an explicit seeded Generator (deterministic
replay); resampling SPELLS not days honours D8's autocorrelation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Sequence, Tuple

import numpy as np

# ---------------------------------------------------------------------------
# R10-registered defaults (declared, changed only for a stated reason, R4/R13).
# ---------------------------------------------------------------------------
DECILE_U: float = 0.10   # severe tail (~21 winter days on the 4-yr record); the W1_3 decile
QUINTILE_U: float = 0.20  # more power, less severe; report the L(u)-vs-u curve where possible
INDEPENDENCE_NULL: float = 1.0  # L at exact independence -- the crisp, mutation-testable null

# A control fires when an observed lift is within this band of the independence
# null (i.e. the coupling has collapsed). NOT a physics constant -- a mechanism
# threshold; a real run's block-bootstrap CI is the honest arbiter (S4 R15).
_COUPLING_COLLAPSE_BAND: float = 0.15


class DegenerateSeriesError(ValueError):
    """FAIL-OPEN: an empty/all-equal/NaN/zero-denominator input has no defensible
    lift -- raised loud rather than returning a passing-looking 1.0 or 0.0."""


class SeriesUnavailableError(Exception):
    """FAIL-SILENT guard: a required series/anchor is unavailable -> the check is
    a FAILED check, never skipped-green."""


def _clean_pair(a: Sequence[float], b: Sequence[float]) -> Tuple[np.ndarray, np.ndarray]:
    """Aligned finite pairs, or raise (FAIL-OPEN on degenerate input)."""
    av = np.asarray(a, dtype=float)
    bv = np.asarray(b, dtype=float)
    if av.shape != bv.shape:
        raise DegenerateSeriesError(f"length mismatch: {av.shape} vs {bv.shape}")
    if av.size == 0:
        raise DegenerateSeriesError("empty series -- nothing to estimate")
    finite = np.isfinite(av) & np.isfinite(bv)
    av, bv = av[finite], bv[finite]
    if av.size == 0:
        raise DegenerateSeriesError("no finite paired observations")
    if np.all(av == av[0]) or np.all(bv == bv[0]):
        raise DegenerateSeriesError("a constant series has no tail -- lift undefined")
    return av, bv


def _tail_mask(series: np.ndarray, u: float, *, upper: bool) -> np.ndarray:
    """Boolean membership of the tail_u corner. upper=True -> top-u fraction
    (>= the (1-u) quantile); upper=False -> bottom-u fraction (<= the u quantile)."""
    if not (0.0 < u < 1.0):
        raise ValueError(f"tail quantile u must be in (0,1), got {u}")
    if upper:
        thresh = float(np.quantile(series, 1.0 - u))
        return series >= thresh
    thresh = float(np.quantile(series, u))
    return series <= thresh


@dataclass(frozen=True)
class LiftEstimate:
    """A joint-tail lift reported WITH its declared `u` (a lift without its u is
    meaningless, S3.2). `lam` is the implied tail-dependence coefficient
    lambda ~ L*(1-u). `n_conditioned` is the effective sample the estimate rests
    on (small + autocorrelated -> trust the block-bootstrap CI, not this point)."""

    lift: float
    u: float
    upper: bool
    lam: float
    n_conditioned: int
    p_joint: float
    p_a: float
    p_b: float

    @property
    def coupled(self) -> bool:
        """Tail-coupled == lift meaningfully above the independence null."""
        return self.lift > INDEPENDENCE_NULL + _COUPLING_COLLAPSE_BAND

    @property
    def anti_coupled(self) -> bool:
        """Relief-withdrawn hazard: lift meaningfully BELOW independence."""
        return self.lift < INDEPENDENCE_NULL - _COUPLING_COLLAPSE_BAND


def joint_tail_lift(
    a: Sequence[float],
    b: Sequence[float],
    u: float = DECILE_U,
    *,
    upper: bool = True,
) -> LiftEstimate:
    """The portable spine (S4). `L = P(A&B in tail) / [P(A in tail)*P(B in tail)]`
    on the (already-conditioned) sample. TAUTOLOGY guard: recomputed from the
    series' own corner counts, never a stored parameter. FAIL-OPEN: a zero
    denominator (a tail that never fires) raises, never returns a passing 1.0."""
    av, bv = _clean_pair(a, b)
    ma = _tail_mask(av, u, upper=upper)
    mb = _tail_mask(bv, u, upper=upper)
    n = av.size
    p_a = float(ma.mean())
    p_b = float(mb.mean())
    p_joint = float((ma & mb).mean())
    denom = p_a * p_b
    if denom <= 0.0:
        raise DegenerateSeriesError(
            f"empty tail corner at u={u} (p_a={p_a}, p_b={p_b}) -- lift undefined"
        )
    lift = p_joint / denom
    return LiftEstimate(
        lift=lift, u=u, upper=upper, lam=lift * (1.0 - u),
        n_conditioned=n, p_joint=p_joint, p_a=p_a, p_b=p_b,
    )


def lift_curve(
    a: Sequence[float],
    b: Sequence[float],
    us: Sequence[float] = (0.05, 0.10, 0.20, 0.30),
    *,
    upper: bool = True,
) -> Tuple[Tuple[float, float], ...]:
    """The `L(u)`-vs-`u` curve (the chi(u) diagnostic in lift units): does the
    corner fatten INTO the tail (rising L as u->0 = asymptotic dependence) or
    fade (asymptotic independence)? A single `u` is a summary of this curve."""
    out = []
    for u in us:
        try:
            out.append((u, joint_tail_lift(a, b, u, upper=upper).lift))
        except DegenerateSeriesError:
            continue  # a tail too thin at this u drops out of the curve (declared, not faked)
    if not out:
        raise DegenerateSeriesError("no estimable u in the requested curve")
    return tuple(out)


def condition(series: Sequence[float], regime_mask: Sequence[bool]) -> np.ndarray:
    """The anti-pooling step (S3.1): restrict to the regime where the coupling is
    claimed BEFORE estimating. `regime_mask` is a boolean selector (e.g. winter
    DJF, a configurable cold-season set -- never a hardcoded {12,1,2}, S6)."""
    sv = np.asarray(series, dtype=float)
    mv = np.asarray(regime_mask, dtype=bool)
    if sv.shape != mv.shape:
        raise DegenerateSeriesError(f"mask/series length mismatch: {sv.shape} vs {mv.shape}")
    return sv[mv]


def block_bootstrap_lift_ci(
    a: Sequence[float],
    b: Sequence[float],
    u: float = DECILE_U,
    *,
    upper: bool = True,
    block_len: int = 5,
    n_boot: int = 500,
    alpha: float = 0.10,
    seed: int = 0,
) -> Tuple[float, float]:
    """A (1-alpha) CI on `L` by MOVING-BLOCK bootstrap: resample contiguous
    SPELLS of length `block_len` (>= the persistence scale, D8 temp lag-1 ~0.78),
    NOT individual days, so the CI honours autocorrelation -- the effective
    independent sample is far below the nominal n and a naive day-resample CI is
    far too tight. Deterministic given `seed` (C-S2 replay). Returns (lo, hi)."""
    av, bv = _clean_pair(a, b)
    n = av.size
    if block_len < 1 or block_len > n:
        raise ValueError(f"block_len must be in [1, n={n}], got {block_len}")
    rng = np.random.default_rng(seed)
    n_blocks = int(np.ceil(n / block_len))
    max_start = n - block_len
    lifts = []
    for _ in range(n_boot):
        starts = rng.integers(0, max_start + 1, size=n_blocks)
        idx = np.concatenate([np.arange(s, s + block_len) for s in starts])[:n]
        try:
            lifts.append(joint_tail_lift(av[idx], bv[idx], u, upper=upper).lift)
        except DegenerateSeriesError:
            continue  # a degenerate resample is dropped (never counted as a passing 1.0)
    if not lifts:
        raise DegenerateSeriesError("every bootstrap resample was degenerate -- CI undefined")
    lo = float(np.quantile(lifts, alpha / 2.0))
    hi = float(np.quantile(lifts, 1.0 - alpha / 2.0))
    return lo, hi


def end_to_end_lift(
    terminal: Sequence[float],
    driver: Sequence[float],
    u: float = DECILE_U,
    *,
    upper: bool = True,
) -> LiftEstimate:
    """`L_end` (S4, D6): the terminal-quantity (imbalance cost / price) joint-tail
    lift against the first driver. The compounding claim is the testable
    inequality `L_end >= prod(L_link) >= L_A` -- the chain AMPLIFIES the tail,
    never thins it. (Same estimator; named distinctly for the cascade-level read.)"""
    return joint_tail_lift(terminal, driver, u, upper=upper)


def compounding_holds(l_end: float, link_lifts: Sequence[float], *, tol: float = 1e-9) -> bool:
    """The compounding inequality `L_end >= prod(L_link)` (S4). A cascade whose
    end-to-end tail is THINNER than the product of its links violates the
    physics claim -- a finding, returned as False (not silently accepted)."""
    if not link_lifts:
        raise DegenerateSeriesError("no link lifts -- compounding inequality undefined")
    product = float(np.prod([float(x) for x in link_lifts]))
    return l_end + tol >= product


# ===========================================================================
# R10 honesty: register an ASSERTED (not estimated) dependence
# ===========================================================================

@dataclass(frozen=True)
class AssertedDependence:
    """A link whose (nature, strength) is ASSERTED, not estimated (S3.6) -- a
    pre-registered R10 simplification. Carries what is asserted, why, its assumed
    value/sign, and precisely which real series + statistic would ground it. An
    asserted dependence dressed as estimated is the defect requirement 4 forbids."""

    link_id: str
    assumed_lift: float
    assumed_sign: str            # "upper" | "lower" | "anti"
    reason: str                  # why not estimated (series unavailable / sample too thin / structural)
    grounding: str               # the real series + statistic that would estimate it


def asserted_dependence(
    link_id: str, *, assumed_lift: float, assumed_sign: str, reason: str, grounding: str,
) -> AssertedDependence:
    """Build a registered asserted-dependence record. `grounding` MUST name the
    real series + statistic that would ground it (an assertion with no path to
    estimation is not honest registration, S3.6) -- enforced non-empty."""
    if not reason.strip() or not grounding.strip():
        raise ValueError("an asserted dependence must state its reason AND its grounding path (R10)")
    if assumed_sign not in ("upper", "lower", "anti"):
        raise ValueError(f"assumed_sign must be upper|lower|anti, got {assumed_sign!r}")
    return AssertedDependence(
        link_id=link_id, assumed_lift=float(assumed_lift), assumed_sign=assumed_sign,
        reason=reason, grounding=grounding,
    )


# ===========================================================================
# R15 control -- a coupling that has been CUT must be caught
# ===========================================================================

@dataclass(frozen=True)
class CouplingVerdict:
    present: bool
    lift: float
    u: float
    detail: str


def assert_coupling_present(
    a: Sequence[float],
    b: Sequence[float],
    u: float = DECILE_U,
    *,
    upper: bool = True,
    min_lift: Optional[float] = None,
) -> CouplingVerdict:
    """The R15 control. A link CLAIMED to be tail-coupled must show `L` above the
    independence null; if its coupling has been CUT (the two series drawn
    independently) `L -> 1` and this control FIRES (present=False). FAIL-SILENT
    guard: an unavailable series raises SeriesUnavailableError (a failed check),
    never returns present=True. FAIL-OPEN inherited from joint_tail_lift."""
    if a is None or b is None:
        raise SeriesUnavailableError("a series is unavailable -- an unavailable check is a FAILED check")
    floor = INDEPENDENCE_NULL + _COUPLING_COLLAPSE_BAND if min_lift is None else float(min_lift)
    est = joint_tail_lift(a, b, u, upper=upper)
    present = est.lift >= floor
    return CouplingVerdict(
        present=present, lift=est.lift, u=u,
        detail=(f"L={est.lift:.3f} at u={u} vs floor {floor:.3f} "
                f"(null={INDEPENDENCE_NULL}); {'coupled' if present else 'COLLAPSED to independence'}"),
    )


def cut_coupling(b: Sequence[float], *, seed: int = 0) -> np.ndarray:
    """The killer MUTATION (S4 R15): break a link by replacing B with an
    independent permutation of itself -- identical marginal, destroyed joint
    structure. On the cut series `L -> 1` and `assert_coupling_present` MUST fire.
    Provided so the mutation is a first-class, reusable test primitive, not
    re-hand-rolled per link. Deterministic given `seed` (C-S2)."""
    bv = np.asarray(b, dtype=float).copy()
    np.random.default_rng(seed).shuffle(bv)
    return bv
