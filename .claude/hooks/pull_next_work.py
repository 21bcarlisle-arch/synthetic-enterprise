#!/usr/bin/env python3
"""PULL-LOOP transport (STAGING_PULL_LOOP_RESCOPE.md, 2026-07-15, director-decided).

The session PULLS work at every turn boundary: when a turn ends, this Stop hook
calls the EXISTING supervisor draw (find_work / Rule-0 non-empty draw) and feeds
the drawn work back as the next turn's input. The session never idles while atoms
exist, and NOTHING EVER TYPES INTO THE PANE -- this hook only emits JSON on stdout
(the documented block-stop/continue path). It is the replacement for keystroke/
tmux send-keys injection (banned; five deaths).

Verified against the official Stop-hook docs (code.claude.com/docs/en/hooks) before
building, per Finding 1: block+continue = exit 0 with {"decision":"block","reason":...};
`reason` becomes the next input; `stop_hook_active` is the loop guard.

SAFE ROLLOUT: gated OFF by default. It fires only when
docs/observability/.pull_loop_enabled exists, so REGISTERING the hook in
settings.json is inert until the director deliberately creates that flag --
enabling the loop is a decision, never a side effect of merging. It also NEVER
fires inside a block loop (stop_hook_active), fails SAFE (allows the stop) on any
draw error, and writes only to stdout + its own log (never the pane).
"""
import json
import os
import sys
import time
from pathlib import Path

# parents[2], NOT parent.parent: this file lives at <repo>/.claude/hooks/, so
# hooks -> .claude -> <repo> is TWO levels up. The old .parent.parent resolved
# to <repo>/.claude, so ENABLE_FLAG pointed at <repo>/.claude/docs/observability/
# .build_executor_enabled -- a path that never exists -- and kill_switch_enabled()
# was permanently False: the director's real flag at <repo>/docs/observability/
# was never read, so the Stop hook AND executor_daemon silently refused to run
# (2026-07-16: "flag enabled but nothing executes the loop").
PROJECT_DIR = Path(__file__).resolve().parents[2]
# The Stop hook can be invoked with a cwd that is NOT the repo root, so `import background` fails
# unless the repo root is on sys.path. Without this the pull loop raised
# ModuleNotFoundError('background') on EVERY fire and fail-safe'd to allow-stop -- the transport
# silently NEVER delivered work (found on the serial-autonomy maiden-turn watch, 2026-07-17).
sys.path.insert(0, str(PROJECT_DIR))
# WORKER-SEAT-ONLY: the pull loop must feed work to the ONE dedicated worker seat and
# NEVER to the director's sanctified console (or any other session) -- an automated
# mechanism acting on the console is a G-L1 violation (the same law that exempts the
# console from the reaper). The Stop hook fires on EVERY session in the project, so it
# must positively identify the worker by conversation id. Single source of truth: the
# id is imported from worker_seat (which seeds the seat via `--session-id`/`--resume`
# against exactly this id) so the filter and the seed can never drift. VERIFIED against
# a REAL dumped Stop payload (2026-07-17): the identity field is `session_id` and it
# equals the conversation UUID (== the transcript filename stem). FAIL-SAFE: if the id
# can't be resolved, WORKER_SESSION_ID stays None so NO session ever matches -> nobody
# is pulled (autonomy pauses; the console is never wrongly pulled) -- the safe direction.
# LOAD-TIME SELF-CHECK (OPS1_transport_failure_must_be_loud, §9): the worker_seat import
# is the gate before every draw -- if it fails, WORKER_SESSION_ID is None and the worker-seat
# guard allow-stops EVERY session, so the worker is silently never pulled (the same fail-silent
# class as the day-long ModuleNotFoundError). Record that as a transport DRAW_ERROR so it is
# LOUD (the deadman alarms on it) instead of indistinguishable from a healthy idle worker.
# (find_work importability is NOT probed at load -- that import is heavier and would add latency
# to the director's console Stop; a broken find_work is caught in decide()'s draw try/except.)
_SELF_CHECK_ERROR: str | None = None
try:
    from background.worker_seat import WORKER_SESSION_ID
except Exception as _e:
    WORKER_SESSION_ID = None
    _SELF_CHECK_ERROR = f"worker_seat import failed: {_e!r}"
