"""The flex-observable seam -- atom W1_9_dsr_flex_markets (L1), the SEAM
third of the DSR/flexibility coupled triad (SIM flex-need + dispatch /
this seam / company flex-participation / the revenue-gap harness).

WHAT THIS IS: a typed, versioned request/response contract exposing the
demand-side-response / flexibility world to the company layer exactly as a
real UK aggregator / VLP / supplier would receive it -- off a dispatch
instruction (a NESO Bid-Offer Acceptance), a settlement statement line
(Elexon-settled utilisation), or an enrolment/offer submission. It is
expressed in the generic ``WallRequest``/``WallResponse`` envelope
(``wall_envelope.py``) instantiated for the flex crossing specifically,
the same idiom as ``payment_observable_seam.py``
(docs/design/frame/W1_9_dsr_flex_markets_FRAME.md §7).

THE EPISTEMIC-WALL GUARANTEE (binding on every dataclass below): every
field answers YES to "could a real UK flex party know this from its own
dispatch instruction / settlement statement alone?" None of these types may
carry:
  * the SIM's TRUE system need / true residual margin / merit-order internals,
  * the TRUE counterfactual baseline (what demand WOULD have been) -- a real
    party only ever sees a *measured* baseline on its statement, and at L1
    baseline is trivial so it is not carried here at all,
  * any model parameter, probability, or hidden scarcity signal.
The company's own INFERENCE of when flex is worth bidding, how much revenue
to expect, and what it will be measured against is
``company/market/flex_participation.py``'s job, done on the far side of this
seam; the belief-vs-truth GAP between that inference and the SIM's true
system-need is the flex-dispatch triad harness's job to measure. This module
carries neither inference nor ground truth -- only the observation.

ASYNC BY CONSTRUCTION (C-S3, real here, not theoretical): a real BOA is
issued in-day and the Elexon settlement line that pays for it lands days
later, out of order relative to other events. A ``FlexEnrolment``
(WallRequest) submitted today resolves via a ``FlexDispatchInstruction``
(WallResponse) later, and the ``FlexSettlementLine`` (a SEPARATE WallResponse)
later still -- matched only by ``correlation_id`` (see ``wall_envelope``).
Dispatch and settlement are never same-step resolution.

PORTABILITY: ``FlexVenue`` is keyed by MARKET FUNCTION (balancing /
capacity / turn-down / local-constraint), not a hardcoded GB venue name --
a second geography's flex market adds a member here, never a new dataclass
shape (CLAUDE.md portability lens).

NO SIM/GENERATOR/COMPANY SYMBOL: this module imports nothing from ``sim``,
``simulation``, or ``company`` -- it is pure contract, checked by
``tests/interface/test_flex_observable_seam.py::test_no_sim_or_company_import``.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum

from interface.contracts.wall_envelope import WallRequest, WallResponse

SCHEMA_VERSION = 1


class FlexVenue(str, Enum):
    """The flex MARKET FUNCTION, not a counterparty. Portability: a second
    geography adds a member here, never a new dataclass shape. L1 uses only
    ``BALANCING_MECHANISM`` (one BM-like venue); the rest are declared so the
    L2/L3 venue expansion (Capacity Market, DFS turn-down, DNO/DSO local) is
    an enum addition, not a schema change."""

    BALANCING_MECHANISM = "balancing_mechanism"
    CAPACITY_MARKET = "capacity_market"
    DFS_TURN_DOWN = "dfs_turn_down"
    DSO_LOCAL_CONSTRAINT = "dso_local_constraint"
    OTHER = "other"


class FlexDirection(str, Enum):
    """Turn demand DOWN (shed/shift away) or UP (soak surplus). L1 models
    turn-down against a scarcity call; turn-up is declared for symmetry."""

    TURN_DOWN = "turn_down"
    TURN_UP = "turn_up"


# ---------------------------------------------------------------------------
# Request payload -- COMPANY -> WORLD: the party offering flex into a venue.
# Company-owned data only (the capacity IT chose to enrol, the window IT
# declares); the epistemic wall polices what flows BACK across the seam, not
# what the company already possesses and sends out.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FlexEnrolment:
    """Payload of ``WallRequest[FlexEnrolment]``: an offer of ``offered_mw``
    of flexibility into ``venue`` over an availability window, in
    ``direction``. Crosses COMPANY -> WORLD; resolution is a
    ``FlexDispatchInstruction`` (if called) and later a ``FlexSettlementLine``,
    arriving asynchronously (C-S3), keyed back to this request's
    ``correlation_id`` alone.

    ``offered_mw`` is the company's OWN participation-size decision -- an
    input, not a sourced benchmark. The triad gap is scale-invariant in it
    (both truth and belief scale together), so no fabricated MW figure
    contaminates the score."""

    unit_id: str
    venue: FlexVenue
    offered_mw: float
    direction: FlexDirection
    window_start: dt.datetime
    window_end: dt.datetime


# ---------------------------------------------------------------------------
# Observable response payloads -- WORLD -> COMPANY. Every field here is the
# load-bearing epistemic-wall surface: OBSERVATION ONLY, never truth.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FlexDispatchInstruction:
    """Observable: a dispatch instruction (a NESO Bid-Offer Acceptance for
    the BM venue) -- "deliver ``direction`` over [window_start, window_end)
    at cleared price ``cleared_price_gbp_per_mwh``." This is what a real
    party reads off its instruction feed: WHEN it was called and the price
    it cleared at. It carries NO reason for the call -- the true system need
    / residual tightness that provoked it is SIM-internal and never appears
    here (the company must INFER stress from the observable price, not read
    it off the instruction)."""

    instruction_id: str
    unit_id: str
    venue: FlexVenue
    direction: FlexDirection
    window_start: dt.datetime
    window_end: dt.datetime
    cleared_price_gbp_per_mwh: float


@dataclass(frozen=True)
class FlexSettlementLine:
    """Observable: one settlement statement line -- the Elexon-settled
    utilisation payment for a delivered dispatch. Carries the METERED
    delivery and the utilisation price bid against (the observed outturn
    price a supplier reads as Elexon SSP), never the TRUE counterfactual
    baseline or true system need.

    L1 NAMED SIMPLIFICATION (R10): baseline is trivial and delivery is
    perfect, so ``metered_delivery_mwh`` equals the instructed volume and no
    ``measured_baseline`` field is carried. L2 adds the measured-baseline
    field + stochastic delivery + an availability/utilisation split; those
    are additive fields, not a schema reshape."""

    settlement_id: str
    unit_id: str
    venue: FlexVenue
    window_start: dt.datetime
    window_end: dt.datetime
    metered_delivery_mwh: float
    utilisation_price_gbp_per_mwh: float
    utilisation_payment_gbp: float


# ---------------------------------------------------------------------------
# Envelope specialisations -- the ONLY sanctioned typed shape crossing this
# seam. Company (``company/market``) and SIM (``sim/flex_dispatch``) adapters
# depend on these, never on each other.
# ---------------------------------------------------------------------------

FlexEnrolmentWallRequest = WallRequest[FlexEnrolment]
FlexDispatchWallResponse = WallResponse[FlexDispatchInstruction]
FlexSettlementWallResponse = WallResponse[FlexSettlementLine]


# Every observable payload type this seam is permitted to carry in a
# WallResponse -- the epistemic-wall test enumerates exactly this list so a
# future payload addition is forced to pass the same field-level scrutiny.
OBSERVABLE_RESPONSE_PAYLOAD_TYPES: tuple[type, ...] = (
    FlexDispatchInstruction,
    FlexSettlementLine,
)

# Field names that would leak the SIM's hidden truth across this seam -- the
# wall test asserts none of the observable payloads carries any of these.
FORBIDDEN_TRUTH_FIELDS: tuple[str, ...] = (
    "residual_mw",
    "residual_demand",
    "true_baseline",
    "true_baseline_mwh",
    "true_need",
    "system_need_mw",
    "true_counterfactual",
    "scarcity_true",
)
