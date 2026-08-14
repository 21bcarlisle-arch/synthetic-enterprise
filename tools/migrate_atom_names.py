#!/usr/bin/env python3
"""SINGLE-USE migration: rehome the atom BRIEF (`name`) out of the map into the note tenant.

    >>> python3 -m tools.migrate_atom_names            # migrate in place
    >>> python3 -m tools.migrate_atom_names --check    # proofs only, write nothing

=========================  SINGLE-USE  =========================================
A ONE-SHOT, the fourth of the same move (FM-1 `simplifications`, H32 `map_notes`,
H41 `map_records`). IDEMPOTENT -- a map with no inline `name` is left untouched.
It is NOT a maintenance tool: ongoing brief writes go through
`simplifications_store.set_note_for_atom`, and an inline `name` is refused at
commit time by `test_atom_notes_store.py::test_map_carries_no_inline_note_fields`
once `name` is in the note class.
================================================================================

WHY THIS FIELD, AND WHY THE EARLIER MIGRATIONS SAID IT WAS FINE. Both prior drains
explicitly EXEMPTED `name`, on the stated ground that it is atom-COUNT driven growth
-- "a new atom's `name`/`lane`/levels ... which is the map doing its job"
(tools/migrate_atom_lists.py) and "Every other map field's growth is atom-COUNT
driven" (simplifications_store.py, the `map_records` tenant comment). That was TRUE
WHEN WRITTEN and is now FALSE, which is why it is restated here rather than deleted.

Measured on the live map 2026-08-14 (296 atoms, 410,095 B), `name` bytes by map
position -- the map is append-ordered, so position is mint recency:

    oldest 50 atoms     mean    91 B    max   310 B     <- a name
    middle 50 atoms     mean 1,253 B    max 4,929 B     <- a brief
    newest 50 atoms     mean   860 B    max 4,060 B

    whole field: 150,389 B over 296 atoms (mean 508 B) = 37% OF THE ENTIRE SPINE
    25 atoms carry 67,585 B of it -- 45% of the field in 8% of the atoms

A field whose per-atom cost rises 9x from the oldest atoms to the newest is not
count-driven growth; it is ACCRETION wearing an identity field's name. `name`
became the atom's narrative BRIEF (the D-series entries are multi-KB Expert-Hour
write-ups), which is precisely the unbounded-prose class H32 rehomed under a
different field name. The count-driven half of the original claim survives intact
for `lane`/`level_*`/`loop_stage`, and those stay in the spine.

THE FLOW, NOT JUST THE STOCK. The lesson every prior drain paid for is that moving
a stock while leaving the flow running brings the wedge back (H32's drain was back
over the ratchet in 24h). Here the flow is stopped BY CONSTRUCTION rather than by
discipline: adding `name` to `simplifications_store.NOTE_FIELDS` makes
`check_no_inline_notes` refuse an inline `name`, so a mint that writes the brief
into the spine is UNCOMMITTABLE once the store-contract tests are reachable from a
map edit (which is the sibling half of this atom's repair -- see
`tools/pre_commit_test_gate.py::LEVEL_SENSITIVE_TESTS`).

WHY THIS FILE EXISTS AT ALL, RATHER THAN RE-RUNNING tools/migrate_atom_notes.py.
That module migrates by `store.is_note_field` and would pick `name` up for free --
but its `_rewrite_block` INSERTS a fresh `notes_rehomed:` line at the first removed
span unconditionally. It ran when no atom had that declaration yet. 81 atoms carry
one now, so re-running it would leave those atoms with TWO `notes_rehomed:` keys in
one block -- a YAML duplicate key, which PyYAML resolves silently to the last one,
dropping the earlier declaration and making the declaration-matches-store contract
read as satisfied while a field's declaration had been discarded. This file exists
for exactly that difference: it MERGES into an existing declaration. Everything
else -- the indentation-based span surgery and all three proofs -- is imported.

REUSE: tools/migrate_atom_names.py
CLASS: CUSTOM
INDEX: searched "migrate", "simplifications store", "maturity map text edit",
       "notes_rehomed". `_atom_blocks`/`_field_span`/`_parse_span`/`_dedent`/`KEY_RE`
       are imported from tools/migrate_atom_notes.py (as tools/migrate_atom_lists.py
       already does) rather than copied -- a third copy of the span logic would be
       the first one free to drift. CUSTOM because it is harness/map machinery, and
       SINGLE-USE.

PROOF (built in, four layers -- three inherited in shape from the sibling
migrations, plus one this migration's merge step needs):
  1. SPAN PROOF: each removed span is re-parsed standalone and must yield exactly
     the value the whole-file parse gives for that field.
  2. HASH PROOF: the canonical-JSON SHA-256 of {atom_id: {field: text}} taken from
     the ORIGINAL map must equal the same hash recombined from the store through
     the LOADER (`simplifications_store.notes_load_all`) -- an independent read
     path, not the dict this process just built.
  3. REMAINDER PROOF: re-parsing the migrated map, every atom's every non-note
     field must be byte-for-byte the value it had before.
  4. DECLARATION PROOF: no atom block may contain more than one `notes_rehomed:`
     key (the duplicate-key failure this file was written to avoid), and each
     atom's merged declaration must equal the sorted union of what it already
     declared and what this run moved.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import yaml

PROJECT = Path(__file__).resolve().parent.parent
MATURITY_MAP_YAML = PROJECT / "docs" / "design" / "maturity_map.yaml"
STORE_DIR = PROJECT / "docs" / "design" / "simplifications"

if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

from tools import simplifications_store as store  # noqa: E402
from tools.migrate_atom_notes import (  # noqa: E402  -- REUSE, see INDEX above
    KEY_RE,
    MigrationError,
    _atom_blocks,
    _field_span,
    _indent_of,
    _parse_span,
)

DECL = store.NOTES_DECLARATION_FIELD


# --------------------------------------------------------------------------
# Text surgery (only the declaration-merge half; the scanners are imported)
# --------------------------------------------------------------------------
def _rewrite_block(block: list[str]) -> tuple[list[str], dict, list[str]]:
    """Strip every inline note-class field from one atom block and emit ONE merged
    `notes_rehomed` declaration. Returns (new_block, {field: text}, merged_decl).

    The declaration is placed at the position of the first span removed -- the
    existing declaration line counts as a span, so an atom that already had one
    keeps the declaration where the reader last saw it rather than having it jump
    to wherever the brief happened to sit."""
    notes: dict = {}
    spans: list[tuple[int, int]] = []
    existing: list[str] = []
    j = 0
    while j < len(block):
        m = KEY_RE.match(block[j])
        if not m:
            j += 1
            continue
        key = m.group(2)
        if key == DECL:
            end = _field_span(block, j)
            _, value = _parse_span(block, j, end)
            if value is not None and not isinstance(value, list):
                raise MigrationError(
                    f"{DECL} is {type(value).__name__}, expected a list"
                )
            existing.extend(str(v) for v in (value or []))
            spans.append((j, end))
            j = end
            continue
        if not store.is_note_field(key):
            j += 1
            continue
        end = _field_span(block, j)
        field, value = _parse_span(block, j, end)
        if field != key:
            raise MigrationError(f"span key mismatch: {field!r} != {key!r}")
        if not isinstance(value, str) or not value.strip():
            raise MigrationError(
                f"note {field!r} is not a non-empty string ({type(value).__name__}) "
                "-- refusing to rehome a shape the store cannot represent"
            )
        notes[field] = value
        spans.append((j, end))
        j = end

    if not notes:
        # Nothing moved. Leave the block EXACTLY as found, including any existing
        # declaration -- a no-op run must not reformat the map.
        return list(block), {}, sorted(set(existing))

    merged = sorted(set(existing) | set(notes))
    indent = " " * _indent_of(block[spans[0][0]])
    cut = {i for s, e in spans for i in range(s, e)}
    out: list[str] = []
    for i, ln in enumerate(block):
        if i == spans[0][0]:
            out.append(f"{indent}{DECL}: [{', '.join(merged)}]\n")
        if i not in cut:
            out.append(ln)
    return out, notes, merged


def rewrite_map_text(text: str) -> tuple[str, dict[str, dict], dict[str, list[str]]]:
    """(migrated text, {atom_id: {field: text}}, {atom_id: merged declaration}).
    Pure -- no I/O, so the tests can drive it on synthetic maps."""
    lines = text.splitlines(keepends=True)
    extracted: dict[str, dict] = {}
    decls: dict[str, list[str]] = {}
    out: list[str] = []
    blocks = _atom_blocks(lines)
    if not blocks:
        return text, {}, {}
    out.extend(lines[: blocks[0][1]])
    for atom_id, start, end in blocks:
        new_block, notes, merged = _rewrite_block(lines[start:end])
        if notes:
            extracted[atom_id] = notes
        if merged:
            decls[atom_id] = merged
        out.extend(new_block)
    return "".join(out), extracted, decls


# --------------------------------------------------------------------------
# Proofs
# --------------------------------------------------------------------------
def _notes_subtree(atoms: list) -> dict[str, dict]:
    """{atom_id: {note_field: text}} over atoms carrying any INLINE one."""
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


def _remainder(atoms: list) -> dict:
    """Every atom's every NON-note field, keyed by atom id. PROOF LAYER 3."""
    return {
        str(a["id"]): {k: v for k, v in a.items() if not store.is_note_field(k)}
        for a in atoms
        if isinstance(a, dict) and a.get("id")
    }


