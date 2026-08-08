#!/usr/bin/env python3
"""
Synthetic Enterprise — Background Worker
Runs autonomously using local Qwen only (no frontier tokens).
Checks docs/instructions/background-tasks.md for queued tasks.
Respects UK peak electricity hours: pauses between 16:00-19:00 GMT daily.
Logs all activity to docs/observability/background-worker-log.md
"""

import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Stdlib-only helper (H30) -- safe at module scope, unlike the publish pipeline.
from background.child_diagnostics import STDERR_TAIL_LINES, stderr_tail  # noqa: E402

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
# Persistent sweep state (oldest-marker stall counter). Module-level so tests
# can redirect it -- a new real-disk flag that tests do NOT pin leaks into
# every unpinned loader and starts alarming off other tests' fixtures.
SWEEP_STATE_FILE = Path("docs/observability/.run_marker_sweep_state.json")
# Consecutive sweeps with the SAME oldest marker still sitting in staging/
# before the zero-progress alarm fires. The worker loop is 30 min, so this is
# ~1.5h of a retry loop that is provably not retrying.
STALL_ALARM_CYCLES = 3


def _marker_stamp(name: str) -> str | None:
    """`run_complete_20260803T064304Z.md` -> `20260803T064304Z`.

    Returns None for anything that does not parse. FAIL-SAFE DIRECTION (R15):
    an unparseable name is treated as PENDING by every caller, never as
    superseded -- the failure mode of a bad parse must be "we tried to publish
    something we didn't need to", never "we retired a marker nobody published".
    """
    stem = Path(name).stem
    if not stem.startswith("run_complete_"):
        return None
    stamp = stem[len("run_complete_"):]
    return stamp or None


def _newest_published_stamp(done_dir: Path) -> str | None:
    """The latest run stamp that actually REACHED done/, i.e. the newest run
    whose publish pipeline ran to completion. This is the supersession
    frontier: any marker older than it describes a snapshot that has already
    been overtaken on every published surface."""
    if not done_dir.is_dir():
        return None
    stamps = [s for s in (_marker_stamp(p.name) for p in done_dir.glob("run_complete_*.md")) if s]
    return max(stamps) if stamps else None


def classify_markers(markers, newest_published):
    """Split leftover markers into (superseded, pending).

    SUPERSEDED == a strictly LATER run has already been published. Re-running
    the pipeline on such a marker does not "catch up" -- it regenerates
    ANNUAL_REPORT.md, LATEST.md and the whole site FROM A STALE SNAPSHOT,
    overwriting current figures with older ones. That is a fidelity
    regression (R11/R14: every published figure carries its clock; this would
    silently wind the clock backwards), so supersession is a TERMINAL state,
    not a retry state.

    Ordering is lexicographic on the fixed-width UTC stamp, which for this
    format is chronological. Unparseable names sort as pending (see
    _marker_stamp)."""
    superseded, pending = [], []
    for marker in markers:
        stamp = _marker_stamp(marker.name)
        if newest_published and stamp and stamp < newest_published:
            superseded.append(marker)
        else:
            pending.append(marker)
    return superseded, pending


def retire_superseded_marker(marker: Path, newest_published: str, done_dir: Path) -> bool:
    """Move a superseded marker to done/ with the reason RECORDED IN THE FILE.

    R10 forbids closing the backlog defect by DELETING the backlog. This does
    not delete: the marker keeps its content and gains an explicit
    superseded-by stamp, so an auditor reading done/ can see exactly why this
    run was never published and which run overtook it."""
    try:
        done_dir.mkdir(parents=True, exist_ok=True)
        note = (
            "\n\n## Superseded (not published)\n\n"
            f"Retired by background_worker.process_leftover_run_markers() at "
            f"{datetime.now(timezone.utc).isoformat()}.\n"
            f"A strictly later run ({newest_published}) had already completed its publish "
            f"pipeline, so this snapshot was overtaken on every published surface before "
            f"this marker could be processed. Re-running the pipeline here would have "
            f"republished stale figures over current ones. No publish was performed.\n"
        )
        with open(marker, "a") as fh:
            fh.write(note)
        marker.rename(done_dir / marker.name)
        return True
    except Exception as exc:
        log(f"Could not retire superseded marker {marker.name}: {exc}")
        return False


def _load_sweep_state() -> dict:
    try:
        return json.loads(SWEEP_STATE_FILE.read_text())
    except Exception:
        return {}


def _save_sweep_state(state: dict):
    try:
        SWEEP_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        SWEEP_STATE_FILE.write_text(json.dumps(state, indent=2))
    except Exception as exc:
        log(f"Could not persist run-marker sweep state: {exc}")


