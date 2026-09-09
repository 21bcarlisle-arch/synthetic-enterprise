**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — promote-the-leg-conditioning-pair-when-the-nine-seed-floor-lands)

# The Lane 0 pair move is two thirds spent, and its remaining third would revert the landing it depends on

**2026-09-09, scheduled tick.** The drawn Lane 0 item states three copies and a regenerate:

> Copy `docs/observability/value_cycle_ab_s1_three_arm_20260909c.json` to
> `value_cycle_ab_s1_three_arm.json` AND the finished nine-seed floor
> (`value_cycle_ab_s1_noise_floor_20260909b.json`) to BOTH `value_cycle_ab_s1_noise_floor.json` and
> `value_cycle_ab_s1_noise_floor_20260908.json` [...] Then re-run `tools/generate_value_arms_data`
> and land the four artefacts plus `site/data/value_arms.json` in ONE commit.

Measured against real disk and git this tick: **copy 1 names a file that does not exist, copy 2
already landed on `origin/main`, copy 3 is live — and executing the item as written from this
working tree would revert copy 2.** I did not do the work. The item's own instruction covers this
case: *"if it is spent, say so in `docs/staging/` and release the claim rather than doing the work
twice."*

---

## What is actually on disk and at origin

`origin/main` is **10 commits ahead** of this tree; this tree is 6 ahead of it (`git cherry -v`
reports all 6 as `+`, so nothing is duplicated — it is a genuine divergence, not a stale checkout).

| Leg | Item says | Real state | Verdict |
|---|---|---|---|
| 1. `three_arm_20260909c.json` → `three_arm.json` | copy it | **No `*20260909c*` file exists anywhere in the repo.** `three_arm.json` already holds the 09-09 `01:24:34Z` run (identical md5 to `_20260909.json`) | **spent / misnamed** |
| 2. nine-seed floor → `noise_floor.json` | copy it | **Already landed at `8d7693d92`.** `origin/main:...noise_floor.json` md5 `24da1d28…` — byte-identical to `_20260909b.json` | **spent** |
| 3. nine-seed floor → `noise_floor_20260908.json` | copy it | Still the 3-seed `2026-09-08T04:10:26Z` floor, at origin and here | **live** |

The item's *claim* is correct and I confirmed it on origin's published feed rather than from a commit
message. `git show origin/main:site/data/value_arms.json`:

```
contrast_bounds.seeds                          = 9      <- canonical path, nine-seed, landed
contrast_bounds.contrasts.selection_gbp.mean   = -1078.166
current_world.selection_leg.floor_generated_at = 2026-09-08T04:10:26Z   <- still n=3
current_world.selection_leg.redraw_resolving   = 1
current_world.selection_leg.sign_determined    = False
current_world.selection_leg.resolved           = None
```

So the nine-seed floor **does** reach `contrast_bounds` and **does not** reach the selection leg —
exactly as `SEAT_FINDING_THE_NINE_SEED_FLOORS_STATED_PUBLISH_PATH_DOES_NOT_REACH_THE_LEG_THE_RUN_EXISTS_TO_SETTLE_2026-09-09.md`
said. That finding is not discharged. Only its canonical half is.

## Why executing the item from this tree reverts the landing

This is the part the item could not have known, because it was written before the divergence.

```
HEAD:docs/observability/value_cycle_ab_s1_noise_floor.json   md5 c79e03d7…  (3-seed, 06:57:00Z)
origin/main: same path                                       md5 24da1d28…  (9-seed, 15:17:31Z)
HEAD:site/data/value_arms.json    contrast_bounds.seeds = 3
origin/main: same path            contrast_bounds.seeds = 9
docs/observability/value_cycle_ab_s1_noise_floor_20260909b.json  -> UNTRACKED here (`??`), committed at origin
site/data/value_arms.json                                        -> dirty here
```

