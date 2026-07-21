"""W1_9_dsr_flex_markets (L1) -- the SIM-SIDE ground truth of the DSR /
flexibility coupled triad, layered on the W1_6 physics price signal.

WHAT THIS IS (L1, per docs/design/frame/W1_9_dsr_flex_markets_FRAME.md §3).
A real flex market pays a party to shed/shift demand when the SYSTEM is
tight. The SIM holds the TRUE system need: residual demand (load thermal
plant must serve = demand - wind - solar), computed by the W1_6 chain
(`sim.weather_price_chain.derive_price_on_record` -> `residual_mw`). The
TRUE scarcity events are the tightest-residual periods -- the genuine
Dunkelflaute corner where a real NESO dispatches flexibility. During a true
scarcity event the enrolled flex is dispatched (L1: perfect delivery,
trivial baseline) and paid utilisation at the OBSERVED outturn price (the
chain's derived price IS the published SSP a supplier bids against -- no
fabricated £/MWh).

THE WALL (CLAUDE.md Architectural Laws -- LOAD-BEARING). The TRUE dispatch
schedule is driven by residual demand, which is SIM-INTERNAL. Nothing in
`company/` may read it. What crosses the seam
(`interface/contracts/flex_observable_seam.py`) is OBSERVABLES ONLY: the
dispatch instruction (WHEN called + the cleared price) and the settlement
line (metered delivery + utilisation payment). The company must INFER
system stress from the price it can see; it never reads residual. The
belief-vs-truth GAP is measured by `background/flex_dispatch_triad.py` (the
HARNESS, the only layer holding both sides). This module imports nothing
from `company/`/`saas/`.

WHY THE GAP IS REAL, NOT A TAUTOLOGY (R15 independence). The truth here
dispatches on RESIDUAL DEMAND (a convex composed physics quantity). The
company's belief (far side of the wall) dispatches on PRICE percentile (an
observables-only proxy). Residual drives price through the merit order but
is NOT identical to it (gas price also moves price; the merit order is
convex, so equal residuals can clear at very different prices). So the two
dispatch sets genuinely differ -- the gap is a real form-inadequacy
measurement, not a leak. If the belief recovered the true schedule exactly
the observables would have leaked residual (a wall violation, not a
triumph).

LEVEL STATE (R10, registered not hidden):
  * DELIVERY (L2 LANDED) -- `delivery=None` keeps L1 PERFECT delivery
    byte-identical; a `DeliveryModel` turns on L2 STOCHASTIC portfolio
    delivery (rebound / non-response) drawn from the named `flex_delivery`
    RNG substream (C-S2). The true per-event delivery ratio is SIM-INTERNAL;
    the company forecasts against its own learned/observed estimate through
    the wall (`company.market.flex_participation.form_participation_belief_l2`)
    and the baseline-vs-delivery gap is scored by the harness.
  * ONE VENUE (BM-like). No availability/utilisation split, no Capacity
    Market, no DFS turn-down -- L2 second-venue + L3.
  * SCALE-FREE UNITS -- `enrolled_mw` and `period_hours` are illustrative
    participation inputs, NOT sourced benchmarks. Every revenue figure is
    LINEAR in both, and the triad's normalised gap is invariant to them, so
    no un-sourced £/kW or MW figure can move the score. The L2 mean delivery
    ratio and any real £/kW/yr / availability price remain a BENCHMARK
    REQUIRED (source: NESO/Elexon) -- the L2 STRUCTURE (stochastic delivery +
    baseline-error gap) is built here; a sourced ratio + the CM availability
    venue stay benchmark/level-gated.
  * DETERMINISTIC REPLAY (C-S2) -- delivery noise draws ONLY from the named
    `flex_delivery` substream; same seed -> byte-identical ratios, and the
    draw can never shift another subsystem's RNG.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import Dict, List, Optional

import numpy as np

from interface.contracts.flex_observable_seam import (
    FlexDirection,
    FlexDispatchInstruction,
    FlexDispatchWallResponse,
    FlexSettlementLine,
    FlexSettlementWallResponse,
    FlexVenue,
    SCHEMA_VERSION,
)
from interface.contracts.wall_envelope import WallStatus

# The true-scarcity threshold: residual demand at/above this percentile is a
# genuine system-tight period a real NESO would dispatch flex against. A
# BASELINE (R13) structural choice about the world's need process (how often
# the system is tight), NOT a curriculum difficulty dial and NOT tuned to any
# company outcome. Top ~5% of residual = the tight tail.
TRUE_SCARCITY_PERCENTILE: float = 95.0

# Illustrative participation units (see the L1 simplifications above): the
# normalised triad gap is invariant to both, so these are not benchmarks.
DEFAULT_ENROLLED_MW: float = 1.0
DEFAULT_PERIOD_HOURS: float = 1.0

# Settlement lands AFTER dispatch (C-S3): a nominal lag so the two events are
# separable in time (real Elexon settlement runs days after the BOA). L1 uses
# a fixed nominal lag; the value is not a benchmark, only an ordering.
_SETTLEMENT_LAG_DAYS: int = 16

# --- L2: stochastic portfolio delivery (W1_9 FRAME §3 L2) --------------------
# A real aggregated flex portfolio does NOT deliver 100% of its instructed
# volume: rebound (demand snaps back), customer non-response, and metering
# imperfection mean the realised reduction is a FRACTION of what was called.
# The SIM holds the TRUE per-event delivery ratio; the company cannot see it
# ex-ante and forecasts against its own learned/observed estimate (the L2 gap).
#
# R13/R12: mean and dispersion are BASELINE structural portfolio-physics -- how
# reliably demand responds to a call -- decided BLIND to company P&L, never
# tuned to a target gap. The specific numeric mean is a BENCHMARK REQUIRED
# (source: NESO DFS delivery reports / Elexon BM performance) and is
# ILLUSTRATIVE until sourced; the normalised triad gap is invariant to its
# exact level, sensitive only to the FACT that delivery < instruction. So the
# stochastic-delivery MECHANISM is L2, while the calibrated ratio stays a
# benchmark gate (this atom claims the L2 STRUCTURE, not a sourced figure).
DEFAULT_MEAN_DELIVERY_RATIO: float = 0.85
DEFAULT_DELIVERY_DISPERSION: float = 0.10

# C-S2: the flex portfolio-delivery stochasticity draws from its OWN named,
# seeded RNG substream, so adding delivery noise here can NEVER shift any other
# subsystem's draws (the 01:09Z shared-RNG incident law). Deterministic replay:
# same seed -> byte-identical ratios.
_DELIVERY_SUBSTREAM: str = "W1_9_flex_delivery"


@dataclass(frozen=True)
class DeliveryModel:
    """Parameters of the SIM-side stochastic portfolio delivery (L2). `None`
    passed to `dispatch_and_settle` keeps L1 perfect delivery byte-identical."""

    mean_ratio: float = DEFAULT_MEAN_DELIVERY_RATIO
    dispersion: float = DEFAULT_DELIVERY_DISPERSION
    seed: int = 0


def _delivery_rng(seed: int) -> "np.random.Generator":
    """The dedicated `flex_delivery` RNG substream (C-S2). Seed is a stable
    sha256 of the substream name + caller seed, so the stream is reproducible
    across processes and independent of every other subsystem's draws."""
    import hashlib

    h = hashlib.sha256(f"{_DELIVERY_SUBSTREAM}:{int(seed)}".encode()).digest()
    return np.random.default_rng(int.from_bytes(h[:8], "big"))


