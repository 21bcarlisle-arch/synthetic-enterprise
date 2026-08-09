#!/usr/bin/env python3
"""SINGLE-USE migration: rehome the narrative NOTE fields out of the map (atom H32).

    >>> python3 -m tools.migrate_atom_notes            # migrate in place
    >>> python3 -m tools.migrate_atom_notes --check    # verify round-trip only

=========================  SINGLE-USE  =========================================
A ONE-SHOT, modelled directly on tools/migrate_simplifications.py (the same move,
for the second tenant of the same store). It is IDEMPOTENT -- a map with no inline
note fields is left untouched and the run is a no-op -- so a second accidental run
is harmless. It is NOT a maintenance tool: ongoing note writes go through
tools/simplifications_store.set_note_for_atom. Do not extend this into an editor.
================================================================================

WHY. The 2026-08-09 publish wedge forced the spine size ratchet from 400K to 640K
as an explicit INTERIM, with the reason stated in tests/design/test_simplifications_store.py:
"what is oversized is `build_note`/`harden_note`/`level_hold_note` -- the map's
evidence trail... A control that gets angrier the more faithfully the record is kept
will eventually be paid with the record." That raise named THIS atom as the real fix
and forbade a second raise without it. Measured on the 521,770-byte map: the note
class is 129,750 bytes, 25% of the spine, over just 84 atoms -- `level_hold_note`
alone is 13,791 bytes on ONE atom.

WHAT IT DOES (a MOVE, never an edit -- content preservation is the hard invariant):
  * For every atom carrying any field in the note class (simplifications_store.NOTE_FIELDS
    / anything `*_note`), it writes those fields VERBATIM into that atom's file in the
    EXISTING store, docs/design/simplifications/<atom_id>.yaml, under `map_notes:`.
    The atom's simplifications register in that same file is preserved untouched.
  * In the map TEXT it deletes those fields and leaves ONE declaration line,
    `notes_rehomed: [<field>, ...]`, at the position of the first field removed --
    so the spine still says WHICH notes exist without carrying their prose, and the
    contract test can check the declaration against the store in both directions.
  * Every OTHER byte of the map is preserved: surgical per-field span removal, NOT a
    yaml re-dump (a re-dump would reflow the whole spine and destroy the hand-authored
    form that tools/merge_atom_status.py's text fold relies on).

REUSE: tools/migrate_atom_notes.py
CLASS: CUSTOM
INDEX: searched "migrate", "simplifications store", "maturity map text edit" -- the nearest rows are
       tools/migrate_simplifications.py (the SAME move for the first tenant of the SAME store) and
       tools/merge_atom_status.py (the proven quote/depth-aware map-text scanners). Neither is
       reusable as-is and neither was copied blindly: migrate_simplifications' scanners are shaped
       for a LIST field (flow-vs-block list disambiguation, `_flow_list_lines`), whereas the note
       class is SCALARS in three hand-authored shapes (single-line quoted, wrapped quoted, folded
       block). The generalisation here is `_field_span` -- pure indentation, shape-agnostic, which
       covers all three and would also have covered the list case. What IS reused rather than
       reinvented: the store itself (tools/simplifications_store.py, extended with the note tenant
       instead of a second parallel store), and the three-layer proof discipline that file
       established. This is harness/map machinery -- the product, not mathematics -- so CUSTOM, and
       it is SINGLE-USE besides.

PROOF (built in, three layers -- a migration that loses prose is the failure mode):
  1. SPAN PROOF: each removed span is re-parsed standalone and must yield exactly the
     value the whole-file parse gives for that field. A span scanner that swallowed a
     neighbouring field, or clipped a folded block scalar, fails HERE, before any write.
  2. HASH PROOF: the canonical-JSON SHA-256 of {atom_id: {field: text}} from the ORIGINAL
     map must equal the same hash recombined from the store via the loader
     (`simplifications_store.notes_load_all`) -- an independent read path.
  3. REMAINDER PROOF: re-parsing the migrated map, every atom's every NON-note field
     must be byte-for-byte the value it had before. This is what catches a span that
     ate one line too many.
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


class MigrationError(Exception):
    """A structural precondition of the migration was violated."""


# --------------------------------------------------------------------------
# Text surgery
# --------------------------------------------------------------------------
def _atom_blocks(lines: list[str]) -> list[tuple[str, int, int]]:
    """(atom_id, start, end) for every top-level `- id: X` block."""
    starts = [i for i, ln in enumerate(lines) if ln.startswith("- id: ")]
    out = []
    for n, i in enumerate(starts):
        end = starts[n + 1] if n + 1 < len(starts) else len(lines)
        out.append((lines[i][len("- id: "):].strip(), i, end))
    return out


def _indent_of(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def _dedent(line: str, n: int) -> str:
    """Strip up to `n` leading SPACES, never more than the line actually has.

    A plain slice `line[n:]` is wrong and was the second bug proof layer 1 caught:
    an empty line inside a block scalar is exactly "\\n", so `"\\n"[2:]` is "" -- the
    line disappears, and with it the PARAGRAPH BREAK it encoded. In a folded (`>-`)
    scalar that break is a real newline in the value, so dropping it silently
    reflowed two atoms' prose into one paragraph."""
    drop = min(n, len(line) - len(line.lstrip(" ")))
    return line[drop:]


