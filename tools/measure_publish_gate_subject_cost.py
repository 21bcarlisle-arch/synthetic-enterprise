#!/usr/bin/env python3
"""Measure what the publish gate's SUBJECT costs: in-tree vs a reused HEAD checkout.

OPS2_publish_gate_head_worktree exit criterion 1 says the clean-subject gate must run within
1.3x the in-tree baseline, "measured both sides, not asserted", and criterion 2 derives
GATE_SUITE_TIMEOUT_SECONDS from the NEW measured runtime. This is the harness that produces
those numbers, kept in the repo so the claim in
docs/design/OPS2_PUBLISH_GATE_HEAD_CHECKOUT.md can be re-run rather than believed.

Three phases, in this order so the cold run also does the work of warming the cache:

    COLD     -- reused checkout deleted first, so every module compiles from source
    WARM     -- the same directory refreshed in place; __pycache__ survives. THE steady state
    BASELINE -- the pre-ruling subject: the live working tree

`-x` is removed from the argv on ALL THREE sides. With it, a red suite stops at the first
failure, so "duration" would be time-to-first-failure and the sides would not be comparable.
The suite is expected to be red at HEAD for unrelated reasons; the runtime is the measurement,
the verdict is not.

The box is shared with the live publisher, whose own suite would both skew the wall-clock and
contend for a machine with ~5GB free. Each phase therefore TAKES the publisher's own run lock
(`process_run_complete.py::_run_lock`) for its duration and waits for memory headroom before
timing anything, and DEFERS -- banking what it has measured for the next launch to resume -- if
either wait times out. It never times a suite into a contended box: two full suites do not fit
in 15.9G (two runs were OOM-killed proving it), and the run that survives contention reports a
slow BASELINE, which is the ratio's denominator and so moves the exit criterion toward MEETS.

Holding the lock rather than waiting for a gap is what makes this converge: with a queue of
pending markers the publisher runs nearly back-to-back, so nine launches waiting for idleness
banked two phases and never once reached the baseline. A publisher that cannot take the lock
exits `EXIT_LOCK_SKIPPED` with its marker still pending -- an outcome the worker's sweep already
retries -- so the cost is one deferred publish cycle per phase. See `_publisher_exclusion`.

Usage:  python3 -m tools.measure_publish_gate_subject_cost --systemd  [THE committed launch]
        python3 -m tools.measure_publish_gate_subject_cost --detach   [session-detach only]
        python3 -m tools.measure_publish_gate_subject_cost [--out PATH]   [inline, blocks ~50min]
"""
from __future__ import annotations

import argparse
import fcntl
import json
import os
import shutil
import subprocess
import sys
import time
from contextlib import contextmanager
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from background import process_run_complete as prc  # noqa: E402

# A phase must not start while the real publisher is mid-suite. Bounded -- but the timeout
# DEFERS rather than measuring anyway (see `_Deferred`): two suites do not fit in this box's
# memory, and the contended run biases the exit-criterion ratio toward MEETS.
#
# ── AND WAITING FOR A GAP IS NOT THE SAME AS TAKING ONE (2026-08-10, ninth launch) ───────────
#
# OBSERVED. Nine launches, `deferral_count` rising, `in_tree_baseline` never once timed. The
# 19:55Z launch resumed both banked phases correctly, entered the baseline's quiet-wait, and
# deferred at 20:40:05Z -- *"publisher still live after 2700s"*. It was not unlucky. There are
# **112 `run_complete_*.md` markers pending** in `docs/staging/`, `background_worker.py::
# process_leftover_run_markers` re-globs them every cycle, and one publish cycle is now up to
# `GATE_SUITE_TIMEOUT_SECONDS` (2600s) of gate plus the publish path after it. The publisher is
# therefore running very nearly back-to-back, and a guard that WAITS FOR A GAP in a queue that
# refills faster than it drains does not converge -- it starves, quietly, one deferral at a
# time, with every banked phase looking healthy in the record.
#
# The primitive was already here and this harness was not using it. `process_run_complete.py::
# _run_lock` is a non-blocking `flock` on `.process_run_complete.lock` wrapping the WHOLE cycle
# (`_process`), and a publisher that cannot take it exits `EXIT_LOCK_SKIPPED` (75) leaving its
# marker pending -- a path `background_worker.py` already handles as "still pending, will retry
# next cycle", not as a failure. So the measurement HOLDS that lock for the duration of a phase
# instead of polling for its absence:
#
#   * it converges -- the acquire waits out at most ONE live publisher, then no further one can
#     start, where the poll had to win a race against a queue that never empties;
#   * `box_was_quiet` becomes true BY CONSTRUCTION rather than by luck. The invariant the
#     seventh launch's fix asserts (`test_a_banked_phase_was_always_admitted_quiet`) previously
#     rested on nothing having started in the gap between the last poll and the first test;
#   * it costs the publisher one deferred cycle per phase, on an already-deferred queue, and
#     costs the marker nothing.
#
# The deadline is DERIVED from the longest a publisher may legitimately hold that lock rather
# than restated as a round number -- the same defect this atom's criterion 2 closed one layer
# down, where a 900s caller cap sat under a 2600s gate and decided its verdict by stopwatch. A
# wait shorter than the work it waits on does not bound the wait; it just guarantees a deferral.
QUIET_WAIT_SECONDS = prc.PUBLISH_PATH_TIMEOUT_SECONDS + 5 * 60
QUIET_POLL_SECONDS = 30

