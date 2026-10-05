"""Estimated reads make billed differ from used, and an actual read trues it up (W2_36, first slice).

The persistences passed below are TEST FIXTURES, chosen only to exercise the chain. The real value
is not established (`MONTHLY_ESTIMATE_PERSISTENCE` is None), which is what the first test holds.
"""
from __future__ import annotations

import random

import pytest

from simulation.unbilled_energy import (
    ANNUAL_NO_READ_BILL_SHARE,
    ESTIMATED,
    MONTHLY_ESTIMATE_PERSISTENCE,
    HouseholdReadState,
    UnsizedReadChain,
    entry_hazard,
    simulate,
    step,
)

# A GB-shaped seasonal year of household use, kWh/month, high in winter.
SEASONAL_YEAR = [400, 380, 330, 260, 200, 170, 160, 170, 210, 280, 350, 400]


def test_the_sourced_leg_refuses_while_persistence_is_not_established():
    """Defect caught: a placeholder persistence quietly sizing the chain as if it were sourced."""
    assert MONTHLY_ESTIMATE_PERSISTENCE is None
    with pytest.raises(UnsizedReadChain, match="practitioner"):
        simulate(SEASONAL_YEAR, random.Random(0))


def test_used_minus_billed_is_nonzero_while_estimated_and_closes_on_the_true_up():
    """Defect caught: billing on estimate that still tracks use, or a true-up that leaves a gap."""
    h = HouseholdReadState(estimate_kwh=170.0)
    rows = [step(h, used, read_actual=False) for used in (210, 280, 350)]
    assert all(r["branch"] == ESTIMATED for r in rows)
    assert [r["unbilled_kwh"] for r in rows] == [40.0, 150.0, 330.0]
    true_up = step(h, 400, read_actual=True)
    assert true_up["branch"] == "true_up"
    assert true_up["unbilled_kwh"] == 0.0
    # The catch-up bills everything used in the spell that the estimates missed, plus this month.
    assert true_up["billed_kwh"] == 330.0 + 400.0


def test_a_true_up_after_an_over_estimate_is_a_credit():
    """Defect caught: a true-up that can only ever charge more (summer use against a winter estimate)."""
    h = HouseholdReadState(estimate_kwh=400.0)
    step(h, 170, read_actual=False)
    assert step(h, 160, read_actual=True)["billed_kwh"] == 160.0 - 230.0


def test_every_branch_of_the_chain_is_reachable_including_the_rare_true_up():
    """Defect caught: a chain that never leaves (or never returns to) an actual read, which would
    pass every test of what a true-up does while no true-up ever happens."""
    branches = set()
    for seed in range(50):
        h = simulate(SEASONAL_YEAR * 3, random.Random(seed), persistence=0.9)
        branches |= {r["branch"] for r in h.history}
        assert h.unbilled_kwh == sum(r["used_kwh"] - r["billed_kwh"] for r in h.history)
    assert branches == {"actual", ESTIMATED, "true_up"}


def test_the_chain_reproduces_the_published_share_unread_for_a_year():
    """Defect caught: an entry hazard derived wrongly, so the sized chain misses the Ofgem figure."""
    p = 0.9
    q = entry_hazard(p)
    pi_e = q / (q + 1 - p)
    rng = random.Random(7)
    n, unread = 20_000, 0
    for _ in range(n):
        estimated = rng.random() < pi_e
        run = []
        for _ in range(12):
            estimated = rng.random() < (p if estimated else q)
            run.append(estimated)
        unread += all(run)
    assert abs(unread / n - ANNUAL_NO_READ_BILL_SHARE) < 0.006


def test_a_persistence_too_low_for_the_published_share_is_refused_with_its_reason():
    """Defect caught: an entry 'probability' above 1 (a first draft returned 5.1 at p = 0.77)."""
    with pytest.raises(UnsizedReadChain, match="too low for the published share"):
        entry_hazard(0.77)
    assert 0.0 < entry_hazard(0.79) <= 1.0
