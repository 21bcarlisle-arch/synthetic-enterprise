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
    # Same class again (2026-08-11): the outcome router now reads `.last_tested_hash` to tell a
    # real gate pass from a publisher that merely exited 0, so that file is a surface this sweep
    # touches and must be per-test. Left on the real path it would decide these tests off
    # whatever the live pipeline last stamped.
    monkeypatch.setattr(prc, "LAST_TESTED_HASH_FILE", tmp_path / ".last_tested_hash")
    # OPS_run_marker_sweep_livelock: the sweep's stall counter is real on-disk
    # state. An unpinned flag leaks into every other test's loader and starts
    # alarming off their fixtures -- pin it per-test.
    monkeypatch.setattr(background_worker, "SWEEP_STATE_FILE", tmp_path / ".run_marker_sweep_state.json")
    yield


#: RECORD ONLY THE PUBLISHER LAUNCHES (2026-08-26).
#:
#: These tests patch `background_worker.subprocess.run` -- the MODULE's `run`, so every
#: subprocess ANY module makes inside `process_leftover_run_markers` lands in the recorder, not
#: just the publisher launch the test is about. That was harmless while the failure path made no
#: subprocess calls of its own. It is not harmless now: on a non-zero return the worker calls
#: `process_run_complete.record_publish_gate_outcome` -> `wedge_suspects` -> `blame_commits`,
#: which shells `git log -- <file>` for each test named in the LIVE
#: `.last_gate_blocking_tests.json`. So the call count became a function of whether the machine
#: currently has a wedged publish -- these two tests were green all week and went red at 07:06
#: today because a real refusal had put a real file in that state.
#:
#: A control that fails exactly when the thing it watches is in the state it exists to describe
#: is the shape this whole morning was about. The blame lookup is CORRECT behaviour and the test
#: must not forbid it; what the test means is "which markers did the publisher get", so it
#: records that and nothing else. Keyed on the processor's own filename rather than on argument
#: position, because position is what made this fragile in the first place.
_PUBLISHER = "process_run_complete.py"


def _is_publisher_launch(cmd) -> bool:
    return any(_PUBLISHER in str(part) for part in (cmd or []))


