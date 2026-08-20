"""F1b estimator — a per-customer Bayesian belief over each conversational
susceptibility lever, updated ONLY on what the customer was OBSERVED to do.

WHAT THIS IS (in front of the wall, allowed to be wrong): a real supplier CRM
that slowly learns which nudge lands on which customer, from nothing but which
past messages produced a response. It maintains, per customer, a Beta belief
over the positive-response rate for each FRAMING value it can send
(``loss_framed`` / ``gain_framed`` / ``neutral_framed``) and each TONE value
(``empathetic_toned`` / ``firm_toned`` / ``neutral_toned``). The posterior
means ARE the company's belief; the argmax lever value is what the generator
should send next; the inferred susceptibility CATEGORY (loss_averse /
gain_responsive / neutral, and empathetic / firm / neutral) is the
company-side estimate the harness (F1c) compares against the SIM's true hidden
scalar to score the belief-vs-truth gap.

THE EPISTEMIC WALL (load-bearing): this module imports nothing from ``sim`` /
``simulation`` and reads no susceptibility scalar. Its only inputs are (1) the
``ConversationMessage`` the COMPANY ITSELF chose to send (company-owned
outbound data -- the framing/tone it picked) and (2) the observable
``ConversationResponse`` that came back over the wall (action + channel +
latency). A belief-update that reached for the true scalar would have to
``import`` the SIM internal that holds it -- which the epistemic verifier
catches on the diff (proven by the R15 mutation test in
``tests/company/comms/test_conversation_comms.py``). The wall is not a comment
here; it is the absence of any path to the truth.

Scale discipline (the seam's C-S laws, honoured company-side):
  * C-S2 idempotency -- a response processed twice is a no-op, keyed on
    ``response_id``. Replaying a history reproduces the identical belief.
  * C-S1/C-S3 async, out-of-order -- ``observe_response`` needs only the
    (message, response) pair; responses may arrive singly, late, or out of
    order, and each is folded in independently (Beta counts commute).
  * C-S5 time-scale invariance -- ``latency`` is a count of abstract steps and
    only ever enters as a decaying WEIGHT via a declared ``latency_scale``
    parameter, never as a hardcoded clock.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import (
    Any,
    Dict,
    Iterable,
    Mapping,
    Optional,
    Tuple,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)

from interface.contracts.conversation_seam import (
    FORBIDDEN_TRUTH_FIELDS,
    ConversationMessage,
    ConversationResponse,
    OBSERVABLE_RESPONSE_PAYLOAD_TYPES,
    ResponseAction,
    validate_response_follows_message,
)
from company.interfaces.wall_protocol import WallProtocolError, decode_response

# The FRAMING values the company can put on a message, and the SIM-side
# susceptibility CATEGORY each is the "matched" lever for. These strings match
# simulation/nudge_physics.py's own matched-framing values (loss_framed /
# gain_framed) BY CONVENTION of the shared lever vocabulary -- NOT by import:
# the company happens to speak the same lever language the world responds to,
# exactly as a real supplier's "loss-framed retention offer" is the same
# artefact the customer reacts to. neutral_framed is the no-signal default.
FRAMING_VALUES: Tuple[str, ...] = ("loss_framed", "gain_framed", "neutral_framed")
TONE_VALUES: Tuple[str, ...] = ("empathetic_toned", "firm_toned", "neutral_toned")

# framing/tone value -> the susceptibility category the company would INFER a
# customer to hold if that value is the one that lands best for them. neutral
# is not a lever value the company distinguishes toward -- it is the verdict
# when no lever separates (see inferred_* below).
_FRAMING_VALUE_TO_CATEGORY: Dict[str, str] = {
    "loss_framed": "loss_averse",
    "gain_framed": "gain_responsive",
    "neutral_framed": "neutral",
}
_TONE_VALUE_TO_CATEGORY: Dict[str, str] = {
    "empathetic_toned": "empathetic_responsive",
    "firm_toned": "firm_responsive",
    "neutral_toned": "neutral",
}

# Observable customer actions the company reads as a POSITIVE response to a
# nudge (engaged / did the desired thing) vs a NEGATIVE one. This is a
# company-side READING of an observable, never a read of intent: a real
# supplier likewise counts "paid / clicked / replied" as the message landing
# and "no reply / missed / switched away / complained" as it not landing.
_POSITIVE_ACTIONS = frozenset(
    {ResponseAction.REPLY, ResponseAction.CLICK, ResponseAction.PAY}
)
_NEGATIVE_ACTIONS = frozenset(
    {
        ResponseAction.NO_REPLY,
        ResponseAction.MISS,
        ResponseAction.SWITCH,
        ResponseAction.COMPLAIN,
    }
)

# A posterior-mean lead this small (best value vs the field) is treated as NO
# real signal -> the company infers "neutral" rather than over-committing to a
# lever on thin evidence. A diagnostic threshold, not a tuned target (R12).
_NEUTRAL_EPSILON = 0.02


# ---------------------------------------------------------------------------
# OFF THE WIRE (atom EP6_wall_protocol_typing, 2026-08-20) -- the company's
# payload decoder for the OBSERVABLE leg of this crossing.
#
# `company.interfaces.wall_protocol` decodes the ENVELOPE and treats `payload`
# as opaque: its payload codec is a required argument with no default, so
# nothing is deserialised by accident and a new crossing never edits it. This
# function is this crossing's half of that bargain.
#
# It is deliberately NOT written by reading `simulation.conversation_response`'s
# encoder. Both sides are written against `interface.contracts.conversation_seam`
# -- the payload dataclasses and their declared field types -- which is what a
# real supplier has: the published schema, not the counterparty's source. The
# field set and types below come from `get_type_hints`, an INDEPENDENT source
# from anything the sender emitted.
#
# ABSENCE IS NEVER AGREEMENT, at payload depth too: a missing field is not
# defaulted (the company would otherwise fold a belief update the world never
# advised) and an unknown field is not tolerated (a schema that grew announces
# itself by its version, never by a key appearing quietly).
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
    """Decode one payload field to the type THE CONTRACT declares for it."""
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
    if base is int:
        # bool is an int subclass; a True latency is malformed, not 1.
        if isinstance(raw, bool) or not isinstance(raw, int):
            raise WallProtocolError("MALFORMED_FIELD", f"{where} must be an int, got {raw!r}")
        return raw
    raise WallProtocolError(
        "CONTRACT_VIOLATION",
        f"{where}: this seam has no decoder for declared type {declared!r} -- a field "
        "type was added to the contract without deciding how it crosses",
    )


def decode_observable_payload(raw: Any) -> Any:
    """Rebuild one observable conversation payload off the wire, or refuse it.

    THE WALL IS CHECKED HERE TOO, AND THIS IS THE LEG THAT HAD NOTHING.
    `_OBSERVABLE_PAYLOAD_HINTS` below is `get_type_hints(ConversationResponse)`
    -- it WIDENS whenever that dataclass widens, so as an answer to "could a
    real supplier know this" it is an R15 TAUTOLOGY. The encode leg
    (`simulation/conversation_response.py`) has a non-derived answer, refusing
    by name from the contract's own `FORBIDDEN_TRUTH_FIELDS`; until EP6 pass 28
    this leg had none, which made this seam the one crossing on the wall belted
    on the side the WORLD owns and bare on the side the COMPANY owns -- the
    same asymmetry pass 27 closed on payment, on the seam that carries a
    customer's hidden latent traits.

    That asymmetry is the wrong way round for what this seam is for. The whole
    F1b/F1c gap exists to score the company's INFERRED susceptibility against
    the SIM's true hidden scalar. A world that started shipping
    `framing_susceptibility` alongside the observed action would produce a
    perfectly well-formed envelope and a perfectly well-typed payload, and a
    company that folded it in would be reading the answer key rather than
    estimating it -- scoring itself against a number it was handed. Refused BY
    NAME from the contract's own denylist, so the CLASS fails rather than the
    instance somebody remembered (R10).

    DENYLIST FIRST, the same ordering and the same reason as
    `sim/flex_dispatch.py`, `company/market/flex_participation.py` and
    `company/billing/payment_observation_consumer.py`: the truth-leak message
    is the more diagnostic of the two, and the ordering keeps each belt
    separately observable rather than one masking the other.

    NEVER THE CONTROL. `OBSERVABLE_PAYLOAD_FIELDS` is, and it answers the
    strictly wider question. This belt fires on the one case the closed set
    cannot see -- a trait field added to the dataclass AND declared observable
    in the same edit, which moves the very thing the closed set reads.
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
            "this seam's observable types",
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
            f"{tag} carries world-internal latent trait(s) {leaking} -- this company "
            "INFERS a customer's susceptibility from which past messages landed, and "
            "may never be handed the scalar that produced the action",
        )
    absent = sorted(set(hints) - set(body))
    if absent:
        raise WallProtocolError(
            "MISSING_FIELD",
            f"{tag} omits required field(s) {absent} -- never defaulted; the company "
            "would otherwise fold in a reply the customer did not make",
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


@dataclass
class _BetaCounts:
    """Beta(alpha, beta) belief over the positive-response rate for one lever
    value. Real-valued counts (latency enters as a fractional weight)."""

    alpha: float = 1.0
    beta: float = 1.0

    @property
    def mean(self) -> float:
        return self.alpha / (self.alpha + self.beta)

    @property
    def observations(self) -> float:
        # Evidence accumulated beyond the Beta(1,1) uniform prior.
        return (self.alpha - 1.0) + (self.beta - 1.0)


@dataclass
class CustomerBelief:
    """The company's whole belief about one customer's conversational
    susceptibility: a Beta belief per framing value and per tone value.
    Posterior means are the company's estimate; nothing here is ground truth."""

    framing: Dict[str, _BetaCounts] = field(default_factory=dict)
    tone: Dict[str, _BetaCounts] = field(default_factory=dict)

    def framing_means(self) -> Dict[str, float]:
        return {v: self.framing[v].mean for v in FRAMING_VALUES if v in self.framing}

    def tone_means(self) -> Dict[str, float]:
        return {v: self.tone[v].mean for v in TONE_VALUES if v in self.tone}


class SusceptibilityEstimator:
    """Per-customer Bayesian belief over conversational susceptibility,
    updated only from observed replies. Construct once and feed it
    (message, response) pairs as they resolve over the wall.

    ``prior_alpha`` / ``prior_beta`` set the Beta prior for a lever value the
    company has never yet exercised (default Beta(1,1) -- uniform, maximal
    humility). ``latency_scale`` (C-S5, in abstract steps) governs how much a
    fast reply counts for over a slow one; ``latency_weight`` is the maximum
    extra Beta weight a zero-latency-limit positive would earn. Both are
    declared parameters, not hardcoded clocks.
    """

    def __init__(
        self,
        prior_alpha: float = 1.0,
        prior_beta: float = 1.0,
        latency_scale: float = 3.0,
        latency_weight: float = 0.5,
    ) -> None:
        if prior_alpha <= 0 or prior_beta <= 0:
            raise ValueError("Beta prior parameters must be strictly positive")
        if latency_scale <= 0:
            raise ValueError("latency_scale must be strictly positive (steps)")
        if latency_weight < 0:
            raise ValueError("latency_weight must be non-negative")
        self._prior_alpha = float(prior_alpha)
        self._prior_beta = float(prior_beta)
        self._latency_scale = float(latency_scale)
        self._latency_weight = float(latency_weight)
        self._beliefs: Dict[str, CustomerBelief] = {}
        # C-S2 idempotency: response_ids already folded in. A repeat is a no-op.
        self._seen_response_ids: set[str] = set()

    # -- belief access -----------------------------------------------------

    def _belief(self, customer_id: str) -> CustomerBelief:
        b = self._beliefs.get(customer_id)
        if b is None:
            b = CustomerBelief()
            self._beliefs[customer_id] = b
        return b

    def _framing_counts(self, customer_id: str, value: str) -> _BetaCounts:
        b = self._belief(customer_id)
        c = b.framing.get(value)
        if c is None:
            c = _BetaCounts(self._prior_alpha, self._prior_beta)
            b.framing[value] = c
        return c

    def _tone_counts(self, customer_id: str, value: str) -> _BetaCounts:
        b = self._belief(customer_id)
        c = b.tone.get(value)
        if c is None:
            c = _BetaCounts(self._prior_alpha, self._prior_beta)
            b.tone[value] = c
        return c

    def belief(self, customer_id: str) -> CustomerBelief:
        """The company's current belief about a customer. A customer never
        messaged returns an empty (all-prior) belief -- honest ignorance,
        never a fabricated point estimate."""
        return self._beliefs.get(customer_id, CustomerBelief())

    # -- the update (observed replies ONLY) --------------------------------

    def _latency_bonus(self, latency: int) -> float:
        """Extra Beta weight a POSITIVE reply earns for arriving quickly. A
        fast reply (small ``latency``) is stronger evidence the message
        landed; the bonus decays exponentially over ``latency_scale`` steps
        toward 0 for a very late reply. latency is guaranteed >=1 by the seam
        contract (a non-positive latency is unrepresentable, C-S3)."""
        return self._latency_weight * math.exp(-(latency - 1) / self._latency_scale)

    def observe_wire(
        self,
        customer_id: str,
        message: ConversationMessage,
        wire: Any,
    ) -> bool:
        """Fold in one reply that arrived AS A WIRE MESSAGE -- the entry point a
        real customer-contact platform reaches, and the one the live gap ledger
        now uses (atom EP6_wall_protocol_typing).

        This is EP6's claim made concrete for this crossing: a real counterparty
        hands over bytes and a mock hands over an object, and that is the ONLY
        place the two observably differ. Coming through here they are the same,
        because the message has passed the same envelope refusals and the same
        payload refusals either way.

        Raises ``WallProtocolError`` on anything malformed -- one exception type
        at the seam, and never a half-built object reaching the belief update
        below. A refusal is NOT an observation: nothing is marked seen, so a
        corrected re-delivery of the same ``response_id`` can still land.

        A NON-OK ENVELOPE IS REFUSED ON THIS SEAM, and that is a contract fact
        rather than a strictness preference: silence is an ACTION here
        (``ResponseAction.NO_REPLY``), not an absent payload, so every honest
        conversation answer is an OK carrying an observation. A payload-less
        envelope is therefore a malformed crossing and not a legitimate "not
        yet" -- accepting it quietly would let a broken counterparty erase
        replies the company should have learned from.

        The absent payload is tested for directly rather than through the
        status enum, and not to save an import: ``WallResponse.__post_init__``
        already makes "payload is None" and "status is not OK" the SAME fact,
        so reading the status here would add a second wall crossing that asks
        nothing the first one has not already answered -- and channel C of
        ``tools/wall_channel_census.py`` is a shrink-only list.
        """
        response = decode_response(wire, decode_payload=decode_observable_payload)
        if response.payload is None:
            raise WallProtocolError(
                "CONTRACT_VIOLATION",
                f"conversation response {response.correlation_id!r} arrived with status "
                f"{response.status.value} and no observation -- on this seam silence is "
                "the NO_REPLY action, so every answer carries a payload",
            )
        return self.observe_response(customer_id, message, response.payload)

    def observe_response(
        self,
        customer_id: str,
        message: ConversationMessage,
        response: ConversationResponse,
    ) -> bool:
        """Fold one observed reply into the customer's belief. Returns True if
        applied, False if this ``response_id`` was already folded in (C-S2
        idempotent no-op).

        ``customer_id`` is company-owned context (the company knows who it
        messaged); it is NOT read from the wall. ``message`` is the company's
        OWN outbound record (which framing/tone it chose). ``response`` is the
        observable that came back. NOTHING here reads a susceptibility scalar
        -- the update is a function of (framing_value, tone_value, action,
        latency) only.
        """
        # Contract-level async/pairing guard (C-S3): a response must reference
        # this message and land strictly after it. A mis-paired or same-step
        # response is a defect, surfaced loudly, never silently folded in.
        validate_response_follows_message(message, response)

        if response.response_id in self._seen_response_ids:
            return False  # C-S2: already counted, harmless no-op

        if response.action in _POSITIVE_ACTIONS:
            positive = True
        elif response.action in _NEGATIVE_ACTIONS:
            positive = False
        else:  # pragma: no cover - defensive: a new ResponseAction must be triaged
            raise ValueError(
                f"unhandled ResponseAction {response.action!r} -- a new observable "
                "action must be explicitly classified positive/negative before it "
                "can update a belief (fail-closed, never silently ignored)"
            )

        framing_value = message.framing if message.framing in FRAMING_VALUES else "neutral_framed"
        tone_value = message.tone if message.tone in TONE_VALUES else "neutral_toned"

        fc = self._framing_counts(customer_id, framing_value)
        tc = self._tone_counts(customer_id, tone_value)

        if positive:
            weight = 1.0 + self._latency_bonus(response.latency)
            fc.alpha += weight
            tc.alpha += weight
        else:
            fc.beta += 1.0
            tc.beta += 1.0

        self._seen_response_ids.add(response.response_id)
        return True

    def observe_many(
        self,
        pairs: Iterable[Tuple[str, ConversationMessage, ConversationResponse]],
    ) -> int:
        """Fold in many (customer_id, message, response) triples. Returns how
        many were newly applied (duplicates skipped, C-S2). Order-independent."""
        applied = 0
        for customer_id, message, response in pairs:
            if self.observe_response(customer_id, message, response):
                applied += 1
        return applied

    # -- what the generator asks: which lever to send ----------------------

    @staticmethod
    def _argmax_value(means: Dict[str, float], default: str) -> str:
        if not means:
            return default
        best_value = max(means, key=means.__getitem__)
        best = means[best_value]
        # No meaningful separation from the field -> no signal -> default.
        others = [m for v, m in means.items() if v != best_value]
        if others and (best - max(others)) < _NEUTRAL_EPSILON:
            return default
        return best_value

    def best_framing_value(self, customer_id: str) -> str:
        """The framing string the generator should send next -- the value the
        belief rates highest, or ``neutral_framed`` when the belief separates
        no lever (no data, or a dead heat)."""
        return self._argmax_value(self.belief(customer_id).framing_means(), "neutral_framed")

    def best_tone_value(self, customer_id: str) -> str:
        return self._argmax_value(self.belief(customer_id).tone_means(), "neutral_toned")

    # -- what F1c compares: the inferred susceptibility category ------------

    def inferred_framing_susceptibility(self, customer_id: str) -> str:
        """The company's best guess at the customer's hidden FramingSusceptibility
        CATEGORY (loss_averse / gain_responsive / neutral). This is a BELIEF,
        explicitly allowed to be wrong; the harness scores it against the SIM's
        true scalar. Empty belief -> ``neutral`` (honest default)."""
        return _FRAMING_VALUE_TO_CATEGORY[self.best_framing_value(customer_id)]

    def inferred_tone_susceptibility(self, customer_id: str) -> str:
        return _TONE_VALUE_TO_CATEGORY[self.best_tone_value(customer_id)]

    def posterior_report(self, customer_id: str) -> Dict[str, Dict[str, float]]:
        """The full posterior-mean vectors + inferred categories for one
        customer -- the surface F1c reads to compute the belief-vs-truth gap.
        Pure company belief; carries no ground truth."""
        b = self.belief(customer_id)
        return {
            "framing_means": b.framing_means(),
            "tone_means": b.tone_means(),
            "inferred": {
                "framing_susceptibility": self.inferred_framing_susceptibility(customer_id),
                "tone_susceptibility": self.inferred_tone_susceptibility(customer_id),
            },
        }
