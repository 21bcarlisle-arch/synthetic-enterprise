"""RESOURCE HEADROOM — the machine sees the contention window before the kernel arbitrates it.

ADVISOR_FLAG_RESOURCE_HEADROOM_GOVERNOR_2026-08-09, sequenced by
DIRECTOR_PRIORITY_MEMORY_CLEANSE_2026-08-10 step 2 ("next draw after BUILD_THE_BREATHING:
the resource-headroom governor -- headroom watchdog with episode memory + the heavy-job
concurrency budget (sim runs, gates, publishers declare and defer, never collide)").

THE DEFECT THIS NAMES
---------------------
Nothing on this box knows how much memory is left, and nothing knows what else is already
running. So heavy jobs collide and the KERNEL picks the victim -- which it does by
oom_score, i.e. by size, i.e. it executes whichever innocent happens to be largest. Measured,
not inferred (2026-08-10, this seat): `/proc/vmstat oom_kill` stands at 64 lifetime kills;
dmesg shows the most recent executing `publish-gate-subject-cost.service` at 9,648,484 kB
anon-rss. Four heavy residents were observed live in one window -- an annual-report run at
5,548 MB, two scoped pytest gates at 854 MB and 577 MB, and a 316 MB agent seat -- against
a MemTotal the estimating code believed was 32 GB and which is really 15.9 GB.

Every number in the paragraph above is a 2026-08-10 MEASUREMENT and is kept as the incident
record, not as current state -- both have since moved, in opposite directions. The guest is
now ~24 GB (raised by the director mid-outage 2026-08-24), and the annual-report run is not
5,548 MB any more: it was OOM-killed fourteen times that day at peaks up to 13.5 G. Read the
guest size from `sample()["total_mb"]` and the job's size from `weight_drift()`, never from
this paragraph -- a memory constant read out of a docstring is the exact defect this module
was built about, and `CLASS_WEIGHTS_MB["sim_run"]` then repeated it.

The cost is not the crash. It is that an oom-kill is INDISTINGUISHABLE DOWNSTREAM from a
test regression: the gate dies mid-suite with no summary line, the publisher records
`kind: "test_regression"`, and the next cycle hunts a bug that never existed. A weekend of
"flapping reds" was partly this.

WHAT THIS IS, AND WHAT IT IS NOT
--------------------------------
Two mechanisms with one purpose -- make the contention VISIBLE and make it DEFERRABLE:

  1. A WATCHDOG (`observe`) that samples real kernel telemetry and carries episode memory:
     since-when the pressure began, the WORST availability seen inside the episode, and the
     VICTIMS taken during it. Victims are counted from `/proc/vmstat oom_kill`, a monotonic
     privilege-free counter -- not from parsing dmesg, which needs privilege this seat does
     not have and which rotates.

  2. A CONCURRENCY BUDGET (`admit` / `reservation`) where heavy jobs DECLARE their class
     before starting and are told to defer rather than collide.

It is a GOVERNOR, not a gate: it never fails a test, never reds a suite, never decides
whether anything publishes. Its only verdict is "start now" or "start later", and a
deferral is always reversible by waiting.

WHY TWO INDEPENDENT CONDITIONS (R15 -- killer pattern 1, TAUTOLOGY)
-------------------------------------------------------------------
Admission requires BOTH:
  * DECLARED -- the sum of live reservations plus this request fits the budget; and
  * MEASURED -- `/proc/meminfo MemAvailable` really has the room, right now.

Neither alone is sound, and they come from genuinely different sources: the ledger is what
this project INTENDED to be running, `MemAvailable` is what the kernel says IS running. A
ledger-only check is blind to anything that never declared (a human's pytest, the agent seat
itself, a leaked child). A measurement-only check is blind to the job that declared 6 GB and
has so far allocated 200 MB of it -- the collision that has not happened YET. Two tests pin
this and each kills a mutation that keeps only one condition:
`test_denies_when_the_budget_is_exhausted_though_memory_looks_free` and its mirror
`test_denies_when_memory_is_tight_though_the_ledger_is_empty`.

FAIL-CLOSED, AND WHY THAT DOES NOT WEDGE (R15 -- killer patterns 2 and 3)
-------------------------------------------------------------------------
An unreadable `/proc/meminfo` returns None and DENIES admission -- an unavailable check is a
failed check, never a fabricated green. The usual objection is the one this project has
already been bitten by (`feedback_control_that_can_only_fail_wedges`): a control that can
only refuse wedges the machine. It does not wedge here, for a structural reason -- **the
verdict is a DEFERRAL, not a refusal.** Nothing is cancelled; the caller retries on its own
next tick, and every deferral writes a receipt, so a governor that started denying
everything would be LOUD within one cycle rather than silently freezing the pipeline. That
is the deliberate asymmetry: refusing to start a 6 GB job costs minutes, and being wrong the
other way costs an innocent process and a false regression diagnosis.

WHY RESERVATIONS ARE REAPED BY (pid, starttime) AND NOT BY A LOCK
------------------------------------------------------------------
A crashed holder must not hold its reservation forever, so liveness is checked -- but this
project has already learned that a lock is not occupancy when the worker is a grandchild
(`feedback_a_lock_is_not_occupancy_when_the_worker_is_a_grandchild`: a killed parent frees
the flock while its pytest keeps running and keeps consuming). So a reservation is NOT a
lock held by a process: it is a record keyed to (pid, starttime), reaped only when that
exact process is gone. `starttime` (field 22 of `/proc/<pid>/stat`) defeats PID reuse --
without it a recycled PID silently resurrects a dead job's claim on 6 GB.

R5 -- TRANSITIONS ONLY. The watchdog alarms ONCE on entering pressure and ONCE on recovery,
with a hysteresis gap so a machine sitting on the threshold does not page every sample.

R12 -- headroom is a DIAGNOSTIC. The fastest way to make this number green is to run less;
that is forbidden as a response to the figure. Tight headroom means defer, schedule, or buy
memory -- never trim verification depth (CLAUDE.md: "DEPTH IS NOT THE PLACE TO SAVE").
"""
from __future__ import annotations

