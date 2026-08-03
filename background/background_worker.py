#!/usr/bin/env python3
"""
Synthetic Enterprise — Background Worker
Runs autonomously using local Qwen only (no frontier tokens).
Checks docs/instructions/background-tasks.md for queued tasks.
Respects UK peak electricity hours: pauses between 16:00-19:00 GMT daily.
Logs all activity to docs/observability/background-worker-log.md
"""

import json
import re
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

# `run_complete_YYYYMMDDTHHMMSSZ.md` -- fixed width, so a lexicographic sort of
# the names IS a chronological sort. A marker whose name does NOT match this is
# NOT provably older than any other, so it is never superseded (fail-CLOSED:
# an unrecognised marker gets its own publish attempt rather than a silent
# archive).
MARKER_NAME_RE = re.compile(r"^run_complete_(\d{8}T\d{6}Z)\.md$")

# ── Zero-progress alarm (R15 FAIL-SILENT closure, 2026-08-03) ──────────────────
# The sweep's own health state. See _record_sweep_cycle() for the full purpose /
# guarantees / fit statement.
SWEEP_STATE_FILE = Path("docs/observability/.run_marker_sweep_state.json")
# Cycles of "backlog present AND not one marker drained" before the retry loop is
# declared STUCK. 3 -- the sweep runs at the top of every worker loop (>=30 min
# apart when idle), so three consecutive dead cycles is >=1h of a retry loop that
# has moved nothing, which no transient lock contention explains (a lock-skipped
# marker is superseded and archived on the very next cycle).
ZERO_PROGRESS_ALARM_CYCLES = 3
SWEEP_ALARM_KEY = "run_marker_sweep_zero_progress"
# While genuinely stuck, re-page at most this often (notify()'s documented
# re_escalate_after pattern). R5 still holds: an UNCHANGED status never re-pages
# inside the window, and recovery is its own single transition.
SWEEP_ALARM_RE_ESCALATE_S = 6 * 60 * 60


def process_leftover_run_markers():
    """Process any run_complete_*.md markers that process_run_complete.py left behind.

    SUPERSEDE-AND-ARCHIVE (2026-08-03, atom OPS_run_marker_sweep_livelock).
    This sweep used to attempt EVERY marker in staging/, oldest-first, every
    cycle. Measured on the live tree 2026-08-03: 406 markers spanning five
    days; worker log 1668 "Lock-skipped" / 571 "Failed to process" / 300
    "Processed"; backlog GROWING (382 at 23:48Z -> 405 at 04:12Z) because
    sim_runner.py mints a marker every ~9 min while one publish costs ~8 min.
    A per-marker retry loop can never win that race.

    The three "Processed" hundreds were the more damaging half, not the
    healthy one: `process_run_complete._process()` regenerates
    ANNUAL_REPORT.md / LATEST.md / dashboard.json FROM THE MARKER'S OWN
    json_path, so publishing a five-day-old marker overwrites the live
    business surfaces with five-day-old figures.

    So markers are SUPERSEDED, not queued: only the newest reflects current
    state, every marker is an idempotent "regenerate the surfaces" request,
    and the older ones are archived to done/ WITH a recorded superseded-by
    reason (`process_run_complete.supersede_run_markers`) -- archiving, never
    deletion. Each cycle therefore ends with at most ONE unresolved marker
    (plus any name-unparseable ones, which are never superseded), so the
    backlog is O(1) instead of unbounded.

    Why NOT a blocking/backoff lock acquire (the other candidate fix): the run
    lock is deliberately non-blocking (`process_run_complete._run_lock`) after
    two concurrent full pipelines were observed on 2026-07-06, and a sweep that
    waited would park background_worker for up to ~10 min inside the lock
    holder's window. With supersede-archiving a lock-skip costs nothing at all
    -- next cycle the skipped marker is itself superseded by a fresher one and
    the fresher one is published -- so blocking would buy latency for no gain.

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
    cycle"). The glob stays unconditional; what changed is that a marker's
    terminal state may now be ARCHIVED-AS-SUPERSEDED rather than published.
    Every marker still reaches a terminal state every cycle -- a strictly
    stronger property than "every marker is attempted", which the backlog
    above proves was never actually delivered. If this function is ever
    removed, disabled, or made conditional, a lock-skipped marker becomes
    permanently orphaned with no other mechanism to rescue it -- see tests/
    background/test_background_worker.py and tests/background/
    test_run_marker_sweep.py for the regression guards on both properties."""
    markers = sorted(STAGING_DIR.glob("run_complete_*.md"))
    if not markers:
        _record_sweep_cycle(before=set(), oldest=None)
        return
    before = {m.name for m in markers}
    log(f"Found {len(markers)} leftover run_complete marker(s) — sweeping")

    dated = [m for m in markers if MARKER_NAME_RE.match(m.name)]
    unparseable = [m for m in markers if not MARKER_NAME_RE.match(m.name)]
    newest = dated[-1] if dated else None
    superseded = dated[:-1] if dated else []

    if superseded:
        archived = _supersede_markers(superseded, newest)
        log("Superseded {} of {} marker(s) — archived to staging/done/ with a "
            "recorded superseded-by={} reason (a run_complete marker is an "
            "idempotent 'regenerate the surfaces' request; publishing an older "
            "one would republish STALE figures)".format(
                len(archived), len(superseded), newest.name))
        if len(archived) != len(superseded):
            log("WARNING: {} superseded marker(s) could NOT be archived and were "
                "left in staging (never deleted)".format(len(superseded) - len(archived)))

    # The newest marker is the only one worth publishing. Name-unparseable
    # markers are never provably superseded, so each still gets its own attempt.
    to_process = ([newest] if newest is not None else []) + unparseable

    processor = Path(__file__).parent / "process_run_complete.py"
    for marker in to_process:
        result = subprocess.run(
            [sys.executable, str(processor), str(marker)],
            cwd=str(Path(__file__).resolve().parent.parent),
            timeout=900,
        )
        if result.returncode == EXIT_LOCK_SKIPPED:
            # NOT processed -- another instance holds the run lock and the
            # marker is untouched. Saying "Processed" here was a false claim in
            # the worker log (it is what a reader sees first when diagnosing a
            # backlog) as well as a false success to the wedge detector.
            log(f"Lock-skipped {marker.name} (another instance holds the run "
                f"lock) — still pending, will retry next cycle")
        elif result.returncode == 0:
            log(f"Processed {marker.name}")
        else:
            log(f"Failed to process {marker.name} (rc={result.returncode}) — will retry next cycle")
        # H15_publish_gate_failure_alert: feed every processing outcome into the
        # publish-gate wedge detector. This sweep is the recurring caller that
        # actually manifests a silent wedge -- process_run_complete returns
        # rc!=0 every cycle (test-fail / OOM SIGKILL rc=-9 / report-regen fail)
        # and leaves the marker in staging, so N consecutive failures here == a
        # stalled pipeline that must raise ONE [ACTION NEEDED] alert.
        _record_publish_gate_outcome(marker, result.returncode)

    _record_sweep_cycle(before=before, oldest=markers[0].name)


