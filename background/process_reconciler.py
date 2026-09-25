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

import datetime
import json
import os
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
                  "UNIT_FAILED", "UNIT_CRASHLOOPING", "DOUBLE_LAUNCH"}


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
        unit_active = bool(us.get("active"))
        tmux_present = session in tmux_running
        if e["match"] == SEAT_MATCH:
            running = bool(seat_active)
        else:
            running = unit_active or tmux_present
        # G-L3: SubState failure states are alarms regardless of the declared state.
        if substate == "failed":
            status = "UNIT_FAILED"
        elif substate == "auto-restart":
            status = "UNIT_CRASHLOOPING"
        elif e["match"] != SEAT_MATCH and unit_active and tmux_present:
            # DOUBLE_LAUNCH (2026-07-29, DIRECTOR_RULING_FIX_DOUBLE_MESSAGING, R10 CLASS FIX).
            # The transition-tolerant `or` above answers "is it up?" and is RIGHT for that --
            # but it is blind to HOW MANY launchers are up: one and two read identically as
            # running=True/OK. That blindness is why ntfy-responder ran twice (systemd unit
            # active AND start_worker.sh's tmux launch) for hours while the reconciler said OK,
            # and one director NTFY became two queued instructions. Counting launchers is a
            # DIFFERENT question from liveness, so it gets its own status. This fires for the
            # WHOLE class -- any daemon whose cutover installed+enabled a unit but never flipped
            # `launched_by: systemd`, so both launchers own it.
            status = "DOUBLE_LAUNCH"
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
    order = {"UNIT_FAILED": 0, "UNIT_CRASHLOOPING": 1, "DOUBLE_LAUNCH": 2, "MISSING": 3,
             "HELD_VIOLATED": 4, "RETIRED_RUNNING": 5, "DARK_ACTIVE": 6, "HELD": 7,
             "DARK": 8, "OK": 9}
    lines = []
    for r in sorted(results, key=lambda r: (order.get(r["status"], 9), r["session"])):
        mark = "✗" if r["alarm"] else ("•" if r["status"] not in ("OK",) else "✓")
        line = f"  {mark} {r['session']:<20} {r['status']:<16} (state={r['state']}, running={r['running']})"
        if r["status"] in ("HELD", "DARK", "HELD_VIOLATED", "DARK_ACTIVE") and r["reason"]:
            line += f"\n        reason: {r['reason']}\n        flip:   {r['flip']}"
        lines.append(line)
    return "\n".join(lines)


# NOTE (PW1, 2026-08-09): `_systemd_owned_sessions()` -- owner==systemd AND launched_by==systemd --
# is DELETED, not deprecated. Its only remaining caller was the boot-SHA drift population, and
# choosing that population from a DECLARED field is precisely the defect: seven un-flipped rows
# silently decided which daemons the staleness detector was allowed to watch, and the two that
# caused the 10h wedge were among them. The population is now OBSERVED (`drift_population`); the
# declaration is the cross-check that ALARMS on disagreement (`launcher_drift`). Do not reintroduce
# a declaration-derived population -- `test_drift_population_is_observed_never_declared` fails if
# the manifest field can shrink the answer again.


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
    # DOUBLE_LAUNCH visibility (2026-07-29): read the unit of EVERY systemd-owned entry, not
    # just the migrated ones. Restricting this to `launched_by==systemd` meant a half-migrated
    # daemon -- unit installed, enabled and ACTIVE, but still in start_worker.sh's tmux set --
    # had its live unit never queried at all, so the second launcher was invisible by
    # construction. An unread source cannot alarm.
    sessions = [e["session"] for e in load_manifest(path) if e.get("owner") == "systemd"]
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


def _runs_daemon(args: str, match: str) -> bool:
    """True iff `args` is a process actually RUNNING this daemon, not merely MENTIONING it.

    The naive `match in args` substring test counts any command line containing the name --
    `grep ntfy_responder`, an editor, a deploy script, or the very diagnostic shell command
    used to investigate a duplicate. That false-positived DOUBLE_LAUNCH on a healthy
    single-launcher daemon within minutes of the control going live (2026-07-29). A control
    that cries wolf on healthy input gets ignored, which is worse than no control.

    So: the executable must be a python interpreter, and some ARGUMENT's basename must equal
    the match exactly. `python3 background/ntfy_responder.py` runs it; `grep ntfy_responder.py`
    and `pytest tests/.../test_ntfy_responder.py` do not.
    """
    tokens = args.split()
    if not tokens:
        return False
    if not os.path.basename(tokens[0]).startswith("python"):
        return False
    return any(os.path.basename(t) == match for t in tokens[1:])


