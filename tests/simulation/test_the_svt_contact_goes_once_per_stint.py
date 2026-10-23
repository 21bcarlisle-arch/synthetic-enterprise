"""C30: the per-account SVT sender writes once per default-tariff stint, at its first segment.

The rule is the company's (`contact_programme.sends_at_segment`), read off its own record of when
the account rolled onto its default. One short real run of 2016-01 .. 2017-02 checks that the run
loop asks it; the partition is checked on the function, where every leg is one call.
"""
from __future__ import annotations

from dataclasses import replace

import pytest

from company.interfaces.contact_programme import sends_at_segment
from company.policy.decision_policy import CURRENT_POLICY, policy_scope


def test_the_rule_sends_at_a_stints_first_segment_and_nowhere_else_and_flat_sends_everywhere():
    """DEFECT: the once-per-stint rule sends nowhere (every reach test of it passes on a sender
    that never fires) or everywhere (it is the flat rule under a new name). MUTATION: returning
    False reds the first leg; dropping `segment_start == stint_start` reds the second."""
    assert sends_at_segment("2016-04-01", "2016-04-01", True)
    assert not sends_at_segment("2016-10-01", "2016-04-01", True)
    assert sends_at_segment("2016-10-01", "2016-04-01", False)


@pytest.fixture(scope="module")
def _rows(tmp_path_factory):
    from simulation.run_phase2b import main
    policy = replace(CURRENT_POLICY, name="svt_once_per_stint_test",
                     svt_contact_instrument="cmoc_letter", svt_contact_once_per_stint=True)
    with policy_scope(policy):
        return main(report_end="2017-02-28", policy=policy,
                    gap_ledger_path=tmp_path_factory.mktemp("gap") / "coupled_gap_ledger.json",
                    )["svt_decisions"]


def test_the_run_sends_at_first_segments_only(_rows):
    """DEFECT: the run loop ignores the policy and keeps sending at every segment, or sends at
    none. MUTATION: dropping the `sends_at_segment(...)` clause from the send's guard puts a
    contact on a later segment; passing `True` for the stint start's comparison sends nowhere."""
    firsts = [r for r in _rows if r["sim_years_on_svt"] == 0.0]
    later = [r for r in _rows if r["sim_years_on_svt"] > 0.0]
    assert firsts and later, "the window holds no stint with more than one segment to tell apart"
    assert all(r["contact_instrument"] == "cmoc_letter" for r in firsts)
    # A missed-payment contact reaches the same store, so only the letter itself is asked after.
    assert not any(r["contact_instrument"] == "cmoc_letter" for r in later)
