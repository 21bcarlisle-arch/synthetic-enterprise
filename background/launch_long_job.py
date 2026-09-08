"""The one way a long job is launched: a transient user unit, and its liveness record, in one call.

THE DEFECT THIS EXISTS FOR. Five launches of one measurement, three deaths, one cause:

    $ cat /proc/self/cgroup                       # inside a bounded tick, or this seat
    0::/user.slice/user-1000.slice/user@1000.service/app.slice/seat-executor.service
    $ systemctl --user show worker-tick.service -p KillMode
    KillMode=control-group

`setsid` changes the SESSION and the PROCESS GROUP. A cgroup is neither, so a textbook POSIX
detach is irrelevant to the actual killer: when the launching service's oneshot finishes, systemd
SIGKILLs every process in its cgroup, `setsid` child included. The 2026-08-28 run recorded
`pid==pgid==sess` -- the detach demonstrably HELD -- and died anyway. So did the 09-07 relaunch.
So did the 09-08 one.

`systemd-run --user` reparents the job to the user manager, so it lives in a cgroup of its own and
the tick's teardown cannot reach it. That remedy has been known since 2026-08-29 and was
rediscovered by dying twice since, because it was banked inside ONE tool
(`tools/measure_publish_gate_subject_cost.py:_systemd_run_argv`) and every other long job
hand-rolled its own launch in a throwaway `/var/tmp/*.sh`. Five such scripts existed when this was
written; each had learned a different subset of the same lesson, and the newest still had to
rediscover the rest.

THE RECORD IS NOT A SEPARATE STEP, AND THAT IS THE POINT. `background/launch_liveness.py` holds a
launch claim a later reader can RE-ASK, and `deadmans_switch._check_launch_liveness` re-asks every
one of them on a timer. But nothing PERFORMED a launch, so writing the record stayed a thing the
launcher had to remember -- and the live floor leg went unrecorded for 35 minutes after the
mechanism existed, which is the vacuity this closes. Here there is no launch without a record:
`launch()` writes one, and A JOB WHOSE RECORD COULD NOT BE WRITTEN IS STOPPED (see `launch`). An
unrecorded long job is invisible to everything downstream, and invisible is the state that cost
four launches; a relaunch costs one command.

WHAT THIS DELIBERATELY DOES NOT DO.

  * **No rc file.** The 09-07 script wrote one precisely so "gone" could be told from "gone with
    rc=137", and it could not: a group SIGKILL takes the wrapper that would have written it, so the
    file is absent in exactly the case it was built to describe. An exit status written by the
    process being killed cannot report its own kill. systemd holds an exit record the job had no
    part in writing, and that is what `launch_liveness.reask()` asks first.
  * **No `--collect`, ever.** `--collect` garbage-collects the unit on exit and takes the exit
    record with it, turning a diagnosable death into `UNKNOWN`. That is the one systemd-run flag
    this module must never grow; `tests/background/test_launch_long_job.py` says so.
  * **No shell wrapper.** `StandardOutput=append:` and `StandardError=append:` point BOTH streams
    at one file, in order, and `PYTHONUNBUFFERED=1` stops python block-buffering stdout into a
    buffer a kill discards. The 09-07 launch left a 240-byte log holding one import warning and not
    one byte of stdout, and nobody could say what command produced it. Those were three separate
    hand-rolled fixes across three scripts; here they are properties of the unit.
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

from background import launch_liveness

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent

#: Every unit this module starts carries it, so `systemctl --user list-units 'longjob-*'` is the
#: census of what this seat has in flight -- and a job's unit name is derivable from its job name
#: by anyone reading a record, rather than being a string only the launcher knew.
UNIT_PREFIX = "longjob-"

#: The ActiveStates that mean a name is held by something still alive. Kept in step with
#: `launch_liveness._STILL_GOING` on purpose: the two modules must agree on what "not finished yet"
#: means, or a launch refuses a name the re-ask has already settled.
_HOLDING = ("active", "activating", "reloading", "deactivating")


class LaunchRefused(RuntimeError):
    """A launch that did not happen, carrying WHY in its message.

    Never raised for "we could not look" -- see `verify_detached`. A refusal that names its reason
    is how you find out the refusal itself was wrong.
    """


def unit_name(job: str) -> str:
    """The FIXED unit name for `job`. Fixed is load-bearing, not cosmetic.

    systemd refuses to start a second unit under a name already active, so double-launch refusal
    becomes a fact asserted by init rather than a command line this harness parses and could
    misread -- six launches got past a `pgrep` guard on 2026-08-10 because each previous child had
    already died, and the guard could only see the live ones.
    """
    slug = re.sub(r"[^a-z0-9]+", "-", job.strip().lower()).strip("-")
    if not slug:
        raise LaunchRefused(
            f"job name {job!r} slugs to nothing, so its unit could not be named -- and a unit "
            "nobody can name is a job nobody can ask systemd about")
    return f"{UNIT_PREFIX}{slug}"


def systemd_run_argv(unit: str, command: list, *, workdir: str, log: str,
                     description: str, env: dict | None = None) -> list:
    """The launch argv. Built here so a test can assert its shape without running anything.

    Every property on it is a death this project already paid for; the docstring at the top of this
    module says which. `--collect` is absent by construction and must stay absent.
    """
    argv = [
        "systemd-run", "--user", f"--unit={unit}",
        f"--description={description}",
        f"--property=WorkingDirectory={workdir}",
        "--property=Type=simple",
        f"--property=StandardOutput=append:{log}",
        f"--property=StandardError=append:{log}",
        "--setenv=PYTHONUNBUFFERED=1",
    ]
    for key, value in (env or {}).items():
        argv.append(f"--setenv={key}={value}")
    return argv + list(command)


def _show(unit: str, *properties: str, runner=subprocess.run) -> dict | None:
    """What the user manager holds about `unit`, or None if the probe could not be RUN.

    None is "we could not look" and is NOT an empty answer. Conflating them is how a control
    reports a state it never observed -- the same distinction `launch_liveness.systemd_probe`
    keeps, for the same reason.

    THE FLAG FORM IS LOAD-BEARING AND THE FIRST DRAFT HAD IT WRONG. `-p=ActiveState` is not a
    parse error: `systemctl show` accepts it, prints NOTHING, and exits 0. So every property read
    came back empty with a healthy rc, `name_is_held` read the empty answer as "the name is free",
    and the launcher would have started a second copy of a job beside a live one -- the exact
    fail-open the fixed unit name exists to make impossible. Nine tests against a fake runner
    were green; the real-launch door test at the bottom of the suite caught it on its first run.
    """
    try:
        res = runner(["systemctl", "--user", "show", unit,
                      *[arg for p in properties for arg in ("-p", p)]],
                     capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    fields = {}
    for line in (res.stdout or "").splitlines():
        if "=" in line:
            key, _, value = line.partition("=")
            fields[key.strip()] = value.strip()
    return fields


def name_is_held(unit: str, *, runner=subprocess.run) -> bool:
    """True if something alive holds this name. UNKNOWN READS AS HELD.

    The safe direction is the refusing one: a systemctl we cannot interrogate must not be taken as
    permission to start a second copy of a job beside a live one. That is the opposite of
    `verify_detached`'s direction below, and the difference is which way the mistake hurts --
    here a wrong "free" starts a duplicate long run, there a wrong "not detached" kills a good one.
    """
    fields = _show(unit, "ActiveState", runner=runner)
    if fields is None:
        return True
    return (fields.get("ActiveState") or "") in _HOLDING


def clear_a_corpse(unit: str, *, runner=subprocess.run) -> bool:
    """Reset the unit ONLY if nothing alive holds the name. Never raises: a convenience, not a
    control.

    A FAILED unit stays loaded, and the refusal it produces is word-for-word the one a LIVE unit
    produces (`Unit ... was already loaded or has a fragment file`). Without this, one dead run
    blocks every future launch of that job forever. Never a blanket reset: that would delete a
    RUNNING measurement's own registration and hand a second one the name.
    """
    if name_is_held(unit, runner=runner):
        return False
    try:
        res = runner(["systemctl", "--user", "reset-failed", unit],
                     capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return False
    return res.returncode == 0


def own_cgroup(path: Path | None = None) -> str:
    """This process's cgroup path, or "" if it could not be read."""
    try:
        text = (path or Path("/proc/self/cgroup")).read_text(encoding="utf-8")
    except OSError:
        return ""
    for line in text.splitlines():
        # cgroup v2 lines are `0::/user.slice/.../app.slice/seat-executor.service`.
        parts = line.split(":", 2)
        if len(parts) == 3 and parts[0] == "0":
            return parts[2].strip()
    return ""


