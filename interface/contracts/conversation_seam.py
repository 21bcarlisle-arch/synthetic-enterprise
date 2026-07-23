"""The conversation seam -- atom F1 (the interface-steward step of the F1
"simulating conversations" coupled triad). This is the FIRST sequenced step
of the director-authorized F1 build (ruling 2026-07-23, proposal
docs/design/proposals/F1_conversations_coupled_triad_BUILD_PROPOSAL.md §6):
"define the Message/Response types at the seam FIRST -- a small
interface-steward step -- then the two sides build to it." It defines the
typed, versioned message/response contract ONLY -- no response model (F1a),
no company generator/estimator (F1b), no harness (F1c) lives here.

WHAT THIS IS: the shape of a single conversational exchange crossing the
sim/company seam. The company EMITS a ``ConversationMessage`` (company ->
wall: a nudge it chose to send -- situation, channel, tone, framing, offer,
product) and later OBSERVES a ``ConversationResponse`` (wall -> company: what
the customer did -- action + which channel they chose + how long they took).
Both are carried in the generic ``WallRequest``/``WallResponse`` envelope
(``wall_envelope.py``), the same idiom as ``flex_observable_seam.py`` and
``payment_observable_seam.py``.

THE EPISTEMIC-WALL GUARANTEE (binding, load-bearing): the customer's TRUE
hidden traits -- the per-customer ``FramingSusceptibility`` /
``ToneSusceptibility`` scalars (``sim`` / ``nudge_physics``), trust,
budget-stress, and true intent -- NEVER appear on either type. A real UK
supplier sees only what the customer DID (action + reply + latency +
which channel they answered on), never the latent trait that produced it.
The company's INFERENCE of those traits (a per-customer Bayesian belief) is
F1b's job on the far side of this seam; the belief-vs-truth GAP is F1c's job
to measure. This module carries neither the belief nor the ground truth --
only the observation. ``FORBIDDEN_TRUTH_FIELDS`` + the payload-type tuple
below let the wall test assert this structurally, so a future field addition
is forced through the same field-level scrutiny.

ASYNC BY CONSTRUCTION (C-S3, real here, not theoretical): a message goes out
and the customer's response lands later -- minutes (SMS), days (letter), or
never (no_reply). The ``ConversationResponse`` is therefore a SEPARATE event
in time from the ``ConversationMessage``, matched only by ``responds_to`` (=
the message id) and, at the envelope level, by ``correlation_id``. The
contract MAKES same-step resolution impossible two ways: (1) a
``ConversationResponse`` cannot be constructed with a non-positive
``latency`` (a zero/negative-latency reply is a same-step or time-travelling
reply -- rejected at construction); (2) ``validate_response_follows_message``
rejects any (message, response) pair whose response clock is not strictly
after the message clock.

TIME-SCALE INVARIANCE (C-S5, portability -- no hardcoded clock speed /
settlement granularity): the clock carried here is an abstract integer
``step``, not a wall-clock timestamp. ``latency`` is a count of steps, and
``responded_step == emitted_step + latency``. A build that runs the sim at
half-hourly, daily, or event granularity reuses this contract unchanged; the
GB-specific trigger DATES (e.g. the SLC 22A 42-49d renewal window) are
config on the F1b generator, never baked into these types.

PORTABILITY (§8): ``product`` is a REQUIRED dimension on every message --
carried wherever fuel is one. A second product is a new ``Product`` member
and new ``Situation`` members, never a new dataclass shape or a new engine.
The types key on ``situation`` + ``channel``, never on a hardcoded
counterparty / regulator name.

IDEMPOTENCY (C-S2): ``message_id`` and ``response_id`` are stable ids, so a
resolver/consumer that processes the same response twice is harmless (the
second processing is a no-op keyed on ``response_id``).

NO SIM/GENERATOR/COMPANY SYMBOL: this module imports nothing from ``sim``,
``simulation``, ``company``, or ``saas`` -- it is pure contract, checked by
``tests/interface/test_conversation_seam.py::test_no_sim_or_company_import``.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from interface.contracts.wall_envelope import WallRequest, WallResponse

SCHEMA_VERSION = 1


class Situation(str, Enum):
    """The conversation TRIGGER -- the DISCOVER Q1 situation set. A second
    product adds members here (portability lens §8), never a new type. The
    GB-specific date each trigger fires on (SLC 22A 42-49d renewal window,
    30d tariff-change notice, ...) is F1b generator config, NOT baked into
    this enum -- the enum names the situation kind, not its statutory clock."""

    RENEWAL = "renewal"
    TARIFF_CHANGE = "tariff_change"
    MISSED_PAYMENT = "missed_payment"
    BILL_SHOCK = "bill_shock"
    INBOUND_COMPLAINT = "inbound_complaint"
    WIN_BACK = "win_back"
    WELCOME = "welcome"
    ANNUAL_STATEMENT = "annual_statement"


class Channel(str, Enum):
    """The delivery channel of a message, and (on the response) the channel
    the customer actually answered on -- an OBSERVABLE (a real supplier sees
    which channel a reply arrived on), never a hidden preference trait."""

    EMAIL = "email"
    SMS = "sms"
    LETTER = "letter"
    APP = "app"
    PHONE = "phone"


class Product(str, Enum):
    """The product the conversation is about -- carried wherever fuel is one
    (portability §8). A second product is a member addition here, never a new
    engine."""

    ELECTRICITY = "electricity"
    GAS = "gas"
    DUAL_FUEL = "dual_fuel"


class ResponseAction(str, Enum):
    """EXACTLY the observable customer actions (proposal §3, F1a output). What
    the customer DID -- never why. The latent trait that produced this action
    is SIM-internal and never crosses the seam."""

    REPLY = "reply"
    NO_REPLY = "no_reply"
    CLICK = "click"
    PAY = "pay"
    MISS = "miss"
    SWITCH = "switch"
    COMPLAIN = "complain"


# ---------------------------------------------------------------------------
# Request payload -- COMPANY -> WALL: the nudge the company chose to send.
# Company-owned data only (its own situation trigger, channel, tone, framing,
# offer, product); the epistemic wall polices what flows BACK (the response),
# not what the company already possesses and sends out.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ConversationMessage:
    """Payload of ``WallRequest[ConversationMessage]``: one nudge the company
    emits. ``message_id`` is the stable idempotency + response-matching key.
    ``emitted_step`` is the abstract monotonic clock at which it was sent
    (C-S5 time-scale-invariant -- an integer step, not a wall-clock time).

    ``product`` is REQUIRED (portability §8) -- there is no default; a message
    is always about a product. ``tone`` and ``framing`` are the levers whose
    (hidden) per-customer susceptibility F1a will scale -- carried here as the
    company's free-form choice of lever, NOT as any susceptibility value.
    ``offer`` is optional (many situations carry no offer)."""

    message_id: str
    situation: Situation
    channel: Channel
    product: Product
    tone: str
    framing: str
    emitted_step: int
    offer: Optional[str] = None


# ---------------------------------------------------------------------------
# Observable response payload -- WALL -> COMPANY. Every field here is the
# load-bearing epistemic-wall surface: OBSERVATION ONLY, never the latent
# trait. A real supplier reads exactly these off its own systems.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ConversationResponse:
    """Payload of ``WallResponse[ConversationResponse]``: what the customer
    did in reply to a message. A SEPARATE event in time from the message
    (C-S3), matched back to it by ``responds_to`` (= the message's
    ``message_id``) alone. ``response_id`` is the stable idempotency key
    (processing it twice is harmless, C-S2).

    ``latency`` is the observable count of steps the customer took to answer;
    ``responded_step == emitted_step + latency`` on the matching message.
    A non-positive ``latency`` is a same-step or time-travelling reply and is
    REJECTED at construction -- the contract cannot represent same-step
    resolution (C-S3 made structural). Carries NO susceptibility / trust /
    intent / true-scalar field: the company must INFER the trait from these
    observed actions, never read it here."""

    response_id: str
    responds_to: str
    action: ResponseAction
    channel_chosen: Channel
    latency: int
    responded_step: int

    def __post_init__(self) -> None:
        if self.latency <= 0:
            raise ValueError(
                "ConversationResponse.latency must be strictly positive "
                "(C-S3: a response is a SEPARATE, LATER event than its "
                f"message -- same-step resolution is not representable); got {self.latency}"
            )


def validate_response_follows_message(
    message: ConversationMessage, response: ConversationResponse
) -> None:
    """C-S3 pairing check: a ``ConversationResponse`` must reference its
    ``ConversationMessage`` and land STRICTLY AFTER it on the abstract clock.
    Raises ``ValueError`` on any pair that is not a well-formed
    later-in-time reply -- so a build cannot resolve a message in the same
    step it was sent, nor pair a response to the wrong message.

    This is the contract-level enforcement of the Point-in-Time / async wall:
    the response's own clock (``responded_step``) is the only ordering truth,
    and it must exceed the message's ``emitted_step``."""
    if response.responds_to != message.message_id:
        raise ValueError(
            f"response {response.response_id!r} responds_to "
            f"{response.responds_to!r}, not message {message.message_id!r}"
        )
    if response.responded_step <= message.emitted_step:
        raise ValueError(
            "C-S3: response must land STRICTLY AFTER its message "
            f"(responded_step={response.responded_step} must be > "
            f"emitted_step={message.emitted_step})"
        )


