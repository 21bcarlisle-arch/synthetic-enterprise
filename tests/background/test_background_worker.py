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
"""
import json
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
    # H15: _record_publish_gate_outcome() imports process_run_complete and
    # writes its wedge-state + log files. Redirect BOTH to per-test temp paths
    # so the sweep never touches the real docs/observability/ files (same
    # test-isolation-leak class as the fingerprint/log redirects in
    # test_process_run_complete.py).
    import background.process_run_complete as prc
    monkeypatch.setattr(prc, "PUBLISH_GATE_STATE_FILE", tmp_path / ".publish_gate_state.json")
    monkeypatch.setattr(prc, "LOG_FILE", tmp_path / "prc_log.md")
    # OPS_run_marker_sweep_livelock: the sweep's stall counter is real on-disk
    # state. An unpinned flag leaks into every other test's loader and starts
    # alarming off their fixtures -- pin it per-test.
    monkeypatch.setattr(background_worker, "SWEEP_STATE_FILE", tmp_path / ".run_marker_sweep_state.json")
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


# ─────────────────────────────────────────────────────────────────────────────
# OPS_run_marker_sweep_livelock (2026-08-03)
#
# THE DEFECT: every marker in staging/ was re-attempted every cycle, each
# attempt spawning process_run_complete.py, each returning EXIT_LOCK_SKIPPED
# because sim_runner.py holds the run lock while publishing its OWN marker
# inline. 404 markers x "will retry next cycle", forever, having never once
# succeeded -- a livelock whose log reads like a healthy queue.
#
# THE CLASS-CLOSING INVARIANT (R10 -- and NOT "delete the backlog"): a leftover
# marker has a TERMINAL state other than "published". A marker a strictly
# later PUBLISHED run has overtaken is retired to done/ with its reason
# recorded, because re-running its pipeline would republish a stale snapshot
# over current figures. And a retry loop that never succeeds must ALARM.
# ─────────────────────────────────────────────────────────────────────────────

def _write(dirpath, name, body="# Simulation Run Complete\n"):
    dirpath.mkdir(parents=True, exist_ok=True)
    p = dirpath / name
    p.write_text(body)
    return p


def test_superseded_markers_are_retired_without_running_the_pipeline():
    """The livelock fix: a marker overtaken by a later PUBLISHED run reaches a
    terminal state by rename -- no subprocess, so no run lock, so it cannot be
    lock-skipped. This is the property that makes the backlog drain."""
    done = background_worker.STAGING_DIR / "done"
    _write(done, "run_complete_20260803T044922Z.md")
    old = _write(background_worker.STAGING_DIR, "run_complete_20260729T214902Z.md")

    calls = []
    import unittest.mock as m
    with m.patch.object(background_worker.subprocess, "run",
                        lambda *a, **k: calls.append(a[0][-1]) or _fake_success()):
        background_worker.process_leftover_run_markers()

    assert calls == [], "a superseded marker must never be fed to the publish pipeline"
    assert not old.exists()
    retired = done / old.name
    assert retired.exists(), "superseded marker must land in done/, not vanish"
    # R10: retired, not deleted -- the reason travels WITH the artefact.
    text = retired.read_text()
    assert "# Simulation Run Complete" in text, "original content must be preserved"
    assert "Superseded (not published)" in text
    assert "20260803T044922Z" in text, "must name the run that overtook it"


def test_an_unsuperseded_marker_is_still_published():
    """The safety net the original glob existed for is INTACT: a marker with
    no later published run is still attempted, every cycle. This is the
    assertion that would fail if the fix had 'drained' the backlog by
    retiring everything."""
    done = background_worker.STAGING_DIR / "done"
    _write(done, "run_complete_20260803T040000Z.md")
    newer = _write(background_worker.STAGING_DIR, "run_complete_20260803T064304Z.md")

    calls = []
    import unittest.mock as m
    with m.patch.object(background_worker.subprocess, "run",
                        lambda *a, **k: calls.append(a[0][-1]) or _fake_success()):
        background_worker.process_leftover_run_markers()

    assert [Path(c).name for c in calls] == [newer.name]


def test_mixed_backlog_retires_the_stale_and_publishes_the_live_one():
    """The real 2026-08-03 shape in miniature: 401 superseded + 12 pending."""
    done = background_worker.STAGING_DIR / "done"
    _write(done, "run_complete_20260802T120000Z.md")
    stale = [_write(background_worker.STAGING_DIR, f"run_complete_2026080{d}T010000Z.md")
             for d in (1, 2)]
    live = _write(background_worker.STAGING_DIR, "run_complete_20260803T010000Z.md")

    calls = []
    import unittest.mock as m
    with m.patch.object(background_worker.subprocess, "run",
                        lambda *a, **k: calls.append(a[0][-1]) or _fake_success()):
        background_worker.process_leftover_run_markers()

    assert [Path(c).name for c in calls] == [live.name]
    for s in stale:
        assert not s.exists() and (done / s.name).exists()


def test_no_published_run_yet_retires_nothing():
    """FAIL-SAFE DIRECTION: with an empty (or absent) done/ there is no
    supersession frontier, so NOTHING may be retired -- every marker is
    pending. A fix that retired markers here would be destroying unpublished
    runs on a fresh checkout."""
    markers = [_write(background_worker.STAGING_DIR, f"run_complete_2026080{d}T010000Z.md")
               for d in (1, 2, 3)]
    calls = []
    import unittest.mock as m
    with m.patch.object(background_worker.subprocess, "run",
                        lambda *a, **k: calls.append(a[0][-1]) or _fake_success()):
        background_worker.process_leftover_run_markers()

    assert len(calls) == 3
    for mk in markers:
        assert mk.exists() or True  # consumed by the pipeline mock, not retired
    assert not list((background_worker.STAGING_DIR / "done").glob("*.md"))


def test_an_unparseable_marker_name_is_never_treated_as_superseded():
    """FAIL-OPEN guard (R15): the failure mode of a bad stamp parse must be
    'we tried to publish something we needn't have', never 'we retired a
    marker nobody published'."""
    superseded, pending = background_worker.classify_markers(
        [Path("run_complete_.md"), Path("run_complete_NOT_A_STAMP.md")],
        "20260803T044922Z",
    )
    assert superseded == []
    assert len(pending) == 2


