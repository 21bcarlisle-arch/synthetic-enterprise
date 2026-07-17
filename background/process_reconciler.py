"""Reconcile the DECLARED process set (process_manifest.yaml) against ACTUAL.
OPS1 sub-step 2 (G-L2 / G-R3), docs/design/OPERATIONAL_LAYER_DESIGN.md §2.1.

The manifest is the SINGLE source of "what should be running". Everything derives from it:
  - health_check.EXPECTED_PANES  = health_checked_map()  (state==enabled entries)
  - start_worker.sh's launch set = startlist()           (owner==start_worker.sh, enabled|dark)
There is no second list to drift.

Guarantees:
  - G-L2  one committed declaration; the per-entry `state` distinguishes intended-down
          (held/dark/retired) from failed (enabled & absent) -- so a deliberately-HELD
          daemon reads HELD (silent), never MISSING (the false-DEGRADED that the worker's
          resurrect reflex fired on, design §8). A HELD daemon found RUNNING is HELD_VIOLATED.
  - G-R3  reconcile REPORTS drift; it has NO kill path by construction. Reaping an undeclared
          process by inference is what killed the director's console in the blackout.

Schema is ENFORCED at load: every non-enabled entry MUST carry reason+flip (a state without
its reason is archaeology; IaC). An empty manifest is a hard error (fail-closed).
"""
from __future__ import annotations

import subprocess
from pathlib import Path

_HERE = Path(__file__).resolve().parent
MANIFEST_PATH = _HERE / "process_manifest.yaml"

VALID_STATES = {"enabled", "held", "dark", "retired"}
ALARM_STATUSES = {"MISSING", "HELD_VIOLATED", "RETIRED_RUNNING", "UNEXPECTED"}


class ManifestError(ValueError):
    """The manifest violates its schema -- fail LOUD, never load an untrustworthy declaration."""


def load_manifest(path: Path | None = None) -> list[dict]:
    import yaml
    path = path or MANIFEST_PATH
    data = yaml.safe_load(Path(path).read_text())
    procs = (data or {}).get("processes") or []
    if not procs:
        raise ManifestError(f"process manifest {path} declares no processes — refusing empty set")
    _validate(procs)
    return procs


def _validate(procs: list) -> None:
    seen = set()
    for i, e in enumerate(procs):
        where = f"processes[{i}] ({e.get('session') if isinstance(e, dict) else '?'})"
        if not isinstance(e, dict):
            raise ManifestError(f"{where}: entry must be a mapping")
        for req in ("session", "command", "match", "owner", "state"):
            if not str(e.get(req, "")).strip():
                raise ManifestError(f"{where}: missing required field '{req}'")
        if e["session"] in seen:
            raise ManifestError(f"{where}: duplicate session '{e['session']}'")
        seen.add(e["session"])
        if e["state"] not in VALID_STATES:
            raise ManifestError(f"{where}: state '{e['state']}' not in {sorted(VALID_STATES)}")
        if e["state"] != "enabled":
            for req in ("reason", "flip"):
                if not str(e.get(req, "")).strip():
                    raise ManifestError(
                        f"{where}: state '{e['state']}' requires a non-empty '{req}' "
                        "(a held/dark/retired state without its reason+flip is forbidden)")


def health_checked_map(path: Path | None = None) -> dict[str, str]:
    """{session: match} for ENABLED entries only. THE cure for held-vs-failed: held/dark/
    retired are excluded, so health_check never alarms on a deliberately-held daemon."""
    return {p["session"]: p["match"] for p in load_manifest(path) if p["state"] == "enabled"}


def declared_sessions(path: Path | None = None) -> set[str]:
    return {p["session"] for p in load_manifest(path)}


def startlist(path: Path | None = None) -> list[tuple[str, str]]:
    """(session, command) for the systemd daemons that should be STARTED now: owner==systemd
    and state in {enabled, dark}. Held/retired are NOT started -- that IS the hold, expressed
    once in the manifest. OPS1 sub-step 4 transition: ownership moved start_worker.sh -> systemd
    (units in background/systemd/); this is the set install_schedule.sh installs+starts. The old
    tmux launch in start_worker.sh is superseded and removed in the sub-step-4 absorption pass."""
    return [(p["session"], p["command"]) for p in load_manifest(path)
            if p["owner"] == "systemd" and p["state"] in ("enabled", "dark")]


