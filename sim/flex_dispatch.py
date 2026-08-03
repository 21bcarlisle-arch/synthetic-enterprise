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
  * STACKING (L3 LANDED) -- `dispatch_and_settle_stacked` runs N CONCURRENT
    venues (a utilisation-paid BM-like venue + an availability-paid CM-like
    venue) against ONE physical portfolio, with the hard physics that the SAME
    MW CANNOT BE DELIVERED TWICE in a settlement period. Contention is
    resolved SIM-side by declared venue PRIORITY (`_allocate_by_priority`) and
    the conservation law is ENFORCED, not asserted in prose
    (`assert_mw_conservation`, called on every stacked truth). The company's
    belief about stacked revenue is formed on the far side of the wall and is
    ALLOWED to double-count (`company.market.flex_participation.
    form_stacked_belief`); the over-claim is what the harness scores.
  * ONE VENUE at L1/L2 (BM-like). `dispatch_and_settle` is untouched and stays
    byte-identical -- the stacked path is a separate entry point.
  * SCALE-FREE UNITS -- `enrolled_mw` and `period_hours` are illustrative
    participation inputs, NOT sourced benchmarks. Every revenue figure is
    LINEAR in both, and the triad's normalised gap is invariant to them, so
    no un-sourced £/kW or MW figure can move the score. The L2 mean delivery
    ratio and any real £/kW/yr / availability price remain a BENCHMARK
    REQUIRED (source: NESO/Elexon) -- the L2 STRUCTURE (stochastic delivery +
    baseline-error gap) is built here; a sourced ratio stays benchmark-gated.
  * NO INVENTED AVAILABILITY PRICE (L3, benchmark gate HONOURED IN CODE) --
    `VenueSpec.availability_price_gbp_per_mw_hour` has NO DEFAULT: an
    availability-basis venue with a missing/zero/non-finite price FAILS LOUD
    (`DegenerateFlexError`) rather than silently modelling a fabricated
    £/kW/yr. The real Capacity Market clearing price is still BENCHMARK
    REQUIRED (source: NESO / EMR Delivery Body auction results); the L3
    STRUCTURE (availability product + non-delivery clawback + contention) is
    built here and its HEADLINE gap is measured on physical DELIVERED MWh,
    which carries no £ figure at all, so no un-sourced price can move the
    score. The non-delivery clawback multiple defaults to 1.0 -- a structural
    identity ("you are not paid for availability you did not have"), not a
    magnitude; a real CM over-penalty (>1.0) is BENCHMARK REQUIRED.
  * DETERMINISTIC REPLAY (C-S2) -- delivery noise draws ONLY from the named
    `flex_delivery` substream; same seed -> byte-identical ratios, and the
    draw can never shift another subsystem's RNG.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Sequence, Tuple

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


# ===========================================================================
# L3 -- MULTI-VENUE STACKING (FRAME section 3 L3: "multiple concurrent venues
# with conflicting/overlapping calls and stacking rules")
#
# WHY THIS EXISTS (the real-world mechanism, not an accretion). A real DSR
# portfolio STACKS revenue: the same batteries/sites sit behind a BM-like
# utilisation product (paid per MWh actually delivered) AND an availability
# product (Capacity Market: paid GBP/MW held available, penalised for
# non-delivery during a stress event). Stacking is legitimate and is where the
# money is -- but it is bounded by one hard physical law:
#
#     THE SAME MW CANNOT BE DELIVERED TWICE IN THE SAME SETTLEMENT PERIOD.
#
# When two venues call in the same half-hour and the sum of what was offered
# exceeds the portfolio's physical capability, something gives. WHICH thing
# gives is WORLD TRUTH (dispatch physics + the party's own declared priority
# order), resolved here in the SIM by `_allocate_by_priority`, and the
# conservation law is ENFORCED by `assert_mw_conservation` on every stacked
# truth -- a law that only appears in a docstring is not a law.
#
# THE WALL. The company cannot see this allocation. It observes only its own
# per-venue dispatch instructions and settlement lines, and must form its own
# belief about stacked revenue -- including whether contention will bind. A
# naive stacker double-counts the same MW across venues, books phantom revenue,
# and eats a non-delivery clawback it did not forecast. That over-claim is a
# REAL failure mode of real aggregators, and the harness scores it
# (`background/flex_dispatch_triad.py::measure_l3`).
#
# R13/R12. Which venues exist, their call thresholds and their priority order
# are BASELINE structural world facts (or the party's own declared preference),
# decided BLIND to company P&L. Nothing here is tuned toward a gap number. The
# availability PRICE is a required caller input with no default (see the module
# header) so no fabricated GBP/kW/yr can enter, and the HEADLINE L3 gap is
# measured on physical delivered MWh, which is price-free.
#
# C-S2. Stacked portfolio-delivery stochasticity draws from its OWN named
# substream `W1_9_flex_stacked_delivery`, separate from the L2
# `W1_9_flex_delivery` stream, so adding the stacked path can never shift the
# L1/L2 draws (the 01:09Z shared-RNG law).
# C-S5 TIME-SCALE INVARIANCE. Nothing below assumes a half-hour. `period_hours`
# is the only time quantum, it enters every MW->MWh conversion linearly, and the
# allocation/conservation logic is per-record-row, so the same code runs on HH,
# hourly or daily rows. Registered named simplification (R10): the availability
# WINDOW is the whole record (a real CM agreement is a delivery YEAR with a
# defined obligation season) -- a season-shaped availability window is an
# additive refinement, not a reshape.
# ===========================================================================

