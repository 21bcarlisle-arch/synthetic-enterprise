"""W2_14 items 1-2 -- the continuous engagement latent beneath the three
ratified bins (docs/design/W2_14_CONTINUOUS_BEHAVIOURAL_ENGAGEMENT_MODEL_
DISCOVER.md §4).

The control that matters is the REFINEMENT IDENTITY: the R13-ratified
0.45/0.35/0.20 shares must be preserved BY CONSTRUCTION, not by a tolerance
test that could drift. Every test here is written to be able to FAIL on its own
named defect (R15) -- the mutation tests at the bottom prove it, in both
directions.
"""
from __future__ import annotations

import math
from collections import Counter

import pytest

from simulation import household_segments as hs
from simulation.household_segments import (
    ENGAGEMENT_POPULATION_SHARE,
    EngagementLevel,
    engagement_level_for_customer,
    engagement_level_from_propensity,
    engagement_propensity_bounds,
    engagement_propensity_for_customer,
)

# A wide id sweep: synthetic book ids, hand-authored ids, and shapes the sim
# actually uses (SYN-*, CUST-*, plain integers as strings).
SWEEP_IDS = (
    [f"C{i}" for i in range(3000)]
    + [f"SYN-{i:06d}" for i in range(500)]
    + [f"CUST-{i:04d}" for i in range(500)]
    + ["x", "resi-777", "", "C9", "unicode-ø-42"]
)


# ---------------------------------------------------------------------------
# 1. The identity (the whole point of the atom)
# ---------------------------------------------------------------------------
def test_refinement_identity_holds_for_every_customer_id():
    """engagement_level_from_propensity(propensity(cid)) == level(cid), ALWAYS.

    Not "within a tolerance" -- for every single id in the sweep. This is what
    makes the ratified share preservation structural (DISCOVER §1.3).
    """
    mismatches = [
        cid
        for cid in SWEEP_IDS
        if engagement_level_from_propensity(engagement_propensity_for_customer(cid))
        is not engagement_level_for_customer(cid)
    ]
    assert mismatches == [], f"{len(mismatches)} ids broke the identity, e.g. {mismatches[:5]}"


def test_propensity_is_in_range_and_projectable_for_every_id():
    """Every propensity is a finite float in [0, 1) -- i.e. an input the
    projection accepts. Guards the float-cumulative-walk defect specifically:
    0.20 + 0.35 + 0.45 == 1.0000000000000002, so an unclamped top bin would
    emit >= 1.0 for the most engaged households.
    """
    for cid in SWEEP_IDS:
        p = engagement_propensity_for_customer(cid)
        assert isinstance(p, float) and math.isfinite(p), (cid, p)
        assert 0.0 <= p < 1.0, (cid, p)


def test_top_bin_closes_at_exactly_one():
    assert engagement_propensity_bounds(EngagementLevel.ACTIVE)[1] == 1.0


def test_propensity_is_stable_across_calls():
    """A trait for the whole tenure, not a per-call draw (movability is NOT
    built -- DISCOVER §5)."""
    for cid in ["C1", "C9", "SYN-000123", "resi-777"]:
        values = {engagement_propensity_for_customer(cid) for _ in range(5)}
        assert len(values) == 1, (cid, values)


# ---------------------------------------------------------------------------
# 2. Nothing existing moved (the atom's zero-risk claim)
# ---------------------------------------------------------------------------
# Captured from the working tree BEFORE the W2_14 edit. If the new substream had
# perturbed the `engagement_{cid}` sequence, or the projection had replaced the
# coarse draw rather than refining it, these change.
GOLDEN_LEVELS = {
    "C1": "passive",
    "C9": "active",
    "C42": "disengaged",
    "CUST-0001": "active",
    "SYN-000123": "active",
    "resi-777": "disengaged",
    "x": "disengaged",
}


def test_existing_coarse_draw_is_byte_for_byte_unchanged():
    assert {cid: engagement_level_for_customer(cid).value for cid in GOLDEN_LEVELS} == GOLDEN_LEVELS


