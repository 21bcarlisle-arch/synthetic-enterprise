# [SEAT FINDING] The reconciler is not silent — its clearing rule is all-or-nothing, and three machine-written artefacts hold the fast-forward open

**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery, origin-fork reconciliation

**Filed** 2026-09-10 by the delivery seat, as the second half of the Lane 0 item
`two-always-run-ratchets-are-red-because-a-finished-module-never-left-the-working-tree`, which asked
whether `background/origin_reconcile.py` had run at all since 11:23 and why the gap widened from 4
to 9 while it was supposed to be closing it.

---

## 1. The question's premise is refuted: it has run, and it was running while this was written

The item read the widening gap as silence. It is not silence.

```
PID 1366561  started 18:02:23  elapsed 08:38  STAT S
/usr/bin/python3 -m tools.surgical_land --merge origin/main -m "merge origin/main: automatic
reconciliation in an isolated worktree  Closed by `background/origin_reconcile` on the deadman
cadence, ..."
```

That is the reconciler's own gated merge door, launched by the reconciler, alive on the box. The
elapsed time is not a wedge: a `surgical_land` runs the full nine-gate battery, which CLAUDE.md
already records as taking more than ten minutes. Eight minutes in is a merge working.

`background-worker-log.md` shows the same module running repeatedly across 09-08, 09-09 and 09-10.
Its docstring cites a 2026-09-04 measurement of **41 real forks closed unaided**. The daemon is
alive and doing its job.

**The gap did not widen because nothing ran. It widened because the thing that runs cannot clear
what is actually blocking it, and says so identically every time.**

## 2. What is actually blocking it, measured on real disk

13 untracked paths in this checkout are also added by `origin/main`. Each one blocks the
fast-forward, because git will not overwrite an untracked file. Of the 13:

| | count | what they are |
|---|---:|---|
| byte-identical to origin's copy | **10** | staging documents this tree wrote and origin already has |
| **not** identical | **3** | all machine-written |

The three that differ:

```
docs/observability/head_red_observed.json                     producer output (nightly census)
docs/observability/value_cycle_ab_s1_three_arm_20260910.json  run artefact
docs/staging/reference/HEAD_RED_REGISTER.md                   machine-rendered register
```

Not one of them is a person's unlanded work. All three are **exhaust from producers that run on a
cadence in this tree**, and every run rewrites them and re-diverges them from origin.

## 3. The mechanism — the clearing rule is all-or-nothing, so one differing path is enough

The reconciler's own refusal, quoted verbatim from the log at 2026-09-10 08:00:

> The advance reported: **1 of 4 blocking path(s) are NOT byte-identical to what origin brings, so
> clearing the 3 that are would delete files and still not advance. Nothing was removed.**

That is the defect, and it is stated plainly by the thing that has it. The rule is: remove a
blocking untracked path only when its bytes already equal origin's — and if any path fails that
test, **clear nothing at all**, because a partial clear deletes files without advancing.

The conservatism is right. The consequence is not. A single machine-written artefact that a local
producer keeps rewriting is enough to make every subsequent run of the reconciler a **no-op that
returns the identical complaint**. The deadman brings it back in five minutes; it re-refuses the
same way; origin meanwhile keeps receiving commits from other lanes. The gap grows monotonically
between gated merges, which is precisely the 4 → 9 → 12 the item observed. It was 12 behind / 8
ahead while this was written.

The refusal even names the remedy for the generated case — `git show HEAD:<path> > <path>`, let the
fast-forward install origin's copy, let the producer regenerate. But **nothing performs it**: the
remedy is prose addressed to a reader, on a path whose whole premise is that no reader is coming,
because this is the deadman cadence running unattended.

## 4. Why this is the same class as the item that found it

The Lane 0 item's class was *"finished work sits untracked."* Its instance was a 20KB module. This
finding is the same class one turn out and costs more: **untracked machine state holds the fork
open**, and the fork is what makes two always-run ratchets red in the shared tree while they are
green at `origin/main` — the presentation the item itself called the worst possible, because it
reads as ratchet drift and sends the next reader to widen a bound.

One of the three, `HEAD_RED_REGISTER.md`, is rendered by `background/head_red_register.py`. The
uncommitted `standing_red` integration deleted this turn would have changed that file's bytes
permanently. **The abandoned work and the wedge were about to become the same problem.**

## 5. This is a finding, not a repair, and deliberately

The item was explicit that the reconciler's silence is "a finding about the reconciler, not a reason
to hand-merge a tree holding this many dirty paths." That holds, and more so now that the cause is
known: a merge was already in flight from the module that owns this, and a second concurrent
`surgical_land` would have killed it.

No bound was widened, no path was hand-cleared, and the shared index was not opened.

## 6. What is next

1. **The reconciler should clear the identical paths even when some differ.** Removing a path whose
   bytes already equal origin's is lossless by construction, and doing it unconditionally shrinks
   the blocking set every cycle instead of leaving it whole. Today's arithmetic: 13 blockers → 3.
   That does not close the fork alone, and it stops the set growing without bound between merges.
2. **Generated paths need a route that does not ask a reader.** The refusal already classifies them
   as producer output and already knows the safe move. On the deadman path that move should be
   taken, not printed — restoring `HEAD:<path>` over a producer's exhaust cannot lose work, and the
   producer rewrites it on its next tick either way.
3. **Establish why three producers write untracked artefacts at all.** `head_red_observed.json` has
   a landed copy at `origin/main`, so the local one is a tracked file's untracked twin — the shape
   `SEAT_RESULT_THE_HEAD_RED_OBSERVATION_IS_MACHINE_STATE_AND_UNTRACKING_IT_IN_PLACE_WOULD_HAVE_WEDGED_EVERY_LANE_2026-09-10.md`
   already reached, from the other direction. These two records should be read together.