_STACKED_DELIVERY_SUBSTREAM: str = "W1_9_flex_stacked_delivery"

# The availability venue's call is the EXTREME stress tail -- a Capacity Market
# Notice fires far more rarely than a BM acceptance. Top ~1% of residual. A
# BASELINE structural choice about the world (how often the system is in a
# stress event), NOT a curriculum dial and NOT tuned to any company outcome.
DEFAULT_AVAILABILITY_CALL_PERCENTILE: float = 99.0

# Absolute MW tolerance for the conservation law (float arithmetic only -- not a
# slack allowance). Deliberately tiny: a real over-allocation is O(MW).
_MW_CONSERVATION_TOL: float = 1e-9


class MwConservationError(ValueError):
    """The stacking physics was violated: more MW was delivered in a settlement
    period than the portfolio physically has. FAIL-LOUD -- a stacked truth that
    double-delivers would silently manufacture revenue out of nothing and every
    downstream gap would then be measured against a fiction."""


class FlexPaymentBasis(str, Enum):
    """WHAT a venue pays for -- the portable product distinction (payment
    FUNCTION, not a GB venue name; a second geography reuses these two).

    UTILISATION  -- paid per MWh actually DELIVERED against a call (BM/BOA,
                    DFS turn-down): no call, no money.
    AVAILABILITY -- paid per MW HELD AVAILABLE across the window whether or not
                    called (Capacity Market), and CLAWED BACK when called and
                    unable to deliver. This is the leg a naive stacker
                    double-counts.
    """

    UTILISATION = "utilisation"
    AVAILABILITY = "availability"


@dataclass(frozen=True)
class VenueSpec:
    """One flex venue the portfolio participates in concurrently.

    `priority` orders CONTENTION resolution: the lowest number is served first
    when the same MW is wanted by two venues in one period (a real party's
    declared dispatch preference / the stricter obligation first). `call_pct` is
    the residual-demand percentile at/above which THIS venue calls -- the
    world's need process for this product, SIM-internal.

    `availability_price_gbp_per_mw_hour` is REQUIRED (no default) for an
    AVAILABILITY venue and FORBIDDEN for a UTILISATION one: the benchmark gate
    enforced in code, so an availability product can never be modelled with a
    silently-defaulted (i.e. fabricated) GBP/kW figure. Fail-loud on
    missing/zero/negative/non-finite -- never fail-open to 0.
    """

    venue: FlexVenue
    basis: FlexPaymentBasis
    offered_mw: float
    priority: int
    call_pct: float = TRUE_SCARCITY_PERCENTILE
    availability_price_gbp_per_mw_hour: Optional[float] = None
    nondelivery_clawback_multiple: float = 1.0

    def __post_init__(self) -> None:
        import math

        if not (isinstance(self.offered_mw, (int, float))
                and math.isfinite(float(self.offered_mw))):
            raise DegenerateFlexError(f"VenueSpec {self.venue}: offered_mw must be finite")
        if self.offered_mw <= 0.0:
            raise DegenerateFlexError(
                f"VenueSpec {self.venue}: offered_mw must be > 0 (got {self.offered_mw})")
        if not (0.0 < float(self.call_pct) < 100.0):
            raise DegenerateFlexError(
                f"VenueSpec {self.venue}: call_pct must be in (0, 100), got {self.call_pct}")
        if not math.isfinite(float(self.nondelivery_clawback_multiple)) or \
                self.nondelivery_clawback_multiple < 0.0:
            raise DegenerateFlexError(
                f"VenueSpec {self.venue}: nondelivery_clawback_multiple must be finite >= 0")
        p = self.availability_price_gbp_per_mw_hour
        if self.basis is FlexPaymentBasis.AVAILABILITY:
            # BENCHMARK GATE, in code: no default, no zero, no NaN. An
            # availability product without a real price is not modelled at all.
            if p is None:
                raise DegenerateFlexError(
                    f"VenueSpec {self.venue}: an AVAILABILITY venue requires an explicit "
                    "availability_price_gbp_per_mw_hour -- there is NO default (a defaulted "
                    "price would be a fabricated GBP/kW figure). The real Capacity Market "
                    "clearing price is BENCHMARK REQUIRED (source: NESO / EMR Delivery Body "
                    "auction results); pass the sourced figure or do not model the venue.")
            if not math.isfinite(float(p)) or float(p) <= 0.0:
                raise DegenerateFlexError(
                    f"VenueSpec {self.venue}: availability price must be finite > 0, got {p!r}")
        elif p is not None:
            raise DegenerateFlexError(
                f"VenueSpec {self.venue}: a UTILISATION venue is paid per delivered MWh; "
                "carrying an availability price here would double-pay the same product")

    @property
    def key(self) -> str:
        """Stable string key (the seam enum's value) used for the per-venue maps
        crossing into the harness and (as an observable) on the company's own
        instruction/settlement lines."""
        return str(self.venue.value)


