**Severity:** LATENT · **Lane:** delivery seat (lane 0) · **Item:** `land10-gates-before-b11m7s-first-wave-not-beside-it`

# The post-rankq box order: rankq, book, land10 gate, B11 M7 waves, census (2026-11-24)

This is the one place a later tick reads the order from. Two armed jobs fired on the same artefact, the first
`docs/reports/run_output_*.json` after rankq ends: **land10** (`/var/tmp/se-msc-keep/land10.sh`, the MSC
replacement-win landing, a full pre-commit gate) and **b11m7-watch** (`/var/tmp/box-plan/b11m7/arm.sh`, two waves
of three 80-minute `seed_family` members). Started together, they reproduce the 3600 s gate timeout, the
co-residence failure MSC has already hit nine times, and they skew the six M7 books' timing.

## The order

| # | Job | Starts when | Keyed on |
|---|---|---|---|
| 1 | rankq (`longjob-value-test-s12g-rankq`, pid 1718464 / child 1718490) | running | — |
| 2 | sim-runner's owed book | sim-runner's own schedule | — |
| 3 | **land10 gate** | rankq's unit inactive, then a `run_output_<sha>_*.json` descending from 31bf40e03 and newer than `/var/tmp/se-msc-land10-armed.stamp`, then `busy()` clear | artefacts (unchanged from land10's design) |
| 4 | **B11 M7 waves** (61113-61115, then 61116-61118) | rankq's pid gone, the first book after `.rankq_ended` (or 6 h), **then land10's end file** | `/var/tmp/se-msc-land10-ended.txt` **newer than** `/var/tmp/b11m7/.rankq_ended` |
| 5 | HEAD-green census (`head-green-census.timer`, nightly ~03:32Z) | its timer, admitted by memory | **not ordered** (see Gaps) |
| 6 | **A4, EP1's dated rate as a value arm** (`longjob-a4-ep1-dated-rate-value-arm`, `/var/tmp/vte-driver/run_ep1.sh`, added 24 Nov ~20:40Z) | B11 M7's `/var/tmp/b11m7/readout.json` exists, then no land10 / seed_family / census / value-test unit live (5-min polls); refuses at 96 h | `SEAT_PREREG_A4_EP1_DATED_RATE_AS_A_VALUE_ARM_2026-11-24.md` |

**Why land10 goes before M7:** the gate takes one or two hours, and the waves take two 80-minute rounds. MSC has
failed nine times on co-residence and races. M7's grade is not waiting on anything downstream, so giving the gate
the quiet box first costs M7 one or two hours. Putting the gate second would expose it to a third round of races.

## What changed (24 Nov ~18:47-18:50Z)

- **b11m7 keys on land10.** New step 2b in `arm.sh` calls `/var/tmp/box-plan/b11m7/wait_land10.sh`. It returns 0
  when land10's end file is newer than `.rankq_ended`. A file written by a stop before rankq ended does not count,
  and the 18:48:14Z re-arm wrote one (`exit 1`). It also returns 0 if land10's unit has not been live for two polls
  (died without its trap, so nothing is gating). It **refuses with exit 5** after 24 h with land10 still live, so a
  wave never starts beside the gate. Dry-run on fakes in `/tmp/b11wait`: refuse rc=5, ended-after rc=0, dead unit rc=0.
  The pin (`16e8323701`, `/var/tmp/b11m7-tree`) is unchanged.
- **land10's `busy()` sees the waves.** It now also asks `longjob-seed-family*` units, `-m tools[.]seed_family
  launch` and `head-green-census.service`. This is a belt in case b11m7's wait is bypassed. It is still the 12 h
  re-ask, so a stray argv match cannot end the attempt. Base `31bf40e03`, `msc8.patch` and the arming stamp are
  unchanged. `pgrep` was checked against a fake `seed_family launch` argv, and the systemd globs were checked
  against live units (match 0, no match 4).
- **land10 re-armed** through `launch_long_job` with `--wait-for-pid 1718490`. A fresh admission refuses 6 GB
  beside rankq's 11.8 GB, and the original arming predates that. The script's first wait is on rankq anyway.
- **`land10-redeadline.service`** (`/var/tmp/se-msc-keep/land10_redeadline.sh`). The wrapper's pid wait has a fixed
  21600 s deadline (to about 00:48Z), and rankq had about 6 h left at 18:50Z (2016-2021 took 9.2 h). If that
  deadline fires, land10.sh never runs. This watcher re-arms it (up to 4 times) and exits 0 once land10.sh has
  logged. Dry-run on fakes: both branches fire.

## How to reverse

- b11m7: `systemctl --user stop b11m7-watch`; `cp -p /var/tmp/box-plan/b11m7/arm.sh.before-land10-order
  /var/tmp/box-plan/b11m7/arm.sh`; re-arm with `systemd-run --user --unit b11m7-watch -p
  WorkingDirectory=/var/tmp/b11m7-tree /bin/bash /var/tmp/box-plan/b11m7/arm.sh`.
- land10: `systemctl --user stop land10-redeadline longjob-land10-msc-replacement-win-artefact-waits`; `cp -p
  /var/tmp/se-msc-keep/land10.sh.before-b11m7-order /var/tmp/se-msc-keep/land10.sh`; re-arm with
  `WAITPID=1718490 bash /var/tmp/se-msc-keep/land10_rearm.sh` (drop `WAITPID` once rankq has gone).

## Gaps

- **The census is not ordered.** `head_green_census` queues on the memory governor, not on land10 or M7. land10
  will not *start* its gate while the census runs, but the census can start *during* the gate or a wave if memory
  allows. If rankq ends near 01:00Z and the book follows within an hour or two, the gate overlaps 03:32Z. One way to
  enforce it: `python3 -m background.tick_mode` or a one-night skip of the timer. **Not done**, because the census
  is the nightly HEAD-green signal and suppressing it is a bigger call than this item. A later tick that sees the
  gate still running at 03:00Z should make it.
- `wait_land10.sh`'s "unit not live" branch reads one unit name. If land10 is ever re-armed under another job
  name, update `W_UNIT` in arm.sh's step 2b.