def _unit_main_pid(session: str) -> int:
    """PID systemd itself started for `session`, or 0 if the unit is unknown/inactive. Used to
    tell a daemon's OWN systemd process apart from a second, non-systemd copy of it."""
    r = subprocess.run(
        ["systemctl", "--user", "show", f"{session}.service", "-p", "MainPID"],
        capture_output=True, text=True,
    )
    if getattr(r, "returncode", 1) != 0:
        return 0
    for line in (r.stdout or "").splitlines():
        if line.startswith("MainPID="):
            try:
                return int(line.split("=", 1)[1].strip())
            except ValueError:
                return 0
    return 0


def _live_tmux_running(path: Path | None = None) -> set[str]:
    """Declared sessions currently present as a tmux session OR a matching `ps` process -- the
    not-yet-migrated (`launched_by`!=systemd) daemons that start_worker.sh still tmux-launches.
    The seat (`claude`) is handled separately via `_seat_active`, so it is excluded here."""
    # DOUBLE_LAUNCH visibility (2026-07-29): scan EVERY non-seat entry, including ones already
    # flipped to `launched_by: systemd`. Excluding migrated daemons made a stray tmux copy of a
    # systemd-owned daemon undetectable -- which is precisely the duplicate we are hunting, and
    # would have made this very fix fail-open the moment the manifest entry was flipped.
    entries = [e for e in load_manifest(path) if e["match"] != SEAT_MATCH]
    running: set[str] = set()
    r = subprocess.run(["tmux", "list-sessions", "-F", "#{session_name}"],
                       capture_output=True, text=True)
    sessions = set((r.stdout or "").split()) if getattr(r, "returncode", 1) == 0 else set()
    # PID-AWARE (2026-07-29): the old test was `e["match"] in ps_out` -- a substring scan over
    # ALL of ps. A systemd-launched daemon's OWN command line matches its own `match`, so once
    # the launched_by filter was lifted every migrated daemon reported itself as a second
    # launcher and DOUBLE_LAUNCH false-positived on all five (caught on the LIVE box, not by the
    # tests, which inject tmux_running directly). Exclude the unit's own MainPID: what remains is
    # a process running this daemon that systemd did NOT start -- the real stray.
    ps = subprocess.run(["ps", "-eo", "pid=,args="], capture_output=True, text=True)
    rows: list[tuple[int, str]] = []
    if getattr(ps, "returncode", 1) == 0:
        for line in (ps.stdout or "").splitlines():
            pid_s, _, args = line.strip().partition(" ")
            try:
                rows.append((int(pid_s), args))
            except ValueError:
                continue
    for e in entries:
        own = _unit_main_pid(e["session"]) if e.get("owner") == "systemd" else 0
        stray = any(_runs_daemon(args, e["match"]) and pid != own for pid, args in rows)
        if e["session"] in sessions or stray:
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


