#!/usr/bin/env python3
"""Scheduled bounded invocation — the continuity tick (SCHEDULED_BOUNDED_INVOCATIONS_DESIGN.md, 2026-07-20).

Fired by systemd `worker-tick.timer` (every 60s) and `worker-tick.path` (immediately on a new
staged doc). It replaces the persistent stop-hook-rearm worker seat and its rest-heartbeat, which
failed three independent ways in ~30h (input-blocking 27min, death-on-API-error ~6h, token-burn at
rest ~128.7k tok/h) — all from a resident turn-chain that must pay inference to stay alive.

THE WHOLE JOB (cheap Python, NO model inference):
  1. Autonomy enabled?  (.build_executor_enabled, fail-closed)          -> else exit 0
  2. Scheduled mode on?  (.scheduled_invocations_enabled)               -> else exit 0 (dark/pre-cutover)
  3. An invocation already live?  (lockfile + live-pid check)           -> else exit 0 (no stacking)
  4. Sync origin-staged docs (RC3) + find_work() — the sole draw authority.
       - no work (drained-and-gated)  -> exit 0    <== ZERO tokens: this is what makes rest cheap (P1)
       - work                          -> spawn ONE `claude -p "<doorbell>"` (headless,
                                          env SE_SBI_WORKER=1), record its pid in the lock, exit.

The spawned invocation runs its NATURAL agentic session (read/edit/test/commit) and EXITS — no
self-re-arm. The next tick starts a fresh one if work remains. Death of an invocation is a skipped
tick, not an outage (the next tick recovers from disk state).

WORKER IDENTITY: the tick sets SE_SBI_WORKER=1 on the invocation it spawns; the Stop hook
(pull_next_work.py, scheduled-mode) discriminates the worker by that inherited env var, NOT by a
pinned session id. So there is no identity to drift (the 2026-07-19 deadlock class is deleted).

DARK BY DEFAULT: this does nothing until `docs/observability/.scheduled_invocations_enabled` exists
(created at the director-run cutover). Installing the units is inert until then — enabling scheduled
continuity is a deliberate act, never a side effect of merging.
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from background.secrets_location import scrub_model_facing_env  # noqa: E402

# THE single kill switch for ALL autonomous execution (same flag the Stop hook reads — no second
# flag; DIRECTOR_ANSWERS_C7 #6). Console-only/director-reserved. FAIL-CLOSED.
ENABLE_FLAG = PROJECT_DIR / "docs" / "observability" / ".build_executor_enabled"
# Scheduled-mode flag: the cutover switch. While ABSENT, the persistent-seat heartbeat is live and
# this tick is inert (belt-and-braces so a stray timer pre-cutover can never double-drive the seat).
SCHEDULED_FLAG = PROJECT_DIR / "docs" / "observability" / ".scheduled_invocations_enabled"
LOCK_FILE = PROJECT_DIR / "docs" / "observability" / ".worker_tick.lock"
LOG_FILE = PROJECT_DIR / "docs" / "observability" / "worker-tick-log.md"
HEALTH_FILE = PROJECT_DIR / "docs" / "observability" / ".worker_tick_health.json"
# RAIL-3 HEARTBEAT (DIRECTOR_RULING_HEARTBEAT_AND_QUIET_CLASSIFICATION 2026-07-24). Unlike LOG_FILE
# and HEALTH_FILE (both .gitignored -> never leave this machine), this lives under site/data/, which
# process_run_complete.py commits WHOLE every publish cycle. So the tick verdict is fetchable from
# ORIGIN without SSH -- the ruling's acceptance test. Placed here (not worker-tick-log.md) because a
# liveness signal the advisor cannot fetch is fail-silent.
HEARTBEAT_FILE = PROJECT_DIR / "site" / "data" / "tick_heartbeat.json"
HEARTBEAT_RECENT_MAX = 15
# Map the raw tick outcome onto the director's three verdict classes (drew / rested / exception),
# plus 'paused' for the kill-switch / pre-cutover states that are neither work nor rest.
_VERDICT_CLASS = {
    "SPAWNED": "drew",
    "LOCK_HELD": "drew",        # a prior invocation is still running -- the machine IS drawing
    "REST_NO_WORK": "rested",
    "DRAW_ERROR": "exception",
    "DISABLED": "paused",
    "NOT_SCHEDULED": "paused",
}

MODEL = "claude-opus-5"

# Worker preamble prepended to the drawn doorbell. R7: the reason is a DOORBELL — act on real
# disk/git state, not this text. The invocation re-orients, does the drawn work, and EXITS.
WORKER_PREAMBLE = (
    "You are the autonomous worker, woken by a scheduled tick because there is work to do. "
    "This is a bounded invocation: do the drawn work on REAL disk/git state, commit it via "
    "tree_lock, then STOP and exit cleanly. Do NOT try to keep yourself alive or re-arm — the "
    "scheduler starts the next invocation if more work remains. Drawn work follows.\n\n"
)


def _log(msg: str) -> None:
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(f"- [{time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}] {msg}\n")
    except Exception:
        pass


def _write_health(outcome: str, detail: str = "") -> None:
    """Typed tick-health signal (mirrors the pull-loop's HEALTH_FILE so the reconciler/deadman can
    read scheduled-mode liveness the same way). outcome: SPAWNED | REST_NO_WORK | DISABLED |
    NOT_SCHEDULED | LOCK_HELD | DRAW_ERROR. Never raises."""
    try:
        HEALTH_FILE.parent.mkdir(parents=True, exist_ok=True)
        HEALTH_FILE.write_text(json.dumps(
            {"ts": time.time(), "outcome": outcome, "detail": detail[:500]}))
    except Exception:
        pass


def _enumeration_line() -> str:
    """The whole-set enumeration (every authorized level + drawable Y/.) as one line, per the
    ruling's 'timestamp · drew/rested/exception · the whole-set enumeration'. Best-effort: a pure
    read of the maturity map (NO inference), imported lazily so a gated tick pays nothing. Never
    raises -- a heartbeat must ship even if the enumeration can't be computed."""
    try:
        from background.supervisor import authorized_set_enumeration_line
        return authorized_set_enumeration_line()
    except Exception as e:  # pragma: no cover - defensive
        return f"(enumeration unavailable: {e!r})"


