"""R15 mutation tests for the THIRD door of the publish-gate fail-open.

WORKER_FINDING_THE_PUBLISH_COMMIT_STOPPED_LANDING_WHILE_RUNS_KEPT_ARCHIVING_2026-08-19 (BLOCKING,
class `publish_gate_and_wedge`).

THE INCIDENT, observed with evidence (R9), not inferred. On 2026-08-19 the publish path ran to
completion fourteen times between 01:56Z and 11:45Z and every one of them logged
`Commit/push failed (commit_refused)` -- the pre-commit hook chain refusing on an unrelated
lane's red on the shared tree ("FINDING-CLASS CONSOLIDATION BROKEN -- COMMIT REFUSED"). Each run
had already archived its own `run_complete_*.md` to `done/`, so every local record read "done"
while `poesys.net/data/dashboard.json` served figures 11.5 hours stale.

WHY NOTHING FIRED, WHICH IS THE PART THIS FILE IS ABOUT. `_process` logged the failure and then
`return 0`. rc=0 is the ONE input the wedge detector consumes, and the router's independent
evidence for rc=0 -- `_green_is_on_record_for`, reading `.last_tested_hash` -- was TRUE, because
the publisher's own scoped suite really had passed; the refusal came afterwards, from a different
gate, on a red the publish did not cause. So the router did not merely stay quiet: it called
`record_publish_gate_success()` and CLEARED the streak. "Publish gate recovered -- cleared wedge
state, re-armed alarm." is in the log at 07:23Z, in the middle of the outage.

That is the same fail-open the two codes above it already closed twice (EXIT_LOCK_SKIPPED for a
lock-skip, EXIT_NOTHING_PUBLISHED for a duplicate marker), arriving through a third door -- and
the one the earlier fixes could not have caught, because those are about a publish that never
STARTED and this is a publish that ran the whole way and did not LAND.

THE CONTROL, AND HOW EACH TEST BELOW CAN FAIL (R15 -- a control that cannot fail is worse than
none). `publish_exit_code` maps the outcome `git_commit_push` named to the process exit code;
`record_publish_gate_outcome` routes that code to a FAILURE. Both halves are mutated here, and
`test_the_null_control_...` is the one that matters most: it re-runs the identical fixture with
the pre-fix return code and shows the alarm being disarmed, so a green result in this file is a
statement about the exit code and not about the fixture.
"""
import json

import pytest

import background.process_run_complete as prc
import background.sim_runner as sim_runner

MARKER_HASH = "b98722cb2"
MARKER_NAME = "run_complete_20260819T095100Z.md"


@pytest.fixture(autouse=True)
def _isolate(tmp_path, monkeypatch):
    """Every file this control touches, redirected. An alarm test that reads this morning's
    real wedge state -- or writes it -- is a test of nothing, and would poison the live
    detector it is checking."""
    monkeypatch.setattr(prc, "PUBLISH_GATE_STATE_FILE", tmp_path / ".publish_gate_state.json")
    monkeypatch.setattr(prc, "LAST_TESTED_HASH_FILE", tmp_path / ".last_tested_hash")
    monkeypatch.setattr(prc, "GATE_BLOCKING_TESTS_FILE", tmp_path / ".blocking.json")
    monkeypatch.setattr(prc, "WEDGE_SUSPECT_HIT_RATE_FILE", tmp_path / ".hit_rate.json")
    # ORIGIN IS LEVEL. The publish path reads origin before staging (2026-09-01,
    # `_divergence_refusal`) and this file's scratch tree is not a git repository, so without
    # this the subject under test becomes the divergence refusal rather than the lost tree lock.
    monkeypatch.setattr(prc, "_commits_origin_is_ahead_by", lambda: 0)
    monkeypatch.setattr(prc, "LOG_FILE", tmp_path / "log.md")
    import background.action_needed as an
    monkeypatch.setattr(an, "REGISTER_PATH", tmp_path / "action_needed_register.json")
    yield


