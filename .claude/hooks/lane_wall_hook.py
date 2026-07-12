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
REPO_ROOT = Path(__file__).resolve().parents[2]

# 2026-07-12 HARDEN pass (docs/observability/invariant_redteam-style adversarial
# review, self-refill dial-weighted draw): the original `path.lstrip("./")`
# normalization only stripped a leading "./" -- it did nothing for an
# ABSOLUTE path (confirmed: Claude Code's own Read tool spec requires
# absolute paths, meaning this hook's Read-side protection was very likely
# dead on arrival against real Read calls, not just a contrived edge case),
# nothing for a `..`-traversal that resolves back into denied territory
# (including one disguised behind REGULATION_COMMONS_DOCTRINE.md's own
# shared-readable docs/domain_artefact_library/ prefix), and nothing for a
# differently-cased path. All three are the same root cause: comparing a
# barely-touched string instead of a properly RESOLVED, repo-root-relative,
# case-normalized path. Fixed by _normalize_path() below; deny patterns are
# now matched against that, never the raw caller-supplied string.
_LANE_DENIES = {
    "supplier": re.compile(r"^(sim|simulation)/"),
    "sim": re.compile(r"^(company|saas)/"),
}


def _normalize_path(path_str: str) -> str | None:
    """Resolve `path_str` (absolute or relative, however messy -- `..`
    segments, redundant slashes, mixed case) against the repo root and
    return its lowercased, POSIX-style path relative to the repo root.
    Returns None if it resolves outside the repo entirely (not this
    hook's concern) or can't be resolved at all."""
    try:
        p = Path(path_str)
        if not p.is_absolute():
            p = REPO_ROOT / p
        resolved = p.resolve()
        rel = resolved.relative_to(REPO_ROOT)
    except (ValueError, OSError):
        return None
    return rel.as_posix().lower()

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
_SCOPED_TOOLS = _PATH_BEARING_TOOLS | {_GREP_TOOL}


def _lane_from_marker_file() -> str | None:
    """Read the lane declared by a `.se_lane` file in the current working
    directory, if one exists. Deliberately only checks cwd (not walking up
    parent directories) -- a worktree root IS the hook's cwd for any tool
    call made from within it, so a marker one level up would be a
    different worktree/repo, not this one's declaration.

    HARDEN pass fixes: only the FIRST line is read (a stray second line --
    e.g. accidental extra content -- no longer silently corrupts the
    comparison via a leftover embedded newline surviving .strip()), and
    the result is lowercased so "Supplier" matches the same as "supplier"
    (this project's own directories/lane names are case-normalized
    everywhere else; a marker file shouldn't be the one place case-
    sensitivity quietly disables the wall). An existing-but-unreadable
    marker (e.g. corrupted permissions) previously failed open with zero
    signal; now logs a warning to stderr before falling through -- still
    fails open (this is a soft dev-time pilot, not the runtime wall), but
    no longer silently."""
    marker = Path.cwd() / _MARKER_FILE_NAME
    if not marker.is_file():
        return None
    try:
        first_line = marker.read_text().splitlines()[0] if marker.stat().st_size else ""
        return first_line.strip().lower() or None
    except OSError as exc:
        sys.stderr.write(
            "lane_wall_hook.py: WARNING -- {} exists but could not be read "
            "({}); lane enforcement DISABLED for this call rather than "
            "silently assumed correct.\n".format(marker, exc)
        )
        return None


