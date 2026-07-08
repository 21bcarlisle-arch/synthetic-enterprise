"""Phase 2 Layer 1 (CORE_FIDELITY_PHASES.md): household engagement-level
archetype.

Tests simulation/household_segments.py: deterministic per-customer
assignment, population-share calibration, and the aggregate active-renewal
rate reproducing the existing anchored ~35% figure.
"""
import statistics

from simulation.household_segments import (
    ENGAGEMENT_POPULATION_SHARE,
    EngagementLevel,
    active_renewal_probability,
    active_renewal_probability_for_customer,
    engagement_level_for_customer,
)


def test_population_shares_sum_to_one():
    assert abs(sum(ENGAGEMENT_POPULATION_SHARE.values()) - 1.0) < 1e-9


def test_engagement_level_is_deterministic():
    a = engagement_level_for_customer("C1")
    b = engagement_level_for_customer("C1")
    assert a == b


def test_engagement_level_varies_across_customers():
    levels = {engagement_level_for_customer(f"C{i}") for i in range(200)}
    assert len(levels) == 3  # all three archetypes should appear across 200 customers


def test_engagement_level_returns_valid_enum():
    for i in range(50):
        level = engagement_level_for_customer(f"CUST{i}")
        assert level in EngagementLevel


def test_active_renewal_probability_ordering():
    """Active archetype must be more likely to actively renew than passive,
    which must be more likely than disengaged."""
    p_active = active_renewal_probability(EngagementLevel.ACTIVE)
    p_passive = active_renewal_probability(EngagementLevel.PASSIVE)
    p_disengaged = active_renewal_probability(EngagementLevel.DISENGAGED)
    assert p_active > p_passive > p_disengaged


def test_active_renewal_probability_in_valid_range():
    for level in EngagementLevel:
        p = active_renewal_probability(level)
        assert 0.0 <= p <= 1.0


def test_population_weighted_aggregate_reproduces_anchored_rate():
    """The whole point of the calibration: population share x per-archetype
    probability, weighted-summed, must land close to the existing anchored
    ~35% aggregate active-renewal rate already in company/crm/churn_model.py."""
    aggregate = sum(
        ENGAGEMENT_POPULATION_SHARE[level] * active_renewal_probability(level)
        for level in EngagementLevel
    )
    assert abs(aggregate - 0.35) < 0.02


def test_large_sample_matches_population_shares():
    """A large sample of distinct customer_ids should approximate the
    declared population shares (sanity check on the deterministic hash
    distribution, not just the declared constants)."""
    n = 3000
    counts = {level: 0 for level in EngagementLevel}
    for i in range(n):
        counts[engagement_level_for_customer(f"SAMPLE_{i}")] += 1
    for level, share in ENGAGEMENT_POPULATION_SHARE.items():
        observed = counts[level] / n
        assert abs(observed - share) < 0.03


def test_active_renewal_probability_for_customer_matches_manual_lookup():
    for i in range(20):
        cid = f"C{i}"
        expected = active_renewal_probability(engagement_level_for_customer(cid))
        assert active_renewal_probability_for_customer(cid) == expected


def test_large_sample_realized_active_renewal_rate_close_to_anchor():
    """A different, independent check from the arithmetic test above: draw
    a large sample of (customer engagement archetype, per-renewal Bernoulli
    outcome) pairs deterministically and confirm the REALIZED active rate
    -- not just the declared probabilities -- lands near 35%."""
    import random as _random
    n = 5000
    active_count = 0
    for i in range(n):
        cid = f"REALIZED_{i}"
        p = active_renewal_probability_for_customer(cid)
        active_count += _random.Random(f"outcome_{cid}").random() < p
    rate = active_count / n
    assert abs(rate - 0.35) < 0.03