def pull_loop_status(health: dict | None, enable_on: bool, *,
                     now: float | None = None, stale_after: float = 3600.0) -> dict:
    """PURE predicate (mutation-testable): classify the transport from its last-fire health
    record + whether the loop is enabled. REPORT ONLY. Returns {status, alarm, detail}.

      DISABLED      loop off (kill switch) -> autonomy deliberately paused         (no alarm)
      HEALTHY_DREW  last fire drew work                                            (no alarm)
      HEALTHY_IDLE  last fire allow-stopped: no drawable work / paused             (no alarm)
      LOOP_BROKEN   last fire hit a draw/import error -> cannot draw               (ALARM)
      LOOP_STALE    a healthy record frozen while ENABLED -> hook stopped firing   (ALARM)
      UNKNOWN       no / unrecognised health record                               (no alarm)

    THE distinction the director required: HEALTHY_IDLE ('idle because no grant / no work')
    reads DIFFERENTLY from LOOP_BROKEN ('idle because the loop is broken').

    FRESHNESS (`now`, 2026-07-17 HARDEN): the outcome-only classification was time-BLIND -- a
    dead/hung worker whose Stop hook stops firing entirely (crash, hook exception before the
    health write, session-id mismatch) leaves the record FROZEN at its last healthy value, which
    read HEALTHY_DREW forever: the exact day-long fail-silent this atom exists to kill, arriving
    via staleness instead of an error outcome (the named backstops -- deadman commit-clock,
    reconciler MISSING -- can't distinguish it: the commit-clock reads a director-gated idle the
    same as a dead worker, and the process may be UP with only its transport dead). When a clock is
    supplied and a healthy record is older than `stale_after` WHILE ENABLED, it is LOUD. Strictly
    more-conservative (adds an alarm, removes none). `now=None` -> freshness skipped (pure,
    back-compat)."""
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
    if outcome == "ALLOW_STOP_SCHEDULED":
        # SCHEDULED-INVOCATION MODE (SCHEDULED_BOUNDED_INVOCATIONS_DESIGN.md, 2026-07-20): after the
        # cutover the Stop hook no longer owns continuity -- the external systemd timer/path
        # (worker_tick.py) does. The hook only fires when a session stops, and at rest NO session is
        # running, so this record freezes BY DESIGN. Placed BEFORE the freshness gate (same class as
        # DISABLED / ALLOW_STOP_QUIET_WAIT): a frozen scheduled record is a healthy rest, NOT a
        # dead/hung worker, and must NOT page. Scheduled-mode liveness is the worker-tick.timer/.path
        # unit state (reconcile drift alarms on a missing/failed unit) + the deadman commit clock --
        # NOT this record. A genuinely broken scheduled worker stops committing -> the commit clock
        # STALLs, and/or its unit fails -> reconcile pages.
        return {"status": "HEALTHY_IDLE", "alarm": False,
                "detail": "scheduled-invocation mode -- external timer/path owns continuity (NOT this hook); "
                          "frozen record is a healthy rest; liveness = unit state + commit clock"}
    if outcome == "ALLOW_STOP_QUIET_WAIT":
        # DRAINED-AND-GATED quiet wait (ADVISOR_STEER 2026-07-18, item 1): below-target work is
        # exhausted and the remainder is blocked on a director act, so the only draw would be at-
        # target HARDEN re-verification -- the treadmill the director correctly declines. A
        # LEGITIMATE resting state, NOT a broken loop. FRESHNESS-EXEMPT (placed BEFORE the gate,
        # same class as DISABLED): the loop deliberately stops firing while resting, so a stale
        # quiet-wait record must NOT read as a frozen/dead worker and page the director. A
        # genuinely new signal re-enters via find_work's primary/lane paths and the loop resumes.
        return {"status": "HEALTHY_IDLE", "alarm": False,
                "detail": "drained-and-gated quiet wait -- resting, blocked on a director act (NOT broken)"}
    # FRESHNESS gate (the alarm outcomes above already returned; only resting/healthy states remain).
    # A frozen healthy record while ENABLED means the transport stopped firing -> LOUD, not healthy.
    if now is not None:
        ts = health.get("ts")
        if isinstance(ts, (int, float)) and (now - ts) > stale_after:
            return {"status": "LOOP_STALE", "alarm": True,
                    "detail": (f"pull-loop transport frozen: last fire {int((now - ts) // 60)}m ago "
                               f"(>{int(stale_after // 60)}m) while ENABLED -- hook stopped firing "
                               f"(dead/hung worker); reads {outcome!r} but is stale")}
    if outcome == "HEARTBEAT_REARM":
        # REST HEARTBEAT (LOOP_CONTINUITY_REARM_DESIGN.md, 2026-07-19): the drained-and-gated seat now
        # keeps its turn-chain ALIVE with a keep-alive continuation each hold window instead of allow-
        # stopping into a dead chain. Deliberately placed AFTER the freshness gate (unlike the old
        # freshness-EXEMPT ALLOW_STOP_QUIET_WAIT): a healthy resting seat re-stamps this every <=HOLD
        # (< the default 1h stale window), so a STALE heartbeat means the beat STOPPED -- a dead/hung
        # worker -- and MUST read LOUD via the gate above. Fresh => a legitimate, alive rest.
        return {"status": "HEALTHY_IDLE", "alarm": False,
                "detail": "rest heartbeat: chain alive, waiting for new work (freshness-checked -- a stopped beat alarms)"}
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
    return pull_loop_status(read_pull_loop_health(), pull_loop_enabled(), now=time.time())


# ── Deployment-by-construction: is the code this daemon LOADS stale? (PW1, rebuilt 2026-08-09) ──
# A managed daemon stamps the git SHA it booted from (its unit's ExecStartPre → boot_sha.stamp).
#
# The ORIGINAL question was "has HEAD moved past that stamp?" — and it had BOTH failure modes the
# director named in DIRECTOR_STEER_SECOND_PUBLISH_WEDGE_2026-08-09:
#   BLIND  — its population came from the manifest's `launched_by` field, so the seven rows the
#            2026-07-29 cutover left un-flipped (sim-runner and background-worker among them, the
#            two daemons that ran pre-cure code through the 10h wedge) were excluded BY DECLARATION
#            from the answer. A declaration can drift; an observation cannot.
#   ALWAYS RED — on a repo that commits every tick, "HEAD moved" is true for every daemon minutes
#            after boot. "A detector for that failure mode that is always red will be ignored
#            exactly as reliably as one that is blind" (DECIDED #2).
# So both halves are rebuilt here, and NEITHER is sufficient alone:
#   (a) POPULATION = every daemon OBSERVED running under its own --user systemd unit (unit active +
#       MainPID + /proc cgroup cross-check). The manifest is now the CROSS-CHECK that alarms on
#       disagreement (`launcher_drift` → MISDECLARED_LAUNCHER), never the filter that shrinks.
#   (b) SIGNAL = the modules this daemon ACTUALLY IMPORTS (background.code_closure) that changed
#       between its boot SHA and the working tree. Untouched closure → GREEN however far HEAD ran;
#       one changed imported module → RED even if nothing else moved.
# REPORT ONLY (the deploy step — systemctl restart — is separate, G-D2).