def _target_paths(tool_name: str, tool_input: dict) -> list[str]:
    """Every path-shaped string this call could touch. Glob's own `pattern`
    (e.g. "sim/**/*.py") is path-shaped and checked alongside `path` --
    Grep's `pattern` is a content search string, never a path, and is
    deliberately NOT checked here."""
    if tool_name == "Read":
        p = tool_input.get("file_path") or tool_input.get("path")
        return [p] if p else []
    if tool_name == "Glob":
        path = tool_input.get("path")
        pattern = tool_input.get("pattern")
        # `pattern` is resolved RELATIVE TO `path` (Glob semantics) -- check
        # the combined string, not each independently, or a base "path" of
        # "simulation/" with pattern "*.py" would be checked as two
        # unrelated fragments, neither of which alone matches the deny
        # regex's own "^(sim|simulation)/" anchor.
        if path and pattern:
            return [path.rstrip("/") + "/" + pattern]
        if path:
            return [path]
        if pattern:
            return [pattern]
        return []
    if tool_name == _GREP_TOOL:
        p = tool_input.get("path")
        return [p] if p else []
    return []


def _has_explicit_scope(tool_name: str, tool_input: dict) -> bool:
    """Did the caller give this call ANY explicit scoping path at all?
    Glob/Grep with no `path` (or `path="."`) search from cwd recursively --
    on a single, un-worktree-isolated checkout that recurses straight
    through both sides of the wall, and a hook can only allow/deny a whole
    call, never filter its results. HARDEN pass fix: an unscoped
    Glob/Grep call is denied outright while a lane is active rather than
    silently passed through as "no path to check.\""""
    if tool_name == "Read":
        return True  # always has file_path -- not this ambiguity's concern
    path = tool_input.get("path")
    if tool_name == "Glob":
        pattern = tool_input.get("pattern") or ""
        # An absolute or repo-rooted pattern (e.g. "sim/**/*.py") is its
        # own scope even with no separate `path` key.
        if path and path not in (".", "./"):
            return True
        return bool(pattern) and not pattern.startswith("**")
    if tool_name == _GREP_TOOL:
        return bool(path) and path not in (".", "./")
    return True


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


def _resolve_lane() -> str | None:
    """HARDEN pass fix: the original `env or marker_file` used TRUTHINESS,
    not VALIDITY -- any non-empty SE_LANE (even a typo/leftover env var
    from an unrelated tool) won over a correctly-configured `.se_lane`
    file and silently disabled enforcement. Now: a set-and-VALID env var
    wins (the explicit, harder-to-leave-behind-by-accident signal); a
    set-but-INVALID env var falls through to the marker file instead of
    silently nullifying it."""
    env_lane = os.environ.get("SE_LANE")
    if env_lane and env_lane in _LANE_DENIES:
        return env_lane
    return _lane_from_marker_file()


def main() -> int:
    lane = _resolve_lane()
    if not lane or lane not in _LANE_DENIES:
        return 0

    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0

    tool_name = payload.get("tool_name")
    if tool_name not in _SCOPED_TOOLS:
        return 0

    tool_input = payload.get("tool_input") or {}

    if not _has_explicit_scope(tool_name, tool_input):
        _log_denial(lane, tool_name, "<unscoped -- no path/pattern given>")
        sys.stderr.write(
            "DENIED by lane_wall_hook.py: this session is lane={} -- an "
            "unscoped {} call (no explicit path/pattern) would recurse "
            "across the whole tree, including the other side of the wall. "
            "Give it an explicit, scoped path.\n".format(lane, tool_name)
        )
        return 2

    for raw_path in _target_paths(tool_name, tool_input):
        normalized = _normalize_path(raw_path)
        if normalized is None:
            continue  # outside the repo entirely -- not this hook's concern
        if _LANE_DENIES[lane].match(normalized):
            _log_denial(lane, tool_name, raw_path)
            other_side = "sim/simulation" if lane == "supplier" else "company/saas"
            sys.stderr.write(
                "DENIED by lane_wall_hook.py: this session is lane={} -- {} on {!r} "
                "crosses into {} territory, denied by the development-time wall pilot "
                "(GOVERNED_COMPANY_AND_THREE_LANES.md Part 2). If this lane genuinely "
                "needs cross-wall data, it should arrive through a typed interface "
                "contract, not a direct read.\n".format(lane, tool_name, raw_path, other_side)
            )
            return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
