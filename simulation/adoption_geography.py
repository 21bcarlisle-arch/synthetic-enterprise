"""EV + heat-pump national adoption S-curves — W1_10 (L1).

This is the first-of-three levels of the adoption-geography subsystem framed in
``docs/design/W1_10_FRAME.md``. It sits *between* W1_4 (regional weather field)
and W1_5 (premise demand): the weather hierarchy (W1_3→W1_4→W1_5) treats EV /
heat-pump ownership as a *static* per-premise flag, whereas in reality these are
the two fastest-moving structural drivers of GB demand *shape and level*, both
growing on an S-curve through the 2016–2025 window and beyond.

Scope of THIS level (L1)
------------------------
For each technology ``k ∈ {ev, heat_pump}`` a **national logistic diffusion
curve** ``a_k(t)`` giving the national share of *eligible* premises adopted at
time ``t``, calibrated to published history and **monotone non-decreasing** (no
un-adoption). The regional field (L2) and the per-premise assignment + load
signature into W1_5 (L3) are NOT built here — see the maturity map / FRAME.

The calibration anchors (Historical Ground Truth, R13)
------------------------------------------------------
The anchor tables below are published-statistic estimates of GB household
penetration, ``data_regime = "historical"``, calibrated blind to company P&L
(R12/R13 — this is BASELINE-world fidelity, not a tuned output):

- **EV** — plug-in car ownership as a share of GB households, from DVLA/SMMT
  registration statistics (cumulative plug-in car parc over ~28M households).
- **heat_pump** — certified heat-pump installations as a share of GB homes, from
  MCS / DESNZ heat-pump installation statistics.

HONEST LIMITATION (R9, R10 simplification — registered, not faked): these anchor
values are order-of-magnitude published estimates fixed at the model's knowledge
reference date, entered without a live re-fetch (autonomous runs have no network).
The **independent VALIDATOR** the FRAME requires — a *different*, held-out
published sub-national source (DESNZ sub-national consumption, MCS regional
counts) checked against these curves — is the anti-marking-own-homework control
and is L3 work, deferred here. L1 builds the *mechanism* (logistic fit +
monotonicity invariant + named RNG substream), which is what is tested.

Epistemic wall
--------------
Adoption is genuinely COMPANY-KNOWABLE at the aggregate (published registration /
install statistics + the company's own book), so these national curves sit on the
*public* side of the wall. This module is SIM-side world *generation* and imports
no ``company.*`` / ``saas.*`` state. What the company must not read is the SIM's
per-premise ground-truth assignment (L3) for non-customers — that is where the
company infers, is allowed to be wrong, and the COUPLED_TRIAD gap is measured.

C-S2 (RNG substream + deterministic replay)
-------------------------------------------
The mean curve uses NO randomness (it is a historical fit). The only stochastic
element — a national timing *jitter* on the curve midpoint — draws exclusively
from a single named ``adoption_field`` substream, derived from a stable sha256 so
the same (base_seed) reproduces the same draw across processes and, because the
substream is independent, adding it can never shift any other subsystem's RNG
sequence (the 01:09Z shared-RNG incident precedent).
"""

from __future__ import annotations

import hashlib
import math
import random
from dataclasses import dataclass, field

import numpy as np

# Technology keys — generic so a third technology (battery / V2G) can be added
# with no engine change (portability constraint: keyed by technology, not
# GB-specific hardcoding in the logic).
TECHNOLOGIES: tuple[str, ...] = ("ev", "heat_pump")

# The named RNG substream for ALL adoption stochasticity (C-S2). One name only.
ADOPTION_SUBSTREAM = "adoption_field"

# data_regime marker for the anchor series (SIM/WORLD convention: real vs generated).
DATA_REGIME = "historical"

