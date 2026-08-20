"""W1_9_dsr_flex_markets (L1) -- the COMPANY side of the DSR/flexibility
coupled triad. The company copes THROUGH THE WALL and is allowed to be wrong.

WHAT A REAL UK FLEX PARTY KNOWS (the only inputs this module may read):
  * the OBSERVED wholesale price outturn (Elexon SSP) -- public market data,
  * its OWN enrolled capacity and offers (its own records),
  * its OWN past settlement lines (`FlexSettlementLine`, off its statement).
It does NOT know the SIM's true system need, the true residual margin, or the
merit-order internals -- so it cannot see WHY a scarcity call happens, only
the PRICE it can observe. It must INFER when flex is worth bidding, and how
much revenue to expect, from that price alone (FRAME §8 refinement: the honest
L1 trigger is a price-derived scarcity proxy, never a read of true residual).

THE BELIEF (L1). The company predicts it will be dispatched in the highest-
price periods (a rolling/whole-window price percentile is its scarcity proxy)
and expects to be paid utilisation at the observed price for those periods.
Its EXPECTED utilised revenue is what it would forecast ex-ante; the SIM's
TRUE utilised revenue is driven by residual demand (which the company cannot
see). The two dispatch sets differ -- the belief-vs-truth GAP is that
forecast error, scored by `background/flex_dispatch_triad.py`.

EPISTEMIC WALL. This module imports the typed observable seam
(`interface.contracts.flex_observable_seam`), the company's OWN envelope codec
(`company.interfaces.wall_protocol`) and numpy. It imports NOTHING from
`sim`/`simulation` -- verified by `python3 -m tools.epistemic_verifier` and by
`tests/company/test_flex_participation.py::test_no_sim_import`. The price
series is handed in as market data (as a real supplier reads SSP); the company
never reaches into the SIM to fetch it, and since EP6 pass 22 it does not
receive an in-process object from it either -- the settlement statement and the
dispatch instruction arrive as BYTES it decodes and may refuse.

L1 NAMED SIMPLIFICATIONS (R10): the proxy is a single whole-window price
percentile (the simplest honest scarcity inference); a point-in-time /
rolling estimate and a learned dispatch-frequency model are L2+. Participation
size is the company's own input, not a benchmark.

L2 (`form_participation_belief_l2`): the company no longer assumes PERFECT
delivery. It LEARNS a de-rating from its OWN past settlement observables
(metered delivery / instructed volume -- both on its own statement) and
applies it to future forecasts, and it estimates its counterfactual BASELINE
with a methodology that may be BIASED. Both are observables-only company
BELIEFS; the SIM's true per-event delivery ratio and true baseline stay behind
the wall, so the residual belief-vs-truth GAP (sampling error in the learned
ratio + baseline-methodology error exposure) is what the harness scores.

L3 (`form_stacked_belief`): the company runs a STACKED book -- more than one
flex product at once against ONE physical portfolio. It must form a belief about
stacked revenue WITHOUT being able to see whether the same MW is being promised
twice. Its cold-start belief is NAIVE (it double-counts, exactly as real
aggregators do); it LEARNS an overlap frequency and per-venue call rates from
its OWN dispatch-instruction feed and nets that fraction, and forecasts its own
availability clawback from that belief. It stays wrong, structurally: overlap
frequency is a past sample, overlap is not the same as BINDING, and the world's
priority allocation is unobservable. `as_of` adds the POINT-IN-TIME split so the
de-rating and the contention rate are learned from a PAST window and applied to
a FUTURE one (see the L3 section below).
"""
from __future__ import annotations

import datetime as dt
import math
from dataclasses import dataclass
from enum import Enum
from typing import (
    Any,
    Dict,
    List,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)

import numpy as np

from company.interfaces.wall_protocol import WallProtocolError, decode_response
from interface.contracts.flex_observable_seam import (
    FORBIDDEN_TRUTH_FIELDS,
    OBSERVABLE_RESPONSE_PAYLOAD_TYPES,
    FlexSettlementLine,
)

# The company's OWN scarcity-proxy threshold: it expects dispatch in periods
# whose observed price is at/above this percentile. Its belief parameter (a
# guess), deliberately the SAME nominal percentile the SIM uses for residual
# so the ONLY thing separating truth from belief is residual-vs-price -- the
# real form inadequacy, not a threshold mismatch artefact.
DEFAULT_PRICE_SCARCITY_PERCENTILE: float = 95.0


# ---------------------------------------------------------------------------
# THE WIRE -- the company RECEIVING the flex seam's response leg (EP6 pass 22).
#
# WHAT CHANGED. The settlement statement and the dispatch instruction used to
# reach this module as Python `WallResponse` objects handed across a call
# frame, which means their `schema_version` was a field nobody encoded, nobody
# decoded and nobody could refuse. A version that is never checked is not a
# version. Now the world hands over BYTES and this module parses them, so a
# mock counterparty and a real endpoint are indistinguishable from here --
# which is the atom's whole claim (EP6).
#
# THE COMPANY OWNS ITS CODEC AND CALLS IT: envelope parsing is
# `company.interfaces.wall_protocol.decode_response`, one implementation for
# every seam. The COUNTERPARTY may not import it (`sim/**` cannot see
# `company.*`), so it restates the contract's key set and builds the bytes
# itself. Neither side is the other's source of truth -- both read
# `interface.contracts.flex_observable_seam`, the way a real party reads a
# published schema.
#
# ABSENCE IS NEVER AGREEMENT: a missing payload field is REFUSED, never
# defaulted. Defaulting is how a company folds a settlement figure into its
# belief that no counterparty ever sent it, and the belief-vs-truth gap this
# module exists to be scored on would then be measuring the default.
# ---------------------------------------------------------------------------

