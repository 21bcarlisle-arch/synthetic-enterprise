"""Operational process manifest — loader + reconciliation.
OPS1 sub-step 2, guarantee G-L2 (docs/design/OPERATIONAL_LAYER_DESIGN.md §2.1).

The manifest (docs/design/operational_manifest.yaml) is the SINGLE committed
declaration of what should run. This module loads + validates it and reconciles it
against the actual running set (tmux), classifying every process as one of:

    OK              enabled & running | held & down | dark & down | retired & down
    MISSING         enabled & NOT running                     -> alarm (a real failure)
    HELD_VIOLATED   held & running (a director-HELD daemon is up) -> alarm (the 2026-07-17 incident)
    DARK_ACTIVE     dark & running (executor live via its flag)   -> report (director-authorised)
    RETIRED_RUNNING retired & running                         -> alarm
    UNEXPECTED      a running session not in the manifest      -> alarm (undeclared drift)

RECONCILE IS REPORT-ONLY. It never starts, stops, or resurrects anything -- that is
the whole point: drift is surfaced and classified, never silently "fixed" by
restarting whatever was there (design §8). The director's console (tmux `work`, or any
console started via background/console.sh) is excluded via its G-L1 sanctity marker.

Schema is ENFORCED at load: every non-enabled entry MUST carry `reason` and `flip`
(a state without its reason is archaeology in three weeks -- IaC).
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import yaml

PROJECT_DIR = Path(__file__).resolve().parent.parent
MANIFEST_PATH = PROJECT_DIR / "docs" / "design" / "operational_manifest.yaml"

VALID_STATES = {"enabled", "held", "dark", "retired"}
# classifications that should page the director
ALARM_STATUSES = {"MISSING", "HELD_VIOLATED", "RETIRED_RUNNING", "UNEXPECTED"}


class ManifestError(ValueError):
    """Raised when the manifest violates its schema -- fail LOUD, never load a
    manifest whose declarations can't be trusted."""


def load_manifest(path: Path | None = None) -> dict:
    path = path or MANIFEST_PATH
    data = yaml.safe_load(Path(path).read_text())
    _validate(data)
    return data


def _validate(data: dict) -> None:
    if not isinstance(data, dict) or "processes" not in data:
        raise ManifestError("manifest must be a mapping with a 'processes' list")
    names = set()
    for i, e in enumerate(data["processes"]):
        where = f"processes[{i}]" + (f" ({e.get('name')})" if isinstance(e, dict) else "")
        if not isinstance(e, dict):
            raise ManifestError(f"{where}: entry must be a mapping")
        for req in ("name", "tmux", "command", "owner", "state"):
            if not e.get(req):
                raise ManifestError(f"{where}: missing required field '{req}'")
        if e["name"] in names:
            raise ManifestError(f"{where}: duplicate name '{e['name']}'")
        names.add(e["name"])
        if e["state"] not in VALID_STATES:
            raise ManifestError(f"{where}: state '{e['state']}' not in {sorted(VALID_STATES)}")
        # THE guard: a non-enabled state without its reason+flip is archaeology.
        if e["state"] != "enabled":
            for req in ("reason", "flip"):
                if not str(e.get(req, "")).strip():
                    raise ManifestError(
                        f"{where}: state '{e['state']}' requires a non-empty '{req}' "
                        "(a held/dark/retired state without its reason+flip-condition is forbidden)")


def _running_sessions() -> dict[str, int]:
    """Map of live tmux session_name -> its pane_pid. Empty on tmux failure."""
    r = subprocess.run(
        ["tmux", "list-panes", "-a", "-F", "#{session_name} #{pane_pid}"],
        capture_output=True, text=True,
    )
    if getattr(r, "returncode", 1) != 0:
        return {}
    out: dict[str, int] = {}
    for line in (r.stdout or "").splitlines():
        parts = line.split()
        if len(parts) == 2:
            try:
                out.setdefault(parts[0], int(parts[1]))
            except ValueError:
                pass
    return out