def _field_span(block: list[str], key_idx: int) -> int:
    """Index one past the last physical line of the field starting at block[key_idx].

    Indent-based and shape-agnostic, which is what makes it safe across every form
    these notes are hand-authored in: a single-line double-quoted scalar, a wrapped
    quoted scalar, and a folded block scalar (`>-`) all continue on lines indented
    DEEPER than the key. A sibling field or the next atom's `- id:` is at the key's
    indent or less, and terminates the span. Blank lines are provisional: consumed
    only if more deeply-indented content follows (a trailing blank separates fields).
    """
    key_indent = _indent_of(block[key_idx])
    end = key_idx + 1
    for j in range(key_idx + 1, len(block)):
        ln = block[j]
        if not ln.strip():
            continue  # provisional -- only kept if a later deeper line extends `end`
        if _indent_of(ln) > key_indent:
            end = j + 1
            continue
        break
    return end


def _parse_span(block: list[str], key_idx: int, end: int) -> tuple[str, object]:
    """Re-parse a removed span standalone -> (field, value). PROOF LAYER 1: the span
    must be a complete, self-contained YAML mapping of exactly one key."""
    key_indent = _indent_of(block[key_idx])
    # `block` lines keep their line endings, so join with "" -- joining with "\n"
    # inserts a blank line between every pair, and a blank line inside a FOLDED
    # (`>-`) scalar is a paragraph break that survives as a literal newline. That
    # silently reflowed four `notes:` blocks until proof layer 1 caught it.
    text = "".join(_dedent(ln, key_indent) for ln in block[key_idx:end])
    parsed = yaml.safe_load(text)
    if not isinstance(parsed, dict) or len(parsed) != 1:
        raise MigrationError(
            f"span at line {key_idx} did not re-parse as exactly one field: {text[:200]!r}"
        )
    (field, value), = parsed.items()
    return str(field), value


def _rewrite_block(block: list[str]) -> tuple[list[str], dict]:
    """Strip every note field from one atom block, inserting the `notes_rehomed`
    declaration where the first one stood. Returns (new_block, {field: value})."""
    notes: dict = {}
    spans: list[tuple[int, int]] = []
    key_re = re.compile(r"^(\s+)([A-Za-z_][A-Za-z0-9_]*):")
    j = 0
    while j < len(block):
        m = key_re.match(block[j])
        if not m or not store.is_note_field(m.group(2)):
            j += 1
            continue
        end = _field_span(block, j)
        field, value = _parse_span(block, j, end)
        if field != m.group(2):
            raise MigrationError(f"span key mismatch: {field!r} != {m.group(2)!r}")
        if not isinstance(value, str) or not value.strip():
            raise MigrationError(
                f"note {field!r} is not a non-empty string ({type(value).__name__}) "
                "-- refusing to rehome a shape the store cannot represent"
            )
        notes[field] = value
        spans.append((j, end))
        j = end
    if not spans:
        return list(block), {}
    indent = " " * _indent_of(block[spans[0][0]])
    decl = f"{indent}{store.NOTES_DECLARATION_FIELD}: [{', '.join(sorted(notes))}]\n"
    out: list[str] = []
    cut = {i for s, e in spans for i in range(s, e)}
    for i, ln in enumerate(block):
        if i == spans[0][0]:
            out.append(decl)
        if i not in cut:
            out.append(ln)
    return out, notes


def rewrite_map_text(text: str) -> tuple[str, dict[str, dict]]:
    """(migrated map text, {atom_id: {field: value}}). Pure -- no I/O, so the tests
    can drive it on synthetic maps."""
    lines = text.splitlines(keepends=True)
    extracted: dict[str, dict] = {}
    out: list[str] = []
    blocks = _atom_blocks(lines)
    if not blocks:
        return text, {}
    out.extend(lines[: blocks[0][1]])
    for atom_id, start, end in blocks:
        new_block, notes = _rewrite_block(lines[start:end])
        if notes:
            extracted[atom_id] = notes
        out.extend(new_block)
    return "".join(out), extracted


