**Severity:** LATENT — the defect is fixed and landed with this finding; the shared tree is still
22 behind at filing, held by one genuinely dirty path that belongs to another lane and has a named
remedy · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — RUNG 1 shared-tree advance ·
**Class:** publish_gate_and_wedge

# The twin sweep was defeated by `git add`, and nine identical files waited behind four

Filed 2026-09-05 by the autonomous worker. The tick drew *"continue the self-clearing-alarm census
loader sweep — 26 benign rows still carry no `loader` field"*. **That work is finished.** It landed
on origin in `c30738d77` and every one of the 46 disposition rows carries a `loader` field there,
including all seven carriers the draw named as the ranked head. The draw was computed from a local
tree **22 commits behind origin**, and the 26 unswept rows it reports are what that stale tree
holds. Re-deriving the queue is not the finding; **why the tree was stale** is.

## 1. What was actually holding the shared tree

`origin_reconcile.advance_shared_tree` exists to clear this exact wedge, and it has been reporting
`NOT_ADVANCED` every cadence. Measured on the live tree:

```
blocking: 14   untracked twins: 9   tracked: 5
```

Fourteen paths refused `merge --ff-only`. Nine were untracked, and `identical_untracked_twins`
matched all nine — files whose bytes origin already holds at the same path, which the module's own
docstring describes as *"protecting a file from being replaced by itself"*. The advance still
cleared none of them, correctly, because the all-or-nothing property refuses unless clearing the
twins would leave the fast-forward nothing else to refuse on, and five `FF_MODIFIED` paths stood.

**Four of those five hashed EQUAL to origin's blob at the same path.**

| path | index | worktree vs origin |
|---|---|---|
| `background/origin_reconcile.py` | at HEAD | **identical** — origin's own copy of the module, on disk, unstaged |
| `tests/…/test_a_refused_advance_names_the_paths_that_refused_it.py` | staged ADD | **identical** |
| `tests/…/test_a_staged_document_no_longer_blocks_every_landing.py` | staged M | **identical** |
| `tests/…/test_the_advance_refused_on_files_it_was_about_to_write_back_unchanged.py` | staged ADD | **identical** |
| `background/process_run_complete.py` | at HEAD | **differs** — 58 lines origin has never seen |

Thirteen of the fourteen blockers were files about to be replaced by themselves. The sweep built
for exactly that sentence saw nine of them.

## 2. THE DEFECT: the sweep was scoped to a KIND, and the property is about CONTENT — FIXED

`identical_untracked_twins` skips every entry whose kind is not `FF_UNTRACKED`. So a byte-identical
file that somebody had run `git add` over reclassifies to `FF_MODIFIED` and leaves the sweep's
subject — **identical bytes, opposite outcome, decided by an act that changes no content.** Two
of the four were staging notes another lane staged instead of leaving untracked; a third was a test
file; the fourth was the reconciler's own source.

And the sentence that stopped anyone looking was in `paths_blocking_fast_forward`'s docstring, which
said of `FF_MODIFIED` that *"it belongs to whichever lane is holding it"* — true of the kind, false
of four instances out of five, and stated with no hedge. `test_a_modified_path_beside_a_twin_
removes_nothing` restated it as *"cannot be hashed away"*. Both are **corrected in place, beside the
claim**, rather than quietly rewritten.

The repair: `identical_tracked_twins` asks the same hash question of the `FF_MODIFIED` half, and
`advance_shared_tree` takes its all-or-nothing test over the **union**. The safety argument is the
sibling's unchanged — if the working-tree bytes at `P` equal origin's blob at `P`, that content is
already on origin, so returning `P` to HEAD cannot lose it and the fast-forward writes those same
bytes straight back.

**The two kinds need different acts, and that is not cosmetic.** `unlink` on a path with an index
entry leaves the entry behind, and the fast-forward stays refused on a file that is no longer even
on disk — strictly worse than not touching it. `restore_tracked_twin` discriminates on
`_blob_in_head`: a path HEAD knows goes back to HEAD's copy; a staged ADD has no HEAD copy to go
back to, so it leaves the index *and* the disk.

## 3. What this does NOT do, and the fifth path

`background/process_run_complete.py` carries another lane's 58 uncommitted lines (a provenance
re-read after the advance, at both commit sites). It is not on origin by any route — three
distinguishing strings, zero hits in `origin/main`'s copy. It is real work, it correctly refuses the
whole advance, and `tools/isolate_hunks.py --survey` is that lane's remedy, not mine. **So the tree
is still behind at filing.** The repair removes four of the five holds and unblocks nine more
behind them; it does not, and must not, clear the one that is somebody's work.

Predicted next state, recorded before it happens: once this commit lands, `origin_reconcile.py` and
its two test files stop being dirty at all, and the blocking set becomes nine untracked twins plus
two staged twins plus `process_run_complete.py` — **all resolvable except the last**, which holds
everything until that lane lands its hunks.

**Measured after landing `aab6fb990`, beside the prediction:** `blocking: 13 | untracked twins: 10
| tracked twins: 2 | STILL HELD BY: ['background/process_run_complete.py']`. The substance held —
one path, and it is the one that is somebody's work. The **count** did not: I predicted nine
untracked twins and there are ten, because a further staging note arrived from another lane between
the prediction and the measurement. That is the tree being live, not the mechanism being wrong, and
it is worth keeping written down: **a prediction about a count over a shared tree is a prediction
about a minute.** The property (which paths are resolvable, and why) is what was actually being
tested and is what held.

## 4. Controls

`tests/background/test_the_twin_sweep_was_defeated_by_git_add.py`, 9 tests, **nine named mutations
each verified to red it** (drop `tracked` from the union; take the length test over `twins` alone;
relax all-or-nothing to `if not resolvable`; route every path through `_remove`; ignore
`_restore`'s return value; guard only the untracked `None`; return `None` unconditionally from
`restore_tracked_twin`; drop the `_blob_in_head` discrimination; refuse unconditionally). The last
is the reachability control — every other control here asserts a refusal, and an
`advance_shared_tree` that refused unconditionally would pass all of them.

Two of the nine run against a real throwaway git repository rather than a mock, because
`restore_tracked_twin` shells out to git and asserting it against a mock would assert my belief
about `git checkout HEAD --` rather than git's behaviour. That is what caught the staged-ADD leg:
a single `git checkout HEAD -- <path>` fails there with *"did not match any file(s) known to git"*.

`_Advance` in the pre-existing suite also gained the injected seam. Left at its default the new
call would have shelled out to git against the live repository, and those controls would have
graded whatever the shared tree happened to be holding that minute.

## 5. The class this belongs to

Sibling to `SEAT_FINDING_THE_RECONCILER_AND_THE_PUBLISHER_EACH_STAND_DOWN_FOR_THE_OTHER…`, and a
different mechanism: nobody was standing down here. The reconciler reached its window, looked,
found the fork, and refused on a set it had mis-partitioned. **A control that classifies its
subject before measuring it is blind to every member the classification puts on the other side** —
and the classification here was `git add`, which is not a fact about the file at all.
