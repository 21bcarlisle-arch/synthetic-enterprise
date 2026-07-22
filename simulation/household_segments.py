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

Population shares (R13 curriculum ruling, director console 2026-07-22 —
docs/design/ENGAGEMENT_MIX_RECONCILIATION_2026-07-22.md): ACTIVE 0.45 /
PASSIVE 0.35 / DISENGAGED 0.20, anchored to the Ofgem Retail Market
Indicators "default tariffs" panel as of Oct 2025 (non-prepayment domestic
electricity: 45.1% actively-chosen; 54.9% default, split 34.6% held <3yr
[the churning middle → PASSIVE proxy] and 20.3% held 3+yr [clearly
disengaged → DISENGAGED proxy]). Q-A of the ruling: the archetype stays a
BEHAVIOURAL disposition ("shops ~every renewal", drives active_renewal_
probability below) — the Ofgem STOCK split (on-a-chosen-tariff-now) anchors
only the SHARES, it does not redefine the archetype (the two measure
different objects; see the reconciliation doc §0). The default-tariff
cohort (PASSIVE+DISENGAGED = 0.55) is a genuine majority — honouring the
board's veteran "disengaged majority" instinct — while hard-DISENGAGED
stays at the honest 0.20, not a majority (the board's strong form
overshoots the hard Ofgem number). Neither side adopted blind.

The per-archetype per-renewal ACTIVE probabilities below are UNCHANGED
(0.65 / 0.15 / 0.02) — a calibration CHOICE, not independently sourced. The
weighted aggregate is near-neutral vs the prior anchor: 0.45*0.65 +
0.35*0.15 + 0.20*0.02 ≈ 0.349 (was ~0.352). The re-anchor fixes the
within-book SHAPE without re-levelling the portfolio's aggregate active-
renewal rate. Honestly flagged as such per the Anchored-noise law.

Layer 1 scope: engagement_level only. Layer 2 dimensions 1-4 (payment-
method mix, fuel poverty, tenure, occupancy -- see PaymentChannel/
TenureType/OccupancyBand below) added 2026-07-09/10. Complaint-
propensity as its own archetype (distinct from occupancy feeding INTO
complaint probability, which IS built) is the one remaining dimension
in CORE_FIDELITY_PHASES.md's Phase 1 archetype table not yet built.

✔ Recalibration RESOLVED (R13 ruling, director console 2026-07-22). The
prior ⚠ flag (older 2018-19 Consumer Engagement Survey shares 0.48/0.23/0.29
vs the newer Ofgem RMI Oct-2025 ~45% active) is now closed: the shares are
re-anchored to the Oct-2025 stock split as above. NOTE the aggregate active-
renewal RATE is deliberately left near its prior ~35% anchor (per-archetype
probabilities held) — raising the aggregate itself toward the ~45% recovery
regime is a SEPARATE, larger R13 lever, NOT taken here (R12 anti-goal-seek:
the aggregate is a diagnostic, not a target).
Q-B of the ruling: the mix is kept STATIC (a single behavioural mix); a
hardcoded regime-timed schedule is explicitly forbidden (it would be the
MC-1 script class). Instead, "engagement responds to market state (offer
availability, fixed-vs-SVT spread)" is registered as a FUTURE MECHANISM
PROPOSAL through the gate — see docs/design/ENGAGEMENT_MARKET_STATE_
RESPONSIVENESS_PROPOSAL_2026-07-22.md (provenance: proposal, not built).

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


