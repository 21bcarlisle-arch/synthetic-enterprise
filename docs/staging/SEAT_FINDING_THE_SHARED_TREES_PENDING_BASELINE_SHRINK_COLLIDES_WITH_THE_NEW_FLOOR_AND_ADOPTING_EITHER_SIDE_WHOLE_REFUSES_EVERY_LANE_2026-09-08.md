**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (follow-on to Lane 0 `prune-comment-only-path-edges-and-freeze-the-33-in-one-commit`)

# The shared tree's pending baseline shrink collides with the new floor, and adopting either side whole refuses every lane

Found after landing `2e4fa042a`, while checking whether the shared tree could import it. Recorded
rather than acted on: the contested edit is another lane's uncommitted work and is not mine to move.

## The two facts

1. **`2e4fa042a` rewrote `docs/design/orphan_baseline.json`**, 374 rows → 408, because a path in a
   comment stopped being a reachability edge.
2. **`/home/rich/synthetic-enterprise` holds that same file DIRTY**, uncommitted, with a one-row
   *shrink*: `simulation.household_physical_layer` removed, `module_count` 1123 → 1122.

So the shared tree cannot fast-forward to `origin/main` while that edit stands. My commit is on
origin and **not yet imported** — pushed is not imported, and the daemons running from that tree are
still on the old edge model.

## The pending shrink is wrong on its own terms, independently of my commit

Measured in the shared tree itself, not in mine:

```
orphan in SHARED tree: True | total orphans 365
```

`simulation.household_physical_layer` is an orphan **in the very tree holding the edit that
un-freezes it**. Its only importer is `tests/simulation/test_household_physical_layer.py`, and a test
is evidence, not a caller. It is also an orphan under both edge models in my tree — the pruning
neither caused this nor fixes it.

Landing that shrink as it stands makes the module a *new* orphan and refuses every lane under
*"THIS COMMIT ADDS WORK THAT NOTHING RUNS"*. **The machinery built for exactly this is working**:
because the module is frozen at HEAD, `attribute_added` classifies it as `unfrozen` and the shared
tree's refusal already reads *"AN UNCOMMITTED EDIT TO THE BASELINE IS WHY THIS REFUSES — NOT YOUR
COMMIT."* That is the correct attribution and it is why this is a RECORDED note and not an incident.

## The merge hazard, which is the part worth writing down

When that lane resolves, `orphan_baseline.json` will have moved on both sides, and **the two sides
are not symmetric**:

- **Adopting the shared tree's side whole deletes 34 freeze rows** and re-creates the defect
  `2e4fa042a` exists to remove — an editorial reword of a comment refusing every lane, naming a
  module the refused lane never touched.
- **Adopting origin's side whole** silently keeps `household_physical_layer` frozen. That is the
  *safe* direction, and it is also the correct one: the module genuinely is an orphan, so the row
  belongs in the floor.

**The resolution is neither side's file. It is `python3 -m tools.orphan_ratchet` re-frozen from a
tree that has both changes** — the floor is derived, so a re-freeze on the merged tree is the only
resolution that is not a paste from somewhere else. This is the failure `baseline_tree_note` was
built to detect, and the `module_count` field is the tell: 1122 on the dirty copy against 1123 at
HEAD and 1124 on origin means three different trees have written this file.

## What I did not do, and why

I did not touch the dirty copy. `git checkout`/`git stash` on another lane's uncommitted work is out,
and a shrink is that lane's judgement to land or drop. The one thing that would be wrong is resolving
the future conflict by picking a side, so this note exists to make sure whoever meets it re-freezes
instead.