# ── Calibration anchors: GB household penetration by year (published estimates) ──
# See the module docstring for sources and the R9/R10 honesty note. Values are the
# adopted share of GB *households* (a proxy for eligible premises at L1); the
# eligible-premise refinement (off-gas-grid / off-street-parking) is an L2/L3
# covariate, not applied to the national curve.
_ADOPTION_ANCHORS: dict[str, dict[int, float]] = {
    # Plug-in car household penetration (DVLA/SMMT parc ÷ ~28M GB households).
    "ev": {
        2016: 0.003,
        2018: 0.006,
        2020: 0.014,
        2022: 0.035,
        2024: 0.060,
    },
    # Heat-pump household penetration (MCS/DESNZ cumulative installs ÷ GB homes).
    "heat_pump": {
        2016: 0.0020,
        2018: 0.0032,
        2020: 0.0050,
        2022: 0.0082,
        2024: 0.0130,
    },
}

# Long-run saturation ceilings (share of eligible premises that ultimately adopt).
# A modelling assumption, NOT a fit to P&L (R13): most premises could eventually
# run an EV; a larger fraction of homes are ill-suited to a heat pump (flats,
# space, heat-demand), so its ceiling is lower. Registered as an R10 calibration
# simplification — the L3 VALIDATOR against held-out sub-national data is what
# would move these, never company outcomes.
_SATURATION_CEILING: dict[str, float] = {
    "ev": 0.90,
    "heat_pump": 0.80,
}


@dataclass(frozen=True)
class AdoptionCurve:
    """A national logistic diffusion curve ``a(t) = L / (1 + exp(-r·(t − t0)))``.

    ``ceiling`` (L) is the long-run saturation share, ``rate`` (r > 0) the
    diffusion speed, ``midpoint`` (t0) the year of half-ceiling adoption. r > 0 is
    enforced at fit time, which is what makes the curve monotone non-decreasing
    by construction (A2).
    """

    technology: str
    ceiling: float
    rate: float
    midpoint: float
    data_regime: str = DATA_REGIME

    def share(self, year: float) -> float:
        """National adopted share at ``year`` — a value in ``[0, ceiling]``.

        Monotone non-decreasing in ``year`` because ``rate > 0`` (guaranteed by
        the fit). Extrapolates on the fitted curve beyond the calibration window
        (the FRAME's explicit intent), asymptoting to ``ceiling``.
        """
        return self.ceiling / (1.0 + math.exp(-self.rate * (year - self.midpoint)))


def _logit(x: float) -> float:
    return math.log(x / (1.0 - x))


def fit_logistic(anchors: dict[int, float], ceiling: float, technology: str) -> AdoptionCurve:
    """Fit a monotone logistic curve to ``{year: share}`` anchors at a fixed
    saturation ``ceiling`` by OLS on the logit ``log((a/L)/(1 − a/L)) = r·t − r·t0``.

    FAIL-CLOSED (R15): raises — never silently returns a degenerate/flat curve —
    on fewer than two anchors, a non-positive ceiling, an anchor at/above the
    ceiling (logit undefined), or a fitted ``rate ≤ 0`` (a flat or *decreasing*
    fit is a broken adoption curve, not a valid one). An empty or malformed
    calibration is a FAILED fit, not a pass.
    """
    if ceiling <= 0.0 or ceiling >= 1.0:
        raise ValueError(f"{technology}: saturation ceiling must be in (0, 1), got {ceiling}")
    if len(anchors) < 2:
        raise ValueError(f"{technology}: need >= 2 calibration anchors, got {len(anchors)}")

    xs = sorted(anchors)
    ys = []
    for yr in xs:
        share = anchors[yr]
        if not (0.0 < share < ceiling):
            raise ValueError(
                f"{technology}: anchor {yr}={share} must be in (0, ceiling={ceiling})"
            )
        ys.append(_logit(share / ceiling))

    n = len(xs)
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    sxx = sum((x - mean_x) ** 2 for x in xs)
    sxy = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    if sxx <= 0.0:
        raise ValueError(f"{technology}: degenerate anchor years (zero variance)")
    rate = sxy / sxx
    if rate <= 0.0:
        raise ValueError(
            f"{technology}: fitted diffusion rate {rate:.4g} <= 0 — not a monotone "
            "adoption curve (calibration is decreasing or flat)"
        )
    # intercept = mean_y - rate*mean_x = -rate*t0  =>  t0 = mean_x - mean_y/rate
    midpoint = mean_x - mean_y / rate
    return AdoptionCurve(technology=technology, ceiling=ceiling, rate=rate, midpoint=midpoint)


