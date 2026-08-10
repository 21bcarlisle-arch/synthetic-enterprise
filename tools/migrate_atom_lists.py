#!/usr/bin/env python3
"""SINGLE-USE migration: rehome the unbounded RECORD LIST fields out of the map (atom H41).

    >>> python3 -m tools.migrate_atom_lists            # migrate in place
    >>> python3 -m tools.migrate_atom_lists --check    # verify round-trip only

=========================  SINGLE-USE  =========================================
A ONE-SHOT, the same move tools/migrate_atom_notes.py made for the store's second
tenant. It is IDEMPOTENT -- a map with no inline list fields is left untouched and
the run is a no-op -- so a second accidental run is harmless. It is NOT a
maintenance tool: ongoing evidence writes go through
tools/simplifications_store.append_to_record_for_atom (which tools/merge_atom_status.py
now calls for `append_evidence`). Do not extend this into an editor.
================================================================================

WHY -- AND WHY H32's MOVE WAS NOT ENOUGH. H32 rehomed the narrative note class and
took the map 464,110 -> 393,692 bytes. Inside 24 hours it was back at 430,962 and
wedging publishing again (WORKER_FINDING_THE_MAP_RATCHET_REPAIR_DID_NOT_HOLD).
That finding's diagnosis is the one this migration acts on: *a ratchet with no
ongoing drain is a one-time cleanup, not a control* -- H32 drained the field that
was largest AT THAT MOMENT and left the refill running.

Measured over the 24h to 2026-08-10 (git-diffed, field by field, on the committed
map -- not estimated):

    evidence        66,699 -> 113,552   +46,853
    exit_evidence        0 ->  20,652   +20,652
    ...                                        (whole map: +67,096 net)

The two list fields ARE the refill. Every other field's growth is atom-COUNT driven
(229 -> 260 atoms brought +19,643 bytes of `name`), which is the map doing its job.
So this migration is chosen to move the FLOW, not merely the biggest stock, and the
control that guards it afterwards is a per-atom budget (invariant to atom count)
rather than only a whole-file ceiling.

WHAT IT DOES (a MOVE, never an edit -- content preservation is the hard invariant):
  * For every atom carrying a field in the list class (simplifications_store.is_record_field:
    `evidence` plus any `*_evidence`), it writes those fields VERBATIM into that atom's
    file in the EXISTING store, docs/design/simplifications/<atom_id>.yaml, under
    `map_records:`. The atom's simplifications register and `map_notes` in that same
    file are preserved untouched (`_write_tenants` is now the sole write path).
  * In the map TEXT it deletes those fields and leaves ONE declaration line,
    `records_rehomed: [<field>, ...]`, at the position of the first field removed.
  * Every OTHER byte of the map is preserved: surgical per-field span removal, NOT a
    yaml re-dump.

REUSE: tools/migrate_atom_lists.py
CLASS: CUSTOM
INDEX: searched "migrate", "simplifications store", "maturity map text edit". The text
       surgery is IMPORTED from tools/migrate_atom_notes.py rather than copied --
       `_atom_blocks`/`_field_span`/`_parse_span`/`_dedent` are indentation-based and
       shape-agnostic, and that module's own docstring records that the generalisation
       "would also have covered the list case". This file therefore contains only what
       genuinely differs: the field class, the value-shape precondition (a list, not a
       non-empty string), and the three proofs re-pointed at the list tenant. Copying
       the scanners would have been the third copy of the same span logic and the first
       one free to drift. CUSTOM because it is harness/map machinery, and SINGLE-USE.

PROOF (built in, three layers -- a migration that loses the artefact trail is the
failure mode, and `evidence` is what every level-move claim rests on):
  1. SPAN PROOF: each removed span is re-parsed standalone and must yield exactly the
     value the whole-file parse gives for that field.
  2. HASH PROOF: the canonical-JSON SHA-256 of {atom_id: {field: [entries]}} from the
     ORIGINAL map must equal the same hash recombined from the store via the loader
     (`simplifications_store.records_load_all`) -- an independent read path.
  3. REMAINDER PROOF: re-parsing the migrated map, every atom's every NON-list field
     must be byte-for-byte the value it had before.
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


# --------------------------------------------------------------------------
# Text surgery (the record-class half; the scanners are imported)
# --------------------------------------------------------------------------
def _record_field_span(block: list[str], key_idx: int) -> int:
    """Index one past the last physical line of the record field at block[key_idx].

    Extends the imported `_field_span` with the one shape the note class could not
    contain: a YAML BLOCK SEQUENCE written at the SAME indent as its key --

        evidence:
        - docs/design/SUBSTEP4_SUPERVISOR_HYBRID.md

    which YAML permits and 5 atoms on the live map actually use. `_field_span` is
    strictly deeper-indent, so it stopped at the key line, `_parse_span` read the
    value as None, and those atoms' evidence would have been silently DROPPED
    rather than moved. Proof layer 1 caught exactly that before anything was
    written -- which is the entire reason the extraction is cross-checked against
    an independent whole-file yaml parse instead of trusted.

    A `- ` line at the FIELD indent can only be a sequence item of the preceding
    key: the next atom's own `- id:` sits at indent 0, strictly less. Blank lines
    are provisional, exactly as in `_field_span`."""
    end = _field_span(block, key_idx)
    key_indent = _indent_of(block[key_idx])
    j = end
    while j < len(block):
        ln = block[j]
        if not ln.strip():
            j += 1
            continue
        if _indent_of(ln) == key_indent and ln.lstrip().startswith("- "):
            j += 1
            end = j
            continue
        break
    return end



def _rewrite_block(block: list[str]) -> tuple[list[str], dict]:
    """Strip every list-class field from one atom block, inserting the
    `records_rehomed` declaration where the first one stood. Returns
    (new_block, {field: [entries]})."""
    lists: dict = {}
    spans: list[tuple[int, int]] = []
    j = 0
    while j < len(block):
        m = KEY_RE.match(block[j])
        if not m or not store.is_record_field(m.group(2)):
            j += 1
            continue
        end = _record_field_span(block, j)
        field, value = _parse_span(block, j, end)
        if field != m.group(2):
            raise MigrationError(f"span key mismatch: {field!r} != {m.group(2)!r}")
        if value is not None and not isinstance(value, (list, str)):
            raise MigrationError(
                f"record field {field!r} is neither a list nor a string "
                f"({type(value).__name__}) -- refusing to rehome a shape the store "
                "cannot represent verbatim"
            )
        # An EMPTY (or explicitly null) list is dropped, not rehomed: `evidence: []`
        # and `evidence: null` carry no record, and storing them would create store
        # files whose only content is an absence -- plus a `records_rehomed`
        # declaration promising content that is not there, which is exactly the
        # fail-open the declaration-matches-store contract test exists to catch.
        # `_lists_subtree` filters on truthiness for the same reason, so the two
        # sides of the hash proof agree about what "has a record" means.
        if not value:
            spans.append((j, end))
            j = end
            continue
        lists[field] = value
        spans.append((j, end))
        j = end
    if not spans:
        return list(block), {}
    indent = " " * _indent_of(block[spans[0][0]])
    cut = {i for s, e in spans for i in range(s, e)}
    out: list[str] = []
    for i, ln in enumerate(block):
        if i == spans[0][0] and lists:
            out.append(f"{indent}{store.RECORDS_DECLARATION_FIELD}: [{', '.join(sorted(lists))}]\n")
        if i not in cut:
            out.append(ln)
    return out, lists


def rewrite_map_text(text: str) -> tuple[str, dict[str, dict]]:
    """(migrated map text, {atom_id: {field: [entries]}}). Pure -- no I/O, so the
    tests can drive it on synthetic maps."""
    lines = text.splitlines(keepends=True)
    extracted: dict[str, dict] = {}
    out: list[str] = []
    blocks = _atom_blocks(lines)
    if not blocks:
        return text, {}
    out.extend(lines[: blocks[0][1]])
    for atom_id, start, end in blocks:
        new_block, lists = _rewrite_block(lines[start:end])
        if lists:
            extracted[atom_id] = lists
        out.extend(new_block)
    return "".join(out), extracted


# --------------------------------------------------------------------------
# Proofs
# --------------------------------------------------------------------------
def _lists_subtree(atoms: list) -> dict[str, dict]:
    """{atom_id: {list_field: [entries]}} over atoms carrying any NON-EMPTY one --
    the exact set the store's list tenant holds (empty lists are dropped, see
    `_rewrite_block`)."""
    out: dict[str, dict] = {}
    for a in atoms:
        if not isinstance(a, dict):
            continue
        found = {k: v for k, v in a.items() if store.is_record_field(k) and v}
        if found:
            out[str(a.get("id"))] = found
    return out


def _hash(subtree: dict[str, dict]) -> str:
    canonical = json.dumps(subtree, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def original_hash(map_path: Path = MATURITY_MAP_YAML) -> str:
    return _hash(_lists_subtree(yaml.safe_load(map_path.read_text(encoding="utf-8"))))


def recombined_hash(store_dir: Path = STORE_DIR) -> str:
    """The hash rebuilt from the store via the LOADER -- an independent read path."""
    return _hash(store.records_load_all(store_dir))


def _remainder(atoms: list) -> dict:
    """Every atom's every NON-list field, keyed by atom id. PROOF LAYER 3."""
    return {
        str(a["id"]): {k: v for k, v in a.items() if not store.is_record_field(k)}
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
    before_lists = _lists_subtree(before_atoms)
    before_remainder = _remainder(before_atoms)

    new_text, extracted = rewrite_map_text(original_text)

    if extracted != before_lists:
        missing = set(before_lists) - set(extracted)
        extra = set(extracted) - set(before_lists)
        raise MigrationError(
            f"span extraction != parsed subtree (missing={sorted(missing)}, "
            f"extra={sorted(extra)})"
        )

    after_atoms = yaml.safe_load(new_text)
    if _lists_subtree(after_atoms):
        raise MigrationError("migrated map still carries inline list fields")
    after_remainder = _remainder(after_atoms)
    for aid, fields in before_remainder.items():
        got = {k: v for k, v in after_remainder.get(aid, {}).items()
               if k != store.RECORDS_DECLARATION_FIELD}
        if got != fields:
            diff = [k for k in set(fields) | set(got) if fields.get(k) != got.get(k)]
            raise MigrationError(f"atom {aid}: non-list fields changed: {diff}")
    for aid, lists in extracted.items():
        declared = after_remainder.get(aid, {}).get(store.RECORDS_DECLARATION_FIELD)
        if sorted(declared or []) != sorted(lists):
            raise MigrationError(
                f"atom {aid}: declaration {declared!r} != rehomed fields {sorted(lists)}"
            )

    result = {
        "atoms_with_lists": len(extracted),
        "list_fields_moved": sum(len(v) for v in extracted.values()),
        "list_entries_moved": sum(len(v) for f in extracted.values() for v in f.values()),
        "map_bytes_before": len(original_text.encode("utf-8")),
        "map_bytes_after": len(new_text.encode("utf-8")),
        "original_hash": _hash(before_lists),
        "applied": False,
    }
    if not apply:
        return result

    # COMMIT. Store FIRST, then the map: a crash between the two leaves the record in
    # BOTH places (recoverable) rather than in neither (a lost artefact trail).
    for aid, lists in extracted.items():
        for field, entries in sorted(lists.items()):
            store.set_record_for_atom(aid, field, entries, store_dir)
    rec = recombined_hash(store_dir)
    if rec != result["original_hash"]:
        raise MigrationError(
            f"recombination hash mismatch: original {result['original_hash']} != store {rec} "
            "-- map NOT rewritten, the record is still inline"
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