_OBSERVABLE_PAYLOAD_TYPES = {t.__name__: t for t in OBSERVABLE_RESPONSE_PAYLOAD_TYPES}
_OBSERVABLE_PAYLOAD_HINTS = {
    t.__name__: get_type_hints(t) for t in OBSERVABLE_RESPONSE_PAYLOAD_TYPES
}


def _declared_base(declared: Any) -> Tuple[Any, bool]:
    """Split ``Optional[X]`` into ``(X, True)``; anything else into ``(it, False)``."""
    if get_origin(declared) is Union:
        args = [a for a in get_args(declared) if a is not type(None)]
        if len(args) == 1:
            return args[0], True
    return declared, False


def _decode_payload_field(raw: Any, declared: Any, where: str) -> Any:
    """Decode one payload field to the type THE CONTRACT declares for it.

    Read from the contract's own `get_type_hints`, never from a list restated
    here: a field whose declared type changes moves this decoder with it, where
    a copy would agree with itself for ever.
    """
    base, optional = _declared_base(declared)
    if raw is None:
        if optional:
            return None
        raise WallProtocolError(
            "MALFORMED_FIELD", f"{where} is null but the contract declares it required"
        )
    if isinstance(base, type) and issubclass(base, Enum):
        try:
            return base(raw)
        except ValueError as exc:
            raise WallProtocolError(
                "MALFORMED_FIELD",
                f"{where}: {raw!r} is not one of {[m.value for m in base]}",
            ) from exc
    if base is str:
        if not isinstance(raw, str):
            raise WallProtocolError("MALFORMED_FIELD", f"{where} must be a str, got {raw!r}")
        return raw
    if base is dt.datetime:
        if not isinstance(raw, str):
            raise WallProtocolError(
                "MALFORMED_FIELD", f"{where} must be an ISO-8601 str, got {raw!r}"
            )
        try:
            return dt.datetime.fromisoformat(raw)
        except ValueError as exc:
            raise WallProtocolError(
                "MALFORMED_FIELD", f"{where}: {raw!r} is not an ISO-8601 datetime"
            ) from exc
    if base is float:
        # bool is an int subclass; a True metered delivery would decode to a
        # plausible, actionable 1.0 and be settled against.
        if isinstance(raw, bool) or not isinstance(raw, (int, float)):
            raise WallProtocolError(
                "MALFORMED_FIELD", f"{where} must be a number, got {raw!r}"
            )
        return float(raw)
    raise WallProtocolError(
        "CONTRACT_VIOLATION",
        f"{where}: this seam has no decoder for declared type {declared!r} -- a field "
        "type was added to the contract without deciding how it crosses",
    )


def decode_observable_payload(raw: Any) -> Any:
    """Rebuild one observable flex payload off the wire, or refuse it.

    THE WALL IS CHECKED HERE TOO, and not only by the counterparty. A world
    that started shipping `true_baseline_mwh` alongside the metered delivery
    would produce a perfectly well-formed ENVELOPE -- only a payload-depth
    refusal catches it, and it must, because a company that folded that number
    in would be READING the SIM's counterfactual rather than estimating it,
    which is the one thing this triad's gap is supposed to measure. Refused BY
    NAME from the contract's own `FORBIDDEN_TRUTH_FIELDS`, so the class fails
    rather than the instance somebody remembered (R10).
    """
    if not isinstance(raw, Mapping):
        raise WallProtocolError(
            "NOT_A_MESSAGE", f"payload must be a mapping, got {type(raw).__name__}"
        )
    missing = sorted({"payload_type", "fields"} - set(raw))
    if missing:
        raise WallProtocolError(
            "MISSING_FIELD",
            f"payload omits {missing} -- an untagged payload cannot be routed to one of "
            "this seam's observable types, and a dispatch instruction and a settlement "
            "line share four field names",
        )
    unknown_keys = sorted(set(raw) - {"payload_type", "fields"})
    if unknown_keys:
        raise WallProtocolError(
            "UNKNOWN_FIELD", f"payload carries undefined key(s) {unknown_keys}"
        )
    tag = raw["payload_type"]
    if tag not in _OBSERVABLE_PAYLOAD_TYPES:
        raise WallProtocolError(
            "UNKNOWN_FIELD",
            f"payload_type {tag!r} is not one of this seam's observable types "
            f"{sorted(_OBSERVABLE_PAYLOAD_TYPES)}",
        )
    body = raw["fields"]
    if not isinstance(body, Mapping):
        raise WallProtocolError(
            "NOT_A_MESSAGE", f"{tag}.fields must be a mapping, got {type(body).__name__}"
        )
    hints = _OBSERVABLE_PAYLOAD_HINTS[tag]
    leaking = sorted(set(body) & set(FORBIDDEN_TRUTH_FIELDS))
    if leaking:
        raise WallProtocolError(
            "CONTRACT_VIOLATION",
            f"{tag} carries SIM-internal truth field(s) {leaking} -- this company infers "
            "its baseline and its system-need from observables and may never be handed them",
        )
    absent = sorted(set(hints) - set(body))
    if absent:
        raise WallProtocolError(
            "MISSING_FIELD",
            f"{tag} omits required field(s) {absent} -- never defaulted; the company would "
            "otherwise settle against a figure no counterparty sent",
        )
    extra = sorted(set(body) - set(hints))
    if extra:
        raise WallProtocolError(
            "UNKNOWN_FIELD", f"{tag} carries field(s) {extra} the contract does not define"
        )
    return _OBSERVABLE_PAYLOAD_TYPES[tag](
        **{
            name: _decode_payload_field(body[name], declared, f"{tag}.{name}")
            for name, declared in hints.items()
        }
    )


