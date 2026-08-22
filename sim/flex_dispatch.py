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
from dataclasses import dataclass, field
from dataclasses import fields as dataclass_fields
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

from interface.contracts.flex_observable_seam import (
    ENROLMENT_REFUSAL_CODES,
    FORBIDDEN_TRUTH_FIELDS,
    OBSERVABLE_PAYLOAD_FIELDS,
    OBSERVABLE_RESPONSE_PAYLOAD_TYPES,
    REQUEST_PAYLOAD_FIELDS,
    SCHEMA_VERSION,
    FlexDirection,
    FlexDispatchInstruction,
    FlexDispatchWallResponse,
    FlexEnrolment,
    FlexEnrolmentOutcome,
    FlexEnrolmentOutcomeWallResponse,
    FlexSettlementLine,
    FlexSettlementWallResponse,
    FlexVenue,
)
from interface.contracts.wall_envelope import ErrorDetail, WallRequest, WallResponse, WallStatus

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


# ---------------------------------------------------------------------------
# THE WIRE -- this counterparty's OWN codec for the flex seam's RESPONSE leg
# (EP6 pass 22).
#
# WHY IT IS HERE AND NOT IMPORTED. The company owns `company.interfaces.
# wall_protocol` and calls it; `sim/**` may not import `company.*`, so a real
# counterparty's only lawful move is to read the PUBLISHED contract and build
# the bytes itself. That asymmetry is the wall's, not a shortcut: two codecs
# written independently against one schema is what makes the round trip
# evidence rather than a tautology. If the two ever disagree the messages stop
# crossing, which is the correct outcome and the whole reason they are
# separate code (`simulation/conversation_response.py` does the same, for the
# same reason).
#
# ABSENCE IS NEVER AGREEMENT: every key of the declared response form is
# written including its nulls, `schema_version` comes from the CONTRACT's own
# constant and never from a writer's default, and a payload type outside the
# seam's `OBSERVABLE_RESPONSE_PAYLOAD_TYPES` is refused rather than serialised
# generically -- a codec that can serialise anything is a codec that can leak
# anything.
#
# ONLY THE RESPONSE LEG. `FlexEnrolmentWallRequest` is DORMANT: nothing in the
# census trees constructs a `FlexEnrolment`, so the contract describes a
# message this build does not yet exchange. Wiring it would move no crossing
# onto a wire and `tools.wall_channel_census` is built to say so.
# ---------------------------------------------------------------------------

#: The observable payload types this seam is permitted to put on a wire, keyed
#: by tag. Read from the CONTRACT's own tuple, so a future payload type is
#: encodable the day it is declared observable and not a day before.
_ENCODABLE_RESPONSE_PAYLOAD_TYPES = {t.__name__: t for t in OBSERVABLE_RESPONSE_PAYLOAD_TYPES}


class SeamCodecError(ValueError):
    """This seam refused to put a value on the wire. Deliberately NOT
    `WallProtocolError`: that type is the COMPANY's, and a counterparty does
    not raise the receiver's exceptions -- nor may it import them."""


def _encode_scalar(value: Any, field: str) -> Any:
    """Encode one payload field. Refuses an unhandled type rather than
    coercing -- `str(value)` here is how a platform silently ships an object's
    repr and the receiver silently accepts a string."""
    if value is None:
        return None
    if isinstance(value, Enum):
        return value.value
    # bool is an int subclass; a True metered delivery is a malformed field,
    # not a plausible, actionable 1.
    if isinstance(value, bool):
        raise SeamCodecError(f"{field}: bool is not a flex payload field type")
    if isinstance(value, dt.datetime):
        return value.isoformat()
    if isinstance(value, (int, float, str)):
        return value
    raise SeamCodecError(
        f"{field}: {type(value).__name__} has no defined wire form on this seam"
    )