# ---------------------------------------------------------------------------
# Envelope specialisations -- the ONLY sanctioned typed shape crossing this
# seam. The SIM (F1a) and COMPANY (F1b) adapters depend on these, never on
# each other.
# ---------------------------------------------------------------------------

ConversationMessageWallRequest = WallRequest[ConversationMessage]
ConversationResponseWallResponse = WallResponse[ConversationResponse]


# Every payload type this seam is permitted to carry -- the epistemic-wall
# test enumerates exactly this list so a future payload addition is forced to
# pass the same field-level (no-hidden-trait) scrutiny.
CONTRACT_PAYLOAD_TYPES: tuple[type, ...] = (
    ConversationMessage,
    ConversationResponse,
)

# The wall -> company observable payloads specifically (the load-bearing wall
# surface). Kept distinct from the outbound message for parity with the flex
# seam's OBSERVABLE_RESPONSE_PAYLOAD_TYPES.
OBSERVABLE_RESPONSE_PAYLOAD_TYPES: tuple[type, ...] = (ConversationResponse,)

# Field names that would leak a customer's HIDDEN latent trait across the
# seam -- the wall test asserts NO payload (message or response) carries any
# of these. A real supplier never sees the scalar that produced the action.
FORBIDDEN_TRUTH_FIELDS: tuple[str, ...] = (
    "framing_susceptibility",
    "framingsusceptibility",
    "tone_susceptibility",
    "tonesusceptibility",
    "susceptibility",
    "true_intent",
    "intent",
    "trust",
    "trust_true",
    "budget_stress",
    "engagement_archetype",
    "archetype",
    "true_scalar",
    "latent",
    "nudge_uplift",
)