def _record_publisher(calls):
    """A `subprocess.run` stand-in that appends only the publisher's marker argument."""
    def _run(*a, **k):
        cmd = a[0] if a else k.get("args")
        if _is_publisher_launch(cmd):
            calls.append(cmd[-1])
        return None
    return _run


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
    glob is ever narrowed (e.g. skip markers older than N), a lock-skipped
    marker becomes permanently orphaned with nothing left to rescue it.

    THE PROPERTY IS DISPOSAL, NOT PUBLICATION (restated 2026-08-14, OPS3). This used to assert
    that all three were handed to the PUBLISHER, which conflated the guard with the FIFO order
    that happened to implement it. Under drain-supersession the newest publishes and the rest
    are retired naming it -- every marker is still collected and still reaches a terminal state
    in the same cycle, which is what 'never orphaned' actually means. Asserting the publisher
    call count instead would have frozen the very ordering that made the backlog ungrowable."""
    names = [f"run_complete_2026071{i}T000000Z.md" for i in range(1, 4)]
    for name in names:
        (background_worker.STAGING_DIR / name).write_text("# Simulation Run Complete\n")
    # A non-marker file must never be swept up by the same glob.
    (background_worker.STAGING_DIR / "from_rich_20260713.md").write_text("not a run marker")

    calls = []
    monkeypatch.setattr(background_worker.subprocess, "run", lambda *a, **k: calls.append(a[0]) or _fake_success())

    background_worker.process_leftover_run_markers()

    published = {Path(c[-1]).name for c in calls}
    retired = {p.name for p in (background_worker.STAGING_DIR / "done").glob("run_complete_*.md")}
    assert published | retired == set(names), (
        "every leftover marker must be DISPOSED this cycle -- published or retired. "
        f"published={published} retired={retired}"
    )
    assert not retired & published, "a marker is published or retired, never both"
    assert (background_worker.STAGING_DIR / "from_rich_20260713.md").exists(), \
        "a non-marker file must never be swept up by the marker glob"


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
    """H15 wiring: an rc==0 outcome CLEARS the wedge state (re-arm).

    The gate PASS for this marker's commit is recorded explicitly: since 2026-08-11 rc=0 alone
    is not evidence of a healthy gate (a publisher that publishes nothing also exits 0), so the
    healthy path this test names has to state both halves."""
    marker = background_worker.STAGING_DIR / "run_complete_20260714T010000Z.md"
    marker.write_text("# Simulation Run Complete\nGit: cafef00\n")
    monkeypatch.setattr(background_worker.subprocess, "run",
                        lambda *a, **k: MagicMock(returncode=0))

    cleared = []
    import background.process_run_complete as prc
    prc.LAST_TESTED_HASH_FILE.write_text("cafef00")
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
    marker.write_text("# Simulation Run Complete\nGit: beefbee\n")
    prc.LAST_TESTED_HASH_FILE.write_text("beefbee")  # the suite passed for this commit
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
    """Order is deterministic (sorted on the fixed-width UTC stamp), and it is NEWEST-FIRST.

    This asserted oldest-first until 2026-08-14 on a stated 'fairness' rationale. Fairness is
    the wrong frame for this queue: the markers are not competing jobs, they are successive
    snapshots of ONE thing, so serving them in arrival order publishes the stalest and calls it
    fair. Determinism is the property worth locking in; the direction now follows the freshness
    argument in process_leftover_run_markers()."""
    names = ["run_complete_20260713T030000Z.md", "run_complete_20260713T010000Z.md", "run_complete_20260713T020000Z.md"]
    for name in names:
        (background_worker.STAGING_DIR / name).write_text("# Simulation Run Complete\n")

    calls = []
    monkeypatch.setattr(background_worker.subprocess, "run",
                        lambda *a, **k: _record_publisher(calls)(*a, **k) or MagicMock(returncode=1, stderr=""))

    background_worker.process_leftover_run_markers()

    processed_order = [Path(c).name for c in calls]
    # NARROWED 2026-09-04 to what this test's own docstring claims: DETERMINISM AND DIRECTION.
    # It used to assert all three were handed to the publisher, which pinned something else
    # entirely -- the sweep WALKING BACKWARDS through the queue after a failure, publishing
    # progressively older snapshots at a full expensive cycle each. Observed live at 10:35 that
    # day: the frontier refused and the sweep immediately started an older marker. The success
    # branch has always returned after the first marker; the failure branch now does too, so the
    # only order this sweep can express is WHICH ONE IT TRIES FIRST -- and that is the direction
    # the docstring argues for.
    # MUTATION: drop the `reversed()` and the oldest is attempted instead. FIRES.
    assert processed_order == [sorted(names)[-1]], (
        "the sweep must attempt the NEWEST marker, and only that one: every older marker is a "
        "staler snapshot of the same thing"
    )


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
                        lambda *a, **k: _record_publisher(calls)(*a, **k) or _fake_success()):
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
                        lambda *a, **k: _record_publisher(calls)(*a, **k) or _fake_success()):
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
                        lambda *a, **k: _record_publisher(calls)(*a, **k) or _fake_success()):
        background_worker.process_leftover_run_markers()

    assert [Path(c).name for c in calls] == [live.name]
    for s in stale:
        assert not s.exists() and (done / s.name).exists()


def test_no_published_run_yet_retires_nothing():
    """FAIL-SAFE DIRECTION: with an empty (or absent) done/ there is no supersession frontier,
    so the top-of-sweep retirement may retire NOTHING -- a fix that retired markers here would
    be destroying unpublished runs on a fresh checkout.

    The publisher is held RED here deliberately (2026-08-14, OPS3): this test is about the
    frontier read from done/, and a green publisher would additionally trigger
    drain-supersession, which is a different mechanism with its own evidence (a run that
    actually published) and its own tests below. Keeping them separate is what lets this one
    still fail for its own reason."""
    markers = [_write(background_worker.STAGING_DIR, f"run_complete_2026080{d}T010000Z.md")
               for d in (1, 2, 3)]
    calls = []
    import unittest.mock as m
    with m.patch.object(background_worker.subprocess, "run",
                        lambda *a, **k: _record_publisher(calls)(*a, **k) or MagicMock(returncode=1, stderr="")):
        background_worker.process_leftover_run_markers()

    # NARROWED 2026-09-04 to this test's own stated property (RETIRES NOTHING). `len(calls) == 3`
    # asserted the backwards walk, which was never this test's subject and is now removed -- the
    # markers all still stay pending, which is the fail-safe direction it exists to pin.
    assert len(calls) == 1, "the sweep attempts the frontier only"
    for mk in markers:
        assert mk.exists(), "no frontier and no publish means nothing may be retired"
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
    """The alarm must be able to be QUIET when things work, or it is noise.

    PW4 CHANGED WHAT COUNTS AS "MOVES" HERE, and the old version of this test pinned the defect.
    It drove a different oldest marker each cycle and asserted silence, on the reasoning that a
    changing oldest name means the queue is draining. It does not: retiring a superseded marker
    is a rename that needs no run lock and cannot be lock-skipped, so the name churns whether or
    not the publish path works at all -- which is exactly how a running stall reset its own
    counter. The intent of the test is preserved; the evidence is now a publish (rc == 0),
    which is what the alarm's claim is actually about."""
    sent = []
    import background.ntfy_utils as nu
    monkeypatch.setattr(nu, "send_ntfy", lambda msg, *a, **k: sent.append(msg) or "id")

    for i in range(background_worker.STALL_ALARM_CYCLES * 2):
        assert background_worker._check_zero_progress(
            [Path(f"run_complete_2026080{i}T010000Z.md")]) is False
        background_worker._record_marker_published(f"run_complete_2026080{i}T010000Z.md")
    assert sent == []