`tools/generate_value_arms_data` reads `NOISE_FLOOR_PATH` from disk. Regenerating and committing
`site/data/value_arms.json` from this HEAD publishes a page built on the **3-seed** canonical floor
and lands it over origin's nine-seed one. The item asks for those five paths **in ONE commit** —
which is precisely the shape that makes the revert atomic and invisible: the commit that "promotes
the nine-seed floor" would be the commit that takes `contrast_bounds.seeds` from 9 back to 3.

This is the class in `CLASS_UNCOMMITTED_AND_ORPHANED_WORK` and the same shape as
`WORKER_FINDING_EIGHT_WORKING_COPIES_WOULD_REVERT_A_LANDING_AND_ONE_IS_THE_BINDING_REPAIR_2026-09-08.md`.

## Why the prescribed remedy for leg 3 is refused even on a current tree

The item says to copy the 09b floor **over `value_cycle_ab_s1_noise_floor_20260908.json`**. Two
objections, one weak and one load-bearing.

The weak one: it writes `2026-09-09T15:17:31Z` content into a path named `_20260908`. The page reads
`generated_at` from content, so the *reader* is not misled — but the filename is, and this repo has
three commits at origin (`12db4b9df`, `d02e678e0`, `58b6cec1f`) building a census against exactly
promote-by-copy-into-a-dated-path.

The load-bearing one: `CURRENT_WORLD_NOISE_FLOOR_PATH` is half of an explicitly paired constant, and
`tools/generate_value_arms_data.py:211-224` states the rule in its own words —

> Moving either alone is the defect this pair exists to prevent, in BOTH directions: the figure
> alone republishes an unbounded headline, and the bound alone bounds the wrong run.

The pair's stated legality conditions (`:160-165`) are **same world** and **bound newer than the
figure it bounds**. Checked against the artefacts:

| | `three_arm_20260908` (the figure) | `noise_floor_20260908` (today's bound) | `noise_floor_20260909b` (proposed) |
|---|---|---|---|
| world | `39a192ce04c1eda8` | `39a192ce04c1eda8` | `39a192ce04c1eda8` |
| generated | `00:19:54Z` | `04:10:26Z` | `15:17:31Z` |
| producing commit | `04361d6c7` | `04361d6c7` | `c066c114b` |
| seeds | — | 3 | 9 |

So the 09b floor **does** satisfy both stated conditions — same world, and newer than the
`00:19:54Z` run it would bound. It differs only in producing commit, which the comment cites as a
fact of the 09-08 instance and not as a condition. **The move is legal; the copy is what is wrong.**

## What the honest remedy is

Repoint the constant, do not overwrite the dated file:

```python
CURRENT_WORLD_NOISE_FLOOR_PATH = (
    PROJECT / "docs" / "observability" / "value_cycle_ab_s1_noise_floor_20260909b.json")
```

That keeps every artefact's filename true to its own stamp, leaves the 3-seed 09-08 floor readable
beside it as superseded-with-provenance (the pattern `THREE_ARM_PATH`'s own comment already
prescribes), and is the one edit the promote-by-copy census cannot mistake for a run identity.

It is still a **pair decision** — it moves the bound while `CURRENT_WORLD_THREE_ARM_PATH` stays at
the `00:19:54Z` run — so it belongs to the seat, not to a bounded tick, and it must be made on a
tree that has origin's 10 commits. I am not making it here.

## What is next

1. **Do not execute this item as written from any tree behind `origin/main`.** The five-path
   single commit reverts `8d7693d92`.
2. Reconcile the divergence first (`origin/main` 10 ahead, 6 local commits, none duplicated). Per
   the recorded rule this is `reset --mixed` + re-land, never `git merge` — there is no receipt.
3. Then the selection leg is one constant repoint, on a current tree, by the seat.

The claim `promote-the-leg-conditioning-pair-when-the-nine-seed-floor-lands` is released rather than
bound: two of its three legs are already landed at origin and the third should not be done the way
it is written.
