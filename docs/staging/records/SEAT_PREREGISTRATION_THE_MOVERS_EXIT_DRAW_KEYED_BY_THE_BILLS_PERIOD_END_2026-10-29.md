**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** unassigned · **Atom:** `unminted`

# Pre-registration: the mover's exit draw keyed by the bill's period end, graded on the next fresh run (2026-10-29)

**Filed before any run carries the fix.** The fix: `LivePaymentTriad.record_period` takes the bill's
`period_end` (the run passes the month's last supplied day) and asks `arrears_engine.mover_final_bill_outcome`
with it, as `dd_collection_book`, the arrears engine and the pay-on-receipt path already do. Before it, the
triad passed the bill's due date. Item `the-mover-exit-draw-reads-the-bills-period-not-its-due-date`; found by
156f8dfd6 on `SEAT_FINDING_THE_PAGE_PRINTS_MORE_OVERDUE_THAN_IT_SAYS_IS_OWED_ON_493_OF_752_HOUSEHOLDS_2026-10-28.md`.
It lands on top of the companion gate in `SEAT_PREREGISTRATION_A_MOVERS_DD_IS_NEVER_LATE_ON_THE_NEXT_FRESH_RUN_2026-10-29.md`,
which already stopped the bill before the final being drawn as an exit; this change moves the final bill's seed.

**Measured on the 209c3350ab book before the run.** Method: for every mover leg in `p2b__per_customer_behavioral`,
call `mover_final_bill_outcome` on each of its `top__bills` bills twice, keyed by `bill_due_date(cid, period_end)`
(the old key) and by `period_end` (the new), with the leg's `moved_out_on`, `stress_for_year` and the channel
its `world_payment_truth` outcome recorded, base seed 42; compare to the book's recorded outcome.

- 259 mover legs; 211 final bills reach the exit rule. The due-date key reproduces the book's own outcome on
  **210 of 211**, so the replay is the triad's draw.
- 207 legs had their penultimate bill drawn as an exit under the due-date key (the companion fix removes these).
- Under the period-end key, **71 final bills on 60 households** change outcome (result, or part paid vs not):
  35 go from success to failed or part paid, 36 the other way. SYN-2016-083's own final bill does not move.

**Predictions for the next fresh run** (same population and seed, so the final bills are the same bills):

- **P1. About 60 households' final-bill outcomes differ from 209c3350ab's, range 45 to 75**, counted on the
  run's `world_payment_truth` outcomes for each mover leg's last supplied month. The number is a reseed of a
  ~1-in-3 draw, so the identity of the households moves and the rate does not.
- **P2. Movers' final-bill failure rate: no move beyond its binomial spread** (35 vs 36 flips). A material
  move in the rate refutes "this is a reseed only".
- **Not predicted:** a disagreement count between the DD book and the triad. Under `world_payment_truth.UNIFIED`
  the DD book reads the triad's outcome for the bill and draws nothing, so the book showed none before and will
  show none after; the fix matters wherever a path draws the bill without the triad's truth.

Several commits may land before the next run. Where a row is touched by more than one of them, its move is graded
and not attributed.
