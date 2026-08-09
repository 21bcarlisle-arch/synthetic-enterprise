# WORKER FINDING — the map's own size ratchet is red on committed HEAD, and it penalises honest recording

**Found:** 2026-08-09, during the D16 build (incidental — not that atom's scope).
**Disposition:** QUEUED as `H32_map_size_ratchet_red_on_head`. Not fixed on sight; not blocking.
**Rank:** backlog unless someone is wedged by it.

## Observed, with evidence

`tests/design/test_simplifications_store.py::test_map_within_size_ratchet_when_store_populated`
asserts `docs/design/maturity_map.yaml < 409600` bytes. It fails:

```
$ git show HEAD:docs/design/maturity_map.yaml | wc -c
464110            # already 54,510 bytes over the ceiling, before this tick touched anything
$ wc -c < docs/design/maturity_map.yaml
474656            # after D16's build note, D17 and H32 (+10,546)
```

**The overage is on committed HEAD**, not on working-tree dirt. That distinction is written down
because the *known* wedge class here is the opposite one — "the gate lints the working tree, so one
uncommitted change wedges publishing for everyone" — and reaching for the usual remedy would have
found nothing. Same shape as `WORKER_FINDING_RUFF_RATCHET_RED_ON_COMMITTED_HEAD_2026-08-09`, two
different ratchets, one week apart.

**Not currently blocking:** the pre-commit gate (`tools/git-hooks/pre-commit`) does not run
`tests/design/`, so this is a red test rather than a wedged publish.

## Why it is worth an atom rather than a shrug

The ratchet's own failure message says "the register must live in the store, not the map" — a rule
written when the oversized thing was the `simplifications:` field, which *was* rehomed. What is
oversized now is the long-form `build_note` / `harden_note` / `level_hold_note` fields, and those
are the map's **record**: the reason a level moved, the reason a hold was held, the measurement that
refuted a prior claim. Every atom that records its work honestly makes this control redder.

A control that gets angrier the more faithfully the record is kept will eventually be paid with the
record. That is the failure mode to avoid, and it is why this is queued rather than settled by
trimming the note that tripped it.

## The two candidate answers, and what would decide between them

1. **The ceiling is wrong for a map this size.** 241 atoms, each carrying its own evidence trail.
   Raise it *with a stated reason and a new ratchet that can still fire* — a ceiling nobody can hit
   is not a control.
2. **The long-note fields belong in the store**, beside `simplifications`, loaded back by id. This
   is the H27 precedent (the class register was **rehomed**, not trimmed) and keeps a real ratchet
   on the spine.

What it may **not** be closed by: trimming build notes to fit. That pays a size warning with the
record, which is the thing the size warning exists to protect.

---

## CLOSED 2026-08-09 — H32 built candidate 2, ratchet restored to 400K

Both candidates this finding named have now been taken, in order:

* **Candidate 1** (2026-08-09, same day): ceiling raised 400K → 640K as a stated INTERIM to unwedge
  the publish queue, with the reason recorded in the test and a standing bar on any second raise
  before candidate 2 was done.
* **Candidate 2** (this closure): the narrative note CLASS — `build_note`, `discover_note`,
  `harden_note`, `level_hold_note`, `level_note`, `notes`, `origin_note`, plus anything `*_note` by
  suffix — was rehomed verbatim into the existing sibling store's new `map_notes:` tenant.
  **84 fields over 61 atoms, 129,750 bytes.** Map 521,770 → 393,884 bytes, so the ceiling went back
  to its **original 400K** rather than staying at the interim. The amnesty was repaid, not extended.

It was **not** closed by trimming build notes, which this finding explicitly forbade: nothing was
reworded or dropped, and the move is hash-proven identical
(`tools/migrate_atom_notes.py` — per-span re-parse, canonical-JSON SHA-256 of the whole note subtree
matched against an independent recombination through the loader, and a remainder proof that every
non-note field of every atom is byte-identical).

Artefacts: `tools/migrate_atom_notes.py` (single-use), `tools/simplifications_store.py` (note tenant),
`tests/design/test_atom_notes_store.py` (13 R15 mutation tests; the class guard fires on an invented
`frame_note`), `docs/design/simplifications/README.md` (second-tenant birth certificate).
`tests/design/` 69 passed. Ledger: `LEVEL_UP_SELF_CERTIFIED H32_map_size_ratchet_red_on_head → L2`.

Follow-on queued, not fixed on sight:
`WORKER_FINDING_KNIFE_MUTATION_FIXTURE_PINS_A_GENERATED_VALUE_2026-08-09.md`.
