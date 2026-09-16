**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# FINDING — the pair move's named run path holds a superseded copy, and its AUCs are not the ones the item quotes

LATENT rather than BLOCKING: nothing on the page is wrong today and no control refuses. It fires on
the FIRST execution of the pair move as written — which is the work this item exists to do, and
which was ~4 hours from being possible when the defect was found.

**Filed:** 2026-09-10, scheduled tick, delivery seat. Continues
`pair-move-the-20260910-run-and-its-floor-so-the-independent-grading-reaches-the-page`. The claim is
**not released**: the pair move is still owed. What is refuted is its stated *path*, not its purpose.

---

## The premise is not spent, but the tick could not do the work

The item's own precondition is "when `longjob-noise-floor-20260910` finishes". It has not.

```
PID 1072649  started Thu 2026-09-10 14:50:22Z  elapsed 43:09  (at 15:33Z)
  python3 -m tools.run_value_cycle_ab
    --noise-floor-seeds 11111,22222,33333,44444,55555,66666,77777,88888,99999
    --redraw-mode all --out docs/observability/value_cycle_ab_s1_noise_floor_20260910.json
  cwd=/var/tmp/se-floorrun-20260910   (worktree pinned at 4e7938f67, locked)
```

Alive and healthy — 27MB of log, mtime current, `launch_liveness --check` PASS with no stale claim.
43 minutes into a ~5h/27-pass run, so roughly 4h15m remained. The artefact
`/var/tmp/se-floorrun-20260910/docs/observability/value_cycle_ab_s1_noise_floor_20260910.json` does
not exist yet. A bounded tick cannot wait for it, and the run must not be disturbed.

Both commits the item cites (`32f6e70ba`, `4e7938f67`) are ancestors of `origin/main`, as the draw's
premise check said — but they are cited as *dependencies already landed*, not as work to do. On that
reading the premise is intact.

## The defect: the path the item names does not hold the run the item describes

The instruction is a file copy:

> copy BOTH `docs/observability/value_cycle_ab_s1_three_arm_20260910.json` ->
> `value_cycle_ab_s1_three_arm.json` AND the new floor -> `value_cycle_ab_s1_noise_floor.json`

That path exists in this tree. It is **not** the run the item is about. There are two artefacts
wearing one name:

| | `generated_at` | `producing_commit` | blob |
|---|---|---|---|
| landed at `origin/main` (in `4e7938f67`) | `2026-09-10T14:04:08Z` | `9cf9d16ed` | `c9170e174` (195,710 B) |
| on this tree's disk at that path | `2026-09-10T13:00:14Z` | `8dd060194` | `73d076662` (198,509 B) |

The item quotes **AUC 0.6237 against the control arm's outcomes, vs 0.6148 against the value arm's
own**. Those are the landed copy's figures, and only its:

```
ORIGIN (14:04Z, 9cf9d16ed)   discrimination_auc = 0.6236502960640892  -> 0.6237  ✓
                             belief_vs_outcome  = 0.6147812971342383  -> 0.6148  ✓
DISK   (13:00Z, 8dd060194)   discrimination_auc = 0.6250435388366423  -> 0.6250  ✗
                             belief_vs_outcome  = 0.6162895927601810  -> 0.6163  ✗
```

`cp` from the named path therefore promotes the 13:00Z run to canonical while every sentence written
about it — in the item, and in the prose already landed for the render half — describes the 14:04Z
one. The two also disagree structurally, not just in the fourth decimal:
`cross_section_reconciliation` is `available: false` in the landed copy ("predates the `population`
block") and `available: true` on disk; `distinct_margins` is 74 vs 73 on the value arm and 140 vs 139
on the level arm; every arm total differs (`control_arm.total_net_gbp` £147,954.26 vs £147,886.78).

This is the rival-copy class again, and the tell was cheap: the item's own quoted numbers did not
reproduce from the file it told me to copy.

## The second hazard: this tree is 11 behind origin, on exactly these paths

```
git rev-list --count HEAD..origin/main = 11        (HEAD = 4b3d531bc)
git rev-list --count origin/main..HEAD = 6         (diverged, not a fast-forward)
```

Those 11 are not elsewhere in the tree — they land on the pair move's own surface:

```
docs/observability/value_cycle_ab_s1_three_arm_20260910.json | 4883 ++++++  (the run, landed)
site/data/value_arms.json                                    |  509 +-
tests/tools/test_generate_value_arms_data.py                 |  208 +-
tools/generate_value_arms_data.py                            |  441 +-
```

So "re-run `python3 -m tools.generate_value_arms_data` and land run+floor+`site/data/value_arms.json`
in ONE commit" from this tree regenerates the feed with a producer **11 commits stale** and lands it
over the current one — an atomic revert of 441 lines of producer, 208 of control and 509 of feed,
wearing a commit message about promoting a run. The regenerate-and-land-in-one-commit shape is only
safe from a tree at `origin/main`.

## The third hazard: a rival nine-seed floor is in flight, and it has the arm this one lacks

```
PID 1146711  started 15:06:44Z  cwd=/home/rich/synthetic-enterprise   (the SHARED tree)
  python3 -m tools.run_value_cycle_ab --level-arm --redraw-mode all
    --out .../value_cycle_ab_s1_noise_floor_20260910b.json
    --noise-floor-seeds 111111,222222,333333,444444,555555,666666,777777,888888,999999
```

`launch_liveness` reports `arms-rerun-20260910b: RUNNING`. Two nine-seed `--redraw-mode all` floors
are being produced at once, on disjoint seed sets, and **the drawn one has no `--level-arm` while the
rival does**. The already-filed
`SEAT_FINDING_THE_PUBLISHERS_OWN_REMEDY_CANNOT_CLEAR_ITS_OWN_REFUSAL_AND_THE_REPLACEMENT_RUN_HAS_NO_LEVEL_ARM_2026-09-08`
is the same shape. Whichever floor reaches canonical decides whether the level-share leg has a floor
of its own; the drawn one cannot serve it. Neither run has been disturbed by this tick.

Note also that the canonical floor is already nine seeds
(`value_cycle_ab_s1_noise_floor.json`, `generated_at 2026-09-09T15:17:31Z`, 9 seed rows), so the
trade the item describes is n=9-at-09-09 against n=9-at-09-10, not n=3 against n=9.

## What the pair move should do instead

1. Bring the tree to `origin/main` first — the 11 include the run's own landing and the producer the
   feed must be built by. Not from a tree 11 behind.
2. Take the run's bytes from `origin/main:docs/observability/value_cycle_ab_s1_three_arm_20260910.json`
   (blob `c9170e174`), **never** from the working-tree copy at that path. It is already committed, so
   the canonical promote is a blob copy, not a file copy.
3. Confirm the promoted copy reproduces `0.6237` / `0.6148` before regenerating, as the one cheap
   check that separates the two runs.
4. Decide between the two floors on whether the level-share leg needs one, not on which finishes
   first.
5. Only then regenerate and land — and recall that the canonical floor path feeds `contrast_bounds`
   alone; the selection leg reads `CURRENT_WORLD_NOISE_FLOOR_PATH`, per
   `SEAT_FINDING_THE_NINE_SEED_FLOORS_STATED_PUBLISH_PATH_DOES_NOT_REACH_THE_LEG_THE_RUN_EXISTS_TO_SETTLE_2026-09-09`,
   which is still unanswered.

## What is next

The pair move remains owed and the claim stays held. Its input lands roughly 19:50Z; the tick that
picks it up should start from `origin/main`, not from this tree, and should read this file before the
copy.
