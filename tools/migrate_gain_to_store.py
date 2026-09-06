#!/usr/bin/env python3
"""SINGLE-USE migration: rehome the atom `gain` field out of the map (atom H41).

    >>> python3 -m tools.migrate_gain_to_store --check    # prove, write nothing
    >>> python3 -m tools.migrate_gain_to_store            # migrate in place

=========================  SINGLE-USE  =========================================
A ONE-SHOT. It is IDEMPOTENT -- a map with no inline `gain` is left untouched and the
run is a no-op -- so a second accidental run is harmless. It is NOT a maintenance
tool: ongoing writes go through `simplifications_store.set_note_for_atom`, and the
inline field is refused from here on by `check_no_inline_notes`.
================================================================================

WHY. H32 moved the note class and took the map 521,770 -> 393,692 B; the spine ratchet
came back down to 400K on the strength of it. ELEVEN DAYS LATER the map was at 408,540 B
of a 409,600 B ceiling -- 0.3% headroom, and every lane's next mint refused by a control
none of them had touched. The bytes did not come back as notes. `gain` was the largest
class in the spine (48,858 B) and it is not a tenant, because the class guard is keyed to
the `_note` SUFFIX and a field called `gain` is invisible to it. The prose did not stop
being written; it routed around the control. That finding is
`docs/staging/SEAT_FINDING_THE_SPINE_RATCHET_REFILLED_IN_ELEVEN_DAYS_...`, and it names
this migration as the fix and its own hand-rehome of 21 atoms as "a reprieve, not a fix".

THE TWO HALVES, and only both together are a drain rather than another reprieve:
  * STOCK -- this file, once. Every inline `gain` moves to the store, verbatim.
  * FLOW  -- `simplifications_store.NOTE_FIELDS` now contains `gain`, so an inline one is
    refused from now on, and `INLINE_PROSE_BUDGET` catches the next fat field whatever it
    is called (the suffix-blind half; `gain` itself proved a name-keyed guard insufficient).

THE MISFILING IT ALSO CORRECTS. The emergency hand-rehome had no `gain` tenant to write
to, so it put 22 atoms' gain prose under the `origin_note` KEY and left the first sentence
inline. Those atoms are detected here (stored `origin_note` begins with the inline `gain`)
and RENAMED -- the same text under the right key, `origin_note` dropped from both the store
and the declaration. Their inline first sentence is the only text this migration discards,
and only where the store already holds it in full.

REUSE: tools/migrate_atom_notes.py
CLASS: CUSTOM
INDEX: `write_time_gate --explain` and a search for "migrate", "map text edit", "atom
       block" return tools/migrate_atom_notes.py and tools/migrate_simplifications.py.
       The span machinery there is REUSED DIRECTLY rather than copied -- `_atom_blocks`,
       `_field_span`, `_parse_span`, `_indent_of` and `MigrationError` are imported, so
       the quote/indent/folded-scalar scanner that three earlier drains hardened is the
       one that runs here. What could NOT be reused is its driver, for two reasons that
       are defects if ignored rather than preferences: (1) `_rewrite_block` INSERTS a
       `notes_rehomed:` line unconditionally, which on an atom that already has one --
       and 91 do, after H32 -- writes a duplicate YAML key; this driver merges into the
       existing declaration. (2) `migrate()`'s hash proof compares the whole store's note
       tenant against the extracted subtree, which is only true of a virgin store; that
       is what makes it genuinely single-use, and the proof is re-scoped here to the
       fields this run actually moves, read back through the loader's independent path.
       It also runs over BOTH map halves, where the H32 one-shot ran over the live one.

PROOF (three layers, same discipline, a migration that loses prose is the failure mode):
  1. SPAN PROOF: each removed span re-parses standalone to exactly the value the
     whole-file parse gives for that field (inherited -- `_parse_span` raises).
  2. READ-BACK PROOF: after the store write, every moved (atom, field) is re-read through
     `simplifications_store.notes_for_atom` -- an independent path -- and must be
     byte-identical to the text taken out of the map. Scoped to what moved, so it is a
     real proof on a store that already has 300 files rather than a hash that cannot hold.
  3. REMAINDER PROOF: re-parsing the migrated map, every atom's every field other than
     `gain` and the declaration is byte-for-byte what it was. This catches a span that
     ate one line too many.
The store is written BEFORE the map, so a crash between them leaves the prose in both
places (recoverable) rather than in neither.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

from tools import simplifications_store as store
from tools.migrate_atom_notes import (
    KEY_RE,
    MigrationError,
    _atom_blocks,
    _field_span,
    _indent_of,
    _parse_span,
)

PROJECT = Path(__file__).resolve().parent.parent
MAP_PATHS = (
    PROJECT / "docs" / "design" / "maturity_map.yaml",
    PROJECT / "docs" / "design" / "maturity_map_closed.yaml",
)
STORE_DIR = PROJECT / "docs" / "design" / "simplifications"

FIELD = "gain"
DECL = store.NOTES_DECLARATION_FIELD

#: The key the emergency hand-rehome misfiled gain prose under (see module docstring).
MISFILED_UNDER = "origin_note"


def _normalised(text: str) -> str:
    """Whitespace-normalised, for comparing a folded map scalar with a stored one."""
    return " ".join(text.split())


def misfiled_as_origin_note(atom_id: str, inline_gain: str, store_dir: Path) -> str | None:
    """The stored `origin_note` text when it is really this atom's gain, else None.

    The test is that the stored note BEGINS with the inline gain: the hand-rehome kept the
    first sentence in the map and moved the whole thing, so a prefix match is evidence of
    that operation and a genuine `origin_note` about provenance will not match by accident.
    """
    stored = store.notes_for_atom(atom_id, store_dir).get(MISFILED_UNDER)
    if not isinstance(stored, str):
        return None
    return stored if _normalised(stored).startswith(_normalised(inline_gain)) else None


def _declaration_span(block: list[str]) -> tuple[int, int] | None:
    """(start, end) of the atom's existing `notes_rehomed:` field, or None."""
    for j, line in enumerate(block):
        m = KEY_RE.match(line)
        if m and m.group(2) == DECL:
            return j, _field_span(block, j)
    return None


