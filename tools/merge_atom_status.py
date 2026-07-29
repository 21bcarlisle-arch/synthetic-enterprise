#!/usr/bin/env python3
"""Fold per-atom write-inbox files into the hand-authored maturity_map.yaml.

Half B of the WORKTREE_AND_MAP_CONTENTION_DESIGN (H9). The velocity problem:
N concurrent BUILD forks each read-edit-write the single `maturity_map.yaml`
to record their level; `background/tree_lock.py` serialises the git *commit*
but NOT the read-edit-write, so two forks lost-update each other's level bump.

The structural fix (design option (a), "safe by construction not by
convention"): each fork writes ONLY its own narrow write-inbox at
`docs/design/atom_status/<id>.yaml` -- disjoint paths, so a lost update is
impossible with NO lock at all. The integrator then runs THIS tool once,
single-threaded, to fold each landed inbox's fields into the canonical map.

CRITICAL CONTRACT -- this is a NARROW FIELD MERGE, never a wholesale
regeneration. `maturity_map.yaml` carries rich hand-authored content
(`simplifications` prose, `provenance`, `expert_hour`, `depends_on`) that must
survive untouched. We therefore edit the map's TEXT in place, rewriting only
the specific field lines of the specific target atoms; every other atom's
bytes are preserved exactly. Round-tripping the whole file through
yaml.safe_dump would reflow all 61 atoms and destroy that hand-authored form,
so we deliberately do NOT do that.

Inbox schema (write-inbox fields only):
    id: <atom id, must exist in the map>
    level_current: <int>              # optional; folded onto the atom
    append_evidence: [<str>, ...]     # optional; appended to `evidence`
    append_simplification: [<str>, ...] # optional; appended to `simplifications`
    written_by: <fork-branch>         # provenance only, not folded
    written_at: <iso8601>             # provenance only, not folded

Usage:
    python3 -m tools.merge_atom_status            # merge + clear real inboxes
    python3 -m tools.merge_atom_status --dry-run  # report, change nothing
    # programmatic (the proof test drives this form):
    from tools.merge_atom_status import merge, preflight_overlap
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import yaml

PROJECT = Path(__file__).resolve().parent.parent
MATURITY_MAP_YAML = PROJECT / "docs" / "design" / "maturity_map.yaml"
INBOX_DIR = PROJECT / "docs" / "design" / "atom_status"

# Fields a fork is permitted to mutate via its inbox.
_APPENDABLE = {"append_evidence": "evidence", "append_simplification": "simplifications"}


class MergeError(Exception):
    """A structural precondition of the merge was violated."""


# --------------------------------------------------------------------------
# Inbox loading
# --------------------------------------------------------------------------
def load_inboxes(inbox_dir: Path = INBOX_DIR) -> list[dict]:
    """Load every `<id>.yaml` write-inbox in `inbox_dir` (README/non-yaml skipped)."""
    inboxes = []
    if not inbox_dir.exists():
        return inboxes
    for p in sorted(inbox_dir.glob("*.yaml")):
        data = yaml.safe_load(p.read_text())
        if not isinstance(data, dict) or "id" not in data:
            raise MergeError(f"Inbox {p} is not a mapping with an 'id' field")
        data["_path"] = p
        inboxes.append(data)
    return inboxes


def unfolded_inbox_ids(inbox_dir: Path = INBOX_DIR) -> list[str]:
    """Atom ids with a write-inbox still present AT REST — a RECONCILIATION FAILURE.

    `merge()` clears an inbox only AFTER folding its level/evidence into the canonical
    map, so anything left here is a fork's level report that never reached the map: the
    self-report-vs-external-truth divergence signal (docs/design/MAP_TRUTH_RECONCILIATION.md
    F2). Reuses `load_inboxes` so there is ONE definition of "an inbox," never two that
    drift. A NON-EMPTY return is fail-closed: the unwatched executor loop treats it as a
    STOP (an unreconciled map is a failed map — the draw reads level_current, so a
    mis-folded level would silently mis-rank work). A malformed inbox raises via
    load_inboxes — an unreadable reconciliation signal is itself a failure, never ignored."""
    return [str(ib.get("id") or "<no-id>") for ib in load_inboxes(inbox_dir)]


# --------------------------------------------------------------------------
# Pre-flight conflict detection
# --------------------------------------------------------------------------
def preflight_inbox_overlap(inboxes: list[dict]) -> list[str]:
    """Return atom ids targeted by more than one inbox (would be a same-atom
    lost update at fold time). Empty list == safe to fold."""
    seen: dict[str, int] = {}
    for ib in inboxes:
        seen[ib["id"]] = seen.get(ib["id"], 0) + 1
    return sorted(aid for aid, n in seen.items() if n > 1)


def changed_files(base: str, ref: str, cwd: Path = PROJECT) -> set[str]:
    """Files changed between merge-base(base, ref) and ref -- the concrete git
    read-only pre-flight from the design (A2)."""
    mb = subprocess.run(
        ["git", "merge-base", base, ref], cwd=cwd, capture_output=True, text=True, check=True
    ).stdout.strip()
    out = subprocess.run(
        ["git", "diff", "--name-only", mb, ref], cwd=cwd, capture_output=True, text=True, check=True
    ).stdout
    return {ln for ln in out.splitlines() if ln}


def preflight_overlap(changed_a: set[str], changed_b: set[str]) -> set[str]:
    """The merge-base changed-file intersection of two fork branches. Non-empty
    => a mis-declared `file_scope`; do NOT auto-merge, re-sequence (rebase +
    re-run scoped suite). Empty => clean `git merge --no-ff` is safe. This is
    the belt-and-braces behind Lane 1's disjoint-file_scope dispatch rule."""
    return set(changed_a) & set(changed_b)


