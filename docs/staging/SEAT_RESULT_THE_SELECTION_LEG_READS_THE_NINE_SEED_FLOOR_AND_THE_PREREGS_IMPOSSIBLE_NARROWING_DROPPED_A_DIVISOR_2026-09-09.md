**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — `land-the-nine-seed-floor-by-the-three-pointer-recipe-and-own-it-to-the-rendered-selection-leg`) · **Class:** measurements_that_mirror

# RESULT — the selection leg reads the nine-seed floor, and the pre-registration's "arithmetically impossible" narrowing dropped a divisor

Graded against `docs/staging/records/SEAT_PREREGISTRATION_WHAT_THE_NINE_SEED_PAIR_MOVE_PUBLISHES_AND_WHICH_OF_ITS_LEGS_ARE_DECIDED_ALREADY_2026-09-09.md`,
which was landed at `3e85fefe3` **before the nine-seed floor existed**. Two of its claims are
refuted and both refutations are in the same sentence of it.

## What was drawn, and what was actually left to do

The item named three pointers. Measured against `origin/main` this tick rather than assumed:

| # | Pointer | State at draw |
|---|---|---|
| 1 | `three_arm_20260909c.json` → `THREE_ARM_PATH` | **not needed** — `method_skill.fixed_horizon.leg_conditioning` is already `true` on the canonical path's current run |
| 2 | `noise_floor_20260909b.json` → `NOISE_FLOOR_PATH` | **already landed** — canonical floor is byte-identical to the nine-seed artefact, `contrast_bounds.seeds` already 9 |
| 3 | `CURRENT_WORLD_NOISE_FLOOR_PATH` → the nine-seed floor | **live, and the whole defect** |

The previous tick recorded that no `20260909c` artefact "exists anywhere in the repo". It exists on
`origin/main`; that tree was 14 behind when it looked. The instance was wrong, the refusal to land
from a stale tree was right.

## The defect, stated as what a reader met

`current_world.selection_leg` — whether our advantage is per-customer **selection** or **level**,
which is the whole claim this company makes — was reading a **3-draw** floor while `contrast_bounds`
a few lines away already read the **9-draw** one. Two blocks on one page answering one question at
two sample sizes, with the wider-sampled one in the flattering position.

## What landed

One constant. `CURRENT_WORLD_NOISE_FLOOR_PATH` → `value_cycle_ab_s1_noise_floor_20260909b.json`,
and the feed regenerated. **No promote-by-copy**: nothing was copied onto a dated path, so the
census class three origin commits exist to catch is not entered.

The leg **still states no direction**, and that is the outcome, not a failure to land one — at n=9
the family runs −3,036.25 to +1,260.93, 5 of 9 re-draws clear the bound, and it still falls on both
sides of zero. What the move buys is that **the refusal now names the sample the rest of the page is
already using**. A refusal at n=9 and a refusal at n=3 are not the same refusal.

Nothing was lost: no field added or removed by the regenerate, and the headline and level legs both
go 3 → 9 re-draws with **all 9 resolving**, so no figure on the page loses its stated direction
(R6, R7 hold). R4's poison round is what makes this attributable — steps 1+2 alone leave the leg at
n=3; only the constant move takes it to 9.

## Refutation 1 — the pre-registration's floor, and why its conclusion survived by luck

`8b846013e` derived that the three retained seeds pin the n=9 stdev from below at **£1,145.99**, and
the pre-registration stated that a narrower spread at n=9 than at n=3 "would be **arithmetically
impossible** and would itself be the finding".

Observed: **n=9 stdev 1,810.50 against n=3's 2,279.22 — narrower by 468.72.**

Wrong twice, and the second error is the one worth keeping:

1. **The retained seeds did not retain their values.** The two floors were produced by different
   commits — `04361d6c7` and `c066c114b` — and the same seed in the same world returns a different
   `selection_gbp` under each (11111 +61.38, 22222 +38.96, 33333 +61.38).
