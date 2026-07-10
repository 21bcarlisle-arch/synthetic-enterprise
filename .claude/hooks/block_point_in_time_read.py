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

_DANGEROUS_PATTERN = re.compile(r"\brun_settlement\s*\(|\ball_records\b")
_BOUNDING_EVIDENCE = re.compile(r"as_of|bisect")
_COMPANY_SAAS_PATH = re.compile(r"^(company|saas)/.*\.py$")


def _new_content(payload: dict) -> str | None:
    tool_name = payload.get("tool_name")
    tool_input = payload.get("tool_input") or {}
    if tool_name == "Write":
        return tool_input.get("content")
    if tool_name == "Edit":
        return tool_input.get("new_string")
    return None


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0

    if payload.get("tool_name") not in ("Edit", "Write"):
        return 0

    file_path = (payload.get("tool_input") or {}).get("file_path", "")
    if not _COMPANY_SAAS_PATH.match(file_path):
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