def _rewrite_block(block: list[str], atom_id: str, store_dir: Path) -> tuple[list[str], dict]:
    """Strip the inline `gain` from one atom block and reconcile its declaration.

    Returns (new_block, {"gain": <text to store>, "drop": [<fields to drop>]}) or
    (block, {}) when the atom has no inline gain.
    """
    gain_at = None
    for j, line in enumerate(block):
        m = KEY_RE.match(line)
        if m and m.group(2) == FIELD:
            gain_at = j
            break
    if gain_at is None:
        return list(block), {}

    gain_end = _field_span(block, gain_at)
    field, value = _parse_span(block, gain_at, gain_end)
    if field != FIELD:
        raise MigrationError(f"{atom_id}: span key mismatch {field!r} != {FIELD!r}")
    if not isinstance(value, str) or not value.strip():
        raise MigrationError(
            f"{atom_id}: `gain` is {type(value).__name__}, not non-empty prose "
            "-- refusing to rehome a shape the store cannot represent"
        )

    decl_span = _declaration_span(block)
    if decl_span is not None:
        _, parsed = _parse_span(block, decl_span[0], decl_span[1])
        if not isinstance(parsed, list):
            raise MigrationError(f"{atom_id}: {DECL} is not a list ({parsed!r})")

    stored = store.notes_for_atom(atom_id, store_dir)

    # WHICH TEXT WINS, and this is the half a re-run gets wrong if it is not written down.
    # The store is checked FIRST because a previous partial run may already hold the full
    # prose here, in which case the inline value is the first sentence of it and writing
    # that back would be a silent truncation -- prose loss dressed as idempotence. The
    # rename case is the same shape one key over: the hand-rehome left the full text under
    # `origin_note` and the first sentence inline.
    already = stored.get(FIELD)
    misfiled = misfiled_as_origin_note(atom_id, value, store_dir)
    if isinstance(already, str) and _normalised(already).startswith(_normalised(value)):
        to_store, drop = already, []
    elif misfiled is not None:
        to_store, drop = misfiled, [MISFILED_UNDER]
    else:
        to_store, drop = value, []

    # THE STORE GETS A VETO, and the atom keeps its inline gain when it uses it. One atom
    # (`OPS2_publish_gate_head_worktree`) is already past the note-tenant bound, and the
    # bound is right to refuse it: compacting another lane's 56 KB `build_note` to green a
    # control is the laundering this store exists to refuse. Refusing the MOVE as well
    # would leave the prose nowhere, so the map keeps it and `check_no_inline_notes` reads
    # the same refusal and permits exactly that atom -- an exception that clears itself
    # when the tenant is compacted, rather than a name on a list.
    refusal = store.note_write_refusal(atom_id, FIELD, to_store, store_dir)
    if refusal is not None:
        return list(block), {"refused": refusal}

    # DECLARED FROM THE STORE, never from the map's own previous declaration: the
    # declaration is a claim ABOUT the store, so deriving it from the store is what makes
    # this idempotent and self-healing after a part-applied run (the map can name an
    # `origin_note` a completed rename has already removed). It is also exactly the
    # comparison `check_declarations_match` makes, so the two cannot drift.
    new_declared = sorted((set(stored) | {FIELD}) - set(drop))
    indent = " " * _indent_of(block[gain_at])
    decl_line = f"{indent}{DECL}: [{', '.join(new_declared)}]\n"

    cut = set(range(gain_at, gain_end))
    if decl_span is not None:
        cut |= set(range(decl_span[0], decl_span[1]))
    anchor = min(gain_at, decl_span[0] if decl_span else gain_at)

    out: list[str] = []
    for i, line in enumerate(block):
        if i == anchor:
            out.append(decl_line)
        if i not in cut:
            out.append(line)
    return out, {FIELD: to_store, "drop": drop}


