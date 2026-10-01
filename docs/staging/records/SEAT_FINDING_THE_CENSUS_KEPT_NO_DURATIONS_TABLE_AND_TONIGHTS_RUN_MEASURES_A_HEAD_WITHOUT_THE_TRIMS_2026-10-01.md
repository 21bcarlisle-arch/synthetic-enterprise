**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `unminted`

# FINDING — the census kept no durations table, and tonight's run measures a HEAD without the trims

Lane 0 `the-census-bound-follows-the-trimmed-suite`. The direction: after the next complete nightly
census, read its wall clock and `--durations=80` table, move `WORST_OBSERVED_SUITE_SECONDS` to that
run and `SUITE_TIMEOUT_SECONDS` to just over twice it, and trim whatever tops the table.

**Duplicate-work note at draw:** the "other live claim" was this same id, written by this draw's own
executor (pid 2955244, the owner of this worktree). No rival seat or `surgical_land` held it. No
disposition needed.

## Two things stood between the direction and doing it

**1. The table the direction asks for did not exist.** `pytest_argv()` never passed `--durations`,
and `main()` printed only the verdict -- the suite's output was parsed for reds and dropped. The
journal held a wall clock and nothing about which tests spent it; every past trim began with a
separate multi-hour timing run outside the unit. **Fixed in this commit**: the census runs
`--durations=80` and prints each row to the journal as `  SLOW     <row>` (and as `durations` under
`--json`). Three mutations fire: drop the print, empty the parser, drop the flag.

**2. Tonight's 03:34 census does not measure the trimmed suite.** Its subject is
`git rev-parse HEAD` in the SHARED tree (`prc._head_sha`), which at 02:05 was `9a5dc872e`, diverged
from origin (2 ahead, 23 behind) and not containing `571a79e9f` or the other trims. Its driver is
the shared tree's working copy too, so the durations change above also only reaches the unit once
the shared tree carries this commit. Whatever wall clock tonight's run produces is the UNTRIMMED
suite and must not be used to move the bound down.

## Pre-registration (written 02:20 BST, before either run has started)

- **Tonight (03:34, subject `9a5dc872e` or whatever shared HEAD is at 03:34, untrimmed):** if it
  completes, 7,500-9,500 s wall, same band as the 09-30 timing run (8,647 s). No durations table in
  the journal unless the shared tree has advanced past this commit by 03:34 (I predict it will not).
- **First complete census whose subject contains `571a79e9f` AND whose driver carries this
  commit:** 5,800-7,600 s wall (8,647 s less the ~1,750 s the trims saved, widened for contention),
  and a `SLOW` table whose top row is under 300 s.

## What done means for this item

The bound moves when -- and only when -- a complete census with a trimmed subject and a printed
table exists in the journal: `WORST_OBSERVED_SUITE_SECONDS` to that run's wall (unit line
`Consumed ... over <wall>`), `SUITE_TIMEOUT_SECONDS` to just over twice it, unit
`TimeoutStartSec` = timeout + 300, and the top of its `SLOW` table trimmed. That is handed on as a
continuation, because it needs a run that cannot exist inside this turn.