class DegenerateFlexError(ValueError):
    """FAIL-LOUD: a dispatch asked for on empty/degenerate input raises rather
    than returning silent zeros that would read as a passing (revenue-free)
    flex book."""


@dataclass(frozen=True)
class FlexDispatchTruth:
    """The SIM ground truth of one flex participation run over a record. Held
    ONLY by the SIM and the harness -- never crosses the seam.

    `true_utilised_revenue` is the per-period revenue vector theta the harness
    scores the company's belief against; `dispatch_mask` marks the true
    scarcity periods (residual-driven)."""

    dates: np.ndarray
    true_utilised_revenue: np.ndarray   # per-period, GBP (0 outside dispatch)
    dispatch_mask: np.ndarray           # bool, per-period true scarcity
    outturn_price: np.ndarray           # observed SSP-equivalent, GBP/MWh
    residual_mw: np.ndarray             # SIM-INTERNAL true system need
    enrolled_mw: float
    period_hours: float
    scarcity_percentile: float
    # L2: the TRUE per-event delivery ratio (SIM-INTERNAL -- the company never
    # sees it) and the derived true delivered MWh + true counterfactual
    # baseline. For L1 (delivery=None) the ratio is all-ones so the truth is
    # byte-identical to the perfect-delivery case.
    true_delivery_ratio: np.ndarray = None      # type: ignore[assignment]
    true_delivered_mwh: np.ndarray = None       # type: ignore[assignment]
    true_baseline_mwh: np.ndarray = None         # type: ignore[assignment]

    @property
    def total_true_revenue_gbp(self) -> float:
        return float(self.true_utilised_revenue.sum())

    @property
    def n_dispatch(self) -> int:
        return int(self.dispatch_mask.sum())

    @property
    def mean_delivery_ratio(self) -> float:
        """Mean TRUE delivery ratio over the dispatched periods (SIM-internal;
        the harness may read it, the company may not)."""
        if self.true_delivery_ratio is None or self.n_dispatch == 0:
            return 1.0
        return float(self.true_delivery_ratio[self.dispatch_mask].mean())


