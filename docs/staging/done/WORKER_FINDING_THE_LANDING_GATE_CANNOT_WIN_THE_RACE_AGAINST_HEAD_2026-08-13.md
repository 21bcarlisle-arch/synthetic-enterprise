# WORKER FINDING — the landing gate cannot win the race against HEAD, so expensive work cannot land

**Severity:** BLOCKING · **Lane:** H_harness

**Found:** 2026-08-13 ~19:20–20:00 UTC, during the `H27_payment_belief_gap` 2→3 HARDEN draw
(worker tick), while trying to land Expert Hour #27.
**Class:** a control that must win a race has the weather as its subject.
**Disposition:** QUEUED, not fixed on sight (SELF-INTERRUPT DISCIPLINE) — the repair touches
`tools/surgical_land.py`, which is the mechanism behind a WALL (hook-bypass), and a wall control
is not the thing to patch in a hurry at the end of a bounded tick.

## Observed, with evidence

`tools/surgical_land.py` is the ONLY legal landing move on this shared tree (CLAUDE.md:
"HOOK-BYPASS IS A WALL"; `--no-verify` and hand-built merges are never a judgment call). Its
step 5 is a compare-and-swap: **refuse if HEAD moved since the gate started**, because the gated
tree would no longer be the tree the commit creates. That refusal is CORRECT in principle. It is
also, on this box today, unsatisfiable for any commit whose gate selects an expensive test file.

**Three consecutive attempts, all refused, none for a test failure** (`observed-with-evidence`):

```
[surgical-land] REFUSED: HEAD moved from c8284059b to 24c14f629 while the gate ran
[surgical-land] REFUSED: HEAD moved from 24c14f629 to 0115741d4 while the gate ran
[surgical-land] REFUSED: HEAD moved from 0115741d4 to 33443e716 while the gate ran
```

**The two clocks that cannot both be satisfied:**

| clock | measured |
|---|---|
| gate duration | **~9m24s** (735 tests, 564s) |
| HEAD move cadence | 19:21:40 → 19:31:23 → 19:34:57 → 19:43:43 = **3.5–10 min** |

The gate is longer than the median gap between commits, so the compare-and-swap loses more often
than it wins. Three losses in a row is not bad luck at those two numbers; it is the expected outcome.

**The gate cost is one file, and it is the drawn atom's own.** The gate ran 735 tests in 564s.
`tests/tools/test_couple_w2_11_d5.py` alone is 457 tests in **556.78s** measured standalone — so
~99% of the gate's wall-clock is a single 9,700-line module's test file, and the other 278 tests
cost ~7s. Any H27 Hour touches that module by definition (it is the atom's whole `file_scope`),
so **every future H27 Hour inherits this same unlandable shape.**

**Who moves HEAD:** not other BUILD lanes competing for the same files. The movers in the window
were the publisher and daemons — `chore(provenance): verification paused banner`,
`Auto-process run complete`, `chore(liveness): publish heartbeat` — whose paths are disjoint from
the pathspec being landed. The gate's verdict was invalidated by commits that could not have
changed it.

## Why this is a defect and not just slowness

The refusal is load-bearing and must not be weakened — that is the wall. The defect is that the
control has no move that terminates. A rule that leaves no legal move evaporates (MAKE_IT_STICK),
and the observed consequence is already in this repo's history: **Hour #27's mechanism was written
by the prior tick and left uncommitted**, which is how this tick found it (absent at HEAD,
`_DoorRowWalker` grep = 0, green in the tree). That is the orphaned-work class
(`CLASS_UNCOMMITTED_AND_ORPHANED_WORK`) being *manufactured* by the landing control, one tick at
a time. This tick reproduced it rather than escaping it.

## The candidate repairs, none taken here

1. **Bounded auto-retry in `surgical_land`** (`--retries N`, re-gating against the new base each
   time). Honest — it still gates the exact tree it commits, so the wall is untouched. But each
   retry costs another full gate, so at these two clocks it converges slowly and burns CPU.
2. **Make the verdict transferable.** After a HEAD move, re-gate only if the new commits touch
   paths the verdict depends on; otherwise fast-forward. This is the *correct* fix and the
   riskiest to get right — "disjoint paths" is exactly the reasoning that made `git merge` sweep
   35 paths on 2026-08-09. Needs R15 mutation proof that it still fires on a genuine conflict.
3. **Cut the gate's dominant cost.** `test_couple_w2_11_d5.py` at 1.2s/test × 457 is the whole
   bill. Splitting it, or making the gate's selection finer than a name stem, helps every lane and
   weakens no control. **Recommended first** — it is the only one of the three that touches no wall.

## What this finding does NOT claim

That the gate is wrong to refuse — it is right. That HEAD movement is misbehaviour — the publisher
and daemons are doing their jobs. Only that the two, together, leave a class of legitimate work
with no terminating path to land, and that the class is exactly the expensive-to-verify work most
worth landing.
