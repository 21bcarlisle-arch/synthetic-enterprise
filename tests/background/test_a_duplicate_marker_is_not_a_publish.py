"""A duplicate (already-archived) marker publishes NOTHING -- it must not read as a publish.

THE DEFECT THIS PINS (`WORKER_FINDING_A_DUPLICATE_MARKER_DISARMS_THE_WEDGE_ALARM_2026-08-10`,
BLOCKING, class `publish_gate_and_wedge`). `process_run_complete._process()` returns 0 when the
marker it was handed has already been archived by a concurrent publisher -- an outcome
indistinguishable, to every caller, from a run that actually opened the gate and published. It is
the exact sibling of the lock-skip fail-open closed on 2026-07-29, which was given its own exit
code (EXIT_LOCK_SKIPPED) and left this neighbouring door returning 0
(cf. `feedback_audit_sibling_half_for_hardened_class`).

WHAT IS STILL LIVE, AND WHAT IS NOT (observed, R9). The wedge-state half is already defended one
layer downstream: `record_publish_gate_outcome` refuses to clear a wedge on rc=0 without a suite
PASS on record for the marker's own commit, and a duplicate cannot even be parsed for a commit, so
it lands in "unproven". That guard is right, but it defends by ACCIDENT here -- it reads "unknown
hash", not "nothing was published" -- and it is the only thing standing between a duplicate and
`record_publish_gate_success()`.

The half that IS still live, and that these tests fire on: `background_worker`'s sweep logs
"Processed <marker>" for a duplicate and calls `_record_marker_published()`, which is PW4's ONE
evidenced close condition for the zero-progress episode. So a stale marker that some other process
archived milliseconds earlier silently closes the alarm that exists to say the backlog is not
moving -- the same disarming, one door further out.

R15 BOTH WAYS. Each test below states the mutation that reds it. The class-closure test at the
bottom is the R10 half: a NEW no-publish path that returns 0 must fail by name rather than quietly
joining the class.
"""

import ast
import inspect
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import background.background_worker as background_worker  # noqa: E402
import background.process_run_complete as prc  # noqa: E402


@pytest.fixture(autouse=True)
def _isolate(tmp_path, monkeypatch):
    """Every real-disk surface these paths touch is redirected into tmp_path.

    Same test-isolation-leak class the sibling suites guard: the router writes wedge state, the
    publisher and the worker each write a log, and the router now reads `.last_tested_hash`. Left
    on their real paths, the LIVE observability files would decide these assertions.
    """
    staging = tmp_path / "staging"
    staging.mkdir()
    done = tmp_path / "done"
    done.mkdir()
    monkeypatch.setattr(background_worker, "STAGING_DIR", staging)
    monkeypatch.setattr(background_worker, "LOG_FILE", tmp_path / "worker_log.md")
    monkeypatch.setattr(background_worker, "SWEEP_STATE_FILE", tmp_path / ".sweep_state.json")
    monkeypatch.setattr(prc, "LOG_FILE", tmp_path / "prc_log.md")
    monkeypatch.setattr(prc, "DONE_DIR", done)
    monkeypatch.setattr(prc, "PUBLISH_GATE_STATE_FILE", tmp_path / ".publish_gate_state.json")
    monkeypatch.setattr(prc, "LAST_TESTED_HASH_FILE", tmp_path / ".last_tested_hash")
    yield


MARKER_NAME = "run_complete_20260810T221200Z.md"


def _already_archived(tmp_path):
    """A marker that is GONE from staging and present in done/ -- the observed race.

    The sweep globs staging/, and a concurrent publisher archives the marker between the glob and
    the subprocess actually opening it. 43 such lines were logged on 2026-08-10 alone.
    """
    (tmp_path / "done" / MARKER_NAME).write_text("# Simulation Run Complete\n\nGit: abc1234\n")
    return tmp_path / "staging" / MARKER_NAME


# --------------------------------------------------------------------------------------
# 1. The publisher's own exit code
# --------------------------------------------------------------------------------------


def test_a_duplicate_marker_returns_its_own_exit_code(tmp_path):
    """MUTATION: restore `return 0` on the already-archived path and this goes red.

    A duplicate is evidence of exactly as little as a lock-skip: this process published nothing
    and touched nothing. It gets its own third outcome for the same reason the lock-skip did.
    """
    rc = prc._process(str(_already_archived(tmp_path)))

    assert rc == prc.EXIT_NOTHING_PUBLISHED, (
        "an already-archived marker published nothing -- returning {} makes it "
        "indistinguishable from a run that opened the gate, got {}".format(
            prc.EXIT_NOTHING_PUBLISHED, rc))
    assert rc != 0


def test_a_missing_marker_that_is_nowhere_is_still_a_failure(tmp_path):
    """BOTH WAYS: the new code must not swallow the genuine 'marker not found' error.

    MUTATION: return EXIT_NOTHING_PUBLISHED unconditionally on the not-exists branch and this
    reds -- a marker that is in neither staging nor the archive is a real fault, not a no-op.
    """
    assert prc._process(str(tmp_path / "staging" / "run_complete_20990101T000000Z.md")) == 1


