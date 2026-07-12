#!/usr/bin/env python3
"""PreToolUse hook: deny cross-wall reads by lane, extending the epistemic
wall from RUNTIME into DEVELOPMENT itself ("builder blindness, not just
runtime blindness" -- GOVERNED_COMPANY_AND_THREE_LANES.md Part 2 item 1,
director-decided 2026-07-12, "fork as enforcement, not risk").

Pilot, deliberately cheap and narrow (not the full three-lane development
model -- that's the still-owed parallel-lanes proposal, docs/design/
PARALLEL_LANES_PROPOSAL.md). This hook does exactly one thing: if the
current session declares itself a lane via the SE_LANE environment
variable, deny Read/Grep/Glob calls whose target path falls on the OTHER
side of the sim/company wall, and log every denial.

No-op (returns 0 immediately) when SE_LANE is unset AND no `.se_lane`
marker file is found -- this is an opt-in pilot for sessions/worktrees
that declare a lane, not a standing restriction on every session. A
normal interactive session (like the one that wrote this hook) is
completely unaffected unless SE_LANE is explicitly exported or a
`.se_lane` file sits in its cwd first.

  SE_LANE=supplier  -- company-builder lane: sim/** and simulation/** denied
  SE_LANE=sim       -- SIM-builder lane: company/** and saas/** denied

2026-07-12 marker-file evolution (PARALLEL_LANES_PROPOSAL.md §3.1, the
pilot's own registered follow-up): the env var works for one human's
sequential focused session, but the Agent tool has no evident mechanism
to propagate a custom env var into one spawned subagent's own tool-call
environment -- so SUNDAY_WIDE's own parallel-fork-fan-out pattern couldn't
be lane-scoped at all under the env-var-only design. A `.se_lane` file
(containing just the lane name, e.g. "supplier" or "sim") in the current
working directory is now checked as a second, independent activation
path -- naturally scoping per-worktree (`EnterWorktree`/
`Agent(isolation:"worktree")`) without needing env-var propagation
through subagent spawning at all. Env var still wins if both are present
(the more explicit, harder-to-leave-behind-by-accident signal).

Denials are appended to docs/observability/lane_hook_denials.jsonl (one
JSON object per line) -- "prove it on real M2 tasks; log denials" (the
staged instruction's own DoD wording).
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

DENIAL_LOG = Path("docs/observability/lane_hook_denials.jsonl")

_LANE_DENIES = {
    "supplier": re.compile(r"^(sim|simulation)/"),
    "sim": re.compile(r"^(company|saas)/"),
}

# REGULATION_COMMONS_DOCTRINE.md (2026-07-12): "the TEXT is a commons" --
# regulatory rule digests (the fidelity oracle and successors) live in
# docs/domain_artefact_library/, provenance-tagged, readable by ALL lanes,
# mirroring reality (law is published). This deny-list design already
# makes it readable by omission (neither pattern above matches it), but
# the doctrine wants that EXPLICIT, not accidental -- this constant is the
# named shared-readable list; a future stricter allow-list model must keep
# every one of these paths off both lanes' deny patterns.
SHARED_READABLE = ("docs/domain_artefact_library/",)

_PATH_BEARING_TOOLS = {"Read", "Glob"}
_GREP_TOOL = "Grep"
_MARKER_FILE_NAME = ".se_lane"


def _lane_from_marker_file() -> str | None:
    """Read the lane declared by a `.se_lane` file in the current working
    directory, if one exists. Deliberately only checks cwd (not walking up
    parent directories) -- a worktree root IS the hook's cwd for any tool
    call made from within it, so a marker one level up would be a
    different worktree/repo, not this one's declaration."""
    try:
        marker = Path.cwd() / _MARKER_FILE_NAME
        if marker.is_file():
            return marker.read_text().strip()
    except OSError:
        pass
    return None


def _target_path(tool_name: str, tool_input: dict) -> str | None:
    if tool_name in _PATH_BEARING_TOOLS:
        return tool_input.get("file_path") or tool_input.get("path")
    if tool_name == _GREP_TOOL:
        return tool_input.get("path")
    return None


def _log_denial(lane: str, tool_name: str, path: str) -> None:
    DENIAL_LOG.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "lane": lane,
        "tool_name": tool_name,
        "path": path,
    }
    with DENIAL_LOG.open("a") as f:
        f.write(json.dumps(entry) + "\n")


def main() -> int:
    lane = os.environ.get("SE_LANE") or _lane_from_marker_file()
    if not lane or lane not in _LANE_DENIES:
        return 0

    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0

    tool_name = payload.get("tool_name")
    if tool_name not in _PATH_BEARING_TOOLS and tool_name != _GREP_TOOL:
        return 0

    tool_input = payload.get("tool_input") or {}
    path = _target_path(tool_name, tool_input)
    if not path:
        return 0

    # Relative-path match only (a path outside the repo, e.g. an absolute
    # /home/... path to a non-wall location, is not this hook's concern).
    normalized = path.lstrip("./")
    if not _LANE_DENIES[lane].match(normalized):
        return 0

    _log_denial(lane, tool_name, path)
    other_side = "sim/simulation" if lane == "supplier" else "company/saas"
    sys.stderr.write(
        "DENIED by lane_wall_hook.py: this session is SE_LANE={} -- {} on {!r} "
        "crosses into {} territory, denied by the development-time wall pilot "
        "(GOVERNED_COMPANY_AND_THREE_LANES.md Part 2). If this lane genuinely "
        "needs cross-wall data, it should arrive through a typed interface "
        "contract, not a direct read.\n".format(lane, tool_name, path, other_side)
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