# THE single kill switch for ALL autonomous execution (DIRECTOR_ANSWERS_C7.md #6,
# 2026-07-15, signed): ONE flag governs the pull loop AND any future headless
# executor -- no second flag. CONSOLE-ONLY, director-reserved (same class as
# security profiles); no agent/twin/staged-doc may create or modify it. FAIL-
# CLOSED: missing OR malformed (not a readable regular file) = DISABLED.
ENABLE_FLAG = PROJECT_DIR / "docs" / "observability" / ".build_executor_enabled"
LOG_FILE = PROJECT_DIR / "docs" / "observability" / "pull-loop-log.md"
STATE_FILE = PROJECT_DIR / "docs" / "observability" / ".pull_loop_state.json"
# Typed, first-class transport-health signal (OPS1_transport_failure_must_be_loud, §9). Written
# on every WORKER-seat fire so a broken transport is LOUD, not silent: the deadman reads this and
# alarms on a DRAW_ERROR, while background/process_reconciler.pull_loop_status() classifies it so
# 'idle because no work/grant' (ALLOW_STOP_NO_WORK/DISABLED) reads DIFFERENTLY from 'idle because
# the loop is broken' (DRAW_ERROR -> LOOP_BROKEN). Runtime state (gitignored), not committed.
HEALTH_FILE = PROJECT_DIR / "docs" / "observability" / ".pull_loop_health.json"
# Context hygiene (req 5): after this many continuations, feed a checkpoint/compact
# instruction instead of more work, so the loop never depends on a human noticing
# a 700k-token context.
CHECKPOINT_EVERY = 25
# SELF-SUSTAIN backstop (2026-07-17, director P0: "serial autonomy must SELF-SUSTAIN").
# The loop now CONTINUES across turns (the old `stop_hook_active -> stop` made it one-shot:
# one continuation then idle until an unreliable external Stop -- the disease, ~100-min idles
# with work queued). A continuous loop needs a runaway/stuck backstop that is LOUD, not a
# silent stop: if the loop continues this many turns WITHOUT the repo advancing by a single
# commit (no progress token change), it is thrashing/stuck -> STUCK_NO_PROGRESS (alarm), never
# a quiet idle. A PRODUCTIVE chain resets this counter on every commit, so it never trips; only
# a genuinely stuck spin does. Generous (> CHECKPOINT_EVERY) so a slow-committing but real chain
# gets a compact first and is not false-alarmed.
MAX_NO_PROGRESS = 30


def _repo_progress_token() -> str | None:
    """Best-effort 'has the repo advanced?' token WITHOUT spawning a process (the hook's
    structural no-subprocess invariant is load-bearing). The last line of .git/logs/HEAD changes
    on every commit/ref-move, so its content is a cheap progress proxy. None if unavailable ->
    progress detection degrades safely (the loop still runs; the stuck-cap just can't reset early,
    so a truly stuck loop still alarms, and a productive one is covered by the commit each turn)."""
    try:
        p = PROJECT_DIR / ".git" / "logs" / "HEAD"
        data = p.read_bytes()
        if not data:
            return None
        return data.rsplit(b"\n", 2)[-2 if data.endswith(b"\n") else -1].decode("utf-8", "replace")[:200]
    except Exception:
        return None


def _log(msg: str) -> None:
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(f"- [{time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}] {msg}\n")
    except Exception:
        pass


def _allow_stop() -> None:
    # No JSON, no block -> the session stops normally. ZERO pane writes.
    sys.exit(0)


def _write_health(outcome: str, detail: str = "") -> None:
    """Record the outcome of THIS worker-seat fire as the typed transport-health signal
    (§9). Never raises -- a health-write failure must not break the transport. outcome is
    one of: DREW | ALLOW_STOP_NO_WORK | ALLOW_STOP_DISABLED | DRAW_ERROR."""
    try:
        HEALTH_FILE.parent.mkdir(parents=True, exist_ok=True)
        HEALTH_FILE.write_text(json.dumps(
            {"ts": time.time(), "outcome": outcome, "detail": detail[:500]}
        ))
    except Exception:
        pass


def _autonomous_execution_enabled() -> bool:
    """THE single kill switch, FAIL-CLOSED (DIRECTOR_ANSWERS_C7 #6). Autonomous
    execution continues ONLY if ENABLE_FLAG is a readable regular file. Missing,
    a directory, or unreadable (malformed) => DISABLED. Never raises."""
    try:
        if not ENABLE_FLAG.is_file():
            return False
        ENABLE_FLAG.read_text()  # readable -> a proper flag
        return True
    except OSError:
        return False


