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
RESERVATIONS_PATH = OBS_DIR / ".heavy_job_reservations.json"
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
    # tools.run_annual_report. RE-DERIVED 2026-08-24 from systemd's own record (see
    # CLASS_UNITS and weight_drift below): fourteen OOM kills of sim-runner.service in one
    # day, peaks 3.6G climbing to 13.5G, max 13,824 MB. The previous entry here said 6,144 MB
    # "observed 5,548 MB RSS 2026-08-10" -- true when written and 2.2x short fourteen days
    # later, because the book this job holds in memory grew under it. Budgeted AT the observed
    # peak, like subject_cost: padding it would be the guess this table's own comment forbids,
    # and `weight_drift` is the mechanism that keeps it current instead.
    "sim_run": 13824,
    # tools.measure_publish_gate_subject_cost, oom-killed at 9,648 MB anon-rss 2026-08-10.
    # Budgeted at its observed peak: it is the largest single resident this project runs.
    "subject_cost": 9728,
    # scoped publish-gate pytest, observed 854 MB; budgeted with room for suite growth.
    "publish_gate": 1536,
    # tools.enumerate_publish_gate_reds -- same suite, no -x, so it runs to the end and holds
    # more; observed 577 MB and still climbing at sample time.
    "census": 1536,
}

# Which systemd unit's record re-derives which class weight. Only classes that RUN AS A UNIT
# can appear -- the others are started ad hoc and leave no journal to check against, so they
# have no automatic re-derivation and stay hand-measured.
CLASS_UNITS = {"sim_run": "sim-runner.service"}

#: How far back weight_drift asks. Wider than oom_watch's default so a weekly growth trend is
#: visible rather than only the current episode.
DRIFT_WINDOW = "-24h"


def weight_drift(job_class: str, since: str = DRIFT_WINDOW, journal_reader=None,
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
      * True  -- the journal answered and the observed peak EXCEEDS the declared weight;
      * False -- the journal answered and the weight still covers what was observed;
      * None  -- the journal could not be read, or the class has no unit. An unavailable
                 check is a FAILED check (R15), never a clean one, so None must not be
                 rendered as "no drift" by any caller.
    """
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
    verdict["drifted"] = peak > declared
    if verdict["drifted"]:
        verdict["detail"] = (
            f"{job_class!r} is declared at {declared:.0f} MB but {unit} peaked at "
            f"{peak:.0f} MB across {len(peaks)} run(s) in {since} -- the governor is sizing "
            f"this job at {peak / declared:.1f}x under its measured footprint, which admits "
            f"it into memory that is not there. Re-derive CLASS_WEIGHTS_MB[{job_class!r}]"
        )
    else:
        verdict["detail"] = (
            f"{job_class!r} declared at {declared:.0f} MB still covers the {peak:.0f} MB "
            f"peak observed across {len(peaks)} run(s) in {since}"
        )
    return verdict


def weight_drift_alarm(verdicts) -> str | None:
    """The NTFY/log payload naming every drifted or unverifiable weight, or None if all clean.

    An UNREADABLE verdict is reported, not swallowed: the whole failure mode is a weight
    nobody has checked lately, and "we could not check" is that same state.
    """
    drifted = [v for v in verdicts if v.get("drifted") is True]
    unknown = [v for v in verdicts if v.get("drifted") is None]
    if not drifted and not unknown:
        return None
    parts = []
    if drifted:
        parts.append(
            "DECLARED JOB WEIGHT OUTGROWN: "
            + "; ".join(v["detail"] for v in drifted)
            + ". Until re-derived, admit() is fail-open for these classes."
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


def admit(job_class: str, weight_mb=None, reservations_path: Path | None = None,
          proc_root: Path | None = None, **sample_kwargs) -> dict:
    """May a heavy job of this class start right now?

    Returns {admitted, reason, ...}. BOTH conditions must hold -- see the module docstring on
    why either alone is unsound. Every denial names which condition failed and with what
    numbers, because a deferral nobody can diagnose is just a stall.
    """
    obs = sample(**sample_kwargs)
    weight = weight_for(job_class, weight_mb)
    committed = committed_mb(reservations_path, proc_root)
    total = obs["total_mb"]
    available = obs["available_mb"]
    budget = (total - RESERVE_FOR_UNDECLARED_MB) if total is not None else None

    decision = {
        "timestamp": obs["timestamp"],
        "job_class": job_class,
        "weight_mb": weight,
        "committed_mb": round(committed, 1),
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
        decision["reason"] = (
            f"budget exhausted: {committed:.0f} MB already declared + {weight:.0f} MB "
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
def reservation(job_class: str, weight_mb=None, reservations_path: Path | None = None,
                proc_root: Path | None = None):
    """Hold a declared claim for the duration of a heavy job.

    Released on the way out INCLUDING on exception -- but the (pid, starttime) reaping above
    is what actually guarantees release, because a hard kill (the exact case this exists for)
    never runs a finally block. The context manager is the tidy path, not the safety net.
    """
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
    try:
        yield holder
    finally:
        rows = [r for r in (_read_json(path, []) or []) if isinstance(r, dict)]
        rows = [r for r in rows
                if _is_live(r, proc_root) and not (r.get("pid") == pid
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
