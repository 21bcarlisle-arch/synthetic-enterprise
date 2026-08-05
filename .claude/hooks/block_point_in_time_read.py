#!/usr/bin/env python3
"""PreToolUse hook: flag a company/saas Edit/Write introducing the exact
known-dangerous shape of the 2026-07-10 hedge-volatility bug -- a function
receiving a full historical settlement/price dataset with no visible
as-of/date bound.

HARNESS_BEST_PRACTICE_ADOPTION.md item 1(a). Director-authorized 2026-07-10
(docs/staging/done/from_rich_20260710_203008.md) as the NEAR-TERM detector,
explicitly NOT a modification to tools/epistemic_verifier.py (that stays
untouched per the closed EPISTEMIC_VERIFIER_TIMING_DETECTION_TIER1.md gate --
this is a separate, new mechanism). The permanent fix is the point-in-time
snapshot/as-of interface object (docs/review_gates/done/
POINT_IN_TIME_SNAPSHOT_TIER1.md), not this hook.

Deliberately narrow, matching that gate's own caution against a naive
detector eroding trust: this does NOT attempt general data-flow analysis.
It only flags the ONE known-real pattern from the actual incident --
`run_settlement(` or a bare `all_records` reference (the exact objects
involved in the hedge-volatility bug) appearing in NEW code being written
to a company/ or saas/ file, with no `as_of`/`bisect` bounding evidence
anywhere in the same diff. A real false-positive risk exists (legitimate
code might reference these without needing an as-of bound, or might bound
correctly using different terminology) -- this is a WARNING via stderr on
exit 2, not a hard, unappealable block: the model sees why it tripped and
can either fix the real issue or explicitly proceed if it judges the flag
to be a false positive (Bash hooks here are hard blocks; this one is
intentionally softer given the heuristic's real recall/precision tradeoff,
matching Option A's own documented risk in the closed gate).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# Seat guard: this blindfold heuristic gates the RESIDENT seat's company/saas
# authorship; a foreign session editing those paths must not be flagged by it.
# Make the hooks dir importable, then import the guard.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _seat import is_resident_seat  # noqa: E402

_DANGEROUS_PATTERN = re.compile(r"\brun_settlement\s*\(|\ball_records\b")
_BOUNDING_EVIDENCE = re.compile(r"as_of|bisect")
_COMPANY_SAAS_PATH = re.compile(r"^(company|saas)/.*\.py$")

# .claude/hooks/block_point_in_time_read.py -> repo root is parents[2].
REPO_ROOT = Path(__file__).resolve().parents[2]


def _normalize_path(path_str: str) -> str | None:
    """Resolve `path_str` (absolute, `./`-prefixed, or bare-relative) against
    the repo root and return its POSIX-style path relative to the repo root.

    The Edit/Write harness passes an ABSOLUTE file_path, so the raw
    `^(company|saas)/` gate matched only the bare-relative form the unit
    tests use and FAILED OPEN (returned exit 0, inert) on every real
    invocation -- the exact fail-open class closed for the sibling
    lane_wall_hook.py's `_normalize_path`, mirrored here (2026-07-28 HARDEN
    W1_reveal_over_time, Rule-0 dial=4). Returns None if the path resolves
    outside the repo (genuinely not a company/saas file) or is unresolvable.
    """
    if not path_str:
        return None
    try:
        p = Path(path_str)
        if not p.is_absolute():
            p = REPO_ROOT / p
        rel = p.resolve().relative_to(REPO_ROOT)
    except (ValueError, OSError):
        return None
    parts = rel.parts
    # The isolated worker seat runs in a git worktree under
    # .claude/worktrees/<name>/ (reference_worktree_main_daemon_split), whose
    # company/saas edits are REAL authorship that merges back to main. After
    # the absolute-path normalization above, such an edit lands as
    # `.claude/worktrees/<name>/company/...py`, which the `^(company|saas)/`
    # gate does NOT match -- so the blindfold hook FAILED OPEN on every
    # worktree-authored company change (a sibling of the 2026-07-28 abs-path
    # fail-open, found by red-teaming the same hook, Rule-0 dial=4). Strip the
    # worktree prefix so the inner company/saas path re-surfaces and is gated
    # identically to a main-tree edit.
    if len(parts) > 3 and parts[0] == ".claude" and parts[1] == "worktrees":
        rel = Path(*parts[3:])
    return rel.as_posix()


def _new_content(payload: dict) -> str | None:
    tool_name = payload.get("tool_name")
    tool_input = payload.get("tool_input") or {}
    if tool_name == "Write":
        return tool_input.get("content")
    if tool_name == "Edit":
        return tool_input.get("new_string")
    return None


def main() -> int:
    # Seat guard FIRST: inert (exit 0, no output) in any foreign seat.
    if not is_resident_seat():
        return 0
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0

    if payload.get("tool_name") not in ("Edit", "Write"):
        return 0

    file_path = (payload.get("tool_input") or {}).get("file_path", "")
    normalized = _normalize_path(file_path)
    if normalized is None or not _COMPANY_SAAS_PATH.match(normalized):
        return 0

    content = _new_content(payload)
    if content is None:
        return 0

    if not _DANGEROUS_PATTERN.search(content):
        return 0

    if _BOUNDING_EVIDENCE.search(content):
        return 0

    sys.stderr.write(
        "FLAGGED by block_point_in_time_read.py: new code in "
        f"{file_path!r} references a full historical settlement dataset "
        "(run_settlement(...) or all_records) with no visible as_of/bisect "
        "bounding in the same change -- this is the exact shape of the "
        "2026-07-10 hedge-volatility bug (docs/review_gates/done/"
        "HEDGE_VOLATILITY_LOOKBACK_FORESIGHT_BUG.md). If this genuinely "
        "needs the full dataset (e.g. it IS the bounding logic itself), "
        "proceed -- this is a heuristic warning, not a hard rule.\n"
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