def _advance_state(progress_token: str | None) -> tuple[int, int]:
    """Advance the loop's persistent counters and return (continuations, no_progress).

    continuations -- global monotonic count (drives the checkpoint/compact cadence).
    no_progress   -- consecutive continuations with NO repo advance (token unchanged). Resets to
                     0 the moment the repo advances (a commit) or on the first-ever fire, so a
                     productive chain never trips the stuck-cap; a genuinely stuck spin does.
    Never raises -- a state I/O failure must not break the transport (degrades to n=1,np=0)."""
    prior = {}
    try:
        if STATE_FILE.is_file():
            prior = json.loads(STATE_FILE.read_text())
    except Exception:
        prior = {}
    n = int(prior.get("continuations", 0)) + 1
    last_token = prior.get("last_token")
    # Progress = the token moved (a commit landed) since the last fire. Unknown token (None) on
    # either side counts as NO progress so a truly stuck loop still trips the cap; but the very
    # first fire (no last_token recorded) is treated as progress so a fresh chain starts clean.
    if "last_token" not in prior:
        no_progress = 0
    elif progress_token is not None and progress_token != last_token:
        no_progress = 0
    else:
        no_progress = int(prior.get("no_progress", 0)) + 1
    try:
        STATE_FILE.write_text(json.dumps(
            {"continuations": n, "no_progress": no_progress, "last_token": progress_token}
        ))
    except Exception:
        pass
    return n, no_progress