def encode_observable_payload(payload: Any) -> dict:
    """Put one observable flex payload on the wire, TAGGED with its type.

    TAGGED because this seam genuinely carries two response payload types --
    a `FlexDispatchInstruction` and a `FlexSettlementLine` arrive as SEPARATE
    responses at different `observed_at` times (C-S3) and share four field
    names. `WallResponse.payload` is opaque to the envelope codec, so a
    receiver that guessed the type from the field set would mis-route them.
    The tag set is read from the contract's own tuple, so it grows with it.

    THE WALL, AT PAYLOAD DEPTH, AND IT IS THE CLOSED SET THAT CARRIES IT.
    A payload is refused HERE, at the point of emission, not left to the
    receiver, if it declares ANY field the contract has not declared
    observable in `OBSERVABLE_PAYLOAD_FIELDS`. That is the R10 form of this
    check: the CLASS "a field nobody has certified a real flex party could
    know" fails, so a future L2 field addition is refused because it was
    never declared, not because someone predicted its name.

    `FORBIDDEN_TRUTH_FIELDS` is checked too and is a SECOND belt, not the
    control. It was the control until 2026-08-20 and it was fail-open by
    construction: measured against this module's own `FlexDispatchTruth`, it
    named 2 of 11 truth fields, so `true_delivered_mwh` -- the exact leak the
    old docstring here claimed was refused as a class -- encoded onto the
    wire. A denylist answers "did we think of this name"; only the closed set
    answers "is this observable". It is retained because it still fires on
    the one case the closed set cannot see: a truth field added to the
    dataclass and declared observable in the same edit.
    """
    payload_type = type(payload)
    if payload_type.__name__ not in _ENCODABLE_RESPONSE_PAYLOAD_TYPES or (
        _ENCODABLE_RESPONSE_PAYLOAD_TYPES[payload_type.__name__] is not payload_type
    ):
        raise SeamCodecError(
            f"{payload_type.__name__} is not one of this seam's "
            f"OBSERVABLE_RESPONSE_PAYLOAD_TYPES "
            f"{sorted(_ENCODABLE_RESPONSE_PAYLOAD_TYPES)}"
        )
    names = [f.name for f in dataclass_fields(payload)]
    # DENYLIST FIRST, deliberately: when a field is both undeclared AND a name
    # the contract already knows leaks truth, the truth-leak message is the
    # more diagnostic of the two. Ordering also keeps the two belts separately
    # observable -- each has a test that can only pass if ITS check fired.
    leaking = sorted(set(names) & set(FORBIDDEN_TRUTH_FIELDS))
    if leaking:
        raise SeamCodecError(
            f"{payload_type.__name__} declares forbidden truth field(s) {leaking} -- the "
            "SIM's own hidden quantities may never cross this seam, whatever the envelope says"
        )
    declared = OBSERVABLE_PAYLOAD_FIELDS.get(payload_type.__name__)
    if declared is None:
        raise SeamCodecError(
            f"{payload_type.__name__} has no OBSERVABLE_PAYLOAD_FIELDS declaration -- "
            "a payload type the contract has not certified field-by-field may not cross"
        )
    undeclared = sorted(set(names) - set(declared))
    if undeclared:
        raise SeamCodecError(
            f"{payload_type.__name__} declares field(s) {undeclared} the contract has not "
            "declared observable -- widen OBSERVABLE_PAYLOAD_FIELDS only after answering "
            "'could a real UK flex party know this from its own statement alone?'"
        )
    absent = sorted(set(declared) - set(names))
    if absent:
        raise SeamCodecError(
            f"{payload_type.__name__} omits declared observable field(s) {absent} -- the "
            "contract's declaration has gone stale against the payload it certifies"
        )
    return {
        "payload_type": payload_type.__name__,
        "fields": {
            name: _encode_scalar(
                getattr(payload, name), f"{payload_type.__name__}.{name}"
            )
            for name in names
        },
    }


def encode_wall_response(response: WallResponse) -> dict:
    """Serialise one flex `WallResponse` into the wire form this seam publishes.

    Written against the SCHEMA, not against the company's decoder: the key set
    below is the response schema as the contract documents it, and if the
    company widens its own expectation without the schema changing, this
    encoder keeps emitting the old shape and the far side refuses it.
    """
    if not isinstance(response, WallResponse):
        raise SeamCodecError(f"expected a WallResponse, got {type(response).__name__}")
    return {
        "correlation_id": response.correlation_id,
        "status": response.status.value,
        # THE MESSAGE'S OWN VINTAGE, NOT THIS MODULE'S CURRENT ONE (EP6 pass 44).
        # This read was `SCHEMA_VERSION` -- the encoder's own constant -- in all
        # THREE world-side seam encoders, while the company's codec
        # (`wall_protocol.encode_response`) had always preserved the field. The
        # defect was invisible for as long as exactly one version existed, and
        # the payment seam going to v2 is what made the two able to disagree.
        # An encoder that overwrites the stamp makes the vintage field unable to
        # differ from the reader's constant, so the decoder's version check --
        # the one thing a version number is FOR -- could never fire on anything
        # this seam emitted. Live behaviour is unchanged either way, because
        # every construction site here already stamps `SCHEMA_VERSION`; what is
        # removed is the latent relabelling.
        "schema_version": response.schema_version,
        "observed_at": response.observed_at.isoformat(),
        "valid_time": None if response.valid_time is None else response.valid_time.isoformat(),
        "payload": (
            None if response.payload is None else encode_observable_payload(response.payload)
        ),
        "error": (
            None
            if response.error is None
            else {"code": response.error.code, "message": response.error.message}
        ),
    }


def _frame_feed(responses, *, handed_over_at: dt.datetime) -> List[dict]:
    """Encode every response of one feed and hand each one over inside the
    transport frame of the participant that operates ITS OWN venue.

    PER MESSAGE, NOT PER FEED, and that is not a stylistic choice: a stacked
    feed carries lines for several venues at once, and in GB those venues are
    not all run by the same party. A feed signed once by "the sender" would
    stamp a local constraint market's line with the system operator's identity
    -- a forgery the world itself committed, and one no company-side check
    could ever catch, because the company would be authenticating a claim the
    world had already made false.

    The venue is read off `r.payload.venue`, which is the WORLD'S own record of
    which market it is settling -- the payload is being constructed here, not
    received, so there is no message to be believed and no tautology to avoid.
    """
    return [
        frame_venue_message(
            encode_wall_response(r),
            venue=r.payload.venue,
            handed_over_at=handed_over_at,
        )
        for r in responses
    ]