def _proc_cgroup(pid: int) -> str:
    """The cgroup line of a live pid ('' if unreadable). A user-scope systemd daemon's cgroup
    names its own unit (…/app.slice/sim-runner.service). Used to REFUTE a claimed systemd launch,
    never to require one — an unreadable /proc must not shrink the population (that is the very
    fail-open shape this rebuild exists to close)."""
    try:
        return Path(f"/proc/{int(pid)}/cgroup").read_text()
    except Exception:
        return ""


#: systemd renders every absolute timestamp it shows in the BOX'S LOCAL ZONE, to the second:
#: `Fri 2026-09-25 12:04:00 BST`. The zone abbreviation is dropped rather than parsed -- `%Z`
#: cannot round-trip `BST` on this box, and the rendered clock is already local, so reading the
#: naive datetime back through the local zone is the identity. Truncation to the second is the
#: reason the comparisons below are all `<` against a whole-second floor and never an equality.
def _systemd_timestamp(text: str) -> float | None:
    """Epoch seconds for a systemd-rendered timestamp, or None if it is `n/a`/unparsable."""
    parts = (text or "").strip().split()
    for i, token in enumerate(parts[:-1]):
        if len(token) == 10 and token.count("-") == 2:
            try:
                return datetime.datetime.strptime(
                    f"{token} {parts[i + 1]}", "%Y-%m-%d %H:%M:%S").timestamp()
            except ValueError:
                return None
    return None


def parse_exec_records(value: str) -> list[dict]:
    """PURE. systemd's `ExecStartPre` property is one `{ k=v ; k=v ; ... }` record per declared
    command; return them as dicts, with `start_time`/`stop_time` already in epoch seconds.

    The bracketed timestamps are systemd's own record of when it ran THAT command on THIS boot,
    written from the same wall clock `boot_sha.stamp` writes its `ts` from -- which is the whole
    reason this parser exists (see `unit_stamper_run`)."""
    out: list[dict] = []
    for line in (value or "").splitlines():
        line = line.strip()
        if not (line.startswith("{") and line.endswith("}")):
            continue
        record: dict = {}
        for field in line[1:-1].split(" ; "):
            if "=" not in field:
                continue
            key, raw = field.split("=", 1)
            key, raw = key.strip(), raw.strip()
            if key in ("start_time", "stop_time"):
                record[key] = _systemd_timestamp(raw.strip("[]"))
            elif key == "status":
                record[key] = int(raw) if raw.lstrip("-").isdigit() else None
            elif key == "ignore_errors":
                record[key] = raw == "yes"
            else:
                record[key] = raw
        if record:
            out.append(record)
    return out


def stamper_record(records: list[dict]) -> dict | None:
    """PURE. The one exec record among `records` that runs the boot stamper, or None.

    Selected by what the record's own `argv[]` NAMES, never by position: a unit is free to declare
    other `ExecStartPre` commands before or after this one, and a positional read would silently
    start grading a different command's exit status the day one is added."""
    for record in records:
        argv = (record.get("argv[]") or "").split()
        if any(a.endswith("boot_sha") or a.endswith("boot_sha.py") for a in argv):
            return record
    return None


def unit_stamper_run(session: str, show=None) -> dict:
    """What systemd itself recorded about THIS boot's run of `session`'s declared boot stamper:
    `{"ran_at": epoch|None, "finished_at": epoch|None, "status": int|None}`.

    THE DEFECT THIS EXISTS FOR, measured 2026-09-25 on eleven live daemons. The staleness rules
    had to ask "was this stamp written by the process running now", and the only clock they had was
    `process_start_time` -- `/proc/stat btime` plus the process's start ticks. On this WSL2 guest
    those two are NOT the same clock: the guest freezes, the monotonic side stops while the wall
    side does not, and `btime` (derived as now-minus-uptime) walks FORWARD. Measured against
    systemd's own record: `token-proxy` reconstructed to 2026-09-16 04:25:20 for a process systemd
    started at 2026-09-15 13:47:55 -- 14h37m of error, and 14h37m is the box's accumulated freeze,
    not noise. Both `token-proxy` and `worker-seat-manager` had stamped in the same SECOND systemd
    started them and were graded `stamp-predates-process` anyway: 2 of the 10 unresolved rows were
    the instrument's clock, not the fleet's.

    systemd's bracketed `start_time` is the escape (the shape from `feedback_a_liveness_signal_
    delivered_through_the_channel_it_monitors...`): an ABSOLUTE stamp, in the wall clock the
    stamper itself writes, recorded by the thing that did the starting. It also carries the
    stamper's EXIT STATUS, which no restart-dated clock can supply at all.

    Fail-closed: anything unreadable returns all-None, and every rule keyed to these values makes
    NO claim on None -- an unanswerable question can never turn a red into a green.
    """
    runner = _show_exec_start_pre if show is None else show
    try:
        record = stamper_record(parse_exec_records(runner(session)))
    except Exception:  # noqa: BLE001 -- cannot read != the stamper is fine
        record = None
    if not record:
        return {"ran_at": None, "finished_at": None, "status": None}
    return {"ran_at": record.get("start_time"), "finished_at": record.get("stop_time"),
            "status": record.get("status")}


