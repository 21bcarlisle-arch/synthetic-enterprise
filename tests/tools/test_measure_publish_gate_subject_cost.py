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
     ran. `complete` must be false until every phase in `PHASE_ORDER` is present, and
     `phases_missing` must name the ones still owed.
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
import datetime
import fcntl
import json
import os
import shutil
import signal
import subprocess
import sys
import time
import types
from pathlib import Path

import pytest

from tools import measure_publish_gate_subject_cost as measure


@pytest.fixture
def out(tmp_path):
    return str(tmp_path / "publish_gate_subject_cost.json")


@pytest.fixture
def runnable_ceiling(monkeypatch):
    """Pin the phase as RUNNABLE, so these tests' subject is the bounded path.

    WHY (2026-08-12, the nineteenth wedge). `PHASE_CEILING_IS_SUFFICIENT` is derived at IMPORT
    from two things neither of which is a test input: the LIVE banked record
    (`docs/observability/publish_gate_subject_cost.json`) and this box's MemTotal. When a
    banked peak of 10240MB landed, `10240 * 1.25 = 12800MB` exceeded the 11816MB this box can
    spare with the publisher's reserve intact -- so `_bounded_argv` began raising `_Unbounded`
    before any of these tests reached its own subject, and nine of them reddened HEAD at once.

    That refusal is CORRECT and stays untouched: it is asserted, un-pinned, by
    `test_the_ratchet_terminates_rather_than_clamping` (the live-state check) and by the
    mutation that removes it. What is wrong is a test of the bounded path whose verdict is
    decided by how much RAM the machine happens to have -- the same shape as a stub root that
    is not repo-shaped (tests/background/publish_gate_root_shape.py).
    """
    monkeypatch.setattr(measure, "PHASE_CEILING_IS_SUFFICIENT", True)


# ── THIS MODULE RUNS INSIDE THE THING IT LOCKS, SO IT MUST NEVER TOUCH THE REAL LOCK ─────────
#
# OBSERVED, 2026-08-10, before the exclusion was committed. The phases now take
# `prc._run_lock` -- and this module is IN the publish gate's own argv, which the publisher runs
# while holding that very lock for the whole of `_process`. So the tests that drive
# `_run_measurement` (whose COLD and WARM phases enter the exclusion directly, past the stubbed
# `_time_suite`) blocked on the live publisher's lock for `QUIET_WAIT_SECONDS` = 3800s. A local
# run was killed at 900s inside `test_a_banked_phase_is_resumed_rather_than_re_run`.
#
# That is a publishing WEDGE, not a slow test, and a self-inflicted one: the gate suite would
# hang until `GATE_SUITE_TIMEOUT_SECONDS` (2600s) and the gate now fail-CLOSES on timeout, so
# every cycle would block publication -- deterministically, on the exact defect this atom exists
# to close. The lesser half is as bad in the other direction: when the lock happens to be FREE,
# a test acquires the real publisher's lock and makes live cycles lock-skip.
#
# Autouse rather than per-test, because the entry points are not all obvious -- two of the three
# phases enter the exclusion from `_run_measurement` itself, which no test opts into by name.
@pytest.fixture(autouse=True)
def _the_live_publishers_lock_is_out_of_reach(monkeypatch, tmp_path):
    """Point `_run_lock`'s file at this test's tmp dir for EVERY test in the module."""
    monkeypatch.setattr(measure.prc, "RUN_LOCK_FILE",
                        tmp_path / ".process_run_complete.lock")


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
    """One of two phases is not a result, and must not read as one.

    The retired phase is in here on purpose: a record can hold three timings and still owe the
    baseline, because two of them belong to a configuration that no longer runs."""
    results = {"phases": {"throwaway_checkout": {"seconds": 900.0, "returncode": 1},
                          "cold_checkout": {"seconds": 1291.9, "returncode": 1},
                          "warm_checkout": {"seconds": 700.0, "returncode": 1}}}
    measure._checkpoint(results, out, print)

    rec = _read(out)
    assert rec["complete"] is False, (
        "a record missing the in-tree baseline cannot support the ratio, so it must not be "
        "flagged complete"
    )
    assert rec["phases_missing"] == ["in_tree_baseline"]
    assert rec["phases_from_a_retired_configuration"] == ["cold_checkout", "warm_checkout"], (
        "a retired phase must be NAMED as retired -- unnamed, a reader counts three timings and "
        "reads a two-phase measurement as done"
    )
    # And it must not be carrying the derived figures a reader would copy into the design doc.
    assert "ratio_throwaway_over_in_tree" not in rec
    assert "implied_timeout_floor_2x" not in rec


def test_a_full_record_is_complete_and_owes_nothing(out):
    """The other direction: a control that can only say "incomplete" is not a control."""
    results = {"phases": {p: {"seconds": 1.0, "returncode": 1}
                          for p in measure.PHASE_ORDER}}
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


# ── AND FOR THE FOURTH DEATH: SESSION-DETACH IS NOT THE SAME PROTECTION AS SYSTEMD ────────────
#
# The 10:42:36Z run went through `--detach` and its own record says `is_session_leader: true`,
# so the detach HELD -- and it died anyway, 3.5 minutes in, still in the quiet-wait. The control
# above proves `--detach` survives a kill of the launcher's process GROUP. It never asked the
# other question, and these do: a session-detached child is STILL A DESCENDANT of its launcher,
# so anything that reaps a tick by walking /proc reaches it regardless of session.
#
# The differential is the point. `test_session_detach_does_not_hide_a_child_from_a_descendant
# _walk` is the counterfactual that makes the systemd assertion mean something: if a
# session-detached child were already invisible to a descendant walk, handing the job to init
# would buy nothing and the test below would pass vacuously.

def _descendants(root_pid: int) -> set:
    """Every pid whose parent chain reaches `root_pid` -- the shape of a tree-walking reaper."""
    found, pids = set(), []
    for entry in Path("/proc").iterdir():
        if entry.name.isdigit():
            pids.append(int(entry.name))
    parent_of = {}
    for pid in pids:
        try:
            stat = (Path("/proc") / str(pid) / "stat").read_text()
            parent_of[pid] = int(stat.rsplit(")", 1)[1].split()[1])
        except (OSError, IndexError, ValueError):
            continue
    for pid in parent_of:
        seen, cur = set(), pid
        while cur in parent_of and cur not in seen:
            seen.add(cur)
            cur = parent_of[cur]
            if cur == root_pid:
                found.add(pid)
                break
    return found


def test_session_detach_does_not_hide_a_child_from_a_descendant_walk():
    """THE DIAGNOSIS of the fourth death, as a control rather than a paragraph.

    `start_new_session` changes the session and the process group. It does not change the
    child's `ppid`, so a reaper that enumerates a launcher's descendants still finds it. This
    is why a run whose record says `is_session_leader: true` could still be killed inside the
    quiet-wait -- and why the escalation is init ownership, not a fifth identical launch."""
    child = measure._detached_popen([sys.executable, "-c", "import time; time.sleep(30)"], None)
    try:
        assert child.pid in _descendants(os.getpid()), (
            "a session-detached child was NOT a descendant of its launcher -- if that were so, "
            "`--detach` would already defeat a tree-walking reaper and the systemd launch below "
            "would be buying nothing"
        )
    finally:
        child.kill()
        child.wait(timeout=10)


def test_the_systemd_launch_hands_the_job_to_init_under_a_fixed_unit_name():
    """The argv is the committed launch, so its shape is asserted rather than typed.

    The FIXED unit name is load-bearing: it is what makes double-launch refusal a fact stated
    by init. Six launches got past the `pgrep` guard within three minutes on 2026-08-10 --
    correctly, since each previous child had already died -- which is precisely a guard that
    cannot see what it is guarding against."""
    argv = measure._systemd_run_argv("/tmp/out.json")

    assert argv[:2] == ["systemd-run", "--user"]
    assert "--unit={}".format(measure.MEASUREMENT_UNIT_NAME) in argv
    assert any(a.startswith("--property=WorkingDirectory=") for a in argv), (
        "without an explicit WorkingDirectory the transient unit inherits the manager's cwd and "
        "`-m tools.…` does not resolve"
    )
    assert "-m" in argv and "tools.measure_publish_gate_subject_cost" in argv
    assert "--systemd" not in argv and "--detach" not in argv, (
        "the unit must run the MEASUREMENT, not another launcher"
    )
    assert "/tmp/out.json" in argv


def test_an_unavailable_systemd_refuses_rather_than_reporting_a_launch(monkeypatch, out):
    """R15 fail-closed. A launcher that returns 0 having started nothing is the exact failure
    of the last four attempts: the next reader sees success and waits for a run that is not
    there. No systemd-run means rc != 0 and a message naming the alternative."""
    monkeypatch.setattr(measure.shutil, "which", lambda _name: None)
    monkeypatch.setattr(measure.subprocess, "run",
                        lambda *a, **k: pytest.fail("must not try to launch without systemd-run"))

    assert measure._launch_under_systemd(out, lambda _m: None) != 0


def test_a_refused_transient_unit_is_reported_as_a_failure(monkeypatch, out):
    """systemd refusing the name (a live unit already holds it) must surface as non-zero.

    This is the double-launch guard that the `pgrep` one could not be: it is asserted by init
    about its own state, not parsed by this harness out of a command line."""
    monkeypatch.setattr(measure.shutil, "which", lambda _name: "/usr/bin/systemd-run")
    monkeypatch.setattr(measure.subprocess, "run",
                        lambda *a, **k: types.SimpleNamespace(
                            returncode=1, stdout="", stderr="Unit publish-gate-subject-cost.service already exists."))

    assert measure._launch_under_systemd(out, lambda _m: None) == 1


def test_the_systemd_launch_is_refused_while_a_measurement_is_live(monkeypatch, out):
    """`--systemd` runs the same liveness guard as `--detach` before it asks init for a unit."""
    monkeypatch.setattr(measure, "_measurement_is_running", lambda: True)
    monkeypatch.setattr(measure, "_launch_under_systemd",
                        lambda *a: pytest.fail("a second measurement must never be launched"))

    assert measure.main(["--systemd", "--out", out]) == 1


def test_the_record_computes_how_it_was_launched_rather_than_being_told():
    """Same discipline as `is_session_leader`, one level finer. The fourth death showed that
    "detached" is not one property but two -- group-kill survival and descendant-walk
    invisibility -- so the record must say WHICH one the run had."""
    import inspect
    import re

    src = inspect.getsource(measure._run_measurement)
    assert '"launched_by": _launched_by()' in src, "the record no longer stamps launched_by"

    fn = inspect.getsource(measure._launched_by)
    assert "INVOCATION_ID" in fn and "getsid" in fn, (
        "launched_by must be derived from the environment systemd sets and from the kernel's "
        "own answer about this process -- a hardcoded string is what could not be verified "
        "about the runs that died"
    )
    del re


def test_launched_by_says_systemd_only_when_systemd_actually_started_the_process(monkeypatch):
    """BEHAVIOURAL, because the source-reading version of this test was itself fail-open: it
    passed against a `_launched_by` that returned "systemd" unconditionally (mutation M5,
    2026-08-10). A stamp that always says systemd is worse than no stamp -- the whole reason it
    exists is to let the NEXT reader of a dead run's record tell which protection it had.

    Both directions, so neither arm can pass vacuously."""
    monkeypatch.delenv("INVOCATION_ID", raising=False)
    without = measure._launched_by()
    assert without != "systemd", (
        "launched_by claimed systemd with no INVOCATION_ID in the environment -- it is asserting, "
        "not observing"
    )
    assert without in ("session-detach", "inline", "unknown")

    monkeypatch.setenv("INVOCATION_ID", "a6a7087cea2f4c8682621049f22fbc50")
    assert measure._launched_by() == "systemd", (
        "a process systemd really did start is not recorded as systemd-launched"
    )


# ── RESUME: the checkpoint is only worth writing if something READS it ───────────────────────
#
# The harness has been killed five times: twice by a bounded tick ending under it, once by a
# descendant walk the session-detach could not hide it from, and -- the fifth, the first one
# init owned -- by the kernel OOM killer 6m20s into phase 2, with phase 1's 1291.9s already
# banked on disk. Until this suite existed, launch six would have deleted the reused checkout
# and re-paid that 21 minutes, and a run that never survives its whole phase set in a row never
# converges. Both directions on every property below.


def _stub_phases(monkeypatch, timed):
    """Make the phases instantaneous and record which ones actually ran."""
    def _fake_time_suite(cwd, log, heartbeat=None):
        timed.append(str(cwd))
        return {"cwd": str(cwd), "head_sha_at_run": "deadbeef", "seconds": 1.0,
                "returncode": 0, "summary": "", "loadavg_before": 0.0, "loadavg_after": 0.0,
                "box_was_quiet": True}
    monkeypatch.setattr(measure, "_time_suite", _fake_time_suite)
    monkeypatch.setattr(measure, "_wait_for_quiet", lambda log, hb=None: True)
    monkeypatch.setattr(measure.prc, "_head_sha", lambda: "deadbeef")


def _materialised(path):
    """Make `path` look like a checkout that actually EXTRACTED, not just one that was mkdir'd.

    A bare `mkdir` stands in for a state the harness produces only when it has FAILED: on
    2026-08-12 `git init` died with `fatal: cannot mkdir`, the directory existed and held
    nothing, and the gate ran the full suite against it (see publish_scope.ROOT_REPO_MARKER --
    28 cycles in 32 hours). The gate now refuses that root, so a fixture that keeps supplying
    it is supplying the defect rather than the subject
    (`feedback_a_render_harness_that_hand_types_its_call_list_supplies_the_defect`).

    Built from the marker constant rather than a literal for the same reason the prefix is:
    a rename must not leave these fixtures standing in for a shape nothing produces."""
    from background import publish_scope

    (path / publish_scope.ROOT_REPO_MARKER).mkdir(parents=True, exist_ok=True)
    return path


def _a_throwaway(tmp_path):
    """A directory named the way `prc._head_checkout()` names one since the R3 elimination.

    Built from `prc.HEAD_CHECKOUT_PREFIX` rather than a literal, so a rename of the real prefix
    cannot leave these tests standing in for a shape the harness no longer produces."""
    path = tmp_path / (measure.prc.HEAD_CHECKOUT_PREFIX + "kf3p1x")
    path.mkdir()
    return _materialised(path)


class _FakeCheckout:
    """Stands in for prc._head_checkout(), yielding whatever directory the caller passes."""

    def __init__(self, path):
        self._path = path

    def __call__(self):
        return self

    def __enter__(self):
        return self._path

    def __exit__(self, *exc):
        return False


def _banked(out_path, **phases):
    """Seed a prior launch's record. Phases get a COMPLETED returncode unless one is given.

    A real banked phase always carries the returncode its suite exited with, and since
    2026-08-11 that is what `_is_ratio_eligible` reads to decide whether the phase answered or
    was killed mid-suite. A fixture that omitted it would be asserting the resume against a
    record no launch produces -- so the default is stamped here, and a test that means to bank a
    TRUNCATED phase says so explicitly (`returncode=-15`)."""
    stamped = {name: (rec if "returncode" in rec else dict(rec, returncode=1))
               for name, rec in phases.items()}
    Path(out_path).write_text(json.dumps({"phases": stamped}))


def test_a_banked_phase_is_resumed_rather_than_re_run(monkeypatch, out, tmp_path):
    """THE defect: `_run_measurement` opened with `phases: {}` while the comment above
    PHASE_ORDER claimed a partial record "tells the next tick precisely which phases to resume
    rather than restart". It told it nothing, because nothing read it.

    MUTATION: seed `results["phases"]` with `{}` instead of `_load_banked_phases(out_path)` and
    the throwaway phase is timed again -- this reds."""
    throwaway = _a_throwaway(tmp_path)
    monkeypatch.setattr(measure.prc, "_head_checkout", _FakeCheckout(throwaway))
    timed = []
    _stub_phases(monkeypatch, timed)
    _banked(out, throwaway_checkout={"seconds": 1291.9, "head_sha_at_run": "deadbeef"})

    assert measure._run_measurement(out, lambda m: None) == 0

    record = _read(out)
    assert record["resumed_phases"] == ["throwaway_checkout"]
    assert record["phases"]["throwaway_checkout"]["seconds"] == 1291.9, (
        "the banked phase was overwritten -- 21 minutes of measured runtime re-paid"
    )
    assert len(timed) == 1, "a resumed run re-timed a phase it already had: {}".format(timed)
    assert record["complete"] is True


def test_without_a_partial_record_both_phases_are_timed(monkeypatch, out, tmp_path):
    """The other direction. A resume that skipped phases it never had would report a ratio
    built from nothing, which is worse than re-running them."""
    throwaway = _a_throwaway(tmp_path)
    monkeypatch.setattr(measure.prc, "_head_checkout", _FakeCheckout(throwaway))
    timed = []
    _stub_phases(monkeypatch, timed)

    assert measure._run_measurement(out, lambda m: None) == 0
    assert len(timed) == 2
    assert _read(out)["resumed_phases"] == []


def test_a_phase_with_no_duration_is_not_treated_as_banked(monkeypatch, out, tmp_path):
    """A half-written checkpoint must not retire a phase that was never timed. The record is
    rewritten on every heartbeat, so a run killed mid-write is the expected case, not the
    exotic one."""
    throwaway = _a_throwaway(tmp_path)
    monkeypatch.setattr(measure.prc, "_head_checkout", _FakeCheckout(throwaway))
    timed = []
    _stub_phases(monkeypatch, timed)
    _banked(out, throwaway_checkout={"head_sha_at_run": "deadbeef"})  # no `seconds`

    measure._run_measurement(out, lambda m: None)
    assert len(timed) == 2, "a phase with no measured duration was accepted as measured"


def test_an_unparseable_record_starts_over_rather_than_raising(out):
    """Never raises: a corrupt record must cost a re-measurement, never the launch."""
    Path(out).write_text("{ not json")
    assert measure._load_banked_phases(out) == {}
    assert measure._load_banked_phases(str(Path(out).parent / "absent.json")) == {}


def test_the_record_names_a_phase_timed_at_a_different_commit(monkeypatch, out, tmp_path):
    """Resuming across launches is what makes this converge on a box that keeps killing it --
    and it means the record can span commits. A reader who assumed one SHA would compare
    runtimes of two different suites without knowing it."""
    throwaway = _a_throwaway(tmp_path)
    monkeypatch.setattr(measure.prc, "_head_checkout", _FakeCheckout(throwaway))
    _stub_phases(monkeypatch, [])
    _banked(out, cold_checkout={"seconds": 1291.9, "head_sha_at_run": "3ee4541a7"})

    measure._run_measurement(out, lambda m: None)
    record = _read(out)
    assert record["phases_from_an_earlier_head"] == ["cold_checkout"]
    # And the other direction: a phase timed at THIS head is not flagged as stale.
    assert "throwaway_checkout" not in record["phases_from_an_earlier_head"]


# ── THE ELIMINATION MOVED THE SUBJECT, AND THE INSTRUMENT'S PRECONDITION WAS THE OLD ONE ─────
#
# 444402ee0 set `prc.REUSE_HEAD_CHECKOUT = False` under R3. Both checkout phases here were gated
# on `path.name != prc.REUSED_HEAD_CHECKOUT_NAME` -> abort, so from that commit every launch
# aborted before timing anything, recording the pre-written cause "another publisher held the
# reuse lock" -- a lock with nothing left to protect, pointing the next diagnosis at a mechanism
# that had been deleted. The consumer is fail-CLOSED (`prc.measured_gate_timeout_floor` reds the
# gate on a record that cannot answer), so an instrument that can never refresh its record is a
# control counting down.
#
# Both directions below: the throwaway IS timed, and a reused directory is refused.


