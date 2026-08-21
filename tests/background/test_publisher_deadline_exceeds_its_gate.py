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
    lock-skipped marker, so 'next cycle' meant the same kill again.

    The kill is pinned to `second` (2026-08-14, OPS3): the sweep now works NEWEST-FIRST, so
    `second` is the marker it attempts first and therefore the one whose death could abandon
    the rest. Pinning it to `first` would have left this test asserting that a marker attempted
    BEFORE any timeout was attempted -- vacuously true, and it would have gone on passing
    through exactly the regression it exists to catch."""
    first, second = two_markers
    attempted = []

    def fake_run(argv, **kwargs):
        attempted.append(argv[-1])
        if argv[-1].endswith(second.name):
            raise subprocess.TimeoutExpired(cmd=argv, timeout=kwargs.get("timeout"))
        return subprocess.CompletedProcess(argv, 0, stderr="")

    monkeypatch.setattr(bw.subprocess, "run", fake_run)
    monkeypatch.setattr(bw, "_record_publish_gate_outcome", _Recorded())
    monkeypatch.setattr(bw, "_record_marker_published", lambda name: None)

    bw.process_leftover_run_markers()

    assert attempted and attempted[0].endswith(second.name), (
        "the sweep must attempt the NEWEST marker first -- otherwise the timeout below is not "
        f"the first attempt and this test proves nothing. attempted={attempted}"
    )
    assert any(a.endswith(first.name) for a in attempted), (
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
    _first, second = two_markers
    recorded = _Recorded()

    # Pinned to `second` for the reason given in the test above: NEWEST-FIRST (OPS3,
    # 2026-08-14) makes it the marker the sweep actually attempts, so it is the one that can
    # be killed by the deadline at all.
    def fake_run(argv, **kwargs):
        if argv[-1].endswith(second.name):
            raise subprocess.TimeoutExpired(cmd=argv, timeout=kwargs.get("timeout"))
        return subprocess.CompletedProcess(argv, 0, stderr="")

    monkeypatch.setattr(bw.subprocess, "run", fake_run)
    monkeypatch.setattr(bw, "_record_publish_gate_outcome", recorded)
    monkeypatch.setattr(bw, "_record_marker_published", lambda name: None)

    bw.process_leftover_run_markers()

    kills = [c for c in recorded.calls if c["marker"] == second.name]
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


# ── THE ABSOLUTE CAP ON GATE DURATION (director, 2026-08-21) ────────────────────────────────
# *"put a limit on the absolute duration that fails loudly when crossed, so this can't grow back
# one reasonable addition at a time."*
#
# The bound had been re-derived SIX times -- 600, 1800, 2600, 2900, 3600, 4500 -- each time
# carefully, each time by measuring the suite and adding margin, and each time asking only what
# the SUITE NEEDS. Its own comment states the asymmetry that made that one-directional: "erring
# low WEDGES PUBLISHING". Nothing asked what a publish gate can AFFORD, so nothing could ever
# push back, and it went 30 -> 75 minutes in nineteen hours.
#
# These two tests are the counter-pressure. They cannot be satisfied by re-deriving; the seventh
# raise has to delete a constant in the open and argue with the reason written beside it.

def test_the_gate_bound_never_rises_above_the_ratchet():
    """The number nothing was watching. MONOTONIC: the bound may fall freely and may never rise.

    First written as an aspirational cap at the 5-minute publish cadence, with the bound set to
    match -- which put the bound below what the gate actually needs and timed publishing out
    twice. A target cannot be enforced by a constant; a ratchet can."""
    assert prc.GATE_SUITE_TIMEOUT_SECONDS <= prc.PUBLISH_GATE_CEILING_RATCHET_SECONDS, (
        f"the publish gate's bound is {prc.GATE_SUITE_TIMEOUT_SECONDS}s, over the absolute cap of "
        f"{prc.PUBLISH_GATE_CEILING_RATCHET_SECONDS}s.\n"
        "Do NOT re-derive the bound -- that is the move that took it from 600s to 4500s in six "
        "steps. The bound may FALL freely; it may not rise. Earn a lower one by narrowing what "
        "`publish_scope.resolve_scope()` resolves to, which is where the twenty minutes live."
    )


def test_the_cap_is_derived_from_cadence_not_from_the_suite():
    """R15: the cap must be independent of the thing it constrains. If it were computed from
    measured suite runtimes it would be the same self-satisfying loop wearing a new name -- the
    suite would define its own ceiling, which is exactly what six re-derivations did."""
    import inspect
    src = inspect.getsource(prc)
    cap_line = [ln for ln in src.splitlines()
                if ln.startswith("PUBLISH_GATE_CEILING_RATCHET_SECONDS")]
    assert cap_line, "the absolute cap constant is gone"
    assert cap_line[0].split("=")[1].strip().isdigit(), (
        "the absolute cap must be a literal, not computed from suite measurements -- a ceiling "
        "derived from the thing it caps cannot constrain it"
    )


# ─────────────────────────────── 5. THE INNER CLOCK — the third caller is the publisher itself
#
# Sections 2-4 closed this class on the OUTER clock: every module that spawns the publisher and
# kills it on its own deadline records `kind="deadline_kill"` and invents no return code. The
# publisher has a SECOND clock over the same gate -- `GATE_SUITE_TIMEOUT_SECONDS`, its own
# budget, whose verdict is `_gate_timed_out()` -- and until 2026-08-21 that one had no carve-out
# at all: it set `tests_ok=False` and fell into the same bare `return 1` as a genuine red, so
# `_classify_gate_failure` filed a stopwatch as `test_regression`.
#
# OBSERVED (WORKER_FINDING_A_PUBLISH_TIMEOUT_IS_RECORDED_AS_A_TEST_REGRESSION_AND_THE_SCOPE_
# CANNOT_MEET_ITS_CAP_2026-08-21, BLOCKING, recommendation 1): both failures in
# `.publish_gate_state.json` read `test_regression` while `total_red` was 0 and `blocking_tests`
# was empty -- an accusation with no accused -- during a 32-hour wedge, 3 of whose 46 refusals
# were this branch.
#
# R10: the fix is not "and also the inner one". It is that a refused publish states WHICH KIND
# of refusal it was, in ONE place (`_gate_refusal`), so the exit code, the log line and the
# public banner cannot disagree about the same cycle. Each test below names the mutation that
# breaks it.


def test_the_inner_timeout_does_not_exit_with_the_reds_code():
    """MUTATION: `return (1, ...)` for the timeout branch -- i.e. the pre-fix code, where a
    stopwatch and a red left the publisher by the same door. Then the router below has nothing
    to distinguish them BY, and every downstream reader is back to inferring from rc=1."""
    timeout_code, _, _ = prc._gate_refusal(True, "abc123", [])
    red_code, _, _ = prc._gate_refusal(False, "abc123", ["tests/x.py::test_y"])

    assert timeout_code == prc.EXIT_GATE_TIMED_OUT
    assert timeout_code != red_code, (
        "a gate that did not finish and a gate that found a red leave the publisher by the same "
        "exit code, so nothing downstream can tell a stopwatch from a test failure"
    )


def test_the_inner_timeout_is_a_failure_not_a_no_publish():
    """R15 FAIL-OPEN, the direction that would be worse than the defect being fixed. Naming the
    timeout is only safe while it still WEDGES: an unavailable check is a FAILED check.
    MUTATION: add EXIT_GATE_TIMED_OUT to NO_PUBLISH_EXIT_CODES and the streak stops counting a
    gate that cannot answer, which is how the alarm gets disarmed by a fix."""
    assert prc.EXIT_GATE_TIMED_OUT not in prc.NO_PUBLISH_EXIT_CODES, (
        "a gate that could not answer is filed as 'published nothing, evidence of nothing' -- "
        "which leaves the wedge streak exactly where it found it and lets a timing-out gate "
        "run silently forever"
    )


def test_the_routers_verdict_for_the_inner_timeout_is_a_failure(tmp_path, monkeypatch):
    """The seam: the code the publisher returns must reach the wedge detector as a FAILURE
    (keeping the streak) and under its OWN name. MUTATION: drop the `EXIT_GATE_TIMED_OUT`
    branch from `record_publish_gate_outcome` and rc=78 falls through to
    `_classify_gate_failure`, which reads any rc>0 as `test_regression`."""
    import json

    state = tmp_path / "publish_gate_state.json"
    monkeypatch.setattr(prc, "PUBLISH_GATE_STATE_FILE", state)
    monkeypatch.setattr(prc, "_marker_git_hash", lambda m: "abc123")
    monkeypatch.setattr(prc, "notify", lambda *a, **k: None, raising=False)

    marker = tmp_path / "run_complete_20260821T160300Z.md"
    marker.write_text("marker\n")

    verdict = prc.record_publish_gate_outcome(marker, prc.EXIT_GATE_TIMED_OUT)

    assert verdict == "failure", (
        "a gate that did not finish must keep the wedge streak -- R15: an unavailable check is "
        "a FAILED check"
    )
    written = json.loads(state.read_text())
    assert written["failures"][-1]["kind"] == "gate_timeout", (
        "the publisher's own gate timeout is recorded as {!r} -- the stopwatch-filed-as-a-red "
        "defect this branch exists to close".format(written["failures"][-1]["kind"])
    )
    assert written["failures"][-1]["kind"] != "test_regression"


def test_a_genuine_red_is_still_a_test_regression(tmp_path, monkeypatch):
    """THE NULL CONTROL. A carve-out that swallowed the real reds would score green on every
    test above while destroying the signal. MUTATION: classify every failure as `gate_timeout`
    and this test reds."""
    import json

    state = tmp_path / "publish_gate_state.json"
    monkeypatch.setattr(prc, "PUBLISH_GATE_STATE_FILE", state)
    monkeypatch.setattr(prc, "_marker_git_hash", lambda m: "abc123")
    monkeypatch.setattr(prc, "notify", lambda *a, **k: None, raising=False)

    marker = tmp_path / "run_complete_20260821T161500Z.md"
    marker.write_text("marker\n")

    assert prc.record_publish_gate_outcome(marker, 1) == "failure"
    written = json.loads(state.read_text())
    assert written["failures"][-1]["kind"] == "test_regression"


def test_the_gate_timeout_label_says_the_tests_are_unjudged():
    """R5 -- the payload carries the diagnostic, and the diagnostic must not be the neighbouring
    clock's. MUTATION: reuse the `deadline_kill` label and the reader is sent to look at the
    CALLER's deadline, which did not fire."""
    label = prc._gate_failure_label("gate_timeout")
    assert "NOT a test failure" in label and "unjudged" in label
    assert "CALLER" not in label, (
        "this is the publisher's OWN clock -- borrowing the caller's label names the wrong "
        "process to go and look at"
    )
    assert label != prc._gate_failure_label("deadline_kill")