import contextlib
import datetime
import json
import os
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
OBS_DIR = PROJECT_DIR / "docs" / "observability"
EPISODE_PATH = OBS_DIR / ".resource_headroom_episode.json"
#: ONE LEDGER FOR THE WHOLE BOX (director, 2026-10-08: "Make one memory budget for the whole box that
#: everything goes through: runs from every lane, test gates and landings. Anything that doesn't fit
#: queues instead of co-running."). It was `OBS_DIR / ...`, i.e. inside whichever tree imported this
#: module, so a landing's gate in a clean extract and a run in a linked worktree each read a ledger
#: of their own and the box had no single budget. Machine-wide now; `SE_BOX_LEDGER_DIR` is the seam
#: for tests.
BOX_LEDGER_DIR = Path(os.environ.get("SE_BOX_LEDGER_DIR") or "/var/tmp/synthetic-enterprise-box")
RESERVATIONS_PATH = BOX_LEDGER_DIR / "heavy_job_reservations.json"
#: Set in the environment of whatever holds a reservation, so the same work asked again lower down
#: (a run inside an admitted gate, a run inside a launched long job) is not counted twice.
ADMITTED_ENV = "SE_BOX_ADMITTED"
DEFERRAL_LOG_PATH = OBS_DIR / "heavy_job_deferrals.jsonl"

MEMINFO = Path("/proc/meminfo")
VMSTAT = Path("/proc/vmstat")
PSI_MEMORY = Path("/proc/pressure/memory")

# Pressure bands, in MB of MemAvailable. Hysteresis gap is deliberate (R5).
#
# 1536 MB: chosen against the observed victims, not a round number. The kernel took a job at
# 9.6 GB anon-rss and another at 5.4 GB; a resident of that class allocates its last GB in
# seconds, so an alarm that waits for a few hundred MB left announces the kill rather than
# predicting it. 1.5 GB is roughly the largest single allocation step observed between
# samples in the weekend's traces -- one sampling interval of warning.
PRESSURE_FLOOR_MB = 1536
RECOVERED_FLOOR_MB = 3072

# What admission must leave behind for everything that never declared: the agent seat, the
# daemons, the OS. Measured floor, not a guess -- the seat alone was 316 MB and the resident
# daemon set ~200 MB in the observed window.
RESERVE_FOR_UNDECLARED_MB = 1024

# Declared peak RSS by job class, in MB. These are MEASUREMENTS from this box, and the source
# of each is named so a future re-measure knows what it is replacing. A class absent here has
# no measured weight and must pass one explicitly -- guessing on a caller's behalf is how a
# budget becomes fiction (the 32 GB constant was exactly that).
CLASS_WEIGHTS_MB = {
    # tools.run_annual_report via sim-runner.service. ORIGIN: systemd's journal, read through
    # weight_drift's own reader (oom_watch.read_unit_memory_peaks_mb) 2026-09-30 -- 82 runs
    # 2026-09-19..09-30, the whole retained record, max 6.9G (7,066 MB) on 09-27; the 24h window
    # peaked at 6.2G. Budgeted at the retained maximum rather than the window's, because
    # under-declaring is the fail-open side. The previous 13,824 MB was the 2026-08-24 peak and
    # stood a month at twice the job's size, reading clean because drift was checked upward only.
    # Do not raise it to keep sim-runner off a long job's box: that is
    # sim_runner.cycle_admission's explicit yield, not this figure's job.
    "sim_run": 7066,
    # tools.measure_publish_gate_subject_cost, oom-killed at 9,648 MB anon-rss 2026-08-10.
    # Budgeted at its observed peak: it is the largest single resident this project runs.
    "subject_cost": 9728,
    # scoped publish-gate pytest, observed 854 MB; budgeted with room for suite growth.
    "publish_gate": 1536,
    # tools.enumerate_publish_gate_reds -- same suite, no -x, so it runs to the end and holds
    # more; observed 577 MB and still climbing at sample time.
    "census": 1536,
    # tools.head_green_census via head-green-census.service -- the UNSCOPED nightly suite, no -x.
    # ORIGIN: systemd's journal through oom_watch.read_unit_memory_peaks_mb, 2026-09-30 -- the
    # whole retained record, 11 nightly runs 09-20..09-30. Only 09-20..09-23 finished (7.5G,
    # 8.9G, 10.5G, 10.9G); every run since hit SUITE_TIMEOUT_SECONDS and was killed, so its
    # peak (6.4G..8.5G) is a FLOOR on a truncated suite, not the job's size. Budgeted at the
    # largest COMPLETE run, 10.9G (11,162 MB). A cgroup peak, so it counts page cache as
    # sim_run's does.
    "head_green_census": 11162,
    # tools/pre_commit_test_gate.py's pytest, whole process tree (forked trace workers included),
    # by PSS. ORIGIN: measured 2026-10-08 on a run-heavy selection -- the run-phase2b event-log,
    # run-phase2b, home-move, void, fabric-demand and wall-census files, 414 tests, 11 min -- at
    # 2,190 MB. The peak is one module-scoped run at a time, so a wider selection pays it serially
    # rather than adding to it. Not a unit, so no journal re-derives it: re-measure when the
    # simulation's per-run peak moves.
    "commit_gate": 2190,
}

