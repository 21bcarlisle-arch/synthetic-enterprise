"""H15 -- sim_runner's OWN publish path must feed the publish-gate wedge detector.

THE DEFECT THIS PINS (observed 2026-07-30..2026-08-03, ~5960 min armed alarm):
`record_publish_gate_success` had exactly ONE caller --
`background_worker.process_leftover_run_markers()`'s sweep. But that sweep is
not the path that publishes in the steady state: `sim_runner.py` publishes the
marker it just wrote, every cycle, and reported its return code to NOBODY.

So the detector was blind to the only healthy publisher and saw only the sweep,
which by construction chews the STALE backlog and fails on it. sim_runner
published cleanly every ~10 min (sim-runner-log.md 04:02Z "Committed
locally... Done") while the streak the sweep kept growing was never cleared --
a PRIORITY-ZERO wedge doorbell fired every tick against a working pipeline.

R15: each test below names the defect it fires on, and the mutation that makes
it go red is stated in its docstring -- deleting the `_record_publish_gate_
outcome` call from sim_runner's auto-process path reds the success test, and
restoring the old "sweep is the only caller" wiring reds the shared-router test.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import background.process_run_complete as prc  # noqa: E402
import background.sim_runner as sim_runner  # noqa: E402


@pytest.fixture(autouse=True)
def _isolate(tmp_path, monkeypatch):
    """Redirect every real-disk surface this touches into tmp_path.

    Same test-isolation-leak class the background_worker suite guards: the
    router writes wedge state + a log line, and a test must never touch the
    live docs/observability/ files.
    """
    monkeypatch.setattr(prc, "PUBLISH_GATE_STATE_FILE", tmp_path / ".publish_gate_state.json")
    monkeypatch.setattr(prc, "LOG_FILE", tmp_path / "prc_log.md")
    monkeypatch.setattr(sim_runner, "LOG_FILE", tmp_path / "sim_log.md", raising=False)
    yield


def _marker(tmp_path, name="run_complete_20260803T040000Z.md"):
    m = tmp_path / name
    m.write_text(
        "# Simulation Run Complete\n\nGit: abc1234\n"
        "JSON: /nonexistent/run_output_abc1234.json\n"
    )
    return m


# ── the shared router itself ────────────────────────────────────────────────

def test_router_rc0_records_success(tmp_path):
    """MUTATION: make the rc==0 branch a no-op -> this goes red."""
    prc.record_publish_gate_failure("seed a wedge", rc=1, git_hash="dead")
    assert prc._read_publish_gate_state().get("failures"), "precondition: streak seeded"

    assert prc.record_publish_gate_outcome(_marker(tmp_path), 0) == "success"

    assert not prc._read_publish_gate_state().get("failures"), \
        "a clean publish must CLEAR the wedge streak"


def test_router_nonzero_records_failure(tmp_path):
    """MUTATION: drop the else-branch -> this goes red."""
    assert prc.record_publish_gate_outcome(_marker(tmp_path), 1) == "failure"
    failures = prc._read_publish_gate_state().get("failures")
    assert len(failures) == 1
    assert failures[0]["rc"] == 1


def test_router_lock_skip_records_neither(tmp_path):
    """A lock-skip is evidence of NOTHING -- it must not clear OR grow the
    streak (the 2026-07-29 fail-open: a skip recorded as success DISARMED the
    detector). MUTATION: treat 75 as success -> this goes red."""
    prc.record_publish_gate_failure("seed a wedge", rc=1, git_hash="dead")
    before = prc._read_publish_gate_state().get("failures")

    assert prc.record_publish_gate_outcome(_marker(tmp_path), prc.EXIT_LOCK_SKIPPED) == "skipped"

    assert prc._read_publish_gate_state().get("failures") == before, \
        "a lock-skip must leave the streak exactly as it found it"


# ── the wiring that was actually missing ────────────────────────────────────

def _drive_auto_process(monkeypatch, tmp_path, returncode=None, timeout=False):
    """Drive sim_runner's REAL publish seam (`auto_process_marker`) with only
    the outbound subprocess stubbed.

    Deliberately does NOT stub `_record_publish_gate_outcome`: the whole point
    is that the wiring inside auto_process_marker is what gets exercised, so
    deleting that call line makes these tests go red.
    """
    marker = _marker(tmp_path)

    def _fake_run(*a, **k):
        if timeout:
            raise sim_runner.subprocess.TimeoutExpired(cmd="prc", timeout=1200)
        return MagicMock(returncode=returncode)

    monkeypatch.setattr(sim_runner.subprocess, "run", _fake_run)
    return marker, sim_runner.auto_process_marker(marker)


def test_sim_runner_clean_publish_clears_the_wedge(monkeypatch, tmp_path):
    """THE named defect. sim_runner publishing cleanly MUST clear a streak the
    leftover sweep grew -- otherwise a healthy pipeline can never disarm the
    alarm, which is exactly the ~5960-min false wedge.

    MUTATION (verified 2026-08-03): delete the `_record_publish_gate_outcome(
    marker, rc)` call from `auto_process_marker` -> this goes red.
    """
    prc.record_publish_gate_failure("stale backlog marker", rc=1, git_hash="dead")
    assert prc._read_publish_gate_state().get("failures"), "precondition: wedge armed"

    _marker_path, rc = _drive_auto_process(monkeypatch, tmp_path, returncode=0)

    assert rc == 0
    assert not prc._read_publish_gate_state().get("failures"), \
        "sim_runner's clean publish must clear the wedge the sweep grew"


def test_sim_runner_failed_publish_grows_the_wedge(monkeypatch, tmp_path):
    """The other direction: a real failure on THIS path must be visible to the
    detector, not just failures the leftover sweep happens to see.

    MUTATION: delete the same call -> this goes red (no failure recorded).
    """
    _drive_auto_process(monkeypatch, tmp_path, returncode=1)

    failures = prc._read_publish_gate_state().get("failures")
    assert len(failures) == 1 and failures[0]["rc"] == 1


def test_sim_runner_lock_skip_leaves_streak_untouched(monkeypatch, tmp_path):
    """A lock-skip on this path published nothing -- it must neither clear nor
    grow the streak. MUTATION: pass 75 through as success -> this goes red."""
    prc.record_publish_gate_failure("stale backlog marker", rc=1, git_hash="dead")
    before = prc._read_publish_gate_state().get("failures")

    _drive_auto_process(monkeypatch, tmp_path, returncode=75)

    assert prc._read_publish_gate_state().get("failures") == before


def test_sim_runner_timeout_is_recorded_as_a_failure(monkeypatch, tmp_path):
    """The 4-day 2026-07-25 blackout presented as a publish TIMEOUT. A timeout
    leaves the marker unpublished, so it is a failure -- the detector must not
    see silence. MUTATION: drop the recorder from the except branch -> red."""
    _marker_path, rc = _drive_auto_process(monkeypatch, tmp_path, timeout=True)

    assert rc == 124
    failures = prc._read_publish_gate_state().get("failures")
    assert len(failures) == 1 and failures[0]["rc"] == 124


def test_sim_runner_and_worker_share_one_router(tmp_path):
    """R10 -- the fix is ONE router every publish path feeds, not a second copy.

    MUTATION: give background_worker back its own inline three-outcome logic
    (or point sim_runner at a private duplicate) -> this goes red, because a
    future third publisher could then reintroduce a half-blind detector.
    """
    import background.background_worker as bw

    assert hasattr(prc, "record_publish_gate_outcome"), \
        "the shared router must exist in process_run_complete"

    src_worker = Path(bw.__file__).read_text()
    src_runner = Path(sim_runner.__file__).read_text()
    for name, src in (("background_worker", src_worker), ("sim_runner", src_runner)):
        assert "record_publish_gate_outcome" in src, \
            f"{name} must feed the shared publish-gate router"
        assert "record_publish_gate_success()" not in src, \
            (f"{name} must NOT call record_publish_gate_success directly -- "
             "route through the shared three-outcome router so a lock-skip "
             "can never be mistaken for a publish")