@dataclass(frozen=True)
class StackedFlexTruth:
    """SIM ground truth of ONE stacked, multi-venue flex run.

    Held ONLY by the SIM and the harness. The per-venue `allocated_mw` (who won
    the contention) and `shortfall_mw` (who was called and could not deliver)
    are the load-bearing hidden truths: a real party sees the CONSEQUENCE (its
    metered delivery, its clawback) but never the allocator."""

    dates: np.ndarray
    portfolio_mw: float
    period_hours: float
    venues: Tuple[VenueSpec, ...]
    outturn_price: np.ndarray
    residual_mw: np.ndarray                     # SIM-INTERNAL true system need
    true_delivery_ratio: np.ndarray             # portfolio-wide, per period
    call_mask: Dict[str, np.ndarray]            # per venue: the world called it
    allocated_mw: Dict[str, np.ndarray]         # per venue: MW the physics gave it
    shortfall_mw: Dict[str, np.ndarray]         # per venue: called-but-unallocated MW
    delivered_mwh: Dict[str, np.ndarray]        # per venue: realised delivery
    revenue_gbp: Dict[str, np.ndarray]          # per venue: net of clawback
    total_delivered_mwh: np.ndarray             # per period, across venues
    total_revenue_gbp: np.ndarray               # per period, across venues
    n_called_venues: np.ndarray                 # int per period
    binding_mask: np.ndarray                    # bool: contention actually BOUND

    @property
    def venue_keys(self) -> Tuple[str, ...]:
        return tuple(v.key for v in self.venues)

    @property
    def total_true_revenue_gbp(self) -> float:
        return float(self.total_revenue_gbp.sum())

    @property
    def total_true_delivered_mwh(self) -> float:
        return float(self.total_delivered_mwh.sum())

    @property
    def n_contended_periods(self) -> int:
        """Periods where MORE THAN ONE venue was called (overlap)."""
        return int((self.n_called_venues > 1).sum())

    @property
    def n_binding_periods(self) -> int:
        """Periods where the overlap actually EXCEEDED the portfolio, so the
        stacking law bit and someone was short. This -- not mere overlap -- is
        the truth a naive stacker gets wrong."""
        return int(self.binding_mask.sum())


def _stacked_delivery_rng(seed: int) -> "np.random.Generator":
    """The dedicated `flex_stacked_delivery` RNG substream (C-S2), distinct from
    the L2 `flex_delivery` stream so the stacked path can never shift it."""
    import hashlib

    h = hashlib.sha256(f"{_STACKED_DELIVERY_SUBSTREAM}:{int(seed)}".encode()).digest()
    return np.random.default_rng(int.from_bytes(h[:8], "big"))