2. **The step from "the sum of squared deviations can only grow" to "the standard deviation can only
   grow" drops the divisor.** Measured on the nine-seed run's *own* values, so "retained" is exact:

   | over | SSD | n−1 | stdev |
   |---|---|---|---|
   | the 3 retained seeds | 10,506,369.5 | 2 | 2,291.98 |
   | all 9 seeds | 26,223,304.5 | 8 | **1,810.50** |

   The SSD grew by 15.7m, exactly as derived. The stdev **fell** by 481.48, because the divisor grew
   2 → 8.

1,810.50 > 1,145.99, so the derived bound holds — **but nothing in the derivation made it hold.** A
control keyed to that bound would have passed for years while its reason was false. This is the
catalogue shape *a surviving prediction whose mechanism is wrong*, and it is only visible because
the prediction was written down before the floor existed.

## Refutation 2 — the pair that "must move together" is not symmetric

The constant's own comment says moving either half alone is the defect, *in both directions*. It is
the defect in **one** of them. "The figure alone republishes an unbounded headline" is about
`CURRENT_WORLD_THREE_ARM_PATH`, which does not move here. "The bound alone bounds the wrong run"
means a floor drawn over a **different world** — and both floors carry digest `39a192ce04c1eda8`,
the bounded arms' own world.

**What the move is not innocent of, admitted at the constant rather than in a footnote:** the arms
being bounded are `04361d6c7`'s and the floor is `c066c114b`'s, so the spread carries a code-tree
difference the figure it bounds does not. It cannot be removed without re-running the arms. Judged
tolerable at ~1% of a 4,297.18 spread whose only verdict is *does this family cross zero* — a
60-unit shift cannot move that. If the arms are re-run, the pair should move together again.

## What is NOT done, and the exact reason

**The checkout is still 14 behind / 7 ahead.** `background/origin_reconcile` was run and refused:
`REFUSED_CONFLICT` on exactly two paths, `site/capabilities/index.html` and
`site/data/value_arms.json`. This is the third tick that refusal has blocked, and it has been
reported each time as a path count. It is not a path count. Diagnosed:

**Two lanes built the same block.** Local `b16281092` (+97 lines) and origin `2df665040` (+36) both
render `fixed_horizon.pair_strata`, both inserted at the same anchor immediately after
`verdict(fh.reading_of_the_estimand)`. They are **rival implementations of one feature**, not two
additive edits, so "keep both" is not available and "take one side" is a judgement about which page
a reader gets:

- **local** — a full `pairStrataBlock()` with a three-row table (within-settled / tie mass / cross),
  rank, comparable pairs and decision pairs, plus `computed_by` and
  `the_interval_these_terms_carry`. It renders the tie mass as *"no comparable pair"* rather than a
  dash or a zero, which are opposite readings.
- **origin** — an inline paragraph rendering `reading` only, amber keyed on
  `the_stratum_that_carries_the_departure === "cross"`, plus `derived_by_identity_here`.

**The hazard, measured against origin's live feed rather than argued from the two descriptions.**
Origin's feed carries `strata` with all three rows, so local's table would render — but it carries
**no `computed_by`**, and local's block guards `the_interval_these_terms_carry` and *does not guard
`computed_by`*. Taking the local side unaltered publishes

> Attributed by **undefined**.

on the Capabilities page. One line, and the wrong kind of thing to find out from the live site. Any
resolution taking the local renderer must guard that field or confirm the merged producer emits it.

**Recorded as a correction to my own first reading:** I suspected origin's amber branch was
unreachable because its producer's quoted literals do not include
`the_stratum_that_carries_the_departure`. The published feed carries it, set to `"cross"`. The
branch fires. A grep for a field name in the producer is blind to a field assembled anywhere else —
the feed is the only place to ask.

## Pre-existing red, named so the next tick does not re-diagnose it

`tests/tools/test_the_value_arms_pages_undriven_pointers.py` has 3 failures at
`_current_world_bound`. Present at `origin/main` `bf929f77f` as line **4613**, reported after this
change as **4642** — the same branch, shifted by the 29 comment lines this commit adds. Proven in a
clean extract of `origin/main` before the change was made, not inferred from the line numbers.