def national_curves() -> dict[str, AdoptionCurve]:
    """The fitted national adoption curve per technology (the L1 output)."""
    return {
        tech: fit_logistic(_ADOPTION_ANCHORS[tech], _SATURATION_CEILING[tech], tech)
        for tech in TECHNOLOGIES
    }


def national_adoption_share(technology: str, year: float) -> float:
    """National adopted share of eligible premises for ``technology`` at ``year``.

    FAIL-CLOSED (R15): an unknown technology raises rather than returning 0.0 (a
    silent zero would read as "nobody has adopted", a fail-open pass).
    """
    if technology not in TECHNOLOGIES:
        raise ValueError(f"unknown technology {technology!r}; known: {TECHNOLOGIES}")
    return national_curves()[technology].share(year)


def adoption_series(technology: str, years: list[int]) -> list[float]:
    """The national adoption share sampled over ``years`` (monotone by A2)."""
    if not years:
        raise ValueError("adoption_series requires a non-empty list of years")
    return [national_adoption_share(technology, y) for y in years]


# ── Invariant A2: monotone non-decreasing adoption (R15, mutation-testable) ──────
# Tolerance absorbs float noise only; a genuine decrement of any real magnitude
# must FIRE. A diagnostic band, not a target (R12).
MONOTONE_TOL = 1e-9


def is_monotone_nondecreasing(series: list[float], tol: float = MONOTONE_TOL) -> bool:
    """A2 as a *failable* predicate: True iff ``series`` never decreases by more
    than ``tol`` between consecutive points.

    R15 FAIL-CLOSED: an empty or single-point series raises (a monotonicity claim
    over nothing is a caller error, never a silently-passing True) — an
    unavailable check is a FAILED check. The predicate genuinely fires: inject a
    decrement in any period and it returns False (proven by the mutation test).
    """
    if len(series) < 2:
        raise ValueError("monotonicity requires at least two points")
    return all(b - a >= -tol for a, b in zip(series, series[1:]))


# ── C-S2: the single named adoption RNG substream + national timing jitter ──────


def _substream(base_seed: int, name: str = ADOPTION_SUBSTREAM) -> random.Random:
    """An independent RNG for the named ``adoption_field`` substream, derived from
    a STABLE sha256 of ``base_seed:name`` (not Python's per-process-salted
    ``hash()``) so the same ``base_seed`` reproduces the same stream across
    processes (C-S2). Because the name seeds an independent generator, wiring this
    substream can never consume from, or shift, any other subsystem's sequence.
    """
    digest = hashlib.sha256(f"{base_seed}:{name}".encode()).digest()
    return random.Random(int.from_bytes(digest[:8], "big"))


# Standard deviation (years) of the national adoption-timing jitter. Real diffusion
# timing is uncertain by a season or two, not decades — a modelling band (R12), not
# a P&L knob.
_TIMING_JITTER_SD_YEARS = 0.5


def jittered_curve(curve: AdoptionCurve, base_seed: int) -> AdoptionCurve:
    """Return ``curve`` with its midpoint shifted by a deterministic national
    timing jitter drawn from the ``adoption_field`` substream.

    The *mean* curve (``national_curves``) uses no randomness; this is the only
    stochastic element at L1, and it lives entirely in the one named substream.
    A shift in ``midpoint`` alone preserves ``rate > 0``, so the jittered curve is
    still monotone (A2 holds under jitter). Deterministic in ``base_seed`` (C-S2).
    """
    jitter = _substream(base_seed).gauss(0.0, _TIMING_JITTER_SD_YEARS)
    return AdoptionCurve(
        technology=curve.technology,
        ceiling=curve.ceiling,
        rate=curve.rate,
        midpoint=curve.midpoint + jitter,
        data_regime=curve.data_regime,
    )