# Which systemd unit's record re-derives which class weight. Only classes that RUN AS A UNIT
# can appear -- the others are started ad hoc and leave no journal to check against, so they
# have no automatic re-derivation and stay hand-measured.
CLASS_UNITS = {
    "sim_run": "sim-runner.service",
    "head_green_census": "head-green-census.service",
}

#: How far back weight_drift asks. Wider than oom_watch's default so a weekly growth trend is
#: visible rather than only the current episode.
DRIFT_WINDOW = "-24h"

#: Per-class override of DRIFT_WINDOW. A once-nightly unit leaves ONE peak in 24h, and the
#: census's night-to-night spread is 6.4G..10.9G, so a one-sample window reads "over" on most
#: nights and "matches" on the rest -- a coin, not a check. ORIGIN: the retained journal the
#: weight itself was read from (~a month of nightly runs).
CLASS_DRIFT_WINDOWS = {"head_green_census": "-30d"}


#: How far a declared weight may sit ABOVE the observed peak before it reads over-declared.
#: Under-declaring has no tolerance -- it is fail-open. Over-declaring is fail-closed but not
#: free: at 13,824 MB against a 6.3 GB job it held back ~7 GB of a 24 GB guest and hid the fact
#: that one deferral rested on it. ORIGIN: the budget's own reserve for undeclared residents --
#: an over-reservation smaller than that margin is inside the error the budget already carries.
OVER_DECLARED_TOLERANCE_MB = RESERVE_FOR_UNDECLARED_MB


def weight_drift(job_class: str, since: str | None = None, journal_reader=None,
                 peaks_reader=None, live_reader=None) -> dict:
    """Has the world outgrown a declared weight? {job_class, declared_mb, observed_peak_mb, ...}

    WHY THIS EXISTS (OPS1: the designed reason, not a patch). `CLASS_WEIGHTS_MB` is the
    governor's model of how big a job is, and `admit()` is only as sound as it. A weight is a
    MEASUREMENT with a date on it, and this project has already been bitten twice by a memory
    constant that was true when written and false when read -- the 32 GB host figure, and then
    `sim_run` itself at 6,144 MB while the job it names was being killed at 13.5 G. A stale
    weight fails in the FAIL-OPEN direction: the governor admits a job it thinks is half its
    real size, and the kernel resolves the difference. So the table needs a reading that can
    contradict it, from a source it does not write.

    INDEPENDENCE (anti-tautology, R15). The observed peak comes from systemd's journal -- a
    record written by neither this table, nor the job, nor this repository. Comparing the
    table against a number derived from the table would be the tautology this rule names.

    `drifted` is TRISTATE and the third value is the point:
      * True  -- the journal answered and the weight is wrong in EITHER direction (`direction`
                 says which): "under" when the peak exceeds it, "over" when it exceeds the
                 peak by more than OVER_DECLARED_TOLERANCE_MB;
      * False -- the journal answered and the weight matches what was observed;
      * None  -- the journal could not be read, or the class has no unit. An unavailable
                 check is a FAILED check (R15), never a clean one, so None must not be
                 rendered as "no drift" by any caller.
    """
    if since is None:
        since = CLASS_DRIFT_WINDOWS.get(job_class, DRIFT_WINDOW)
    declared = CLASS_WEIGHTS_MB.get(job_class)
    unit = CLASS_UNITS.get(job_class)
    verdict = {
        "job_class": job_class,
        "unit": unit,
        "declared_mb": declared,
        "observed_peak_mb": None,
        "live_peak_mb": None,
        "samples": 0,
        "drifted": None,
        "direction": None,
        "detail": None,
    }
    if declared is None:
        verdict["detail"] = (
            f"{job_class!r} has no declared weight, so there is nothing to check it against"
        )
        return verdict
    if unit is None:
        verdict["detail"] = (
            f"{job_class!r} does not run as a systemd unit, so it leaves no independent "
            f"record -- this weight stays hand-measured and UNVERIFIED here, not clean"
        )
        return verdict

    # TWO SOURCES, AND THE SECOND IS NOT REDUNDANT. The journal only learns a peak when the
    # unit STOPS, so for a long-lived loop like sim-runner it reports the LAST unit lifetime
    # and is blind to growth inside the current one -- post-mortem exactly where this check
    # needs to be early. `MemoryPeak` on the running unit closes that. Measured 2026-08-24:
    # journal 13,824 MB vs live 22,703 MB for the same unit, at the same moment.
    #
    # INJECTION SEMANTICS: passing either reader means "this is the observation set", and the
    # other defaults to no-observation. Tests that construct a journal must not have the real
    # box's live peak silently join their sample -- that would make them non-deterministic in
    # the one direction that matters, since the real number is currently above every weight.
    injected = peaks_reader is not None or live_reader is not None
    if injected:
        peaks = peaks_reader(unit, since) if peaks_reader is not None else []
        live = live_reader(unit) if live_reader is not None else None
    else:
        try:
            from background.oom_watch import (
                read_unit_memory_peak_live_mb,
                read_unit_memory_peaks_mb,
            )

            peaks = read_unit_memory_peaks_mb(
                unit=unit, since=since, journal_reader=journal_reader
            )
            live = read_unit_memory_peak_live_mb(unit=unit)
        except Exception:
            peaks, live = None, None

    if live is not None:
        # None means the journal could not be read; a live reading does not repair that, but
        # it IS an observation, so it becomes the sample rather than being discarded.
        peaks = ([] if peaks is None else list(peaks)) + [live]
        verdict["live_peak_mb"] = round(live, 1)

    if peaks is None:
        verdict["detail"] = (
            f"the journal for {unit} could not be read, so whether {job_class!r}'s "
            f"{declared:.0f} MB still covers it is UNKNOWN -- an unavailable check is a "
            f"failed check (R15), not a clean one"
        )
        return verdict
    if not peaks:
        verdict["detail"] = (
            f"the journal for {unit} recorded no memory peak in {since}: nothing to "
            f"re-derive {job_class!r} from, so its {declared:.0f} MB stands unverified"
        )
        return verdict

    peak = max(peaks)
    verdict["observed_peak_mb"] = round(peak, 1)
    verdict["samples"] = len(peaks)
    if peak > declared:
        verdict["direction"] = "under"
        verdict["detail"] = (
            f"{job_class!r} is declared at {declared:.0f} MB but {unit} peaked at "
            f"{peak:.0f} MB across {len(peaks)} run(s) in {since} -- the governor is sizing "
            f"this job at {peak / declared:.1f}x under its measured footprint, which admits "
            f"it into memory that is not there. Re-derive CLASS_WEIGHTS_MB[{job_class!r}]"
        )
    elif declared - peak > OVER_DECLARED_TOLERANCE_MB:
        verdict["direction"] = "over"
        verdict["detail"] = (
            f"{job_class!r} is declared at {declared:.0f} MB but {unit} peaked at only "
            f"{peak:.0f} MB across {len(peaks)} run(s) in {since} -- {declared - peak:.0f} MB "
            f"over-reserved, more than the {OVER_DECLARED_TOLERANCE_MB} MB tolerance. Any "
            f"deferral that rests on the excess is an accident, not a decision. Re-derive "
            f"CLASS_WEIGHTS_MB[{job_class!r}]"
        )
    else:
        verdict["detail"] = (
            f"{job_class!r} declared at {declared:.0f} MB matches the {peak:.0f} MB "
            f"peak observed across {len(peaks)} run(s) in {since}"
        )
    verdict["drifted"] = verdict["direction"] is not None
    return verdict


