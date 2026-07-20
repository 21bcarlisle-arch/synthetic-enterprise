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

L1 NAMED SIMPLIFICATIONS (R10, registered not hidden):
  * PERFECT DELIVERY, TRIVIAL BASELINE -- metered delivery == instructed
    volume; no rebound / non-response / measured-baseline error. L2 adds
    stochastic portfolio delivery (its OWN named RNG substream, C-S2) and a
    baseline methodology with a true-vs-estimated gap.
  * ONE VENUE (BM-like). No availability/utilisation split, no Capacity
    Market, no DFS turn-down -- L2/L3.
  * SCALE-FREE UNITS -- `enrolled_mw` and `period_hours` are illustrative
    participation inputs, NOT sourced benchmarks. Every revenue figure is
    LINEAR in both, and the triad's normalised gap is invariant to them, so
    no un-sourced £/kW or MW figure can move the score. Any real £/kW/yr,
    availability price, or baseline-window figure remains a BENCHMARK
    REQUIRED (source: NESO/Elexon) and is not fabricated here -- which is
    why this atom may claim L1 ONLY, never L2+.
  * DETERMINISTIC -- L1 draws no RNG (perfect delivery). The named delivery
    substream arrives with L2 stochasticity.
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

    @property
    def total_true_revenue_gbp(self) -> float:
        return float(self.true_utilised_revenue.sum())

    @property
    def n_dispatch(self) -> int:
        return int(self.dispatch_mask.sum())


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
) -> FlexDispatchTruth:
    """SIM ground truth: dispatch enrolled flex on the TRUE (residual-driven)
    scarcity schedule and settle each event at the OBSERVED outturn price
    (perfect delivery, L1). Returns the truth theta the harness scores against.

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
    # Perfect delivery (L1): utilised MWh = enrolled_mw * hours in dispatch
    # periods, 0 elsewhere; paid at the observed outturn price.
    delivered_mwh = np.where(mask, enrolled_mw * period_hours, 0.0)
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
