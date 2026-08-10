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

THE CLASS WAS CLOSED ON ONE HALF AND THE WEDGE CONTINUED (2026-08-10, +3h).

Everything above pinned `background_worker`'s sweep. It did not pin `sim_runner`, which is the
caller that publishes in the STEADY STATE -- every ~10 min, the marker it just wrote -- and
which kept its own literal `timeout=1200` behind a comment citing a 600s internal bound three
re-derivations out of date. So the same defect went on killing the same gate from the other
side, and the log says so in the same words:

    docs/observability/sim-runner-log.md 18:51Z
    Auto-process timed out after 1200s -- marker left for background_worker

recorded as rc=124 -> `test_regression`, against a gate that never returned a verdict. R10
forbids closing an absurdity-class defect at the instance, and "the OTHER caller" is the
instance this file already had the evidence to cover. So the coupling is now asserted over the
POPULATION of publisher-spawning call sites (section 4), which is what makes a THIRD caller
added later red on arrival rather than three hours into the next wedge.
"""
from __future__ import annotations

import ast
import subprocess
from pathlib import Path

import pytest

from background import background_worker as bw
from background import process_run_complete as prc
from background import sim_runner as sr


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


# ─────────────────────────────── 4. the POPULATION of callers, not the one that was fixed

# Every module in the repo that spawns `process_run_complete.py` as a subprocess. Adding a
# publisher-spawning caller means adding it here; the scan below FAILS if a module spawns the
# publisher while carrying its own literal deadline, so a caller cannot be added silently with
# a fresh copy of the 900/1200 mistake.
PUBLISHER_CALLERS = (
    ("background/background_worker.py", bw),
    ("background/sim_runner.py", sr),
)


@pytest.mark.parametrize("module_path,module", PUBLISHER_CALLERS,
                         ids=[p for p, _ in PUBLISHER_CALLERS])
def test_every_publisher_caller_derives_its_deadline(module_path, module, monkeypatch):
    """MUTATION, per caller: move the publisher's declared budget and every caller must move
    with it. `sim_runner` FAILED this until 2026-08-10 -- it answered 1200 whatever the
    publisher declared, which is the whole defect as a single number."""
    monkeypatch.setattr(prc, "PUBLISH_PATH_TIMEOUT_SECONDS", 4242)
    assert module._publisher_deadline_seconds() == 4242, (
        "{} carries its own copy of the deadline -- the exact shape that let 900s survive "
        "three re-derivations of the gate's own bound, and then let 1200s survive the fix "
        "aimed at 900s".format(module_path)
    )


@pytest.mark.parametrize("module_path,module", PUBLISHER_CALLERS,
                         ids=[p for p, _ in PUBLISHER_CALLERS])
def test_every_publisher_callers_deadline_exceeds_the_gate_it_wraps(module_path, module):
    """The whole defect in one inequality, asserted over the population. A wrapper bound below
    the work it wraps does not bound anything -- it decides the inner gate's verdict by
    stopwatch."""
    deadline = module._publisher_deadline_seconds()
    assert deadline > prc.GATE_SUITE_TIMEOUT_SECONDS, (
        "{} kills the publisher at {}s, before a gate budgeted {}s can return a verdict"
        .format(module_path, deadline, prc.GATE_SUITE_TIMEOUT_SECONDS)
    )
    slack = deadline - prc.GATE_SUITE_TIMEOUT_SECONDS
    assert slack >= prc.GIT_COMMIT_HOOK_TIMEOUT_SECONDS, (
        "{} leaves no room for the post-gate publish path; the hook-chain commit alone is "
        "budgeted {}s and only {}s remains".format(
            module_path, prc.GIT_COMMIT_HOOK_TIMEOUT_SECONDS, slack)
    )


def _publisher_spawn_calls(module_path):
    """(subprocess calls, literal timeouts) for every function that spawns the publisher.

    STATIC, deliberately: the runtime tests above prove the HELPER derives correctly, which a
    call site that never uses the helper would pass while carrying a literal. This reads the
    call site itself.

    SCOPED TO THE ENCLOSING FUNCTION, not to the call node. The first version of this scan
    matched on the call's own dump containing "process_run_complete", and matched NOTHING in
    either module -- both callers build the path into a local (`processor = Path(...) /
    'process_run_complete.py'`) and pass the local. It therefore returned an empty list for a
    genuinely mutated call site and passed. A scan that cannot see its subject is a control
    that cannot fail (R15), which is why `test_the_scan_can_see_the_call_sites_at_all` below
    exists: the population it finds is asserted non-empty before any claim is made about it."""
    tree = ast.parse((Path(__file__).resolve().parents[2] / module_path).read_text())
    spawns, literals = [], []
    for func in ast.walk(tree):
        if not isinstance(func, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if "process_run_complete" not in ast.dump(func):
            continue
        for node in ast.walk(func):
            if not isinstance(node, ast.Call):
                continue
            if not any(kw.arg == "timeout" for kw in node.keywords):
                continue
            callee = ast.dump(node.func)
            if "subprocess" not in callee and "run" not in callee and "Popen" not in callee:
                continue
            spawns.append(node)
            for kw in node.keywords:
                if kw.arg == "timeout" and isinstance(kw.value, ast.Constant):
                    literals.append(kw.value.value)
    return spawns, literals


def _publisher_spawn_timeouts(module_path):
    return _publisher_spawn_calls(module_path)[1]


@pytest.mark.parametrize("module_path,_module", PUBLISHER_CALLERS,
                         ids=[p for p, _ in PUBLISHER_CALLERS])
def test_the_scan_can_see_the_call_sites_at_all(module_path, _module):
    """VACUITY GUARD, and it is not theoretical -- the first version of the scan below found
    zero call sites in both modules and therefore passed a deliberately mutated one. An
    empty population is a BLIND control, never a clean bill of health."""
    spawns, _literals = _publisher_spawn_calls(module_path)
    assert spawns, (
        "the scan found no timed subprocess call in any publisher-spawning function of {} -- "
        "it is asserting nothing, and the mutation it exists to catch would survive it"
        .format(module_path)
    )


@pytest.mark.parametrize("module_path,_module", PUBLISHER_CALLERS,
                         ids=[p for p, _ in PUBLISHER_CALLERS])
def test_no_publisher_call_site_carries_a_literal_deadline(module_path, _module):
    """MUTATION -- restore `timeout=1200` at sim_runner's spawn and this reds.

    The derivation tests above ask the HELPER. This asks the CALL SITE, because the defect
    that survived the first fix was not a wrong helper: `background_worker` had a correct
    `_publisher_deadline_seconds()` on 2026-08-10 while `sim_runner` spawned the same
    publisher with a hand-written literal three lines from the same import."""
    literals = _publisher_spawn_timeouts(module_path)
    assert not literals, (
        "{} spawns the publisher with a hard-coded timeout {} -- it must pass "
        "_publisher_deadline_seconds(), which is derived from the publisher's own declared "
        "budget".format(module_path, literals)
    )


def test_sim_runners_deadline_kill_is_not_recorded_as_a_test_regression(monkeypatch, tmp_path):
    """THE STEADY-STATE HALF of property 3, and the one that actually fed the 145-failure
    episode: 124 is a return code the classifier maps to `test_regression`, so every deadline
    kill on this path arrived at the RUNG-1 draw as evidence about tests that were never run."""
    recorded = _Recorded()
    marker = tmp_path / "run_complete_20260810T000000Z.md"
    marker.write_text("git_hash: abc123\n")

    def fake_run(argv, **kwargs):
        raise subprocess.TimeoutExpired(cmd=argv, timeout=kwargs.get("timeout"))

    monkeypatch.setattr(sr.subprocess, "run", fake_run)
    monkeypatch.setattr(sr, "_record_publish_gate_outcome", recorded)
    monkeypatch.setattr(sr, "log", lambda *a, **k: None)

    assert sr.auto_process_marker(marker) == 124, "the caller still needs a non-zero rc"
    assert recorded.calls, "the kill never reached the wedge detector at all (fail-silent)"
    assert recorded.calls[0]["kind"] == "deadline_kill"
    assert recorded.calls[0]["rc"] is None, (
        "rc=124 launders a stopwatch into a claim about the tests -- _classify_gate_failure "
        "maps any rc>0 to test_regression"
    )