def weight_drift_alarm(verdicts) -> str | None:
    """The NTFY/log payload naming every drifted or unverifiable weight, or None if all clean.

    An UNREADABLE verdict is reported, not swallowed: the whole failure mode is a weight
    nobody has checked lately, and "we could not check" is that same state.
    """
    drifted = [v for v in verdicts if v.get("drifted") is True and v.get("direction") != "over"]
    over = [v for v in verdicts if v.get("drifted") is True and v.get("direction") == "over"]
    unknown = [v for v in verdicts if v.get("drifted") is None]
    if not drifted and not over and not unknown:
        return None
    parts = []
    if drifted:
        parts.append(
            "DECLARED JOB WEIGHT OUTGROWN: "
            + "; ".join(v["detail"] for v in drifted)
            + ". Until re-derived, admit() is fail-open for these classes."
        )
    if over:
        parts.append(
            "DECLARED JOB WEIGHT OVER-RESERVED: " + "; ".join(v["detail"] for v in over)
        )
    if unknown:
        parts.append(
            "WEIGHT UNVERIFIED (a failed check, not a clean one — R15): "
            + "; ".join(f"{v['job_class']}: {v['detail']}" for v in unknown)
        )
    return " | ".join(parts)


def _now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


# --------------------------------------------------------------------------------------
# Sampling -- real kernel telemetry, or None. Never an estimate presented as a measurement.
# --------------------------------------------------------------------------------------

def _read_meminfo(path: Path | None = None) -> dict:
    """Parse /proc/meminfo into MB. Unreadable or unparseable → empty dict (→ deny)."""
    p = path or MEMINFO
    out: dict = {}
    try:
        text = p.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return out
    for line in text.splitlines():
        key, _, rest = line.partition(":")
        fields = rest.split()
        if not fields:
            continue
        try:
            kb = float(fields[0])
        except ValueError:
            continue
        out[key.strip()] = kb / 1024.0
    return out


def _read_oom_kills(path: Path | None = None):
    """Lifetime oom-kill count from /proc/vmstat, or None. Monotonic and privilege-free."""
    p = path or VMSTAT
    try:
        text = p.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    for line in text.splitlines():
        if line.startswith("oom_kill "):
            try:
                return int(line.split()[1])
            except (IndexError, ValueError):
                return None
    return None


def _read_psi(path: Path | None = None):
    """PSI memory stall, `some avg60` as a float, or None where PSI is unavailable."""
    p = path or PSI_MEMORY
    try:
        text = p.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    for line in text.splitlines():
        if line.startswith("some "):
            for field in line.split():
                if field.startswith("avg60="):
                    try:
                        return float(field.split("=", 1)[1])
                    except ValueError:
                        return None
    return None