def _ppid_of(pid: int) -> int | None:
    try:
        for line in (Path("/proc") / str(pid) / "status").read_text().splitlines():
            if line.startswith("PPid:"):
                return int(line.split()[1])
    except (OSError, ValueError, IndexError):
        pass
    return None


def _console_sessions(sessions: dict[str, int], declared_console_tmux: str | None) -> set[str]:
    """tmux sessions that are the director's console, excluded from UNEXPECTED:
    the declared console (belt) PLUS any session whose pane_pid is an ancestor of a
    G-L1-sanctified pid (so a console started via background/console.sh is recognised
    structurally, by its marker, not by name)."""
    from background import console_sanctity
    console = set()
    if declared_console_tmux and declared_console_tmux in sessions:
        console.add(declared_console_tmux)
    pane_by_pid = {pid: sess for sess, pid in sessions.items()}
    for s in console_sanctity.sanctified_pids():
        cur: int | None = s
        for _ in range(32):
            if cur is None or cur <= 1:
                break
            if cur in pane_by_pid:
                console.add(pane_by_pid[cur])
                break
            cur = _ppid_of(cur)
    return console


def reconcile(manifest: dict | None = None,
              running: dict[str, int] | None = None,
              console: set[str] | None = None) -> list[dict]:
    """Classify declared processes vs actual. Report-only -- returns a list of
    {name, state, running, status, alarm, reason, flip}. Params are injectable for
    testing; production reads live state."""
    manifest = manifest or load_manifest()
    running = _running_sessions() if running is None else running
    if console is None:
        dc = (manifest.get("director_console") or {}).get("tmux")
        console = _console_sessions(running, dc)

    results: list[dict] = []
    declared_tmux = set()
    for e in manifest["processes"]:
        declared_tmux.add(e["tmux"])
        up = e["tmux"] in running
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
            "name": e["name"], "state": st, "running": up, "status": status,
            "alarm": status in ALARM_STATUSES,
            "reason": e.get("reason", ""), "flip": e.get("flip", ""),
        })

    # UNEXPECTED: a running session that is neither declared nor a director console.
    for sess in running:
        if sess in declared_tmux or sess in console:
            continue
        results.append({
            "name": sess, "state": "(undeclared)", "running": True,
            "status": "UNEXPECTED", "alarm": True, "reason": "", "flip": "",
        })
    return results


def drift(results: list[dict] | None = None) -> list[dict]:
    """The subset that should page the director (alarm=True)."""
    results = reconcile() if results is None else results
    return [r for r in results if r["alarm"]]


def format_report(results: list[dict]) -> str:
    order = {"MISSING": 0, "HELD_VIOLATED": 1, "RETIRED_RUNNING": 2, "UNEXPECTED": 3,
             "DARK_ACTIVE": 4, "HELD": 5, "DARK": 6, "OK": 7}
    lines = []
    for r in sorted(results, key=lambda r: (order.get(r["status"], 9), r["name"])):
        mark = "✗" if r["alarm"] else ("•" if r["status"] not in ("OK",) else "✓")
        line = f"  {mark} {r['name']:<20} {r['status']:<16} (state={r['state']}, running={r['running']})"
        if r["status"] in ("HELD", "DARK", "HELD_VIOLATED") and r["reason"]:
            line += f"\n        reason: {r['reason']}\n        flip:   {r['flip']}"
        lines.append(line)
    return "\n".join(lines)


def _main(argv: list[str]) -> int:
    import sys
    try:
        results = reconcile()
    except ManifestError as e:
        print(f"MANIFEST INVALID: {e}", file=sys.stderr)
        return 2
    print(format_report(results))
    alarms = [r for r in results if r["alarm"]]
    print(f"\n{len(alarms)} drift alarm(s); {len(results) - len(alarms)} OK/held/dark.")
    return 1 if alarms else 0


if __name__ == "__main__":
    import sys
    raise SystemExit(_main(sys.argv))