def test_the_timeout_alarm_does_not_send_the_reader_after_a_test(tmp_path, monkeypatch):
    """The RUNG-1 draw reads this payload. MUTATION: drop the `kind == "gate_timeout"` branch in
    `_fire_publish_gate_alert` and the standing clause tells the reader `rc>0 means run that
    test at HEAD to find the regression` about a cycle where no test was judged -- and the
    suspect clause names files derived from an EARLIER cycle's `blocking` list."""
    monkeypatch.setattr(prc, "PUBLISH_GATE_STATE_FILE", tmp_path / "s.json")

    msg = prc._fire_publish_gate_alert(
        recent=[{}], kind="gate_timeout", rc=prc.EXIT_GATE_TIMED_OUT, git_hash="abc123",
        unavailable=False, send_ntfy_fn=lambda m: "sent-1",
        blocking=["tests/background/test_left_over_from_an_earlier_cycle.py::test_x"],
        markers_pending=3, total_red=0,
    )

    assert "NO TEST WAS JUDGED" in msg
    assert "run that test at HEAD to find the regression" not in msg
    assert "test_left_over_from_an_earlier_cycle" not in msg, (
        "the timeout alarm names a test from an earlier cycle as a suspect -- naming nobody "
        "beats naming the innocent"
    )


def test_a_red_alarm_still_names_its_blocking_test(tmp_path, monkeypatch):
    """THE NULL CONTROL for the alarm half. MUTATION: apply the timeout wording to every kind
    and a genuine red stops naming the node the reader needs to run."""
    monkeypatch.setattr(prc, "PUBLISH_GATE_STATE_FILE", tmp_path / "s.json")

    msg = prc._fire_publish_gate_alert(
        recent=[{}], kind="test_regression", rc=1, git_hash="abc123",
        unavailable=False, send_ntfy_fn=lambda m: "sent-1",
        blocking=["tests/background/test_real_red.py::test_x"],
        markers_pending=3, total_red=1,
    )

    assert "test_real_red.py::test_x" in msg
    assert "NO TEST WAS JUDGED" not in msg


