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

import os
import re
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


# nvm installs `claude` under ~/.nvm/versions/node/*/bin and only puts it on PATH in an
# INTERACTIVE shell -- so a systemd --user service (bare, non-login PATH) can't find it via
# `which`. Resolve the absolute nvm path as a fallback, same lesson as session_watchdog's
# resolver (WATCHDOG_NO_SENDKEYS.md). Highest node version wins (nvm dirs are vX.Y.Z).
_CLAUDE_NVM_GLOB = str(Path.home() / ".nvm" / "versions" / "node" / "*" / "bin" / "claude")


def _resolve_claude() -> str | None:
    import shutil
    found = shutil.which("claude")
    if found:
        return found
    import glob
    matches = sorted(glob.glob(_CLAUDE_NVM_GLOB))
    return matches[-1] if matches else None


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
    """DETERMINISTIC IDENTITY (IDENTITY_DRIFT_FIX, 2026-07-19): ALWAYS `--session-id
    WORKER_SESSION_ID`, NEVER `--resume` (and never `claude -c`).

    Root cause of the 2026-07-19 continuity class: the old `--resume WORKER_SESSION_ID` path brought
    the seat up under a DIFFERENT live session id on this Claude Code build (resume reassigns the id).
    The pull-loop Stop hook identifies the worker by `session_id == WORKER_SESSION_ID`, so a reassigned
    seat was rejected as 'non-worker' on EVERY Stop and never received work -- the doorbell rang at a
    stale address while RC1/RC3/the heartbeat all fixed the draw. `--session-id` pins the live id to
    WORKER_SESSION_ID. Bring-up is stateless (git status + verifier + report, then wait), so NOT
    resuming prior transcript history is harmless and matches the clear-at-checkpoint ritual. Any stale
    on-disk transcript for this id is archived first (`_archive_stale_transcript`) so the create is
    clean. NOTE: `--session-id` semantics are Claude-Code-version-dependent; the identity VERIFICATION
    in main() (below) is the backstop that catches any residual drift regardless of seed semantics."""
    return [claude_bin, "--dangerously-skip-permissions", "--model", MODEL,
            "--session-id", WORKER_SESSION_ID, SEED_PROMPT]


def _archive_stale_transcript() -> None:
    """`--session-id` creates a session with an EXACT id; a stale on-disk transcript for
    WORKER_SESSION_ID could make that create ambiguous/colliding, so move it aside before seeding so
    the live id is deterministically WORKER_SESSION_ID (never a resume-style reassignment). Best-
    effort; never raises -- a failure here must not block a re-seed (Rule 0)."""
    try:
        for d in CLAUDE_PROJECTS.iterdir():
            f = d / f"{WORKER_SESSION_ID}.jsonl"
            if f.exists():
                f.rename(f.with_name(f"{WORKER_SESSION_ID}.jsonl.pre_reseed"))
    except OSError:
        pass


def _descendant_pids(root_pid: str) -> list[str]:
    """root_pid + all descendants via /proc ppid links (Linux). Best-effort, [] on error. Used to
    find the actual `claude` process under the tmux seat pane so we can read its live session id."""
    try:
        children: dict[str, list[str]] = {}
        for p in Path("/proc").iterdir():
            if not p.name.isdigit():
                continue
            try:
                stat = (p / "stat").read_text()
                # comm (field 2) may contain spaces/parens -> parse fields AFTER the last ')'.
                ppid = stat[stat.rfind(")") + 1:].split()[1]
            except (OSError, IndexError):
                continue
            children.setdefault(ppid, []).append(p.name)
        out, stack = [], [str(root_pid)]
        while stack:
            pid = stack.pop()
            out.append(pid)
            stack.extend(children.get(pid, []))
        return out
    except Exception:
        return []  # never raise


_UUID_JSONL = re.compile(
    r"/\.claude/projects/.*/([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\.jsonl$")


