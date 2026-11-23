**Severity:** BLOCKING · **Lane:** C_customer_ops · **Epoch:** 2 · **Atom:** `EP4_collections_journey`

# origin/main has been red on the live Consent offer since 7527a2e36, and that red blocks the gas-only win (23 Nov 2026)

Filed by the delivery seat under `verify-reg-6c-and-gas-only-win-resume-chain`.

## What was drawn, and what is spent

The resume chain `/tmp/seat_6c_v4/resume.sh` landed reg 6C (cc9f08ae3d, promoted as 09ae79aa0c;
`/var/tmp/se-reg-6c-landed-20261123.txt`). That half is done. The chain then tried to land the
gas-only win (`SEAT_FINDING_A_WON_SWITCH_FROM_A_GAS_ONLY_HOUSEHOLD_IS_NEVER_SUPPLIED_2026-11-22.md`)
and the commit gate refused it: `GAS LAND EXIT 1`, 2 failed / 2690 passed in 2368 s
(`/tmp/seat_6c_v4/resume.log`). The gas files are uncommitted in the locked worktree
`/var/tmp/se-reg6c-land` and in `/tmp/seat_gas/files`. Nothing has touched their paths on origin
since 09ae79aa0c, so they still apply as they are.

The two red tests:

- `tests/company/billing/test_collections_journey.py::test_a_live_run_withholds_the_prepayment_offer_at_the_ninety_day_rung`:
  "the gate does not decide the live Consent offer both ways" (answered run: `{'prepayment_withheld'}` only)
- `tests/company/billing/test_collections_journey.py::test_the_world_counts_every_consent_offer_the_company_made`:
  "no live Consent offer -- the count's agreement is untested" (0 offers)

## It is not the gas change. It is origin.

Pre-registered before the measurement (`docs/staging/records/SEAT_PREREG_THE_LIVE_CONSENT_RED_IS_THE_GAS_CHANGES_2026-11-23.md`, written 06:36Z). The
prediction was (a) origin green and (b) gas red, at about 65%. **It was wrong.** Run on origin/main
0b4d8ae594, both tests are red with and without the gas files (about 7.5 min each). Both gas-only
wins fall in 2017 (31 Mar, 12 Dec), outside the test's 2016 window, so the gas branch cannot be
reached there.

## Bisect (one test, the 90-day rung, single runs)

| commit | result |
|---|---|
| 8aa5aa350a^ / 8aa5aa350a (C32 class 6) | green / green |
| f3c6a45cbd (growth campaign quote) | green |
| f1a01411fa (docs only, includes 8bd0092e80 conftest) | green |
| **7527a2e36c** (a switching level leaver's final bill is netted by the world) | **red** |
| 9b5116a444, cc9f08ae3d, 0b4d8ae594 (origin) | red |

7527a2e36c changes one runner line (`closing=left` into `record_period`) and the triad's
`final_month` gate (`closing or moved_out_on ...`). Its commit gate ran **4 tests in 11 s**, so the
live-run collections tests were never selected for it. That is how a red reached origin with a
receipt.

## Why one commit can empty the rung: the control stood on one household

At f3c6a45cbd the answered 2016 run (`plan_take_up_share` at the `high` row) reaches the 90-day rung
for exactly two accounts. ACC-SYN-2016-105 is withheld, and **ACC-SYN-2016-005 is offered
(2016-10-26), the only offer** (`/tmp/seat_gas/probe/offered_f3c6a45cbd.json`). ACC-SYN-2016-005 does
not leave in 2016 (its one churn roll, 2016-07-01, stays). So 7527 does not remove a departed
household's offer. It moves what reaches that household, which is consistent with a shared draw
moving in the world's payment triad, against the commit's own "no seed moves". The 7527 probe of the
same run was queued behind the box's `sim_run` admission when this was filed. Its answer goes here,
not into a guess.

Both controls are keyed to today's answer, a single household in a 2016 window, rather than to the
property (some answered household is offered, and the gate decides both ways). Any honest change to
the world can empty them, and when it does it reds every landing that touches
`simulation/run_phase2b.py`.

## Done means

1. Name the mechanism: which 7527 path moves ACC-SYN-2016-005 off the rung (a world draw shifted,
   or a legitimate change in its payments).
2. If a draw moved, that is 7527's defect (it claimed none) and is fixed at its source. If not, the
   control is re-keyed to the property over a window that holds more than one offer, with its own
   defect named and mutation-proven. A test is never loosened to pass.
3. Origin is green on both tests. The gas-only win is then landed from `/tmp/seat_gas/files` with
   its existing message (`/tmp/seat_gas/msg/msg.txt`), promoted, and `/var/tmp/se-reg6c-land` is
   removed.