@pytest.fixture
def archived_marker(tmp_path, monkeypatch):
    """A marker in `done/` produced at MARKER_HASH -- the state a publish leaves behind whether
    its commit landed or not, which is exactly why the marker's own location proves nothing."""
    done = tmp_path / "staging" / "done"
    done.mkdir(parents=True)
    marker = done / MARKER_NAME
    marker.write_text("# Run complete\n\nGit: {}\n".format(MARKER_HASH))
    monkeypatch.setattr(prc, "DONE_DIR", done)
    monkeypatch.setattr(prc, "STAGING_DIR", tmp_path / "staging")
    return marker


@pytest.fixture
def suite_was_green():
    """`.last_tested_hash` pinned to the marker's commit -- the router's independent evidence,
    TRUE on this path. This fixture is the finding: the scoped suite really did pass, so no
    check keyed to the suite could ever have caught a refused commit."""
    prc.LAST_TESTED_HASH_FILE.write_text(MARKER_HASH + "\n")


def _state():
    return json.loads(prc.PUBLISH_GATE_STATE_FILE.read_text())


# ── half one: the exit code must carry the outcome ────────────────────────────

def test_every_outcome_that_did_not_publish_reports_a_non_zero_code():
    """MUTATION: return 0 unconditionally (the pre-fix tail) and every row below goes red.

    Enumerated over the module's own outcome constants rather than a hand-written list, so an
    outcome added later cannot slip past by not being thought of here.
    """
    landed = {prc.PUBLISHED, prc.NOTHING_TO_COMMIT, prc.COMMITTED_PUSH_THROTTLED}
    did_not_land = {prc.COMMIT_TIMEOUT, prc.COMMIT_REFUSED,
                    prc.PUSH_DID_NOT_REACH_ORIGIN, prc.PROVENANCE_REFUSED}

    for reason in landed:
        assert prc.publish_exit_code(reason) == 0, (
            "{!r} landed a commit, so the marker is retired and the surfaces are "
            "current".format(reason))
    for reason in did_not_land:
        assert prc.publish_exit_code(reason) == prc.EXIT_PUBLISH_DID_NOT_LAND, (
            "{!r} published NOTHING -- exiting 0 is what let the wedge detector record it as "
            "a success".format(reason))


def test_an_unclassified_outcome_fails_closed():
    """FAIL-OPEN is the killer pattern this direction closes (R15). A missing or unrecognised
    reason must read as "did not land": the harmless error is one alarm too many, the harmful
    one is eleven hours of stale public figures.

    MUTATION: flip the default to 0 and both rows go red.
    """
    assert prc.publish_exit_code(None) == prc.EXIT_PUBLISH_DID_NOT_LAND
    assert prc.publish_exit_code("an_outcome_nobody_has_written_yet") == \
        prc.EXIT_PUBLISH_DID_NOT_LAND


def test_the_two_consequences_read_the_same_closed_set():
    """The fingerprint decision and the exit code must never disagree about one outcome.

    That drift IS the incident: the fingerprint was correctly withheld fourteen times running
    ("this cycle is unfinished, retry it") while the exit code said 0 every time ("this cycle
    published"). One set, asked twice.

    MUTATION: give `publish_exit_code` a literal set of its own and this reds as soon as the
    two lists differ by one member.
    """
    for reason in prc.RETRYABLE_PUBLISH_OUTCOMES:
        assert prc.publish_exit_code(reason) == 0
    for reason in (prc.COMMIT_REFUSED, prc.COMMIT_TIMEOUT,
                   prc.PUSH_DID_NOT_REACH_ORIGIN, prc.PROVENANCE_REFUSED):
        assert reason not in prc.RETRYABLE_PUBLISH_OUTCOMES
        assert prc.publish_exit_code(reason) != 0


# ── half two: the router must record a FAILURE, never a success ───────────────

def test_a_refused_commit_records_a_failure(archived_marker, suite_was_green):
    """The whole finding in one assertion.

    MUTATION: delete the EXIT_PUBLISH_DID_NOT_LAND branch from `record_publish_gate_outcome`
    and rc=77 falls through to the generic `record_publish_gate_failure` -- still a failure, so
    this row survives; delete the branch AND revert the exit code and it goes red, which is the
    pairing the null control below pins.
    """
    verdict = prc.record_publish_gate_outcome(
        str(archived_marker), prc.EXIT_PUBLISH_DID_NOT_LAND)

    assert verdict == "failure", (
        "a publish whose commit did not land must be recorded as a FAILURE -- it is the only "
        "signal that the live site has stopped advancing")
    state = _state()
    assert len(state["failures"]) == 1
    assert state["wedge_since"] is not None, "the episode clock must start"
    assert state["episode_failures"] == 1