def _show_exec_start_pre(session: str) -> str:
    r = subprocess.run(
        ["systemctl", "--user", "show", f"{session}.service", "-p", "ExecStartPre", "--value"],
        capture_output=True, text=True,
    )
    return r.stdout or "" if getattr(r, "returncode", 1) == 0 else ""


def observed_launched_by(entries: list[dict], unit_states: dict[str, dict],
                         main_pids: dict[str, int],
                         cgroup_of=lambda pid: "") -> dict[str, str | None]:
    """PURE. session -> the launcher OBSERVED to be running it right now ('systemd' | None).

    'systemd' iff the unit is ACTIVE with a real MainPID, and the /proc cgroup cross-check does not
    REFUTE it (cgroup unreadable → not a refutation; cgroup naming a DIFFERENT unit → refuted).
    Declared `launched_by` is deliberately NOT read here — that is the whole point."""
    observed: dict[str, str | None] = {}
    for e in entries:
        session = e.get("session", "")
        if e.get("match") == SEAT_MATCH or e.get("owner") != "systemd":
            continue
        st = unit_states.get(session) or {}
        pid = main_pids.get(session, 0)
        if not st.get("active") or pid <= 0:
            observed[session] = None
            continue
        cg = cgroup_of(pid)
        refuted = bool(cg) and f"{session}.service" not in cg
        observed[session] = None if refuted else "systemd"
    return observed


def drift_population(observed: dict[str, str | None]) -> list[str]:
    """PURE. The sessions the staleness detector MUST evaluate: everything observed to be running
    under systemd. Equal to the observed running set BY CONSTRUCTION — no declaration filter can
    make it a subset (the 2026-07-29 defect)."""
    return sorted(s for s, v in observed.items() if v == "systemd")


def launcher_drift(entries: list[dict], observed: dict[str, str | None]) -> list[dict]:
    """PURE. Rows whose declared `launched_by` disagrees with the observed world. A row claiming
    tmux for a daemon observed under systemd is MISDECLARED_LAUNCHER: it is double-launchable AND
    (before this rebuild) it silently deleted itself from the drift population. Now the wrong row
    FAILS LOUD instead of shrinking the answer."""
    out = []
    for e in entries:
        session = e.get("session", "")
        if e.get("match") == SEAT_MATCH or e.get("owner") != "systemd":
            continue
        declared = e.get("launched_by", "tmux")
        if observed.get(session) == "systemd" and declared != "systemd":
            out.append({"session": session, "declared": declared, "observed": "systemd",
                        "status": "MISDECLARED_LAUNCHER", "alarm": True})
    return out


