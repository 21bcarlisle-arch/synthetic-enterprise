"""Nudge Physics Layer 1 -- loss-aversion offer framing (NUDGE_PHYSICS.md).

Rich's framing: the company can persuade people EVEN IF IT DOESN'T KNOW IT --
nudge mechanics live in the SIM; the company discovers them empirically.

Ground truth of WHY a customer responds to a retention offer's framing lives
here, invisible to the company. Each customer has a hidden framing
susceptibility (loss-averse / gain-responsive / neutral) assigned once,
deterministically, at acquisition. framing_effectiveness_multiplier() is
called only from simulation/run_phase2b.py (SIM-side) to adjust the actual
retention-offer effectiveness used in the dice roll (customer_events.py's
roll_lifecycle_event). The company never imports this module -- it only
observes the framing_type attribute it itself chose (see
company/policy/decision_policy.py::framing_type_for) and the retained/churned
outcome, via company/analytics/nudge_discovery.py.

Effect-size grounding (population-anchored, not a fixed constant, matching
this project's convention elsewhere): Kahneman and Tversky (1979) loss-aversion;
applied-marketing magnitude from Levin, Schneider and Gaeth (1998) meta-review,
not the larger raw lab coefficient. See
docs/market_research/NUDGE_PHYSICS_BENCHMARKS.md.
"""
from __future__ import annotations

import hashlib
from enum import Enum


class FramingSusceptibility(str, Enum):
    LOSS_AVERSE = "loss_averse"
    GAIN_RESPONSIVE = "gain_responsive"
    NEUTRAL = "neutral"


_SUSCEPTIBILITY_WEIGHTS: tuple[tuple[FramingSusceptibility, float], ...] = (
    (FramingSusceptibility.LOSS_AVERSE, 0.45),
    (FramingSusceptibility.GAIN_RESPONSIVE, 0.35),
    (FramingSusceptibility.NEUTRAL, 0.20),
)

_MATCHED_FRAMING_UPLIFT_RANGE: tuple[float, float] = (0.10, 0.35)

_MATCHING_FRAMING: dict[FramingSusceptibility, str] = dict([
    (FramingSusceptibility.LOSS_AVERSE, "loss_framed"),
    (FramingSusceptibility.GAIN_RESPONSIVE, "gain_framed"),
])


def _stable_fraction(seed: str) -> float:
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    return (int(digest, 16) % 10_000) / 10_000.0


def susceptibility_for(customer_id: str) -> FramingSusceptibility:
    roll = _stable_fraction("nudge_susceptibility_" + customer_id)
    cumulative = 0.0
    for label, weight in _SUSCEPTIBILITY_WEIGHTS:
        cumulative += weight
        if roll < cumulative:
            return label
    return FramingSusceptibility.NEUTRAL


def framing_effectiveness_multiplier(customer_id: str, framing_type: str) -> float:
    susceptibility = susceptibility_for(customer_id)
    if susceptibility == FramingSusceptibility.NEUTRAL:
        return 1.0
    if _MATCHING_FRAMING.get(susceptibility) != framing_type:
        return 1.0
    lo, hi = _MATCHED_FRAMING_UPLIFT_RANGE
    frac = _stable_fraction("nudge_uplift_" + customer_id)
    return 1.0 + lo + frac * (hi - lo)


# --- NUDGE_PHYSICS.md remaining mechanism: debt-collection letter tone/framing
# (2026-07-10). Same SIM/company split as Layer 1 above: a hidden per-customer
# tone-susceptibility drives the real response magnitude; the company only
# ever chooses and observes the tone attribute it sends (company/policy/
# decision_policy.py::tone_for()), discovering which tone lifts payment
# response for which segment via company/analytics/nudge_discovery.py --
# without ever seeing this module's hidden trait.
#
# Anchor: Cabinet Office/BIT, "Applying Behavioural Insights to Reduce Fraud,
# Error and Debt" (2012) -- +3 to +10pp additive uplift in payment response
# from debt-collection letter tone/framing (M confidence: cross-sector --
# tax/fines, not energy-specific). See
# docs/market_research/NUDGE_PHYSICS_BENCHMARKS.md.

class ToneSusceptibility(str, Enum):
    EMPATHETIC_RESPONSIVE = "empathetic_responsive"
    FIRM_RESPONSIVE = "firm_responsive"
    NEUTRAL = "neutral"


_TONE_SUSCEPTIBILITY_WEIGHTS: tuple[tuple[ToneSusceptibility, float], ...] = (
    (ToneSusceptibility.EMPATHETIC_RESPONSIVE, 0.45),
    (ToneSusceptibility.FIRM_RESPONSIVE, 0.35),
    (ToneSusceptibility.NEUTRAL, 0.20),
)

# Additive uplift range (Cabinet Office/BIT anchor, +3 to +10pp), applied as
# a multiplier on the base on-time probability -- same "matched tone only"
# mechanic as the retention-offer framing above, no separate calibration
# invented for the magnitude.
_MATCHED_TONE_UPLIFT_RANGE: tuple[float, float] = (0.03, 0.10)

_MATCHING_TONE: dict[ToneSusceptibility, str] = dict([
    (ToneSusceptibility.EMPATHETIC_RESPONSIVE, "empathetic_toned"),
    (ToneSusceptibility.FIRM_RESPONSIVE, "firm_toned"),
])


def tone_susceptibility_for(customer_id: str) -> ToneSusceptibility:
    roll = _stable_fraction("tone_susceptibility_" + customer_id)
    cumulative = 0.0
    for label, weight in _TONE_SUSCEPTIBILITY_WEIGHTS:
        cumulative += weight
        if roll < cumulative:
            return label
    return ToneSusceptibility.NEUTRAL


def tone_effectiveness_multiplier(customer_id: str, tone: str) -> float:
    """Multiplier on payment_outcome()'s on-time probability. 1.0 (no
    effect) unless the customer's hidden tone-susceptibility matches the
    tone the company chose to send."""
    susceptibility = tone_susceptibility_for(customer_id)
    if susceptibility == ToneSusceptibility.NEUTRAL:
        return 1.0
    if _MATCHING_TONE.get(susceptibility) != tone:
        return 1.0
    lo, hi = _MATCHED_TONE_UPLIFT_RANGE
    frac = _stable_fraction("tone_uplift_" + customer_id)
    return 1.0 + lo + frac * (hi - lo)