def test_a_throwaway_checkout_is_timed_rather_than_aborted(monkeypatch, out, tmp_path):
    """THE defect this repair closes. Pre-fix this exact input aborted with `returncode 1` and
    a false reason; the phase set could not converge because it could not start.

    MUTATION: restore `if path.name != prc.REUSED_HEAD_CHECKOUT_NAME: abort` and this reds."""
    throwaway = _a_throwaway(tmp_path)
    monkeypatch.setattr(measure.prc, "_head_checkout", _FakeCheckout(throwaway))
    timed = []
    _stub_phases(monkeypatch, timed)

    assert measure._run_measurement(out, lambda m: None) == 0
    rec = _read(out)
    assert "aborted" not in rec, "a throwaway checkout -- the shipped subject -- was refused"
    assert str(throwaway) in timed, (
        "the throwaway phase never reached the suite: timed {}".format(timed))
    assert rec["phases"]["throwaway_checkout"]["cwd"] == str(throwaway)


def test_a_reused_checkout_is_refused_rather_than_timed_as_a_throwaway(monkeypatch, out,
                                                                       tmp_path):
    """The inverted precondition, and it is a LIVE guard rather than the dead one it replaced:
    a shared directory can only appear if `REUSE_HEAD_CHECKOUT` is turned back on, and then this
    phase would be timing a WARM subject and filing it as the cost of a cold one.

    MUTATION: drop the `path.name == REUSED_HEAD_CHECKOUT_NAME` branch and this reds -- the
    record banks a warm runtime under the throwaway phase's name."""
    reused = tmp_path / measure.prc.REUSED_HEAD_CHECKOUT_NAME
    reused.mkdir()
    _materialised(reused)
    monkeypatch.setattr(measure.prc, "_head_checkout", _FakeCheckout(reused))
    timed = []
    _stub_phases(monkeypatch, timed)

    assert measure._run_measurement(out, lambda m: None) == 1
    rec = _read(out)
    assert rec["aborted"] == "reuse is enabled, so there is no throwaway to time"
    assert "reuse lock" not in rec["aborted"], (
        "the abort still names the reuse lock -- the false cause the old precondition wrote on "
        "every launch"
    )
    assert timed == [], "a warm subject was timed and would have been filed as the throwaway"
    assert "throwaway_checkout" not in rec["phases"]


def test_no_abort_in_this_harness_blames_a_lock_that_no_longer_exists():
    """The specific regression, pinned by an independent oracle: the harness's SOURCE, not its
    behaviour on one input. The defect was not that a check existed but that its failure text
    was pre-written and false, so a reader diagnosing nine dead launches was sent to the reuse
    lock. `_run_measurement` may not carry that sentence again."""
    import inspect

    src = inspect.getsource(measure._run_measurement)
    assert "held the reuse lock" not in src, (
        "the false pre-written cause is back in _run_measurement -- since 444402ee0 there is no "
        "reuse lock to hold, and this string sent the last nine diagnoses to a deleted mechanism"
    )


# ── A RETIRED PHASE IS STILL A MEASUREMENT, AND A FAIL-CLOSED CONTROL IS EATING IT ────────────


def test_a_retired_phase_keeps_feeding_the_fail_closed_timeout_floor(monkeypatch, out, tmp_path):
    """`prc.measured_gate_timeout_floor` reads THIS record, and a record that cannot answer is a
    FAILED check that reds the gate. `_run_measurement` rewrites the file before its first phase,
    so a resume that dropped retired phases would blank the floor's only evidence -- 1291.9s of
    banked `cold_checkout` -- at the instant this harness next launched.

    MUTATION: drop `RETIRED_PHASES` from `_load_banked_phases`'s keepable set and the floor goes
    None here, i.e. publishing wedges on a control that was working."""
    throwaway = _a_throwaway(tmp_path)
    monkeypatch.setattr(measure.prc, "_head_checkout", _FakeCheckout(throwaway))
    _stub_phases(monkeypatch, [])
    _banked(out, cold_checkout={"seconds": 1291.9, "head_sha_at_run": "3ee4541a7"})

    measure._run_measurement(out, lambda m: None)

    rec = _read(out)
    assert rec["phases"]["cold_checkout"]["seconds"] == 1291.9
    assert rec["phases_from_a_retired_configuration"] == ["cold_checkout"]
    floor = measure.prc.measured_gate_timeout_floor(out)
    assert floor is not None, "the retired phase was dropped and the fail-closed floor went blind"
    assert floor >= int(1291.9 * measure.prc.GATE_TIMEOUT_SAFETY_FACTOR)


def test_a_retired_phase_never_enters_the_ratio(monkeypatch, out, tmp_path):
    """The other direction of the same rule. The ratio is throwaway/in-tree; a retired phase in
    the numerator would report the cost of a directory that no longer exists.

    MUTATION: compute the ratio over the worst phase instead of `throwaway_checkout` and this
    reds -- 1291.9/1.0 rather than 1.0/1.0."""
    throwaway = _a_throwaway(tmp_path)
    monkeypatch.setattr(measure.prc, "_head_checkout", _FakeCheckout(throwaway))
    _stub_phases(monkeypatch, [])  # both live phases time at 1.0s
    _banked(out, cold_checkout={"seconds": 1291.9, "head_sha_at_run": "3ee4541a7"})

    measure._run_measurement(out, lambda m: None)

    rec = _read(out)
    assert rec["ratio_throwaway_over_in_tree"] == 1.0
    assert rec["complete"] is True, "a retired phase must not be able to owe a live one"
    assert "cold_checkout" not in measure.RATIO_PHASES


def test_the_floor_names_the_phase_it_rests_on(monkeypatch, out, tmp_path):
    """The bound must clear the WORST legitimate runtime, retired phases included -- they are
    real timings of this suite on this box and can only push it up. Naming the phase is what
    lets a reader tell a bound resting on a live subject from one resting on a dead one, which
    is exactly the confusion that let 2600s sit on a directory that had been deleted.

    MUTATION: take `worst` over `RATIO_PHASES` only and the floor drops from 2583 to 2."""
    throwaway = _a_throwaway(tmp_path)
    monkeypatch.setattr(measure.prc, "_head_checkout", _FakeCheckout(throwaway))
    _stub_phases(monkeypatch, [])
    _banked(out, cold_checkout={"seconds": 1291.9, "head_sha_at_run": "3ee4541a7"})

    measure._run_measurement(out, lambda m: None)

    rec = _read(out)
    assert rec["worst_legitimate_phase"] == "cold_checkout"
    assert rec["worst_legitimate_seconds"] == 1291.9
    assert rec["implied_timeout_floor_2x"] == 2583


def test_the_superseded_criterion_is_stated_rather_than_scored(monkeypatch, out, tmp_path):
    """Criterion 1 asked for <= 1.3x against a REUSED checkout. Reuse is gone, so the question
    has no measurable subject -- and a harness that kept emitting `meets_exit_criterion` would
    let a superseded criterion read as MET on a comparison it did not make. The ratio is
    reported as the TAX and the supersession is in the artefact, not only in a build note."""
    throwaway = _a_throwaway(tmp_path)
    monkeypatch.setattr(measure.prc, "_head_checkout", _FakeCheckout(throwaway))
    _stub_phases(monkeypatch, [])

    measure._run_measurement(out, lambda m: None)

    rec = _read(out)
    assert "meets_exit_criterion" not in rec, (
        "a verdict against a criterion whose subject no longer exists is a pass nobody earned"
    )
    assert "ratio_warm_over_in_tree" not in rec
    assert rec["ratio_throwaway_over_in_tree"] is not None
    assert "TAX" in rec["ratio_measures"]
    assert "444402ee0" in rec["superseded_exit_criterion"]["superseded_by"]


# ── /tmp IS RAM: the reclaim that stopped the OOM ────────────────────────────────────────────


def test_every_timed_phase_gets_its_own_basetemp(monkeypatch):
    """Phase 1 left 2.0G of pytest temp roots in a 7.8G tmpfs -- which is RAM -- and phase 2
    started a full suite on top of them and was OOM-killed. pytest clears `--basetemp` at the
    start of each run, so at most one phase's temps exist at a time.

    MUTATION: drop the `--basetemp` from `_argv_without_x` and this reds."""
    argv = measure._argv_without_x()
    basetemps = [a for a in argv if a.startswith("--basetemp=")]
    assert len(basetemps) == 1, "expected exactly one --basetemp, got {}".format(basetemps)
    assert "-x" not in argv, "-x makes a red run's duration a time-to-first-failure"


def test_the_measurements_basetemp_is_on_the_same_filesystem_as_the_real_gates():
    """The runtime IS the measurement and the timeout is derived from it, so the temps must
    stay where the real gate puts them. Moving them off tmpfs would buy headroom by measuring a
    different machine."""
    basetemp = measure.prc.HEAD_CHECKOUT_ROOT / measure.MEASURE_BASETEMP_NAME
    assert basetemp.parent == measure.prc.HEAD_CHECKOUT_ROOT


def test_the_basetemp_leak_is_reclaimed_by_the_gates_own_sweep(tmp_path, monkeypatch):
    """`finally:` does not run under SIGKILL and this harness has now been SIGKILLed twice, so
    the basetemp WILL leak. It is named under HEAD_CHECKOUT_PREFIX for exactly that reason --
    the machine's own sweep already owns anything wearing that name.

    MUTATION: rename MEASURE_BASETEMP_NAME to anything outside the prefix and this reds, which
    is the fifteenth wedge's lesson (debris nothing owns is debris nobody reclaims)."""
    monkeypatch.setattr(measure.prc, "HEAD_CHECKOUT_ROOT", tmp_path)
    leaked = tmp_path / measure.MEASURE_BASETEMP_NAME
    leaked.mkdir()
    (leaked / "junk").write_text("x" * 100)
    stale = time.time() - measure.prc.STALE_HEAD_CHECKOUT_AGE_SECONDS - 60
    os.utime(leaked, (stale, stale))

    assert measure.prc._sweep_stale_head_checkouts() == 1
    assert not leaked.exists(), (
        "the measurement's basetemp is invisible to the sweep that owns /tmp debris"
    )


def test_a_live_basetemp_is_never_swept_from_under_a_running_measurement(tmp_path, monkeypatch):
    """The other direction. A sweep that took the temp dir out from under a running suite would
    turn a slow measurement into a corrupt one."""
    monkeypatch.setattr(measure.prc, "HEAD_CHECKOUT_ROOT", tmp_path)
    live = tmp_path / measure.MEASURE_BASETEMP_NAME
    live.mkdir()

    assert measure.prc._sweep_stale_head_checkouts() == 0
    assert live.exists()


def test_a_phase_waits_for_memory_headroom_before_timing(monkeypatch):
    """The fifth launch died with 6.5G peak on a 15G box whose /tmp already held 3.5G of RAM.
    Starting a full suite into a box with no room left is the observed failure.

    MUTATION: return True unconditionally from `_wait_for_memory_headroom` and this reds."""
    readings = iter([128, 128, 99999])
    monkeypatch.setattr(measure, "_mem_available_mb", lambda: next(readings))
    monkeypatch.setattr(measure.time, "sleep", lambda _s: None)
    beats = []

    assert measure._wait_for_memory_headroom(lambda m: None, lambda: beats.append(1)) is True
    assert beats, "waited for memory without heartbeating -- a record that stops advancing " \
                  "must be distinguishable from a process that died"


def test_a_starved_box_is_deferred_not_measured_anyway(monkeypatch):
    """SUPERSEDED CONTRACT, kept under its old subject so the change is legible rather than
    silently deleted. This test used to assert `is False` -- that the starved box was measured
    anyway and the number merely FLAGGED. Two launches were OOM-killed proving the flag was not
    the point, and the survivable version of that path biases the exit-criterion ratio toward
    MEETS (the contended phase is the denominator). A flag on a number that gets used anyway is
    decoration; refusing to produce the number is the control."""
    monkeypatch.setattr(measure, "_mem_available_mb", lambda: 1)
    monkeypatch.setattr(measure, "MEMORY_WAIT_SECONDS", -1)
    monkeypatch.setattr(measure.time, "sleep", lambda _s: None)

    with pytest.raises(measure._Deferred):
        measure._wait_for_memory_headroom(lambda m: None)


def test_an_unreadable_meminfo_does_not_block_the_measurement(monkeypatch):
    """DELIBERATE fail-open, and it is the right direction here: this is a measurement harness,
    not a safety control. Refusing to measure because /proc is unreadable would trade a known
    intermittent failure for a permanent one."""
    monkeypatch.setattr(measure, "_mem_available_mb", lambda: None)
    assert measure._wait_for_memory_headroom(lambda m: None) is True


# ── THE UNIT NAME MUST BLOCK A LIVE RUN, NOT A DEAD ONE ──────────────────────────────────────


class _FakeSystemctl:
    """Canned `systemctl` replies, recording which subcommands were issued."""

    def __init__(self, active_reply):
        self.active_reply = active_reply
        self.calls = []

    def __call__(self, argv, **kwargs):
        self.calls.append(argv[2] if len(argv) > 2 else "")
        if argv[2:3] == ["is-active"]:
            return subprocess.CompletedProcess(argv, 0, stdout=self.active_reply, stderr="")
        return subprocess.CompletedProcess(argv, 0, stdout="", stderr="")


def test_a_failed_unit_is_cleared_so_the_next_launch_is_not_blocked_forever(monkeypatch, out):
    """OBSERVED on the launch right after the OOM. systemd keeps a FAILED unit loaded, and the
    refusal it produces is byte-identical to a live unit's -- so nothing ever cleared the corpse
    and every future launch would have been refused by a measurement that died hours earlier.

    DRIVEN THROUGH `_launch_under_systemd`, not through the helper. The first version of this
    test called `_clear_a_failed_unit` directly and PASSED against a launcher with the call
    deleted -- a control that proves a helper works while the only caller no longer reaches it.

    MUTATION: drop the `_clear_a_failed_unit(log)` call from `_launch_under_systemd` and this
    reds."""
    fake = _FakeSystemctl("failed\n")
    monkeypatch.setattr(measure.subprocess, "run", fake)
    monkeypatch.setattr(measure.shutil, "which", lambda _n: "/usr/bin/systemd-run")
    monkeypatch.setattr(measure, "_record_launch_header", lambda _how: None)

    assert measure._launch_under_systemd(out, lambda m: None) == 0
    assert "reset-failed" in fake.calls, (
        "the LAUNCHER left a dead unit's name holding the launch slot -- the corpse-clearing "
        "helper exists but nothing on the launch path calls it"
    )


def test_a_live_unit_is_never_reset_out_from_under_itself(monkeypatch):
    """The other direction, and the one that matters more: resetting an ACTIVE unit would free
    the name for a second measurement, and two of these delete the reused checkout under each
    other's suite."""
    fake = _FakeSystemctl("active\n")
    monkeypatch.setattr(measure.subprocess, "run", fake)

    measure._clear_a_failed_unit(lambda m: None)
    assert "reset-failed" not in fake.calls, (
        "reset a LIVE measurement's unit -- the fixed-name protection is gone"
    )


def test_an_unreadable_systemctl_is_treated_as_active(monkeypatch):
    """FAIL-CLOSED, unlike the memory pre-flight, and deliberately the other way round: this one
    guards against starting a second suite beside a live one, so an unavailable check is a
    failed check (R15)."""
    def _boom(*a, **k):
        raise OSError("systemctl gone")
    monkeypatch.setattr(measure.subprocess, "run", _boom)

    assert measure._unit_is_active() is True


# ── THE ADMISSION GUARDS DEFER; THEY NEVER MEASURE ANYWAY ────────────────────────────────────
#
# The seventh launch (2026-08-10) was OOM-killed 14 minutes into the BASELINE phase, which it
# had entered deliberately alongside a live publisher because the quiet-wait's timeout fell
# through to "measuring anyway, flagged contended". The sixth died the same way in WARM.
#
# The kill is the cheap half of the defect. The expensive half is the run that SURVIVES
# contention: the exit criterion is warm / in-tree <= 1.3 and the contended phase is IN_TREE,
# the DENOMINATOR -- so a slow, contended baseline makes the ratio smaller and the criterion
# likelier to read MEETS. That is fail-open in the R15 sense: the guard's degraded mode moves
# the verdict in the passing direction, and it does so silently, because `box_was_quiet: false`
# lives inside a phase record while `meets_exit_criterion` is what anyone reads.

def test_the_quiet_wait_defers_rather_than_measuring_into_a_live_publisher(monkeypatch):
    """MUTATION: restore `return False` in place of the raise and this reds -- the caller then
    proceeds to time a suite beside the publisher, which is the OOM."""
    monkeypatch.setattr(measure, "_publisher_is_running", lambda: True)
    monkeypatch.setattr(measure, "QUIET_WAIT_SECONDS", -1)  # already past the deadline

    with pytest.raises(measure._Deferred) as excinfo:
        measure._wait_for_quiet(lambda _m: None)
    assert "publisher still live" in str(excinfo.value)


def test_the_memory_wait_defers_rather_than_measuring_into_an_exhausted_box(monkeypatch):
    """Same defect, the other guard. MUTATION: `return False` instead of the raise and this
    reds."""
    monkeypatch.setattr(measure, "_mem_available_mb", lambda: 128)
    monkeypatch.setattr(measure, "MEMORY_WAIT_SECONDS", -1)

    with pytest.raises(measure._Deferred) as excinfo:
        measure._wait_for_memory_headroom(lambda _m: None)
    assert "128MB available" in str(excinfo.value)


def test_both_guards_pass_through_when_the_box_is_actually_fit(monkeypatch):
    """The other direction -- a guard that can only refuse would never let the measurement land,
    which is the failure mode the deferral trade takes on."""
    monkeypatch.setattr(measure, "_publisher_is_running", lambda: False)
    monkeypatch.setattr(measure, "_mem_available_mb",
                        lambda: measure.MIN_MEMORY_HEADROOM_MB + 1)

    assert measure._wait_for_quiet(lambda _m: None) is True
    assert measure._wait_for_memory_headroom(lambda _m: None) is True