def test_new_draw_cannot_shift_the_existing_stream_whatever_the_call_order():
    """C-S2 named-substream discipline: interleaving the new propensity draw
    with the existing per-customer draws must not change any of them, in any
    order (the failure mode a shared sequential RNG would have)."""
    ids = [f"C{i}" for i in range(200)]
    baseline = {
        cid: (
            engagement_level_for_customer(cid).value,
            hs.active_renewal_probability_for_customer(cid),
            hs.payment_channel_for_customer(cid).value,
            hs.tenure_for_customer(cid).value,
            hs.occupancy_for_customer(cid).value,
        )
        for cid in ids
    }
    for cid in reversed(ids):  # interleave the new draw, reversed order
        engagement_propensity_for_customer(cid)
    after = {
        cid: (
            engagement_level_for_customer(cid).value,
            hs.active_renewal_probability_for_customer(cid),
            hs.payment_channel_for_customer(cid).value,
            hs.tenure_for_customer(cid).value,
            hs.occupancy_for_customer(cid).value,
        )
        for cid in ids
    }
    assert after == baseline


# ---------------------------------------------------------------------------
# 3. Fail-open guards on the projection (R15 killer pattern: FAIL-OPEN)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
def test_projection_rejects_non_finite_rather_than_defaulting(bad):
    """A NaN compares False against every boundary, so a fallback `return
    DISENGAGED` would classify a corrupt input as a real archetype. An unusable
    input must be an ERROR."""
    with pytest.raises(ValueError):
        engagement_level_from_propensity(bad)


@pytest.mark.parametrize("bad", [-0.001, 1.0, 1.5, -1.0])
def test_projection_rejects_out_of_range(bad):
    with pytest.raises(ValueError):
        engagement_level_from_propensity(bad)


@pytest.mark.parametrize("bad", [None, "0.5", True, [0.5]])
def test_projection_rejects_non_numeric(bad):
    with pytest.raises((TypeError, ValueError)):
        engagement_level_from_propensity(bad)


def test_projection_accepts_both_bin_edges_and_an_int():
    assert engagement_level_from_propensity(0.0) is EngagementLevel.DISENGAGED
    assert engagement_level_from_propensity(0) is EngagementLevel.DISENGAGED
    assert engagement_level_from_propensity(0.999999) is EngagementLevel.ACTIVE


# ---------------------------------------------------------------------------
# 4. The boundaries are DERIVED from the ratified shares (R13: one copy only)
# ---------------------------------------------------------------------------
def test_bounds_partition_the_unit_interval_in_ascending_engagement_order():
    lo_d, hi_d = engagement_propensity_bounds(EngagementLevel.DISENGAGED)
    lo_p, hi_p = engagement_propensity_bounds(EngagementLevel.PASSIVE)
    lo_a, hi_a = engagement_propensity_bounds(EngagementLevel.ACTIVE)
    assert lo_d == 0.0 and hi_a == 1.0
    assert hi_d == lo_p and hi_p == lo_a
    assert hi_d == pytest.approx(ENGAGEMENT_POPULATION_SHARE[EngagementLevel.DISENGAGED])
    assert (hi_p - lo_p) == pytest.approx(ENGAGEMENT_POPULATION_SHARE[EngagementLevel.PASSIVE])
    assert (hi_a - lo_a) == pytest.approx(ENGAGEMENT_POPULATION_SHARE[EngagementLevel.ACTIVE])


def test_bin_width_equals_the_ratified_share_so_the_latent_is_uniform():
    """The stated R10 assumption made checkable: within-bin uniform + bin width
    == ratified share means the population latent is uniform[0,1). If either
    leg broke, this decile histogram would skew."""
    values = [engagement_propensity_for_customer(f"C{i}") for i in range(20000)]
    deciles = Counter(min(int(v * 10), 9) for v in values)
    for d in range(10):
        assert 0.085 <= deciles[d] / len(values) <= 0.115, (d, deciles[d] / len(values))


def test_bucketed_population_reproduces_the_ratified_shares():
    """The weaker population-level check the identity supersedes -- kept because
    it is the one that would catch a *sampling* regression the identity cannot
    (the identity would still hold if the coarse draw itself drifted)."""
    counts = Counter(
        engagement_level_from_propensity(engagement_propensity_for_customer(f"C{i}")).value
        for i in range(20000)
    )
    for level, share in ENGAGEMENT_POPULATION_SHARE.items():
        assert abs(counts[level.value] / 20000 - share) < 0.015, (level, counts)