def observe_response_wire(wire: Any, *, expect: Optional[type] = None) -> Any:
    """Take ONE flex response off the wire and return its observable payload.

    Refuses rather than returns half a message: an envelope whose status is not
    OK carries no payload (the envelope's own invariant), and a company that
    treated that as "no settlement this period" would silently under-count its
    own revenue instead of noticing the feed had failed.

    `expect` names which observable type this call site is reading -- the
    settlement feed and the instruction feed are separate events in time
    (C-S3), so a caller that asked for one and was handed the other has a
    mis-routed feed, not a usable message.
    """
    response = decode_response(wire, decode_payload=decode_observable_payload)
    if response.payload is None:
        raise WallProtocolError(
            "CONTRACT_VIOLATION",
            f"flex response {response.correlation_id!r} carries no observable payload "
            f"(status {response.status.value}) -- an empty message is not an empty period",
        )
    if expect is not None and not isinstance(response.payload, expect):
        raise WallProtocolError(
            "CONTRACT_VIOLATION",
            f"flex response {response.correlation_id!r} carries a "
            f"{type(response.payload).__name__} where this feed reads {expect.__name__}",
        )
    return response.payload


def observe_settlement_wire(messages: Sequence[Any]) -> List[FlexSettlementLine]:
    """The company's settlement statement, read off the wire.

    This is the crossing the flex triad now scores through: every metered
    delivery the company learns its de-rating from has been encoded by the
    world, decoded here, and version-checked in between.
    """
    return [observe_response_wire(m, expect=FlexSettlementLine) for m in messages]


@dataclass(frozen=True)
class FlexParticipationBelief:
    """The company's observables-only flex participation belief for one run.

    `expected_utilised_revenue` is the per-period revenue vector b the harness
    scores against the SIM truth; `predicted_dispatch_mask` is the company's
    price-proxy guess at which periods it will be called."""

    expected_utilised_revenue: np.ndarray   # per-period, GBP
    predicted_dispatch_mask: np.ndarray     # bool, company's price-proxy guess
    observed_price: np.ndarray              # GBP/MWh, the only signal used
    enrolled_mw: float
    period_hours: float
    price_percentile: float

    @property
    def total_expected_revenue_gbp(self) -> float:
        return float(self.expected_utilised_revenue.sum())

    @property
    def n_predicted_dispatch(self) -> int:
        return int(self.predicted_dispatch_mask.sum())


def form_participation_belief(
    observed_price: Sequence[float],
    *,
    enrolled_mw: float,
    period_hours: float,
    price_percentile: float = DEFAULT_PRICE_SCARCITY_PERCENTILE,
) -> FlexParticipationBelief:
    """Form the company's ex-ante flex participation belief from the OBSERVED
    price alone. It predicts dispatch in the top-`price_percentile` price
    periods (its scarcity proxy) and expects utilisation revenue there at the
    observed price. Reads NO SIM internal -- only the price a supplier sees."""
    price = np.asarray(list(observed_price), dtype=float)
    if price.size == 0:
        raise ValueError("form_participation_belief: empty observed price series")
    thr = float(np.percentile(price, price_percentile))
    predicted = price >= thr
    expected_mwh = np.where(predicted, enrolled_mw * period_hours, 0.0)
    expected_revenue = expected_mwh * price
    return FlexParticipationBelief(
        expected_utilised_revenue=expected_revenue,
        predicted_dispatch_mask=predicted,
        observed_price=price,
        enrolled_mw=enrolled_mw,
        period_hours=period_hours,
        price_percentile=price_percentile,
    )


# The company's baseline-estimation bias (L2). 0.0 = an unbiased counterfactual
# methodology; >0 over-states the baseline (claims more reduction than real,
# clawback exposure); <0 under-states. A COMPANY BELIEF parameter -- the SIM's
# true baseline is not readable across the wall.
DEFAULT_BASELINE_BIAS: float = 0.0


