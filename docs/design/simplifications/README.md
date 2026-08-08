# The simplifications store

This directory is the extracted home of the per-atom **simplifications
register** — the append-only honesty log that records, for each maturity-map
atom, what that atom deliberately simplifies, why, and (where known) how wrong
the simplification is.

It was moved out of `docs/design/maturity_map.yaml` on 2026-08-05 (retro FM-1 /
taxonomy review F1). The register was ~89% of the map's bytes and grows without
bound; the map is the governance spine and must stay phone-readable. This was a
**MOVE, verbatim** — no note was reworded or restructured. In the map, each
atom's `simplifications` field is now a single `simplifications_count: <N>`
scalar (present only where N > 0).

## Birth certificate

**Reader.** The resident worker (map maintenance) and advisor audits. Consumers
read through `tools/simplifications_store.py`:

- `for_atom(atom_id)` → the atom's list of note strings, **exactly** what
  `atom["simplifications"]` used to yield (or `[]` if the atom has no file).
- `load_all()` → `{atom_id: [note, ...]}` across the whole store.
- `count_for_atom(atom_id)` → the note count (0 if none).

**Writer.** The resident worker, via map maintenance. The only supported write
path is `tools/simplifications_store.append_for_atom(atom_id, notes)`, driven by
`tools/merge_atom_status.py` when a build fork's write-inbox carries an
`append_simplification`. It is **append-only** (existing notes are never
rewritten — the register is honest history) and it keeps the map's
`simplifications_count` in sync. `tools/migrate_simplifications.py` was the
one-shot that populated this store; it is SINGLE-USE, not a maintenance tool.

**Bound.** One file per existing atom (`<atom_id>.yaml`), each **≤ 100 KB**.
A file's content is that atom's subtree:

```yaml
atom_id: <id>
simplifications:
- <note, verbatim>
- <note, verbatim>
```

The store location (`docs/design/simplifications/`) is **by convention**,
documented here; it sits beside the map so a tool operating on a map copy finds
the store beside that copy.

**Death.** A file is deleted when its atom is deleted or merged away. The orphan
check in `tests/design/test_simplifications_store.py` enforces the invariant
that **every store file maps to an atom id that still exists in the map** — a
store file with no atom is a defect that fails the suite.

## Invariants (enforced by the store test)

1. Every `<id>.yaml` maps to an existing atom id in the map (no orphans).
2. Each atom's map `simplifications_count` equals its store file's note count.
3. Every store file is ≤ 100 KB.
4. Once the store is populated, the map carries **no** `simplifications` field
   and the map file is **< 400 KB** (the spine's size ratchet).
