#!/usr/bin/env python3
"""NTFY instant-ack responder — always-on, independent of the main session.

Problem this solves: the 'claude' tmux session (the main Claude Code agent)
can be deep in a long GPU-bound background simulation run, a multi-minute
tool call, or simply mid-thought when Rich sends a message via NTFY. The
existing two-way channel (`session_watchdog.py`'s `check_inbound_commands`)
relays the message into that session, but the relay only *types* the
message — it doesn't guarantee a timely reply, and Rich has no feedback that
anything happened.

This script polls the same `skynet-synthetic` NTFY topic independently (its
own watermark file, so it doesn't interfere with session_watchdog's), and for
every inbound message NOT sent by us, immediately replies with a short status
snapshot: what the latest background simulation run is doing (if any), GPU
utilisation, and the current git HEAD. This is a templated reply — no LLM
call, so it never competes with the simulation for GPU and is always fast.

It does NOT interpret, action, or replace anything — session_watchdog still
relays the message into the 'claude' session as before, and the Staging
Directory Protocol still applies for substantial instructions. This is purely
an instant "I heard you, here's what's running" ack so Rich always gets a
response, regardless of what else is happening.

Logs to docs/observability/ntfy-responder-log.md.
Persists its watermark to background/.ntfy_responder_since.json.
"""

import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

PROJECT_DIR = Path("/home/rich/synthetic-enterprise")
LOG_FILE = PROJECT_DIR / "docs" / "observability" / "ntfy-responder-log.md"
STATE_FILE = PROJECT_DIR / "background" / ".ntfy_responder_since.json"
OBSERVABILITY_DIR = PROJECT_DIR / "docs" / "observability"

POLL_INTERVAL_SECONDS = 20
RUN_LOG_GLOB = "*_run.log"
RUN_LOG_FRESH_SECONDS = 3600  # ignore run logs not touched in the last hour

PROGRESS_RE = re.compile(
    r"progress: ([\d,]+) settlement periods processed "
    r"\(latest: (\S+) period (\d+), treasury £([\d.]+)\)"
)

# Standalone script -- add the repo root so `from background.ntfy_utils
# import ...` works regardless of how it's invoked.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from background.ntfy_utils import NTFY_TOPIC, send_ntfy, was_sent_by_us  # noqa: E402

NTFY_POLL_URL = f"https://ntfy.sh/{NTFY_TOPIC}/json"


def log(msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    entry = f"\n- [{ts}] {msg}"
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(entry)
    print(entry)


def _load_since() -> float:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())["since"]
        except (json.JSONDecodeError, KeyError):
            pass
    return time.time()


def _save_since(since: float) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps({"since": since}))


def _latest_run_log() -> Path | None:
    """Most recently modified `*_run.log`, if touched within the last
    RUN_LOG_FRESH_SECONDS — otherwise None (no active run)."""
    candidates = list(OBSERVABILITY_DIR.glob(RUN_LOG_GLOB))
    if not candidates:
        return None
    latest = max(candidates, key=lambda p: p.stat().st_mtime)
    if time.time() - latest.stat().st_mtime > RUN_LOG_FRESH_SECONDS:
        return None
    return latest


def _run_progress_summary() -> str:
    run_log = _latest_run_log()
    if run_log is None:
        return "no active background simulation run"

    # Read the tail of the file without loading it all into memory.
    with open(run_log, "rb") as f:
        f.seek(0, 2)
        size = f.tell()
        f.seek(max(0, size - 8192))
        tail = f.read().decode(errors="replace")

    matches = PROGRESS_RE.findall(tail)
    if not matches:
        return f"{run_log.name} active, no progress line found in tail yet"

    periods, date, period, treasury = matches[-1]
    wake_ups = tail.count("[RISK COMMITTEE] Woken")
    return (
        f"{run_log.name}: {periods} periods processed, latest {date} "
        f"period {period}, treasury £{treasury}"
        + (f", {wake_ups} risk-committee wake-up(s) in the visible tail" if wake_ups else "")
    )


def _gpu_summary() -> str:
    for nvidia_smi in ("nvidia-smi", "/usr/lib/wsl/lib/nvidia-smi"):
        try:
            result = subprocess.run(
                [nvidia_smi, "--query-gpu=utilization.gpu,memory.used,memory.total",
                 "--format=csv,noheader,nounits"],
                capture_output=True, text=True, timeout=10,
            )
            if result.returncode == 0 and result.stdout.strip():
                util, used, total = (x.strip() for x in result.stdout.strip().split(","))
                return f"GPU {util}% util, {used}/{total} MiB VRAM"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    return "GPU status unavailable"


def _git_head_summary() -> str:
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%h %s"],
            capture_output=True, text=True, cwd=PROJECT_DIR, timeout=10,
        )
        return result.stdout.strip() if result.returncode == 0 else "git HEAD unavailable"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return "git HEAD unavailable"


def _write_to_staging(message: str) -> Path | None:
    """Write an inbound NTFY message to docs/staging/ so the Claude Code session
    picks it up on its next staging-directory poll. Returns the path written, or
    None if the message is too short to warrant staging (plain status pings)."""
    if len(message) < 25:
        return None
    staging_dir = PROJECT_DIR / "docs" / "staging"
    staging_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    path = staging_dir / f"from_rich_{ts}.md"
    path.write_text(f"# Inbound NTFY message from Rich\n\n{message}\n")
    return path


def build_status_reply(staged_path: Path | None = None) -> str:
    if staged_path:
        relay_line = f"Staged for Claude Code pickup: {staged_path.name}"
    else:
        relay_line = "Status ping — no staging file written (message too short to be an instruction)"
    return (
        f"{relay_line}\n"
        f"Sim: {_run_progress_summary()}\n"
        f"{_gpu_summary()}\n"
        f"HEAD: {_git_head_summary()}"
    )


def check_once(since: float) -> float:
    """Poll once for messages posted after `since`, not sent by us. For each,
    send an instant status ack. Returns the new watermark."""
    try:
        response = requests.get(
            NTFY_POLL_URL, params={"poll": "1", "since": int(since)}, timeout=10,
        )
    except requests.RequestException as e:
        log(f"Poll error: {e}")
        return since

    latest = since
    for line in response.text.splitlines():
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue

        if record.get("event") != "message":
            continue
        msg_time = record.get("time", 0)
        if msg_time <= since:
            continue
        latest = max(latest, msg_time)

        if was_sent_by_us(record.get("id")):
            continue

        message = record.get("message", "").strip()
        if not message:
            continue

        staged_path = _write_to_staging(message)
        reply = build_status_reply(staged_path)
        send_ntfy(reply, headers={"X-Priority": "3", "X-Tags": "satellite_antenna"})
        log(f"Acked inbound message {record.get('id')!r} ({message[:60]!r})"
            + (f" — staged as {staged_path.name}" if staged_path else ""))

    return latest


def main() -> None:
    since = _load_since()
    log("NTFY responder started")
    while True:
        try:
            new_since = check_once(since)
            if new_since != since:
                since = new_since
                _save_since(since)
        except Exception as e:
            log(f"Responder error: {e}")
        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