@dataclass(frozen=True)
class FlexParticipationBeliefL2:
    """The company's L2 flex participation belief: L1 price-proxy dispatch plus
    a LEARNED delivery de-rating and a (possibly biased) baseline estimate.

    `expected_utilised_revenue` is the de-rated per-period forecast the harness
    scores; `learned_delivery_ratio` is what the company inferred from its own
    settlement; `estimated_baseline_mwh` is its counterfactual estimate whose
    error vs the SIM truth is the company's baseline-methodology exposure."""

    expected_utilised_revenue: np.ndarray   # per-period, GBP (de-rated)
    predicted_dispatch_mask: np.ndarray     # bool, price-proxy guess (as L1)
    observed_price: np.ndarray
    learned_delivery_ratio: float           # inferred from own settlement
    estimated_baseline_mwh: float           # per-event counterfactual estimate
    baseline_bias: float
    enrolled_mw: float
    period_hours: float
    price_percentile: float

    @property
    def total_expected_revenue_gbp(self) -> float:
        return float(self.expected_utilised_revenue.sum())

    @property
    def n_predicted_dispatch(self) -> int:
        return int(self.predicted_dispatch_mask.sum())


def learn_delivery_ratio(
    observed_delivery_mwh: Optional[Sequence[float]],
    *,
    instructed_mwh: float,
) -> float:
    """Infer the portfolio's realised delivery ratio from the company's OWN
    past settlement observables: mean(metered delivery) / instructed volume.
    Both quantities are on the company's statement (metered delivery crosses
    the seam; instructed volume is its own enrolled capacity x window) -- no
    SIM internal is read. Cold start (no history) => 1.0, i.e. the company
    falls back to the L1 perfect-delivery assumption until it has evidence.
    FAIL-CLOSED on a non-positive instructed volume (a degenerate enrolment)."""
    if instructed_mwh <= 0.0:
        raise ValueError("learn_delivery_ratio: instructed_mwh must be > 0")
    if not observed_delivery_mwh:
        return 1.0
    arr = np.asarray(list(observed_delivery_mwh), dtype=float)
    if arr.size == 0:
        return 1.0
    return float(np.clip(arr.mean() / instructed_mwh, 0.0, 1.0))


def form_participation_belief_l2(
    observed_price: Sequence[float],
    *,
    enrolled_mw: float,
    period_hours: float,
    observed_delivery_mwh: Optional[Sequence[float]] = None,
    price_percentile: float = DEFAULT_PRICE_SCARCITY_PERCENTILE,
    baseline_bias: float = DEFAULT_BASELINE_BIAS,
) -> FlexParticipationBeliefL2:
    """Form the company's L2 flex participation belief. Dispatch prediction is
    the L1 price-proxy (top-percentile observed price). Two L2 refinements:

      * DELIVERY DE-RATING -- the expected delivered volume is de-rated by the
        ratio LEARNED from the company's own past settlement observables
        (`observed_delivery_mwh`), instead of the L1 perfect-delivery
        assumption. This is the company coping better with a portfolio that
        under-delivers, still wrong by the sampling error of a finite history.
      * BASELINE ESTIMATE -- the company estimates its per-event counterfactual
        baseline with a (possibly biased) methodology; `estimated_baseline_mwh`
        is exposed so the harness can score the baseline-methodology error
        against the SIM truth (the company cannot see that gap itself).

    Reads NO SIM internal -- only observed price + the company's own settlement
    history + its own enrolment."""
    price = np.asarray(list(observed_price), dtype=float)
    if price.size == 0:
        raise ValueError("form_participation_belief_l2: empty observed price series")
    instructed_mwh = enrolled_mw * period_hours
    thr = float(np.percentile(price, price_percentile))
    predicted = price >= thr
    learned_ratio = learn_delivery_ratio(observed_delivery_mwh, instructed_mwh=instructed_mwh)
    estimated_baseline = instructed_mwh * (1.0 + baseline_bias)
    # De-rated expected delivered volume in the predicted-dispatch periods.
    expected_mwh = np.where(predicted, instructed_mwh * learned_ratio, 0.0)
    expected_revenue = expected_mwh * price
    return FlexParticipationBeliefL2(
        expected_utilised_revenue=expected_revenue,
        predicted_dispatch_mask=predicted,
        observed_price=price,
        learned_delivery_ratio=learned_ratio,
        estimated_baseline_mwh=estimated_baseline,
        baseline_bias=baseline_bias,
        enrolled_mw=enrolled_mw,
        period_hours=period_hours,
        price_percentile=price_percentile,
    )


def realised_revenue_from_settlement(lines: Optional[List[FlexSettlementLine]]) -> float:
    """Sum the company's OWN observable settlement lines -- its realised
    utilisation revenue as read off its statement (observation, not truth).
    Tolerant of an empty / one-at-a-time / out-of-order feed (C-S1): each line
    is independently additive, no batch-completeness assumption."""
    if not lines:
        return 0.0
    return float(sum(line.utilisation_payment_gbp for line in lines))