def _check_zero_progress(pending):
    """A retry loop that has NEVER succeeded is an ALARM, not a log line.

    THE DEFECT THIS CLOSES (2026-08-03, atom OPS_run_marker_sweep_livelock):
    the sweep logged `Lock-skipped ... will retry next cycle` 404 times per
    cycle, for days. That is the vocabulary of a healthy transient queue, and
    it is indistinguishable in the log from progress -- so a permanent total
    failure read as a working retry. FAIL-SILENT, exactly the R15 pattern.

    The signal is the OLDEST pending marker: if the same marker is still the
    oldest N sweeps running, nothing is draining, whatever the per-marker log
    lines say. R5: fires ONCE on the transition into the stalled state and
    stays quiet until the oldest marker actually changes."""
    state = _load_sweep_state()
    oldest = pending[0].name if pending else None
    if oldest is None:
        if state.get("stalled_on"):
            log("Run-marker sweep: backlog cleared — zero-progress alarm reset")
        _save_sweep_state({})
        return False
    if state.get("oldest") == oldest:
        cycles = int(state.get("cycles", 0)) + 1
    else:
        cycles = 1
    already_alarmed = state.get("stalled_on") == oldest
    fire = cycles >= STALL_ALARM_CYCLES and not already_alarmed
    _save_sweep_state({
        "oldest": oldest, "cycles": cycles,
        "stalled_on": oldest if (fire or already_alarmed) else None,
    })
    if fire:
        msg = (
            f"[ACTION NEEDED] Run-marker sweep has made ZERO progress for {cycles} "
            f"consecutive cycles: {oldest} is still the oldest of {len(pending)} pending "
            f"run_complete marker(s). The publish retry loop is not retrying — treat "
            f"'will retry next cycle' in background-worker-log.md as FALSE."
        )
        log(msg)
        try:
            # Pages through the ONE contract (G-N2: an untyped page is forbidden).
            # No transition_key: this call site already owns its own transition
            # suppression via the `stalled_on`/`already_alarmed` sweep state above,
            # and keying it again would suppress the retry that block depends on.
            from background.notify import notify
            notify(msg, kind="real_alarm")
        except Exception as exc:
            # An unavailable checker is a FAILED check, not a passed one (R15
            # FAIL-SILENT). The alarm still lands in the worker log above, and
            # we do NOT record it as alarmed, so the next cycle retries the send.
            log(f"Zero-progress alarm NTFY failed (alarm stands, will re-send): {exc}")
            state = _load_sweep_state()
            state["stalled_on"] = None
            _save_sweep_state(state)
    return fire


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
    check) for the regression guard on this exact property."""
    markers = sorted(STAGING_DIR.glob("run_complete_*.md"))
    if not markers:
        _check_zero_progress([])
        return

    # THE GLOB STAYS UNCONDITIONAL (see docstring above) -- every leftover
    # marker is still collected and still DISPOSED every cycle. What changed
    # (2026-08-03, OPS_run_marker_sweep_livelock) is that disposal now has a
    # terminal state other than "published": a marker a later published run
    # has already overtaken is RETIRED, not retried forever. Retiring is a
    # rename, not a pipeline run, so it needs no run lock and cannot be
    # lock-skipped -- which is what turned this sweep into a livelock.
    done_dir = STAGING_DIR / "done"
    newest_published = _newest_published_stamp(done_dir)
    superseded, pending = classify_markers(markers, newest_published)

    if superseded:
        retired = sum(
            1 for m in superseded
            if retire_superseded_marker(m, newest_published, done_dir)
        )
        log(f"Retired {retired}/{len(superseded)} superseded run_complete marker(s) "
            f"— overtaken by published run {newest_published}, not republished")

    _check_zero_progress(pending)

    if not pending:
        return
    log(f"Found {len(pending)} leftover run_complete marker(s) — processing")
    processor = Path(__file__).parent / "process_run_complete.py"
    for marker in pending:
        result = subprocess.run(
            [sys.executable, str(processor), str(marker)],
            cwd=str(Path(__file__).resolve().parent.parent),
            timeout=900,
            # H30 (2026-08-08): this sweep is the SAFETY NET for every skipped
            # marker, so "Failed to process (rc=N)" with no payload is the one
            # log line a backlog diagnosis starts from. Capture what the
            # publisher actually said.
            stderr=subprocess.PIPE,
            text=True,
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
            tail = stderr_tail(getattr(result, "stderr", None))
            log(f"Failed to process {marker.name} (rc={result.returncode}) — will retry next cycle"
                + (f"\n  publisher stderr (last {STDERR_TAIL_LINES} lines):\n{tail}" if tail
                   else "\n  publisher stderr: EMPTY"))
        # H15_publish_gate_failure_alert: feed every processing outcome into the
        # publish-gate wedge detector. This sweep is the recurring caller that
        # actually manifests a silent wedge -- process_run_complete returns
        # rc!=0 every cycle (test-fail / OOM SIGKILL rc=-9 / report-regen fail)
        # and leaves the marker in staging, so N consecutive failures here == a
        # stalled pipeline that must raise ONE [ACTION NEEDED] alert.
        _record_publish_gate_outcome(marker, result.returncode)


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
    try:  # seat guard, FIRST act -- refuse to start on foreign soil (background/_seat.py)
        from background._seat import refuse_if_foreign
    except ModuleNotFoundError:  # launched as `python3 background/background_worker.py`
        from _seat import refuse_if_foreign
    refuse_if_foreign("background_worker")
    main()