def _allocate_by_priority(
    called: Sequence[bool], offered: Sequence[float], portfolio_mw: float,
) -> List[float]:
    """THE STACKING PHYSICS, SIM-internal: hand the portfolio's physical MW to
    the venues that called, in the given (already priority-sorted) order, until
    it runs out. A venue that was not called gets nothing; a venue that was
    called gets `min(what it offered, what is left)`.

    This is the whole of contention resolution and it is deliberately ONE
    function (SIMPLICITY GUARD) so it is the single mutation point the R15 test
    breaks to prove `assert_mw_conservation` can actually fire."""
    remaining = float(portfolio_mw)
    alloc: List[float] = []
    for is_called, mw in zip(called, offered):
        if not is_called:
            alloc.append(0.0)
            continue
        take = min(float(mw), remaining if remaining > 0.0 else 0.0)
        alloc.append(take)
        remaining -= take
    return alloc


def assert_mw_conservation(truth: "StackedFlexTruth",
                           *, tol: float = _MW_CONSERVATION_TOL) -> float:
    """ENFORCE the stacking law: in no settlement period may the venues, in
    total, be allocated more MW than the portfolio physically has. Returns the
    worst over-allocation (0.0 when the law holds); raises `MwConservationError`
    when it is broken.

    R15 discipline, all three killer patterns closed:
      * NOT FAIL-OPEN -- an empty venue set, an empty allocation series, or a
        non-positive portfolio raises rather than passing vacuously.
      * NOT NaN-BLIND -- non-finite allocations are rejected FIRST, before any
        comparison (a `NaN > cap` comparison is False, i.e. a silent pass).
      * NOT FAIL-SILENT -- a non-StackedFlexTruth or a truth missing its
        per-venue allocation map raises; an unavailable check is a FAILED check,
        never a pass.
    """
    if not isinstance(truth, StackedFlexTruth):
        raise MwConservationError(
            "assert_mw_conservation: not a StackedFlexTruth -- the conservation law "
            "cannot be evaluated, which is a FAILED check, not a pass")
    if not truth.venues:
        raise MwConservationError("assert_mw_conservation: no venues -- nothing to conserve")
    if not truth.allocated_mw:
        raise MwConservationError("assert_mw_conservation: allocation map absent")
    cap = float(truth.portfolio_mw)
    if not np.isfinite(cap) or cap <= 0.0:
        raise MwConservationError(
            f"assert_mw_conservation: portfolio_mw must be finite > 0, got {cap!r}")
    missing = [v.key for v in truth.venues if v.key not in truth.allocated_mw]
    if missing:
        raise MwConservationError(
            f"assert_mw_conservation: no allocation recorded for venues {missing}")
    stack = np.vstack([np.asarray(truth.allocated_mw[v.key], dtype=float) for v in truth.venues])
    if stack.size == 0:
        raise MwConservationError("assert_mw_conservation: empty allocation series")
    if not np.all(np.isfinite(stack)):
        raise MwConservationError(
            "assert_mw_conservation: non-finite allocation (NaN/inf) -- rejected before "
            "comparison, because a NaN would compare False against the cap and pass silently")
    if np.any(stack < -tol):
        raise MwConservationError("assert_mw_conservation: negative allocation")
    per_period = stack.sum(axis=0)
    worst = float(np.max(per_period - cap))
    if worst > tol:
        i = int(np.argmax(per_period))
        raise MwConservationError(
            f"assert_mw_conservation: THE SAME MW WAS DELIVERED TWICE -- period {i} "
            f"allocates {per_period[i]:.6f} MW against a {cap:.6f} MW portfolio "
            f"(over by {worst:.6f} MW). The stacking law is physics, not a preference.")
    return max(worst, 0.0)