# ── THE LAUNCH IS PART OF THE HARNESS (2026-08-10, WORKER_FINDING_THE_DETACH_THAT_FIXED_
# THE_DEATH_IS_NOT_IN_THE_REPO) ──────────────────────────────────────────────────────────────
#
# OBSERVED TWICE. This job takes ~50 minutes and has twice been started from a BOUNDED worker
# tick as an ad-hoc background job; both times it died inside `_wait_for_quiet`, ~12 minutes in,
# before its first phase, because the invocation that started it ended and took its process
# group with it. `3cc60f133` said the second fix was "launched under setsid" -- and `setsid`
# appeared nowhere in the repository. The body was committed; the launch was typed. A harness
# whose launch lives outside the repo cannot be reconstructed from the repo, which is the IaC
# constraint OPS1/OPERATIONAL_LAYER_DESIGN names as the core one.
#
# So `--detach` is the launch, and it is code. The parent re-execs this module through
# `start_new_session=True` (setsid: the child becomes a session AND process-group leader, so a
# group-directed kill aimed at the tick cannot reach it), then returns immediately.
#
# The record does not TAKE THE CALLER'S WORD for any of this. `main` stamps
# `is_session_leader`, computed from the running process's own `os.getsid`, so the next reader
# can tell from the repo artefact alone whether the run that produced it was really detached --
# which is exactly what could not be checked about the 08:35Z run.
DETACHED_LOG_FILE = prc.PROJECT_DIR / "docs" / "observability" / "publish-gate-subject-cost-log.md"


def _ancestor_pids() -> set:
    """This process and every parent of it, as strings.

    The whole ancestor chain, not just the pid: a launch typed at a shell arrives with the
    module name in the command line of the shell, of its `bash -c` wrapper, and of whatever
    spawned that. Excluding only `getpid()` would make the harness see its own launch as a
    competing run and refuse every time -- a guard that can only say no."""
    pids, pid = set(), os.getpid()
    while pid and pid != 1 and str(pid) not in pids:
        pids.add(str(pid))
        try:
            stat = Path("/proc/{}/stat".format(pid)).read_text()
            pid = int(stat.rsplit(")", 1)[1].split()[1])
        except (OSError, IndexError, ValueError):
            break
    return pids


def _measurement_is_running() -> bool:
    """True if another instance of this harness is already live (this process excepted).

    A second concurrent run would delete the reused checkout under the first one's suite and
    both would report a wrong number, so a launch must refuse rather than race."""
    try:
        out = subprocess.run(["pgrep", "-af", "measure_publish_gate_subject_cost"],
                             capture_output=True, text=True, timeout=30).stdout
    except (OSError, subprocess.SubprocessError):
        # An unavailable liveness check is a FAILED check (R15): refuse the launch rather than
        # assume the box is free. A missed launch costs one tick; a double run costs 50 minutes
        # AND produces a number that is wrong without saying so.
        return True
    ours = _ancestor_pids()
    for line in out.splitlines():
        pid, _, cmd = line.partition(" ")
        # Only a real invocation of the module counts -- a `grep`, an editor, or this finding's
        # own text on someone's command line is not a running measurement.
        if pid in ours or "pgrep" in cmd or "pytest" in cmd:
            continue
        if "-m tools.measure_publish_gate_subject_cost" in cmd or \
                "measure_publish_gate_subject_cost.py" in cmd:
            return True
    return False


def _detached_popen(argv: list, stdout_handle) -> subprocess.Popen:
    """Start `argv` in a NEW SESSION, so it outlives this process and its process group.

    This one line is the whole fix, which is why it is a named function with its own control
    (`test_a_detached_child_survives_the_death_of_its_launchers_process_group`) rather than a
    keyword buried in a call the tests never reach."""
    return subprocess.Popen(argv, cwd=str(prc.PROJECT_DIR), stdin=subprocess.DEVNULL,
                            stdout=stdout_handle, stderr=subprocess.STDOUT,
                            start_new_session=True)


def _spawn_detached(out: str, log) -> int:
    """Re-exec this harness in its own session and return, leaving it running.

    Returns the child's pid. The child's argv deliberately does NOT carry `--detach`: it is the
    measurement, not another launcher."""
    DETACHED_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    handle = open(str(DETACHED_LOG_FILE), "a")
    handle.write("\n## detached launch {}\n".format(
        time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())))
    handle.flush()
    child = _detached_popen(
        [sys.executable, "-m", "tools.measure_publish_gate_subject_cost", "--out", out], handle)
    handle.close()
    log("detached: pid {} in its own session, logging to {}".format(
        child.pid, DETACHED_LOG_FILE))
    log("it writes {} -- read `complete`, not the file's existence".format(out))
    return child.pid


# ── SESSION DETACHMENT WAS NOT ENOUGH: THE FOURTH DEATH (2026-08-10) ─────────────────────────
#
# OBSERVED. The 10:42:36Z run was launched through `--detach` above and its own record says
# `is_session_leader: true` -- computed by the running process, so the detach demonstrably HELD.
# It died anyway, 3.5 minutes in, still inside `_wait_for_quiet` (`last_heartbeat` 10:46:06Z,
# then nothing). No kernel OOM in that window (`dmesg` stops at 08:28), and this repository
# contains no reaper: `worker_seat.py` states the reaping path is DELETED, and `pkill`/`killpg`
# appear nowhere outside comments.
#
# INFERRED (R9, and labelled as inference because the killer was not caught in the act): what
# survives a process-GROUP kill does not survive a killer that enumerates a launcher's
# DESCENDANTS. `start_new_session` changes the session and group; it does not change the child's
# `ppid`, so a walk of /proc from the bounded tick still finds it. That is the difference the
# `--detach` control never tested for, and it is exactly the shape of a harness cleaning up
# after a turn.
#
# So the escalation this file's own design doc pre-committed to -- "a systemd unit beside
# reconcile-watch.timer, not a fourth identical launch" -- is what `--systemd` does. A TRANSIENT
# unit, not a manifest entry: `background/process_manifest.yaml` declares the steady-state
# process set, and a one-shot ~50-minute job that is *supposed* to end would read as MISSING to
# `process_reconciler.py` the moment it finished. The launch is still fully in the repo, which
# is what the IaC constraint asks for -- it is the ARGV that is committed, not a hand-typed
# incantation.
#
# The reparenting is the point: `systemd-run` hands the job to the user manager, so the child's
# parent is init and no descendant-walk from any tick can reach it.
MEASUREMENT_UNIT_NAME = "publish-gate-subject-cost"


