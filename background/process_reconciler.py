"""Reconcile the DECLARED process set (process_manifest.yaml) against ACTUAL.

OPS1 sub-step 2 (G-L2 / G-R3), docs/design/OPERATIONAL_LAYER_DESIGN.md.

Purpose: make the manifest the single source of "what should be running", and provide
a REPORT-ONLY reconciliation of declared-vs-actual so drift is detectable instead of
silent. This is the infrastructure-as-code core the director's addendum names: the
declaration lives in git; the machine's live process set is reconciled against it.

Guarantees this module keeps:
  - G-L2  the declared set is one committed manifest; health_check derives its expected
          panes from here (no second hand-maintained list to drift — the old drift hid
          naive-organ from the health check entirely).
  - G-R3  reconcile REPORTS drift; it NEVER returns a kill/reap action. Reaping an
          undeclared process by inference is exactly what killed the director's console
          in the blackout — this module cannot do that by construction (it has no kill
          path at all).

It also parses start_worker.sh's launch set so a test can bind the two declarations and
FAIL on drift (tests/background/test_process_reconciler.py), so the scattered-and-drifted
state cannot recur silently.
"""
from __future__ import annotations

import re
from pathlib import Path

_HERE = Path(__file__).resolve().parent
MANIFEST_PATH = _HERE / "process_manifest.yaml"
START_WORKER_PATH = _HERE / "start_worker.sh"

# start_worker.sh launches a daemon with:  _start_session "name" \
# A commented line begins with optional whitespace then '#'.
_START_SESSION_RE = re.compile(r'^\s*_start_session\s+"([^"]+)"')


def load_manifest(path: Path | None = None) -> list[dict]:
    """Return the declared process entries. Raises if the manifest is unreadable —
    an unreadable declaration is a hard error, never a silently-empty set (fail-closed)."""
    import yaml  # local import: keep module import cheap and yaml-optional at import time

    path = path or MANIFEST_PATH
    data = yaml.safe_load(path.read_text())
    procs = (data or {}).get("processes") or []
    if not procs:
        raise ValueError(f"process manifest {path} declares no processes — refusing empty set")
    return procs


def health_checked_map(path: Path | None = None) -> dict[str, str]:
    """{session: match} for entries whose absence is a fault. Consumed by
    health_check.EXPECTED_PANES so there is a single declared source."""
    return {p["session"]: p["match"] for p in load_manifest(path) if p.get("health_checked")}


def declared_sessions(path: Path | None = None) -> set[str]:
    """Every session named in the manifest (health-checked or not)."""
    return {p["session"] for p in load_manifest(path)}


def start_worker_launched_sessions(path: Path | None = None) -> set[str]:
    """The set of session names start_worker.sh actually launches (commented-out
    launchers, e.g. the retired autonomous-runner, are excluded because the regex
    only matches a line that STARTS with _start_session, not one behind a '# ')."""
    path = path or START_WORKER_PATH
    out: set[str] = set()
    for line in path.read_text().splitlines():
        m = _START_SESSION_RE.match(line)
        if m:
            out.add(m.group(1))
    return out


def _is_running(entry: dict, panes: dict[str, str], ps_lines: list[str]) -> bool:
    """Running if its tmux session is present OR its match token appears in ps."""
    if entry["session"] in panes:
        return True
    tok = entry["match"]
    return any(tok in line for line in ps_lines)


def reconcile(panes: dict[str, str], ps_lines: list[str], path: Path | None = None) -> dict:
    """Compare declared vs actual. REPORT ONLY — no side effects, no kill actions.

    Returns:
      missing               health_checked entries that are NOT running (real faults)
      informational_absent  non-health_checked declared entries not running
                            (e.g. executor-daemon when correctly dark — expected)
      undeclared_daemons    tmux sessions running a background python daemon that is
                            NOT in the manifest (a process the repo doesn't know about —
                            surfaced for a human, never auto-killed)
    """
    entries = load_manifest(path)
    declared = {e["session"] for e in entries}

    missing, informational_absent = [], []
    for e in entries:
        if _is_running(e, panes, ps_lines):
            continue
        (missing if e.get("health_checked") else informational_absent).append(e["session"])

    undeclared_daemons = []
    for session, cmd in panes.items():
        if session in declared:
            continue
        # Only flag sessions that look like a background python daemon — never a
        # console seat (claude/node/shell), so this can never point at the director's
        # console. "background" here matches both `background/x.py` and `background.x`.
        low = cmd.lower()
        if "python" in low and "background" in low:
            undeclared_daemons.append(session)

    return {
        "missing": sorted(missing),
        "informational_absent": sorted(informational_absent),
        "undeclared_daemons": sorted(undeclared_daemons),
    }
