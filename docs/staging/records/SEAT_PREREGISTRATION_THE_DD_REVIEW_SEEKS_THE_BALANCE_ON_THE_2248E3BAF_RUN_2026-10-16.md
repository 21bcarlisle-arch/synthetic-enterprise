# Pre-registration: the DD review seeks the balance, on the 2248e3baf run (2026-10-16, written before the run)

**Subject:** `docs/staging/SEAT_FINDING_D48_A_THIRD_OF_DD_ACCOUNTS_ASKED_FOR_THEIR_BALANCE_LOSE_PART_OF_IT_BECAUSE_THE_REVIEW_NEVER_ASKS_2026-10-14.md`.
**Instrument:** `simulation.dd_balance_book.build_dd_balance_book` over `docs/reports/run_output_2248e3baf_20261013T134447Z.json`,
closed = supply points whose last bill predates the run's last billed month; both arms of
`seek_balance_at_review`, one process.

**Today (seek = false):** 153 of 422 accounts that met a charge recovery action barred, £33,770.

**Predicted, seek = true:**

1. The denominator grows: at least 600 accounts meet a recovery action, because every open account
   with a debit at a review is now asked.
2. The barred share FALLS, to 15% (range 8-25%). Reason: each review asks for the balance while
   most of it is under twelve months old, and the step-up then pays the oldest shortfall first.
3. Money barred falls to about £12k (range £5k-£22k). It does not reach zero: in the rising years
   (2021-22) a reset to last year's spend under-collects again inside the year.
4. The step-up the recovery causes has a median of £5-15 a month per stepped-up account, largest
   in 2022-23.

Graded in the finding after the run.
