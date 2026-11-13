**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The shared tree's residual refusers, named with their holders (2026-11-12)

*Delivery seat, LANE 0 draw `the-shared-trees-residual-refusers-are-cleared-or-named`, isolated executor worktree.*

## What the reconcile-watch pass says

The first passes that run bb10c3a5d's twin fix are on the log from 21:01Z. The last one read here is 23:33Z, run with origin's reconciler @8db2c25cc. It reads `NOT_ADVANCED`, and the shared tree is 64 behind origin with 0 ahead. The refusal names 1,478 blocking paths: 60 GENERATED, 1,394 MODIFIED and 24 UNTRACKED. The log line is cut at about 2,500 characters, so the held set that `advance_shared_tree` computes never reaches it. That is why the count reads the same from one pass to the next while nearly all of the paths are already proven lossless.

## The held set, measured at about 23:40Z

I ran origin's `advance_shared_tree` at 8db2c25cc against the shared tree with no writes. The remover, the restorer and the lock were injected to raise, and the run stopped at the stranded-caller step, before anything is cleared. Like the timer, it first tries the fast-forward, which git refused. Results:

- **1,478** blocking paths. **1,398** are proven lossless by the reconciler's own classes: tracked and untracked twins, earlier-revision twins, stale, generated, append-log, orphans and superseded. **4** are carried live edits: `background/origin_reconcile.py` and three staging findings. **0** are stranded.
- **76 held.** The advance is all or nothing, so these 76 alone keep the other 1,402 from clearing.
- This agrees with the separate dry run in `SEAT_FINDING_THE_81_PATHS_HOLDING_THE_SHARED_TREE_ARE_ONE_UNLANDED_ORIENTATION_AND_ONE_REFUSED_PUBLISH_2026-11-12.md`, done at 23:19Z against 6937b6089. That run held 76: 75 renders from a refused publish (B) and 1 retired finding (C). Nothing has changed since then.
- A separate hash census gives the same picture. Of 1,583 modified tracked paths on the shared tree, 1,315 hash equal to origin's blob.
- `background/live_payment_triad.py` is no longer held because it now equals origin. I did not touch it.

## What I cleared: nothing, and why

The item's clearing steps would not have advanced the tree, and they are not this seat's to take:

- **GENERATED.** The reconciler already proves all 60 resolvable, and it restores them itself when it advances. Restoring them by hand changes nothing while 76 other paths are held.
- **UNTRACKED orphans.** All 24 are resolved by the orphan class, which preserves each to a ref and then clears it. None is held.
- This seat runs in an isolated worktree. Writing to the shared tree from here would break the isolation it is licensed on. I left the 76 MODIFIED paths alone, as the item asks.

## Every remaining refuser and its holder

Holder check: I looked at every id in `.delivery_lane_claims.json` (2 live), `.seat_work_in_hand.json`, and the refusal and draw logs. None names any of the 76 paths. I also ran `git status` over the 76 paths in all 168 linked worktrees, and none of them has any of the paths dirty. **No live claim or worktree holds any of them.** What each one is comes from the 81-paths finding and from the mtimes below.

### B: an unlanded render of run 6fe7827ab2 (75 paths, written 11 Nov 16:26 to 16:34 UTC)

`docs/staging/done/run_complete_20261111T160541Z.md` says `Publish outcome: did not land`. Origin published the same run from a worktree at 20:31 (e816040ce). Origin carries every one of these paths.

- `docs/state/customer_sample.json` (11-11 16:34 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `docs/state/sim_data.json` (11-11 16:34 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/code/galaxy.png` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/OCC-e2ccfacff568.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/PROS-2016-0098.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/PROS-2016-0121g.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/PROS-2016-0207g.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/PROS-2017-0161.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/PROS-2017-0283.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/PROS-2017-0371g.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/PROS-2018-0137.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/PROS-2018-0222.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/PROS-2019-0246.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/PROS-2019-0261.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/PROS-2019-0261g.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/PROS-2019-0318g.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/PROS-2019-0363g.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/PROS-2020-0223g.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/PROS-2020-0321.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/PROS-2021-0322g.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/PROS-2023-0373g.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/SYN-2016-004g.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/SYN-2016-008g.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/SYN-2016-031.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/SYN-2016-034g.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/SYN-2016-037.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/SYN-2016-048.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/SYN-2016-048g.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/SYN-2016-059g.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/SYN-2016-086.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/SYN-2016-089.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/SYN-2016-091g.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/SYN-2016-094.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/SYN-2016-094g.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/SYN-2016-104.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/SYN-2016-142g.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/SYN-2016-183.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/SYN-2016-183g.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/SYN-2016-191.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/SYN-2016-191g.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/SYN-2016-217.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/SYN-2016-237.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/SYN-2016-253g.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/SYN-2016-256g.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/SYN-2016-269.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/SYN-2016-291g.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/SYN-2016-298.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/SYN-2016-302g.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/SYN-2016-323.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/SYN-2016-352.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/SYN-2016-358g.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/SYN-2016-361.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/SYN-2016-363.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/SYN-2016-363g.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/SYN-2016-376g.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/SYN-2016-380.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/SYN-2016-398.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/SYN-2016-404g.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/SYN-2016-406.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/SYN-2016-418g.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/SYN-2016-420.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/SYN-2016-460.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/SYN-2016-499g.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/SYN-2016-504.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/SYN-2016-525.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/SYN-2016-528.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/SYN-2016-528g.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/SYN-2016-536.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/SYN-2016-536g.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/SYN-2016-538.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/SYN-2016-538g.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/SYN-2016-546.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/SYN-2016-558.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/customers/SYN-2016-573.json` (11-11 16:26 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2
- `site/data/director_delta.json` (11-11 16:31 UTC, origin-has): no holder, a refused publish render of 6fe7827ab2

### C: the retired 205-of-238 finding (1 path)

- `docs/staging/WORKER_FINDING_205_OF_238_REFUNDS_ON_THE_068B5E3CC8_PAGES_PAY_PAST_THE_CREDIT_THE_PAGE_PRINTS_2026-11-11.md` (11-11 11:07 UTC, origin-lacks; origin moved it to `done/` in 63ede2e3b with every line of this copy): no holder

## Next

Nobody is holding any of these paths. Landing them would be wrong: each B path is an earlier render of a publish that origin already carries, and C is retired. Reverting them by hand is also wrong, because nothing licenses this seat to write to the shared tree. The tree advances once the reconciler has a class for each group, which is the build the 81-paths finding already handed on as `the-refused-publish-render-and-the-moved-retired-finding-get-reconciler-classes`. Two smaller defects came out of this run:

1. The reconcile-watch line is cut before the held set, so the log shows 1,478 refusers when the actual count is 76. The rendered refusal should put `held` ahead of the per-kind remedy text.
2. Because of that, this item's request to clear the GENERATED and UNTRACKED classes by hand was built on the per-kind text. The reconciler resolves both classes itself.
