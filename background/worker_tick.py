#!/usr/bin/env python3
"""Scheduled bounded invocation — the continuity tick (SCHEDULED_BOUNDED_INVOCATIONS_DESIGN.md, 2026-07-20).

Fired by systemd `worker-tick.timer` (every 60s) and `worker-tick.path` (immediately on a new
staged doc). It replaces the persistent stop-hook-rearm worker seat and its rest-heartbeat, which
failed three independent ways in ~30h (input-blocking 27min, death-on-API-error ~6h, token-burn at
rest ~128.7k tok/h) — all from a resident turn-chain that must pay inference to stay alive.

THE WHOLE JOB (cheap Python, NO model inference):
  1. Autonomy enabled?  (.build_executor_enabled, fail-closed)          -> else exit 0
  2. Scheduled mode on?  (.scheduled_invocations_enabled)               -> else exit 0 (dark/pre-cutover)
  3. CLAIM the spawn slot (O_EXCL lockfile; a stale/dead holder is reclaimed) -> else exit 0 (no
       stacking). Claimed BEFORE step 4 because step 4 is real I/O: checking first and writing the
       lock after the spawn is a TOCTOU window as wide as the draw (H44).
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

# The tier DEFAULT and the fallback for everything the classifier does not recognise. Before
# 2026-08-12 this constant was the whole model policy: every tick paid Opus rates whether it was
# diagnosing a wedged publish gate or re-running a measurement tool and committing the row. The
# model was a property of the transport, not of the work. `background/model_tier.py` now picks per
# drawn doorbell; this stays as the floor it falls back to, and every fallback path lands here.
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


def _content_publish_block() -> dict:
    """The publish-freshness block for the heartbeat. Never raises, and an error is REPORTED
    rather than swallowed into an empty dict -- an absent freshness block reads to every consumer
    as 'nothing to say', which is indistinguishable from 'everything is fine' and is the exact
    fail-silent shape that let a day of frozen content look healthy."""
    try:
        from background import publish_freshness
        return publish_freshness.snapshot()
    except Exception as exc:  # noqa: BLE001
        return {"state": "unknown", "error": f"{exc.__class__.__name__}: {exc}"[:200]}


def _write_heartbeat(decision: "TickDecision", enumeration: str) -> None:
    """Write the origin-verifiable tick heartbeat (see HEARTBEAT_FILE). One line per tick:
    timestamp · verdict(drew/rested/exception) · whole-set enumeration, plus a rolling `recent`
    window so 'is it actually ticking' is answerable from advancing timestamps alone. No inference,
    never raises -- liveness reporting must not itself be able to wedge the tick.

    ALIVE-BUT-UNCHANGED IS NOT ALIVE-AND-PUBLISHING (2026-08-13, director). Everything above this
    line is a true statement about the TICK, and on 2026-08-13 it was true all day -- `drew` every
    sixty seconds, published to origin every thirty minutes -- while the site served the previous
    day's figures because every content commit was dying on the pre-commit hook deadline. The
    verdict was never wrong; it was about the wrong subject, and this file is the surface both the
    site and the advisor fetch to decide whether the system is healthy. So it now also carries how
    long it has been since CONTENT reached origin (background/publish_freshness.py). The two
    questions have separate answers here, and a reader who wants "is it alive AND publishing" has
    to look at both -- which is the whole point, because for eighteen hours they had different
    answers and only one of them was on the page.
    """
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
        # publishing | stale | unpublished | unknown -- see publish_freshness.snapshot().
        # UNAVAILABLE is reported as such and never as healthy: a freshness block that silently
        # became {} would restore exactly the all-clear this exists to remove.
        "content_publish": _content_publish_block(),
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


def _lock_payload(pid: int, reason: str) -> str:
    return json.dumps({"pid": pid, "ts": time.time(), "reason": reason[:300]})


def _write_lock(pid: int, reason: str) -> None:
    """Overwrite the lock's holder. Only legitimate for a caller that ALREADY owns the claim —
    it hands the slot from the tick process to the invocation it just spawned. Claiming is
    _claim_lock's job; this call cannot be the claim, which is exactly the H44 defect."""
    try:
        LOCK_FILE.write_text(_lock_payload(pid, reason))
    except Exception:
        pass