# ════════════════════════════════════════════════════════════════════════════
# L2 — regional adoption field (the W1_4 analogue)
# ════════════════════════════════════════════════════════════════════════════
#
# The national curve a_k(t) says *how many* GB premises have adopted technology k
# by year t; it says nothing about *where*. Real adoption is strongly
# geographic: heat pumps go OFF THE GAS GRID first (rural Scotland, Wales, the
# South West lead; gas-served cities lag), while early EVs cluster in affluent
# suburban/commuter regions. A model with a spatially-uniform share MIS-SHAPES
# regional load growth — which is exactly the thing that reshapes the regional
# system peak the network is planned around (W1_4 → W1_5).
#
# CONSTRUCTION.  Each region r gets a share  a_{k,r}(t) = a_k(t) · m_{k,r}  where
# m_{k,r} is a time-invariant regional MULTIPLIER built from two ingredients:
#   1. a COVARIATE tilt — an observable regional characteristic (off-gas-grid
#      fraction for heat pumps, an affluence proxy for EVs), centred on its
#      demand-weighted mean so it neither adds nor removes national adoption;
#   2. a SPATIALLY-CORRELATED random tilt — a distance-keyed Gaussian field
#      (neighbouring regions covary) drawn via a Cholesky factor, exactly the
#      device W1_4's weather engine uses for correlated regional deviations.
#
# AGGREGATION CONSISTENCY (invariant A1, the structural heart of L2).  The
# multipliers are projected so the demand-weighted regional average is EXACTLY
# the national curve:
#         Σ_r w_r · m_{k,r} = 1      ⇒   Σ_r w_r · a_{k,r}(t) = a_k(t)   ∀ t
# enforced by a weighted-mean projection (m_r ← m_raw_r / Σ_s w_s m_raw_s) — a
# STRUCTURAL identity, not a fitted fudge (the same class of device W1_4 uses to
# make regional weather deviations sum back to the national series). Because the
# multiplier is time-invariant and non-negative and a_k(t) is monotone (A2 from
# L1), each regional series a_{k,r}(t) is monotone too — A2 is inherited by
# construction, no separate enforcement needed.
#
# EPISTEMIC WALL.  All of this is SIM-side WORLD generation. The regional
# characteristics (off-gas-grid fraction, affluence, household weights) are
# genuinely COMPANY-KNOWABLE at the aggregate — they are published regional
# statistics — so the L1/L2 *aggregates* sit on the public side of the wall. What
# the company must NOT read is the SIM's per-premise ground-truth asset
# assignment (L3); there the company infers regional rates from published stats +
# its own book and is allowed to be wrong (the COUPLED_TRIAD gap).
#
# HONEST LIMITATIONS (R9/R10 — registered, not faked):
#   - The regional characteristic tables are order-of-magnitude published
#     estimates fixed at the model's knowledge reference date (no live re-fetch;
#     autonomous runs have no network). The independent VALIDATOR the FRAME
#     requires — a *different*, held-out sub-national source (DESNZ sub-national
#     consumption, MCS regional install counts) checked against this field's
#     demand-weighted aggregate — is the anti-marking-own-homework control and is
#     L3 work, deferred here.
#   - The multiplier is TIME-INVARIANT: regions differ in adoption LEVEL but not
#     (yet) in adoption TIMING (leading/lagging S-curves). A genuinely
#     time-varying m_{k,r}(t) with regional lead/lag is an L3 refinement; the
#     linear-multiplier form is valid while a_k(t) sits well below its ceiling
#     (true across the whole 2016-2025 window and near future — EV national share
#     ≈6% vs a 0.90 ceiling, heat-pump ≈1.3% vs 0.80), so a_k·m_r never approaches
#     the ceiling in the modelled regime; far-horizon extrapolation where a region
#     would exceed the ceiling is registered as outside the L2-valid regime.

# ── The GB region partition (region_set). ───────────────────────────────────────
# Portability (PORTABILITY_DESIGN_CONSTRAINTS): the adoption process is keyed by a
# named ``region_set``, NOT hardcoded to "GB DNOs" in the logic — a second market
# supplies its own RegionSet behind the same interface. This default set is the 14
# GB GSP / DNO areas. Centroids are factual (approximate area centroids);
# household weights and regional characteristics are published-estimate proxies
# per the honesty note above (data_regime = historical).

