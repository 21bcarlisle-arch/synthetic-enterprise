# Pre-registration: how many dual households hold a credit on one fuel and a debt on the other, on the publish run

**Written 2026-10-18 ~17:30Z. No dual-fuel run output has been read for this prereg.** Claim
`may-a-supplier-net-one-fuels-credit-against-the-others-debt` (Lane 0, seat). The knowledge is
`docs/market_research/how_a_gb_domestic_book_splits_by_fuel_and_how_a_two_fuel_home_switches.md` §8b:
from 22 Jan 2021 the customer has a licence-backed right to offset one contract's credit against
another's debt (SLC 27.8D). The question here is how much of the book that right touches. Today the
DD book and collections keep one balance per supply point and never net (finding
`WORKER_FINDING_THE_COMPANY_DECIDES_A_DUAL_HOUSEHOLD_PER_LEG_…_2026-10-18.md` §2, §4 item 3).

## 0. Which run, and what is read

- **The run** is the one `SEAT_PREREG_B11_C35_C34_ON_THE_FIRST_PUBLISHED_DUAL_FUEL_RUN_2026-10-18.md`
  §0 names: the first `run_output_<sha>_20261019T*.json` processed after the 19 Oct 03:00Z publish
  window opens, the one committed as `run_output_latest.json.gz`.
- **The book** is `simulation.dd_balance_book.build_dd_balance_book(bills, opening, closed,
  seek_balance_at_review=<the run's own setting>, **forecast_inputs_from_run(run))`, with `closed`
  built as `review_arms_from_run` builds it (a leg is closed when its last bill predates the run's
  last billed month). A leg's balance is `BalancePoint.balance_gbp` (+ = credit held, − = debit).
- **A dual household** is a `saas.customer_reaction._billing_account_id` with a trajectory on
  **both** legs (`X` and `Xg`). A household with one leg not on DD, or with no opening DD, has one
  trajectory or none and is outside the population. That is what a supplier sees.
- **Opposite signs** means one leg > +£1 and the other < −£1 in the same `month`. The ±£1 band keeps
  rounding noise out.

## 1. What the definition means before anything is counted

The netting question exists only where one leg is in credit and the other is in debit **in the same
month**. Two legs in credit, or two in debit, raise no netting question, however large they are. So
the three readings below count household-months and households with that state, not balance sizes.
The amount netting would move is the smaller of the two magnitudes, `min(credit, |debit|)`.

## 2. Predictions

**N1. Population.** Dual households with both legs on a DD trajectory, over the whole run:
**200–270 (point 240).** Why: 341 of 447 live-book households are dual (finding §5). The DD channel
is drawn once per household with U < 0.72 for electricity and U < 0.75 for gas
(`household_segments.payment_channel_for_customer`), so about 72% have both on DD, which is 245.
Of those, **both legs open at run end: 80–230 (point 150).** That width is honest: I have not read
how many dual homes leave over the window.

**N2. At run end** (the last billed month; `REPORT_END` is 2025-06-07, so May or June 2025), the
share of the run-end population with opposite signs: **0.10–0.35 (point 0.20).** Why it is low:
both legs start at zero on one acquisition date and share one seasonal phase, so the seasonal part
of each balance has the same sign. Without a balance-seeking review, the drift is the review's lag
behind price moves: a DD set on last year's spend over-collects when prices fall. Prices fell on
both fuels through 2023–25, so I expect most households to be in credit on both legs at run end.
**Of the opposite-sign households at run end, more than half have gas in credit and electricity in
debit,** because gas prices fell further.

**N3. Across the run.** Of the household-months where both legs are open on DD, the share with
opposite signs: **0.15–0.40 (point 0.27).** The opposite-sign months with gas in debit fall mostly
in **December to April: at least 60% of them.** The cause is gas's larger winter draw.

**N4. Ever.** The share of the N1 population with opposite signs in at least one month: **0.70–0.98
(point 0.85).** Why: over several years, one leg's small seasonal swing (electricity) and the other's
large one (gas) cross zero at different times, unless the drift is large.

**N5. What netting would move at run end:** the median of `min(credit, |debit|)` over the N2
households is **£15–£90 (point £40).** The electricity leg is usually the smaller magnitude.

## 3. What would refute the reasoning, and what voids a reading

- If **N2 is above 0.35**, the drift is not shared between the fuels as I assumed. The next reading
  is each leg's DD set against its own year's spend, split by fuel.
- If **N4 is below 0.70**, the two legs' trajectories move together more than the seasonal argument
  allows. Read whether the opening DDs are sized from one household figure.
- **Seek-balance switch.** These predictions are for `seek_balance_at_review = False`, which is
  `REVIEW_SEEKS_BALANCE` today (`company/billing/dd_review.py:148`). If the publish run has it on,
  the review pulls each leg toward zero every year. Then the grade reads **both** arms, takes these
  predictions against the off arm, and states the on arm only as a result. For the on arm I predict
  only that N5 falls (point ≤ £30).
- A commit that changes the DD book, the review, the payment-channel draw or the population draw
  between now and the publish run's sha does not void a level reading: these are levels, not
  differences. It does mean the grade must name that sha.

## 4. Grade

To be graded by the reader of the publish run. Write the result **below** this line, and do not
edit the predictions above.

*Instrument, built 2026-10-18 before the publish run and tested on synthetic fixtures only:
`python3 -m tools.dual_leg_opposite_signs <the §0 run>` prints N1 to N5 on both arms. The book's
closed set cannot move these readings (bars are taken after the balance points are written).*

**Book note, 2026-10-19 (seat).** The 19 Oct publish run (`8b6fea024`) predates `30246d6f0`, so its campaign wins are dual on **every** gas home: 172 of 172, 0 gas-only, against about 0.906 at the published rate. The readings here are taken on that always-dual campaign book. It holds about 413 dual households where the split rate gives about 397, roughly 4% fewer. Do not difference a later run's dual counts against these readings as if only the company changed. Reading and prediction: `docs/staging/records/SEAT_PREREG_THE_FIRST_RUN_WITH_SPLIT_CAMPAIGN_HOMES_AGAINST_THE_ALWAYS_DUAL_CAMPAIGN_BOOK_THE_19_OCT_RUN_CARRIES_2026-10-19.md`.
