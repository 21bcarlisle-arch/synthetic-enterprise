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
(WallRequest) submitted today is answered by a ``FlexEnrolmentOutcome``
(WallResponse) -- the venue's registration acknowledgement, and the ONLY
terminal of that exchange -- while the ``FlexDispatchInstruction`` and the
``FlexSettlementLine`` that may follow are LATER, SEPARATE crossings about
periods rather than about the registration. Nothing resolves in the step that
provoked it.

WHAT THIS HEADER SAID UNTIL EP6 PASS 52, AND WHY IT IS WRITTEN DOWN. It said an
enrolment "resolves via a FlexDispatchInstruction later", and that sentence was
the seam's whole request leg: no module in this build ever constructed a
``FlexEnrolment``, so every instruction and settlement line crossed as an answer
to a question nobody had asked -- ``tools.wall_channel_census`` read the seam as
UNSOLICITED INBOUND for exactly that reason, and the world dispatched a unit no
company had ever registered. The registration exchange below is the repair.

STILL UNREPAIRED HERE, named rather than left to be found: the dispatch
instruction and the settlement line for one period are two different
``WallResponse``s carrying ONE ``correlation_id``, which ``WallResponse``'s own
docstring calls a broken contract ("a consumer is entitled to treat the second
as a restatement of the first"). The shape that fixes it exists --
``WallInterim`` (EP6 pass 44), which is what a message meaning "you were called,
payment is still owed" actually is -- and moving those two legs onto it is a
separate pass, because it changes every consumer of both feeds.

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

# v2, EP6 pass 52: bumped in the SAME EDIT that re-pins this seam in
# `tools/wall_channel_census.py::SURFACE_PINS`, which is the only lawful reason
# to touch either line. WHAT THE SURFACE GAINED: `FlexEnrolmentOutcome`, the
# venue's ANSWER to an enrolment -- the response leg of the exchange this seam
# has declared since it was written and this build had never held either end of.
# The observable-vs-hidden judgement on its three fields is made at the dataclass
# itself, where an editor meets it: a registration reference the venue mints, and
# the unit and venue it was minted against. Nothing about the venue's own
# reasoning, capacity or merit order crosses -- an acceptance says THAT you are
# registered, never why or against what else.
SCHEMA_VERSION = 2


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


# The request payload's field set, DECLARED here for the same reason
# `OBSERVABLE_PAYLOAD_FIELDS` is (below): the counterparty may not import the
# company's codec, so its decoder needs a PUBLISHED statement of what an
# enrolment carries to refuse against. Written out rather than derived from the
# dataclass -- a set derived from its subject widens whenever the subject does
# and is the R15 TAUTOLOGY for the one question it is asked.
#
# This is the OUTBOUND direction and it is NOT the epistemic wall: the company
# already owns every field here. What the world may not do is DEFAULT one of
# them -- an enrolment silently read as offering 0 MW over an unbounded window
# is a registration the company never made.
REQUEST_PAYLOAD_FIELDS: dict[str, tuple[str, ...]] = {
    "FlexEnrolment": (
        "unit_id",
        "venue",
        "offered_mw",
        "direction",
        "window_start",
        "window_end",
    ),
}

# The venue's declared REFUSAL vocabulary -- the `ErrorDetail.code` set a
# rejected enrolment may carry, published so the company can branch on the
# reason it was refused instead of parsing prose, and so a code neither side
# recognises is a contract violation rather than a shrug.
#
# EVERY MEMBER IS STRUCTURAL, and that is a deliberate line rather than an
# omission: a venue in this build refuses an enrolment it CANNOT REGISTER, never
# one it does not fancy. An economic refusal (too small, too expensive, merit
# order full) would be a difficulty parameter, which is the director's
# curriculum instrument under R13 and not a thing this seam may invent.
ENROLMENT_REFUSAL_CODES: tuple[str, ...] = (
    "WINDOW_NOT_A_WINDOW",       # window_end at or before window_start
    "OFFER_NOT_DELIVERABLE",     # offered_mw is not a finite positive volume
    "WINDOW_ALREADY_CLOSED",     # the availability window ended before the venue read it
    "UNIT_ALREADY_ENROLLED",     # this unit is already registered here over an overlapping window
)


# ---------------------------------------------------------------------------
# Observable response payloads -- WORLD -> COMPANY. Every field here is the
# load-bearing epistemic-wall surface: OBSERVATION ONLY, never truth.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FlexEnrolmentOutcome:
    """Observable: the venue ACCEPTED this unit's enrolment, and here is the
    reference it minted for it. The answer to a ``WallRequest[FlexEnrolment]``
    and the only terminal this seam's request leg has.

    WHY A REFERENCE IS THE WHOLE PAYLOAD. ``enrolment_reference`` is the venue's
    own id for the registration -- the thing a real party quotes on every later
    query about it and CANNOT MINT ITSELF. That is what makes an acceptance
    worth carrying: a boolean would be information the company could have
    assumed, and assuming it is exactly how this build spent forty passes
    dispatching a unit nobody had registered.

    ``unit_id`` and ``venue`` are echoed back because they are what a MIS-ROUTED
    acceptance gets wrong, and the company checks them against its own
    submission rather than believing them (``FlexEnrolmentBook.observe_outcome``).

    WHAT IS DELIBERATELY ABSENT. No accepted volume: at L1 a venue accepts the
    offer or refuses it, so a field whose value is always the request's own
    ``offered_mw`` would be a mirror that no test could fail on. Partial
    acceptance is a real L2 product and lands as an additive field then, with a
    world that can actually produce a number different from the one it was sent.
    No queue position, no clearing price, no indication of who else registered --
    all of that is the venue's internals and none of it appears on a real
    registration acknowledgement.

    A REFUSAL IS NOT THIS TYPE. The envelope already carries one: a rejected
    enrolment is ``WallResponse(status=ERROR, payload=None,
    error=ErrorDetail(code=<one of ENROLMENT_REFUSAL_CODES>))``. Giving this
    dataclass an ``accepted`` flag would create a False branch that duplicates
    the envelope's own ERROR path, and a payload-carrying refusal would violate
    ``WallResponse``'s invariant that a non-OK status carries no payload."""

    enrolment_reference: str
    unit_id: str
    venue: FlexVenue


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
FlexEnrolmentOutcomeWallResponse = WallResponse[FlexEnrolmentOutcome]
FlexDispatchWallResponse = WallResponse[FlexDispatchInstruction]
FlexSettlementWallResponse = WallResponse[FlexSettlementLine]


# Every observable payload type this seam is permitted to carry in a
# WallResponse -- the epistemic-wall test enumerates exactly this list so a
# future payload addition is forced to pass the same field-level scrutiny.
OBSERVABLE_RESPONSE_PAYLOAD_TYPES: tuple[type, ...] = (
    FlexEnrolmentOutcome,
    FlexDispatchInstruction,
    FlexSettlementLine,
)

# THE CLOSED OBSERVABLE FIELD SET -- the wall proper, and the reason
# ``FORBIDDEN_TRUTH_FIELDS`` below is a second belt and not the control.
#
# WHY THIS EXISTS AND WHY IT IS WRITTEN OUT BY HAND. A denylist of truth field
# NAMES answers "is this one of the leaks we already thought of"; it cannot
# answer "could a real UK flex party know this", which is the guarantee this
# module's header actually makes. Measured on 2026-08-20: ``FlexDispatchTruth``
# carries 11 fields and the denylist named 2 of them, so ``true_delivered_mwh``,
# ``true_delivery_ratio`` and ``true_utilised_revenue`` -- SIM ground truth by
# their own names -- encoded onto the wire unrefused. The failure mode is not
# exotic: it is the single most natural edit anyone makes to a settlement line,
# adding one more useful field.
#
# So the codec asks the CLOSED question instead: is every field on this payload
# one the contract has DECLARED observable? Adding a field to a dataclass above
# and nothing else now REFUSES at the point of emission (R15 FAIL-CLOSED). To
# widen the wall you must edit this tuple, and that edit is the epistemic act --
# it is where a reviewer is forced to answer the header's question out loud.
#
# DECLARED HERE, NOT DERIVED. This is deliberately NOT ``get_type_hints`` of the
# dataclass: a set derived from the subject widens whenever the subject does and
# is an R15 TAUTOLOGY for exactly the question being asked. Independence is the
# whole point, which is why the duplication is load-bearing rather than sloppy.
OBSERVABLE_PAYLOAD_FIELDS: dict[str, tuple[str, ...]] = {
    "FlexEnrolmentOutcome": (
        "enrolment_reference",
        "unit_id",
        "venue",
    ),
    "FlexDispatchInstruction": (
        "instruction_id",
        "unit_id",
        "venue",
        "direction",
        "window_start",
        "window_end",
        "cleared_price_gbp_per_mwh",
    ),
    "FlexSettlementLine": (
        "settlement_id",
        "unit_id",
        "venue",
        "window_start",
        "window_end",
        "metered_delivery_mwh",
        "utilisation_price_gbp_per_mwh",
        "utilisation_payment_gbp",
    ),
}

# Field names that would leak the SIM's hidden truth across this seam -- a
# SECOND belt behind OBSERVABLE_PAYLOAD_FIELDS, kept because it still fires on
# the case the closed set cannot see: a truth field added to the dataclass AND
# declared observable in the same edit. The wall test asserts none of the
# observable payloads carries any of these.
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