def _supersede_markers(superseded, newest):
    """Archive superseded markers via the ONE archive mechanism
    (`process_run_complete.supersede_run_markers` -> `_archive_marker` ->
    staging/done/). Imported lazily for the same reason
    `_record_publish_gate_outcome` does: importing the publish pipeline at
    worker import time drags in the whole reporting stack.

    Returns the list of archived names; [] if the helper itself is
    unavailable -- which then reads as ZERO PROGRESS to the alarm below
    (fail-CLOSED: a superseder that cannot run is a stuck sweep, and the alarm
    is what says so)."""
    try:
        from background import process_run_complete as prc
        return prc.supersede_run_markers(superseded, newest, log_fn=log)
    except Exception as exc:
        log(f"Supersede-archive unavailable ({exc}) — {len(superseded)} marker(s) "
            f"left in staging; the sweep will report zero progress")
        return []


def _read_sweep_state():
    """G-S3: missing / empty / corrupt / wrong-TYPE all read as a FRESH counter,
    never as health. A JSON array parses fine and then `.get` explodes -- caught
    by the malformed-input control, which is the whole point of having one."""
    try:
        state = json.loads(SWEEP_STATE_FILE.read_text())
    except Exception:
        return {}
    return state if isinstance(state, dict) else {}


def _write_sweep_state(state):
    try:
        SWEEP_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        SWEEP_STATE_FILE.write_text(json.dumps(state, sort_keys=True))
    except Exception as exc:
        log(f"Sweep-state write failed: {exc}")