def test_a_deferral_banks_what_is_measured_and_times_no_suite(monkeypatch, out):
    """The whole point of deferring rather than dying: the phases already paid for survive, the
    record says why it stopped, and the exit code is 0 because a deferral is a correct outcome
    (a non-zero exit makes the systemd unit report `failed` for a run that did the right thing).

    MUTATION: drop the `except _Deferred` handler in `_run_measurement` and this reds with the
    exception escaping -- the unit dies and the record never names a reason."""
    # Stamped with the launch's own HEAD so the banked phase is COMPARABLE and survives on its
    # merits. `_drop_incomparable_ratio_phases` would otherwise re-time it here -- correctly,
    # but for a reason this test is not about, and the deferral contract below would then be
    # asserted against a resume state no real record produces. The retired `cold_checkout` rides
    # along because a deferral must not lose it either: it is the timeout floor's evidence.
    # It carries its `returncode` for the same reason: since 2026-08-11 a phase that cannot prove
    # its suite ended under its own control is re-timed rather than banked, so a returncode-less
    # fixture would make this test assert the deferral contract against the WRONG owed phase.
    monkeypatch.setattr(measure.prc, "_head_sha", lambda: "headsha0")
    banked = {"phases": {"cold_checkout": {"seconds": 1291.9, "head_sha_at_run": "old111"},
                         "throwaway_checkout": {"seconds": 1167.5, "returncode": 1,
                                                "head_sha_at_run": "headsha0"}}}
    Path(out).write_text(json.dumps(banked))

    # The guards are driven through their REAL code path -- patching `_time_suite` would bypass
    # the very calls under test. `subprocess.run` is the honest witness for "did it time a
    # suite": that is the pytest invocation whose wall-clock IS the measurement.
    timed = []

    def _record_run(argv, *a, **k):
        # Only a SUITE counts. The harness also shells out to `git rev-parse` and friends, and
        # counting those would make this assert on plumbing rather than on the 20-minute run
        # that is the actual OOM risk.
        if any("pytest" in str(part) for part in argv):
            timed.append(argv)
        return types.SimpleNamespace(returncode=0, stdout="1 passed in 1.00s", stderr="")

    monkeypatch.setattr(measure.subprocess, "run", _record_run)
    monkeypatch.setattr(measure, "_publisher_is_running", lambda: True)
    monkeypatch.setattr(measure, "QUIET_WAIT_SECONDS", -1)

    assert measure._run_measurement(out, lambda _m: None) == 0

    rec = _read(out)
    assert timed == [], "a deferred run timed a suite anyway -- that is the OOM path"
    assert "publisher still live" in rec["deferred"]["reason"]
    assert rec["deferred"]["at_phase"] == "in_tree_baseline", (
        "the deferral must name the phase still owed, or the next launch cannot tell what to "
        "resume"
    )
    assert rec["complete"] is False
    assert rec["phases_missing"] == ["in_tree_baseline"]
    assert rec["phases"]["throwaway_checkout"]["seconds"] == 1167.5, (
        "a deferral threw away a banked phase -- 21 minutes of measurement lost per deferral"
    )
    assert rec["phases"]["cold_checkout"]["seconds"] == 1291.9, (
        "a deferral dropped the retired phase the fail-closed timeout floor rests on"
    )


def test_repeated_deferrals_accumulate_a_visible_count(monkeypatch, out):
    """The convergence risk the deferral takes on -- a box that is never quiet long enough --
    must surface as a rising number in the artefact, not as a measurement that silently never
    lands.

    MUTATION: make `_prior_deferral_count` return 0 unconditionally and this reds at the second
    deferral, which is exactly the blindness it guards.

    It defers at the guard that now fires FIRST -- the exclusion, held here on the redirected
    lock -- rather than at a stubbed `_wait_for_quiet`. That is not cosmetic: with the wait
    stubbed, a run reaches the throwaway phase's REAL `prc._head_checkout()` first, so the test
    extracted HEAD into /tmp and its verdict turned on the state of a directory outside it."""
    monkeypatch.setattr(measure, "QUIET_WAIT_SECONDS", -1)  # already past the acquire deadline
    holder = open(str(measure.prc.RUN_LOCK_FILE), "w")
    fcntl.flock(holder, fcntl.LOCK_EX | fcntl.LOCK_NB)
    try:
        for expected in (1, 2, 3):
            assert measure._run_measurement(out, lambda _m: None) == 0
            record = _read(out)
            assert record["deferral_count"] == expected
            assert record["deferred"]["at_phase"] == "throwaway_checkout", (
                "the deferral must name the phase still owed")
    finally:
        fcntl.flock(holder, fcntl.LOCK_UN)
        holder.close()


def test_a_banked_phase_was_always_admitted_quiet(monkeypatch, out, runnable_ceiling):
    """The invariant the deferral buys, asserted on the ARTEFACT rather than argued in a
    comment: no phase can be banked with `box_was_quiet: false`, so the ratio can never be
    computed from a contended number.

    Independent of the guards' own code -- it reads the record the run produced (R15
    TAUTOLOGY)."""
    monkeypatch.setattr(measure, "_publisher_is_running", lambda: False)
    monkeypatch.setattr(measure, "_mem_available_mb",
                        lambda: measure.MIN_MEMORY_HEADROOM_MB + 1)
    monkeypatch.setattr(measure.subprocess, "run",
                        lambda *a, **k: types.SimpleNamespace(
                            returncode=0, stdout="1 passed in 1.00s", stderr=""))
    monkeypatch.setattr(measure.prc, "_head_sha", lambda: "deadbeef")

    phase = measure._time_suite(Path("."), lambda _m: None)

    assert phase["box_was_quiet"] is True
    assert phase["had_memory_headroom"] is True


def test_the_live_record_carries_no_contended_phase():
    """The same invariant, applied to the record actually on disk. A phase banked before this
    fix could carry `box_was_quiet: false`, and the ratio derived from it would be wrong in the
    PASSING direction -- so it must be re-run, not inherited."""
    live = measure.prc.PROJECT_DIR / "docs" / "observability" / "publish_gate_subject_cost.json"
    if not live.exists():
        pytest.skip("no live measurement record yet")
    rec = json.loads(live.read_text())

    contended = sorted(name for name, p in (rec.get("phases") or {}).items()
                       if isinstance(p, dict)
                       and (p.get("box_was_quiet") is False
                            or p.get("had_memory_headroom") is False))
    assert not contended, (
        f"banked phases {contended} were timed against a contended box; the exit-criterion "
        "ratio must not be computed from them -- delete those phases from the record so the "
        "next launch re-runs them"
    )


# ── THE EXCLUSION: A PHASE TAKES THE PUBLISHER'S GAP, IT DOES NOT WAIT FOR ONE ───────────────
#
# THE DEFECT THESE FIRE ON IS OBSERVED, not hypothetical. Nine launches; `deferral_count`
# climbing; `in_tree_baseline` -- the exit criterion's DENOMINATOR -- never once timed. The
# 2026-08-10 19:55Z launch resumed both banked phases and then deferred at 20:40:05Z with
# *"publisher still live after 2700s"*. With 112 `run_complete_*.md` markers pending and a
# publish cycle now bounded at `GATE_SUITE_TIMEOUT_SECONDS` (2600s), the publisher runs nearly
# back-to-back: waiting for a gap in that queue is not a slow control, it is a control that
# cannot fire, and it fails INVISIBLY -- every banked phase looks healthy and the record simply
# never completes.
#
# So the phase now HOLDS `process_run_complete.py::_run_lock` -- the publisher's own primitive,
# not a second copy of it -- for its duration. These controls pin the four ways that can be
# worse than the poll it replaces: not actually excluding, not releasing, measuring anyway when
# the lock cannot be had, and a deadline shorter than the work it waits on.

def _lock_is_free() -> bool:
    """True if `_run_lock` can be taken right now -- asked of the publisher's OWN context
    manager rather than of a second flock written here, so a test cannot pass against a lock
    the real publisher would not respect."""
    from background import process_run_complete as prc
    with prc._run_lock() as acquired:
        return bool(acquired)


def test_a_phase_holds_the_publishers_run_lock_while_it_times(monkeypatch, tmp_path, runnable_ceiling):
    """MUTATION: drop the `with _publisher_exclusion(...)` from `_time_suite` and this reds --
    the publisher's lock stays free, so a real cycle starts inside the timed window.

    The lock is interrogated through `prc._run_lock` itself: what matters is not that some file
    is flocked but that THE publisher would lock-skip."""
    from background import process_run_complete as prc
    monkeypatch.setattr(measure, "_publisher_is_running", lambda: False)
    monkeypatch.setattr(measure, "_mem_available_mb",
                        lambda: measure.MIN_MEMORY_HEADROOM_MB + 1)
    seen = {}

    def fake_run(*_a, **_kw):
        seen["lock_free_during_the_suite"] = _lock_is_free()
        return types.SimpleNamespace(returncode=0, stdout="1 passed in 0.01s", stderr="")

    monkeypatch.setattr(measure.subprocess, "run", fake_run)
    measure._time_suite(tmp_path, lambda _m: None)

    assert seen["lock_free_during_the_suite"] is False, (
        "a publisher could have started its own cycle inside the timed window")


def test_the_exclusion_is_released_when_the_phase_is_over(monkeypatch, tmp_path):
    """A measurement that kept the lock would wedge publishing outright -- strictly worse than
    an unmeasured ratio. MUTATION: drop the `finally:` unlock and this reds."""
    from background import process_run_complete as prc

    with measure._publisher_exclusion(lambda _m: None):
        assert _lock_is_free() is False
    assert _lock_is_free() is True


def test_the_exclusion_is_released_when_the_phase_raises(monkeypatch, tmp_path):
    """The path that actually happens: an OOM-adjacent phase blows up mid-run. The lock must not
    outlive it, or every subsequent publish cycle lock-skips forever."""
    from background import process_run_complete as prc

    with pytest.raises(RuntimeError):
        with measure._publisher_exclusion(lambda _m: None):
            raise RuntimeError("phase died")
    assert _lock_is_free() is True


def test_the_exclusion_is_re_entrant_so_a_phase_can_span_its_setup(monkeypatch, tmp_path):
    """A second `flock` on a second fd of the same file blocks even inside one process, so a
    nested hold must be counted rather than re-attempted -- otherwise the inner one deadlocks
    into a deferral it would report as a busy publisher.

    No phase nests today: the COLD phase did (delete the reused checkout, rebuild it, time it,
    under one hold) and the R3 elimination removed it. The property is kept because the deadlock
    it prevents is silent and the next phase that needs a setup step would rediscover it."""
    from background import process_run_complete as prc
    monkeypatch.setattr(measure, "QUIET_WAIT_SECONDS", -1)  # a real re-acquire would defer here

    with measure._publisher_exclusion(lambda _m: None):
        with measure._publisher_exclusion(lambda _m: None):
            assert _lock_is_free() is False
        # Still held by the outer block -- an inner exit must not release it early.
        assert _lock_is_free() is False
    assert _lock_is_free() is True


def test_an_unavailable_exclusion_defers_rather_than_measuring_anyway(monkeypatch, tmp_path):
    """The same fail-open the seventh launch's fix closed, in the new guard. MUTATION: fall
    through to the suite instead of raising and this reds -- and the run it lets through is
    timed beside a live publisher, i.e. the OOM, or (surviving) a slow denominator that moves
    the exit criterion toward MEETS."""
    lock_path = measure.prc.RUN_LOCK_FILE  # the autouse fixture's, never the live publisher's
    monkeypatch.setattr(measure, "QUIET_WAIT_SECONDS", -1)  # already past the deadline

    holder = open(str(lock_path), "w")
    fcntl.flock(holder, fcntl.LOCK_EX | fcntl.LOCK_NB)
    try:
        with pytest.raises(measure._Deferred) as excinfo:
            with measure._publisher_exclusion(lambda _m: None):
                pytest.fail("timed a suite while the publisher held its own run lock")
        assert "run lock" in str(excinfo.value)
    finally:
        fcntl.flock(holder, fcntl.LOCK_UN)
        holder.close()


def test_a_held_exclusion_makes_a_real_publisher_lock_skip(monkeypatch, tmp_path):
    """The consumer end, stated as the publisher sees it: `_run_lock` yields False, which is the
    branch that returns EXIT_LOCK_SKIPPED and leaves the marker pending for the worker's sweep.
    The cost of this whole design is exactly that -- one deferred cycle, no lost marker."""
    from background import process_run_complete as prc

    with measure._publisher_exclusion(lambda _m: None):
        with prc._run_lock() as acquired:
            assert acquired is False


def test_the_exclusion_wait_exceeds_the_longest_a_publisher_may_hold_it():
    """DERIVED, not restated. A wait shorter than the work it waits on does not bound anything
    -- it guarantees a deferral, which is the 900s-caller-under-a-2600s-gate defect this atom
    closed one layer down. `PUBLISH_PATH_TIMEOUT_SECONDS` is how long a publisher may legally
    hold the lock, so the acquire must outlast it.

    MUTATION: set QUIET_WAIT_SECONDS back to a hand-typed `45 * 60` and this reds."""
    from background import process_run_complete as prc
    assert measure.QUIET_WAIT_SECONDS > prc.PUBLISH_PATH_TIMEOUT_SECONDS, (
        "a phase would defer while a publisher was still legitimately mid-cycle")


def test_no_test_in_this_module_can_reach_the_live_publishers_lock():
    """The isolation above is load-bearing, so it is asserted rather than trusted.

    MUTATION: drop `autouse=True` from `_the_live_publishers_lock_is_out_of_reach` and this reds
    -- and so does the whole module, by hanging for `QUIET_WAIT_SECONDS` inside the publish
    gate the publisher runs while holding that lock. A green here is the cheap version of that
    discovery."""
    from background import process_run_complete as prc
    live = Path(prc.PROJECT_DIR).resolve()
    in_use = Path(prc.RUN_LOCK_FILE).resolve()
    assert live not in in_use.parents, (
        "a test in this module is pointed at the live publisher's run lock ({}) -- it will "
        "either block for {}s inside the gate or make real publish cycles lock-skip".format(
            in_use, measure.QUIET_WAIT_SECONDS))


def test_any_test_module_that_enters_the_exclusion_redirects_the_lock():
    """DERIVED from the tree, not from a list this file remembers to extend.

    The population is every test module that can reach `_publisher_exclusion` -- directly, or
    through `_time_suite`/`_run_measurement`, which is how it was reached unnoticed here (the
    checkout phase enters it from `_run_measurement`, which no test names). Each such module
    must redirect `RUN_LOCK_FILE`, or it inherits the wedge."""
    entry_points = ("_publisher_exclusion", "_time_suite", "_run_measurement")
    tests_root = Path(__file__).resolve().parent.parent
    drivers, offenders = [], []
    for path in sorted(tests_root.rglob("test_*.py")):
        source = path.read_text(encoding="utf-8", errors="replace")
        if "measure_publish_gate_subject_cost" not in source:
            continue
        if not any(name in source for name in entry_points):
            continue
        drivers.append(str(path.relative_to(tests_root)))
        if "RUN_LOCK_FILE" not in source:
            offenders.append(str(path.relative_to(tests_root)))
    # Vacuity guard: this very module is a driver, so an empty population means the scan has
    # gone blind (a rename, a moved tests root) rather than that everything is safe.
    assert str(Path(__file__).resolve().relative_to(tests_root)) in drivers, (
        "the scan did not find this module -- it is measuring nothing: {}".format(drivers))
    assert not offenders, (
        "these modules drive the measurement's phases without redirecting the publisher's run "
        "lock, so they run against the live one: {}".format(offenders))


# ── AND THE RATIO MAY NOT SPAN COMMITS (OPS2 criterion 1, 2026-08-11) ────────────────────────
#
# The resume above is what makes this measurement converge on a box that keeps killing it, but
# it retired a phase on the strength of a `seconds` alone. The live record carried a warm phase
# timed at 54141b5 (*"235 failed ... 14 errors"*) beside a cold one at 3ee4541a (*"7 failed"*) --
# two different suites -- and the next launch would have timed the in-tree baseline at today's
# HEAD and divided one by the other. The exit criterion would then have been decided by the diff
# between two commits, reported as the cost of the checkout.
#
# These fire on that: the pair is dropped and re-timed together, a RETIRED phase is not (it only
# ever raises the timeout floor), and a pair already banked together is not re-paid for.

def _banked(out, **phases):
    """As the helper above: a COMPLETED returncode unless the test states otherwise, because a
    phase that cannot prove it finished is re-timed and would confound the comparability rule
    these tests are about."""
    stamped = {name: (rec if "returncode" in rec else dict(rec, returncode=1))
               for name, rec in phases.items()}
    Path(out).write_text(json.dumps({"phases": stamped}))
    return out


def test_a_banked_ratio_phase_from_another_commit_is_dropped(out):
    """THE LIVE PROPERTY. Throwaway at an older SHA, baseline owed -- it must be re-timed."""
    _banked(out, cold_checkout={"seconds": 1291.9, "head_sha_at_run": "old111"},
            throwaway_checkout={"seconds": 1167.5, "head_sha_at_run": "old222"})
    phases = measure._load_banked_phases(out)

    dropped = measure._drop_incomparable_ratio_phases(phases, "head999", print)

    assert dropped == ["throwaway_checkout"], (
        "a throwaway phase timed at another commit cannot be the numerator of a ratio whose "
        "denominator is timed at HEAD; it must be re-timed, not inherited"
    )
    assert "throwaway_checkout" not in phases
    assert "cold_checkout" in phases, (
        "a RETIRED phase feeds the timeout floor and never the ratio -- an older, slower one "
        "can only RAISE that bound, so re-paying 21 minutes for it buys nothing, and it is the "
        "floor's only evidence today"
    )


def test_a_ratio_phase_at_this_head_is_kept(out):
    """MUTATION-ADJACENT: a rule that drops everything is as useless as one that drops nothing.

    Without this, `_drop_incomparable_ratio_phases` could return every ratio phase it is shown
    and both the assertion above and the measurement's convergence would still look correct --
    while every launch re-paid 20 minutes for a phase it already held at the right commit."""
    _banked(out, throwaway_checkout={"seconds": 1167.5, "head_sha_at_run": "head999"})
    phases = measure._load_banked_phases(out)

    assert measure._drop_incomparable_ratio_phases(phases, "head999", print) == []
    assert "throwaway_checkout" in phases


def test_a_pair_banked_together_at_an_older_commit_is_not_re_timed(out):
    """Both sides at one (earlier) SHA are comparable TO EACH OTHER, which is all the ratio
    asks. Re-timing them would cost 40 minutes to learn the same number."""
    _banked(out, throwaway_checkout={"seconds": 1100.0, "head_sha_at_run": "old222"},
            in_tree_baseline={"seconds": 1000.0, "head_sha_at_run": "old222"})
    phases = measure._load_banked_phases(out)

    assert measure._drop_incomparable_ratio_phases(phases, "head999", print) == []
    assert set(phases) == {"throwaway_checkout", "in_tree_baseline"}


def test_a_banked_phase_with_no_recorded_commit_is_dropped(out):
    """FAIL-CLOSED. A phase that cannot be SHOWN to have been timed at this commit is not
    evidence for a criterion about this commit -- unprovable is not a pass."""
    _banked(out, throwaway_checkout={"seconds": 1167.5})
    phases = measure._load_banked_phases(out)

    assert measure._drop_incomparable_ratio_phases(
        phases, "head999", print) == ["throwaway_checkout"]
    assert "throwaway_checkout" not in phases


def test_the_drop_is_named_in_the_record_not_just_the_log(out, monkeypatch, tmp_path):
    """A drop only in the log is invisible to the next tick: it must be able to tell "this
    launch chose to re-pay for the throwaway" from "the record was lost"."""
    _banked(out, throwaway_checkout={"seconds": 1167.5, "head_sha_at_run": "old222"})
    monkeypatch.setattr(measure.prc, "_head_sha", lambda: "head999")
    # Defer immediately -- this asserts about the record the launch WRITES, not about a suite.
    monkeypatch.setattr(measure, "_wait_for_quiet",
                        lambda *a, **k: (_ for _ in ()).throw(measure._Deferred("test")))
    monkeypatch.setattr(measure, "_publisher_exclusion",
                        lambda *a, **k: (_ for _ in ()).throw(measure._Deferred("test")))

    measure._run_measurement(out, print)

    rec = json.loads(Path(out).read_text())
    assert rec["dropped_for_comparability"] == ["throwaway_checkout"]
    assert "throwaway_checkout" not in rec["phases"], (
        "the dropped phase must be gone from the record too -- a record still carrying it "
        "would let a reader compute the very ratio this drop exists to prevent"
    )


