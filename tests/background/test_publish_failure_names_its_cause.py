"""A refused publish must name its own cause — on the stream the publisher actually uses.

THE INCIDENT (2026-08-20 07:58Z .. 2026-08-21 16:03Z, 32 hours, 46 refusals).
`background_worker.process_leftover_run_markers` launched the publisher with
`stderr=subprocess.PIPE` and nothing for stdout, under a comment reading "this sweep is
the SAFETY NET ... Capture what the publisher actually said." It captured the wrong
stream. `process_run_complete.log()` — which issues EVERY verdict the publisher can
reach, including the one that mattered — writes to **stdout**. So the entire outage
produced, once per cycle, exactly this:

    Failed to process run_complete_20260821T153714Z.md (rc=1) — will retry next cycle
      publisher stderr (last 40 lines):
    WARNING (pytensor.configdefaults): g++ not detected! ...
    ... SyntaxWarning: "\\_" is an invalid escape sequence ...

Four lines of library noise, byte-identical on all 46, naming nothing. The sentence that
did name it — `Fast test suite timed out (>300s) -- NOT committing` — was printed every
single cycle and thrown away at the pipe. `sim_runner`'s auto-process branch had the same
launch and went further, telling the reader "the refusing gate is named in the publisher
log tail" of a tail that structurally could not name it.

TWO HALVES, and this project has closed this class on one half before — in `sim_runner`'s
own comments, about this same pair of files, for the same reason ("the class was closed on
one half and left open on the half that runs most often"). So both launch sites are pinned
here, in one file, and the sim_runner half is not optional.

MUTATION SENSITIVITY (R15) — each proven by reverting the fix, not asserted:
  * delete `stdout=subprocess.PIPE` from `background_worker`'s launch  ->
    `test_the_worker_launch_asks_for_the_publishers_stdout` and
    `test_the_worker_log_names_the_real_refusal` both red.
  * delete it from `sim_runner.auto_process_marker`'s launch ->
    `test_the_sim_runner_launch_asks_for_the_publishers_stdout` and
    `test_the_sim_runner_log_names_the_real_refusal` both red.
  * collapse `NOT_PIPED`/`SAID_NOTHING` to one string ->
    `test_a_stream_nobody_piped_is_not_a_silent_child` red.
  * revert `child_output_excerpt` to a stderr-only tail -> the two log tests red.

THE FIXTURE IS THE REAL OUTAGE: the stdout and stderr of the 16:03Z cycle, quoted from
docs/observability/sim-runner-log.md and docs/observability/background-worker-log.md.
"""
from __future__ import annotations

import subprocess
from unittest.mock import MagicMock

import pytest

from background import background_worker, sim_runner
from background.child_diagnostics import NOT_PIPED, SAID_NOTHING, child_output_excerpt

#: What the publisher printed to STDOUT on the 16:03Z cycle — its own verdict.
REAL_PUBLISHER_STDOUT = (
    "- [2026-08-21 16:03 UTC] [process_run] Running fast test suite (SIM_FAST_MODE=1)\n"
    "- [2026-08-21 16:03 UTC] [process_run] Fast test suite timed out (>300s) -- NOT "
    "committing. R15: an unavailable check is a FAILED check; a gate that did not finish "
    "cannot authorise a publish.\n"
    "- [2026-08-21 16:03 UTC] [process_run] Scoped publish-path gate FAILED - not "
    "committing content\n"
)

#: What it wrote to STDERR on the same cycle — every byte of it noise.
REAL_PUBLISHER_STDERR = (
    "WARNING (pytensor.configdefaults): g++ not detected!  PyTensor will be unable to "
    "compile C-implementations and will default to Python.\n"
    "/var/tmp/publish-gate-head-rxiz3p3c/saas/reporting/annual_report.py:7952: "
    'SyntaxWarning: "\\_" is an invalid escape sequence.\n'
)

#: The words a reader needs. If none of these reach the log, the cycle is undiagnosable.
CAUSE_PHRASES = ("Fast test suite timed out", "gate FAILED")


def _publisher_that_refuses(kwargs_seen=None):
    """A publisher exiting 1, handing back each stream ONLY if the caller piped it.

    This is the whole point of the fixture: a launch site that does not ask for stdout
    must not be able to pass by accident. `MagicMock` would happily return a truthy
    `.stdout` for a caller that never requested one, which would make every test here
    fail-open — the exact R15 shape this file is about.
    """
    def fake_run(cmd, **kwargs):
        if kwargs_seen is not None:
            kwargs_seen.append(kwargs)
        m = MagicMock()
        m.returncode = 1
        captured = kwargs.get("capture_output")
        m.stdout = REAL_PUBLISHER_STDOUT if (
            captured or kwargs.get("stdout") is subprocess.PIPE) else None
        m.stderr = REAL_PUBLISHER_STDERR if (
            captured or kwargs.get("stderr") is subprocess.PIPE) else None
        return m
    return fake_run


# ── the pure helper ──────────────────────────────────────────────────────────────────────

