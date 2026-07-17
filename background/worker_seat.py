"""The worker-seat manager — OPS1 sub-step 4, the ONE bespoke process.

systemd owns every daemon's lifecycle; the interactive worker seat (a claude session inside a
tmux server) is the one thing systemd cannot own, so this thin manager bridges the gap — and it
is ITSELF a systemd unit (worker-seat-manager.service), so even the bespoke piece has an owned
lifecycle.

DESIGN LAW — this file stays THIN (docs/design/SUBSTEP4_SUPERVISOR_HYBRID.md §3). Its entire job:
  1. SEED-BY-ID: create-or-resume the `claude` tmux session against the dedicated WORKER_SESSION_ID
     (--session-id first, --resume after) — NEVER `claude -c` (the console-latch bug).
  2. KEEP-ALIVE: if the seat process dies, re-seed it — BOUNDED (N re-seeds in a window -> stop +
     record status, never an infinite silent loop; the file-api 32,707 lesson).
  3. REPORT STATUS: write a status line to a file. Nothing else.

FORBIDDEN here, permanently (mutation-tested in test_worker_seat.py):
  - NO reaping / process-killing (os.kill, signal, pkill). The reaper is DELETED; exit-143 is
    impossible by absence, not inference.
  - NO auto-advance: the seed brings-up-and-reports, then STOPS. Advancing is the supervisor's
    job (governed turn-granting), never the seed's (G-R4).
  - NO notification machinery (ntfy). Alarming is the reconciler's job, not the seat manager's.
Scope-creep in this one file is where accretion would restart; its thinness is a permanent invariant.
"""
from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
SESSION_NAME = "claude"
MODEL = "claude-opus-4-8"
# The dedicated worker conversation id (same as the old watchdog's — the seat's identity is stable).
WORKER_SESSION_ID = "22080be5-e19e-4099-a007-d71c3a6e7845"
CLAUDE_PROJECTS = Path.home() / ".claude" / "projects"
STATUS_FILE = PROJECT_DIR / "docs" / "observability" / ".worker_seat_status"

CHECK_INTERVAL_SECONDS = 60
# Bounded re-seed (the crash-loop bound applied to the seat, mirroring systemd StartLimit).
MAX_RESEEDS = 5
RESEED_WINDOW_SECONDS = 600

# Bring-up-and-report ONLY. Deliberately NOT the old RESUME_INSTRUCTION: no "ADVANCE THE PROJECT"
# step. The seat re-orients and reports, then waits for a supervisor-granted turn (G-R4).
SEED_PROMPT = (
    "Worker seat (re)started under systemd. Run the BRING-UP checklist, then STOP and wait:\n"
    "1. git status; note anything uncommitted.\n"
    "2. python3 -m tools.epistemic_verifier (must PASS).\n"
    "3. Report current status to the director via the normal channel.\n"
    "DO NOT draw, advance, or act on any work. This seat does NOT self-advance (G-R4). The "
    "supervisor grants turns; wait for one. Starting work without a granted turn is a defect."
)


def _resolve_claude() -> str | None:
    import shutil
    return shutil.which("claude")


def _session_alive() -> bool:
    return subprocess.run(["tmux", "has-session", "-t", SESSION_NAME],
                          capture_output=True).returncode == 0


def _worker_session_exists() -> bool:
    try:
        for d in CLAUDE_PROJECTS.iterdir():
            if (d / f"{WORKER_SESSION_ID}.jsonl").exists():
                return True
    except OSError:
        pass
    return False


def seat_argv(claude_bin: str) -> list[str]:
    """--session-id (create) first time, --resume after. NEVER `claude -c`."""
    base = [claude_bin, "--dangerously-skip-permissions", "--model", MODEL]
    if _worker_session_exists():
        return base + ["--resume", WORKER_SESSION_ID, SEED_PROMPT]
    return base + ["--session-id", WORKER_SESSION_ID, SEED_PROMPT]


def _report(status: str) -> None:
    """Write one status line. No NTFY -- alarming is the reconciler's job, not ours."""
    try:
        STATUS_FILE.write_text(status + "\n")
    except OSError:
        pass


def seed_seat(claude_bin: str) -> None:
    """Create-or-resume the tmux worker seat. No reaping; no pane injection."""
    subprocess.run(
        ["tmux", "new-session", "-d", "-s", SESSION_NAME, "-c", str(PROJECT_DIR),
         "-e", "DISABLE_AUTOUPDATER=1"] + seat_argv(claude_bin),
        capture_output=True)


def main() -> None:
    _report("worker-seat-manager started (thin: seed-by-id, keep-alive, report)")
    reseeds: list[float] = []
    while True:
        time.sleep(CHECK_INTERVAL_SECONDS)
        if _session_alive():
            continue
        # bounded re-seed: never an infinite silent respawn loop
        now = time.time()
        reseeds[:] = [t for t in reseeds if now - t < RESEED_WINDOW_SECONDS]
        if len(reseeds) >= MAX_RESEEDS:
            _report(f"worker seat down; re-seed bound hit ({MAX_RESEEDS}/{RESEED_WINDOW_SECONDS}s) -- "
                    "holding, not looping. Needs a look.")
            time.sleep(RESEED_WINDOW_SECONDS)
            reseeds.clear()
            continue
        claude_bin = _resolve_claude()
        if not claude_bin:
            _report("worker seat down; claude binary not found -- cannot re-seed")
            continue
        reseeds.append(now)
        seed_seat(claude_bin)
        mode = "resume" if _worker_session_exists() else "create"
        _report(f"re-seeded worker seat ({mode}, dedicated session {WORKER_SESSION_ID}, no `claude -c`)")


if __name__ == "__main__":
    sys.exit(main())
