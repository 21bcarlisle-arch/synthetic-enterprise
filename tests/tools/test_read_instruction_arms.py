"""The read-instruction arms turn the switch on where the policy-less bill rebuilds can see it.

Defect named: an arm that hands `main` an experiment policy but leaves `run_phase2b.CURRENT_POLICY`
alone bills the published bills with the instruction and the DD review / stop-notice rebuilds
without it (`run_phase4c_on_phase2b.read_instruction_request(None)`), so the arm is two variables.
"""
from __future__ import annotations

import pytest

import simulation.run_phase2b as rp2b
import simulation.run_phase4c_on_phase2b as p4c
import tools.read_instruction_arms as arms


@pytest.fixture
def seen(monkeypatch, tmp_path):
    calls = []

    def fake_main(policy=None, instructed_read_arm="register", report_end=None):
        # What the in-loop callers ask, with no policy in hand.
        calls.append((p4c.read_instruction_request(None), instructed_read_arm))
        return {}

    monkeypatch.setattr(p4c, "main", fake_main)
    monkeypatch.setattr("tools.run_annual_report.extract_report_data", lambda raw: {})
    monkeypatch.setattr("tools.run_annual_report.reconcile_and_stamp", lambda data, **_: data)
    monkeypatch.setattr(rp2b, "CURRENT_POLICY", rp2b.CURRENT_POLICY)  # restored after the test
    return calls, tmp_path


def test_every_arm_is_reachable_and_each_reaches_the_policy_less_callers(seen):
    calls, tmp_path = seen
    for arm in arms.ARMS:
        arms.run_arm(arm, tmp_path / f"{arm}.json")
    assert calls == [(False, "register"), (True, "register"), (True, "ceiling")]


def test_an_unknown_arm_is_refused_by_name(seen):
    _, tmp_path = seen
    with pytest.raises(SystemExit, match="not one of"):
        arms.run_arm("half", tmp_path / "x.json")
