"""F1b generator — the supplier's outbound-message brain: given a customer's
(observable) SEGMENT and a SITUATION trigger, choose which message to send, on
which channel, with which tone/framing.

WHAT THIS IS (in front of the wall): a real supplier CRM's campaign engine. It
keys on two things it can legitimately know -- the customer's SEGMENT (an
observable class: residential / SME / I&C, plus a Priority-Services-Register
accessibility flag and a digital-engagement flag) and its own BELIEF about
which levers land on this customer (from ``SusceptibilityEstimator`` -- learned
from replies, never read from the customer's mind). It never reads a hidden
susceptibility scalar; the tone/framing it picks come from the belief, which
is allowed to be wrong.

CHANNEL IS SEGMENT-GATED, and the generator MAY NOT ASSUME ONE CHANNEL
(proposal §3, FRAME §3b): SME/I&C reach through formal broker/TPI-friendly
channels; a PSR customer is owed accessible formats; a digital-first
residential customer is reachable in-app. ``allowed_channels`` always returns
more than one option and the generator selects within the segment's set by a
situation preference order -- so two different segments provably get different
channels for the same situation (tested).

SITUATIONS are the DISCOVER Q1 trigger set (the eight members of
``Situation``). The GB-specific statutory clocks each trigger fires on (the SLC
22A 42-49d renewal window, the 30-day tariff-change notice, ...) are CONFIG in
``SITUATION_CONFIG`` here, NOT baked into the seam types (C-S5 / portability
§8): a second market re-points the config, never the engine. ``product`` is a
required dimension on every message (portability §8 -- carried wherever fuel is
one).

THE WALL: this module imports only the seam contract and the sibling estimator;
nothing from ``sim`` / ``simulation``. See the package docstring and the R15
mutation test.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from interface.contracts.conversation_seam import (
    Channel,
    ConversationMessage,
    ConversationMessageWallRequest,
    Product,
    SCHEMA_VERSION,
    Situation,
)
from interface.contracts.wall_envelope import WallRequest
from company.comms.susceptibility_estimator import SusceptibilityEstimator


# ---------------------------------------------------------------------------
# Segment — the OBSERVABLE customer class the generator gates channel on. Every
# field here is something a real supplier holds in its own CRM (product class,
# whether the customer is on the Priority Services Register, whether they use
# the app), NOT a hidden behavioural trait inferred through the wall.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CustomerSegment:
    """A customer's observable segment. ``customer_class`` is one of
    ``residential`` / ``sme`` / ``i_and_c``. ``psr`` marks a Priority Services
    Register customer owed accessible formats. ``digital_engaged`` marks a
    customer reachable through the app / digital channels."""

    customer_class: str = "residential"
    psr: bool = False
    digital_engaged: bool = True

    def __post_init__(self) -> None:
        if self.customer_class not in ("residential", "sme", "i_and_c"):
            raise ValueError(
                f"unknown customer_class {self.customer_class!r} "
                "(expected residential / sme / i_and_c)"
            )


@dataclass(frozen=True)
class SituationConfig:
    """Per-situation config: the statutory clock the trigger fires on (as
    provenance metadata, never as engine logic), whether the situation
    typically carries an offer, and the offer label to attach if so. Trigger
    DATES live here as config (C-S5 / portability), not baked into the enum."""

    notice_window_days: Optional[Tuple[int, int]]
    carries_offer: bool
    offer_label: Optional[str]
    statutory_ref: Optional[str]


# GB-specific trigger clocks as CONFIG (portability §8): a second market/regime
# re-points this table; the generator logic never changes. The windows are
# recorded for provenance/scheduling; this atom emits messages on demand for a
# given situation and does not itself schedule the statutory countdown.
SITUATION_CONFIG: Dict[Situation, SituationConfig] = {
    Situation.RENEWAL: SituationConfig((42, 49), True, "fixed_term_renewal", "SLC 22A"),
    Situation.TARIFF_CHANGE: SituationConfig((30, 30), False, None, "SLC 23"),
    Situation.MISSED_PAYMENT: SituationConfig(None, False, None, "SLC 27 / Ability-to-Pay"),
    Situation.BILL_SHOCK: SituationConfig(None, False, None, None),
    Situation.INBOUND_COMPLAINT: SituationConfig(None, False, None, "SLC Complaint Handling"),
    Situation.WIN_BACK: SituationConfig(None, True, "win_back_incentive", None),
    Situation.WELCOME: SituationConfig(None, False, None, None),
    Situation.ANNUAL_STATEMENT: SituationConfig(None, False, None, "SLC 21B Annual Statement"),
}


# Channel preference ORDER per situation. The generator walks this order and
# picks the FIRST channel the segment is allowed on -- so the channel is a
# function of BOTH the situation (urgency/formality) and the segment (gating),
# never a single hardcoded channel. Every situation lists several channels.
_SITUATION_CHANNEL_PREFERENCE: Dict[Situation, Tuple[Channel, ...]] = {
    Situation.MISSED_PAYMENT: (Channel.SMS, Channel.PHONE, Channel.APP, Channel.EMAIL, Channel.LETTER),
    Situation.BILL_SHOCK: (Channel.APP, Channel.EMAIL, Channel.SMS, Channel.PHONE, Channel.LETTER),
    Situation.RENEWAL: (Channel.EMAIL, Channel.APP, Channel.LETTER, Channel.SMS, Channel.PHONE),
    Situation.TARIFF_CHANGE: (Channel.LETTER, Channel.EMAIL, Channel.APP, Channel.PHONE, Channel.SMS),
    Situation.INBOUND_COMPLAINT: (Channel.PHONE, Channel.EMAIL, Channel.LETTER, Channel.APP, Channel.SMS),
    Situation.WIN_BACK: (Channel.EMAIL, Channel.APP, Channel.SMS, Channel.PHONE, Channel.LETTER),
    Situation.WELCOME: (Channel.APP, Channel.EMAIL, Channel.LETTER, Channel.SMS, Channel.PHONE),
    Situation.ANNUAL_STATEMENT: (Channel.EMAIL, Channel.LETTER, Channel.APP, Channel.SMS, Channel.PHONE),
}


def allowed_channels(segment: CustomerSegment) -> Tuple[Channel, ...]:
    """The channels the company may use for a segment -- always more than one
    (a real supplier never has exactly one lawful/appropriate channel):

    * PSR (accessibility) -> accessible formats: LETTER, PHONE, EMAIL. No
      SMS-only / app-only, which can exclude a PSR customer.
    * SME / I&C -> formal, broker/TPI-reachable channels: EMAIL, PHONE, LETTER
      (a business account is managed through a broker or an account manager,
      not a consumer app).
    * residential + digital_engaged -> digital-first: APP, EMAIL, SMS.
    * residential, not digital_engaged -> EMAIL, LETTER, SMS.
    """
    if segment.psr:
        return (Channel.LETTER, Channel.PHONE, Channel.EMAIL)
    if segment.customer_class in ("sme", "i_and_c"):
        return (Channel.EMAIL, Channel.PHONE, Channel.LETTER)
    if segment.digital_engaged:
        return (Channel.APP, Channel.EMAIL, Channel.SMS)
    return (Channel.EMAIL, Channel.LETTER, Channel.SMS)


def _choose_channel(segment: CustomerSegment, situation: Situation) -> Channel:
    permitted = allowed_channels(segment)
    for channel in _SITUATION_CHANNEL_PREFERENCE[situation]:
        if channel in permitted:
            return channel
    # Every situation preference lists all five channels, so a permitted one is
    # always found; this fallback keeps the function total by construction.
    return permitted[0]


class ConversationGenerator:
    """Emits situation-keyed, segment-gated ``ConversationMessage`` objects,
    with tone/framing drawn from a ``SusceptibilityEstimator`` belief (learned
    from replies, allowed to be wrong). Stateless apart from the estimator it
    consults and a monotonic message counter for stable ids."""

    def __init__(self, estimator: Optional[SusceptibilityEstimator] = None) -> None:
        # A generator with no estimator sends neutral levers to everyone --
        # honest ignorance, not a fabricated preference.
        self._estimator = estimator

    def _tone_and_framing(self, customer_id: str) -> Tuple[str, str]:
        if self._estimator is None:
            return "neutral_toned", "neutral_framed"
        return (
            self._estimator.best_tone_value(customer_id),
            self._estimator.best_framing_value(customer_id),
        )

    def generate(
        self,
        customer_id: str,
        segment: CustomerSegment,
        situation: Situation,
        product: Product,
        emitted_step: int,
        message_id: Optional[str] = None,
    ) -> ConversationMessage:
        """Choose and build one message for a customer in a situation.

        Channel is segment-gated (``allowed_channels``) and situation-ordered.
        Tone/framing come from the company's belief about this customer. The
        offer is attached only when ``SITUATION_CONFIG`` says the situation
        carries one. ``product`` is required. ``message_id`` defaults to a
        stable ``customer:situation:step`` key so re-generating the same
        (customer, situation, step) is idempotent (C-S2)."""
        if situation not in SITUATION_CONFIG:  # pragma: no cover - enum-exhaustive
            raise ValueError(f"no config for situation {situation!r}")
        config = SITUATION_CONFIG[situation]
        channel = _choose_channel(segment, situation)
        tone, framing = self._tone_and_framing(customer_id)
        offer = config.offer_label if config.carries_offer else None
        mid = message_id or f"{customer_id}:{situation.value}:{emitted_step}"
        return ConversationMessage(
            message_id=mid,
            situation=situation,
            channel=channel,
            product=product,
            tone=tone,
            framing=framing,
            emitted_step=emitted_step,
            offer=offer,
        )

    def generate_wall_request(
        self,
        customer_id: str,
        segment: CustomerSegment,
        situation: Situation,
        product: Product,
        emitted_step: int,
        as_of: dt.datetime,
        emitted_at: dt.datetime,
        correlation_id: Optional[str] = None,
        message_id: Optional[str] = None,
    ) -> ConversationMessageWallRequest:
        """Same as ``generate`` but wrapped in the typed ``WallRequest``
        envelope -- the only sanctioned shape crossing the seam (typed-flow
        preference). ``correlation_id`` defaults to the message id, which is
        both the idempotency and response-matching key (C-S1/C-S2)."""
        message = self.generate(
            customer_id, segment, situation, product, emitted_step, message_id
        )
        return WallRequest(
            correlation_id=correlation_id or message.message_id,
            request_type="conversation_message",
            schema_version=SCHEMA_VERSION,
            as_of=as_of,
            emitted_at=emitted_at,
            payload=message,
        )
