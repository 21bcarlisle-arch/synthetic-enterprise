#!/usr/bin/env python3
"""PreToolUse hook: block outbound "fixed/live/deployed" claims unless they
cite a commit SHA the hook can INDEPENDENTLY confirm is on origin.

HARNESS_BEST_PRACTICE_ADOPTION.md item 1(c), the pixel rule / R11 (verify to
the rendered value). The only tool-interceptable "outbound claim" channel is
an NTFY send via Bash (send_ntfy(...) — see background/ntfy_utils.py); the
assistant's own prose to the user is not a tool call and cannot be hooked.

R15 INDEPENDENCE FIX (2026-07-14, director named the prior design as THEATRE).
The prior contract was a TAUTOLOGY (R15 killer pattern #1): before claiming
fixed/live/deployed the agent `touch`-ed a marker file and this hook read that
same marker. The checked value was produced by the checked party — the hook
could be satisfied by a bare `touch` that verified nothing landed. That is
exactly what happened tonight.

New contract — the evidence must be something the hook checks ITSELF against a
source the agent does NOT control by fiat:

  A claim-carrying NTFY message MUST cite a commit SHA (>=7 hex chars). The
  hook confirms, using LOCAL git only (fast, no network in the common path),
  that the cited SHA is actually reachable on the origin tracking ref
  (origin/main). A commit is on origin only if it was genuinely pushed —
  the agent cannot satisfy this by touching a file, only by doing the work
  and publishing it. That is the independence.

Fail-closed everywhere (R15 killer patterns #2 FAIL-OPEN, #3 FAIL-SILENT):
  * claim word present but NO verifiable SHA cited  -> BLOCK
  * cited SHA is NOT on origin/main (committed-not-pushed, or bogus) -> BLOCK
  * origin tracking ref cannot be resolved / git unavailable -> BLOCK
    (an unavailable check is a FAILED check, never a pass).

The self-touched .last_live_verification marker is REMOVED. This hook no
longer reads any agent-produced file; its verdict comes only from git's view
of origin. It still cannot judge whether the SHA's *content* is semantically
relevant to the specific claim — a human/self-audit does that — but it can no
longer be satisfied by theatre.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys

# Tracking refs to check, in order. The first that resolves is used. If none
# resolve, the check is UNAVAILABLE and we fail closed (block).
_ORIGIN_REFS = ("origin/main", "origin/master", "origin/HEAD")

_CLAIM_RE = re.compile(r"\b(fixed|live|deployed|confirmed|verified)\b", re.IGNORECASE)
# Require the real import, not just the bare word "send_ntfy" -- a commit
# message or comment can mention "a send_ntfy() call" in prose without ever
# invoking it. This distinguishes actually-executed NTFY code from text
# describing NTFY code (the same self-referential false-positive class as
# background/supervisor.py's PRIORITIES.md "## Backlog" heading bug).
_REAL_INVOCATION_RE = re.compile(r"ntfy_utils\s+import\s+send_ntfy\b.*send_ntfy\s*\(", re.DOTALL)

# A candidate git SHA: 7..40 hex chars as a whole token. We verify each
# candidate against origin; a hex-looking non-commit word simply fails to
# verify (and so cannot satisfy the gate).
_SHA_RE = re.compile(r"\b[0-9a-f]{7,40}\b", re.IGNORECASE)


def _extract_message(command: str) -> str | None:
    match = re.search(r"send_ntfy\(\s*(['\"]{1,3})(.*)\1", command, re.DOTALL)
    if match:
        return match.group(2)
    return None


def _resolve_origin_ref() -> str | None:
    """Return the first origin tracking ref that resolves, else None.

    None means the check is UNAVAILABLE -> caller must fail closed.
    """
    for ref in _ORIGIN_REFS:
        try:
            proc = subprocess.run(
                ["git", "rev-parse", "--verify", "--quiet", ref],
                capture_output=True,
                text=True,
                timeout=10,
            )
        except (OSError, subprocess.SubprocessError):
            return None
        if proc.returncode == 0 and proc.stdout.strip():
            return ref
    return None


def _sha_on_origin(sha: str, origin_ref: str) -> bool:
    """True iff `sha` is a real commit reachable from `origin_ref` (local view).

    Independent of any agent-produced artifact: a commit is an ancestor of the
    origin tracking ref only if it was actually pushed. Any error (unknown
    object, git failure) is treated as NOT verified -> fail closed.
    """
    try:
        proc = subprocess.run(
            ["git", "merge-base", "--is-ancestor", sha, origin_ref],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return proc.returncode == 0


def _has_verified_evidence(message: str) -> bool:
    origin_ref = _resolve_origin_ref()
    if origin_ref is None:
        # Check unavailable -> fail closed (do not pass).
        return False
    for candidate in _SHA_RE.findall(message):
        if _sha_on_origin(candidate, origin_ref):
            return True
    return False


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

    if _has_verified_evidence(message):
        return 0

    sys.stderr.write(
        "BLOCKED by block_unevidenced_claim.py: this NTFY message claims "
        "fixed/live/deployed/confirmed/verified but does not cite a commit "
        "SHA that this hook can confirm is on origin. Independence rule (R15): "
        "self-touched markers no longer count -- theatre. Push the real work, "
        "then include its pushed commit SHA (>=7 hex chars, reachable on "
        "origin/main) in the message. If nothing is pushed, the claim is not "
        "yet true: say 'in progress' / 'push pending' instead.\n"
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