def test_the_public_banner_does_not_call_an_unjudged_suite_red():
    """R11/R9 on the ONE sentence a visitor sees. The banner reason was a single format string
    reading `scoped publish-path suite red at git=...` on EVERY refusal, so a cycle where no
    test was judged published the claim that the suite was red. MUTATION: return the same reason
    for both branches and this reds on the word `red`."""
    _, _, timeout_reason = prc._gate_refusal(True, "abc123", [])
    _, _, red_reason = prc._gate_refusal(False, "abc123", ["tests/x.py::test_y"])

    assert "UNJUDGED" in timeout_reason and "did not finish" in timeout_reason
    assert "suite red" not in timeout_reason
    assert "suite red" in red_reason and "tests/x.py::test_y" in red_reason


def test_the_refused_publish_states_one_verdict_in_one_place():
    """R10, the class rather than the instance: the exit code, the log line and the public
    banner are three statements about one cycle, and 2026-08-21 is what it looks like when they
    are authored separately (state file `test_regression`, `total_red: 0`, banner "red"). The
    publish path must therefore take all three from `_gate_refusal` and compose none of its own.

    MUTATION: re-inline the banner reason at the call site and this scan reds."""
    import inspect

    src = inspect.getsource(prc._process) if hasattr(prc, "_process") else inspect.getsource(prc)
    body = src[src.index("tests_ok, timed_out = run_fast_tests("):]
    body = body[:body.index("Move the marker to done/")]

    assert "_gate_refusal(" in body, (
        "the publish path no longer routes its refusal through the one function that names it"
    )
    assert "suite red at git=" not in body, (
        "the refusal wording is composed at the call site again -- that is how the banner and "
        "the state file came to disagree about the same cycle"
    )
