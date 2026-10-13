"""A leg that moves with us settles on its new home's trace under its new home's verdict: the rule.

Defect this names: on fresh seeds 61110-61112 a follower moving from a legacy home into a fabric
one settled on the destination's fabric trace while still carrying the old home's "not eligible"
verdict, and W1_11's settlement-switch guard stopped four mover arms (fixed in e71d5c1db).
Reverting that fix left the nearest test selection green (32 passed); only a 5-12 minute
fresh-seed run saw it. This file holds the rule; `test_run_phase2b_mover_verdict.py` holds the
relocation block to it. Each is named for the module it guards, so the commit that changes that
module selects it.
"""
from __future__ import annotations

from simulation.fabric_demand_path import (
    FABRIC_PROVIDER,
    LEGACY_PROVIDER,
    FabricEligibility,
    rebind_fabric_verdict_to_new_home,
    settlement_providers_match_eligibility,
)


def _settle(series_by_customer, customer_ids):
    """The provider choice run_phase2b makes for a non-HH leg: fabric iff it holds a trace."""
    return {c: FABRIC_PROVIDER if c in series_by_customer else LEGACY_PROVIDER
            for c in customer_ids}


def _move(destination_series, *, from_fabric: bool):
    trace = object()
    series = {"NEIGHBOUR": trace}
    verdicts = [FabricEligibility("NEIGHBOUR", True, "fabric"),
                FabricEligibility("MOVER", from_fabric, "old home")]
    if from_fabric:
        series["MOVER"] = trace
    rebind_fabric_verdict_to_new_home("MOVER", destination_series,
                                      series_by_customer=series, verdicts=verdicts)
    return series, verdicts


def test_both_directions_of_a_move_across_the_line_settle_under_a_matching_verdict():
    destination = object()
    into_fabric = _move(destination, from_fabric=False)
    into_legacy = _move(None, from_fabric=True)
    # Both branches are taken, and each leaves the settled book judged clean by the guard.
    assert into_fabric[0]["MOVER"] is destination and "MOVER" not in into_legacy[0]
    for series, verdicts in (into_fabric, into_legacy):
        settled = _settle(series, ["NEIGHBOUR", "MOVER"])
        assert settlement_providers_match_eligibility(settled, verdicts)
        assert [v.customer_id for v in verdicts].count("MOVER") == 1
        assert {v.customer_id: v.is_eligible for v in verdicts}["NEIGHBOUR"] is True


def test_the_guard_refuses_the_book_the_old_inline_copy_left():
    # The pre-fix shape: the trace moved, the verdict did not. If this stopped reding, the leg above
    # would prove nothing about the defect.
    series = {"MOVER": object()}
    verdicts = [FabricEligibility("MOVER", False, "old home")]
    assert not settlement_providers_match_eligibility(_settle(series, ["MOVER"]), verdicts)
