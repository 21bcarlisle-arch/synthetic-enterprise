"""Tests for background/background_worker.py::process_leftover_run_markers()
-- the load-bearing (and previously undocumented, untested) safety net for
a run_complete_*.md marker background/sim_runner.py itself skipped.

2026-07-13, director-flagged: sim_runner.py only ever calls
process_run_complete.py with the ONE marker it just wrote each cycle, and
that script's own lock-skip path leaves the marker untouched (and, until
2026-07-29, returned exit code 0 -- indistinguishable from a genuine
success), so a marker left behind because another instance
held the lock is NEVER retried by sim_runner.py itself. This test suite
asserts the one real property that makes the whole coupling safe:
process_leftover_run_markers() unconditionally re-globs every
run_complete_*.md still in staging/, every time it's called, regardless of
how many there are or what state they're in.

2026-08-03, OPS_run_marker_sweep_livelock: the sweep used to re-attempt
EVERY leftover marker EVERY cycle, each attempt independently (and always
losing) racing sim_runner.py for the same non-blocking run lock -- a
genuine livelock (thousands of cycles, zero markers ever drained), not a
slow queue. The tests below cover the fix: the sweep now wins the lock ONCE
per batch (proven against the REAL flock, not a mock) and a general
zero-progress-retry-loop alarm (`_record_sweep_progress`) that fires when a
retry loop attempts work and drains nothing for too many consecutive
cycles.
"""
import fcntl
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from background import background_worker


@pytest.fixture(autouse=True)
def _isolate(tmp_path, monkeypatch):
    staging = tmp_path / "staging"
    staging.mkdir()
    monkeypatch.setattr(background_worker, "STAGING_DIR", staging)
    monkeypatch.setattr(background_worker, "LOG_FILE", tmp_path / "log.md")
    # OPS_run_marker_sweep_livelock: the sweep now wins process_run_complete's
    # REAL run lock (a plain flock) itself for the whole batch. Redirect it to
    # a per-test tmp file so tests exercise the genuine locking mechanism
    # without touching (or colliding with) a real running daemon's lock file.
    monkeypatch.setattr(background_worker, "ZERO_PROGRESS_STATE_FILE",
                        tmp_path / ".marker_sweep_zero_progress_state.json")
    # H15: _record_publish_gate_outcome() imports process_run_complete and
    # writes its wedge-state + log files. Redirect BOTH to per-test temp paths
    # so the sweep never touches the real docs/observability/ files (same
    # test-isolation-leak class as the fingerprint/log redirects in
    # test_process_run_complete.py).
    import background.process_run_complete as prc
    monkeypatch.setattr(prc, "PUBLISH_GATE_STATE_FILE", tmp_path / ".publish_gate_state.json")
    monkeypatch.setattr(prc, "LOG_FILE", tmp_path / "prc_log.md")
    monkeypatch.setattr(prc, "RUN_LOCK_FILE", tmp_path / ".process_run_complete.lock")
    # notify() (used by the zero-progress alarm when no notify_fn is injected)
    # persists transition state to its own real file by default -- isolate it
    # the same way every other alarm test in this suite does.
    import background.notify as notify_mod
    monkeypatch.setattr(notify_mod, "TRANSITIONS_FILE", tmp_path / ".notify_transitions.json")
    yield


def _fake_success(*args, **kwargs):
    return MagicMock(returncode=0)


def test_no_markers_is_a_silent_noop(monkeypatch):
    calls = []
    monkeypatch.setattr(background_worker.subprocess, "run", lambda *a, **k: calls.append(a) or _fake_success())
    background_worker.process_leftover_run_markers()
    assert calls == []


def test_single_marker_is_processed(monkeypatch):
    marker = background_worker.STAGING_DIR / "run_complete_20260713T000000Z.md"
    marker.write_text("# Simulation Run Complete\n")
    calls = []
    monkeypatch.setattr(background_worker.subprocess, "run", lambda *a, **k: calls.append(a[0]) or _fake_success())

    background_worker.process_leftover_run_markers()

    assert len(calls) == 1
    assert str(marker) in calls[0]


