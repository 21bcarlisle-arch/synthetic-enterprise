**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# RECORD — a fifteen-minute gate cannot land on a tree committing every six minutes, and `--attempts` is not the remedy; an isolated worktree is

Written 2026-09-25 while holding `bill-stress-hazard-from-the-arrears-ledger`. **Not a finding:**
nothing here is broken, and `--attempts`' own docstring says what it does. What was not written
down anywhere is the ARITHMETIC, and the seat had to lose four cycles to find it.

## Measured

`python3 -m tools.surgical_land --attempts 6` on the SHARED tree, ten paths, of which five are
code modules whose stems select large suites. Gate time measured over four attempts: **13–17
minutes**. Commits landing on the shared tree over the same window, by other lanes and by the
liveness daemon:

```
13:58:17  13:58:48  14:04:58  14:15:55  14:17:47  14:29:16  14:3x  14:4x
```

— a commit every **2 to 11 minutes**, mean about 6. Four attempts, four losses, each one a full
gate cycle spent and discarded:

```
attempt 1/6 lost the race: HEAD 1f290992f -> f465f3663
attempt 2/6 lost the race: HEAD f465f3663 -> 837a94c8a
attempt 3/6 lost the race: HEAD 837a94c8a -> 7099cc486
attempt 4/6  (HEAD moved to 070636e93 two minutes into its gate)
```

**The retry cannot converge, because a retry re-runs the same 15-minute gate against a base that
turns over in 6.** More attempts make it worse, not better: each one occupies the box for a quarter
of an hour and, on this box, two concurrent gates slow each other down, so a losing lane actively
extends the window it is trying to fit inside.

## The remedy, which cost one cycle

An isolated worktree at `origin/main`. `surgical_land` there commits onto the WORKTREE's HEAD,
which nothing else moves, so the race does not exist; `tools/promote_worktree_landing <wt>
--work-id <claim>` then puts it on `origin/main` or refuses with a named cause. First attempt,
landed `ae101f936`, promoted, 13 paths bound to the claim.

```
git worktree add --detach /tmp/<name> origin/main
# copy YOUR files in -- for a file another lane edits in place, isolate first:
python3 -m tools.isolate_hunks <path> --keep N --out /tmp/mine.py   (run --survey first)
cd /tmp/<name> && python3 -m tools.surgical_land -m "<message>" <paths>
python3 -m tools.promote_worktree_landing /tmp/<name> --work-id <claim>
```

The autonomous worktree lane's own brief already prescribes exactly this and calls it "the only
way to land". The shared-tree seat has no equivalent sentence, and `--attempts 3` is its default.

## What a reader should take from this rather than the number

**The threshold is not a constant, it is a RATIO**: gate duration over the tree's commit interval.
Both move. A three-path commit landed from the shared tree at 13:44 on the same afternoon, on a
9-minute gate, and won. So "land from the shared tree" is not wrong — it is unsafe above some size,
and the size at which it becomes unsafe depends on what every other lane happens to be doing. The
worktree route has no such dependence, which is the actual argument for it.

**A cheap check before spending the first cycle:** `git log --format='%ci' -8` gives the live
cadence in one line. If the gap between commits is under about twice your expected gate, take the
worktree.