def dispatch_and_settle_stacked(
    out: Optional[Dict[str, np.ndarray]] = None,
    *,
    venues: Sequence[VenueSpec],
    portfolio_mw: float,
    period_hours: float = DEFAULT_PERIOD_HOURS,
    delivery: Optional[DeliveryModel] = None,
) -> StackedFlexTruth:
    """SIM ground truth for a STACKED portfolio (L3). Each venue calls on its
    own residual-percentile need; where calls OVERLAP, the physical MW is
    allocated by declared priority and the loser is SHORT. Utilisation venues
    are paid on what they actually delivered at the observed outturn price;
    availability venues are paid on MW held available across the record and
    CLAWED BACK on the MW they were called for and could not deliver.

    `delivery=None` keeps delivery perfect (ratio 1.0) so the stacking law can
    be read on its own; a `DeliveryModel` adds the L2 portfolio stochasticity
    from the separate `flex_stacked_delivery` substream (C-S2).

    The conservation law is CHECKED before the truth is returned -- so a broken
    allocator cannot produce a `StackedFlexTruth` at all."""
    import math

    rec = _load_record(out)
    price = np.asarray(rec["derived_price"], dtype=float)
    residual = np.asarray(rec["residual_mw"], dtype=float)
    dates = np.asarray(rec["dates"])
    if price.size == 0 or price.shape != residual.shape:
        raise DegenerateFlexError(
            f"dispatch_and_settle_stacked: bad record shapes price={price.shape} "
            f"residual={residual.shape}")
    specs = tuple(venues)
    if not specs:
        raise DegenerateFlexError("dispatch_and_settle_stacked: no venues -- nothing to stack")
    keys = [v.key for v in specs]
    if len(set(keys)) != len(keys):
        raise DegenerateFlexError(
            f"dispatch_and_settle_stacked: duplicate venue keys {keys} -- one venue per "
            "market function per portfolio (a duplicate would silently double the offer)")
    if not (isinstance(portfolio_mw, (int, float)) and math.isfinite(float(portfolio_mw))) \
            or portfolio_mw <= 0.0:
        raise DegenerateFlexError(
            f"dispatch_and_settle_stacked: portfolio_mw must be finite > 0, got {portfolio_mw!r}")
    if not math.isfinite(float(period_hours)) or period_hours <= 0.0:
        raise DegenerateFlexError(
            f"dispatch_and_settle_stacked: period_hours must be finite > 0, got {period_hours!r}")

    # -- the world's per-venue NEED (SIM-internal: residual-driven) ----------
    call_mask = {v.key: true_scarcity_mask(residual, v.call_pct) for v in specs}
    any_call = np.zeros_like(price, dtype=bool)
    for m in call_mask.values():
        any_call |= m

    # -- portfolio-wide delivery stochasticity over the called periods ------
    ratio = np.ones_like(price)
    if delivery is not None:
        n = int(any_call.sum())
        if n:
            draws = _stacked_delivery_rng(delivery.seed).normal(
                delivery.mean_ratio, delivery.dispersion, size=n)
            ratio[any_call] = np.clip(draws, 0.0, 1.0)

    # -- CONTENTION: priority order, portfolio cap, per period --------------
    order = sorted(range(len(specs)), key=lambda i: (specs[i].priority, specs[i].key))
    alloc = {v.key: np.zeros_like(price) for v in specs}
    n_called = np.zeros(price.shape, dtype=int)
    binding = np.zeros_like(price, dtype=bool)
    for p in range(price.size):
        called = [bool(call_mask[specs[i].key][p]) for i in order]
        offers = [specs[i].offered_mw for i in order]
        n_called[p] = sum(called)
        wanted = sum(o for c, o in zip(called, offers) if c)
        binding[p] = wanted > portfolio_mw + _MW_CONSERVATION_TOL
        got = _allocate_by_priority(called, offers, portfolio_mw)
        for pos, i in enumerate(order):
            alloc[specs[i].key][p] = got[pos]

    # -- settlement per venue, by PRODUCT ------------------------------------
    shortfall: Dict[str, np.ndarray] = {}
    delivered: Dict[str, np.ndarray] = {}
    revenue: Dict[str, np.ndarray] = {}
    for v in specs:
        m = call_mask[v.key]
        a = alloc[v.key]
        shortfall[v.key] = np.where(m, v.offered_mw - a, 0.0)
        delivered[v.key] = a * period_hours * ratio
        if v.basis is FlexPaymentBasis.UTILISATION:
            revenue[v.key] = delivered[v.key] * price
        else:
            ap = float(v.availability_price_gbp_per_mw_hour)   # validated: not None, > 0
            paid = np.full_like(price, ap * v.offered_mw * period_hours)
            clawback = (float(v.nondelivery_clawback_multiple) * ap
                        * shortfall[v.key] * period_hours)
            revenue[v.key] = paid - clawback

    total_delivered = np.sum([delivered[k] for k in keys], axis=0)
    total_revenue = np.sum([revenue[k] for k in keys], axis=0)

    truth = StackedFlexTruth(
        dates=dates,
        portfolio_mw=float(portfolio_mw),
        period_hours=float(period_hours),
        venues=specs,
        outturn_price=price,
        residual_mw=residual,
        true_delivery_ratio=ratio,
        call_mask=call_mask,
        allocated_mw=alloc,
        shortfall_mw=shortfall,
        delivered_mwh=delivered,
        revenue_gbp=revenue,
        total_delivered_mwh=total_delivered,
        total_revenue_gbp=total_revenue,
        n_called_venues=n_called,
        binding_mask=binding,
    )
    # The law is ENFORCED, not documented: a broken allocator cannot ship a truth.
    assert_mw_conservation(truth)
    return truth


