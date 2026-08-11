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
import fcntl
import json
import os
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
# and re-paid that 21 minutes, and a run that never survives three phases in a row never
# converges. Both directions on every property below.


def _stub_phases(monkeypatch, timed):
    """Make the three phases instantaneous and record which ones actually ran."""
    def _fake_time_suite(cwd, log, heartbeat=None):
        timed.append(str(cwd))
        return {"cwd": str(cwd), "head_sha_at_run": "deadbeef", "seconds": 1.0,
                "returncode": 0, "summary": "", "loadavg_before": 0.0, "loadavg_after": 0.0,
                "box_was_quiet": True}
    monkeypatch.setattr(measure, "_time_suite", _fake_time_suite)
    monkeypatch.setattr(measure, "_wait_for_quiet", lambda log, hb=None: True)
    monkeypatch.setattr(measure.prc, "_head_sha", lambda: "deadbeef")


class _FakeCheckout:
    """Stands in for prc._head_checkout(), yielding the REUSED directory name."""

    def __init__(self, path):
        self._path = path

    def __call__(self):
        return self

    def __enter__(self):
        return self._path

    def __exit__(self, *exc):
        return False


def _banked(out_path, **phases):
    Path(out_path).write_text(json.dumps({"phases": phases}))


def test_a_banked_phase_is_resumed_rather_than_re_run(monkeypatch, out, tmp_path):
    """THE defect: `_run_measurement` opened with `phases: {}` while the comment above
    PHASE_ORDER claimed a partial record "tells the next tick precisely which phases to resume
    rather than restart". It told it nothing, because nothing read it.

    MUTATION: seed `results["phases"]` with `{}` instead of `_load_banked_phases(out_path)` and
    the cold phase is timed again -- this reds."""
    reused = tmp_path / measure.prc.REUSED_HEAD_CHECKOUT_NAME
    reused.mkdir()
    monkeypatch.setattr(measure.prc, "_head_checkout", _FakeCheckout(reused))
    timed = []
    _stub_phases(monkeypatch, timed)
    _banked(out, cold_checkout={"seconds": 1291.9, "head_sha_at_run": "deadbeef"})

    assert measure._run_measurement(out, lambda m: None) == 0

    record = _read(out)
    assert record["resumed_phases"] == ["cold_checkout"]
    assert record["phases"]["cold_checkout"]["seconds"] == 1291.9, (
        "the banked cold phase was overwritten -- 21 minutes of measured runtime re-paid"
    )
    assert len(timed) == 2, "a resumed run re-timed a phase it already had: {}".format(timed)
    assert record["complete"] is True


def test_without_a_partial_record_all_three_phases_are_timed(monkeypatch, out, tmp_path):
    """The other direction. A resume that skipped phases it never had would report a ratio
    built from nothing, which is worse than re-running them."""
    reused = tmp_path / measure.prc.REUSED_HEAD_CHECKOUT_NAME
    reused.mkdir()
    monkeypatch.setattr(measure.prc, "_head_checkout", _FakeCheckout(reused))
    timed = []
    _stub_phases(monkeypatch, timed)

    assert measure._run_measurement(out, lambda m: None) == 0
    assert len(timed) == 3
    assert _read(out)["resumed_phases"] == []


def test_a_phase_with_no_duration_is_not_treated_as_banked(monkeypatch, out, tmp_path):
    """A half-written checkpoint must not retire a phase that was never timed. The record is
    rewritten on every heartbeat, so a run killed mid-write is the expected case, not the
    exotic one."""
    reused = tmp_path / measure.prc.REUSED_HEAD_CHECKOUT_NAME
    reused.mkdir()
    monkeypatch.setattr(measure.prc, "_head_checkout", _FakeCheckout(reused))
    timed = []
    _stub_phases(monkeypatch, timed)
    _banked(out, cold_checkout={"head_sha_at_run": "deadbeef"})  # no `seconds`

    measure._run_measurement(out, lambda m: None)
    assert len(timed) == 3, "a phase with no measured duration was accepted as measured"