def emit_settlement_lines_over_wire(
    truth: FlexDispatchTruth,
    *,
    registrations: "VenueRegistrations",
    handed_over_at: dt.datetime,
    unit_id: str = "FLEX_UNIT_1",
    venue: FlexVenue = FlexVenue.BALANCING_MECHANISM,
    settlement_lag_days: int = _SETTLEMENT_LAG_DAYS,
) -> List[dict]:
    """`emit_settlement_lines`, handing over BYTES-shaped wire messages instead
    of in-process objects -- what a real Elexon settlement feed delivers.

    The object form remains: it is how the response is constructed in the first
    place and what this module's own tests measure. What changed is that the
    COMPANY no longer receives one.

    `registrations` is this venue's OWN book and is REQUIRED: every line is
    checked against it before it crosses, and a window it does not cover raises
    `UnregisteredDispatch` rather than settling a unit nobody enrolled (see THE
    VENUE'S TEETH below).

    `handed_over_at` IS REQUIRED AND HAS NO DEFAULT, same rule as
    `frame_venue_message` states it (EP6 pass 61): the tempting default is the
    statement's own `observed_at`, and a hand-over clock read off the document
    it wraps can never disagree with it. A statement is handed over as a BATCH
    -- one settlement run, one moment -- so one clock covers the feed.
    """
    responses = emit_settlement_lines(
        truth,
        unit_id=unit_id,
        venue=venue,
        settlement_lag_days=settlement_lag_days,
    )
    for r in responses:
        _require_registered(
            registrations,
            r.payload.unit_id,
            r.payload.venue,
            r.payload.window_start,
            r.payload.window_end,
            "settlement line",
        )
    return _frame_feed(responses, handed_over_at=handed_over_at)


def emit_dispatch_instructions_over_wire(
    truth: FlexDispatchTruth,
    *,
    registrations: "VenueRegistrations",
    handed_over_at: dt.datetime,
    unit_id: str = "FLEX_UNIT_1",
    venue: FlexVenue = FlexVenue.BALANCING_MECHANISM,
    direction: FlexDirection = FlexDirection.TURN_DOWN,
) -> List[dict]:
    """`emit_dispatch_instructions`, on the wire. The instruction feed and the
    settlement feed are separate events in time (C-S3) and cross separately.

    `registrations` is REQUIRED for the same reason it is on the settlement leg
    -- and it matters MORE here, because an instruction is the moment a unit is
    actually called. `handed_over_at` is required for the reason given on the
    settlement leg."""
    responses = emit_dispatch_instructions(
        truth, unit_id=unit_id, venue=venue, direction=direction
    )
    for r in responses:
        _require_registered(
            registrations,
            r.payload.unit_id,
            r.payload.venue,
            r.payload.window_start,
            r.payload.window_end,
            "dispatch instruction",
        )
    return _frame_feed(responses, handed_over_at=handed_over_at)


# ---------------------------------------------------------------------------
# THE REGISTRATION DESK -- this counterparty RECEIVING the flex seam's REQUEST
# leg (EP6 pass 52).
#
# WHAT WAS WRONG. The seam has declared `FlexEnrolmentWallRequest` since it was
# written and no module in this build ever constructed a `FlexEnrolment`: the
# only sender was `StubSimInterface.enrol_flex`, which appended the envelope to a
# list nothing reads, and `LiveSimInterface` does not implement the method at
# all. So the venue dispatched `unit_id="FLEX_UNIT_1"` -- a KEYWORD DEFAULT --
# whether or not any company had offered it, over windows nobody had declared,
# and the company accepted the instructions because it had no record against
# which to ask whether it had asked. That is the census's UNSOLICITED INBOUND
# reading and the reviewer's Q2 fail ("we model it as a response to a synthetic
# request") in a second seam.
#
# WHY THE DECODER IS HERE AND NOT IMPORTED, same as the encoder above and for
# the same reason: `sim/**` may not import `company.*`, so this module restates
# the PUBLISHED request key set (`_REQUEST_WIRE_FIELDS`, mirroring
# `wall_protocol.REQUEST_WIRE_FIELDS`, which is itself the envelope's own field
# list) and refuses against it. Two codecs written independently against one
# schema is what makes the round trip evidence rather than a handshake with
# itself.
#
# THE VENUE JUDGES ON ITS OWN CLOCK. `answer_enrolment` takes `venue_clock` and
# never reads the request's `emitted_at` to decide whether a window has closed:
# a refusal keyed on a timestamp the SENDER controls is a refusal the sender can
# switch off. Same reasoning as the company's account roster and the
# counterparty fingerprint -- absence is never agreement, and neither is
# self-report.
# ---------------------------------------------------------------------------

#: The exact key set of a REQUEST on the wire, mirrored from the published
#: envelope. Restated rather than imported (see above); a drift between this and
#: the company's `wall_protocol.REQUEST_WIRE_FIELDS` stops enrolments crossing,
#: which is the correct outcome and the whole reason they are separate code.
_REQUEST_WIRE_FIELDS = frozenset(
    {"correlation_id", "request_type", "schema_version", "as_of", "emitted_at", "payload"}
)