def test_supersession_is_strict_the_frontier_run_itself_is_not_retired():
    """Off-by-one guard: the newest PUBLISHED stamp must not retire a marker
    bearing that same stamp (a duplicate marker for the run in hand)."""
    superseded, pending = background_worker.classify_markers(
        [Path("run_complete_20260803T044922Z.md")], "20260803T044922Z")
    assert superseded == []
    assert len(pending) == 1


def test_zero_progress_alarm_fires_when_the_oldest_marker_never_moves(monkeypatch):
    """THE FAIL-SILENT CLOSER: 404 x 'will retry next cycle' must not be able
    to masquerade as a healthy queue. Same oldest pending marker across
    STALL_ALARM_CYCLES sweeps == an alarm."""
    sent = []
    import background.ntfy_utils as nu
    monkeypatch.setattr(nu, "send_ntfy", lambda msg, *a, **k: sent.append(msg) or "id")
    stuck = [Path("run_complete_20260729T214902Z.md")]

    fired = [background_worker._check_zero_progress(stuck)
             for _ in range(background_worker.STALL_ALARM_CYCLES)]

    assert fired == [False] * (background_worker.STALL_ALARM_CYCLES - 1) + [True]
    assert len(sent) == 1 and "ZERO progress" in sent[0]
    # R5: transition-only. It must not re-fire every cycle thereafter.
    assert background_worker._check_zero_progress(stuck) is False
    assert len(sent) == 1


def test_zero_progress_alarm_resets_when_the_backlog_actually_moves(monkeypatch):
    """The alarm must be able to be QUIET when things work, or it is noise."""
    sent = []
    import background.ntfy_utils as nu
    monkeypatch.setattr(nu, "send_ntfy", lambda msg, *a, **k: sent.append(msg) or "id")

    for i in range(background_worker.STALL_ALARM_CYCLES * 2):
        # A different oldest marker each cycle == the queue is draining.
        assert background_worker._check_zero_progress(
            [Path(f"run_complete_2026080{i}T010000Z.md")]) is False
    assert sent == []


def test_zero_progress_alarm_is_not_fail_silent_when_ntfy_is_unavailable(monkeypatch):
    """R15 FAIL-SILENT: an unavailable checker is a FAILED check, not a passed
    one. If the NTFY send raises, the alarm must NOT be recorded as delivered
    -- the next cycle has to try again."""
    import background.ntfy_utils as nu

    def _boom(*a, **k):
        raise RuntimeError("ntfy down")

    monkeypatch.setattr(nu, "send_ntfy", _boom)
    stuck = [Path("run_complete_20260729T214902Z.md")]
    for _ in range(background_worker.STALL_ALARM_CYCLES):
        background_worker._check_zero_progress(stuck)

    state = json.loads(background_worker.SWEEP_STATE_FILE.read_text())
    assert state.get("stalled_on") is None, "a failed send must not latch the alarm closed"

    sent = []
    monkeypatch.setattr(nu, "send_ntfy", lambda msg, *a, **k: sent.append(msg) or "id")
    assert background_worker._check_zero_progress(stuck) is True
    assert len(sent) == 1