# ===========================================================================
# L3 -- STACKED MULTI-VENUE PARTICIPATION, and the POINT-IN-TIME split
#
# WHAT A REAL STACKING PARTY KNOWS (still nothing more):
#   * its OWN offers into each venue -- how much MW it promised where, in what
#     priority order, and (for an availability product) the price IT WON at.
#     This is its own contract, not a world observable: no seam field needed.
#   * its OWN per-venue dispatch-instruction feed -- so it can see that two
#     venues called it in the SAME window. It CANNOT see which venue the
#     physics actually served, nor the portfolio-wide allocation.
#   * its OWN per-venue settlement lines -- metered delivery, utilisation
#     payment. It FEELS contention as an unexplained metering shortfall.
#
# WHAT IT DOES NOT KNOW, and is therefore ALLOWED TO GET WRONG (the point):
#   1. WHETHER CONTENTION WILL BIND. The default belief is NAIVE (awareness 0
#      on a cold start): it books each venue's revenue as if the whole
#      portfolio were free for that venue -- the classic DOUBLE-COUNT of the
#      same MW that real aggregators are penalised for. As instruction history
#      accumulates it LEARNS an overlap frequency from its own feed and nets
#      that fraction. It stays wrong because overlap frequency is a past
#      sample, overlap is not the same thing as BINDING, and the world's
#      priority allocation is unobservable.
#   2. ITS OWN CLAWBACK EXPOSURE. The availability clawback is not carried on
#      the settlement seam, so the company must FORECAST it from its own
#      contention belief. A naive stacker forecasts none.
#
# POINT-IN-TIME BLINDFOLD (`as_of`). Without `as_of` the de-rating and the
# contention rate are learned IN-SAMPLE from the same window that is then
# scored -- honest for an L2 steady-state reading, but not a forecast. With
# `as_of` the company learns ONLY from observables whose settlement window
# CLOSED at or before `as_of` (`past_only` + the `assert_point_in_time` guard,
# which FAILS LOUD on a future-dated observable), takes its price thresholds
# from PAST prices only, and forecasts the periods AFTER `as_of`. The guard and
# the filter are INDEPENDENT (one selects, the other verifies), which is what
# lets the R15 mutation test break the filter and watch the guard fire.
#
# NO WORLD IMPORT. Everything below is numpy + the observable seam type + the
# company's own records. The allocation model here is the COMPANY'S OWN
# construction (a probability-weighted mixture over its declared priority), not
# a copy of the world's allocator -- independent machinery, so the harness gap
# is a real form-inadequacy measurement rather than a tautology (R15).
# ===========================================================================

# Cold-start contention awareness. 0.0 = FULLY NAIVE: the company assumes it can
# sell the same MW into every venue at once. This is a BELIEF default, not a
# control default -- the honest starting position of a party that has never yet
# seen two venues call the same window (and the failure mode the harness
# measures). `contention_awareness=None` means LEARN it from the own-instruction
# feed instead of assuming it.
DEFAULT_CONTENTION_AWARENESS: float = 0.0


class PointInTimeViolation(ValueError):
    """A learning input was dated AFTER the as-of instant -- the company would be
    learning from information it could not yet have. FAIL-LOUD: silently
    tolerating one future-dated settlement line is exactly how an in-sample
    result gets published as a forecast."""


@dataclass(frozen=True)
class CompanyVenueOffer:
    """The company's OWN record of one venue it participates in -- its offer, its
    declared dispatch priority, and (for an availability product) the price IT
    won at. All company-owned contract data; none of it crosses the wall.

    `venue` is the market-function key (the same string that appears on the
    company's own instruction/settlement lines), so a second geography's venue
    needs no new shape here. FAIL-LOUD on a missing availability price: a
    defaulted 0 would silently model an availability product as free."""

    venue: str
    offered_mw: float
    priority: int
    is_availability: bool = False
    availability_price_gbp_per_mw_hour: Optional[float] = None
    nondelivery_clawback_multiple: float = 1.0

    def __post_init__(self) -> None:
        if not math.isfinite(float(self.offered_mw)) or self.offered_mw <= 0.0:
            raise ValueError(f"CompanyVenueOffer {self.venue}: offered_mw must be finite > 0")
        p = self.availability_price_gbp_per_mw_hour
        if self.is_availability:
            if p is None or not math.isfinite(float(p)) or float(p) <= 0.0:
                raise ValueError(
                    f"CompanyVenueOffer {self.venue}: an availability product requires the "
                    "price the company actually won at (finite > 0) -- there is no default, "
                    "because a defaulted price is a fabricated one")
        elif p is not None:
            raise ValueError(
                f"CompanyVenueOffer {self.venue}: a utilisation product is paid per delivered "
                "MWh; an availability price here would double-count the same product")


def _as_datetime(x) -> dt.datetime:
    """Coerce an observable date/timestamp to a datetime. Accepts datetime, date,
    or an ISO-ish string (the first 10 chars parsed as a date, matching how the
    company reads a settlement calendar). Pure parsing -- no world access."""
    if isinstance(x, dt.datetime):
        return x
    if isinstance(x, dt.date):
        return dt.datetime(x.year, x.month, x.day)
    s = str(x)
    return dt.datetime.strptime(s[:10], "%Y-%m-%d")


def past_only(items: Optional[Sequence], as_of) -> List:
    """THE FILTER: keep only observables whose settlement window had CLOSED at or
    before `as_of` -- what the company could actually have known then. Items are
    matched on their own `window_end` (an observable field on both the dispatch
    instruction and the settlement line). A missing/None `as_of` means no
    point-in-time constraint was declared and everything is kept (the in-sample
    L2 path, explicit rather than implied)."""
    if not items:
        return []
    if as_of is None:
        return list(items)
    cut = _as_datetime(as_of)
    return [i for i in items if _as_datetime(getattr(i, "window_end")) <= cut]


