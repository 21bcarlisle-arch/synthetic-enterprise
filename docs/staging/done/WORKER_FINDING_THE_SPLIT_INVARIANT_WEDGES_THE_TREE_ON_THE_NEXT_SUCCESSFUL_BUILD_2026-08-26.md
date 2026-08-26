# The map split's own invariant wedges every lane the moment any atom reaches its target

**Severity:** BLOCKING · **Lane:** H_harness

**Discharged:** `tests/tools/test_maturity_map_store.py::test_refile_moves_BOTH_directions_in_one_call`,
`tests/tools/test_maturity_map_store.py::test_MUTATION_a_refiler_that_moved_NOTHING_fails_this_null_control`,
`tests/tools/test_maturity_map_store.py::test_MUTATION_a_HALF_LANDED_refile_rolls_the_live_half_back`,
`tests/tools/test_maturity_map_store.py::test_refile_satisfies_the_invariant_it_exists_to_satisfy`,
`tests/tools/test_maturity_map_store.py::test_the_split_predicate_agrees_with_where_every_atom_actually_SITS`,
`tools/maturity_map_store.py`, `tools/merge_atom_status.py`

— 2026-08-26 worker tick, read from HEAD and not from the working tree, which is the only
reading that could have told the two apart. Every one of the three repairs this finding asked
for is in the tree. The re-filer exists and moves both directions in one call, so the release
the invariant lacked is now mechanical rather than a hand edit. The fold that raises a level
calls it, so a level move and the move between halves land as one act. The null control fails a
re-filer that moved nothing, and the half-landed mutation rolls the live half back, which is the
hazard this finding named against its own fix. All four map-split files are tracked and clean at
HEAD; the two test files run 54 passed.

Rank: top of H_harness, ahead of the general disposition queue. It arms on the next successful
BUILD, and the BUILD currently drawn is one of the atoms that arms it.

## The mechanism — observed-with-evidence

`tests/tools/test_maturity_map_store.py::test_the_split_predicate_agrees_with_where_every_atom_actually_SITS`
(lines 149-164) asserts, against the LIVE tree:

```
misfiled_live = [a["id"] for a in map_store.load_live_atoms() if map_store.is_closed(a)]
assert not misfiled_live
```

`is_closed(atom)` is `level_current >= level_target`. So an atom in `maturity_map.yaml` that has
reached its own target is a RED — and it reds a test file that sits on the tree-wide selection,
so it refuses **every commit in every lane**, not just the one that raised the level.

Reaching target is not an edge case. It is the success path of the entire machine.

## It arms on the drawn work, not on some future atom

This tick's LANE 1 BUILD draw:

| field | value |
|---|---|
| `id` | `EP13_adapter_carbon_intensity` |
| `level_current` | 2 |
| `level_target` | 3 |
| `loop_stage` | build |

Read from `map_store.load_atoms()` on the live tree. The atom's whole deliverable is level 2 -> 3.
On success `level_current` becomes 3, `is_closed` becomes true, the record is still in the drawn
half, and the tree wedges. **Building the drawn atom correctly is what breaks the tree** — the
"exit criterion greened by the move it forbids" shape, inverted.

## Why nothing absorbs it today

`tools/maturity_map_store.py` exposes `load_atoms`, `load_live_atoms`, `load_closed_atoms`,
`map_text`, `is_closed`, `closed_path_for`. There is **no re-filing function** — nothing in the
tree can move an atom's record from one half to the other. `grep -n "def "` over the store is the
whole surface; the move is a hand edit or it does not happen.

`tools/merge_atom_status.py` is the one writer that folds a fork's level move into the map. It
takes `map_path: Path = MATURITY_MAP_YAML` — the **drawn half only** (line 535) — reads its text,
edits the atom block in place and writes the same file back (lines 559, 588). It has no concept of
a sibling file, so it cannot re-file, and it will happily raise a level into the state the
invariant forbids.

So the release of this hold is undefined: R11's *no orphan transitions* clause, on the invariant
rather than on a flag.

## What is NOT the fix

Loosening the assertion. The predicate is load-bearing — `MAP_SPLIT_2026-08-26.md` argues it is
the same predicate the BUILD draw already used (`if not has_gap: return False`), which is why the
split provably could not change what the machine can work on. A lenient invariant would let an
atom below target sit in the closed half, where the draw never looks, and the atom would go dark.
That is the failure the split was designed to make impossible.

## Recommendation — and I am taking it unless told otherwise

Give the invariant a release, so satisfying it is mechanical rather than a hand edit:

1. `maturity_map_store.refile(...)` — move any atom whose half disagrees with `is_closed` into the
   correct half, as one two-file write, returning what moved. Both directions: an atom whose
   target is later RAISED must come back to the drawn half or it goes dark.
2. Call it from `merge_atom_status.merge()` after the field fold, so a fork's own level move
   re-files itself in the commit that raised it, and `MAP_PARTS_REL` (not `MAP_REL`) is what the
   fold stages — `background/process_run_complete.py` already names both halves in its pre-gate
   add, and the fold must match it.
3. Mutation-test the re-filer against both directions plus a null control, per R15: a re-filer
   that moved nothing would pass a one-directional test silently.

**Note the hazard this repeats.** The re-filer is itself a two-file atomic write, which is the
exact shape that produced the wedge this finding sits behind. Its own tests must red if half of it
lands — otherwise the fix is the next incident.