def loaded_code_drift(running_sessions, boot_shas: dict[str, str | None],
                      closures: dict[str, set[str]], changed_since, *,
                      boot_ts: dict[str, float | None],
                      stamper_ran_at: dict[str, float | None],
                      stamper_exit: dict[str, int | None]) -> dict:
    """PURE (mutation-testable). Per running daemon, which of the modules IT IMPORTS changed since
    it booted. `changed_since(sha, session)` -> set of repo-relative changed paths, or None if
    unresolvable. SESSION is passed because the answer is per-daemon, not per-commit: two daemons
    booted at the same SHA minutes apart loaded different working trees, and from 2026-09-04 the
    comparison is against the bytes each ACTUALLY loaded (see `boot_sha.read_boot_blobs`).

    Returns {"stale": {session: [changed loaded paths]}, "unresolved": {session: reason}}.
    Five fail-SAFE (never fail-open) rules, each with a named reason rather than a silent green:
      - no boot stamp        -> unresolved 'unstamped'      (unknown is not clean)
      - the unit's own stamper exited non-zero on this boot
                             -> unresolved 'stamper-failed'
      - stamp older than this boot's run of that stamper
                             -> unresolved 'stamp-predates-process'
      - closure empty        -> unresolved 'closure-unknown' (a vacuous compare always passes)
      - changed_since None   -> unresolved 'sha-unresolved'  (an unanswerable question is not 'no')
    A daemon with a resolvable diff that touches NOTHING it imports is GREEN — that is the whole
    point: the signal must be able to be green, or it is noise.

    THE FOURTH RULE, added 2026-09-24, and why the other three could not cover it. `unstamped`
    asks whether a stamp EXISTS. Nothing asked whether the stamp describes the process running
    NOW. From 2026-09-04 to 2026-09-24 the units' declared `ExecStartPre` stamper had no
    `__main__` and silently stamped nothing (the leading `-` in the unit swallowed it), so every
    stamp on the box named a boot that had since been replaced. Those read as perfectly valid
    stamps: 9 of 12 daemons were reported `stale` continuously, which is the ALWAYS-RED failure
    the 2026-08-09 rebuild above exists to abolish, and it is precisely why nobody could see the
    2h48m window in which `staging_watcher` ran without the `reask()` that 465a0dfca had landed —
    the session read `stale` before it, during it and after it. "The code moved under a running
    daemon" and "nothing stamped this boot" have OPPOSITE remedies (restart it / repair the
    stamper) and had one indistinguishable verdict.

    THE FIFTH RULE, added 2026-09-25, and why it is not the `-` prefix. `stamper-failed` reads the
    exit status systemd ALREADY records for the ExecStartPre it ran. Dropping the units' leading
    `-` would promote the same non-zero exit into twelve daemons refusing to start, and
    `probe_declared_stamper` below measured why that trade is bad: the twenty-day outage exited
    **0** throughout, so the `-` was never what hid it. Reading the status costs no outage and
    names the one condition the stamp's own age cannot distinguish — a stamper that RAN and FAILED
    (repair it) from a stamp that is simply old (restart the daemon).

    WHICH CLOCK THE THIRD RULE COMPARES AGAINST is the whole of its correctness, and it was wrong
    until 2026-09-25: see `unit_stamper_run`. `stamper_ran_at` is when systemd began THIS boot's
    run of the unit's own stamper, in the same wall clock the stamp is written in — not a process
    start reconstructed from `/proc/stat btime`, which on this frozen-guest box was 14h37m out and
    misgraded two daemons that had stamped in the same second they started.

    `boot_ts`, `stamper_ran_at` and `stamper_exit` are REQUIRED keyword arguments, not optional
    ones, because a rule a caller can forget to feed is a rule that stays green for twenty days. A
    session with any value unknown makes NO new claim and falls through to the rules below — that
    degrades to the previous answer and can never turn a red into a green."""
    stale: dict[str, list[str]] = {}
    unresolved: dict[str, str] = {}
    for session in running_sessions:
        sha = boot_shas.get(session)
        if not sha:
            unresolved[session] = "unstamped"
            continue
        status = stamper_exit.get(session)
        if status is not None and status != 0:
            unresolved[session] = "stamper-failed"
            continue
        stamped, ran = boot_ts.get(session), stamper_ran_at.get(session)
        if stamped is not None and ran is not None and stamped < ran:
            unresolved[session] = "stamp-predates-process"
            continue
        closure = closures.get(session) or set()
        if not closure:
            unresolved[session] = "closure-unknown"
            continue
        changed = changed_since(sha, session)
        if changed is None:
            unresolved[session] = "sha-unresolved"
            continue
        hit = sorted(set(changed) & closure)
        if hit:
            stale[session] = hit
    return {"stale": stale, "unresolved": unresolved}


#: Where systemd user units ACTUALLY live on this box. The probe below reads the INSTALLED copy,
#: never the text `generate_units.regenerate()` would produce. The generated text is what the repo
#: declares, and the commit gate already proves that stamps
#: (`test_the_units_own_declared_stamp_command_stamps`); the installed copy is what systemd will
#: really run, and it is the only side that can drift without a commit -- which is exactly the gap
#: measured on 2026-09-24, when the repair was at HEAD and the daemons restarted 7m18s before it
#: reached the disk they read.
INSTALLED_UNIT_DIR = Path.home() / ".config" / "systemd" / "user"

#: systemd's ExecStartPre= prefix characters: `-` ignore-failure, `@` set argv0, `+`/`!`/`!!`
#: privilege. They are part of the SETTING, not of the command, and must come off before exec.
_EXEC_PREFIXES = "-@+!:"

#: The verdict that means the stamper is alive. `ok` is derived from this ONE value rather than
#: from a list of bad ones, so a verdict added later is not-ok BY CONSTRUCTION. A fail-open probe
#: is the failure this whole mechanism exists to stop repeating.
_STAMPER_OK = "works"