def _write_heartbeat(decision: "TickDecision", enumeration: str) -> None:
    """Write the origin-verifiable tick heartbeat (see HEARTBEAT_FILE). One line per tick:
    timestamp · verdict(drew/rested/exception) · whole-set enumeration, plus a rolling `recent`
    window so 'is it actually ticking' is answerable from advancing timestamps alone. No inference,
    never raises -- liveness reporting must not itself be able to wedge the tick."""
    ts = time.time()
    iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts))
    verdict = _VERDICT_CLASS.get(decision.outcome, decision.outcome.lower())
    line = f"[{iso}] {verdict} ({decision.outcome}) -- {enumeration}"
    record = {
        "ts": ts,
        "ts_iso": iso,
        "verdict": verdict,               # drew | rested | exception | paused
        "outcome": decision.outcome,      # raw TickDecision outcome
        "detail": decision.detail[:300],
        "enumeration": enumeration,       # the whole-set enumeration line (every level, Y/.)
        "line": line,                     # the single human-readable line the ruling asks for
    }
    try:
        HEARTBEAT_FILE.parent.mkdir(parents=True, exist_ok=True)
        recent: list = []
        if HEARTBEAT_FILE.is_file():
            try:
                recent = (json.loads(HEARTBEAT_FILE.read_text()).get("recent") or [])
            except Exception:
                recent = []
        record["recent"] = ([line] + recent)[:HEARTBEAT_RECENT_MAX]
        HEARTBEAT_FILE.write_text(json.dumps(record, indent=2))
    except Exception:  # pragma: no cover - defensive
        pass


def autonomy_enabled() -> bool:
    """THE kill switch, FAIL-CLOSED. Autonomy runs ONLY if ENABLE_FLAG is a readable regular file.
    Missing / a directory / unreadable => DISABLED. Never raises."""
    try:
        if not ENABLE_FLAG.is_file():
            return False
        ENABLE_FLAG.read_text()
        return True
    except OSError:
        return False


def scheduled_mode() -> bool:
    """Cutover switch. Scheduled continuity is live ONLY if SCHEDULED_FLAG is a readable regular
    file. Absent => dark (persistent-seat heartbeat still owns continuity). Never raises."""
    try:
        return SCHEDULED_FLAG.is_file() and (SCHEDULED_FLAG.read_text() or True) is not None
    except OSError:
        return False


def _pid_alive(pid: int) -> bool:
    """True if a process with this pid exists. Uses /proc existence (Linux), NOT os.kill/signals:
    the tick must never send a signal to any process (systemd's worker-tick.service TimeoutStartSec
    owns invocation termination, not this code) -- keeping this file free of any kill-call preserves
    the no-reaper safety invariant (test_process_reconciler). Best-effort; False on any error."""
    try:
        return Path(f"/proc/{pid}").exists()
    except Exception:
        return False


