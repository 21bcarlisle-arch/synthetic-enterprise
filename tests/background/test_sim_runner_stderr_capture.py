"""H30 — the sim runner's failure report must carry the child's traceback.

The guard in `tools/child_stderr_guard.py` proves the CLASS cannot come back
in source. It cannot prove the payload actually reaches a reader: a site could
capture stderr perfectly and then log `rc=1` anyway, and the guard would call
that clean. These tests close that half by driving the real
`run_simulation()` / `auto_process_marker()` failure paths and asserting the
child's own words appear in the log line and in the alert.

The fixture is the REAL failure: the `NameError: _IC_SEGMENTS` traceback that
killed eight consecutive runs on 2026-08-08 and could not be diagnosed from
the runner's own output.

Mutation sensitivity (R15): remove `stderr=subprocess.PIPE` from
`run_simulation` and `test_failure_log_carries_the_childs_traceback` goes red,
because the fake child's stderr is only reachable when the caller asked for
it. `test_the_launch_asks_for_the_childs_stderr` is the direct pin on the
argument itself.
"""
from __future__ import annotations

import subprocess
from unittest.mock import MagicMock

import pytest

from background import sim_runner

REAL_TRACEBACK = (
    'Traceback (most recent call last):\n'
    '  File "/home/rich/synthetic-enterprise/simulation/arrears_engine.py", '
    'line 275, in payment_outcome\n'
    '    if segment in _IC_SEGMENTS:\n'
    "NameError: name '_IC_SEGMENTS' is not defined\n"
)


@pytest.fixture
def runner(tmp_path, monkeypatch):
    """`run_simulation` pointed entirely at tmp_path, with the two human
    channels (log file, NTFY) captured so they can be asserted on."""
    monkeypatch.setattr(sim_runner, "PROJECT_DIR", tmp_path)
    monkeypatch.setattr(sim_runner, "LOG_FILE", tmp_path / "sim-runner-log.md")
    monkeypatch.setattr(sim_runner, "STAGING_DIR", tmp_path / "staging")
    monkeypatch.setattr(sim_runner, "REPORTS_DIR", tmp_path / "reports")
    monkeypatch.setattr(sim_runner, "_git_head", lambda: "abc1234")
    sent: list[str] = []
    monkeypatch.setattr(sim_runner, "notify", lambda msg, **k: sent.append(msg))
    status: list[dict] = []
    monkeypatch.setattr(
        sim_runner, "update_agent_status",
        lambda *a, **k: status.append(dict(k)),
    )
    return tmp_path, sent, status


def _fail_with(stderr, kwargs_seen):
    """A child that exits 1 having written `stderr` — but only hands it back
    if the caller actually asked for it, exactly like the real subprocess."""
    def fake_run(cmd, **kwargs):
        kwargs_seen.append(kwargs)
        m = MagicMock()
        m.returncode = 1
        asked = kwargs.get("capture_output") or kwargs.get("stderr") is subprocess.PIPE
        m.stderr = stderr if asked else None
        return m
    return fake_run


class TestFailureReportCarriesThePayload:

    def test_the_launch_asks_for_the_childs_stderr(self, runner, monkeypatch):
        _, _, _ = runner
        seen: list[dict] = []
        monkeypatch.setattr(sim_runner.subprocess, "run", _fail_with(REAL_TRACEBACK, seen))
        sim_runner.run_simulation()
        assert seen, "run_simulation did not launch a child at all"
        launch = seen[0]
        assert launch.get("capture_output") or launch.get("stderr") is subprocess.PIPE, (
            "the simulation child is launched with its stderr INHERITED — under a "
            "daemon that fd is a socket, and the traceback is destroyed (H30)"
        )

    def test_failure_log_carries_the_childs_traceback(self, runner, monkeypatch):
        tmp_path, _, _ = runner
        monkeypatch.setattr(sim_runner.subprocess, "run", _fail_with(REAL_TRACEBACK, []))

        assert sim_runner.run_simulation() is False

        log_text = (tmp_path / "sim-runner-log.md").read_text()
        assert "rc=1" in log_text
        assert "_IC_SEGMENTS" in log_text, (
            "the log records the return code but not the traceback — this is "
            "precisely the 2026-08-08 state: eight failures, nothing diagnosable"
        )
        assert "NameError" in log_text

    def test_the_alert_names_the_fault_not_just_the_code(self, runner, monkeypatch):
        _, sent, _ = runner
        monkeypatch.setattr(sim_runner.subprocess, "run", _fail_with(REAL_TRACEBACK, []))

        sim_runner.run_simulation()

        assert sent, "a failed run sent no alert at all"
        assert "NameError" in sent[0], (
            "R5: an alert fires on a transition AND carries its diagnostic "
            "payload; 'Run FAILED' alone cannot be acted on"
        )

    def test_agent_status_anomaly_carries_it_too(self, runner, monkeypatch):
        _, _, status = runner
        monkeypatch.setattr(sim_runner.subprocess, "run", _fail_with(REAL_TRACEBACK, []))

        sim_runner.run_simulation()

        anomalies = [s.get("anomaly", "") for s in status]
        assert any("NameError" in a for a in anomalies), anomalies

    def test_a_silent_child_says_so_explicitly(self, runner, monkeypatch):
        """An empty capture and a discarded capture must not look the same.

        If the child genuinely wrote nothing, the log has to SAY that —
        otherwise a future reader cannot tell 'the child was silent' from
        'nobody captured it', which is the ambiguity this atom removes.
        """
        tmp_path, _, _ = runner
        monkeypatch.setattr(sim_runner.subprocess, "run", _fail_with("", []))

        sim_runner.run_simulation()

        log_text = (tmp_path / "sim-runner-log.md").read_text()
        assert "EMPTY" in log_text or "no stderr captured" in log_text


class TestTimeoutPathToo:

    def test_timeout_reports_what_the_child_managed_to_write(self, runner, monkeypatch):
        tmp_path, sent, _ = runner

        def fake_run(cmd, **kwargs):
            raise subprocess.TimeoutExpired(
                cmd=cmd, timeout=7200, output=None,
                stderr=b"  writing settlement runs...\nstuck at 2019-03-31 SP47\n",
            )

        monkeypatch.setattr(sim_runner.subprocess, "run", fake_run)

        assert sim_runner.run_simulation() is False

        log_text = (tmp_path / "sim-runner-log.md").read_text()
        assert "TIMED OUT" in log_text
        assert "2019-03-31 SP47" in log_text, (
            "a killed child's partial stderr is usually where it got stuck; "
            "TimeoutExpired carries it and it must not be dropped"
        )


class TestPublishSeamToo:
    """`auto_process_marker` is the same defect in the same file."""

    def test_publisher_failure_carries_its_stderr(self, runner, monkeypatch):
        tmp_path, _, _ = runner
        monkeypatch.setattr(sim_runner, "_record_publish_gate_outcome", lambda *a, **k: None)

        def fake_run(cmd, **kwargs):
            m = MagicMock()
            m.returncode = 1
            asked = kwargs.get("capture_output") or kwargs.get("stderr") is subprocess.PIPE
            m.stderr = "RuntimeError: dashboard basis-label gate refused\n" if asked else None
            return m

        monkeypatch.setattr(sim_runner.subprocess, "run", fake_run)

        rc = sim_runner.auto_process_marker(tmp_path / "run_complete_x.md")

        assert rc == 1
        log_text = (tmp_path / "sim-runner-log.md").read_text()
        assert "basis-label gate refused" in log_text