def verify_detached(unit: str, *, runner=subprocess.run, launcher_cgroup: str | None = None
                    ) -> tuple[bool | None, str]:
    """Did the job land in a cgroup the launcher's teardown cannot reach?

    KEYED TO THE PROPERTY, NEVER TO A PID BEING BRIEFLY ALIVE. The 09-07 launch was verified live
    at five minutes by a waiter and was dead by the next tick; "the pid exists" is true of every
    job that is about to be killed, so it cannot be the check. What matters is whose cgroup owns
    it, and that answer does not change between now and the teardown.

    Returns `(True|False|None, why)`. **None is UNREADABLE and is not a failure**: `systemd-run`
    returning 0 IS the reparenting, so a probe we could not run is missing corroboration, not
    evidence of a bad launch. Stopping a healthy long run because we could not look would make
    this worse than the hand-rolled launches it replaces.
    """
    mine = own_cgroup() if launcher_cgroup is None else launcher_cgroup
    fields = _show(unit, "ControlGroup", runner=runner)
    if fields is None:
        return None, (f"`systemctl --user show {unit} -p ControlGroup` could not be run, so the "
                      "detach is UNVERIFIED. That is not the same as unsafe: systemd-run returning "
                      "0 is itself the reparenting.")
    theirs = (fields.get("ControlGroup") or "").strip()
    if not theirs:
        return None, (f"the user manager reports no ControlGroup for {unit}, so the detach is "
                      "UNVERIFIED -- most likely the unit has already exited and been collected.")
    if not mine:
        return None, (f"{unit} is in `{theirs}`, but this process could not read its own cgroup, "
                      "so there is nothing to compare it against.")
    if theirs == mine or theirs.startswith(mine.rstrip("/") + "/"):
        return False, (f"{unit} landed in `{theirs}`, which IS the launcher's own cgroup "
                       f"(`{mine}`). A KillMode=control-group teardown of the launcher takes it "
                       "too -- this is the exact death that killed three launches of one job.")
    return True, (f"{unit} is in `{theirs}`, a cgroup of its own; the launcher lives in `{mine}` "
                  "and its teardown cannot reach it.")


