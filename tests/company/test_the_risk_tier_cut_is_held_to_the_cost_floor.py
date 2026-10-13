"""B8: the churn-belief tier cut is taken no deeper than the re-fix's own cost floor.

The tier cut (3-8%) was applied in the run loop after the rate chain's own floor check had
returned, so it alone could sell under cost: the only two held renewals below floor on seed 61109
were both tier cuts (95b3a38d2). The defects each test names: a tier cut taken below the floor; a
cut given with no floor to check it against; the run loop sizing the tier cut without the floored
function, or applying an offer the class rule never asks.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

from company.compliance.domain_invariants import DiscretionaryRateBelowOwnCostFloorError
from company.interfaces.growth_desk import (
    refuse_retention_offer_below_own_cost_floor,
    retention_cut_share_at_risk_tiers,
)

_RUN_LOOP = Path(__file__).resolve().parents[2] / "simulation" / "run_phase2b.py"


def test_every_branch_of_the_floored_tier_cut_can_be_taken():
    """Control over the partition: the whole tier given, a cut stopped at the floor, and none."""
    whole = retention_cut_share_at_risk_tiers(120.0, 0.05, cost_floor=100.0)
    floored = retention_cut_share_at_risk_tiers(120.0, 0.08, cost_floor=115.0)
    none = retention_cut_share_at_risk_tiers(115.0, 0.03, cost_floor=115.0)
    assert whole is not None and floored is not None and none is None
    # Exactly the tier, not a float round-trip of it: the run log grades the cut against its tier.
    assert whole == 0.05 and floored < 0.08


@pytest.mark.parametrize("refix, tier, floor", [
    # The two rows 95b3a38d2 found below floor on seed 61109, at their own inputs.
    (68.73, 0.08, 68.34),
    (64.06, 0.03, 63.61),
])
def test_the_rows_found_below_floor_now_land_on_it(refix, tier, floor):
    """Defect: a tier cut taken below the floor. Unfloored, these offered 63.23 and 62.14."""
    share = retention_cut_share_at_risk_tiers(refix, tier, cost_floor=floor)
    assert refix * (1.0 - tier) < floor
    assert refix * (1.0 - share) == pytest.approx(floor)
    refuse_retention_offer_below_own_cost_floor(
        refix * (1.0 - share), entered=refix, cost_floor=floor, where="t")


def test_no_tier_cut_without_a_floor_to_check_it_against():
    """Defect: a discount nobody can show is above cost. The chain's writer 1 gives none either."""
    assert retention_cut_share_at_risk_tiers(120.0, 0.05, cost_floor=None) is None
    assert retention_cut_share_at_risk_tiers(None, 0.05, cost_floor=100.0) is None


def test_no_tier_cut_on_a_refix_already_under_its_floor():
    assert retention_cut_share_at_risk_tiers(110.0, 0.05, cost_floor=112.0) is None


def test_the_refusal_names_an_offer_under_the_floor():
    with pytest.raises(DiscretionaryRateBelowOwnCostFloorError, match="retention offer SYN-1"):
        refuse_retention_offer_below_own_cost_floor(
            63.23, entered=68.73, cost_floor=68.34, where="SYN-1 electricity 2017-01-01")


def test_the_refusal_allows_an_offer_at_the_floor_and_cuts_nothing_under_an_entered_low_rate():
    refuse_retention_offer_below_own_cost_floor(68.34, entered=68.73, cost_floor=68.34, where="t")
    with pytest.raises(DiscretionaryRateBelowOwnCostFloorError):
        refuse_retention_offer_below_own_cost_floor(
            104.5, entered=110.0, cost_floor=112.0, where="t")


def _called_names(source: str) -> set[str]:
    return {node.func.id for node in ast.walk(ast.parse(source))
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)}


def test_the_run_loop_sizes_the_tier_cut_floored_and_refuses_the_offer_it_applies():
    """Defect: the run loop sizing by the bare tier, or applying an offer the rule never asks.
    Read as CALLS, so a comment naming either function cannot satisfy it."""
    called = _called_names(_RUN_LOOP.read_text())
    assert "retention_cut_share_at_risk_tiers" in called
    assert "refuse_retention_offer_below_own_cost_floor" in called
