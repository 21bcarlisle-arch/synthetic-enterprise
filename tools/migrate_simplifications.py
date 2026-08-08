#!/usr/bin/env python3
"""SINGLE-USE migration: extract the simplifications register out of the map.

    >>> python3 -m tools.migrate_simplifications            # migrate in place
    >>> python3 -m tools.migrate_simplifications --check    # verify round-trip only

=========================  SINGLE-USE  =========================================
This is a ONE-SHOT. It runs once, on the un-migrated map, to populate
docs/design/simplifications/ and shrink the map. It is IDEMPOTENT (a map with no
`simplifications` field is left untouched and the run is a no-op), so a second
accidental run is harmless -- but it is not a maintenance tool. Ongoing writes to
the store go through tools/simplifications_store.append_for_atom (driven by
tools/merge_atom_status.py). Do not extend this file into a general editor.
================================================================================

WHAT IT DOES (a MOVE, never an edit -- content preservation is the hard
invariant):
  * For every atom whose `simplifications` list is non-empty, it writes
    docs/design/simplifications/<atom_id>.yaml containing that atom's list
    VERBATIM (no rewording, no restructuring of any entry).
  * In the map TEXT it replaces the atom's `simplifications:` field -- however it
    is hand-authored (flow list, block list, wrapped, commented, or empty) -- with
    a single `simplifications_count: <N>` line, preserving indentation. An atom
    with an EMPTY list gets no count and no store file (N == 0).
  * Every OTHER byte of the map is preserved: this is a surgical per-field
    replacement, NOT a yaml re-dump (a re-dump would reflow the whole spine and
    destroy the hand-authored form that tools/merge_atom_status.py relies on).

PROOF (built in): the canonical-JSON SHA-256 of {atom_id: simplifications_subtree}
computed from the ORIGINAL map must equal the same hash computed from
(new map counts + store recombination via the loader). `--check` prints both.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

import yaml

PROJECT = Path(__file__).resolve().parent.parent
MATURITY_MAP_YAML = PROJECT / "docs" / "design" / "maturity_map.yaml"
STORE_DIR = PROJECT / "docs" / "design" / "simplifications"

if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

from tools import simplifications_store as store  # noqa: E402

_SIMPL_LINE = re.compile(r"^(\s*)simplifications:(.*)$", re.DOTALL)


# --------------------------------------------------------------------------
# Quote/depth-aware span scanners (modelled on the proven scanners in
# tools/merge_atom_status.py, which are validated against this exact map).
# --------------------------------------------------------------------------
def _flow_list_lines(rest: str, block_tail: str) -> int | None:
    """For a `simplifications:` whose value opens a FLOW list `[...]`, return how
    many EXTRA physical lines the list spans past the key line (0 == single line).
    `rest` is the text after the colon on the key line; `block_tail` is every
    following line in the atom block. Returns None if `rest` does not open a flow
    list."""
    s = (rest + block_tail)
    stripped = rest.lstrip()
    if not stripped.startswith("["):
        return None
    # scan from the first '[' in the combined text
    i = s.index("[")
    depth = 0
    quote = None
    while i < len(s):
        ch = s[i]
        if quote == '"':
            if ch == "\\":
                i += 2
                continue
            if ch == '"':
                quote = None
        elif quote == "'":
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
                consumed = s[: i + 1]
                return consumed.count("\n")
        i += 1
    return None


def _block_list_end(block: list[str], key_idx: int, key_indent: str) -> int:
    """For a block-style `simplifications:` at block[key_idx], return the index one
    past the list's last line. A line belongs to the list if it is a `- ` item at
    the item indent, a deeper-indented continuation of one, or blank BETWEEN items.
    Trailing blank lines are NOT consumed (they separate the field from its
    sibling)."""
    item_indent = None
    end = key_idx + 1
    for j in range(key_idx + 1, len(block)):
        ln = block[j]
        if not ln.strip():
            continue  # provisional: only kept if a later item extends `end` past it
        stripped = ln.lstrip(" ")
        indent = ln[: len(ln) - len(stripped)]
        if stripped.startswith("- ") and (item_indent is None or indent == item_indent):
            if item_indent is None:
                if len(indent) < len(key_indent):
                    break
                item_indent = indent
            end = j + 1
            continue
        if item_indent is not None and len(indent) > len(item_indent):
            end = j + 1
            continue
        break
    return end


def _atom_blocks(lines: list[str]) -> list[tuple[str, int, int]]:
    """(atom_id, start, end) for every top-level `- id: X` block."""
    starts = [i for i, ln in enumerate(lines) if ln.startswith("- id: ")]
    out = []
    for n, i in enumerate(starts):
        end = starts[n + 1] if n + 1 < len(starts) else len(lines)
        atom_id = lines[i][len("- id: "):].strip()
        out.append((atom_id, i, end))
    return out


def _replace_field_in_block(block: list[str], count: int) -> list[str]:
    """Replace the `simplifications:` field in one atom block with a
    `simplifications_count: <count>` line (or remove it entirely when count==0).
    Returns the new block. Raises if the block has no such field."""
    for k, ln in enumerate(block):
        m = _SIMPL_LINE.match(ln)
        if not m:
            continue
        indent, rest = m.group(1), m.group(2)
        block_tail = "".join(block[k + 1:])
        span = _flow_list_lines(rest, block_tail)
        if span is not None:
            last = k + span  # inclusive last physical line of the flow list
        elif rest.strip() == "":
            last = _block_list_end(block, k, indent) - 1
        else:
            raise MigrationError(
                f"unrecognised simplifications value shape: {ln!r}"
            )
        replacement = (
            [] if count == 0 else [f"{indent}simplifications_count: {count}\n"]
        )
        return block[:k] + replacement + block[last + 1:]
    raise MigrationError("atom block has no simplifications field")


class MigrationError(Exception):
    """A structural precondition of the migration was violated."""


# --------------------------------------------------------------------------
# Round-trip proof
# --------------------------------------------------------------------------
def _canonical_subtree_map(atoms: list) -> dict[str, list]:
    """{atom_id: simplifications_list} over atoms with a NON-EMPTY list -- the
    exact set the store holds. Empty lists carry no store file and no count."""
    out: dict[str, list] = {}
    for a in atoms:
        if not isinstance(a, dict):
            continue
        s = a.get("simplifications")
        if isinstance(s, list) and s:
            out[str(a.get("id"))] = s
    return out


def _hash(subtree: dict[str, list]) -> str:
    canonical = json.dumps(subtree, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def original_hash(map_path: Path = MATURITY_MAP_YAML) -> str:
    atoms = yaml.safe_load(map_path.read_text(encoding="utf-8"))
    return _hash(_canonical_subtree_map(atoms))


def recombined_hash(map_path: Path = MATURITY_MAP_YAML, store_dir: Path = STORE_DIR) -> str:
    """The hash rebuilt from (migrated map + loader). Uses the loader's load_all(),
    keyed to the store files -- the independent recombination the PR must match."""
    return _hash(store.load_all(store_dir))


def is_migrated(map_path: Path = MATURITY_MAP_YAML) -> bool:
    """True once the map carries no `simplifications` field anywhere."""
    text = map_path.read_text(encoding="utf-8")
    return not any(_SIMPL_LINE.match(ln) for ln in text.splitlines(keepends=True))


# --------------------------------------------------------------------------
# Migration
# --------------------------------------------------------------------------
def migrate(map_path: Path = MATURITY_MAP_YAML, store_dir: Path = STORE_DIR) -> dict:
    """Run the one-shot migration in place. Returns a summary dict. Idempotent:
    a map already free of the field is left untouched."""
    atoms = yaml.safe_load(map_path.read_text(encoding="utf-8"))
    if not isinstance(atoms, list):
        raise MigrationError("map does not parse as a YAML list")

    before_hash = _hash(_canonical_subtree_map(atoms))

    if is_migrated(map_path):
        return {
            "migrated": False,
            "reason": "map already has no simplifications field (idempotent no-op)",
            "store_files": len(list(store_dir.glob("*.yaml"))) if store_dir.is_dir() else 0,
        }

    # 1) write the store, verbatim, for every atom with a non-empty list.
    counts: dict[str, int] = {}
    store_dir.mkdir(parents=True, exist_ok=True)
    for a in atoms:
        if not isinstance(a, dict):
            continue
        aid = str(a.get("id"))
        notes = a.get("simplifications")
        counts[aid] = len(notes) if isinstance(notes, list) else 0
        if isinstance(notes, list) and notes:
            (store_dir / f"{aid}.yaml").write_text(store._dump(aid, notes), encoding="utf-8")

    # 2) surgically replace each atom's field in the map text.
    lines = map_path.read_text(encoding="utf-8").splitlines(keepends=True)
    blocks = _atom_blocks(lines)
    new_lines: list[str] = list(lines[: blocks[0][1]]) if blocks else list(lines)
    for aid, start, end in blocks:
        block = lines[start:end]
        has_field = any(_SIMPL_LINE.match(ln) for ln in block)
        if has_field:
            block = _replace_field_in_block(block, counts.get(aid, 0))
        new_lines.extend(block)
    new_text = "".join(new_lines)

    # 3) validate: the result parses, carries no field, and the round-trip holds.
    reparsed = yaml.safe_load(new_text)
    if not isinstance(reparsed, list):
        raise MigrationError("post-migration map does not parse as a YAML list")
    if any(_SIMPL_LINE.match(ln) for ln in new_text.splitlines(keepends=True)):
        raise MigrationError("post-migration map still contains a simplifications field")

    map_path.write_text(new_text, encoding="utf-8")
    after_hash = _hash(store.load_all(store_dir))
    if before_hash != after_hash:
        raise MigrationError(
            f"ROUND-TRIP MISMATCH: original {before_hash} != recombined {after_hash} "
            "-- migration aborted (content not preserved)"
        )

    return {
        "migrated": True,
        "store_files": sum(1 for v in counts.values() if v > 0),
        "atoms_with_empty_list": sum(1 for v in counts.values() if v == 0),
        "total_notes": sum(counts.values()),
        "original_hash": before_hash,
        "recombined_hash": after_hash,
    }


def _main(argv: list[str]) -> int:
    if "--check" in argv:
        # The round-trip proof is meaningful only against the ORIGINAL map. Once
        # migrated, the map's field is gone, so `original_hash()` would read an
        # empty subtree -- comparing it to the store would always mismatch and
        # mislead. Report the correct invariant for each state instead.
        if is_migrated():
            atoms = yaml.safe_load(MATURITY_MAP_YAML.read_text(encoding="utf-8"))
            by_id = {a["id"]: a for a in atoms if isinstance(a, dict) and a.get("id")}
            all_notes = store.load_all(STORE_DIR)
            mism = [aid for aid, notes in all_notes.items()
                    if by_id.get(aid, {}).get("simplifications_count") != len(notes)]
            print(json.dumps({
                "is_migrated": True,
                "store_hash": recombined_hash(),
                "store_atoms": len(all_notes),
                "count_mismatches": mism,
                "note": "the migrate() round-trip was verified at migration time; "
                        "post-migration the standing invariant is map-count == store-count",
            }, indent=2))
        else:
            # Pre-migration dry run: does the round-trip hold if we migrate now?
            print(json.dumps({
                "is_migrated": False,
                "original_hash": original_hash(),
                "note": "run without --check to migrate; migrate() re-verifies the "
                        "round-trip and aborts on any mismatch",
            }, indent=2))
        return 0
    summary = migrate()
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