def declared_stamp_argv(unit_dir: Path | None = None) -> dict[str, list[str]]:
    """`{unit_filename: argv}` for every INSTALLED unit whose `ExecStartPre` runs the boot stamper.

    PARSED out of the unit text, never retyped -- keyed to the property ("whatever the unit
    declares is what gets run"), so renaming the module or changing the interpreter path moves the
    probe with it instead of leaving it asserting a string nothing executes.
    """
    directory = INSTALLED_UNIT_DIR if unit_dir is None else Path(unit_dir)
    out: dict[str, list[str]] = {}
    try:
        units = sorted(directory.glob("*.service"))
    except Exception:
        return out
    for unit in units:
        try:
            text = unit.read_text()
        except Exception:
            continue
        for line in text.splitlines():
            if not line.strip().startswith("ExecStartPre="):
                continue
            argv = (line.strip().split("=", 1)[1]).lstrip(_EXEC_PREFIXES).split()
            if any(a.endswith("boot_sha") or a.endswith("boot_sha.py") for a in argv):
                out[unit.name] = argv
                break
    return out


def _stamp_probe_shape(argv: list[str], session: str) -> tuple:
    """The argv with the unit's own session name blanked, so twelve units declaring the same
    command in twelve spellings of one session collapse to ONE shape to probe."""
    return tuple("<session>" if a == session else a for a in argv)


def _run_stamp_argv(argv: list[str], env: dict) -> subprocess.CompletedProcess:
    # cwd matches the units' own `WorkingDirectory=`; without it `-m background.boot_sha` would
    # resolve against whatever the caller happened to be in and the probe would answer a different
    # question from the one systemd asks.
    return subprocess.run(argv, cwd=_HERE.parent, capture_output=True, text=True,
                          timeout=180, env=env)


def _probe_one_stamp_shape(unit: str, argv: list[str], run) -> dict:
    """Run ONE declared stamp command against a throwaway BOOT_DIR and grade what it did.

    The oracle is a FILE APPEARING IN A TEMP DIRECTORY, not the command's exit status, because the
    twenty-day defect exited 0 the whole time (measured 2026-09-24: the `__main__`-less blob exits
    0 and writes nothing). A probe that graded the exit code would have been green throughout.
    """
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        env = dict(os.environ, SE_BOOT_DIR=td)
        try:
            proc = run(argv, env)
        except Exception as exc:  # noqa: BLE001 -- cannot run != the stamper is fine
            return {"unit": unit, "verdict": "unprobed", "detail": f"could not run {argv}: {exc}"}
        written = sorted(Path(td).glob("*.json"))
        if proc.returncode != 0:
            err = (proc.stderr or "").strip().splitlines()
            return {"unit": unit, "verdict": "failed",
                    "detail": f"exit {proc.returncode}: {err[-1] if err else 'no stderr'}"}
        if not written:
            # THE NAMED DEFECT. Exit 0 and nothing written is what ran for twenty days behind a
            # leading `-`, and it had no name, so nothing could report it.
            return {"unit": unit, "verdict": "silent",
                    "detail": "exited 0 and wrote no boot record"}
        try:
            record = json.loads(written[0].read_text())
        except Exception as exc:  # noqa: BLE001
            return {"unit": unit, "verdict": "unreadable", "detail": f"{written[0].name}: {exc}"}
        if not record.get("sha"):
            return {"unit": unit, "verdict": "sha-unknown",
                    "detail": "stamped, but recorded no SHA -- the stamp cannot date anything"}
        return {"unit": unit, "verdict": _STAMPER_OK,
                "detail": f"stamped {written[0].name} at {str(record.get('sha'))[:9]}"}


def probe_declared_stamper(unit_dir: Path | None = None, run=None) -> dict:
    """Does the boot stamper THE INSTALLED UNITS DECLARE actually stamp? Answered by running it.

    THE DEFECT THIS EXISTS FOR. `stamp-predates-process` can only tell a dead stamper from a live
    one AT A RESTART -- and the stamping population is exactly the population that never restarts.
    Censused 2026-09-24: of 24 installed units, the 12 that declare the stamper are long-lived
    daemons whose newest start was 07:10:34, while the 7 that restart several times an hour
    declare no stamp line at all. The two sets are disjoint, so a restart-triggered signal over
    them goes dark BY CONSTRUCTION -- and `deploy_restart.restart_plan` correctly HOLDs on
    `stamp-predates-process`, so nothing in the system will ever restart those 12 on its account.

    This probe needs no restart. It runs on whatever cadence its caller has, which is why it can
    catch the 2026-09-04 regression on the day it happens rather than at the next reboot.

    NOT the `-` prefix's fault, and the `-` deliberately STAYS. Measured 2026-09-24 by running the
    historical `__main__`-less blob as the unit declares it: **exit 0, zero files written**.
    Dropping the `-` promotes only NON-ZERO exits, so it would not have caught one minute of the
    twenty days -- while converting any future stamper fault into twelve daemons that refuse to
    start. That trades an observability gap for an outage and still misses this defect. So the
    failure is reported instead, here, on a surface that is read.
    """
    runner = _run_stamp_argv if run is None else run
    declared = declared_stamp_argv(unit_dir)
    if not declared:
        where = INSTALLED_UNIT_DIR if unit_dir is None else unit_dir
        return {"verdict": "undeclared", "ok": False, "declaring_units": 0, "probes": [],
                "detail": f"no installed unit under {where} declares the boot stamper"}

    shapes: dict[tuple, tuple[str, list[str]]] = {}
    for unit, argv in sorted(declared.items()):
        session = unit[: -len(".service")] if unit.endswith(".service") else unit
        shapes.setdefault(_stamp_probe_shape(argv, session), (unit, argv))

    probes = [_probe_one_stamp_shape(unit, argv, runner) for unit, argv in shapes.values()]
    bad = [p for p in probes if p["verdict"] != _STAMPER_OK]
    worst = bad[0] if bad else probes[0]
    return {"verdict": worst["verdict"],
            "ok": not bad,
            "declaring_units": len(declared),
            "probes": probes,
            "detail": f"{worst['unit']}: {worst['detail']}"
                      + (f" ({len(declared)} unit(s) declare it)" if not bad else "")}


