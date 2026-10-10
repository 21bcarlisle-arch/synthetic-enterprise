"""A home-move successor's per-account decision row names the predecessor whose churn activated it.

On seed 44444 the value arm's price churned C5, the home-move win activated C5_2 in that arm only,
and the account-keyed partition split one decision: C5 -1,375.96 in D, C5_2 +1,345.47 roster-only
(`SEAT_FINDING_THE_ROSTER_ONLY_1345_ON_SEED_44444_IS_C5S_HOME_MOVE_SUCCESSOR_AND_A_DECISION_NOT_A_
HARNESS_LEAK_2026-09-29.md`). The lineage could only be recovered by joining dates across blocks.
"""

from __future__ import annotations

from tools.run_value_cycle_ab import (
    _decisions_by_billing_account,
    fold_by_successor,
    home_move_successor_of,
)


def test_the_lineage_reads_the_registered_successors():
    """The lineage the fold reads is the registered successor roster. Until 2026-10-10 this was keyed
    to `run_phase2b.SUCCESSOR_MAP`, the map the renewal-churn "home-move win" activated; that roll
    is retired (a switcher vacates no property) and the map with it, so the fold now only reads
    captures made before then, and the roster is its one source."""
    lineage = home_move_successor_of()
    assert lineage["C5_2"] == "C5"


def test_a_successor_row_names_its_predecessor_and_an_ordinary_row_names_none():
    """Both legs of the field in one partition: an assertion on only the None leg passes a field
    that is never filled, and the value leg is the rare one."""
    result = {"phase2b": {"customer_events": [
        {"customer_id": "C5", "event_date": "2016-12-31", "event_type": "churned",
         "effective_retention_probability": 0.2135, "random_roll": 0.2812},
        {"customer_id": "C5_2", "event_date": "2017-12-31", "event_type": "renewed",
         "effective_retention_probability": 0.7, "random_roll": 0.4},
    ]}, "bills": []}
    decisions = _decisions_by_billing_account(result)
    assert decisions["C5_2"]["successor_of"] == "C5"
    assert decisions["C5"]["successor_of"] is None


def test_the_fold_turns_seed_44444s_d_ex_0098_positive_and_folds_only_a_members_roster_only_successor():
    """The finding's own figures: -559.81 as pre-registered, +785.66 with C5_2 folded into C5.
    C3_2 renewed in both arms, so its money stays where its own renewals put it; C6_2 is
    roster-only but its predecessor is not in the partition."""
    lineage = {"C5_2": "C5", "C6_2": "C6", "C3_2": "C3"}
    diff = {"C5": -1375.96, "C3": 0.0, "OTHER": 816.15, "C5_2": 1345.47, "C6_2": 999.0,
            "C3_2": -1.01}
    members = ["C5", "C3", "OTHER"]
    assert round(fold_by_successor(diff, members, {}, ["C5_2", "C6_2"]), 2) == -559.81
    assert round(fold_by_successor(diff, members, lineage, ["C5_2", "C6_2"]), 2) == 785.66
    # A successor already in the partition is not counted twice.
    assert round(fold_by_successor(diff, members + ["C5_2"], lineage, ["C5_2"]), 2) == 785.66
