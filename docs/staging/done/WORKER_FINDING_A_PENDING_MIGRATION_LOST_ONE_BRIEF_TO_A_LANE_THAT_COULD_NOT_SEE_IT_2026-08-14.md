# [WORKER-FINDING] A pending migration was lossless for 295 atoms and lost the 296th to a lane that could not see it (2026-08-14)

**Severity:** LATENT · **Lane:** H_harness · **Status:** repaired and landed this tick (commit cited
below, verified at `HEAD` not claimed); the general class is stated and left open.

Found while landing the H27 Hour #29 residue, not looked for. The map was going to be edited for the
D37..D45 mint; reading its state first is what produced this.

## What is on disk, `observed-with-evidence`

`docs/design/maturity_map.yaml` carries a complete, uncommitted run of
`tools/migrate_atom_names.py` — the fourth rehoming of the same shape (FM-1 `simplifications`, H32
`map_notes`, H41 `map_records`). Every atom's `name` has left the spine:

    $ git show HEAD:docs/design/maturity_map.yaml | grep -c '^  name:'   ->  296
    $ grep -c '^  name:' docs/design/maturity_map.yaml                   ->    0
    $ grep -c 'notes_rehomed' docs/design/maturity_map.yaml              ->  296

That migration is legitimate and its arithmetic is in its own docstring (`name` was 37% of the spine,
mean 91 B in the oldest 50 atoms and 1,253 B in the middle 50 — accretion wearing an identity
field's name). This finding is not about whether it should land.

## The measurement, and the false start that preceded it

A first pass compared each HEAD `name` against the raw text of its store file and reported **87
unrecoverable**. That number was wrong and never left this tick: the store writes YAML single-quoted
scalars, so `SYSTEM's` is stored `SYSTEM''s` and a substring test fails on the escaping, not on the
content. Parsing the YAML instead of grepping it:

| | |
|---|---|
| HEAD atoms carrying a `name` | 296 |
| exact match at `map_notes.name` in the store | **295** |
| lost | **1** — `EP13_adapter_carbon_intensity` |

The lesson is the finding's own: a census that reads a serialised file as text measures the
serialiser. 87 of 296 would have been a headline; it was quoting.

## Why exactly one, and why that one

`EP13_adapter_carbon_intensity` is the atom the two most recent commits worked (`2c7aea47e`,
`071a60ec7` — EP13/EP14 DISCOVER). The migration ran at 03:37 and wrote the brief into the store;
the EP13 lane rewrote that store file at 04:29 through `simplifications_store`, from a HEAD where the
brief still lived in the map, and its write did not carry a field it had no reason to know existed.
Its map block still reads `notes_rehomed: [name, origin_note]`, so the map defers to a store entry
that by then held only `origin_note`.

**The class:** an uncommitted migration is invisible to every concurrent lane, and a store the
migration has filled but the tree has not recorded can be *silently un-filled* by any lane that
writes the same tenant. The window is exactly "migration applied, not committed" — the same window
that produced the last two findings on this tree
(`..._A_CUT_RECORDED_AS_EXECUTED_HAD_NEVER_BEEN_COMMITTED_2026-08-13`,
`..._A_CONTROL_ARRIVED_WITH_A_REPO_WIDE_REFUSAL_AND_NO_TEST_2026-08-14`). Three findings, one cause:
work that is finished on disk and absent from `HEAD`.

## THE SECOND LOSS, and it was 63KB, not one brief

The census above asked "is every `name` readable at its new address". Asking the wider question —
**does any key present in a store file at `HEAD` fail to survive the rewrite** — found a second class
the first question could not see:

| atom | key dropped | size |
|---|---|---|
| `OPS2_publish_gate_head_worktree` | `build_note` | 56,846 chars |
| `G12_queryable_projections` | `build_note` | 6,474 chars |

Both were **top-level** keys in the store file. The store's writer (`_write_tenants`) serialises the
tenants it knows — `simplifications`, `map_notes`, `map_records` — so a key sitting outside them is
not migrated, it is *not written back*. And neither atom's map block declared `notes_rehomed` at
`HEAD`, so those 63KB were **already orphaned before this migration touched them**: written to the
store by an earlier writer shape, reachable by no declaration, and therefore invisible to every
check that walks the map's declarations. The migration did not create that orphan; it was the thing
that would have deleted it.

Repaired forward rather than back: both restored through `set_note_for_atom` to
`map_notes.build_note` — the address the current reader uses — and `build_note` added to each atom's
`notes_rehomed` in the map, so they are now DECLARED, which they never were at `HEAD`.

**The general shape, and it is the one worth keeping:** a store rewrite is lossless only for the
tenants the writer enumerates, so the dangerous record is the one no declaration points at. A
losslessness check written as "every declared field is readable" would have passed this migration
while it deleted 63KB, because the deleted fields were exactly the undeclared ones. The check has to
run in the other direction — *every key present before is present after* — which is the direction
this tick had to be pushed into by measuring twice.

## What was repaired

`EP13_adapter_carbon_intensity`'s brief restored to `map_notes.name` through the store's own writer
(`set_note_for_atom`, not a hand edit, so the file's shape is the writer's). Re-run of the census
over all 296: **296 recovered, 0 lost**. Plus the two `build_note`s of the section above, and one
`simplifications_count` the EP13 lane left unwritten while its store file carried 1 (`EP14`'s block
has the same line; `EP13`'s did not), which was reddening `test_counts_match_file_contents`.

The title of this document undersells it: the one lost brief is what the first census found, and the
63KB is what the second one found. Both are the same window.

## The migration itself is landed here, because HEAD was RED without it

    tests/design/test_simplifications_store.py::test_map_within_size_ratchet_when_store_populated
    -> maturity_map.yaml is 410095 bytes, over the 409600-byte spine ratchet

That is `HEAD`, measured this tick: any commit whose paths select the store tests is refused until
the migration lands. The tree map is 262,093 B. So "leave another lane's applied work alone" was not
available — the choice was to land it repaired or leave the repo wedged on a red ratchet with 63KB
of records queued for deletion behind it. Landed with all three repairs, 101 green across
test_atom_notes_store / test_simplifications_store / test_atom_records_store /
test_maturity_map_contract / test_maturity_map_facets, and no `level_current` line anywhere in the
map diff.

Three other diffs in the store were checked and are **revisions by live lanes, not losses**: `D31`
gained a simplifications entry (1 -> 2, and the map count already says 2), `D36`'s evidence swapped a
RESIDUAL line for its RESOLVED successor, `D6`'s `build_note` grew by 2 characters.

## What is NOT taken, and is the reason this is filed rather than closed

The migration still has no losslessness control. Its `--check` mode proves what it is *about to*
write; nothing proves, at the moment it *lands*, that every rehomed field is readable at its new
address. That control is one census — `for every atom carrying notes_rehomed: [f], map_notes[f]
exists` — and it belongs at commit time, and it has to be written in the
present-before-implies-present-after direction for the reason the 63KB case shows. Filed, not built:
it is a gate change, and this tick's draw was the H27 residue.