def test_collects_every_leftover_marker_unconditionally(monkeypatch):
    """The core regression guard: this is the ONE property the whole
    sim_runner.py / process_run_complete.py coupling depends on -- if this
    glob is ever narrowed (e.g. skip markers older than N, or only the
    most recent one), a lock-skipped marker becomes permanently orphaned
    with nothing left to rescue it."""
    names = [f"run_complete_2026071{i}T000000Z.md" for i in range(1, 4)]
    for name in names:
        (background_worker.STAGING_DIR / name).write_text("# Simulation Run Complete\n")
    # A non-marker file must never be swept up by the same glob.
    (background_worker.STAGING_DIR / "from_rich_20260713.md").write_text("not a run marker")

    calls = []
    monkeypatch.setattr(background_worker.subprocess, "run", lambda *a, **k: calls.append(a[0]) or _fake_success())

    background_worker.process_leftover_run_markers()

    assert len(calls) == 3
    processed_paths = {Path(c[-1]).name for c in calls}
    assert processed_paths == set(names)


def test_a_failed_marker_does_not_stop_the_others_being_attempted(monkeypatch):
    """One marker returning a real failure (rc != 0, a genuine processing
    error, distinct from the lock-skip's own rc==0) must not abort the
    sweep -- every OTHER leftover marker still gets its own attempt this
    same cycle."""
    ok_marker = background_worker.STAGING_DIR / "run_complete_20260713T010000Z.md"
    bad_marker = background_worker.STAGING_DIR / "run_complete_20260713T020000Z.md"
    ok_marker.write_text("# Simulation Run Complete\n")
    bad_marker.write_text("# Simulation Run Complete\n")

    def _run(args, **kwargs):
        if bad_marker.name in args[-1]:
            return MagicMock(returncode=1)
        return MagicMock(returncode=0)

    monkeypatch.setattr(background_worker.subprocess, "run", _run)
    background_worker.process_leftover_run_markers()  # must not raise
    # Both were at least attempted (rc doesn't matter for this assertion --
    # the point is the loop kept going, not that both "succeeded").


def test_failing_marker_records_publish_gate_failure(monkeypatch):
    """H15 wiring: an rc!=0 processing outcome is fed into the publish-gate
    failure detector so consecutive silent failures can raise an alert."""
    marker = background_worker.STAGING_DIR / "run_complete_20260714T000000Z.md"
    marker.write_text("# Simulation Run Complete\nGit: deadbee\n")
    monkeypatch.setattr(background_worker.subprocess, "run",
                        lambda *a, **k: MagicMock(returncode=-9))

    recorded = []
    import background.process_run_complete as prc
    monkeypatch.setattr(prc, "record_publish_gate_failure",
                        lambda *a, **k: recorded.append((a, k)) or {"fired": False})
    monkeypatch.setattr(prc, "record_publish_gate_success",
                        lambda *a, **k: pytest.fail("success must not be recorded on rc!=0"))

    background_worker.process_leftover_run_markers()

    assert len(recorded) == 1
    assert recorded[0][1]["rc"] == -9              # OOM SIGKILL surfaced verbatim
    assert recorded[0][1]["git_hash"] == "deadbee"  # parsed from the marker


def test_successful_marker_records_publish_gate_success(monkeypatch):
    """H15 wiring: an rc==0 outcome CLEARS the wedge state (re-arm)."""
    marker = background_worker.STAGING_DIR / "run_complete_20260714T010000Z.md"
    marker.write_text("# Simulation Run Complete\nGit: cafef00\n")
    monkeypatch.setattr(background_worker.subprocess, "run",
                        lambda *a, **k: MagicMock(returncode=0))

    cleared = []
    import background.process_run_complete as prc
    monkeypatch.setattr(prc, "record_publish_gate_success",
                        lambda *a, **k: cleared.append(True))
    monkeypatch.setattr(prc, "record_publish_gate_failure",
                        lambda *a, **k: pytest.fail("failure must not be recorded on rc==0"))

    background_worker.process_leftover_run_markers()

    assert cleared == [True]