# ── THE STAGE MARKER: A KILLED LAUNCH MUST SAY WHETHER IT WAS WAITING OR WORKING ─────────────
#
# THE DEFECT IS OBSERVED, and it is a defect of the INSTRUMENT, not of the box (R15, one level
# up: this harness is the evidence source for OPS2's exit criterion 1).
#
# The 2026-08-10 22:28Z launch was OOM-killed at 23:11:10Z. Its own journal ended at
#
#     [measure] phase 3/3 BASELINE -- the live working tree, the pre-ruling subject
#     [measure]   . waiting to TAKE the publisher's run lock
#
# and `last_heartbeat` in the record froze at the same moment. Both signals said WAITING, so
# `WORKER_FINDING_THE_MEASUREMENT_IS_OOM_KILLED_INSIDE_ITS_OWN_WAIT_2026-08-11` recorded
# *"It died in the wait, not in the suite"* as `observed` and proposed a memory guard inside the
# acquire poll.
#
# The kernel log says otherwise, and it is the more direct evidence (R9):
#
#     Out of memory: Killed process 3272589 (python3) anon-rss:12928996kB
#     oom-kill:constraint=CONSTRAINT_NONE ... global_oom,
#     task_memcg=/.../publish-gate-subject-cost.service
#
# The unit's own python was pid **3244117**; **3272589 was its child** -- the BASELINE phase's
# pytest, at 12.9G on a 15.9G box. It had taken the lock and was IN THE SUITE. The proposed
# repair would not have fired.
#
# Two blind spots produced that: the phase banner is printed BEFORE the wait (so it cannot
# separate the two), and `heartbeat` is called ONLY from the wait loops (so the artefact freezes
# the instant work begins and stays frozen for ~20 minutes). The record therefore could not
# distinguish "still waiting" from "working, and killed at it".
#
# These controls pin the differential in BOTH directions. A single test that only asserted
# `stage == "suite_running"` would pass against a marker hardwired to that string, so the
# waiting side is asserted against the same mechanism, and the mutation below removes the
# distinction rather than the marker.


def _live_marker(out_path):
    """A real `_InFlight` over a real checkpoint file. Returns (results, heartbeat).

    Deliberately NOT a stub: what is under test is that the marker reaches DISK before the kill
    does, which a fake heartbeat could not fail on."""
    results = {"phases": {}}
    heartbeat = measure._InFlight(
        results, lambda: measure._checkpoint(results, out_path, lambda _m: None))
    return results, heartbeat


def test_a_launch_killed_in_the_suite_leaves_a_record_that_says_so(monkeypatch, out, tmp_path, runnable_ceiling):
    """THE property the misread finding needed and did not have. The record is read from DISK
    at the moment the suite child is running -- which is exactly what an OOM kill leaves behind,
    because a kill gives the process no chance to write anything afterwards.

    MUTATION: make `_InFlight.stage` a no-op (or drop its `self._checkpoint()`) and this reds --
    the on-disk marker still says `waiting_for_publisher_lock`, i.e. the 2026-08-10 misread."""
    monkeypatch.setattr(measure, "_wait_for_quiet", lambda log, heartbeat=None: True)
    monkeypatch.setattr(measure, "_wait_for_memory_headroom", lambda log, heartbeat=None: True)
    results, heartbeat = _live_marker(out)
    heartbeat.enter("in_tree_baseline")

    snapshot = {}

    def fake_run(*_a, **_kw):
        # What a SIGKILL arriving right here would leave in the repo. FIRST call only:
        # `monkeypatch.setattr(measure.subprocess, "run", ...)` patches the subprocess MODULE,
        # so `prc._head_sha()` after the suite lands here too and would overwrite the snapshot
        # with the record as it looks once the phase is already over.
        snapshot.setdefault("record", json.loads(Path(out).read_text()))
        return types.SimpleNamespace(returncode=0, stdout="1 passed in 0.01s", stderr="")

    monkeypatch.setattr(measure.subprocess, "run", fake_run)
    measure._time_suite_under_exclusion(tmp_path, lambda _m: None, heartbeat)

    marker = snapshot["record"].get("in_flight")
    assert marker, "a launch killed mid-suite would leave no marker at all"
    assert marker["stage"] == "suite_running", (
        "the record says '{}' while the suite child is running -- a kill here would be read as "
        "a death in the wait, which is the 2026-08-10 misdiagnosis".format(marker["stage"])
    )
    assert marker["phase"] == "in_tree_baseline"


def test_a_launch_killed_waiting_for_the_lock_leaves_a_different_record(monkeypatch, out):
    """The other direction, through the same mechanism. If both deaths wrote the same marker the
    marker would be decoration; the finding's own question -- waiting or working? -- is only
    answerable because these two strings differ."""
    lock_path = measure.prc.RUN_LOCK_FILE  # the autouse fixture's, never the live publisher's
    monkeypatch.setattr(measure, "QUIET_WAIT_SECONDS", -1)  # defer on the first poll
    results, heartbeat = _live_marker(out)
    heartbeat.enter("in_tree_baseline")

    holder = open(str(lock_path), "w")
    fcntl.flock(holder, fcntl.LOCK_EX | fcntl.LOCK_NB)
    try:
        with pytest.raises(measure._Deferred):
            with measure._publisher_exclusion(lambda _m: None, heartbeat):
                pytest.fail("took a lock another holder had")
    finally:
        fcntl.flock(holder, fcntl.LOCK_UN)
        holder.close()

    marker = json.loads(Path(out).read_text())["in_flight"]
    assert marker["stage"] == "waiting_for_publisher_lock", (
        "a death in the acquire poll must not be recorded the same way as a death in the suite"
    )


def test_the_two_deaths_are_told_apart_by_the_record_alone(monkeypatch, out, tmp_path, runnable_ceiling):
    """The pair, as one assertion, because the pair is the property.

    MUTATION that reds this and not much else: give every `_mark_stage` call the same literal
    (say `"running"`). Each test above would still find "a marker"; only the differential
    notices that the instrument has stopped answering the question it exists for."""
    monkeypatch.setattr(measure, "_wait_for_quiet", lambda log, heartbeat=None: True)
    monkeypatch.setattr(measure, "_wait_for_memory_headroom", lambda log, heartbeat=None: True)
    monkeypatch.setattr(measure.subprocess, "run",
                        lambda *a, **k: types.SimpleNamespace(
                            returncode=0, stdout="1 passed in 0.01s", stderr=""))

    _, working = _live_marker(out)
    working.enter("in_tree_baseline")
    seen = {}

    def capture(*_a, **_kw):
        # First call only -- see the note in the test above.
        seen.setdefault("working", json.loads(Path(out).read_text())["in_flight"]["stage"])
        return types.SimpleNamespace(returncode=0, stdout="1 passed in 0.01s", stderr="")

    monkeypatch.setattr(measure.subprocess, "run", capture)
    measure._time_suite_under_exclusion(tmp_path, lambda _m: None, working)

    monkeypatch.setattr(measure, "QUIET_WAIT_SECONDS", -1)
    _, waiting = _live_marker(out)
    waiting.enter("in_tree_baseline")
    holder = open(str(measure.prc.RUN_LOCK_FILE), "w")
    fcntl.flock(holder, fcntl.LOCK_EX | fcntl.LOCK_NB)
    try:
        with pytest.raises(measure._Deferred):
            with measure._publisher_exclusion(lambda _m: None, waiting):
                pass
    finally:
        fcntl.flock(holder, fcntl.LOCK_UN)
        holder.close()
    seen["waiting"] = json.loads(Path(out).read_text())["in_flight"]["stage"]

    assert seen["working"] != seen["waiting"], (
        "both deaths leave the marker '{}' -- the record cannot answer 'waiting or working?', "
        "which is the whole reason the 2026-08-10 finding was aimed at the wrong loop"
        .format(seen["working"])
    )


def test_a_marker_is_never_left_on_an_ending_the_launch_chose(monkeypatch, out, tmp_path):
    """`in_flight` present must mean EXACTLY ONE thing: the writer never reached any of its own
    exits. A completed run, an abort and a deferral all choose their ending, so all three must
    clear it -- otherwise the next launch reports a kill that never happened, and the signal is
    worth nothing.

    MUTATION: drop any one of the `heartbeat.clear()` calls and this reds."""
    throwaway = _a_throwaway(tmp_path)
    monkeypatch.setattr(measure.prc, "_head_checkout", _FakeCheckout(throwaway))
    _stub_phases(monkeypatch, [])

    assert measure._run_measurement(out, lambda _m: None) == 0
    complete = json.loads(Path(out).read_text())
    assert complete["complete"] is True
    assert "in_flight" not in complete, "a finished run is reported as having been killed"

    # And the deferral path, on the same record.
    monkeypatch.setattr(measure, "_publisher_exclusion",
                        lambda *a, **k: (_ for _ in ()).throw(measure._Deferred("test")))
    monkeypatch.setattr(measure, "_time_suite",
                        lambda *a, **k: (_ for _ in ()).throw(measure._Deferred("test")))
    _banked(out)
    assert measure._run_measurement(out, lambda _m: None) == 0
    deferred = json.loads(Path(out).read_text())
    assert deferred["deferred"]["reason"] == "test"
    assert "in_flight" not in deferred, (
        "a deferral is an ending this launch chose -- recording it as a kill would make the "
        "marker fire on the harness's own correct behaviour"
    )


def test_the_next_launch_republishes_the_kill_rather_than_erasing_it(monkeypatch, out, tmp_path):
    """The marker only helps if it survives the launch that reads it. `_run_measurement` rewrites
    the whole file from `results`, so without an explicit read-before-write the diagnosis is
    destroyed by the very next tick -- the same defect `_prior_deferral_count` closed for the
    deferral tally.

    MUTATION (run, not asserted): move the `_prior_in_flight` read BELOW the first
    `_checkpoint(results, args.out, log)` and this reds with `previous_launch_died_in_flight`
    set to None. Note the weaker mutation -- reading it at the assignment site instead of beside
    `_load_banked_phases` -- does NOT red, because that site is still above the first
    checkpoint. The ordering that matters is against the WRITE, not against the other reads."""
    Path(out).write_text(json.dumps({
        "phases": {},
        "in_flight": {"phase": "in_tree_baseline", "stage": "suite_running",
                      "since": "2026-08-10T22:28:49Z", "mem_available_mb": 512},
    }))
    throwaway = _a_throwaway(tmp_path)
    monkeypatch.setattr(measure.prc, "_head_checkout", _FakeCheckout(throwaway))
    _stub_phases(monkeypatch, [])

    assert measure._run_measurement(out, lambda _m: None) == 0

    rec = json.loads(Path(out).read_text())
    assert rec["previous_launch_died_in_flight"] == {
        "phase": "in_tree_baseline", "stage": "suite_running",
        "since": "2026-08-10T22:28:49Z", "mem_available_mb": 512,
    }, "the previous launch's diagnosis was overwritten by the launch that should report it"
    assert "in_flight" not in rec, "this launch's own clean ending must not re-arm the marker"


def test_a_record_with_no_prior_kill_says_so_explicitly(monkeypatch, out, tmp_path):
    """The quiet direction. `None` is WRITTEN, not omitted: a reader must be able to tell "the
    last launch ended on a path it chose" from "this harness predates the marker"."""
    _banked(out)
    throwaway = _a_throwaway(tmp_path)
    monkeypatch.setattr(measure.prc, "_head_checkout", _FakeCheckout(throwaway))
    _stub_phases(monkeypatch, [])

    assert measure._run_measurement(out, lambda _m: None) == 0

    rec = json.loads(Path(out).read_text())
    assert "previous_launch_died_in_flight" in rec
    assert rec["previous_launch_died_in_flight"] is None


def test_the_marker_records_the_memory_a_killed_phase_never_banks(monkeypatch, out, tmp_path, runnable_ceiling):
    """A phase that is OOM-killed banks no phase record, so `mem_available_before_mb` -- the one
    field that would explain the kill -- is never written. The marker carries it instead, and
    re-stamps it at every stage, so the artefact holds the conditions AT the moment of death
    rather than at the moment the phase was entered 40 minutes earlier."""
    monkeypatch.setattr(measure, "_wait_for_quiet", lambda log, heartbeat=None: True)
    monkeypatch.setattr(measure, "_wait_for_memory_headroom", lambda log, heartbeat=None: True)
    mem = iter([9000, 400])
    monkeypatch.setattr(measure, "_mem_available_mb", lambda: next(mem, 400))
    _, heartbeat = _live_marker(out)
    heartbeat.enter("in_tree_baseline")
    assert json.loads(Path(out).read_text())["in_flight"]["mem_available_mb"] == 9000

    seen = {}

    def capture(*_a, **_kw):
        # First call only -- see the note two tests above.
        seen.setdefault("at_suite",
                        json.loads(Path(out).read_text())["in_flight"]["mem_available_mb"])
        return types.SimpleNamespace(returncode=0, stdout="1 passed in 0.01s", stderr="")

    monkeypatch.setattr(measure.subprocess, "run", capture)
    measure._time_suite_under_exclusion(tmp_path, lambda _m: None, heartbeat)

    assert seen["at_suite"] == 400, (
        "the marker froze the headroom it saw when the phase was entered -- a launch that waited "
        "40 minutes and then died would report the box as it was before the wait"
    )


def test_the_stage_helper_is_harmless_without_a_marker():
    """`_time_suite` is called with a plain callable in this module's own tests and with `None`
    from several call sites. A stage helper that raised on either would take the measurement down
    to improve its diagnostics -- the checkpoint's own fail-loud rule, in the new mechanism."""
    measure._mark_stage(None, "suite_running")
    measure._mark_stage(lambda: None, "suite_running")
    results = {}
    heartbeat = measure._InFlight(results, lambda: None)
    heartbeat.stage("suite_running")   # before enter(): nothing to advance
    assert "in_flight" not in results
    heartbeat.clear()                   # idempotent
    assert "in_flight" not in results


# ── THE PHASE'S MEMORY BOUND (OPS2, 2026-08-11) ──────────────────────────────────────────────
#
# WHAT THESE FIRE ON, and it is OBSERVED not hypothetical (`journalctl -k`, 2026-08-10
# 23:11:10Z): the BASELINE phase's pytest reached 12.9G anon RSS on a 15.9G box and was killed
# by the GLOBAL OOM killer -- `constraint=CONSTRAINT_NONE ... global_oom`. A global OOM chooses
# its victim across the whole box, so the live publisher is a candidate every time this harness
# runs, and three launches have now died this way.
#
# The control is option A of WORKER_FINDING_THE_MEASUREMENTS_SUBJECT_IS_LARGER_THAN_THE_GATES:
# each phase's pytest runs inside its own `systemd-run --scope` with a MemoryMax, so an
# over-large run is THAT PHASE's failure and nothing else on the box is at risk.
#
# THE TAUTOLOGY THESE AVOID. Asserting that `_scope_argv` contains the string "MemoryMax" proves
# only that this repo can build a string; it would pass just as happily against a kernel with no
# memory controller, which is the fail-silent shape R15 names. So the first test below spends a
# real two seconds proving the bound KILLS -- and proves it differentially, by running the same
# allocation unbounded and watching it succeed.


def _systemd_run_missing():
    import shutil as _shutil
    return _shutil.which("systemd-run") is None


@pytest.mark.skipif(_systemd_run_missing(), reason="systemd-run is the mechanism under test")
def test_the_kernel_applied_both_limits_not_just_this_repo_writing_them_down():
    """The scope's OWN cgroup is asked what it is limited to, from inside it.

    WHY NOT JUST ASSERT THE KILL. The kill test below is the one that proves enforcement, but it
    cannot cleanly pin `MemorySwapMax=0`: whether a throttled process dies or merely swaps
    depends on how much swap the box happens to have free, and dropping the property was
    MEASURED here surviving as a mutation for exactly that reason -- it stayed green on a box
    that was already 3G into swap. Ambient state must not decide a control's verdict, so the
    property is read back from the kernel instead of inferred from a behaviour it only usually
    produces.

    `memory.swap.max = 0` is load-bearing, not tidiness: with swap allowed, a 12.9G suite under
    an 8G ceiling does not die, it thrashes -- a slower version of the harm the bound exists to
    prevent."""
    probe = ("from pathlib import Path\n"
             "rel = Path('/proc/self/cgroup').read_text().strip().split(':')[-1]\n"
             "base = Path('/sys/fs/cgroup') / rel.lstrip('/')\n"
             "print((base / 'memory.max').read_text().strip())\n"
             "print((base / 'memory.swap.max').read_text().strip())\n")
    res = subprocess.run(measure._scope_argv("ops2-limits-selftest", memory_max_mb=128)
                         + [sys.executable, "-c", probe],
                         capture_output=True, text=True, timeout=120)
    assert res.returncode == 0, "the probe never ran: {}".format(res.stderr[-300:])
    memory_max, swap_max = res.stdout.split()

    assert memory_max == str(128 * 1024 * 1024), (
        "the kernel did not apply MemoryMax -- the argv carries it but the cgroup does not, "
        "which is the fail-silent shape: every phase would run effectively unbounded"
    )
    assert swap_max == "0", (
        "swap is not denied to the phase, so exceeding the ceiling throttles into swap instead "
        "of killing -- a 12.9G suite would thrash this box rather than die alone"
    )


@pytest.mark.skipif(_systemd_run_missing(), reason="systemd-run is the mechanism under test")
def test_the_bound_actually_kills_an_over_large_child_and_the_unbounded_one_survives():
    """The control's own named defect, run for real: a child that exceeds the ceiling dies.

    The DIFFERENTIAL is the whole point. A bounded run that died could be dying of anything --
    a bad interpreter, a missing module, a systemd that refuses scopes. The same allocation run
    WITHOUT the wrapper must succeed, so the death above is demonstrably produced by the bound.
    Both sides allocate 300MB against a 128MB ceiling."""
    alloc = ("b=[]\n"
             "for _ in range(300): b.append(bytearray(1024*1024))\n"
             "print('allocated 300MB')")

    bounded = subprocess.run(measure._scope_argv("ops2-bound-selftest", memory_max_mb=128)
                             + [sys.executable, "-c", alloc],
                             capture_output=True, text=True, timeout=120)
    unbounded = subprocess.run([sys.executable, "-c", alloc],
                               capture_output=True, text=True, timeout=120)

    assert unbounded.returncode == 0 and "allocated 300MB" in unbounded.stdout, (
        "the CONTROL arm failed, so this test cannot attribute the bounded arm's death to the "
        "bound: {}".format(unbounded.stderr[-300:])
    )
    assert bounded.returncode != 0, (
        "a 300MB allocation completed inside a 128MB ceiling -- the MemoryMax property is not "
        "being enforced, so every phase still runs effectively unbounded"
    )
    assert "allocated 300MB" not in bounded.stdout


