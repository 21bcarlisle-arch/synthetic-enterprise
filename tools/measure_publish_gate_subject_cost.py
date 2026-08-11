#!/usr/bin/env python3
"""Measure what the publish gate's SUBJECT costs: in-tree vs the throwaway HEAD checkout.

OPS2_publish_gate_head_worktree exit criterion 1 asked for a REUSED checkout within 1.3x the
in-tree baseline. Reuse was ELIMINATED under R3 on 2026-08-11 (444402ee0) after it reset a
shared directory under four live suites, so `prc.REUSE_HEAD_CHECKOUT` ships False and warm
bytecode is not available to this atom at any price. The criterion is therefore SUPERSEDED, and
its honest successor is THE RATIO IN THE OTHER DIRECTION: what the cold subject costs per cycle
-- the permanent tax the elimination made unavoidable. Criterion 2 (derive
GATE_SUITE_TIMEOUT_SECONDS from the measured runtime) is unchanged and still rests on this
harness. Kept in the repo so the claim in docs/design/OPS2_PUBLISH_GATE_HEAD_CHECKOUT.md can be
re-run rather than believed.

Two phases -- the two subjects that still exist:

    THROWAWAY -- what the gate ACTUALLY runs today: a fresh `mkdtemp` checkout of HEAD, with no
                 `__pycache__`, so every module compiles from source. The shipped steady state
    BASELINE  -- the pre-ruling subject: the live working tree

There is deliberately no WARM phase. Timing one would require the directory the R3 elimination
deleted, and a phase that cannot be run is worse than absent: until this commit both checkout
phases were gated on getting the shared name back from `prc._head_checkout()`, which since
444402ee0 never happens, so every launch aborted with the pre-written and now FALSE cause
"another publisher held the reuse lock". The precondition is inverted here rather than removed:
a checkout that IS the shared directory means someone re-enabled reuse without re-reading this
harness, and that phase is not a throwaway, so it refuses.

`-x` is removed from the argv on BOTH sides. With it, a red suite stops at the first
failure, so "duration" would be time-to-first-failure and the sides would not be comparable.
The suite is expected to be red at HEAD for unrelated reasons; the runtime is the measurement,
the verdict is not.

The box is shared with the live publisher, whose own suite would both skew the wall-clock and
contend for a machine with ~5GB free. Each phase therefore TAKES the publisher's own run lock
(`process_run_complete.py::_run_lock`) for its duration and waits for memory headroom before
timing anything, and DEFERS -- banking what it has measured for the next launch to resume -- if
either wait times out. It never times a suite into a contended box: two full suites do not fit
in 15.9G (two runs were OOM-killed proving it), and the run that survives contention reports a
slow BASELINE -- which is the ratio's DENOMINATOR, so a contended box under-states the tax. The
bias survived the criterion's supersession: it used to move the verdict toward MEETS, and it now
makes the cost of the elimination look smaller than it is. Same direction, still reassuring,
still refused.

Holding the lock rather than waiting for a gap is what makes this converge: with a queue of
pending markers the publisher runs nearly back-to-back, so nine launches waiting for idleness
banked two phases and never once reached the baseline. A publisher that cannot take the lock
exits `EXIT_LOCK_SKIPPED` with its marker still pending -- an outcome the worker's sweep already
retries -- so the cost is one deferred publish cycle per phase. See `_publisher_exclusion`.

Usage:  python3 -m tools.measure_publish_gate_subject_cost --systemd  [THE committed launch]
        python3 -m tools.measure_publish_gate_subject_cost --detach   [session-detach only]
        python3 -m tools.measure_publish_gate_subject_cost [--out PATH]   [inline, blocks ~40min]
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

    Two concurrent runs would each time a full suite into a box that fits one (two OOM kills
    proved it), and the survivor's number would carry the other's contention without saying so,
    so a launch must refuse rather than race."""
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


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


# ── THE HEARTBEAT COVERED ONLY THE WAITING, SO A DEATH AT WORK LOOKED LIKE A DEATH AT REST ───
#
# OBSERVED (2026-08-11), from the KERNEL log for the 22:28Z launch -- `journalctl -k`, not this
# harness's own journal:
#
#   Out of memory: Killed process 3272589 (python3) total-vm:12949376kB, anon-rss:12928996kB
#   oom-kill:constraint=CONSTRAINT_NONE ... global_oom,
#   task_memcg=/user.slice/.../publish-gate-subject-cost.service
#
# The unit's own python was pid **3244117** (`journalctl --user -u publish-gate-subject-cost`).
# **3272589 is its CHILD** -- the BASELINE phase's pytest, at 12.9G anon RSS on a 15.9G box,
# which triggered a GLOBAL oom (`CONSTRAINT_NONE`), not a cgroup-limit one. The launch had
# already taken the lock and was IN THE SUITE.
#
# `WORKER_FINDING_THE_MEASUREMENT_IS_OOM_KILLED_INSIDE_ITS_OWN_WAIT_2026-08-11` concluded the
# opposite -- *"It died in the wait, not in the suite"* -- and filed that as `observed`, because
# every signal available to its reader agreed:
#
#   * the last log line was `. waiting to TAKE the publisher's run lock`. There is no line for
#     ACQUIRING that lock, and none for starting a suite; the phase banner is printed BEFORE the
#     wait, so it cannot separate them either.
#   * `last_heartbeat` froze at the same moment, because `heartbeat` is called only from the
#     three WAIT loops. The instant a wait returns, the artefact stops advancing and stays
#     frozen for the ~20 minutes the suite runs.
#
# So the record could not tell "still waiting" from "working, and killed at it", and the repair
# that finding proposed -- a memory guard inside the ACQUIRE POLL -- would not have fired on the
# thing that actually killed it. An instrument whose blind spot misdirects the next reader is
# worse than one with a gap they can see: R15's fail-silent pattern, one level up, on the
# measurement this atom's exit criterion 1 is waiting for.
#
# `_InFlight` closes it. The record carries WHICH PHASE and WHAT STAGE continuously, so a killed
# launch leaves a diagnosis instead of a silence, and the next launch reads it straight back as
# `previous_launch_died_in_flight` rather than re-deriving it from a journal nobody reads.
class _InFlight:
    """The heartbeat, and the stage marker a KILLED launch leaves behind, in one object.

    CALLABLE, so every existing `heartbeat()` call site keeps working unchanged -- the wait
    loops go on stamping `last_heartbeat`. What is new is `stage()`, which the loops and the
    suite call as they hand off to each other, and which CHECKPOINTS: the marker is only worth
    anything if it is on disk when the kill arrives, and a kill gives no chance to write.

    `mem_available_mb` is stamped at every stage change because the conditions at the moment of
    death are exactly what a phase record cannot carry -- a phase that is killed never banks
    one."""

    def __init__(self, results, checkpoint):
        self._results = results
        self._checkpoint = checkpoint

    def __call__(self):
        self._results["last_heartbeat"] = _utc_now()
        self._checkpoint()

    def enter(self, phase):
        """Open the marker for a phase about to be run (not one being resumed from the bank)."""
        self._results["in_flight"] = {"phase": phase, "stage": "starting",
                                      "since": _utc_now(), "pid": os.getpid(),
                                      "mem_available_mb": _mem_available_mb()}
        self._checkpoint()

    def stage(self, name):
        """Advance the marker. A no-op before `enter`, so a bare `_time_suite` call in a test
        neither crashes nor invents a phase it cannot name."""
        marker = self._results.get("in_flight")
        if not isinstance(marker, dict):
            return
        marker["stage"] = name
        marker["stage_since"] = _utc_now()
        marker["mem_available_mb"] = _mem_available_mb()
        self._checkpoint()

    def clear(self):
        """Close the marker: this phase banked, or the run ended on a path it chose.

        A record that still carries `in_flight` is therefore exactly a record whose writer did
        NOT get to choose its ending -- which is the whole signal."""
        if self._results.pop("in_flight", None) is not None:
            self._checkpoint()


