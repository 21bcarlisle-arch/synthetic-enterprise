# Worker disposition: the 22222 relaunch-and-grade was drawn by the tick while the seat waits on the leg

**Severity:** RECORDED · **Lane:** H_harness · **Claim:** `relaunch-22222-alone-on-the-box-and-grade-five-seeds`

*Tick worker, 2026-09-29 22:30Z. Item `relaunch-22222-alone-on-the-box-and-grade-five-seeds`.*

**Nothing done. No claim touched.** This is the seat's work, and the seat is doing it now.

- **The relaunch half is landed.** `a95fe01ec` records the kernel's reading of the 19:07Z OOM and relaunch 3, unit `longjob-ab5-runa2c`, launched 20:49:13Z.
- **The grading half is in flight, with its holder.**
  - The leg is pid 1592398 (`run_value_cycle_ab --level-arm --noise-floor-seeds 22222,33333 --out /var/tmp/se-ab5-out/runA2.json`). At 22:29Z it had run 1h40m at 6.5 GiB rss, against the ~1h50m it needs.
  - A delivery seat (claude pid 1859704) drew this id at 22:27:13Z. That time is the `claimed_at` in both `.delivery_lane_claims.json` and `.seat_work_in_hand.json`, so it is one claim, not two. The seat is blocked in `tools.wait_for --pid 1592398` with the subject "…whose runA2.json increment 3 grades".
  - `/var/tmp/se-ab5-out/replicate33333.py` was written at 22:20Z to grade the pre-registered 33333 replicate.
- **Why no `--release`:** it marks the item *finished*. Increment 3 is still owed, and the seat's own `--landed` and `--release` close it.
- **Why no `--premise-spent`:** the premise is not spent. `runA2.json` does not exist yet.
- **Also queued:** `longjob-pb6-eh2-rerun-repaired-world` waits on the same pid (wait_for pid 1677300). That matches the successor `pb6-eh2-grade-the-repaired-world-arms`.

The draw fired on an id whose live claim was 25 seconds old, the "draw's own write" shape. `ps` settled it: a rival seat process was live and waiting on the subject.
