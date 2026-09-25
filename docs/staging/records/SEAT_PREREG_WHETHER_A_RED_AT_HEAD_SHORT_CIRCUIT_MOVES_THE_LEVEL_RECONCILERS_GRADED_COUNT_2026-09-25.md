# [PREREG] Whether a red-at-HEAD short circuit moves the level reconciler's graded count

**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** unminted

**Written BEFORE the measurement, 2026-09-25.** The number below is a prediction about an
INSTRUMENT, not about the world, and it is filed here so it can refute me.

## The claim under test

`tools/level_zero_contradicted_by_its_own_controls.py` returns `population 28, graded 0`
(measured 2026-09-25, landed in `8a1269101` + `d214fc5e7`). The age leg that discarded nine
atom-own controls is fixed and the number still did not move, because production caps each atom
at `_LEVEL_ZERO_TIMEOUT_S = 60` (`background/delivery_seat.py:1038`) while `KNIFE3_wall_crossing_
paydown`'s twelve suites cost 1078s. The instrument is bounded by COST, not by evidence, and the
rows naming the most controls are exactly the ones it can never reach.

A row naming a suite that is ALREADY RED AT HEAD cannot be CONTRADICTED — CONTRADICTED needs the
whole named set to pass — so for those rows the expensive run buys a verdict already known.

## What I am about to build

A leg in `assess` that resolves a row to SILENCE without running its suites when any named
control holds a test recorded `currently_red` by the HEAD-red register, and that FAILS CLOSED
(runs the suites, exactly as today) when the register is unobserved, undated or stale.

## The predictions, before running it

1. **KNIFE3 moves from ungradable to silent.** It was discharged by hand this way and came back
   SILENT: 2 of its 224 tests are red at HEAD and have been for 19 consecutive census runs since
   2026-09-02.
2. **`graded` rises from 0 to at least 1**, and `population` stays 28. A silenced row HAS been
   weighed — we have evidence its named set does not all pass — so it counts as graded, which is
   the number the two findings above could not move.
3. **`contradicted` stays 0.** The leg can only ever silence; it is structurally incapable of
   producing the refusing verdict. If `contradicted` moves at all, this build is wrong.
4. **In an isolated worktree the leg is inert**, because `.head_red_observed.json` is untracked
   and therefore absent there — the store reads UNOBSERVED and every row fails closed to the run.
   That is the stale arm, and it is reachable in this very worktree rather than only in a fixture.

I do not know whether any row OTHER than KNIFE3 is silenced by this. I have not counted, and the
count is the part of this that is a genuine question.

## What would refute each

1. KNIFE3 still ungradable → either the register does not name its suites under the paths the row
   names, or the leg is unreachable.
2. `graded` still 0 → the leg fires for no row, or an earlier leg (absent control, predating,
   provenance, budget) returns first for every row that would have qualified.
3. Any movement in `contradicted` → the leg is loosening the refusing verdict, which is the one
   outcome that makes it a defect rather than an economy.