def test_every_phase_runs_inside_a_memory_bound(monkeypatch, tmp_path, runnable_ceiling):
    """The argv the phase actually executes carries the ceiling.

    Mutation: return `_argv_without_x()` from `_bounded_argv` and this reds -- which is the
    pre-repair behaviour exactly, so this test is the one that would have caught the box-killer."""
    monkeypatch.setattr(measure, "_wait_for_quiet", lambda log, heartbeat=None: True)
    monkeypatch.setattr(measure, "_wait_for_memory_headroom", lambda log, heartbeat=None: True)
    seen = {}

    def capture(argv, *_a, **_kw):
        # The SUITE's argv, not the first subprocess the phase happens to start: since
        # `_subject_sha` the phase asks its own tree `git rev-parse HEAD` before and after the
        # run, and a `setdefault` on call one would grade that instead -- a control graded on
        # the wrong subject, which is how it failed when the stamping was repaired.
        if argv and argv[0] != "git":
            seen.setdefault("argv", list(argv))
        return types.SimpleNamespace(returncode=0, stdout="1 passed in 0.01s", stderr="")

    monkeypatch.setattr(measure.subprocess, "run", capture)
    measure._time_suite_under_exclusion(tmp_path, lambda _m: None, None)

    argv = seen["argv"]
    assert argv[0] == "systemd-run", "the phase's pytest was launched without its memory bound"
    assert "--scope" in argv, (
        "a --unit reparents the suite to the user manager, which loses the timing, the captured "
        "summary line and the publisher exclusion this phase runs under"
    )
    assert "--property=MemoryMax={}M".format(measure.PHASE_MEMORY_MAX_MB) in argv
    assert "-m" in argv and "pytest" in argv, "the bound wrapped something that is not the suite"


def test_the_ceiling_sits_below_the_level_that_killed_the_box():
    """A bound above the observed lethal footprint is a bound that changes nothing.

    12.9G is where the global OOM killer took the phase out on 2026-08-10; 2.42G is the live
    publish gate's own sampled peak. A ceiling outside that corridor is either useless (too
    high) or guaranteed to fail every legitimate run (too low)."""
    assert measure.PHASE_MEMORY_MAX_MB < 12_900, (
        "the ceiling is at or above the footprint that global-OOM-killed this box, so it can "
        "never fire before the kernel does"
    )
    assert measure.PHASE_MEMORY_MAX_MB > 2_420 * 2, (
        "the ceiling is within 2x the publish gate's own observed peak -- a legitimate suite "
        "would trip it and the measurement would never converge"
    )


def test_an_unavailable_systemd_run_blocks_the_phase_rather_than_running_it_bare(monkeypatch,
                                                                                 tmp_path):
    """An unavailable control is a FAILED control (R15), and here it is the only thing between a
    12.9G suite and the live publisher.

    Mutation: fall back to `_argv_without_x()` when `shutil.which` returns None and this reds."""
    monkeypatch.setattr(measure.shutil, "which", lambda _name: None)
    said = []
    with pytest.raises(measure._Unbounded):
        measure._bounded_argv(tmp_path, said.append)
    assert any("REFUSING" in m for m in said), (
        "the phase blocked silently -- the next reader gets a non-zero exit with no cause"
    )


def test_a_blocked_run_is_recorded_and_exits_non_zero_unlike_a_deferral(monkeypatch, out,
                                                                       tmp_path):
    """The differential that keeps 'the box was briefly busy' distinguishable from 'the control
    is gone'. A deferral returns 0 and is a correct outcome; this must not."""
    throwaway = _a_throwaway(tmp_path)
    monkeypatch.setattr(measure.prc, "_head_checkout", _FakeCheckout(throwaway))
    monkeypatch.setattr(measure, "_time_suite",
                        lambda *_a, **_kw: (_ for _ in ()).throw(
                            measure._Unbounded("systemd-run unavailable")))

    assert measure._run_measurement(out, lambda _m: None) == 1, (
        "a missing memory bound exited 0, so the transient unit reads `active (exited)` and the "
        "next tick sees one more launch that quietly banked nothing"
    )
    rec = json.loads(Path(out).read_text())
    assert rec["blocked"]["reason"] == "systemd-run unavailable"
    assert "deferred" not in rec or rec.get("deferral_count", 0) == 0, (
        "a block was counted as a deferral, which is the reading that says 'try again later'"
    )


def test_a_phase_killed_by_its_own_ceiling_is_told_from_one_killed_by_the_box():
    """`hit_memory_ceiling`'s discriminator, both directions and the vacuous one.

    The exact signal lives in the scope's `memory.events`, which is torn down with the scope, so
    this is INFERRED from what survives: a cgroup kill leaves the BOX with memory, a global OOM
    leaves it starved. The record labels it inferred; this pins that it at least separates the
    two cases the kernel log actually showed."""
    floor = measure.MIN_MEMORY_HEADROOM_MB
    assert measure._looks_like_the_bound(-9, floor + 1) is True
    assert measure._looks_like_the_bound(-9, floor - 1) is False, (
        "a SIGKILL on a starved box was attributed to this phase's own ceiling -- that is the "
        "global OOM, and calling it a cgroup kill hides the failure the bound exists to prevent"
    )
    assert measure._looks_like_the_bound(1, 9000) is False, "an ordinary red suite is not a kill"
    assert measure._looks_like_the_bound(0, 9000) is False
    assert measure._looks_like_the_bound(-9, None) is False, (
        "an unreadable /proc must not be read as a clean cgroup kill"
    )


def test_the_returncode_fallback_alone_misses_the_shape_that_actually_happened():
    """THE REGRESSION, in the exact shape the live record carried.

    Launch 14's `in_tree_baseline` died at 2026-08-11T22:57:36Z with `returncode: -15` while the
    kernel logged, that same second, a CONSTRAINT_MEMCG kill whose `oom_memcg` was that phase's own
    scope. The record banked `hit_memory_ceiling: false`. Under `systemd-run --scope` the cgroup
    OOM killer takes the fattest task in the cgroup -- a child at 6.1G here, not the pytest this
    harness waits on -- and systemd then SIGTERMs the rest, so -15 is the ORDINARY shape and -9
    is the special case where the kernel happened to pick the process being timed.

    MUTATION (RUN): delete the `kernel_oom is True` branch of `_looks_like_the_bound` and the
    first assertion reds -- which is precisely the state that banked three truncated baselines."""
    roomy = measure.MIN_MEMORY_HEADROOM_MB + 1
    assert measure._looks_like_the_bound(-15, roomy, True) is True, (
        "the kernel named this phase's own cgroup as the OOM's memcg and the verdict still said "
        "the ceiling was not hit -- three relaunches were bought by exactly this answer"
    )
    assert measure._looks_like_the_bound(-15, roomy) is False, (
        "the returncode-only fallback is blind here BY CONSTRUCTION; if this ever starts passing "
        "on its own the kernel oracle has stopped being the thing doing the work"
    )
    assert measure._looks_like_the_bound(-15, roomy, False) is False, (
        "the kernel positively reported no cgroup OOM for this scope; that is an answer, not a "
        "reason to fall back to guessing"
    )
    # The oracle OVERRIDES the fallback in both directions -- a control that can only ever add
    # `True` would turn every unrelated journal line into a ceiling kill.
    assert measure._looks_like_the_bound(-9, roomy, False) is False
    assert measure._looks_like_the_bound(1, roomy, True) is True


def test_the_kernel_oracle_names_this_scope_rather_than_any_oom(monkeypatch):
    """`_scope_oom_killed` must answer about THIS cgroup, and must fail CLOSED to None.

    The distinction it exists to draw is cgroup-kill versus global-OOM, and a global OOM prints
    the whole process table -- so a scope's name appearing SOMEWHERE in the log is not evidence
    about that scope. Only `oom_memcg=` is.

    MUTATION (RUN): match on `unit in line` instead of the `oom_memcg=` field and the
    global-OOM case below reds."""
    scope = "publish-gate-phase-1234-5678"
    memcg = ("oom-kill:constraint=CONSTRAINT_MEMCG,nodemask=(null),"
             "oom_memcg=/user.slice/user-1000.slice/app.slice/{}.scope,"
             "task_memcg=/user.slice/user-1000.slice/app.slice/{}.scope,task=python3".format(
                 scope, scope))
    # A GLOBAL OOM that merely lists this scope's task in its victim table: not this scope's own
    # ceiling, and the whole point of the field.
    globl = ("oom-kill:constraint=CONSTRAINT_NONE,nodemask=(null),global_oom,"
             "task_memcg=/user.slice/user-1000.slice/app.slice/{}.scope,task=python3".format(scope))

    def _journal(stdout, returncode=0):
        return lambda *_a, **_kw: types.SimpleNamespace(
            returncode=returncode, stdout=stdout, stderr="")

    monkeypatch.setattr(measure.shutil, "which", lambda _n: "/usr/bin/journalctl")

    monkeypatch.setattr(measure.subprocess, "run", _journal(memcg))
    assert measure._scope_oom_killed(scope) is True

    monkeypatch.setattr(measure.subprocess, "run", _journal(globl))
    assert measure._scope_oom_killed(scope) is False, (
        "a GLOBAL OOM that happened to list this scope's task was read as this scope's own "
        "ceiling -- that collapses the two outcomes the verdict exists to separate"
    )

    monkeypatch.setattr(measure.subprocess, "run", _journal(memcg.replace(scope, "some-other")))
    assert measure._scope_oom_killed(scope) is False, "another scope's cgroup kill is not ours"

    # FAIL-CLOSED: every way the question cannot be put returns None, never False. None falls back
    # to the labelled inference; False would assert the kernel had answered when it had not.
    monkeypatch.setattr(measure.subprocess, "run", _journal("", returncode=1))
    assert measure._scope_oom_killed(scope) is None, "a failed journalctl is not a clean 'no'"

    def _raise(*_a, **_kw):
        raise OSError("no journal")
    monkeypatch.setattr(measure.subprocess, "run", _raise)
    assert measure._scope_oom_killed(scope) is None

    monkeypatch.setattr(measure.shutil, "which", lambda _n: None)
    assert measure._scope_oom_killed(scope) is None, (
        "an unavailable journalctl is an unavailable CHECK, which R15 says is a failed check -- "
        "it may not render as 'no OOM happened'"
    )
    assert measure._scope_oom_killed("") is None


def test_the_phase_the_kernel_answered_says_observed_not_inferred():
    """R9 labels are the claim. A kernel-answered verdict is `observed`; the returncode guess is
    `inferred`; and the two must not share a sentence, or the record cannot tell a reader whether
    anything actually looked.

    MUTATION (RUN): drop the `kernel_oom` argument at the `_hit_memory_ceiling_basis` call site in
    `_time_suite_under_exclusion` and `test_the_writer_still_emits_a_basis_beside_every_verdict`
    reds on the mismatch."""
    roomy = measure.MIN_MEMORY_HEADROOM_MB + 1
    observed = measure._hit_memory_ceiling_basis(-15, roomy, True, True)
    assert observed.startswith("observed:"), observed
    assert "oom_memcg" in observed, (
        "the basis must name the evidence it rests on, not merely assert a verdict"
    )
    denied = measure._hit_memory_ceiling_basis(-15, roomy, False, False)
    assert denied.startswith("observed:"), denied

    inferred = measure._hit_memory_ceiling_basis(-9, roomy, True, None)
    assert inferred.startswith("inferred:"), (
        "with no kernel answer the verdict is a guess from the returncode and must say so"
    )
    assert len({observed, denied, inferred}) == 3, (
        "a kernel-observed kill, a kernel-denied one and a returncode guess share a sentence"
    )


def test_the_phase_record_states_its_ceiling_and_its_x_premium(monkeypatch, tmp_path, runnable_ceiling):
    """Two things a future reader re-deriving GATE_SUITE_TIMEOUT_SECONDS needs and cannot infer:
    the ceiling the phase ran under, and that this suite is STRICTLY LARGER than the gate's own
    (`-x` is stripped here, kept there, and the suite is red at HEAD)."""
    monkeypatch.setattr(measure, "_wait_for_quiet", lambda log, heartbeat=None: True)
    monkeypatch.setattr(measure, "_wait_for_memory_headroom", lambda log, heartbeat=None: True)
    monkeypatch.setattr(measure, "_mem_available_mb", lambda: 9000)
    monkeypatch.setattr(measure.subprocess, "run",
                        lambda *_a, **_kw: types.SimpleNamespace(
                            returncode=0, stdout="1 passed in 0.01s", stderr=""))

    rec = measure._time_suite_under_exclusion(tmp_path, lambda _m: None, None)

    assert rec["memory_max_mb"] == measure.PHASE_MEMORY_MAX_MB
    assert rec["hit_memory_ceiling"] is False
    assert rec["subject_larger_than_the_gates"] is True, (
        "the record does not say the timing carries an -x premium, so the timeout floor derived "
        "from it reads as a fit to the gate's own runtime when it is an over-estimate"
    )
    assert "-x" in rec["subject_note"]


# ── A LOWER BOUND MAY RAISE A FLOOR AND MAY NOT BE A DENOMINATOR ──
#
# THE DEFECT, OBSERVED IN THE LIVE RECORD (launch 11, 2026-08-11). `in_tree_baseline` was
# SIGTERMed mid-suite: `returncode: -15`, a summary of nine progress dots, no summary line ever
# printed. It was banked like any completed phase, `complete` was written `true` over it, and it
# became the DENOMINATOR of `ratio_throwaway_over_in_tree: 1.084` -- the single number superseded
# criterion 1's honest successor rests on.
#
# The prose was already right, which is the whole lesson. `_time_suite`'s own field comment said
# "a phase that hit its own bound is a phase whose SECONDS mean nothing, so a reader must not
# average it into a ratio" -- addressed to a reader, enforced nowhere, and covering only rc=-9.
# These are the control.
#
# The rule is an ASYMMETRY and both halves need a test: a truncated phase still feeds the timeout
# FLOOR (its seconds is a lower bound, and a lower bound can only push a fail-closed bound UP,
# the safe direction) while being refused as a RATIO term (a truncated denominator does not err
# safely, it overstates the tax).

def test_a_signal_killed_phase_is_not_a_completed_one():
    """The discriminator itself. A red suite REPORTED; a killed one did not."""
    assert measure._ran_to_completion_from(0, False) is True
    assert measure._ran_to_completion_from(1, False) is True, (
        "a red suite ran every test it meant to and printed a summary -- rc=1 is a verdict, "
        "not a death"
    )
    assert measure._ran_to_completion_from(-15, False) is False, (
        "SIGTERM mid-suite is the exact shape that reached the live ratio as a measurement"
    )
    assert measure._ran_to_completion_from(-9, False) is False
    assert measure._ran_to_completion_from(1, True) is False, (
        "a phase squeezed against its own memory ceiling has a meaningless runtime even if it "
        "exited politely"
    )


def test_the_ratio_refuses_a_truncated_term_and_says_why(out, monkeypatch, tmp_path):
    """THE LIVE PROPERTY, against the real numbers. 1411.2s / 1302.4s = 1.084 was published from
    a completed run over a killed one; the ratio must now be absent, with the cause NAMED rather
    than left as a null for the next reader to re-diagnose.

    MUTATION: delete the `ineligible` branch in `_run_measurement` so the ratio is computed
    unconditionally, and this reds on 1.084 reappearing."""
    # The re-timed baseline is killed AGAIN, which is how this state is reached for real: the
    # truncated phase is never banked, so the only way both terms exist with one truncated is a
    # fresh run that also died. `deadbeef` is `_stub_phases`'s HEAD -- the banked throwaway must
    # be comparable to it or it is dropped for a reason this test is not about.
    monkeypatch.setattr(measure.prc, "_head_checkout", _FakeCheckout(_a_throwaway(tmp_path)))
    _stub_phases(monkeypatch, [])
    monkeypatch.setattr(measure, "_time_suite", lambda cwd, log, heartbeat=None: {
        "cwd": str(cwd), "head_sha_at_run": "deadbeef", "seconds": 1302.4,
        "returncode": -15, "summary": ".........", "box_was_quiet": True})
    Path(out).write_text(json.dumps({"phases": {
        "throwaway_checkout": {"seconds": 1411.2, "returncode": 1,
                               "head_sha_at_run": "deadbeef"},
    }}))

    measure._run_measurement(out, lambda _m: None)

    rec = _read(out)
    assert rec["ratio_throwaway_over_in_tree"] != 1.084, (
        "the published ratio divided a completed run by a SIGTERMed one -- the number this "
        "control exists to withdraw"
    )
    assert "in_tree_baseline" in rec.get("ratio_unavailable_because", ""), (
        "a null with no stated cause sends the next reader back to the journal to re-derive "
        "what this record already knows"
    )


def test_a_truncated_phase_is_re_timed_rather_than_banked(out, monkeypatch, tmp_path):
    """The never-converging shape: a killed phase banked forever means the ratio it poisons can
    never become honest. The truncated baseline must be OWED, and the sound throwaway beside it
    must not be re-paid for.

    MUTATION: make `_load_banked_phases`/`_owed_phases` key on `seconds is not None` again and
    the baseline is skipped as banked -- this reds."""
    monkeypatch.setattr(measure.prc, "_head_checkout", _FakeCheckout(_a_throwaway(tmp_path)))
    timed = []
    _stub_phases(monkeypatch, timed)
    Path(out).write_text(json.dumps({"phases": {
        "throwaway_checkout": {"seconds": 1411.2, "returncode": 1,
                               "head_sha_at_run": "deadbeef"},
        "in_tree_baseline": {"seconds": 1302.4, "returncode": -15,
                             "head_sha_at_run": "deadbeef"},
    }}))

    measure._run_measurement(out, lambda _m: None)

    assert timed == [str(measure.prc.PROJECT_DIR)], (
        "expected exactly the truncated baseline to be re-timed (the sound throwaway must not "
        "be re-paid for), got {}".format(timed)
    )


def test_a_phase_that_cannot_prove_it_finished_is_re_timed(out, monkeypatch, tmp_path):
    """FAIL-CLOSED, and it needs its own test because the fixture helpers now stamp a completed
    returncode by default -- a default that would otherwise hide this branch entirely.

    A record carrying `seconds` and no `returncode` cannot show its suite ended under its own
    control. Unprovable is not a pass."""
    throwaway = _a_throwaway(tmp_path)
    monkeypatch.setattr(measure.prc, "_head_checkout", _FakeCheckout(throwaway))
    timed = []
    _stub_phases(monkeypatch, timed)
    Path(out).write_text(json.dumps({"phases": {
        "throwaway_checkout": {"seconds": 1411.2, "head_sha_at_run": "deadbeef"},
        "in_tree_baseline": {"seconds": 1302.4, "head_sha_at_run": "deadbeef"},
    }}))

    measure._run_measurement(out, lambda _m: None)

    assert sorted(timed) == sorted([str(throwaway), str(measure.prc.PROJECT_DIR)]), (
        "a phase with no returncode cannot show its suite finished, so both must be re-timed"
    )


def test_a_truncated_phase_still_feeds_the_timeout_floor(out):
    """THE OTHER HALF OF THE ASYMMETRY, and the one that would wedge publishing if it were got
    wrong. Dropping truncated phases outright would blank the fail-closed floor's evidence --
    the same fail-open shape the retired-phase rule exists to avoid. A suite that provably ran
    1302.4s before it was killed is a genuine LOWER BOUND, and a lower bound can only push the
    bound UP.

    MUTATION: have `_load_banked_phases` drop non-completing phases instead of marking them, and
    the floor loses this evidence -- this reds."""
    kept = measure._load_banked_phases(_banked(
        out, in_tree_baseline={"seconds": 1302.4, "returncode": -15}))

    assert "in_tree_baseline" in kept, (
        "a truncated phase was discarded -- its seconds is real evidence of how long this suite "
        "runs, and the timeout floor is fail-CLOSED on having none"
    )
    assert kept["in_tree_baseline"]["retimed_because_truncated"] is True
    assert measure.prc.measured_gate_timeout_floor(out) == 2604, (
        "the floor must still read a truncated phase's lower bound: 1302.4 * 2"
    )