def _mark_stage(heartbeat, name):
    """Advance a heartbeat's stage marker if it has one.

    The wait helpers take a plain `heartbeat` callable in their own tests and a `_InFlight` in
    the real run, so the marker is optional at every call site rather than a new required
    argument threaded through five signatures."""
    stage = getattr(heartbeat, "stage", None)
    if callable(stage):
        stage(name)


def _prior_in_flight(out_path: str):
    """The `in_flight` marker an earlier launch left behind, or None. Never raises.

    Present == that launch was killed without reaching any of its own exits (bank, defer,
    abort). It is read at launch and re-published as `previous_launch_died_in_flight` so the
    diagnosis survives into the record this launch writes, instead of being overwritten by it."""
    try:
        prior = json.loads(Path(out_path).read_text())
    except (OSError, ValueError):
        return None
    marker = prior.get("in_flight") if isinstance(prior, dict) else None
    return marker if isinstance(marker, dict) else None


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
        _mark_stage(heartbeat, "waiting_for_publisher_to_finish")
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


# Held across a phase so no NEW publisher can start inside it. RE-ENTRANT: a second `flock` on a
# second fd of the same file blocks even within one process, so a nested hold must be counted
# here rather than attempted, or the inner one deadlocks into a deferral it would misreport as a
# busy publisher. No phase nests today -- the COLD phase did, because it deleted the reused
# checkout, rebuilt it and timed it under one hold, and the R3 elimination removed that phase.
# The counting is kept because the deadlock it prevents is silent and its cost is one integer;
# it is a property of this contextmanager, not of any current caller.
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
            _mark_stage(heartbeat, "waiting_for_publisher_lock")
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

    # THE LINE WHOSE ABSENCE COST A MISREAD FINDING. Without it the journal jumps straight from
    # "waiting to TAKE the lock" to the OOM, and every reader concludes the wait was still
    # running -- see the `_InFlight` note above.
    if waited:
        log("  . took the publisher's run lock -- the wait is over, the phase starts now")
    _mark_stage(heartbeat, "holding_publisher_lock")
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
        _mark_stage(heartbeat, "waiting_for_memory_headroom")
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
    basetemp arrives. Both apply identically to both phases, so neither can move the ratio."""
    argv = [a for a in prc.publish_gate_pytest_argv("tests/") if a != "-x"]
    return argv + ["--basetemp={}".format(prc.HEAD_CHECKOUT_ROOT / MEASURE_BASETEMP_NAME)]


# ── A PHASE MAY KILL ITSELF; IT MAY NOT KILL THE BOX ─────────────────────────────────────────
#
# OBSERVED (`journalctl -k`, 2026-08-10 23:11:10Z): the BASELINE phase's pytest reached 12.9G
# anon RSS on a 15.9G box and was killed by the GLOBAL OOM killer --
# `constraint=CONSTRAINT_NONE ... global_oom`, not a cgroup limit. A global OOM is not a failure
# of this harness alone: the kernel picks its victim by badness score across the whole box, so
# the live publisher is a candidate every time this runs. Three launches have died this way.
#
# The repair is option A of
# WORKER_FINDING_THE_MEASUREMENTS_SUBJECT_IS_LARGER_THAN_THE_GATES_2026-08-11: give each phase's
# pytest its own memory bound, so an over-large run ends as THAT PHASE's named failure and the
# rest of the box -- the publisher above all -- is never a candidate for it.
#
# `--scope` and not `--unit`: a scope stays a child of this process and inherits cwd, env and
# stdio, so the timing, the captured summary line and `_publisher_exclusion` all keep working
# unchanged. (`--unit` reparents to the user manager, which is right for the LAUNCH -- see
# `_systemd_run_argv` -- and wrong for a thing we are timing.)
#
# THE BOUND IS A CEILING, NOT A DERIVED FIGURE, and says so: the whole point of the run is that
# the -x-less peak has never been measured. What is known is that the publish gate -- the
# production path this imitates -- peaked at 2.42G in a live sample, and that 12.9G is where the
# box dies. 8G is comfortably above any legitimate peak observed and comfortably below the
# lethal one. `tools/sample_gate_rss_premium.py` is measuring the real peaks; when it reports,
# this ceiling should be re-derived from them rather than left at a round number.
PHASE_MEMORY_MAX_MB = 8192


class _Unbounded(Exception):
    """Raised when a phase cannot be given a memory bound, so it must not run.

    Fail-CLOSED and deliberately not a `_Deferred`: deferring says "try again later", and a box
    with no `systemd-run` will not grow one. The unbounded path is the one that has killed this
    box three times, so 'measure anyway' is the option that is not on the table."""


def _scope_argv(unit: str, memory_max_mb: int = PHASE_MEMORY_MAX_MB) -> list:
    """The `systemd-run` prefix that bounds one phase. Built here so a test can assert its
    shape without spending twenty minutes proving it."""
    # `MemorySwapMax=0` is NOT belt-and-braces, it is the half that does the killing. Measured
    # while building this: a 300MB allocation under `MemoryMax=128M` alone COMPLETES, rc=0 --
    # the kernel reclaims and pushes anonymous pages into this box's 4G of swap instead of
    # killing anything. A bound that only throttles would leave a 12.9G suite thrashing the box
    # rather than global-OOMing it, which is a slower version of the same harm. With swap denied,
    # exceeding the ceiling is a cgroup OOM kill, and the phase dies alone.
    return ["systemd-run", "--user", "--scope", "--quiet",
            "--unit={}".format(unit),
            "--property=MemoryAccounting=yes",
            "--property=MemorySwapMax=0",
            "--property=MemoryMax={}M".format(memory_max_mb)]


def _phase_scope_unit(cwd: Path) -> str:
    """A distinct scope name per phase run, so two never collide on a retry."""
    return "publish-gate-phase-{}-{}".format(os.getpid(), abs(hash(str(cwd))) % 100000)


def _bounded_argv(cwd: Path, log) -> list:
    """The phase's pytest argv, wrapped in its memory bound. Raises `_Unbounded` if it cannot be.

    An unreadable/absent `systemd-run` BLOCKS the phase rather than running it bare: an
    unavailable control is a failed control (R15), and here the control is the only thing
    standing between a 12.9G suite and the publisher."""
    if shutil.which("systemd-run") is None:
        log("  ! systemd-run unavailable -- REFUSING to time an unbounded suite; the "
            "unbounded path is what global-OOM-killed this box three times")
        raise _Unbounded("systemd-run unavailable")
    return _scope_argv(_phase_scope_unit(cwd)) + _argv_without_x()


def _looks_like_the_bound(result_returncode: int, mem_available_after_mb) -> bool:
    """Did this phase die against ITS OWN ceiling rather than the box's?

    `inferred`, and labelled as such in the record. The exact discriminator lives in the scope's
    `memory.events`, which is torn down with the scope before we can read it. What survives is
    the pair the kernel log made legible: a cgroup kill leaves the BOX with memory (only the
    phase was squeezed), a global OOM leaves it starved. Only ever consulted on a SIGKILL."""
    if result_returncode != -9:
        return False
    if mem_available_after_mb is None:
        return False
    return mem_available_after_mb >= MIN_MEMORY_HEADROOM_MB


# ── A BASIS IS A CLAIM ABOUT THIS PHASE, NOT A PARAGRAPH ABOUT THE FIELD (2026-08-11) ─────────
#
# THE DEFECT, READ OFF THIS RECORD RATHER THAN IMAGINED. Both `_basis` fields were single string
# LITERALS, written identically beside every verdict, so each described exactly one branch and
# was wrong beside the other. In the banked record of launch 13:
#
#   "ran_to_completion": true,
#   "ran_to_completion_basis": "observed: a negative returncode is death by signal, so the suite
#                               never reported and its seconds is a lower bound"
#
# for a phase with `returncode: 1` and a printed summary of 23,831 passed in 1771.69s. The
# returncode was not negative, the suite DID report, and its seconds is not a lower bound. The
# same literal sat beside `false` on the truncated phase, where it happened to be true.
# `hit_memory_ceiling_basis` had it the other way round: the basis for a POSITIVE cgroup-kill
# inference was stamped beside `false` on two phases that never saw a SIGKILL at all.
#
# WHY THIS IS NOT COSMETIC, and it is the reason this atom is the one that got bitten: the
# sentence "its seconds is a LOWER BOUND" is the exact discriminator deciding what a number may
# be used for here -- floors admit it, the ratio refuses it (`_ran_to_completion_from` above).
# The one number this atom still owes is a RATIO, and the record was telling its next reader that
# the one phase which ran to completion was a lower bound. A reader who believed the basis over
# the boolean would refuse the only sound ratio term in the file.
#
# It is also an R9 breach in miniature: `observed` and `inferred` are not decorations, and a fixed
# literal cannot label a verdict it did not look at. Completion by returncode is OBSERVED; the
# cgroup-versus-global discriminator is INFERRED; and the case where MemAvailable could not be
# read is neither -- it is a question that went unanswered, which now says so instead of quietly
# rendering as a confident `false`.
def _ran_to_completion_basis(returncode, hit_memory_ceiling: bool) -> str:
    """The evidence for THIS phase's `ran_to_completion`, in its own terms."""
    if hit_memory_ceiling:
        return ("inferred: this phase was killed against its own {}MB ceiling, so it never "
                "reported and its seconds is a lower bound on the runtime it was heading for"
                .format(PHASE_MEMORY_MAX_MB))
    if not isinstance(returncode, int) or isinstance(returncode, bool):
        return ("unavailable: no returncode was recorded, so completion is unprovable -- which "
                "is treated as NOT completed rather than as a pass")
    if returncode < 0:
        return ("observed: returncode {} is death by signal, so the suite never reported and "
                "its seconds is a lower bound on the runtime it was heading for"
                .format(returncode))
    return ("observed: pytest returned {} and printed its own summary line, so the suite ended "
            "under its own control and its seconds is a completed runtime".format(returncode))


