"""Premise-level demand off LOCAL weather, reconciled to national — W1_5 (L2).

The `simulation.demand_model.build_demand_shape` layer (W1_5 L1) already turns a
property's characteristics + a *national* daily mean temperature into a 48-period
half-hourly demand shape. This module closes the L1→L2 gap the maturity map makes
load-bearing: **each premise responds to its OWN LOCAL weather**, not the national
mean, and the **demand-weighted aggregate of premise demand reconciles to national
demand** — an aggregation-consistency invariant that is *mutation-testable* (R15),
the premise-level twin of W1_4's regional-field reconciliation one level up.

Where the local weather comes from
----------------------------------
W1_4 (`sim.weather_engine.simulate_regional_deviations`) produces, per macro
variable, a per-region daily *deviation from the national signal*, spatially
correlated and (demand-weighted) reconciling to national to ~1e-4 by construction.
A premise in region ``r`` therefore sees ``local_temp = national_temp + dev_r``.
This module stays decoupled from the weather engine's numpy/array machinery the
same way `demand_model` does: it takes plain scalar deviations in and returns
plain lists out, so it is unit-testable without the RNG/covariance stack.

The invariant is NOT a tautology (R15 doctrine)
-----------------------------------------------
Because premise demand is a *non-linear* function of temperature (the HDD/CDD
``max(0, ...)`` kink), the demand-weighted aggregate of premise demand computed
off dispersed local weather is NOT identically equal to the demand at the average
(national) weather — the difference is the second-order convexity (Jensen) term at
the kink. `reconciliation_residual` measures that gap against an **independently
computed** national reference (each region's premise evaluated at the *national*
temperature), never against the premise sum itself — so the check genuinely
compares two quantities and can FIRE. `aggregate_reconciles` is the failable
predicate: it passes for the real field (small convexity residual) and fires when
a region is perturbed off-manifold so the demand-weighted deviations stop summing
to ~0. `reconcile_to_national` supplies the "summed+SCALED" enforcement step
(a single scale factor makes the aggregate match national exactly by construction)
for callers that need settlement-consistent premise demand.

Epistemic note: regional weather is genuinely public (company-knowable), so this
lives on the public side of the wall. The module is SIM-side demand *generation*
and imports no company/saas state — the reconciliation reference is derived from
the same demand physics, not from any company observable.

Idiosyncratic per-property noise — the L2→L3 term (C-S2)
--------------------------------------------------------
The W1_5 DoD's final term is "+ idiosyncratic noise": two premises with identical
characteristics, weather and archetype still do not meter identically. That is a
premise-level draw, so it lives in its OWN named, seeded RNG substream
(`_substream`, C-S2 discipline copied from `household_budget`): the factor for a
premise is a pure function of `(STREAM_NAME, salt, premise_id, seed)`, so a draw
here can never shift another subsystem's sequence and replay is deterministic.

The noise is **multiplicative and mean-1 by construction** (a lognormal with its
log-mean set so ``E[factor] == 1``): a premise consumes a bit more or less than its
deterministic shape, but the noise does NOT bias the population. That is exactly
what keeps the aggregation-consistency invariant true at L3 — as the book grows the
demand-weighted mean factor converges to 1.0, so the noised aggregate reconciles to
national just as the noise-free one does. `noise_is_unbiased` is the R15-failable
control for this: it PASSES for a real mean-1 draw and FIRES the moment the factors
carry a bias (mean != 1), which would silently inflate or deflate national demand.
"""

from __future__ import annotations

import hashlib
import math
import random

from simulation.demand_model import PERIODS_PER_DAY, build_demand_shape


def local_mean_temp_c(national_temp_c: float, regional_deviation_c: float) -> float:
    """The LOCAL daily mean temperature a premise in a region actually sees:
    the national signal plus that region's deviation (W1_4). A zero deviation
    reproduces the national temperature exactly (backward compatibility)."""
    return national_temp_c + regional_deviation_c