def _claim_lock(pid: int, reason: str) -> bool:
    """Atomically claim the spawn slot. True iff THIS process now owns the lockfile.

    O_CREAT|O_EXCL makes the check and the claim ONE step. The old two-step shape
    (invocation_in_flight() ... draw ... _write_lock() after the spawn) left a window as wide as
    the draw's origin-sync + find_work() I/O in which two ticks could both read the lock free and
    both spawn — and the second _write_lock() then OVERWROTE the first, so the evidence afterwards
    was a single apparently-legitimate holder even when two `claude -p` sessions were live on the
    same shared tree (H44_worker_tick_lock_toctou).

    A STALE lock (dead holder / malformed / unreadable) is reclaimed exactly ONCE and the atomic
    create retried, so a crashed invocation never wedges the tick — the same fail-toward-progress
    rule invocation_in_flight() has always had. Losing that retry means another tick claimed it
    first: not ours.

    Any OTHER failure to create the file (unwritable dir, permissions) returns False and LOGS: with
    no lockfile there is no mutual exclusion at all, so spawning would double-spawn on every tick.
    An unavailable control is a FAILED control (R15) — a visible rest beats a silent stacking."""
    for reclaimed in (False, True):
        try:
            LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
            fd = os.open(str(LOCK_FILE), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
        except FileExistsError:
            if reclaimed or invocation_in_flight():
                return False                      # a live holder, or we already spent the reclaim
            with contextlib.suppress(Exception):  # stale -> reclaim once, then retry atomically
                LOCK_FILE.unlink()
            continue
        except Exception as e:
            _log(f"LOCK UNAVAILABLE ({e!r}) — refusing to spawn: no lockfile means no no-stacking")
            return False
        try:
            os.write(fd, _lock_payload(pid, reason).encode())
        except Exception:
            pass
        finally:
            os.close(fd)
        return True
    return False


def _release_lock(*owned_pids: int) -> None:
    """Drop the lock only if it is still OURS. A blind unlink would delete a claim someone else
    made after a stale reclaim, re-opening the double-spawn window at the exit edge. A malformed
    or absent lock is garbage/gone and is cleared either way (it already reads as free)."""
    try:
        holder = int(json.loads(LOCK_FILE.read_text()).get("pid", 0))
        if holder not in owned_pids:
            return
    except Exception:
        pass
    with contextlib.suppress(Exception):
        LOCK_FILE.unlink()


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


def choose_model(reason: str) -> "tuple[str, object | None]":
    """Pick the model for this doorbell, and return the decision alongside it for logging.

    NEVER RAISES, AND NEVER FAILS CHEAP. Any error importing or running the classifier falls back to
    MODEL (Opus) with no decision object. A tiering bug must be able to cost tokens and must not be
    able to cost quality — the same asymmetry the classifier itself is built around."""
    try:
        from background.model_tier import classify
        decision = classify(reason)
        return decision.model, decision
    except Exception as e:  # pragma: no cover - defensive
        _log(f"model_tier unavailable, falling back to {MODEL}: {e!r}")
        return MODEL, None


def spawn_invocation(reason: str) -> "subprocess.Popen | None":
    """Spawn ONE headless bounded `claude -p` worker invocation. Returns the Popen (still running),
    or None if it could not be launched. The invocation is marked SE_SBI_WORKER=1 (the Stop hook's
    worker discriminator, inherited by the hook subprocess) and DISABLE_AUTOUPDATER=1.

    The MODEL is chosen per drawn doorbell (2026-08-12 tiering pilot, see background/model_tier.py),
    not pinned to the process. The choice and its reasoning are appended to
    docs/observability/model_tier_log.jsonl before the spawn, so a turn's tier is attributable
    afterwards even if the invocation dies — measuring quality by tier is the whole point of the
    pilot, and a tier that is only recorded on success would bias the measurement toward the tier
    that crashes less.

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
    model, decision = choose_model(reason)
    if decision is not None:
        _log(f"model={model} tier={decision.tier} classes={','.join(decision.classes)} "
             f"-- {decision.why}")
        try:
            from background.model_tier import log_decision
            log_decision(decision, reason)
        except Exception:  # pragma: no cover - measurement must never wedge the tick
            pass
    prompt = WORKER_PREAMBLE + "[SCHEDULED-TICK doorbell -- R7: act on real disk/git state] " + reason
    try:
        return subprocess.Popen(
            [claude_bin, "-p", "--dangerously-skip-permissions", "--model", model, prompt],
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
    # Cheap-first: don't even draw if disabled/dark. Then CLAIM the spawn slot atomically BEFORE
    # the draw (H44) — the draw is real I/O, and a check-then-draw-then-write lock is a TOCTOU
    # window exactly that wide. Everything past this point runs holding the claim, so the release
    # lives in a finally.
    me = os.getpid()
    claimed = _claim_lock(me, "tick drawing") if (enabled and scheduled) else False
    if not enabled or not scheduled or not claimed:
        d = decide_tick(enabled, scheduled, (enabled and scheduled and not claimed), (None, False))
        _write_health(d.outcome, d.detail)
        # Gated tick (paused/dark/in-flight): still ship a heartbeat for liveness, but skip the
        # map read -- the cheap path stays cheap (no supervisor import when autonomy is off).
        _write_heartbeat(d, f"(not evaluated -- tick {d.outcome})")
        _log(f"{d.outcome}: {d.detail[:120]}")
        return d
    owned = [me]
    try:
        draw = _draw()
        d = decide_tick(True, True, False, draw)
        _write_health(d.outcome, d.detail)
        # RAIL-3: ship the verdict + whole-set enumeration on every drew/rested/exception tick.
        # _draw() already imported supervisor, so the enumeration read is free here.
        _write_heartbeat(d, _enumeration_line())
        if d.spawn:
            proc = spawn_invocation(d.reason)
            if proc is not None:
                _write_lock(proc.pid, d.reason)   # hand the claim we already hold to the child
                owned.append(proc.pid)
                _log(f"SPAWNED bounded invocation pid={proc.pid}: {d.reason[:120]}")
                try:
                    rc = proc.wait()
                except Exception as e:
                    rc = f"wait-error {e!r}"
                _log(f"invocation pid={proc.pid} exited (rc={rc})")
            else:
                _log("decided to spawn but launch failed — next tick retries")
        else:
            _log(f"{d.outcome}: {d.detail[:120]}")
        return d
    finally:
        # Released on EVERY exit including a rested/errored draw: the claim is now taken before the
        # draw, so a tick that decides not to spawn must give the slot back rather than make the
        # next tick wait for its pid to die.
        _release_lock(*owned)


if __name__ == "__main__":
    try:  # seat guard, FIRST act -- refuse to start on foreign soil (background/_seat.py)
        from background._seat import refuse_if_foreign
    except ModuleNotFoundError:  # launched as `python3 background/worker_tick.py`
        from _seat import refuse_if_foreign
    refuse_if_foreign("worker_tick")
    run_tick()