def _duplicate_declarations(text: str) -> list[str]:
    """Atom ids whose block carries more than one `notes_rehomed:` key. PROOF
    LAYER 4 -- the duplicate-key failure this module exists to avoid, checked on
    the TEXT because yaml.safe_load resolves duplicates silently and would report
    a clean parse over exactly the corruption being looked for."""
    lines = text.splitlines(keepends=True)
    dupes = []
    for atom_id, start, end in _atom_blocks(lines):
        n = sum(
            1 for ln in lines[start:end]
            if (m := KEY_RE.match(ln)) and m.group(2) == DECL
        )
        if n > 1:
            dupes.append(f"{atom_id}: {n} `{DECL}` keys")
    return dupes


def recombined_hash(store_dir: Path = STORE_DIR) -> str:
    """The note tenant rebuilt from the store via the LOADER -- independent path."""
    return _hash(store.notes_load_all(store_dir))


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
    before_inline = _notes_subtree(before_atoms)
    before_remainder = _remainder(before_atoms)

    new_text, extracted, decls = rewrite_map_text(original_text)

    # PROOF 1 -- span extraction must agree with the independent whole-file parse.
    if extracted != before_inline:
        missing = set(before_inline) - set(extracted)
        extra = set(extracted) - set(before_inline)
        raise MigrationError(
            f"span extraction != parsed subtree (missing={sorted(missing)}, "
            f"extra={sorted(extra)})"
        )

    after_atoms = yaml.safe_load(new_text)
    if _notes_subtree(after_atoms):
        raise MigrationError("migrated map still carries inline note fields")

    # PROOF 4 -- no atom may end up with two declarations.
    if dupes := _duplicate_declarations(new_text):
        raise MigrationError("duplicate declarations:\n  " + "\n  ".join(dupes))

    # PROOF 3 -- every non-note field byte-identical, declaration aside.
    after_remainder = _remainder(after_atoms)
    for aid, fields in before_remainder.items():
        got = {k: v for k, v in after_remainder.get(aid, {}).items() if k != DECL}
        want = {k: v for k, v in fields.items() if k != DECL}
        if got != want:
            diff = [k for k in set(want) | set(got) if want.get(k) != got.get(k)]
            raise MigrationError(f"atom {aid}: non-note fields changed: {diff}")

    # The merged declaration must be the union of prior + moved, per atom.
    for aid, merged in decls.items():
        declared = after_remainder.get(aid, {}).get(DECL)
        if sorted(declared or []) != sorted(merged):
            raise MigrationError(
                f"atom {aid}: declaration {declared!r} != merged {sorted(merged)}"
            )

    moved_bytes = sum(
        len(str(v).encode("utf-8")) for f in extracted.values() for v in f.values()
    )
    result = {
        "atoms_with_moved_notes": len(extracted),
        "note_fields_moved": sum(len(v) for v in extracted.values()),
        "note_value_bytes_moved": moved_bytes,
        "map_bytes_before": len(original_text.encode("utf-8")),
        "map_bytes_after": len(new_text.encode("utf-8")),
        "inline_hash": _hash(before_inline),
        "applied": False,
    }
    if not apply:
        return result

    # COMMIT. Store FIRST, then the map: a crash between the two leaves the brief in
    # BOTH places (recoverable) rather than in neither (a lost record).
    store_before = store.notes_load_all(store_dir)
    for aid, notes in extracted.items():
        for field, text in sorted(notes.items()):
            store.set_note_for_atom(aid, field, text, store_dir)

    # PROOF 2 -- recombine through the loader. The expected tenant is what the store
    # ALREADY held merged with what this run moved, because earlier migrations put
    # the other note fields there; comparing against `before_inline` alone would
    # fail for a reason that is not a defect.
    expected = {aid: dict(v) for aid, v in store_before.items()}
    for aid, notes in extracted.items():
        expected.setdefault(aid, {}).update(notes)
    rec = recombined_hash(store_dir)
    if rec != _hash(expected):
        raise MigrationError(
            f"recombination hash mismatch: expected {_hash(expected)} != store {rec} "
            "-- map NOT rewritten, the brief is still inline"
        )
    map_path.write_text(new_text, encoding="utf-8")
    result["applied"] = True
    result["recombined_hash"] = rec
    return result


def main(argv: list[str]) -> int:
    check_only = "--check" in argv
    res = migrate(apply=not check_only)
    print(json.dumps(res, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