def assert_point_in_time(items: Optional[Sequence], as_of, *, what: str = "observables") -> int:
    """THE GUARD, independent of the filter: raise `PointInTimeViolation` if ANY
    retained item is dated after `as_of`. Returns how many items were verified.

    R15 discipline: this cannot fail open. `as_of=None` is rejected (a guard with
    nothing to compare against is an unavailable guard = a FAILED guard, not a
    pass), an item lacking `window_end` is rejected rather than skipped, and a
    non-finite/unparseable date raises. An EMPTY input returns 0 verified --
    legitimate (a cold-start company has no history) and reported so a caller can
    tell "verified nothing" from "verified 400 items"."""
    if as_of is None:
        raise ValueError(
            f"assert_point_in_time({what}): as_of is required -- a point-in-time guard "
            "with no as-of instant cannot fail, so it must not be allowed to pass")
    cut = _as_datetime(as_of)
    checked = 0
    for i in items or []:
        if not hasattr(i, "window_end"):
            raise PointInTimeViolation(
                f"assert_point_in_time({what}): item {i!r} carries no window_end -- an "
                "undateable observable cannot be proven to be past information")
        end = _as_datetime(i.window_end)
        if end > cut:
            raise PointInTimeViolation(
                f"assert_point_in_time({what}): observable ending {end.isoformat()} is AFTER "
                f"as_of {cut.isoformat()} -- the company would be learning from the future")
        checked += 1
    return checked


def learn_delivery_ratio_from_lines(
    lines: Optional[Sequence[FlexSettlementLine]],
    offers: Sequence[CompanyVenueOffer],
    *,
    period_hours: float,
) -> float:
    """Learn the portfolio's realised delivery ratio across a MULTI-VENUE book,
    from the company's own settlement lines: mean over lines of (metered
    delivery / what that venue was instructed for). Multi-venue-aware because a
    single ratio over raw MWh would be dominated by whichever venue offered more.

    Cold start (no lines) -> 1.0, the L1 perfect-delivery assumption. FAIL-LOUD
    on a line for a venue the company does not offer (a book/feed mismatch is a
    defect, not something to silently drop) and on a non-positive
    `period_hours`."""
    if not math.isfinite(float(period_hours)) or period_hours <= 0.0:
        raise ValueError("learn_delivery_ratio_from_lines: period_hours must be finite > 0")
    by_venue = {o.venue: o for o in offers}
    if not by_venue:
        raise ValueError("learn_delivery_ratio_from_lines: no offers -- nothing to learn against")
    ratios: List[float] = []
    for line in lines or []:
        key = str(getattr(line.venue, "value", line.venue))
        offer = by_venue.get(key)
        if offer is None:
            raise ValueError(
                f"learn_delivery_ratio_from_lines: settlement line for venue {key!r} which the "
                "company has no offer in -- unreconciled statement, refusing to learn from it")
        instructed = offer.offered_mw * float(period_hours)
        ratios.append(float(line.metered_delivery_mwh) / instructed)
    if not ratios:
        return 1.0
    return float(np.clip(float(np.mean(ratios)), 0.0, 1.0))


def learn_contention_rate(instructions: Optional[Sequence]) -> float:
    """Learn, from the company's OWN dispatch-instruction feed, how often MORE
    THAN ONE venue called it in the SAME settlement window -- its only
    observable handle on stacking contention.

    = (# windows in which >= 2 distinct venues were instructed) / (# windows with
    any instruction). Cold start (no feed) -> 0.0, i.e. FULLY NAIVE. That zero is
    a BELIEF (a party with no evidence of contention assumes none, and gets
    punished for it -- the failure mode this atom exists to measure), never a
    control passing on empty input."""
    windows: Dict[dt.datetime, set] = {}
    for instr in instructions or []:
        start = _as_datetime(getattr(instr, "window_start"))
        key = str(getattr(instr.venue, "value", instr.venue))
        windows.setdefault(start, set()).add(key)
    if not windows:
        return 0.0
    overlapped = sum(1 for venues in windows.values() if len(venues) > 1)
    return float(overlapped) / float(len(windows))


def learn_venue_call_rates(
    instructions: Optional[Sequence], *, n_observed_periods: int,
) -> Dict[str, float]:
    """Learn each venue's CALL FREQUENCY from the company's own instruction feed:
    (# periods this venue instructed me) / (# periods I have been watching). A
    real party knows both numbers. This is how the company discovers that an
    availability venue calls far more rarely than a balancing venue -- it never
    reads the world's call thresholds.

    FAIL-LOUD on a non-positive observation window (dividing by nothing would
    fabricate a rate)."""
    if int(n_observed_periods) <= 0:
        raise ValueError(
            "learn_venue_call_rates: n_observed_periods must be > 0 -- a rate over an "
            "empty observation window is not a measurement")
    counts: Dict[str, int] = {}
    for instr in instructions or []:
        key = str(getattr(instr.venue, "value", instr.venue))
        counts[key] = counts.get(key, 0) + 1
    return {k: min(1.0, v / float(n_observed_periods)) for k, v in counts.items()}


def _allocate_by_declared_priority(
    offers: Sequence[CompanyVenueOffer], called: Mapping[str, bool], portfolio_mw: float,
) -> Dict[str, float]:
    """The COMPANY'S OWN model of what its portfolio could actually deliver if
    every called venue wanted MW at once: serve its declared priority order until
    the portfolio runs out. Deliberately the company's own construction -- it has
    never seen the world's allocator, it only knows the order it declared."""
    remaining = float(portfolio_mw)
    out: Dict[str, float] = {}
    for offer in sorted(offers, key=lambda o: (o.priority, o.venue)):
        if not called.get(offer.venue):
            out[offer.venue] = 0.0
            continue
        take = min(float(offer.offered_mw), remaining if remaining > 0.0 else 0.0)
        out[offer.venue] = take
        remaining -= take
    return out