def _live_session_id() -> str | None:
    """The session id the LIVE seat in tmux '<SESSION_NAME>' is ACTUALLY running under -- which may
    differ from WORKER_SESSION_ID if a resume reassigned it (the identity-drift bug). Reads the tmux
    pane's process tree and finds the `<uuid>.jsonl` transcript it holds open under ~/.claude/projects.
    Best-effort, FAIL-SAFE None (unknown) on any error -- an unverifiable id must NEVER be mistaken for
    a positive mismatch (which would falsely flag drift), so callers treat None as 'not confirmed'.
    (The /proc read is environment-specific and unproven from the sandbox; the pure classifier
    `_classify_seat` is what the R15 tests cover, with the live id injected.)"""
    try:
        r = subprocess.run(["tmux", "list-panes", "-t", SESSION_NAME, "-F", "#{pane_pid}"],
                           capture_output=True, text=True)
        if r.returncode != 0 or not r.stdout.strip():
            return None
        pane_pid = r.stdout.strip().splitlines()[0].strip()
        for pid in _descendant_pids(pane_pid):
            fd_dir = Path(f"/proc/{pid}/fd")
            try:
                entries = list(fd_dir.iterdir())
            except OSError:
                continue
            for fd in entries:
                try:
                    target = os.readlink(fd)
                except OSError:
                    continue
                m = _UUID_JSONL.search(target)
                if m:
                    return m.group(1)
        return None
    except Exception:
        return None


def _classify_seat(alive: bool, live_id: str | None) -> str:
    """PURE keep-alive decision (the R15-covered core):
      'dead'    -> tmux seat gone: re-seed (the existing bounded path).
      'drift'   -> tmux ALIVE but its live session id is CONFIRMED != WORKER_SESSION_ID: the transport
                   rejects it as non-worker, so it will never get work AND the old liveness-only check
                   would call it healthy forever (the 2026-07-19 deadlock). worker_seat must NOT reap
                   (permanent invariant) -> it REPORTS loud so the reconciler/deadman pages and the
                   director runs the console-authorized bounce.
      'healthy' -> tmux alive AND id matches, OR id unverifiable this cycle (None -> never a false
                   drift; the deterministic --session-id seed is the prevention, this is the backstop).
    Making keep-alive IDENTITY-aware (not just liveness) is the seat manager doing its ONE job
    correctly -- keep the RECOGNISED seat alive, not any tmux session named '<SESSION_NAME>'."""
    if not alive:
        return "dead"
    if live_id is not None and live_id != WORKER_SESSION_ID:
        return "drift"
    return "healthy"


def _report(status: str) -> None:
    """Write one status line. No NTFY -- alarming is the reconciler's job, not ours."""
    try:
        STATUS_FILE.write_text(status + "\n")
    except OSError:
        pass


def seed_seat(claude_bin: str) -> None:
    """Create the tmux worker seat with a DETERMINISTIC session id. No reaping; no pane injection.
    Archives any stale transcript first so `--session-id WORKER_SESSION_ID` yields exactly that live
    id (IDENTITY_DRIFT_FIX)."""
    _archive_stale_transcript()
    subprocess.run(
        ["tmux", "new-session", "-d", "-s", SESSION_NAME, "-c", str(PROJECT_DIR),
         "-e", "DISABLE_AUTOUPDATER=1"] + seat_argv(claude_bin),
        capture_output=True)


def main() -> None:
    _report("worker-seat-manager started (thin: seed-by-id, keep-alive, report)")
    reseeds: list[float] = []
    while True:
        time.sleep(CHECK_INTERVAL_SECONDS)
        alive = _session_alive()
        live = _live_session_id()
        state = _classify_seat(alive, live)
        if state == "healthy":
            continue
        if state == "drift":
            # ALIVE but WRONG identity: the pull-loop rejects it as non-worker, so it will never get
            # work -- yet the old liveness-only check called this 'healthy' forever (the 2026-07-19
            # deadlock). worker_seat must NOT reap (permanent invariant; the reaper is deleted), so it
            # REPORTS loud -> the reconciler/deadman pages, and the director runs the console-
            # authorized bounce (background/bounce_worker_seat.sh) from OUTSIDE the seat. Deterministic
            # --session-id seeding prevents recurrence after that bounce. Auto-killing here is exactly
            # the capability this file forbids, so we never do it.
            _report(f"IDENTITY DRIFT: tmux '{SESSION_NAME}' seat is live session {live} != "
                    f"WORKER_SESSION_ID {WORKER_SESSION_ID} -- the pull-loop rejects it as non-worker, "
                    f"so NO work is delivered. NEEDS A BOUNCE (worker_seat cannot reap): run "
                    f"background/bounce_worker_seat.sh from OUTSIDE the seat.")
            continue
        # state == 'dead': bounded re-seed (never an infinite silent respawn loop)
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
        _report(f"re-seeded worker seat (create, deterministic --session-id {WORKER_SESSION_ID}, "
                "no `claude -c`)")


if __name__ == "__main__":
    sys.exit(main())