def test_an_unparseable_record_starts_over_rather_than_raising(out):
    """Never raises: a corrupt record must cost a re-measurement, never the launch."""
    Path(out).write_text("{ not json")
    assert measure._load_banked_phases(out) == {}
    assert measure._load_banked_phases(str(Path(out).parent / "absent.json")) == {}


def test_a_resume_does_not_delete_the_reused_checkout(monkeypatch, out, tmp_path):
    """The rmtree is the COLD phase's SETUP. Left outside the branch it would delete exactly
    the warmth the next phase exists to measure, and the warm number would silently be a second
    cold number.

    MUTATION: hoist the `shutil.rmtree(reused, ...)` back above the `if` and this reds."""
    reused = tmp_path / measure.prc.REUSED_HEAD_CHECKOUT_NAME
    reused.mkdir()
    (reused / "__pycache__").mkdir()
    monkeypatch.setattr(measure.prc, "HEAD_CHECKOUT_ROOT", tmp_path)
    monkeypatch.setattr(measure.prc, "_head_checkout", _FakeCheckout(reused))
    _stub_phases(monkeypatch, [])
    _banked(out, cold_checkout={"seconds": 1291.9, "head_sha_at_run": "deadbeef"})

    measure._run_measurement(out, lambda m: None)

    assert (reused / "__pycache__").exists(), (
        "the resume deleted the reused checkout's bytecode -- the warm phase it went on to "
        "time was a cold run wearing the warm phase's name"
    )


def test_a_resumed_warm_phase_says_who_warmed_the_cache(monkeypatch, out, tmp_path):
    """"Warm" is a claim about the DIRECTORY, not about this process. When the cold phase came
    from an earlier launch, the record must not imply this run established it."""
    reused = tmp_path / measure.prc.REUSED_HEAD_CHECKOUT_NAME
    reused.mkdir()
    monkeypatch.setattr(measure.prc, "_head_checkout", _FakeCheckout(reused))
    _stub_phases(monkeypatch, [])
    _banked(out, cold_checkout={"seconds": 1291.9, "head_sha_at_run": "deadbeef"})

    measure._run_measurement(out, lambda m: None)
    assert _read(out)["warm_cache_established_by"] == "an earlier launch or the live publisher"


def test_the_record_names_a_phase_timed_at_a_different_commit(monkeypatch, out, tmp_path):
    """Resuming across launches is what makes this converge on a box that keeps killing it --
    and it means the record can span commits. A reader who assumed one SHA would compare
    runtimes of two different suites without knowing it."""
    reused = tmp_path / measure.prc.REUSED_HEAD_CHECKOUT_NAME
    reused.mkdir()
    monkeypatch.setattr(measure.prc, "_head_checkout", _FakeCheckout(reused))
    _stub_phases(monkeypatch, [])
    _banked(out, cold_checkout={"seconds": 1291.9, "head_sha_at_run": "3ee4541a7"})

    measure._run_measurement(out, lambda m: None)
    record = _read(out)
    assert record["phases_from_an_earlier_head"] == ["cold_checkout"]
    # And the other direction: a phase timed at THIS head is not flagged as stale.
    assert "warm_checkout" not in record["phases_from_an_earlier_head"]


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
    # Stamped with the launch's own HEAD so the banked pair is COMPARABLE and survives on its
    # merits. `_drop_incomparable_ratio_phases` would otherwise re-time warm here -- correctly,
    # but for a reason this test is not about, and the deferral contract below would then be
    # asserted against a resume state no real record produces.
    monkeypatch.setattr(measure.prc, "_head_sha", lambda: "headsha0")
    banked = {"phases": {"cold_checkout": {"seconds": 1291.9, "head_sha_at_run": "headsha0"},
                         "warm_checkout": {"seconds": 1167.5, "head_sha_at_run": "headsha0"}}}
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
    assert rec["phases"]["cold_checkout"]["seconds"] == 1291.9, (
        "a deferral threw away a banked phase -- 21 minutes of measurement lost per deferral"
    )
    assert rec["phases"]["warm_checkout"]["seconds"] == 1167.5