@dataclass(frozen=True)
class StackedParticipationBelief:
    """The company's L3 belief about a STACKED book: per-venue expected delivery
    and revenue, the de-rating and contention rate it LEARNED from its own
    observables, and (when a point-in-time split was declared) the forecast
    window the belief is actually a forecast FOR.

    `expected_delivered_mwh` is the price-free physical vector the harness scores
    (no un-sourced GBP figure can move it); `expected_revenue_gbp` is the money
    view including the company's forecast of its own availability clawback."""

    expected_delivered_mwh: np.ndarray            # per period, total across venues
    expected_revenue_gbp: np.ndarray              # per period, total across venues
    per_venue_delivered_mwh: Dict[str, np.ndarray]
    per_venue_revenue_gbp: Dict[str, np.ndarray]
    predicted_call_mask: Dict[str, np.ndarray]    # per venue, price-proxy guess
    observed_price: np.ndarray
    portfolio_mw: float
    period_hours: float
    learned_delivery_ratio: float
    learned_contention_rate: float
    contention_awareness: float
    learned_call_rates: Dict[str, float]
    expected_clawback_gbp: float
    forecast_mask: np.ndarray                     # periods this belief forecasts
    as_of: Optional[dt.datetime]
    n_train_periods: int
    n_train_observables: int

    @property
    def total_expected_delivered_mwh(self) -> float:
        return float(self.expected_delivered_mwh.sum())

    @property
    def total_expected_revenue_gbp(self) -> float:
        return float(self.expected_revenue_gbp.sum())

    @property
    def n_predicted_contended_periods(self) -> int:
        """Periods where the company itself expects >1 venue to call it."""
        if not self.predicted_call_mask:
            return 0
        stack = np.vstack([m.astype(int) for m in self.predicted_call_mask.values()])
        return int((stack.sum(axis=0) > 1).sum())