# --------------------------------------------------------------------------
# Proofs
# --------------------------------------------------------------------------
def _notes_subtree(atoms: list) -> dict[str, dict]:
    """{atom_id: {note_field: text}} over atoms that carry any -- the exact set the
    store's note tenant holds."""
    out: dict[str, dict] = {}
    for a in atoms:
        if not isinstance(a, dict):
            continue
        found = {k: v for k, v in a.items() if store.is_note_field(k)}
        if found:
            out[str(a.get("id"))] = found
    return out


def _hash(subtree: dict[str, dict]) -> str:
    canonical = json.dumps(subtree, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def original_hash(map_path: Path = MATURITY_MAP_YAML) -> str:
    return _hash(_notes_subtree(yaml.safe_load(map_path.read_text(encoding="utf-8"))))


def recombined_hash(store_dir: Path = STORE_DIR) -> str:
    """The hash rebuilt from the store via the LOADER -- an independent read path."""
    return _hash(store.notes_load_all(store_dir))


def _remainder(atoms: list) -> dict:
    """Every atom's every NON-note field, keyed by atom id. PROOF LAYER 3."""
    return {
        str(a["id"]): {k: v for k, v in a.items() if not store.is_note_field(k)}
        for a in atoms
        if isinstance(a, dict) and a.get("id")
    }


# --------------------------------------------------------------------------
# Driver
# --------------------------------------------------------------------------
def migrate(
    map_path: Path = MATURITY_MAP_YAML,
    store_dir: Path = STORE_DIR,
    apply: bool = True,
) -> dict:
    original_text = map_path.read_text(encoding="utf-8")
    before_atoms = yaml.safe_load(original_text)
    before_notes = _notes_subtree(before_atoms)
    before_remainder = _remainder(before_atoms)

    new_text, extracted = rewrite_map_text(original_text)

    if extracted != before_notes:
        missing = set(before_notes) - set(extracted)
        extra = set(extracted) - set(before_notes)
        raise MigrationError(
            f"span extraction != parsed subtree (missing={sorted(missing)}, "
            f"extra={sorted(extra)})"
        )

    after_atoms = yaml.safe_load(new_text)
    if _notes_subtree(after_atoms):
        raise MigrationError("migrated map still carries inline note fields")
    after_remainder = _remainder(after_atoms)
    for aid, fields in before_remainder.items():
        got = {k: v for k, v in after_remainder.get(aid, {}).items()
               if k != store.NOTES_DECLARATION_FIELD}
        if got != fields:
            diff = [k for k in set(fields) | set(got) if fields.get(k) != got.get(k)]
            raise MigrationError(f"atom {aid}: non-note fields changed: {diff}")
    for aid, notes in extracted.items():
        declared = after_remainder.get(aid, {}).get(store.NOTES_DECLARATION_FIELD)
        if sorted(declared or []) != sorted(notes):
            raise MigrationError(
                f"atom {aid}: declaration {declared!r} != rehomed fields {sorted(notes)}"
            )

    result = {
        "atoms_with_notes": len(extracted),
        "note_fields_moved": sum(len(v) for v in extracted.values()),
        "map_bytes_before": len(original_text.encode("utf-8")),
        "map_bytes_after": len(new_text.encode("utf-8")),
        "original_hash": _hash(before_notes),
        "applied": False,
    }
    if not apply:
        return result

    # COMMIT. Store FIRST, then the map: a crash between the two leaves the prose in
    # BOTH places (recoverable) rather than in neither (a lost record).
    for aid, notes in extracted.items():
        for field, text in sorted(notes.items()):
            store.set_note_for_atom(aid, field, text, store_dir)
    rec = recombined_hash(store_dir)
    if rec != result["original_hash"]:
        raise MigrationError(
            f"recombination hash mismatch: original {result['original_hash']} != store {rec} "
            "-- map NOT rewritten, prose is still inline"
        )
    map_path.write_text(new_text, encoding="utf-8")
    result["applied"] = True
    result["recombined_hash"] = rec
    return result


def main(argv: list[str]) -> int:
    check_only = "--check" in argv
    res = migrate(apply=not check_only)
    print(json.dumps(res, indent=2))
    if check_only:
        print(f"recombined_hash (current store): {recombined_hash()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