class TestTheExcerptShowsBothStreams:

    def test_it_carries_the_verdict_that_lives_on_stdout(self):
        text = child_output_excerpt(REAL_PUBLISHER_STDOUT, REAL_PUBLISHER_STDERR)
        assert "Fast test suite timed out" in text

    def test_it_still_carries_stderr_for_a_child_that_died_on_a_traceback(self):
        """Preferring stdout would fail-open the other way — pin that it does not."""
        text = child_output_excerpt("", "NameError: name '_IC_SEGMENTS' is not defined")
        assert "_IC_SEGMENTS" in text

    def test_a_stream_nobody_piped_is_not_a_silent_child(self):
        """'Nobody looked' is a bug in the launch site; 'it said nothing' is a fact
        about the child. A reader who cannot tell them apart debugs the wrong one —
        and this is precisely how the stderr-only launch read for thirteen days."""
        text = child_output_excerpt(None, "boom", stdout_piped=False)
        assert NOT_PIPED in text
        assert SAID_NOTHING not in text.split("stderr")[0]

    def test_a_piped_but_empty_stream_says_the_child_was_silent(self):
        text = child_output_excerpt("", "", stdout_piped=True, stderr_piped=True)
        assert text.count(SAID_NOTHING) == 2
        assert NOT_PIPED not in text

    def test_it_never_raises_on_junk(self):
        """A diagnostic helper that can raise turns a child's failure into the
        parent's failure — how a monitoring path takes down what it monitors."""
        assert isinstance(child_output_excerpt(MagicMock(), 7), str)
        assert isinstance(child_output_excerpt(b"\xff\xfe bytes", None), str)


# ── half one: the leftover-marker sweep ──────────────────────────────────────────────────

@pytest.fixture
def worker(tmp_path, monkeypatch):
    staging = tmp_path / "staging"
    staging.mkdir()
    (staging / "run_complete_20260821T153714Z.md").write_text("# Simulation Run Complete\n")
    monkeypatch.setattr(background_worker, "STAGING_DIR", staging)
    monkeypatch.setattr(background_worker, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(background_worker, "SWEEP_STATE_FILE", tmp_path / ".sweep.json")
    import background.process_run_complete as prc
    monkeypatch.setattr(prc, "PUBLISH_GATE_STATE_FILE", tmp_path / ".gate.json")
    monkeypatch.setattr(prc, "LOG_FILE", tmp_path / "prc_log.md")
    monkeypatch.setattr(prc, "LAST_TESTED_HASH_FILE", tmp_path / ".last_tested_hash")
    return tmp_path


def test_the_worker_launch_asks_for_the_publishers_stdout(worker, monkeypatch):
    seen: list[dict] = []
    monkeypatch.setattr(background_worker.subprocess, "run", _publisher_that_refuses(seen))

    background_worker.process_leftover_run_markers()

    assert seen, "the sweep launched no publisher at all"
    launch = seen[0]
    assert launch.get("capture_output") or launch.get("stdout") is subprocess.PIPE, (
        "the publisher is launched with its STDOUT inherited. Under a daemon that fd is a "
        "socket, and stdout is the only stream process_run_complete.log() writes its "
        "verdicts to — so every refusal is discarded at the pipe (the 32-hour wedge of "
        "2026-08-20/21, 46 refusals, none diagnosable from this log)"
    )


def test_the_worker_log_names_the_real_refusal(worker, monkeypatch):
    monkeypatch.setattr(background_worker.subprocess, "run", _publisher_that_refuses())

    background_worker.process_leftover_run_markers()

    log_text = (worker / "log.md").read_text()
    assert "rc=1" in log_text
    assert any(p in log_text for p in CAUSE_PHRASES), (
        "the sweep logged the return code and not the cause. This is the 2026-08-21 state "
        "exactly: 46 consecutive refusals whose log carried only pytensor warnings, while "
        f"the publisher printed {CAUSE_PHRASES[0]!r} on every one of them"
    )


def test_the_worker_log_does_not_pass_off_library_noise_as_a_diagnosis(worker, monkeypatch):
    """The noise may appear — but never as the ONLY thing, and never unlabelled.

    Without this, a fix that captured stdout and then rendered only stderr would pass
    the test above by accident on a child whose stdout happened to repeat the phrase.
    """
    monkeypatch.setattr(background_worker.subprocess, "run", _publisher_that_refuses())

    background_worker.process_leftover_run_markers()

    log_text = (worker / "log.md").read_text()
    assert "stdout" in log_text, (
        "the excerpt does not label which stream it is quoting, so a reader cannot tell "
        "the publisher's verdict from whatever the runtime warned about last"
    )


# ── half two: the steady-state path (sim_runner), the half left open last time ───────────

@pytest.fixture
def runner(tmp_path, monkeypatch):
    monkeypatch.setattr(sim_runner, "PROJECT_DIR", tmp_path)
    monkeypatch.setattr(sim_runner, "LOG_FILE", tmp_path / "sim-runner-log.md")
    monkeypatch.setattr(sim_runner, "_record_publish_gate_outcome", lambda *a, **k: None)
    marker = tmp_path / "run_complete_20260821T153714Z.md"
    marker.write_text("# Simulation Run Complete\n")
    return tmp_path, marker


def test_the_sim_runner_launch_asks_for_the_publishers_stdout(runner, monkeypatch):
    tmp_path, marker = runner
    seen: list[dict] = []
    monkeypatch.setattr(sim_runner.subprocess, "run", _publisher_that_refuses(seen))

    sim_runner.auto_process_marker(marker)

    assert seen, "auto_process_marker launched no publisher at all"
    launch = seen[0]
    assert launch.get("capture_output") or launch.get("stdout") is subprocess.PIPE, (
        "the SIBLING HALF is unpiped again — this is the path that publishes in the steady "
        "state, and this file's own history records the last time a class was closed on "
        "background_worker and left open here"
    )


def test_the_sim_runner_log_names_the_real_refusal(runner, monkeypatch):
    tmp_path, marker = runner
    monkeypatch.setattr(sim_runner.subprocess, "run", _publisher_that_refuses())

    sim_runner.auto_process_marker(marker)

    log_text = (tmp_path / "sim-runner-log.md").read_text()
    assert any(p in log_text for p in CAUSE_PHRASES), (
        "auto-process logged 'rc=1' and not the cause, while its own sibling branch tells "
        "the reader the refusing gate 'is named in the publisher log tail'"
    )