def _load_record(out: Optional[Dict[str, np.ndarray]]) -> Dict[str, np.ndarray]:
    if out is not None:
        return out
    from sim.weather_price_chain import derive_price_on_record
    return derive_price_on_record()


def true_scarcity_mask(residual_mw, percentile: float = TRUE_SCARCITY_PERCENTILE) -> np.ndarray:
    """The TRUE system-need dispatch schedule: periods whose residual demand
    is at/above `percentile` of the residual distribution -- the tight tail a
    real NESO dispatches flex against. Residual is SIM-INTERNAL; this function
    is SIM-side only and its output never crosses the seam."""
    residual = np.asarray(residual_mw, dtype=float)
    if residual.size == 0:
        raise DegenerateFlexError("true_scarcity_mask: empty residual series")
    thr = float(np.percentile(residual, percentile))
    return residual >= thr


def dispatch_and_settle(
    out: Optional[Dict[str, np.ndarray]] = None,
    *,
    enrolled_mw: float = DEFAULT_ENROLLED_MW,
    period_hours: float = DEFAULT_PERIOD_HOURS,
    scarcity_percentile: float = TRUE_SCARCITY_PERCENTILE,
    delivery: Optional[DeliveryModel] = None,
) -> FlexDispatchTruth:
    """SIM ground truth: dispatch enrolled flex on the TRUE (residual-driven)
    scarcity schedule and settle each event at the OBSERVED outturn price.
    Returns the truth theta the harness scores against.

    `delivery` is None for L1 (PERFECT delivery -- byte-identical to the
    original path) or a `DeliveryModel` for L2 STOCHASTIC portfolio delivery:
    each dispatched event realises only a fraction of its instructed volume
    (rebound / non-response), drawn from the named `flex_delivery` RNG
    substream (C-S2). The delivered fraction is SIM-INTERNAL truth -- the
    company forecasts against its own learned estimate through the wall.

    Reuses the W1_6 chain's derived-price record: `derived_price` is the
    observed SSP (utilisation price a supplier bids against); `residual_mw` is
    the SIM-internal true system need driving the dispatch. `out` may be
    injected (a small synthetic record) for fast, deterministic tests."""
    rec = _load_record(out)
    price = np.asarray(rec["derived_price"], dtype=float)
    residual = np.asarray(rec["residual_mw"], dtype=float)
    dates = np.asarray(rec["dates"])
    if price.size == 0 or price.shape != residual.shape:
        raise DegenerateFlexError(
            f"dispatch_and_settle: bad record shapes price={price.shape} residual={residual.shape}")

    mask = true_scarcity_mask(residual, scarcity_percentile)

    # Per-event delivery ratio: 1.0 everywhere for L1 (perfect delivery), or a
    # clipped-normal draw in [0, 1] over the DISPATCHED periods for L2. Drawing
    # only over the dispatched periods (n = mask.sum()) keeps the substream
    # consumption a pure function of the dispatch schedule (deterministic
    # replay, C-S2).
    ratio = np.ones_like(price)
    if delivery is not None:
        n = int(mask.sum())
        if n:
            draws = _delivery_rng(delivery.seed).normal(
                delivery.mean_ratio, delivery.dispersion, size=n)
            ratio[mask] = np.clip(draws, 0.0, 1.0)

    # The counterfactual BASELINE (what the unit would have consumed absent the
    # call) and the TRUE delivered reduction = baseline * ratio. Utilisation is
    # paid on the true reduction at the observed price. For L1 ratio==1 so
    # true_delivered == baseline in-dispatch and revenue matches the old path.
    baseline_mwh = np.where(mask, enrolled_mw * period_hours, 0.0)
    delivered_mwh = baseline_mwh * ratio
    revenue = delivered_mwh * price
    return FlexDispatchTruth(
        dates=dates,
        true_utilised_revenue=revenue,
        dispatch_mask=mask,
        outturn_price=price,
        residual_mw=residual,
        enrolled_mw=enrolled_mw,
        period_hours=period_hours,
        scarcity_percentile=scarcity_percentile,
        true_delivery_ratio=ratio,
        true_delivered_mwh=delivered_mwh,
        true_baseline_mwh=baseline_mwh,
    )


