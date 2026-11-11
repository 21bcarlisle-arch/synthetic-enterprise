**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The operational red outlived its fix because the shared tree sat 103 commits behind origin (2026-11-11)

**Found by.** The worker tick drawn on the operational-layer persistent red, 11 Nov 2026, about 07:20 GMT.

## What was seen

- The operational fix `0c8d05099b` landed on origin at 06:45 GMT. It isolates the deadman-cycle tests
  from the live repo's content age.
- At 07:05 the hourly check still recorded a fifth consecutive red
  (`docs/observability/.operational_layer_signal.json`).
- At origin/main, in a clean worktree, `pytest tests/ -q -m operational` gave **1203 passed**.
- The shared tree's `main` was `e57bda6891`, committed 9 Nov at 21:02. That is **103 commits behind
  origin**, and the fix was not among its ancestors. The hourly check runs in the shared tree, so it
  was testing code from before the fix.

## Cause of the stall

`git checkout -B main origin/main` refused on 39 paths:

- 23 were byte-identical to origin.
- 10 were older committed copies. These are the "armed to revert" set the tree-divergence alarm names,
  for example `DOMAIN_INVARIANTS.yaml` at `75f66f6521`.
- 7 held bytes in no commit. All 7 turned out to be superseded:
  - D9 is closed on origin, so its map row was stale.
  - `STARTUP_ANCHORS.md` is generated.
  - Origin's copy of the alarm document carries the written end-to-end check.
  - The finding's C7 section was an earlier, ~19:30 variant of the section origin carries from ~21:00.
  - `sanity_daemon.py` merged to origin's own bytes.
  - Two were genuinely local: a regenerated `site/harness/index.html`, and one orphaned W3_3
    `LEVEL_UP_SELF_CERTIFIED` line in `gate_authorizations.jsonl`. That line is on neither origin nor
    the held `w3-3-network-split-held` branch.

`background/origin_reconcile.py` (`reconcile-watch`) clears twins. It did not clear this mix, and
nothing paged that the shared HEAD was 34 hours stale. The tree-divergence alarm reported "1 commit
behind" when it was last re-derived.

## What was done, and how to reverse it

1. Preserved every one of the 16 differing blockers as a blob under
   `refs/preserved/headmove-20261111T0725/1` through `/16`. Each is recoverable with
   `git cat-file -p <ref>`. The numbers follow the blocker list order as `checkout -B` printed it.
2. Put HEAD's bytes back on the tracked blockers, removed the untracked twins, and ran
   `git update-index -q --refresh && git checkout -B main origin/main`. The shared index's one staged
   entry (another lane's ninth-cold-read finding) was carried through unchanged; the index raw diff was
   checked before and after.
3. Wrote the two genuinely local items back, uncommitted, exactly as they were: the harness page, and
   the W3_3 line appended to origin's log.
4. Ran the operational suite in the shared tree: **1203 passed**. The signal clears on its next hourly
   check.

NTFY is mothballed (CLAUDE.md, 15 Oct), so the cause is recorded here rather than sent to his phone.

## Open

Why did `reconcile-watch` not move the shared HEAD for 34 hours, and why did no alarm name a stale
HEAD? A stale shared HEAD makes every shared-tree check read old code, so a fix on origin cannot clear
the red it fixes.

NEXT: none -- the instance is cleared; the reconciler question is filed above for the harness lane