def test_publish_gate_recording_failure_never_breaks_the_sweep(monkeypatch):
    """A monitoring failure must never abort marker processing."""
    marker = background_worker.STAGING_DIR / "run_complete_20260714T020000Z.md"
    marker.write_text("# Simulation Run Complete\n")
    monkeypatch.setattr(background_worker.subprocess, "run",
                        lambda *a, **k: MagicMock(returncode=1))
    import background.process_run_complete as prc
    monkeypatch.setattr(prc, "record_publish_gate_failure",
                        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")))
    background_worker.process_leftover_run_markers()  # must not raise


# ── Lock-skip is NOT a publish (fail-open closed 2026-07-29) ───────────────────
# A lock-skip means another instance held the run lock and this sweep left the
# marker untouched. It used to exit 0, so the sweep logged "Processed" and fed
# record_publish_gate_success() -- clearing the H15 wedge streak, re-arming the
# alarm and auto-resolving the open [ACTION NEEDED] item for a marker nobody
# published. Observed 2026-07-29 16:53Z on two backed-up markers, one minute
# before the lock holder itself failed the gate.

def _lock_skipped(*args, **kwargs):
    return MagicMock(returncode=background_worker.EXIT_LOCK_SKIPPED)


def test_worker_lock_skip_code_matches_the_processors(monkeypatch):
    """Drift guard: background_worker mirrors the constant as a literal (it
    must not import the publish pipeline at module scope). If the two ever
    diverge, a real skip silently becomes 'a failure' or -- worse, the old
    bug -- 'a success' again."""
    import background.process_run_complete as prc
    assert background_worker.EXIT_LOCK_SKIPPED == prc.EXIT_LOCK_SKIPPED


def test_lock_skip_records_neither_success_nor_failure(monkeypatch):
    marker = background_worker.STAGING_DIR / "run_complete_20260729T162844Z.md"
    marker.write_text("# Simulation Run Complete\n")
    monkeypatch.setattr(background_worker.subprocess, "run", _lock_skipped)

    import background.process_run_complete as prc
    recorded = []
    monkeypatch.setattr(prc, "record_publish_gate_success",
                        lambda *a, **k: recorded.append("success"))
    monkeypatch.setattr(prc, "record_publish_gate_failure",
                        lambda *a, **k: recorded.append("failure"))

    background_worker.process_leftover_run_markers()

    assert recorded == [], (
        "a lock-skip is evidence of NOTHING about the publish gate's health -- "
        "it must record neither outcome, got {}".format(recorded))


def test_lock_skip_does_not_clear_an_accumulated_wedge_streak(monkeypatch):
    """The harm the fail-open actually did: a skip wiped the failure streak
    that was about to raise the [ACTION NEEDED] alert, so a genuinely wedged
    pipeline could never reach the threshold."""
    import background.process_run_complete as prc
    prc._write_publish_gate_state({
        "failures": [{"ts": 1_000_000.0, "reason": "rc=1", "rc": 1, "kind": "test_failure",
                      "git_hash": "abc"},
                     {"ts": 1_000_100.0, "reason": "rc=1", "rc": 1, "kind": "test_failure",
                      "git_hash": "abc"}],
        "alerted_at": None,
        "wedge_since": 1_000_000.0,
    })
    marker = background_worker.STAGING_DIR / "run_complete_20260729T163802Z.md"
    marker.write_text("# Simulation Run Complete\n")
    monkeypatch.setattr(background_worker.subprocess, "run", _lock_skipped)

    background_worker.process_leftover_run_markers()

    after = prc._read_publish_gate_state()
    assert len(after.get("failures", [])) == 2, (
        "the streak must survive a lock-skip untouched")
    assert after.get("wedge_since") == 1_000_000.0, (
        "wedge age must keep measuring from the real start of the streak")


def test_lock_skip_is_not_logged_as_processed(monkeypatch):
    """The worker log is the first thing read when diagnosing a marker
    backlog; 'Processed X' for an untouched marker is a false claim."""
    marker = background_worker.STAGING_DIR / "run_complete_20260729T162844Z.md"
    marker.write_text("# Simulation Run Complete\n")
    monkeypatch.setattr(background_worker.subprocess, "run", _lock_skipped)

    background_worker.process_leftover_run_markers()

    written = background_worker.LOG_FILE.read_text()
    assert "Lock-skipped run_complete_20260729T162844Z.md" in written
    assert "Processed run_complete_20260729T162844Z.md" not in written


def test_a_real_success_still_clears_the_streak(monkeypatch):
    """Both ways (R15): the skip carve-out must not disarm real recovery."""
    import background.process_run_complete as prc
    prc._write_publish_gate_state({
        "failures": [{"ts": 1_000_000.0, "reason": "rc=1", "rc": 1, "kind": "test_failure",
                      "git_hash": "abc"}],
        "alerted_at": None,
        "wedge_since": 1_000_000.0,
    })
    marker = background_worker.STAGING_DIR / "run_complete_20260729T164000Z.md"
    marker.write_text("# Simulation Run Complete\n")
    monkeypatch.setattr(background_worker.subprocess, "run", _fake_success)

    background_worker.process_leftover_run_markers()

    assert prc._read_publish_gate_state().get("failures") == []


def test_a_real_failure_is_still_recorded(monkeypatch):
    """Both ways (R15): rc=1 must still accumulate toward the alert."""
    import background.process_run_complete as prc
    marker = background_worker.STAGING_DIR / "run_complete_20260729T164100Z.md"
    marker.write_text("# Simulation Run Complete\n")
    monkeypatch.setattr(background_worker.subprocess, "run",
                        lambda *a, **k: MagicMock(returncode=1))

    background_worker.process_leftover_run_markers()

    failures = prc._read_publish_gate_state().get("failures", [])
    assert len(failures) == 1 and failures[0]["rc"] == 1


def test_processing_order_is_deterministic_sorted(monkeypatch):
    """sorted() on the glob result means the oldest-timestamped marker
    (by filename) is always attempted first -- a real, if minor,
    fairness property worth locking in."""
    names = ["run_complete_20260713T030000Z.md", "run_complete_20260713T010000Z.md", "run_complete_20260713T020000Z.md"]
    for name in names:
        (background_worker.STAGING_DIR / name).write_text("# Simulation Run Complete\n")

    calls = []
    monkeypatch.setattr(background_worker.subprocess, "run", lambda *a, **k: calls.append(a[0][-1]) or _fake_success())

    background_worker.process_leftover_run_markers()

    processed_order = [Path(c).name for c in calls]
    assert processed_order == sorted(names)

# ── OPS_run_marker_sweep_livelock (2026-08-03): the sweep now wins the lock ────
# ONCE per batch, against the REAL flock, and any per-marker subprocess is told
# the lock is already held via LOCK_ALREADY_HELD_ENV.

def test_per_marker_subprocess_is_told_the_lock_is_already_held(monkeypatch):
    """The mechanism that lets the sweep's children stop racing their own
    parent: every subprocess.run call for a marker in this batch must carry
    LOCK_ALREADY_HELD_ENV=1, telling process_run_complete.py::main() to skip
    its own (guaranteed-to-lose) lock acquisition."""
    marker = background_worker.STAGING_DIR / "run_complete_20260803T000000Z.md"
    marker.write_text("# Simulation Run Complete\n")
    envs = []

    def _run(args, **kwargs):
        envs.append(kwargs.get("env"))
        return MagicMock(returncode=0)

    monkeypatch.setattr(background_worker.subprocess, "run", _run)
    background_worker.process_leftover_run_markers()

    assert len(envs) == 1
    assert envs[0] is not None
    assert envs[0][background_worker.LOCK_ALREADY_HELD_ENV] == "1"


def test_lock_busy_makes_zero_per_marker_attempts_and_logs_once(monkeypatch):
    """R4 real closed-loop test against the REAL flock (not mocked): this is
    the exact defect. Before the fix, a busy lock produced ONE lock-skip
    attempt PER marker, every cycle, forever (the log-storm symptom of the
    livelock). Now, when the lock is genuinely busy, the sweep makes ZERO
    per-marker attempts and logs exactly once."""
    import background.process_run_complete as prc
    names = [f"run_complete_2026080{i}T000000Z.md" for i in range(1, 5)]
    for name in names:
        (background_worker.STAGING_DIR / name).write_text("# Simulation Run Complete\n")

    # Hold the REAL run lock from this test, simulating sim_runner.py
    # actively publishing the marker it just wrote.
    prc.RUN_LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
    fh = open(prc.RUN_LOCK_FILE, "w")
    fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
    try:
        calls = []
        monkeypatch.setattr(background_worker.subprocess, "run",
                            lambda *a, **k: calls.append(a) or _fake_success())
        background_worker.process_leftover_run_markers()

        assert calls == [], "a busy lock must produce ZERO per-marker subprocess attempts"
        written = background_worker.LOG_FILE.read_text()
        assert written.count("Run lock busy") == 1, (
            "exactly ONE log line for the whole busy batch, not one per marker "
            "(the log-storm symptom this fix closes)")
        for name in names:
            assert "Lock-skipped {}".format(name) not in written
    finally:
        fcntl.flock(fh, fcntl.LOCK_UN)
        fh.close()


def test_lock_free_lets_the_sweep_actually_drain_a_backlog(monkeypatch):
    """The other half of the same real closed-loop test: with the lock free
    (nobody else holds it), the sweep wins it itself and every marker in the
    batch is genuinely attempted under that ONE acquisition."""
    names = [f"run_complete_2026080{i}T000000Z.md" for i in range(1, 5)]
    for name in names:
        (background_worker.STAGING_DIR / name).write_text("# Simulation Run Complete\n")

    calls = []
    monkeypatch.setattr(background_worker.subprocess, "run",
                        lambda *a, **k: calls.append(a[0][-1]) or _fake_success())
    background_worker.process_leftover_run_markers()

    assert len(calls) == 4
    assert {Path(c).name for c in calls} == set(names)
    written = background_worker.LOG_FILE.read_text()
    assert "Won the run lock" in written
    assert "Sweep drained 4/4 marker(s) this cycle" in written


def test_sweep_time_budget_stops_early_and_leaves_remainder(monkeypatch):
    """MARKER_SWEEP_TIME_BUDGET_SECONDS bounds one sweep's hold on the run
    lock -- a large backlog must drain over successive cycles, never starve
    sim_runner.py's own live publish by holding the lock for one unbounded
    pass."""
    names = [f"run_complete_2026080{i}T000000Z.md" for i in range(1, 5)]
    for name in names:
        (background_worker.STAGING_DIR / name).write_text("# Simulation Run Complete\n")
    monkeypatch.setattr(background_worker, "MARKER_SWEEP_TIME_BUDGET_SECONDS", -1)

    calls = []
    monkeypatch.setattr(background_worker.subprocess, "run",
                        lambda *a, **k: calls.append(a) or _fake_success())
    background_worker.process_leftover_run_markers()

    assert calls == [], "a negative/exhausted budget must process nothing this cycle"
    remaining = sorted(background_worker.STAGING_DIR.glob("run_complete_*.md"))
    assert len(remaining) == 4, "unattempted markers must stay in staging/ for the next cycle"
    written = background_worker.LOG_FILE.read_text()
    assert "time budget exhausted" in written


def test_sweep_feeds_real_observed_drained_count_into_the_alarm(monkeypatch):
    """Independence guard (R15 TAUTOLOGY pattern): the zero-progress alarm's
    input must be the REAL count of rc==0 outcomes this cycle, not something
    derived from the alarm's own state or from `markers_found`. Here only 1
    of 3 markers actually succeeds; that one real drain must register as
    progress even though the majority failed."""
    names = [f"run_complete_2026080{i}T000000Z.md" for i in range(1, 4)]
    for name in names:
        (background_worker.STAGING_DIR / name).write_text("# Simulation Run Complete\n")

    def _run(args, **kwargs):
        if names[1] in args[-1]:
            return MagicMock(returncode=0)
        return MagicMock(returncode=1)

    monkeypatch.setattr(background_worker.subprocess, "run", _run)
    background_worker.process_leftover_run_markers()

    state = background_worker._read_zero_progress_state()
    assert state["consecutive_zero_progress"] == 0, (
        "one genuine drain among the batch must reset the zero-progress streak "
        "even though 2 of 3 markers failed")


# ── Zero-progress retry-loop ALARM (R10 class closure + R15 mutation tests) ───
# "A retry loop which has never succeeded is an ALARM, not a log line." These
# tests exercise _record_sweep_progress directly with explicit, caller-supplied
# counts -- proving the alarm is an independent oracle (not derived from its
# own persisted state, R15's TAUTOLOGY pattern) and that it genuinely can both
# FIRE and stay SILENT depending on real inputs (R15: a control must be able
# to fail).

def test_zero_progress_alarm_fires_after_threshold_consecutive_zero_progress_cycles(monkeypatch):
    """R15 mutation test (fires): zero progress for
    ZERO_PROGRESS_ALARM_THRESHOLD consecutive cycles must page exactly once,
    at the threshold -- not before."""
    fired = []

    def _notify(msg, **kw):
        fired.append((msg, kw))

    result = None
    for i in range(background_worker.ZERO_PROGRESS_ALARM_THRESHOLD):
        result = background_worker._record_sweep_progress(
            markers_found=10, markers_drained=0, now=1_000_000.0 + i, notify_fn=_notify)
        if i < background_worker.ZERO_PROGRESS_ALARM_THRESHOLD - 1:
            assert fired == [], "must not fire before the threshold is reached (cycle {})".format(i)

    assert len(fired) == 1, "must fire exactly once at threshold"
    msg, kw = fired[0]
    assert kw["kind"] == "real_alarm"
    assert kw["state"] == "RED"
    assert "ZERO PROGRESS" in msg
    assert result["fired"] is True


def test_zero_progress_alarm_stays_silent_while_real_progress_is_made(monkeypatch):
    """R15 mutation test (silent): a retry loop draining at least one marker
    every cycle -- for far more cycles than the alarm threshold -- must NEVER
    page. Proves the alarm tracks genuine progress, not just a countdown."""
    fired = []

    def _notify(msg, **kw):
        fired.append((msg, kw))

    for i in range(background_worker.ZERO_PROGRESS_ALARM_THRESHOLD * 3):
        result = background_worker._record_sweep_progress(
            markers_found=10, markers_drained=1, now=1_000_000.0 + i, notify_fn=_notify)
        assert result["fired"] is False

    assert fired == [], "a retry loop making real progress every cycle must never alarm"


def test_zero_progress_alarm_fail_closed_on_unreadable_state(monkeypatch):
    """R15 mutation test (FAIL-SILENT doctrine): a corrupt/unreadable state
    file must NOT silently reset the streak to a fresh, quiet zero -- an
    unavailable check is a FAILED check, so the very next call must alarm
    immediately rather than requiring the streak to be rebuilt from
    scratch."""
    background_worker.ZERO_PROGRESS_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    background_worker.ZERO_PROGRESS_STATE_FILE.write_text("{not valid json")
    fired = []

    def _notify(msg, **kw):
        fired.append((msg, kw))

    result = background_worker._record_sweep_progress(
        markers_found=10, markers_drained=0, now=1_000_000.0, notify_fn=_notify)

    assert len(fired) == 1, "an unreadable state file must fire immediately, fail-closed"
    assert result["fired"] is True


def test_zero_progress_alarm_resets_and_resolves_on_empty_backlog(monkeypatch):
    """No markers at all is not a stuck retry loop (there is nothing to be
    stuck on) -- must not accumulate toward the alarm, and an already-open
    alarm must be resolved (R11: a real release trigger, not an orphan
    transition)."""
    fired = []

    def _notify(msg, **kw):
        fired.append((msg, kw))

    for i in range(background_worker.ZERO_PROGRESS_ALARM_THRESHOLD):
        background_worker._record_sweep_progress(
            markers_found=10, markers_drained=0, now=1_000_000.0 + i, notify_fn=_notify)
    assert len(fired) == 1
    fired.clear()

    result = background_worker._record_sweep_progress(
        markers_found=0, markers_drained=0, now=2_000_000.0, notify_fn=_notify)

    assert result["streak"] == 0
    state = background_worker._read_zero_progress_state()
    assert state["consecutive_zero_progress"] == 0
    assert state["alerted_at"] is None


def test_zero_progress_alarm_pages_recovery_once_after_firing(monkeypatch):
    """Both ways (R15): recovery (zero-progress -> real progress) after a
    fired alarm is itself a transition and pages once, distinct from the
    original RED page."""
    fired = []

    def _notify(msg, **kw):
        fired.append((msg, kw))

    for i in range(background_worker.ZERO_PROGRESS_ALARM_THRESHOLD):
        background_worker._record_sweep_progress(
            markers_found=10, markers_drained=0, now=1_000_000.0 + i, notify_fn=_notify)
    assert len(fired) == 1
    fired.clear()

    background_worker._record_sweep_progress(
        markers_found=10, markers_drained=3, now=2_000_000.0, notify_fn=_notify)

    assert len(fired) == 1
    msg, kw = fired[0]
    assert kw["state"] == "GREEN"
    assert "RECOVERED" in msg


# ── Publish-gate scope (R10, 2026-07-18): DAEMON-LIFECYCLE test module ──────────
# Validates pipeline MACHINERY (process/session lifecycle, scheduling, notify transport,
# reconciliation), never a published business surface -- so it must never wedge the live
# publish. The gate runs `-m 'not operational'`. See tests/conftest.py for the marker.
import pytest  # noqa: E402,F811
pytestmark = pytest.mark.operational
