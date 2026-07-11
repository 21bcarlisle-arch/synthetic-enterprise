#!/usr/bin/env python3
"""Stop hook: advisory safety-net for the [ACTION NEEDED] rule
(from_rich_20260711_051508.md: "anything waiting on ME gets its own
dedicated [ACTION NEEDED] ntfy... never a line inside a status message").

Root cause of that rule failing repeatedly (2026-07-11, director-flagged,
third recurrence): background/action_needed.py and background/
deadmans_switch.py's [BLOCKED] class BOTH work correctly when actually
used (3 prior items in docs/observability/action_needed_register.json were
registered, re-pinged, and resolved cleanly) -- the gap is that
register_item() is a MANUAL API. Nothing detects "the agent asked an open
question in prose and forgot to register it" automatically. [BLOCKED]
doesn't cover this either -- it requires 90+ minutes of zero activity AND
real queued docs/staging/ work, neither of which is true of "an interactive
session ended a turn with an unanswered question and nothing else queued."

This hook is the structural fix, not a promise to remember harder (R3:
two-strike redesign, not another patch). It is DELIBERATELY narrow and
best-effort, not a general NLP classifier -- broad detection would false-
positive constantly (most turn-ending text isn't a blocking question) and
this project's own prior research (via the claude-code-guide agent, before
building anything) flagged transcript-format parsing as version-fragile.
So: a short, high-precision phrase list modelled directly on this agent's
OWN actual phrasing when it left questions unregistered this session
("Awaiting your steer on...", "your call", etc.), wrapped in broad
try/except so any transcript-format change makes this silently no-op
rather than crash or block -- observe-only, exits 0 always.

Heuristic, not authoritative: a hit here means "worth a human or a future
turn double-checking whether this should have been an [ACTION NEEDED]
ntfy", not a certain violation. False negatives are expected and fine
(this is a safety net under the real rule, not a replacement for it).
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_DIR))
REGISTER_FILE = PROJECT_DIR / "docs" / "observability" / "action_needed_register.json"
# 2026-07-11, director-flagged: the hook never visibly fired despite a clear
# trigger match on a real turn, and the broad except-Exception-pass below
# made "ran and silently decided not to" indistinguishable from "crashed
# silently" -- there was no way to tell which from outside the process.
# This log makes every invocation observable regardless of outcome, closing
# that blind spot structurally (R1: consumer-verified, not just "the code
# looks right").
DEBUG_LOG_FILE = PROJECT_DIR / "docs" / "observability" / ".stop_hook_debug.log"


DEBUG_LOG_MAX_LINES = 2000  # rotation cap -- risk-committee-log.md grew to
# an unbounded 277MB with no rotation (PRODUCTION_READINESS_EVIDENCE_PASS.md
# finding, same session); not repeating that mistake here.


def _debug_log(line: str) -> None:
    """Best-effort, never allowed to raise or block the hook it's
    instrumenting -- a broken debug log must never become a second reason
    for the actual hook to fail silently. Rotates at DEBUG_LOG_MAX_LINES."""
    try:
        from datetime import datetime, timezone
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        existing = DEBUG_LOG_FILE.read_text().splitlines() if DEBUG_LOG_FILE.is_file() else []
        existing.append(f"[{ts}] {line}")
        DEBUG_LOG_FILE.write_text("\n".join(existing[-DEBUG_LOG_MAX_LINES:]) + "\n")
    except Exception:
        pass

# High-precision phrases only -- modelled on this agent's own real lapses
# this session, not a broad "any question mark" scan.
_BLOCKING_PHRASE_RE = re.compile(
    r"(awaiting your|your call|your steer|need your (input|call|decision)|"
    r"blocking on you|waiting on you|up to you|your decision on)",
    re.IGNORECASE,
)

_RECENT_REGISTER_TOUCH_SECONDS = 300  # 5 min: proxy for "did register_item() actually get called this turn"


def _load_env_file() -> None:
    """2026-07-11, Option 2 floor (director in-console authorization):
    resolves through background/secrets_location.py, which checks the new
    out-of-tree ~/.config/synthetic-enterprise/ location first, falling
    back to the old in-tree path during the transition."""
    from background.secrets_location import resolve_secret_file
    env_file = resolve_secret_file(".env.ntfy")
    if not env_file.is_file():
        return
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


def _last_assistant_text(transcript_path: str) -> str | None:
    """Best-effort: read the transcript JSONL, return the last assistant
    message's text content. Defensive against format variation -- any
    shape mismatch returns None rather than raising."""
    path = Path(transcript_path)
    if not path.is_file():
        return None
    last_text = None
    with path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            message = entry.get("message") if isinstance(entry, dict) else None
            if not isinstance(message, dict) or message.get("role") != "assistant":
                continue
            content = message.get("content")
            if isinstance(content, str):
                last_text = content
            elif isinstance(content, list):
                texts = [
                    block.get("text", "") for block in content
                    if isinstance(block, dict) and block.get("type") == "text"
                ]
                if texts:
                    last_text = "\n".join(texts)
    return last_text


def _register_recently_touched() -> bool:
    if not REGISTER_FILE.is_file():
        return False
    import time
    return (time.time() - REGISTER_FILE.stat().st_mtime) < _RECENT_REGISTER_TOUCH_SECONDS


def main() -> int:
    _debug_log("invoked")
    try:
        raw_stdin = sys.stdin.read()
    except Exception as exc:
        _debug_log(f"stdin read failed: {exc!r}")
        return 0
    try:
        payload = json.loads(raw_stdin)
    except (json.JSONDecodeError, ValueError) as exc:
        _debug_log(f"stdin not valid JSON ({exc!r}); first 200 chars: {raw_stdin[:200]!r}")
        return 0

    transcript_path = payload.get("transcript_path")
    if not transcript_path:
        _debug_log(f"no transcript_path in payload; keys were: {list(payload.keys())}")
        return 0

    try:
        text = _last_assistant_text(transcript_path)
        if not text:
            _debug_log(f"no assistant text found in transcript {transcript_path}")
            return 0
        match = _BLOCKING_PHRASE_RE.search(text)
        if not match:
            _debug_log(f"no phrase match; last 120 chars of assistant text: {text[-120:]!r}")
            return 0
        _debug_log(f"phrase match: {match.group(0)!r}")
        if _register_recently_touched():
            _debug_log("register recently touched -- suppressing (assumed already handled)")
            return 0

        _load_env_file()
        sys.path.insert(0, str(PROJECT_DIR))
        from background.ntfy_utils import send_ntfy
        msg_id = send_ntfy(
            "[ACTION NEEDED rule check] The last turn's response contained "
            "phrasing that looks like an unregistered blocking question "
            "(e.g. \"awaiting your steer\"/\"your call\") and "
            "action_needed_register.json wasn't touched recently. Advisory "
            "only -- may be a false positive. If this IS a real open "
            "question, register it via background/action_needed.py."
        )
        _debug_log(f"sent advisory ntfy, id={msg_id}")
    except Exception as exc:
        import traceback
        _debug_log(f"EXCEPTION (swallowed, hook must never block a turn): {exc!r}\n{traceback.format_exc()}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
