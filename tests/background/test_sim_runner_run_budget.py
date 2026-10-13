"""The run's timeout is derived from the last successful run, not a constant the run can grow into.

The defect this names: a fixed `timeout=7200` killed the 2026-10-13 11:24Z run about 7300s in,
after its simulation had finished and while it was writing the report. The run had grown from
4273s (2026-10-11) to 5119s (2026-10-12), and the state file overwrote the last good duration on
every failure.
"""

import json
import subprocess
from unittest.mock import MagicMock

from background import sim_runner


def _isolate(tmp_path, monkeypatch):
    monkeypatch.setattr(sim_runner, "PROJECT_DIR", tmp_path)
    monkeypatch.setattr(sim_runner, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(sim_runner, "STAGING_DIR", tmp_path / "staging")
    monkeypatch.setattr(sim_runner, "REPORTS_DIR", tmp_path / "reports")
    monkeypatch.setattr(sim_runner, "PRODUCER_STATE_FILE", tmp_path / "producer.json")
    monkeypatch.setattr(sim_runner, "notify", lambda *a, **k: None)
    monkeypatch.setattr(sim_runner, "update_agent_status", lambda *a, **k: None)
    monkeypatch.setattr(sim_runner, "_git_head", lambda: "abc1234")
    return tmp_path / "producer.json"


def test_a_run_slower_than_the_old_bound_is_not_killed_once_its_predecessor_succeeded(tmp_path):
    state = tmp_path / "producer.json"
    sim_runner.record_run_outcome(True, head="47e8e6993", elapsed=5119, state_path=state)
    # The 2026-10-13 run needed about 7300s. Under the fixed bound it was killed.
    assert sim_runner.run_budget_seconds(state) > 7300
    # A hang is still a hang: the bound is finite and scales with what the run last needed.
    assert sim_runner.run_budget_seconds(state) == 2 * 5119


def test_failures_carry_the_last_success_forward_and_cannot_escalate_the_bound(tmp_path):
    state = tmp_path / "producer.json"
    sim_runner.record_run_outcome(True, head="a", elapsed=5119, state_path=state)
    before = sim_runner.run_budget_seconds(state)
    for _ in range(3):
        sim_runner.record_run_outcome(False, detail="timeout", head="b",
                                      elapsed=sim_runner.run_budget_seconds(state), state_path=state)
    assert json.loads(state.read_text())["last_success_elapsed_s"] == 5119
    assert sim_runner.run_budget_seconds(state) == before


def test_the_bound_is_never_tighter_than_the_legacy_bound_and_unreadable_state_is_loose(tmp_path):
    state = tmp_path / "producer.json"
    sim_runner.record_run_outcome(True, head="a", elapsed=60, state_path=state)
    assert sim_runner.run_budget_seconds(state) == sim_runner.LEGACY_RUN_TIMEOUT_S
    for garbage in ("{not json", json.dumps({}), json.dumps({"last_success_elapsed_s": True}),
                    json.dumps({"last_success_elapsed_s": 0}), json.dumps([1])):
        state.write_text(garbage)
        assert sim_runner.run_budget_seconds(state) == 2 * sim_runner.LEGACY_RUN_TIMEOUT_S, garbage
    assert sim_runner.run_budget_seconds(tmp_path / "absent.json") == 2 * sim_runner.LEGACY_RUN_TIMEOUT_S


def test_run_simulation_hands_the_derived_budget_to_the_child_and_names_it_on_a_kill(tmp_path, monkeypatch):
    state = _isolate(tmp_path, monkeypatch)
    sim_runner.record_run_outcome(True, head="a", elapsed=5119, state_path=state)
    seen = []

    def fake_run(cmd, **kwargs):
        if "annual_report" in " ".join(str(a) for a in cmd):
            seen.append(kwargs.get("timeout"))
            raise subprocess.TimeoutExpired(cmd, kwargs.get("timeout"), stderr="")
        return MagicMock(returncode=0)

    monkeypatch.setattr(sim_runner.subprocess, "run", fake_run)
    assert sim_runner.run_simulation() is False
    assert seen == [10238]
    assert "(budget 10238s)" in (tmp_path / "log.md").read_text()
