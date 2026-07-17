"""Read-only probe of interactive Claude Code sessions (OPS1 sub-step 6/session_watchdog collapse).

The three still-live helpers that outlived session_watchdog.py: after the OPS1 sub-step-4 systemd
migration, worker_seat.py replaced the watchdog (seed-by-id + keep-alive + report, no reap), so all
of session_watchdog's restart/resume/usage-limit machinery went inert and was deleted. These three
were its ONLY surviving consumers — health_check.py's report-only duplicate-interactive-session
check — so they move here, to a neutral module with no lifecycle role, and session_watchdog.py is
gone. Purely observational: reads /proc, never spawns, reaps, or writes.
"""
from __future__ import annotations

from pathlib import Path

# The managed worker seat's tmux session name (the seat is `claude`; the director's console lives
# in its OWN session, which is how the duplicate-session check excludes it).
SESSION_NAME = "claude"


def interactive_claude_pids() -> list[int]:
    """PIDs of INTERACTIVE main Claude Code sessions -- the auto-resumed pane process
    (`claude --dangerously-skip-permissions ... -c <resume>`), EXCLUDING headless
    `claude -p` build-executor turns and node/MCP helpers. The single-session invariant
    keys on the PROCESS, not the tmux session: a Jul-15 crash-recovery ghost survived a
    FULL DAY (spamming the director every gate cycle) because a tmux-session check plus
    kill-session leaves an orphaned claude PROCESS alive (2026-07-16)."""
    pids: list[int] = []
    for entry in Path("/proc").iterdir() if Path("/proc").is_dir() else []:
        if not entry.name.isdigit():
            continue
        try:
            argv = (entry / "cmdline").read_bytes().split(b"\x00")
        except OSError:
            continue
        argv = [a.decode("utf-8", "replace") for a in argv if a]
        if not argv:
            continue
        # argv[0] must BE the claude binary -- excludes the `tmux new-session ... claude`
        # LAUNCHER (argv[0]=="tmux") that merely mentions claude in its args, which was
        # false-counted as a second session (2026-07-16 mis-page "MULTIPLE sessions").
        exe = argv[0].rsplit("/", 1)[-1]
        if exe not in ("claude", "node") or not exe:
            continue
        joined = " ".join(argv)
        if "--dangerously-skip-permissions" not in joined:
            continue  # not a launched Claude Code session
        if "-p" in argv or "--print" in argv:
            continue  # a headless build-executor turn, not an interactive session
        pids.append(int(entry.name))
    return pids


def _ppid_of(pid: int) -> int | None:
    """Parent pid of `pid` from /proc/<pid>/status, or None if unreadable."""
    try:
        for line in (Path("/proc") / str(pid) / "status").read_text().splitlines():
            if line.startswith("PPid:"):
                return int(line.split()[1])
    except (OSError, ValueError, IndexError):
        pass
    return None
