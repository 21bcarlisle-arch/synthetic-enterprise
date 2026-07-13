"""C9_cantpay_wontpay_classifier -- company-side arrears can't-pay/won't-pay twin.

The ARCHETYPE company twin of the coupled triad. The company cannot see the SIM's
hidden ABILITY x WILLINGNESS answer key (``simulation.willingness_classification``,
W2_7). It never reads it. Given an arrears account -- the SINGLE observable
``is_in_arrears()`` is identical across the three non-paying cells (CAN_WONT,
CANNOT_WILL, CANNOT_WONT) -- this classifier must decide, from OBSERVABLES ONLY,
whether the customer:

    * genuinely CANNOT afford to pay  (the "can't-pay": ability = cannot), or
    * CAN afford it but WON'T          (the strategic "won't-pay": can/wont),

and then whether to PURSUE (collections/enforcement) or FORBEAR (support). The
observables it reads are exactly those a real UK supplier holds on an arrears
account:

    * payment behaviour  -- has the customer made any PART-PAYMENT (paying what
                            they can, a can't-pay-but-willing signal) or paid
                            nothing at all.
    * engagement         -- does the customer RESPOND to contact (calls, letters,
                            portal), or avoid it. Strategic non-payers avoid;
                            customers who want to resolve engage.
    * disclosure         -- has the customer DISCLOSED hardship / asked for a
                            payment plan / a support scheme / the Priority
                            Services Register.
    * consumption        -- metered kWh vs the account's own baseline. A sustained
                            COLLAPSE is self-rationing (going cold to save money):
                            a hardship / cannot-pay corroborant.

THE CONFOUND (the whole point). A strategic won't-pay and a genuine can't-pay both
emit the identical observable: an unpaid bill. The company's only handles are
behavioural (engagement, part-payment, disclosure) and consumption -- and those
handles are systematically FOOLED by the hardest cases: a genuine can't-pay who is
DISENGAGED (shame, chaotic life, digital exclusion) looks exactly like a strategic
non-payer, and gets read as won't-pay -- the EXPENSIVE error (pressuring a
vulnerable household = a Consumer-Duty / ability-to-pay breach, the 8:1-weighted
harm). This classifier is ALLOWED TO BE WRONG. Do NOT "improve" it with visibility
a real supplier lacks -- that would be an epistemic-wall violation, not a fix.

THE DECISION GATE (director-signed curriculum, R13 / HARM_COST_WEIGHTS_DECISION.md).
The harm:loss ratio R = 8:1 is SIGNED: treating a genuine can't-pay as a won't-pay
(pursuing a vulnerable customer) is 8x as costly as forbearing a strategic
defaulter (moral hazard + bad debt). With p = P(won't-pay | observables) -- for an
arrears account the ONLY can-pay cell is the strategic CAN_WONT, so p is
equivalently P(can-pay | in arrears) -- the Bayes-optimal decision under that cost
matrix is:

    PURSUE iff  p > R/(R+1)        (at R=8: pursue only when p > 8/9 ~= 0.889)
    FORBEAR otherwise
    flip-point odds  R* = p/(1-p)  (pursue iff R* > R)

R is read as a CONSTANT here (single-sourced from the director-signed
``background.gap_metric.HARM_RATIO_R``). It is NEVER tuned toward a gap number
(R12 anti-goal-seek / R13 curriculum wall).

EPISTEMIC WALL (.claude/rules/epistemic-wall-company.md). This module imports
NOTHING from ``simulation.*`` / ``sim.*``. Its inputs are observables a real
supplier holds; its scoring weights are supplier-side domain reasoning, set
DELIBERATELY BLIND to the SIM's hidden willingness-incidence / budget parameters --
that independence is what makes the measured gap a real measurement, not a
tautology (R15). Pure module: plain values in, a dataclass out; no wall-clock, no
unseeded randomness (C-S2); it works on whatever observation window it is given and
never assumes a complete or ordered batch (C-S1).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Sequence, Tuple

# R is director-signed curriculum -- single-sourced from the harness constant so
# the gate and the gap-metric can never drift apart. Importing a CONSTANT from the
# harness layer is not a wall crossing (no SIM internals flow through it); the
# epistemic verifier forbids only ``simulation.*`` reads in company code.
from background.gap_metric import HARM_RATIO_R


# ---------------------------------------------------------------------------
# Company-owned label space (the company's BELIEF -- never the SIM answer key).
# The 2x2 the shared metric scores: ABILITY x WILLINGNESS. For an arrears account
# the confound lives on the ABILITY axis (can-pay strategic vs cannot-pay genuine).
# ---------------------------------------------------------------------------
class Ability(str, Enum):
    CAN = "can"
    CANNOT = "cannot"


class Willingness(str, Enum):
    WILL = "will"
    WONT = "wont"


class Decision(str, Enum):
    """The action the gate authorises on an arrears account."""
    PURSUE = "pursue"      # collections / enforcement -- appropriate only for a
                           # confident strategic won't-pay (can afford it)
    FORBEAR = "forbear"    # support / payment plan / hold -- the safe default when
                           # ability is uncertain (8:1 harm asymmetry)


# ---------------------------------------------------------------------------
# Domain scoring weights -- supplier-side reasoning, FROZEN, never fitted to a SIM
# parameter or a gap number (R15 independence, R12/R13). Additive log-odds; each
# observable pushes the ability belief toward can-pay (+) or cannot-pay (-).
# ---------------------------------------------------------------------------
# ABILITY (P(can pay | observables)) --------------------------------------------
_ABILITY_PRIOR_LOGODDS = 0.0        # neutral: the company does NOT know the true
                                    # willingness incidence (that is SIM-hidden).
_W_CONSUMPTION_NORMAL = 1.2         # kWh at/above baseline -> living normally -> can
_W_CONSUMPTION_RATIONING = -1.6     # sustained kWh collapse -> self-rationing -> cannot
_W_ENGAGED_TOWARD_CANNOT = -0.6     # engages to resolve -> more often a genuine can't-pay
_W_NOT_ENGAGED_TOWARD_CAN = 0.6     # avoids contact -> the strategic pattern
_W_DISCLOSED_TOWARD_CANNOT = -1.4   # discloses hardship / asks for help -> cannot
_W_NOT_DISCLOSED_TOWARD_CAN = 0.4
_W_PARTPAY_TOWARD_CANNOT = -0.9     # pays what they can -> constrained ability -> cannot
_W_NO_PARTPAY_TOWARD_CAN = 0.4      # pays nothing despite means -> strategic
_CONSUMPTION_RATIONING_RATIO = 0.80  # recent/baseline at/below this = rationing
_CONSUMPTION_NORMAL_RATIO = 0.95     # recent/baseline at/above this = normal

# WILLINGNESS (P(willing to pay | observables)) ---------------------------------
_WILLINGNESS_PRIOR_LOGODDS = -0.4   # arrears with no positive signal leans won't
_W_ENGAGED_TOWARD_WILL = 1.3
_W_DISCLOSED_TOWARD_WILL = 0.9
_W_PARTPAY_TOWARD_WILL = 1.1


def _sigmoid(x: float) -> float:
    if x >= 0:
        z = math.exp(-x)
        return 1.0 / (1.0 + z)
    z = math.exp(x)
    return z / (1.0 + z)


# ---------------------------------------------------------------------------
# The director-signed pursue/forbear gate.
# ---------------------------------------------------------------------------
def pursue_threshold(harm_ratio: float = HARM_RATIO_R) -> float:
    """The p-threshold above which PURSUE is Bayes-optimal: R/(R+1). At R=8 this is
    8/9 ~= 0.889 -- pursue only when very confident the customer CAN pay."""
    return harm_ratio / (harm_ratio + 1.0)


def flip_point_odds(p: float) -> float:
    """The harm ratio at which the decision flips for a given p: R* = p/(1-p).
    PURSUE iff R* > R. Undefined at p=1 (certainty) -> returns +inf."""
    if p >= 1.0:
        return math.inf
    if p <= 0.0:
        return 0.0
    return p / (1.0 - p)


def pursue_forbear_gate(p_wont_pay: float,
                        harm_ratio: float = HARM_RATIO_R) -> Decision:
    """PURSUE iff p_wont_pay > R/(R+1), else FORBEAR (director-signed curriculum).

    ``p_wont_pay`` = P(strategic won't-pay | observables) = P(can-pay | in arrears).
    The strict ``>`` makes the harm-averse choice the tie-break default: at exactly
    the threshold the expected costs are equal, and FORBEAR is chosen (never pursue
    a household on a coin-flip). NOTE for the mutation test: this MUST be tested at
    p=0.9 (expect PURSUE) AND p=0.1 (expect FORBEAR) -- a p=0.5 coin-flip test
    passes an inverted gate, because p/(1-p) and (1-p)/p both equal 1 at p=0.5.
    """
    return Decision.PURSUE if p_wont_pay > pursue_threshold(harm_ratio) else Decision.FORBEAR


# ---------------------------------------------------------------------------
# Observation window + assessment dataclasses.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ArrearsObservationWindow:
    """Everything the company can OBSERVE about one arrears account. Every field is
    a real supplier-side record; none is SIM ground truth. Missing signals are
    simply absent (C-S1: partial observation is normal, never assumed complete)."""

    customer_id: str
    made_part_payment: Optional[bool] = None    # paid SOMETHING toward the arrears
    engaged: Optional[bool] = None              # responded to contact
    hardship_disclosed: Optional[bool] = None   # disclosed hardship / asked for help
    baseline_consumption_kwh: Optional[float] = None
    recent_consumption_kwh: Optional[float] = None


@dataclass(frozen=True)
class ArrearsAssessment:
    """The company's fallible BELIEF about one arrears account, plus the gate's
    action. ``p_can_pay`` is the probability driving the gate (= P(won't-pay) for an
    arrears account). ``quadrant`` projects the belief onto the 2x2 the shared
    classification metric reads."""

    customer_id: str
    ability: Ability
    willingness: Willingness
    p_can_pay: float                            # == P(strategic won't-pay | arrears)
    p_will_pay: float
    decision: Decision
    signals: dict = field(default_factory=dict)

    @property
    def quadrant(self) -> Tuple[str, str]:
        return (self.ability.value, self.willingness.value)

    def to_dict(self) -> dict:
        return {
            "customer_id": self.customer_id,
            "ability": self.ability.value,
            "willingness": self.willingness.value,
            "p_can_pay": round(self.p_can_pay, 4),
            "p_will_pay": round(self.p_will_pay, 4),
            "decision": self.decision.value,
            "signals": self.signals,
        }


def _consumption_ratio(window: ArrearsObservationWindow) -> Optional[float]:
    b = window.baseline_consumption_kwh
    r = window.recent_consumption_kwh
    if not b or r is None:
        return None
    return r / b


class CantPayWontPayClassifier:
    """Classifies arrears accounts can't-pay vs won't-pay and applies the
    director-signed pursue/forbear gate, from observables ONLY. Stateless and
    deterministic (C-S2); handles partial observation (C-S1)."""

    def __init__(self, harm_ratio: float = HARM_RATIO_R) -> None:
        self.harm_ratio = harm_ratio

    def assess(self, window: ArrearsObservationWindow) -> ArrearsAssessment:
        ratio = _consumption_ratio(window)
        engaged = window.engaged
        disclosed = window.hardship_disclosed
        part_pay = window.made_part_payment

        # --- ABILITY log-odds: P(can pay | observables) --------------------
        a = _ABILITY_PRIOR_LOGODDS
        if ratio is not None:
            if ratio <= _CONSUMPTION_RATIONING_RATIO:
                a += _W_CONSUMPTION_RATIONING
            elif ratio >= _CONSUMPTION_NORMAL_RATIO:
                a += _W_CONSUMPTION_NORMAL
        if engaged is not None:
            a += _W_ENGAGED_TOWARD_CANNOT if engaged else _W_NOT_ENGAGED_TOWARD_CAN
        if disclosed is not None:
            a += _W_DISCLOSED_TOWARD_CANNOT if disclosed else _W_NOT_DISCLOSED_TOWARD_CAN
        if part_pay is not None:
            a += _W_PARTPAY_TOWARD_CANNOT if part_pay else _W_NO_PARTPAY_TOWARD_CAN
        p_can = _sigmoid(a)

        # --- WILLINGNESS log-odds: P(willing to pay | observables) ---------
        w = _WILLINGNESS_PRIOR_LOGODDS
        if engaged:
            w += _W_ENGAGED_TOWARD_WILL
        if disclosed:
            w += _W_DISCLOSED_TOWARD_WILL
        if part_pay:
            w += _W_PARTPAY_TOWARD_WILL
        p_will = _sigmoid(w)

        ability = Ability.CAN if p_can >= 0.5 else Ability.CANNOT
        willingness = Willingness.WILL if p_will >= 0.5 else Willingness.WONT
        decision = pursue_forbear_gate(p_can, self.harm_ratio)

        signals = {
            "consumption_ratio": None if ratio is None else round(ratio, 4),
            "engaged": engaged,
            "hardship_disclosed": disclosed,
            "made_part_payment": part_pay,
            "ability_logodds": round(a, 4),
            "willingness_logodds": round(w, 4),
            "pursue_threshold": round(pursue_threshold(self.harm_ratio), 6),
        }
        return ArrearsAssessment(
            customer_id=window.customer_id,
            ability=ability,
            willingness=willingness,
            p_can_pay=p_can,
            p_will_pay=p_will,
            decision=decision,
            signals=signals,
        )

    def assess_many(
        self, windows: Sequence[ArrearsObservationWindow]
    ) -> List[ArrearsAssessment]:
        return [self.assess(w) for w in windows]