def emit_dispatch_instructions_stacked(
    truth: StackedFlexTruth,
    *,
    unit_id: str = "FLEX_UNIT_1",
    direction: FlexDirection = FlexDirection.TURN_DOWN,
) -> List[FlexDispatchWallResponse]:
    """The OBSERVABLE per-venue instruction feed: one instruction per venue per
    period it was CALLED. This is the feed a real party reads, and it is the
    ONLY way the company can observe that two venues wanted the same MW in the
    same window (`window_start` + `venue` are both on the instruction) -- it
    still cannot see who WON, only that it was called twice.

    NAMED SIMPLIFICATION (R10, seam-bounded): the seam's
    `FlexDispatchInstruction` carries a UTILISATION price only, so an
    AVAILABILITY-basis instruction (a Capacity Market Notice, which carries no
    GBP/MWh) is emitted with `cleared_price_gbp_per_mwh=0.0` -- the availability
    payment is CONTRACTUAL (the party's own agreement price, company-owned data
    it already possesses) and does not need to cross the wall. Carrying an
    availability price on the seam would be an ADDITIVE field on a gated path
    (`interface/`) -- registered as debt, deliberately not built here."""
    responses: List[FlexDispatchWallResponse] = []
    for v in truth.venues:
        idx = np.nonzero(truth.call_mask[v.key])[0]
        for i in idx:
            start = _base_date(truth.dates[i])
            end = start + dt.timedelta(hours=truth.period_hours)
            cleared = (float(truth.outturn_price[i])
                       if v.basis is FlexPaymentBasis.UTILISATION else 0.0)
            instr = FlexDispatchInstruction(
                instruction_id=f"BOA-{unit_id}-{v.key}-{start:%Y%m%d%H%M}",
                unit_id=unit_id,
                venue=v.venue,
                direction=direction,
                window_start=start,
                window_end=end,
                cleared_price_gbp_per_mwh=cleared,
            )
            responses.append(FlexDispatchWallResponse(
                correlation_id=f"flex-{unit_id}-{v.key}-{start:%Y%m%d%H%M}",
                status=WallStatus.OK,
                schema_version=SCHEMA_VERSION,
                observed_at=start,
                valid_time=start.date(),
                payload=instr,
            ))
    return responses


def emit_settlement_lines_stacked(
    truth: StackedFlexTruth,
    *,
    unit_id: str = "FLEX_UNIT_1",
    settlement_lag_days: int = _SETTLEMENT_LAG_DAYS,
) -> List[FlexSettlementWallResponse]:
    """The OBSERVABLE per-venue settlement feed -- a SEPARATE, LATER event than
    the instruction (C-S3). Carries the METERED delivery (which is where the
    company FEELS contention: it was called for its full offer and metered far
    less) and the utilisation payment. It does NOT carry the allocation, the
    priority order, the true delivery ratio, or the availability clawback --
    the company must infer its stacked position from consequences.

    Same seam-bounded simplification as the instruction feed: an availability
    venue's line carries `utilisation_price/payment = 0.0` because the product is
    not utilisation-paid."""
    responses: List[FlexSettlementWallResponse] = []
    for v in truth.venues:
        idx = np.nonzero(truth.call_mask[v.key])[0]
        for i in idx:
            start = _base_date(truth.dates[i])
            end = start + dt.timedelta(hours=truth.period_hours)
            met = float(truth.delivered_mwh[v.key][i])
            up = (float(truth.outturn_price[i])
                  if v.basis is FlexPaymentBasis.UTILISATION else 0.0)
            line = FlexSettlementLine(
                settlement_id=f"SETT-{unit_id}-{v.key}-{start:%Y%m%d%H%M}",
                unit_id=unit_id,
                venue=v.venue,
                window_start=start,
                window_end=end,
                metered_delivery_mwh=met,
                utilisation_price_gbp_per_mwh=up,
                utilisation_payment_gbp=met * up,
            )
            responses.append(FlexSettlementWallResponse(
                correlation_id=f"flex-{unit_id}-{v.key}-{start:%Y%m%d%H%M}",
                status=WallStatus.OK,
                schema_version=SCHEMA_VERSION,
                observed_at=start + dt.timedelta(days=settlement_lag_days),
                valid_time=start.date(),
                payload=line,
            ))
    return responses
