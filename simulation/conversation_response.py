"""F1a -- the SIM customer RESPONSE model: the far (world) side of the F1
"simulating conversations" coupled triad. This is what a real customer's mind
does when a supplier message lands -- and it is allowed to hold TRUTH the
company can never read (proposal
``docs/design/proposals/F1_conversations_coupled_triad_BUILD_PROPOSAL.md`` §3,
atom ``F1a_sim_customer_response``).

THE ONE MECHANISM (proposal §2):

    response = f( message, {FramingSusceptibility, ToneSusceptibility},
                  trust, budget-stress, true-intent, situation-state )
             -> action + channel-chosen + latency

A per-customer *hidden* susceptibility scalar SCALES a DISCOVER-benchmarked
nudge uplift on top of a situation base rate; the product saturates (never a
probability > 1). The company (F1b) NEVER sees the scalar -- it sees only the
observable ``ConversationResponse`` (action + which channel the customer
answered on + how long they took). That asymmetry is the whole atom: the
missing loop between the engagement-axis *traits* and actual *behaviour*.

REUSE, DO NOT RE-DRAW (proposal §3, §6): the two latent susceptibilities are
NOT re-invented here. They are the exact hidden traits already assigned once,
deterministically, at acquisition in ``simulation/nudge_physics.py``
(``susceptibility_for`` / ``tone_susceptibility_for``), and the matched-lever
uplift magnitudes are ``framing_effectiveness_multiplier`` /
``tone_effectiveness_multiplier`` -- population-anchored ranges (framing
10-35%, tone +3-10pp), sampled per customer, never a point estimate (R10).
This module adds the *conversation* physics (situation base rates, adverse
reactions, latency, channel-answered), not a second copy of the susceptibility
model.

THE EPISTEMIC WALL (binding, load-bearing): this module lives behind the wall
(``simulation/``) and holds ground truth. It imports ONLY the neutral seam
contract (``interface.contracts.*``) and its sibling SIM module
``simulation.nudge_physics`` -- NEVER ``company.*`` / ``saas.*``. Its OUTPUT
crossing the wall is a ``ConversationResponse``, whose contract structurally
forbids any hidden-trait field (``FORBIDDEN_TRUTH_FIELDS``). The hidden trust /
budget-stress / true-intent scalars below shape the action but are NEVER
attached to the response -- a real supplier infers them, never reads them.

SCALE DISCIPLINE (CLAUDE.md C-S1..C-S5, load-bearing not decoration):
  * C-S2 (named RNG substream + idempotent replay): every draw comes from a
    named, sha256-seeded substream keyed on (customer, message) -- so a NEW
    conversation draw can NEVER shift another subsystem's random sequence (the
    01:09Z shared-RNG incident is structurally impossible here), and re-running
    the same (customer, message) reproduces the identical response. The R15
    mutation that must FAIL the isolation test is a *shared/global* RNG variant
    (``tests/simulation/test_conversation_response.py``).
  * C-S3 (async): the response is a SEPARATE event in time from the message --
    ``responded_step == emitted_step + latency`` with ``latency >= 1`` (the
    contract rejects ``latency <= 0`` at construction; same-step resolution is
    not representable).
  * C-S1 (single/late/out-of-order): ``respond`` is a pure function of
    (customer, message) -- the response for customer A does not depend on
    whether customer B was processed first.
  * C-S5 (time-scale invariance): ``latency`` is a count of ABSTRACT steps; the
    message->response lag is a DECLARED parameter (``_SITUATION_PROFILE`` +
    ``_CHANNEL_LATENCY_OFFSET_STEPS``), not a hardcoded wall-clock duration.

ANTI-GOAL-SEEK (R12): the base rates and uplift bands are a DIAGNOSTIC of how
the world behaves, calibrated blind to company P&L (R13 baseline). They are
never tuned because the company's results look wrong; the belief-vs-truth gap
is F1c's to MEASURE, never this model's to make small.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import math
import random
from dataclasses import dataclass, fields
from enum import Enum
from typing import Any, Mapping, Optional, Union, get_args, get_origin, get_type_hints

from interface.contracts.conversation_seam import (
    Channel,
    ConversationMessage,
    ConversationMessageWallRequest,
    ConversationResponse,
    ConversationResponseWallResponse,
    OBSERVABLE_RESPONSE_PAYLOAD_TYPES,
    ResponseAction,
    SCHEMA_VERSION,
    Situation,
    validate_response_follows_message,
)
from interface.contracts.wall_envelope import WallRequest, WallResponse, WallStatus
from simulation.nudge_physics import (
    framing_effectiveness_multiplier,
    tone_effectiveness_multiplier,
)


# ---------------------------------------------------------------------------
# Named RNG substreams (C-S2). One per independent decision the response model
# makes. Order is irrelevant to isolation: each substream is an independent
# function of (base_seed, name), so appending a new named draw here can never
# consume from, or shift, any existing substream's sequence -- nor any OTHER
# subsystem's (life_events, payments, ...), which seed their own names.
# ---------------------------------------------------------------------------
_CONVERSATION_SUBSTREAMS: tuple[str, ...] = (
    "conversation_positive",   # does the nudge-liftable positive action fire?
    "conversation_adverse",    # given no positive, adverse reaction vs silence
    "conversation_latency",    # response lag jitter (steps)
    "conversation_channel",    # which channel the customer answers on
)


def _substream(base_seed: int, name: str) -> random.Random:
    """An independent RNG for a named decision substream, derived from a STABLE
    sha256 of ``base_seed:name`` (never Python's per-process-salted ``hash()``),
    so the same (base_seed, name) yields the same stream across processes -- the
    hard requirement for C-S2 deterministic replay -- and each name is an
    independent generator (a new name cannot shift an existing sequence)."""
    digest = hashlib.sha256(f"{base_seed}:{name}".encode()).digest()
    return random.Random(int.from_bytes(digest[:8], "big"))


def _base_seed_for(customer_id: str, message_id: str) -> int:
    """Resolve the response base seed for ONE (customer, message). Stable
    md5-derived (process-independent), keyed on BOTH the customer and the
    message id, so: (a) two different messages to the same customer draw
    independent responses, and (b) replaying the identical message reproduces
    the identical response (C-S2 idempotency)."""
    return int(hashlib.md5(f"{customer_id}|{message_id}".encode()).hexdigest()[:8], 16)


def _stable_unit(customer_id: str, name: str) -> float:
    """A stable per-customer scalar in [0, 1) for a named hidden trait -- the
    same idiom ``nudge_physics._stable_fraction`` uses, kept local so the hidden
    trust / budget-stress / intent scalars are drawn once, deterministically,
    and independently of the response substreams above."""
    digest = hashlib.sha256(f"{name}:{customer_id}".encode()).hexdigest()
    return (int(digest, 16) % 10_000) / 10_000.0


# ---------------------------------------------------------------------------
# Per-situation response profile (R13 BASELINE world constants, calibrated blind
# to company P&L). Base rates are order-of-magnitude engagement/response priors
# (email/SMS open-click benchmarks; debt-letter payment-response; win-back is
# hard) -- M confidence, cross-domain imports, honest about their provenance in
# the comments below. They set the DIAGNOSTIC world behaviour, never a target.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SituationResponseProfile:
    """How the world reacts to a message about one situation.

    ``positive_action`` -- the nudge-liftable good outcome (pay, reply, click).
    ``adverse_action``  -- the negative reaction when the nudge fails AND the
    customer reacts rather than staying silent (switch / complain / miss).
    ``base_positive_rate`` -- probability of the positive action absent any
    matched nudge. ``adverse_share`` -- of the non-positive mass, the fraction
    that becomes an adverse reaction (the rest is ``NO_REPLY``).
    ``framing_sensitive`` / ``tone_sensitive`` -- which hidden susceptibility
    lever modulates this situation (offer framing vs handling tone).
    ``base_latency_steps`` -- declared message->response lag (C-S5, abstract
    steps). ``no_reply_timeout_steps`` -- how many steps of silence are
    observed before a NO_REPLY is recorded (a non-response is still an event in
    time: "we waited N steps and saw nothing")."""

    positive_action: ResponseAction
    adverse_action: ResponseAction
    base_positive_rate: float
    adverse_share: float
    framing_sensitive: bool
    tone_sensitive: bool
    base_latency_steps: int
    no_reply_timeout_steps: int


# Framing-sensitive situations carry an OFFER whose framing the loss/gain-averse
# customer reacts to (nudge_physics framing lever). Tone-sensitive situations
# are payment/handling moments where the debt-letter/complaint TONE lands
# (nudge_physics tone lever). No situation is both -- the company chooses one
# lever per message, and only the matched lever lifts the base rate.
_SITUATION_PROFILE: dict[Situation, SituationResponseProfile] = {
    # Welcome journeys: onboarding open/click ~40% (utility email benchmark).
    Situation.WELCOME: SituationResponseProfile(
        ResponseAction.CLICK, ResponseAction.NO_REPLY, 0.40, 0.0, True, False, 1, 6),
    # Fixed-term renewal (SLC 22A window): engaged reply ~30%; the adverse tail
    # is a switch to a rival's acquisition offer.
    Situation.RENEWAL: SituationResponseProfile(
        ResponseAction.REPLY, ResponseAction.SWITCH, 0.30, 0.35, True, False, 3, 10),
    # Statutory tariff-change notice (SLC 23): mostly ignored (~15% engage); the
    # adverse tail switches away in protest at the increase.
    Situation.TARIFF_CHANGE: SituationResponseProfile(
        ResponseAction.REPLY, ResponseAction.SWITCH, 0.15, 0.40, True, False, 3, 10),
    # Missed payment (SLC 27 / Ability-to-Pay): the debt-letter TONE mechanic --
    # ~50% pay on-time base, empathetic/firm tone lifts it; adverse tail misses
    # again (deeper into arrears).
    Situation.MISSED_PAYMENT: SituationResponseProfile(
        ResponseAction.PAY, ResponseAction.MISS, 0.50, 0.60, False, True, 2, 5),
    # Bill shock: ~35% reach out; handling tone matters; the adverse tail
    # escalates to a formal complaint.
    Situation.BILL_SHOCK: SituationResponseProfile(
        ResponseAction.REPLY, ResponseAction.COMPLAIN, 0.35, 0.45, False, True, 2, 6),
    # Inbound complaint already raised: ~55% accept the resolution (CA weights
    # complaint handling heavily); tone of handling is decisive; the adverse
    # tail switches supplier.
    Situation.INBOUND_COMPLAINT: SituationResponseProfile(
        ResponseAction.REPLY, ResponseAction.SWITCH, 0.55, 0.50, False, True, 2, 8),
    # Win-back (lost customer): hard -- ~10% click a win-back incentive; framing
    # of the incentive matters; the rest simply do not re-engage.
    Situation.WIN_BACK: SituationResponseProfile(
        ResponseAction.CLICK, ResponseAction.NO_REPLY, 0.10, 0.0, True, False, 5, 14),
    # Annual statement (SLC 21B): ~25% open/click; framing of any embedded
    # saving offer lands; mostly silent otherwise.
    Situation.ANNUAL_STATEMENT: SituationResponseProfile(
        ResponseAction.CLICK, ResponseAction.NO_REPLY, 0.25, 0.0, True, False, 4, 12),
}


# Declared per-channel latency offset in ABSTRACT steps (C-S5): a letter lands
# and is answered slower than an SMS/app nudge; a phone call resolves fastest.
# Config, not baked into the seam types -- a build at a different clock speed
# re-points this table without touching the logic.
_CHANNEL_LATENCY_OFFSET_STEPS: dict[Channel, int] = {
    Channel.PHONE: 0,
    Channel.SMS: 0,
    Channel.APP: 0,
    Channel.EMAIL: 1,
    Channel.LETTER: 3,
}

# High-touch situations where an upset/engaged customer may answer on the PHONE
# rather than the channel the company reached out on (an OBSERVABLE channel
# switch a real supplier sees on its inbound lines).
_PHONE_ANSWER_SITUATIONS: frozenset[Situation] = frozenset(
    {Situation.INBOUND_COMPLAINT, Situation.BILL_SHOCK, Situation.MISSED_PAYMENT}
)
_PHONE_ANSWER_PROB = 0.20


# ---------------------------------------------------------------------------
# Hidden per-customer traits (BEHIND THE WALL, never on any response). Drawn
# once, deterministically, per customer -- the company must INFER these from
# observed actions, never read them.
# ---------------------------------------------------------------------------


def _trust(customer_id: str) -> float:
    """Hidden trust in [0, 1): high trust dampens the adverse (switch/complain)
    reaction; low trust amplifies it. Never crosses the wall."""
    return _stable_unit(customer_id, "conv_trust")


def _budget_stress(customer_id: str) -> float:
    """Hidden budget stress in [0, 1): reduces the ability to PAY on a missed
    payment even when the tone lands. Never crosses the wall."""
    return _stable_unit(customer_id, "conv_budget_stress")


def _considering_switch(customer_id: str) -> float:
    """Hidden true intent in [0, 1): a latent propensity to leave, which raises
    the adverse SWITCH share on renewal/tariff-change situations regardless of
    what the company sends. Never crosses the wall."""
    return _stable_unit(customer_id, "conv_true_intent_switch")


def positive_action_probability(
    customer_id: str, message: ConversationMessage
) -> float:
    """The (hidden-trait-driven) probability that the situation's POSITIVE
    action fires for this customer and this message -- the load-bearing number
    the company can never read, only infer from outcomes.

    ``base_rate x matched-lever-uplift``, saturating at 1.0. The uplift comes
    from ``nudge_physics`` and is 1.0 (no lift) UNLESS the company's chosen
    framing/tone happens to match this customer's hidden susceptibility -- which
    the company does not know, so it may send the wrong lever and get no lift.
    Budget stress erodes the PAY probability on a missed payment (a real
    inability to pay the tone cannot fix)."""
    profile = _SITUATION_PROFILE[message.situation]
    prob = profile.base_positive_rate
    if profile.framing_sensitive:
        prob *= framing_effectiveness_multiplier(customer_id, message.framing)
    if profile.tone_sensitive:
        prob *= tone_effectiveness_multiplier(customer_id, message.tone)
        if profile.positive_action == ResponseAction.PAY:
            # Budget stress caps ability-to-pay: up to a ~40% haircut at maximal
            # stress. A hidden real constraint the tone lever cannot overcome.
            prob *= 1.0 - 0.4 * _budget_stress(customer_id)
    if not math.isfinite(prob):
        # R15 NaN-blindness guard: a non-finite probability must be REJECTED
        # here, before it ever reaches a `<` comparison against a random
        # draw -- comparisons against NaN are silently False in Python, so an
        # un-guarded caller would misroute every customer to the adverse/
        # silent branch without ever raising (fail-silent). Reject loudly
        # instead, before the min() clamp below (which is itself NaN-blind:
        # ``min(nan, 1.0)`` returns ``nan``, not ``1.0``).
        raise ValueError(
            f"positive_action_probability produced a non-finite value "
            f"({prob!r}) for customer {customer_id!r}, situation "
            f"{message.situation!r} -- rejected before any comparison"
        )
    return min(prob, 1.0)


def _adverse_share(customer_id: str, message: ConversationMessage) -> float:
    """The fraction of the NON-positive mass that becomes an adverse reaction
    (rather than silence), modulated by the hidden trust and (for
    renewal/tariff) the hidden switch intent -- both behind the wall."""
    profile = _SITUATION_PROFILE[message.situation]
    share = profile.adverse_share
    # Low trust amplifies the adverse reaction, high trust dampens it: scale by
    # (0.6 .. 1.4) around the base as trust runs 1 -> 0.
    share *= 0.6 + 0.8 * (1.0 - _trust(customer_id))
    if profile.adverse_action == ResponseAction.SWITCH:
        # A latent intent to leave raises the switch share directly.
        share += 0.3 * _considering_switch(customer_id)
    if not math.isfinite(share):
        # R15 NaN-blindness guard (same pattern as positive_action_probability
        # above), but the failure mode here is the WORSE one: the clamp below
        # does not propagate the NaN, it LAUNDERS it. ``min(nan, 1.0)`` is
        # ``nan``, but ``max(0.0, nan)`` returns ``0.0`` -- so an un-guarded
        # non-finite share silently becomes a perfectly plausible "no adverse
        # action" instead of an obviously-broken value, and nothing downstream
        # can ever tell the difference. Reject it here, loudly, before the
        # clamp can disguise it.
        raise ValueError(
            f"_adverse_share produced a non-finite value ({share!r}) for "
            f"customer {customer_id!r}, situation {message.situation!r} -- "
            f"rejected before any comparison"
        )
    return max(0.0, min(share, 1.0))


def _latency_steps(
    customer_id: str, message: ConversationMessage, action: ResponseAction
) -> int:
    """A strictly-positive, declared-scale (C-S5) response lag in steps. A
    NO_REPLY is observed only after the situation's silence-timeout window (a
    non-response is still a later-in-time observation). Everything else lands at
    the situation base lag + channel offset + a small hidden jitter, clamped to
    >= 1 so the async contract (C-S3) can never be violated."""
    profile = _SITUATION_PROFILE[message.situation]
    if action == ResponseAction.NO_REPLY:
        return max(1, profile.no_reply_timeout_steps + _CHANNEL_LATENCY_OFFSET_STEPS[message.channel])
    base = _base_seed_for(customer_id, message.message_id)
    jitter = _substream(base, "conversation_latency").randint(0, 2)
    return max(1, profile.base_latency_steps + _CHANNEL_LATENCY_OFFSET_STEPS[message.channel] + jitter)


def _channel_chosen(
    customer_id: str, message: ConversationMessage, action: ResponseAction
) -> Channel:
    """The OBSERVABLE channel the customer answered on. Usually the channel the
    company reached out on; on a high-touch situation an engaged/upset customer
    may pick up the PHONE instead (a real inbound a supplier sees)."""
    if action in (ResponseAction.NO_REPLY,):
        return message.channel
    if message.situation in _PHONE_ANSWER_SITUATIONS and message.channel != Channel.PHONE:
        base = _base_seed_for(customer_id, message.message_id)
        if _substream(base, "conversation_channel").random() < _PHONE_ANSWER_PROB:
            return Channel.PHONE
    return message.channel


def respond(customer_id: str, message: ConversationMessage) -> ConversationResponse:
    """Resolve ONE message into ONE observable ``ConversationResponse`` for a
    named customer -- the SIM's whole answer across the wall.

    Pure function of (customer_id, message): no process/global state, no shared
    RNG, so the response for customer A is independent of whether B was
    processed first (C-S1) and replaying the same message reproduces the same
    response (C-S2). Draws only from named substreams keyed on (customer,
    message) -- the isolation the R15 shared-RNG mutation test guards.

    The action is: the situation's positive action with
    ``positive_action_probability`` (hidden-trait driven); otherwise an adverse
    reaction with the (trust/intent-modulated) adverse share, else silence.
    The response carries action + channel-answered + latency ONLY -- never the
    scalar that produced it."""
    profile = _SITUATION_PROFILE[message.situation]
    base = _base_seed_for(customer_id, message.message_id)

    if _substream(base, "conversation_positive").random() < positive_action_probability(
        customer_id, message
    ):
        action = profile.positive_action
    elif _substream(base, "conversation_adverse").random() < _adverse_share(
        customer_id, message
    ):
        action = profile.adverse_action
    else:
        action = ResponseAction.NO_REPLY

    latency = _latency_steps(customer_id, message, action)
    return ConversationResponse(
        response_id=f"resp:{message.message_id}",
        responds_to=message.message_id,
        action=action,
        channel_chosen=_channel_chosen(customer_id, message, action),
        latency=latency,
        responded_step=message.emitted_step + latency,
    )


def respond_over_wall(
    customer_id: str,
    message: ConversationMessage,
    correlation_id: str,
    observed_at: dt.datetime,
    valid_time: Optional[dt.date] = None,
) -> ConversationResponseWallResponse:
    """``respond`` wrapped in the typed ``WallResponse`` envelope -- the only
    sanctioned shape crossing this seam (typed-flow preference), matched back to
    the request by ``correlation_id`` alone (C-S1). ``observed_at`` is the
    wall-clock transaction time the answer became known (the ENVELOPE's clock,
    supplied by the caller); the abstract-step clock stays in the payload
    (C-S5). The pairing is contract-validated before it is returned, so a
    same-step or mis-linked response can never leave this function."""
    response = respond(customer_id, message)
    validate_response_follows_message(message, response)
    return WallResponse(
        correlation_id=correlation_id,
        status=WallStatus.OK,
        schema_version=SCHEMA_VERSION,
        observed_at=observed_at,
        valid_time=valid_time,
        payload=response,
    )


# ---------------------------------------------------------------------------
# THE WIRE (atom EP6_wall_protocol_typing, 2026-08-20) -- the counterparty's
# OWN codec, BOTH DIRECTIONS.
#
# Until this section existed, every conversation envelope crossed as a Python
# object handed straight down the call frame: `schema_version` was populated at
# construction and never encoded, never decoded, never refused. The wall census
# (`tools/wall_channel_census.py::envelope_wire_conformance`) reported this seam
# IN-PROCESS at 63bf50039 for exactly that reason.
#
# WHY THE COUNTERPARTY WRITES ITS OWN CODEC, and why that is not duplication:
# EP6's claim is that "a mock counterparty and a real one are indistinguishable
# to the company". That is only testable if the mock produces its bytes with its
# OWN code. Calling `company.interfaces.wall_protocol.encode_response` here and
# decoding with the same module on the other side would make the round-trip a
# TAUTOLOGY in the R15 sense -- a decoder checked against its own arithmetic,
# green through a schema change no real counterparty would have made. It is also
# forbidden outright: this module never imports `company.*` (module docstring),
# exactly as a real customer-contact platform never links the supplier's library.
#
# WHAT MAKES THE TWO SIDES AGREE IS THE CONTRACT AND ONLY THE CONTRACT: both
# read `interface.contracts.conversation_seam` -- the payload dataclasses, their
# declared field types, `OBSERVABLE_RESPONSE_PAYLOAD_TYPES` and `SCHEMA_VERSION`
# -- the way a real counterparty reads a published schema. A field added to a
# payload reaches both sides at once; a field one side invents reaches neither.
#
# BOTH LEGS, because this seam has two and the payment seam had one. A
# conversation is a REQUEST (company -> wall: the nudge it chose to send) and,
# separately in time, a RESPONSE (wall -> company: what the customer did). Wiring
# only the observable leg would leave the request envelope crossing as an object
# with an unread version -- the same defect on the other leg, and one the census
# cannot currently see, because its subject is the SEAM and not the LEG.
#
# ABSENCE IS NEVER AGREEMENT applies to both halves: every field is written
# including its nulls, `schema_version` is written from the CONTRACT's constant
# (never from a reader's default), a missing key is refused rather than defaulted
# and an unknown key is refused rather than tolerated.
# ---------------------------------------------------------------------------

#: The exact key set of a request as the published schema states it. Restated
#: here rather than imported: the company's codec is not this counterparty's
#: source of truth, and if the two ever disagree the messages must stop crossing
#: -- which is the correct outcome and the whole reason they are separate code.
_REQUEST_WIRE_FIELDS: frozenset[str] = frozenset(
    {"correlation_id", "request_type", "schema_version", "as_of", "emitted_at", "payload"}
)

_ENCODABLE_RESPONSE_PAYLOAD_TYPES = {t.__name__: t for t in OBSERVABLE_RESPONSE_PAYLOAD_TYPES}
_REQUEST_PAYLOAD_HINTS = get_type_hints(ConversationMessage)


class SeamCodecError(ValueError):
    """This seam refused to put a value on the wire, or refused one that
    arrived. Deliberately NOT `WallProtocolError`: that type is the COMPANY's,
    and a counterparty does not raise the receiver's exceptions."""