#: The request payload's key set, read from the CONTRACT's own declaration so a
#: field added to `FlexEnrolment` and published is decodable the day it is
#: declared and not a day before.
_ENROLMENT_PAYLOAD_FIELDS = frozenset(REQUEST_PAYLOAD_FIELDS["FlexEnrolment"])

#: The request_type this desk answers. A request naming anything else has been
#: mis-routed to the wrong venue, which is not the same thing as a malformed one.
ENROLMENT_REQUEST_TYPE = "flex_enrolment"


# ---------------------------------------------------------------------------
# WHO IS SPEAKING -- the flex seam's transport identity (EP6 pass 61, Q13).
#
# WHAT WAS WRONG, and it is not that the answer was unchecked. The company DID
# check that an acceptance described its own offer -- `MisroutedOutcome` compares
# the outcome's `unit_id`/`venue` against its own submission. But both of those
# fields are read OUT OF THE MESSAGE, so the only thing standing between this
# company and a registration minted by anything at all was that the impostor
# echo the right two values back: a process that could put bytes on this leg
# supplied the evidence for its own admissibility. That is the R15 TAUTOLOGY
# pattern at the transport layer, and the payment seam has not had it since
# pass 50.
#
# A VENUE IS A MARKET FUNCTION AND A SENDER IS A PARTICIPANT, which is the whole
# reason this mapping exists rather than a `sender = venue.value` line. The
# contract says so in as many words (`FlexVenue`: "The flex MARKET FUNCTION, not
# a counterparty"), and in GB the two genuinely do not line up: the system
# operator runs the balancing mechanism, the capacity market's delivery role and
# the demand-flexibility service -- THREE functions, ONE counterparty -- while a
# local constraint market is run by the network operator for that region, which
# is a different party holding a different key. So the company cannot derive who
# should be speaking from the venue it addressed without being told, and this is
# the world's own statement of it.
#
# `OTHER` HAS NO OPERATOR AND THAT IS THE POINT. It is the contract's
# placeholder member -- a venue nobody runs a market for yet -- and a lookup
# that fell back to some default participant for it would be exactly the
# fail-open shape `COUNTERPARTY_REGISTRY` refuses on the other side (a table
# with a default is a table that cannot say no). An unoperated venue cannot put
# a message on the wire at all.
#
# NOT A SECRET IN THE SECRETS SENSE, same as the payment stand-in's: these are
# synthetic credentials for stand-in counterparties inside a simulation, with no
# real-world participant and (by `tools/company_network_isolation.py`) no route
# to one. They are literals here because they are WORLD STATE, not configuration
# -- and rotating one without updating the company's registry BREAKS THIS SEAM
# deliberately, which is what a participant changing its key without telling its
# counterparty does on a real network.
# ---------------------------------------------------------------------------

#: The participant that runs the national market functions.
SYSTEM_OPERATOR_ID = "SYSTEM-OPERATOR-01"

#: The participant that runs a local constraint market. A DIFFERENT party from
#: the one above, holding a different key -- which is what makes "the sender is
#: registered with us" and "the sender runs the venue we addressed" two
#: different questions rather than one.
NETWORK_OPERATOR_ID = "NETWORK-OPERATOR-01"

SYSTEM_OPERATOR_CREDENTIAL = "system-operator-01::participant-credential::v1"
NETWORK_OPERATOR_CREDENTIAL = "network-operator-01::participant-credential::v1"

#: Which participant operates each market function. Deliberately NOT total over
#: `FlexVenue`: `OTHER` is absent, and absence refuses.
FLEX_VENUE_OPERATORS: Dict[FlexVenue, str] = {
    FlexVenue.BALANCING_MECHANISM: SYSTEM_OPERATOR_ID,
    FlexVenue.CAPACITY_MARKET: SYSTEM_OPERATOR_ID,
    FlexVenue.DFS_TURN_DOWN: SYSTEM_OPERATOR_ID,
    FlexVenue.DSO_LOCAL_CONSTRAINT: NETWORK_OPERATOR_ID,
}

_OPERATOR_CREDENTIALS: Dict[str, str] = {
    SYSTEM_OPERATOR_ID: SYSTEM_OPERATOR_CREDENTIAL,
    NETWORK_OPERATOR_ID: NETWORK_OPERATOR_CREDENTIAL,
}


class UnoperatedVenue(ValueError):
    """This world runs no market for that venue, so nobody can speak for it.

    Raised on the SENDING side, before any bytes exist. Deliberately not a
    `WallResponse` refusal: a structured refusal is a message FROM a
    participant, and the whole content of this error is that there is no
    participant to send it.
    """


