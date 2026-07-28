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

KNOWN LIMITATION -- Bash-mediated reads bypass this wall (2026-07-28 fresh
red-team of the AT-target atom, Rule-0 self-refill dial=1 yielded). This
hook is registered ONLY for the structured Read/Glob/Grep tools
(`.claude/settings.json` matcher "Read|Glob|Grep"), so a lane-scoped
session that reaches for Bash instead reads straight across the wall with
ZERO signal: under SE_LANE=supplier, `Read sim/forward_curve_builder.py`
is DENIED (rc=2) but `Bash: cat sim/forward_curve_builder.py` is ALLOWED
(rc=0, demonstrated live) -- as are `grep -rn ... sim/`, `python -c
"open('sim/...')"`, `head`, `sed`, redirects, command substitution, etc.
This is the single largest residual hole in the development-time wall and,
unlike the glob-parsing findings above, is NOT closed here: (1) it needs a
`.claude/settings.json` matcher change, which is OUTSIDE this atom's
file_scope; and (2) soundly detecting cross-wall file access in an
arbitrary shell command is impossible, so any Bash guard must be an
ADVISORY tripwire (warn + log, do not block) proportionate to this dial=1
soft pilot -- a hard Bash deny on a heuristic would be R15 theatre
(false confidence, unable to reliably fire). Registered as follow-up
`H6b_lane_wall_bash_tripwire` (director-facing: the advisory-vs-block call
changes a whole tool class's behaviour in lane sessions). Pinned by
TestKnownScopeBoundaryBashBypass so the contrast stays visible and cannot
be silently misremembered as "the wall covers everything".
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
# 2026-07-27 HARDEN pass (fresh red-team of the AT-target atom, Rule-0
# self-refill dial=1 yielded): the anchors required a trailing SLASH
# (`^(sim|simulation)/`), but _normalize_path() resolves through Path.resolve()
# + relative_to().as_posix(), which STRIPS the trailing slash off a directory
# target -- so a target that IS the denied top-level directory itself
# ('sim', 'sim/', 'simulation', 'sim/.') all normalize to bare 'sim' and the
# slash-requiring anchor never matched. Grep(pattern="hedge", path="sim") --
# the single most idiomatic way to search the sim tree -- therefore read
# straight across the wall (demonstrated live rc=0 under SE_LANE=supplier).
# A FAIL-OPEN (R15 pattern 2) on the exact directory the wall exists to
# protect, distinct from the whole-tree-SPAN class (that is wildcard/`.`
# first segments; this is the concrete denied dir named exactly). Closed by
# anchoring on a segment boundary `($|/)` instead of a literal `/`: the bare
# directory and everything beneath it both match, while a sibling like
# 'simple/' or 'companyx/' still does not (the `(sim)` alternative must be
# followed by end-of-string or a slash, never more name characters).
_LANE_DENIES = {
    "supplier": re.compile(r"^(sim|simulation)($|/)"),
    "sim": re.compile(r"^(company|saas)($|/)"),
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


_GLOB_METACHARS = frozenset("*?[]{}")

# 2026-07-28 HARDEN pass (fresh red-team of the AT-target atom, Rule-0
# self-refill dial=1 yielded -- no below-target work). A NEW fail-open
# class, distinct from every prior finding (absolute-path, traversal,
# unscoped-recursion, whole-tree-span, bare-directory): the previous fixes
# all leaned on _normalize_path()'s Path.resolve() to collapse `..` back to
# its true target so the deny regex could catch the landing directory. But
# pathlib does NOT expand brace alternations `{a,b}`, while the glob engine
# behind the real Glob tool (minimatch / node-glob family) DOES -- and a
# brace alternative can carry a `../` that escapes a concrete allowed first
# segment into the denied side. Glob(pattern="company/{compliance,../sim}/*.py")
# normalizes (pathlib) to a benign 'company/{compliance,../sim}/*.py' -- first
# segment the concrete 'company', so _spans_whole_tree passes it and the deny
# regex misses it -- yet the glob engine expands the second alternative to
# 'company/../sim/*.py' == sim/*.py, reading straight across the wall. The
# hook allowed it (rc=0) while the plain, brace-free 'company/../sim/...' form
# was correctly denied: the hook's SAFETY depended on the glob engine NOT
# supporting a standard feature. Closed as a CLASS by expanding braces here
# to the SAME path set the glob engine sees, then normalizing+checking EACH
# expansion -- one crossing alternative denies the whole call. A pure
# allowed-side brace ('company/{crm,compliance}/*.py') expands to allowed
# paths only and still passes (false-positive-guarded).
_MAX_BRACE_EXPANSIONS = 256


def _expand_braces(s: str) -> list[str]:
    """Expand shell-style brace alternations `{a,b,c}` into the full list of
    literal strings, cartesian-product across multiple/nested groups --
    mirroring what the real Glob engine does BEFORE it walks the filesystem,
    which pathlib's resolve() does not. A group with no top-level comma
    (e.g. a literal '{1}' or an empty '{}') is treated as literal text, not
    an alternation, so it is not mangled. Bails to the raw string on
    unbalanced braces. Capped at _MAX_BRACE_EXPANSIONS: a target that
    expands past the cap selects an unknown, unbounded set of paths -- the
    caller returns a sentinel so main() denies it as a span rather than
    silently checking a truncated subset (fail-CLOSED on explosion)."""
    open_i = s.find("{")
    if open_i == -1:
        return [s]
    depth = 0
    close_i = None
    for k in range(open_i, len(s)):
        if s[k] == "{":
            depth += 1
        elif s[k] == "}":
            depth -= 1
            if depth == 0:
                close_i = k
                break
    if close_i is None:
        return [s]  # unbalanced -- treat literally, don't guess
    pre, body, post = s[:open_i], s[open_i + 1 : close_i], s[close_i + 1 :]
    # Split body on TOP-LEVEL commas only (a nested {..} comma is not a
    # separator for this group).
    parts: list[str] = []
    depth = 0
    cur = ""
    for ch in body:
        if ch == "{":
            depth += 1
            cur += ch
        elif ch == "}":
            depth -= 1
            cur += ch
        elif ch == "," and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    parts.append(cur)
    post_expansions = _expand_braces(post)
    if post_expansions == [_BRACE_EXPLOSION]:
        return [_BRACE_EXPLOSION]  # propagate the sentinel up, don't mangle it
    if len(parts) == 1:
        # No alternation -- keep the braces as literal text.
        return [pre + "{" + body + "}" + tail for tail in post_expansions]
    results: list[str] = []
    for part in parts:
        part_expansions = _expand_braces(part)
        if part_expansions == [_BRACE_EXPLOSION]:
            return [_BRACE_EXPLOSION]
        for exp_part in part_expansions:
            for tail in post_expansions:
                results.append(pre + exp_part + tail)
                if len(results) > _MAX_BRACE_EXPANSIONS:
                    return [_BRACE_EXPLOSION]
    return results


# Sentinel returned by _expand_braces on a target whose brace expansion
# exceeds the cap: main() maps it to a whole-tree-span denial (an unbounded
# path set is exactly the "unknown set of directories" _spans_whole_tree
# already denies).
_BRACE_EXPLOSION = "\x00brace-explosion\x00"


# 2026-07-28 HARDEN pass #4 (fresh red-team of the AT-target atom, Rule-0
# self-refill dial=1 yielded -- no below-target work). A NEW fail-open class,
# the SIBLING of the same-day brace-expansion finding: the glob engine behind
# the real Glob tool (minimatch / node-glob family) supports EXTGLOB
# alternations -- @(a|b) (exactly one), +(a|b) (one or more), ?(a|b) (zero or
# one), *(a|b) (zero or more), !(a) (anything but a) -- which pathlib does NOT
# expand, and whose operator characters (@ + ! ( ) |) are ALL absent from both
# _expand_braces (only {}) and _spans_whole_tree's metachar set (*?[]{}). So an
# extglob alternative carrying a denied top-level dir, or a ../ traversal,
# slips past every gate exactly as the brace form did:
#   @(company|sim)/**/*.py     -> engine matches sim/ ; hook ALLOWED (rc=0)
#   +(sim|company)/**/*.py     -> denied side is an alternative ; ALLOWED
#   company/@(crm|../sim)/*.py -> ../sim escapes concrete 'company' ; ALLOWED
#   !(company|saas)/**/*.py    -> negation selects sim/simulation ; ALLOWED
# All four OBSERVED rc=0 at the hook under SE_LANE=supplier; the end-to-end
# cross via the real Glob TOOL is INFERRED from standard extglob semantics
# (R9 -- the Glob tool was unavailable this worker session to demo end-to-end),
# not asserted as demonstrated. Closed as a CLASS by rewriting extglob
# alternations into the SAME brace form the tested _expand_braces already
# expands+caps -- @/+ -> {alts} (or the bare alternative when there is only
# one, so it isn't mistaken for a literal single-element brace), ?/* -> {alts,}
# (they also match the empty string) -- then checking every expansion. A !()
# NEGATION matches an open-ended set that can include the denied side and
# cannot be enumerated into a finite crossing set, so it fails CLOSED via the
# explosion sentinel (denied as a span). A pure own-side extglob
# (company/@(crm|compliance)/*.py) expands to allowed paths only and still
# passes (false-positive-guarded).
_EXTGLOB_OPS = "?*+@!"


def _split_top_level_pipes(s: str) -> list[str]:
    """Split `s` on `|` separators sitting at brace-depth 0 -- a `|` inside an
    already-converted nested `{...}` group is that group's own content, not
    this extglob's alternative separator."""
    parts: list[str] = []
    depth = 0
    cur = ""
    for ch in s:
        if ch == "{":
            depth += 1
            cur += ch
        elif ch == "}":
            depth -= 1
            cur += ch
        elif ch == "|" and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    parts.append(cur)
    return parts


def _extglobs_to_braces(s: str) -> str:
    """Rewrite shell/minimatch EXTGLOB alternations into the equivalent brace
    alternation so the existing _expand_braces machinery expands them to the
    same path set the real glob engine walks. @(a|b) / +(a|b) -> {a,b};
    ?(a|b) / *(a|b) -> {a,b,} (they also match the empty string); a single
    alternative under @/+ becomes the bare literal (not `{x}`, which
    _expand_braces would keep as literal-text and _spans_whole_tree would then
    deny as a metachar span -- a false positive). A !(...) NEGATION matches an
    open-ended name set that can include the denied side and cannot be
    enumerated, so it returns the explosion sentinel and is denied as a span
    (fail CLOSED). Nested extglobs are converted recursively; an unbalanced
    operator-paren is left literal (don't guess); an operator char NOT followed
    by `(` (a literal `@`/`+`/`!` in a filename) is untouched."""
    out: list[str] = []
    i = 0
    n = len(s)
    while i < n:
        ch = s[i]
        if ch in _EXTGLOB_OPS and i + 1 < n and s[i + 1] == "(":
            depth = 0
            close = None
            for j in range(i + 1, n):
                if s[j] == "(":
                    depth += 1
                elif s[j] == ")":
                    depth -= 1
                    if depth == 0:
                        close = j
                        break
            if close is None:
                out.append(ch)  # unbalanced -- literal, don't guess
                i += 1
                continue
            if ch == "!":
                return _BRACE_EXPLOSION  # negation: un-enumerable -> fail CLOSED
            inner_converted = _extglobs_to_braces(s[i + 2 : close])
            if inner_converted == _BRACE_EXPLOSION:
                return _BRACE_EXPLOSION
            alts = _split_top_level_pipes(inner_converted)
            if ch in "?*":
                out.append("{" + ",".join(alts) + ",}")  # zero-or-one/more: allow empty
            elif len(alts) == 1:
                out.append(alts[0])  # exactly-one/one-or-more, single alt: bare literal
            else:
                out.append("{" + ",".join(alts) + "}")
            i = close + 1
        else:
            out.append(ch)
            i += 1
    return "".join(out)


def _expand_globs(target: str) -> list[str]:
    """Expand BOTH extglob alternations and brace alternations to the full
    literal path set the real glob engine walks -- the single entry main() uses
    so every expansion is normalized and wall-checked. Propagates the explosion
    sentinel (brace cap exceeded, or a !() negation) unchanged so main() denies
    it as a span."""
    converted = _extglobs_to_braces(target)
    if converted == _BRACE_EXPLOSION:
        return [_BRACE_EXPLOSION]
    return _expand_braces(converted)


def _spans_whole_tree(normalized: str) -> bool:
    """A search whose normalized target reaches BOTH sides of the wall
    reaches the denied side regardless of which lane is active -- yet it
    matches neither _LANE_DENIES pattern (those anchor on a concrete first
    segment like `^(sim|simulation)/`).

    2026-07-27 HARDEN pass (sibling-half red-team of the already-fixed
    Finding 3): Finding 3 closed the UNSCOPED case -- a Glob/Grep with no
    `path`/pattern (or `path="."`) that recurses from cwd -- via
    _has_explicit_scope(). A first sibling-pass then closed the
    explicit-repo-root-base case for a `.`- or `**`-leading target. But that
    enumerated two SPELLINGS of the span rather than the invariant, and a
    THIRD spelling still slipped through: an explicit repo-root base with a
    pattern whose FIRST segment is any OTHER glob wildcard --
    'pattern="*/forward_curve.py"' (single star), 'pattern="*/*.py"', or a
    brace 'pattern="{company,sim}/**/*.py"'. Each combined to a normalized
    target like '*/forward_curve.py' / '{company,sim}/**/*.py' whose first
    segment is neither a concrete directory nor a leading '**', so the
    old `== "." or startswith("**")` check missed it. Demonstrated live
    under SE_LANE=supplier: all three returned rc=0, reading straight
    across into sim/. Closed here as the actual CLASS.

    The invariant: the target's FIRST path segment is the top-level
    directory selector. If it is a concrete name ('company', 'sim') the
    search is anchored to exactly that top-level directory -- the
    _LANE_DENIES regex then adjudicates it correctly. If instead the first
    segment is '.' (the repo root) OR contains a glob metacharacter
    ('*', '?', '[', ']', '{', '}'), it selects an UNKNOWN set of top-level
    directories that can include the denied side, and no concrete-anchored
    deny pattern can catch it -- so it spans. Anchored recursive searches
    stay allowed: 'company/**/*.py' has a concrete first segment
    ('company') and is confined to the allowed side."""
    if normalized == ".":
        return True
    first_segment = normalized.split("/", 1)[0]
    return any(ch in _GLOB_METACHARS for ch in first_segment)


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

    for raw_target in _target_paths(tool_name, tool_input):
        # Expand brace AND extglob alternations to the SAME path set the real
        # Glob engine sees (pathlib does neither) -- one crossing alternative
        # (or an un-enumerable negation) denies the call.
        for raw_path in _expand_globs(raw_target):
            if raw_path == _BRACE_EXPLOSION:
                _log_denial(lane, tool_name, raw_target)
                sys.stderr.write(
                    "DENIED by lane_wall_hook.py: this session is lane={} -- {} on {!r} "
                    "expands to an unbounded or un-enumerable set of paths (brace explosion "
                    "or a !() negation) that cannot be shown to stay on your side of the "
                    "wall. Scope it to a concrete directory.\n".format(lane, tool_name, raw_target)
                )
                return 2
            normalized = _normalize_path(raw_path)
            if normalized is None:
                continue  # outside the repo entirely -- not this hook's concern
            if _spans_whole_tree(normalized):
                _log_denial(lane, tool_name, raw_path)
                sys.stderr.write(
                    "DENIED by lane_wall_hook.py: this session is lane={} -- {} on {!r} "
                    "selects an unknown set of top-level directories that can include the "
                    "other side of the wall (its normalized target {!r} anchors on "
                    "neither side). Scope it to a concrete directory on your own lane's "
                    "side of the wall.\n".format(lane, tool_name, raw_path, normalized)
                )
                return 2
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