# --------------------------------------------------------------------------
# Scoped-suite selector (design A3) -- N forks pay N small suites; the full
# ~17k suite runs ONCE at integration, never per fork.
# --------------------------------------------------------------------------
def scoped_suite_for(file_scope: list[str]) -> list[str]:
    """Map an atom's `file_scope` to the minimal pytest target dirs to run in
    its worktree. Returns [] for scopes with no python suite (e.g. site/**,
    which is pixel-verified per R11, not unit-tested)."""
    roots = set()
    for entry in file_scope or []:
        top = str(entry).split("/", 1)[0]
        roots.add(top)
    suites: list[str] = []

    def add(*dirs: str):
        for d in dirs:
            if d not in suites:
                suites.append(d)

    for top in sorted(roots):
        if top in ("sim", "simulation"):
            add("tests/sim", "tests/simulation")
        elif top == "saas":
            add("tests/saas")
        elif top == "company":
            add("tests/company")
        elif top == "interface":
            # both consumers of the seam -- build-time verify per design A3
            add("tests/company", "tests/saas")
        elif top in ("background", ".claude"):
            add("tests/background")
        elif top == "tools":
            add("tests/tools")
        elif top == "docs":
            # a doc-scoped harness change lands next to tools/background tests
            add("tests/background", "tests/tools")
        elif top == "site":
            pass  # no python suite; pixel-verify the live surface (R11)
    return suites


# --------------------------------------------------------------------------
# The narrow text fold
# --------------------------------------------------------------------------
def _dump_flow_list(items: list) -> str:
    """Serialise a python list as a single-line YAML flow list, matching the
    map's existing `field: [ ... ]` style."""
    return yaml.safe_dump(
        items, default_flow_style=True, allow_unicode=True, width=10**9
    ).strip()