def sample(meminfo_path: Path | None = None, vmstat_path: Path | None = None,
           psi_path: Path | None = None) -> dict:
    """One observation of the machine. Absent quantities are None, never zero.

    `available_mb` is MemAvailable, which the kernel computes including reclaimable cache --
    the right quantity for "can another job start". It is NOT MemFree, which on this box
    reads ~2 GB while 5 GB is genuinely available, and a governor keyed to MemFree would
    defer forever.

    `shmem_mb` is reported alongside because /tmp here is a TMPFS: files written to /tmp are
    RAM, they do NOT appear as process RSS, and MemAvailable already reflects them. A reader
    diagnosing "where did the memory go" needs that term visible or the sum never closes.
    """
    mem = _read_meminfo(meminfo_path)
    total = mem.get("MemTotal")
    avail = mem.get("MemAvailable")
    return {
        "timestamp": _now_iso(),
        "total_mb": round(total, 1) if total is not None else None,
        "available_mb": round(avail, 1) if avail is not None else None,
        "shmem_mb": round(mem["Shmem"], 1) if "Shmem" in mem else None,
        "swap_free_mb": round(mem["SwapFree"], 1) if "SwapFree" in mem else None,
        "psi_some_avg60": _read_psi(psi_path),
        "oom_kills_total": _read_oom_kills(vmstat_path),
    }


def band(available_mb, previous: str | None = None) -> str:
    """Classify availability into pressure / ok / unknown, holding `previous` in the gap.

    None → "unknown", which upstream renders RED and denies admission. An unmeasurable
    machine is not a healthy machine (R15 killer pattern 3, FAIL-SILENT).
    """
    if available_mb is None:
        return "unknown"
    try:
        a = float(available_mb)
    except (TypeError, ValueError):
        return "unknown"
    if a < PRESSURE_FLOOR_MB:
        return "pressure"
    if a >= RECOVERED_FLOOR_MB:
        return "ok"
    return previous if previous in ("pressure", "ok") else "ok"


# --------------------------------------------------------------------------------------
# Episode memory -- since-when, worst, victims.
# --------------------------------------------------------------------------------------

def _read_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return default


def _write_json(path: Path, payload) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        os.replace(tmp, path)
    except OSError:
        pass


def observe(episode_path: Path | None = None, drift_kwargs: dict | None = None,
            **sample_kwargs) -> dict:
    """Sample, fold into the episode, and return {sample, episode, transition}.

    `transition` is "entered", "recovered", or None -- and ONLY a non-None transition may be
    alarmed (R5). An unchanged status is never re-announced.

    VICTIMS are the delta in the lifetime oom_kill counter since the episode opened, so the
    alarm can say "this window has already cost us two processes" rather than reporting a
    level. The counter is monotonic, so a delta cannot be gamed by a restart -- and if it is
    unreadable the field is None (unknown), never 0 (nobody died).
    """
    path = episode_path or EPISODE_PATH
    prev = _read_json(path, {}) or {}
    obs = sample(**sample_kwargs)
    prev_state = prev.get("state") if prev.get("state") in ("pressure", "ok") else None
    state = band(obs["available_mb"], prev_state)

    kills_now = obs["oom_kills_total"]
    if state in ("pressure", "unknown") and prev_state != "pressure":
        # Episode opens.
        episode = {
            "state": "pressure" if state == "pressure" else "unknown",
            "since": obs["timestamp"],
            "worst_available_mb": obs["available_mb"],
            "worst_at": obs["timestamp"],
            "oom_kills_at_open": kills_now,
            "victims": 0 if kills_now is not None else None,
            "samples": 1,
        }
        transition = "entered"
    elif state == "ok" and prev_state == "pressure":
        episode = {
            "state": "ok",
            "since": obs["timestamp"],
            "recovered_from": {
                "since": prev.get("since"),
                "worst_available_mb": prev.get("worst_available_mb"),
                "victims": _victims(prev, kills_now),
            },
            "worst_available_mb": obs["available_mb"],
            "worst_at": obs["timestamp"],
            "oom_kills_at_open": kills_now,
            "victims": 0 if kills_now is not None else None,
            "samples": 1,
        }
        transition = "recovered"
    else:
        episode = dict(prev)
        episode["state"] = state if state in ("pressure", "ok") else episode.get("state", "unknown")
        episode.setdefault("since", obs["timestamp"])
        episode.setdefault("oom_kills_at_open", kills_now)
        worst = episode.get("worst_available_mb")
        if obs["available_mb"] is not None and (worst is None or obs["available_mb"] < worst):
            episode["worst_available_mb"] = obs["available_mb"]
            episode["worst_at"] = obs["timestamp"]
        episode["victims"] = _victims(episode, kills_now)
        episode["samples"] = int(episode.get("samples") or 0) + 1
        transition = None

    episode["last_sample"] = obs

    # THE WEIGHT-DRIFT READING (2026-08-24). Folded in here rather than given its own daemon
    # because OPS1 forbids a new operational mechanism to patch a symptom: this is a missing
    # READING handed to the observer that already runs, already owns the memory picture, and
    # is already wired into background_worker's cycle. Nothing here schedules, holds or
    # restarts.
    #
    # R5 -- TRANSITION ONLY, on the same doctrine as the pressure band above. A drifted weight
    # is a STANDING condition that persists until someone edits the table, so alarming it
    # every cycle would be the repeating-status noise R5 exists to stop. The set of drifted
    # classes is remembered in the episode and announced only when it CHANGES.
    drift_alarm = None
    try:
        verdicts = [weight_drift(name, **(drift_kwargs or {})) for name in sorted(CLASS_UNITS)]
        # Keyed on the class names, not the raw MB: the peak moves a little on every run and
        # would re-announce constantly, whereas "which weights are now wrong" is the fact.
        flagged = sorted(
            v["job_class"] for v in verdicts if v.get("drifted") is not False
        )
        episode["weight_drift"] = verdicts
        if flagged != (prev.get("weight_drift_flagged") or []):
            drift_alarm = weight_drift_alarm(verdicts)
        episode["weight_drift_flagged"] = flagged
    except Exception as exc:  # noqa: BLE001 -- a governor that crashes the worker is worse
        episode["weight_drift"] = None
        episode["weight_drift_flagged"] = prev.get("weight_drift_flagged") or []
        drift_alarm = f"weight-drift check itself failed to run ({exc}) — R15: a failed check"

    _write_json(path, episode)
    result = {"sample": obs, "episode": episode, "transition": transition}
    if drift_alarm:
        result["shadow_alarm"] = drift_alarm
    return result