def test_the_record_says_when_its_worst_phase_is_only_a_lower_bound(out, monkeypatch, tmp_path):
    """A reader re-deriving the bound from `worst_legitimate_seconds` must not read a killed
    run's partial time as a completed runtime.

    MUTATION: hardcode `worst_is_a_lower_bound` to False and this reds."""
    monkeypatch.setattr(measure.prc, "_head_checkout", _FakeCheckout(_a_throwaway(tmp_path)))
    _stub_phases(monkeypatch, [])
    # The re-timed baseline is killed again, and it is the SLOWEST thing in the record -- so the
    # timeout floor now rests on a run that never finished.
    monkeypatch.setattr(measure, "_time_suite", lambda cwd, log, heartbeat=None: {
        "cwd": str(cwd), "head_sha_at_run": "deadbeef", "seconds": 1302.4,
        "returncode": -15, "summary": ".........", "box_was_quiet": True})
    Path(out).write_text(json.dumps({"phases": {
        "throwaway_checkout": {"seconds": 900.0, "returncode": 1,
                               "head_sha_at_run": "deadbeef"},
    }}))

    measure._run_measurement(out, lambda _m: None)

    rec = _read(out)
    assert rec["worst_legitimate_phase"] == "in_tree_baseline"
    assert rec["implied_timeout_floor_2x"] == 2604
    assert rec["worst_is_a_lower_bound"] is True, (
        "the bound rests on a phase that was still running when it died, and the record does "
        "not say so"
    )
    assert rec["complete"] is False, (
        "`complete` is the one field a reader is told to check, and launch 11 wrote it true "
        "over a killed baseline"
    )


def test_a_truncated_phase_does_not_count_as_half_a_comparable_pair(out, monkeypatch):
    """THE GAP THE COMPLETION RULE LEFT, caught on launch 12 rather than reasoned about.

    `_drop_incomparable_ratio_phases` short-circuits when both ratio phases are already banked --
    a pair timed together at an earlier commit is comparable to itself, so re-timing it is 40
    wasted minutes. That test was `name in phases` while the completion rule that landed beside it
    made "banked" mean something stricter, so a TRUNCATED baseline counted as present here and as
    owed everywhere else. Launch 12 duly skipped a throwaway banked at d1a5875b4 as "not re-run"
    and set about re-timing the baseline at 7ef696ea8: a ratio spanning two commits, reported as
    the cost of the checkout.

    MUTATION: restore `all(name in phases ...)` and this reds -- the throwaway is kept and the
    pair spans commits."""
    phases = {"throwaway_checkout": {"seconds": 1411.2, "returncode": 1,
                                     "head_sha_at_run": "old111"},
              "in_tree_baseline": {"seconds": 1302.4, "returncode": -15,
                                   "head_sha_at_run": "old111"}}

    dropped = measure._drop_incomparable_ratio_phases(phases, "new222", lambda _m: None)

    assert dropped == ["in_tree_baseline", "throwaway_checkout"], (
        "a truncated baseline is OWED, so its throwaway partner is not half of a banked pair -- "
        "keeping it pairs a phase timed at one commit with one timed at another"
    )
    assert "throwaway_checkout" not in phases


def test_a_genuinely_complete_pair_is_still_not_re_paid_for(out):
    """The other direction, so the fix above is not just "drop more". Two COMPLETED phases at one
    earlier commit are comparable to each other and must survive -- otherwise every launch at a
    new HEAD re-pays 40 minutes to learn the same ratio."""
    phases = {"throwaway_checkout": {"seconds": 1411.2, "returncode": 1,
                                     "head_sha_at_run": "old111"},
              "in_tree_baseline": {"seconds": 1302.4, "returncode": 0,
                                   "head_sha_at_run": "old111"}}

    dropped = measure._drop_incomparable_ratio_phases(phases, "new222", lambda _m: None)

    assert dropped == []
    assert sorted(phases) == ["in_tree_baseline", "throwaway_checkout"]


# ── THE BASIS MUST BE A CLAIM ABOUT THE PHASE IT SITS BESIDE (2026-08-11) ─────────────────────
#
# THE DEFECT THESE FIRE ON IS IN THE BANKED RECORD, not in a scenario. Launch 13 wrote:
#
#     "ran_to_completion": true,
#     "ran_to_completion_basis": "observed: a negative returncode is death by signal, so the
#                                 suite never reported and its seconds is a lower bound"
#
# beside `returncode: 1` and a summary reading "23,831 passed ... in 1771.69s". Both `_basis`
# fields were fixed literals written next to a COMPUTED verdict, so each described one branch and
# contradicted the other. `hit_memory_ceiling_basis` had it the other way: the basis for a
# positive cgroup-kill inference, stamped beside `false` on two phases that never saw a SIGKILL.
#
# WHY IT IS LOAD-BEARING HERE OF ALL PLACES: "its seconds is a LOWER BOUND" is the exact sentence
# this harness's asymmetry turns on -- floors admit a lower bound, the ratio refuses it. The one
# number OPS2 still owes is that ratio, and the record was telling its next reader that the only
# phase which ran to completion was a lower bound. The boolean was right the whole time; the
# prose beside it said the opposite, and prose is what a human reads.
#
# THE CONTROL IS THE PHASE'S OWN RETURNCODE, quoted back. A single literal cannot quote a
# per-phase number, so a revert to one reds these without any test needing to match on wording.
def _completion_basis_cases():
    return [(1, False), (0, False), (-15, False), (-9, True), (None, False)]


def test_the_completion_basis_quotes_the_returncode_it_was_computed_from():
    """MUTATION (RUN): collapse `_ran_to_completion_basis` to the old single literal and this
    reds on every returncode but -15, because a fixed sentence cannot name the number it is
    about. This is deliberately not a keyword match on the prose -- the property is that the
    basis was derived from THIS phase's evidence."""
    for rc, hit in _completion_basis_cases():
        basis = measure._ran_to_completion_basis(rc, hit)
        if rc is None or hit:
            continue
        assert str(rc) in basis, (
            "the basis for returncode {} never mentions it, so it is a paragraph about the "
            "field rather than a claim about this phase: {!r}".format(rc, basis)
        )


def test_a_completed_phase_is_never_described_as_a_lower_bound():
    """THE OBSERVED DEFECT, made to fail. The banked `throwaway_checkout` carried `true` next to
    the words "its seconds is a lower bound", which is the discriminator that decides whether the
    number may be a ratio denominator.

    MUTATION (RUN): restore the single literal and this reds on rc=1 and rc=0.

    THE PROPERTY IS TWO DIRECTIONS, NOT A BICONDITIONAL, and the difference is real rather than a
    convenience. A phase killed by a signal or against its ceiling HAS a lower bound -- it ran
    that long and was heading further. A phase with no returncode at all has no such claim to
    make: its non-completion is unprovable, which this harness treats as not-completed
    (fail-closed) without thereby asserting anything about what its seconds means. Demanding the
    words "lower bound" there would be inventing evidence to satisfy a symmetry."""
    for rc, hit in _completion_basis_cases():
        completed = measure._ran_to_completion_from(rc, hit) if isinstance(rc, int) else False
        basis = measure._ran_to_completion_basis(rc, hit)
        if completed:
            assert "lower bound" not in basis, (
                "returncode {} ran to completion but its basis calls the runtime a lower bound: "
                "{!r} -- that sentence is what disqualifies a ratio denominator".format(rc, basis)
            )
        elif isinstance(rc, int) and (rc < 0 or hit):
            assert "lower bound" in basis, (
                "returncode {} (hit_ceiling={}) died mid-suite, so its seconds is a lower bound "
                "and the record must say so: {!r}".format(rc, hit, basis)
            )
        else:
            assert "lower bound" not in basis, (
                "returncode {!r} yields no evidence about the runtime at all, so claiming a "
                "lower bound would be inventing one: {!r}".format(rc, basis)
            )


def test_every_way_the_memory_verdict_can_be_false_states_a_different_reason():
    """A verdict with three distinct causes and one sentence is a verdict that hides two of them.
    The SIGKILL-but-MemAvailable-unreadable case is the one that matters: it is not a `false`, it
    is an unanswered question, and it used to render as a confident cgroup-kill sentence.

    MUTATION (RUN): return one literal from `_hit_memory_ceiling_basis` and this reds."""
    starved = measure.MIN_MEMORY_HEADROOM_MB - 1
    roomy = measure.MIN_MEMORY_HEADROOM_MB + 1
    cases = {
        "not a sigkill": (1, roomy),
        "sigkill, box starved": (-9, starved),
        "sigkill, memory unreadable": (-9, None),
        "sigkill, box roomy": (-9, roomy),
    }
    bases = {}
    for label, (rc, mem) in cases.items():
        hit = measure._looks_like_the_bound(rc, mem)
        bases[label] = measure._hit_memory_ceiling_basis(rc, mem, hit)

    assert len(set(bases.values())) == len(cases), (
        "two of these distinct causes share one sentence: {}".format(bases)
    )
    assert bases["sigkill, box roomy"].startswith("inferred:")
    assert bases["not a sigkill"].startswith("observed:"), (
        "a returncode is read, not inferred -- R9 labels are the claim, not decoration"
    )
    assert bases["sigkill, memory unreadable"].startswith("unavailable:"), (
        "the discriminator had no input, so nothing may be claimed -- an unanswered question "
        "rendered as a confident verdict is the fail-silent shape R15 names"
    )


def test_the_banked_record_agrees_with_the_basis_written_beside_it():
    """THE POPULATION CHECK, over the REAL record rather than a fixture -- because a fixture is
    where this defect was already invisible for two launches. Every banked phase's stored basis
    is re-derived from that phase's own returncode and must match.

    This reads a live artefact, so it can red mid-tick with no source change. That is the same
    property as the timeout floor above and it is wanted: the record is the evidence.

    THE ANTI-VACUITY PROPERTY IS NOT HERE, AND PUTTING IT HERE WAS A FALSE POSITIVE THAT WOULD
    HAVE WEDGED PUBLISHING -- caught within minutes of committing it, by the very measurement this
    tick launched. The first draft required at least one banked phase to carry a basis. But the
    harness legitimately DROPS both ratio phases whenever HEAD moves under it (the comparability
    rule), and this tick's own commit did exactly that: the record fell back to `cold_checkout`
    alone, which predates these fields, so the guard fired on a healthy transient state. This test
    is in the publish gate's scope, and a control that reds for the ~40 minutes of every re-timing
    is the 41-hour wedge shape this atom exists to close.

    An empty population here is a REAL empty population, so this test grades pairing and says so.
    The question the vacuity guard was reaching for -- "does the harness still WRITE a basis?" --
    is a property of the writer, not of whatever happens to be banked, and it is graded against
    the writer in `test_the_writer_still_emits_a_basis_beside_every_verdict` below, where no
    re-timing can starve it."""
    record = json.loads(Path(measure.prc.GATE_SUBJECT_COST_RECORD).read_text())
    phases = record.get("phases") or {}
    checked = 0
    for name, phase in phases.items():
        if "ran_to_completion_basis" not in phase:
            continue
        checked += 1
        hit = phase.get("hit_memory_ceiling") is True
        # ASKED IN THE PHASE'S OWN TERMS: `memory_max_mb` is what THAT phase ran under, and the
        # module constant now ratchets away from it. Re-deriving with today's constant would make
        # this control red on every ceiling move -- a healthy mechanism wedging publishing.
        expected = measure._ran_to_completion_basis(phase.get("returncode"), hit,
                                                    phase.get("memory_max_mb"))
        assert phase["ran_to_completion_basis"] == expected, (
            "phase {!r} states evidence that does not follow from its own returncode {!r}:\n"
            "  stored:   {}\n  implied:  {}".format(
                name, phase.get("returncode"), phase["ran_to_completion_basis"], expected)
        )
        assert ("lower bound" in phase["ran_to_completion_basis"]) is not (
            phase.get("ran_to_completion") is True), (
            "phase {!r} contradicts itself between its boolean and its prose".format(name)
        )
    # NO COUNT ASSERTION -- see the docstring. `checked` is reported so a reader can see what the
    # population actually was rather than inferring coverage from a green tick.
    print("[basis-consistency] graded {} banked phase(s) of {}".format(checked, len(phases)))


def test_the_writer_still_emits_a_basis_beside_every_verdict(out, monkeypatch, tmp_path, runnable_ceiling):
    """THE ANTI-VACUITY CONTROL, moved off the banked population and onto the WRITER.

    The record can legitimately hold no basis at all (a re-timing drops the ratio phases), so
    "some phase carries one" cannot be the guard -- it fires on a healthy state. What must never
    silently stop is the harness EMITTING the field, and that is provable here whatever is banked:
    drive the real phase-record builder with a stubbed suite and assert every verdict it writes
    arrives with the basis that follows from that phase's own returncode.

    MUTATION (RUN): delete either `_basis` key from `_time_suite_under_exclusion`'s returned dict
    and this reds; pin either to a literal and it reds on one of the two returncodes below."""
    monkeypatch.setattr(measure, "_wait_for_quiet", lambda log, heartbeat=None: True)
    monkeypatch.setattr(measure, "_wait_for_memory_headroom", lambda log, heartbeat=None: True)

    for rc, summary in ((1, "4 failed, 23831 passed in 1771.69s"), (-15, ".........")):
        monkeypatch.setattr(measure.subprocess, "run",
                            lambda *_a, **_kw: types.SimpleNamespace(
                                returncode=rc, stdout=summary, stderr=""))
        phase = measure._time_suite_under_exclusion(tmp_path, lambda _m: None)

        for field in ("ran_to_completion", "hit_memory_ceiling"):
            assert field in phase and field + "_basis" in phase, (
                "the harness wrote {!r} without its basis -- a verdict with no stated evidence "
                "is the thing R9 forbids, and the consistency control above cannot see it "
                "because it only grades what is written".format(field)
            )
        assert phase["ran_to_completion_basis"] == measure._ran_to_completion_basis(
            rc, phase["hit_memory_ceiling"]), (
            "the basis written for returncode {} is not the one its own evidence implies".format(rc)
        )
        # Re-derived from the phase's OWN banked oracle answer (`scope_oom_killed`), not from the
        # returncode alone: the verdict now has two inputs, and a consistency check that knows
        # about one of them grades a question the writer stopped asking.
        assert phase["hit_memory_ceiling_basis"] == measure._hit_memory_ceiling_basis(
            rc, phase.get("mem_available_after_mb"), phase["hit_memory_ceiling"],
            phase.get("scope_oom_killed"))
        assert "scope_oom_killed" in phase and "scope_unit" in phase, (
            "the verdict was written without the evidence it was derived from, so nothing "
            "downstream can re-derive it -- which is how the last false verdict survived"
        )
        assert ("lower bound" in phase["ran_to_completion_basis"]) is (rc < 0), (
            "returncode {} was written up as {!r}".format(rc, phase["ran_to_completion_basis"])
        )


def _completed(seconds, sha):
    return {"seconds": seconds, "returncode": 1, "head_sha_at_run": sha,
            "ran_to_completion": True}


def test_a_ratio_is_refused_when_head_moved_between_its_two_phases(out, monkeypatch, tmp_path):
    """THE COMPARABILITY RULE REACHES THE WITHIN-LAUNCH PATH, not only the banked one.

    `_drop_incomparable_ratio_phases` runs at LAUNCH against phases inherited from an earlier
    run. It cannot see a pair timed inside ONE launch at two different commits -- and that is the
    ordinary case here, not the exotic one: each phase is ~20 minutes on a shared tree where the
    publisher and other lanes commit every few minutes. Both phases complete, both are ratio-
    eligible, and the number silently becomes a comparison between two different codebases.

    MUTATION (RUN): delete the `len(spanned) > 1` branch and this reds -- the ratio computes to
    1.5 across two commits with nothing in the record saying so."""
    monkeypatch.setattr(measure.prc, "_head_checkout", _FakeCheckout(_a_throwaway(tmp_path)))
    _stub_phases(monkeypatch, [])
    Path(out).write_text(json.dumps({"phases": {
        "throwaway_checkout": _completed(1800.0, "aaaaaaaaa"),
        "in_tree_baseline": _completed(1200.0, "bbbbbbbbb"),
    }}))

    measure._run_measurement(out, lambda _m: None)

    rec = _read(out)
    assert rec["ratio_throwaway_over_in_tree"] is None, (
        "1800/1200 = 1.5 was reported as the cost of the checkout, but the two runs are of "
        "different code"
    )
    assert "DIFFERENT commits" in rec["ratio_unavailable_because"], (
        "a null with no cause sends the next reader back to the journal: {!r}"
        .format(rec.get("ratio_unavailable_because"))
    )
    assert "aaaaaaaaa" in rec["ratio_unavailable_because"]


def test_a_ratio_at_one_commit_is_still_computed(out, monkeypatch, tmp_path):
    """The other direction, so the guard above is not just "refuse more". Two completed phases at
    the SAME commit are exactly what this measurement exists to produce, and a rule that refused
    them would leave the atom permanently unable to answer its own criterion."""
    monkeypatch.setattr(measure.prc, "_head_checkout", _FakeCheckout(_a_throwaway(tmp_path)))
    _stub_phases(monkeypatch, [])
    Path(out).write_text(json.dumps({"phases": {
        "throwaway_checkout": _completed(1800.0, "aaaaaaaaa"),
        "in_tree_baseline": _completed(1200.0, "aaaaaaaaa"),
    }}))

    measure._run_measurement(out, lambda _m: None)

    rec = _read(out)
    assert rec["ratio_throwaway_over_in_tree"] == 1.5
    assert "ratio_unavailable_because" not in rec


# ── THE STAMP MUST COME FROM THE SUBJECT, NOT FROM THE REPO THIRTY MINUTES LATER ─────────────
#
# THE DEFECT, OBSERVED IN THE LIVE RECORD (launch 14, 2026-08-11), not imagined. Banked:
#
#     "throwaway_checkout": {"cwd": "/var/tmp/publish-gate-head-qey8309l",
#                            "head_sha_at_run": "a322429d1...", "seconds": 1873.7}
#
# The launch started at 20:29:36Z and the next phase entered at 21:33:51Z, so that suite started
# at ~21:02:37Z -- and `git show -s --format=%cI a322429d1` is 21:26:07Z, TWENTY-THREE MINUTES
# LATER. The tree under test was a `git archive` extraction taken before that commit existed; it
# could not contain it. `head_sha_at_run` was `prc._head_sha()` read in the LIVE repo AFTER the
# suite returned, so it named whatever another lane landed during the run.
#
# WHY IT MATTERS, and why it bites THIS atom: that field is the only input to the cross-commit
# comparability guard the two tests above enforce. End-stamping makes it FAIL-OPEN in exactly the
# conditions this harness waits for -- a quiet second phase ends at the same SHA the first phase
# drifted into, `spanned` sees one commit, and the ratio is computed across two different
# codebases and published as the cost of the checkout. And FAIL-CLOSED the other way: a pair that
# genuinely ran the same code is refused because one unrelated commit landed during phase two.
#
# These drive the real builder against a REAL git repo, so nothing here asserts a stub against
# itself: the subject is asked what it is, and the live repo is given a sentinel that must not
# appear in the record.

def _a_repo(path: Path, message="first"):
    """A real one-commit git repo at `path`, returning its SHA."""
    env = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
           "GIT_COMMITTER_EMAIL": "t@t", "PATH": os.environ.get("PATH", "")}
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q"], cwd=str(path), env=env, check=True)
    return _a_commit(path, message)