def decide(payload: dict) -> dict | None:
    """Pure decision function (unit-testable): returns the block-JSON dict to
    emit, or None to allow the stop. No I/O to the pane, ever."""
    # NOTE (2026-07-17): the old `if stop_hook_active: return None` guard was DELETED. It made the
    # loop ONE-SHOT -- Claude Code sets stop_hook_active=True on the re-Stop after a continuation,
    # so that guard stopped the chain after a single turn, leaving the worker idle until an
    # unreliable external Stop re-armed it (the ~100-min-idle-with-work-queued disease). Serial
    # autonomy MUST self-sustain (director P0): the loop CONTINUES turn-to-turn on its own draw.
    # Runaway is bounded not by stop_hook_active but by the LOUD stuck-cap (MAX_NO_PROGRESS) below
    # -- a continuous loop that stops producing commits is thrashing and must ALARM, not idle.
    # WORKER-SEAT-ONLY GUARD (G-L1): pull work ONLY for the dedicated worker seat.
    # Any other session -- the director's sanctified console, an ad-hoc session, or
    # (fail-safe) an unresolved worker id -- gets allow-stop, never a doorbell. The
    # field is `session_id`, verified against a real dumped payload; it carries the
    # conversation UUID. This is positive identification: absent/mismatched id ->
    # allow stop, so an unknown session can never be pulled into the loop.
    sid = payload.get("session_id")
    # `not WORKER_SESSION_ID` covers the fail-safe case (id unresolved -> None/empty):
    # nothing is ever pulled. `sid != WORKER_SESSION_ID` requires a POSITIVE match to a
    # real worker id (None==None must NOT slip through as a match), so an absent/mismatched
    # session id -> allow stop. Both together = strict positive identification.
    if not WORKER_SESSION_ID or sid != WORKER_SESSION_ID:
        _log(
            f"non-worker session (session_id={str(sid)[:8]}...) -> allow stop "
            "(G-L1 console/other exempt)"
        )
        return None
    # THE kill switch, fail-closed: continue ONLY if the single flag is a readable
    # regular file. Missing / a directory / unreadable = DISABLED (refuse to
    # continue). This is the R15-proven kill: flag off -> next boundary refuses.
    if not _autonomous_execution_enabled():
        _write_health("ALLOW_STOP_DISABLED", "kill switch off -- autonomy deliberately paused")
        return None
    # Draw work from the EXISTING supervisor draw (Rule-0: non-empty while atoms
    # exist). find_work only READS the map/staging; the placeholder topic just
    # satisfies ntfy_utils' import guard (this hook never sends an ntfy).
    os.environ.setdefault("SE_NTFY_TOPIC", "pull-loop-draw-only")
    try:
        import contextlib
        import io
        # find_work (via the supervisor's log()) PRINTS to stdout. The Stop hook's stdout must be
        # PURE JSON or Claude Code cannot parse the block+continue -- leading log lines would drop
        # the drawn turn silently. Capture find_work's stdout so ONLY main()'s json.dumps reaches
        # the transport (2nd transport bug found on the serial-autonomy maiden-turn watch, 2026-07-17).
        with contextlib.redirect_stdout(io.StringIO()):
            from background.supervisor import find_work
            reason, map_exhausted = find_work(resumed_from_pause=False)
    except Exception as e:  # fail SAFE: never block on a broken draw
        _log(f"draw error: {e!r} -> allow stop (fail-safe)")
        # LOUD, not silent (§9): the transport tried to draw and could not. The deadman
        # alarms on this DRAW_ERROR -- a broken loop must not read as a healthy idle worker.
        _write_health("DRAW_ERROR", repr(e))
        return None
    if not reason:
        # find_work now returns THREE states, distinguished by the second element (map_exhausted):
        #   (None, False) = DRAINED-AND-GATED quiet wait (ADVISOR_STEER 2026-07-18, item 1): every
        #     below-target BUILD/SITE/DISCOVER lane + backlog is empty and the remainder is blocked
        #     on a director act, so the only draw would be at-target HARDEN re-verification. This is
        #     a LEGITIMATE resting state -> allow-stop QUIETLY (no block+continue treadmill, no
        #     token burn, no STUCK/LOOP_BROKEN alarm, freshness-exempt in the reconciler). New
        #     signals (a staged doc, a director act, new below-target work) short-circuit find_work
        #     before the drained branch and wake the loop on the next turn -- responsiveness intact.
        #   (None/"" , True) = genuine empty/broken draw: under Rule-0 the queue is NEVER genuinely
        #     empty (an unreadable/malformed map read swallowed as [] by every lane), so this must
        #     be LOUD -- the director named it a case that must never read as silent healthy idle.
        if map_exhausted:
            _log("draw empty -> allow stop (UNEXPECTED under Rule-0 -> loud alarm)")
            _write_health("DRAW_EMPTY_UNEXPECTED",
                          "find_work returned no work -- never legitimate under Rule-0 (broken draw?)")
        else:
            _log("drained-and-gated -> allow stop (quiet wait; legitimate resting state, not broken)")
            _write_health("ALLOW_STOP_QUIET_WAIT",
                          "drained-and-gated: only at-target HARDEN remains while blocked on a director act")
        return None
    # SELF-SUSTAIN: advance counters and check the stuck-cap. The loop CONTINUES turn-to-turn (no
    # one-shot stop_hook_active guard); the only continuous-loop backstop is progress-based.
    n, no_progress = _advance_state(_repo_progress_token())
    if no_progress > MAX_NO_PROGRESS:
        # Drew work and continued for MAX_NO_PROGRESS turns but the repo never advanced (no commit)
        # -> the loop is thrashing/stuck, not advancing. LOUD (director's fail-silent law), then
        # allow-stop so it does not spin forever. A productive chain resets no_progress on every
        # commit and never reaches here.
        _log(f"STUCK: {no_progress} continuations with no commit -> allow stop + ALARM")
        _write_health("STUCK_NO_PROGRESS",
                      f"{no_progress} continuations, no repo advance -- loop thrashing/stuck")
        return None
    if n % CHECKPOINT_EVERY == 0:
        reason = (
            f"PULL-LOOP CHECKPOINT (continuation {n}): commit any in-flight work, then "
            "run /compact -- state-on-disk is the real memory. Then resume the draw."
        )
    # BLOCK the stop; the reason becomes the next input. R7: it is a DOORBELL --
    # verify against disk/git and act on real state, never trust this text alone.
    out = {
        "decision": "block",
        "reason": "[PULL-LOOP doorbell -- R7: act on real disk/git state, not this text] " + reason,
    }
    _log(f"BLOCK+continue (n={n}): {reason[:120]}")
    _write_health("DREW", reason[:200])
    return out


def main() -> None:
    # Load-time self-check (§9): if the worker_seat import failed, the worker-seat guard
    # would silently allow-stop every session -> the worker is never pulled. Record it as a
    # LOUD DRAW_ERROR (the deadman alarms), then fail-safe allow-stop as always.
    if _SELF_CHECK_ERROR:
        _write_health("DRAW_ERROR", _SELF_CHECK_ERROR)
        _log(f"self-check FAILED: {_SELF_CHECK_ERROR} -> allow stop")
        _allow_stop()
    try:
        payload = json.load(sys.stdin)
    except Exception:
        _allow_stop()
    result = decide(payload)
    if result is None:
        _allow_stop()
    print(json.dumps(result))
    sys.exit(0)


if __name__ == "__main__":
    main()
