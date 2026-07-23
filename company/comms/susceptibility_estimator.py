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
from typing import Dict, Iterable, Optional, Tuple

from interface.contracts.conversation_seam import (
    ConversationMessage,
    ConversationResponse,
    ResponseAction,
    validate_response_follows_message,
)

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