def premise_demand_shape(
    base_shape: list[float],
    national_temp_c: float,
    regional_deviation_c: float,
    commodity: str,
    property: dict,
    irradiance_w_m2_periods: list[float] | None = None,
    idiosyncratic_factor: float = 1.0,
) -> list[float]:
    """A single premise's 48-period demand shape driven by its LOCAL weather.

    Identical to `demand_model.build_demand_shape` except the temperature is the
    premise's LOCAL mean (national + regional deviation) rather than the national
    mean. ``regional_deviation_c == 0.0`` is byte-identical to calling
    `build_demand_shape` with ``national_temp_c`` — so this is a pure, additive
    forward extension of the shipped L1 path, not a change to it.

    ``idiosyncratic_factor`` (default ``1.0``) scales the whole shape by a
    premise-specific multiplier (see `idiosyncratic_factor`). The default of exactly
    ``1.0`` leaves the L2 result byte-identical (``x * 1.0 == x``), so the noise term
    is again a pure additive forward extension with zero blast radius on the L2 path.
    """
    local_temp = local_mean_temp_c(national_temp_c, regional_deviation_c)
    shape = build_demand_shape(
        base_shape, local_temp, commodity, property, irradiance_w_m2_periods
    )
    if idiosyncratic_factor == 1.0:
        return shape
    return [v * idiosyncratic_factor for v in shape]


def _normalised_weights(weights: list[float]) -> list[float]:
    total = float(sum(weights))
    if total <= 0.0:
        raise ValueError("premise demand weights must sum to a positive value")
    return [w / total for w in weights]


def demand_weighted_aggregate(
    premise_shapes: list[list[float]], weights: list[float]
) -> list[float]:
    """The demand-weighted national aggregate shape: ``sum_i w_i * shape_i`` per
    settlement period, weights renormalised to sum to 1.

    Raises on empty input or non-positive total weight — an aggregate of nothing
    is a caller error, never a silently-passing zero (FAIL-OPEN guard, R15).
    """
    if not premise_shapes:
        raise ValueError("cannot aggregate an empty set of premise shapes")
    if len(premise_shapes) != len(weights):
        raise ValueError("premise_shapes and weights must be the same length")
    for s in premise_shapes:
        if len(s) != PERIODS_PER_DAY:
            raise ValueError(f"each premise shape must have {PERIODS_PER_DAY} periods")
    w = _normalised_weights(weights)
    return [
        sum(w[i] * premise_shapes[i][p] for i in range(len(premise_shapes)))
        for p in range(PERIODS_PER_DAY)
    ]


def national_reference_shape(
    base_shapes: list[list[float]],
    national_temp_c: float,
    weights: list[float],
    commodities: list[str],
    properties: list[dict],
    irradiances: list[list[float] | None] | None = None,
) -> list[float]:
    """The INDEPENDENT national-demand reference: each region's premise evaluated
    at the *national* temperature (zero regional deviation), demand-weighted.

    This is the quantity aggregate premise demand must reconcile to. It is derived
    from the demand physics at national weather, NOT from the local-weather premise
    sum — the independence that makes `reconciliation_residual` a real comparison
    rather than a tautology (R15).
    """
    n = len(base_shapes)
    if irradiances is None:
        irradiances = [None] * n
    ref_shapes = [
        premise_demand_shape(
            base_shapes[i], national_temp_c, 0.0, commodities[i], properties[i], irradiances[i]
        )
        for i in range(n)
    ]
    return demand_weighted_aggregate(ref_shapes, weights)


def reconciliation_residual(
    aggregate_shape: list[float], national_shape: list[float]
) -> float:
    """Relative L1 residual between the demand-weighted premise aggregate and the
    independent national reference: ``sum|agg - nat| / sum|nat|``.

    Small (a few % or less) for the real field — the residual is the convexity
    term at the HDD/CDD kink after W1_4's demand-weighted deviations have summed
    to ~0. Grows without bound as the regional field is perturbed off-manifold.
    """
    denom = sum(abs(x) for x in national_shape)
    if denom <= 0.0:
        raise ValueError("national reference demand is zero — cannot reconcile")
    return sum(abs(a - b) for a, b in zip(aggregate_shape, national_shape)) / denom