def _hit_memory_ceiling_basis(returncode, mem_available_after_mb, hit: bool) -> str:
    """The evidence for THIS phase's `hit_memory_ceiling`, in its own terms."""
    if hit:
        return ("inferred: SIGKILL with the box still holding {}MB, above the {}MB headroom "
                "floor -- a cgroup kill of this phase, not a global OOM"
                .format(mem_available_after_mb, MIN_MEMORY_HEADROOM_MB))
    if returncode != -9:
        return ("observed: returncode {} is not a SIGKILL, and this inference is only ever "
                "consulted on one".format(returncode))
    if mem_available_after_mb is None:
        return ("unavailable: SIGKILL, but MemAvailable could not be read afterwards, so the "
                "cgroup-versus-global discriminator has no input and nothing is claimed here")
    return ("inferred: SIGKILL with the box itself down to {}MB, below the {}MB headroom floor "
            "-- a global OOM the box lost, not this phase's own ceiling"
            .format(mem_available_after_mb, MIN_MEMORY_HEADROOM_MB))


# ── ASK THE SUBJECT WHAT IT IS, NOT THE REPO WHAT IT HAS BECOME (2026-08-11) ─────────────────
#
# THE DEFECT, OBSERVED IN THE LIVE RECORD RATHER THAN IMAGINED. Launch 14 banked:
#
#     "throwaway_checkout": {"cwd": "/var/tmp/publish-gate-head-qey8309l",
#                            "head_sha_at_run": "a322429d1...", "seconds": 1873.7}
#
# and the field's own comment called that "the SHA THIS phase actually ran against". It was not.
# The launch header says `started_at 20:29:36Z`; the next phase entered at 21:33:51Z, so this
# suite STARTED at ~21:02:37Z -- and a322429d1 was committed at 21:26:07Z, twenty-three minutes
# LATER, into a repo whose contents could not reach a `git archive` extraction that had already
# happened. The stamp was `prc._head_sha()` read in the LIVE repo AFTER the suite returned, so it
# named whichever commit some other lane happened to land during the ~31 minutes of the run.
#
# WHY IT IS NOT COSMETIC, AND WHY IT BITES HERE. This field is the ONLY input to the cross-commit
# comparability guard -- the rule ticks 4 and 8 both exist to enforce, that a ratio may not span
# two commits. End-stamping makes that guard answer a question about neither subject:
#
#   * FAIL-OPEN, and likeliest exactly when the harness runs. Throwaway extracted at X, runs 31
#     minutes while commits land to Z; baseline starts at Z and the box stays quiet, so it too
#     ends at Z. Both stamps read Z, `spanned` is a single SHA, and the ratio is COMPUTED across
#     subjects X and Z and published as the cost of the checkout. That is precisely the defect
#     the guard was written twice to prevent, arriving through the door it was watching -- and it
#     needs a QUIET second phase, which is the condition this harness waits for.
#   * FAIL-CLOSED the other way: two phases that genuinely ran the same code are refused, and the
#     atom pays another ~40 minutes, because one unrelated commit landed during the second phase.
#
# THE FIX IS TO ASK THE ARTEFACT. A checkout made by `prc._head_checkout()` is a real repo whose
# `.git/HEAD` is the extracted SHA (`_make_checkout_a_repo`), so the subject can be asked what
# commit it is instead of the live repo being asked what commit it now has. For the in-tree phase
# the subject IS the working tree, so the same question answers live HEAD -- but asked BEFORE the
# suite starts, which is when that subject was fixed as far as it is ever fixed.
#
# AND THE MOVE IS RECORDED RATHER THAN REFUSED. Asking twice -- before and after -- makes a
# mid-run commit VISIBLE (`subject_changed_during_run`) instead of silently relabelling the
# phase. It is deliberately not a ratio refusal: the in-tree subject is a shared tree that other
# lanes commit to every few minutes, so refusing on it would starve this atom's one owed number
# forever, which is the guard-that-waits-for-a-gap shape. A checkout cannot move under itself, so
# on that phase the flag is always False and its being True would itself be evidence of a bug.
def _subject_sha(cwd) -> str:
    """The commit the SUBJECT AT `cwd` is, or None if git cannot say.

    Deliberately not `prc._head_sha()`, which always asks PROJECT_DIR: a throwaway checkout is a
    different repo from the one this process lives in, and asking the wrong one is the defect
    above. None -- never a guess -- so a phase git could not answer for is dropped by the
    comparability rule rather than being compared on a fabricated SHA."""
    try:
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(cwd),
                              capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    if head.returncode != 0:
        return None
    return head.stdout.strip() or None


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
    # The suite is the ~20-minute stretch in which nothing else here writes, and it is where the
    # 22:28Z launch was killed. Marked AND logged before the child starts, so the artefact and
    # the journal both say so even though neither gets another word afterwards.
    _mark_stage(heartbeat, "suite_running")
    argv = _bounded_argv(cwd, log)
    log("  . suite starting in {} ({}MB available, capped at {}MB)"
        .format(cwd, mem_before, PHASE_MEMORY_MAX_MB))
    # ASKED OF THE SUBJECT, AND ASKED FIRST -- see the block above `_subject_sha`. This is the
    # commit the suite below actually starts against; reading it afterwards in the live repo
    # named a commit that did not exist when the tree was extracted.
    subject_before = _subject_sha(cwd)
    started_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    started = time.monotonic()
    result = subprocess.run(argv, cwd=str(cwd), env=env,
                            capture_output=True, text=True, errors="replace")
    elapsed = time.monotonic() - started
    ended_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    subject_after = _subject_sha(cwd)
    _mark_stage(heartbeat, "suite_returned")
    tail = [ln for ln in result.stdout.strip().splitlines() if ln.strip()][-1:]
    mem_after = _mem_available_mb()
    hit_bound = _looks_like_the_bound(result.returncode, mem_after)
    if hit_bound:
        log("  ! phase exceeded its own {}MB ceiling and was killed inside its scope -- the box "
            "kept {}MB, so the publisher was never a candidate"
            .format(PHASE_MEMORY_MAX_MB, mem_after))
    return {
        "cwd": str(cwd),
        # The SHA THIS phase actually ran against -- read FROM THE SUBJECT, BEFORE the suite,
        # never from the live repo afterwards (see the block above `_subject_sha` for the live
        # record that carried a commit made 23 minutes after its own suite had started).
        # Stamped per phase, not once at launch: HEAD moves under a long measurement, and a
        # single launch-time stamp would make a sound result look stale to whoever reads it.
        "head_sha_at_run": subject_before,
        # The same question after the run, so a subject that moved is VISIBLE rather than
        # silently relabelled -- and so `head_sha_at_run` can be told from a stamp that merely
        # happens to still be current. A checkout cannot move under itself; the working tree can.
        "head_sha_at_end": subject_after,
        "subject_changed_during_run": bool(
            subject_before and subject_after and subject_before != subject_after),
        # The phase's own clock. Not decoration: it is what lets a reader (and
        # `test_no_banked_phase_stamps_a_commit_that_postdates_its_own_start`) check the stamp
        # against git's commit dates instead of taking the record's word for it.
        "started_at": started_at,
        "ended_at": ended_at,
        "seconds": round(elapsed, 1),
        "returncode": result.returncode,
        "summary": tail[0][:300] if tail else "",
        "loadavg_before": round(load_before, 2),
        "loadavg_after": round(os.getloadavg()[0], 2),
        "box_was_quiet": quiet,
        # The conditions the OOM happened in, recorded so a short phase can be told from a
        # starved one without going back to the journal.
        "mem_available_before_mb": mem_before,
        "mem_available_after_mb": mem_after,
        "had_memory_headroom": had_headroom,
        # The ceiling this phase ran under, and whether it hit it. `hit_memory_ceiling` is
        # INFERRED (see `_looks_like_the_bound`) -- a phase that hit its own bound is a phase
        # whose SECONDS mean nothing, so a reader must not average it into a ratio.
        "memory_max_mb": PHASE_MEMORY_MAX_MB,
        "hit_memory_ceiling": hit_bound,
        # DERIVED FROM THIS PHASE, not a literal restating the field (see the block above the two
        # basis helpers): a fixed sentence beside a computed verdict describes one branch and
        # misdescribes the other, and both of these did.
        "hit_memory_ceiling_basis": _hit_memory_ceiling_basis(
            result.returncode, mem_after, hit_bound),
        # Stated because the number carries it and a future reader re-deriving
        # GATE_SUITE_TIMEOUT_SECONDS "from the measured runtime" would not otherwise know: this
        # is a run of a STRICTLY LARGER suite than the gate performs, because `-x` is stripped
        # here and kept there, and the suite is red at HEAD. Erring high is the safe direction
        # for a bound whose undersizing wedges publishing -- but it is an error, not a fit.
        "subject_larger_than_the_gates": True,
        "subject_note": "-x stripped for comparability; the gate stops at the first failure of "
                        "a red suite and this does not",
        # DID THE SUITE END ON ITS OWN? A red suite (rc=1) did: it ran every test it meant to and
        # reported. A suite killed by a SIGNAL (rc<0) did not -- its `seconds` is a LOWER BOUND on
        # the runtime it was heading for, and that distinction decides which questions the number
        # may be used to answer. See `_ran_to_completion`.
        "ran_to_completion": _ran_to_completion_from(result.returncode, hit_bound),
        "ran_to_completion_basis": _ran_to_completion_basis(result.returncode, hit_bound),
    }


