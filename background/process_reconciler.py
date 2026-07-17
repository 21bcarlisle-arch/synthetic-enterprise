"""Reconcile the DECLARED process set (process_manifest.yaml) against ACTUAL.
OPS1 sub-step 2 (G-L2 / G-R3) + sub-step 4 (systemd absorption),
docs/design/OPERATIONAL_LAYER_DESIGN.md §2.1, SUBSTEP4_SUPERVISOR_HYBRID.md §4/§5.

The manifest is the SINGLE source of "what should be running". Everything derives from it:
  - health_check.EXPECTED_PANES  = health_checked_map()  (state==enabled entries)
  - start_worker.sh's launch set = startlist()           (owner==systemd, enabled|dark)
  - the systemd unit set          = generate_units.py     (owner==systemd)
There is no second list to drift.

Sub-step 4 absorption (systemd is the single lifecycle owner, SUBSTEP4 §4): actual state is
read from **systemd unit state** (`is-active`/SubState via `_live_unit_states`), NOT from tmux
panes. The one exception is the interactive worker *seat* (the `claude` tmux session, which
systemd cannot own): it is detected by `_seat_active` (tmux has-session). The prior tmux-pane +
`ps`-token detection is DELETED (no parallel path). Undeclared-*unit* detection now lives in
schedule_reconciler (which owns the box's whole systemd-unit view and is process-manifest-aware),
so the old UNEXPECTED tmux-pane scan is retired with the pane reads it depended on.

Guarantees:
  - G-L2  one committed declaration; the per-entry `state` distinguishes intended-down
          (held/dark/retired) from failed (enabled & absent) -- so a deliberately-HELD
          daemon reads HELD (silent), never MISSING (the false-DEGRADED that the worker's
          resurrect reflex fired on, design §8). A HELD daemon found RUNNING is HELD_VIOLATED.
  - G-L3  a crash-looping/failed unit is LOUD, never silent: SubState `failed` -> UNIT_FAILED,
          `auto-restart` (seen across two samples) -> UNIT_CRASHLOOPING. Had this existed,
          file-api would have alarmed at failure #5, not looped 32,707 times invisibly.
  - G-R3  reconcile REPORTS drift; it has NO kill path by construction. Reaping an undeclared
          process by inference is what killed the director's console in the blackout.

Schema is ENFORCED at load: every non-enabled entry MUST carry reason+flip (a state without
its reason is archaeology; IaC). An empty manifest is a hard error (fail-closed).
"""
from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

_HERE = Path(__file__).resolve().parent
MANIFEST_PATH = _HERE / "process_manifest.yaml"

# The sentinel `match` of the interactive worker seat (owned by worker-seat-manager, NOT a
# systemd unit): detected via the `claude` tmux session, the one thing systemd can't own.
SEAT_MATCH = "__worker_seat__"

VALID_STATES = {"enabled", "held", "dark", "retired"}
ALARM_STATUSES = {"MISSING", "HELD_VIOLATED", "RETIRED_RUNNING",
                  "UNIT_FAILED", "UNIT_CRASHLOOPING"}


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
    """(session, command) for the daemons start_worker.sh should TMUX-launch now: owner==systemd,
    state in {enabled, dark}, AND NOT YET migrated to systemd (`launched_by` != systemd; default
    'tmux'). Held/retired are excluded -- that IS the hold. OPS1 sub-step 4 staged migration
    (director-ruled 2026-07-17): each daemon's cutover is ONE atomic change -- systemd takes it +
    it LEAVES this tmux set (`launched_by: systemd`) + its declaration flips -- so there is NEVER
    two launchers for one daemon and never a lying manifest. When the last daemon migrates, this
    list is empty and start_worker.sh's tmux-launch is retired entirely."""
    return [(p["session"], p["command"]) for p in load_manifest(path)
            if p["owner"] == "systemd" and p["state"] in ("enabled", "dark")
            and p.get("launched_by", "tmux") != "systemd"]


def _classify_by_state(state: str, running: bool) -> str:
    """The HELD<->unit mapping (SUBSTEP4 §4): a declared state + observed running -> status.
    Failure states (UNIT_FAILED/UNIT_CRASHLOOPING) are decided BEFORE this from SubState."""
    if state == "enabled":
        return "OK" if running else "MISSING"
    if state == "held":
        return "HELD_VIOLATED" if running else "HELD"
    if state == "dark":
        return "DARK_ACTIVE" if running else "DARK"
    return "RETIRED_RUNNING" if running else "OK"  # retired