def _optional_base(declared: Any) -> tuple[Any, bool]:
    """Split ``Optional[X]`` into ``(X, True)``; anything else into ``(it, False)``."""
    if get_origin(declared) is Union:
        args = [a for a in get_args(declared) if a is not type(None)]
        if len(args) == 1:
            return args[0], True
    return declared, False


def _encode_scalar(value: Any, field: str) -> Any:
    """Encode one payload field. Refuses an unhandled type rather than coercing
    -- ``str(value)`` here is how a platform silently ships an object's repr and
    the receiver silently accepts a string."""
    if value is None:
        return None
    if isinstance(value, Enum):
        return value.value
    # bool is an int subclass; a True latency is a malformed field, not 1.
    if isinstance(value, bool):
        raise SeamCodecError(f"{field}: bool is not a conversation payload field type")
    if isinstance(value, (int, str)):
        return value
    raise SeamCodecError(
        f"{field}: {type(value).__name__} has no defined wire form on this seam"
    )


def encode_observable_payload(payload: Any) -> dict:
    """Put one observable response payload on the wire, TAGGED with its type.

    Tagged for the payment seam's reason and not because two types cross today:
    `WallResponse.payload` is opaque to the envelope codec, so a receiver that
    guessed the type from the field set would silently mis-route the day this
    seam's `OBSERVABLE_RESPONSE_PAYLOAD_TYPES` grows a second member. The tag
    set is read from that tuple, so it grows with the contract.
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
    return {
        "payload_type": payload_type.__name__,
        "fields": {
            f.name: _encode_scalar(
                getattr(payload, f.name), f"{payload_type.__name__}.{f.name}"
            )
            for f in fields(payload)
        },
    }


def encode_wall_response(response: WallResponse) -> dict:
    """Serialise one ``WallResponse`` into the wire form this seam publishes.

    Written against the SCHEMA, not against the company's decoder: the key set
    below is the response schema as this seam documents it, and if the company
    widens its own expectation without the schema changing, this encoder keeps
    emitting the old shape and the far side refuses it.
    """
    if not isinstance(response, WallResponse):
        raise SeamCodecError(f"expected a WallResponse, got {type(response).__name__}")
    return {
        "correlation_id": response.correlation_id,
        "status": response.status.value,
        "schema_version": SCHEMA_VERSION,
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


def respond_over_wire(
    customer_id: str,
    message: ConversationMessage,
    correlation_id: str,
    observed_at: dt.datetime,
    valid_time: Optional[dt.date] = None,
) -> dict:
    """``respond_over_wall``, but handing over a BYTES-shaped wire message
    instead of an in-process object -- what a real customer-contact platform
    delivers, and the form the live gap ledger now crosses on.

    The object form remains: it is how the response is constructed in the first
    place and what the offline harness measures. What changed is that the
    COMPANY no longer receives one.
    """
    return encode_wall_response(
        respond_over_wall(customer_id, message, correlation_id, observed_at, valid_time)
    )


# -- the inbound leg: the counterparty RECEIVING the company's message --------


def _decode_payload_field(raw: Any, declared: Any, where: str) -> Any:
    """Decode one message field to the type THE CONTRACT declares for it."""
    base, optional = _optional_base(declared)
    if raw is None:
        if optional:
            return None
        raise SeamCodecError(f"{where} is null but the contract declares it required")
    if isinstance(base, type) and issubclass(base, Enum):
        try:
            return base(raw)
        except ValueError as exc:
            raise SeamCodecError(
                f"{where}: {raw!r} is not one of {[m.value for m in base]}"
            ) from exc
    if base is str:
        if not isinstance(raw, str):
            raise SeamCodecError(f"{where} must be a str, got {raw!r}")
        return raw
    if base is int:
        # bool is an int subclass; a True step is malformed, not 1.
        if isinstance(raw, bool) or not isinstance(raw, int):
            raise SeamCodecError(f"{where} must be an int, got {raw!r}")
        return raw
    raise SeamCodecError(
        f"{where}: this seam has no decoder for declared type {declared!r} -- a field "
        "type was added to the contract without deciding how it crosses"
    )


def decode_message_payload(raw: Any) -> ConversationMessage:
    """Rebuild the company's outbound message off the wire, or refuse it.

    Not written as the inverse of the company's encoder by reading that
    encoder's source. The field set and types come from ``get_type_hints`` on
    the CONTRACT -- an independent source from anything the sender emitted --
    which is what a real counterparty has: the published schema.
    """
    if not isinstance(raw, Mapping):
        raise SeamCodecError(f"payload must be a mapping, got {type(raw).__name__}")
    missing = sorted({"payload_type", "fields"} - set(raw))
    if missing:
        raise SeamCodecError(
            f"payload omits {missing} -- an untagged payload cannot be routed to a "
            "declared message type"
        )
    unknown = sorted(set(raw) - {"payload_type", "fields"})
    if unknown:
        raise SeamCodecError(f"payload carries undefined key(s) {unknown}")
    tag = raw["payload_type"]
    if tag != ConversationMessage.__name__:
        raise SeamCodecError(
            f"payload_type {tag!r} is not {ConversationMessage.__name__!r} -- this seam's "
            "request leg carries exactly one payload type"
        )
    body = raw["fields"]
    if not isinstance(body, Mapping):
        raise SeamCodecError(f"{tag}.fields must be a mapping, got {type(body).__name__}")
    absent = sorted(set(_REQUEST_PAYLOAD_HINTS) - set(body))
    if absent:
        raise SeamCodecError(
            f"{tag} omits required field(s) {absent} -- never defaulted; an absent "
            "field and an agreeing field are not the same bytes"
        )
    extra = sorted(set(body) - set(_REQUEST_PAYLOAD_HINTS))
    if extra:
        raise SeamCodecError(f"{tag} carries field(s) {extra} the contract does not define")
    return ConversationMessage(
        **{
            name: _decode_payload_field(body[name], declared, f"{tag}.{name}")
            for name, declared in _REQUEST_PAYLOAD_HINTS.items()
        }
    )


def decode_wire_request(wire: Any) -> ConversationMessageWallRequest:
    """Parse one ``WallRequest[ConversationMessage]`` off the wire, or refuse it.

    The counterparty's half of "indistinguishable": the company's nudge arrives
    here as bytes and is version-checked before anything in this module can act
    on it. A `schema_version` this build does not speak is refused rather than
    assumed to be the one version that exists today -- the whole point of
    putting a version on the wire is that it can DISAGREE.
    """
    if not isinstance(wire, Mapping):
        raise SeamCodecError(f"request must be a mapping, got {type(wire).__name__}")
    present = frozenset(wire)
    missing = sorted(_REQUEST_WIRE_FIELDS - present)
    if missing:
        raise SeamCodecError(
            f"request omits required field(s) {missing} -- an absent field is never read "
            "as agreement with this process's own defaults"
        )
    unknown = sorted(present - _REQUEST_WIRE_FIELDS)
    if unknown:
        raise SeamCodecError(
            f"request carries field(s) {unknown} that schema version {SCHEMA_VERSION} "
            "does not define"
        )
    version = wire["schema_version"]
    if not isinstance(version, int) or isinstance(version, bool):
        raise SeamCodecError(f"schema_version must be an int, got {version!r}")
    if version != SCHEMA_VERSION:
        raise SeamCodecError(
            f"schema_version {version} is not the {SCHEMA_VERSION} this seam speaks"
        )
    correlation_id = wire["correlation_id"]
    if not isinstance(correlation_id, str) or not correlation_id:
        raise SeamCodecError(
            f"correlation_id must be a non-empty str, got {correlation_id!r} -- it is both "
            "the idempotency key and the only link to the response"
        )
    request_type = wire["request_type"]
    if not isinstance(request_type, str) or not request_type:
        raise SeamCodecError(f"request_type must be a non-empty str, got {request_type!r}")
    return WallRequest(
        correlation_id=correlation_id,
        request_type=request_type,
        schema_version=version,
        as_of=_decode_wire_datetime(wire["as_of"], "as_of"),
        emitted_at=_decode_wire_datetime(wire["emitted_at"], "emitted_at"),
        payload=decode_message_payload(wire["payload"]),
    )


def _decode_wire_datetime(raw: Any, field: str) -> dt.datetime:
    if not isinstance(raw, str):
        raise SeamCodecError(f"{field} must be an ISO-8601 str, got {raw!r}")
    try:
        return dt.datetime.fromisoformat(raw)
    except ValueError as exc:
        raise SeamCodecError(f"{field} is not ISO-8601: {raw!r}") from exc


def respond_to_wire_request(customer_id: str, wire_request: Any) -> dict:
    """The whole crossing, end to end, as a real counterparty performs it: bytes
    in, bytes out. The company's request is decoded and version-checked here, the
    world answers, and the answer leaves as bytes with its own version on it.

    ``observed_at`` is taken from the request's ``emitted_at``: a response is a
    SEPARATE, LATER event (C-S3), and the abstract-step clock that expresses HOW
    much later stays in the payload (C-S5), so the envelope clock is anchored to
    the only wall-clock instant this seam actually observed.
    """
    request = decode_wire_request(wire_request)
    return respond_over_wire(
        customer_id,
        request.payload,
        correlation_id=request.correlation_id,
        observed_at=request.emitted_at,
    )