def _systemd_run_argv(out: str) -> list:
    """The transient-unit launch. Built here so a test can assert its shape without running it.

    The FIXED unit name is load-bearing, not cosmetic: systemd itself refuses to start a second
    unit under a name already active, so double-launch refusal becomes a fact asserted by init
    rather than a command line this harness parses and could misread (six launches got past the
    `pgrep` guard on 2026-08-10 because each previous child had already died)."""
    return ["systemd-run", "--user", "--unit={}".format(MEASUREMENT_UNIT_NAME),
            "--description=OPS2 publish-gate subject-cost measurement (one-shot, ~50 min)",
            "--property=WorkingDirectory={}".format(prc.PROJECT_DIR),
            "--property=Type=simple",
            sys.executable, "-m", "tools.measure_publish_gate_subject_cost", "--out", out]


# ── A CORPSE HOLDS THE NAME JUST AS FIRMLY AS A LIVE RUN ─────────────────────────────────────
#
# OBSERVED, on the very next launch after the OOM. The fixed unit name is load-bearing and stays
# -- but systemd keeps a FAILED unit loaded, so the refusal it produces is identical to the one a
# live measurement produces:
#
#   Failed to start transient service unit: Unit publish-gate-subject-cost.service was already
#   loaded or has a fragment file
#
# and this harness printed "a live unit of this name IS the refusal", which was simply untrue:
# `systemctl --user is-active` said `failed`. A guard whose message is right in one of the two
# states it fires in is a guard that misdirects the next reader half the time -- and here it
# would have blocked every future launch forever, because nothing ever clears the corpse.
#
# So a FAILED unit is reset and the launch proceeds; an ACTIVE one still refuses, which is the
# protection that was actually wanted. Never a blanket reset: that would delete the running
# measurement's own registration and hand a second one the name.
def _unit_is_active() -> bool:
    """True if the measurement unit is running or starting. Unknown reads as ACTIVE.

    The safe direction is the refusing one: a systemctl we cannot interrogate must not be taken
    as permission to start a second suite next to a live one."""
    try:
        res = subprocess.run(["systemctl", "--user", "is-active", MEASUREMENT_UNIT_NAME],
                             capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return True
    return res.stdout.strip() in ("active", "activating", "reloading")


def _clear_a_failed_unit(log) -> None:
    """Reset the unit ONLY if it is dead. Never raises: this is a convenience, not a control."""
    if _unit_is_active():
        return
    try:
        res = subprocess.run(["systemctl", "--user", "reset-failed", MEASUREMENT_UNIT_NAME],
                             capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return
    if res.returncode == 0:
        log("  . cleared the corpse of a previous unit -- it was not active, so its name was "
            "blocking every future launch rather than protecting a live one")


def _launch_under_systemd(out: str, log) -> int:
    """Hand the measurement to the init system. Returns a process exit code, not a pid.

    Fails CLOSED on every unhappy path -- no systemd-run, a name held by a LIVE unit, a non-zero
    rc -- because a launch that silently did nothing is precisely the failure mode of the last
    four attempts, and the next reader must be able to tell 'refused' from 'running'."""
    if shutil.which("systemd-run") is None:
        log("! systemd-run unavailable -- use --detach, and expect it to die if this tick's "
            "harness reaps its descendants (see the note above)")
        return 1
    _clear_a_failed_unit(log)
    try:
        res = subprocess.run(_systemd_run_argv(out), capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.SubprocessError) as exc:
        log("! could not launch the transient unit: {}".format(exc))
        return 1
    if res.returncode != 0:
        log("! systemd-run refused (rc={}): {}".format(
            res.returncode, (res.stderr or "").strip()[-400:]))
        log("  a LIVE unit of this name IS the refusal (a dead one is cleared above) -- check: "
            "systemctl --user status {}".format(MEASUREMENT_UNIT_NAME))
        return res.returncode
    _record_launch_header("systemd-run --user --unit={}".format(MEASUREMENT_UNIT_NAME))
    log("launched as transient unit {}.service -- owned by the user manager, so no "
        "descendant-walk from this tick can reach it".format(MEASUREMENT_UNIT_NAME))
    log("it writes {} -- read `complete`, not the file's existence".format(out))
    log("follow with: journalctl --user -u {} -f".format(MEASUREMENT_UNIT_NAME))
    return 0


def _record_launch_header(how: str) -> None:
    """Append a launch line to the repo-readable trail. Never raises."""
    try:
        DETACHED_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(str(DETACHED_LOG_FILE), "a") as fh:
            fh.write("\n## launch {} via {}\n".format(
                time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), how))
    except OSError:
        pass


def _launched_by() -> str:
    """How THIS process was started, asked of the kernel/environment rather than claimed.

    `INVOCATION_ID` is set by systemd for a process it started, and by nothing else here. Same
    discipline as `is_session_leader`: a reader of the record must be able to tell how the run
    that produced it was launched WITHOUT trusting whoever wrote the launch line."""
    if os.environ.get("INVOCATION_ID"):
        return "systemd"
    try:
        return "session-detach" if os.getpid() == os.getsid(0) else "inline"
    except OSError:
        return "unknown"


def _publisher_is_running() -> bool:
    """True if a real process_run_complete cycle is live (this process excepted)."""
    try:
        out = subprocess.run(["pgrep", "-af", "process_run_complete.py"],
                             capture_output=True, text=True, timeout=30).stdout
    except (OSError, subprocess.SubprocessError):
        return False
    mine = str(os.getpid())
    for line in out.splitlines():
        pid = line.split(" ", 1)[0]
        if pid != mine and "measure_publish_gate_subject_cost" not in line:
            return True
    return False


# ── "MEASURE ANYWAY" WAS BIASED TOWARD PASS, NOT MERELY NOISY (2026-08-10, seventh launch) ───
#
# Both admission guards below were bounded and both fell through to "measure anyway, flagged
# contended", justified as "a harness that can wait forever is worse than a number labelled
# noisy". OBSERVED: that trade was wrong twice, and in two different ways.
#
#   * IT DOES NOT PRODUCE A NOISY NUMBER, IT PRODUCES NO NUMBER. The seventh launch entered the
#     BASELINE phase's quiet-wait at 18:25:58Z, timed out at ~19:11, started its suite into a
#     live publisher, and was OOM-killed at 19:25:11Z -- 11.1G peak, `Result: oom-kill`, unit
#     `publish-gate-subject-cost.service`. Two full suites do not fit in 15.9G. The sixth launch
#     died the same way at 13:55:30Z (6.5G peak). Cost: two ~1h36m launches, no baseline.
#
#   * WHEN IT DOES NOT KILL THE RUN, IT BIASES THE EXIT CRITERION TOWARD PASS. The criterion is
#     warm / in-tree <= 1.3, and the phase that keeps losing the race is IN_TREE -- the
#     DENOMINATOR. A baseline timed against a live publisher runs slow, which makes the ratio
#     SMALLER, which makes the criterion likelier to read MEETS. A guard whose degraded mode
#     moves the measured verdict in the passing direction is fail-open (R15), and it would have
#     done so silently: `box_was_quiet: false` sits inside the phase record, while
#     `meets_exit_criterion` is what anyone reads.
#
# SO: the timeout DEFERS instead. The phases are already resumable -- banked phases are kept and
# only what is owed is re-run -- so exiting cleanly costs exactly what dying costs, minus the OOM
# and minus the false number, and the next launch picks up where this one stopped. That makes
# `box_was_quiet`/`had_memory_headroom` INVARIANTLY true on any banked phase, which is the point:
# they stop being a caveat attached to a number that is used anyway, and become a property the
# record can be checked against (`test_a_banked_phase_was_always_admitted_quiet`).
#
# The convergence risk this takes on is real and is made VISIBLE rather than argued away: a box
# that is never quiet for long enough now shows up as a rising `deferral_count` in the record,
# not as a measurement that quietly never lands.
class _Deferred(Exception):
    """Admission was refused. Bank what is measured and let the next launch resume."""

    def __init__(self, reason):
        super().__init__(reason)
        self.reason = reason


def _wait_for_quiet(log, heartbeat=None) -> bool:
    """Wait for the publisher to finish. Returns True if the box went quiet.

    Raises `_Deferred` rather than returning if the wait times out -- see the block above: a
    phase timed alongside the live publisher is killed by the OOM killer, and on the survivable
    path it moves the exit-criterion ratio in the PASSING direction.

    `heartbeat`, when given, is called on every poll. Both deaths so far happened INSIDE this
    wait, so a record that stops advancing here is the difference between "it is still waiting"
    and "it was killed waiting" -- and the latter would mean the detach did not hold and the
    next escalation is a systemd unit, not a third identical launch."""
    deadline = time.time() + QUIET_WAIT_SECONDS
    waited = False
    while _publisher_is_running():
        if time.time() > deadline:
            log("  ! publisher still live after {}s -- DEFERRING; banked phases are kept and "
                "the next launch resumes".format(QUIET_WAIT_SECONDS))
            raise _Deferred("publisher still live after {}s".format(QUIET_WAIT_SECONDS))
        if not waited:
            log("  . waiting for the live publisher to finish before timing")
            waited = True
        if heartbeat is not None:
            heartbeat()
        time.sleep(QUIET_POLL_SECONDS)
    return True


# Held across a phase so no NEW publisher can start inside it. RE-ENTRANT because the cold phase
# needs the exclusion wider than one suite -- it deletes the reused checkout, rebuilds it and
# then times it, and a publisher slipping in between those steps would be running its own gate
# inside the directory this harness just deleted. A second `flock` on a second fd of the same
# file blocks even within one process, so re-entry is counted here rather than attempted.
_EXCLUSION = {"fh": None, "depth": 0}


@contextmanager
def _publisher_exclusion(log, heartbeat=None):
    """Hold the publisher's own run lock for the duration of the block.

    Raises `_Deferred` rather than proceeding if the lock cannot be taken inside
    `QUIET_WAIT_SECONDS` -- for the same reason the waits below defer: a phase timed beside a
    live publisher is OOM-killed, and on the surviving path it moves the exit-criterion ratio
    in the PASSING direction. Never "measure anyway".

    Polls `LOCK_EX | LOCK_NB` rather than blocking on `LOCK_EX` so the heartbeat keeps advancing:
    a record that stops updating is how the next tick tells "still waiting" from "was killed
    waiting", and a blocking flock would freeze that signal for the whole wait."""
    if _EXCLUSION["depth"] > 0:
        _EXCLUSION["depth"] += 1
        try:
            yield True
        finally:
            _EXCLUSION["depth"] -= 1
        return

    prc.RUN_LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
    fh = open(str(prc.RUN_LOCK_FILE), "w")
    deadline = time.time() + QUIET_WAIT_SECONDS
    waited = False
    while True:
        try:
            fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
            break
        except BlockingIOError:
            if time.time() > deadline:
                fh.close()
                log("  ! the publisher's run lock was held for {}s -- DEFERRING; banked phases "
                    "are kept and the next launch resumes".format(QUIET_WAIT_SECONDS))
                raise _Deferred(
                    "publisher held the run lock for {}s".format(QUIET_WAIT_SECONDS))
            if not waited:
                log("  . waiting to TAKE the publisher's run lock (not merely for a gap) -- a "
                    "publisher is mid-cycle; once held, no new one can start inside this phase")
                waited = True
            if heartbeat is not None:
                heartbeat()
            time.sleep(QUIET_POLL_SECONDS)

    _EXCLUSION["fh"] = fh
    _EXCLUSION["depth"] = 1
    try:
        yield True
    finally:
        # Released on EVERY exit, including a raising phase: a measurement that kept the lock
        # after failing would wedge publishing outright, which is a far worse outcome than an
        # unmeasured ratio. SIGKILL needs no handling here -- the kernel drops flocks with the fd.
        _EXCLUSION["depth"] = 0
        _EXCLUSION["fh"] = None
        try:
            fcntl.flock(fh, fcntl.LOCK_UN)
        finally:
            fh.close()


# ── /tmp IS RAM ON THIS BOX, AND EACH PHASE WAS LEAVING GIGABYTES OF IT BEHIND ───────────────
#
# OBSERVED. The fifth launch -- the first one init owned, so the detach finally held -- completed
# phase 1 (cold, 1291.9s) and was OOM-KILLED 6m20s into phase 2:
#
#   publish-gate-subject-cost.service: The kernel OOM killer killed some processes in this unit.
#   Active: failed (Result: oom-kill) ... Mem peak: 6.5G
#
# The box has **15G of RAM**, not 32 (WSL2 hands the VM half), 4G of swap with 3G already in use,
# and `/tmp` is a **7.8G tmpfs** -- which is RAM, not disk. A suite run leaves its pytest temp
# roots there: measured live, `/tmp/pytest-of-rich` held **2.0G** across roots of 775M, 676M and
# 570M, all from that day's runs.
#
# So a three-phase measurement was accumulating a phase's worth of RAM-resident temp per phase
# and then starting the next full suite on top of it. `_sweep_stale_pytest_temp_roots` cannot
# reclaim any of it: its bound is 3h old, keep-newest-3, and this debris is MINUTES old and only
# three roots deep. That sweep is scoped for the debris of killed runs across cycles; it was
# never a within-run reclaim, and the OOM is what within-run accumulation looks like.
#
# CLOSED BY GIVING THE MEASUREMENT ITS OWN BASETEMP, which pytest clears at the start of every
# run. Reclaim then happens by construction, before each phase rather than after -- at most one
# phase's temps exist at a time, and the three phases start from the same tmpfs state, which
# also makes them more comparable than they were.
#
# Two properties this basetemp has to keep:
#   * SAME FILESYSTEM as the real gate's default (both under `/tmp`, both tmpfs), because the
#     runtime is the measurement -- moving temps to spinning disk would change the number the
#     timeout is derived from.
#   * SWEEPABLE. It is named under `HEAD_CHECKOUT_PREFIX` so `_sweep_stale_head_checkouts`
#     already owns it, per the convention the fifteenth wedge established: anything this
#     machine leaves in /tmp carries a name the machine's own sweep can see. `finally:` does
#     not run under SIGKILL, and this harness has now been SIGKILLed twice.
MEASURE_BASETEMP_NAME = prc.HEAD_CHECKOUT_PREFIX + "measure-tmp"

# A phase must not start into a box that is already out of memory -- the fifth launch died
# exactly there. Bounded like the quiet wait: we say so and measure anyway rather than hang,
# because a harness that can wait forever is worse than a number labelled contended.
MIN_MEMORY_HEADROOM_MB = 4096
MEMORY_WAIT_SECONDS = 20 * 60


def _mem_available_mb():
    """MemAvailable in MB, or None if the kernel will not say (never raises)."""
    try:
        for line in Path("/proc/meminfo").read_text().splitlines():
            if line.startswith("MemAvailable:"):
                return int(line.split()[1]) // 1024
    except (OSError, ValueError, IndexError):
        return None
    return None


def _wait_for_memory_headroom(log, heartbeat=None) -> bool:
    """Wait until the box has room for a full suite. True if the headroom was there.

    Raises `_Deferred` rather than returning if the wait times out, for the same reason as the
    quiet wait above: starting a suite into a box that is already out of memory is what the OOM
    killer ends, and the survivable version of it biases the ratio toward MEETS.

    A kernel that will not report MemAvailable is treated as "go" rather than as a block: this
    is a measurement harness, and refusing to measure because /proc is unreadable would trade a
    known failure for a permanent one."""
    deadline = time.time() + MEMORY_WAIT_SECONDS
    waited = False
    while True:
        available = _mem_available_mb()
        if available is None or available >= MIN_MEMORY_HEADROOM_MB:
            return True
        if time.time() > deadline:
            log("  ! only {}MB available after {}s (want {}MB) -- DEFERRING; banked phases are "
                "kept and the next launch resumes"
                .format(available, MEMORY_WAIT_SECONDS, MIN_MEMORY_HEADROOM_MB))
            raise _Deferred("only {}MB available after {}s (want {}MB)".format(
                available, MEMORY_WAIT_SECONDS, MIN_MEMORY_HEADROOM_MB))
        if not waited:
            log("  . waiting for memory headroom: {}MB available, want {}MB"
                .format(available, MIN_MEMORY_HEADROOM_MB))
            waited = True
        if heartbeat is not None:
            heartbeat()
        time.sleep(QUIET_POLL_SECONDS)


def _argv_without_x() -> list:
    """The gate's own argv, minus -x, plus the measurement's own basetemp.

    See the module docstring for why -x goes, and the MEASURE_BASETEMP_NAME comment for why the
    basetemp arrives. Both apply identically to all three phases, so neither can move the ratio
    the exit criterion is read from."""
    argv = [a for a in prc.publish_gate_pytest_argv("tests/") if a != "-x"]
    return argv + ["--basetemp={}".format(prc.HEAD_CHECKOUT_ROOT / MEASURE_BASETEMP_NAME)]


def _time_suite(cwd: Path, log, heartbeat=None) -> dict:
    with _publisher_exclusion(log, heartbeat):
        return _time_suite_under_exclusion(cwd, log, heartbeat)


def _time_suite_under_exclusion(cwd: Path, log, heartbeat=None) -> dict:
    # The exclusion above stops a NEW publisher starting; this drains one that was already live
    # without the lock (an older build, a hand-run invocation). With the lock held it normally
    # returns immediately -- it is the belt to the exclusion's braces, not the mechanism.
    quiet = _wait_for_quiet(log, heartbeat)
    had_headroom = _wait_for_memory_headroom(log, heartbeat)
    env = dict(os.environ)
    env["SIM_FAST_MODE"] = "1"
    load_before = os.getloadavg()[0]
    mem_before = _mem_available_mb()
    started = time.monotonic()
    result = subprocess.run(_argv_without_x(), cwd=str(cwd), env=env,
                            capture_output=True, text=True, errors="replace")
    elapsed = time.monotonic() - started
    tail = [ln for ln in result.stdout.strip().splitlines() if ln.strip()][-1:]
    return {
        "cwd": str(cwd),
        # The SHA THIS phase actually ran against. Stamped per phase, not once at launch: HEAD
        # moves under a long measurement (ordinary commits land while it waits for the box), and
        # a single launch-time stamp would make a sound result look stale to whoever reads it.
        "head_sha_at_run": prc._head_sha(),
        "seconds": round(elapsed, 1),
        "returncode": result.returncode,
        "summary": tail[0][:300] if tail else "",
        "loadavg_before": round(load_before, 2),
        "loadavg_after": round(os.getloadavg()[0], 2),
        "box_was_quiet": quiet,
        # The conditions the OOM happened in, recorded so a short phase can be told from a
        # starved one without going back to the journal.
        "mem_available_before_mb": mem_before,
        "mem_available_after_mb": _mem_available_mb(),
        "had_memory_headroom": had_headroom,
    }


# ── A KILLED MEASUREMENT MUST STILL SAY WHAT IT DID (2026-08-10) ─────────────────────────────
#
# OBSERVED, not hypothetical: the 05:28 run of this harness was launched from a bounded worker
# tick, went into `_wait_for_quiet`, and died with the tick. It left NOTHING in the repo -- the
# only trace was a two-line file in /tmp -- so the next tick could not tell "died in the wait"
# from "never launched" from "ran and found nothing", and the design doc's instruction to READ
# the JSON had no JSON to read. Three phases at ~15 minutes each on a box where the OOM killer
# is a known visitor is exactly the shape that must not be all-or-nothing.
#
# So the record is written from BEFORE the first phase and re-written after each one, carrying
# `complete: false` until the derived figures exist. A reader must therefore check `complete`
# rather than the file's existence -- `_phases_missing` names what is still owed, so a partial
# record tells the next tick precisely which phases to resume rather than restart.
PHASE_ORDER = ("cold_checkout", "warm_checkout", "in_tree_baseline")


# ── AND THE RESUME HAS TO BE CODE, NOT A COMMENT ABOUT THE RECORD ────────────────────────────
#
# The paragraph above has said since it was written that "a partial record tells the next tick
# precisely which phases to resume rather than restart". It did not. `_run_measurement` opened
# with `"phases": {}` every time, so each launch re-ran all three from the top, and every launch
# so far has been killed before finishing three -- which is precisely the shape that never
# converges. The fifth launch banked a real 1291.9s cold phase and the sixth would have thrown
# it away and re-paid 21 minutes for it.
#
# A checkpoint nothing reads is a log line. This is the read side.
def _load_banked_phases(out_path: str) -> dict:
    """Phases an earlier launch already timed. Never raises: a bad record means start over.

    A phase counts as banked only if it carries a `seconds`, so a half-written checkpoint or a
    hand-edited record cannot retire a phase that was never timed."""
    try:
        prior = json.loads(Path(out_path).read_text())
    except (OSError, ValueError):
        return {}
    phases = prior.get("phases") if isinstance(prior, dict) else None
    if not isinstance(phases, dict):
        return {}
    return {name: rec for name, rec in phases.items()
            if name in PHASE_ORDER and isinstance(rec, dict) and rec.get("seconds") is not None}


# ── THE RATIO'S TWO SIDES MUST SHARE A COMMIT, AND THAT WAS A COMMENT TOO ────────────────────
#
# `_run_measurement` has said since the resume was built that "the exit-criterion ratio is
# warm/in-tree, and those two are re-run together whenever either is owed, so a stale COLD can
# move the timeout floor but never the ratio". Nothing did that. `_load_banked_phases` retires
# any phase carrying a `seconds`, whatever commit it was timed at, so the resume kept a warm
# phase from an earlier HEAD and would have divided it by a baseline timed at today's.
#
# OBSERVED in the live record before this fix: warm banked at 54141b5 summarising *"235 failed,
# 23069 passed, 14 errors"* against a cold phase at 3ee4541a summarising *"7 failed, 23249
# passed"*. Those are not the same suite. A ratio across them measures the diff between two
# commits and reports it as the cost of the checkout -- and `phases_from_an_earlier_head` would
# have named the problem in the artefact while the exit criterion was decided by it anyway.
#
# So the pair is dropped and re-timed together whenever either is owed. A banked phase with no
# `head_sha_at_run` at all cannot be SHOWN comparable, so it is dropped for the same reason:
# this is the criterion's own evidence, and unprovable is not a pass.
#
# COLD is deliberately exempt. It feeds `implied_timeout_floor_2x` -- a bound that must clear the
# worst legitimate runtime -- and an older, slower cold phase can only raise that bound. It never
# enters the ratio.
RATIO_PHASES = ("warm_checkout", "in_tree_baseline")


def _drop_incomparable_ratio_phases(phases: dict, head_sha: str, log) -> list:
    """Drop banked ratio phases not provably timed at `head_sha`. Returns the names dropped.

    Only when one of the pair is still OWED: once both are banked at the same earlier commit
    they are comparable to each other, and re-timing them would cost 40 minutes to learn the
    same number."""
    if all(name in phases for name in RATIO_PHASES):
        return []
    dropped = []
    for name in RATIO_PHASES:
        rec = phases.get(name)
        if rec is None:
            continue
        if rec.get("head_sha_at_run") != head_sha:
            phases.pop(name)
            dropped.append(name)
    if dropped:
        log("  . dropping banked {} -- timed at another commit than this launch's HEAD ({}), "
            "and the exit-criterion ratio may not span commits".format(
                ", ".join(sorted(dropped)), head_sha[:9]))
    return sorted(dropped)


def _checkpoint(results: dict, out: str, log) -> None:
    """Persist what is known so far. Never raises: a failed write must not lose a live run."""
    results["complete"] = all(p in results["phases"] for p in PHASE_ORDER)
    results["phases_missing"] = [p for p in PHASE_ORDER if p not in results["phases"]]
    try:
        Path(out).write_text(json.dumps(results, indent=2) + "\n")
    except OSError as exc:
        log("! could not checkpoint to {}: {}".format(out, exc))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(prc.PROJECT_DIR / "docs" / "observability"
                                         / "publish_gate_subject_cost.json"))
    ap.add_argument("--detach", action="store_true",
                    help="re-exec in a new session and return immediately; survives a kill of "
                         "the launcher's process GROUP but not of its descendant tree")
    ap.add_argument("--systemd", action="store_true",
                    help="hand the run to the user manager as a transient unit; THE committed "
                         "launch from a bounded tick, because init owns it and no walk of this "
                         "tick's descendants can reach it")
    args = ap.parse_args(argv)

    def log(msg):
        print("[measure] {}".format(msg), flush=True)

    if args.systemd:
        if _measurement_is_running():
            log("! a measurement is already live -- refusing to start a second one, which "
                "would delete the reused checkout under the first one's suite")
            return 1
        return _launch_under_systemd(args.out, log)
    if args.detach:
        if _measurement_is_running():
            log("! a measurement is already live -- refusing to start a second one, which "
                "would delete the reused checkout under the first one's suite")
            return 1
        _spawn_detached(args.out, log)
        return 0
    return _run_measurement(args.out, log)


