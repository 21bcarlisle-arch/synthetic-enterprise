# WORKER DISPOSITION — the 22222 relaunch was drawn by the tick while its holder already had it running

**Severity:** RECORDED · **Lane:** H_harness · **Claim:** `relaunch-22222-alone-on-the-box-and-grade-five-seeds`, which is held in `.seat_work_in_hand.json` under the same id

## What the tick found, read at 20:49Z on 2026-09-29

- `longjob-ab5-runa2c.service` was already running: pid 1592398, started 21:49 local. It runs `python3 -m tools.run_value_cycle_ab --level-arm --noise-floor-seeds 22222,33333 --out /var/tmp/se-ab5-out/runA2.json` with its cwd in the pinned worktree `/var/tmp/se-ab5-b79e2c0e8`. Its log is `/var/tmp/se-ab5-out/runA2c.log`, and it prints the weather digest at leg start as `e11451b5…d242`, which is the prereg's.
- It was launched by the isolated seat session that holds the claim (pid 1588939). A second tick worker (pid 1593197) drew the same item at the same moment.
- No other full-window run was resident. Available memory was 19G.

## Disposition

**Not launched.** A second copy alongside `runa2c` would recreate the memory contention that killed `runa2b`. That is the one thing this item exists to prevent.

**Claim not released.** The claim belongs to its holder. Releasing it would return in-flight work to the pool.

The "Relaunch of 22222" note for `runa2c`, and increment 3 when `runA2.json` lands, are the holder's to write.
