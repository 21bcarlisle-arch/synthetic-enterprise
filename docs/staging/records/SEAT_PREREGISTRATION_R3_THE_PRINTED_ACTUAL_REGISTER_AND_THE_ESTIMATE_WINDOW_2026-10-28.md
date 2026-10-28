# Pre-registration: R3 re-graded with the meter's own register on actual bills, and the estimate window's reach (2026-10-28)

Filed before either measurement below is run. The trace that motivates it is already done (results known):

- OCC-01e79fcf2d4fg's Dec 2021 gas estimate (2,138.62 kWh) is `annualised_advance_kwh` exactly: the register
  advanced 6,514.85 kWh from the 20 Mar 2021 opening read to the 30 Nov 2021 read (the meter-read log's true
  kWh, Apr to Nov), annualised at the 182-day floor. That is what the meter told the supplier. The
  `trailing_actual_periods` window is not what set it (that window gives 1,483.9).
- The ledger (`tools/generate_billing_ledger.py`) prints the Nov 2021 actual read as 1,618.9: the estimated
  register (seven 0 kWh estimates) plus the month's true kWh. The meter read 6,514.85. The grader's references
  come from printed actual reads, so its reference for Dec was about a quarter of the meter's.

**Book.** `/var/tmp/fresh-run-out-1a02c46116`, ledger `/var/tmp/n2n7-grade/ledger.json` (as graded for the
292). Scratch copy only; nothing published.

**M1. Re-grade with the meter's register on actual bills.** In a scratch copy of the ledger, each A bill's
closing read is the cumulative true kWh to its period end from `top__meter_read_log` (what the register shows),
and the next bill opens on it. Grade `INV_ESTIMATE_FOLLOWS_THE_LATEST_ACTUAL_READS` only.
- P1: OCC-01e79fcf2d4fg Dec 2021 no longer breaches.
- P2: the 292 falls to between 0 and 120. Point prediction 60. The residual is the window-definition
  difference the exception already names.

**M2. The window crossing's reach.** Count estimated bills (meter-read log) whose estimate was taken from
`trailing_actual_periods` with an estimated run before the latest actual read. That is the case where the window
held one month's settlement kWh that no read gave, and no actual read lay 182 to 731 days earlier.
- P3: fewer than 2% of the book's estimated bills.

A wrong prediction stays here beside its result.

## Results (filed after both runs; predictions above unedited)

Scripts: `/var/tmp/r3-grade/patch.py` (scratch ledger), `grade_r3.py` (the two read rows, printed invoices),
`m2.py` (window reach). The unpatched ledger reproduces the book's grade: 292 breaches on 50 accounts and 11 runs.

| | prediction | result | verdict |
|---|---|---|---|
| P1 | OCC-01e79fcf2d4fg Dec 2021 stops breaching | no breach on the account | HOLDS |
| P2 | 292 falls to 0 to 120 (point 60) | **151 on 30 accounts** (97 above, 54 below; 35 of them new) | REFUTED: the printed register explains 141, not about 230 |
| P3 | the window crossing sets under 2% of estimates | **2,754 of 31,588 (8.7%), 493 accounts**. The honest window moves 2,716 of them, ratio 0.42 to 2.54, median 1.003 | REFUTED |

The window crossing set 55 of the 292 breaches and 38 of the 151.
Unpredicted: on the meter's register, `INV_ESTIMATED_RUN_CONSISTENT_WITH_THE_METER` rises from 11 runs to 20.
The printed register had hidden nine runs that were out of band against what the meter really advanced. Five
of those runs billed 3 to 5.5 times the meter (PROS-2017-0336 2023-06 to 08 at 5.495).

## Filed before the next fresh run: the grade of a book carrying the window fix

The first fresh run launched after the window fix lands (expected: `the-desk-fix-is-graded-on-a-fresh-run`).
Grade `INV_ESTIMATE_FOLLOWS_THE_LATEST_ACTUAL_READS` with `grade_r3.py` on its ledger as built, and again on
`patch.py`'s meter-register copy.
- P4: as built, where the ledger still prints the estimated register, between 200 and 300. The window fix
  removes about 55 and the run's other changes move the rest. If the count falls under 200, something besides
  these two causes moved, and the grade must say what.
- P5: on the meter's register, between 80 and 140 (151 less the 38 the crossing set, plus the run's noise).
- P6: no estimated bill in the run's meter-read log takes a window entry shorter than the span back to
  the last actual read. Check: repeat `m2.py`'s honest window and confirm it equals the billed estimate
  wherever the window set it.