def stop(unit: str, *, runner=subprocess.run) -> None:
    """Best-effort teardown of a unit we have decided must not be left running."""
    try:
        runner(["systemctl", "--user", "stop", unit], capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        pass


def launch(job: str, command: list, *, artefact: str, workdir: str | None = None,
           log: str | None = None, description: str | None = None,
           asserted_live_by=(), env: dict | None = None,
           records_path: Path | None = None, runner=subprocess.run,
           launched_at: str | None = None, out=None) -> dict:
    """Start `command` in a transient user unit AND write its liveness record. One call, both.

    THE ORDER IS THE ARGUMENT, and it is the opposite of the obvious one. The record is written
    AFTER the launch, because a record written first for a launch that is then refused is a `live`
    claim for a job that never existed -- and `launch_liveness.check()` settles that to UNKNOWN,
    which by design does not clear the claim. A false "in flight" that nothing can ever settle is
    strictly worse than the silence this module replaces.

    AND A JOB WHOSE RECORD COULD NOT BE WRITTEN IS STOPPED. That is a deliberate, costly choice:
    it can kill a long run that had started fine, over a failed JSON write. It is still right.
    The state this module exists to abolish is "running and unrecorded" -- invisible to the
    deadman, to `--check`, and to every document that says it is in flight -- and it is the state
    that let the floor leg run unrecorded for 35 minutes. A relaunch is one command; an
    unattributable death costs a day.

    Returns the launch record, with `unit`, `detached` and `detach_why` added.
    """
    def say(line: str) -> None:
        print(line, file=out or sys.stdout)

    if not command:
        raise LaunchRefused("no command to launch")
    if shutil.which("systemd-run") is None:
        raise LaunchRefused(
            "`systemd-run` is not on PATH, so there is no way to launch this job into a cgroup of "
            "its own. Refusing rather than falling back to setsid: a setsid launch looks "
            "identical to a good one and dies at the next teardown, which is precisely how this "
            "job has been lost three times.")

    unit = unit_name(job)
    workdir = str(Path(workdir).resolve()) if workdir else str(_REPO)
    log = str(Path(log).resolve()) if log else f"/var/tmp/{unit}.log"
    Path(log).parent.mkdir(parents=True, exist_ok=True)
    Path(artefact).parent.mkdir(parents=True, exist_ok=True)

    if name_is_held(unit, runner=runner):
        raise LaunchRefused(
            f"a live unit already holds `{unit}` -- this job is ALREADY RUNNING, and starting a "
            "second copy is how one measurement became six on 2026-08-10. Ask it: "
            f"`systemctl --user show {unit} -p ActiveState`, or "
            "`python3 -m background.launch_liveness --check`.")
    if clear_a_corpse(unit, runner=runner):
        say(f"  . cleared the corpse of a previous `{unit}` -- it was not active, so its name was "
            "blocking every future launch of this job rather than protecting a live one")

    argv = systemd_run_argv(
        unit, command, workdir=workdir, log=log,
        description=description or f"long job {job} (launched by background.launch_long_job)",
        env=env)
    try:
        res = runner(argv, capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.SubprocessError) as exc:
        raise LaunchRefused(f"`systemd-run` could not be run: {exc}") from exc
    if res.returncode != 0:
        raise LaunchRefused(
            f"`systemd-run` refused with rc={res.returncode}: "
            f"{(res.stderr or res.stdout or '').strip()[:500]}")

    detached, why = verify_detached(unit, runner=runner)
    if detached is False:
        stop(unit, runner=runner)
        raise LaunchRefused(
            f"the launch was STOPPED because the detach did not hold: {why}")

    try:
        entry = launch_liveness.record(
            job, unit, artefact, log=log, asserted_live_by=list(asserted_live_by),
            launched_at=launched_at, path=records_path)
    except Exception as exc:  # noqa: BLE001 -- see the docstring: unrecorded must not stay running
        stop(unit, runner=runner)
        raise LaunchRefused(
            f"the job started and its liveness record could NOT be written ({exc}), so the unit "
            "was stopped. A running job nothing has recorded is invisible to the deadman and to "
            "every reader of a document claiming it is in flight, and that invisibility is what "
            "this launcher exists to abolish. Fix the record path and relaunch.") from exc

    entry = dict(entry, unit=unit, detached=detached, detach_why=why)
    say(f"launched {job} -> unit {unit}")
    say(f"  cgroup:   {'VERIFIED' if detached else 'UNVERIFIED'} -- {why}")
    say(f"  log:      {log}")
    say(f"  artefact: {artefact}")
    say(f"  recorded: claim={entry['claim']} at {entry['launched_at']}; re-ask it with "
        "`python3 -m background.launch_liveness --check`")
    return entry


def main(argv: list | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Launch a long job into a transient user unit and record its liveness.",
        epilog="Everything after `--` is the command to run.")
    parser.add_argument("--job", required=True,
                        help="the job's name; its unit is longjob-<slug> and its record is keyed "
                             "on this")
    parser.add_argument("--artefact", required=True,
                        help="the path the job writes on success -- a record without one cannot "
                             "be re-asked")
    parser.add_argument("--workdir", help="working directory for the unit (default: this repo)")
    parser.add_argument("--log", help="one file for BOTH streams (default: /var/tmp/<unit>.log)")
    parser.add_argument("--description")
    parser.add_argument("--setenv", action="append", default=[], metavar="K=V")
    parser.add_argument("--asserted-live-by", action="append", default=[], metavar="DOC",
                        help="a document that will state this run is in flight (repeatable); it "
                             "is what turns a stale claim into an address")
    parser.add_argument("--dry-run", action="store_true",
                        help="print the launch argv and exit, launching and recording nothing")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)

    command = [a for a in args.command if a != "--"] if args.command[:1] == ["--"] \
        else list(args.command)
    if not command:
        print("nothing to launch: put the command after `--`")
        return 2
    env = dict(kv.split("=", 1) for kv in args.setenv if "=" in kv)

    if args.dry_run:
        unit = unit_name(args.job)
        print(" ".join(systemd_run_argv(
            unit, command, workdir=args.workdir or str(_REPO),
            log=args.log or f"/var/tmp/{unit}.log",
            description=args.description or f"long job {args.job}", env=env)))
        return 0

    try:
        launch(args.job, command, artefact=args.artefact, workdir=args.workdir, log=args.log,
               description=args.description, asserted_live_by=args.asserted_live_by, env=env)
    except LaunchRefused as exc:
        print(f"REFUSED: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