def frame_venue_message(
    envelope_wire: dict, *, venue: FlexVenue, handed_over_at: dt.datetime
) -> dict:
    """Wrap one encoded envelope in the transport frame of the participant that
    operates `venue`, stamped with the moment it let go of the message.

    Written against the frame SCHEMA and not against the company's
    `decode_frame`, same rule as `encode_wall_response` above and for the same
    reason: `sim/**` may not import `company.*`, and a frame built by reading
    the receiver's code would make the round trip a handshake with itself.

    `handed_over_at` IS REQUIRED AND HAS NO DEFAULT. The tempting default --
    the envelope's own `observed_at` -- would make a prompt hand-over
    unfalsifiable by construction: the field could then never disagree with the
    document it wraps, which is the R15 TAUTOLOGY shape one layer down. A
    caller that cannot say when it handed a message over does not get to send
    one.
    """
    if not isinstance(envelope_wire, dict):
        raise SeamCodecError(
            f"expected an encoded envelope dict, got {type(envelope_wire).__name__}"
        )
    if not isinstance(handed_over_at, dt.datetime):
        raise SeamCodecError(
            f"handed_over_at must be a datetime, got {type(handed_over_at).__name__}"
        )
    operator = FLEX_VENUE_OPERATORS.get(venue)
    if operator is None:
        raise UnoperatedVenue(
            f"no participant in this world operates {getattr(venue, 'value', venue)!r} -- "
            "a venue with no operator has nobody to put a message on the wire, and a "
            "fallback sender here would be a transport identity nobody decided about"
        )
    return {
        "sender": operator,
        "credential": _OPERATOR_CREDENTIALS[operator],
        "handed_over_at": handed_over_at.isoformat(),
        "envelope": envelope_wire,
    }


class EnrolmentRefused(ValueError):
    """This venue would not register an enrolment. Carries the declared
    `ENROLMENT_REFUSAL_CODES` member as `code` so the refusal crosses the wall as
    a structured `ErrorDetail` rather than as prose the company has to parse.

    Deliberately NOT `SeamCodecError`: a refusal is a well-formed message the
    venue understood and declined, and collapsing it into "could not decode"
    would let a company read its own rejected registration as a bad line on the
    feed."""

    def __init__(self, code: str, message: str) -> None:
        if code not in ENROLMENT_REFUSAL_CODES:
            raise ValueError(
                f"EnrolmentRefused: {code!r} is not one of the venue's declared refusal "
                f"codes {list(ENROLMENT_REFUSAL_CODES)} -- an undeclared reason is one the "
                "company cannot branch on, so it may not be sent"
            )
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


def _decode_enrolment_payload(raw: Any) -> FlexEnrolment:
    """Rebuild a `FlexEnrolment` off the wire, or refuse it.

    ABSENCE IS NEVER AGREEMENT, in this direction too: a missing key is refused,
    never defaulted. A defaulted `offered_mw` would register the company for a
    volume it never offered and then settle it against that volume.
    """
    if not isinstance(raw, dict):
        raise SeamCodecError(f"enrolment payload must be a mapping, got {type(raw).__name__}")
    keys = set(raw)
    if keys != _ENROLMENT_PAYLOAD_FIELDS:
        missing = sorted(_ENROLMENT_PAYLOAD_FIELDS - keys)
        unknown = sorted(keys - _ENROLMENT_PAYLOAD_FIELDS)
        raise SeamCodecError(
            f"enrolment payload key set {sorted(keys)} is not the published one "
            f"{sorted(_ENROLMENT_PAYLOAD_FIELDS)} (missing={missing}, unknown={unknown})"
        )
    try:
        venue = FlexVenue(raw["venue"])
        direction = FlexDirection(raw["direction"])
    except ValueError as exc:
        raise SeamCodecError(f"enrolment names a venue/direction this venue does not run: {exc}")
    unit_id = raw["unit_id"]
    if not isinstance(unit_id, str) or not unit_id:
        raise SeamCodecError(f"enrolment unit_id must be a non-empty str, got {unit_id!r}")
    offered = raw["offered_mw"]
    # bool is an int subclass; a True offer would register as a plausible 1 MW.
    if isinstance(offered, bool) or not isinstance(offered, (int, float)):
        raise SeamCodecError(f"enrolment offered_mw must be a number, got {offered!r}")
    return FlexEnrolment(
        unit_id=unit_id,
        venue=venue,
        offered_mw=float(offered),
        direction=direction,
        window_start=_decode_wire_datetime(raw["window_start"], "window_start"),
        window_end=_decode_wire_datetime(raw["window_end"], "window_end"),
    )


def _decode_wire_datetime(raw: Any, field: str) -> dt.datetime:
    if not isinstance(raw, str):
        raise SeamCodecError(f"{field} must be an ISO-8601 str, got {raw!r}")
    try:
        return dt.datetime.fromisoformat(raw)
    except ValueError as exc:
        raise SeamCodecError(f"{field}: {raw!r} is not an ISO-8601 datetime") from exc