def _split_flow_list(rest: str):
    """Split `rest` (everything after `field:`) into (flow_list_text, trailing).

    Returns (None, None) when `rest` does not open a flow list. The scan is
    bracket-depth and quote aware: a regex like `\\[.*\\]` is greedy and would
    swallow a `]` appearing inside a TRAILING COMMENT, and the map really does
    carry commented flow lists (`evidence: [x]  # why ...`) -- six atoms had one
    at the 2026-07-29 wedge, each an invisible fold failure because neither the
    flow regex nor the block regex matched the line at all."""
    s = rest.lstrip()
    if not s.startswith("["):
        return None, None
    depth = 0
    quote = None
    i = 0
    while i < len(s):
        ch = s[i]
        if quote == '"':
            # YAML double-quoted style honours backslash escapes; missing this
            # closed the string early on `\"` and left the scanner desynchronised
            # (one real atom, W2_2_population_draw, hit exactly that).
            if ch == "\\":
                i += 2
                continue
            if ch == '"':
                quote = None
        elif quote == "'":
            # YAML single-quoted style escapes a quote by DOUBLING it, not with a
            # backslash -- the map's prose is full of `it''s`.
            if ch == "'":
                if i + 1 < len(s) and s[i + 1] == "'":
                    i += 2
                    continue
                quote = None
        elif ch in "'\"":
            quote = ch
        elif ch in "[{":
            depth += 1
        elif ch in "]}":
            depth -= 1
            if depth == 0:
                return s[: i + 1], s[i + 1:].rstrip("\n")
        i += 1
    return None, None


def _dump_block_item(item) -> str:
    """Serialise ONE list element as the scalar half of a `- <scalar>` block-list
    entry, on a single physical line (width=10**9 defeats yaml's line wrapping, so
    a folded entry never spills into continuation lines we would then have to
    re-indent).

    Dumped as a ONE-ELEMENT FLOW LIST with the brackets stripped, NOT as a bare
    scalar: `safe_dump("x")` emits a `...` document-end marker on its own line,
    which a `.strip()` leaves attached and which corrupts the map. Flow-context
    quoting is a superset of what a block entry needs, so the result is always
    valid where it lands."""
    dumped = yaml.safe_dump(
        [item], default_flow_style=True, allow_unicode=True, width=10**9
    ).strip()
    if not (dumped.startswith("[") and dumped.endswith("]")):
        raise MergeError(f"could not serialise list item for a block fold: {item!r}")
    return dumped[1:-1].strip()


def _block_list_bounds(block: list[str], key_idx: int, key_indent: str):
    """For a block-style `key:` at `block[key_idx]`, return (item_indent, end_idx)
    where `end_idx` is the index one past the list's last line.

    A line belongs to the list if it is a `- ` item at the item indent, a deeper-
    indented continuation of one (yaml wraps long scalars), or blank. The list ends
    at the first line indented at-or-shallower than the key that is not an item.
    Returns (None, key_idx + 1) when the key has no items at all (an empty list),
    in which case the caller supplies the indent."""
    item_indent = None
    end = key_idx + 1
    for j in range(key_idx + 1, len(block)):
        ln = block[j]
        if not ln.strip():
            end = j + 1
            continue
        stripped = ln.lstrip(" ")
        indent = ln[: len(ln) - len(stripped)]
        if stripped.startswith("- ") and (item_indent is None or indent == item_indent):
            if item_indent is None:
                # First item fixes the list's indentation; it must be at least as
                # deep as the key, else `key:` had no items and we are looking at
                # a sibling list.
                if len(indent) < len(key_indent):
                    break
                item_indent = indent
            end = j + 1
            continue
        if item_indent is not None and len(indent) > len(item_indent):
            end = j + 1  # continuation line of the previous wrapped item
            continue
        break
    return item_indent, end


