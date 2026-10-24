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


@pytest.mark.parametrize("asked, ran", [(None, True), (True, True), (False, False)])
def test_the_payload_stamps_the_estimate_the_arm_ran_not_the_flag(seen, asked, ran):
    """Defect: with the annualised advance on by default (23 Oct), an arm run without the flag ran
    it ON and stamped it OFF from the flag, so a control arm read as the three-read estimate.

    MUTATION (must fire): stamp `annualised_advance` (the flag) instead of the policy's field (the
    `None` row reds), or ignore `False` (the off row reds)."""
    import json
    _, tmp_path = seen
    out = arms.run_arm("register", tmp_path / "a.json", annualised_advance=asked)
    assert json.loads(out.read_text())["_bill_estimate_reads_the_annualised_advance"] is ran



def test_the_gas_floor_reaches_the_policy_less_callers_and_is_refused_with_the_advance_off(
        monkeypatch, tmp_path):
    """Defect named: the floor arm flooring the published bills but not the DD review's rebuild,
    and a floor asked for with the advance off, which would run the control under a floor's name.
    The standing policy has the advance on, so the floor needs no `--annualised-advance`."""
    import json
    seen_flags = []
    monkeypatch.setattr(p4c, "main", lambda policy=None, instructed_read_arm="register",
                        report_end=None: seen_flags.append(p4c.gas_advance_floor_request(None))
                        or {})
    monkeypatch.setattr("tools.run_annual_report.extract_report_data", lambda raw: {})
    monkeypatch.setattr("tools.run_annual_report.reconcile_and_stamp", lambda data, **_: data)
    monkeypatch.setattr(rp2b, "CURRENT_POLICY", rp2b.CURRENT_POLICY)
    arms.run_arm("register", tmp_path / "a.json")
    monkeypatch.setattr(rp2b, "CURRENT_POLICY", rp2b.CURRENT_POLICY)
    out = arms.run_arm("register", tmp_path / "b.json", gas_nine_month_floor=True)
    assert seen_flags == [False, True]
    assert json.loads(out.read_text())["_bill_estimate_floors_the_gas_advance_at_nine_months"] is True
    monkeypatch.setattr(rp2b, "CURRENT_POLICY", rp2b.CURRENT_POLICY)
    with pytest.raises(SystemExit, match="has the advance off"):
        arms.run_arm("register", tmp_path / "c.json", annualised_advance=False,
                     gas_nine_month_floor=True)