def test_a_churning_oldest_name_alone_does_not_quieten_the_alarm(monkeypatch):
    """The other half of the pair above (PW4): the SAME churn, WITHOUT any publish, must still
    reach the alarm. Without this, the test above could be satisfied by a guard that simply never
    fires, and the pair would prove nothing."""
    sent = []
    import background.ntfy_utils as nu
    monkeypatch.setattr(nu, "send_ntfy", lambda msg, *a, **k: sent.append(msg) or "id")

    fired = [background_worker._check_zero_progress(
             [Path(f"run_complete_2026080{i}T010000Z.md")])
             for i in range(background_worker.STALL_ALARM_CYCLES * 2)]
    assert any(fired), "a churning oldest name silenced a stall in which nothing published"
    assert len(sent) == 1, "R5: one page per open episode"


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
                        lambda *a, **k: _record_publisher(calls)(*a, **k) or _fake_success())

    background_worker.process_leftover_run_markers()  # must not raise

    assert [Path(c).name for c in calls] == [live.name], \
        "the live marker must still be published even though retirement failed"


# ── DRAIN-SUPERSESSION (OPS3, 2026-08-14) ──────────────────────────────────────
# The sweep walked the queue OLDEST-FIRST while supersession was only ever computed against
# what had ALREADY published. Measured 2026-08-14 19:22Z: 102 pending, the publisher chewing
# 20260814T090117Z while 20260814T183636Z sat unpublished -- publishing figures 9.5h stale over
# current ones, the clock-rewind classify_markers' own docstring forbids.

def _queue(names):
    for n in names:
        (background_worker.STAGING_DIR / n).write_text("# Simulation Run Complete\n")


BACKLOG = [
    "run_complete_20260814T090117Z.md",
    "run_complete_20260814T120000Z.md",
    "run_complete_20260814T183636Z.md",
]


