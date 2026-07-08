"""Household engagement-level archetype (Phase 2 Layer 1, docs/design/
CORE_FIDELITY_PHASES.md: "household segments & psychology").

Phase 1's audit found `company/crm/churn_model.py`'s active/passive renewal
split real but *flat*: every renewal draws independently against the same
population-wide 35% active-rate (Ofgem Consumer Engagement Surveys
2018-2019; CMA 2016), so the model has no persistent household-level
engagement trait -- the same customer could roll dice into "active" one
renewal and "disengaged" the next, which is not how real shopping behaviour
works (some households reliably shop around every renewal; others never
do). This module gives each customer a fixed, deterministic engagement
archetype for their whole tenure, calibrated so the population-weighted
aggregate still reproduces the existing anchored 35% figure.

Anchors (docs/market_research/svt_rates_active_passive_2016_2025.md, H
confidence, Ofgem Consumer Engagement Survey 2018): of SVT customers, 29%
had sat 3+ years without switching (used here as the DISENGAGED population
share proxy), 23% under 3 years / switched once (PASSIVE proxy); the
remaining ~48% had switched more than once (ACTIVE proxy). The per-archetype
per-renewal ACTIVE probabilities below are a calibration CHOICE, not
independently sourced -- tuned only so the weighted aggregate lands at the
existing anchored ~35% (0.48*0.65 + 0.23*0.15 + 0.29*0.02 ≈ 0.352),
honestly flagged as such per the Anchored-noise law.

Layer 1 scope: engagement_level only. Fuel-poverty/income-band, payment-
method-mix, tenure, occupancy, and complaint-propensity archetype threading
(the remaining dimensions in CORE_FIDELITY_PHASES.md's Phase 1 archetype
table) are explicit backlog, not built this pass -- see
docs/market_research/ASSUMPTIONS.md's "Household Segment & Psychology"
section for real anchors already registered for those (ONS Census 2021
occupancy, EHS 2023-24 tenure, DESNZ fuel poverty/payment-method).

⚠ Recalibration flag (docs/market_research/ASSUMPTIONS.md, same section):
a MORE RECENT Ofgem Retail Market Indicators series (Oct 2025) puts the
real active-tariff share at ~45%, materially higher than the ~35% this
module deliberately preserves (itself sourced from the older 2018-2019
Consumer Engagement Survey, already baked into
company/crm/churn_model.py::PASSIVE_RENEWAL_RATE before this phase).
Recalibrating the population-wide aggregate is a separate, larger decision
(shifts churn/revenue dynamics broadly) -- not actioned unilaterally here,
flagged for director review.

Deterministic assignment: `random.Random(f"engagement_{customer_id}")`,
matching this codebase's standing per-customer-deterministic convention.
"""
from __future__ import annotations

import random
from enum import Enum


class EngagementLevel(str, Enum):
    ACTIVE = "active"
    PASSIVE = "passive"
    DISENGAGED = "disengaged"


# Population shares -- Ofgem Consumer Engagement Survey 2018 proxy (see
# module docstring). Order matters for the cumulative draw below.
ENGAGEMENT_POPULATION_SHARE: dict[EngagementLevel, float] = {
    EngagementLevel.ACTIVE: 0.48,
    EngagementLevel.PASSIVE: 0.23,
    EngagementLevel.DISENGAGED: 0.29,
}

# Per-archetype active-renewal probability -- a calibration choice (NOT
# independently sourced), tuned so the population-weighted aggregate
# reproduces company/crm/churn_model.py's existing anchored ~35% aggregate
# active-renewal rate. See module docstring for the arithmetic.
_ACTIVE_RENEWAL_PROBABILITY_BY_ENGAGEMENT: dict[EngagementLevel, float] = {
    EngagementLevel.ACTIVE: 0.65,
    EngagementLevel.PASSIVE: 0.15,
    EngagementLevel.DISENGAGED: 0.02,
}

assert abs(sum(ENGAGEMENT_POPULATION_SHARE.values()) - 1.0) < 1e-9


def engagement_level_for_customer(customer_id: str) -> EngagementLevel:
    """Deterministic per-customer engagement archetype, stable for the
    customer's whole tenure (a persistent behavioural trait, not redrawn
    per renewal)."""
    rng = random.Random(f"engagement_{customer_id}")
    roll = rng.random()
    cumulative = 0.0
    for level, share in ENGAGEMENT_POPULATION_SHARE.items():
        cumulative += share
        if roll < cumulative:
            return level
    return EngagementLevel.DISENGAGED  # float-rounding fallback


def active_renewal_probability(engagement_level: EngagementLevel) -> float:
    """Per-renewal probability this customer's engagement archetype
    actively renews (picks a new fixed deal) rather than passively rolling
    to SVT. Passed as a plain float into
    company/crm/churn_model.py::is_active_renewal -- that module stays free
    of any simulation.* import (epistemic wall)."""
    return _ACTIVE_RENEWAL_PROBABILITY_BY_ENGAGEMENT[engagement_level]


def active_renewal_probability_for_customer(customer_id: str) -> float:
    """Convenience: resolve a customer's engagement archetype and its
    active-renewal probability in one call -- the typical call site
    (simulation/run_phase2b.py) only needs the final float."""
    return active_renewal_probability(engagement_level_for_customer(customer_id))
