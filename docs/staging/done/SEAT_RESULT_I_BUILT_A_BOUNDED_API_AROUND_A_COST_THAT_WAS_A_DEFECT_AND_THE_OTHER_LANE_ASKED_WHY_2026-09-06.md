**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** EP13_adapter_carbon_intensity
· **Class:** measurements_that_mirror

# RESULT: I built a bounded API around a cost that was a defect, and the other lane asked why

**2026-09-06, delivery seat, lane 0 claim `ep13-embedded-generation-measure-has-no-test`.
Pre-registered at
`docs/staging/SEAT_PREREG_WHAT_A_CONTROL_OVER_EP13S_MEASURE_COSTS_AND_WHAT_SHAPE_THAT_LICENSES_2026-09-06.md`.
This document supersedes the result written before the merge; the withdrawn work is described
here rather than deleted, because the withdrawal is the finding.**

## What happened

Two lanes drew the same defect — `tools/ep13_embedded_generation_bound.measure()` is executed by
nothing but `main()`, and no test runs `main()` — and worked it concurrently. The merge is where
we found out. `eaac64f49` landed first and is the better answer; commit `932713380` in this lane
is withdrawn, and `tests/tools/test_ep13_embedded_generation_bound_measure.py` is deleted rather
than merged.

**Both lanes were right about the defect and only one asked why it had survived.**

## The two answers

| | this lane | `eaac64f49` |
|---|---|---|
| first move | measured what a full `measure()` costs | measured what a full `measure()` costs |
| reading | > 3,000s, killed at its timeout without finishing | one real year did not finish in seven minutes |
| **next move** | **designed a bounded API so a control could afford it** | **asked why a correlation fit over 15,000 half hours takes seven minutes** |
| what it found | a control that runs one year, one grid, one seed, in 331s | `_matched_scale` called INSIDE a comprehension over the year's half hours, each call walking all of them — a loop-invariant recomputed n times, O(n²). Hoisted: 3.7s → 0.1s, a full real pass is **23s** |

With the hoist, the whole reason my design existed is gone. `measure()` needed no `only_years`,
no `grids`, no `null_seeds`; the control simply runs it. Every parameter I added was machinery
built to survive a defect instead of removing it.

## THE LESSON, and it is not "measure first"

I did measure first, before writing anything, with the predictions registered. The rule worked.
What is missing from my own habits is the step after it:

> **A cost you measure is a reading about the code, not a fact about the problem. Before you
> design around a number, ask whether the number is a defect.**

Seven minutes for a correlation fit over a year of half hours should have been implausible on its
face — the same arithmetic on synthetic worlds of the same size was in the suite already, taking
the same implausible time, and the suite's own 623 seconds had been read for months as *what this
measurement costs*. Two lanes looked at the same figure; the difference was one question.

This is `measurements_that_mirror`: my cost measurement was correct, reproducible, pre-registered
and about a subject that was broken, so it measured the defect back to me and I built a shape
that fitted it.

## The secondary finding, which stands on its own

The withdrawn file's load-bearing control could not fail, and the shape is general enough to be
worth keeping:

The bounded design rested on `only_years` **filtering** the year intersection rather than
**selecting** from it — a selector would have made every assertion in the file a statement about
its own argument. I asserted that property directly, by asking for `1999` alongside a year that
must exist, and named the test after it. **Replace the filter with `years = list(only_years)` and
the returned dict is identical**: `measure_year("1999", …)` finds no fit half hours, raises
`NesoIntensityUnavailable`, and the year loop's `except …: continue` swallows it. The selector
mutation is an equivalence, not a survivor, and the swallow is why.

> **A fail-quiet loop makes the property of its own input filter unprovable from outside the
> function.** Any control over "the argument narrows the work rather than choosing it" is a
> tautology wherever the work silently drops what it cannot do.

Caught by working the mutation through before buying the round, which is the only reason it is
recorded here rather than shipped as a green test.

## What this lane did buy, kept

Two poison rounds, both pre-registered, both on the withdrawn code but both about `measure()`
itself and both still true of the merged version:

| round | mutation | predicted | observed |
|---|---|---|---|
| A | a `fuel_mix()` failure swallowed inside `measure` | the `fuel_mix` leg reds, the demand leg does not | exactly that, 2.78s |
| B | top-level `"grid"` key renamed | two named tests red, all others green | exactly that |

Round A also establishes a number the other lane's write-up leaves open: **the four cache loads
cost ~1s in total, not 20–90s** (pre-registration prediction 2, refuted). The whole bill was the
quadratic term.

Round B is the source of the one control from the withdrawn file worth porting, and it is being
ported rather than dropped: `measure()`'s top-level `grid` block is hand-written beside numbers
computed from `U_BINS`/`V_BINS`/`W_BINS`, so it can declare 12x4x3 while the rungs were
partitioned on something else. Multiplied out, it must equal the cell count `ceiling_3d` reports.
`eaac64f49`'s class does not assert it, and its `--out` run writes into a directory that already
exists, so `main`'s own `mkdir(parents=True)` is never exercised either. Both land as legs on
that lane's class.

## What is NOT established

- **The battery has not been re-run.** `eaac64f49` says the tenth column is now affordable at
  about six minutes; nobody has bought it, and no `reaches_subject` verdict from the engine
  exists for the repaired suite. That is the obvious next piece and it is handed on, not done.
- **Whether the same quadratic shape is in the sibling bounds.** `ep13_input_ceiling`,
  `ep13_peer_bound`, `ep13_per_fuel_oracle_bound` and the two CCGT ceilings share this file's
  binning, split and shuffle by import. None of their runtimes has been looked at with this
  question in hand.
