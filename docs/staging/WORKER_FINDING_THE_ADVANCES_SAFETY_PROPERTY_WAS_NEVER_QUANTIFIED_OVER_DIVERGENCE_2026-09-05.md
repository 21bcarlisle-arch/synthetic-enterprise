**Severity:** LATENT — the defect is fixed and landed with this finding; it cost no file on
2026-09-05 only because four non-twin paths refused the advance for the wrong reason, and the twin
sweep's whole purpose is to remove exactly those four · **Lane:** H_harness · **Epoch:** 3 ·
**Atom:** none — RUNG 1 shared-tree advance · **Class:** publish_gate_and_wedge

# The advance's safety property was never quantified over divergence

Filed 2026-09-05 by the autonomous worker. The tick's direction was *"land the 58 uncommitted lines
in `process_run_complete.py` so the advance gets its first real trial."* That landing was already
done when this tick opened (`7b3134f86`), and the trial it enabled is written up in
`WORKER_FINDING_THE_BRIDGE_STRIPPED_ONE_NEWLINE_AND_THAT_IS_WHY_THE_ADVANCE_HAS_NEVER_FIRED`.
**This is what the trial found one layer down: the advance would have been wrong even if it had
been handed the tree it was waiting for.**

## 1. What the tree actually said

On the live shared tree, immediately after the landing:

```
fork_state()                      → behind 32, ahead 5
git merge --ff-only origin/main   → hint: Diverging branches can't be fast-forwarded
paths_blocking_fast_forward()     → 18 paths
  untracked twins: 14 · tracked twins: 0 · held by: 4 non-twins
```

Eighteen paths were named. **Not one of them was the cause.** The tree had diverged — five local
commits origin did not have — and a diverged branch cannot fast-forward whatever its working tree
holds. Git says so in a sentence the module never read.

## 2. Why that is a defect and not a diagnostic wart

`advance_shared_tree`'s docstring makes a safety claim:

> ALL-OR-NOTHING, AND THAT IS A SAFETY PROPERTY, NOT TIDINESS. Nothing is touched unless clearing
> the twins would leave the fast-forward with nothing else to refuse on.

That sentence is **false under divergence**, because "nothing else to refuse on" was only ever
quantified over the dirty-tree collisions `paths_blocking_fast_forward` enumerates. On 2026-09-05
the guard refused — and it refused for the wrong reason, held by four non-twins that are not the
cause of anything. Clear those four (which is what the lanes holding them are being asked to do,
and what the twin sweep exists to make unnecessary) and the count check passes. Then this takes the
tree lock, unlinks fourteen files, restores the tracked ones, and fails the second `--ff-only`
exactly as it failed the first.

That is the module's own named worst case —

> clearing them there would be a deletion bought for no advance — the one shape in which this could
> actually cost someone something

— reached through the one door its guard was not watching. **The tree was one repair away from the
harm, and the repair was the thing everyone was working on.**

## 3. The window is minutes wide, not hypothetical

`reconcile()` reads `ahead` once at the top, then merges in an isolated worktree, gates that merge,
and pushes it before calling `advance_shared_tree` — bounded by `MERGE_TIMEOUT_SECONDS`, so minutes.
Several sessions and daemons commit into this one shared tree throughout; this tick alone found a
rival seat executor committing while it worked. A tree that was level when `reconcile` looked is
routinely diverged by the time the advance runs. Both call sites read `ahead` before the work, not
before the act.

## 4. The repair

One question, asked of git, before any path is judged — `background/origin_reconcile.py`:

- `advance_shared_tree` gains an injectable `ahead_fn`, defaulting to the module's own
  `commits_ahead` — the same seam `reconcile` already trusts to decide whether a merge is
  legitimate at all. No new way to read git.
- Divergence refuses, names the commit count, and points at the leg that closes a fork. It does
  **not** name the blocking paths: naming them is what sent readers to `isolate_hunks` on innocent
  files every five minutes while the tree lost 22 commits of ground.
- Unreadable refuses too. A file is never deleted on a question that was not answered.
- The blocking set is not even enumerated on a diverged tree.

## 5. What the controls would catch

`tests/background/test_a_diverged_tree_is_not_a_dirty_tree_and_clearing_twins_cannot_advance_it.py`.
Four mutations were run against the live module and each fired on its own control alone:

| Mutation | Reds |
|---|---|
| delete the `if ahead:` branch | the defect, the refusal wording, the ordering, the seam |
| make the guard unconditional | **only** the reachability control — all three refusal tests stay green |
| default `ahead_fn` to a constant `0` | **only** the seam control |
| treat an unreadable count as zero | **only** the fail-closed control |

The second row is the one that matters. A guard that refused every tree would pass every refusal
test in the file while silently retiring the twin sweep — a mechanism that has never once fired in
production and so has no live behaviour to notice its own absence. That is this project's recurring
shape (*a world check ahead of the verdict silently retired six decomposition controls*), and the
reachability leg is the only thing standing between this repair and repeating it.

The ordering control is a genuine one rather than the same answer by another route: asked before the
clearing loop, a diverged tree loses no files; asked after it — which is where a "report the true
cause" fix would naturally be written, beside the second `--ff-only` that *already* says the
collision was not the cause — the files are gone by the time the truth is told.

## 6. What this does not fix

The fork itself. At filing the tree is still `behind 32, ahead 5`, and closing it is the
reconciler's own merge leg, blocked at the time of this tick by a running publish gate
(`gate_is_running: True`, two pytest runs mid-flight) — which the reconciler correctly stands down
for. A live rival seat executor is on that same Lane 0 item in an isolated worktree and has already
filed `the direction's premise expired mid-turn: the same repair landed twice`. This tick did not
race it on the shared tree.

**Prediction, filed before the fork closes:** when it does close, the advance's first real trial
will refuse on the four non-twin paths and not on divergence — because the merge leg pushes before
it advances, which makes `ahead` zero at that moment. If it instead refuses naming divergence, the
TOCTOU window in §3 is not merely reachable but routine, and the guard should move from
`advance_shared_tree` into `reconcile`'s own re-read.