def reconcile(unit_states: dict[str, dict] | None = None,
              seat_active: bool | None = None,
              tmux_running: set[str] | None = None,
              path: Path | None = None) -> list[dict]:
    """Classify declared vs actual. REPORT ONLY -- no side effects, no kill path (G-R3).

    TRANSITION-CORRECT (director-ruled 2026-07-17, staged migration): a daemon is RUNNING if its
    systemd unit is active OR it is present as a tmux/ps process -- because during the one-at-a-time
    migration some daemons are already systemd (migrated) while others are still tmux (start_worker).
    The OR reads whichever source is real for each daemon, so an un-migrated tmux daemon never reads
    MISSING and a migrated systemd daemon never needs a tmux pane. When migration completes,
    `tmux_running` is empty and this converges to the systemd-only end state.

    Inputs (injectable for tests; production reads live via `_live_unit_states` /
    `_live_tmux_running` / `_seat_active`):
      - unit_states: {session: {"active", "enabled", "substate"}} for the systemd-launched entries.
      - seat_active: whether the interactive worker seat (the `claude` tmux session) is up.
      - tmux_running: set of session names currently present as tmux/ps processes (the not-yet-
        migrated daemons). Absent -> empty.

    Per entry -> {session, state, running, status, alarm, reason, flip}. Failure states come FIRST
    off SubState (a `failed`/`auto-restart` unit alarms whatever its declared state); otherwise the
    HELD<->unit mapping (`_classify_by_state`) decides from running."""
    unit_states = unit_states or {}
    tmux_running = tmux_running or set()
    entries = load_manifest(path)
    results: list[dict] = []
    for e in entries:
        session = e["session"]
        st = e["state"]
        us = unit_states.get(session, {})
        substate = str(us.get("substate", ""))
        if e["match"] == SEAT_MATCH:
            running = bool(seat_active)
        else:
            running = bool(us.get("active")) or session in tmux_running
        # G-L3: SubState failure states are alarms regardless of the declared state.
        if substate == "failed":
            status = "UNIT_FAILED"
        elif substate == "auto-restart":
            status = "UNIT_CRASHLOOPING"
        else:
            status = _classify_by_state(st, running)
        results.append({
            "session": session, "state": st, "running": running, "status": status,
            "alarm": status in ALARM_STATUSES,
            "reason": e.get("reason", ""), "flip": e.get("flip", ""),
        })
    return results


def drift(results: list[dict]) -> list[dict]:
    return [r for r in results if r["alarm"]]


def format_report(results: list[dict]) -> str:
    order = {"UNIT_FAILED": 0, "UNIT_CRASHLOOPING": 1, "MISSING": 2, "HELD_VIOLATED": 3,
             "RETIRED_RUNNING": 4, "DARK_ACTIVE": 5, "HELD": 6, "DARK": 7, "OK": 8}
    lines = []
    for r in sorted(results, key=lambda r: (order.get(r["status"], 9), r["session"])):
        mark = "✗" if r["alarm"] else ("•" if r["status"] not in ("OK",) else "✓")
        line = f"  {mark} {r['session']:<20} {r['status']:<16} (state={r['state']}, running={r['running']})"
        if r["status"] in ("HELD", "DARK", "HELD_VIOLATED", "DARK_ACTIVE") and r["reason"]:
            line += f"\n        reason: {r['reason']}\n        flip:   {r['flip']}"
        lines.append(line)
    return "\n".join(lines)


def _systemd_owned_sessions(path: Path | None = None) -> list[str]:
    """Sessions whose lifecycle is ACTUALLY on systemd now (migrated): owner==systemd AND
    launched_by==systemd. Only these are worth a `systemctl show` -- an un-migrated daemon has no
    installed unit yet and is detected via `_live_tmux_running` instead."""
    return [e["session"] for e in load_manifest(path)
            if e.get("owner") == "systemd" and e.get("launched_by", "tmux") == "systemd"]


def _unit_snapshot(session: str) -> dict:
    """One instantaneous read of a `--user` unit's state (systemd is the lifecycle owner).
    Uses `systemctl --user show` (one call, machine-parsable) -- an uninstalled/unknown unit
    reports ActiveState=inactive/SubState=dead, which reconcile reads as not-running."""
    r = subprocess.run(
        ["systemctl", "--user", "show", f"{session}.service",
         "-p", "ActiveState", "-p", "SubState", "-p", "UnitFileState"],
        capture_output=True, text=True,
    )
    props: dict[str, str] = {}
    if getattr(r, "returncode", 1) == 0:
        for line in (r.stdout or "").splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                props[k] = v
    return {
        "active": props.get("ActiveState") == "active",
        "enabled": props.get("UnitFileState") == "enabled",
        "substate": props.get("SubState", ""),
    }


