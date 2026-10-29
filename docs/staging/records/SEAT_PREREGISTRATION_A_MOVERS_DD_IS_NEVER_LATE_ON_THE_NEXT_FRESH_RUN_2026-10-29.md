**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# Pre-registration: a mover's DD is never late, graded on the next fresh run (2026-10-29)

**Filed before any run carries the fix.** The fix: `arrears_engine.mover_final_bill_outcome` returns a paid
final bill on a DD leg with `days_late` 0, and `LivePaymentTriad.record_period` asks the exit model only for the
bill whose month reaches the last supplied day's. Trace:
`docs/staging/SEAT_FINDING_THREE_SMALL_EXCEPTIONS_TRACED_ON_THE_209C_BOOK_MOVERS_DDS_HELD_BILLS_AND_THE_REVENUE_ROWS_CLASSES_2026-10-29.md`.
Baseline: 35 on the 209c3350ab book graded with origin 1ba034b9c8's code, every one a mover's.

- **P1. `INV_PAYMENT_RECORD_RECONCILES_TO_COLLECTIONS_DUE`: 0, range 0 to 2.** Every one of the 38 bills was on one
  of the two paths fixed. If any breach remains, that is a path not yet seen, and it is traced before the ceiling
  moves. Above 2 means the fix is not reaching the run.
- **P2. Movers' bills that the exit model draws: about half of what they were.** Before the fix, two bills per
  mover could be drawn (the final and the one before it). After it, one. The book's mover bad debt may fall a
  little, because the penultimate bill now takes the mid-tenure failure rate instead of the exit's. **I cannot
  yet say by how much.** This is not graded against a number.
- **P3. No other row moves on this account.** The fix changes only movers' bills. A row that moves by more than its
  run-to-run spread, and has no other commit to attribute it to, refutes this.

Several commits may land before the next run. Where a row is touched by more than one of them, its move is graded
and not attributed.