def _block_declares_field(block: list[str], map_field: str) -> bool:
    """INDEPENDENT re-ask of "does this atom already declare `map_field`?".

    Deliberately uses a DIFFERENT mechanism from the line-at-a-time scanner in
    `_apply_inbox_to_lines`: it hands the atom block to pyyaml and inspects the
    parsed mapping's keys. That independence is the entire point -- the create
    path must never fire on the strength of the same reasoning that just failed
    to find the field, because writing a second `field:` key silently loses the
    original value (pyyaml keeps the last) while still round-tripping.

    FAIL-CLOSED (R15 fail-silent doctrine: an unavailable check is a FAILED
    check). Anything that leaves absence UNPROVEN -- a block that does not parse,
    or that parses to an unexpected shape -- returns True ("treat as present"),
    which makes the caller abort loudly rather than create a duplicate key.
    Absence is asserted only when pyyaml successfully parses the block into
    exactly one mapping and that mapping has no such key.
    """
    try:
        parsed = yaml.safe_load("".join(block))
    except yaml.YAMLError:
        return True
    if isinstance(parsed, list) and len(parsed) == 1 and isinstance(parsed[0], dict):
        return map_field in parsed[0]
    return True


def _atom_field_indent(block: list[str], atom_id: str) -> str:
    """The indentation of the atom's own top-level fields, read from the block
    itself rather than assumed, so a re-indented map cannot silently mis-nest a
    created field."""
    for ln in block[1:]:
        m = re.match(r"^(\s+)[A-Za-z_][A-Za-z0-9_]*:", ln)
        if m:
            return m.group(1)
    raise MergeError(f"atom '{atom_id}' has no field lines to take indentation from")


def _atom_block_bounds(lines: list[str], atom_id: str) -> tuple[int, int]:
    """[start, end) line indices of the atom whose `- id:` is `atom_id`.
    A block ends at the next top-level list item (`- ` at column 0) or EOF."""
    start = None
    for i, ln in enumerate(lines):
        if ln.rstrip("\n") == f"- id: {atom_id}":
            start = i
            break
    if start is None:
        raise MergeError(f"atom id '{atom_id}' not found in {MATURITY_MAP_YAML.name}")
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("- "):
            end = j
            break
    return start, end


def _apply_inbox_to_lines(lines: list[str], inbox: dict) -> list[str]:
    """Fold one inbox's fields into `lines` (mutates only the target atom's
    block). Returns the new lines list."""
    atom_id = inbox["id"]
    start, end = _atom_block_bounds(lines, atom_id)
    block = lines[start:end]

    # level_current -- scalar replace, indentation preserved
    if "level_current" in inbox and inbox["level_current"] is not None:
        new_val = inbox["level_current"]
        for k, ln in enumerate(block):
            m = re.match(r"^(\s*)level_current:\s*(.*)$", ln)
            if m:
                block[k] = f"{m.group(1)}level_current: {new_val}\n"
                break
        else:
            raise MergeError(f"atom '{atom_id}' has no level_current line to fold")

    # append_evidence / append_simplification -- single-line flow-list append
    for inbox_key, map_field in _APPENDABLE.items():
        additions = inbox.get(inbox_key)
        if not additions:
            continue
        if not isinstance(additions, list):
            raise MergeError(f"{inbox_key} in inbox '{atom_id}' must be a list")
        for k, ln in enumerate(block):
            m = re.match(rf"^(\s*){map_field}:(.*)$", ln, re.DOTALL)
            if not m:
                continue
            flow, trailing = _split_flow_list(m.group(2))
            if flow is not None:
                # (a) single-line flow list: rewrite the one line in place,
                # PRESERVING any trailing comment (hand-authored rationale).
                current = yaml.safe_load(flow)
                if not isinstance(current, list):
                    raise MergeError(
                        f"'{map_field}' on atom '{atom_id}' is not a flow list"
                    )
                current.extend(additions)
                block[k] = (
                    f"{m.group(1)}{map_field}: {_dump_flow_list(current)}{trailing}\n"
                )
                break
            if m.group(2).strip():
                continue  # a scalar or something else -- not a list we can append to
            # (b) block-style list: append `- item` lines after the last existing
            # entry. The map is hand-authored in BOTH styles (30 block-style
            # `simplifications:` at the 2026-07-29 fold that exposed this), so
            # aborting on style -- as this did until then -- left the inbox
            # permanently unfoldable, and an unfoldable inbox never clears, which
            # fail-closes the publish gate forever.
            key_indent = m.group(1)
            item_indent, insert_at = _block_list_bounds(block, k, key_indent)
            if item_indent is None:
                item_indent = key_indent  # empty list: match the map's own style
            block[insert_at:insert_at] = [
                f"{item_indent}- {_dump_block_item(a)}\n" for a in additions
            ]
            break
        else:
            # (c) the field is ABSENT: create it in block style at the end of the
            # atom. A freshly minted atom legitimately has no `evidence:` yet (six
            # did on 2026-07-29, including two in that night's own draw) -- raising
            # here would make the FIRST fork to report on a new atom wedge the
            # publish gate, which is the very fault this function is being fixed for.
            # INDEPENDENT ABSENCE CHECK before creating. The loop above concluded
            # "no such field" from its own parsing; if that parsing has a gap, path
            # (c) writes a SECOND `field:` key and pyyaml silently keeps the last --
            # a corrupted map that still round-trips. Never create on the strength
            # of the same reasoning that failed to find it: re-ask the question a
            # different way, and abort loudly if the two disagree.
            if _block_declares_field(block, map_field):
                raise MergeError(
                    f"atom '{atom_id}' HAS a '{map_field}:' line that the fold could "
                    "not parse -- refusing to create a duplicate key. Fix the parse, "
                    "do not paper over it"
                )
            field_indent = _atom_field_indent(block, atom_id)
            insert_at = len(block)
            while insert_at > 0 and not block[insert_at - 1].strip():
                insert_at -= 1  # keep any trailing blank separator line last
            block[insert_at:insert_at] = [f"{field_indent}{map_field}:\n"] + [
                f"{field_indent}- {_dump_block_item(a)}\n" for a in additions
            ]

    return lines[:start] + block + lines[end:]