def _a_commit(path: Path, message):
    env = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
           "GIT_COMMITTER_EMAIL": "t@t", "PATH": os.environ.get("PATH", "")}
    subprocess.run(["git", "commit", "-q", "--allow-empty", "-m", message],
                   cwd=str(path), env=env, check=True)
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(path), env=env,
                          capture_output=True, text=True, check=True).stdout.strip()


def _run_the_phase(monkeypatch, cwd, on_suite=None, returncode=1):
    """Drive the REAL phase-record builder with a stubbed suite, leaving git alone.

    The stub dispatches: `git` argv go to the real subprocess (so `_subject_sha` asks a real
    repo a real question), anything else is the pytest that is not being run here. `on_suite` is
    called at the moment the suite would be running -- which is where a mid-run commit lands."""
    real_run = subprocess.run

    def dispatch(argv, *args, **kwargs):
        if argv and argv[0] == "git":
            return real_run(argv, *args, **kwargs)
        if on_suite is not None:
            on_suite()
        return types.SimpleNamespace(returncode=returncode, stdout="1 failed in 1.00s", stderr="")

    monkeypatch.setattr(measure, "_wait_for_quiet", lambda log, heartbeat=None: True)
    monkeypatch.setattr(measure, "_wait_for_memory_headroom", lambda log, heartbeat=None: True)
    monkeypatch.setattr(measure, "_bounded_argv", lambda cwd, log, unit=None: ["pytest"])
    monkeypatch.setattr(measure.subprocess, "run", dispatch)
    return measure._time_suite_under_exclusion(Path(cwd), lambda _m: None, None)


def test_the_phase_stamps_the_sha_of_the_subject_it_ran_in(monkeypatch, tmp_path):
    """The subject is asked what commit it is; the live repo is not asked what it has become.

    A throwaway checkout is a DIFFERENT repo from the one this process lives in
    (`_make_checkout_a_repo` writes its `.git/HEAD` to the extracted SHA), so `prc._head_sha()`
    -- which always asks PROJECT_DIR -- is the wrong repo, not merely the wrong moment.

    MUTATION (RUN): put `prc._head_sha()` back as the stamp and this reds on the sentinel."""
    subject = tmp_path / "checkout"
    sha = _a_repo(subject)
    monkeypatch.setattr(measure.prc, "_head_sha", lambda: "LIVE-REPO-NOT-THE-SUBJECT")

    phase = _run_the_phase(monkeypatch, subject)

    assert phase["head_sha_at_run"] == sha, (
        "the phase was stamped {!r}, which is not the commit of the tree it ran in"
        .format(phase["head_sha_at_run"])
    )
    assert phase["head_sha_at_run"] != "LIVE-REPO-NOT-THE-SUBJECT", (
        "the stamp came from the live repo, so the comparability guard is comparing labels that "
        "belong to neither subject -- the launch-14 defect"
    )
    assert phase["subject_changed_during_run"] is False, (
        "a checkout cannot move under itself; True here is evidence of a bug, not of a commit"
    )


def test_a_commit_landing_mid_suite_does_not_relabel_the_phase(monkeypatch, tmp_path):
    """THE OBSERVED DEFECT, REPRODUCED. A commit lands while the suite runs -- the ordinary case
    on this tree, where other lanes commit every few minutes through a ~30-minute phase.

    End-stamping renamed the phase after its own subject: launch 14's throwaway was labelled with
    a commit made 23 minutes after its suite had started. Start-stamping keeps the label the
    subject actually had, and the move is recorded rather than swallowed.

    MUTATION (RUN): stamp `head_sha_at_run` after the suite instead of before, and this reds --
    `head_sha_at_run` becomes the mid-run commit and the phase claims to have run code it never
    saw."""
    subject = tmp_path / "tree"
    before = _a_repo(subject)
    landed = {}

    def another_lane_commits():
        landed["sha"] = _a_commit(subject, "another lane, mid-suite")

    phase = _run_the_phase(monkeypatch, subject, on_suite=another_lane_commits)

    assert phase["head_sha_at_run"] == before, (
        "the phase was relabelled to {!r}, a commit that did not exist when its suite started"
        .format(phase["head_sha_at_run"])
    )
    assert phase["head_sha_at_end"] == landed["sha"], (
        "the mid-run commit is invisible in the record, so a reader cannot tell a frozen subject "
        "from one that took an edit while it was being timed"
    )
    assert phase["subject_changed_during_run"] is True
    assert phase["started_at"] <= phase["ended_at"]


def test_the_writer_stamps_every_phase_with_its_subject_and_its_clock(monkeypatch, tmp_path):
    """The non-emptiable half, and it is here for a reason this module has already been taught
    once: a population control over the banked record cannot be the guard, because the harness
    legitimately DROPS both ratio phases whenever HEAD moves under it. What must never silently
    stop is the WRITER emitting these fields, and that is provable whatever is banked.

    MUTATION (RUN): delete any one of the four keys from `_time_suite_under_exclusion`'s returned
    dict and this reds."""
    subject = tmp_path / "tree"
    sha = _a_repo(subject)

    for rc in (1, -15):
        phase = _run_the_phase(monkeypatch, subject, returncode=rc)
        for field in ("head_sha_at_run", "head_sha_at_end", "started_at", "ended_at"):
            assert phase.get(field), (
                "the harness banked a phase with no {!r} -- the comparability guard and the "
                "postdating control both read it, and both fail SILENTLY on its absence"
                .format(field)
            )
        assert phase["head_sha_at_run"] == sha
        assert "subject_changed_during_run" in phase