def _is_running(entry: dict, panes: dict[str, str], ps_lines: list[str]) -> bool:
    if entry["session"] in panes:
        return True
    tok = entry["match"]
    return any(tok in line for line in ps_lines)


def reconcile(panes: dict[str, str], ps_lines: list[str], path: Path | None = None) -> list[dict]:
    """Classify declared vs actual. REPORT ONLY -- no side effects, no kill path.
    Returns per-entry {session, state, running, status, alarm, reason, flip}; plus an
    UNEXPECTED entry per undeclared *background-python* daemon (never a console seat -- the
    undeclared match requires python+background, so it can't point at the director's console)."""
    entries = load_manifest(path)
    declared = {e["session"] for e in entries}
    results: list[dict] = []
    for e in entries:
        up = _is_running(e, panes, ps_lines)
        st = e["state"]
        if st == "enabled":
            status = "OK" if up else "MISSING"
        elif st == "held":
            status = "HELD_VIOLATED" if up else "HELD"
        elif st == "dark":
            status = "DARK_ACTIVE" if up else "DARK"
        else:  # retired
            status = "RETIRED_RUNNING" if up else "OK"
        results.append({
            "session": e["session"], "state": st, "running": up, "status": status,
            "alarm": status in ALARM_STATUSES,
            "reason": e.get("reason", ""), "flip": e.get("flip", ""),
        })
    for session, cmd in panes.items():
        if session in declared:
            continue
        low = (cmd or "").lower()
        if "python" in low and "background" in low:
            results.append({"session": session, "state": "(undeclared)", "running": True,
                            "status": "UNEXPECTED", "alarm": True, "reason": "", "flip": ""})
    return results


def drift(results: list[dict]) -> list[dict]:
    return [r for r in results if r["alarm"]]


def format_report(results: list[dict]) -> str:
    order = {"MISSING": 0, "HELD_VIOLATED": 1, "RETIRED_RUNNING": 2, "UNEXPECTED": 3,
             "DARK_ACTIVE": 4, "HELD": 5, "DARK": 6, "OK": 7}
    lines = []
    for r in sorted(results, key=lambda r: (order.get(r["status"], 9), r["session"])):
        mark = "✗" if r["alarm"] else ("•" if r["status"] not in ("OK",) else "✓")
        line = f"  {mark} {r['session']:<20} {r['status']:<16} (state={r['state']}, running={r['running']})"
        if r["status"] in ("HELD", "DARK", "HELD_VIOLATED", "DARK_ACTIVE") and r["reason"]:
            line += f"\n        reason: {r['reason']}\n        flip:   {r['flip']}"
        lines.append(line)
    return "\n".join(lines)


def _live_panes_and_ps() -> tuple[dict[str, str], list[str]]:
    panes: dict[str, str] = {}
    r = subprocess.run(["tmux", "list-panes", "-a", "-F", "#{session_name} #{pane_current_command}"],
                       capture_output=True, text=True)
    if getattr(r, "returncode", 1) == 0:
        for line in (r.stdout or "").splitlines():
            parts = line.split(None, 1)
            if parts:
                panes.setdefault(parts[0], parts[1] if len(parts) == 2 else "")
    ps = subprocess.run(["ps", "-eo", "args"], capture_output=True, text=True)
    ps_lines = ps.stdout.splitlines() if getattr(ps, "returncode", 1) == 0 else []
    return panes, ps_lines


def _main(argv: list[str]) -> int:
    import sys
    if len(argv) > 1 and argv[1] == "startlist":
        # emit "session<TAB>command" per launchable entry (consumed by start_worker.sh)
        try:
            for session, command in startlist():
                print(f"{session}\t{command}")
        except ManifestError as e:
            print(f"MANIFEST INVALID: {e}", file=sys.stderr)
            return 2
        return 0
    try:
        results = reconcile(*_live_panes_and_ps())
    except ManifestError as e:
        print(f"MANIFEST INVALID: {e}", file=sys.stderr)
        return 2
    print(format_report(results))
    alarms = drift(results)
    print(f"\n{len(alarms)} drift alarm(s); {len(results) - len(alarms)} OK/held/dark.")
    return 1 if alarms else 0


if __name__ == "__main__":
    import sys
    raise SystemExit(_main(sys.argv))
