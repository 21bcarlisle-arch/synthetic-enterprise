**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# The fresh run at 9553d403b7 that grades the overdue and missed-payment fixes (2026-10-29)

**Item:** `the-fresh-run-that-grades-the-overdue-and-missed-payment-fixes` (Lane 0, under the correctness
stretch, `docs/staging/advisor/DIRECTOR_RULING_CORRECTNESS_BEFORE_THE_NEXT_FEATURE_2026-10-26.md`, exit-test leg one).
**Written at launch, before any output exists.** No new prediction is made here. The run is graded against
the predictions already on origin, listed below.

**Run.** `launch_long_job` job `fresh-run-9553d403b7`, launched 17:34Z. Worktree `/var/tmp/fresh-run-wt-9553d403b7`
(origin 9553d403b7, locked), script `/var/tmp/fresh-run-scripts/arm.py`, output `/var/tmp/fresh-run-out-9553d403b7`.
It was queued behind one pending landing. The 209c3350ab run took 74 minutes once it started.

**What it carries that the 209c3350ab book did not.** Items 1 to 3 of the stretch have all landed:
- 5d7775b40d: the ledger's letters yield to the desk.
- 8d9dd19b58: a mover's DD is collected on its date or returned.
- ea73ccebed: the mover's exit draw is keyed by the period end.

It also carries the earlier replay-only fixes:
- dae9f598d: one missed-payment definition.
- 714b0ce3c: the desk asks the printed total, and sees a final bill's part payment.
- 156f8dfd6: a credit bill is posted to the desk.

**Grade.** The transient unit `grade-chain-fresh-run-9553d403b7` follows the job to its end. It then runs
`/var/tmp/fresh-grade-9553-scripts/after_run.sh` into `/var/tmp/fresh-grade-9553/`, in this order:
1. the ledger;
2. the full domain-invariant suite (`grade.py`, the 209c grade's own);
3. the overdue row's classes (`overdue820/probe.py` and `classify.py`);
4. the mover-exit comparison against 209c3350ab (`mover_cmp.py`).

It writes `ALLDONE` on success and `NO_DONE` if the run left no `DONE.json`.

**Predictions it grades:**

| source | predictions |
|---|---|
| `SEAT_PREREGISTRATION_THE_OVERDUE_ROWS_2500_STEPS_BY_CAUSE_ON_THE_209C_BOOK_2026-10-29.md` | P1 to P6, and P-C |
| `SEAT_PREREGISTRATION_ONE_DEFINITION_OF_A_MISSED_PAYMENT_ON_BOTH_BOOKS_2026-10-29.md` | its 209c3350ab rows, re-read on this book |
| `SEAT_PREREGISTRATION_A_MOVERS_DD_IS_NEVER_LATE_ON_THE_NEXT_FRESH_RUN_2026-10-29.md` | P1 to P3 |
| `SEAT_PREREGISTRATION_THE_MOVERS_EXIT_DRAW_KEYED_BY_THE_BILLS_PERIOD_END_2026-10-29.md` | P1 and P2 |

Several of these commits touch the same rows. A row that more than one of them moves is graded and not
attributed.

## Results (graded 2026-10-29, after the run)

The run ended at 19:24Z (DONE.json, 4,284 s, no key skipped). The chain graded it and wrote `ALLDONE`.
Output is in `/var/tmp/fresh-grade-9553/`; the seat's own probes are in `/var/tmp/clse/`.

**Leg one of the exit test, on this book: met in the letter, not in substance.**
- Under the exceptions file as it stood, the suite **refused the publish**. The revenue row was 25 against a
  ceiling of 24.
- Every one of the 25 is now traced, and the file is set to this book. Re-gated, the result is **0 unexcepted
  breaches across 1,293 accounts; 247 breaches on 7 rows, each named and dated**. So there are zero unexplained
  breaches.
- But "explained" is not "correct". Two of the causes are billing defects filed today and not yet fixed (below).
  The carbon, EBSS and estimate rows also carry open work under their retire conditions.
- 5 rows are UNCHECKABLE on the raw export, so leg one says nothing about them.

| row | 209c3350ab | 9553d403b7 | |
|---|---|---|---|
| INV_OVERDUE_WITHIN_PAGE_BALANCE | 2,500 of 19,491 | **0** of 19,819 | exception retired |
| INV_PAYMENT_RECORD_RECONCILES_TO_COLLECTIONS_DUE | 35 (one definition) | **0** of 1,130 | exception retired |
| INV_BILLED_EX_VAT_RECONCILES_TO_REVENUE | 24 | 25 | traced, ceiling 25 |
| PPM not credit billed / EBSS ×2 / carbon / estimate follows reads / estimated run | 12 / 6 / 6 / 6 / 179 / 6 | the same, on the same accounts | ceilings unchanged |

**Predictions** (each graded beside itself in its own record):
- Overdue rows: P1 to P4, P6 and P-C held, the row going to 0. **P5 refuted as stated**: the desk's close write-off
  fell £1,856.34, not at most £509.52. Two of the run's changes move it, so it is not attributed.
- One definition of a missed payment: the row is 0. The debt slot's rows were not re-read, because this book's
  pages were not built.
- A mover's DD is never late: P1 held (0). P2 not measured. P3 held.
- Mover exit keyed by period end: P1 held (59 households, range 45 to 75). P2 held (41 to 44 of 252).

**The revenue row, every breach traced** (replacing classes (a) to (e); (c) and "(a)'s price side" refuted):
- **F, 17 accounts.** A read-to-read correction under £5 is dropped, and the book drops 2,747 such corrections
  overall. Filed in `SEAT_FINDING_AN_ACTUAL_READ_UNDER_FIVE_POUNDS_OFF_THE_ESTIMATES_NEVER_CORRECTS_THEM_THE_REVENUE_ROWS_CLASS_E_2026-10-29.md`.
- **V, 7 accounts, to the penny.** The catch-up is added to the bill gross, and its VAT never reaches `vat_gbp`.
  3,705 bills print too little VAT, about £5,700. Filed in `SEAT_FINDING_A_CATCH_UP_IS_ADDED_TO_THE_BILL_GROSS_AND_ITS_VAT_NEVER_REACHES_THE_VAT_LINE_2026-10-29.md`.
- **B, 1 account.** PROS-2017-0117's open run of under-estimates exceeds the row's bound U.

**Also corrected beside the claims** (earlier today, 795765c2a): "held bills are never issued" in the carbon and
revenue exceptions.

**Next.** Fix V, then F, knowledge page first (K8), and grade both in replay on this book. The prediction is
that the revenue row goes to 1 (PROS-2017-0117).
