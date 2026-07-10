#!/usr/bin/env python3
"""PreToolUse hook: block outbound "fixed/live/deployed" claims with no fresh evidence.

HARNESS_BEST_PRACTICE_ADOPTION.md item 1(c), the pixel rule / R11 (verify to
the rendered value). The only tool-interceptable "outbound claim" channel is
an NTFY send via Bash (send_ntfy(...) — see background/ntfy_utils.py); the
assistant's own prose to the user is not a tool call and cannot be hooked.

Evidence contract: before sending an NTFY message that claims something is
fixed/live/deployed/confirmed, touch the marker file
docs/observability/.last_live_verification (e.g. right after a real `curl`
against the live site, per R11). This hook blocks the send if that marker
is missing or older than EVIDENCE_WINDOW_SECONDS.

This is deliberately narrow: it cannot verify the evidence is *actually
relevant* to the specific claim, only that *some* live-verification action
happened recently. A human/self-audit still does the semantic check; this
hook only catches the "claimed fixed with zero verification this session"
case.
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

EVIDENCE_MARKER = Path("docs/observability/.last_live_verification")
EVIDENCE_WINDOW_SECONDS = 30 * 60  # 30 minutes

_CLAIM_RE = re.compile(r"\b(fixed|live|deployed|confirmed|verified)\b", re.IGNORECASE)
# Require the real import, not just the bare word "send_ntfy" -- a commit
# message or comment can mention "a send_ntfy() call" in prose without ever
# invoking it. This distinguishes actually-executed NTFY code from text
# describing NTFY code (the same self-referential false-positive class as
# background/supervisor.py's PRIORITIES.md "## Backlog" heading bug).
_REAL_INVOCATION_RE = re.compile(r"ntfy_utils\s+import\s+send_ntfy\b.*send_ntfy\s*\(", re.DOTALL)


def _extract_message(command: str) -> str | None:
    match = re.search(r"send_ntfy\(\s*(['\"]{1,3})(.*)\1", command, re.DOTALL)
    if match:
        return match.group(2)
    return None


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0

    if payload.get("tool_name") != "Bash":
        return 0

    command = (payload.get("tool_input") or {}).get("command", "")
    if not _REAL_INVOCATION_RE.search(command):
        return 0

    message = _extract_message(command)
    if message is None or not _CLAIM_RE.search(message):
        return 0

    if not EVIDENCE_MARKER.exists():
        sys.stderr.write(
            "BLOCKED by block_unevidenced_claim.py: NTFY message claims "
            "fixed/live/deployed/confirmed/verified but no evidence marker "
            f"exists at {EVIDENCE_MARKER}. Do the live check first (e.g. curl "
            "the deployed URL per R11), then `touch` that marker, then retry.\n"
        )
        return 2

    age = time.time() - EVIDENCE_MARKER.stat().st_mtime
    if age > EVIDENCE_WINDOW_SECONDS:
        sys.stderr.write(
            "BLOCKED by block_unevidenced_claim.py: NTFY message claims "
            f"fixed/live/deployed/confirmed/verified but the evidence marker "
            f"is {int(age)}s old (window is {EVIDENCE_WINDOW_SECONDS}s). "
            "Re-verify live, then `touch` the marker, then retry.\n"
        )
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