def _victims(episode: dict, kills_now):
    """Victims since the episode opened. None (unknown) when either end is unreadable."""
    opened = episode.get("oom_kills_at_open")
    if kills_now is None or opened is None:
        return None
    return max(0, int(kills_now) - int(opened))


# --------------------------------------------------------------------------------------
# The heavy-job concurrency budget -- declare, then be admitted or deferred.
# --------------------------------------------------------------------------------------

def _proc_starttime(pid: int, proc_root: Path | None = None):
    """Field 22 of /proc/<pid>/stat, or None if the process is gone.

    Read from the parenthesised-comm form deliberately: a process whose name contains a
    space or a ')' (pytest workers do) breaks a naive split, and a mis-parsed starttime
    would silently make every liveness check answer "different process, reap it".
    """
    root = proc_root or Path("/proc")
    try:
        raw = (root / str(pid) / "stat").read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    close = raw.rfind(")")
    if close == -1:
        return None
    fields = raw[close + 2:].split()
    # After comm, field indices shift by 2: starttime is field 22 → index 19 here.
    if len(fields) < 20:
        return None
    return fields[19]


def _is_live(holder: dict, proc_root: Path | None = None) -> bool:
    """True only if THAT process still exists -- same pid AND same starttime (PID reuse)."""
    pid = holder.get("pid")
    if not isinstance(pid, int):
        return False
    starttime = _proc_starttime(pid, proc_root)
    if starttime is None:
        return False
    recorded = holder.get("starttime")
    if recorded is None:
        return False
    return str(recorded) == str(starttime)


def live_reservations(reservations_path: Path | None = None,
                      proc_root: Path | None = None) -> list[dict]:
    """Reservations whose holder is still running. Dead holders are dropped, not honoured."""
    path = reservations_path or RESERVATIONS_PATH
    rows = _read_json(path, []) or []
    if not isinstance(rows, list):
        return []
    return [r for r in rows if isinstance(r, dict) and _is_live(r, proc_root)]


def committed_mb(reservations_path: Path | None = None, proc_root: Path | None = None) -> float:
    """Total MB claimed by live holders."""
    total = 0.0
    for r in live_reservations(reservations_path, proc_root):
        try:
            total += float(r.get("weight_mb") or 0)
        except (TypeError, ValueError):
            continue
    return total


def weight_for(job_class: str, weight_mb=None):
    """The declared weight for a class. None when unknown and none was passed -- deny."""
    if weight_mb is not None:
        try:
            w = float(weight_mb)
        except (TypeError, ValueError):
            return None
        return w if w > 0 else None
    return CLASS_WEIGHTS_MB.get(job_class)


def running_long_jobs(records_path: Path | None = None, residents: list | None = None) -> list[dict]:
    """[{unit, peak_mb, pids}] for every long job that declared a peak AND still has a process.

    A launch through `launch_long_job` declares `--peak-mb`; this is how a neighbour that did NOT
    launch through that door sees it. Counted at the declared peak, not today's RSS: the 22222 leg
    read 3.7 GiB an hour into a run that peaked at 10.2 GiB, and at 19:07Z a sim-runner cycle
    arrived beside it and the kernel chose. Only units with a live process count -- a record left
    `live` after its job ended holds no memory, and counting it would defer the caller forever.
    """
    from background import launch_long_job

    declared = launch_long_job.declared_peaks(records_path)
    if not declared:
        return []
    if residents is None:
        residents = launch_long_job.resident_census()
    jobs = []
    for unit, peak in sorted(declared.items()):
        pids = sorted(r["pid"] for r in residents if r.get("unit") == unit)
        if pids:
            jobs.append({"unit": unit, "peak_mb": peak, "pids": pids})
    return jobs