def form_stacked_belief(
    observed_price: Sequence[float],
    *,
    offers: Sequence[CompanyVenueOffer],
    portfolio_mw: float,
    period_hours: float,
    observed_dates: Optional[Sequence] = None,
    observed_instructions: Optional[Sequence] = None,
    observed_settlement_lines: Optional[Sequence[FlexSettlementLine]] = None,
    contention_awareness: Optional[float] = None,
    price_percentile: float = DEFAULT_PRICE_SCARCITY_PERCENTILE,
    as_of=None,
) -> StackedParticipationBelief:
    """Form the company's STACKED, multi-venue participation belief from
    observables only.

    Per venue it predicts calls in the top price band, with the band WIDTH set by
    the call frequency it has observed for that venue (so a rarely-calling
    availability venue is forecast rarely -- learned, never read). It then models
    contention with a probability-weighted mixture between the NAIVE view (every
    venue gets the whole portfolio -- double-counting) and the FULLY-NETTED view
    (its declared priority order under the portfolio cap):

        expected_mw[v] = naive[v] - awareness * (naive[v] - netted[v])

    `contention_awareness=None` LEARNS the weight from the company's own
    instruction feed (`learn_contention_rate`); an explicit float overrides it
    (0 = fully naive, 1 = fully netted) -- which is also how the R15 test proves
    the harness's over-claim measure fires on naivety and not otherwise.

    `as_of` turns on the POINT-IN-TIME split: learning inputs are filtered to
    closed-window observables and verified by `assert_point_in_time`, price
    thresholds come from past prices only, and `forecast_mask` marks the future
    periods the belief is a genuine forecast for. Without `as_of` the belief is
    in-sample (the L2 reading) and `forecast_mask` is every period.

    Reads NO world internal: observed price, its own dates, its own instruction
    and settlement feeds, its own offers."""
    price = np.asarray(list(observed_price), dtype=float)
    if price.size == 0:
        raise ValueError("form_stacked_belief: empty observed price series")
    if not np.all(np.isfinite(price)):
        raise ValueError("form_stacked_belief: non-finite observed price")
    book = list(offers)
    if not book:
        raise ValueError("form_stacked_belief: no venue offers -- nothing to stack")
    keys = [o.venue for o in book]
    if len(set(keys)) != len(keys):
        raise ValueError(f"form_stacked_belief: duplicate venue offers {keys}")
    if not math.isfinite(float(portfolio_mw)) or portfolio_mw <= 0.0:
        raise ValueError("form_stacked_belief: portfolio_mw must be finite > 0")
    if not math.isfinite(float(period_hours)) or period_hours <= 0.0:
        raise ValueError("form_stacked_belief: period_hours must be finite > 0")

    # -- POINT-IN-TIME window -------------------------------------------------
    as_of_dt: Optional[dt.datetime] = None
    if as_of is not None:
        if observed_dates is None:
            raise ValueError(
                "form_stacked_belief: as_of given without observed_dates -- a point-in-time "
                "split needs the calendar it is splitting")
        dates = [_as_datetime(d) for d in observed_dates]
        if len(dates) != price.size:
            raise ValueError(
                f"form_stacked_belief: observed_dates ({len(dates)}) and price ({price.size}) "
                "must be the same length")
        as_of_dt = _as_datetime(as_of)
        train_mask = np.array([d <= as_of_dt for d in dates], dtype=bool)
        forecast_mask = ~train_mask
        if not train_mask.any():
            raise ValueError(
                "form_stacked_belief: point-in-time split leaves an EMPTY training window "
                "-- refusing to report a forecast learned from nothing")
        if not forecast_mask.any():
            raise ValueError(
                "form_stacked_belief: point-in-time split leaves an EMPTY forecast window "
                "-- an as-of after the last period is an in-sample result in disguise")
    else:
        train_mask = np.ones_like(price, dtype=bool)
        forecast_mask = np.ones_like(price, dtype=bool)

    # -- learning inputs, filtered to the past and then VERIFIED (independently)
    train_instructions = past_only(observed_instructions, as_of_dt)
    train_lines = past_only(observed_settlement_lines, as_of_dt)
    n_verified = 0
    if as_of_dt is not None:
        n_verified = (assert_point_in_time(train_instructions, as_of_dt, what="instructions")
                      + assert_point_in_time(train_lines, as_of_dt, what="settlement lines"))
    else:
        n_verified = len(train_instructions) + len(train_lines)

    learned_ratio = learn_delivery_ratio_from_lines(
        train_lines, book, period_hours=period_hours)
    learned_contention = learn_contention_rate(train_instructions)
    n_train_periods = int(train_mask.sum())
    call_rates = learn_venue_call_rates(
        train_instructions, n_observed_periods=n_train_periods)

    if contention_awareness is None:
        awareness = learned_contention
    else:
        awareness = float(contention_awareness)
        if not math.isfinite(awareness) or not (0.0 <= awareness <= 1.0):
            raise ValueError(
                f"form_stacked_belief: contention_awareness must be in [0, 1], "
                f"got {contention_awareness!r}")

    # -- per-venue predicted call mask: top price band, width from the OBSERVED
    #    call rate (cold start -> the default scarcity percentile) ------------
    train_prices = price[train_mask]
    predicted: Dict[str, np.ndarray] = {}
    for offer in book:
        rate = call_rates.get(offer.venue)
        if rate is None or rate <= 0.0:
            q = float(price_percentile)
        else:
            q = float(np.clip(100.0 * (1.0 - rate), 0.1, 99.9))
        thr = float(np.percentile(train_prices, q))
        predicted[offer.venue] = price >= thr

    # -- contention mixture, per period ---------------------------------------
    per_venue_mw: Dict[str, np.ndarray] = {o.venue: np.zeros_like(price) for o in book}
    for p in range(price.size):
        called = {o.venue: bool(predicted[o.venue][p]) for o in book}
        if not any(called.values()):
            continue
        netted = _allocate_by_declared_priority(book, called, portfolio_mw)
        for o in book:
            if not called[o.venue]:
                continue
            naive = float(o.offered_mw)
            per_venue_mw[o.venue][p] = naive - awareness * (naive - netted[o.venue])

    # -- expected delivery + revenue ------------------------------------------
    per_venue_mwh: Dict[str, np.ndarray] = {}
    per_venue_rev: Dict[str, np.ndarray] = {}
    clawback_total = 0.0
    for o in book:
        mwh = per_venue_mw[o.venue] * float(period_hours) * learned_ratio
        per_venue_mwh[o.venue] = mwh
        if not o.is_availability:
            per_venue_rev[o.venue] = mwh * price
        else:
            ap = float(o.availability_price_gbp_per_mw_hour)
            paid = np.full_like(price, ap * o.offered_mw * float(period_hours))
            # The company's OWN forecast of its clawback: in the periods it
            # expects to be called, the MW it expects NOT to be able to deliver,
            # weighted by how likely it thinks contention is to bind. A naive
            # stacker (awareness 0) forecasts ZERO clawback -- and is wrong.
            shortfall = np.zeros_like(price)
            for p in np.nonzero(predicted[o.venue])[0]:
                shortfall[p] = max(0.0, float(o.offered_mw) - per_venue_mw[o.venue][p])
            claw = (float(o.nondelivery_clawback_multiple) * ap * shortfall
                    * float(period_hours))
            clawback_total += float(claw.sum())
            per_venue_rev[o.venue] = paid - claw

    total_mwh = np.sum([per_venue_mwh[k] for k in keys], axis=0)
    total_rev = np.sum([per_venue_rev[k] for k in keys], axis=0)

    return StackedParticipationBelief(
        expected_delivered_mwh=total_mwh,
        expected_revenue_gbp=total_rev,
        per_venue_delivered_mwh=per_venue_mwh,
        per_venue_revenue_gbp=per_venue_rev,
        predicted_call_mask=predicted,
        observed_price=price,
        portfolio_mw=float(portfolio_mw),
        period_hours=float(period_hours),
        learned_delivery_ratio=learned_ratio,
        learned_contention_rate=learned_contention,
        contention_awareness=awareness,
        learned_call_rates=call_rates,
        expected_clawback_gbp=clawback_total,
        forecast_mask=forecast_mask,
        as_of=as_of_dt,
        n_train_periods=n_train_periods,
        n_train_observables=int(n_verified),
    )
