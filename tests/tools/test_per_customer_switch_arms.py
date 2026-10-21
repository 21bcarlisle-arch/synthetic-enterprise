"""The per-customer arms differ from CURRENT_POLICY in exactly their own fields, and each is reached.

Defect named: an all-on arm that leaves one of its three switches off (or a flat arm that is not
FLAT_SUPPLIER_POLICY) still runs and writes a run output that reads as the comparison asked for;
and an arm handed to `main` but not bound to `run_phase2b.CURRENT_POLICY` is two variables.
"""
from __future__ import annotations

import dataclasses

import pytest

import simulation.run_phase2b as rp2b
import simulation.run_phase4c_on_phase2b as p4c
import tools.per_customer_switch_arms as arms
from company.policy.decision_policy import CURRENT_POLICY, FLAT_SUPPLIER_POLICY


def _differing(a, b):
    return {f.name for f in dataclasses.fields(a) if getattr(a, f.name) != getattr(b, f.name)}


def test_each_arm_differs_from_current_in_exactly_its_own_fields():
    assert _differing(arms.arm_policy("current"), CURRENT_POLICY) == set()
    # Named here, not read from the module, so a switch dropped from the arm turns this red.
    assert _differing(arms.arm_policy("all_on"), CURRENT_POLICY) == {
        "name", "next_best_action_decides_at_renewal", "next_best_action_shares_by_retention_rise",
        "save_offer_decides_per_household"}
    assert arms.arm_policy("flat") == FLAT_SUPPLIER_POLICY
    assert _differing(arms.arm_policy("flat"), CURRENT_POLICY)  # flat is not the control


@pytest.fixture
def seen(monkeypatch, tmp_path):
    calls = []

    def fake_main(policy=None, instructed_read_arm="register", report_end=None):
        calls.append((policy.name, rp2b.CURRENT_POLICY.name))
        return {"phase2b": {"next_best_action_renewal_log": [policy.name]}}

    monkeypatch.setattr(p4c, "main", fake_main)
    monkeypatch.setattr("tools.run_annual_report.extract_report_data", lambda raw: {})
    monkeypatch.setattr("tools.run_annual_report.reconcile_and_stamp", lambda data, **_: data)
    monkeypatch.setattr("tools.run_annual_report.dump_run_output", lambda data: repr(data))
    monkeypatch.setattr(rp2b, "CURRENT_POLICY", rp2b.CURRENT_POLICY)  # restored after the test
    return calls, tmp_path


def test_every_arm_is_reachable_bound_where_policy_less_callers_see_it_and_keeps_the_desk_log(seen):
    calls, tmp_path = seen
    for arm in arms.ARMS:
        out = arms.run_arm(arm, tmp_path / f"{arm}.json")
        assert "next_best_action_renewal_log" in out.read_text()
    names = [arms.arm_policy(a).name for a in arms.ARMS]
    assert calls == [(n, n) for n in names]
    assert len(set(names)) == 3


def test_an_unknown_arm_is_refused_by_name(seen):
    _, tmp_path = seen
    with pytest.raises(SystemExit, match="not one of"):
        arms.run_arm("half", tmp_path / "x.json")
