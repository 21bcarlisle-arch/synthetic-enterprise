"""Controls on the one launcher, and each names the death it exists for.

THE DEFECTS THESE EXIST FOR are five launches of one measurement and three deaths, all to a cgroup
nobody's `setsid` could escape, plus a live floor leg that ran unrecorded for 35 minutes after the
recording mechanism already existed. The launcher's job is to make both impossible in one call, so
these controls are written against exactly those two failures and not against its shape.

THE PARTITION IS ASSERTED BEFORE ANY LEG'S MEANING IS -- the same rule
`test_launch_liveness.py` opens with. `test_every_outcome_is_reachable` comes first, because a
launcher that refused EVERYTHING would pass every refusal test below it, and a launcher that
verified NOTHING would pass every acceptance test. Both were live possibilities while this was
being written.

BOTH DIRECTIONS OF THE FAIL-CLOSED CHOICE ARE CONTROLLED, because the module makes it twice and in
opposite directions. An unreadable `systemctl` must REFUSE a launch (a wrong "the name is free"
starts a duplicate long run) and must NOT kill one already started (a wrong "the detach failed"
destroys a good job over a broken probe). A single "fails closed" test would pass on a module that
had them the wrong way round.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import time
from pathlib import Path

import pytest

from background import launch_liveness as ll
from background import launch_long_job as llj


class _Runner:
    """A fake `subprocess.run`, answering per argv shape. Records every call it was given."""

    def __init__(self, *, active="", control_group="/user.slice/other.service",
                 run_rc=0, run_err="", show_raises=False, reset_rc=0):
        self.active, self.control_group = active, control_group
        self.run_rc, self.run_err, self.show_raises, self.reset_rc = (
            run_rc, run_err, show_raises, reset_rc)
        self.calls = []

    #: Only the TWO-ARGUMENT form is answered, because that is the only form the real thing
    #: answers. `-p=ActiveState` is accepted by `systemctl show`, prints nothing and exits 0 --
    #: the first draft of this fake matched any argv CONTAINING the property name, so it answered
    #: a flag form that returns empty in production, and nine green tests sat on top of a launcher
    #: that could not read a live unit's state at all. A fake that is more permissive than its
    #: subject converts a fail-open into a passing suite.
    def _requested(self, argv, prop):
        return any(argv[i] == "-p" and argv[i + 1] == prop for i in range(len(argv) - 1))

    def __call__(self, argv, **kw):
        self.calls.append(list(argv))
        if argv[:3] == ["systemctl", "--user", "show"]:
            if self.show_raises:
                raise OSError("systemctl is not answering")
            out = []
            if self._requested(argv, "ActiveState"):
                out.append(f"ActiveState={self.active}")
            if self._requested(argv, "ControlGroup"):
                out.append(f"ControlGroup={self.control_group}")
            return subprocess.CompletedProcess(argv, 0, "\n".join(out) + "\n", "")
        if argv[:3] == ["systemctl", "--user", "reset-failed"]:
            return subprocess.CompletedProcess(argv, self.reset_rc, "", "")
        if argv[:3] == ["systemctl", "--user", "stop"]:
            return subprocess.CompletedProcess(argv, 0, "", "")
        return subprocess.CompletedProcess(argv, self.run_rc, "", self.run_err)

    def ran(self, *prefix):
        return [c for c in self.calls if c[:len(prefix)] == list(prefix)]


@pytest.fixture
def faked_path(monkeypatch):
    """These controls are about the launcher's decisions, not about this machine's PATH.

    NOT autouse, deliberately: the door test at the bottom needs the real `systemd-run`, and a
    fixture it has to UNDO is one that silently stops applying to everything else in the same
    test the day someone adds a second patch.
    """
    monkeypatch.setattr(shutil, "which", lambda name: f"/usr/bin/{name}")


def _launch(tmp_path, runner, **over):
    kwargs = dict(
        artefact=str(tmp_path / "out.json"), workdir=str(tmp_path),
        log=str(tmp_path / "job.log"), records_path=tmp_path / "records.json",
        runner=runner)
    kwargs.update(over)
    return llj.launch("a-long-run", ["python3", "-m", "tools.nothing"], **kwargs)


def test_every_outcome_is_reachable(tmp_path, monkeypatch, faked_path):
    """The partition, before any leg's meaning. A launcher that always refuses passes every
    refusal test below; one that never verifies passes every acceptance test.

    Fires on: a module whose accept path or whose refuse path has become unreachable -- which is
    what a guard tightened one leg at a time turns into, three times in one afternoon.
    """
    monkeypatch.setattr(llj, "own_cgroup", lambda *a, **k: "/user.slice/launcher.service")

    def _refusal(runner, records):
        try:
            _launch(tmp_path, runner, records_path=tmp_path / records)
        except llj.LaunchRefused as exc:
            return str(exc)
        return ""

    accepted = _launch(tmp_path, _Runner())
    by_name = _refusal(_Runner(active="active"), "r2.json")
    by_cgroup = _refusal(_Runner(control_group="/user.slice/launcher.service"), "r3.json")

    assert accepted["claim"] == ll.LIVE and accepted["detached"] is True
    assert "ALREADY RUNNING" in by_name, by_name
    assert "detach did not hold" in by_cgroup, by_cgroup


def test_the_launch_argv_never_carries_collect():
    """`--collect` garbage-collects the unit on exit and takes its exit record with it.

    Fires on: anyone adding `--collect` for tidiness. That record is the ONLY witness that
    survives a group SIGKILL -- `launch_liveness.reask` asks systemd first precisely because the
    job's own rc file is absent in exactly the case it was written to describe. Collect the unit
    and every death downgrades from DIED-with-a-Result to UNKNOWN.
    """
    argv = llj.systemd_run_argv("longjob-x", ["python3", "-c", "pass"],
                                workdir="/tmp", log="/tmp/x.log", description="d")
    assert not any(a.startswith("--collect") for a in argv), (
        f"--collect is in the launch argv: {argv}")
    assert "--user" in argv and "--unit=longjob-x" in argv


def test_both_streams_land_in_one_file_and_python_does_not_buffer():
    """The 09-07 launch left a 240-byte log holding one import warning and no stdout at all.

    Fires on: a launch that redirects only one stream, sends the two to different files, or drops
    PYTHONUNBUFFERED. Python block-buffers stdout to a file; a killed process loses the buffer
    entirely, so an unbuffered stream is the difference between a diagnosable death and a log that
    looks like the job never started.
    """
    argv = llj.systemd_run_argv("longjob-x", ["python3", "-c", "pass"],
                                workdir="/tmp", log="/var/tmp/one.log", description="d")
    assert "--property=StandardOutput=append:/var/tmp/one.log" in argv
    assert "--property=StandardError=append:/var/tmp/one.log" in argv
    assert "--setenv=PYTHONUNBUFFERED=1" in argv
    assert "--property=WorkingDirectory=/tmp" in argv


def test_a_launch_that_lands_in_the_launchers_own_cgroup_is_stopped_and_never_recorded(
        tmp_path, monkeypatch, faked_path):
    """The whole point, asserted at the property and not at a pid.

    Fires on: a launcher that checks "is the pid alive" instead of "whose cgroup owns it". The
    09-07 run was verified live at five minutes by a waiter and was dead by the next tick -- being
    briefly alive is true of every job that is about to be killed. And a launch that did not
    detach must leave NO `live` record behind, or the deadman inherits a claim for a corpse.
    """
    monkeypatch.setattr(llj, "own_cgroup", lambda *a, **k: "/user.slice/app.slice/seat.service")
    runner = _Runner(control_group="/user.slice/app.slice/seat.service/child")
    with pytest.raises(llj.LaunchRefused) as refused:
        _launch(tmp_path, runner)

    assert "KillMode=control-group" in str(refused.value)
    assert runner.ran("systemctl", "--user", "stop"), "the failed launch was left running"
    assert ll.load(tmp_path / "records.json") == [], (
        "a launch that did not detach wrote a `live` record anyway")


def test_an_unverifiable_cgroup_does_not_kill_a_healthy_launch(tmp_path, monkeypatch, faked_path):
    """The OTHER direction of the same choice, and it must not be the same direction.

    Fires on: a launcher that reads a broken probe as a failed detach. `systemd-run` returning 0
    IS the reparenting; an unanswerable `systemctl` is missing corroboration, not evidence. Killing
    a good long run over it would make this module worse than the hand-rolled scripts it replaces.
    """
    monkeypatch.setattr(llj, "own_cgroup", lambda *a, **k: "/user.slice/app.slice/seat.service")
    runner = _Runner(show_raises=True)
    # The name-held probe fails closed, so it would refuse first; let that one answer and break
    # only the ControlGroup read, which is the state under test.
    monkeypatch.setattr(llj, "name_is_held", lambda unit, **kw: False)
    monkeypatch.setattr(llj, "clear_a_corpse", lambda unit, **kw: False)
    entry = _launch(tmp_path, runner)

    assert entry["detached"] is None and "UNVERIFIED" in entry["detach_why"]
    assert not runner.ran("systemctl", "--user", "stop"), (
        "a healthy launch was stopped because its cgroup could not be READ")
    assert ll.load(tmp_path / "records.json")[0]["claim"] == ll.LIVE


def test_an_unreadable_systemctl_refuses_rather_than_starting_a_second_copy(tmp_path, faked_path):
    """Fail-closed on the name, which is the opposite direction to the test above it.

    Fires on: a launcher that treats "we could not ask" as "the name is free". Six launches of one
    measurement got past a `pgrep` guard on 2026-08-10 because the guard could only see the live
    ones; the fixed unit name makes double-launch refusal a fact asserted by init, and that only
    holds while an unreadable answer refuses.
    """
    assert llj.name_is_held("longjob-a-long-run", runner=_Runner(show_raises=True)) is True
    with pytest.raises(llj.LaunchRefused) as refused:
        _launch(tmp_path, _Runner(show_raises=True))
    assert "ALREADY RUNNING" in str(refused.value)


def test_a_corpse_is_cleared_but_a_live_unit_is_never_reset(tmp_path):
    """A FAILED unit stays loaded and its refusal is word-for-word a LIVE unit's.

    Fires on: no clearing (one dead run blocks every future launch of that job forever) and on
    blanket clearing (which deletes a RUNNING measurement's own registration and hands a second
    one the name). Both legs, because a `reset-failed` that fires on everything passes the first
    test alone.
    """
    dead = _Runner(active="failed")
    assert llj.clear_a_corpse("longjob-x", runner=dead) is True
    assert dead.ran("systemctl", "--user", "reset-failed")

    alive = _Runner(active="active")
    assert llj.clear_a_corpse("longjob-x", runner=alive) is False
    assert not alive.ran("systemctl", "--user", "reset-failed")


def test_a_launch_whose_record_cannot_be_written_is_stopped(tmp_path, monkeypatch, faked_path):
    """THE VACUITY THIS MODULE CLOSES: there is no such thing here as a running, unrecorded job.

    Fires on: a launcher that shrugs at a failed record write and returns the running job anyway.
    That state -- alive and invisible -- is what let a live floor leg run unrecorded for 35 minutes
    after `launch_liveness` already existed, and it is invisible to the deadman, to `--check`, and
    to every document asserting it in flight. Stopping the job is the costly half of the trade and
    it is deliberate: a relaunch is one command.
    """
    monkeypatch.setattr(llj, "own_cgroup", lambda *a, **k: "/user.slice/launcher.service")

    def _no(*a, **k):
        raise OSError("read-only file system")

    monkeypatch.setattr(ll, "record", _no)
    runner = _Runner()
    with pytest.raises(llj.LaunchRefused) as refused:
        _launch(tmp_path, runner)

    assert "was stopped" in str(refused.value) and "invisible" in str(refused.value)
    assert runner.ran("systemctl", "--user", "stop"), (
        "a job that could not be recorded was left running, which is the exact invisibility this "
        "launcher exists to abolish")


def test_a_recorded_launch_is_one_the_deadman_can_settle(tmp_path, monkeypatch, faked_path):
    """End to end: what `launch()` writes is what `launch_liveness.check()` re-asks.

    Fires on: a record whose fields the re-ask cannot use -- a missing `unit` (so systemd is never
    asked and every verdict falls through to UNKNOWN) or a missing `artefact` (so a completed run
    can never read as FINISHED). Written against the CONSUMER rather than against the field names,
    because the two modules going out of step is silent otherwise.
    """
    monkeypatch.setattr(llj, "own_cgroup", lambda *a, **k: "/user.slice/launcher.service")
    records = tmp_path / "records.json"
    entry = _launch(tmp_path, _Runner(), records_path=records)
    assert entry["unit"] == "longjob-a-long-run"

    Path(entry["artefact"]).write_text("{}", encoding="utf-8")
    stale, lines, settled = ll.check(
        records, probe=lambda unit: {"ActiveState": "inactive", "Result": "success",
                                     "ExecMainStatus": "0"})
    assert stale == 1 and settled[0]["claim"] == ll.FINISHED, lines
    assert json.loads(records.read_text())[0]["claim"] == ll.FINISHED


def test_the_unit_name_is_fixed_and_derivable_from_the_job(tmp_path):
    """A record's reader must be able to ask systemd about the job without a string only the
    launcher knew.

    Fires on: a per-launch unique unit name (a pid, a timestamp). Uniqueness would defeat the one
    protection init gives for free -- it refuses to start a second unit under a live name -- and
    would leave `systemctl --user list-units 'longjob-*'` unable to census what is in flight.
    """
    assert llj.unit_name("A Long Run/2026") == "longjob-a-long-run-2026"
    assert llj.unit_name("a-long-run") == llj.unit_name("A Long Run")
    with pytest.raises(llj.LaunchRefused):
        llj.unit_name("///")


@pytest.mark.real_subprocess
@pytest.mark.skipif(shutil.which("systemd-run") is None, reason="no user systemd here")
def test_a_real_launch_detaches_and_logs_both_streams(tmp_path):
    """THE DOOR. Everything above runs against a fake runner and is therefore blind to whether
    these properties are ones systemd actually accepts.

    Fires on: a property name systemd rejects, an `append:` form it does not support, a unit that
    lands in the launcher's own cgroup for real. Four seconds of a real transient unit buys the one
    thing no fake can: that the argv this module builds is an argv the init system will take.

    IT EARNED ITS PLACE ON ITS FIRST RUN. `_show` was built with `-p=ActiveState`, which
    `systemctl show` accepts, answers with nothing, and exits 0 -- so every property read came
    back empty with a healthy rc and `name_is_held` read that as "the name is free". Nine tests
    above this one were green against a launcher that could not read a live unit at all, and
    would have started a second copy of a long job beside a running one.
    """
    log, artefact = tmp_path / "real.log", tmp_path / "real.json"
    job = f"selftest-{abs(hash(str(tmp_path))) % 10**8}"
    unit = llj.unit_name(job)
    try:
        # It has to still be RUNNING when we look. A job that exits instantly is already
        # collected by the time the cgroup is probed -- observed on the first run of this test,
        # and it is why `verify_detached` reports UNVERIFIED rather than a failure for that case.
        entry = llj.launch(
            job, ["/bin/bash", "-c",
                  f"echo to-stdout; echo to-stderr >&2; echo '{{}}' > {artefact}; sleep 4"],
            artefact=str(artefact), workdir=str(tmp_path), log=str(log),
            records_path=tmp_path / "records.json")
        assert entry["detached"] is True, entry["detach_why"]
        # A bounded wait on the artefact this launch names -- ten seconds, then we read whatever
        # is there and let the assertion say what was missing.
        for _ in range(100):
            if artefact.exists():
                break
            time.sleep(0.1)
        text = log.read_text(encoding="utf-8")
        assert "to-stdout" in text and "to-stderr" in text, (
            f"both streams must reach one file; got {text!r}")
    finally:
        subprocess.run(["systemctl", "--user", "stop", unit], capture_output=True, timeout=60)
        subprocess.run(["systemctl", "--user", "reset-failed", unit],
                       capture_output=True, timeout=60)
