**Severity:** RECORDED · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** none — focus `the-last-pc2-catch-up-defect-then-the-publish`, part (2)

# The 85b044be54 book graded against both pre-registrations: 16 predictions held, 2 refuted, 1 row moved unpredicted (2026-11-02)

Under the correctness stretch (`docs/staging/advisor/DIRECTOR_RULING_CORRECTNESS_BEFORE_THE_NEXT_FEATURE_2026-10-26.md`).
This grades
`SEAT_PREREGISTRATION_THE_FRESH_RUN_AT_85B044BE54_CARRIES_THE_PC2_AND_GAS_FIXES_2026-11-02.md` and
`SEAT_PREREGISTRATION_THE_PC2_FIXES_PREDICTED_PER_ROW_FOR_THE_NEXT_FRESH_RUN_2026-10-30.md`. Neither file is edited.

The book: `/var/tmp/fresh-run-out-85b044be54` (1,293 accounts, 52,828 invoices). The grade was produced by its own
chain at 10:15Z (`/var/tmp/fresh-grade-85b044be54/grade.txt`, `grade.json`), with pages built under `tree/`. This
record writes it down. Counts on the cd4fc5b8d8 side come from `/var/tmp/fresh-grade-cd4fc5b8d8/grade.json`.

**Verdict: refused, 9 unexcepted breaches on 4 rows** (E7 two registers 2, read monotonic 2, ToU bands 2, estimate
after actual 3). The 6 excepted rows are all at or under their ceilings.

## Prediction by prediction

| Row | cd4fc5b8d8 | Predicted | 85b044be54 | |
|---|---:|---:|---:|---|
| INV_BILLED_EX_VAT_RECONCILES_TO_REVENUE | 4 | <= 1 | 0 | held |
| INV_CARBON_PANEL_KWH_MATCHES_USAGE_PANEL | 120 | <= 6 | 6 | held (PROS-2024-0010, PROS-2025-0106, SYN-2016-582: the excepted class) |
| INV_EBSS_CREDIT_EACH_MONTH / _ON_THE_BILL | 21 / 21 | 6 / 6 | 6 / 6 | held (all OCC void or occupier months) |
| INV_ESTIMATE_FOLLOWS_THE_LATEST_ACTUAL_READS | 170 | <= 10 | 3 | held (on count; see below for what the 3 are) |
| INV_E7_METER_BILLED_ON_TWO_REGISTERS | 4 | 0 | 2 | **refuted** |
| INV_TOU_BANDS_SUM_TO_THE_TOTAL | 2 | 0 | 2 | **refuted** |
| INV_PERIODS_CONTIGUOUS | 2 | 0 | 0 | held |
| INV_ESTIMATED_RUN_CONSISTENT_WITH_THE_METER | 4 | <= 4 | 4 | held (excepted) |
| INV_GAS_READ_IS_A_VOLUME_CONVERTED_AT_CV_AND_CF | uncheckable | 0 | 0 of 23,745 | held |
| INV_SVT_ONE_PRICE_PER_REGION_METHOD_WINDOW | 690 (pre row fix) | 0 | 0 | held |
| INV_METER_SERIAL_ONE_SUPPLY_POINT | 0 | 0 | 0 | held |
| F/VAT: reads left uncorrected; catch-ups off the VAT line | 0; 0 | 0; 0 | 0; 0 (6,431 catch-ups applied) | held |
| desk-cure P1: `cured` at `days_overdue == 0` | 0 | 0 | 0 of 1,078 journeys | held |
| INV_UNIT_RATE_EPG_HOUSEHOLD | 350 | <= 350 | 350 | held (excepted ceiling) |
| INV_PPM_NOT_CREDIT_BILLED | <= 12 | <= 12 | 12 | held (excepted ceiling) |
| Storage-heating Explore slot | empty | fills | PROS-2017-0233 | held; 7 of 8 slots fill, EV is honestly empty (4 of 6 candidates fail the 1,750-3,300 kWh rise) |
| Debt survivors (cleared while still owed) | 2 | both survive, no new one | PROS-2020-0191, PROS-2025-0013, no others | held |
| Gas energy, the weaker book-level test (within 0.26%) | 20,355,257.3 kWh | within 0.26% | 20,355,257.3 kWh | held, and so did the **stronger** test the pre-registration said it might not be able to run: bill for bill, 0 of 23,745 gas invoices differ in kWh |

## The two refutations, and the row nobody predicted

- **E7 two registers 2 and ToU bands 2 are one cause, on OCC-23ee23cb44e4 (2022-01-25) and OCC-7e06d09fc108
  (2024-11-23).** The PC2 fix's point 5 zeroed the void row's kWh, which moved the Anytime stub rather than
  removing it: the 7-day owner stub priced by `_estimate_records_at_tariff_rate` wrote no band. Traced and fixed in
  1b709ac0e9 (after this book was built). Two of the three estimate-after-actual hits are the same two stubs.
- **INV_READ_MONOTONIC moved 0 -> 2, which neither file predicted.** PROS-2017-0336 Night 2018-05-31 -> 2018-11-30
  (-795.4) and PROS-2024-0010 Night 2024-05-31 -> 2024-09-30 (-170.2). The finding traces both to a downward
  catch-up shared over Day and Night by printed share; fixed in 8cf2ecb744 by closing each register on its own read.
  **I cannot yet say** whether the PC2 fix exposed this (on cd4fc5b8d8 these winters were held bills, so their
  catch-ups never printed) or W2_37 (59bde3e790, the named confound) moved it. Gas being identical bill for bill
  says W2_37 did not move the gas world; it says nothing about electricity reads.
- The third estimate-after-actual hit, PROS-2017-0336 2018-08, sits in the same Night over-estimate window.
  8cf2ecb744 is not shown to move it.

## What this predicts for the next fresh run (at or after 8cf2ecb744), filed before it exists

The sim_runner holds its next run until about 14:01Z; both fixes were on the shared tree's disk at 12:57Z, so that
run carries them. Predicted unexcepted rows: E7 two registers 2 -> 0, ToU bands 2 -> 0, read monotonic 2 -> 0,
estimate after actual 3 -> at most 1 (PROS-2017-0336 2018-08). If that holds, the domain-invariant gate passes
and the run is the publish. A row above these counts refutes its fix and is traced again, not re-explained.