# ── A LOWER BOUND MAY RAISE A FLOOR AND MAY NOT BE A DENOMINATOR (2026-08-11) ─────────────────
#
# THE DEFECT THIS CLOSES, OBSERVED IN THIS RECORD RATHER THAN IMAGINED. Launch 11 timed
# `in_tree_baseline` at 1302.4s with `returncode: -15` and a summary of nine progress dots --
# SIGTERM, mid-suite, no summary line ever printed. It was banked as a phase like any other and
# became the RATIO'S DENOMINATOR: `ratio_throwaway_over_in_tree: 1.084`, the one number superseded
# criterion 1's honest successor rests on, was a completed run divided by a truncated one.
#
# The prose was already right and that is the point. `_time_suite`'s own field comment says "a
# phase that hit its own bound is a phase whose SECONDS mean nothing, so a reader must not average
# it into a ratio" -- addressed to a READER, enforced nowhere, and `hit_memory_ceiling` only ever
# covered rc=-9 anyway. A reported state is not a control; this is the control.
#
# THE RULE IS AN ASYMMETRY, NOT AN EXCLUSION, and both halves are load-bearing:
#   * FLOOR (`implied_timeout_floor_2x`, `prc.measured_gate_timeout_floor`) -- ADMITS a truncated
#     phase. The suite provably ran at least that long, so a lower bound can only push the bound
#     UP, and up is the safe direction: erring high costs a longer wait on a genuinely hung gate,
#     erring low WEDGES PUBLISHING. Dropping these would blank the floor's evidence, which is the
#     fail-open shape the retired-phase block above exists to avoid.
#   * RATIO -- REFUSES it. A truncated denominator does not err in a safe direction, it distorts:
#     the true in-tree runtime is >= 1302.4s, so a truncated baseline can only OVERSTATE the tax.
#     "At most 8.4%" is a different claim from "8.4%", and an atom does not certify on the second
#     when it measured the first.
# So a truncated phase stays in the record, keeps feeding the floor, and is neither a ratio term
# nor able to retire the owed phase it failed to time.
def _ran_to_completion_from(returncode: int, hit_memory_ceiling: bool) -> bool:
    """Did this phase's suite end under its own control?

    Any returncode >= 0 did, red included -- pytest chose it and printed a summary. A negative
    returncode is death by signal (-15 SIGTERM, -9 SIGKILL/OOM), and `hit_memory_ceiling` is
    carried too so the memory case cannot pass on a technicality if that inference ever widens
    beyond rc=-9."""
    if hit_memory_ceiling:
        return False
    return returncode is not None and returncode >= 0