# ---------------------------------------------------------------------------
# 5. R15 MUTATION TESTS -- the controls above proven to FIRE, then to CLEAR
# ---------------------------------------------------------------------------
def test_R15_mutating_the_ratified_shares_moves_the_boundaries(monkeypatch):
    """Named defect: a second copy of 0.45/0.35/0.20 that could drift away from
    the director's ratified value. Proof there is only ONE copy -- move it and
    the boundaries follow."""
    before = engagement_propensity_bounds(EngagementLevel.DISENGAGED)
    monkeypatch.setitem(hs.ENGAGEMENT_POPULATION_SHARE, EngagementLevel.DISENGAGED, 0.50)
    monkeypatch.setitem(hs.ENGAGEMENT_POPULATION_SHARE, EngagementLevel.PASSIVE, 0.30)
    monkeypatch.setitem(hs.ENGAGEMENT_POPULATION_SHARE, EngagementLevel.ACTIVE, 0.20)
    after = engagement_propensity_bounds(EngagementLevel.DISENGAGED)
    assert before != after
    assert after == (0.0, 0.50)
    assert engagement_level_from_propensity(0.40) is EngagementLevel.DISENGAGED  # was PASSIVE


def test_R15_ordering_control_FIRES_when_engagement_order_is_reversed(monkeypatch):
    """Named defect: the walk ordered the bins the other way, so a HIGHER
    propensity would mean a LESS engaged household -- the whole variable read
    backwards, while every published share still reconciles.

    Recorded finding (2026-07-29, this suite): the refinement IDENTITY cannot
    catch this. Both the latent and the projection derive their bounds from the
    same `_ENGAGEMENT_ASCENDING`, so a *consistent* re-ordering keeps the
    round-trip exact -- it is a valid partition, just with inverted semantics.
    An identity is the wrong instrument for a direction defect. Asserted here
    explicitly (the identity holds under the mutation) so nobody later mistakes
    the identity for a semantic guarantee, and the SEMANTIC control -- the
    partition test's `lo_d == 0.0` / ascending-bounds assertions -- is the one
    proven to fire.
    """
    monkeypatch.setattr(
        hs,
        "_ENGAGEMENT_ASCENDING",
        (EngagementLevel.ACTIVE, EngagementLevel.PASSIVE, EngagementLevel.DISENGAGED),
    )
    # 1. the identity is INSENSITIVE to this mutation (the point of the note)
    assert all(
        hs.engagement_level_from_propensity(hs.engagement_propensity_for_customer(cid))
        is hs.engagement_level_for_customer(cid)
        for cid in SWEEP_IDS[:500]
    )
    # 2. the semantic control DOES fire: DISENGAGED no longer sits at the bottom
    #    and ACTIVE no longer at the top of the propensity axis.
    lo_d, _ = hs.engagement_propensity_bounds(EngagementLevel.DISENGAGED)
    _, hi_a = hs.engagement_propensity_bounds(EngagementLevel.ACTIVE)
    assert lo_d != 0.0 and hi_a != 1.0, (
        "the ascending-order control cannot fail -- it is not a control"
    )


def test_R15_identity_check_FIRES_when_the_latent_is_an_independent_draw(monkeypatch):
    """Named defect -- THE defect this atom's design exists to prevent: drawing
    a second, independent latent instead of refining the coarse draw. The
    population shares would still look right; the per-customer identity breaks.
    """
    monkeypatch.setattr(
        hs,
        "engagement_propensity_for_customer",
        lambda cid: hs._engagement_propensity_substream(cid).random(),
    )
    ids = SWEEP_IDS[:1000]
    mismatches = [
        cid
        for cid in ids
        if hs.engagement_level_from_propensity(hs.engagement_propensity_for_customer(cid))
        is not hs.engagement_level_for_customer(cid)
    ]
    assert len(mismatches) > 100, (
        "an independent draw must break the identity for a large fraction of "
        f"customers; only {len(mismatches)}/{len(ids)} broke"
    )
    # ...and the population-share check does NOT catch it -- which is exactly
    # why the identity is the control and the tolerance test is the supplement.
    counts = Counter(
        hs.engagement_level_from_propensity(hs.engagement_propensity_for_customer(f"C{i}")).value
        for i in range(20000)
    )
    for level, share in ENGAGEMENT_POPULATION_SHARE.items():
        assert abs(counts[level.value] / 20000 - share) < 0.015


def test_R15_the_identity_control_CLEARS_on_the_real_implementation():
    """The other direction: with nothing mutated, the control passes -- so the
    two FIRE tests above are not passing on an always-broken checker."""
    assert all(
        engagement_level_from_propensity(engagement_propensity_for_customer(cid))
        is engagement_level_for_customer(cid)
        for cid in SWEEP_IDS[:500]
    )
