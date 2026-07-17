"""Console-sanctity marker — OPS1 sub-step 1, guarantee G-L1
(docs/design/OPERATIONAL_LAYER_DESIGN.md §2.1).

PURPOSE
    Structurally distinguish the director's interactive console from managed
    daemons/workers so it can NEVER be reaped by any automated mechanism -- by
    an explicit POSITIVE marker the console carries, not by inference about how
    a session "looks". The blackout's exit-143 console kill must be impossible by
    construction, and that guarantee must NOT depend on tmux being reachable
    (the acute fix's inference falls back to raw guessing when tmux is down).

GUARANTEE (what this gives, stated honestly -- the threat is ACCIDENTAL
console-kill, not an adversarial process evading reap):
    - A sanctified PID is spared independent of tmux (reads only /proc + a file).
    - A daemon/worker is never accidentally marked (only an explicit sanctify()
      call -- the sanctioned launcher or a director action -- registers a PID).
    - PID reuse cannot transfer sanctity: an entry is valid only while the live
      process's start-time (from /proc/<pid>/stat field 22, assigned at process
      creation and preserved across exec) still matches what was recorded.
    NON-goal: this does not defend against a local process deliberately writing
    the registry to avoid being reaped. That is out of scope -- over-sparing is
    safe, under-sparing (killing the console) is the catastrophe; the marker
    only ever ADDS reasons to spare, never a reason to reap.

STATE (IaC note, per the mandate's §5 flag-registry finding):
    The MECHANISM is committed code (this module + the launcher + the watchdog
    check). The registry FILE is ephemeral machine-state -- live PIDs are
    per-boot and cannot be committed, exactly like a pidfile. It is self-pruning
    (dead / start-time-mismatched entries are dropped on every read/write), so it
    never grows stale in the way an untracked hand-edited flag would.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
REGISTRY_PATH = PROJECT_DIR / "docs" / "observability" / ".sanctified_consoles.json"


def _parse_start_ticks(stat: str) -> int | None:
    """Extract start-time (field 22) from a /proc/<pid>/stat string. comm (field 2)
    is parenthesised and may contain spaces/parens -> split after the LAST ')'.
    Remaining fields are 1-indexed from field 3 (state); field 22 (starttime) is
    remaining[22 - 3] = remaining[19]. Pure, so it is unit-testable directly."""
    rparen = stat.rfind(")")
    if rparen == -1:
        return None
    rest = stat[rparen + 2:].split()
    if len(rest) < 20:
        return None
    try:
        return int(rest[19])
    except ValueError:
        return None


def _proc_start_ticks(pid: int) -> int | None:
    """The process start-time (clock ticks since boot, /proc/<pid>/stat field 22),
    or None if the pid is not alive / unreadable. Assigned by the kernel at process
    creation and PRESERVED across exec -- so the launcher can register a shell PID
    and `exec claude` keeps the same, still-valid, start-time. Distinct per PID
    incarnation, so a reused PID number gets a different value (the anti-forgery
    key)."""
    try:
        stat = (Path("/proc") / str(pid) / "stat").read_text()
    except (OSError, ValueError):
        return None
    return _parse_start_ticks(stat)


def _load() -> dict:
    try:
        data = json.loads(REGISTRY_PATH.read_text())
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def _live_and_matching(pid_str: str, entry: dict) -> bool:
    """True iff the recorded pid is still the SAME live process (start-time match)."""
    try:
        pid = int(pid_str)
    except (TypeError, ValueError):
        return False
    recorded = entry.get("start_ticks")
    current = _proc_start_ticks(pid)
    return current is not None and current == recorded


def _prune(reg: dict) -> dict:
    """Drop entries whose pid is dead or whose start-time no longer matches
    (PID reuse). Pure -- returns the cleaned dict."""
    return {p: e for p, e in reg.items() if _live_and_matching(p, e)}


def _atomic_write(reg: dict) -> None:
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = REGISTRY_PATH.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(reg, indent=2, sort_keys=True))
    os.replace(tmp, REGISTRY_PATH)


def is_sanctified(pid: int) -> bool:
    """True iff `pid` is a registered console AND still the same live process.
    tmux-INDEPENDENT by construction: reads only the registry file and /proc.
    This is the G-L1 exemption the watchdog consults before any reap."""
    reg = _load()
    entry = reg.get(str(pid))
    if entry is None:
        return False
    return _live_and_matching(str(pid), entry)


def sanctify(pid: int) -> bool:
    """Mark `pid` as a director console that must never be reaped. Records the
    process's current start-time as the anti-forgery key. Prunes dead entries in
    the same write. Returns False if the pid is not a live process (nothing to
    mark)."""
    start = _proc_start_ticks(pid)
    if start is None:
        return False
    reg = _prune(_load())
    reg[str(pid)] = {
        "start_ticks": start,
        "marked_at": datetime.now(timezone.utc).isoformat(),
    }
    _atomic_write(reg)
    return True


def unsanctify(pid: int) -> None:
    """Remove `pid`'s sanctity (e.g. the director deliberately retires a console)."""
    reg = _prune(_load())
    reg.pop(str(pid), None)
    _atomic_write(reg)


def sanctified_pids() -> list[int]:
    """Currently-valid sanctified PIDs (dead/reused entries excluded)."""
    return [int(p) for p in _prune(_load())]


def prune() -> list[int]:
    """Rewrite the registry dropping dead/reused entries; return the survivors."""
    reg = _prune(_load())
    _atomic_write(reg)
    return [int(p) for p in reg]


def _main(argv: list[str]) -> int:
    import sys
    if len(argv) < 2 or argv[1] not in {"sanctify", "unsanctify", "check", "list", "prune"}:
        print("usage: python3 -m background.console_sanctity "
              "{sanctify <pid>|unsanctify <pid>|check <pid>|list|prune}", file=sys.stderr)
        return 2
    cmd = argv[1]
    if cmd == "list":
        print(sanctified_pids()); return 0
    if cmd == "prune":
        print("survivors:", prune()); return 0
    if len(argv) < 3:
        print(f"{cmd} needs a <pid>", file=sys.stderr); return 2
    pid = int(argv[2])
    if cmd == "sanctify":
        ok = sanctify(pid)
        print(f"sanctified {pid}" if ok else f"NOT a live pid: {pid}")
        return 0 if ok else 1
    if cmd == "unsanctify":
        unsanctify(pid); print(f"unsanctified {pid}"); return 0
    if cmd == "check":
        ok = is_sanctified(pid)
        print(f"{pid}: {'SANCTIFIED' if ok else 'not sanctified'}")
        return 0 if ok else 1
    return 2


if __name__ == "__main__":
    import sys
    raise SystemExit(_main(sys.argv))