def _live_unit_states(samples: int = 2, interval: float = 2.0,
                      path: Path | None = None) -> dict[str, dict]:
    """Live systemd state for every systemd-owned entry. Sampled `samples` times so
    UNIT_CRASHLOOPING requires `auto-restart` seen across BOTH reads (SUBSTEP4 §5) -- a single
    legitimate restart flashes `auto-restart` once and must NOT alarm; a real crash-loop shows it
    every read. The last read wins for every other field."""
    sessions = _systemd_owned_sessions(path)
    states = {s: _unit_snapshot(s) for s in sessions}
    auto_seen = {s: st["substate"] == "auto-restart" for s, st in states.items()}
    for _ in range(max(0, samples - 1)):
        time.sleep(interval)
        latest = {s: _unit_snapshot(s) for s in sessions}
        for s in sessions:
            auto_seen[s] = auto_seen[s] and latest[s]["substate"] == "auto-restart"
        states = latest
    # Only report auto-restart when confirmed across all samples; otherwise mask it so a lone
    # transient restart doesn't read as a crash-loop.
    for s in sessions:
        if states[s]["substate"] == "auto-restart" and not auto_seen[s]:
            states[s]["substate"] = "activating"
    return states


def _seat_active() -> bool:
    """Whether the interactive worker seat (`claude` tmux session) is up -- the one entry
    systemd cannot own. NOTE: `has-session` is session-scoped, so it is NOT confused by the
    director-console window also being named 'claude' (unlike a bare pane-scoped `-t claude`)."""
    return subprocess.run(["tmux", "has-session", "-t", "claude"],
                          capture_output=True).returncode == 0


def _live_tmux_running(path: Path | None = None) -> set[str]:
    """Declared sessions currently present as a tmux session OR a matching `ps` process -- the
    not-yet-migrated (`launched_by`!=systemd) daemons that start_worker.sh still tmux-launches.
    The seat (`claude`) is handled separately via `_seat_active`, so it is excluded here."""
    entries = [e for e in load_manifest(path)
               if e["match"] != SEAT_MATCH and e.get("launched_by", "tmux") != "systemd"]
    running: set[str] = set()
    r = subprocess.run(["tmux", "list-sessions", "-F", "#{session_name}"],
                       capture_output=True, text=True)
    sessions = set((r.stdout or "").split()) if getattr(r, "returncode", 1) == 0 else set()
    ps = subprocess.run(["ps", "-eo", "args"], capture_output=True, text=True)
    ps_out = ps.stdout if getattr(ps, "returncode", 1) == 0 else ""
    for e in entries:
        if e["session"] in sessions or e["match"] in ps_out:
            running.add(e["session"])
    return running


# ── Pull-loop transport health (OPS1_transport_failure_must_be_loud, §9) ──────────────────
# The pull loop is the company's turn-transport lifeline; its failure was fail-SILENT for a day
# (a broken loop was byte-for-byte indistinguishable from a healthy idle worker). The Stop hook
# now writes a typed outcome to .pull_loop_health.json on every worker fire; this classifies it
# so a broken loop is LOUD and, crucially, 'idle because no work/grant' reads DIFFERENTLY from
# 'idle because the loop is broken'. Firing is wired into the deadman (the running periodic alarm).
PULL_LOOP_HEALTH_PATH = _HERE.parent / "docs" / "observability" / ".pull_loop_health.json"
PULL_LOOP_ENABLE_PATH = _HERE.parent / "docs" / "observability" / ".build_executor_enabled"


