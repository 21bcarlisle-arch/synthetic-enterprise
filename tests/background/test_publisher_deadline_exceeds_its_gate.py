"""R15 on the sweep's deadline, and on what a deadline kill is allowed to be recorded as.

THE DEFECT THIS PINS (observed 2026-08-10, docs/observability/background-worker-log.md 17:44Z):

    process_leftover_run_markers error: Command '[...process_run_complete.py,
    docs/staging/run_complete_20260809T131422Z.md]' timed out after 900 seconds

`background_worker.process_leftover_run_markers` -- the ONLY path that drains a lock-skipped
marker -- wrapped the publisher in an INDEPENDENT `timeout=900`, while the publisher's own
gate budget was re-derived 600 -> 1800 -> 2600s against the cold HEAD-checkout subject the
ruling moved it to. The pair drifted apart in the fatal direction: the wrapper killed the
publisher at 900s, before a gate budgeted 2600s could return any verdict. 95 markers backed
up, 142 consecutive recorded "failures", and the blocking test they were all blamed on
(`test_every_live_hit_is_dispositioned`) PASSED at HEAD the whole time.

THREE properties, each with the mutation that breaks it:

  1. THE COUPLING -- the sweep's deadline must EXCEED the publisher's own gate bound, and be
     DERIVED from it rather than restated. Mutation: shrink the publisher's declared budget
     below its gate bound and the derivation test reds. A hand-copied number would pass this
     while drifting, so the test asserts the sweep reads the publisher's value, not that two
     literals happen to match today.
  2. THE SWEEP SURVIVES ONE KILL -- a timed-out marker must not abandon the markers behind
     it. Mutation: the pre-fix code (a bare `subprocess.run(timeout=...)`) lets
     TimeoutExpired escape the loop; the test asserts marker #2 is still attempted.
  3. THE KILL IS NOT LAUNDERED INTO A TEST VERDICT -- it must reach the wedge detector, and
     reach it as `deadline_kill`, never `test_regression`. The pre-fix code recorded NOTHING
     at all (the exception skipped the recorder), which is the fail-silent half; recording it
     as a regression would be the lying half. Both are asserted against.
"""
from __future__ import annotations

import subprocess

import pytest

from background import background_worker as bw
from background import process_run_complete as prc


# ─────────────────────────────────────────────────────── 1. the coupling

def test_the_sweeps_deadline_exceeds_the_publishers_own_gate_bound():
    """The whole defect in one inequality. A wrapper bound below the work it wraps does not
    bound anything -- it decides the inner gate's verdict by stopwatch."""
    assert bw._publisher_deadline_seconds() > prc.GATE_SUITE_TIMEOUT_SECONDS, (
        "the sweep kills the publisher before its own gate is allowed to finish -- this is "
        "the 900s-vs-2600s wedge of 2026-08-10, reintroduced"
    )


def test_the_deadline_leaves_room_for_the_publish_path_after_the_gate():
    """The gate returning green is not the end of the publisher's work -- site regeneration,
    the report, the mirror, the hook-chain commit (GIT_COMMIT_HOOK_TIMEOUT_SECONDS) and the
    push all follow it. A deadline of exactly the gate bound would kill every GREEN cycle at
    the commit, which is the same wedge wearing a different hat."""
    slack = bw._publisher_deadline_seconds() - prc.GATE_SUITE_TIMEOUT_SECONDS
    assert slack >= prc.GIT_COMMIT_HOOK_TIMEOUT_SECONDS, (
        "no room left for the post-gate publish path; the hook-chain commit alone is "
        f"budgeted {prc.GIT_COMMIT_HOOK_TIMEOUT_SECONDS}s and only {slack}s remains"
    )


def test_the_sweep_derives_its_deadline_rather_than_restating_it(monkeypatch):
    """MUTATION -- the anti-drift property, and the one a matching pair of literals would
    pass while broken. Move the publisher's declared budget; the sweep must move with it."""
    monkeypatch.setattr(prc, "PUBLISH_PATH_TIMEOUT_SECONDS", 4242)
    assert bw._publisher_deadline_seconds() == 4242, (
        "the sweep is carrying its own copy of the number -- the exact shape that let 900s "
        "survive three re-derivations of the gate's own bound"
    )


def test_the_publishers_declared_budget_is_derived_from_its_gate_bound():
    """FIRES on the mutation the inequality above is protecting: if the publisher's total
    budget ever stops being a function of its gate bound, the two can drift apart again."""
    assert (prc.PUBLISH_PATH_TIMEOUT_SECONDS
            == prc.GATE_SUITE_TIMEOUT_SECONDS + prc.PUBLISH_PATH_ALLOWANCE_SECONDS)


# ─────────────────────────────────────────────── 2 & 3. the kill is survived and named

class _Recorded:
    """Captures what the sweep told the wedge detector, without touching real state."""

    def __init__(self):
        self.calls = []

    def __call__(self, marker, rc, *, kind=None):
        self.calls.append({"marker": getattr(marker, "name", str(marker)), "rc": rc, "kind": kind})


