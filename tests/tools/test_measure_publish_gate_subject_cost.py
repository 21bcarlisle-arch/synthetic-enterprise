"""Controls for the OPS2 subject-cost measurement harness's CHECKPOINT contract.

The harness (`tools/measure_publish_gate_subject_cost.py`) is the evidence source for two
OPS2 exit criteria: the warm/in-tree ratio (≤ 1.3x) and the timeout floor derived from the
worst legitimate run. It is a ~50-minute, three-phase job on a box where the OOM killer is a
known visitor, so it is expected to be killed sometimes.

WHAT THESE CONTROLS ARE FOR (R15). The defect they fire on is OBSERVED, not hypothetical: the
2026-08-10 05:28 run died inside `_wait_for_quiet` and left NOTHING in the repo, so the next
tick could not distinguish "died in the wait" from "never launched" from "ran and found
nothing". The fix is a checkpoint written before the first phase and after each one — and a
checkpoint has exactly one way to be worse than useless, which is to look like a RESULT:

  1. FAIL-OPEN TO A READER KEYING ON EXISTENCE — a partial record whose `complete` flag is
     absent or true would let a reader fill in the design doc's table from phases that never
     ran. `complete` must be false until all three phases are present, and `phases_missing`
     must name the ones still owed.
  2. FAIL-LOUD ON ITS OWN WRITE — a checkpoint that raises would kill the live measurement it
     exists to protect. Losing the record must never cost the run.

MUTATION-PROVEN: setting `results["complete"] = True` unconditionally in `_checkpoint` reds
`test_a_partial_record_is_not_complete` and `test_an_aborted_record_is_not_complete`; deleting
the `except OSError` reds `test_an_unwritable_checkpoint_never_kills_the_run`.

AND FOR THE LAUNCH (2026-08-10, second section below). The checkpoint fix held; its sibling did
not, because it was never in the repo to hold. `3cc60f133` claimed the job was "launched under
setsid" and `setsid` appeared nowhere in the repository — so the ~50-minute run was still an
ad-hoc background job of a bounded tick, and it died in the quiet-wait for the second time, at
the same point, before its first phase. `--detach` is now that launch, in code, and these
controls pin the property it exists for: **a child started this way survives the death of the
process group that started it**. The differential is the point — the same scenario without the
detach is run alongside, and the undetached child dies, so the survival above is produced by
`start_new_session` and not by the kill being harmless.
"""
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import pytest

from tools import measure_publish_gate_subject_cost as measure


@pytest.fixture
def out(tmp_path):
    return str(tmp_path / "publish_gate_subject_cost.json")


def _read(path):
    with open(path) as fh:
        return json.load(fh)


def test_a_record_exists_before_the_first_phase_runs(out):
    """The 05:28 defect exactly: a run killed in the quiet-wait must still be evidenced.

    MUTATION: drop the pre-wait `_checkpoint` call in `main` and there is no file at all, which
    is indistinguishable from never having been launched."""
    measure._checkpoint({"phases": {}}, out, print)

    rec = _read(out)
    assert rec["complete"] is False
    assert rec["phases_missing"] == list(measure.PHASE_ORDER)


def test_a_partial_record_is_not_complete(out):
    """Two of three phases is not a result, and must not read as one."""
    results = {"phases": {"cold_checkout": {"seconds": 900.0},
                          "warm_checkout": {"seconds": 700.0}}}
    measure._checkpoint(results, out, print)

    rec = _read(out)
    assert rec["complete"] is False, (
        "a record missing the in-tree baseline cannot support the ratio criterion, so it must "
        "not be flagged complete"
    )
    assert rec["phases_missing"] == ["in_tree_baseline"]
    # And it must not be carrying the derived figures a reader would copy into the design doc.
    assert "ratio_warm_over_in_tree" not in rec
    assert "implied_timeout_floor_2x" not in rec


def test_a_full_record_is_complete_and_owes_nothing(out):
    """The other direction: a control that can only say "incomplete" is not a control."""
    results = {"phases": {p: {"seconds": 1.0} for p in measure.PHASE_ORDER}}
    measure._checkpoint(results, out, print)

    rec = _read(out)
    assert rec["complete"] is True
    assert rec["phases_missing"] == []


def test_an_aborted_record_is_not_complete(out):
    """An abort names its reason AND stays incomplete -- the reason is not a substitute."""
    results = {"phases": {}, "aborted": "another publisher held the reuse lock"}
    measure._checkpoint(results, out, print)

    rec = _read(out)
    assert rec["complete"] is False
    assert rec["aborted"] == "another publisher held the reuse lock"


