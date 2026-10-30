**Severity:** RECORDED · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** none — Lane 0 `the-fresh-run-at-the-meter-fixes`

# Pre-registration: the fresh run at cd4fc5b8d8 carries the Economy 7, PC2-estimate and serial fixes, and not gas (2026-10-30)

Written before the run was launched. Under the correctness stretch
(`docs/staging/advisor/DIRECTOR_RULING_CORRECTNESS_BEFORE_THE_NEXT_FEATURE_2026-10-26.md`).

## Why it launches without the gas build

The direction bounded the wait: if the gas build (item `a-gas-read-is-a-volume-and-the-bill-converts-it`)
was not on origin by the next orientation, launch without it. At 12:57Z it is not on origin, and its claim
(taken 12:04Z) has no live process and no worktree carrying gas changes behind it. Waiting would buy nothing,
so the seat launches now rather than at the next orientation. **The gas prediction (energy down about 0.13% on
average, never more than 0.26% on any bill) is left to the run after this one.** That run must carry the gas
build.

## The run

- Full default book, origin `cd4fc5b8d8`, via `launch_long_job` (`longjob-fresh-run-cd4fc5b8d8`).
- The same `/var/tmp/fresh-run-scripts/arm.py` as the 3dc5a92948 book.
- Worktree `/var/tmp/fresh-run-wt-cd4fc5b8d8`, locked. Output `/var/tmp/fresh-run-out-cd4fc5b8d8`.
- Grade chain: `/var/tmp/fresh-grade-cd4f-scripts/chain.sh`, which is the 3dc5a92948 chain re-pointed. It writes
  to `/var/tmp/fresh-grade-cd4fc5b8d8/`.
- Comparison book: `/var/tmp/fresh-run-out-3dc5a92948`, graded in
  `SEAT_RECORD_THE_3DC5A92948_BOOK_GRADED_AND_ITS_PAGES_BUILT_2026-10-30.md`.

**Attribution.** These run-side commits have landed since 3dc5a92948:
- fca63e87d8, the Economy 7 two-register bills;
- 32ddfa8ca2, the PC2 per-register estimate;
- 6ef8f1b678, the serial minted per supply point;
- cb53859273, the declared-policy estimate grade;
- 128149f343, the one-day-bill penny;
- 3924810446, part-year carbon;
- 161f70f7d8, the PC2 2026 TDCV row.

A move on any row the first three cannot reach is attributed to the others, or to nondeterminism. It is not
attributed to the meter fixes.

## Predictions

The meter fixes' predictions were filed with their builds, before this run, and are graded as written:
- `SEAT_FINDING_AN_ECONOMY_7_METER_IS_BILLED_ON_ITS_TWO_REGISTERS_2026-10-30.md`, N1-N4. Its N5 is replaced by
  the next finding's P1.
- `SEAT_FINDING_A_PC2_METERS_UNREAD_MONTH_IS_ESTIMATED_PER_REGISTER_2026-10-30.md`, P1-P3.

The seat adds:

- **S1.** INV_METER_SERIAL_ONE_SUPPLY_POINT (N10): 0 serials re-minted. No page serial sits on more than one supply
  point.
- **S2.** These rows stay at their 3dc5a92948 counts:
  - the SVT one-price row reads 0, as 128149f343 graded it;
  - F and V both read 0;
  - INV_BILLED_EX_VAT_RECONCILES_TO_REVENUE reads 1 (PROS-2017-0117), unless the PC2 estimate moves that
    account. It is not a storage home, so I predict it does not;
  - desk-cure P1 reads 0 journeys `cured` at `days_overdue == 0`;
  - INV_ESTIMATE_FOLLOWS_THE_LATEST_ACTUAL_READS reads 0 under the declared policy.
- **S3.** INV_ESTIMATED_RUN_CONSISTENT_WITH_THE_METER falls from 6 to 2. Cause (a)'s four runs on storage homes
  leave; (b) SYN-2016-396g and (c) PROS-2016-0263g stay. If any of (a) stays, P1's reference-window cause is the
  first thing to check.
- **S4.** The storage-heating Explore slot fills. On 3dc5a92948 it refused 96 of 96 households on "no PC2 meter on
  the record". `registered_profile_class` now crosses the seam, so at least one storage home should pass. If it
  stays empty, the failing check it names is the finding.
- **S5.** The "cleared while still owed" households PROS-2025-0013 and PROS-2020-0191: no prediction about cause.
  Each one is traced by name if it survives. On the last book, PROS-2025-0013's "repaid" fell after its page's
  ledger ended, and PROS-2020-0191's desk/page gap was 40.73.

A wrong prediction is kept beside its measured value in the grade. It is not revised.