# --------------------------------------------------------------------------------------
# 2. The router
# --------------------------------------------------------------------------------------


def test_the_router_records_neither_outcome_for_nothing_published(tmp_path):
    """MUTATION: drop EXIT_NOTHING_PUBLISHED from the router's skip branch and this reds.

    Asserted on the router's OWN declared verdict rather than on the wedge file, deliberately:
    the wedge file cannot tell these two apart today (a duplicate has no parseable commit, so
    rc=0 already lands in "unproven"), and a test that cannot distinguish the fixed code from the
    broken code is not a control.
    """
    marker = _already_archived(tmp_path)

    assert prc.record_publish_gate_outcome(marker, prc.EXIT_NOTHING_PUBLISHED) == "skipped"


def test_nothing_published_leaves_an_accumulated_wedge_streak_untouched(tmp_path):
    """The harm the fail-open does: wiping the streak that was about to raise the alert."""
    prc._write_publish_gate_state({
        "failures": [{"ts": 1_000_000.0, "reason": "rc=1", "rc": 1, "kind": "test_failure",
                      "git_hash": "abc"},
                     {"ts": 1_000_100.0, "reason": "rc=1", "rc": 1, "kind": "test_failure",
                      "git_hash": "abc"}],
        "alerted_at": None,
        "wedge_since": 1_000_000.0,
    })

    prc.record_publish_gate_outcome(_already_archived(tmp_path), prc.EXIT_NOTHING_PUBLISHED)

    after = prc._read_publish_gate_state()
    assert len(after.get("failures", [])) == 2
    assert after.get("wedge_since") == 1_000_000.0


# --------------------------------------------------------------------------------------
# 3. The sweep -- the half that is still live
# --------------------------------------------------------------------------------------


def _duplicate_run(*args, **kwargs):
    return MagicMock(returncode=prc.EXIT_NOTHING_PUBLISHED, stderr="")


def test_the_worker_mirror_constant_cannot_drift(tmp_path):
    """The worker duplicates the code as a literal to avoid an import-time dependency on the
    publish stack; the same pin the lock-skip mirror already carries keeps the copy honest."""
    assert background_worker.EXIT_NOTHING_PUBLISHED == prc.EXIT_NOTHING_PUBLISHED


def test_a_duplicate_does_not_close_the_zero_progress_episode(monkeypatch, tmp_path):
    """The branch contract, stated at the sweep's own layer.

    MUTATION, stated exactly (this test is weaker than it looks and the docstring must say so):
    it reds if the duplicate branch is made to call `_record_marker_published`. It does NOT red
    if that branch is deleted outright -- rc=76 then falls through to the failure branch, which
    is wrong about the log but still does not close the episode. The cross-process property (the
    publisher's rc actually reaching this branch) is not testable here at all, because this
    sweep's subprocess is a mock; it is pinned end-to-end below.
    """
    (background_worker.STAGING_DIR / MARKER_NAME).write_text("# Simulation Run Complete\n")
    monkeypatch.setattr(background_worker.subprocess, "run", _duplicate_run)
    closed = []
    monkeypatch.setattr(background_worker, "_record_marker_published", closed.append)

    background_worker.process_leftover_run_markers()

    assert closed == [], (
        "a duplicate marker published nothing, so it cannot be the evidence that closes the "
        "zero-progress episode -- got {}".format(closed))


def test_a_duplicate_is_not_logged_as_processed(monkeypatch, tmp_path):
    """The worker log is the first thing read when diagnosing a backlog; 'Processed X' for a
    marker this sweep never published is a false claim in the diagnostic record."""
    (background_worker.STAGING_DIR / MARKER_NAME).write_text("# Simulation Run Complete\n")
    monkeypatch.setattr(background_worker.subprocess, "run", _duplicate_run)

    background_worker.process_leftover_run_markers()

    written = background_worker.LOG_FILE.read_text()
    assert "Processed {}".format(MARKER_NAME) not in written
    assert MARKER_NAME in written, "the outcome must still be visible in the log, not silent"


def test_the_publishers_verdict_reaches_the_sweep_end_to_end(monkeypatch, tmp_path):
    """THE ONE THAT CATCHES THE REAL DEFECT -- the two halves wired together, no mocked rc.

    Every other test in this file mocks one side of the seam, so each can pass while the pair is
    broken; that is precisely how the sibling lock-skip fix landed on one door and left this one
    open. Here the sweep's subprocess REALLY calls `_process`, and the race is reproduced as it
    was observed: the marker is present when the sweep globs it and archived by another
    publisher a moment before this process opens it.

    MUTATION: restore `return 0` on the publisher's already-archived path and this reds -- the
    rc reaches the sweep's `elif returncode == 0` branch, which logs "Processed" and closes
    PW4's zero-progress episode for a marker nobody published here.
    """
    staged = background_worker.STAGING_DIR / MARKER_NAME
    staged.write_text("# Simulation Run Complete\n\nGit: abc1234\n")

    def _really_publish(argv, **kwargs):
        # The concurrent publisher wins the race, between this sweep's glob and the open.
        (tmp_path / "done" / MARKER_NAME).write_text(staged.read_text())
        staged.unlink()
        return MagicMock(returncode=prc._process(argv[-1]), stderr="")

    monkeypatch.setattr(background_worker.subprocess, "run", _really_publish)
    closed = []
    monkeypatch.setattr(background_worker, "_record_marker_published", closed.append)

    background_worker.process_leftover_run_markers()

    assert closed == [], (
        "the publisher published NOTHING (the marker was already archived), yet its return code "
        "reached the sweep as a publish and closed the zero-progress episode")
    assert "Processed {}".format(MARKER_NAME) not in background_worker.LOG_FILE.read_text()


