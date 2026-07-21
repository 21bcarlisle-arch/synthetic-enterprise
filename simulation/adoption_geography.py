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
from dataclasses import dataclass

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
