#!/usr/bin/env python3
"""
Synthetic Enterprise — Background Worker
Runs autonomously using local Qwen only (no frontier tokens).
Checks docs/instructions/background-tasks.md for queued tasks.
Respects UK peak electricity hours: pauses between 16:00-19:00 GMT daily.
Logs all activity to docs/observability/background-worker-log.md
"""

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


def process_leftover_run_markers():
    """Process any run_complete_*.md markers that process_run_complete.py left behind.

    UNDOCUMENTED COUPLING, now documented (2026-07-13, director-flagged): this
    function is the ENTIRE real safety net for a marker that
    `background/sim_runner.py` itself skipped -- sim_runner.py only ever
    passes process_run_complete.py the ONE marker it just wrote each
    iteration, and process_run_complete.py's own lock-skip path returns 0
    (indistinguishable from a genuine success to that caller), so a marker
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
        return
    log(f"Found {len(markers)} leftover run_complete marker(s) — processing")
    processor = Path(__file__).parent / "process_run_complete.py"
    for marker in markers:
        result = subprocess.run(
            [sys.executable, str(processor), str(marker)],
            cwd=str(Path(__file__).resolve().parent.parent),
            timeout=900,
        )
        if result.returncode == 0:
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


def _record_publish_gate_outcome(marker, rc):
    """H15: route a run-complete processing return code into the publish-gate
    failure detector (background/process_run_complete.py). Defensive by
    construction -- a monitoring failure must never break the marker sweep or
    the loop that calls it."""
    try:
        from background import process_run_complete as prc
        if rc == 0:
            prc.record_publish_gate_success()
        else:
            git_hash = "unknown"
            try:
                git_hash = prc.parse_marker(marker).get("git_hash", "unknown")
            except Exception:
                pass
            prc.record_publish_gate_failure(
                f"process_run_complete rc={rc} on {marker.name}",
                rc=rc, git_hash=git_hash,
            )
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
            update_agent_status("background-worker", status="idle", last_action=f"Peak hours pause — {now.strftime('%H:%M UTC')}")
            time.sleep(60 * 15)  # check every 15min during peak
            continue

        # Read task queue
        if not TASKS_FILE.exists():
            log("No background-tasks.md found — sleeping")
            update_agent_status("background-worker", status="idle", last_action="No task queue found — sleeping")
            time.sleep(60 * CHECK_INTERVAL_MINUTES)
            continue

        tasks_content = TASKS_FILE.read_text()
        if "## QUEUED" not in tasks_content:
            log("No queued tasks — sleeping")
            update_agent_status("background-worker", status="idle", last_action="No queued tasks — sleeping")
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