def test_repeated_deferrals_accumulate_a_visible_count(monkeypatch, out):
    """The convergence risk the deferral takes on -- a box that is never quiet long enough --
    must surface as a rising number in the artefact, not as a measurement that silently never
    lands.

    MUTATION: make `_prior_deferral_count` return 0 unconditionally and this reds at the second
    deferral, which is exactly the blindness it guards.

    It defers at the guard that now fires FIRST -- the exclusion, held here on the redirected
    lock -- rather than at a stubbed `_wait_for_quiet`. That is not cosmetic: with the wait
    stubbed, a run reaches the cold phase's REAL `prc._head_checkout()` first, so the test
    extracted HEAD into /tmp and its verdict turned on whether a live publisher happened to hold
    the reuse lock."""
    monkeypatch.setattr(measure, "QUIET_WAIT_SECONDS", -1)  # already past the acquire deadline
    holder = open(str(measure.prc.RUN_LOCK_FILE), "w")
    fcntl.flock(holder, fcntl.LOCK_EX | fcntl.LOCK_NB)
    try:
        for expected in (1, 2, 3):
            assert measure._run_measurement(out, lambda _m: None) == 0
            record = _read(out)
            assert record["deferral_count"] == expected
            assert record["deferred"]["at_phase"] == "cold_checkout", (
                "the deferral must name the phase still owed")
    finally:
        fcntl.flock(holder, fcntl.LOCK_UN)
        holder.close()


def test_a_banked_phase_was_always_admitted_quiet(monkeypatch, out):
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


def test_a_phase_holds_the_publishers_run_lock_while_it_times(monkeypatch, tmp_path):
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


def test_the_exclusion_is_re_entrant_so_the_cold_phase_can_span_its_setup(monkeypatch, tmp_path):
    """COLD deletes the reused checkout, rebuilds it and times it under ONE hold. A second
    `flock` on a second fd of the same file blocks even inside one process, so nesting must be
    counted rather than re-attempted -- without this the cold phase deadlocks itself into a
    deferral it would report as a busy publisher."""
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
    through `_time_suite`/`_run_measurement`, which is how it was reached unnoticed here (two of
    the three phases enter it from `_run_measurement`, which no test names). Each such module
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
# These fire on that: the pair is dropped and re-timed together, COLD is not (it only ever
# raises the timeout floor), and a pair already banked together is not re-paid for.

def _banked(out, **phases):
    Path(out).write_text(json.dumps({"phases": phases}))
    return out


def test_a_banked_ratio_phase_from_another_commit_is_dropped(out):
    """THE LIVE PROPERTY. Warm at an older SHA, baseline owed -- warm must be re-timed."""
    _banked(out, cold_checkout={"seconds": 1291.9, "head_sha_at_run": "old111"},
            warm_checkout={"seconds": 1167.5, "head_sha_at_run": "old222"})
    phases = measure._load_banked_phases(out)

    dropped = measure._drop_incomparable_ratio_phases(phases, "head999", print)

    assert dropped == ["warm_checkout"], (
        "a warm phase timed at another commit cannot be the numerator of a ratio whose "
        "denominator is timed at HEAD; it must be re-timed, not inherited"
    )
    assert "warm_checkout" not in phases
    assert "cold_checkout" in phases, (
        "COLD feeds the timeout floor and never the ratio -- an older, slower cold phase can "
        "only RAISE that bound, so re-paying 21 minutes for it buys nothing"
    )