def test_an_unwritable_checkpoint_never_kills_the_run(tmp_path):
    """Losing the record must cost the record, never the 50-minute measurement.

    MUTATION: remove the `except OSError` in `_checkpoint` and this raises."""
    logged = []
    unwritable = str(tmp_path / "no-such-dir" / "c.json")

    measure._checkpoint({"phases": {}}, unwritable, logged.append)

    assert logged, "a failed checkpoint must say so rather than fail silently"
    assert "could not checkpoint" in logged[0]


def test_every_phase_the_harness_times_is_named_in_the_phase_order():
    """PHASE_ORDER is what `phases_missing` is computed from, so a phase absent from it would
    be silently un-owed: the record would read complete with that phase never run.

    Independent oracle -- the phase KEYS are read out of `main`'s own source rather than from
    PHASE_ORDER itself, so the two cannot agree by construction (R15 TAUTOLOGY)."""
    import inspect
    import re

    src = inspect.getsource(measure._run_measurement)
    assigned = set(re.findall(r'results\["phases"\]\["(\w+)"\]', src))

    assert assigned, "no phase assignments found in _run_measurement -- this oracle has gone blind"
    assert assigned == set(measure.PHASE_ORDER), (
        f"_run_measurement times {sorted(assigned)} but PHASE_ORDER declares "
        f"{sorted(measure.PHASE_ORDER)}; a phase missing from PHASE_ORDER is never reported "
        "as owed"
    )


# ── THE LAUNCH (2026-08-10) ──────────────────────────────────────────────────────────────────

def _launcher_source(detached: bool) -> str:
    """A stand-in launcher: spawns a sleeper the same way the harness spawns itself, prints the
    sleeper's pid, and exits — leaving the sleeper as the only member of its old process group.

    The `detached=False` arm is the counterfactual, written here rather than by mutating the
    production file, so the differential runs on every suite: if the group-kill below could not
    kill an undetached child, the survival assertion would be vacuous."""
    spawn = ("measure._detached_popen(argv, None)" if detached else
             "subprocess.Popen(argv, stdin=subprocess.DEVNULL)")
    return (
        "import subprocess, sys\n"
        "sys.path.insert(0, {repo!r})\n"
        "from tools import measure_publish_gate_subject_cost as measure\n"
        "argv = [sys.executable, '-c', 'import time; time.sleep(60)']\n"
        "child = {spawn}\n"
        "print(child.pid, flush=True)\n"
    ).format(repo=str(measure.prc.PROJECT_DIR), spawn=spawn)


def _alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except (ProcessLookupError, PermissionError):
        return False
    return True


def _spawn_then_group_kill(detached: bool) -> bool:
    """Run a launcher in its own group, kill that group, and report whether its child lived."""
    launcher = subprocess.Popen([sys.executable, "-c", _launcher_source(detached)],
                                stdout=subprocess.PIPE, text=True, start_new_session=True)
    # `start_new_session` makes the launcher its own group leader, so its pgid IS its pid --
    # read here rather than after `wait()`, which reaps it and makes `getpgid` raise.
    group = launcher.pid
    try:
        child_pid = int(launcher.stdout.readline().strip())
        launcher.wait(timeout=30)
        try:
            os.killpg(group, signal.SIGKILL)
        except ProcessLookupError:
            # The group is already empty: the launcher is reaped and nothing else is in it,
            # which is itself the detached outcome. The aliveness poll below is the verdict.
            pass
        deadline = time.time() + 5
        while _alive(child_pid) and time.time() < deadline:
            time.sleep(0.1)
        return _alive(child_pid)
    finally:
        launcher.stdout.close()
        try:
            os.kill(child_pid, signal.SIGKILL)
        except (NameError, ProcessLookupError, PermissionError):
            pass


def test_a_detached_child_survives_the_death_of_its_launchers_process_group():
    """THE property the `--detach` flag exists for, and the one the un-committed `setsid` was
    supposed to provide: the ~50-minute measurement must outlive the bounded tick that starts it.

    Both arms in one test on purpose. The undetached arm is what actually happened twice on
    2026-08-10 — a run that died with its launcher, inside the quiet-wait, before phase one."""
    assert _spawn_then_group_kill(detached=False) is False, (
        "the undetached child survived a kill of its launcher's group, so this test cannot tell "
        "the two apart and the assertion below proves nothing"
    )
    assert _spawn_then_group_kill(detached=True) is True, (
        "a child started through `_detached_popen` died with its launcher's group -- the detach "
        "is not holding, and a 50-minute job started from a bounded tick will die again"
    )


