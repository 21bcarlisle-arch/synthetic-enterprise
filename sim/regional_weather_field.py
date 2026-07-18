"""W1_4 — regional weather field: aggregation-consistent, spatially-correlated
regional deviations bound to the national (W1_3) signal.

This module builds the *precise remaining gap* of the regional-weather atom. The
spatial-correlation mechanism itself already exists — ``sim/weather_engine.py``
Pass 2 (``fit_regional_cholesky`` / ``simulate_regional_deviations``) fits a real
cross-location covariance of ``(location - national)`` deviations and draws
correlated deviations from it. What did NOT exist, and is built here, is:

  1. The **demand-weighted AGGREGATION-CONSISTENCY invariant, true by
     construction**: after drawing regional deviations, a linear *projection* onto
     the zero-weighted-mean manifold makes the demand-weighted regional aggregate
     reconcile to the national signal *exactly* (up to floating point), per
     variable, per period. A world where every region freezes while national is
     mild is off the manifold and cannot be constructed — not merely improbable.

  2. A **real GB region partition** (the 14 GB DNO licence areas) defined
     *neutrally on the SIM side*, plus a **demand-weight** table sourced
     independently of the generator fit (anti-marking-own-homework).

  3. A **named, seeded RNG substream** (``regional_field``) for the regional draw
     (C-S2), so a draw here can never perturb another subsystem's sequence.

The reconciliation invariant + its mutation tests are the load-bearing R15
deliverable and live in ``tests/sim/test_regional_weather_field.py``.

Epistemic wall: this is SIM-side WORLD physics. It defines its OWN region key and
does NOT import ``company.*`` (importing ``company/market/duos_ledger.py::DNOArea``
here would be an architecture-backwards dependency — the company must never be a
prerequisite of the world). See ``docs/design/REGIONAL_WEATHER_FIELD_FRAME.md``.

HONESTY NOTES (read these before trusting a magnitude):
  * The **demand weights** below are a CLEARLY-LABELLED PLACEHOLDER (a rough
    population/consumption proxy), NOT the real DESNZ sub-national electricity
    consumption shares — those require a network pull (``discovery-agent`` against
    DESNZ regional statistics) not available to this build fork. The *mechanism*
    (projection, invariant, mutation tests) is fully real and independent of the
    exact weight values; the weights are an injectable input, so the real table
    drops in without touching any logic. Registered as a named simplification
    (R10) in ``SIMPLIFICATIONS`` below.
  * The **feasibility bounds** are placeholder climatological guards, not
    Met-Office-calibrated per-region spreads. Also registered.
  * This module does NOT re-derive a real per-region spatial covariance for all 14
    regions (only 4 calibration points have real Open-Meteo series). Callers who
    want a correlated draw over the full partition must supply their own covariance
    or reuse the 4-point Cholesky; ``draw_placeholder_deviations`` provides an
    isotropic placeholder draw for end-to-end exercise, explicitly flagged.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from enum import Enum

import numpy as np

# The RNG substream name for the regional field (C-S2). Distinct from
# ``national_regime`` (W1_3), ``premise_noise`` (W1_5), ``price`` (W1_6) and every
# other subsystem's stream — matching the naming fixed in
# WEATHER_PHYSICS_HIERARCHY_DESIGN.md §7.
SUBSTREAM_NAME = "regional_field"

# Numerical tolerance for the aggregation-consistency invariant. Because
# consistency is STRUCTURAL (projection, §3.2 of the FRAME), this is a pure
# floating-point-accumulation tolerance over |R| regions, never a modelling
# fudge-factor. Scaled generously above machine epsilon to absorb float summation
# over ~14 regions while still being astronomically tighter than any real
# perturbation a mutation would introduce.
TOL_AGG = 1e-9


class GBRegion(str, Enum):
    """The 14 GB electricity distribution (DNO) licence areas — the real
    administrative partition GB settlement/DUoS uses — defined NEUTRALLY on the
    SIM side.

    Why a sim-side copy rather than importing ``company.market.duos_ledger.DNOArea``:
    the epistemic wall runs one way — the WORLD may never depend on the COMPANY.
    A shared location could be justified later (regulation-commons style), but the
    minimal, wall-safe choice today is an independent key. These names use the real
    GB DNO licence-area descriptions (correcting two probable naming slips in the
    company enum — ``MERSEYRAIL`` → SP Manweb / Merseyside & N. Wales, and
    ``EAST_OF_SCOTLAND`` → SP Distribution / S. & Central Scotland — which are out
    of scope to fix in the billing enum from here).
    """

    NORTH_SCOTLAND = "north_scotland"                    # SSEN North
    SOUTH_CENTRAL_SCOTLAND = "south_central_scotland"    # SP Distribution
    NORTH_EAST_ENGLAND = "north_east_england"            # NPg Northeast
    YORKSHIRE = "yorkshire"                              # NPg Yorkshire
    NORTH_WEST_ENGLAND = "north_west_england"            # Electricity North West
    MERSEYSIDE_NORTH_WALES = "merseyside_north_wales"    # SP Manweb
    EAST_MIDLANDS = "east_midlands"                      # NGED East Midlands
    WEST_MIDLANDS = "west_midlands"                      # NGED West Midlands
    SOUTH_WALES = "south_wales"                          # NGED South Wales
    SOUTH_WEST_ENGLAND = "south_west_england"            # NGED South West
    EAST_ENGLAND = "east_england"                        # UKPN Eastern
    LONDON = "london"                                    # UKPN London
    SOUTH_EAST_ENGLAND = "south_east_england"            # UKPN South Eastern
    SOUTHERN_ENGLAND = "southern_england"                # SSEN Southern


# ---------------------------------------------------------------------------
# Demand weights — PLACEHOLDER, independent of the generator fit.
# ---------------------------------------------------------------------------
# Anti-marking-own-homework (FRAME §2.2): the weights used to CHECK/RECONCILE the
# field must come from a source INDEPENDENT of the historical weather series the
# generator covariance was fitted on. These are a rough population/consumption
# proxy (roughly ordered by regional GB electricity demand), CLEARLY FLAGGED as a
# placeholder pending a real DESNZ sub-national-consumption pull. They are NOT
# presented as the true regional demand split — do not cite these as real.
#   * Structural properties that ARE guaranteed and DO matter: strictly positive,
#     normalised to sum 1. The invariant's correctness depends only on these two
#     properties, never on the exact magnitudes.
_PLACEHOLDER_DEMAND_WEIGHTS_RAW: dict[GBRegion, float] = {
    GBRegion.NORTH_SCOTLAND: 3.0,
    GBRegion.SOUTH_CENTRAL_SCOTLAND: 7.0,
    GBRegion.NORTH_EAST_ENGLAND: 5.0,
    GBRegion.YORKSHIRE: 8.0,
    GBRegion.NORTH_WEST_ENGLAND: 8.0,
    GBRegion.MERSEYSIDE_NORTH_WALES: 6.0,
    GBRegion.EAST_MIDLANDS: 8.0,
    GBRegion.WEST_MIDLANDS: 8.0,
    GBRegion.SOUTH_WALES: 5.0,
    GBRegion.SOUTH_WEST_ENGLAND: 7.0,
    GBRegion.EAST_ENGLAND: 9.0,
    GBRegion.LONDON: 9.0,
    GBRegion.SOUTH_EAST_ENGLAND: 8.0,
    GBRegion.SOUTHERN_ENGLAND: 9.0,
}

# Named simplifications (R10) — a class-level register, not fixed on sight.
SIMPLIFICATIONS: list[dict[str, str]] = [
    {
        "id": "W1_4_PLACEHOLDER_DEMAND_WEIGHTS",
        "what": "Regional demand weights are a rough population/consumption proxy, "
                "not real DESNZ sub-national electricity-consumption shares.",
        "why": "No network access in this build fork to pull DESNZ statistics; the "
               "reconciliation mechanism is independent of the exact weights.",
        "resolve": "discovery-agent pull of DESNZ 'Sub-national electricity "
                   "consumption' regional shares -> replace demand_weights() table.",
    },
    {
        "id": "W1_4_PLACEHOLDER_GENERATION_WEIGHTS",
        "what": "No separate wind/solar capacity-share weight table is provided; a "
                "generation-relevant reconciliation would need installed-capacity "
                "shares (a DIFFERENT real source than demand shares).",
        "why": "Same network constraint; and generation reconciliation is a later "
               "concern (W1_6/W1_7) not required for the temperature/demand invariant.",
        "resolve": "DESNZ/NESO regional generation-capacity statistics -> a second "
                   "weight table passed to the same projection/invariant functions.",
    },
    {
        "id": "W1_4_PLACEHOLDER_FEASIBILITY_BOUNDS",
        "what": "Feasibility bounds (regional temp spread, wind ceiling) are "
                "placeholder climatological guards, not Met-Office-calibrated "
                "per-region spreads.",
        "why": "Real per-region spread data requires a network pull.",
        "resolve": "Met Office regional climate-normal spreads -> per-region bounds.",
    },
    {
        "id": "W1_4_PLACEHOLDER_ISOTROPIC_COVARIANCE",
        "what": "draw_placeholder_deviations() uses an isotropic covariance, not a "
                "real distance-keyed per-region spatial covariance for all 14 regions.",
        "why": "Only the 4 calibration points (C1-C4) have real Open-Meteo series; a "
               "real 14-region covariance needs per-region historical pulls. The "
               "PROJECTION + INVARIANT (the deliverable) are covariance-agnostic.",
        "resolve": "Per-region Open-Meteo pulls via sim/weather_ingestor.py -> real "
                   "distance-keyed covariance, then reuse fit_regional_cholesky.",
    },
]


def default_regions() -> list[GBRegion]:
    """The canonical 14-region GB partition, in a stable order."""
    return list(GBRegion)


def demand_weights(regions: list[GBRegion] | None = None) -> dict[GBRegion, float]:
    """Return normalised (sum == 1), strictly-positive demand weights for the
    given regions (default: all 14).

    PLACEHOLDER magnitudes (see module docstring / SIMPLIFICATIONS). The two
    properties the invariant actually relies on — positivity and sum-to-one — are
    guaranteed here regardless of the underlying proxy values.
    """
    if regions is None:
        regions = default_regions()
    raw = {r: _PLACEHOLDER_DEMAND_WEIGHTS_RAW[r] for r in regions}
    total = sum(raw.values())
    if total <= 0:
        raise ValueError("demand weights must sum to a positive value")
    return {r: w / total for r, w in raw.items()}


# ---------------------------------------------------------------------------
# RNG substream (C-S2) — a named, seeded, ISOLATED numpy Generator.
# ---------------------------------------------------------------------------
def regional_field_rng(base_seed: int, salt: str = "") -> np.random.Generator:
    """An isolated ``np.random.Generator`` for the regional field, seeded
    deterministically from ``SUBSTREAM_NAME:salt:base_seed`` via SHA-256.

    Structural isolation (matching simulation/population_draw.py::_substream and
    background/gap_metric.py): a fresh Generator whose seed shares no state with
    the global RNG or any other subsystem's substream, so a draw here can never
    shift another subsystem's sequence (the 01:09Z shared-RNG lesson). Deterministic
    replay: same (base_seed, salt) => identical field => identical residual (C-S2).
    """
    key = f"{SUBSTREAM_NAME}:{salt}:{base_seed}".encode("utf-8")
    seed_int = int.from_bytes(hashlib.sha256(key).digest()[:8], "big")
    return np.random.default_rng(seed_int)


# ---------------------------------------------------------------------------
# The projection step — makes the invariant TRUE BY CONSTRUCTION.
# ---------------------------------------------------------------------------
def _weight_vector(weights: dict[GBRegion, float], regions: list[GBRegion]) -> np.ndarray:
    """Validate and return weights as an ordered vector. FAIL-OPEN guard: a
    missing region, a non-finite weight, a non-positive weight, or a set that does
    not sum to ~1 raises — a degenerate weight table is never silently accepted."""
    if not regions:
        raise ValueError("region set is empty — a field with no regions cannot reconcile")
    w = np.empty(len(regions), dtype=float)
    for i, r in enumerate(regions):
        if r not in weights:
            raise ValueError(f"missing weight for region {r!r}")
        val = weights[r]
        if not np.isfinite(val):
            raise ValueError(f"non-finite weight for region {r!r}: {val}")
        if val <= 0.0:
            # Strictly positive: a zero-weight region is unconstrained by the
            # aggregate, which would create a blind spot for the invariant. Every
            # GB DNO area has demand, so this is a safe, control-strengthening rule.
            raise ValueError(f"weight for region {r!r} must be strictly positive: {val}")
        w[i] = val
    total = w.sum()
    if not np.isclose(total, 1.0, atol=1e-9):
        raise ValueError(f"weights must sum to 1.0 (got {total})")
    return w


def project_to_national_consistency(
    deviations: dict[GBRegion, np.ndarray],
    weights: dict[GBRegion, float],
) -> dict[GBRegion, np.ndarray]:
    """Project raw regional deviations onto the zero-weighted-mean manifold:

        Delta'_r = Delta_r - Sum_s w_s * Delta_s

    so that ``Sum_r w_r * Delta'_r == 0`` identically. Applied per element (period),
    the resulting region values ``X_r = X_national + Delta'_r`` satisfy
    ``Sum_r w_r * X_r == X_national`` exactly, up to floating point — the
    aggregation-consistency invariant BY CONSTRUCTION, not by luck.

    ``deviations`` maps region -> array over periods (all arrays same length).
    FAIL-OPEN: an empty region set, a NaN deviation, or a shape mismatch raises.
    """
    regions = list(deviations.keys())
    w = _weight_vector(weights, regions)
    stacked = _stack(deviations, regions)  # shape (n_regions, n_periods)
    weighted_mean = (w[:, None] * stacked).sum(axis=0)  # shape (n_periods,)
    projected = stacked - weighted_mean[None, :]
    return {r: projected[i] for i, r in enumerate(regions)}


def _stack(field: dict[GBRegion, np.ndarray], regions: list[GBRegion]) -> np.ndarray:
    """Stack a region->array field into (n_regions, n_periods), validating finiteness
    and shape. FAIL-OPEN: NaN/inf or ragged arrays raise rather than pass."""
    arrays = []
    n_periods = None
    for r in regions:
        a = np.asarray(field[r], dtype=float)
        if a.ndim == 0:
            a = a.reshape(1)
        if n_periods is None:
            n_periods = a.shape[0]
        elif a.shape[0] != n_periods:
            raise ValueError(f"region {r!r} has {a.shape[0]} periods, expected {n_periods}")
        if not np.all(np.isfinite(a)):
            raise ValueError(f"region {r!r} contains non-finite values")
        arrays.append(a)
    if not arrays:
        raise ValueError("empty field — no regions to stack")
    return np.vstack(arrays)


def build_consistent_region_values(
    national: np.ndarray,
    deviations: dict[GBRegion, np.ndarray],
    weights: dict[GBRegion, float],
) -> dict[GBRegion, np.ndarray]:
    """Full construction: project the deviations, add the national anchor, return
    per-region values that reconcile to ``national`` by construction.

    ``national`` is the W1_3 national signal for one variable over periods — held
    independently and NEVER re-derived from the regional sum (TAUTOLOGY guard)."""
    national = np.asarray(national, dtype=float)
    if national.ndim == 0:
        national = national.reshape(1)
    if not np.all(np.isfinite(national)):
        raise ValueError("national signal contains non-finite values")
    projected = project_to_national_consistency(deviations, weights)
    return {r: national + d for r, d in projected.items()}


# ---------------------------------------------------------------------------
# The aggregation-consistency invariant (I1) + its check.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ReconciliationResult:
    passed: bool
    max_abs_residual: float
    tol: float
    reason: str = ""


def reconciliation_residual(
    region_values: dict[GBRegion, np.ndarray],
    national: np.ndarray,
    weights: dict[GBRegion, float],
) -> np.ndarray:
    """rho_agg(t) = Sum_r w_r * X_{r}(t) - X_national(t), per period.

    INDEPENDENCE (R15 TAUTOLOGY guard): the weighted aggregate is recomputed from
    the region series, and compared to ``national`` — the W1_3 output held
    independently and passed in by the caller. It is NEVER re-derived from the
    region sum, so a broken field cannot make itself pass.
    """
    national = np.asarray(national, dtype=float)
    if national.ndim == 0:
        national = national.reshape(1)
    regions = list(region_values.keys())
    w = _weight_vector(weights, regions)              # FAIL-OPEN on bad weights
    stacked = _stack(region_values, regions)          # FAIL-OPEN on NaN/ragged
    if stacked.shape[1] != national.shape[0]:
        raise ValueError(
            f"region series has {stacked.shape[1]} periods, national has {national.shape[0]}"
        )
    if not np.all(np.isfinite(national)):
        raise ValueError("national signal contains non-finite values")
    aggregate = (w[:, None] * stacked).sum(axis=0)
    return aggregate - national


def check_aggregation_consistency(
    region_values: dict[GBRegion, np.ndarray] | None,
    national: np.ndarray | None,
    weights: dict[GBRegion, float] | None,
    tol: float = TOL_AGG,
) -> ReconciliationResult:
    """Evaluate invariant I1. Returns a ReconciliationResult; a failed check is a
    FIRED failure (``passed=False``), never a silent skip.

    R15 killer-pattern guards, all closed here:
      * FAIL-SILENT — if the national signal, the weights, or the region values are
        UNAVAILABLE (None), the check returns FAILED (an unavailable check is a
        failed check), never green-by-absence.
      * FAIL-OPEN — an empty region set, a missing/NaN/non-positive weight, or a
        NaN region value raises inside reconciliation_residual and is reported as a
        FAILED check here, never a trivial pass.
      * TAUTOLOGY — see reconciliation_residual: national is held independently.
    """
    # FAIL-SILENT guard: unavailable inputs => FAILED, not green.
    if region_values is None:
        return ReconciliationResult(False, float("inf"), tol, "region_values unavailable")
    if national is None:
        return ReconciliationResult(False, float("inf"), tol, "national signal unavailable")
    if weights is None:
        return ReconciliationResult(False, float("inf"), tol, "weights unavailable")
    try:
        residual = reconciliation_residual(region_values, national, weights)
    except (ValueError, KeyError, TypeError) as exc:
        # FAIL-OPEN guard: a degenerate field is a FAILED check, not a pass.
        return ReconciliationResult(False, float("inf"), tol, f"degenerate field: {exc}")
    max_abs = float(np.max(np.abs(residual)))
    passed = max_abs <= tol
    reason = "" if passed else f"reconciliation residual {max_abs:.3e} exceeds tol {tol:.1e}"
    return ReconciliationResult(passed, max_abs, tol, reason)


def assert_aggregation_consistency(
    region_values: dict[GBRegion, np.ndarray] | None,
    national: np.ndarray | None,
    weights: dict[GBRegion, float] | None,
    tol: float = TOL_AGG,
) -> None:
    """Raise ``AggregationConsistencyError`` if I1 does not hold. Use as a hard gate."""
    result = check_aggregation_consistency(region_values, national, weights, tol)
    if not result.passed:
        raise AggregationConsistencyError(result.reason or "aggregation consistency failed")


class AggregationConsistencyError(AssertionError):
    """Raised when the regional field fails to reconcile to the national signal."""


# ---------------------------------------------------------------------------
# Feasibility checks (§5) — independent of reconciliation. A field can reconcile
# in aggregate while an individual region is physically impossible.
# ---------------------------------------------------------------------------
# PLACEHOLDER climatological guards (see SIMPLIFICATIONS). Bounds are deliberately
# wide so they flag only genuinely impossible values, not tail events.
FEASIBILITY_TEMP_MAX_REGIONAL_SPREAD_C = 20.0   # a region 20C off national is impossible
FEASIBILITY_WIND_CEILING_MS = 45.0              # ~hurricane force; above = infeasible
FEASIBILITY_WIND_FLOOR_MS = 0.0                 # wind speed is non-negative


def check_temperature_feasibility(
    region_temps: dict[GBRegion, np.ndarray],
    national_temp: np.ndarray,
    max_spread_c: float = FEASIBILITY_TEMP_MAX_REGIONAL_SPREAD_C,
) -> ReconciliationResult:
    """A region may not deviate from national by more than a plausible spread."""
    national_temp = np.asarray(national_temp, dtype=float)
    regions = list(region_temps.keys())
    if not regions:
        return ReconciliationResult(False, float("inf"), max_spread_c, "no regions")
    stacked = _stack(region_temps, regions)
    max_dev = float(np.max(np.abs(stacked - national_temp[None, :])))
    passed = max_dev <= max_spread_c
    return ReconciliationResult(
        passed, max_dev, max_spread_c,
        "" if passed else f"regional temp deviation {max_dev:.1f}C exceeds {max_spread_c}C",
    )


def check_wind_feasibility(
    region_wind: dict[GBRegion, np.ndarray],
    floor_ms: float = FEASIBILITY_WIND_FLOOR_MS,
    ceiling_ms: float = FEASIBILITY_WIND_CEILING_MS,
) -> ReconciliationResult:
    """Regional wind must be non-negative and below a physical ceiling."""
    regions = list(region_wind.keys())
    if not regions:
        return ReconciliationResult(False, float("inf"), ceiling_ms, "no regions")
    stacked = _stack(region_wind, regions)
    lo, hi = float(stacked.min()), float(stacked.max())
    passed = lo >= floor_ms and hi <= ceiling_ms
    reason = "" if passed else f"wind out of [{floor_ms}, {ceiling_ms}] m/s: min={lo:.1f}, max={hi:.1f}"
    return ReconciliationResult(passed, hi, ceiling_ms, reason)


# ---------------------------------------------------------------------------
# Placeholder correlated draw — for end-to-end exercise ONLY (flagged).
# ---------------------------------------------------------------------------
def draw_placeholder_deviations(
    regions: list[GBRegion],
    n_periods: int,
    rng: np.random.Generator,
    sigma: float = 1.5,
) -> dict[GBRegion, np.ndarray]:
    """Draw raw (UN-projected) regional deviations from an ISOTROPIC placeholder
    covariance, purely to exercise the projection/invariant end-to-end.

    THIS IS A PLACEHOLDER (SIMPLIFICATIONS: W1_4_PLACEHOLDER_ISOTROPIC_COVARIANCE) —
    it does NOT reproduce the real distance-keyed spatial correlation. The real
    correlated draw is the existing weather_engine.py Cholesky path fed with a real
    per-region covariance. The projection and the invariant are covariance-agnostic,
    so this placeholder is sufficient to demonstrate reconciliation; it is NOT a
    fidelity claim about the spatial structure.
    """
    n = len(regions)
    z = rng.standard_normal((n, n_periods)) * sigma
    return {r: z[i] for i, r in enumerate(regions)}