def invocation_in_flight() -> bool:
    """True if a prior invocation is still running (its pid in the lockfile is alive). A STALE lock
    (pid dead / file absent / malformed) reads as NOT in-flight so a crashed invocation never wedges
    the tick forever — the next tick reclaims it. Never raises."""
    try:
        if not LOCK_FILE.is_file():
            return False
        data = json.loads(LOCK_FILE.read_text())
        pid = int(data.get("pid", 0))
        return pid > 0 and _pid_alive(pid)
    except Exception:
        return False  # malformed/unreadable lock => treat as free (fail toward progress; single tick)


def _write_lock(pid: int, reason: str) -> None:
    try:
        LOCK_FILE.write_text(json.dumps({"pid": pid, "ts": time.time(), "reason": reason[:300]}))
    except Exception:
        pass


@dataclass
class TickDecision:
    """Pure decision (unit-testable, no side effects): whether to spawn, and why not / with what."""
    spawn: bool
    outcome: str          # SPAWNED | REST_NO_WORK | DISABLED | NOT_SCHEDULED | LOCK_HELD | DRAW_ERROR
    reason: str = ""      # the drawn doorbell (only when spawn=True)
    detail: str = ""


def decide_tick(enabled: bool, scheduled: bool, in_flight: bool,
                draw: "tuple[str | None, bool] | Exception") -> TickDecision:
    """PURE decision function — the R15-covered core. Takes the already-evaluated guards and the
    result of the find_work draw (or the exception it raised) and returns the decision. No I/O.

    Gate order is fail-closed/cheap-first: kill switch, then cutover flag, then no-stacking, then the
    draw. The draw is the ONLY thing that (when it returns work) authorizes an inference-costing spawn
    — so at rest (drained-and-gated) the answer is REST_NO_WORK and nothing is spawned (P1)."""
    if not enabled:
        return TickDecision(False, "DISABLED", detail="kill switch off — autonomy paused")
    if not scheduled:
        return TickDecision(False, "NOT_SCHEDULED", detail="scheduled-mode flag absent (dark/pre-cutover)")
    if in_flight:
        return TickDecision(False, "LOCK_HELD", detail="a prior invocation is still running")
    if isinstance(draw, Exception):
        # LOUD, not silent (fail-silent law): the draw itself broke. Do not spawn on a broken draw.
        return TickDecision(False, "DRAW_ERROR", detail=repr(draw))
    reason, _map_exhausted = draw
    if not reason:
        # Drained-and-gated (or map-exhausted): legitimate rest -> spawn NOTHING, zero cost. New
        # signals (a staged doc, a director act) are caught by the NEXT tick's origin-sync + draw.
        return TickDecision(False, "REST_NO_WORK", detail="drained-and-gated; nothing to draw")
    return TickDecision(True, "SPAWNED", reason=reason, detail=reason[:200])


def _draw() -> "tuple[str | None, bool] | Exception":
    """Sync origin-staged docs (RC3) then run the sole draw authority. Returns (reason, exhausted)
    or the Exception (so decide_tick can classify it LOUD). find_work prints via supervisor.log();
    capture stdout so this stays a clean library call. Sets the ntfy topic guard (never sends one)."""
    os.environ.setdefault("SE_NTFY_TOPIC", "worker-tick-draw-only")
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            from background.supervisor import _sync_origin_staging, find_work
            _sync_origin_staging()
            return find_work(resumed_from_pause=False)
    except Exception as e:
        return e


def _resolve_claude() -> str | None:
    """nvm installs `claude` off the interactive-shell PATH; a systemd --user oneshot has no nvm
    PATH. Resolve absolute (highest node version), same lesson as worker_seat._resolve_claude."""
    import glob
    import shutil
    found = shutil.which("claude")
    if found:
        return found
    matches = sorted(glob.glob(str(Path.home() / ".nvm" / "versions" / "node" / "*" / "bin" / "claude")))
    return matches[-1] if matches else None