def test_the_newest_marker_is_the_one_published(monkeypatch):
    """THE DEFECT: with a backlog, the sweep published the marker at the BACK of the queue.

    MUTATION: drop the `reversed()` in process_leftover_run_markers and this fails -- the
    publisher is handed the 09:01Z snapshot while the 18:36Z one waits."""
    _queue(BACKLOG)
    published = []

    def _run(*a, **k):
        argv = a[0]
        if any("process_run_complete" in str(x) for x in argv):
            published.append(Path(argv[-1]).name)
        return MagicMock(returncode=0, stderr="")

    monkeypatch.setattr(background_worker.subprocess, "run", _run)
    background_worker.process_leftover_run_markers()

    assert published == ["run_complete_20260814T183636Z.md"], (
        "the sweep must publish the NEWEST snapshot and exactly once -- publishing an older "
        f"one winds the published clock backwards. Got: {published}"
    )


def test_the_older_markers_are_retired_naming_the_run_that_superseded_them(monkeypatch):
    """OPS3 exit criterion 2: drain-SUPERSEDED, not bulk-archived. Each older marker keeps its
    content and gains a note naming the run that overtook it (R10: the backlog defect may not
    be closed by deleting the backlog).

    MUTATION: replace the retire_superseded_marker() call with `m.unlink()` and this fails on
    both the archive location and the named superseding run."""
    _queue(BACKLOG)
    monkeypatch.setattr(background_worker.subprocess, "run",
                        lambda *a, **k: MagicMock(returncode=0, stderr=""))

    background_worker.process_leftover_run_markers()

    done = background_worker.STAGING_DIR / "done"
    for name in BACKLOG[:-1]:
        retired = done / name
        assert retired.exists(), f"{name} must be RETIRED to done/, not deleted and not left"
        body = retired.read_text()
        assert "# Simulation Run Complete" in body, "the marker's own content must survive"
        assert "20260814T183636Z" in body, (
            f"{name}'s retirement note must NAME the run that superseded it"
        )
    # The published marker is archived by process_run_complete itself, which is mocked here, so
    # it legitimately remains. What must be gone is the BACKLOG BEHIND it -- that is this
    # sweep's own work and the thing that could not drain before.
    left = sorted(p.name for p in background_worker.STAGING_DIR.glob("run_complete_*.md"))
    assert left == [BACKLOG[-1]], (
        f"every marker behind the published one must have drained in the one cycle, left={left}"
    )


def test_a_red_gate_retires_nothing_and_keeps_the_whole_backlog(monkeypatch):
    """THE FAIL-SAFE DIRECTION (R15). Retirement is justified by a marker having PUBLISHED. If
    the publish fails, nothing was overtaken, so nothing may be retired -- otherwise a red gate
    would silently eat the queue and the wedge would look like progress.

    MUTATION: retire the remainder unconditionally (outside the rc == 0 branch) and this fails."""
    _queue(BACKLOG)
    monkeypatch.setattr(background_worker.subprocess, "run",
                        lambda *a, **k: MagicMock(returncode=1, stderr=""))

    background_worker.process_leftover_run_markers()

    assert not (background_worker.STAGING_DIR / "done").exists() or \
        not list((background_worker.STAGING_DIR / "done").glob("run_complete_*.md")), \
        "a FAILED publish must retire nothing"
    still_pending = sorted(p.name for p in
                           background_worker.STAGING_DIR.glob("run_complete_*.md"))
    assert still_pending == sorted(BACKLOG), \
        "every marker must stay pending when the gate is red"


def test_a_lock_skipped_newest_does_not_retire_the_queue_behind_it(monkeypatch):
    """EXIT_LOCK_SKIPPED is 'not attempted', not 'published'. A concurrent publisher holding the
    run lock must not cause this sweep to retire the backlog on the strength of a marker nobody
    published.

    MUTATION: move the retirement out of the `rc == 0` branch (proven 2026-08-14: it fails here,
    on the red-gate test, and on the no-frontier test)."""
    _queue(BACKLOG)
    monkeypatch.setattr(
        background_worker.subprocess, "run",
        lambda *a, **k: MagicMock(returncode=background_worker.EXIT_LOCK_SKIPPED, stderr=""))

    background_worker.process_leftover_run_markers()

    assert sorted(p.name for p in background_worker.STAGING_DIR.glob("run_complete_*.md")) \
        == sorted(BACKLOG), "a lock-skipped marker retires nothing -- it was never attempted"