def test_the_detach_flag_hands_the_run_to_a_child_that_is_not_another_launcher(monkeypatch, out):
    """`--detach` spawns the MEASUREMENT, never a second launcher: a child carrying `--detach`
    would fork forever without ever timing anything."""
    seen = {}
    # `_spawn_detached` opens the real launch log before it spawns anything; without this the
    # test would append a launch header to a live observability file on every suite run.
    monkeypatch.setattr(measure, "DETACHED_LOG_FILE", Path(out).parent / "launch-log.md")
    monkeypatch.setattr(measure, "_measurement_is_running", lambda: False)
    monkeypatch.setattr(measure, "_detached_popen",
                        lambda argv, handle: seen.setdefault("argv", argv) and None
                        or type("P", (), {"pid": 4242})())
    monkeypatch.setattr(measure, "_run_measurement",
                        lambda *a: pytest.fail("--detach must not measure inline"))

    assert measure.main(["--detach", "--out", out]) == 0
    assert "--detach" not in seen["argv"]
    assert seen["argv"][1:3] == ["-m", "tools.measure_publish_gate_subject_cost"]
    assert out in seen["argv"]


def test_without_the_flag_the_measurement_runs_in_this_process(monkeypatch, out):
    """The other direction: no flag means no spawn. A launcher that ALWAYS detached would make
    the harness impossible to run in the foreground and impossible to debug."""
    monkeypatch.setattr(measure, "_detached_popen",
                        lambda *a, **k: pytest.fail("spawned without --detach"))
    monkeypatch.setattr(measure, "_run_measurement", lambda out_path, log: 0)

    assert measure.main(["--out", out]) == 0


def test_a_second_launch_is_refused_while_a_measurement_is_live(monkeypatch, out):
    """Two concurrent runs would delete the reused checkout under each other's suite and both
    would report a wrong ratio without saying so."""
    monkeypatch.setattr(measure, "_measurement_is_running", lambda: True)
    monkeypatch.setattr(measure, "_detached_popen",
                        lambda *a, **k: pytest.fail("launched a second concurrent measurement"))

    assert measure.main(["--detach", "--out", out]) == 1


def _pgrep_returning(text):
    """Stand in for the `pgrep -af` the guard shells out to. Canned rather than observed: the
    real answer depends on whether a 50-minute measurement happens to be live on this box, and a
    control whose verdict depends on that is a flake, not a control."""
    class _Result:
        stdout = text

    return lambda *a, **k: _Result()


def test_the_liveness_guard_ignores_its_own_ancestors(monkeypatch):
    """A guard that counted the launch's OWN command line — which appears in this process, in its
    shell, and in the `bash -c` wrapper above it — would refuse every launch: a control that can
    only say no. The pytest and grep lines are here for the same reason; this module's own path
    on a test runner's argv is not a running measurement."""
    lines = "\n".join([
        "{} /usr/bin/python3 -m tools.measure_publish_gate_subject_cost --detach".format(
            os.getpid()),
        "{} /bin/bash -c python3 -m tools.measure_publish_gate_subject_cost --detach".format(
            os.getppid()),
        "99991 grep -rn measure_publish_gate_subject_cost .",
        "99992 python3 -m pytest tests/tools/test_measure_publish_gate_subject_cost.py",
    ])
    monkeypatch.setattr(measure.subprocess, "run", _pgrep_returning(lines))

    assert measure._measurement_is_running() is False
    assert str(os.getpid()) in measure._ancestor_pids()
    assert str(os.getppid()) in measure._ancestor_pids()


def test_the_liveness_guard_sees_a_foreign_measurement(monkeypatch):
    """The other direction — without this, the test above is satisfied by a guard hard-wired to
    False, and the refusal that protects the reused checkout would never fire."""
    monkeypatch.setattr(measure.subprocess, "run", _pgrep_returning(
        "99993 /usr/bin/python3 -m tools.measure_publish_gate_subject_cost --out /x.json"))

    assert measure._measurement_is_running() is True


def test_an_unavailable_liveness_check_refuses_the_launch(monkeypatch):
    """R15: an unavailable check is a FAILED check. If the guard cannot see the box it must
    refuse, not assume it is free — a double run costs 50 minutes AND a wrong ratio."""
    def _boom(*a, **k):
        raise OSError("pgrep is missing")

    monkeypatch.setattr(measure.subprocess, "run", _boom)

    assert measure._measurement_is_running() is True


def test_the_record_computes_whether_it_was_detached_rather_than_claiming_it():
    """`is_session_leader` must be asked of the kernel, not asserted by the caller. The 08:35Z
    run's detachment could only be re-typed, never checked — that is the whole finding."""
    import inspect
    import re

    src = inspect.getsource(measure._run_measurement)
    match = re.search(r'"is_session_leader":\s*([^,\n]+)', src)

    assert match, "the record no longer stamps is_session_leader"
    assert "getsid" in match.group(1), (
        "is_session_leader is set to {} -- a claimed value is exactly what could not be "
        "verified about the run that died".format(match.group(1))
    )