def test_the_payload_does_not_blame_the_tests(archived_marker, suite_was_green):
    """`_classify_gate_failure` maps any rc>0 to `test_regression`, and the RUNG-1 unwedge draw
    reads that kind off the state file. Letting rc=77 be classified that way would send the
    draw hunting a red test at a HEAD whose suite was green -- the same laundering of a
    stopwatch into test evidence that `kind="deadline_kill"` exists to stop.

    MUTATION: drop `kind=` from the router's branch and this reds with `test_regression`.
    """
    prc.record_publish_gate_outcome(str(archived_marker), prc.EXIT_PUBLISH_DID_NOT_LAND)

    assert _state()["failures"][0]["kind"] == "commit_did_not_land"
    label = prc._gate_failure_label("commit_did_not_land")
    assert "GREEN" in label and "pre-commit" in label, (
        "the alert payload must tell the reader the publish path is not the suspect")


def test_the_null_control_the_pre_fix_code_disarms_the_alarm(archived_marker, suite_was_green):
    """THE NULL CONTROL. Identical marker, identical `.last_tested_hash`, identical wedge state
    -- only the return code differs, and it is the pre-fix 0.

    This is what makes the rows above evidence about the exit code rather than about the
    fixture: with rc=0 the router calls the publish a SUCCESS and clears a streak that was
    three failures deep. That is not a hypothetical -- it is 2026-08-19 07:23Z, "Publish gate
    recovered -- cleared wedge state, re-armed alarm.", logged in the middle of the outage.
    """
    import time

    def _seed_three_recent_failures():
        # Stamped just before NOW, not at t=0: the router calls the recorder with the real
        # clock, and PUBLISH_GATE_WINDOW_SECONDS would trim epoch-stamped seeds out from
        # under the assertion. The cooldown that the third failure arms is what keeps the
        # fourth from paging a real phone.
        base = time.time()
        for offset in (30, 20, 10):
            prc.record_publish_gate_failure("seeded", rc=1, git_hash="dead", now=base - offset,
                                            send_ntfy_fn=lambda _m: "sent")

    _seed_three_recent_failures()
    assert len(_state()["failures"]) == 3

    # THE DEFECT, reproduced.
    assert prc.record_publish_gate_outcome(str(archived_marker), 0) == "success"
    assert _state()["failures"] == [], (
        "reproduction check: rc=0 with a green .last_tested_hash really does clear the streak")

    # THE FIX, on the same fixture.
    _seed_three_recent_failures()
    prc.record_publish_gate_outcome(str(archived_marker), prc.EXIT_PUBLISH_DID_NOT_LAND)
    assert len(_state()["failures"]) == 4, (
        "the refused publish must ADD to the streak, not clear it")
    assert _state()["failures"][-1]["kind"] == "commit_did_not_land"


def test_the_code_is_not_filed_as_evidence_of_nothing():
    """NO_PUBLISH_EXIT_CODES means "record neither a success nor a failure". Filing the new code
    there would re-silence the alarm in the name of the fix that opened it -- the single most
    likely wrong edit a later reader makes, so it is made to fail by name.

    MUTATION: add EXIT_PUBLISH_DID_NOT_LAND to NO_PUBLISH_EXIT_CODES and this reds.
    """
    assert prc.EXIT_PUBLISH_DID_NOT_LAND not in prc.NO_PUBLISH_EXIT_CODES
    assert prc.EXIT_PUBLISH_DID_NOT_LAND not in (0, 1)
    assert prc.EXIT_PUBLISH_DID_NOT_LAND not in (
        prc.EXIT_LOCK_SKIPPED, prc.EXIT_NOTHING_PUBLISHED)


# ── the caller that runs every ~10 min in the steady state ────────────────────

