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
import random
from dataclasses import dataclass
from typing import Optional

from interface.contracts.conversation_seam import (
    Channel,
    ConversationMessage,
    ConversationResponse,
    ConversationResponseWallResponse,
    ResponseAction,
    SCHEMA_VERSION,
    Situation,
    validate_response_follows_message,
)
from interface.contracts.wall_envelope import WallResponse, WallStatus
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