REGIONAL_SUBSTREAM = "adoption_field:regional"


@dataclass(frozen=True)
class Region:
    """One member of a region_set.

    ``household_weight`` is the region's share of eligible GB premises (the
    ``w_r`` in the A1 aggregation identity; the set's weights sum to 1).
    ``off_gas_grid_fraction`` and ``affluence_index`` are the observable regional
    covariates that tilt heat-pump and EV adoption respectively; ``lat``/``lon``
    are the centroid used to build the distance-keyed spatial-correlation field.
    """

    region_id: str
    name: str
    lat: float
    lon: float
    household_weight: float
    off_gas_grid_fraction: float
    affluence_index: float
    data_regime: str = DATA_REGIME


# 14 GB GSP/DNO areas. Weights sum to 1.0 exactly (validated at build time).
_GB_REGIONS: tuple[Region, ...] = (
    Region("north_scotland", "North Scotland", 57.5, -4.2, 0.03, 0.45, 0.48),
    Region("south_scotland", "South Scotland", 55.8, -3.8, 0.05, 0.20, 0.50),
    Region("north_east_england", "North East England", 54.9, -1.6, 0.05, 0.08, 0.42),
    Region("north_west_england", "North West England", 53.5, -2.6, 0.10, 0.06, 0.47),
    Region("yorkshire", "Yorkshire", 53.8, -1.5, 0.08, 0.10, 0.46),
    Region("north_wales_mersey", "North Wales & Merseyside", 53.2, -3.0, 0.05, 0.18, 0.45),
    Region("south_wales", "South Wales", 51.6, -3.4, 0.05, 0.16, 0.44),
    Region("east_midlands", "East Midlands", 52.9, -1.1, 0.08, 0.12, 0.50),
    Region("west_midlands", "West Midlands", 52.5, -1.9, 0.09, 0.05, 0.48),
    Region("eastern_england", "Eastern England", 52.2, 0.5, 0.10, 0.18, 0.55),
    Region("london", "London", 51.5, -0.1, 0.13, 0.02, 0.62),
    Region("southern_england", "Southern England", 51.0, -1.3, 0.08, 0.15, 0.58),
    Region("south_east_england", "South East England", 51.2, 0.5, 0.06, 0.12, 0.60),
    Region("south_west_england", "South West England", 50.8, -3.5, 0.05, 0.30, 0.52),
)

# The covariate driving each technology's regional tilt, and the sensitivity band
# (R10 modelling assumptions — NOT fitted to company P&L). Heat-pump adoption is
# highest off the gas grid; EV adoption is earliest in more affluent regions.
_TILT_COVARIATE: dict[str, str] = {"heat_pump": "off_gas_grid_fraction", "ev": "affluence_index"}
_TILT_BETA: dict[str, float] = {"heat_pump": 1.5, "ev": 2.0}

