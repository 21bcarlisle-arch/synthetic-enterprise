"""A production run reaches the contact response on default-tariff stock, and only through the seam (W2_39 L2).

Two runs of the 2016-01 .. 2017-02 window, identical but for `svt_contact_instrument` on the
company's policy. The one with no contact must roll every SVT segment exactly as before; the one with
a contact must reach `svt_departure_after_contact` on every segment, keep each household's
uncontacted outcome on the same draw, and only ever add departures.
"""
from __future__ import annotations

from dataclasses import replace

import pytest

from company.policy.decision_policy import CURRENT_POLICY, policy_scope

_END = "2017-02-28"
_INSTRUMENT = "collective_switch"


def _run(policy, tmp_path_factory):
    from simulation.run_phase2b import main

    with policy_scope(policy):
        return main(report_end=_END, policy=policy,
                    gap_ledger_path=tmp_path_factory.mktemp("gap") / "coupled_gap_ledger.json")


@pytest.fixture(scope="module")
def _arms(tmp_path_factory):
    contacted = replace(CURRENT_POLICY, name="svt_contact_test", svt_contact_instrument=_INSTRUMENT)
    return {
        "none": _run(CURRENT_POLICY, tmp_path_factory)["svt_decisions"],
        "contact": _run(contacted, tmp_path_factory)["svt_decisions"],
    }


def _key(row):
    return row["customer_id"], row["event_date"]


def test_with_no_contact_every_svt_roll_is_the_one_it_always_was(_arms):
    """DEFECT: wiring the response moves an uncontacted household -- a probability, a cause, or a
    draw changes when nothing was sent."""
    rows = _arms["none"]
    assert rows, "the window must hold SVT segments or this control is vacuous"
    for r in rows:
        assert r["contact_instrument"] is None
        assert r["realized_churn_probability"] == r["sim_p_depart_uncontacted"]
        assert r["departure_cause"] == ("svt_inertia" if r["event_type"] == "churned" else None)


def test_a_sent_contact_reaches_every_segment_and_keeps_its_uncontacted_outcome(_arms):
    """DEFECT: the send never reaches the roll, the contacted roll draws afresh so the pair is no
    counterfactual, or a contact lowers departure on this segment.

    MUTATION: deleting the `send_contact` call in the run loop empties `contacted` (first assert);
    seeding the contacted roll differently breaks the paired roll equality.
    """
    none = {_key(r): r for r in _arms["none"]}
    contacted = [r for r in _arms["contact"] if r["contact_instrument"] == _INSTRUMENT]
    assert contacted and len(contacted) == len(_arms["contact"])
    # A household the contact sent away has no later segments, so pair on what both arms rolled.
    paired = [(r, none[_key(r)]) for r in contacted if _key(r) in none]
    assert paired
    lifted = 0
    for r, base in paired:
        assert r["random_roll"] == base["random_roll"]
        assert r["sim_p_depart_uncontacted"] == base["realized_churn_probability"]
        assert r["realized_churn_probability"] >= r["sim_p_depart_uncontacted"]
        if base["event_type"] == "churned":
            assert r["event_type"] == "churned" and r["departure_cause"] == "svt_inertia"
        lifted += r["realized_churn_probability"] > r["sim_p_depart_uncontacted"]
    assert lifted, "a contact that woke nobody on any segment means the response was not reached"