def _phases_stamped_after_their_own_start(rec, repo):
    """(graded, offenders) for a record, against git's OWN commit dates in `repo`.

    A phase cannot have run code committed after that phase started: the tree was already
    extracted (a checkout) or already collected (in-tree). Written as a helper so the criterion
    can be put on trial with an oracle below rather than only asked where it has always answered
    -- the live record legitimately holds phases with no `started_at` at all, so the live call
    can grade an empty population and a criterion tried only on its own declared points is not
    one that has been shown to fire."""
    graded, offenders = [], []
    for name, phase in sorted((rec.get("phases") or {}).items()):
        if not isinstance(phase, dict):
            continue
        sha, started = phase.get("head_sha_at_run"), phase.get("started_at")
        if not sha or not started:
            continue
        shown = subprocess.run(["git", "show", "-s", "--format=%cI", sha],
                               cwd=str(repo), capture_output=True, text=True)
        if shown.returncode != 0:
            continue  # a commit this repo no longer has cannot be dated here
        committed = datetime.datetime.fromisoformat(
            shown.stdout.strip()).astimezone(datetime.timezone.utc)
        began = datetime.datetime.strptime(started, "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=datetime.timezone.utc)
        graded.append(name)
        if committed > began:
            offenders.append("{} started {} but is stamped {} committed {}".format(
                name, started, sha[:9], committed.strftime("%Y-%m-%dT%H:%M:%SZ")))
    return graded, offenders


def test_the_postdating_criterion_fires_on_the_defect_that_was_banked(tmp_path):
    """THE ORACLE. The criterion is tried on a record built to carry the launch-14 defect and on
    its honest twin, in a real repo, so it is shown to discriminate -- not merely to pass where
    it has always passed. This is what makes the live-record test below evidence when its
    population is empty.

    The two records differ in ONE value, the phase's `started_at`, either side of the stamped
    commit's own date."""
    repo = tmp_path / "repo"
    _a_repo(repo, "before the phase started")
    later = _a_commit(repo, "landed while the suite was running")
    committed = subprocess.run(["git", "show", "-s", "--format=%cI", later],
                               cwd=str(repo), capture_output=True, text=True).stdout.strip()
    at = datetime.datetime.fromisoformat(committed).astimezone(datetime.timezone.utc)
    before = (at - datetime.timedelta(minutes=23)).strftime("%Y-%m-%dT%H:%M:%SZ")
    after = (at + datetime.timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M:%SZ")

    guilty = {"phases": {"throwaway_checkout": {"head_sha_at_run": later, "started_at": before}}}
    innocent = {"phases": {"throwaway_checkout": {"head_sha_at_run": later, "started_at": after}}}

    graded, offenders = _phases_stamped_after_their_own_start(guilty, repo)
    assert graded == ["throwaway_checkout"] and offenders, (
        "the criterion did not fire on a phase stamped with a commit made 23 minutes after it "
        "started -- which is exactly what launch 14 banked, so it could never have caught it"
    )
    graded, offenders = _phases_stamped_after_their_own_start(innocent, repo)
    assert graded == ["throwaway_checkout"] and not offenders, (
        "the criterion fires on an honestly stamped phase too, so it is an always-red detector "
        "and as ignored as a blind one"
    )


def test_no_banked_phase_stamps_a_commit_that_postdates_its_own_start():
    """The same criterion asked of the artefact on disk, against an INDEPENDENT source: git's own
    commit dates. This is what would have caught launch 14 from the repo alone, with no timeline
    reconstructed by hand.

    It grades whatever population carries both fields and PRINTS its size rather than requiring
    one: phases banked before this fix carry no `started_at`, and a guard keyed to a population a
    healthy mechanism legitimately empties is a second failure mode wearing a vacuity guard's
    clothes (this module has been taught that once already). What cannot go empty is the WRITER
    test above; what proves this criterion can fire at all is the oracle above."""
    live = measure.prc.PROJECT_DIR / "docs" / "observability" / "publish_gate_subject_cost.json"
    if not live.exists():
        pytest.skip("no live measurement record yet")
    rec = json.loads(live.read_text())

    graded, offenders = _phases_stamped_after_their_own_start(rec, measure.prc.PROJECT_DIR)

    print("graded {} banked phase(s) against git commit dates: {}".format(
        len(graded), ", ".join(graded) or "none carry both fields yet"))
    assert not offenders, (
        "a banked phase claims to have run a commit made after it started, so its label is the "
        "live repo's HEAD rather than its own subject -- and the comparability guard is reading "
        "it: {}".format("; ".join(offenders))
    )


def test_a_subject_that_moved_mid_run_is_named_beside_the_ratio(out, monkeypatch, tmp_path):
    """REPORTED, NOT REFUSED -- and the asymmetry against the cross-commit rule is the point.

    A phase whose subject moved mid-run is one subject that took a small edit part-way through,
    not two subjects; and the in-tree phase runs in a shared tree that other lanes commit to
    every few minutes, so refusing on it would starve this atom's one owed number permanently --
    the guard-that-waits-for-a-gap shape. So the ratio still computes, and the record NAMES the
    phase, which is what stops the number being read as a comparison of two frozen trees.

    MUTATION (RUN): drop `ratio_subject_moved_during` and this reds; make the flag a refusal
    instead and the ratio assertion reds."""
    monkeypatch.setattr(measure.prc, "_head_checkout", _FakeCheckout(_a_throwaway(tmp_path)))
    _stub_phases(monkeypatch, [])
    moved = dict(_completed(1200.0, "aaaaaaaaa"), subject_changed_during_run=True)
    Path(out).write_text(json.dumps({"phases": {
        "throwaway_checkout": _completed(1800.0, "aaaaaaaaa"),
        "in_tree_baseline": moved,
    }}))

    measure._run_measurement(out, lambda _m: None)

    rec = _read(out)
    assert rec["ratio_throwaway_over_in_tree"] == 1.5, (
        "a mid-run commit on the shared tree refused the ratio -- that is a gap this box never "
        "gives, so the atom's owed number becomes unreachable rather than caveated"
    )
    assert rec["ratio_subject_moved_during"] == ["in_tree_baseline"], (
        "the ratio is published with nothing saying one of its two subjects changed while it was "
        "being timed: {!r}".format(rec.get("ratio_subject_moved_during"))
    )


# ── THE CEILING IS DERIVED FROM MEASURED DEMAND, AND THE SUBJECT IS THE CGROUP (2026-08-11) ───
#
# WHAT THESE PIN, and why it needed a mechanism rather than a better number. `PHASE_MEMORY_MAX_MB`
# was 8192 because 8192 was "comfortably above any legitimate peak observed", with a comment
# saying to re-derive it from `sample_gate_rss_premium.py`'s peaks when they arrived. They
# arrived -- 5.34G, a PER-PROCESS high-water mark -- and the kernel had already killed this
# phase's CGROUP at its 8192MiB limit with a child at 6.13G inside it. Re-deriving 8192 from
# 5.34G would have set the bound below a demand already observed, and bought a fourth truncation.
#
# So the tests below grade three separate claims, none of which the old constant could make:
#   * the ceiling MOVES WITH ITS EVIDENCE (a pinned constant reds);
#   * the evidence is THIS SCOPE's demand, measured from the kernel's own `memory.peak`, and a
#     peak that cannot be exact SAYS SO;
#   * when the derived ceiling outgrows the box, the phase is REFUSED rather than clamped and
#     re-run -- the clamp is the shape that funded launches 12, 13 and 14.


def test_the_ceiling_moves_with_the_demand_the_record_measured():
    """The derivation reads its evidence. MUTATION: return a constant from
    `_derive_phase_ceiling_mb` -- i.e. the pre-repair 8192 -- and this reds.

    Both floors below sit under this box's cap, so the cap cannot be what separates them."""
    small = measure._derive_phase_ceiling_mb(4096, box_total_mb=64_000)
    large = measure._derive_phase_ceiling_mb(8192, box_total_mb=64_000)

    assert small == int(4096 * measure.CEILING_HEADROOM)
    assert large == int(8192 * measure.CEILING_HEADROOM)
    assert large > small, (
        "the ceiling did not move when the measured demand doubled, so it is a chosen number "
        "wearing a derivation's clothes -- which is exactly the state three launches died in"
    )


def test_a_phase_killed_against_its_ceiling_banks_that_ceiling_as_measured_demand():
    """A cgroup kill is proof that demand REACHED the limit, so the limit is a floor under the
    next one. This is the ratchet: 8192 was measured insufficient, so the next launch is not
    permitted to run at 8192 again.

    MUTATION: read only `scope_peak_mb` and ignore `hit_memory_ceiling` and this reds on the
    live record, whose one killed phase predates the sampler and has no peak field at all."""
    floor = measure._measured_demand_floor_mb({
        "in_tree_baseline": {"hit_memory_ceiling": True, "memory_max_mb": 8192},
    })
    assert floor == 8192, (
        "a phase the kernel killed at 8192MB contributed no floor, so the next ceiling can be "
        "derived at or below a demand already observed to be insufficient: {}".format(floor)
    )


def test_a_phase_that_never_reported_a_peak_does_not_lower_the_floor():
    """Not knowing a phase's peak is not evidence that the phase was small.

    MUTATION: treat a missing/zero `scope_peak_mb` as 0 and include it -- the max is unchanged
    here, but the `None` case below becomes 0 and `_derive_phase_ceiling_mb` then derives a
    ceiling of 0 from a broken instrument. Fail-CLOSED: no evidence falls back to the cited
    kernel figure, never to a small number."""
    assert measure._measured_demand_floor_mb({
        "cold_checkout": {"seconds": 1873.7, "returncode": 0},
        "throwaway_checkout": {"scope_peak_mb": None},
    }) is None
    assert measure._measured_demand_floor_mb({}) is None
    assert measure._derive_phase_ceiling_mb(None, box_total_mb=64_000) == int(
        measure.FALLBACK_DEMAND_FLOOR_MB * measure.CEILING_HEADROOM)


def test_a_demand_this_box_cannot_bound_refuses_the_phase_rather_than_clamping_it(monkeypatch,
                                                                                  tmp_path):
    """THE TERMINUS OF THE RATCHET. A phase whose measured demand needs more than this box can
    spare is UNRUNNABLE here -- running it at the cap reproduces the kill that produced the
    floor, which is what each of launches 12, 13 and 14 did in turn.

    MUTATION: drop the `PHASE_CEILING_IS_SUFFICIENT` check from `_bounded_argv` (the ceiling is
    already clamped to the cap, so the phase would simply run) and this reds."""
    # 12000MB of measured demand on a 16000MB box: 15000 wanted, ~11900 available.
    assert measure._ceiling_is_sufficient(12_000, box_total_mb=16_000) is False
    assert measure._ceiling_is_sufficient(4_000, box_total_mb=16_000) is True
    # ... and the clamp is still visible, which is why sufficiency is asked SEPARATELY.
    assert measure._derive_phase_ceiling_mb(12_000, box_total_mb=16_000) == (
        16_000 - measure.MIN_MEMORY_HEADROOM_MB)

    monkeypatch.setattr(measure, "PHASE_CEILING_IS_SUFFICIENT", False)
    with pytest.raises(measure._Unbounded):
        measure._bounded_argv(tmp_path, lambda _m: None, "ops2-refusal-selftest")


def test_a_box_that_will_not_report_its_size_refuses_rather_than_assuming_a_large_one():
    """An unreadable /proc/meminfo is an unavailable check, and an unavailable check is a FAILED
    check (R15). MUTATION: return True when the cap is unknown and this reds -- and the phase
    that state permits is a 12.9G suite launched at whatever ceiling happened to be derived."""
    assert measure._box_safe_cap_mb(box_total_mb=None, reserve_mb=4096) is None, (
        "an unknown box size produced a cap, so the sentinel for 'the kernel would not say' is "
        "being read as 'ask the box' -- the fail-open branch"
    )
    assert measure._ceiling_is_sufficient(8192, box_total_mb=None) is False


def test_the_shipped_ceiling_clears_every_demand_the_live_record_has_evidence_for():
    """The criterion asked of the artefact on disk rather than of a fixture -- this is the state
    that funded three relaunches: a ceiling of 8192 shipped while the record held a kill AT 8192.

    Stated as a DISJUNCTION so a healthy mechanism cannot wedge the suite: either the ceiling
    clears the measured demand, or the phase is refused outright (`PHASE_CEILING_IS_SUFFICIENT`
    False). Both are correct end states; shipping a ceiling at or below a demand already observed
    while still claiming the phase is runnable is not."""
    live = measure.prc.PROJECT_DIR / "docs" / "observability" / "publish_gate_subject_cost.json"
    if not live.exists():
        pytest.skip("no live measurement record yet")
    floor = measure._measured_demand_floor_mb(json.loads(live.read_text()).get("phases"))
    print("live record's measured demand floor: {}MB; shipped ceiling {}MB; sufficient={}".format(
        floor, measure.PHASE_MEMORY_MAX_MB, measure.PHASE_CEILING_IS_SUFFICIENT))
    if floor is None:
        pytest.skip("no banked phase carries demand evidence yet")

    assert (measure.PHASE_MEMORY_MAX_MB > floor) or not measure.PHASE_CEILING_IS_SUFFICIENT, (
        "the shipped ceiling is at or below a demand the record has already measured, and the "
        "phase is still marked runnable -- so the next launch dies exactly where the last three "
        "did: floor {}MB, ceiling {}MB".format(floor, measure.PHASE_MEMORY_MAX_MB)
    )


# ── THE UNAVAILABLE RATIO MUST GIVE ITS PROGNOSIS, NOT JUST ITS OUTCOME (2026-08-12) ─────────
#
# `ratio_unavailable_because` said "these phases did not run to completion, so their seconds is a
# lower bound" -- accurate about what HAPPENED and silent about whether it can be fixed. Every
# consumer reads that as transient, including this atom's own EXIT text, which still says the
# ceiling must be "re-derived from a measured peak before any relaunch can complete". The
# re-derivation happened; its verdict is that the phase is UNRUNNABLE on this box (10240MB of
# banked demand needs 12800MB, the box spares 11816MB), so `_bounded_argv` refuses before the
# phase starts. Without the clause below, launch 15 gets funded to re-learn that.

# 12000MB of banked demand needs 15000MB at 1.25x; a 16000MB box spares 11904MB. Terminus.
_TOO_BIG = {"in_tree_baseline": {"hit_memory_ceiling": True, "memory_max_mb": 12_000}}
# 4000MB needs 5000MB, which the same box spares comfortably. A relaunch is still worth funding.
_FITS = {"in_tree_baseline": {"scope_peak_mb": 4_000}}


def test_an_unrunnable_phase_says_a_relaunch_cannot_fix_it():
    """THE CONTROL. The clause has to name the three figures a reader needs to act: what demand
    was measured, what ceiling it implies, and what this box can actually spare."""
    clause = measure._terminus_clause(_TOO_BIG, box_total_mb=16_000)

    assert clause, "a phase whose demand this box cannot bound produced no prognosis at all"
    assert "12000MB" in clause and "15000MB" in clause, (
        "the clause must quote the measured demand and the ceiling it implies, or the reader "
        "cannot check the arithmetic that condemns the phase: {}".format(clause))
    assert str(16_000 - measure.MIN_MEMORY_HEADROOM_MB) + "MB" in clause, (
        "the clause must quote what the box can spare: {}".format(clause))
    assert "bigger box, not another launch" in clause


def test_mutation_a_phase_that_still_fits_gets_no_terminus_clause():
    """MUTATION (R15), the other way. If the clause fired regardless of whether the box can hold
    the phase, it would be a fixed string appended to every incomplete run -- and a prognosis
    that is always "give up" is not a measurement, it is a mood. A phase that was merely killed
    or deferred while its demand still fits MUST stay silently retryable."""
    assert measure._terminus_clause(_FITS, box_total_mb=16_000) == ""
    # ... and the same demand on a box that genuinely cannot hold it DOES speak, so the
    # difference is the box and not the phase's presence in the record.
    assert measure._terminus_clause(_FITS, box_total_mb=6_000) != ""


def test_a_record_with_no_demand_evidence_makes_no_prognosis():
    """FAIL-QUIET on absent evidence, deliberately unlike the fail-CLOSED sufficiency check it
    calls. Not knowing a phase's demand is not evidence that the box is too small, and a clause
    that condemned the phase on silence would retire this atom's owed number on no measurement
    at all -- the mirror of the fail-open branch `_measured_demand_floor_mb` exists to close."""
    assert measure._terminus_clause({}, box_total_mb=16_000) == ""
    assert measure._terminus_clause({"in_tree_baseline": {"seconds": 900.0}},
                                    box_total_mb=16_000) == ""


def test_a_box_that_will_not_say_its_size_is_told_apart_from_a_box_that_is_too_small():
    """Two states that both refuse the phase and call for different next moves: buy a bigger box,
    versus find out why the kernel will not report MemTotal. One string for both would send the
    reader shopping for RAM over an unreadable /proc/meminfo."""
    unknown = measure._terminus_clause(_TOO_BIG, box_total_mb=None)
    too_small = measure._terminus_clause(_TOO_BIG, box_total_mb=16_000)

    assert unknown and too_small and unknown != too_small
    assert "MemTotal" in unknown and "bigger box" not in unknown


def test_the_prognosis_reaches_the_artefact_a_reader_actually_opens():
    """WIRED, not merely defined. The clause is only worth anything if it lands in
    `ratio_unavailable_because` -- the field the next reader greps -- alongside the phase name.

    MUTATION: drop the `_terminus_clause(...)` argument from that format call and this reds while
    every unit test above still passes, which is the gap a helper-only test would leave."""
    results = {"phases": dict(_TOO_BIG, throwaway_checkout={
        "seconds": 1876.4, "returncode": 0, "head_sha_at_run": "abc123def"})}
    results["phases"]["in_tree_baseline"].update(
        {"seconds": 1425.1, "returncode": -15, "head_sha_at_run": "abc123def"})

    measure._record_ratio(results, box_total_mb=16_000)

    because = results["ratio_unavailable_because"]
    assert results["ratio_throwaway_over_in_tree"] is None
    assert "in_tree_baseline" in because, "the reason must still name which phase is missing"
    assert "cannot fix it" in because, (
        "the terminus never reached the artefact, so the record still reads as retryable: {}"
        .format(because))


@pytest.mark.skipif(_systemd_run_missing(), reason="systemd-run is the mechanism under test")
def test_the_sampler_reads_this_scopes_own_high_water_mark_from_the_kernel():
    """Spends real seconds proving the instrument measures a real cgroup, for the same reason the
    MemoryMax self-tests above do: asserting that a sampler builds a path proves only that this
    repo can build a path, and would pass on a kernel with no `memory.peak` at all.

    A 400MB allocation inside a 1024MB scope must read back as ~400MB -- not as the ceiling, not
    as zero -- and the sampler's `lower bound` qualifier must AGREE with whether its read
    actually landed after the child exited.

    NARROWED 2026-08-12 (18th publish wedge, this test was the blocking red). Every assertion
    that survives HERE is load-independent: it holds whether or not the final read wins its race
    with systemd's teardown. The assertion that REQUIRED winning that race is gone -- see
    `test_a_read_that_lands_after_exit_is_exact_and_one_that_does_not_is_a_lower_bound`, which
    tests the same qualifier property in both directions without a race. The comment this file
    already carried named the defect exactly ("a verdict decided by ambient load is not a
    control") and then left the load-dependent assertion in the blocking gate anyway, where it
    reddened under the gate's own full-suite fallback and wedged publishing.

    This half keeps the expensive, irreplaceable part: a REAL systemd scope and a REAL kernel
    `memory.peak`. Asserting that a sampler builds a path proves only that this repo can build a
    path, and would pass on a kernel with no `memory.peak` at all."""
    for sampler in _peak_selftest_rounds(attempts=1):
        pass


def _peak_selftest_rounds(attempts):
    """Run the real 400MB-in-a-1024MB-scope self-test, yielding each round's sampler.

    Shared by the blocking test above and the operational one below so BOTH judge the same
    instrument on the same evidence -- a second hand-written copy would be free to drift into
    asserting something the blocking half never checks."""
    alloc = ("import time\n"
             "b = bytearray(400*1024*1024)\n"
             "b[::4096] = b'x' * (len(b)//4096)\n"
             "time.sleep(3)\n")

    for attempt in range(attempts):
        unit = "ops2-peak-selftest-{}-{}".format(os.getpid(), attempt)
        sampler = measure._ScopePeakSampler(unit, poll_seconds=0.5).start()
        res = subprocess.run(measure._scope_argv(unit, memory_max_mb=1024)
                             + [sys.executable, "-c", alloc],
                             capture_output=True, text=True, timeout=180)
        sampler.stop()

        assert res.returncode == 0, "the allocation never ran: {}".format(res.stderr[-300:])
        assert sampler.peak_mb is not None, (
            "the sampler read nothing from a scope that demonstrably ran, so the ceiling has "
            "no measured subject and falls back to a chosen number for ever"
        )
        assert 350 < sampler.peak_mb < 700, (
            "the sampler did not measure this scope's own demand: {}MB for a 400MB allocation "
            "under a 1024MB ceiling".format(sampler.peak_mb)
        )
        assert sampler.source == "memory.peak"
        # The qualifier must AGREE with what the sampler says it got, on every attempt --
        # this is the half that holds even when the race is lost, and it is what stops the
        # sampler from calling a lower bound an exact read.
        assert sampler.is_lower_bound_on_demand(False) is not sampler.read_after_exit
        yield sampler


def _constructed_scope_cgroup(root, unit, peak_bytes):
    """A cgroup directory shaped exactly as `_scope_cgroup_dir` looks for one, under `root`.

    The sampler already takes `root` for this reason, so this is the mechanism's own seam and
    not a hole cut for a test. Whether the directory still EXISTS at `stop()` is under this
    test's control rather than systemd's -- which is the entire point."""
    uid = os.getuid()
    cgdir = (Path(root) / "user.slice" / "user-{}.slice".format(uid)
             / "user@{}.service".format(uid) / "app.slice" / (unit + ".scope"))
    cgdir.mkdir(parents=True)
    (cgdir / "memory.peak").write_text("{}\n".format(peak_bytes))
    return cgdir


def test_a_read_that_lands_after_exit_is_exact_and_one_that_does_not_is_a_lower_bound(tmp_path):
    """The exact/lower-bound QUALIFIER, both directions, with the race taken out.

    ELIMINATION, 2026-08-12 (18th publish wedge). This replaces
    `test_the_sampler_reads_this_scopes_own_high_water_mark_from_the_kernel`'s final assertion,
    which required WINNING A RACE with systemd's asynchronous teardown to observe the exact
    branch. That assertion wedged the publish gate: it is green run alone and red inside its own
    module, so its verdict was decided by ambient load rather than by the instrument -- a
    property the file's own comment had already named and then answered with a retry loop, which
    only lowers the odds. Retrying harder cannot fix a control whose subject is the weather.

    WHERE THE PINNED PROPERTY WENT (an elimination must move the controls that pin it): the
    defect the old assertion guarded is "a sampler that can NEVER read after exit yields only
    lower bounds, so the ratchet can never measure an exact demand". That is tested here
    directly and in BOTH directions, against a cgroup whose existence at `stop()` is controlled
    rather than raced.

    PRECISELY WHAT THIS DOES AND DOES NOT COVER, so it is not read as more than it is: it drives
    `stop()` with no sampling thread, so it proves `stop()` TAKES a final read and qualifies it
    honestly. It does NOT exercise the read-before-join ORDERING that `stop()`'s own comment
    records as measured ("`read_after_exit` was False on every run until this order was
    swapped") -- with no thread there is nothing to join. That ordering remains covered only by
    the real-systemd sibling above, where it is observed rather than asserted.
    What is deliberately NOT asserted any more is that systemd's teardown is sometimes slow
    enough to lose: that is a property of systemd's timing, not of this instrument, and nothing
    the ratchet publishes should hang on it.

    The REAL-cgroup half of the contract is untouched and still blocking in the sibling above,
    which spends real seconds proving `memory.peak` on a genuine 400MB scope reads back as
    ~400MB -- so this constructed fixture cannot become the only evidence that the instrument
    measures anything real."""
    # DIRECTION 1 -- the scope is still there when stop() takes its final read.
    live = _ScopePeakSamplerHarness(tmp_path, "exact", peak_bytes=400 * 1024 * 1024)
    live.sample_once()
    live.stop(remove_cgroup=False)
    assert live.sampler.read_after_exit is True, (
        "the final read did not land on a cgroup that was demonstrably still present -- "
        "`stop()` must read BEFORE it joins, or the exact branch is unreachable by construction"
    )
    assert live.sampler.peak_mb == 400
    assert live.sampler.source == "memory.peak"
    assert live.sampler.is_lower_bound_on_demand(False) is False
    assert "observed:" in live.sampler.basis(False)

    # DIRECTION 2 -- the scope is gone by then, exactly as a lost race leaves it.
    gone = _ScopePeakSamplerHarness(tmp_path, "torn-down", peak_bytes=400 * 1024 * 1024)
    gone.sample_once()
    gone.stop(remove_cgroup=True)
    assert gone.sampler.read_after_exit is False
    assert gone.sampler.peak_mb == 400, (
        "a peak already observed must SURVIVE the teardown -- dropping it would make a torn-down "
        "scope indistinguishable from one that used no memory"
    )
    assert gone.sampler.is_lower_bound_on_demand(False) is True, (
        "a peak with no post-exit read is a LOWER BOUND; labelling it exact is the one error "
        "`_derive_phase_ceiling_mb` must never be fed"
    )
    assert "observed:" not in gone.sampler.basis(False)


class _ScopePeakSamplerHarness:
    """Drives a real `_ScopePeakSampler` against a constructed cgroup, with no sampling thread.

    The thread is what makes the real test slow and racy; the ordering property under test lives
    entirely in `stop()`, so this calls `_sample()`/`stop()` directly."""

    def __init__(self, tmp_path, name, peak_bytes):
        self.root = tmp_path / name
        self.unit = "ops2-constructed-{}".format(name)
        self.cgdir = _constructed_scope_cgroup(self.root, self.unit, peak_bytes)
        self.sampler = measure._ScopePeakSampler(self.unit, root=self.root, poll_seconds=0.01)

    def sample_once(self):
        """One reading while the 'phase' is live, as the polling thread would take."""
        assert self.sampler._sample() is True, "the constructed cgroup was not readable at all"

    def stop(self, remove_cgroup):
        if remove_cgroup:
            shutil.rmtree(self.cgdir)
        self.sampler.stop()


@pytest.mark.skipif(_systemd_run_missing(), reason="systemd-run is the mechanism under test")
def test_a_killed_phases_peak_is_its_ceiling_and_is_labelled_a_lower_bound():
    """The branch that matters to the ratchet, run for real. A phase killed against its bound
    never used more than the bound, so its peak IS the ceiling -- and a reader (or
    `_measured_demand_floor_mb`) taking that for the phase's peak would derive every future
    ceiling from the previous ceiling.

    MUTATION: return False from `is_lower_bound_on_demand` on a killed phase and this reds."""
    unit = "ops2-peak-kill-selftest-{}".format(os.getpid())
    # PACED, not one big bytearray: a scope that dies inside a single allocation can be torn
    # down before any read lands, and this test would then be graded on the sampler's
    # unavailable branch instead of its killed-phase branch. 32MB at a time against a 512MB
    # ceiling takes ~16 steps, an order of magnitude more than the poll interval below.
    alloc = ("import time\n"
             "b = []\n"
             "for _ in range(40):\n"
             "    c = bytearray(32*1024*1024); c[::4096] = b'x' * (len(c)//4096)\n"
             "    b.append(c); time.sleep(0.05)\n")
    sampler = measure._ScopePeakSampler(unit, poll_seconds=0.02).start()
    res = subprocess.run(measure._scope_argv(unit, memory_max_mb=512)
                         + [sys.executable, "-c", alloc],
                         capture_output=True, text=True, timeout=180)
    sampler.stop()

    assert res.returncode != 0, "the 900MB allocation survived a 512MB ceiling"
    assert sampler.peak_mb is not None and sampler.peak_mb <= 512
    assert sampler.is_lower_bound_on_demand(True) is True
    assert "lower bound:" in sampler.basis(True) and "not what the phase wanted" in sampler.basis(
        True)


@pytest.mark.skipif(_systemd_run_missing(), reason="systemd-run is the mechanism under test")
def test_another_scopes_memory_is_not_this_scopes_peak():
    """The same distinction `_scope_oom_killed` had to draw on `oom_memcg=`: a scope whose name
    merely SHARES A PREFIX with a live one is a different cgroup, and reading its memory as this
    one's is how a phase inherits a neighbour's number.

    MUTATION: match on a prefix or a substring in `_scope_cgroup_dir` and this reds -- the
    sampler below would find the sibling scope that is running while it looks."""
    live_unit = "ops2-sibling-selftest-{}-running".format(os.getpid())
    asked_for = "ops2-sibling-selftest-{}".format(os.getpid())
    sampler = measure._ScopePeakSampler(asked_for, poll_seconds=0.25).start()
    subprocess.run(measure._scope_argv(live_unit, memory_max_mb=1024)
                   + [sys.executable, "-c", "import time; b=bytearray(200*1024*1024); "
                                            "b[::4096]=b'x'*(len(b)//4096); time.sleep(2)"],
                   capture_output=True, text=True, timeout=180)
    sampler.stop()

    assert sampler.peak_mb is None, (
        "a scope that does not exist reported {}MB -- borrowed from the sibling scope that was "
        "running throughout".format(sampler.peak_mb)
    )


def test_an_unreadable_cgroup_reads_as_unknown_rather_than_as_zero(tmp_path):
    """FAIL-CLOSED. A zero peak is indistinguishable from 'this phase used no memory', and it is
    fed straight to the ceiling derivation -- so a broken instrument would silently produce a
    tighter ceiling and a fresh round of kills.

    MUTATION: return 0 instead of None from `_read_scope_memory_kb` and this reds."""
    sampler = measure._ScopePeakSampler("ops2-no-such-scope", root=tmp_path, poll_seconds=0.01)
    sampler.stop()

    assert sampler.peak_mb is None and sampler.samples == 0
    assert sampler.is_lower_bound_on_demand(False) is None, (
        "a phase with no peak at all was given a lower-bound VERDICT, so a reader cannot tell "
        "an unmeasured phase from a measured one"
    )
    assert "unavailable:" in sampler.basis(False) and "not zero" in sampler.basis(False)
    assert measure._scope_cgroup_dir("", root=tmp_path) is None
    assert measure._read_scope_memory_kb(None) == (None, None)

    # AND THE OTHER UNREADABLE SHAPE, which the missing-directory case above does NOT reach: the
    # scope directory EXISTS but its memory files do not (a kernel with no memory controller in
    # that cgroup, a scope caught mid-teardown). Measured as a surviving mutation before this
    # was added -- returning 0 from the bottom of `_read_scope_memory_kb` stayed green, because
    # every assertion above exits at the `cgdir is None` guard at the top.
    hollow = tmp_path / "user.slice" / "ops2-hollow-scope.scope"
    hollow.mkdir(parents=True)
    assert measure._scope_cgroup_dir("ops2-hollow-scope", root=tmp_path) == hollow
    assert measure._read_scope_memory_kb(hollow) == (None, None), (
        "a scope whose memory files could not be read reported a NUMBER -- and a zero peak is "
        "fed to the ceiling derivation as measured demand"
    )
    hollow_sampler = measure._ScopePeakSampler("ops2-hollow-scope", root=tmp_path,
                                               poll_seconds=0.01)
    hollow_sampler.stop()
    assert hollow_sampler.peak_mb is None and hollow_sampler.samples == 0


def test_the_banked_phase_carries_its_peak_and_the_provenance_of_its_ceiling(monkeypatch,
                                                                            tmp_path, runnable_ceiling):
    """The record is where the next reader meets these numbers, and a bound whose provenance is
    absent from the record is a round number to them -- which is what 8192 became.

    MUTATION: drop `memory_max_basis`/`scope_peak_basis` from the banked phase and this reds."""
    monkeypatch.setattr(measure, "_wait_for_quiet", lambda log, heartbeat=None: True)
    monkeypatch.setattr(measure, "_wait_for_memory_headroom", lambda log, heartbeat=None: True)
    monkeypatch.setattr(measure.subprocess, "run",
                        lambda *_a, **_kw: types.SimpleNamespace(
                            returncode=0, stdout="1 passed in 0.01s", stderr=""))

    rec = measure._time_suite_under_exclusion(tmp_path, lambda _m: None, None)

    assert rec["memory_max_mb"] == measure.PHASE_MEMORY_MAX_MB
    assert rec["memory_max_demand_floor_mb"] == measure.PHASE_MEMORY_DEMAND_FLOOR_MB
    assert "derived:" in rec["memory_max_basis"] and "headroom" in rec["memory_max_basis"]
    assert "scope_peak_mb" in rec and "scope_peak_source" in rec
    assert rec["scope_peak_is_lower_bound_on_demand"] is None, (
        "no scope existed in this test, so the record must say the peak is UNKNOWN rather than "
        "qualify a number it never took"
    )
    assert "unavailable:" in rec["scope_peak_basis"]
