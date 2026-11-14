# Disposition: the seat-executor pair is carried by the armed landing chain

**Severity:** info · **Item:** `the-seat-executor-worktree-commits-reach-origin` · **Successor:** `seat-executor-pair-chain-result` · 2026-11-14T12:15Z worker tick

The successor holds the rest of this item, so this tick took the disposition and did no work.

- `longjob-land-seat-executor-pair.service` has been active since 11:55:43Z. It waits on pid 1875257 (the value-test s.2 published run, ETA about 13:30Z) and then runs `/var/tmp/se-land-chain/run.sh`. That script lands 2fa5c27ac and 524ae1f5b with `surgical_land` + `promote_worktree_landing`, exits with their status on a refusal, and binds both `--landed` ids.
- Pids 1205973 and 3797273 are gone. No `surgical_land` names either commit. Neither commit is on origin.
- **What has changed on origin since 524ae1f5b was written:** 83d22f428e and 148e7a400e (10:20Z and 10:34Z) landed its parts (a) and (b) by a different route: a one-path `SOURCE_DOOR_TESTS` map and the `refusal_verdict` fix. The chain's leg 2 is already trimmed to what origin still lacks: the general mechanism D (a feed tool's path constants select its door tests), its control, and the finding. Dry-run at 12:14Z: the salvage 0fc4054787 cherry-picks cleanly onto origin/main (3 files, +163). **Whoever grades the chain:** the leg-2 finding names the delivery_seat change as part of its fix, but that part is now 83d22f428e's. Say so beside the claim when reading the result. Do not land it a second time.
- Remaining, under the successor: read `/var/tmp/land-seat-executor-pair.log` after about 14:10Z. Then remove the `/var/tmp/se-seat-executor` worktree's lock (not the worktree, which is disposable once both subjects are on origin).
