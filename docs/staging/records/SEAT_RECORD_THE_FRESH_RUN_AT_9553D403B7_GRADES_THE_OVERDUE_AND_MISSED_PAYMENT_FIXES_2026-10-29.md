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

## Results

To be graded when the run ends. Each prediction's result goes beside it in its own record, and that record
is cross-referenced here. `DOMAIN_INVARIANT_EXCEPTIONS.yaml`'s ceilings are set to what this book measures,
and every row that reads 0 is retired.