def _is_ratio_eligible(rec) -> bool:
    """May this banked phase be a term in the ratio?

    DERIVED FROM THE EVIDENCE, NOT FROM THE PRESENCE OF A KEY. Phases banked before
    `ran_to_completion` existed carry no such field, but they do carry the `returncode` it is
    computed from -- so completion stays PROVABLE for them and this control does not throw away
    a sound 1411.2s measurement over a schema change. It is the returncode, not the schema
    version, that says whether a suite finished.

    FAIL-CLOSED where the record genuinely cannot say: no `returncode` at all is an unprovable
    completion, and unprovable is not a pass."""
    if not isinstance(rec, dict):
        return False
    if not isinstance(rec.get("seconds"), (int, float)) or isinstance(rec.get("seconds"), bool):
        return False
    if "ran_to_completion" in rec:
        return rec["ran_to_completion"] is True
    rc = rec.get("returncode")
    if not isinstance(rc, int) or isinstance(rc, bool):
        return False
    return _ran_to_completion_from(rc, rec.get("hit_memory_ceiling") is True)


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
PHASE_ORDER = ("throwaway_checkout", "in_tree_baseline")


# ── AND WHEN A PHASE SET IS RETIRED, ITS BANKED NUMBERS ARE STILL MEASUREMENTS ────────────────
#
# `cold_checkout` and `warm_checkout` belonged to the pre-elimination configuration. They are no
# longer runnable and no longer comparable to anything this harness will time again, so they may
# never enter the ratio or retire an owed phase.
#
# They are NOT discarded, and the reason is a live fail-closed control. `prc.
# measured_gate_timeout_floor` reads every phase in this record that carries a `seconds` and
# derives the lowest legitimate `GATE_SUITE_TIMEOUT_SECONDS` from the worst of them;
# `test_the_timeout_clears_the_floor_the_measurement_implies` treats a record that cannot answer
# as a FAILED check. Today that control's entire evidence is one banked `cold_checkout` at
# 1291.9s. `_run_measurement` rewrites the record from `results["phases"]` BEFORE its first
# phase, so a resume that dropped retired phases would blank the floor's only evidence at the
# instant this harness next launched -- and wedge publishing on a control that was working.
#
# A retired phase is a real timing of this suite on this box. The floor errs high on it, which
# is the safe direction, and the record names it (`phases_from_a_retired_configuration`) so no
# reader mistakes it for part of the comparison.
RETIRED_PHASES = ("cold_checkout", "warm_checkout")


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
    hand-edited record cannot retire a phase that was never timed.

    `RETIRED_PHASES` are carried too -- see the block above: they never enter the ratio and never
    retire an owed phase, but they are the fail-closed timeout floor's only evidence, and this
    function is what decides whether the next launch keeps it."""
    try:
        prior = json.loads(Path(out_path).read_text())
    except (OSError, ValueError):
        return {}
    phases = prior.get("phases") if isinstance(prior, dict) else None
    if not isinstance(phases, dict):
        return {}
    keepable = PHASE_ORDER + RETIRED_PHASES
    banked = {name: rec for name, rec in phases.items()
              if name in keepable and isinstance(rec, dict) and rec.get("seconds") is not None}
    # A TRUNCATED PHASE IS KEPT AND STILL OWED. It stays in the record so the timeout floor keeps
    # its lower-bound evidence (see `_ran_to_completion_from`), but it is stripped of the right to
    # retire the phase it failed to time -- otherwise launch 11's SIGTERMed baseline is banked
    # forever and the ratio it poisons can never become honest, which is the never-converging
    # shape the resume was built to end.
    for name in PHASE_ORDER:
        rec = banked.get(name)
        if rec is not None and not _is_ratio_eligible(rec):
            banked[name] = dict(rec, retimed_because_truncated=True)
    return banked


def _owed_phases(banked: dict) -> list:
    """Phases still owed a run: absent, or present but never completed under their own control."""
    return [name for name in PHASE_ORDER if not _is_ratio_eligible(banked.get(name))]


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
# RETIRED phases are deliberately exempt. They feed `implied_timeout_floor_2x` -- a bound that
# must clear the worst legitimate runtime -- and an older, slower phase can only raise that bound.
# They never enter the ratio.
#
# Post-elimination BOTH surviving phases are ratio phases, so the pair-drop rule now governs the
# whole measurement: there is no third phase to bank across a commit boundary, and a launch that
# inherits one side of a stale pair re-times both.
RATIO_PHASES = ("throwaway_checkout", "in_tree_baseline")


def _drop_incomparable_ratio_phases(phases: dict, head_sha: str, log) -> list:
    """Drop banked ratio phases not provably timed at `head_sha`. Returns the names dropped.

    Only when one of the pair is still OWED: once both are banked at the same earlier commit
    they are comparable to each other, and re-timing them would cost 40 minutes to learn the
    same number.

    "OWED" HERE MUST MEAN WHAT IT MEANS EVERYWHERE ELSE (2026-08-11). This test was `name in
    phases`, and the completion rule landed beside it without reaching it -- so a TRUNCATED
    baseline counted as present here while counting as owed everywhere else, and the pair-drop
    concluded both sides were banked together when one of them was about to be re-timed at a new
    HEAD. Observed on launch 12, which skipped a throwaway banked at d1a5875b4 as "not re-run"
    while re-timing the baseline at 7ef696ea8: a ratio across two commits, reported as the cost
    of the checkout, which is the exact defect `_drop_incomparable_ratio_phases` was written one
    tick earlier to prevent. A new rule must be carried to every consumer of the notion it
    changes, or the older control keeps answering the old question."""
    if all(_is_ratio_eligible(phases.get(name)) for name in RATIO_PHASES):
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
    # COMPLETE MEANS EVERY PHASE ANSWERED, not every phase attempted. Launch 11 wrote
    # `complete: true` over a baseline that had been SIGTERMed mid-suite, so the one field a
    # reader is told to check ("read `complete`, not the file's existence") was the field that
    # concealed it. A truncated phase is missing until it has been re-timed.
    results["phases_missing"] = [p for p in PHASE_ORDER
                                 if not _is_ratio_eligible(results["phases"].get(p))]
    results["complete"] = not results["phases_missing"]
    # DERIVED on every write, not stamped once at launch: a reader must never have to work out
    # from the phase NAMES which of them belong to a configuration that no longer runs, and a
    # field computed in one place cannot drift from the phases actually present.
    results["phases_from_a_retired_configuration"] = sorted(
        name for name in results["phases"] if name in RETIRED_PHASES)
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
                "would time a second full suite into a box that fits one")
            return 1
        return _launch_under_systemd(args.out, log)
    if args.detach:
        if _measurement_is_running():
            log("! a measurement is already live -- refusing to start a second one, which "
                "would time a second full suite into a box that fits one")
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
    # Read BEFORE the first `_checkpoint` rewrites the file from `results` -- same reason
    # `_prior_deferral_count` is read here and not at deferral time.
    died_in_flight = _prior_in_flight(out_path)
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
    # sees a banked phase re-timed needs to know it was re-timed on purpose and why, and the
    # next tick needs to tell "this launch chose to pay for it again" from "the record was lost".
    results["dropped_for_comparability"] = dropped_for_comparability
    # Phases timed at a DIFFERENT commit than this launch's HEAD. Resuming across launches is
    # what makes the measurement converge on a box that keeps killing it, but it means the
    # record can span commits -- so it says so rather than letting a reader assume one SHA. Only
    # a RETIRED phase can survive that: it feeds the timeout floor, never the ratio, and the
    # pair that DOES feed the ratio is dropped and re-timed together above.
    results["phases_from_an_earlier_head"] = sorted(
        name for name, rec in results["phases"].items()
        if rec.get("head_sha_at_run") and rec["head_sha_at_run"] != head_sha)

    # A previous launch's marker, republished under its own name so THIS launch's record still
    # carries the diagnosis. `None` is written explicitly: a reader must be able to tell "the
    # last launch ended on a path it chose" from "this field was never populated".
    results["previous_launch_died_in_flight"] = died_in_flight
    if died_in_flight:
        log("  . the previous launch was KILLED in phase {} at stage '{}' (since {}, {}MB "
            "available) -- it did not defer, abort or bank".format(
                died_in_flight.get("phase"), died_in_flight.get("stage"),
                died_in_flight.get("stage_since") or died_in_flight.get("since"),
                died_in_flight.get("mem_available_mb")))

    heartbeat = _InFlight(results, lambda: _checkpoint(results, args.out, log))
    # Before the first wait, so that a run killed IN the wait is still distinguishable from a
    # run that was never launched at all -- which is the failure this harness just suffered.
    _checkpoint(results, args.out, log)

    try:
        log("HEAD={} -- two timed runs, expect ~40 min total".format(head_sha))

        # THROWAWAY: what the gate actually runs every cycle since the R3 elimination -- a fresh
        # `mkdtemp` extraction of HEAD with no bytecode. No setup: there is nothing to delete,
        # because the directory this phase used to have to clear no longer exists.
        if _is_ratio_eligible(results["phases"].get("throwaway_checkout")):
            log("phase 1/2 THROWAWAY -- banked by an earlier launch at {}s, not re-run".format(
                results["phases"]["throwaway_checkout"]["seconds"]))
        else:
            log("phase 1/2 THROWAWAY -- a fresh checkout of HEAD, bytecode compiles from source")
            heartbeat.enter("throwaway_checkout")
            with _publisher_exclusion(log, heartbeat), prc._head_checkout() as path:
                if path is None:
                    log("! checkout unavailable -- cannot measure the clean subject")
                    heartbeat.clear()
                    results["aborted"] = "checkout unavailable"
                    _checkpoint(results, args.out, log)
                    return 1
                # THE PRECONDITION, INVERTED. It used to demand the shared reused directory and
                # so refused every launch after 444402ee0. What must be refused now is the
                # opposite case: a shared directory means `prc.REUSE_HEAD_CHECKOUT` was turned
                # back on, this phase would be timing a WARM subject, and the record would call
                # that number the cost of a throwaway. The reason logged is the reason that is
                # true -- the previous one named a lock with nothing left to protect.
                if path.name == prc.REUSED_HEAD_CHECKOUT_NAME:
                    log("! got the SHARED reused checkout ({}) -- reuse has been re-enabled, so "
                        "this phase would time a warm subject and report it as the throwaway "
                        "cost. Aborting rather than mislabelling the number.".format(path.name))
                    heartbeat.clear()
                    results["aborted"] = "reuse is enabled, so there is no throwaway to time"
                    _checkpoint(results, args.out, log)
                    return 1
                results["phases"]["throwaway_checkout"] = _time_suite(path, log, heartbeat)
            heartbeat.clear()
            log("   throwaway: {}s".format(results["phases"]["throwaway_checkout"]["seconds"]))
            _checkpoint(results, args.out, log)

        # BASELINE: the pre-ruling subject, the live working tree.
        if _is_ratio_eligible(results["phases"].get("in_tree_baseline")):
            log("phase 2/2 BASELINE -- banked by an earlier launch at {}s, not re-run".format(
                results["phases"]["in_tree_baseline"]["seconds"]))
        else:
            log("phase 2/2 BASELINE -- the live working tree, the pre-ruling subject")
            heartbeat.enter("in_tree_baseline")
            results["phases"]["in_tree_baseline"] = _time_suite(prc.PROJECT_DIR, log, heartbeat)
            heartbeat.clear()
            log("   baseline: {}s".format(results["phases"]["in_tree_baseline"]["seconds"]))
            _checkpoint(results, args.out, log)

        throwaway = results["phases"]["throwaway_checkout"]["seconds"]
        base = results["phases"]["in_tree_baseline"]["seconds"]
        # THE TAX, NOT THE SAVING. Superseded criterion 1 asked "is the clean subject within 1.3x
        # of in-tree?" -- a question about a reused checkout that can no longer be built. What is
        # measurable, and what the atom now owes, is how much the elimination costs every cycle
        # forever. It is reported, not graded: there is no threshold left to pass, and inventing
        # one would let a superseded criterion read as met.
        # REFUSED, NOT COMPUTED, when either term did not end under its own control. The number
        # this replaces (1.084, launch 11) divided a completed run by a SIGTERMed one; the reason
        # is named in the artefact so the next reader gets the cause rather than a null.
        # AND THE COMPARABILITY RULE HAS TO REACH THIS PATH TOO (2026-08-11). The cross-commit
        # guard lives in `_drop_incomparable_ratio_phases`, which runs at LAUNCH against BANKED
        # phases -- so it covers a pair inherited from an earlier run and does not cover a pair
        # timed inside THIS one. That is now the likelier path, not the exotic one: the two phases
        # are ~20 minutes each on a shared tree where the publisher and other lanes commit every
        # few minutes, so HEAD moving BETWEEN them is ordinary. Both would be complete, both
        # eligible, and the ratio would silently span two commits -- the exact defect that
        # function was written to prevent, arriving through the door it does not watch.
        # Fail-CLOSED and named, like the completion rule beside it: a ratio is a comparison, and
        # two runs of different code are not one.
        spanned = sorted({results["phases"][name].get("head_sha_at_run") for name in RATIO_PHASES})
        ineligible = sorted(name for name in RATIO_PHASES
                            if not _is_ratio_eligible(results["phases"].get(name)))
        if not ineligible and base and len(spanned) > 1:
            results["ratio_throwaway_over_in_tree"] = None
            results["ratio_unavailable_because"] = (
                "these phases were timed at DIFFERENT commits ({}), so their difference is not "
                "the subject's cost -- HEAD moved between the two ~20-minute phases"
                .format(", ".join(str(sha)[:9] for sha in spanned)))
        elif ineligible or not base:
            results["ratio_throwaway_over_in_tree"] = None
            results["ratio_unavailable_because"] = (
                "these phases did not run to completion, so their seconds is a lower bound and "
                "cannot be a ratio term: {}".format(", ".join(ineligible)) if ineligible else
                "the baseline measured zero seconds")
        else:
            results["ratio_throwaway_over_in_tree"] = round(throwaway / base, 3)
            results.pop("ratio_unavailable_because", None)
        # REPORTED, NOT REFUSED, and the asymmetry against the SHA rule above is deliberate. A
        # phase whose subject moved mid-run is not two subjects -- it is one subject that took a
        # small edit part-way through -- and the in-tree phase runs in a shared tree that other
        # lanes commit to every few minutes, so refusing on it would starve this atom's one owed
        # number permanently: the guard-that-waits-for-a-gap shape. It is named instead, so no
        # reader takes the ratio for a comparison of two frozen trees.
        results["ratio_subject_moved_during"] = sorted(
            name for name in RATIO_PHASES
            if (results["phases"].get(name) or {}).get("subject_changed_during_run"))
        results["ratio_measures"] = (
            "the permanent per-cycle TAX of gating on a cold HEAD checkout, against the pre-"
            "ruling in-tree subject. >1 is the cost of the R3 elimination, not a failure.")
        results["superseded_exit_criterion"] = {
            "was": "a REUSED checkout within 1.3x the in-tree baseline (OPS2 criterion 1)",
            "superseded_by": "444402ee0 -- reuse eliminated under R3 after it reset a shared "
                             "checkout under four live suites",
            "why_not_gradeable": "warm bytecode is unavailable to this atom at any price, so "
                                 "the 1.3x question has no measurable subject",
        }
        # Criterion 2: the bound must clear the worst LEGITIMATE runtime, so it is taken over
        # every phase this record holds -- including retired ones, which are real timings of this
        # suite on this box and can only push the bound up. Same rule as
        # `prc.measured_gate_timeout_floor`, deliberately: two rules for one number drift.
        timed = {name: rec["seconds"] for name, rec in results["phases"].items()
                 if isinstance(rec.get("seconds"), (int, float))}
        worst_phase = max(timed, key=timed.get)
        worst = timed[worst_phase]
        results["worst_legitimate_seconds"] = worst
        # NAMED, so the floor can be checked rather than recomputed by hand -- and so a reader
        # can tell a bound resting on a live phase from one resting on a retired one.
        results["worst_legitimate_phase"] = worst_phase
        # AND WHETHER THAT NUMBER IS THE RUNTIME OR ONLY A FLOOR UNDER IT. A truncated phase is
        # deliberately admitted here (it can only push the bound UP, the safe direction), but a
        # reader re-deriving the bound must know the suite was still running when it died --
        # otherwise "the worst measured run" reads as a completed one.
        results["worst_is_a_lower_bound"] = not _is_ratio_eligible(
            results["phases"].get(worst_phase))
        results["implied_timeout_floor_2x"] = int(worst * 2)

        _checkpoint(results, args.out, log)
        log("ratio throwaway/in-tree = {} -- the per-cycle TAX of gating on a cold checkout "
            "({}s vs {}s). Reported, not graded: criterion 1 is superseded.".format(
                results["ratio_throwaway_over_in_tree"], throwaway, base))
        log("worst legitimate run {}s ({}) -> timeout floor at 2x = {}s".format(
            worst, worst_phase, results["implied_timeout_floor_2x"]))
        log("written to {}".format(args.out))
        return 0
    except _Deferred as deferred:
        # A deferral is a CORRECT outcome, not a failure: the box was not fit to time a suite
        # in, the phases already banked are kept, and the next launch resumes from here. It is
        # recorded rather than merely logged because the journal of a killed unit is not
        # something the next tick reads -- the artefact is.
        # A deferral is an exit this launch CHOSE, so the marker comes down: `in_flight` present
        # in a record must mean exactly one thing -- the writer never reached any of its own
        # endings -- or it stops being evidence of a kill.
        heartbeat.clear()
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
    except _Unbounded as unbounded:
        # NOT a deferral. A deferral means "the box was briefly unfit"; this means "the one
        # control protecting the box from this harness is absent", which no amount of waiting
        # repairs. Recorded in the artefact and exited NON-ZERO so the unit goes `failed` and
        # says so, rather than looking like one more launch that quietly banked nothing.
        heartbeat.clear()
        results["blocked"] = {
            "reason": str(unbounded),
            "at_phase": results["phases_missing"][0] if results.get("phases_missing") else None,
            "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "why_not_a_deferral": "an unbounded phase is what global-OOM-killed this box three "
                                  "times; waiting does not grow a systemd-run",
        }
        _checkpoint(results, args.out, log)
        log("BLOCKED ({}) -- phases still owed: {}".format(
            unbounded, ", ".join(results["phases_missing"]) or "nothing"))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
