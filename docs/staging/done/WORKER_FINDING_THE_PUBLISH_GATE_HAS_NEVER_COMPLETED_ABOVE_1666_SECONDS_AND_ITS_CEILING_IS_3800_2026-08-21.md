**Severity:** LATENT · **Lane:** H_harness

# The publish gate has never completed above 1666s in 147 measured passes, and its ceiling is 3800s: the "75-minute gate" is not a duration, it is the last number anyone wrote

**DIRECTOR, 2026-08-21 14:56Z console:** *"A 75-minute gate is absurd on its face and neither of
us said so. Two weeks ago it was ten minutes... Say what the gate is actually for and how long
that should take."*

This document answers the second half with the gate's own record, and the answer contradicts the
premise both of us were working from. **The gate did not grow to 75 minutes. It stopped
finishing.** Every figure below is read from `docs/observability/publish_gate_duration.jsonl` at
the commit that files this document, fixtures excluded (`deadbeef`, `abc1234`, per the
2026-08-20 repair).

## Observed, not inferred

`publish_gate_duration.jsonl` holds 5,571 rows, 1,954 of them non-fixture:

| outcome | rows |
|---|---|
| `pass` | 882 (147 with a substantive runtime > 60s) |
| `fail` | 1,067 (median 0.0s — `-x` fail-fast) |
| `timeout` | 5 |

**In 147 substantive completed runs the gate has never once exceeded 1666.0s.** Median 1251.7s.
The six most recent, newest last:

```
d7c80d110  1320.79     6467c826f  1299.90     a5bfec712  1246.27
43766e01e  1322.64     b559c070f  1302.93     a892df011  1247.73
```

**Every one of the 5 timeouts equals its own ceiling**, to within the polling interval:

```
ceiling  300 -> 303.89, 304.05
ceiling 3400 -> 3403.67
ceiling 4500 -> 4503.53, 4503.70
```

A timeout duration is therefore not a measurement of anything. It is the ceiling, read back. Six
ceiling raises (600 → 1800 → 2600 → 2900 → 3600 → 3800/4500) have **never once converted a
timeout into a pass** — the run simply got killed at the new number instead of the old one.

## What this means, stated plainly

The gate's honest cost, the last time it completed, was **1247.73s — 21 minutes** (subject
`a892df011`, 2026-08-20 19:04, the run that produced the last successful publish at 02d0078e2).
There has not been a completed gate run since **2026-08-21 01:40** (subject `2c0ba712b`, the
first 4500s timeout).

So "75 minutes" was never the suite's duration. It is `GATE_SUITE_TIMEOUT_SECONDS`, and the
suite has been running into it because something made it unbounded, not because it got slow.
**The remedy the shape invites — cut scope until the number comes down — cannot work on a
quantity that has no finite value.** The scope narrowing that landed at 92e5b380a (198 → 163
blocking files, including the 198s check filed at 104101496) is right on its own merits and
removes real cost; it is not addressed at this.

## The regression window, named

Bounded by the two adjacent subjects in the series:

- **last pass** `a892df011` — 2026-08-20 19:04, 1247.73s
- **first timeout** `2c0ba712b` — 2026-08-21 01:40, 4503.70s

**28 commits, ~6.5 hours.** `git log a892df011..2c0ba712b`. That is the search space, and it is
small enough to bisect.

## Two hypotheses tested here and REJECTED, so the next reader does not re-run them

1. **Simplifications-store growth driving the pure-Python YAML scan** (the shape fixed for the
   *operational* suite at 0c63d3080). The store went **392 → 395 files across the whole window**
   (405 at HEAD) — no step change. And the gate runs `-m "not operational"`, so 0c63d3080 does
   not touch it either way.
2. **Draw-test cost.** `tests/background/test_forward_discovery_draw.py` runs in **2.57s** at
   HEAD.

Also observed, and it rules out the class already fixed: the in-flight gate (pid 2729053) is
**CPU-bound inside the Python process** — 773s user CPU over 957s elapsed, `state=R`, **zero
child processes**. The 198s defect of 104101496 was a *child* (`blocked_atom_visibility --check`).
This is not that.

## The second defect: two records of one quantity, and the bound reads the smaller

`GATE_SUITE_TIMEOUT_SECONDS = 3800` is **derived, not hand-set** — credit where due. It comes
from `measured_gate_timeout_floor()`, which reads `docs/observability/publish_gate_subject_cost.json`
and returns `worst phase x GATE_TIMEOUT_SAFETY_FACTOR`:

```
cold_checkout       1291.9
throwaway_checkout  1876.4   <- worst
in_tree_baseline    1428.3
implied_timeout_floor_2x = 3752   ->   3800, "the lowest round number above the floor"
```

That record carries **three phases, one observation each, and `complete: false`**. Meanwhile
`publish_gate_duration.jsonl` carries **147 substantive observations of the same quantity** —
the real gate, on the real subject, in production — and **no bound reads it.** Its own worst
case is 1666.0s against the cost record's 1876.4s, and its `cold_checkout` figure (1291.9s) is
the one that matches live reality.

The consequence is not that 3800 is wrong. It is that **the number that decides when a hung gate
is declared hung was derived from the record with 3 observations while the record with 147 sat
unread**, and that is why nobody — the director included — had the sentence "the gate takes 21
minutes" available to say. A ratio-shaped instrument was watching the budget; the absolute-number
verdict added at 317da079a fixed the *reporting* of this, correctly and against the publish
cadence. It did not change what the *bound* is derived from.

## What is NOT proposed, and why

**No production timeout is changed by this document.** That restraint is bought with evidence
from today: the first attempt at the director's *"put a limit on the absolute duration"* made
300s a real ceiling (9dc57daee) and **wedged publishing twice at `304.05s ceiling=300`** before
being reverted. `measured_gate_timeout_floor()`'s own docstring states the asymmetry — *"erring
high costs a longer wait on a genuinely hung gate; erring low wedges publishing"*. Lowering a
gate ceiling while publishing is in its 26th hour down would be that mistake a second time in
one day.

## Queued, in order

1. **Bisect `a892df011..2c0ba712b`** for the unbounded regression. This is the item that actually
   restores publishing; everything else is accounting.
2. **Admit the live pass distribution into `measured_gate_timeout_floor()`** — worst of *both*
   records, so 147 observations can raise the floor but the 3-phase record can still defend it.
   Strictly a widening, so it cannot wedge publishing, and it makes the ceiling responsive to the
   subject that actually runs. Owes an R15 mutation proving it fires on a fabricated fast row.
3. **A pass/timeout split in every duration surface.** A timeout row's `duration_seconds` is the
   ceiling, so any mean, median or trend that mixes the two is reporting the budget as if it were
   a measurement — the censoring defect this project already named in
   `feedback_a_bound_derived_from_completed_runs_is_derived_from_the_survivors_of_that_bound`.
   `row_cadence_band()` handles censoring for the cadence verdict; nothing does for the series.

## On the director's self-feeding question

*"each wedge makes a finding, each finding a control, each control more tests, and a slower gate
makes more wedges. If that's real, say so."*

**It is real and it is measurable, but it is not what broke publishing.** 104101496 put a number
on one instance (198s/cycle for a harness visibility check) and 92e5b380a removed 37 such files
from the blocking scope — 30 of them harness self-governance, i.e. tests about the gate, inside
the gate. That is the loop, observed. But the loop is *linear accretion*, and the 147-run record
shows it had reached only ~21 minutes by 2026-08-20. What happened on the night of 2026-08-20 is
a different thing with a different shape, and treating it as more accretion is what bought six
ceiling raises and 26 hours of outage.