@pytest.mark.parametrize("rc", [-9, 2, 137])
def test_a_crashed_publisher_is_not_a_publish_and_retires_nothing(monkeypatch, rc):
    """FAIL-OPEN guard found by a mutation that DIDN'T reproduce (R15, 2026-08-14).

    The intended mutation for the test above -- 'treat any non-1 return code as success' -- left
    the suite green, because EXIT_LOCK_SKIPPED and EXIT_NOTHING_PUBLISHED are matched by earlier
    branches and rc=1 was excluded by the mutation itself. Nothing was covering the codes that
    actually reach the final branch by another route: an OOM SIGKILL (-9), a Python traceback
    (2), a shell-reported kill (137). Those are the publisher DYING, and a death must never
    drain the queue -- that would be the wedge eating its own evidence while looking like
    progress, the exact fail-silent shape this sweep already paid for twice.

    MUTATION: widen the branch to `result.returncode != 1` and this fails on every parameter."""
    _queue(BACKLOG)
    monkeypatch.setattr(background_worker.subprocess, "run",
                        lambda *a, **k: MagicMock(returncode=rc, stderr=""))

    background_worker.process_leftover_run_markers()

    assert sorted(p.name for p in background_worker.STAGING_DIR.glob("run_complete_*.md")) \
        == sorted(BACKLOG), (
        f"a publisher that died (rc={rc}) published nothing, so nothing may be retired"
    )


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
        # `background_worker.subprocess` IS the stdlib module object, so this patch is global:
        # it also catches read-only git calls the publish-gate recorder makes downstream (the
        # H42 suspect blame trail). Only PUBLISHER invocations are attempts at this marker.
        argv = a[0]
        if any("process_run_complete" in str(x) for x in argv):
            attempts.append(argv)
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


def test_a_failed_frontier_ends_the_sweep_instead_of_publishing_ever_older_snapshots(monkeypatch):
    """THE DEFECT THIS OWNS, observed live 2026-09-04 10:35.

    `run_complete_20260904T085811Z` refused (commit_refused) after a 71-minute cycle, and the very
    next thing the sweep started was `...T084511Z` -- an OLDER marker, at another full expensive
    cycle, to publish a staler snapshot. The success branch ends the sweep precisely to stop that
    ("publishing an older snapshot AFTER a newer one has published is the clock-rewind this
    ordering exists to stop"); the failure branch walked on. The queue grew 15 -> 17 while every
    log line said "will retry next cycle".

    RETENTION IS NOT THE FIX AND MUST NOT BE TRADED FOR IT. The first draft retired the queue
    behind the failed frontier and three existing controls caught it -- a red gate that ate its
    own backlog would leave the wedge detector reading an empty queue as health. Every marker
    stays pending here; only the walk stops.

    MUTATION: remove the `return` from the frontier-failure branch and this fires, naming the
    older markers the sweep went on to attempt.
    """
    names = ["run_complete_20260904T084511Z.md",
             "run_complete_20260904T085811Z.md",
             "run_complete_20260904T091113Z.md"]
    for name in names:
        (background_worker.STAGING_DIR / name).write_text("# Simulation Run Complete\n")

    calls = []
    monkeypatch.setattr(background_worker.subprocess, "run",
                        lambda *a, **k: _record_publisher(calls)(*a, **k)
                        or MagicMock(returncode=1, stderr="", stdout="commit_refused"))

    background_worker.process_leftover_run_markers()

    attempted = [Path(c).name for c in calls]
    assert attempted == ["run_complete_20260904T091113Z.md"], (
        "the sweep walked backwards after the frontier failed and attempted {} -- each of those "
        "is a full publish cycle spent on a staler snapshot than the one that just refused"
        .format(attempted[1:])
    )
    # ...and the fail-safe the first draft broke: the backlog is the evidence the publish is
    # stuck, so it must survive the failure intact.
    assert sorted(p.name for p in background_worker.STAGING_DIR.glob("run_complete_*.md")) \
        == sorted(names), "a failed frontier retired markers -- a red gate must not eat its queue"
