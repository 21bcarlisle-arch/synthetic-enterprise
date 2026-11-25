# The land10 item is spent: land10 and land11 were read, and the split now carries the MSC landing

**Severity:** low. This record closes a duplicate item. It also fixes one stalled gate.

`land10-outcome-is-read-and-msc-lands-or-is-re-cut` was drawn at 2026-11-25 ~06:30Z. The work it asks for is already done:

- **land10 outcome read.** `/var/tmp/se-msc-land10-ended.txt` says `exit 1 2026-11-25T00:59:08Z`. The log shows the
  test gate went red on 2 tests (3,347 passed, 3,379 s). That is written up in
  `WORKER_RECORD_LAND10_WENT_RED_ON_TWO_TESTS_ORIGIN_ITSELF_FAILED_AND_LAND11_IS_ARMED_BEHIND_THE_FIX_2026-11-25.md`.
- **Re-cut.** land11 timed out. That confirms da44381d2, and the landing was split
  (`WORKER_RECORD_LAND11_TIMED_OUT_AND_THE_MSC_LANDING_IS_SPLIT_IN_TWO_2026-11-25.md`).
- **Increment A is on origin/main** as `567288c031` (2026-11-25 06:18Z), promoted by the backgrounded
  `longjob-land-se-seat-executor-1795585767` after its turn ended (`/var/tmp/se-msc-keep/split/landA4.log`, EXIT 75).
- **Increment B** is carried by the live continuation `msc-b-the-world-charges-the-msc-on-a-replacement-win`.

**Fixed here: B's draw gate could never open.** B is held by `DO NOT DRAW BEFORE /var/tmp/se-msc-split-A-landed.txt EXISTS`.
A was promoted by a background unit after the turn that armed it had ended, so nothing wrote that file.
B would have waited for ever. The file is now written, holding A's origin sha `567288c031…`
(checked as an ancestor of origin/main before writing).

The general lesson: a handoff gated on a signal file has to be written by the job that does the
work, not by the turn that armed it. Whoever arms the B landing should have that job write its own
completion file.
