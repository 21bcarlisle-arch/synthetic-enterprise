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

PROJECT_DIR = Path(__file__).resolve().parent.parent
# THE single kill switch for ALL autonomous execution (DIRECTOR_ANSWERS_C7.md #6,
# 2026-07-15, signed): ONE flag governs the pull loop AND any future headless
# executor -- no second flag. CONSOLE-ONLY, director-reserved (same class as
# security profiles); no agent/twin/staged-doc may create or modify it. FAIL-
# CLOSED: missing OR malformed (not a readable regular file) = DISABLED.
ENABLE_FLAG = PROJECT_DIR / "docs" / "observability" / ".build_executor_enabled"
LOG_FILE = PROJECT_DIR / "docs" / "observability" / "pull-loop-log.md"
STATE_FILE = PROJECT_DIR / "docs" / "observability" / ".pull_loop_state.json"
# Context hygiene (req 5): after this many continuations, feed a checkpoint/compact
# instruction instead of more work, so the loop never depends on a human noticing
# a 700k-token context.
CHECKPOINT_EVERY = 25


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


def _bump_continuation_count() -> int:
    n = 0
    try:
        if STATE_FILE.is_file():
            n = int(json.loads(STATE_FILE.read_text()).get("continuations", 0))
    except Exception:
        n = 0
    n += 1
    try:
        STATE_FILE.write_text(json.dumps({"continuations": n}))
    except Exception:
        pass
    return n


def decide(payload: dict) -> dict | None:
    """Pure decision function (unit-testable): returns the block-JSON dict to
    emit, or None to allow the stop. No I/O to the pane, ever."""
    # Loop guard (verified): already continuing in a block loop -> allow stop.
    if payload.get("stop_hook_active"):
        _log("stop_hook_active -> allow stop (loop guard)")
        return None
    # THE kill switch, fail-closed: continue ONLY if the single flag is a readable
    # regular file. Missing / a directory / unreadable = DISABLED (refuse to
    # continue). This is the R15-proven kill: flag off -> next boundary refuses.
    if not _autonomous_execution_enabled():
        return None
    # Draw work from the EXISTING supervisor draw (Rule-0: non-empty while atoms
    # exist). find_work only READS the map/staging; the placeholder topic just
    # satisfies ntfy_utils' import guard (this hook never sends an ntfy).
    os.environ.setdefault("SE_NTFY_TOPIC", "pull-loop-draw-only")
    try:
        from background.supervisor import find_work
        reason, _map_exhausted = find_work(resumed_from_pause=False)
    except Exception as e:  # fail SAFE: never block on a broken draw
        _log(f"draw error: {e!r} -> allow stop (fail-safe)")
        return None
    if not reason:
        _log("draw empty -> allow stop")
        return None
    n = _bump_continuation_count()
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
    return out


def main() -> None:
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