def decode_request(wire: Any) -> WallRequest:
    """Parse one flex enrolment request off the wire, or refuse it.

    Named for the leg it decodes, matching the company codec's own entry point:
    the two implementations are independent, the NAME is the published one.
    """
    if not isinstance(wire, dict):
        raise SeamCodecError(f"a request must be a mapping, got {type(wire).__name__}")
    keys = set(wire)
    if keys != _REQUEST_WIRE_FIELDS:
        raise SeamCodecError(
            f"request key set {sorted(keys)} is not the published one "
            f"{sorted(_REQUEST_WIRE_FIELDS)}"
        )
    version = wire["schema_version"]
    if version != SCHEMA_VERSION:
        raise SeamCodecError(
            f"schema_version {version!r} is not the {SCHEMA_VERSION} this seam speaks"
        )
    correlation_id = wire["correlation_id"]
    if not isinstance(correlation_id, str) or not correlation_id:
        raise SeamCodecError(
            f"correlation_id must be a non-empty str, got {correlation_id!r} -- a "
            "registration nothing can be matched to cannot be answered"
        )
    request_type = wire["request_type"]
    if request_type != ENROLMENT_REQUEST_TYPE:
        raise SeamCodecError(
            f"request_type {request_type!r} is not {ENROLMENT_REQUEST_TYPE!r} -- this desk "
            "registers flex enrolments and does not guess at anything else"
        )
    return WallRequest(
        correlation_id=correlation_id,
        request_type=request_type,
        schema_version=version,
        as_of=_decode_wire_datetime(wire["as_of"], "as_of"),
        emitted_at=_decode_wire_datetime(wire["emitted_at"], "emitted_at"),
        payload=_decode_enrolment_payload(wire["payload"]),
    )


@dataclass
class VenueRegistrations:
    """The VENUE's own book of who is registered here -- the world side's record,
    held separately from the company's (`FlexEnrolmentBook`) because neither
    party may read the other's.

    This is what makes `UNIT_ALREADY_ENROLLED` answerable at all: a venue that
    kept no book could not tell a first registration from a second one, and
    would sell the same unit's MW twice into the same market function for the
    same period. Overlap is scoped BY VENUE deliberately -- one unit registered
    into several DIFFERENT venues over one window is the legitimate multi-venue
    book `dispatch_and_settle_stacked` models, and the contention it creates is
    a thing the company is supposed to be able to get wrong.
    """

    _held: Dict[Tuple[str, str], List[Tuple[dt.datetime, dt.datetime, str]]] = field(
        default_factory=dict
    )
    _minted: int = 0

    def accepted(self, enrolment: FlexEnrolment) -> Optional[str]:
        """The reference this venue minted for an accepted enrolment, if any."""
        for start, end, ref in self._held.get((enrolment.unit_id, enrolment.venue.value), []):
            if start == enrolment.window_start and end == enrolment.window_end:
                return ref
        return None

    def overlapping(self, enrolment: FlexEnrolment) -> Optional[str]:
        """The reference of a registration whose window OVERLAPS this one, if any.

        Half-open windows: a registration ending exactly when another starts is
        two consecutive availability periods, not a double sale.
        """
        for start, end, ref in self._held.get((enrolment.unit_id, enrolment.venue.value), []):
            if enrolment.window_start < end and start < enrolment.window_end:
                return ref
        return None

    def covers(
        self,
        unit_id: str,
        venue: FlexVenue,
        window_start: dt.datetime,
        window_end: dt.datetime,
    ) -> Optional[str]:
        """The reference of a registration whose AVAILABILITY window CONTAINS
        this delivery window, if any -- the question a dispatch must pass.

        CONTAINMENT, NOT OVERLAP, and this is the whole content of the rule. A
        party declares availability FROM x TO y; an instruction that begins
        inside it and runs past y calls the unit over minutes it never offered,
        and a venue that accepted that would be settling volume outside the
        product. `overlapping` above answers a different question (may I
        register this?) and the two must not be collapsed: overlap is the right
        test for a double sale and the wrong one for a call.
        """
        for start, end, ref in self._held.get((unit_id, venue.value), []):
            if start <= window_start and window_end <= end:
                return ref
        return None

    def register(self, enrolment: FlexEnrolment) -> str:
        """Mint a reference and hold the registration. The reference is the
        VENUE'S, minted from its own sequence: a company that could predict it
        could quote a registration it never made."""
        self._minted += 1
        ref = f"{enrolment.venue.value.upper()}-REG-{self._minted:06d}"
        self._held.setdefault((enrolment.unit_id, enrolment.venue.value), []).append(
            (enrolment.window_start, enrolment.window_end, ref)
        )
        return ref


