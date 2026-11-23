**Severity:** S3 (a baseline, not a defect: it moves no switch and repairs nothing)

# The two renewal beliefs on held-back renewal years, on the 20 Nov book

**Written 2026-11-23 by the delivery seat, for the claim
`the-renewal-belief-switch-on-has-a-held-back-baseline-from-the-20-nov-book`.** This is the baseline
for the read `read-the-ending-term-belief-grade-on-the-coming-book`
(`SEAT_PREREG_THE_ENDING_TERM_BELIEF_ON_THE_COMING_BOOK_2026-11-22.md`). It is filed before any
`run_output` built from a commit that descends from `59cd5ebda` exists. The policy file is read, not changed. No switch moves.

## 0. Premise check, done before reading any outcome

- **No earlier record gives a per-year held-back ranking for both beliefs.** `427e5f021` and
  `5cdb72eb3` grade §14's departure channel: paired arms, money, pooled across seeds. §10 of the
  arms record (`7a7ad95dc`) gives one held-back year, 2019: 0.819 conditioned against 0.333 live, on
  a 21 Oct arms book. The 22 Nov pre-registration pools 2019–2024 into one AUC. So the item is not
  already spent.
- **The 20 Nov book (`6a588a832f`, `docs/reports/run_output_latest.json`) carries no
  `desk_belief_log`.** The 22 Nov pre-registration found this and its grader refuses the book
  by name. The item's word "its desk states" therefore names nothing on disk. What the book
  does carry is 570 renewal events in `customer_events`, each with the desk belief
  (`company_churn_estimate` is the same `company_est_pre` that `desk_belief_log` writes at
  `simulation/run_phase2b.py:5148`) and its outcome. This record rebuilds the desk rows from those
  events, as stated in §1. It labels every figure as coming from **rebuilt rows**. None of them is
  a reading of the field the coming book will carry.

## 1. Method (fixed before the run)

The rebuild is one row per renewal event that carries `company_churn_estimate`:
- `account_id` is `household_of(customer_id)`.
- `term_start` is `event_date`.
- `desk_churn_belief` is `company_churn_estimate`.
- `left` means `event_type == "churned"`.
- `desk_asked` is True. Every one of these events carries a belief, and the book does not record
  whether the desk was asked.
- **`ending_term_type`** is read off the world's own roll gate. The run sets `departure_rolled`
  False only when the previous term was an SVT segment (`departure_rolled_at_renewal`,
  `simulation/customer_events.py:493`). So:
  - a row with `departure_rolled` False is `default`, or `default_after_declined_fix` when the
    same supply point's previous renewal event was `declined_fix`;
  - every other row is `fixed`.

  This is a rebuild. It can differ from `ending_term_type()` in the run in two ways. (a) A
  previous term that was neither a fix nor the default (deemed, pass-through) is typed `fixed`
  here, where the run gives None. (b) The splice flag is inferred from the order of events, not
  read.

Those rows go into the grader that landed with the 22 Nov pre-registration, unchanged:
`tools.grade_ending_term_belief_on_a_book.grade`. Its outcome is a `churned` row in
`customer_events` within 365 days. Its conditioned belief is the online ending-term ledger fed
only by earlier years. Its interval is an account-clustered bootstrap (1,000 draws, seed 7).

Per renewal year 2019–2024, I take the grader's `_point` and `_clustered_bounds` on that year's
states. I report the AUC of each belief, the paired difference, the number of states and the
number of leavers. A year with fewer than 15 leavers is reported but marked **void**, not graded.
That is the grader's own floor, applied per year.

As a secondary, the outcome widened to include the book's separate `svt_departures` list. That
list holds the drift exits, and the grader does not read it on this book.

## 2. Predictions (filed 2026-11-23 10:20Z, before the run)

| | prediction | confidence |
|---|---|---|
| **P1** pooled 2019–2024 live AUC | 0.30–0.58, point 0.45 | 70% |
| **P2** pooled conditioned AUC | above the live AUC; point 0.70 | 70% |
| **P3** pooled paired lower bound | above 0 | 60% |
| **P4** years with ≥ 15 leavers | at most two of the six | 80% |
| **P5** every non-void year's paired interval | includes 0 (too few states for a per-year call) | 65% |

Why these are lower than the 22 Nov file's Q1/Q3: this book has 570 renewal states over ten years,
and many years in 2019–2024 hold fewer than 70 of them. The rebuilt types also add noise.

## 3. What each result does

Nothing here meets the switch-on rule: paired arms with a `departure` interval above zero. So
**nothing here flips the switch**. The record is the baseline that the coming book's read cites.
- If the coming book's per-year figures fall inside these intervals, the world has not moved the
  ranking since 20 Nov.
- If they fall outside, the s.12g commits moved it, and that read must say so.
- If the rebuilt `fixed` and `default` counts here differ by more than 10% from the coming book's
  `by_type`, the rebuild is wrong, and the read must cite this record for its counts only.

## 4. The read