def admit(job_class: str, weight_mb=None, reservations_path: Path | None = None,
          proc_root: Path | None = None, launch_records_path: Path | None = None,
          residents: list | None = None, **sample_kwargs) -> dict:
    """May a heavy job of this class start right now?

    Returns {admitted, reason, ...}. BOTH conditions must hold -- see the module docstring on
    why either alone is unsound. Every denial names which condition failed and with what
    numbers, because a deferral nobody can diagnose is just a stall.

    The declared side is reservations PLUS the declared peaks of running long jobs. An injected
    `reservations_path` with no `launch_records_path` reads no launch records: a synthetic
    ledger must not silently recruit whatever long job is live on the real box.
    """
    obs = sample(**sample_kwargs)
    weight = weight_for(job_class, weight_mb)
    reserved = committed_mb(reservations_path, proc_root)
    long_jobs = ([] if reservations_path is not None and launch_records_path is None
                 else running_long_jobs(launch_records_path, residents))
    committed = reserved + sum(j["peak_mb"] for j in long_jobs)
    total = obs["total_mb"]
    available = obs["available_mb"]
    budget = (total - RESERVE_FOR_UNDECLARED_MB) if total is not None else None

    decision = {
        "timestamp": obs["timestamp"],
        "job_class": job_class,
        "weight_mb": weight,
        "committed_mb": round(committed, 1),
        "reserved_mb": round(reserved, 1),
        "long_jobs": long_jobs,
        "available_mb": available,
        "budget_mb": round(budget, 1) if budget is not None else None,
        "admitted": False,
        "reason": None,
    }

    if weight is None:
        decision["reason"] = (
            f"undeclared weight: job class {job_class!r} has no measured weight in "
            "CLASS_WEIGHTS_MB and none was passed -- a budget that guesses is fiction"
        )
        return decision
    if available is None or budget is None:
        decision["reason"] = (
            "unmeasurable: /proc/meminfo gave no MemTotal/MemAvailable -- an unavailable "
            "check is a FAILED check (R15), so this defers rather than assuming room"
        )
        return decision
    if committed + weight > budget:
        named = "".join(
            f"; long job {j['unit']} declared {j['peak_mb']:.0f} MB, "
            f"pid(s) {', '.join(str(p) for p in j['pids'])}" for j in long_jobs)
        decision["reason"] = (
            f"budget exhausted: {committed:.0f} MB already declared ({reserved:.0f} MB reserved"
            f"{named}) + {weight:.0f} MB "
            f"requested exceeds the {budget:.0f} MB budget "
            f"(MemTotal {total:.0f} MB less {RESERVE_FOR_UNDECLARED_MB} MB for undeclared)"
        )
        return decision
    if available - weight < RESERVE_FOR_UNDECLARED_MB:
        decision["reason"] = (
            f"measured memory too tight: {available:.0f} MB available, {weight:.0f} MB "
            f"requested would leave less than the {RESERVE_FOR_UNDECLARED_MB} MB floor"
        )
        return decision

    decision["admitted"] = True
    decision["reason"] = (
        f"admitted: {weight:.0f} MB fits both the declared budget "
        f"({committed:.0f}+{weight:.0f} <= {budget:.0f} MB) and measured availability "
        f"({available:.0f} MB)"
    )
    return decision


def record_deferral(decision: dict, log_path: Path | None = None) -> None:
    """Append a deferral receipt. THE EXIT CRITERION IS THIS LINE.

    The flag's falsifiable exit is "a week without an oom-kill, OR every near-miss visible as
    a deferral with an alarm receipt". A deferral that left no trace would make a governed
    machine look identical to an idle one -- and this project has already learned that a
    silently-narrowed control reads as success (`feedback_prose_inventory_needs_a_falsifier`).
    """
    path = log_path or DEFERRAL_LOG_PATH
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(decision) + "\n")
    except OSError:
        pass


@contextlib.contextmanager
def admitted(job_class: str, log=None, reservations_path: Path | None = None,
             deferral_log_path: Path | None = None, **admit_kwargs):
    """Ask `admit`, and either receipt the refusal or hold a reservation for the whole job.

    Yields the decision. On a refusal the caller skips the job and the deferral is already
    receipted; on admission the job runs inside `reservation`, so the NEXT asker counts it.
    Asking without reserving is half a governor: sim-runner's admission sums reservations,
    and until a gate held one it summed a ledger nobody wrote.

    A governor that raises defers, never admits -- the same fail-closed direction as
    `sim_runner.cycle_admission`.
    """
    try:
        decision = admit(job_class, reservations_path=reservations_path, **admit_kwargs)
    except Exception as exc:  # noqa: BLE001 -- an unreadable governor is a deferral, not a pass
        decision = {"job_class": job_class, "admitted": False,
                    "reason": f"the admission check raised {type(exc).__name__}: {exc}"}
    if not decision["admitted"]:
        if log is not None:
            log(f"DEFERRED {job_class} -- {decision['reason']}")
        record_deferral(decision, deferral_log_path)
        yield decision
        return
    with reservation(job_class, reservations_path=reservations_path):
        yield decision


@contextlib.contextmanager
def _ledger_lock(reservations_path: Path | None = None):
    """Exclusive lock on the box ledger, so ASKING and RESERVING are one step: two queued jobs
    must not both be admitted between one's `admit` and its write."""
    import fcntl
    path = (reservations_path or RESERVATIONS_PATH).with_suffix(".lock")
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a+") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(fh, fcntl.LOCK_UN)


class QueueTimeout(RuntimeError):
    """The box never had room for the job inside its deadline. Carries the last refusal."""


#: How often a queued job asks again. Not a domain constant: it bounds how stale a queue is.
QUEUE_POLL_SECONDS = 30