def answer_enrolment(
    wire: Any,
    *,
    venue_clock: dt.datetime,
    registrations: VenueRegistrations,
) -> dict:
    """Take one enrolment request off the wire and hand back the venue's ANSWER,
    on the wire -- the flex seam's response leg for its own request leg.

    C-S2 (idempotency): a re-sent registration for a window this venue has
    already accepted returns the SAME reference rather than minting a second
    one. `correlation_id` is the idempotency key and a resolver that recomputed
    would hand the company two references for one registration.

    A refusal crosses as `WallResponse(status=ERROR, error=ErrorDetail(...))`
    with a code from `ENROLMENT_REFUSAL_CODES` -- the envelope's own shape for
    "understood and declined", carrying no payload because a non-OK response may
    not (`WallResponse.__post_init__`).

    RAISES `SeamCodecError` for a message this desk could not read at all, which
    is a different thing from a registration it refused and is why the two do not
    share an exception type: an unreadable message has no correlation_id to
    answer on.

    THE ANSWER CROSSES INSIDE A TRANSPORT FRAME (EP6 pass 61), so the company
    learns WHO said it before it reads anything it said. A REFUSAL is framed
    too, and that is not symmetry for its own sake: an unframed refusal would be
    a message any process could put on this leg to make a company believe its
    registration had been declined, and a registration a company believes it
    does not hold is as expensive as one it wrongly believes it does.

    WHICH PARTICIPANT SIGNS IS READ OFF THE REQUEST'S VENUE, which is a field the
    SENDER controls -- deliberately, and it grants nothing. All it decides is
    which of this world's own desks answers; the company then checks the PROVEN
    sender against the venue in its OWN submission book, so a request naming a
    venue whose operator the sender cannot present a credential for produces an
    answer the company refuses.
    """
    request = decode_request(wire)
    enrolment = request.payload
    try:
        reference = _register_or_refuse(enrolment, venue_clock, registrations)
    except EnrolmentRefused as refusal:
        return frame_venue_message(
            encode_wall_response(
                WallResponse(
                    correlation_id=request.correlation_id,
                    status=WallStatus.ERROR,
                    schema_version=SCHEMA_VERSION,
                    observed_at=venue_clock,
                    valid_time=enrolment.window_start.date(),
                    payload=None,
                    error=ErrorDetail(code=refusal.code, message=refusal.message),
                )
            ),
            venue=enrolment.venue,
            handed_over_at=venue_clock,
        )
    return frame_venue_message(
        encode_wall_response(
            FlexEnrolmentOutcomeWallResponse(
                correlation_id=request.correlation_id,
                status=WallStatus.OK,
                schema_version=SCHEMA_VERSION,
                observed_at=venue_clock,
                valid_time=enrolment.window_start.date(),
                payload=FlexEnrolmentOutcome(
                    enrolment_reference=reference,
                    unit_id=enrolment.unit_id,
                    venue=enrolment.venue,
                ),
            )
        ),
        venue=enrolment.venue,
        handed_over_at=venue_clock,
    )


def _register_or_refuse(
    enrolment: FlexEnrolment,
    venue_clock: dt.datetime,
    registrations: VenueRegistrations,
) -> str:
    """The venue's registration rules. STRUCTURAL ONLY (see
    `ENROLMENT_REFUSAL_CODES`): this venue refuses what it cannot register, never
    what it does not fancy -- an economic acceptance rule would be a difficulty
    parameter and those are the director's (R13)."""
    already = registrations.accepted(enrolment)
    if already is not None:
        return already
    if enrolment.window_end <= enrolment.window_start:
        raise EnrolmentRefused(
            "WINDOW_NOT_A_WINDOW",
            f"availability window ends {enrolment.window_end.isoformat()}, at or before its "
            f"start {enrolment.window_start.isoformat()}",
        )
    if not np.isfinite(enrolment.offered_mw) or enrolment.offered_mw <= 0.0:
        raise EnrolmentRefused(
            "OFFER_NOT_DELIVERABLE",
            f"offered_mw {enrolment.offered_mw!r} is not a finite positive volume",
        )
    if enrolment.window_end <= venue_clock:
        raise EnrolmentRefused(
            "WINDOW_ALREADY_CLOSED",
            f"availability window ended {enrolment.window_end.isoformat()}, before this venue "
            f"read the request at {venue_clock.isoformat()}",
        )
    clash = registrations.overlapping(enrolment)
    if clash is not None:
        raise EnrolmentRefused(
            "UNIT_ALREADY_ENROLLED",
            f"unit {enrolment.unit_id} is already registered at {enrolment.venue.value} over an "
            f"overlapping window under {clash}",
        )
    return registrations.register(enrolment)


# ---------------------------------------------------------------------------
# THE VENUE'S TEETH -- a dispatch is only lawful against a registration this
# venue actually holds (EP6 pass 57).
#
# WHAT WAS STILL WRONG AFTER PASS 54. The loop gained a request leg and the
# harness compared the unit the world settled against the unit the venue said
# it registered -- two quantities from two sides, which is a real check and is
# the right thing for a HARNESS to do. But it is an OBSERVATION, made after the
# fact by the one layer allowed to see both sides, and the world went on being
# able to produce the statement it was observing: nothing in `sim/**` consulted
# `VenueRegistrations` before putting an instruction or a settlement line on the
# wire, so a unit nobody had ever enrolled was still dispatchable and still
# settleable. A gap the harness can only report is not a law the world obeys,
# and the difference shows up the moment a loop is written that forgets to
# score it.
#
# WHY IT BELONGS ON THE WIRE LEGS AND NOT IN `dispatch_and_settle`. The truth
# function has no unit and no venue -- it takes a scalar `enrolled_mw` over a
# price/residual record and knows nothing about WHO is enrolled. The unit
# enters at EMISSION, where an identity is first attached to a volume, and the
# wire legs are where that identity crosses to a company. So that is where the
# book is consulted, and `registrations` is a REQUIRED keyword on both of them:
# a default of None would be this project's own fail-open pattern, where the
# control passes on the argument nobody remembered to pass.
#
# EVERY WIRE LEG IS BELTED AS OF EP6 PASS 58. The STACKED L3 emitters were the
# hold-out, and the reason they were unbelted was real rather than an oversight:
# the L3 loop did not register at all, so belting them would have refused every
# stacked run. `background.flex_dispatch_triad.solicit_registration_stacked`
# gives that loop its registration leg -- one enrolment per venue through the
# production seam, into ONE book -- which is what made the belt landable here.
#
# WHAT IS NOT BELTED, said plainly rather than left to be discovered: the
# in-process `emit_dispatch_instructions` / `emit_settlement_lines` and their
# stacked twins are constructors (they are how the wire form is built in the
# first place, and what this module's own truth tests measure). Belting a
# constructor would put the check on the object path as well as the wire without
# adding a refusal the wire does not already make.
# ---------------------------------------------------------------------------