# Spatial-correlation field: standard deviation of the correlated regional tilt
# and the distance length-scale (km) over which the correlation decays (a
# diffusion band, R12 — a diagnostic never a target).
_SPATIAL_TILT_SD = 0.08
_SPATIAL_LENGTH_SCALE_KM = 200.0
# Positivity floor on the raw multiplier before projection (a fail-CLOSED clamp,
# not a fudge: with the bands above raw multipliers stay ≈0.4–1.6, well clear of
# this floor; it only ever bites on a pathological covariate table).
_MULTIPLIER_FLOOR = 0.05


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in km between two (lat, lon) points."""
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h))


def _spatial_cholesky(regions: tuple[Region, ...]) -> np.ndarray:
    """Cholesky factor of the distance-keyed spatial covariance of the regional
    tilt: ``Σ[i,j] = sd² · exp(−dist_km(i,j) / length_scale)`` (neighbouring
    regions covary). A tiny diagonal jitter keeps the factorisation numerically
    stable — the same construction as ``weather_engine.fit_regional_cholesky``.
    """
    n = len(regions)
    cov = np.empty((n, n))
    var = _SPATIAL_TILT_SD ** 2
    for i in range(n):
        for j in range(n):
            d = _haversine_km(regions[i].lat, regions[i].lon, regions[j].lat, regions[j].lon)
            cov[i, j] = var * math.exp(-d / _SPATIAL_LENGTH_SCALE_KM)
    cov = cov + np.eye(n) * 1e-12
    return np.linalg.cholesky(cov)


def _regional_rng_seed(base_seed: int, technology: str) -> int:
    """Stable, per-technology integer seed for the regional spatial draw, derived
    from a sha256 (not Python's per-process-salted ``hash()``) so the same
    ``base_seed`` reproduces the same field across processes (C-S2). The
    ``:regional:<tech>`` namespacing makes the draw independent of L1's national
    timing jitter and of the other technology — a new draw here can never shift
    any other subsystem's RNG sequence.
    """
    digest = hashlib.sha256(f"{base_seed}:{REGIONAL_SUBSTREAM}:{technology}".encode()).digest()
    return int.from_bytes(digest[:8], "big")


def _validate_region_set(regions: tuple[Region, ...]) -> None:
    """FAIL-CLOSED (R15): a region_set that cannot support the A1 identity RAISES
    rather than silently degrading. Empty set, duplicate ids, a non-positive
    weight, or weights not summing to 1 are all FAILED inputs, never a pass.
    """
    if not regions:
        raise ValueError("region_set is empty — cannot build a regional field")
    ids = [r.region_id for r in regions]
    if len(set(ids)) != len(ids):
        raise ValueError(f"region_set has duplicate ids: {ids}")
    if any(r.household_weight <= 0.0 for r in regions):
        raise ValueError("every region needs a positive household_weight (w_r > 0)")
    total_w = sum(r.household_weight for r in regions)
    if abs(total_w - 1.0) > 1e-9:
        raise ValueError(f"household weights must sum to 1, got {total_w:.6g}")


@dataclass(frozen=True)
class RegionalAdoptionField:
    """A technology's regional adoption field: the national curve plus a
    time-invariant, A1-consistent per-region multiplier.

    ``share(region_id, year)`` gives ``a_{k,r}(year) = a_k(year) · m_{k,r}``. The
    demand-weighted mean of the regional shares equals the national curve exactly
    (A1), by construction of the multipliers.
    """

    technology: str
    curve: AdoptionCurve
    regions: tuple[Region, ...]
    multipliers: dict[str, float]  # region_id -> m_{k,r}
    weights: dict[str, float] = field(default_factory=dict)  # region_id -> w_r

    def share(self, region_id: str, year: float) -> float:
        """Regional adopted share ``a_{k,r}(year)``.

        FAIL-CLOSED (R15): an unknown region RAISES rather than returning 0.0 (a
        silent zero would read as "nobody in that region has adopted").
        """
        if region_id not in self.multipliers:
            raise ValueError(f"unknown region {region_id!r} for {self.technology}")
        return self.curve.share(year) * self.multipliers[region_id]

    def national_from_field(self, year: float) -> float:
        """The demand-weighted aggregate of the regional shares — used by the A1
        check. Equals ``curve.share(year)`` by construction (A1)."""
        return sum(self.weights[r] * self.share(r, year) for r in self.multipliers)


def build_regional_field(
    technology: str,
    base_seed: int,
    regions: tuple[Region, ...] = _GB_REGIONS,
    curve: AdoptionCurve | None = None,
) -> RegionalAdoptionField:
    """Build the A1-consistent regional adoption field for ``technology``.

    The multiplier is ``m_raw_r = 1 + β·(cov_r − w̄·cov) + spatial_tilt_r`` floored
    positive, then projected ``m_r = m_raw_r / Σ_s w_s m_raw_s`` so
    ``Σ_r w_r m_r = 1`` EXACTLY (invariant A1). Deterministic in ``base_seed``
    (C-S2). FAIL-CLOSED on an unknown technology or an invalid region_set.
    """
    if technology not in TECHNOLOGIES:
        raise ValueError(f"unknown technology {technology!r}; known: {TECHNOLOGIES}")
    _validate_region_set(regions)
    if curve is None:
        curve = national_curves()[technology]

    weights = np.array([r.household_weight for r in regions])
    cov_name = _TILT_COVARIATE[technology]
    cov = np.array([getattr(r, cov_name) for r in regions])
    beta = _TILT_BETA[technology]

    # Covariate tilt, centred on the DEMAND-WEIGHTED mean so it is mean-zero under
    # w_r (adds/removes no national adoption before projection).
    cov_centred = cov - float(np.dot(weights, cov))
    covariate_tilt = beta * cov_centred

    # Spatially-correlated random tilt (distance-keyed Cholesky field, C-S2).
    chol = _spatial_cholesky(regions)
    rng = np.random.default_rng(_regional_rng_seed(base_seed, technology))
    spatial_tilt = chol @ rng.standard_normal(len(regions))

    m_raw = np.maximum(1.0 + covariate_tilt + spatial_tilt, _MULTIPLIER_FLOOR)

    # Weighted-mean projection → Σ_r w_r m_r = 1 EXACTLY (A1). Denominator is a
    # convex combination of strictly-positive floored multipliers, so it is
    # ≥ _MULTIPLIER_FLOOR > 0 — the projection can never divide by zero.
    denom = float(np.dot(weights, m_raw))
    multipliers = {r.region_id: float(m_raw[i] / denom) for i, r in enumerate(regions)}
    weight_map = {r.region_id: r.household_weight for r in regions}
    return RegionalAdoptionField(
        technology=technology,
        curve=curve,
        regions=tuple(regions),
        multipliers=multipliers,
        weights=weight_map,
    )


def regional_fields(base_seed: int, regions: tuple[Region, ...] = _GB_REGIONS) -> dict[str, RegionalAdoptionField]:
    """The regional adoption field per technology (the L2 output)."""
    return {tech: build_regional_field(tech, base_seed, regions) for tech in TECHNOLOGIES}


# ── Invariant A1: regional → national aggregation consistency (R15) ─────────────
# TAUTOLOGY GUARD (R15): the check recomputes the national share INDEPENDENTLY
# from the fitted national curve (national_adoption_share) and compares it to the
# demand-weighted sum of the field's per-region shares — it does not read back the
# same stored number it is checking. A mutation that offsets one region's
# multiplier breaks Σ w_r m_r = 1 and the check FIRES.
A1_TOL = 1e-9


def aggregation_consistency_error(fieldObj: RegionalAdoptionField, year: float) -> float:
    """The A1 error at ``year``: ``|Σ_r w_r a_{k,r}(year) − a_k(year)|``.

    R15 FAIL-CLOSED: an empty field or a weight set that does not sum to 1 RAISES
    (an aggregation claim over nothing, or over an inconsistent weight vector, is
    a caller/data error — never a silently-passing 0.0). The independently-fitted
    national curve is the reference, not the field's own stored aggregate.
    """
    if not fieldObj.multipliers:
        raise ValueError("cannot check aggregation consistency of an empty field")
    total_w = sum(fieldObj.weights[r] for r in fieldObj.multipliers)
    if abs(total_w - 1.0) > 1e-9:
        raise ValueError(f"field weights must sum to 1 for the A1 check, got {total_w:.6g}")
    field_aggregate = sum(
        fieldObj.weights[r] * fieldObj.share(r, year) for r in fieldObj.multipliers
    )
    national = national_adoption_share(fieldObj.technology, year)
    return abs(field_aggregate - national)


def check_aggregation_consistency(fieldObj: RegionalAdoptionField, years: list[int], tol: float = A1_TOL) -> bool:
    """A1 as a *failable* predicate over ``years``: True iff every year's
    aggregation error is within ``tol``. FAIL-CLOSED on an empty year list."""
    if not years:
        raise ValueError("A1 check requires a non-empty list of years")
    return all(aggregation_consistency_error(fieldObj, y) <= tol for y in years)


def regional_series(fieldObj: RegionalAdoptionField, region_id: str, years: list[int]) -> list[float]:
    """The regional adoption share ``a_{k,r}`` sampled over ``years`` (monotone by
    A2, inherited from the national curve × a non-negative constant multiplier)."""
    if not years:
        raise ValueError("regional_series requires a non-empty list of years")
    return [fieldObj.share(region_id, y) for y in years]