def test_a_real_publish_still_closes_the_episode(monkeypatch, tmp_path):
    """BOTH WAYS: the new carve-out must not disarm the genuine close condition."""
    (background_worker.STAGING_DIR / MARKER_NAME).write_text("# Simulation Run Complete\n")
    monkeypatch.setattr(background_worker.subprocess, "run",
                        lambda *a, **k: MagicMock(returncode=0, stderr=""))
    closed = []
    monkeypatch.setattr(background_worker, "_record_marker_published", closed.append)

    background_worker.process_leftover_run_markers()

    assert closed == [MARKER_NAME]


# --------------------------------------------------------------------------------------
# 4. R10 -- close the CLASS, not the instance
# --------------------------------------------------------------------------------------


def _rc_zero_sites(func):
    """Every `return 0` in `func`, keyed by the branch condition that guards it.

    Keyed on the enclosing `if` test's SOURCE rather than a line number so the pin survives
    ordinary edits above it and only moves when the control flow genuinely changes.
    """
    tree = ast.parse(inspect.getsource(func))
    parents = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parents[child] = node

    sites = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Return):
            continue
        if not (isinstance(node.value, ast.Constant) and node.value.value == 0):
            continue
        guard = "<function tail -- the publish path ran to completion>"
        walker = parents.get(node)
        while walker is not None:
            if isinstance(walker, ast.If):
                guard = ast.unparse(walker.test)
                break
            if isinstance(walker, (ast.FunctionDef, ast.AsyncFunctionDef)):
                break
            walker = parents.get(walker)
        sites.append(guard)
    return sorted(sites)


# The publisher's rc=0 register. rc=0 means ONE thing -- this process retired the marker and the
# published surfaces are current. Every OTHER outcome has a code of its own (EXIT_LOCK_SKIPPED =
# nobody published it; EXIT_NOTHING_PUBLISHED = it was already published elsewhere; 1 = a real
# processing error). A new branch that returns 0 without retiring the marker is the defect this
# whole file is about, so it is made to fail HERE, by name, at the moment it is written.
DECLARED_RC_ZERO_SITES = sorted([
    # The change-detection gate: outputs are byte-identical to the last processed run, so there
    # is nothing to publish -- but this process DID retire the marker (`_archive_marker`) and DID
    # refresh published liveness, so the sweep made progress and the surfaces are current.
    'last_fp == fingerprint and (not fingerprint[\'administration_event\']) and (not forced)',
    # The publish path ran to completion.
    "<function tail -- the publish path ran to completion>",
])


def test_no_new_no_publish_path_may_quietly_return_zero():
    """R10 class closure. If this test fails you have added a `return 0` to `_process()`.

    Decide which it is and act, do not just extend the list:
      * it RETIRED the marker and the surfaces are current -> add its guard below with one line
        saying which, exactly as the two existing entries do;
      * it published NOTHING -> return EXIT_NOTHING_PUBLISHED instead, so no caller can read it
        as a publish. That is the whole finding this file exists for.

    MUTATION: add `return 0` anywhere in `_process` and this reds naming the new guard.
    """
    found = _rc_zero_sites(prc._process)

    assert found == DECLARED_RC_ZERO_SITES, (
        "the set of rc=0 exits from _process() has changed.\n"
        "  declared: {}\n"
        "  found:    {}\n"
        "Every one of them asserts 'this process retired the marker and the published surfaces "
        "are current'. A path that published nothing must return EXIT_NOTHING_PUBLISHED.".format(
            DECLARED_RC_ZERO_SITES, found))


def test_main_reports_no_outcome_of_its_own(tmp_path):
    """`main()` is a lock wrapper: it returns EXIT_LOCK_SKIPPED or whatever `_process` decided.

    A bare `return 0` here would be a publish claim invented by the wrapper, above the code that
    knows what actually happened.
    """
    assert _rc_zero_sites(prc.main) == []


def test_every_no_publish_code_is_distinct_and_declared():
    """The codes must be mutually distinct and non-zero, or the whole distinction collapses."""
    codes = prc.NO_PUBLISH_EXIT_CODES

    assert len(set(codes)) == len(codes)
    assert 0 not in codes
    assert 1 not in codes, "1 is a real processing error, not a no-publish outcome"
    assert set(codes) == {prc.EXIT_LOCK_SKIPPED, prc.EXIT_NOTHING_PUBLISHED}
