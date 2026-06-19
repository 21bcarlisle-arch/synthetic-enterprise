#!/usr/bin/env python3
"""Continuous simulation runner — keeps the GPU busy between Claude sessions.

Runs the full 9.5-year simulation in a loop, saving each result to a
timestamped JSON and report file. Writes a run_complete_*.md staging marker
so Claude picks up new results on its next autonomous or interactive turn.

Output files are timestamped so successive runs don't overwrite each other.
run_output_latest.json IS updated so Claude always has fresh data available.
ANNUAL_REPORT.md is NOT overwritten — Claude regenerates that explicitly
when it processes the run_complete marker (preserving manual fixes like
Phase 9a reconciliation).

Respects peak electricity hours: pauses 16:00-19:00 UTC.
"""

import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
LOG_FILE = PROJECT_DIR / "docs" / "observability" / "sim-runner-log.md"
STAGING_DIR = PROJECT_DIR / "docs" / "staging"
REPORTS_DIR = PROJECT_DIR / "docs" / "reports"

PEAK_START = 16
PEAK_END = 19
BETWEEN_RUN_PAUSE_SECONDS = 60  # brief pause between back-to-back runs

sys.path.insert(0, str(PROJECT_DIR))
from background.ntfy_utils import send_ntfy  # noqa: E402


def log(msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    entry = f"\n- [{ts}] {msg}"
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(entry)
    print(entry, flush=True)


def is_peak_hours() -> bool:
    return PEAK_START <= datetime.now(timezone.utc).hour < PEAK_END


def _git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(PROJECT_DIR), text=True, timeout=5,
        ).strip()
    except Exception:
        return "unknown"


def run_simulation() -> bool:
    """Run one full simulation. Returns True on success."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    head = _git_head()
    out_json = REPORTS_DIR / f"run_output_{head}_{ts}.json"
    out_md = REPORTS_DIR / f"ANNUAL_REPORT_{ts}.md"

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    log(f"Starting run — git={head}, json={out_json.name}")
    send_ntfy(f"[SIM] Run started — git={head} {ts}")

    t0 = time.monotonic()
    result = subprocess.run(
        [
            sys.executable, "-m", "saas.reporting.annual_report",
            "--save-json", str(out_json),
            "--output", str(out_md),
        ],
        cwd=str(PROJECT_DIR),
        timeout=7200,
    )
    elapsed = time.monotonic() - t0

    if result.returncode != 0 or not out_json.exists():
        log(f"Run FAILED (rc={result.returncode}) after {elapsed:.0f}s")
        send_ntfy(f"[SIM] Run FAILED after {elapsed:.0f}s — check sim-runner-log.md")
        return False

    size_kb = out_json.stat().st_size / 1024
    log(f"Run complete — {elapsed:.0f}s, {size_kb:.0f} KB ({out_json.name})")

    # Update latest pointer so Claude always has fresh data
    latest_json = REPORTS_DIR / "run_output_latest.json"
    latest_json.write_bytes(out_json.read_bytes())

    # Write staging marker — Claude processes this on its next turn
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    marker = STAGING_DIR / f"run_complete_{ts}.md"
    marker.write_text(
        f"# Simulation Run Complete\n\n"
        f"Finished: {datetime.now(timezone.utc).isoformat()}\n"
        f"Git: {head}\n"
        f"JSON: {out_json}\n"
        f"Draft report: {out_md}\n"
        f"Duration: {elapsed:.0f}s | Size: {size_kb:.0f} KB\n\n"
        f"## Action required\n\n"
        f"1. Regenerate docs/reports/ANNUAL_REPORT.md from this run's data:\n"
        f"   `python3 -m saas.reporting.annual_report`\n"
        f"2. Update docs/status/LATEST.md with key figures.\n"
        f"3. Run tests, commit (include report + LATEST.md), push.\n"
        f"4. NTFY Rich with headline net margin, gross margin, enterprise value.\n"
    )

    send_ntfy(
        f"[SIM] Run complete {ts} — {elapsed:.0f}s, {size_kb:.0f}KB. "
        f"Staged run_complete_{ts}.md for Claude to process."
    )
    return True


def main() -> None:
    log("Simulation runner started")
    send_ntfy("[SIM-RUNNER] Continuous simulation loop started — will run every ~15-20 min off-peak")

    while True:
        if is_peak_hours():
            now = datetime.now(timezone.utc)
            log(f"Peak hours ({PEAK_START}:00-{PEAK_END}:00 UTC) — pausing. "
                f"Current: {now.strftime('%H:%M UTC')}")
            time.sleep(900)
            continue

        success = run_simulation()
        wait = BETWEEN_RUN_PAUSE_SECONDS if success else 300
        log(f"Waiting {wait}s before next run...")
        time.sleep(wait)


if __name__ == "__main__":
    main()