def _prior_deferral_count(out_path: str) -> int:
    """How many launches have already deferred. Never raises: an unreadable record means zero.

    Carried across launches so that "the box is never quiet long enough to measure" -- the risk
    the deferral trade takes on -- surfaces as a rising number in the artefact rather than as a
    measurement that silently never lands."""
    try:
        prior = json.loads(Path(out_path).read_text())
    except (OSError, ValueError):
        return 0
    count = prior.get("deferral_count") if isinstance(prior, dict) else None
    return count if isinstance(count, int) and count >= 0 else 0


def _run_measurement(out_path: str, log) -> int:
    """The measurement itself, in THIS process. Blocks ~50 minutes.

    Returns 0 on a complete measurement AND on a deferral -- a deferral is a correct outcome,
    not a failure, and a non-zero exit would make the systemd unit report `failed` for a run
    that did exactly the right thing."""
    args = argparse.Namespace(out=out_path)

    head_sha = prc._head_sha()
    banked = _load_banked_phases(out_path)
    # BEFORE `resumed_phases` is taken, so the record names what this launch will actually
    # re-time rather than what the file happened to hold.
    dropped_for_comparability = _drop_incomparable_ratio_phases(banked, head_sha, log)
    results = {"head_sha_at_launch": head_sha, "pid": os.getpid(),
               # COMPUTED, never claimed. "Detached" means "session leader", and this is the
               # process asking the kernel about itself -- so a reader can tell from the repo
               # artefact alone whether the run that wrote it really was detached. The 08:35Z
               # run's detachment could only be re-typed, never checked; this one can.
               "is_session_leader": os.getpid() == os.getsid(0),
               # And WHICH detachment, because the fourth death proved the two are not the same
               # protection: session-detach survives a group kill, systemd survives a walk of
               # the launcher's descendants. A record that says only "detached" cannot tell the
               # next reader which of the two failed.
               "launched_by": _launched_by(),
               "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               # RESUMED, not restarted. Phases an earlier launch paid for are kept; only what
               # is still owed is re-run.
               "phases": banked,
               # Read HERE, beside the banked phases, and for the same reason: `_checkpoint`
               # rewrites the file from `results` before the first phase, so a count read at
               # deferral time would be reading a record this launch had already blanked --
               # and the tally would stick at 1 forever.
               "deferral_count": _prior_deferral_count(out_path)}
    results["resumed_phases"] = sorted(results["phases"])
    # What `_drop_incomparable_ratio_phases` refused to inherit, in the artefact: a reader who
    # sees the warm phase re-timed needs to know it was re-timed on purpose and why, and the
    # next tick needs to tell "this launch chose to pay for it again" from "the record was lost".
    results["dropped_for_comparability"] = dropped_for_comparability
    # Phases timed at a DIFFERENT commit than this launch's HEAD. Resuming across launches is
    # what makes the measurement converge on a box that keeps killing it, but it means the
    # record can span commits -- so it says so rather than letting a reader assume one SHA. Only
    # a stale COLD can survive that: it feeds the timeout floor, never the ratio, and the pair
    # that DOES feed the ratio is dropped and re-timed together above.
    results["phases_from_an_earlier_head"] = sorted(
        name for name, rec in results["phases"].items()
        if rec.get("head_sha_at_run") and rec["head_sha_at_run"] != head_sha)

    def heartbeat():
        results["last_heartbeat"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        _checkpoint(results, args.out, log)
    # Before the first wait, so that a run killed IN the wait is still distinguishable from a
    # run that was never launched at all -- which is the failure this harness just suffered.
    _checkpoint(results, args.out, log)

    try:
        log("HEAD={} -- three timed runs, expect ~45-60 min total".format(head_sha))

        # COLD: delete the reused checkout so nothing survives from an earlier cycle.
        #
        # WAIT FIRST, THEN DELETE. A live publisher may be running its suite inside that very
        # directory, and removing it mid-run would corrupt a real publish cycle to take a
        # measurement -- the harness must never be able to damage the thing it measures.
        if "cold_checkout" in results["phases"]:
            # Deleting the reused checkout is the COLD phase's setup, so it lives inside this
            # branch: a resume that still deleted it would throw away the warmth the next phase is
            # there to measure.
            log("phase 1/3 COLD -- banked by an earlier launch at {}s, not re-run".format(
                results["phases"]["cold_checkout"]["seconds"]))
        else:
            # ONE exclusion spanning delete -> rebuild -> time. Not three: between them a
            # publisher would be free to start a cycle in the directory just deleted from under
            # it, and to take the reuse lock this phase is about to need.
            with _publisher_exclusion(log, heartbeat):
                reused = prc.HEAD_CHECKOUT_ROOT / prc.REUSED_HEAD_CHECKOUT_NAME
                shutil.rmtree(reused, ignore_errors=True)
                log("phase 1/3 COLD -- reused checkout deleted, bytecode compiles from source")
                with prc._head_checkout() as path:
                    if path is None:
                        log("! checkout unavailable -- cannot measure the clean subject")
                        results["aborted"] = "checkout unavailable"
                        _checkpoint(results, args.out, log)
                        return 1
                    if path.name != prc.REUSED_HEAD_CHECKOUT_NAME:
                        log("! got a THROWAWAY checkout ({}) -- another publisher holds the reuse "
                            "lock, so the warm phase would not be warm. Aborting rather than "
                            "reporting a wrong ratio.".format(path.name))
                        results["aborted"] = "another publisher held the reuse lock"
                        _checkpoint(results, args.out, log)
                        return 1
                    results["phases"]["cold_checkout"] = _time_suite(path, log, heartbeat)
            log("   cold: {}s".format(results["phases"]["cold_checkout"]["seconds"]))
            _checkpoint(results, args.out, log)

        # WARM: same directory, refreshed in place. __pycache__ survives the refresh.
        if "warm_checkout" in results["phases"]:
            log("phase 2/3 WARM -- banked by an earlier launch at {}s, not re-run".format(
                results["phases"]["warm_checkout"]["seconds"]))
        else:
            # On a RESUME the warmth was established by whoever last ran in that directory -- this
            # run's own cold phase, an earlier launch's, or the live publisher's ordinary cycle.
            # All three are the same steady state the real gate pays, but the record says which,
            # because "warm" is a claim about the directory and not about this process.
            results["warm_cache_established_by"] = (
                "this run's cold phase" if "cold_checkout" not in results["resumed_phases"]
                else "an earlier launch or the live publisher")
            log("phase 2/3 WARM -- same directory refreshed in place, bytecode retained ({})".format(
                results["warm_cache_established_by"]))
            # Same reason as COLD: the reuse lock this phase depends on must not be winnable by
            # a publisher between the checkout and the timing.
            with _publisher_exclusion(log, heartbeat), prc._head_checkout() as path:
                if path is None or path.name != prc.REUSED_HEAD_CHECKOUT_NAME:
                    log("! lost the reused checkout between phases -- aborting")
                    results["aborted"] = "lost the reused checkout between phases"
                    _checkpoint(results, args.out, log)
                    return 1
                results["phases"]["warm_checkout"] = _time_suite(path, log, heartbeat)
            log("   warm: {}s".format(results["phases"]["warm_checkout"]["seconds"]))
            _checkpoint(results, args.out, log)

        # BASELINE: the pre-ruling subject, the live working tree.
        if "in_tree_baseline" in results["phases"]:
            log("phase 3/3 BASELINE -- banked by an earlier launch at {}s, not re-run".format(
                results["phases"]["in_tree_baseline"]["seconds"]))
        else:
            log("phase 3/3 BASELINE -- the live working tree, the pre-ruling subject")
            results["phases"]["in_tree_baseline"] = _time_suite(prc.PROJECT_DIR, log, heartbeat)
            log("   baseline: {}s".format(results["phases"]["in_tree_baseline"]["seconds"]))
            _checkpoint(results, args.out, log)

        warm = results["phases"]["warm_checkout"]["seconds"]
        base = results["phases"]["in_tree_baseline"]["seconds"]
        results["ratio_warm_over_in_tree"] = round(warm / base, 3) if base else None
        results["exit_criterion_ratio_max"] = 1.3
        results["meets_exit_criterion"] = bool(base and (warm / base) <= 1.3)
        # Criterion 2: the bound is derived from the runtime the gate ACTUALLY pays, which is the
        # warm steady state -- but a cold cycle is a real outcome (a fallback throwaway, a rebuilt
        # corrupt checkout), so the bound must clear the worst legitimate case, not the usual one.
        worst = max(warm, results["phases"]["cold_checkout"]["seconds"], base)
        results["worst_legitimate_seconds"] = worst
        results["implied_timeout_floor_2x"] = int(worst * 2)

        _checkpoint(results, args.out, log)
        log("ratio warm/in-tree = {} (criterion <= 1.3) -- {}".format(
            results["ratio_warm_over_in_tree"],
            "MEETS" if results["meets_exit_criterion"] else "MISSES"))
        log("worst legitimate run {}s -> timeout floor at 2x = {}s".format(
            worst, results["implied_timeout_floor_2x"]))
        log("written to {}".format(args.out))
        return 0
    except _Deferred as deferred:
        # A deferral is a CORRECT outcome, not a failure: the box was not fit to time a suite
        # in, the phases already banked are kept, and the next launch resumes from here. It is
        # recorded rather than merely logged because the journal of a killed unit is not
        # something the next tick reads -- the artefact is.
        results["deferred"] = {
            "reason": deferred.reason,
            "at_phase": results["phases_missing"][0] if results.get("phases_missing") else None,
            "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        results["deferral_count"] += 1
        _checkpoint(results, args.out, log)
        log("deferred ({}) -- {} still owed; re-launch with --systemd to resume. "
            "Deferrals so far: {}".format(
                deferred.reason, ", ".join(results["phases_missing"]) or "nothing",
                results["deferral_count"]))
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