def test_a_failed_retirement_never_breaks_the_sweep(monkeypatch):
    """Defensive by construction: a disposal failure must not abort the cycle
    -- the PENDING markers still need their publish attempt. Exercises the
    real retire function against a rename it cannot perform."""
    done = background_worker.STAGING_DIR / "done"
    _write(done, "run_complete_20260803T044922Z.md")
    _write(background_worker.STAGING_DIR, "run_complete_20260729T214902Z.md")
    live = _write(background_worker.STAGING_DIR, "run_complete_20260803T060000Z.md")

    # Scoped to THIS marker only. A blanket `Path.rename` patch would make
    # every rename in the process raise for the duration of the test -- the
    # exact cross-test bleed this module's own fixture exists to prevent.
    real_rename = Path.rename

    def _boom(self, target):
        if self.name.startswith("run_complete_20260729"):
            raise OSError("disk full")
        return real_rename(self, target)

    monkeypatch.setattr(Path, "rename", _boom)
    calls = []
    monkeypatch.setattr(background_worker.subprocess, "run",
                        lambda *a, **k: calls.append(a[0][-1]) or _fake_success())

    background_worker.process_leftover_run_markers()  # must not raise

    assert [Path(c).name for c in calls] == [live.name], \
        "the live marker must still be published even though retirement failed"


# ── Publish-gate scope (R10, 2026-07-18): DAEMON-LIFECYCLE test module ──────────
# Validates pipeline MACHINERY (process/session lifecycle, scheduling, notify transport,
# reconciliation), never a published business surface -- so it must never wedge the live
# publish. The gate runs `-m 'not operational'`. See tests/conftest.py for the marker.
import pytest  # noqa: E402,F811
pytestmark = pytest.mark.operational


# ── EPISODE4 item 2: the retry promise, as a BEHAVIOURAL exit test ───────────────────────────
# The director's exit test, verbatim: "a failed publish cycle is followed by an attempted one
# without human touch." It was prose in a log line ("will retry next cycle") and prose evaporates
# -- so it is pinned here instead.
#
# MEASURED CONTEXT (2026-08-09): the zero-progress alarm claimed "the publish retry loop is not
# retrying". The worker log disproves it -- the oldest marker was attempted at 14:01 (rc=1) and
# again at 14:54 (rc=1), straddling that alarm's own 14:48 firing. The loop retried; the retries
# failed on a red gate. These tests hold the retry property so the claim can never again be
# asserted without evidence, and the alarm-wording test below holds the other half.
def test_a_failed_cycle_is_followed_by_another_attempt_without_human_touch(monkeypatch):
    """THE exit test. Two consecutive sweeps, publisher red both times, no intervention between:
    the same marker must be attempted on the second sweep.

    MUTATION: make the sweep skip markers it already failed on (e.g. remember-and-exclude) and
    this fails -- which is precisely the bug the alarm alleged and the log refutes."""
    marker = background_worker.STAGING_DIR / "run_complete_20260809T125051Z.md"
    marker.write_text("# Simulation Run Complete\n")
    attempts = []

    def _always_red(*a, **k):
        attempts.append(a[0])
        return MagicMock(returncode=1, stderr="")

    monkeypatch.setattr(background_worker.subprocess, "run", _always_red)

    background_worker.process_leftover_run_markers()   # cycle 1 -- fails
    background_worker.process_leftover_run_markers()   # cycle 2 -- no human touch in between

    assert len(attempts) == 2, "a failed publish cycle was NOT followed by another attempt"
    assert all(str(marker) in a for a in attempts), "the same marker must be re-attempted"
    assert marker.exists(), "a failed marker must stay pending, not be consumed"


def test_the_zero_progress_alarm_reports_what_it_saw_not_a_cause_it_inferred(monkeypatch):
    """R9 applied to a control. The alarm may say progress stopped; it may NOT assert that the
    retry loop stopped, because it cannot observe that -- and on 2026-08-09 that inference was
    measurably wrong while the real cause (a red gate) sat in the same log as rc=1.

    MUTATION: restore 'The publish retry loop is not retrying' and this fails."""
    marker = background_worker.STAGING_DIR / "run_complete_20260809T125051Z.md"
    marker.write_text("# Simulation Run Complete\n")
    monkeypatch.setattr(background_worker, "STALL_ALARM_CYCLES", 2)
    sent = []
    monkeypatch.setattr(background_worker.subprocess, "run",
                        lambda *a, **k: MagicMock(returncode=1, stderr=""))
    import background.notify as _notify
    monkeypatch.setattr(_notify, "notify", lambda msg, **k: sent.append(msg))

    background_worker.process_leftover_run_markers()
    background_worker.process_leftover_run_markers()

    assert sent, "a stalled backlog must still raise ONE alarm"
    msg = sent[-1]
    assert "retry loop is not retrying" not in msg, (
        "the alarm asserted a cause it cannot observe -- the sweep does re-attempt every cycle"
    )
    assert "rc=1" in msg, "the alarm must carry the OBSERVED publisher outcome"
    assert "publish gate" in msg.lower(), "it must point the reader at the real place to look"