def rewrite_map_text(text: str, store_dir: Path = STORE_DIR) -> tuple[str, dict[str, dict]]:
    """(migrated map text, {atom_id: {"gain": text, "drop": [...]}}). Pure but for the
    store READ that detects the misfiling, so tests can drive it on synthetic maps."""
    lines = text.splitlines(keepends=True)
    extracted: dict[str, dict] = {}
    blocks = _atom_blocks(lines)
    if not blocks:
        return text, {}
    out: list[str] = list(lines[: blocks[0][1]])
    for atom_id, start, end in blocks:
        new_block, moved = _rewrite_block(lines[start:end], atom_id, store_dir)
        if moved:
            extracted[atom_id] = moved
        out.extend(new_block)
    return "".join(out), extracted


def _remainder(atoms: list) -> dict:
    """Every atom's every field other than `gain` and the declaration. PROOF LAYER 3."""
    return {
        str(a["id"]): {k: v for k, v in a.items() if k not in (FIELD, DECL)}
        for a in atoms
        if isinstance(a, dict) and a.get("id")
    }


def migrate(
    map_paths=MAP_PATHS, store_dir: Path = STORE_DIR, apply: bool = True
) -> dict:
    plans = []
    refused: dict[str, str] = {}
    for map_path in map_paths:
        original = map_path.read_text(encoding="utf-8")
        before = yaml.safe_load(original)
        new_text, found = rewrite_map_text(original, store_dir)
        extracted = {k: v for k, v in found.items() if "refused" not in v}
        refused.update({k: v["refused"] for k, v in found.items() if "refused" in v})

        after = yaml.safe_load(new_text)
        still = [
            a.get("id")
            for a in after
            if isinstance(a, dict) and FIELD in a and a.get("id") not in refused
        ]
        if still:
            raise MigrationError(f"{map_path.name}: still carries inline gain: {still[:5]}")

        before_rem, after_rem = _remainder(before), _remainder(after)
        for aid, fields in before_rem.items():
            if after_rem.get(aid) != fields:
                got = after_rem.get(aid, {})
                diff = [k for k in set(fields) | set(got) if fields.get(k) != got.get(k)]
                raise MigrationError(f"{map_path.name}/{aid}: other fields changed: {diff}")

        # The declaration must name exactly what the store will hold, or the contract
        # test that reads it both ways is the thing that finds out.
        for aid, moved in extracted.items():
            declared = next(
                (a.get(DECL) for a in after if isinstance(a, dict) and a.get("id") == aid),
                None,
            )
            expected = sorted(
                (set(store.notes_for_atom(aid, store_dir)) | {FIELD}) - set(moved["drop"])
            )
            if sorted(declared or []) != expected:
                raise MigrationError(
                    f"{aid}: declaration {declared!r} != store-after {expected}"
                )

        plans.append((map_path, original, new_text, extracted))

    result = {
        "refused_by_the_store": refused,
        "atoms_moved": sum(len(p[3]) for p in plans),
        "renamed_from_origin_note": sum(
            1 for p in plans for m in p[3].values() if m["drop"]
        ),
        "chars_moved": sum(len(m[FIELD]) for p in plans for m in p[3].values()),
        "maps": {
            p[0].name: {
                "bytes_before": len(p[1].encode("utf-8")),
                "bytes_after": len(p[2].encode("utf-8")),
            }
            for p in plans
        },
        "applied": False,
    }
    if not apply:
        return result

    # COMMIT: store first, then the maps.
    for _, _, _, extracted in plans:
        for aid, moved in extracted.items():
            store.set_note_for_atom(aid, FIELD, moved[FIELD], store_dir)
            for dead in moved["drop"]:
                store.remove_note_for_atom(aid, dead, store_dir)

    for _, _, _, extracted in plans:
        for aid, moved in extracted.items():
            back = store.notes_for_atom(aid, store_dir)
            if back.get(FIELD) != moved[FIELD]:
                raise MigrationError(
                    f"{aid}: read-back mismatch -- maps NOT rewritten, prose still inline"
                )
            for dead in moved["drop"]:
                if dead in back:
                    raise MigrationError(f"{aid}: {dead!r} survived the rename")

    for map_path, _, new_text, _ in plans:
        map_path.write_text(new_text, encoding="utf-8")
    result["applied"] = True
    return result


def main(argv: list[str]) -> int:
    print(json.dumps(migrate(apply="--check" not in argv), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