@contextlib.contextmanager
def queued(job_class: str, weight_mb=None, log=None, deadline_seconds: float = 4 * 3600,
           poll_seconds: float = QUEUE_POLL_SECONDS, sleep=None, reservations_path: Path | None = None,
           deferral_log_path: Path | None = None, **admit_kwargs):
    """Wait until the box has room for this job, then hold its reservation until it ends.

    THE ONE DOOR EVERY HEAVY THING GOES THROUGH: commit gates, direct runs and the sim-runner ask
    this; long jobs ask `launch_long_job.co_residence`, which counts the same ledger. A refusal
    QUEUES (asks again every `poll_seconds`) instead of co-running, which is what killed the
    2026-10-08 vulnerability landing beside three lanes' 10-11 GB of runs.

    Already inside an admitted holder (`ADMITTED_ENV` set), it neither waits nor reserves: the
    holder's reservation already counts this work. Past the deadline it raises `QueueTimeout`
    with the last refusal's reason, so a job that never fits says why rather than waiting forever.
    """
    if os.environ.get(ADMITTED_ENV):
        yield {"admitted": True, "reason": f"inside {os.environ[ADMITTED_ENV]}, already counted"}
        return
    import time as _time
    sleep = sleep or _time.sleep
    start = _time.monotonic()
    first = True
    while True:
        with _ledger_lock(reservations_path):
            decision = admit(job_class, weight_mb=weight_mb, reservations_path=reservations_path,
                             **admit_kwargs)
            if decision["admitted"]:
                holder = _reserve(job_class, weight_mb, reservations_path)
                break
        if first:
            if log is not None:
                log(f"QUEUED {job_class} -- {decision['reason']}")
            record_deferral({**decision, "queued": True}, deferral_log_path)
            first = False
        if _time.monotonic() - start >= deadline_seconds:
            raise QueueTimeout(f"{job_class} waited {deadline_seconds:.0f}s for room and never "
                               f"fitted: {decision['reason']}")
        sleep(poll_seconds)
    previous = os.environ.get(ADMITTED_ENV)
    os.environ[ADMITTED_ENV] = job_class
    try:
        yield decision
    finally:
        with _ledger_lock(reservations_path):
            _release(holder, reservations_path)
        if previous is None:
            os.environ.pop(ADMITTED_ENV, None)
        else:
            os.environ[ADMITTED_ENV] = previous


@contextlib.contextmanager
def reservation(job_class: str, weight_mb=None, reservations_path: Path | None = None,
                proc_root: Path | None = None):
    """Hold a declared claim for the duration of a heavy job.

    Released on the way out INCLUDING on exception -- but the (pid, starttime) reaping above
    is what actually guarantees release, because a hard kill (the exact case this exists for)
    never runs a finally block. The context manager is the tidy path, not the safety net.
    """
    with _ledger_lock(reservations_path):
        holder = _reserve(job_class, weight_mb, reservations_path, proc_root)
    try:
        yield holder
    finally:
        with _ledger_lock(reservations_path):
            _release(holder, reservations_path, proc_root)


def _reserve(job_class: str, weight_mb=None, reservations_path: Path | None = None,
             proc_root: Path | None = None) -> dict:
    path = reservations_path or RESERVATIONS_PATH
    pid = os.getpid()
    holder = {
        "pid": pid,
        "starttime": _proc_starttime(pid, proc_root),
        "job_class": job_class,
        "weight_mb": weight_for(job_class, weight_mb),
        "since": _now_iso(),
    }
    rows = [r for r in (_read_json(path, []) or []) if isinstance(r, dict)]
    rows = [r for r in rows if _is_live(r, proc_root)]
    rows.append(holder)
    _write_json(path, rows)
    return holder


def _release(holder: dict, reservations_path: Path | None = None, proc_root: Path | None = None):
    path = reservations_path or RESERVATIONS_PATH
    rows = [r for r in (_read_json(path, []) or []) if isinstance(r, dict)]
    rows = [r for r in rows
            if _is_live(r, proc_root) and not (r.get("pid") == holder["pid"]
                                               and r.get("since") == holder["since"])]
    _write_json(path, rows)


# --------------------------------------------------------------------------------------
# Reporting -- one line for a surface that is read.
# --------------------------------------------------------------------------------------

def note_line(episode_path: Path | None = None) -> str:
    """One line for the daily self-note. RED when unmeasured -- never a fabricated green."""
    ep = _read_json(episode_path or EPISODE_PATH, {}) or {}
    obs = ep.get("last_sample") or {}
    available = obs.get("available_mb")
    if available is None:
        return ("🔴 RED — memory headroom unmeasured: no usable /proc/meminfo sample recorded "
                "(fail-closed, not a green — R15). One appears at the next watchdog sample.")
    state = ep.get("state", "unknown")
    victims = ep.get("victims")
    total = obs.get("total_mb")
    icon = "🔴" if state == "pressure" else ("⚠️" if state == "unknown" else "✅")
    victim_fragment = (
        f", {victims} oom victim(s) in this episode" if victims
        else (", victims unknown" if victims is None else "")
    )
    return (f"{icon} memory headroom: **{available:.0f} MB** available of "
            f"{total:.0f} MB total (band {state}, worst "
            f"{ep.get('worst_available_mb')} MB since {ep.get('since')}{victim_fragment}). "
            "R12: a DIAGNOSTIC — defer or add memory, never trim verification depth.")


def alarm_line(result: dict) -> str | None:
    """The NTFY payload for a TRANSITION, or None. R5: unchanged status is never announced."""
    transition = result.get("transition")
    if transition is None:
        return None
    ep = result.get("episode", {})
    obs = result.get("sample", {})
    if transition == "entered":
        return (f"MEMORY PRESSURE: {obs.get('available_mb')} MB available of "
                f"{obs.get('total_mb')} MB (floor {PRESSURE_FLOOR_MB} MB), PSI some/60s "
                f"{obs.get('psi_some_avg60')}, lifetime oom kills {obs.get('oom_kills_total')}. "
                "Heavy jobs will be deferred until recovery.")
    recovered = ep.get("recovered_from", {})
    return (f"MEMORY RECOVERED: {obs.get('available_mb')} MB available. Episode began "
            f"{recovered.get('since')}, worst {recovered.get('worst_available_mb')} MB, "
            f"victims {recovered.get('victims')}.")