def merge(
    map_path: Path = MATURITY_MAP_YAML,
    inbox_dir: Path = INBOX_DIR,
    clear: bool = True,
    dry_run: bool = False,
) -> list[str]:
    """Fold every landed inbox into `map_path` (narrow field merge, in place).

    Returns the sorted list of atom ids that were folded. Raises MergeError on
    any structural violation (unknown atom, same-atom double-target, block-style
    list). On success, clears (deletes) the folded inbox files unless
    `clear=False` or `dry_run=True`.
    """
    inboxes = load_inboxes(inbox_dir)
    if not inboxes:
        return []

    overlap = preflight_inbox_overlap(inboxes)
    if overlap:
        raise MergeError(
            f"pre-flight: {len(overlap)} atom(s) targeted by >1 inbox "
            f"({', '.join(overlap)}) -- re-sequence, do not fold blind"
        )

    text = map_path.read_text()
    lines = text.splitlines(keepends=True)
    for ib in inboxes:
        lines = _apply_inbox_to_lines(lines, ib)
    new_text = "".join(lines)

    # Validate the result still parses as YAML before writing anything.
    parsed = yaml.safe_load(new_text)
    if not isinstance(parsed, list):
        raise MergeError("post-fold map does not parse as a YAML list")

    folded = sorted(ib["id"] for ib in inboxes)
    if dry_run:
        return folded

    map_path.write_text(new_text)
    if clear:
        for ib in inboxes:
            ib["_path"].unlink()
    return folded


def main(argv: list[str]) -> int:
    dry_run = "--dry-run" in argv
    try:
        folded = merge(dry_run=dry_run)
    except MergeError as e:
        print(f"MERGE ABORTED: {e}", file=sys.stderr)
        return 1
    if not folded:
        print("No inboxes to merge.")
    else:
        verb = "would fold" if dry_run else "folded"
        print(f"{verb} {len(folded)} inbox(es): {', '.join(folded)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