def _record_sweep_cycle(before, oldest):
    """R15 FAIL-SILENT closure: a retry loop that never succeeds must ALARM,
    not log.

    PURPOSE. The defect this closes is not the backlog, it is the VOCABULARY.
    The sweep reported a permanent, total, five-day failure using the words of
    a transient retry -- "will retry next cycle", 2239 times in
    docs/observability/background-worker-log.md, one line per marker per cycle.
    In a log, that is indistinguishable from a healthy queue draining. Nothing
    anywhere measured whether the retrying ever *worked*.

    GUARANTEES.
      G-S1  INDEPENDENT ORACLE (anti-TAUTOLOGY). Progress is NOT the sweep's own
            bookkeeping (return codes, "archived" counts) -- those are exactly
            what was lying. It is re-observed from the filesystem: the set of
            marker names present in staging BEFORE the pass, minus the set
            present AFTER. A marker only counts as drained if it is really gone.
      G-S2  ZERO-PROGRESS IS AN ALARM. `ZERO_PROGRESS_ALARM_CYCLES` consecutive
            passes with a non-empty backlog and NOT ONE marker drained pages the
            director once, with the diagnostic payload (backlog size, oldest
            marker, dead-cycle count, stuck-since).
      G-S3  FAIL-CLOSED, both directions. An empty backlog is not "progress" and
            not "stuck" -- it resets the counter with nothing sent. A state file
            that is missing/empty/corrupt reads as a fresh counter rather than
            as health. If the alarm cannot be DELIVERED, the dead-cycle counter
            is NOT reset and the failure is logged loudly -- an undeliverable
            alarm is a FAILED check, never a silent pass.
      G-S4  NO ORPHAN TRANSITION (R11). Recovery is itself a transition: the
            first pass that drains a marker after the alarm fired clears the
            armed state and sends ONE recovery line.

    FIT. Uses `background.notify.notify`, the ONE notification contract, which
    already owns transition-only suppression (R5/G-N1) and the typed `kind`
    (G-N2) -- no new notification mechanism, and no new hand-rolled `_last_ts`
    dedup of the sort OPS1 exists to delete. State lives in
    docs/observability/ alongside every other daemon's state file."""
    try:
        after = {p.name for p in STAGING_DIR.glob("run_complete_*.md")}
    except Exception as exc:
        # G-S3: if the independent oracle cannot be read, we do NOT get to claim
        # progress. Treat the pass as having drained nothing.
        log(f"Sweep progress re-check failed ({exc}) — recording zero progress")
        after = set(before)

    drained = before - after
    backlog = len(after)
    state = _read_sweep_state()
    try:
        dead_cycles = int(state.get("zero_progress_cycles", 0) or 0)
    except (TypeError, ValueError):
        dead_cycles = 0
    was_alarmed = bool(state.get("alarmed"))
    now = time.time()

    if drained or not before:
        # Real progress, or nothing to do. Neither is a stuck retry loop.
        if was_alarmed and drained:
            _send_sweep_recovery(len(drained), backlog)
        state = {"zero_progress_cycles": 0, "last_progress_ts": now,
                 "last_backlog": backlog, "alarmed": False,
                 "stuck_since": None}
        _write_sweep_state(state)
        return state

    dead_cycles += 1
    stuck_since = state.get("stuck_since") or now
    state = {"zero_progress_cycles": dead_cycles,
             "last_progress_ts": state.get("last_progress_ts"),
             "last_backlog": backlog, "alarmed": was_alarmed,
             "stuck_since": stuck_since}

    if dead_cycles >= ZERO_PROGRESS_ALARM_CYCLES:
        stuck_h = max(0.0, (now - float(stuck_since))) / 3600.0
        msg = (
            "[OPS] RUN-MARKER SWEEP STUCK — {} consecutive sweeps drained ZERO of "
            "{} run_complete marker(s) (stuck {:.1f}h; oldest={}). This is a retry "
            "loop that has never succeeded, not a queue: every cycle logs 'will "
            "retry next cycle' and nothing moves. Recommended action: check "
            "docs/observability/background-worker-log.md and the run lock "
            "docs/observability/.process_run_complete.lock — a live holder blocks "
            "every attempt. No action needed from you if the next sweep drains."
        ).format(dead_cycles, backlog, stuck_h, oldest or "unknown")
        delivered = _send_sweep_alarm(msg, dead_cycles, backlog)
        if delivered:
            state["alarmed"] = True
        else:
            # G-S3 FAIL-SILENT: an alarm that could not be delivered has NOT
            # fired. Do not mark it sent, and keep counting so the next cycle
            # tries again.
            state["alarm_delivery_failed_at"] = now
            log("ZERO-PROGRESS ALARM COULD NOT BE DELIVERED — the sweep is stuck "
                "AND the alarm channel is down; both are unreported to the director")

    _write_sweep_state(state)
    return state


def _send_sweep_alarm(msg, dead_cycles, backlog):
    """Page via the ONE notification contract. Returns True iff delivered
    (or legitimately suppressed as an unchanged state, R5). Never raises."""
    try:
        from background.notify import notify, clear_transition
    except Exception as exc:
        log(f"Zero-progress alarm channel unavailable: {exc}")
        return False
    try:
        result = notify(msg, kind="real_alarm",
                        transition_key=SWEEP_ALARM_KEY,
                        state="stuck",
                        re_escalate_after=SWEEP_ALARM_RE_ESCALATE_S)
        if result is not None:
            return True
        log("Zero-progress alarm returned no id (transport failure)")
    except Exception as exc:
        log(f"Zero-progress alarm send raised: {exc}")
    # G-S3 FAIL-SILENT, second-order: notify() records the transition BEFORE it
    # POSTs, so a transport failure would otherwise leave the key marked "stuck"
    # and every retry suppressed as an unchanged state -- an alarm that failed
    # once would then never be delivered at all. Re-arm the key so the next
    # cycle genuinely re-fires. (Found by this control's own both-ways test.)
    try:
        clear_transition(SWEEP_ALARM_KEY)
    except Exception:
        pass
    return False


def _send_sweep_recovery(drained, backlog):
    """R11 no-orphan-transition: the alarm's RELEASE has a defined effect."""
    try:
        from background.notify import notify
        notify(
            "[OPS] Run-marker sweep RECOVERED — drained {} marker(s) this pass; "
            "{} left in staging.".format(drained, backlog),
            kind="real_alarm", transition_key=SWEEP_ALARM_KEY, state="ok")
    except Exception as exc:
        log(f"Zero-progress recovery send raised: {exc}")


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
