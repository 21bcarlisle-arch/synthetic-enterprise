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
contend for a machine with ~5GB free. Each phase therefore waits for the publisher to be idle
first, and records loadavg alongside its own number so a contaminated run is visible rather
than silently averaged in.

Usage:  python3 -m tools.measure_publish_gate_subject_cost --systemd  [THE committed launch]
        python3 -m tools.measure_publish_gate_subject_cost --detach   [session-detach only]
        python3 -m tools.measure_publish_gate_subject_cost [--out PATH]   [inline, blocks ~50min]
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from background import process_run_complete as prc  # noqa: E402

# A phase must not start while the real publisher is mid-suite. Bounded: if it never goes quiet
# we measure anyway and say so, because a harness that can hang forever is worse than a noisy
# number that is labelled noisy.
QUIET_WAIT_SECONDS = 45 * 60
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


def _launch_under_systemd(out: str, log) -> int:
    """Hand the measurement to the init system. Returns a process exit code, not a pid.

    Fails CLOSED on every unhappy path -- no systemd-run, a name already taken, a non-zero rc --
    because a launch that silently did nothing is precisely the failure mode of the last four
    attempts, and the next reader must be able to tell 'refused' from 'running'."""
    if shutil.which("systemd-run") is None:
        log("! systemd-run unavailable -- use --detach, and expect it to die if this tick's "
            "harness reaps its descendants (see the note above)")
        return 1
    try:
        res = subprocess.run(_systemd_run_argv(out), capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.SubprocessError) as exc:
        log("! could not launch the transient unit: {}".format(exc))
        return 1
    if res.returncode != 0:
        log("! systemd-run refused (rc={}): {}".format(
            res.returncode, (res.stderr or "").strip()[-400:]))
        log("  a live unit of this name IS the refusal -- check: "
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


def _wait_for_quiet(log, heartbeat=None) -> bool:
    """Wait for the publisher to finish. Returns True if the box went quiet.

    `heartbeat`, when given, is called on every poll. Both deaths so far happened INSIDE this
    wait, so a record that stops advancing here is the difference between "it is still waiting"
    and "it was killed waiting" -- and the latter would mean the detach did not hold and the
    next escalation is a systemd unit, not a third identical launch."""
    deadline = time.time() + QUIET_WAIT_SECONDS
    waited = False
    while _publisher_is_running():
        if time.time() > deadline:
            log("  ! publisher still live after {}s -- measuring anyway, flagged contended"
                .format(QUIET_WAIT_SECONDS))
            return False
        if not waited:
            log("  . waiting for the live publisher to finish before timing")
            waited = True
        if heartbeat is not None:
            heartbeat()
        time.sleep(QUIET_POLL_SECONDS)
    return True


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
            log("  ! only {}MB available after {}s (want {}MB) -- measuring anyway, flagged"
                .format(available, MEMORY_WAIT_SECONDS, MIN_MEMORY_HEADROOM_MB))
            return False
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


def _run_measurement(out_path: str, log) -> int:
    """The measurement itself, in THIS process. Blocks ~50 minutes."""
    args = argparse.Namespace(out=out_path)

    head_sha = prc._head_sha()
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
               "phases": _load_banked_phases(out_path)}
    results["resumed_phases"] = sorted(results["phases"])
    # Phases timed at a DIFFERENT commit than this launch's HEAD. Resuming across launches is
    # what makes the measurement converge on a box that keeps killing it, but it means the
    # record can span commits -- so it says so rather than letting a reader assume one SHA. The
    # exit-criterion ratio is warm/in-tree, and those two are re-run together whenever either is
    # owed, so a stale COLD can move the timeout floor but never the ratio.
    results["phases_from_an_earlier_head"] = sorted(
        name for name, rec in results["phases"].items()
        if rec.get("head_sha_at_run") and rec["head_sha_at_run"] != head_sha)

    def heartbeat():
        results["last_heartbeat"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        _checkpoint(results, args.out, log)
    # Before the first wait, so that a run killed IN the wait is still distinguishable from a
    # run that was never launched at all -- which is the failure this harness just suffered.
    _checkpoint(results, args.out, log)

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
        _wait_for_quiet(log, heartbeat)
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
                log("! got a THROWAWAY checkout ({}) -- another publisher holds the reuse lock, "
                    "so the warm phase would not be warm. Aborting rather than reporting a wrong "
                    "ratio.".format(path.name))
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
        with prc._head_checkout() as path:
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


if __name__ == "__main__":
    raise SystemExit(main())