def _worker_env() -> dict:
    """Per-launch env for the spawned `claude -p` worker. Copies this process's env,
    then applies hygiene: go direct to Anthropic (drop the optional proxy), force
    DISABLE_AUTOUPDATER, mark the Stop-hook worker discriminator, and — the authority
    gap fix (DIRECTOR_RULING_HMAC_GAP_OPTION_1, 2026-07-23) — SCRUB every model-facing
    forbidden secret (SE_WAKE_HMAC_KEY) so the worker keeps SE_NTFY_TOPIC to SEND but
    can never hold the wake key to SIGN a forged director-authority message. The scrub
    is the shared class-fix (secrets_location.scrub_model_facing_env); every model-
    facing spawner routes through it."""
    env = os.environ.copy()
    env.pop("ANTHROPIC_BASE_URL", None)   # go direct to Anthropic (proxy is optional monitoring)
    env["DISABLE_AUTOUPDATER"] = "1"
    env["SE_SBI_WORKER"] = "1"            # the Stop-hook worker discriminator (inherited by the hook)
    return scrub_model_facing_env(env)


def spawn_invocation(reason: str) -> "subprocess.Popen | None":
    """Spawn ONE headless bounded `claude -p` worker invocation. Returns the Popen (still running),
    or None if it could not be launched. The invocation is marked SE_SBI_WORKER=1 (the Stop hook's
    worker discriminator, inherited by the hook subprocess) and DISABLE_AUTOUPDATER=1.

    The caller WAITS for it (run_tick): worker-tick.service is Type=oneshot, so ExecStart must not
    return until the invocation finishes -- otherwise systemd tears down the cgroup and kills the
    child. Waiting also gives natural no-stacking (systemd skips a timer/path trigger while the
    oneshot is still active) and lets worker-tick.service's TimeoutStartSec bound a hung invocation
    (a hang is then a killed cgroup -> a skipped tick, not a wedge)."""
    claude_bin = _resolve_claude()
    if not claude_bin:
        _log("claude binary not found — cannot spawn invocation")
        return None
    env = _worker_env()
    prompt = WORKER_PREAMBLE + "[SCHEDULED-TICK doorbell -- R7: act on real disk/git state] " + reason
    try:
        return subprocess.Popen(
            [claude_bin, "-p", "--dangerously-skip-permissions", "--model", MODEL, prompt],
            cwd=str(PROJECT_DIR),
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL, env=env, start_new_session=True,
        )
    except Exception as e:
        _log(f"spawn failed: {e!r}")
        return None


def run_tick() -> TickDecision:
    """Evaluate the guards, draw, decide, and act. Returns the decision (for logging/tests). On a
    spawn it BLOCKS until the bounded invocation exits (keeping the oneshot service active for its
    whole lifetime — see spawn_invocation)."""
    enabled = autonomy_enabled()
    scheduled = scheduled_mode()
    # Cheap-first: don't even draw if disabled/dark/in-flight (no origin fetch, no work).
    if not enabled or not scheduled or invocation_in_flight():
        d = decide_tick(enabled, scheduled, invocation_in_flight() if enabled and scheduled else False,
                        (None, False))
        _write_health(d.outcome, d.detail)
        # Gated tick (paused/dark/in-flight): still ship a heartbeat for liveness, but skip the
        # map read -- the cheap path stays cheap (no supervisor import when autonomy is off).
        _write_heartbeat(d, f"(not evaluated -- tick {d.outcome})")
        _log(f"{d.outcome}: {d.detail[:120]}")
        return d
    draw = _draw()
    d = decide_tick(True, True, False, draw)
    _write_health(d.outcome, d.detail)
    # RAIL-3: ship the verdict + whole-set enumeration on every drew/rested/exception tick. _draw()
    # already imported supervisor, so the enumeration read is free here.
    _write_heartbeat(d, _enumeration_line())
    if d.spawn:
        proc = spawn_invocation(d.reason)
        if proc is not None:
            _write_lock(proc.pid, d.reason)
            _log(f"SPAWNED bounded invocation pid={proc.pid}: {d.reason[:120]}")
            try:
                rc = proc.wait()
            except Exception as e:
                rc = f"wait-error {e!r}"
            finally:
                # suppression-lint: not-a-suppression suppress -- contextlib exception context manager on lockfile cleanup, not a page/alarm suppression
                with contextlib.suppress(Exception):
                    LOCK_FILE.unlink()
            _log(f"invocation pid={proc.pid} exited (rc={rc})")
        else:
            _log("decided to spawn but launch failed — next tick retries")
    else:
        _log(f"{d.outcome}: {d.detail[:120]}")
    return d


if __name__ == "__main__":
    try:  # seat guard, FIRST act -- refuse to start on foreign soil (background/_seat.py)
        from background._seat import refuse_if_foreign
    except ModuleNotFoundError:  # launched as `python3 background/worker_tick.py`
        from _seat import refuse_if_foreign
    refuse_if_foreign("worker_tick")
    run_tick()