def test_a_ratio_phase_at_this_head_is_kept(out):
    """MUTATION-ADJACENT: a rule that drops everything is as useless as one that drops nothing.

    Without this, `_drop_incomparable_ratio_phases` could return every ratio phase it is shown
    and both the assertion above and the measurement's convergence would still look correct --
    while every launch re-paid 20 minutes for a phase it already held at the right commit."""
    _banked(out, warm_checkout={"seconds": 1167.5, "head_sha_at_run": "head999"})
    phases = measure._load_banked_phases(out)

    assert measure._drop_incomparable_ratio_phases(phases, "head999", print) == []
    assert "warm_checkout" in phases


def test_a_pair_banked_together_at_an_older_commit_is_not_re_timed(out):
    """Both sides at one (earlier) SHA are comparable TO EACH OTHER, which is all the ratio
    asks. Re-timing them would cost 40 minutes to learn the same number."""
    _banked(out, warm_checkout={"seconds": 1100.0, "head_sha_at_run": "old222"},
            in_tree_baseline={"seconds": 1000.0, "head_sha_at_run": "old222"})
    phases = measure._load_banked_phases(out)

    assert measure._drop_incomparable_ratio_phases(phases, "head999", print) == []
    assert set(phases) == {"warm_checkout", "in_tree_baseline"}


def test_a_banked_phase_with_no_recorded_commit_is_dropped(out):
    """FAIL-CLOSED. A phase that cannot be SHOWN to have been timed at this commit is not
    evidence for a criterion about this commit -- unprovable is not a pass."""
    _banked(out, warm_checkout={"seconds": 1167.5})
    phases = measure._load_banked_phases(out)

    assert measure._drop_incomparable_ratio_phases(phases, "head999", print) == ["warm_checkout"]
    assert "warm_checkout" not in phases


def test_the_drop_is_named_in_the_record_not_just_the_log(out, monkeypatch, tmp_path):
    """A drop only in the log is invisible to the next tick: it must be able to tell "this
    launch chose to re-pay for warm" from "the record was lost"."""
    _banked(out, warm_checkout={"seconds": 1167.5, "head_sha_at_run": "old222"})
    monkeypatch.setattr(measure.prc, "_head_sha", lambda: "head999")
    # Defer immediately -- this asserts about the record the launch WRITES, not about a suite.
    monkeypatch.setattr(measure, "_wait_for_quiet",
                        lambda *a, **k: (_ for _ in ()).throw(measure._Deferred("test")))
    monkeypatch.setattr(measure, "_publisher_exclusion",
                        lambda *a, **k: (_ for _ in ()).throw(measure._Deferred("test")))

    measure._run_measurement(out, print)

    rec = json.loads(Path(out).read_text())
    assert rec["dropped_for_comparability"] == ["warm_checkout"]
    assert "warm_checkout" not in rec["phases"], (
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


def test_a_launch_killed_in_the_suite_leaves_a_record_that_says_so(monkeypatch, out, tmp_path):
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


def test_the_two_deaths_are_told_apart_by_the_record_alone(monkeypatch, out, tmp_path):
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
    reused = tmp_path / measure.prc.REUSED_HEAD_CHECKOUT_NAME
    reused.mkdir()
    monkeypatch.setattr(measure.prc, "_head_checkout", _FakeCheckout(reused))
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
    reused = tmp_path / measure.prc.REUSED_HEAD_CHECKOUT_NAME
    reused.mkdir()
    monkeypatch.setattr(measure.prc, "_head_checkout", _FakeCheckout(reused))
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
    reused = tmp_path / measure.prc.REUSED_HEAD_CHECKOUT_NAME
    reused.mkdir()
    monkeypatch.setattr(measure.prc, "_head_checkout", _FakeCheckout(reused))
    _stub_phases(monkeypatch, [])

    assert measure._run_measurement(out, lambda _m: None) == 0

    rec = json.loads(Path(out).read_text())
    assert "previous_launch_died_in_flight" in rec
    assert rec["previous_launch_died_in_flight"] is None


def test_the_marker_records_the_memory_a_killed_phase_never_banks(monkeypatch, out, tmp_path):
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
