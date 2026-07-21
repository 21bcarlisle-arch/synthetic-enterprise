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

R10 simplification (deferred, not faked): idiosyncratic per-property noise (the
"+ noise" term in the W1_5 DoD) is NOT added here — this pass builds the
LOCAL-weather response + the national-reconciliation invariant, which are the two
load-bearing DoD properties. Idiosyncratic noise needs its own named RNG substream
(C-S2) and is registered as remaining L2→L3 work alongside the coupled-triad gap.
"""

from __future__ import annotations

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
) -> list[float]:
    """A single premise's 48-period demand shape driven by its LOCAL weather.

    Identical to `demand_model.build_demand_shape` except the temperature is the
    premise's LOCAL mean (national + regional deviation) rather than the national
    mean. ``regional_deviation_c == 0.0`` is byte-identical to calling
    `build_demand_shape` with ``national_temp_c`` — so this is a pure, additive
    forward extension of the shipped L1 path, not a change to it.
    """
    local_temp = local_mean_temp_c(national_temp_c, regional_deviation_c)
    return build_demand_shape(
        base_shape, local_temp, commodity, property, irradiance_w_m2_periods
    )


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