@pytest.fixture
def two_markers(tmp_path, monkeypatch):
    staging = tmp_path / "docs" / "staging"
    (staging / "done").mkdir(parents=True)
    first = staging / "run_complete_20260810T000000Z.md"
    second = staging / "run_complete_20260810T010000Z.md"
    for m in (first, second):
        m.write_text("git_hash: abc123\n")
    monkeypatch.setattr(bw, "STAGING_DIR", staging)
    monkeypatch.setattr(bw, "log", lambda *a, **k: None)
    monkeypatch.setattr(bw, "_check_zero_progress", lambda pending: False)
    monkeypatch.setattr(bw, "_remember_oldest_outcome", lambda *a, **k: None)
    monkeypatch.setattr(bw, "_newest_published_stamp", lambda done: None)
    monkeypatch.setattr(bw, "classify_markers", lambda markers, newest: ([], list(markers)))
    return first, second


def test_a_timed_out_marker_does_not_abandon_the_markers_behind_it(two_markers, monkeypatch):
    """FIRES on the pre-fix code. TimeoutExpired escaped the for-loop, so ONE slow marker
    took all 94 behind it down with it -- and the sweep is the entire safety net for a
    lock-skipped marker, so 'next cycle' meant the same kill again."""
    first, second = two_markers
    attempted = []

    def fake_run(argv, **kwargs):
        attempted.append(argv[-1])
        if argv[-1].endswith(first.name):
            raise subprocess.TimeoutExpired(cmd=argv, timeout=kwargs.get("timeout"))
        return subprocess.CompletedProcess(argv, 0, stderr="")

    monkeypatch.setattr(bw.subprocess, "run", fake_run)
    monkeypatch.setattr(bw, "_record_publish_gate_outcome", _Recorded())
    monkeypatch.setattr(bw, "_record_marker_published", lambda name: None)

    bw.process_leftover_run_markers()

    assert any(a.endswith(second.name) for a in attempted), (
        "the sweep stopped at the first timeout -- every marker behind it was abandoned"
    )


def test_a_deadline_kill_reaches_the_detector_and_is_not_called_a_test_regression(
        two_markers, monkeypatch):
    """The fail-silent half AND the lying half, in one assertion.

    Pre-fix, the exception skipped `_record_publish_gate_outcome` entirely, so a kill reached
    the wedge detector as NOTHING while the detector's own docstring claimed it saw kills.
    Recording it with an invented non-zero rc would be worse: `_classify_gate_failure` maps
    any rc>0 to `test_regression`, which is how a stopwatch becomes evidence about tests and
    how the RUNG-1 draw spent 27h naming a test that passes."""
    first, _second = two_markers
    recorded = _Recorded()

    def fake_run(argv, **kwargs):
        if argv[-1].endswith(first.name):
            raise subprocess.TimeoutExpired(cmd=argv, timeout=kwargs.get("timeout"))
        return subprocess.CompletedProcess(argv, 0, stderr="")

    monkeypatch.setattr(bw.subprocess, "run", fake_run)
    monkeypatch.setattr(bw, "_record_publish_gate_outcome", recorded)
    monkeypatch.setattr(bw, "_record_marker_published", lambda name: None)

    bw.process_leftover_run_markers()

    kills = [c for c in recorded.calls if c["marker"] == first.name]
    assert kills, "the kill never reached the wedge detector at all (fail-silent)"
    assert kills[0]["kind"] == "deadline_kill"
    assert kills[0]["rc"] is None, (
        "an invented return code launders a deadline kill into a claim about the tests"
    )


def test_the_detector_records_a_deadline_kill_under_its_own_name(tmp_path, monkeypatch):
    """The other side of the seam: the kind the sweep states must SURVIVE into the state file
    the RUNG-1 unwedge draw reads, rather than being re-inferred from the absent rc."""
    state = tmp_path / "publish_gate_state.json"
    monkeypatch.setattr(prc, "PUBLISH_GATE_STATE_FILE", state)

    prc.record_publish_gate_failure(
        "process_run_complete killed by the caller's deadline on run_complete_X.md",
        rc=None, git_hash="abc123", kind="deadline_kill", send_ntfy_fn=lambda m: None,
    )

    import json
    written = json.loads(state.read_text())
    assert written["failures"][-1]["kind"] == "deadline_kill"


def test_without_a_stated_kind_the_classifier_still_decides(tmp_path, monkeypatch):
    """SILENT half -- the override must not become the new default path. Every existing
    caller passes no kind and must keep getting the return-code classification."""
    state = tmp_path / "publish_gate_state.json"
    monkeypatch.setattr(prc, "PUBLISH_GATE_STATE_FILE", state)

    prc.record_publish_gate_failure("tests failed", rc=1, git_hash="abc123",
                                    send_ntfy_fn=lambda m: None)

    import json
    written = json.loads(state.read_text())
    assert written["failures"][-1]["kind"] == "test_regression"


def test_the_deadline_kill_label_says_the_tests_are_unjudged():
    """R5 -- the page carries the diagnostic. A kill labelled like a test failure is what
    sent the unwedge draw after a passing test for 27h, so the label has to say outright
    that no verdict was reached."""
    label = prc._gate_failure_label("deadline_kill")
    assert "NOT a test failure" in label and "unjudged" in label
