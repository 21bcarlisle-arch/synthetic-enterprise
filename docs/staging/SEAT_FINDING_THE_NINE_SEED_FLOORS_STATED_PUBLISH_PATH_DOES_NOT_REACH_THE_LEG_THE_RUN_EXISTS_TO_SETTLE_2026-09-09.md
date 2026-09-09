**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — resolve the selection leg by seeds because the ranking cut already names its sign)

# The nine-seed floor's stated publish path does not reach the leg the run exists to settle

**2026-09-09, scheduled tick.** The Lane 0 item is running a nine-seed noise floor
(`value_cycle_ab_s1_noise_floor_20260909b.json`, PID 704091, started 09:05Z, ~5 of 27 passes at
10:13Z) for one stated reason: **the selection leg is the thesis and it is unanswered for want of
seeds alone.** The item then states its own done-condition:

> Publishing is a file copy to the canonical `docs/observability/value_cycle_ab_s1_noise_floor.json`
> (that path, via `_seed_spreads` at `generate_value_arms_data.py:5956`, is what feeds
> `contrast_bounds`, so it is what satisfies this item's done)

That sentence is **true about `contrast_bounds` and false about the selection leg.** The two blocks
are fed by two different constants, and the selection leg is not on the canonical path. Copy the
nine-seed floor only to the canonical and the page publishes an n=9 headline bound beside a
selection leg still graded at n=3 — the run's entire purpose unserved, and the item marked done.

---

## The two feeds, poison-proven in both directions

Both blocks are computed by the same function, `_seed_spreads` (`tools/generate_value_arms_data.py:1353`),
applied to two different artefacts:

| Block | Fed from | Constant | Call site |
|---|---|---|---|
| `contrast_bounds` | `value_cycle_ab_s1_noise_floor.json` | `NOISE_FLOOR_PATH` (:192) | `build`, :6204 → :6240 |
| `current_world.bound`, `current_world.selection_leg` | `value_cycle_ab_s1_noise_floor_20260908.json` | `CURRENT_WORLD_NOISE_FLOOR_PATH` (:205) | `_current_world_bound`, :4629; `_leg_in_this_world`, :4825 |

Truncating each floor's seed rows to two in turn, through `build`'s own parameters (in memory —
nothing published), separates them cleanly:

```
baseline (canon=3, current=3)   contrast_bounds.seeds=3  selection_leg says n=3  bound.n=3
canon TRUNCATED to 2            contrast_bounds.seeds=2  selection_leg says n=3  bound.n=3
current-world TRUNCATED to 2    contrast_bounds.seeds=3  selection_leg says n=2  bound.n=2
```

Row 2 is the finding: **the canonical path moves `contrast_bounds` and moves nothing else.** Row 3
is the poison round that proves the probe can detect a change at all — without it, "the selection
leg did not move" and "the probe is blind" read identically.

## The page already carries two spreads for one quantity in one world

All four artefacts currently in play name the **same** world digest `39a192ce04c1eda8`
(`three_arm.json`, `three_arm_20260908.json`, `noise_floor.json`, `noise_floor_20260908.json`), and
both floors are `--redraw-mode all`. So the two blocks are two estimates of **one** population
quantity, and they disagree:

| | floor | generated | n | `value_advantage_gbp` stdev | mean |
|---|---|---|---|---|---|
| `contrast_bounds` | canonical | 2026-09-09T06:57:00Z | 3 | £1,457.33 | £18,918.51 |
| `current_world.bound` | `_20260908` | 2026-09-08T04:10:26Z | 3 | £1,522.47 | £19,015.45 |

£65.14 apart on the spread, £96.94 on the mean. Today both read `n=3`, both blocks publish their own
`floor_generated_at` / `world_measured_in`, and the verdict is `resolved: true` **under either
floor** — so the page is not currently lying and this is not a red. What the canonical-only publish
does is turn a disclosed disagreement between two same-size draws into an **undisclosed difference
of sample size on the page's most load-bearing number**, in the one direction that flatters: the
headline bound gets the nine seeds and the unresolved leg keeps the three.

## What done actually requires

The selection leg reaches n=9 only when `CURRENT_WORLD_NOISE_FLOOR_PATH` moves. The publish is
therefore **three pointers, decided together**, not one file copy:

1. `noise_floor_20260909b.json` → canonical `value_cycle_ab_s1_noise_floor.json` (`contrast_bounds`).
2. `CURRENT_WORLD_NOISE_FLOOR_PATH` → `..._20260909b.json` (the selection leg — **this is the item**).
3. `CURRENT_WORLD_THREE_ARM_PATH` → `three_arm_20260909b.json`, which a second lane is producing
   right now (PID 1265528, `/var/tmp/se-seat-executor/`, started 12:38Z).

**On the pair rule.** The comments at :190–:206 say moving one of `CURRENT_WORLD_THREE_ARM_PATH` /
`CURRENT_WORLD_NOISE_FLOOR_PATH` alone is the defect that pair exists to prevent — "the figure alone
republishes an unbounded headline, and the bound alone bounds the wrong run". Step 2 without step 3
is *not* that defect, and the distinction is worth stating rather than inferring: the prohibition is
against a floor from a **superseded world** or one **predating** the run it bounds. A 09-09b floor
is a later floor of the *same* world `39a192ce04c1eda8`, so it bounds the 09-08 00:19:54Z run
legitimately, exactly as the canonical 06:57Z floor already bounds the 09-09 01:24:34Z run today.
**Do not assert that — check it:** `_staleness_caveat` and the `world_identity.digest` equality are
the two gates, and if either refuses, `_seed_spreads` withholds all three bounds and the page says
so. If the three-arm partner is late, step 2 alone is available and settles the thesis; if its world
digest comes back anything other than `39a192ce04c1eda8`, none of the three moves and the run is a
measurement of a different world.

**Before any copy, check the artefact reconciles with itself.** `_seed_spreads` recomputes
`selection_gbp` spread from the seed rows and requires it to match the artefact's published
`selection_gbp_spread.stdev` within `SAME_SUPPLIER_TOLERANCE_GBP`; a disagreement withholds **all
three** contrasts, not the one that failed. A nine-seed floor that fails that check publishes
strictly less than the three-seed floor it replaced.

## Why BLOCKING

Clause 2, by construction: this document's own text says an instrument in this area is wrong. The
instrument is the item's done-criterion — it measures `contrast_bounds` and calls that the selection
leg. Left standing, the next tick to see the artefact land follows the stated recipe, publishes, and
records the thesis as settled at a sample size it never reached.

## What is next

Not this turn — the run has ~2h50m left at 12:56Z and this is a bounded tick, so the publish belongs
to whichever invocation finds the artefact on disk. What that invocation must not do is the
one-line copy. The three steps above, with the two gates checked and `python3 -m
tools.generate_value_arms_data` after, then grade the pre-registration against the page's real gate
(`spread_to_point_estimate_ratio >= 1`, per `docs/staging/records/SEAT_FINDING_THE_ERROR_BAR_CONTROL_AND_ITS_OWN_PREREGISTRATION_WERE_BOTH_GRADED_ON_A_QUANTITY_THE_PAGE_DOES_NOT_GATE_ON_2026-09-09.md`)
and never by hand — `_resolvable` rules.

The artefact is **not** gitignored and a floor artefact was eaten by `git clean -qfd` on 2026-09-03.
Commit it the moment it exists.
