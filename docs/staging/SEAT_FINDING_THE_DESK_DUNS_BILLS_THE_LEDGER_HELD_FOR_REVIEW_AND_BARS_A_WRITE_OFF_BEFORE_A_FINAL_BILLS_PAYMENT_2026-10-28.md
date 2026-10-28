**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 2 · **Atom:** `unminted`

# The desk dunns bills the ledger held for review, and bars a write-off before a final bill's payment

These are the two residuals left by the one-due-date fix on the fresh run at `1691ec0ecd`. The grade
is beside
`docs/staging/records/SEAT_PREREGISTRATION_ONE_DUE_DATE_FOR_THE_DESK_AND_THE_LEDGER_ON_A_FRESH_RUN_2026-10-27.md`,
and both are excepted at their counts in `docs/design/DOMAIN_INVARIANT_EXCEPTIONS.yaml`.

1. **Overdue with nothing issued (4 of 7,380 journey openings).** PROS-2017-0336, PROS-2024-0010,
   PROS-2025-0106 and SYN-2016-582 are exactly the billing ledger's `exception_queue`. That queue is
   nine months of household-labelled accounts whose metered load looks like an SME's
   (`vat_by_segment`), and the ledger holds those bills and issues none. The run still posts them to
   the company's ledger as due, and the desk opens a journey the day after. Fix: a held bill is not
   due until it is issued. Either the hold reaches the company's ledger, or the run does not post a
   bill the ledger holds. Which side owns the hold is the design question.
2. **A write-off barred before the household's last payment (3 of 64).** OCC-6e59dd8b63e8,
   SYN-2016-016 and SYN-2016-611 each carry two limitation write-offs. The first is dated six years
   after a payment that a final-bill payment, arriving 1 to 16 days later and after the leg closed,
   should have restarted. For the first two, that later payment is on the other fuel leg; for
   SYN-2016-611 it is on the same leg. `collections_journey.statute_barred_gbp` returns zero when any
   payment lands after the bar, so the desk's ledger either lacks the post-close payment or bars per
   leg. That is not traced. **Knowledge first:** whether limitation runs per fuel contract or per
   household account is not on `docs/market_research/debt_and_collections.md` (GAP). If it is per
   contract, the two dual-fuel cases are the grader's reading being wrong, not the desk's. The
   single-fuel case is a defect on either reading.

## Item 1 closed on a fresh run (2026-10-28, item `the-desk-fix-is-graded-on-a-fresh-run`)

On the fresh run at b2fc50facf, `INV_OVERDUE_WITHIN_BALANCE` grades **0 of 7,374** openings, from
4. That run carries ec079776de, which posts the desk the issued bill, so a bill the ledger holds
posts nothing. Its exception is retired. Item 2 is unchanged: `INV_STATUTE_BARRED_WRITE_OFF_AGE`
still grades 3, now of 63, and stays excepted at 3. Grade beside
`records/SEAT_PREREGISTRATION_THE_DESK_POSTED_THE_ISSUED_BILL_READ_ON_A_FRESH_RUN_2026-10-28.md`.