class UnregisteredDispatch(ValueError):
    """This venue would not put an instruction or a settlement line for this
    unit on the wire, because its own book holds no registration covering the
    window.

    Deliberately NOT `EnrolmentRefused`: that type answers a REQUEST the
    company made and crosses as a structured `ErrorDetail` on the response leg.
    This is the venue declining to SPEAK UNPROMPTED about a unit it never
    registered, so there is no correlation_id to answer on and no company
    message it is a reply to -- it is a defect in the world's own caller.
    """


def _require_registered(
    registrations: "VenueRegistrations",
    unit_id: str,
    venue: FlexVenue,
    window_start: dt.datetime,
    window_end: dt.datetime,
    what: str,
) -> str:
    """The reference this event is settled/instructed under, or refuse it.

    Returns the reference rather than a bool so the caller cannot check and
    then emit under a different one, and so an empty book has no path through:
    `covers` returns None for a book that holds nothing, which is a REFUSAL and
    not a pass (R15 fail-open -- missing/empty is the state the defect lives
    in).
    """
    reference = registrations.covers(unit_id, venue, window_start, window_end)
    if reference is None:
        raise UnregisteredDispatch(
            f"{what} for unit {unit_id!r} at {venue.value} over "
            f"[{window_start.isoformat()}, {window_end.isoformat()}) is covered by no "
            f"registration this venue holds -- a venue may only call a unit inside an "
            f"availability window that unit declared to it"
        )
    return reference


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


# -- the L3 feeds on the wire ------------------------------------------------
# The census asks its question per SEAM and per LEG, so migrating the L1/L2
# feeds alone would have flipped channel C's reading to `3 of 3` with the
# stacked feeds still handed over as objects: the same defect, at the one
# granularity below the instrument's. Both stacked feeds cross as bytes too.


def emit_dispatch_instructions_stacked_over_wire(
    truth: StackedFlexTruth,
    *,
    registrations: "VenueRegistrations",
    handed_over_at: dt.datetime,
    unit_id: str = "FLEX_UNIT_1",
) -> List[dict]:
    """`emit_dispatch_instructions_stacked`, on the wire.

    THIS IS THE FEED WITH TWO SENDERS IN IT. A stacked portfolio is called at
    several venues at once, and a local constraint market is run by a different
    participant from the national ones -- so `_frame_feed` signs each message
    with ITS OWN venue's operator, and one list crosses carrying two identities.

    `registrations` is REQUIRED, exactly as on the single-venue legs, and here
    the book is asked a question it is not asked anywhere else: the SAME unit
    holds a SEPARATE registration per venue, so a call at the Capacity Market
    is licensed by the Capacity Market registration alone. `covers` is keyed by
    (unit, venue) already, so a portfolio registered at one venue and called at
    another is refused rather than waved through on the strength of being a
    known unit.
    """
    responses = emit_dispatch_instructions_stacked(truth, unit_id=unit_id)
    for r in responses:
        _require_registered(
            registrations,
            r.payload.unit_id,
            r.payload.venue,
            r.payload.window_start,
            r.payload.window_end,
            "stacked dispatch instruction",
        )
    return _frame_feed(responses, handed_over_at=handed_over_at)


def emit_settlement_lines_stacked_over_wire(
    truth: StackedFlexTruth,
    *,
    registrations: "VenueRegistrations",
    handed_over_at: dt.datetime,
    unit_id: str = "FLEX_UNIT_1",
    settlement_lag_days: int = _SETTLEMENT_LAG_DAYS,
) -> List[dict]:
    """`emit_settlement_lines_stacked`, on the wire.

    `registrations` is REQUIRED for the same reason as on every other wire leg.
    The stacked settlement feed is where an unregistered venue would be PAID,
    so a book that covers the unit at one venue does not license a statement
    line at another. Signed per venue, as the stacked instruction feed is.
    """
    responses = emit_settlement_lines_stacked(
        truth, unit_id=unit_id, settlement_lag_days=settlement_lag_days
    )
    for r in responses:
        _require_registered(
            registrations,
            r.payload.unit_id,
            r.payload.venue,
            r.payload.window_start,
            r.payload.window_end,
            "stacked settlement line",
        )
    return _frame_feed(responses, handed_over_at=handed_over_at)