# The convexity residual for the real 4-region field sits well under this bound;
# a region perturbed off-manifold by a few degrees pushes it past. Tuned to PASS
# the real field and FIRE the mutation, per R15 (the value is a diagnostic band,
# not a target — R12).
RECONCILIATION_TOL = 0.05


def aggregate_reconciles(
    aggregate_shape: list[float],
    national_shape: list[float],
    tol: float = RECONCILIATION_TOL,
) -> bool:
    """The AGGREGATION-CONSISTENCY invariant, as a failable predicate: True iff the
    demand-weighted premise aggregate reconciles to national demand within ``tol``.

    R15: this control CAN fail — it fires (returns False) when premise demand no
    longer adds up to the country (a region perturbed off the reconciling manifold,
    or a wrong national reference). It is not fail-open: a zero/empty national
    reference raises in `reconciliation_residual` rather than passing.
    """
    return reconciliation_residual(aggregate_shape, national_shape) <= tol


def reconcile_to_national(
    premise_shapes: list[list[float]],
    weights: list[float],
    national_shape: list[float],
) -> tuple[list[list[float]], float]:
    """Scale premise demand so the demand-weighted aggregate matches the national
    reference TOTAL exactly by construction — the "summed+SCALED" enforcement step.

    Returns ``(scaled_premise_shapes, factor)``. The factor is national_total /
    aggregate_total; applying it to every premise makes the reconciliation residual
    ~0 by construction. Callers that need settlement-consistent premise demand use
    this; the invariant `aggregate_reconciles` still measures the *pre-scale*
    physical gap (so scaling does not hide a broken field — the residual is reported
    as a diagnostic, R12, before being corrected).
    """
    aggregate = demand_weighted_aggregate(premise_shapes, weights)
    agg_total = sum(aggregate)
    nat_total = sum(national_shape)
    if agg_total <= 0.0:
        raise ValueError("aggregate premise demand is zero — nothing to scale")
    factor = nat_total / agg_total
    scaled = [[v * factor for v in shape] for shape in premise_shapes]
    return scaled, factor


# ---------------------------------------------------------------------------
# Idiosyncratic per-property noise — the L2→L3 "+ noise" DoD term (C-S2).
# ---------------------------------------------------------------------------
# Named substream, one salt per stochastic mechanism (C-S2). A future premise-level
# draw APPENDS a salt here; it never inserts a draw into an existing substream, so it
# can never shift this one's sequence (the RNG-substream discipline).
STREAM_NAME = "W1_5_premise_demand_shape"
_IDIOSYNCRATIC_SALT = "idiosyncratic"

# Coefficient of variation of the per-premise idiosyncratic multiplier. R10
# convention / R12 diagnostic band, NOT a fitted truth: real premise-level metered
# demand disperses far more than the deterministic archetype shape predicts, but the
# exact spread needs real half-hourly premise metering (Elexon settlement / smart-
# meter panel) unavailable to this session — flagged for calibration, not fabricated.
# It is mean-preserving regardless of value, so the aggregation invariant does not
# depend on the number chosen (that is the point).
_DEFAULT_CV = 0.15


def _substream(base_seed: int, salt: str = "") -> random.Random:
    """An ISOLATED `random.Random` seeded from a STABLE sha256 of
    (`STREAM_NAME`::`salt`::`base_seed`) — the C-S2 heart of this term.

    The seed is a pure function of (name, salt, base_seed): shares no state with the
    global `random`, with any other salt here, or with any other subsystem's
    substream, so a draw can never shift another sequence. A stable digest (not
    Python's per-process-salted `hash()`) gives deterministic replay across processes.
    """
    key = f"{STREAM_NAME}::{salt}::{base_seed}".encode("utf-8")
    seed_int = int.from_bytes(hashlib.sha256(key).digest()[:8], "big")
    return random.Random(seed_int)