# Population shares -- Ofgem RMI Oct-2025 stock anchor, R13 ruling 2026-07-22
# (see module docstring). Order matters for the cumulative draw below.
ENGAGEMENT_POPULATION_SHARE: dict[EngagementLevel, float] = {
    EngagementLevel.ACTIVE: 0.45,
    EngagementLevel.PASSIVE: 0.35,
    EngagementLevel.DISENGAGED: 0.20,
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


class PaymentChannel(str, Enum):
    DIRECT_DEBIT = "direct_debit"
    STANDARD_CREDIT = "standard_credit"


# Layer 2, dimension 1 (payment-method mix): the exact named gap in
# docs/market_research/ASSUMPTIONS.md's "Household Segment & Psychology"
# section -- `simulation/arrears_engine.py::payment_method()` was
# segment-aware (resi/SME/I&C) but returned a FLAT "direct_debit" for every
# resi customer, i.e. the whole population, when real suppliers have a
# genuinely mixed payment-method book.
#
# Anchor: DESNZ "Quarterly Energy Prices: June 2026" commentary, "Payment
# methods" section (fetched 2026-07-08) -- Direct Debit was 72% of standard
# electricity customers and 75% of gas customers, end of March 2026. The
# remaining ~25-28% (prepayment + standard credit combined) has NO published
# sub-split in the fetched commentary text (genuine registered gap, not
# guessed) -- so that remainder is collapsed into one STANDARD_CREDIT bucket
# here rather than inventing an unanchored three-way split. Recovering the
# PPM-vs-standard-credit sub-split (and PPM's genuinely different mechanic --
# pre-payment, self-disconnect risk, no "returned" event -- rather than a
# late/missed bank-transfer payment) is explicit backlog, flagged again here.
DIRECT_DEBIT_SHARE_BY_FUEL: dict[str, float] = {
    "electricity": 0.72,
    "gas": 0.75,
}


def payment_channel_for_customer(customer_id: str, fuel: str = "electricity") -> PaymentChannel:
    """Deterministic per-customer, per-fuel payment-channel archetype,
    stable for the account's whole tenure. Keyed on (customer_id, fuel) --
    not just customer_id -- because the anchor itself is fuel-specific
    (72% elec vs 75% gas) and this codebase already bills/meters electricity
    and gas as two independent accounts (own MPAN/MPRN) per household."""
    share = DIRECT_DEBIT_SHARE_BY_FUEL.get(fuel, DIRECT_DEBIT_SHARE_BY_FUEL["electricity"])
    rng = random.Random(f"paychannel_{customer_id}_{fuel}")
    return PaymentChannel.DIRECT_DEBIT if rng.random() < share else PaymentChannel.STANDARD_CREDIT


# Layer 2 dimension 2 (fuel poverty / income-band, 2026-07-09): DESNZ "Annual
# Fuel Poverty Statistics in England, 2025 (2024 data)" (fetched 2026-07-08,
# see ASSUMPTIONS.md) gives fuel-poverty rate (LILEE metric) BY ELECTRICITY
# PAYMENT METHOD: prepayment 22.3%, standard credit 18.5%, direct debit 8.8%.
# This codebase's own PaymentChannel collapses prepayment+standard-credit
# into one STANDARD_CREDIT bucket (see the DD-share note above -- the real
# sub-split isn't published), so the non-DD rate used here is the unweighted
# mean of the two published non-DD rates (22.3+18.5)/2 = 20.4% -- an honest
# blend, not an independently anchored figure, flagged as such.
FUEL_POVERTY_RATE_BY_CHANNEL: dict[PaymentChannel, float] = {
    PaymentChannel.DIRECT_DEBIT: 0.088,
    PaymentChannel.STANDARD_CREDIT: 0.204,
}


def fuel_poverty_for_customer(customer_id: str, payment_channel: PaymentChannel) -> bool:
    """Deterministic per-customer fuel-poverty flag, conditioned on the
    customer's own payment-channel archetype (real anchors are published
    conditional on payment method, not as a flat population rate) -- stable
    for the account's tenure, same convention as the other archetypes in
    this module."""
    rate = FUEL_POVERTY_RATE_BY_CHANNEL.get(payment_channel, FUEL_POVERTY_RATE_BY_CHANNEL[PaymentChannel.STANDARD_CREDIT])
    rng = random.Random(f"fuelpoverty_{customer_id}")
    return rng.random() < rate


class TenureType(str, Enum):
    OWNER_OCCUPIER = "owner_occupier"
    PRIVATE_RENTER = "private_renter"
    SOCIAL_RENTER = "social_renter"


# Layer 2 dimension 3 (tenure, 2026-07-09): EHS 2023-24 Headline Report on
# Demographics and Household Resilience, Chapter 1 "Trends in tenure"
# (MHCLG, fetched 2026-07-08, see ASSUMPTIONS.md) -- England housing tenure
# split: owner-occupier 65% (35% outright + 30% mortgagors, combined here
# since this module doesn't yet model outright-vs-mortgaged), private
# renters 19%, social renters 16% (10% housing association + 6% local
# authority, combined -- the mechanism this dimension feeds, switching
# friction, doesn't currently distinguish the two social-rent sub-types).
TENURE_POPULATION_SHARE: dict[TenureType, float] = {
    TenureType.OWNER_OCCUPIER: 0.65,
    TenureType.PRIVATE_RENTER: 0.19,
    TenureType.SOCIAL_RENTER: 0.16,
}

assert abs(sum(TENURE_POPULATION_SHARE.values()) - 1.0) < 1e-9


def tenure_for_customer(customer_id: str) -> TenureType:
    """Deterministic per-customer tenure archetype, stable for the
    customer's whole tenure (a persistent housing-status trait) -- same
    convention as engagement_level/payment_channel above."""
    rng = random.Random(f"tenure_{customer_id}")
    roll = rng.random()
    cumulative = 0.0
    for tenure, share in TENURE_POPULATION_SHARE.items():
        cumulative += share
        if roll < cumulative:
            return tenure
    return TenureType.SOCIAL_RENTER  # float-rounding fallback


class OccupancyBand(str, Enum):
    ONE_PERSON = "one_person"
    TWO_PERSON = "two_person"
    THREE_TO_FOUR_PERSON = "three_to_four_person"
    FIVE_PLUS_PERSON = "five_plus_person"


# Layer 2 dimension 4 (occupancy / household size, 2026-07-10): ONS Census
# 2021 table TS017 "Household size" (England-only aggregate, computed
# directly from the published LTLA-level CSV by a discovery-agent pass,
# fetched 2026-07-08, see ASSUMPTIONS.md) -- H confidence, primary census
# microdata. 1-person 30.1%, 2-person 34.0%, 3-4-person 28.9% (3-person
# 16.0% + 4-person 12.9%, combined here since this module doesn't yet need
# the finer split), 5+-person 7.0% (5/6/7/8+-person 4.5/1.5/0.5/0.4%,
# combined). Mean 2.37 persons/household, cross-checked against EHS
# 2023-24 (2.2-2.4 range) -- consistent.
OCCUPANCY_POPULATION_SHARE: dict[OccupancyBand, float] = {
    OccupancyBand.ONE_PERSON: 0.301,
    OccupancyBand.TWO_PERSON: 0.340,
    OccupancyBand.THREE_TO_FOUR_PERSON: 0.289,
    OccupancyBand.FIVE_PLUS_PERSON: 0.070,
}

assert abs(sum(OCCUPANCY_POPULATION_SHARE.values()) - 1.0) < 1e-9


def occupancy_for_customer(customer_id: str) -> OccupancyBand:
    """Deterministic per-customer occupancy (household-size) archetype,
    stable for the customer's whole tenure -- same convention as
    engagement_level/payment_channel/tenure above."""
    rng = random.Random(f"occupancy_{customer_id}")
    roll = rng.random()
    cumulative = 0.0
    for band, share in OCCUPANCY_POPULATION_SHARE.items():
        cumulative += share
        if roll < cumulative:
            return band
    return OccupancyBand.FIVE_PLUS_PERSON  # float-rounding fallback
