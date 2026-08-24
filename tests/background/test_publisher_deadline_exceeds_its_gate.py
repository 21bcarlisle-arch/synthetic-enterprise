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
from background import publisher_budget
from background import sim_runner as sr


@pytest.fixture(scope="module", autouse=True)
def _the_publisher_log_goes_to_tmp(tmp_path_factory):
    """THIS FILE DRIVES THE REAL PUBLISHER, so its diagnostics must not reach the real record.

    The deadline-kill tests below call the detector and classifier for real, and those paths
    log. `prc.log()` appends to `docs/observability/sim-runner-log.md` -- the file the
    PUBLISHING DOWN alarm sends a human to -- so fixture rows there read as real gate verdicts.
    Same isolation the neighbouring publisher tests already apply per-test."""
    dest = tmp_path_factory.mktemp("publisher-log") / "sim-runner-log.md"
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(prc, "LOG_FILE", dest)
        yield dest


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


def test_the_sweep_derives_its_deadline_rather_than_restating_it():
    """MUTATION -- the anti-drift property, and the one a matching pair of literals would
    pass while broken: restore `return 1200` (or 900, or 4300) and this reds.

    The reference is this test process's OWN import of the publisher, which -- in a
    freshly-started interpreter -- is by definition what is on disk. Two independent paths to
    the same source; a caller that restated the number reaches neither.

    It used to `monkeypatch.setattr(prc, "PUBLISH_PATH_TIMEOUT_SECONDS", 4242)` and assert the
    helper followed. That asserted the helper read the module object in THIS process, which is
    exactly the property that turned out to be the defect (section 6) -- so the test that was
    meant to prove currency was pinning the mechanism that lost it."""
    assert bw._publisher_deadline_seconds() == prc.PUBLISH_PATH_TIMEOUT_SECONDS, (
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
def test_every_publisher_caller_derives_its_deadline(module_path, module):
    """MUTATION, per caller: restate the number anywhere in the chain and this reds.
    `sim_runner` FAILED this until 2026-08-10 -- it answered 1200 whatever the publisher
    declared, which is the whole defect as a single number."""
    assert module._publisher_deadline_seconds() == prc.PUBLISH_PATH_TIMEOUT_SECONDS, (
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


# ─────────────── 6. THE NUMBER WAS RIGHT AND THE PROCESS WAS OLD (observed 2026-08-22)
#
# Sections 1 and 4 pinned that every caller DERIVES its deadline from the publisher's declared
# budget rather than restating it. Both callers passed. Both callers were also, in production,
# using numbers the publisher had not declared for ten hours -- 1200 in `sim_runner`, 4300 in
# `background_worker` -- and their own logs printed those numbers in as many words.
#
# The derivation was never the problem. `sys.modules` was. Each helper did
#
#     from background import process_run_complete as prc   # inside the function
#     return prc.PUBLISH_PATH_TIMEOUT_SECONDS
#
# under a docstring asserting that importing at CALL time (not at module import) kept the value
# current. A lazy import is still a ONE-TIME import: after the first call the name resolves out
# of `sys.modules`, and the constant read off it is frozen at whatever was on disk when THAT
# PROCESS first published. "Call time" was true of the import statement and false of the number.
#
# OBSERVED, not inferred:
#   * `GATE_SUITE_TIMEOUT_SECONDS` was 300 from 16:10:46 to 17:28:57 on 2026-08-21 (commit
#     8d6f4a2b4, narrowing the gate's scope), then 3400, then 3800 at 18:32:27.
#   * `sim_runner` started 16:45:22 -- inside that window -- and cached 300 + 900 = 1200.
#   * docs/observability/sim-runner-log.md, four consecutive cycles 00:55Z–02:13Z on 08-22:
#     "Auto-process timed out after 1200s". The fourth died with a GREEN gate behind it,
#     mid-`git commit`, after the marker had already been archived to done/.
#   * `.publish_gate_state.json` for all four: `kind: deadline_kill`, `total_red: 0`,
#     `blocking_tests: []` -- four publish failures with no accused.
#   * `background_worker` started 17:28:59, two seconds after the 3400 commit, and its own log
#     says "TIMED OUT ... after 4300s" three times on 08-21 while the publisher declared 4700.
#     Two daemons, two different frozen values, one mechanism -- which is what makes it a class.
#
# R10 forbids closing this at the instance, and the instance here is tempting and useless: the
# constant is correct on disk RIGHT NOW, so every static test in this file passes at HEAD. The
# only fix that holds is that a caller reads the FILE, not a module object it is holding.

def test_the_publisher_budget_probe_reads_the_current_declared_value():
    """The probe is the whole mechanism, so it gets its own node: it must agree with the
    publisher this test process imported. If it drifts from that, every test below is
    measuring a number nothing else in the system uses."""
    assert (publisher_budget.declared_publisher_budget_seconds()
            == prc.PUBLISH_PATH_TIMEOUT_SECONDS)


@pytest.mark.parametrize("module_path,module", PUBLISHER_CALLERS,
                         ids=[p for p, _ in PUBLISHER_CALLERS])
def test_a_stale_in_process_publisher_does_not_decide_the_deadline(
        module_path, module, monkeypatch):
    """THE MUTATION IS THE INCIDENT. Poison the in-process module object with the exact value
    `sim_runner` was frozen on -- 1200 -- and ask the caller for its deadline.

    Pre-fix, the helper resolves `process_run_complete` out of `sys.modules`, finds 1200, and
    returns it: this test reds, which is the whole ten-hour wedge reproduced in three lines.
    Post-fix it shells out to the file and answers what the publisher declares today.

    This is deliberately the mutation the OLD version of
    `test_every_publisher_caller_derives_its_deadline` performed and ASSERTED THE OPPOSITE of
    -- it patched the module object and required the helper to follow. That test could only
    pass if the helper read the stale object, so the control proving currency was pinning the
    exact mechanism that lost it. A control can be green, honest, and aimed backwards."""
    on_disk = prc.PUBLISH_PATH_TIMEOUT_SECONDS
    monkeypatch.setattr(prc, "PUBLISH_PATH_TIMEOUT_SECONDS", 1200)

    assert module._publisher_deadline_seconds() == on_disk, (
        "{} answered a deadline from a module object held in this process rather than from "
        "the publisher on disk. That is the 2026-08-22 wedge: a daemon that started while the "
        "gate bound was transiently 300 killed four green publish cycles at 1200s over the "
        "next ten hours, while every static test in this file passed.".format(module_path)
    )


@pytest.mark.parametrize("module_path,module", PUBLISHER_CALLERS,
                         ids=[p for p, _ in PUBLISHER_CALLERS])
def test_every_caller_reaches_the_publisher_through_the_fresh_reader(module_path, module):
    """VACUITY GUARD for the test above. A caller could pass it by hard-coding a number that
    happens to equal today's budget, and the parametrised derivation test would then be the
    only thing standing -- which is precisely the pair of green tests that coexisted with the
    live defect. So assert the wiring too: the helper must go through the module whose whole
    contract is that it re-reads the file."""
    import inspect

    src = inspect.getsource(module._publisher_deadline_seconds)
    assert "publisher_budget" in src, (
        "{}._publisher_deadline_seconds() no longer routes through background.publisher_budget "
        "-- if it imports the publisher directly again, it is holding a frozen constant and "
        "nothing in this file will notice until the next wedge".format(module_path)
    )


def test_the_fallback_exceeds_the_largest_budget_the_publisher_can_declare():
    """FAIL-LONG, and the sibling instance of the same class one layer down.

    The fallback that stood until 2026-08-22 was `60 * 60` under a comment calling it
    "deliberately larger than any bound the publisher currently declares". It was 3600 against
    a declared 4700 -- a constant frozen in place while its subject grew past it, in the very
    fallback whose job is to never be too small.

    Checked against the RATCHET, not against today's value: the ratchet is the largest bound
    the publisher can ever declare and it may only fall, so this stays true without being
    re-derived every time the gate bound moves."""
    largest_declarable = (prc.PUBLISH_GATE_CEILING_RATCHET_SECONDS
                          + prc.PUBLISH_PATH_ALLOWANCE_SECONDS)
    assert publisher_budget.FALLBACK_SECONDS > largest_declarable, (
        "the fail-long fallback is {}s against a largest declarable budget of {}s -- it would "
        "kill the publisher before its own gate could answer, which is the defect the fallback "
        "exists to avoid".format(publisher_budget.FALLBACK_SECONDS, largest_declarable)
    )


def test_the_probe_answers_from_the_file_as_it_is_now(tmp_path, monkeypatch):
    """THE FRESHNESS PROPERTY AT THE PROBE ITSELF, and the reason this module exists: the same
    call, against the same name, must give two different answers when the FILE changes between
    them. An imported constant cannot do that; that is the whole incident.

    It also pins that the derived expression is EVALUATED rather than pattern-matched -- the
    budget is a sum of two constants declared above it, so a reader that only understood
    integer literals would find nothing and fall back long forever."""
    fake = tmp_path / "process_run_complete.py"
    monkeypatch.setattr(publisher_budget, "PUBLISHER_SOURCE", fake)

    fake.write_text(
        "GATE_SUITE_TIMEOUT_SECONDS = 1000\n"
        "PUBLISH_PATH_ALLOWANCE_SECONDS = 2 * 60\n"
        "PUBLISH_PATH_TIMEOUT_SECONDS = "
        "GATE_SUITE_TIMEOUT_SECONDS + PUBLISH_PATH_ALLOWANCE_SECONDS\n"
    )
    assert publisher_budget.declared_publisher_budget_seconds() == 1120

    fake.write_text(
        "GATE_SUITE_TIMEOUT_SECONDS = 3800\n"
        "PUBLISH_PATH_ALLOWANCE_SECONDS = 15 * 60\n"
        "PUBLISH_PATH_TIMEOUT_SECONDS = "
        "GATE_SUITE_TIMEOUT_SECONDS + PUBLISH_PATH_ALLOWANCE_SECONDS\n"
    )
    assert publisher_budget.declared_publisher_budget_seconds() == 4700, (
        "the probe answered the same number after the file changed -- it is caching, which is "
        "the defect it was written to end"
    )


def test_the_probe_refuses_rather_than_inventing_a_number(tmp_path, monkeypatch):
    """R15 FAIL-OPEN, the direction that would be worse than the bug. The probe must RAISE when
    the publisher will not state a budget, so the caller logs a fail-LONG fallback against the
    run it affects. A probe that returned a plausible default would put this whole class back:
    an unavailable check is a FAILED check, and a silently-defaulted deadline is unfalsifiable.

    Three ways it can fail to read, all of which must refuse rather than guess."""
    fake = tmp_path / "process_run_complete.py"
    monkeypatch.setattr(publisher_budget, "PUBLISHER_SOURCE", fake)

    # 1. the constant is gone
    fake.write_text("SOMETHING_ELSE = 5\n")
    with pytest.raises(publisher_budget.BudgetUnreadable):
        publisher_budget.declared_publisher_budget_seconds()

    # 2. it is no longer integer arithmetic this reader may evaluate. It must NOT execute the
    #    publisher's code to find out -- refusing is the safe answer, guessing is not.
    fake.write_text("PUBLISH_PATH_TIMEOUT_SECONDS = _measure_the_suite()\n")
    with pytest.raises(publisher_budget.BudgetUnreadable):
        publisher_budget.declared_publisher_budget_seconds()

    # 3. the file is not there at all
    monkeypatch.setattr(publisher_budget, "PUBLISHER_SOURCE", tmp_path / "gone.py")
    with pytest.raises(OSError):
        publisher_budget.declared_publisher_budget_seconds()


def test_the_probe_never_executes_what_it_reads():
    """The publisher's source is a file the publish path EXECUTES; this module only measures
    it. An `eval`-based reader would import-by-side-effect from inside a daemon's deadline
    calculation, which is a worse failure than the one being fixed -- and it is the shape the
    first version of this module had, which broke ten sibling tests by putting the probe on the
    same `subprocess.run` seam a publisher spawn uses.

    MUTATION: swap `_evaluate_int` for `eval(compile(...))` and this reds.

    Scanned as AST, not as text: the module's own docstring explains at length why it does not
    use `subprocess`, and a substring search over the source counted that explanation as a
    violation. A control that reads prose as code is measuring the wrong file."""
    import inspect

    tree = ast.parse(inspect.getsource(publisher_budget))

    called = {node.func.id for node in ast.walk(tree)
              if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)}
    assert not (called & {"eval", "exec", "compile", "__import__"}), (
        "the budget reader executes the publisher's source -- it must parse it; it is called "
        "from inside a daemon's deadline calculation and must not be able to run what it reads"
    )

    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert "subprocess" not in imported, (
        "the budget probe is back on the subprocess seam -- every test that stubs a publisher "
        "spawn intercepts it there, which is how ten sibling tests broke the first time"
    )
    assert "importlib" not in imported, (
        "reloading the publisher to read one integer re-runs its module body inside a daemon's "
        "deadline calculation -- the fresh READ must not become a fresh IMPORT"
    )


def test_the_callers_fallback_is_the_probes_own(tmp_path, monkeypatch):
    """The fail-long path, end to end, PER CALLER -- not merely that a constant exists.

    MUTATION: return a bare `60 * 60` in either caller's `except` (which is what both did
    until 2026-08-22) and this reds, because 3600 is not the fallback the ratchet test above
    is protecting."""
    monkeypatch.setattr(publisher_budget, "PUBLISHER_SOURCE", tmp_path / "gone.py")
    for module_path, module in PUBLISHER_CALLERS:
        assert module._publisher_deadline_seconds() == publisher_budget.FALLBACK_SECONDS, (
            "{} invents its own fallback when the publisher will not state a budget"
            .format(module_path)
        )