def _base_seed_for(premise_id: str, seed: int | None) -> int:
    """Resolve a premise's base seed: a stable md5 of the premise_id, with any
    explicit book-level ``seed`` mixed in. Every premise gets a DISTINCT seed (so a
    book of premises draws distinct factors), and a given ``seed`` makes the whole
    book reproducible — deterministic per (premise_id, seed) across processes (C-S2).
    """
    key = premise_id if seed is None else f"{premise_id}::{seed}"
    return int.from_bytes(hashlib.md5(key.encode("utf-8")).digest()[:8], "big")


def idiosyncratic_factor(
    premise_id: str, *, seed: int | None = None, cv: float = _DEFAULT_CV
) -> float:
    """A premise's idiosyncratic demand multiplier: a mean-1, strictly-positive
    lognormal draw from this atom's OWN named C-S2 substream.

    Mean-1 BY CONSTRUCTION — a lognormal ``exp(mu + sigma*Z)`` with ``mu`` set to
    ``-sigma^2/2`` so ``E[factor] == 1`` exactly — so the noise perturbs an
    individual premise without biasing the population aggregate. Strictly positive
    (a premise cannot meter negative energy). Deterministic in (premise_id, seed):
    the same premise draws the same factor on replay (C-S2 idempotency). ``cv <= 0``
    returns exactly ``1.0`` (noise off).
    """
    if cv <= 0.0:
        return 1.0
    sigma = math.sqrt(math.log(1.0 + cv * cv))
    mu = -0.5 * sigma * sigma
    r = _substream(_base_seed_for(premise_id, seed), _IDIOSYNCRATIC_SALT)
    return math.exp(mu + sigma * r.gauss(0.0, 1.0))


def demand_weighted_mean_factor(
    premise_ids: list[str],
    weights: list[float],
    *,
    seed: int | None = None,
    cv: float = _DEFAULT_CV,
) -> float:
    """The demand-weighted mean of the premises' idiosyncratic factors.

    This is what must stay ~1.0 for the aggregation-consistency invariant to survive
    the noise term: a mean-1 draw over a demand-weighted book converges to 1.0 as the
    book grows (LLN), so the noised aggregate reconciles to national just as the
    noise-free one does. Raises on empty input or non-positive total weight (FAIL-OPEN
    guard, R15) — the mean factor of no premises is a caller error, not a silent 1.0.
    """
    if not premise_ids:
        raise ValueError("cannot take the mean factor of an empty premise set")
    if len(premise_ids) != len(weights):
        raise ValueError("premise_ids and weights must be the same length")
    w = _normalised_weights(weights)
    return sum(
        w[i] * idiosyncratic_factor(premise_ids[i], seed=seed, cv=cv)
        for i in range(len(premise_ids))
    )


# The demand-weighted mean of N mean-1 factors has sampling std ~ cv*sqrt(sum w_i^2),
# which → 0 as the book grows. This tol PASSES a real (unbiased) draw over a
# realistic book and FIRES on any systematic bias in the factors (R15). Diagnostic
# band, not a target (R12).
NOISE_BIAS_TOL = 0.02


def noise_is_unbiased(
    premise_ids: list[str],
    weights: list[float],
    *,
    seed: int | None = None,
    cv: float = _DEFAULT_CV,
    tol: float = NOISE_BIAS_TOL,
) -> bool:
    """The R15-failable control that the idiosyncratic noise preserves the
    aggregation-consistency invariant: True iff the demand-weighted mean factor is
    within ``tol`` of 1.0.

    It CAN fail — it FIRES (returns False) the moment the factors carry a bias (a
    mean != 1 that would silently inflate or deflate the national aggregate), and it
    is not fail-open: an empty book raises in `demand_weighted_mean_factor` rather
    than passing. Over a realistic book of mean-1 draws it passes (the whole point of
    building the noise mean-preserving).
    """
    return abs(demand_weighted_mean_factor(premise_ids, weights, seed=seed, cv=cv) - 1.0) <= tol
