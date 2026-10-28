**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# Pre-registration: the actual-bill register fix (37abacdf42) graded on a fresh full run, with the read chain it may break (2026-10-28)

**Item:** `the-ledger-register-rerun` (Lane 0, under
`docs/staging/advisor/DIRECTOR_RULING_CORRECTNESS_BEFORE_THE_NEXT_FEATURE_2026-10-26.md` step 4). **Filed after
the launch and before any output exists.** R3's 141 (of 292) was measured on a scratch-patched ledger
(`SEAT_PREREGISTRATION_R3_THE_PRINTED_ACTUAL_REGISTER_AND_THE_ESTIMATE_WINDOW_2026-10-28.md`); the fix landed with a
unit test only. This grades a book the run itself builds.

**Run.** `launch_long_job` job `fresh-run-37abacdf42`, worktree `/var/tmp/fresh-run-wt-37abacdf42` (origin
37abacdf42: carries both c4738b64c9, the estimate window, and 37abacdf42, the printed register), script
`/var/tmp/fresh-run-scripts/arm.py`, output `/var/tmp/fresh-run-out-37abacdf42`. Grading scripts:
`/var/tmp/regrerun-scripts/` (R3's `grade_r3.py` and `patch.py`, paths as arguments; `chain.py` new).

## Baseline, measured before this file on the previous book (129e7de698: neither fix)

| measure | as built | R3's meter-register patch |
|---|---|---|
| `INV_ESTIMATE_FOLLOWS_THE_LATEST_ACTUAL_READS` breaches (`grade_r3.py`) | 249 on 42 accounts | 151 on 30 |
| `INV_ESTIMATED_RUN_CONSISTENT_WITH_THE_METER` breached runs | 1 | 10 on 9 accounts |
| `INV_PERIOD_MATCHES_READS` (full runner, third-read grade) | 0 | — |
| E→A transitions (an actual bill straight after an estimate) | 6,444 | |
| actual bills whose printed opening is not the previous printed closing | 0 | |
| ToU invoices whose band indices do not sum to the total index | 223 of 1,189, 16 of 79 accounts | |

The 223 predate the fix: a band index does not move while the household is on a single rate (the ledger's
own LIMIT note).

## Predictions for the 37abacdf42 book, as built

- **Q1.** `INV_ESTIMATE_FOLLOWS_THE_LATEST_ACTUAL_READS`: 80 to 140, point 113 (151 less the 38 the window
  crossing set). This is R3's P5 applied to the book as built, since the ledger now prints the register. If
  over 200, the assembly's field is not reaching the ledger.
- **Q2.** As built equals R3's patch on the same book to within 10 (the fix and the patch should be the same
  register). A larger gap means the fix and the patch disagree, and the grade must say where.
- **Q3.** `INV_ESTIMATED_RUN_CONSISTENT_WITH_THE_METER`: 5 to 20 runs. The fix exposes runs the printed register
  hid. These are real estimate errors, and today only one is excepted, so I expect **unexcepted breaches to
  appear** in the full runner's grade.
- **Q4.** `INV_PERIOD_MATCHES_READS`: 0. closing − opening is the billed month by construction.
- **Q5. The read the supplier never saw.** The actual bill's opening is the register less the month, which is
  not the previous bill's closing. Actual bills whose printed opening is not the previous printed closing:
  4,500 to 6,600, all after an estimate. No invariant grades this today. The K8 page's own §13 practice says the
  opening should be the previous estimated read.
- **Q6. ToU.** The total index re-anchors to the register but the band indices do not. Band-sum-off invoices rise
  above 223: 300 to 900.

A wrong prediction stays here beside its result.

## Results (graded 2026-10-28, after the run finished; the predictions above are unchanged)

The run took 86 minutes. Outputs are in `/var/tmp/regrerun/` (`r3_asbuilt.txt`, `r3_patched.txt`, `chain.txt`,
`grade.txt`).

| | predicted | measured | verdict |
|---|---|---|---|
| Q1 `INV_ESTIMATE_FOLLOWS_THE_LATEST_ACTUAL_READS` | 80 to 140, point 113 | **153 on 32 accounts** (115 above, 38 below) | **Refuted.** It is under 200, so the field reaches the ledger. The point assumed the window fix only removes breaches. It removed 37, close to the 38 counted, and set 39 new ones on 6 accounts (PROS-2019-0173g 13, SYN-2016-159g 13, SYN-2016-050 6, OCC-17ff099218d5g 5). 114 of the 153 are the bills R3's scratch ledger left on the old book |
| Q2 as built against R3's patch | within 10 | 153 against 162 | Held, at the edge |
| Q3 `INV_ESTIMATED_RUN_CONSISTENT_WITH_THE_METER` | 5 to 20, with unexcepted breaches | **13 runs on 12 accounts**, over the old ceiling of 11, so the publish was refused | Held. None of the 13 is a zero run, so the zero-advance fix holds |
| Q4 `INV_PERIOD_MATCHES_READS` | 0 | 0 of 52,901 | Held |
| Q5 actual bills whose opening is not the previous closing | 4,500 to 6,600, all after an estimate | **6,436**, of which 6,435 follow an estimate (6,444 E→A transitions) | Held |
| Q6 ToU invoices whose bands do not sum to the total index | 300 to 900 | **417 of 1,189, on 39 of 79 accounts** (223 on 16 before) | Held |

R3's "141 of 292 reconciled" is now measured on a book the run built, not predicted: the row falls from 292 to 153
(-139). That is the printed-register cause less the window fix's net zero.

**The 13 runs, by cause (hypotheses until a fix moves them):**
- **8 follow a single actual read**, usually an occupier's short first month. On OCC-f6813bf9f05eg gas, 138 kWh in
  Oct 2016 is followed by eight estimates totalling about 1,890 kWh, against about 8,065 kWh on the meter (0.233).
  All 7 below-the-line runs are this cause, plus PROS-2024-0010 above it.
- **5 are summer runs on heating households** (9.6 to 34.5 MWh a year), estimated 3.0 to 5.5 times the meter.
  PROS-2017-0336 electricity uses about 300 kWh a month in summer and was estimated at about 1,600.

**Exceptions re-based** in `DOMAIN_INVARIANT_EXCEPTIONS.yaml` to 153 and 13, each marked partly diagnosed. The full
runner on this book now reports 0 unexcepted breaches with 11 excepted, so the publish stands. Finding:
`docs/staging/SEAT_FINDING_THE_PRINTED_REGISTER_FIX_EXPOSES_ESTIMATES_FROM_ONE_READ_AND_PRINTS_6436_OPENING_READS_NOBODY_TOOK_2026-10-28.md`.
