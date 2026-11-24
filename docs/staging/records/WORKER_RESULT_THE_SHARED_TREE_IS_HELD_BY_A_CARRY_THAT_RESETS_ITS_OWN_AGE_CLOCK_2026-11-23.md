**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The shared tree is held by a carry that reset its own age clock, and by one live landing (2026-11-23)

*Worker, LANE 0 draw `the-shared-checkout-runs-the-promotion-fix-origin-already-has`.*

**Premise, re-measured ~14:00Z.** It holds. The shared tree is 39 behind origin/main and 0 ahead. The
twins are not the hold. `reconcile-watch-log.md` (13:38Z) says 26 of 29 blocking paths could be
cleared, but the all-or-nothing rule correctly writes nothing while 3 paths hold:

| path | what it is | why it held |
|---|---|---|
| `simulation/run_phase2b.py` | live work: the closed-account Consent-offer landing, `surgical_land` pid 2645749, gating now | held, correctly |
| `saas/reporting/annual_report.py` | stale. Its only line not on origin is `"switching_gsop_payments": _NO_READER`, the state before 0efa633c1b moved that key to a forward (from salvage a7bb4b28cd) | "8.1h old, LIVE". The mtime is 05:32:07, the reconciler's own carry b19e2a51de. That was the fourth carry since 21 Nov (d39539f7ac, 96dbd2f364, cd4caff3e8) |
| `tests/simulation/test_run_phase2b.py` | stale. All 28 lines not on origin are at 83570bd1c^, and it lacks a525847e98's gas-only test. Bytes are on salvage a00ac96e63 | under 48h (22 Nov 09:23) |

**The defect fixed (this commit).** `origin_reconcile._apply_carry` rewrote a carried file and left
its own time on it, so `abandoned_copy_verdicts` read each carry as fresh lane work. A copy carried
on every advance could never age out. The carry now restores the lane's own atime/mtime. This is
mutation-proven by
`test_a_carried_edit_keeps_its_lanes_last_write_time_so_it_can_still_age_out`.

**Not done: HEAD != origin.** This lane did not touch the two stale copies.
`refresh_to_head --base origin/main` refuses annual_report (the stale-copy control cannot see a
key moved between the register and a forward). For the test file it needs `--discard-prose`, which
is a person's flag. Both age out under the existing class with no help: the test copy on 24 Nov
09:23, annual_report on 25 Nov 05:32 (it now conflicts, so it is no longer carried). That holds
only if the closed-account landing has released `run_phase2b.py` by then. 0b4d8ae59's retry fix
stays unlive until the advance.

**The drawn BLOCKING finding** (origin red on the live Consent offer) is held by the live claim
`a-closed-account-is-never-offered-a-prepayment-meter`, whose landing is gating now. Its gas-only
step 3 is already on origin (a525847e98). This lane did not duplicate it.
