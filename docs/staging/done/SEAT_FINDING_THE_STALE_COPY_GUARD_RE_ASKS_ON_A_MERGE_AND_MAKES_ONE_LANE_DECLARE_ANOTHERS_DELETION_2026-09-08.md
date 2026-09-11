**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — found while landing

# FINDING — the stale-copy guard re-asks on a merge, and the only way through is for one lane to declare another lane's deletion as its own

**Found 2026-09-08** while promoting `per-page-pointer-rungs-for-the-thirteen-untied-producer-literals`
from an isolated worktree. Reproduced, not inferred: it cost two cycles and the receipt is in
`22df46614`.

## What happened

`promote_worktree_landing` refused twice because origin/main moved under the landing. The second
mover was `d3e0e408b`, another lane's own work on `tools/surgical_land.py` and its tests, which
**deliberately deleted `_staged`** from `tests/background/test_the_publish_commit_carries_only_its
_own_work.py` and **declared that deletion with `--drops` in its own landing**, exactly as designed.

Re-gating on the new base with `surgical_land --merge origin/main` was then refused:

```
[stale-copy] ❌ COMMIT REFUSED -- 1 path(s) would revert work that has already landed.
A pathspec stages the WORKING-TREE copy. If you opened one of these files before another
lane landed in it, your copy is the OLD one and this commit deletes their work.
  tests/background/test_the_publish_commit_carries_only_its_own_work.py  [strict_symbol_subset]
      would DELETE 1 name(s) HEAD has, and adds none:  - _staged
```

Every sentence of that refusal is false of the landing it refused. **No working-tree copy was read**
— `--merge` computes the tree by plumbing precisely so the shared index is never opened. **This lane
never opened that file.** And the deletion had already landed on origin, already been declared, and
already been attributed to the landing that chose it.

## Why the guard cannot tell

`tools/stale_copy_refusal.violations(root, parent, result, paths, allow)` takes **`parent` and
`result` and nothing else**. It has no channel for the merge ref, so on a `--merge` it cannot
distinguish *"the other parent's landed, declared deletion"* from *"this lane's stale working copy"*.
`surgical_land._land_once` calls it on the same line for both landing kinds.

**The cost is not the refusal — it is fail-closed and that is the right direction. The cost is the
attribution.** The only route through is `--drops`, whose own comment says it "makes a deliberate
deletion attributable to the landing that chose it". Used here it does the opposite: `22df46614` now
carries a declared drop that belongs to `d3e0e408b`. The guard's own attribution mechanism is
defeated by the guard's own refusal, and any census of who deleted what will read this lane as the
deleter.

## The remedy, and the obvious version of it is WRONG

The tempting predicate is *"exempt a path whose result blob equals the merged ref's blob"*. **Do not
ship that.** It reopens a failure this repository has already paid for: a merge that adopts one
side's rewrite silently deletes the other side's purely additive work. If `parent` carries names the
ref does not, `result == ref` is exactly the shape of that deletion, and the guard would be
exempting the case it exists for.

The safe predicate is narrower and it is about **this side's history, not the other's**: a path is
not this lane's loss when it is **unchanged between `merge-base(parent, ref)` and `parent`** — this
side never touched it — and the ref changed it. Adopting the other side's evolution of a file you
never edited cannot delete anything of yours. Anything this side DID touch stays refused, which is
the whole population the guard was built for.

That is one predicate and one extra argument threaded from `_land_once`, and it needs its own R15
pair: a merge over a path this side never touched must land, and a merge over a path this side
edited must still refuse.

## Why it was not fixed in this turn, stated rather than left implicit

`tools/surgical_land.py` was rewritten by another lane **twenty minutes before this was found** —
`d3e0e408b` is the commit that caused the collision — so it is the likeliest file in the tree to be
held dirty by a live writer, and landing into a file another lane holds dirty wedges the shared
tree's fast-forward for everyone. This is the landing door for every lane; it is worth one clean
turn rather than a hurried one on a contested file.

## What is next

* Thread the merge ref into `stale_copy_refusal.violations` and add the merge-base predicate above,
  with both legs of the partition driven.
* **Census `--drops` declarations against the commit that actually chose each deletion.** If this
  has happened before, the record already contains lanes credited with deletions they merely merged,
  and nothing would have said so.