# ---------------------------------------------------------------------------
# Seam emission -- OBSERVABLES ONLY cross here (C-S3: dispatch and settlement
# are SEPARATE WallResponse events at different observed_at times).
# ---------------------------------------------------------------------------

def _base_date(d) -> dt.datetime:
    if isinstance(d, dt.datetime):
        return d
    if isinstance(d, dt.date):
        return dt.datetime(d.year, d.month, d.day)
    s = str(d)
    return dt.datetime.strptime(s[:10], "%Y-%m-%d")


def emit_dispatch_instructions(
    truth: FlexDispatchTruth,
    *,
    unit_id: str = "FLEX_UNIT_1",
    venue: FlexVenue = FlexVenue.BALANCING_MECHANISM,
    direction: FlexDirection = FlexDirection.TURN_DOWN,
) -> List[FlexDispatchWallResponse]:
    """Build the OBSERVABLE dispatch instructions for each true scarcity
    period -- WHEN the unit was called and the cleared (observed outturn)
    price. Carries NO residual / true need: the company sees the call and the
    price, never why it was called."""
    responses: List[FlexDispatchWallResponse] = []
    idx = np.nonzero(truth.dispatch_mask)[0]
    for i in idx:
        start = _base_date(truth.dates[i])
        end = start + dt.timedelta(hours=truth.period_hours)
        instr = FlexDispatchInstruction(
            instruction_id=f"BOA-{unit_id}-{start:%Y%m%d}",
            unit_id=unit_id,
            venue=venue,
            direction=direction,
            window_start=start,
            window_end=end,
            cleared_price_gbp_per_mwh=float(truth.outturn_price[i]),
        )
        responses.append(FlexDispatchWallResponse(
            correlation_id=f"flex-{unit_id}-{start:%Y%m%d}",
            status=WallStatus.OK,
            schema_version=SCHEMA_VERSION,
            observed_at=start,                      # instruction known in-day
            valid_time=start.date(),
            payload=instr,
        ))
    return responses


def emit_settlement_lines(
    truth: FlexDispatchTruth,
    *,
    unit_id: str = "FLEX_UNIT_1",
    venue: FlexVenue = FlexVenue.BALANCING_MECHANISM,
    settlement_lag_days: int = _SETTLEMENT_LAG_DAYS,
) -> List[FlexSettlementWallResponse]:
    """Build the OBSERVABLE settlement lines -- a SEPARATE, LATER event than
    the dispatch instruction (C-S3: `observed_at` is dispatch day +
    `settlement_lag_days`, matched to the instruction only by
    `correlation_id`). Carries metered delivery + utilisation payment, never
    the true baseline (L1: baseline trivial, delivery perfect)."""
    responses: List[FlexSettlementWallResponse] = []
    idx = np.nonzero(truth.dispatch_mask)[0]
    for i in idx:
        start = _base_date(truth.dates[i])
        end = start + dt.timedelta(hours=truth.period_hours)
        # OBSERVABLE metered delivery = the TRUE delivered reduction (L2:
        # stochastic; L1: full enrolled volume). The company sees this metered
        # figure on its statement -- it does NOT see the true baseline or the
        # true ratio that produced it.
        if truth.true_delivered_mwh is not None:
            delivered_mwh = float(truth.true_delivered_mwh[i])
        else:
            delivered_mwh = truth.enrolled_mw * truth.period_hours
        price = float(truth.outturn_price[i])
        line = FlexSettlementLine(
            settlement_id=f"SETT-{unit_id}-{start:%Y%m%d}",
            unit_id=unit_id,
            venue=venue,
            window_start=start,
            window_end=end,
            metered_delivery_mwh=float(delivered_mwh),
            utilisation_price_gbp_per_mwh=price,
            utilisation_payment_gbp=float(delivered_mwh * price),
        )
        responses.append(FlexSettlementWallResponse(
            correlation_id=f"flex-{unit_id}-{start:%Y%m%d}",
            status=WallStatus.OK,
            schema_version=SCHEMA_VERSION,
            observed_at=start + dt.timedelta(days=settlement_lag_days),
            valid_time=start.date(),
            payload=line,
        ))
    return responses