def pull_loop_status(health: dict | None, enable_on: bool) -> dict:
    """PURE predicate (mutation-testable): classify the transport from its last-fire health
    record + whether the loop is enabled. REPORT ONLY. Returns {status, alarm, detail}.

      DISABLED      loop off (kill switch) -> autonomy deliberately paused         (no alarm)
      HEALTHY_DREW  last fire drew work                                            (no alarm)
      HEALTHY_IDLE  last fire allow-stopped: no drawable work / paused             (no alarm)
      LOOP_BROKEN   last fire hit a draw/import error -> cannot draw               (ALARM)
      UNKNOWN       no / unrecognised health record                               (no alarm)

    THE distinction the director required: HEALTHY_IDLE ('idle because no grant / no work')
    reads DIFFERENTLY from LOOP_BROKEN ('idle because the loop is broken')."""
    if not enable_on:
        return {"status": "DISABLED", "alarm": False,
                "detail": "pull loop disabled (kill switch off) -- autonomy paused"}
    if not isinstance(health, dict) or not health.get("outcome"):
        return {"status": "UNKNOWN", "alarm": False,
                "detail": "no transport-health record yet (deadman commit-clock is the backstop)"}
    outcome = str(health.get("outcome"))
    if outcome == "DRAW_ERROR":
        return {"status": "LOOP_BROKEN", "alarm": True,
                "detail": f"pull-loop transport cannot draw: {health.get('detail', '')}"}
    # SELF-SUSTAIN loud states (2026-07-17, director P0). Both are the fail-silent law applied to a
    # CONTINUOUS loop: it kept running but stopped making progress / drew nothing under Rule-0.
    if outcome == "STUCK_NO_PROGRESS":
        return {"status": "LOOP_STUCK", "alarm": True,
                "detail": f"pull-loop thrashing (no commit): {health.get('detail', '')}"}
    if outcome == "DRAW_EMPTY_UNEXPECTED":
        # Under Rule-0 the queue is never genuinely empty, so an empty draw = a broken draw.
        return {"status": "LOOP_BROKEN", "alarm": True,
                "detail": f"pull-loop drew nothing (never legitimate under Rule-0): {health.get('detail', '')}"}
    if outcome == "DREW":
        return {"status": "HEALTHY_DREW", "alarm": False, "detail": "last fire drew work"}
    if outcome in ("ALLOW_STOP_NO_WORK", "ALLOW_STOP_DISABLED"):
        # ALLOW_STOP_DISABLED = kill switch off (deliberate). ALLOW_STOP_NO_WORK is retained for
        # back-compat but the hook no longer emits it (empty is now DRAW_EMPTY_UNEXPECTED, loud).
        return {"status": "HEALTHY_IDLE", "alarm": False,
                "detail": "idle: paused (kill switch) -- NOT a broken loop"}
    return {"status": "UNKNOWN", "alarm": False, "detail": f"unrecognised outcome {outcome!r}"}


def read_pull_loop_health(path: Path | None = None) -> dict | None:
    """Read the last transport-health record, or None if absent/unreadable (never raises)."""
    try:
        return json.loads((path or PULL_LOOP_HEALTH_PATH).read_text())
    except Exception:
        return None


def pull_loop_enabled(path: Path | None = None) -> bool:
    """True if the single kill-switch flag is a readable regular file (fail-closed)."""
    try:
        return (path or PULL_LOOP_ENABLE_PATH).is_file()
    except Exception:
        return False


def evaluate_pull_loop() -> dict:
    """Live wrapper: read the health record + the enable flag, return pull_loop_status(...).
    REPORT ONLY -- no side effects."""
    return pull_loop_status(read_pull_loop_health(), pull_loop_enabled())


# ── Deployment-by-construction: booted-SHA drift (OPS1 sub-step 5, G-D1/G-D3) ─────────────
# A managed daemon stamps the git HEAD it booted from (its unit's ExecStartPre → boot_sha.stamp).
# Here we compare that stamp against current HEAD: a running daemon whose boot-SHA is older than
# HEAD is running STALE code. This GENERALISES health_check.stale_daemon_sessions (own-script
# mtime only) — any HEAD advance past the boot SHA is stale, including a changed IMPORTED module
# the mtime check never saw. REPORT ONLY (the deploy step — systemctl restart — is separate, G-D2).
def boot_sha_drift(head: str | None, boot_shas: dict[str, str | None], running_sessions) -> list[str]:
    """PURE (mutation-testable): the running daemons on STALE code. A running daemon whose stamped
    boot-SHA is present AND != head booted from older code → stale. A session with no stamp yet is
    NOT flagged (fail-safe: unknown, never a false 'stale'). head None → [] (git unavailable, can't
    judge — the deadman/commit-clock is the backstop). REPORT ONLY."""
    if not head:
        return []
    return sorted(
        s for s in running_sessions
        if boot_shas.get(s) and boot_shas.get(s) != head
    )


def evaluate_boot_sha_drift() -> dict:
    """Live wrapper: for each ACTIVE systemd-launched daemon (the ones whose unit ExecStartPre
    actually stamps), compare its boot-SHA to current HEAD. Returns {head, stale:[session,...]}.
    REPORT ONLY — no restart, no side effects."""
    from background import boot_sha
    head = boot_sha.current_head()
    unit_states = _live_unit_states()
    running = [s for s in _systemd_owned_sessions() if unit_states.get(s, {}).get("active")]
    boot_shas = {s: boot_sha.read_boot_sha(s) for s in running}
    return {"head": head, "stale": boot_sha_drift(head, boot_shas, running)}


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
        results = reconcile(_live_unit_states(), _seat_active(), _live_tmux_running())
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