def test_the_runner_mirror_constant_cannot_drift():
    """sim_runner keeps its own copy of the codes (it must not import the publish pipeline at
    module scope). The number is not the property; this is."""
    assert sim_runner.EXIT_PUBLISH_DID_NOT_LAND == prc.EXIT_PUBLISH_DID_NOT_LAND


def test_the_runner_does_not_send_the_reader_after_a_pending_marker():
    """The generic `else` branch logs "marker left for background_worker", which is FALSE here:
    the publisher archived the marker before ever attempting the commit, so no sweep will see
    it again. A wrong sentence in the first log a diagnosis opens is how the 2026-08-19 outage
    stayed misread.

    MUTATION: delete the elif and this reds.
    """
    import inspect
    src = inspect.getsource(sim_runner.auto_process_marker)
    assert "elif rc == EXIT_PUBLISH_DID_NOT_LAND:" in src
    assert "Marker already archived" in src


# ── CONTENTION IS AN OUTCOME, NOT A TRACEBACK (2026-08-30) ───────────────────────────────
# THE DEFECT, observed live: `git_commit_push` entered `tree_lock()` OUTSIDE its own try, so
# when another writer held the lock for the full 60s the TreeLockTimeout propagated out of
# `main()` as an uncaught traceback. That is rc=1 -- the generic code -- which the wedge
# detector reads as `test_regression`. The 2026-08-30 episode recorded two such failures with
# `blocking_tests: []` and `total_red: 0` while the log for the same cycle read "Tests skipped
# -- already passed": the suite had not been run at all, and the RUNG-1 draw sent to diagnose
# the wedge went looking for a red test that did not exist.

def test_a_lost_tree_lock_is_a_named_outcome_and_not_an_uncaught_traceback(tmp_path, monkeypatch):
    """MUTATION: put `tree_lock()` back in a bare `with` and this raises instead of returning,
    which is exactly the shape that became rc=1.

    The assertion is deliberately BOTH halves -- that it does not raise, AND that it names
    TREE_LOCK_UNAVAILABLE. Catching the timeout and filing it as COMMIT_REFUSED would satisfy
    the first alone while still pointing the reader at a hook chain that never ran.
    """
    import background.process_run_complete as prc
    from background.tree_lock import TreeLockTimeout

    monkeypatch.setattr(prc, "PROJECT_DIR", tmp_path)
    monkeypatch.setattr(prc, "LATEST_MD", tmp_path / "LATEST.md")
    monkeypatch.setattr(prc, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(prc, "_provenance_is_publishable", lambda *a, **k: True)

    def _held(*a, **k):
        raise TreeLockTimeout("Could not acquire tree lock (x) within 60.0s")

    monkeypatch.setattr(prc, "tree_lock", _held)

    outcome = {}
    result = prc.git_commit_push("abc1234", 1000.0, outcome)

    assert result is False, "a cycle that never got the lock did not publish"
    assert outcome["reason"] == prc.TREE_LOCK_UNAVAILABLE, (
        "the lost lock is filed as {!r} -- the reader is sent to the wrong subject".format(
            outcome.get("reason"))
    )
    # And the code the process actually exits with is the named one, not the generic 77 that
    # tells the reader to go and read a hook chain that never ran.
    assert prc.publish_exit_code(outcome["reason"]) == prc.EXIT_TREE_LOCK_UNAVAILABLE


def test_the_guard_covers_acquisition_only_so_a_nested_deadlock_still_surfaces(tmp_path, monkeypatch):
    """A TreeLockTimeout raised from INSIDE the lock body is a different fact -- the nested
    re-acquisition documented at `_git_add_or_refuse`, i.e. a deadlock in our own code, not
    contention with another writer. Mislabelling that as contention would tell the reader to
    wait for a lock that will never be released.

    MUTATION: widen the guard to an outer `try` around the whole `with` and this stops raising.
    """
    import inspect

    import background.process_run_complete as prc

    src = inspect.getsource(prc.git_commit_push)
    assert "stack.enter_context(tree_lock())" in src, (
        "the lock is no longer acquired through a guarded ExitStack -- re-check that a "
        "TreeLockTimeout from the BODY is still distinguishable from one at acquisition"
    )
    assert "with tree_lock():" not in src, (
        "a bare `with tree_lock():` is back: an acquisition timeout escapes as a traceback"
    )