def evaluate_boot_sha_drift() -> dict:
    """Live wrapper. Population = OBSERVED systemd daemons; signal = their own loaded modules.
    Returns {head, population, graded, stale, stale_detail, unresolved, misdeclared, vacuous}.
    `stale` stays a list of session names (health_check's existing consumer). REPORT ONLY.

    `graded` IS THE DENOMINATOR AND IT IS NOT DECORATION. Measured on this box 2026-09-25: 11
    daemons in the population, 10 unresolved, so `stale: []` was `0 out of 1` published in the
    shape of `0 out of 11` — and `deploy_restart --report` duly printed `stale 0` at a fleet whose
    running code version was unknown for all but one member. This is the same failure as the level
    grader's `contradicted: 0` out of 0 graded, in a second instrument, and the remedy is the same:
    publish the population a verdict was actually REACHED over, counted through this function's own
    partition, never asserted alongside it."""
    from background import boot_sha, code_closure
    entries = load_manifest()
    unit_states = _live_unit_states()
    main_pids = {e["session"]: _unit_main_pid(e["session"])
                 for e in entries if e.get("owner") == "systemd" and e.get("match") != SEAT_MATCH}
    observed = observed_launched_by(entries, unit_states, main_pids, _proc_cgroup)
    population = drift_population(observed)
    closures = {s: code_closure.closure_for_session(s) for s in population}
    boot_shas = {s: boot_sha.read_boot_sha(s) for s in population}
    stamper_runs = {s: unit_stamper_run(s) for s in population}
    d = loaded_code_drift(
        population, boot_shas, closures,
        lambda sha, session: boot_sha.changed_paths_since(sha, boot_sha.read_boot_blobs(session)),
        boot_ts={s: boot_sha.read_boot_ts(s) for s in population},
        stamper_ran_at={s: r["ran_at"] for s, r in stamper_runs.items()},
        stamper_exit={s: r["status"] for s, r in stamper_runs.items()})
    # VACUITY GUARD (R15): an empty population while units are demonstrably active is a FAILED
    # check, not a clean one. The old detector's silent shrink is what this must never repeat.
    any_active = any((unit_states.get(e["session"]) or {}).get("active")
                     for e in entries if e.get("owner") == "systemd")
    return {"head": boot_sha.current_head(),
            "population": population,
            # Derived by SUBTRACTION through the partition the rules above actually produce, so a
            # rule added later shrinks `graded` by construction. A `graded` recomputed from its own
            # idea of who was resolvable would agree with itself and drift from the verdict.
            "graded": sorted(set(population) - set(d["unresolved"])),
            "stale": sorted(d["stale"]),
            "stale_detail": d["stale"],
            "unresolved": d["unresolved"],
            "misdeclared": launcher_drift(entries, observed),
            # Is the instrument itself alive? Every verdict above is computed FROM the stamps, so
            # all of them are silently vacuous when nothing writes stamps -- which was true of this
            # box for twenty days. This one field is the only answer here that does not come
            # through the channel it is reporting on.
            "stamper": probe_declared_stamper(),
            "vacuous": bool(any_active and not population)}


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
    try:  # seat guard, FIRST act -- refuse to start on foreign soil (background/_seat.py)
        from background._seat import refuse_if_foreign
    except ModuleNotFoundError:  # launched as `python3 background/process_reconciler.py`
        from _seat import refuse_if_foreign
    refuse_if_foreign("process_reconciler")
    import sys
    raise SystemExit(_main(sys.argv))
