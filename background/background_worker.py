#!/usr/bin/env python3
"""
Synthetic Enterprise — Background Worker
Runs autonomously using local Qwen only (no frontier tokens).
Checks docs/instructions/background-tasks.md for queued tasks.
Respects UK peak electricity hours: pauses between 16:00-19:00 GMT daily.
Logs all activity to docs/observability/background-worker-log.md
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

PEAK_START = 16  # 4pm GMT
PEAK_END = 19    # 7pm GMT
CHECK_INTERVAL_MINUTES = 30
TASKS_FILE = Path("docs/instructions/background-tasks.md")
# Mirrors background.process_run_complete.EXIT_LOCK_SKIPPED. Duplicated as a
# literal (rather than imported at module scope) because importing the
# publish pipeline at worker import time drags in the whole reporting stack;
# tests/background/test_background_worker.py pins the two values equal so the
# mirror can never silently drift back into "a skip looks like a success".
EXIT_LOCK_SKIPPED = 75
LOG_FILE = Path("docs/observability/background-worker-log.md")
OLLAMA_MODEL = "qwen3:14b"

def is_peak_hours():
    """Return True if current GMT time is between 16:00 and 19:00."""
    now_gmt = datetime.now(timezone.utc)
    return PEAK_START <= now_gmt.hour < PEAK_END

def log(message: str):
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    entry = f"\n- [{timestamp}] {message}"
    with open(LOG_FILE, "a") as f:
        f.write(entry)
    print(entry)

def run_ollama_task(prompt: str, task_name: str) -> str:
    """Run a task via local Ollama. Returns the model output."""
    log(f"Starting task: {task_name}")
    result = subprocess.run(
        ["ollama", "run", OLLAMA_MODEL, prompt],
        capture_output=True, text=True, timeout=300
    )
    if result.returncode != 0:
        log(f"Task failed: {task_name} — {result.stderr[:200]}")
        return ""
    log(f"Task complete: {task_name}")
    return result.stdout

STAGING_DIR = Path("docs/staging")
DONE_DIR = STAGING_DIR / "done"

# ── OPS_run_marker_sweep_livelock (2026-08-03) ──────────────────────────────
# PURPOSE: this sweep is the safety net for a run_complete marker that
# process_run_complete.py's own lock-skip path left untouched (see this
# function's docstring below for the producer-side half of the coupling).
# Before this fix the sweep re-attempted EVERY leftover marker EVERY cycle,
# each attempt independently racing sim_runner.py (or any earlier marker in
# the SAME sweep) for the same non-blocking flock -- a race it could only
# ever LOSE while the lock holder was mid-pipeline, since the lock holder
# takes it inline while publishing the marker it just wrote and never
# releases it "for" a sweeper. Result: 404 markers, every one of ~thousands
# of cycles, EXIT_LOCK_SKIPPED, forever -- a livelock indistinguishable in
# the log from a slow-but-working queue.
#
# GUARANTEE / WHY THIS CAN NOW WIN: the sweep acquires process_run_complete's
# run lock ITSELF, ONCE, for the whole batch -- not once per marker -- and
# tells every per-marker subprocess it spawns (via LOCK_ALREADY_HELD_ENV)
# to skip its own doomed re-acquisition and process directly. A marker can
# now only fail to be attempted for a real reason (the lock is genuinely
# busy with something else RIGHT NOW), never because the sweep's own
# children were racing each other or their own parent.
#
# BOUNDED BATCH: holding the run lock indefinitely would starve
# sim_runner.py's own live publish (its ~9-min cadence is the thing that
# matters most). MARKER_SWEEP_TIME_BUDGET_SECONDS caps how long one sweep
# call keeps draining before yielding the lock back for the next cycle --
# the backlog drains over successive cycles, never in one unbounded pass.
# In practice this is a safety bound, not the common case: process_run_
# complete.py's own change-detection gate makes every marker after the
# first "real" publish in a batch a cheap archive-only skip.
MARKER_SWEEP_TIME_BUDGET_SECONDS = 600  # 10 min/cycle; leaves headroom in the 30-min worker loop
# The env var contract with process_run_complete.py::main() -- see that
# module's own LOCK_ALREADY_HELD_ENV constant and docstring.
LOCK_ALREADY_HELD_ENV = "SE_RUN_LOCK_ALREADY_HELD"

# ── Zero-progress retry-loop alarm (R10 class closure) ──────────────────────
# A retry loop that has attempted work for thousands of cycles and DRAINED
# ZERO of it is an ALARM, not a log line -- it is structurally
# indistinguishable, in a log of "Lock-skipped ... will retry next cycle",
# from a queue that is merely slow. This is a GENERAL primitive: any retry
# loop can report (markers_found, markers_drained) for its own cycle and get
# the same zero-progress detection, independent of what "a marker" even
# means. It is deliberately NOT derived from the sweep's own decision to
# skip/attempt (that would be a tautology, R15) -- the caller passes counts
# it observed directly from real subprocess return codes.
ZERO_PROGRESS_STATE_FILE = Path("docs/observability/.marker_sweep_zero_progress_state.json")
ZERO_PROGRESS_ALARM_THRESHOLD = 5        # consecutive cycles: markers pending, zero drained
ZERO_PROGRESS_COOLDOWN_SECONDS = 60 * 60  # re-arm: at most one alert/hour while it stays stuck
ZERO_PROGRESS_TRANSITION_KEY = "marker_sweep_zero_progress"


def _read_zero_progress_state():
    """FAIL-CLOSED read (R15 fail-silent doctrine, same shape as
    process_run_complete._read_publish_gate_state): an unreadable/corrupt
    state file must NOT be treated as a fresh, healthy zero-streak -- that
    would let a disk hiccup silently erase a real in-progress alarm streak
    right before it reaches threshold. It reports state_unavailable=True so
    the caller can treat "the checker can't see its own history" as itself
    alarm-worthy (an unavailable check is a FAILED check)."""
    if not ZERO_PROGRESS_STATE_FILE.exists():
        return {"consecutive_zero_progress": 0, "alerted_at": None, "state_unavailable": False}
    try:
        st = json.loads(ZERO_PROGRESS_STATE_FILE.read_text())
        if not isinstance(st, dict):
            raise ValueError("zero-progress state is not an object")
        st.setdefault("consecutive_zero_progress", 0)
        st.setdefault("alerted_at", None)
        st["state_unavailable"] = False
        return st
    except (json.JSONDecodeError, OSError, ValueError):
        return {"consecutive_zero_progress": 0, "alerted_at": None, "state_unavailable": True}


def _write_zero_progress_state(state):
    out = {
        "consecutive_zero_progress": state.get("consecutive_zero_progress", 0),
        "alerted_at": state.get("alerted_at"),
    }
    ZERO_PROGRESS_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    ZERO_PROGRESS_STATE_FILE.write_text(json.dumps(out, sort_keys=True))


def _record_sweep_progress(*, markers_found, markers_drained, now=None, notify_fn=None):
    """The zero-progress-retry-loop ALARM itself (R10 class closure for
    OPS_run_marker_sweep_livelock). `markers_found`/`markers_drained` MUST be
    counts the caller observed directly from real per-marker outcomes this
    cycle -- never re-derived from this function's own state file (that
    would make the checked value depend on the same source it checks, R15's
    TAUTOLOGY pattern).

    Semantics:
      - markers_found == 0: nothing to drain -- not a stuck retry loop.
        Reset the streak; if a persistent-zero alarm was open, log its
        resolution (a real release trigger, R11 no-orphan-transitions: the
        backlog being genuinely empty IS the thing that resolves it).
      - markers_found > 0 and markers_drained > 0: real progress this cycle,
        even if the backlog isn't fully cleared. Reset the streak; page a
        recovery notice if a persistent-zero alarm had previously fired.
      - markers_found > 0 and markers_drained == 0: one more zero-progress
        cycle. After ZERO_PROGRESS_ALARM_THRESHOLD consecutive such cycles,
        page once (re-armed by a cooldown so a persistent livelock can't
        spam every cycle).
    Fully defensive: a monitoring failure here must never break the sweep
    that calls it -- matches every other check in this codebase's alarm
    primitives (record_publish_gate_failure, run_operational_layer_signal)."""
    try:
        now = float(now) if now is not None else time.time()
        if notify_fn is None:
            from background.notify import notify as notify_fn
        state = _read_zero_progress_state()
        unavailable = bool(state.get("state_unavailable"))
        streak = int(state.get("consecutive_zero_progress") or 0)
        last_alert = state.get("alerted_at")

        if not markers_found:
            was_alarmed = streak >= ZERO_PROGRESS_ALARM_THRESHOLD
            _write_zero_progress_state({"consecutive_zero_progress": 0, "alerted_at": None})
            if was_alarmed:
                log("Zero-progress retry-loop alarm cleared -- marker backlog is empty.")
            return {"streak": 0, "fired": False}

        if markers_drained:
            was_alarmed = streak >= ZERO_PROGRESS_ALARM_THRESHOLD
            _write_zero_progress_state({"consecutive_zero_progress": 0, "alerted_at": None})
            if was_alarmed:
                notify_fn(
                    "[MARKER SWEEP RECOVERED] process_leftover_run_markers drained {} of {} "
                    "backlogged run_complete marker(s) this cycle, after {} consecutive "
                    "zero-progress cycles -- the retry loop is making real progress again."
                    .format(markers_drained, markers_found, streak),
                    kind="real_alarm", transition_key=ZERO_PROGRESS_TRANSITION_KEY, state="GREEN",
                )
                log("Zero-progress retry-loop alarm RECOVERED -- paged.")
            return {"streak": 0, "fired": False}

        # markers_found > 0 and markers_drained == 0: one more zero-progress cycle.
        streak += 1
        threshold_met = unavailable or streak >= ZERO_PROGRESS_ALARM_THRESHOLD
        armed = last_alert is None or (now - float(last_alert)) >= ZERO_PROGRESS_COOLDOWN_SECONDS
        fired = False
        alerted_at = last_alert
        if threshold_met and armed:
            reason = ("its own state file is unreadable (fail-closed alarm)" if unavailable
                      else "{} consecutive cycles with markers pending and zero drained".format(streak))
            notify_fn(
                "[MARKER SWEEP ZERO PROGRESS] process_leftover_run_markers has made NO "
                "progress -- {} ({} marker(s) currently pending in docs/staging/). A retry "
                "loop that has never succeeded is a livelock, not a slow queue: check whether "
                "the process_run_complete run lock is held by a stuck process."
                .format(reason, markers_found),
                kind="real_alarm", transition_key=ZERO_PROGRESS_TRANSITION_KEY, state="RED",
                re_escalate_after=ZERO_PROGRESS_COOLDOWN_SECONDS,
            )
            alerted_at = now
            fired = True
            log("Zero-progress retry-loop alarm FIRED ({} consecutive cycles).".format(streak))
        else:
            log("Sweep zero-progress streak = {} (threshold {}) -- {}".format(
                streak, ZERO_PROGRESS_ALARM_THRESHOLD,
                "below threshold" if not threshold_met else "armed/cooldown"))
        _write_zero_progress_state({"consecutive_zero_progress": streak, "alerted_at": alerted_at})
        return {"streak": streak, "fired": fired}
    except Exception as exc:
        log("Zero-progress alarm error (swallowed): {}".format(exc))
        return {"streak": 0, "fired": False, "error": str(exc)}


def process_leftover_run_markers():
    """Process any run_complete_*.md markers that process_run_complete.py left behind.

    UNDOCUMENTED COUPLING, now documented (2026-07-13, director-flagged): this
    function is the ENTIRE real safety net for a marker that
    `background/sim_runner.py` itself skipped -- sim_runner.py only ever
    passes process_run_complete.py the ONE marker it just wrote each
    iteration, and process_run_complete.py's own lock-skip path returns
    EXIT_LOCK_SKIPPED (75) without touching the marker, so a marker
    left behind because another instance was already running is NEVER
    retried by sim_runner.py itself. This function's own unconditional glob
    of every `run_complete_*.md` still in staging/ -- called at the TOP of
    background_worker.py's main loop, every cycle, "regardless of peak
    hours" per that call site's own comment -- is what actually keeps the
    promise the skip-path's own log line makes ("will be picked up... next
    cycle"). If this function is ever removed, disabled, or made
    conditional, a lock-skipped marker becomes permanently orphaned with no
    other mechanism to rescue it -- see tests/background/
    test_background_worker.py's own test asserting this glob is genuinely
    unconditional (not gated behind queue state, peak-hours, or any other
    check) for the regression guard on this exact property.

    LOCK-ONCE-PER-SWEEP (2026-08-03, OPS_run_marker_sweep_livelock): the
    unconditional glob above is unchanged, but HOW leftover markers get
    attempted changed structurally -- see the block comment above this
    function for the full purpose/guarantee/why. In short: this function now
    wins process_run_complete's run lock itself, ONCE, for the whole batch
    (bounded by MARKER_SWEEP_TIME_BUDGET_SECONDS), instead of each per-marker
    subprocess independently -- and always losing -- the same race. If the
    lock can't be won right now, this makes ZERO per-marker attempts and logs
    ONE line, closing the log-storm symptom as a side effect of closing the
    livelock itself. Every cycle's (found, drained) outcome feeds the
    zero-progress alarm above."""
    markers = sorted(STAGING_DIR.glob("run_complete_*.md"))
    if not markers:
        _record_sweep_progress(markers_found=0, markers_drained=0)
        return

    from background import process_run_complete as prc
    with prc._run_lock() as acquired:
        if not acquired:
            log(f"Run lock busy (another instance is actively publishing) -- "
                f"{len(markers)} leftover marker(s) still pending, making ZERO "
                f"per-marker attempts this cycle (will retry next cycle)")
            _record_sweep_progress(markers_found=len(markers), markers_drained=0)
            return

        log(f"Won the run lock -- draining leftover marker backlog "
            f"({len(markers)} found, budget {MARKER_SWEEP_TIME_BUDGET_SECONDS}s)")
        processor = Path(__file__).parent / "process_run_complete.py"
        drained = 0
        start = time.monotonic()
        for marker in markers:
            if time.monotonic() - start > MARKER_SWEEP_TIME_BUDGET_SECONDS:
                log(f"Sweep time budget exhausted -- {len(markers) - drained} marker(s) "
                    f"left for next cycle")
                break
            env = dict(os.environ)
            env[LOCK_ALREADY_HELD_ENV] = "1"
            try:
                result = subprocess.run(
                    [sys.executable, str(processor), str(marker)],
                    cwd=str(Path(__file__).resolve().parent.parent),
                    env=env,
                    timeout=900,
                )
            except Exception as exc:
                # A per-marker crash/timeout must not abort the rest of the
                # batch -- log and move on to the next marker, same
                # resilience the loop already gave a real rc!=0.
                log(f"Exception processing {marker.name}: {exc} -- will retry next cycle")
                continue
            if result.returncode == EXIT_LOCK_SKIPPED:
                # Should be structurally impossible now (this sweep holds the
                # lock for every child's whole lifetime) -- if it ever
                # happens, the env-var contract broke, not that the race was
                # lost again. Treated exactly as before: untouched, no false
                # claim of success.
                log(f"Lock-skipped {marker.name} (unexpected under the sweep's own held "
                    f"lock -- check LOCK_ALREADY_HELD_ENV wiring) -- still pending, will "
                    f"retry next cycle")
            elif result.returncode == 0:
                log(f"Processed {marker.name}")
                drained += 1
            else:
                log(f"Failed to process {marker.name} (rc={result.returncode}) -- will retry next cycle")
            # H15_publish_gate_failure_alert: feed every processing outcome into the
            # publish-gate wedge detector. This sweep is the recurring caller that
            # actually manifests a silent wedge -- process_run_complete returns
            # rc!=0 every cycle (test-fail / OOM SIGKILL rc=-9 / report-regen fail)
            # and leaves the marker in staging, so N consecutive failures here == a
            # stalled pipeline that must raise ONE [ACTION NEEDED] alert.
            _record_publish_gate_outcome(marker, result.returncode)
        log(f"Sweep drained {drained}/{len(markers)} marker(s) this cycle")
        _record_sweep_progress(markers_found=len(markers), markers_drained=drained)


def _record_publish_gate_outcome(marker, rc):
    """H15: route a run-complete processing return code into the publish-gate
    failure detector (background/process_run_complete.py). Defensive by
    construction -- a monitoring failure must never break the marker sweep or
    the loop that calls it.

    THREE outcomes, not two (fail-open closed 2026-07-29). A lock-skip
    (EXIT_LOCK_SKIPPED) means this sweep did NOT publish the marker -- it is
    evidence of NOTHING about the gate's health, so it records NEITHER a
    success NOR a failure and leaves the streak exactly as it found it.
    Recording it as a success (the old behaviour, when the skip path returned
    0) actively DISARMED the detector: `record_publish_gate_success` clears the
    failure list, re-arms the alarm, and auto-resolves the open [ACTION NEEDED]
    item with "a run published cleanly" -- for a marker nobody published.
    Observed 2026-07-29 16:53Z: both backed-up markers recorded successes one
    minute before the lock holder itself failed the gate at 16:54Z, wiping the
    streak that was supposed to raise the alert.

    DELEGATES (2026-08-03): the three-outcome logic now lives ONCE in
    `process_run_complete.record_publish_gate_outcome` so that EVERY publish
    path feeds the same detector. This sweep was the only caller, which left
    the detector blind to sim_runner.py -- the path that actually publishes in
    the steady state -- for ~4 days. This wrapper stays because it is the name
    tests/background/test_background_worker.py pins."""
    try:
        from background import process_run_complete as prc
        prc.record_publish_gate_outcome(marker, rc)
    except Exception as exc:
        log(f"publish-gate outcome recording skipped for {marker.name}: {exc}")


def main():
    from background.agent_status import update_agent_status
    log("Background worker started")
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    update_agent_status(
        "background-worker", status="idle",
        last_action="Worker started",
        role="Runs background automation tasks via local Qwen; respects 16-19 UTC peak hours",
        produces="docs/observability/background-worker-log.md",
    )

    while True:
        # Always check for leftover run_complete markers first, regardless of peak hours
        try:
            process_leftover_run_markers()
        except Exception as exc:
            log(f"process_leftover_run_markers error: {exc}")

        if is_peak_hours():
            now = datetime.now(timezone.utc)
            log(f"Peak hours (16:00-19:00 GMT) — pausing. Current time: {now.strftime('%H:%M UTC')}")
            update_agent_status("background-worker", status="idle", last_action=f"Peak hours pause — {now.strftime('%H:%M UTC')}", is_heartbeat=True)
            time.sleep(60 * 15)  # check every 15min during peak
            continue

        # Read task queue
        if not TASKS_FILE.exists():
            log("No background-tasks.md found — sleeping")
            update_agent_status("background-worker", status="idle", last_action="No task queue found — sleeping", is_heartbeat=True)
            time.sleep(60 * CHECK_INTERVAL_MINUTES)
            continue

        tasks_content = TASKS_FILE.read_text()
        if "## QUEUED" not in tasks_content:
            log("No queued tasks — sleeping")
            update_agent_status("background-worker", status="idle", last_action="No queued tasks — sleeping", is_heartbeat=True)
            time.sleep(60 * CHECK_INTERVAL_MINUTES)
            continue

        log("Found queued tasks — beginning execution")
        update_agent_status("background-worker", status="working", last_action="Executing queued tasks")
        # Tasks are executed by the individual task scripts (see below)
        # This worker just triggers them and logs completion
        exec(open("background/run_queued_tasks.py").read(), globals())
        update_agent_status("background-worker", status="idle", last_action="Task batch complete")
        time.sleep(60 * CHECK_INTERVAL_MINUTES)

if __name__ == "__main__":
    main()
